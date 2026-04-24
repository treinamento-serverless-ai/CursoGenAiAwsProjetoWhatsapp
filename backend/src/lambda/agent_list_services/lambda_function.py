import json
import logging
import os

import boto3
from difflib import SequenceMatcher

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
services_table = dynamodb.Table(os.environ['DYNAMODB_SERVICES_TABLE'])


def matches_tags(search_term, tags):
    term = search_term.lower()
    return any(term in tag.lower() or tag.lower() in term for tag in tags)


def fuzzy_match(search_term, text, threshold=0.5):
    search_lower = search_term.lower()
    text_lower = text.lower()
    if search_lower in text_lower or text_lower in search_lower:
        return True
    return SequenceMatcher(None, search_lower, text_lower).ratio() >= threshold


def filter_services(services, search_term):
    # Priority: tags (exact/contains) → name (fuzzy) → description (fuzzy)
    by_tags = [s for s in services if matches_tags(search_term, s.get('tags', []))]
    if by_tags:
        return by_tags
    by_name = [s for s in services if fuzzy_match(search_term, s.get('name', ''))]
    if by_name:
        return by_name
    return [s for s in services if fuzzy_match(search_term, s.get('description', ''))]


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    params = {p.get("name"): p.get("value", "").replace('&quot;', '').strip('" ') for p in event.get('parameters', []) if p.get("name")}
    search_term = params.get('search_term')

    logger.info(f"[{context.aws_request_id}] ListServices called. search_term={search_term}")

    try:
        response = services_table.scan(
            FilterExpression='is_active = :val',
            ExpressionAttributeValues={':val': True}
        )
        services = response.get('Items', [])

        if not services:
            return _response(action_group, function_name, "No services available at the moment.")

        if search_term:
            services = filter_services(services, search_term)
            if not services:
                return _response(action_group, function_name,
                                 f"No services found matching '{search_term}'. Try listing all services without filters.")

        summary = [
            {
                "name": s.get('name'),
                "description": s.get('description') or 'Sem descrição disponível',
                "category": s.get('category', 'General')
            }
            for s in services
        ]

        return _response(action_group, function_name,
                         f"Available services: {json.dumps(summary, ensure_ascii=False)}")

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
