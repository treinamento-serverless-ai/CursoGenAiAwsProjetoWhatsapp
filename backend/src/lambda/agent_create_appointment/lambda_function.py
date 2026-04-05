import json
import logging
import os
import uuid
from datetime import datetime, timedelta

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
appconfig = boto3.client('appconfig')

APPOINTMENTS_TABLE = os.environ['DYNAMODB_APPOINTMENTS_TABLE']
PROFESSIONALS_TABLE = os.environ['DYNAMODB_PROFESSIONALS_TABLE']
CLIENTS_TABLE = os.environ['DYNAMODB_CLIENTS_TABLE']
APPCONFIG_APP = os.environ['APPCONFIG_APPLICATION']
APPCONFIG_ENV = os.environ['APPCONFIG_ENVIRONMENT']
APPCONFIG_CONFIG = os.environ['APPCONFIG_CONFIGURATION']

appointments_table = dynamodb.Table(APPOINTMENTS_TABLE)
professionals_table = dynamodb.Table(PROFESSIONALS_TABLE)
clients_table = dynamodb.Table(CLIENTS_TABLE)

def convert_params_to_dict(params_list):
    """Convert Bedrock Agent parameter list to dictionary."""
    return {param.get("name"): param.get("value") for param in params_list if param.get("name")}

def get_appconfig():
    """Retrieve configuration from AWS AppConfig."""
    try:
        response = appconfig.get_configuration(
            Application=APPCONFIG_APP,
            Environment=APPCONFIG_ENV,
            Configuration=APPCONFIG_CONFIG,
            ClientId='lambda-create-appointment'
        )
        config_content = response['Content'].read().decode('utf-8')
        return json.loads(config_content)
    except Exception as e:
        logger.error(f"CRITICAL: Failed to get AppConfig: {e}")
        return {"max_booking_days": 90}

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = convert_params_to_dict(event.get('parameters', []))
    
    # userId pode vir em sessionAttributes (teste) ou promptSessionAttributes (Bedrock Agent)
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
        config = get_appconfig()
        max_booking_days = int(config.get('max_booking_days', 90))
        
        appointment_date_str = parameters.get('appointment_date')
        professional_id = parameters.get('professional_id')
        service_id = parameters.get('service_id')

        if not all([appointment_date_str, professional_id, service_id]):
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "Error: appointment_date, professional_id, and service_id are required."}}
                    }
                }
            }

        appointment_date = datetime.fromisoformat(appointment_date_str)
        today = datetime.now()
        max_date = today + timedelta(days=max_booking_days)

        if appointment_date.date() > max_date.date():
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": f"Cannot book beyond {max_booking_days} days. Maximum date: {max_date.date().isoformat()}"}}
                    }
                }
            }

        # Get professional info
        prof_response = professionals_table.get_item(Key={'professional_id': professional_id})
        if 'Item' not in prof_response:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "Professional not found."}}
                    }
                }
            }
        
        professional = prof_response['Item']
        
        # Find service
        service = next((s for s in professional.get('services', []) if s['service_id'] == service_id), None)
        if not service:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "Service not available for this professional."}}
                    }
                }
            }

        # Get client info
        client_response = clients_table.get_item(Key={'phone_number': user_id})
        client_name = client_response.get('Item', {}).get('name', 'Cliente')

        # Create appointment
        appointment_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        appointment = {
            "appointment_id": appointment_id,
            "appointment_date": appointment_date.isoformat(),
            "client_name": client_name,
            "client_phone": user_id,
            "service_id": service_id,
            "service_name": service['service_name'],
            "professional_id": professional_id,
            "professional_name": professional['name'],
            "status": "PENDING",
            "created_at": now,
            "updated_at": now
        }
        
        appointments_table.put_item(Item=appointment)
        
        response_text = f"Appointment created successfully! ID: {appointment_id}. {client_name} with {professional['name']} for {service['service_name']} on {appointment_date.strftime('%Y-%m-%d %H:%M')}. Status: PENDING"

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
        logger.error(f"Error: {e}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseState": "FAILURE",
                    "responseBody": {"TEXT": {"body": f"Error creating appointment: {str(e)}"}}
                }
            }
        }
