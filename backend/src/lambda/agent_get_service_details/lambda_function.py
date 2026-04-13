import json
import logging
import os

import boto3
from difflib import SequenceMatcher

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
professionals_table = dynamodb.Table(os.environ['DYNAMODB_PROFESSIONALS_TABLE'])
services_table = dynamodb.Table(os.environ['DYNAMODB_SERVICES_TABLE'])


def fuzzy_find(search_term, items, key, threshold=0.6):
    term = search_term.lower()
    return [item for item in items if SequenceMatcher(None, term, item.get(key, '').lower()).ratio() >= threshold]


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    params = {p.get("name"): p.get("value", "").replace('&quot;', '').strip('" ') for p in event.get('parameters', []) if p.get("name")}

    service_name = params.get('service_name', '')
    logger.info(f"[{context.aws_request_id}] GetServiceDetails called. service_name={service_name}")

    if not service_name:
        return _response(action_group, function_name, "Error: service_name is required.")

    try:
        services = services_table.scan(FilterExpression='is_active = :val', ExpressionAttributeValues={':val': True}).get('Items', [])

        # Fuzzy search by name, then by description
        matches = fuzzy_find(service_name, services, 'name')
        if not matches:
            matches = fuzzy_find(service_name, services, 'description')
        if not matches:
            available = ", ".join(s.get('name', '') for s in services)
            return _response(action_group, function_name,
                             f"Service '{service_name}' not found. Available services: {available}")

        service = matches[0]
        service_id = service['service_id']

        # Find professionals offering this service
        profs = professionals_table.scan(FilterExpression='is_active = :val', ExpressionAttributeValues={':val': True}).get('Items', [])
        details = []
        for prof in profs:
            ps = next((s for s in prof.get('services', []) if s['service_id'] == service_id), None)
            if ps:
                details.append({
                    "professional_name": prof.get('name'),
                    "duration_hours": float(ps.get('duration_hours', 0)),
                    "price": float(ps.get('price', 0))
                })

        if not details:
            return _response(action_group, function_name,
                             f"Service '{service.get('name')}' is not currently offered by any professional.")

        data = {
            "service_name": service.get('name'),
            "description": service.get('description', ''),
            "category": service.get('category', 'General'),
            "professionals": details
        }
        return _response(action_group, function_name, f"Service details: {json.dumps(data, ensure_ascii=False)}")

    except Exception as e:
        logger.error(f"Error getting service details: {e}")
        return _response(action_group, function_name, f"Error: {str(e)}", failure=True)


def _response(action_group, function_name, body, failure=False):
    r = {"responseBody": {"TEXT": {"body": body}}}
    if failure:
        r["responseState"] = "FAILURE"
    return {
        "messageVersion": "1.0",
        "response": {"actionGroup": action_group, "function": function_name, "functionResponse": r}
    }
