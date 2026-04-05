import os
import json
import boto3
import time
import logging
import urllib3

from datetime import datetime
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_client = boto3.client('bedrock-agent-runtime', config=Config(read_timeout=600))
dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')
appconfig = boto3.client('appconfigdata')
sns = boto3.client('sns')

buffer_table = dynamodb.Table(os.environ['MESSAGE_BUFFER_TABLE'])
history_table = dynamodb.Table(os.environ['CONVERSATION_HISTORY_TABLE'])
clients_table = dynamodb.Table(os.environ['CLIENTS_TABLE'])

def get_appconfig():
    try:
        response = appconfig.start_configuration_session(
            ApplicationIdentifier=os.environ['APPCONFIG_APP_ID'],
            EnvironmentIdentifier=os.environ['APPCONFIG_ENV_ID'],
            ConfigurationProfileIdentifier=os.environ['APPCONFIG_PROFILE_ID']
        )
        config_token = response['InitialConfigurationToken']
        config_response = appconfig.get_latest_configuration(ConfigurationToken=config_token)
        return json.loads(config_response['Configuration'].read())
    except Exception as e:
        logger.error(f"CRITICAL: Error reading AppConfig: {e}")
        return {
            'ai_error_message': 'Desculpe, estou com dificuldades técnicas no momento. Um atendente humano entrará em contato em breve.',
            'reply_with_context': True,
            'reply_context_use_last': True
        }

def save_messages_to_history(user_id, messages, sender='user'):
    """Salva mensagens no histórico"""
    timestamp = int(time.time())
    for msg in messages:
        history_table.put_item(Item={
            'phone_number': user_id,
            'timestamp': timestamp,
            'sender': sender,
            'content': msg['content'],
            'message_id': msg.get('id', ''),
            'created_at': datetime.utcnow().isoformat()
        })
        timestamp += 1

def send_whatsapp_message(user_id, message_text, message_ids=None, config=None):
    """Envia mensagem via Meta API"""
    try:
        secret = json.loads(secrets_client.get_secret_value(SecretId=os.environ['WHATSAPP_SECRET_NAME'])['SecretString'])
        
        url = f"https://graph.facebook.com/{secret['API_VERSION']}/{secret['PHONE_NUMBER_ID']}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': user_id,
            'text': {'body': message_text}
        }
        
        # Add context (reply to message) based on config
        reply_enabled = True  # Default: enabled
        if config:
            raw_value = config.get('reply_with_context', True)
            # Convert string to boolean if needed
            if isinstance(raw_value, str):
                reply_enabled = raw_value.lower() in ('true', '1', 'yes')
            else:
                reply_enabled = bool(raw_value)
        
        if message_ids and reply_enabled:
            use_last = True  # Default: use last message
            if config:
                raw_use_last = config.get('reply_context_use_last', True)
                if isinstance(raw_use_last, str):
                    use_last = raw_use_last.lower() in ('true', '1', 'yes')
                else:
                    use_last = bool(raw_use_last)
            
            message_to_reply = message_ids[-1] if use_last else message_ids[0]
            payload['context'] = {'message_id': message_to_reply}
        
        http = urllib3.PoolManager()
        
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
        
        if response.status != 200:
            raise Exception(f"Meta API returned status {response.status}: {response.data.decode('utf-8')}")
        
        return True, json.loads(response.data.decode('utf-8'))
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False, str(e)

def mark_messages_as_read(message_ids):
    """Marca mensagens como lidas no WhatsApp"""
    try:
        secret = json.loads(secrets_client.get_secret_value(SecretId=os.environ['WHATSAPP_SECRET_NAME'])['SecretString'])
        url = f"https://graph.facebook.com/{secret['API_VERSION']}/{secret['PHONE_NUMBER_ID']}/messages"
        
        http = urllib3.PoolManager()
        
        for message_id in message_ids:
            if not message_id:
                continue
                
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            try:
                response = http.request(
                    'POST',
                    url,
                    body=json.dumps(payload),
                    headers={
                        'Authorization': f"Bearer {secret['ACCESS_TOKEN']}",
                        'Content-Type': 'application/json'
                    },
                    timeout=5.0
                )
                logger.info(f"Marked message {message_id} as read. Status: {response.status}")
            except Exception as e:
                logger.error(f"Failed to mark message {message_id} as read: {e}")
    except Exception as e:
        logger.error(f"Error in mark_messages_as_read: {e}")

