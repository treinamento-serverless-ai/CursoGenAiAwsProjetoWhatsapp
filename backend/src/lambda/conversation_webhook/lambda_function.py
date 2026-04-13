import json
import logging
import os
import time
import uuid
import urllib3
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger()
logger.setLevel(logging.INFO)

secrets_client = boto3.client('secretsmanager')
ssm_client = boto3.client('ssm')
dynamodb = boto3.resource('dynamodb')
sfn_client = boto3.client('stepfunctions')
appconfig = boto3.client('appconfigdata')
lambda_client = boto3.client('lambda')

buffer_table = dynamodb.Table(os.environ['MESSAGE_BUFFER_TABLE'])
clients_table = dynamodb.Table(os.environ['CLIENTS_TABLE'])
history_table = dynamodb.Table(os.environ['CONVERSATION_HISTORY_TABLE'])

_step_function_arn = None
_config_cache = None
_config_cache_time = 0

def get_appconfig():
    global _config_cache, _config_cache_time
    if _config_cache and (time.time() - _config_cache_time < 300):
        return _config_cache
    
    try:
        response = appconfig.start_configuration_session(
            ApplicationIdentifier=os.environ['APPCONFIG_APP_ID'],
            EnvironmentIdentifier=os.environ['APPCONFIG_ENV_ID'],
            ConfigurationProfileIdentifier=os.environ['APPCONFIG_PROFILE_ID']
        )
        config_token = response['InitialConfigurationToken']
        config_response = appconfig.get_latest_configuration(ConfigurationToken=config_token)
        _config_cache = json.loads(config_response['Configuration'].read())
        _config_cache_time = time.time()
        return _config_cache
    except Exception as e:
        logger.error(f"CRITICAL: Error reading AppConfig: {e}")
        if _config_cache:
            logger.warning("Using stale AppConfig cache as fallback")
            _config_cache_time = time.time()
            return _config_cache
        return {
            'business_hours_start': '00:00',
            'business_hours_end': '23:59',
            'business_hours_timezone': 'America/Sao_Paulo',
            'inactivity_threshold_seconds': 60,
            'audio_processing_grace_period': 15,
            'closed_message': 'Olá! Nosso horário de atendimento é das __HORARIO_INICIO__ às __HORARIO_FIM__. Por favor, retorne durante o horário de funcionamento.',
            'banned_message': 'Desculpe, não conseguimos processar sua mensagem no momento. Por favor, entre em contato via telefone para atendimento.',
            'transcribe_enabled': False,
            'transcribe_disabled_message': 'Desculpe, não consigo processar mensagens de áudio no momento. Por favor, envie sua mensagem em texto.',
            'audio_min_size_kb': 10,
            'audio_max_size_kb': 275,
            'ai_error_message': 'Desculpe, estou com dificuldades técnicas no momento. Um atendente humano entrará em contato em breve.',
            'save_messages_after_hours': True,
            'reply_with_context': True,
            'reply_context_use_last': True
        }

def is_business_hours(config):
    try:
        tz = ZoneInfo(config.get('business_hours_timezone', 'America/Sao_Paulo'))
        now = datetime.now(tz)
        
        start_hour, start_min = map(int, config.get('business_hours_start', '08:00').split(':'))
        end_hour, end_min = map(int, config.get('business_hours_end', '00:00').split(':'))
        
        start_time = now.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
        end_time = now.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
        
        # Handle overnight hours (e.g., 22:00 to 02:00 crosses midnight)
        if end_time <= start_time:
            # Overnight shift: check if now is after start OR before end
            # Example: 22:00-02:00 means 22:00-23:59 OR 00:00-02:00
            return now >= start_time or now <= end_time
        else:
            # Normal shift: check if now is between start and end
            return start_time <= now <= end_time
    except Exception as e:
        logger.warning(f"Error checking business hours: {e}")
        return True  # Default: allow messages

def get_step_function_arn():
    global _step_function_arn
    if _step_function_arn is None:
        parameter_name = f"/{os.environ['PROJECT_NAME']}/{os.environ['ENVIRONMENT']}/stepfunctions/message_orchestrator_arn"
        response = ssm_client.get_parameter(Name=parameter_name)
        _step_function_arn = response['Parameter']['Value']
    return _step_function_arn

