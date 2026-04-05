import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
SERVICES_TABLE = os.environ['DYNAMODB_SERVICES_TABLE']
services_table = dynamodb.Table(SERVICES_TABLE)

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    
    try:
        response = services_table.scan(
            FilterExpression='is_active = :val',
            ExpressionAttributeValues={':val': True}
        )
        services = response.get('Items', [])
        
        if not services:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "No services available at the moment."}}
                    }
                }
            }
        
        summary = []
        for service in services:
            service_info = {
                "service_id": service.get('service_id'),
                "name": service.get('name'),
                "description": service.get('description', ''),
                "category": service.get('category', 'General')
            }
            summary.append(service_info)
        
        response_text = f"Available services: {json.dumps(summary, ensure_ascii=False)}"
        
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
        logger.error(f"Error listing services: {e}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseState": "FAILURE",
                    "responseBody": {"TEXT": {"body": f"Error listing services: {str(e)}"}}
                }
            }
        }
