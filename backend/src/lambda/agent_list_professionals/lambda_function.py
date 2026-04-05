import json
import logging
import os
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
PROFESSIONALS_TABLE = os.environ['DYNAMODB_PROFESSIONALS_TABLE']
professionals_table = dynamodb.Table(PROFESSIONALS_TABLE)

def convert_params_to_dict(params_list):
    """Convert Bedrock Agent parameter list to dictionary."""
    return {param.get("name"): param.get("value") for param in params_list if param.get("name")}

def calculate_years_experience(career_start_date):
    """Calculate years of experience from career start date."""
    if not career_start_date:
        return None
    try:
        start = datetime.fromisoformat(career_start_date)
        years = (datetime.now() - start).days / 365.25
        return round(years, 1)
    except:
        return None

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    
    try:
        response = professionals_table.scan(
            FilterExpression='is_active = :val',
            ExpressionAttributeValues={':val': True}
        )
        professionals = response.get('Items', [])
        
        if not professionals:
            return {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "functionResponse": {
                        "responseBody": {"TEXT": {"body": "No professionals available at the moment."}}
                    }
                }
            }
        
        summary = []
        for prof in professionals:
            years_exp = calculate_years_experience(prof.get('career_start_date'))
            
            prof_info = {
                "name": prof.get('name'),
                "specialty": prof.get('specialty', 'General'),
                "years_experience": years_exp if years_exp else "Not specified",
                "social_media": prof.get('social_media_link', 'Not available')
            }
            summary.append(prof_info)
        
        response_text = f"Available professionals: {json.dumps(summary, ensure_ascii=False)}"
        
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
        logger.error(f"Error listing professionals: {e}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseState": "FAILURE",
                    "responseBody": {"TEXT": {"body": f"Error listing professionals: {str(e)}"}}
                }
            }
        }
