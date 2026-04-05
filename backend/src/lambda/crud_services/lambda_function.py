import json
import os
import boto3
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMODB_SERVICES_TABLE"])

def lambda_handler(event, context):
    try:
        method = event["httpMethod"]
        if method == "OPTIONS":
            return response(200, {})
        
        params = event.get("queryStringParameters") or {}
        service_id = params.get("id")
        
        if method == "GET":
            return get_services(params) if not service_id else get_service(service_id)
        elif method == "POST":
            return create_service(json.loads(event.get("body", "{}")))
        elif method == "PUT":
            if not service_id:
                return response(400, {"error": "id parameter required"})
            return update_service(service_id, json.loads(event.get("body", "{}")))
        elif method == "DELETE":
            if not service_id:
                return response(400, {"error": "id parameter required"})
            return delete_service(service_id)
        
        return response(405, {"error": "Method not allowed"})
    except Exception as e:
        return response(500, {"error": str(e)})

def get_services(params):
    try:
        page_size = int(params.get("page_size", "25"))
        is_active = params.get("is_active")
        category = params.get("category")
        last_key = params.get("last_evaluated_key")
        
        query_args = {"Limit": page_size}
        if last_key:
            query_args["ExclusiveStartKey"] = json.loads(last_key)
        
        result = table.scan(**query_args)
        items = result.get("Items", [])
        
        if is_active is not None:
            items = [i for i in items if i.get("is_active") == (is_active == "1")]
        if category:
            items = [i for i in items if i.get("category") == category]
        
        return response(200, {
            "items": items,
            "page_size": page_size,
            "last_evaluated_key": result.get("LastEvaluatedKey")
        })
    except Exception as e:
        return response(500, {"error": str(e)})

def get_service(service_id):
    try:
        result = table.get_item(Key={"service_id": service_id})
        if "Item" not in result:
            return response(404, {"error": "Service not found"})
        return response(200, result["Item"])
    except Exception as e:
        return response(500, {"error": str(e)})

def create_service(data):
    try:
        required = ["service_id", "name"]
        if not all(k in data for k in required):
            return response(400, {"error": f"Required fields: {required}"})
        
        data["is_active"] = data.get("is_active", True)
        table.put_item(Item=data)
        return response(201, {"message": "Service created", "service_id": data["service_id"]})
    except Exception as e:
        return response(500, {"error": str(e)})

def update_service(service_id, data):
    try:
        result = table.get_item(Key={"service_id": service_id})
        if "Item" not in result:
            return response(404, {"error": "Service not found"})
        
        update_expr = "SET "
        expr_values = {}
        expr_names = {}
        updates = []
        
        for field in ["name", "description", "category", "is_active"]:
            if field in data:
                updates.append(f"#{field} = :{field}")
                expr_names[f"#{field}"] = field
                expr_values[f":{field}"] = data[field]
        
        if not updates:
            return response(400, {"error": "No fields to update"})
        
        update_expr += ", ".join(updates)
        table.update_item(
            Key={"service_id": service_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )
        return response(200, {"message": "Service updated"})
    except Exception as e:
        return response(500, {"error": str(e)})

def delete_service(service_id):
    try:
        result = table.get_item(Key={"service_id": service_id})
        if "Item" not in result:
            return response(404, {"error": "Service not found"})
        
        table.update_item(
            Key={"service_id": service_id},
            UpdateExpression="SET is_active = :is_active",
            ExpressionAttributeValues={":is_active": False}
        )
        return response(200, {"message": "Service deactivated"})
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
