import json
import logging
import os
from datetime import datetime

import boto3
from difflib import SequenceMatcher
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
appointments_table = dynamodb.Table(os.environ['DYNAMODB_APPOINTMENTS_TABLE'])


def fuzzy_find(search_term, items, key, threshold=0.6):
    term = search_term.lower()
    return [item for item in items if SequenceMatcher(None, term, item.get(key, '').lower()).ratio() >= threshold]


def sanitize_param(value):
    if not isinstance(value, str):
        return value
    return value.replace('&quot;', '').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip('" ')


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    params = {p.get("name"): sanitize_param(p.get("value")) for p in event.get('parameters', []) if p.get("name")}

    user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
    service_name = params.get('service_name', '')
    appointment_date = params.get('appointment_date', '')

    logger.info(f"[{context.aws_request_id}] CancelAppointment called. user_id={user_id}, service_name={service_name}, date={appointment_date}")

    if not user_id:
        return _response(action_group, function_name, "Error: User ID not found.", failure=True)

    if not service_name and not appointment_date:
        return _response(action_group, function_name,
                         "Error: provide service_name and/or appointment_date to identify the appointment to cancel.")

    try:
        # Get user's active appointments
        now = datetime.now().isoformat()
        resp = appointments_table.query(
            IndexName='client_phone-appointment_date-index',
            KeyConditionExpression=Key('client_phone').eq(user_id) & Key('appointment_date').gte(now),
            FilterExpression='#status <> :cancelled',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':cancelled': 'CANCELLED'}
        )
        appointments = resp.get('Items', [])

        if not appointments:
            return _response(action_group, function_name, "You have no upcoming appointments to cancel.")

        # Filter by service name (fuzzy) and/or date
        matches = appointments
        if service_name:
            matches = fuzzy_find(service_name, matches, 'service_name')
        if appointment_date:
            matches = [a for a in matches if a.get('appointment_date', '').startswith(appointment_date[:10])]

        if not matches:
            upcoming = ", ".join(f"{a.get('service_name')} with {a.get('professional_name')} on {a.get('appointment_date')}" for a in appointments)
            return _response(action_group, function_name,
                             f"No matching appointment found. Your upcoming appointments: {upcoming}")

        if len(matches) > 1:
            options = ", ".join(f"{a.get('service_name')} with {a.get('professional_name')} on {a.get('appointment_date')}" for a in matches)
            return _response(action_group, function_name,
                             f"Multiple appointments match. Please be more specific: {options}")

        appointment = matches[0]

        # Cancel
        appointments_table.update_item(
            Key={'appointment_id': appointment['appointment_id'], 'appointment_date': appointment['appointment_date']},
            UpdateExpression='SET #status = :cancelled, updated_at = :now',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':cancelled': 'CANCELLED', ':now': datetime.now().isoformat()}
        )

        return _response(action_group, function_name,
                         f"Appointment cancelled successfully. Details: {appointment.get('service_name')} with {appointment.get('professional_name')} on {appointment.get('appointment_date')}.")

    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return _response(action_group, function_name, f"Error cancelling appointment: {str(e)}", failure=True)


def _response(action_group, function_name, body, failure=False):
    r = {"responseBody": {"TEXT": {"body": body}}}
    if failure:
        r["responseState"] = "FAILURE"
    return {
        "messageVersion": "1.0",
        "response": {"actionGroup": action_group, "function": function_name, "functionResponse": r}
    }
