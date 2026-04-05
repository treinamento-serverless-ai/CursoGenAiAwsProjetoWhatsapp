import json
import logging
import os
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
APPOINTMENTS_TABLE = os.environ['DYNAMODB_APPOINTMENTS_TABLE']
appointments_table = dynamodb.Table(APPOINTMENTS_TABLE)

def convert_params_to_dict(params_list):
    """Convert Bedrock Agent parameter list to dictionary."""
    return {param.get("name"): param.get("value") for param in params_list if param.get("name")}

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = convert_params_to_dict(event.get('parameters', []))
    
    user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
    appointment_id = parameters.get('appointment_id')
    
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
    
    if not appointment_id:
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": "Error: appointment_id is required."}}
                }
            }
        }
    
    try:
        # Get appointment
        response = appointments_table.query(
            KeyConditionExpression='appointment_id = :id',
            ExpressionAttributeValues={':id': appointment_id}
        )
        
        items = response.get('Items', [])
        if not items:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "Appointment not found."}}
                    }
                }
            }
        
        appointment = items[0]
        
        # Verify ownership
        if appointment.get('client_phone') != user_id:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "You can only cancel your own appointments."}}
                    }
                }
            }
        
        # Check if already cancelled
        if appointment.get('status') == 'CANCELLED':
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "This appointment is already cancelled."}}
                    }
                }
            }
        
        # Cancel appointment
        appointments_table.update_item(
            Key={
                'appointment_id': appointment_id,
                'appointment_date': appointment['appointment_date']
            },
            UpdateExpression='SET #status = :cancelled, updated_at = :now',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':cancelled': 'CANCELLED',
                ':now': datetime.now().isoformat()
            }
        )
        
        response_text = f"Appointment {appointment_id} cancelled successfully. Details: {appointment.get('service_name')} with {appointment.get('professional_name')} on {appointment.get('appointment_date')}."
        
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
        logger.error(f"Error cancelling appointment: {e}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseState": "FAILURE",
                    "responseBody": {"TEXT": {"body": f"Error cancelling appointment: {str(e)}"}}
                }
            }
        }
