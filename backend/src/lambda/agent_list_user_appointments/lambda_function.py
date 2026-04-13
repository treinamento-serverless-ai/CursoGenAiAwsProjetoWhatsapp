import json
import logging
import os
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
appointments_table = dynamodb.Table(os.environ['DYNAMODB_APPOINTMENTS_TABLE'])


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')

    user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
    logger.info(f"[{context.aws_request_id}] ListUserAppointments called. user_id={user_id}")

    if not user_id:
        return _response(action_group, function_name, "Error: User ID not found.", failure=True)

    try:
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
            return _response(action_group, function_name, "You have no upcoming appointments.")

        summary = [
            {
                "date": appt.get('appointment_date'),
                "professional": appt.get('professional_name'),
                "service": appt.get('service_name'),
                "status": appt.get('status')
            }
            for appt in appointments
        ]

        return _response(action_group, function_name,
                         f"Your upcoming appointments: {json.dumps(summary, ensure_ascii=False)}")

    except Exception as e:
        logger.error(f"Error listing appointments: {e}")
        return _response(action_group, function_name, f"Error: {str(e)}", failure=True)


def _response(action_group, function_name, body, failure=False):
    r = {"responseBody": {"TEXT": {"body": body}}}
    if failure:
        r["responseState"] = "FAILURE"
    return {
        "messageVersion": "1.0",
        "response": {"actionGroup": action_group, "function": function_name, "functionResponse": r}
    }
