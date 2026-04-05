import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'unknown')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'unknown')


def lambda_handler(event, context):
    """
    Processes EventBridge Scheduler DLQ messages and forwards to SNS.
    
    This function is triggered when EventBridge Scheduler fails to invoke
    a scheduled Lambda function. It formats the error message and sends
    a notification via SNS.
    """
    
    if not SNS_TOPIC_ARN:
        logger.error("SNS_TOPIC_ARN not configured")
        return {'statusCode': 500, 'body': 'SNS_TOPIC_ARN not configured'}
    
    processed_count = 0
    
    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            
            # Extract relevant information
            schedule_name = body.get('detail', {}).get('scheduleName', 'Unknown')
            error_message = body.get('detail', {}).get('errorMessage', 'No error message')
            event_time = body.get('time', 'Unknown')
            
            # Format notification message
            message = f"""EventBridge Scheduler Failure Alert

Project: {PROJECT_NAME}
Environment: {ENVIRONMENT}

Schedule Name: {schedule_name}
Error: {error_message}
Time: {event_time}

Full Event Details:
{json.dumps(body, indent=2)}

---
This is an automated alert from the Agendente scheduling system.
"""
            
            # Publish to SNS
            response = sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f'[{ENVIRONMENT.upper()}] Scheduler Failure: {schedule_name}',
                Message=message
            )
            
            logger.info(f"Notification sent for schedule: {schedule_name}, MessageId: {response['MessageId']}")
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
            logger.error(f"Record: {json.dumps(record)}")
            # Continue processing other records
            continue
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': processed_count,
            'total': len(event['Records'])
        })
    }