def get_secret():
    secret_arn = os.environ.get('SECRET_ARN')
    response = secrets_client.get_secret_value(SecretId=secret_arn)
    return json.loads(response['SecretString'])

def send_unavailable_message(user_id, message):
    try:
        logger.info(f"Preparing to send unavailable message to {user_id}")
        secret = get_secret()
        
        http = urllib3.PoolManager()
        url = f"https://graph.facebook.com/{secret['API_VERSION']}/{secret['PHONE_NUMBER_ID']}/messages"
        payload = json.dumps({'messaging_product': 'whatsapp', 'to': user_id, 'text': {'body': message}})
        
        logger.info(f"Sending POST to {url}")
        response = http.request(
            'POST',
            url,
            body=payload,
            headers={
                'Authorization': f"Bearer {secret['ACCESS_TOKEN']}",
                'Content-Type': 'application/json'
            },
            timeout=10.0
        )
        
        logger.info(f"Meta API response status: {response.status}")
        logger.info(f"Meta API response body: {response.data.decode('utf-8')}")
        
        if response.status != 200:
            logger.warning(f"Meta API returned non-200 status: {response.status}")
        else:
            logger.info(f"Sent unavailable message to {user_id}")
    except Exception as e:
        logger.warning(f"Failed to send unavailable message: {e}")

def send_reply_message(user_id, reply_to_message_id, message, config):
    try:
        secret = get_secret()
        
        http = urllib3.PoolManager()
        url = f"https://graph.facebook.com/{secret['API_VERSION']}/{secret['PHONE_NUMBER_ID']}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': user_id,
            'text': {'body': message}
        }
        
        if config.get('reply_with_context', True):
            payload['context'] = {'message_id': reply_to_message_id}
        
        response = http.request(
            'POST',
            url,
            body=json.dumps(payload),
            headers={
                'Authorization': f"Bearer {secret['ACCESS_TOKEN']}",
                'Content-Type': 'application/json'
            },
            timeout=10.0
        )
        
        logger.info(f"Sent reply to {user_id}: status {response.status}")
    except Exception as e:
        logger.warning(f"Failed to send reply: {e}")

def invoke_transcription_lambda(message):
    try:
        lambda_client.invoke(
            FunctionName=os.environ['TRANSCRIPTION_LAMBDA_NAME'],
            InvocationType='Event',
            Payload=json.dumps(message)
        )
        logger.info(f"Invoked transcription lambda for audio message")
    except Exception as e:
        logger.error(f"Failed to invoke transcription lambda: {e}")

def lambda_handler(event, context):
    logger.info(f"Event: {json.dumps(event)}")
    
    http_method = event.get('httpMethod', '')
    
    if http_method == 'GET':
        return handle_verification(event)
    elif http_method == 'POST':
        body = json.loads(event.get('body', '{}'))
        return handle_incoming_message(body)
    else:
        return {'statusCode': 405, 'body': json.dumps({'error': f'Method {http_method} not allowed'})}

def handle_verification(event):
    params = event.get('queryStringParameters') or {}
    mode = params.get('hub.mode')
    token = params.get('hub.verify_token')
    challenge = params.get('hub.challenge')
    
    secret = get_secret()
    verify_token = secret.get('VERIFY_TOKEN', '')
    
    if mode == 'subscribe' and token == verify_token:
        logger.info("Webhook verified successfully")
        return {'statusCode': 200, 'body': challenge}
    else:
        logger.warning("Webhook verification failed")
        return {'statusCode': 403, 'body': json.dumps({'error': 'Verification failed'})}

