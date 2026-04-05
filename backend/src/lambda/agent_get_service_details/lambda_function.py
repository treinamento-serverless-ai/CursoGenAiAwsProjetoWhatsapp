import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
PROFESSIONALS_TABLE = os.environ['DYNAMODB_PROFESSIONALS_TABLE']
SERVICES_TABLE = os.environ['DYNAMODB_SERVICES_TABLE']
professionals_table = dynamodb.Table(PROFESSIONALS_TABLE)
services_table = dynamodb.Table(SERVICES_TABLE)

def convert_params_to_dict(params_list):
    """Convert Bedrock Agent parameter list to dictionary."""
    return {param.get("name"): param.get("value") for param in params_list if param.get("name")}

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = convert_params_to_dict(event.get('parameters', []))
    
    service_id = parameters.get('service_id')
    
    if not service_id:
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": "Error: service_id is required."}}
                }
            }
        }
    
    try:
        # Get service info
        service_response = services_table.get_item(Key={'service_id': service_id})
        if 'Item' not in service_response:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "Service not found."}}
                    }
                }
            }
        
        service = service_response['Item']
        
        # Get professionals offering this service
        prof_response = professionals_table.scan(
            FilterExpression='is_active = :val',
            ExpressionAttributeValues={':val': True}
        )
        professionals = prof_response.get('Items', [])
        
        details = []
        for prof in professionals:
            prof_service = next((s for s in prof.get('services', []) if s['service_id'] == service_id), None)
            if prof_service:
                details.append({
                    "professional_name": prof.get('name'),
                    "professional_id": prof.get('professional_id'),
                    "duration_hours": float(prof_service.get('duration_hours', 0)),
                    "price": float(prof_service.get('price', 0))
                })
        
        if not details:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": f"Service '{service.get('name')}' is not currently offered by any professional."}}
                    }
                }
            }
        
        response_data = {
            "service_name": service.get('name'),
            "description": service.get('description', ''),
            "category": service.get('category', 'General'),
            "professionals": details
        }
        
        response_text = f"Service details: {json.dumps(response_data, ensure_ascii=False)}"
        
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
        logger.error(f"Error getting service details: {e}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseState": "FAILURE",
                    "responseBody": {"TEXT": {"body": f"Error getting service details: {str(e)}"}}
                }
            }
        }
