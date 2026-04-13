import json
import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TIMEZONE = ZoneInfo("America/Sao_Paulo")
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'amazon.nova-lite-v1:0')

bedrock_runtime = boto3.client('bedrock-runtime')


def resolve_with_bedrock(reference, now):
    """Usa Bedrock para interpretar qualquer referência temporal em linguagem natural."""
    today_str = now.strftime("%Y-%m-%d")
    weekday = now.strftime("%A")

    prompt = (
        f"Today is {weekday}, {today_str}. "
        f"The user said: \"{reference}\". "
        f"Return ONLY a JSON object with the resolved date(s). "
        f"If it's a single date: {{\"type\":\"single\",\"date\":\"YYYY-MM-DD\"}} "
        f"If it's a range: {{\"type\":\"range\",\"start_date\":\"YYYY-MM-DD\",\"end_date\":\"YYYY-MM-DD\"}} "
        f"Return ONLY the JSON, no explanation."
    )

    response = bedrock_runtime.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 100, "temperature": 0}
    )

    text = response['output']['message']['content'][0]['text'].strip()
    # Extrair JSON da resposta (pode vir com markdown)
    if '```' in text:
        text = text.split('```')[1].replace('json', '').strip()
    return json.loads(text)


def sanitize_param(value):
    if not isinstance(value, str):
        return value
    return value.replace('&quot;', '').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip('" ')


def convert_params_to_dict(params_list):
    return {param.get("name"): sanitize_param(param.get("value")) for param in params_list if param.get("name")}


def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = convert_params_to_dict(event.get('parameters', []))

    reference = parameters.get('reference')
    logger.info(f"[{context.aws_request_id}] ResolveDateReference called. reference={reference}")

    if not reference:
        return _response(action_group, function_name, "Error: reference parameter is required.")

    try:
        now = datetime.now(TIMEZONE)
        result = resolve_with_bedrock(reference, now)

        if result.get("type") == "single":
            date_obj = datetime.strptime(result["date"], "%Y-%m-%d")
            result["day_of_week"] = date_obj.strftime("%A")

        result["reference"] = reference
        return _response(action_group, function_name, json.dumps(result, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Error resolving date reference: {e}")
        return _response(action_group, function_name, f"Error resolving '{reference}': {str(e)}")


def _response(action_group, function_name, body):
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "function": function_name,
            "functionResponse": {
                "responseBody": {"TEXT": {"body": body}}
            }
        }
    }
