import json
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import boto3
from difflib import SequenceMatcher
from boto3.dynamodb.conditions import Key

TIMEZONE = ZoneInfo("America/Sao_Paulo")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
appconfig = boto3.client('appconfig')

appointments_table = dynamodb.Table(os.environ['DYNAMODB_APPOINTMENTS_TABLE'])
professionals_table = dynamodb.Table(os.environ['DYNAMODB_PROFESSIONALS_TABLE'])

APPCONFIG_APP = os.environ['APPCONFIG_APPLICATION']
APPCONFIG_ENV = os.environ['APPCONFIG_ENVIRONMENT']
APPCONFIG_CONFIG = os.environ['APPCONFIG_CONFIGURATION']


def fuzzy_find(search_term, items, key, threshold=0.6):
    term = search_term.lower()
    return [item for item in items if SequenceMatcher(None, term, item.get(key, '').lower()).ratio() >= threshold]


def get_appconfig():
    try:
        response = appconfig.get_configuration(
            Application=APPCONFIG_APP, Environment=APPCONFIG_ENV,
            Configuration=APPCONFIG_CONFIG, ClientId='lambda-availability-checker'
        )
        return json.loads(response['Content'].read().decode('utf-8'))
    except Exception as e:
        logger.error(f"CRITICAL: Failed to get AppConfig: {e}")
        return {"max_booking_days": 90}


def sanitize_param(value):
    if not isinstance(value, str):
        return value
    return value.replace('&quot;', '').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip('" ')


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    params = {p.get("name"): sanitize_param(p.get("value")) for p in event.get('parameters', []) if p.get("name")}

    user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
    logger.info(f"[{context.aws_request_id}] CheckAvailability called. params={params}, user_id={user_id}")

    if not user_id:
        return _response(action_group, function_name, "Error: User ID not found.", failure=True)

    try:
        config = get_appconfig()
        max_booking_days = int(config.get('max_booking_days', 90))

        start_date_str = params.get('start_date')
        end_date_str = params.get('end_date', start_date_str)
        professional_name = params.get('professional_name')

        if not start_date_str:
            return _response(action_group, function_name, "Error: start_date is required.")

        start_date = datetime.fromisoformat(start_date_str).date()
        end_date = datetime.fromisoformat(end_date_str).date()
        today = datetime.now(TIMEZONE).date()
        max_date = today + timedelta(days=max_booking_days)

        if start_date < today:
            start_date = today
            logger.info(f"[{context.aws_request_id}] start_date was in the past, adjusted to today: {today}")
        if end_date < today:
            end_date = today
        if start_date > max_date:
            return _response(action_group, function_name,
                             f"Cannot book beyond {max_booking_days} days. Maximum date: {max_date}")

        # Get professionals (fuzzy search by name if provided)
        all_profs = professionals_table.scan(FilterExpression='is_active = :val', ExpressionAttributeValues={':val': True}).get('Items', [])

        if professional_name:
            professionals = fuzzy_find(professional_name, all_profs, 'name')
            if not professionals:
                available = ", ".join(p.get('name', '') for p in all_profs)
                return _response(action_group, function_name,
                                 f"Professional '{professional_name}' not found. Available: {available}")
        else:
            professionals = all_profs

        if not professionals:
            return _response(action_group, function_name, "No professionals available.")

        # Get existing appointments
        appointments = []
        for prof in professionals:
            resp = appointments_table.query(
                IndexName='professional_id-appointment_date-index',
                KeyConditionExpression=Key('professional_id').eq(prof['professional_id']) & Key('appointment_date').between(
                    start_date.isoformat(), (end_date + timedelta(days=1)).isoformat()
                )
            )
            appointments.extend(resp.get('Items', []))

        # Build availability
        availability = []
        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime('%A').lower()
            for prof in professionals:
                if day_name not in prof.get('working_days', []):
                    continue
                wh = prof.get('working_hours', {})
                day_appts = [a for a in appointments if a['professional_id'] == prof['professional_id'] and a['appointment_date'].startswith(current_date.isoformat())]
                availability.append({
                    "date": current_date.isoformat(),
                    "professional_name": prof['name'],
                    "available_hours": f"{wh.get('start', '08:00')} to {wh.get('end', '18:00')}",
                    "booked_slots": len(day_appts)
                })
            current_date += timedelta(days=1)

        return _response(action_group, function_name,
                         f"Found {len(availability)} available slots from {start_date} to {end_date}. Details: {json.dumps(availability, default=str)}")

    except Exception as e:
        logger.error(f"Error: {e}")
        return _response(action_group, function_name, f"Error checking availability: {str(e)}", failure=True)


def _response(action_group, function_name, body, failure=False):
    r = {"responseBody": {"TEXT": {"body": body}}}
    if failure:
        r["responseState"] = "FAILURE"
    return {
        "messageVersion": "1.0",
        "response": {"actionGroup": action_group, "function": function_name, "functionResponse": r}
    }
