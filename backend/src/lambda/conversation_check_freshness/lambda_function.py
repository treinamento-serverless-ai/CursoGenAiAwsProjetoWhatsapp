import os
import boto3
import time
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MESSAGE_BUFFER_TABLE'])
appconfig = boto3.client('appconfigdata')

MAX_RETRIES = 5

def get_appconfig():
    try:
        response = appconfig.start_configuration_session(
            ApplicationIdentifier=os.environ['APPCONFIG_APP_ID'],
            EnvironmentIdentifier=os.environ['APPCONFIG_ENV_ID'],
            ConfigurationProfileIdentifier=os.environ['APPCONFIG_PROFILE_ID']
        )
        config_token = response['InitialConfigurationToken']
        
        config_response = appconfig.get_latest_configuration(ConfigurationToken=config_token)
        config = json.loads(config_response['Configuration'].read())
        return config
    except Exception as e:
        logger.error(f"CRITICAL: Error reading AppConfig: {e}")
        return {
            'inactivity_threshold_seconds': 60,
            'audio_processing_grace_period': 15
        }

def lambda_handler(event, context):
    user_id = event['user_id']
    config = get_appconfig()
    
    WAIT_THRESHOLD_SECONDS = int(config.get('inactivity_threshold_seconds', 30))
    AUDIO_GRACE_PERIOD = int(config.get('audio_processing_grace_period', 15))
    
    response = table.get_item(Key={'phone_number': user_id})
    item = response.get('Item')
    
    if not item or 'messages' not in item:
        return {'should_wait': False, 'wait_seconds': 0, 'reason': 'No messages found'}
    
    messages = item['messages']
    if not messages:
        return {'should_wait': False, 'wait_seconds': 0, 'reason': 'Empty message set'}
    
    try:
        message_timestamps = [int(ts) for ts in messages.keys()]
    except ValueError:
        return {'should_wait': False, 'wait_seconds': 0, 'reason': 'Invalid timestamps'}
    
    latest_timestamp = max(message_timestamps)
    current_timestamp = int(time.time())
    elapsed_time = current_timestamp - latest_timestamp
    
    if elapsed_time < WAIT_THRESHOLD_SECONDS:
        remaining_wait = WAIT_THRESHOLD_SECONDS - elapsed_time
        return {
            'should_wait': True,
            'wait_seconds': remaining_wait,
            'reason': f'{remaining_wait}s remaining until threshold'
        }
    
    # Check pending audio transcriptions
    attempts = item.get('transcription_attempts', {})
    update_needed = False
    
    for timestamp, msg_data in messages.items():
        # Check if content is None (audio pending transcription)
        if isinstance(msg_data, dict) and msg_data.get('content') is None:
            current_attempt = attempts.get(timestamp, 0) + 1
            
            if current_attempt >= MAX_RETRIES:
                messages[timestamp]['content'] = "[ÁUDIO - TRANSCRIÇÃO FALHOU]"
                update_needed = True
            else:
                attempts[timestamp] = current_attempt
                update_needed = True
    
    if update_needed:
        table.update_item(
            Key={'phone_number': user_id},
            UpdateExpression="SET messages = :messages, transcription_attempts = :attempts",
            ExpressionAttributeValues={':messages': messages, ':attempts': attempts}
        )
    
    # Check if any audio is still pending
    has_pending = any(isinstance(v, dict) and v.get('content') is None for v in messages.values())
    
    if has_pending:
        return {
            'should_wait': True,
            'wait_seconds': AUDIO_GRACE_PERIOD,
            'reason': f'Audio processing. Waiting {AUDIO_GRACE_PERIOD}s'
        }
    
    return {'should_wait': False, 'wait_seconds': 0, 'reason': 'Ready to process'}
