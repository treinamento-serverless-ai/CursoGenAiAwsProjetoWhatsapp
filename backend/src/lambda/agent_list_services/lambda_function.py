import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
services_table = dynamodb.Table(os.environ['DYNAMODB_SERVICES_TABLE'])


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    logger.info(f"[{context.aws_request_id}] ListServices called")

    try:
        response = services_table.scan(
            FilterExpression='is_active = :val',
            ExpressionAttributeValues={':val': True}
        )
        services = response.get('Items', [])

        if not services:
            return _response(action_group, function_name, "No services available at the moment.")

        summary = [
            {
                "name": s.get('name'),
                "description": s.get('description') or 'Sem descrição disponível',
                "category": s.get('category', 'General')
            }
            for s in services
        ]

        return _response(action_group, function_name,
                         f"Available services (use name or description to identify): {json.dumps(summary, ensure_ascii=False)}")

    except Exception as e:
        logger.error(f"Error listing services: {e}")
        return _response(action_group, function_name, f"Error listing services: {str(e)}", failure=True)


def _response(action_group, function_name, body, failure=False):
    r = {"responseBody": {"TEXT": {"body": body}}}
    if failure:
        r["responseState"] = "FAILURE"
    return {
        "messageVersion": "1.0",
        "response": {"actionGroup": action_group, "function": function_name, "functionResponse": r}
    }
