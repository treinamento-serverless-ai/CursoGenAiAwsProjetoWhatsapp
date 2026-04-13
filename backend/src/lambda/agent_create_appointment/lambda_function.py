import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import boto3
from difflib import SequenceMatcher

TIMEZONE = ZoneInfo("America/Sao_Paulo")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
appconfig = boto3.client('appconfig')

appointments_table = dynamodb.Table(os.environ['DYNAMODB_APPOINTMENTS_TABLE'])
professionals_table = dynamodb.Table(os.environ['DYNAMODB_PROFESSIONALS_TABLE'])
services_table = dynamodb.Table(os.environ['DYNAMODB_SERVICES_TABLE'])
clients_table = dynamodb.Table(os.environ['DYNAMODB_CLIENTS_TABLE'])

APPCONFIG_APP = os.environ['APPCONFIG_APPLICATION']
APPCONFIG_ENV = os.environ['APPCONFIG_ENVIRONMENT']
APPCONFIG_CONFIG = os.environ['APPCONFIG_CONFIGURATION']


def fuzzy_find(search_term, items, key, threshold=0.6):
    term = search_term.lower()
    return [item for item in items if SequenceMatcher(None, term, item.get(key, '').lower()).ratio() >= threshold]


def sanitize_param(value):
    if not isinstance(value, str):
        return value
    return value.replace('&quot;', '').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip('" ')


def get_appconfig():
    try:
        response = appconfig.get_configuration(
            Application=APPCONFIG_APP, Environment=APPCONFIG_ENV,
            Configuration=APPCONFIG_CONFIG, ClientId='lambda-create-appointment'
        )
        return json.loads(response['Content'].read().decode('utf-8'))
    except Exception as e:
        logger.error(f"CRITICAL: Failed to get AppConfig: {e}")
        return {"max_booking_days": 90}


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    params = {p.get("name"): sanitize_param(p.get("value")) for p in event.get('parameters', []) if p.get("name")}

    user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
    logger.info(f"[{context.aws_request_id}] CreateAppointment called. user_id={user_id}, params={params}")

    if not user_id:
        return _response(action_group, function_name, "Error: User ID not found.", failure=True)

    try:
        config = get_appconfig()
        max_booking_days = int(config.get('max_booking_days', 90))

        appointment_date_str = params.get('appointment_date')
        professional_name = params.get('professional_name')
        service_name = params.get('service_name')

        if not all([appointment_date_str, professional_name, service_name]):
            return _response(action_group, function_name,
                             "Error: appointment_date, professional_name, and service_name are required.")

        appointment_date = datetime.fromisoformat(appointment_date_str)
        today = datetime.now(TIMEZONE)

        if appointment_date.date() < today.date():
            return _response(action_group, function_name,
                             f"Error: date {appointment_date_str} is in the past. Today is {today.date()}. Please choose a future date.")
        if appointment_date.date() > (today + timedelta(days=max_booking_days)).date():
            return _response(action_group, function_name,
                             f"Cannot book beyond {max_booking_days} days.")

        # Fuzzy resolve professional
        all_profs = professionals_table.scan(FilterExpression='is_active = :val', ExpressionAttributeValues={':val': True}).get('Items', [])
        prof_matches = fuzzy_find(professional_name, all_profs, 'name')
        if not prof_matches:
            available = ", ".join(p.get('name', '') for p in all_profs)
            return _response(action_group, function_name,
                             f"Professional '{professional_name}' not found. Available: {available}")
        professional = prof_matches[0]

        # Fuzzy resolve service
        all_services = services_table.scan(FilterExpression='is_active = :val', ExpressionAttributeValues={':val': True}).get('Items', [])
        svc_matches = fuzzy_find(service_name, all_services, 'name')
        if not svc_matches:
            svc_matches = fuzzy_find(service_name, all_services, 'description')
        if not svc_matches:
            available = ", ".join(s.get('name', '') for s in all_services)
            return _response(action_group, function_name,
                             f"Service '{service_name}' not found. Available: {available}")
        service = svc_matches[0]
        service_id = service['service_id']

        # Verify professional offers this service
        prof_service = next((s for s in professional.get('services', []) if s['service_id'] == service_id), None)
        if not prof_service:
            return _response(action_group, function_name,
                             f"Service '{service.get('name')}' is not available with {professional.get('name')}.")

        # Get client info
        client_response = clients_table.get_item(Key={'phone_number': user_id})
        client_name = client_response.get('Item', {}).get('name', 'Cliente')

        # Create appointment
        appointment_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        appointments_table.put_item(Item={
            "appointment_id": appointment_id,
            "appointment_date": appointment_date.isoformat(),
            "client_name": client_name,
            "client_phone": user_id,
            "service_id": service_id,
            "service_name": service['name'],
            "professional_id": professional['professional_id'],
            "professional_name": professional['name'],
            "status": "scheduled",
            "created_at": now,
            "updated_at": now
        })

        return _response(action_group, function_name,
                         f"Appointment created successfully! {client_name} with {professional['name']} for {service['name']} on {appointment_date.strftime('%Y-%m-%d %H:%M')}. Status: scheduled")

    except Exception as e:
        logger.error(f"Error: {e}")
        return _response(action_group, function_name, f"Error creating appointment: {str(e)}", failure=True)


def _response(action_group, function_name, body, failure=False):
    r = {"responseBody": {"TEXT": {"body": body}}}
    if failure:
        r["responseState"] = "FAILURE"
    return {
        "messageVersion": "1.0",
        "response": {"actionGroup": action_group, "function": function_name, "functionResponse": r}
    }
