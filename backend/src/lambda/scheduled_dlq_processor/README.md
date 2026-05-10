# scheduled_dlq_processor

Processa mensagens da Dead Letter Queue (DLQ) do EventBridge Scheduler e envia alertas via SNS.

## Funcionalidade

- Acionada automaticamente quando o EventBridge Scheduler falha ao invocar uma Lambda agendada
- Recebe mensagens da fila SQS DLQ via Event Source Mapping
- Formata detalhes da falha em notificação legível
- Publica alerta no tópico SNS para notificar administradores por email

## Fluxo

```
EventBridge Scheduler (falha)
    -> SQS DLQ
    -> Esta Lambda (triggered automaticamente)
    -> SNS Topic
    -> Email subscribers
```

## Variáveis de Ambiente

- `SNS_TOPIC_ARN`: ARN do tópico SNS para alertas
- `PROJECT_NAME`: Nome do projeto
- `ENVIRONMENT`: Ambiente (dev/prod)
