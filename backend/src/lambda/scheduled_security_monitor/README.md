# scheduled_security_monitor

Valida token do WhatsApp via Graph API da Meta e envia alertas quando esta proximo da expiracao.

## Funcionalidade

- Busca credenciais no Secrets Manager
- Valida token via Facebook Graph API (debug_token endpoint)
- Calcula dias restantes ate expiracao
- Envia alerta via SNS se o token expira em 14 dias ou menos
- Executada diariamente via EventBridge (CRON)

## Variaveis de Ambiente

- `SECRET_ARN`: ARN do secret com credenciais da Meta WhatsApp API
- `SNS_TOPIC_ARN`: ARN do topico SNS para alertas
- `PROJECT_NAME`: Nome do projeto
- `ENVIRONMENT`: Ambiente (dev/prod)
