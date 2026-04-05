import json
import os
import boto3
import decimal
from boto3.dynamodb.conditions import Key

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMODB_CONVERSATION_HISTORY_TABLE"])

def lambda_handler(event, context):
    try:
        method = event["httpMethod"]
        if method == "OPTIONS":
            return response(200, {})
        
        if method != "GET":
            return response(405, {"error": "Method not allowed"})
        
        params = event.get("queryStringParameters") or {}
        phone_number = params.get("phone_number")
        
        if not phone_number:
            return response(400, {"error": "phone_number parameter required"})
        
        return get_conversations(phone_number, params)
    except Exception as e:
        return response(500, {"error": str(e)})

def get_conversations(phone_number, params):
    try:
        limit = int(params.get("limit", "50"))
        date_from = params.get("date_from")
        last_key = params.get("last_evaluated_key")
        
        query_args = {
            "KeyConditionExpression": Key("phone_number").eq(phone_number),
            "Limit": limit,
            "ScanIndexForward": False
        }
        
        if date_from:
            timestamp_from = int(date_from)
            query_args["KeyConditionExpression"] &= Key("timestamp").gte(timestamp_from)
        
        if last_key:
            query_args["ExclusiveStartKey"] = json.loads(last_key)
        
        result = table.query(**query_args)
        
        return response(200, {
            "items": result.get("Items", []),
            "limit": limit,
            "last_evaluated_key": result.get("LastEvaluatedKey")
        })
    except Exception as e:
        return response(500, {"error": str(e)})

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Api-Key"
        },
        "body": json.dumps(body, cls=DecimalEncoder, default=str)
    }
