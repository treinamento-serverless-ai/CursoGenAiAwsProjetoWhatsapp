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
table = dynamodb.Table(os.environ["DYNAMODB_PROFESSIONALS_TABLE"])

def lambda_handler(event, context):
    try:
        method = event["httpMethod"]
        if method == "OPTIONS":
            return response(200, {})
        
        params = event.get("queryStringParameters") or {}
        professional_id = params.get("id")
        
        if method == "GET":
            return get_professionals(params) if not professional_id else get_professional(professional_id)
        elif method == "POST":
            return create_professional(json.loads(event.get("body", "{}")))
        elif method == "PUT":
            if not professional_id:
                return response(400, {"error": "id parameter required"})
            return update_professional(professional_id, json.loads(event.get("body", "{}")))
        elif method == "DELETE":
            if not professional_id:
                return response(400, {"error": "id parameter required"})
            return delete_professional(professional_id)
        
        return response(405, {"error": "Method not allowed"})
    except Exception as e:
        return response(500, {"error": str(e)})

def get_professionals(params):
    try:
        page_size = int(params.get("page_size", "25"))
        is_active = params.get("is_active")
        name_filter = params.get("name", "").lower()
        last_key = params.get("last_evaluated_key")
        
        query_args = {"Limit": page_size}
        if last_key:
            query_args["ExclusiveStartKey"] = json.loads(last_key)
        
        result = table.scan(**query_args)
        items = result.get("Items", [])
        
        if is_active is not None:
            items = [i for i in items if i.get("is_active") == (is_active == "1")]
        
        if name_filter:
            items = [i for i in items if name_filter in i.get("name", "").lower()]
        
        return response(200, {
            "items": items,
            "page_size": page_size,
            "last_evaluated_key": result.get("LastEvaluatedKey")
        })
    except Exception as e:
        return response(500, {"error": str(e)})

def get_professional(professional_id):
    try:
        result = table.get_item(Key={"professional_id": professional_id})
        if "Item" not in result:
            return response(404, {"error": "Professional not found"})
        return response(200, result["Item"])
    except Exception as e:
        return response(500, {"error": str(e)})

def create_professional(data):
    try:
        import uuid
        from datetime import datetime
        from decimal import Decimal
        
        required = ["name", "working_days", "working_hours", "services", "scheduling_policy"]
        if not all(k in data for k in required):
            return response(400, {"error": f"Required fields: {required}"})
        
        # Convert floats to Decimal for DynamoDB
        def convert_floats(obj):
            if isinstance(obj, dict):
                return {k: convert_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_floats(item) for item in obj]
            elif isinstance(obj, float):
                return Decimal(str(obj))
            return obj
        
        data = convert_floats(data)
        
        professional_id = str(uuid.uuid4())
        data["professional_id"] = professional_id
        data["is_active"] = data.get("is_active", True)
        data["created_at"] = datetime.utcnow().isoformat() + "Z"
        
        table.put_item(Item=data)
        return response(201, {"message": "Professional created", "professional_id": professional_id})
    except Exception as e:
        return response(500, {"error": str(e)})

def update_professional(professional_id, data):
    try:
        result = table.get_item(Key={"professional_id": professional_id})
        if "Item" not in result:
            return response(404, {"error": "Professional not found"})
        
        update_expr = "SET "
        expr_values = {}
        expr_names = {}
        updates = []
        
        for field in ["name", "specialty", "career_start_date", "social_media_link", "working_days", "working_hours", "services", "scheduling_policy", "is_active"]:
            if field in data:
                updates.append(f"#{field} = :{field}")
                expr_names[f"#{field}"] = field
                expr_values[f":{field}"] = data[field]
        
        if not updates:
            return response(400, {"error": "No fields to update"})
        
        update_expr += ", ".join(updates)
        table.update_item(
            Key={"professional_id": professional_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )
        return response(200, {"message": "Professional updated"})
    except Exception as e:
        return response(500, {"error": str(e)})

def delete_professional(professional_id):
    try:
        result = table.get_item(Key={"professional_id": professional_id})
        if "Item" not in result:
            return response(404, {"error": "Professional not found"})
        
        table.update_item(
            Key={"professional_id": professional_id},
            UpdateExpression="SET is_active = :is_active",
            ExpressionAttributeValues={":is_active": False}
        )
        return response(200, {"message": "Professional deactivated"})
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