def disable_ai_for_client(user_id, user_messages=None, error_details=None):
    """Desabilita atendimento por IA para o cliente e envia notificação detalhada"""
    clients_table.update_item(
        Key={'phone_number': user_id},
        UpdateExpression="SET ai_enabled = :val",
        ExpressionAttributeValues={':val': False}
    )
    
    # Enviar notificação SNS detalhada
    if 'ALERTS_TOPIC_ARN' in os.environ:
        try:
            messages_text = "\n".join([f"- {msg['content']}" for msg in (user_messages or [])])
            
            subject = f"AI Desabilitada - {os.environ.get('PROJECT_NAME', 'Sistema')} {os.environ.get('ENVIRONMENT', 'env')}"
            
            message = f"""Houve um erro no processamento de mensagens de:

Project: {os.environ.get('PROJECT_NAME', 'N/A')}
Environment: {os.environ.get('ENVIRONMENT', 'N/A')}
User: {user_id}

Erro: {error_details or 'Erro não especificado'}

O erro surgiu depois do usuário enviar essas mensagens:

{messages_text or 'Nenhuma mensagem capturada'}

O usuário aguarda a continuação da conversa por interação humana.

Ação necessária: Reabilitar AI manualmente após resolver o problema.
"""
            
            sns.publish(
                TopicArn=os.environ['ALERTS_TOPIC_ARN'],
                Subject=subject,
                Message=message
            )
            logger.info(f"Detailed alert sent for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send detailed alert: {e}")

def lambda_handler(event, context):
    user_id = event['user_id']
    request_id = context.aws_request_id
    
    config = get_appconfig()
    
    # 1. Buscar mensagens do buffer
    response = buffer_table.get_item(Key={'phone_number': user_id})
    item = response.get('Item')
    
    if not item or 'messages' not in item:
        return {'status': 'no_messages', 'user_id': user_id}
    
    messages = item['messages']
    session_id = item.get('session_id', user_id)
    
    # Ordenar e preparar mensagens
    sorted_timestamps = sorted([int(ts) for ts in messages.keys()])
    user_messages = [{'content': messages[str(ts)]['content'], 'id': messages[str(ts)]['id']} for ts in sorted_timestamps if messages[str(ts)].get('content')]
    message_content = "\n".join([msg['content'] for msg in user_messages])
    message_ids = [msg['id'] for msg in user_messages]
    
    # Marcar mensagens como lidas
    mark_messages_as_read(message_ids)
    
    # Deletar do buffer com lock condicional (apenas se ainda existir)
    try:
        buffer_table.delete_item(
            Key={'phone_number': user_id},
            ConditionExpression='attribute_exists(phone_number)'
        )
    except buffer_table.meta.client.exceptions.ConditionalCheckFailedException:
        logger.info(f"Buffer already deleted by another execution for {user_id}")
        return {'status': 'already_processed', 'user_id': user_id}
    
    # 2. Arquivar mensagens do usuário
    save_messages_to_history(user_id, user_messages, sender='user')
    
    # 3. Tentar gerar resposta com Bedrock
    try:
        bedrock_response = bedrock_client.invoke_agent(
            agentId=os.environ['BEDROCK_AGENT_ID'],
            agentAliasId=os.environ['BEDROCK_AGENT_ALIAS_ID'],
            sessionId=session_id,
            inputText=message_content,
            sessionState={
                'promptSessionAttributes': {
                    'userId': user_id
                }
            }
        )
        
        agent_response = ""
        for event in bedrock_response['completion']:
            if 'chunk' in event:
                agent_response += event['chunk']['bytes'].decode('utf-8')
        
        if not agent_response:
            raise Exception("Empty response from Bedrock")
        
        # 3.1. Sucesso - tentar enviar
        success, result = send_whatsapp_message(user_id, agent_response, message_ids, config)
        
        if success:
            # 3.1.1.1. Sucesso no envio - salvar resposta da IA
            logger.info(f"[{request_id}] WhatsApp message sent successfully")
            save_messages_to_history(user_id, [{'content': agent_response, 'id': result.get('messages', [{}])[0].get('id', '')}], sender='ai')
            return {'status': 'success', 'user_id': user_id, 'agent_response': agent_response, 'request_id': request_id}
        else:
            # 3.1.1.2. Erro no envio - desabilitar IA e notificar
            logger.error(f"[{request_id}] Failed to send WhatsApp: {result}")
            disable_ai_for_client(user_id, user_messages, f"Meta API Error: {result}")
            history_table.put_item(Item={'phone_number': user_id, 'timestamp': int(time.time()), 'sender': 'system', 'content': 'ERROR: Failed to send message to Meta API', 'error': result})
            return {'status': 'send_error', 'user_id': user_id, 'error': result, 'request_id': request_id}
    
    except Exception as e:
        # 3.2. Erro no Bedrock - usar mensagem padrão
        logger.error(f"[{request_id}] Bedrock error: {e}")
        error_message = config.get('ai_error_message', 'Desculpe, estou com dificuldades técnicas.')
        disable_ai_for_client(user_id, user_messages, f"Bedrock Error: {str(e)}")
        
        success, result = send_whatsapp_message(user_id, error_message, message_ids, config)
        
        if success:
            save_messages_to_history(user_id, [{'content': error_message, 'id': ''}], sender='system')
            return {'status': 'bedrock_error_sent', 'user_id': user_id}
        else:
            history_table.put_item(Item={'phone_number': user_id, 'timestamp': int(time.time()), 'sender': 'system', 'content': 'ERROR: Bedrock failed and Meta API failed', 'error': str(e)})
            sns.publish(TopicArn=os.environ['ALERTS_TOPIC_ARN'], Subject='Critical Error', Message=f"Both Bedrock and Meta API failed for user {user_id}")
            return {'status': 'critical_error', 'user_id': user_id}