def handle_incoming_message(body):
    try:
        config = get_appconfig()
        messages = body.get('entry', [])[0].get('changes', [])[0].get('value', {}).get('messages', [])
        contacts = body.get('entry', [])[0].get('changes', [])[0].get('value', {}).get('contacts', [])
        
        if not messages:
            logger.info("No messages in webhook")
            return {'statusCode': 200, 'body': json.dumps({'message': 'No messages'})}
        
        contact_map = {c.get('wa_id'): c.get('profile', {}).get('name', '') for c in contacts}
        
        for message in messages:
            user_id = message.get('from')
            message_id = message.get('id')
            timestamp = int(message.get('timestamp', time.time()))
            
            message_type = message.get('type')
            
            if message_type == 'text':
                content = message.get('text', {}).get('body', '')
            elif message_type == 'audio':
                transcribe_enabled = config.get('transcribe_enabled', True)
                
                # Convert to boolean if string
                if isinstance(transcribe_enabled, str):
                    transcribe_enabled = transcribe_enabled.lower() in ('true', '1', 'yes')
                
                if not transcribe_enabled:
                    # Transcribe disabled - send error message with reply
                    transcribe_disabled_msg = config.get('transcribe_disabled_message', 'Não consigo processar áudios.')
                    if config.get('reply_with_context', True):
                        send_reply_message(user_id, message_id, transcribe_disabled_msg, config)
                    else:
                        send_unavailable_message(user_id, transcribe_disabled_msg)
                    save_message_to_history(user_id, message_id, timestamp, None, 'user')
                    save_message_to_history(user_id, '', int(time.time()), transcribe_disabled_msg, 'auto')
                    continue
                
                content = None  # Will be processed by transcription lambda
                invoke_transcription_lambda(message)
            else:
                logger.info(f"Unsupported message type: {message_type}")
                continue
            
            # Get or create client
            client_info = get_or_create_client(user_id, contact_map.get(user_id, ''))
            
            # Check if user is banned
            if client_info.get('is_banned', False):
                today = datetime.now(ZoneInfo(config.get('business_hours_timezone', 'America/Sao_Paulo'))).date().isoformat()
                last_unavailable_date = client_info.get('last_unavailable_message_date', '')
                
                save_message_to_history(user_id, message_id, timestamp, content, 'user')
                if last_unavailable_date != today:
                    message_text = config.get('banned_message', 'Serviço indisponível.')
                    send_unavailable_message(user_id, message_text)
                    save_message_to_history(user_id, '', int(time.time()), message_text, 'auto')
                    clients_table.update_item(
                        Key={'phone_number': user_id},
                        UpdateExpression='SET last_unavailable_message_date = :date',
                        ExpressionAttributeValues={':date': today}
                    )
                logger.info(f"User {user_id} is banned, message ignored")
                continue
            
            # Check business hours
            if not is_business_hours(config):
                today = datetime.now(ZoneInfo(config.get('business_hours_timezone', 'America/Sao_Paulo'))).date().isoformat()
                last_unavailable_date = client_info.get('last_unavailable_message_date', '')
                
                # Save message if configured
                if config.get('save_messages_after_hours', True):
                    save_message_to_history(user_id, message_id, timestamp, content, 'user')
                
                # Send closed message only once per day
                if last_unavailable_date != today:
                    message_text = config.get('closed_message', 'Horário encerrado.')
                    message_text = message_text.replace('__HORARIO_INICIO__', config.get('business_hours_start', '08:00'))
                    message_text = message_text.replace('__HORARIO_FIM__', config.get('business_hours_end', '00:00'))
                    send_unavailable_message(user_id, message_text)
                    save_message_to_history(user_id, '', int(time.time()), message_text, 'auto')
                    clients_table.update_item(
                        Key={'phone_number': user_id},
                        UpdateExpression='SET last_unavailable_message_date = :date',
                        ExpressionAttributeValues={':date': today}
                    )
                continue
            
            # Check if AI is enabled
            if not client_info.get('ai_enabled', True):
                today = datetime.now(ZoneInfo(config.get('business_hours_timezone', 'America/Sao_Paulo'))).date().isoformat()
                last_unavailable_date = client_info.get('last_unavailable_message_date', '')
                
                # Save message to history
                save_message_to_history(user_id, message_id, timestamp, content, 'user')
                
                # Send AI error message only once per day
                if last_unavailable_date != today:
                    message_text = config.get('ai_error_message', 'Serviço temporariamente indisponível.')
                    send_unavailable_message(user_id, message_text)
                    save_message_to_history(user_id, '', int(time.time()), message_text, 'auto')
                    clients_table.update_item(
                        Key={'phone_number': user_id},
                        UpdateExpression='SET last_unavailable_message_date = :date',
                        ExpressionAttributeValues={':date': today}
                    )
                logger.info(f"AI disabled for {user_id}, error message sent")
                continue
            
            # Normal flow: store in buffer and trigger Step Functions
            store_message_in_buffer(user_id, message_id, timestamp, content, client_info['session_id'])
            trigger_step_function(user_id)
        
        return {'statusCode': 200, 'body': json.dumps({'message': 'Message processed'})}
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

