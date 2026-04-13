import json
import logging
import os
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
professionals_table = dynamodb.Table(os.environ['DYNAMODB_PROFESSIONALS_TABLE'])


def calculate_years_experience(career_start_date):
    if not career_start_date:
        return None
    try:
        start = datetime.fromisoformat(career_start_date)
        return round((datetime.now() - start).days / 365.25, 1)
    except Exception:
        return None


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    logger.info(f"[{context.aws_request_id}] ListProfessionals called")

    try:
        response = professionals_table.scan(
            FilterExpression='is_active = :val',
            ExpressionAttributeValues={':val': True}
        )
        professionals = response.get('Items', [])

        if not professionals:
            return _response(action_group, function_name, "No professionals available at the moment.")

        summary = [
            {
                "name": prof.get('name'),
                "specialty": prof.get('specialty', 'General'),
                "years_experience": calculate_years_experience(prof.get('career_start_date')) or "Not specified",
            }
            for prof in professionals
        ]

        return _response(action_group, function_name,
                         f"Available professionals (use name to identify): {json.dumps(summary, ensure_ascii=False)}")

    except Exception as e:
        logger.error(f"Error listing professionals: {e}")
        return _response(action_group, function_name, f"Error listing professionals: {str(e)}", failure=True)


def _response(action_group, function_name, body, failure=False):
    r = {"responseBody": {"TEXT": {"body": body}}}
    if failure:
        r["responseState"] = "FAILURE"
    return {
        "messageVersion": "1.0",
        "response": {"actionGroup": action_group, "function": function_name, "functionResponse": r}
    }
