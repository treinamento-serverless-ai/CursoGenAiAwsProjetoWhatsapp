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
table = dynamodb.Table(os.environ["DYNAMODB_CLIENTS_TABLE"])

def lambda_handler(event, context):
    try:
        method = event["httpMethod"]
        if method == "OPTIONS":
            return response(200, {})
        
        params = event.get("queryStringParameters") or {}
        phone_number = params.get("phone_number")
        
        if method == "GET":
            return get_clients(params) if not phone_number else get_client(phone_number)
        elif method == "PUT":
            if not phone_number:
                return response(400, {"error": "phone_number parameter required"})
            return update_client(phone_number, json.loads(event.get("body", "{}")))
        
        return response(405, {"error": "Method not allowed"})
    except Exception as e:
        return response(500, {"error": str(e)})

def get_clients(params):
    try:
        page_size = int(params.get("page_size", "25"))
        is_banned = params.get("is_banned")
        ai_enabled = params.get("ai_enabled")
        last_key = params.get("last_evaluated_key")
        
        query_args = {"Limit": page_size}
        if last_key:
            query_args["ExclusiveStartKey"] = json.loads(last_key)
        
        result = table.scan(**query_args)
        items = result.get("Items", [])
        
        if is_banned is not None:
            items = [i for i in items if i.get("is_banned") == (is_banned == "1")]
        if ai_enabled is not None:
            items = [i for i in items if i.get("ai_enabled") == (ai_enabled == "1")]
        
        return response(200, {
            "items": items,
            "page_size": page_size,
            "last_evaluated_key": result.get("LastEvaluatedKey")
        })
    except Exception as e:
        return response(500, {"error": str(e)})

def get_client(phone_number):
    try:
        result = table.get_item(Key={"phone_number": phone_number})
        if "Item" not in result:
            return response(404, {"error": "Client not found"})
        return response(200, result["Item"])
    except Exception as e:
        return response(500, {"error": str(e)})

def update_client(phone_number, data):
    try:
        result = table.get_item(Key={"phone_number": phone_number})
        if "Item" not in result:
            return response(404, {"error": "Client not found"})
        
        update_expr = "SET "
        expr_values = {}
        expr_names = {}
        updates = []
        
        for field in ["ai_enabled", "is_banned", "name", "email"]:
            if field in data:
                updates.append(f"#{field} = :{field}")
                expr_names[f"#{field}"] = field
                expr_values[f":{field}"] = data[field]
        
        if not updates:
            return response(400, {"error": "No fields to update"})
        
        update_expr += ", ".join(updates)
        table.update_item(
            Key={"phone_number": phone_number},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )
        return response(200, {"message": "Client updated"})
    except Exception as e:
        return response(500, {"error": str(e)})

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Api-Key"
        },
        "body": json.dumps(body, cls=DecimalEncoder, default=str)
    }
