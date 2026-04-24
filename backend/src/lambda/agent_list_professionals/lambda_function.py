import json
import logging
import os
from datetime import datetime
from difflib import SequenceMatcher

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


def sanitize_param(value):
    if not isinstance(value, str):
        return value
    return value.replace('&quot;', '').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip('" ')


def matches_tags(search_term, tags):
    term = search_term.lower()
    return any(term in tag.lower() or tag.lower() in term for tag in tags)


def fuzzy_match(search_term, text, threshold=0.5):
    search_lower = search_term.lower()
    text_lower = text.lower()
    if search_lower in text_lower or text_lower in search_lower:
        return True
    return SequenceMatcher(None, search_lower, text_lower).ratio() >= threshold


def filter_by_specialty(professionals, specialty):
    by_tags = [p for p in professionals if matches_tags(specialty, p.get('tags', []))]
    if by_tags:
        return by_tags
    return [p for p in professionals if fuzzy_match(specialty, p.get('specialty', ''))]


def filter_by_service(professionals, service_name):
    by_tags = [p for p in professionals if matches_tags(service_name, p.get('tags', []))]
    if by_tags:
        return by_tags
    filtered = []
    for prof in professionals:
        for svc in prof.get('services', []):
            if fuzzy_match(service_name, svc.get('service_name', '')):
                filtered.append(prof)
                break
    return filtered


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = {p.get("name"): p.get("value") for p in event.get('parameters', []) if p.get("name")}

    specialty = sanitize_param(parameters.get('specialty'))
    service_name = sanitize_param(parameters.get('service_name'))

    logger.info(f"[{context.aws_request_id}] ListProfessionals called. specialty={specialty}, service_name={service_name}")

    try:
        response = professionals_table.scan(
            FilterExpression='is_active = :val',
            ExpressionAttributeValues={':val': True}
        )
        professionals = response.get('Items', [])

        if not professionals:
            return _response(action_group, function_name, "No professionals available at the moment.")

        if specialty:
            professionals = filter_by_specialty(professionals, specialty)
        if service_name:
            professionals = filter_by_service(professionals, service_name)

        if not professionals:
            filter_desc = specialty or service_name
            return _response(action_group, function_name,
                             f"No professionals found matching '{filter_desc}'. "
                             f"Try listing all professionals without filters to see available options.")

        summary = [
            {
                "name": prof.get('name'),
                "specialty": prof.get('specialty', 'General'),
                "services": [svc.get('service_name') for svc in prof.get('services', [])],
                "years_experience": calculate_years_experience(prof.get('career_start_date')) or "Not specified",
            }
            for prof in professionals
        ]

        filter_info = ""
        if specialty or service_name:
            filter_info = f" matching '{specialty or service_name}'"

        return _response(action_group, function_name,
                         f"Found {len(summary)} professional(s){filter_info}: {json.dumps(summary, ensure_ascii=False)}")

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
