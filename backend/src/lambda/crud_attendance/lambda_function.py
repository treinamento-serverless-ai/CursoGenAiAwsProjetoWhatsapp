import json
import os
import time
import boto3
import decimal
import logging
import urllib3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)

dynamodb = boto3.resource("dynamodb")
clients_table = dynamodb.Table(os.environ["DYNAMODB_CLIENTS_TABLE"])
history_table = dynamodb.Table(os.environ["DYNAMODB_CONVERSATION_HISTORY_TABLE"])
secrets_client = boto3.client("secretsmanager")
http = urllib3.PoolManager()


s3_client = boto3.client("s3")


def get_secret():
    response = secrets_client.get_secret_value(SecretId=os.environ["SECRET_ARN"])
    return json.loads(response["SecretString"])


def lambda_handler(event, context):
    try:
        method = event["httpMethod"]
        path = event.get("path", "")

        if method == "OPTIONS":
            return response(200, {})

        if method == "GET" and path.endswith("/attendance"):
            return get_open_attendances(event)
        elif method == "POST" and path.endswith("/attendance/message"):
            claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
            sender_email = claims.get("email", "")
            return send_human_message(json.loads(event.get("body", "{}")), sender_email)
        elif method == "POST" and path.endswith("/attendance/close"):
            return close_attendance(json.loads(event.get("body", "{}")))

        return response(405, {"error": "Method not allowed"})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return response(500, {"error": str(e)})


def get_open_attendances(event):
    """List clients with ai_enabled=false (waiting for human attendance)."""
    params = event.get("queryStringParameters") or {}
    page_size = int(params.get("page_size", "25"))

    result = clients_table.scan()
    items = result.get("Items", [])

    attendances = []
    for client in items:
        phone = client["phone_number"]
        # Get last message
        hist = history_table.query(
            KeyConditionExpression=Key("phone_number").eq(phone),
            Limit=1,
            ScanIndexForward=False,
        )
        hist_items = hist.get("Items", [])
        last_msg = hist_items[0] if hist_items else None

        if not last_msg:
            continue

        attendances.append({
            "phone_number": phone,
            "name": client.get("name"),
            "last_message": last_msg.get("content") if last_msg else None,
            "last_message_at": last_msg.get("timestamp", 0) if last_msg else client.get("last_message_at", 0),
            "session_id": client.get("session_id", ""),
            "ai_enabled": client.get("ai_enabled", True),
        })

    attendances.sort(key=lambda x: x["last_message_at"], reverse=True)
    return response(200, {"items": attendances[:page_size], "page_size": page_size})


def send_human_message(body, sender_email=""):
    """Send a message as human attendant via WhatsApp and save to history."""
    phone_number = body.get("phone_number")
    content = body.get("content")
    if not phone_number or not content:
        return response(400, {"error": "phone_number and content required"})

    # Send via WhatsApp
    secret = get_secret()
    url = f"https://graph.facebook.com/{secret.get('API_VERSION', 'v22.0')}/{secret['PHONE_NUMBER_ID']}/messages"
    headers = {"Authorization": f"Bearer {secret['ACCESS_TOKEN']}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": phone_number, "type": "text", "text": {"body": content}}

    resp = http.request("POST", url, body=json.dumps(payload), headers=headers)
    if resp.status != 200:
        logger.error(f"WhatsApp send failed: {resp.status} {resp.data.decode()}")
        return response(502, {"error": "Failed to send WhatsApp message"})

    # Save to conversation history
    now = int(time.time())
    item = {
        "phone_number": phone_number,
        "timestamp": now,
        "sender": "human",
        "content": content,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
    }
    if sender_email:
        item["sender_email"] = sender_email
    history_table.put_item(Item=item)

    return response(200, {"message": "Message sent"})


def close_attendance(body):
    """Close attendance: archive conversation to S3, delete from DynamoDB, re-enable AI."""
    phone_number = body.get("phone_number")
    if not phone_number:
        return response(400, {"error": "phone_number required"})

    # 1. Fetch all messages
    messages = []
    kwargs = {"KeyConditionExpression": Key("phone_number").eq(phone_number)}
    while True:
        result = history_table.query(**kwargs)
        messages.extend(result.get("Items", []))
        if "LastEvaluatedKey" not in result:
            break
        kwargs["ExclusiveStartKey"] = result["LastEvaluatedKey"]

    # 2. Archive to S3 (Hive-style partitioning for Athena)
    if messages:
        messages.sort(key=lambda m: m.get("timestamp", 0))
        now = time.gmtime()
        archive_key = (
            f"year={now.tm_year:04d}/month={now.tm_mon:02d}/day={now.tm_mday:02d}"
            f"/hour={now.tm_hour:02d}/{phone_number}_{time.strftime('%Y-%m-%dT%H:%M:%SZ', now)}.json"
        )
        s3_client.put_object(
            Bucket=os.environ["S3_ARCHIVE_BUCKET"],
            Key=archive_key,
            Body=json.dumps(messages, cls=DecimalEncoder, default=str, ensure_ascii=False),
            ContentType="application/json",
        )

        # 3. Delete messages from DynamoDB
        with history_table.batch_writer() as batch:
            for msg in messages:
                batch.delete_item(Key={"phone_number": msg["phone_number"], "timestamp": msg["timestamp"]})

    return response(200, {"message": "Attendance closed and archived", "archived_count": len(messages)})


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Api-Key",
        },
        "body": json.dumps(body, cls=DecimalEncoder, default=str),
    }
