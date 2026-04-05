import os
import json
import boto3
import logging
import urllib3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

secrets_client = boto3.client('secretsmanager')
http = urllib3.PoolManager()

def get_secret():
    secret_arn = os.environ.get('SECRET_ARN')
    response = secrets_client.get_secret_value(SecretId=secret_arn)
    return json.loads(response['SecretString'])

def send_whatsapp_message(to_number, message_body, access_token, phone_number_id, api_version):
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_body}
    }
    
    try:
        response = http.request("POST", url, body=json.dumps(payload), headers=headers)
        logger.info(f"Sent to {to_number}. Status: {response.status}")
        return response.status == 200
    except Exception as e:
        logger.error(f"Failed to send: {str(e)}")
        raise

def mark_messages_as_read(message_ids, access_token, phone_number_id, api_version):
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    for message_id in message_ids:
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        try:
            http.request("POST", url, body=json.dumps(payload), headers=headers)
            logger.info(f"Marked {message_id} as read")
        except Exception as e:
            logger.error(f"Failed to mark as read: {str(e)}")

def lambda_handler(event, context):
    user_id = event['user_id']
    agent_response = event['agent_response']
    message_ids = event.get('message_ids', [])
    
    secret = get_secret()
    access_token = secret['ACCESS_TOKEN']
    phone_number_id = secret['PHONE_NUMBER_ID']
    api_version = secret.get('API_VERSION', 'v22.0')
    
    # Mark messages as read
    if message_ids:
        mark_messages_as_read(message_ids, access_token, phone_number_id, api_version)
    
    # Send response
    success = send_whatsapp_message(user_id, agent_response, access_token, phone_number_id, api_version)
    
    return {
        'status': 'success' if success else 'failed',
        'user_id': user_id,
        'message_length': len(agent_response)
    }
