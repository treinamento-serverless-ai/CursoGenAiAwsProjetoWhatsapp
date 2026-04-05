import os
import json
import urllib3
import boto3
from urllib.parse import urlencode
from datetime import datetime, timezone
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()

secrets_client = boto3.client("secretsmanager")
sns_client = boto3.client("sns")
s3_client = boto3.client("s3")

SECRET_ARN = os.environ.get("SECRET_ARN")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
MTLS_TRUSTSTORE_BUCKET = os.environ.get("MTLS_TRUSTSTORE_BUCKET")
MTLS_TRUSTSTORE_KEY = os.environ.get("MTLS_TRUSTSTORE_KEY")
PROJECT_NAME = os.environ.get("PROJECT_NAME", "unknown")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")

def get_secret():
    response = secrets_client.get_secret_value(SecretId=SECRET_ARN)
    return json.loads(response["SecretString"])

def check_token_expiration():
    """Verifica expiração do token WhatsApp"""
    try:
        secret = get_secret()
        access_token = secret.get("ACCESS_TOKEN")
        app_id = secret.get("APP_ID")
        app_secret = secret.get("APP_SECRET")
        
        if not access_token or not app_id or not app_secret:
            return {"error": "Missing credentials in secret"}

        url = "https://graph.facebook.com/debug_token"
        params = {
            "input_token": access_token,
            "access_token": f"{app_id}|{app_secret}"
        }
        
        response = http.request("GET", f"{url}?{urlencode(params)}")
        
        if response.status != 200:
            error_body = response.data.decode("utf-8")
            logger.error(f"Graph API error: {response.status} - {error_body}")
            return {"error": "Token validation failed"}

        data = json.loads(response.data.decode("utf-8"))["data"]
        
        result = {
            "type": "token",
            "is_valid": data.get("is_valid"),
            "expires_at": None,
            "days_remaining": None,
            "needs_alert": False
        }

        expires_at_ts = data.get("expires_at")
        if expires_at_ts:
            expires_at = datetime.fromtimestamp(expires_at_ts, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            days_remaining = (expires_at - now).days

            result["expires_at"] = expires_at.strftime("%Y-%m-%d %H:%M:%S")
            result["days_remaining"] = days_remaining
            result["needs_alert"] = days_remaining <= 14

        return result
    except Exception as e:
        logger.exception("Token validation error")
        return {"error": str(e)}

def check_certificate_expiration():
    """Verifica expiração dos certificados mTLS"""
    try:
        if not MTLS_TRUSTSTORE_BUCKET or not MTLS_TRUSTSTORE_KEY:
            logger.info("mTLS not configured, skipping certificate check")
            return None
        
        # Buscar metadata do objeto S3
        response = s3_client.head_object(
            Bucket=MTLS_TRUSTSTORE_BUCKET,
            Key=MTLS_TRUSTSTORE_KEY
        )
        
        metadata = response.get("Metadata", {})
        digicert_expiry_str = metadata.get("digicert_expiry")
        meta_expiry_str = metadata.get("meta_expiry")
        
        results = []
        
        # Verificar certificado DigiCert
        if digicert_expiry_str and digicert_expiry_str != "N/A":
            try:
                # Formato: "Oct 22 12:00:00 2028 GMT"
                digicert_expiry = datetime.strptime(digicert_expiry_str.strip(), "%b %d %H:%M:%S %Y %Z")
                digicert_expiry = digicert_expiry.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_remaining = (digicert_expiry - now).days
                
                results.append({
                    "type": "certificate",
                    "name": "DigiCert SHA2 High Assurance Server CA",
                    "expires_at": digicert_expiry.strftime("%Y-%m-%d %H:%M:%S"),
                    "days_remaining": days_remaining,
                    "needs_alert": days_remaining <= 30
                })
            except Exception as e:
                logger.error(f"Error parsing DigiCert expiry: {e}")
        
        # Verificar certificado Meta
        if meta_expiry_str and meta_expiry_str != "N/A":
            try:
                meta_expiry = datetime.strptime(meta_expiry_str.strip(), "%b %d %H:%M:%S %Y %Z")
                meta_expiry = meta_expiry.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_remaining = (meta_expiry - now).days
                
                results.append({
                    "type": "certificate",
                    "name": "Meta Outbound API CA",
                    "expires_at": meta_expiry.strftime("%Y-%m-%d %H:%M:%S"),
                    "days_remaining": days_remaining,
                    "needs_alert": days_remaining <= 30
                })
            except Exception as e:
                logger.error(f"Error parsing Meta expiry: {e}")
        
        return results
    except Exception as e:
        logger.exception("Certificate validation error")
        return [{"error": str(e)}]

def send_alerts(token_result, cert_results):
    """Envia alertas via SNS se necessário"""
    if not SNS_TOPIC_ARN:
        logger.warning("SNS_TOPIC_ARN not configured, alerts not sent")
        return
    
    alerts = []
    
    # Alerta de token
    if token_result.get("needs_alert"):
        days = token_result["days_remaining"]
        alerts.append(
            f"⚠️ TOKEN WHATSAPP\n"
            f"Dias restantes: {days}\n"
            f"Expira em: {token_result['expires_at']} UTC\n"
            f"Ação: Gerar novo token antes dessa data"
        )
    
    # Alertas de certificados
    if cert_results:
        for cert in cert_results:
            if cert.get("needs_alert"):
                days = cert["days_remaining"]
                alerts.append(
                    f"⚠️ CERTIFICADO mTLS: {cert['name']}\n"
                    f"Dias restantes: {days}\n"
                    f"Expira em: {cert['expires_at']} UTC\n"
                    f"Ação: Atualizar truststore antes dessa data"
                )
    
    if alerts:
        message = (
            f"🔒 Alerta de Segurança - {PROJECT_NAME}\n"
            f"Ambiente: {ENVIRONMENT}\n\n"
            + "\n\n".join(alerts)
        )
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=f"[{PROJECT_NAME}] Alerta de Expiração"
        )
        logger.info(f"Alerts sent: {len(alerts)} items")

def lambda_handler(event, context):
    try:
        if not SECRET_ARN:
            return {"statusCode": 500, "body": json.dumps({"error": "SECRET_ARN not configured"})}
        
        # Verificar token
        token_result = check_token_expiration()
        
        # Verificar certificados
        cert_results = check_certificate_expiration()
        
        # Enviar alertas se necessário
        send_alerts(token_result, cert_results)
        
        result = {
            "token": token_result,
            "certificates": cert_results
        }
        
        logger.info(f"Security monitoring complete: {json.dumps(result)}")
        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        logger.exception("Security monitoring error")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
