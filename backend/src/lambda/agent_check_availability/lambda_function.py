import json
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
appconfig = boto3.client('appconfig')

APPOINTMENTS_TABLE = os.environ['DYNAMODB_APPOINTMENTS_TABLE']
PROFESSIONALS_TABLE = os.environ['DYNAMODB_PROFESSIONALS_TABLE']
APPCONFIG_APP = os.environ['APPCONFIG_APPLICATION']
APPCONFIG_ENV = os.environ['APPCONFIG_ENVIRONMENT']
APPCONFIG_CONFIG = os.environ['APPCONFIG_CONFIGURATION']

appointments_table = dynamodb.Table(APPOINTMENTS_TABLE)
professionals_table = dynamodb.Table(PROFESSIONALS_TABLE)

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
            ClientId='lambda-availability-checker'
        )
        config_content = response['Content'].read().decode('utf-8')
        return json.loads(config_content)
    except Exception as e:
        logger.error(f"CRITICAL: Failed to get AppConfig: {e}")
        return {"max_booking_days": 90}

def get_day_name(date_obj):
    """Convert date to day name in English lowercase."""
    return date_obj.strftime('%A').lower()

def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")
    
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = convert_params_to_dict(event.get('parameters', []))
    
    # userId pode vir em sessionAttributes (teste) ou promptSessionAttributes (Bedrock Agent)
    user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
    
    logger.info(f"Extracted user_id: {user_id}")
    logger.info(f"sessionAttributes: {event.get('sessionAttributes')}")
    logger.info(f"promptSessionAttributes: {event.get('promptSessionAttributes')}")

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
        
        start_date_str = parameters.get('start_date')
        end_date_str = parameters.get('end_date', start_date_str)
        professional_id = parameters.get('professional_id')

        if not start_date_str:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "Error: start_date is required."}}
                    }
                }
            }

        start_date = datetime.fromisoformat(start_date_str).date()
        end_date = datetime.fromisoformat(end_date_str).date()
        today = datetime.now().date()
        max_date = today + timedelta(days=max_booking_days)

        if start_date > max_date:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": f"Cannot book beyond {max_booking_days} days. Maximum date: {max_date.isoformat()}"}}
                    }
                }
            }

        # Get professionals
        if professional_id:
            prof_response = professionals_table.get_item(Key={'professional_id': professional_id})
            professionals = [prof_response['Item']] if 'Item' in prof_response else []
        else:
            prof_response = professionals_table.scan(FilterExpression='is_active = :val', ExpressionAttributeValues={':val': True})
            professionals = prof_response.get('Items', [])

        if not professionals:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "No professionals available."}}
                    }
                }
            }

        # Get existing appointments
        appointments = []
        for prof in professionals:
            response = appointments_table.query(
                IndexName='professional_id-appointment_date-index',
                KeyConditionExpression=Key('professional_id').eq(prof['professional_id']) & Key('appointment_date').between(
                    start_date.isoformat(), (end_date + timedelta(days=1)).isoformat()
                )
            )
            appointments.extend(response.get('Items', []))

        # Build availability response
        availability = []
        current_date = start_date
        while current_date <= end_date:
            day_name = get_day_name(current_date)
            
            for prof in professionals:
                if day_name not in prof.get('working_days', []):
                    continue
                
                working_hours = prof.get('working_hours', {})
                start_time = working_hours.get('start', '08:00')
                end_time = working_hours.get('end', '00:00')
                
                # Count appointments for this professional on this date
                day_appointments = [a for a in appointments if a['professional_id'] == prof['professional_id'] and a['appointment_date'].startswith(current_date.isoformat())]
                
                availability.append({
                    "date": current_date.isoformat(),
                    "professional_id": prof['professional_id'],
                    "professional_name": prof['name'],
                    "available_hours": f"{start_time} to {end_time}",
                    "booked_slots": len(day_appointments)
                })
            
            current_date += timedelta(days=1)

        response_text = f"Found {len(availability)} available slots from {start_date} to {end_date}. Details: {json.dumps(availability, default=str)}"

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
                    "responseBody": {"TEXT": {"body": f"Error checking availability: {str(e)}"}}
                }
            }
        }
