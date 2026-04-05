import json
import os
import time
import uuid
import logging
import urllib3
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')
appconfig = boto3.client('appconfigdata')

buffer_table = dynamodb.Table(os.environ['MESSAGE_BUFFER_TABLE'])

def get_secret():
    response = secrets_client.get_secret_value(SecretId=os.environ['WHATSAPP_SECRET_NAME'])
    return json.loads(response['SecretString'])

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
            'audio_min_size_kb': 10,
            'audio_max_size_kb': 275
        }

def download_audio_from_whatsapp(media_id, secret):
    try:
        http = urllib3.PoolManager()
        
        # Get media URL
        media_url = f"https://graph.facebook.com/{secret['API_VERSION']}/{media_id}"
        headers = {'Authorization': f"Bearer {secret['ACCESS_TOKEN']}"}
        
        response = http.request('GET', media_url, headers=headers)
        if response.status != 200:
            raise Exception(f"Failed to get media metadata: {response.status}")
        
        media_data = json.loads(response.data.decode('utf-8'))
        download_url = media_data.get('url')
        
        if not download_url:
            raise Exception("No download URL in response")
        
        # Download audio file
        file_response = http.request('GET', download_url, headers=headers)
        if file_response.status != 200:
            raise Exception(f"Failed to download audio: {file_response.status}")
        
        return file_response.data
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        raise

def lambda_handler(event, context):
    logger.info(f"Processing audio message: {json.dumps(event)}")
    
    user_id = event.get('from')
    timestamp = str(event.get('timestamp'))  # Garantir que é string
    message_id = event.get('id')
    audio_info = event.get('audio', {})
    media_id = audio_info.get('id')
    mime_type = audio_info.get('mime_type', 'audio/ogg')
    
    config = get_appconfig()
    secret = get_secret()
    
    try:
        # Download audio
        audio_data = download_audio_from_whatsapp(media_id, secret)
        
        # Upload to S3
        extension = mime_type.split('/')[-1].split(';')[0]
        s3_key = f"{user_id}/{timestamp}.{extension}"
        s3_bucket = os.environ['MEDIA_BUCKET_NAME']
        
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=audio_data,
            ContentType=mime_type
        )
        
        s3_uri = f"s3://{s3_bucket}/{s3_key}"
        logger.info(f"Audio uploaded to {s3_uri}")
        
        # Validate size
        file_size_bytes = len(audio_data)
        file_size_kb = file_size_bytes / 1024
        
        min_size_kb = float(config.get('audio_min_size_kb', 10))
        max_size_kb = float(config.get('audio_max_size_kb', 275))
        
        if file_size_kb < min_size_kb:
            transcription = f"[ÁUDIO MUITO CURTO - MÍNIMO {min_size_kb}KB]"
        elif file_size_kb > max_size_kb:
            transcription = f"[ÁUDIO MUITO LONGO - MÁXIMO {max_size_kb}KB (~2 MINUTOS)]"
        else:
            # Start transcription
            job_name = f"transcribe-{uuid.uuid4().hex}"
            
            transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': s3_uri},
                MediaFormat=extension if extension in ['mp3', 'mp4', 'wav', 'flac'] else 'ogg',
                LanguageCode='pt-BR',
                OutputBucketName=s3_bucket,
                OutputKey=f"{s3_key}_transcribe.json"
            )
            
            # Poll for completion
            max_attempts = 60
            attempt = 0
            
            while attempt < max_attempts:
                result = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
                status = result['TranscriptionJob']['TranscriptionJobStatus']
                
                if status == 'COMPLETED':
                    output_key = f"{s3_key}_transcribe.json"
                    obj = s3_client.get_object(Bucket=s3_bucket, Key=output_key)
                    transcript_data = json.loads(obj['Body'].read())
                    transcription = transcript_data['results']['transcripts'][0]['transcript']
                    break
                elif status == 'FAILED':
                    transcription = "[TRANSCRIÇÃO FALHOU]"
                    break
                
                time.sleep(5)
                attempt += 1
            
            if attempt >= max_attempts:
                transcription = "[TRANSCRIÇÃO TIMEOUT]"
        
        # Update buffer
        buffer_table.update_item(
            Key={'phone_number': user_id},
            UpdateExpression='SET messages.#ts.content = :content',
            ExpressionAttributeNames={'#ts': str(timestamp)},
            ExpressionAttributeValues={':content': transcription}
        )
        
        logger.info(f"Transcription completed for {user_id}: {transcription[:50]}...")
        
        return {'statusCode': 200, 'body': json.dumps({'transcription': transcription})}
    
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        
        # Update buffer with error
        try:
            buffer_table.update_item(
                Key={'phone_number': user_id},
                UpdateExpression='SET messages.#ts.content = :content',
                ExpressionAttributeNames={'#ts': str(timestamp)},
                ExpressionAttributeValues={':content': f"[ERRO NO PROCESSAMENTO: {str(e)[:50]}]"}
            )
        except Exception as update_error:
            logger.error(f"Failed to update buffer with error: {update_error}")
        
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
