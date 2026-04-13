import json
import os
import uuid
import boto3
import decimal
from datetime import datetime
from boto3.dynamodb.conditions import Key

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMODB_APPOINTMENTS_TABLE"])

def lambda_handler(event, context):
    try:
        method = event["httpMethod"]
        if method == "OPTIONS":
            return response(200, {})
        
        params = event.get("queryStringParameters") or {}
        appointment_id = params.get("id")
        
        if method == "GET":
            return get_appointments(params) if not appointment_id else get_appointment(appointment_id)
        elif method == "POST":
            return create_appointment(json.loads(event.get("body", "{}")))
        elif method == "PUT":
            if not appointment_id:
                return response(400, {"error": "id parameter required"})
            return update_appointment(appointment_id, json.loads(event.get("body", "{}")))
        elif method == "DELETE":
            if not appointment_id:
                return response(400, {"error": "id parameter required"})
            return delete_appointment(appointment_id)
        
        return response(405, {"error": "Method not allowed"})
    except Exception as e:
        return response(500, {"error": str(e)})

def get_appointments(params):
    try:
        page_size = int(params.get("page_size", "25"))
        professional_id = params.get("professional_id")
        client_phone = params.get("client_phone")
        date_from = params.get("date_from")
        status = params.get("status")
        last_key = params.get("last_evaluated_key")
        
        query_args = {"Limit": page_size}
        if last_key:
            query_args["ExclusiveStartKey"] = json.loads(last_key)
        
        if professional_id:
            query_args["IndexName"] = "professional_id-appointment_date-index"
            query_args["KeyConditionExpression"] = Key("professional_id").eq(professional_id)
            if date_from:
                query_args["KeyConditionExpression"] &= Key("appointment_date").gte(date_from)
            result = table.query(**query_args)
        elif client_phone:
            query_args["IndexName"] = "client_phone-appointment_date-index"
            query_args["KeyConditionExpression"] = Key("client_phone").eq(client_phone)
            if date_from:
                query_args["KeyConditionExpression"] &= Key("appointment_date").gte(date_from)
            result = table.query(**query_args)
        else:
            result = table.scan(**query_args)
        
        items = result.get("Items", [])
        if status:
            items = [i for i in items if i.get("status") == status]
        
        return response(200, {
            "items": items,
            "page_size": page_size,
            "last_evaluated_key": result.get("LastEvaluatedKey")
        })
    except Exception as e:
        return response(500, {"error": str(e)})

def get_appointment(appointment_id):
    try:
        result = table.query(KeyConditionExpression=Key("appointment_id").eq(appointment_id))
        items = result.get("Items", [])
        if not items:
            return response(404, {"error": "Appointment not found"})
        return response(200, items[0])
    except Exception as e:
        return response(500, {"error": str(e)})

def create_appointment(data):
    try:
        required = ["appointment_date", "client_phone", "professional_id", "service_id"]
        if not all(k in data for k in required):
            return response(400, {"error": f"Required fields: {required}"})
        
        if "appointment_id" not in data:
            data["appointment_id"] = str(uuid.uuid4())
        
        data["created_at"] = datetime.utcnow().isoformat() + "Z"
        data["status"] = data.get("status", "scheduled")
        table.put_item(Item=data)
        return response(201, {"message": "Appointment created", "appointment_id": data["appointment_id"]})
    except Exception as e:
        return response(500, {"error": str(e)})

def update_appointment(appointment_id, data):
    try:
        result = table.query(KeyConditionExpression=Key("appointment_id").eq(appointment_id))
        items = result.get("Items", [])
        if not items:
            return response(404, {"error": "Appointment not found"})
        
        item = items[0]
        update_expr = "SET updated_at = :updated_at"
        expr_values = {":updated_at": datetime.utcnow().isoformat() + "Z"}
        expr_names = {}
        
        for field in ["status", "scheduled_time", "professional_id", "service_id"]:
            if field in data:
                if field == "status":
                    update_expr += ", #status = :status"
                    expr_names["#status"] = "status"
                    expr_values[":status"] = data[field]
                else:
                    update_expr += f", {field} = :{field}"
                    expr_values[f":{field}"] = data[field]
        
        update_params = {
            "Key": {"appointment_id": appointment_id, "appointment_date": item["appointment_date"]},
            "UpdateExpression": update_expr,
            "ExpressionAttributeValues": expr_values
        }
        if expr_names:
            update_params["ExpressionAttributeNames"] = expr_names
        
        table.update_item(**update_params)
        return response(200, {"message": "Appointment updated"})
    except Exception as e:
        return response(500, {"error": str(e)})

def delete_appointment(appointment_id):
    try:
        result = table.query(KeyConditionExpression=Key("appointment_id").eq(appointment_id))
        items = result.get("Items", [])
        if not items:
            return response(404, {"error": "Appointment not found"})
        
        item = items[0]
        table.update_item(
            Key={"appointment_id": appointment_id, "appointment_date": item["appointment_date"]},
            UpdateExpression="SET #status = :status, updated_at = :updated_at",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": "cancelled",
                ":updated_at": datetime.utcnow().isoformat() + "Z"
            }
        )
        return response(200, {"message": "Appointment cancelled"})
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
