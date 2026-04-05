import os
import json
import boto3
import logging
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_client = boto3.client(
    'bedrock-agent-runtime',
    config=Config(read_timeout=600, connect_timeout=10)
)

dynamodb = boto3.resource('dynamodb')
buffer_table = dynamodb.Table(os.environ['MESSAGE_BUFFER_TABLE'])

def lambda_handler(event, context):
    user_id = event['user_id']
    
    # Get messages from buffer
    response = buffer_table.get_item(Key={'phone_number': user_id})
    item = response.get('Item')
    
    if not item or 'messages' not in item:
        return {'status': 'no_messages', 'user_id': user_id}
    
    messages = item['messages']
    session_id = item.get('session_id', user_id)
    
    # Sort and concatenate messages
    sorted_timestamps = sorted([int(ts) for ts in messages.keys()])
    message_content = "\n".join([
        messages[str(ts)]['content']
        for ts in sorted_timestamps
        if messages[str(ts)].get('content')
    ])
    
    message_ids = [
        messages[str(ts)]['id']
        for ts in sorted_timestamps
        if messages[str(ts)].get('id')
    ]
    
    # Delete from buffer
    buffer_table.delete_item(Key={'phone_number': user_id})
    
    # Invoke Bedrock Agent
    agent_id = os.environ['BEDROCK_AGENT_ID']
    agent_alias_id = os.environ['BEDROCK_AGENT_ALIAS_ID']
    
    try:
        response = bedrock_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=message_content,
            sessionState={
                'promptSessionAttributes': {
                    'userId': user_id,
                    'timestamp': str(sorted_timestamps[0])
                }
            }
        )
        
        # Process stream
        completion = response.get('completion')
        full_response = ""
        
        for event in completion:
            if 'chunk' in event and 'bytes' in event['chunk']:
                full_response += event['chunk']['bytes'].decode('utf-8')
        
        logger.info(f"Agent response: {full_response}")
        
        return {
            'status': 'success',
            'user_id': user_id,
            'agent_response': full_response,
            'message_ids': message_ids,
            'session_id': session_id,
            'timestamp': str(sorted_timestamps[0])
        }
    
    except Exception as e:
        logger.error(f"Error invoking agent: {str(e)}")
        raise
