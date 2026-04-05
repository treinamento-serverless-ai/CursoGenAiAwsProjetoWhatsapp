import json
import logging
import os
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
APPOINTMENTS_TABLE = os.environ['DYNAMODB_APPOINTMENTS_TABLE']
appointments_table = dynamodb.Table(APPOINTMENTS_TABLE)

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    
    user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
    
    if not user_id:
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseState": "FAILURE",
                    "responseBody": {"TEXT": {"body": "Error: User ID not found."}}
                }
            }
        }
    
    try:
        now = datetime.now().isoformat()
        
        response = appointments_table.query(
            IndexName='client_phone-appointment_date-index',
            KeyConditionExpression=Key('client_phone').eq(user_id) & Key('appointment_date').gte(now),
            FilterExpression='#status <> :cancelled',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':cancelled': 'CANCELLED'}
        )
        
        appointments = response.get('Items', [])
        
        if not appointments:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "You have no upcoming appointments."}}
                    }
                }
            }
        
        summary = []
        for appt in appointments:
            appt_info = {
                "appointment_id": appt.get('appointment_id'),
                "date": appt.get('appointment_date'),
                "professional": appt.get('professional_name'),
                "service": appt.get('service_name'),
                "status": appt.get('status')
            }
            summary.append(appt_info)
        
        response_text = f"Your upcoming appointments: {json.dumps(summary, ensure_ascii=False)}"
        
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": response_text}}
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error listing appointments: {e}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseState": "FAILURE",
                    "responseBody": {"TEXT": {"body": f"Error listing appointments: {str(e)}"}}
                }
            }
        }