def save_message_to_history(user_id, message_id, timestamp, content, sender):
    try:
        history_table.put_item(Item={
            'phone_number': user_id,
            'timestamp': timestamp,
            'sender': sender,
            'content': content or '',
            'message_id': message_id,
            'created_at': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.warning(f"Failed to save to history: {e}")

def store_message_in_buffer(user_id, message_id, timestamp, content, session_id):
    try:
        response = buffer_table.get_item(Key={'phone_number': user_id})
        item = response.get('Item', {'phone_number': user_id, 'messages': {}, 'session_id': session_id})
        
        item['messages'][str(timestamp)] = {'id': message_id, 'content': content, 'timestamp': timestamp}
        item['session_id'] = session_id
        item['updated_at'] = int(time.time())
        
        buffer_table.put_item(Item=item)
        logger.info(f"Stored message for {user_id} at {timestamp}")
    except Exception as e:
        logger.error(f"Failed to store message: {str(e)}")
        raise

def get_or_create_client(user_id, name):
    try:
        response = clients_table.get_item(Key={'phone_number': user_id})
        item = response.get('Item')
        
        current_time = int(time.time())
        
        if not item:
            session_id = str(uuid.uuid4())
            new_client = {
                'phone_number': user_id,
                'name': name,
                'session_id': session_id,
                'last_message_at': current_time,
                'ai_enabled': True,
                'created_at': datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%dT%H:%M:%S')
            }
            clients_table.put_item(Item=new_client)
            logger.info(f"Created new client: {user_id}")
            return new_client
        
        last_message_at = item.get('last_message_at', 0)
        session_id = item.get('session_id', str(uuid.uuid4()))
        
        if current_time - last_message_at > 1800:
            session_id = str(uuid.uuid4())
            clients_table.update_item(
                Key={'phone_number': user_id},
                UpdateExpression='SET session_id = :sid, last_message_at = :lma',
                ExpressionAttributeValues={':sid': session_id, ':lma': current_time}
            )
            item['session_id'] = session_id
            logger.info(f"Refreshed session for {user_id}")
        else:
            clients_table.update_item(
                Key={'phone_number': user_id},
                UpdateExpression='SET last_message_at = :lma',
                ExpressionAttributeValues={':lma': current_time}
            )
        
        return item
    except Exception as e:
        logger.error(f"Failed to get/create client: {str(e)}")
        raise

def is_execution_running(user_id, sfn_arn):
    try:
        paginator = sfn_client.get_paginator('list_executions')
        for page in paginator.paginate(stateMachineArn=sfn_arn, statusFilter='RUNNING'):
            for execution in page.get('executions', []):
                if execution['name'].startswith(f"{user_id}-"):
                    return True
        return False
    except Exception as e:
        logger.warning(f"Could not verify executions for {user_id}: {str(e)}")
        return False

def trigger_step_function(user_id):
    try:
        sfn_arn = get_step_function_arn()
        
        if is_execution_running(user_id, sfn_arn):
            return
        
        execution_name = f"{user_id}-{int(time.time())}"
        
        sfn_client.start_execution(
            stateMachineArn=sfn_arn,
            name=execution_name,
            input=json.dumps({'user_id': user_id})
        )
    except sfn_client.exceptions.ExecutionAlreadyExists:
        pass  # Already running, ignore
    except Exception as e:
        logger.error(f"Failed to trigger Step Function for {user_id}: {str(e)}")
        raise

