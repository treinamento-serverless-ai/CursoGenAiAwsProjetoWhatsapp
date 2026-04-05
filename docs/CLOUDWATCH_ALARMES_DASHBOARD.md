# CloudWatch - Alarmes e Dashboard

## Visão Geral

O projeto utiliza Amazon CloudWatch para monitoramento da aplicação com:
- **Alarmes** para detecção de erros críticos
- **Dashboard** para visualização de métricas operacionais

Todos os alarmes notificam via SNS topic `{project}-{environment}-alerts`.

---

## Alarmes

### Convenção de Nomenclatura

```
{projeto}-{ambiente}-{servico}-{recurso}-{tipo_alerta}
```

### Alarmes Ativos

| Alarme | Serviço | Recurso | Tipo | Descrição |
|--------|---------|---------|------|-----------|
| `...-apigateway-admin-error-rate` | API Gateway | Admin | error-rate | Taxa de erros (4XX+5XX) > 5% |
| `...-apigateway-whatsapp-error-rate` | API Gateway | WhatsApp | error-rate | Taxa de erros (4XX+5XX) > 5% |
| `...-lambda-conversation-process-and-send-error-logs` | Lambda | conversation-process-and-send | error-logs | Qualquer `logger.error()` detectado |
| `...-lambda-conversation-process-and-send-error-rate` | Lambda | conversation-process-and-send | error-rate | Taxa de erros (Errors/Invocations) > 5% |
| `...-lambda-scheduled-security-monitor-error-logs` | Lambda | scheduled-security-monitor | error-logs | Qualquer `logger.error()` detectado |
| `...-lambda-scheduled-security-monitor-error-rate` | Lambda | scheduled-security-monitor | error-rate | Taxa de erros (Errors/Invocations) > 5% |

### Estratégia de Monitoramento

- **API Gateways** — monitoram erros no nível do gateway como um todo, cobrindo indiretamente todas as Lambdas que atendem via API
- **Lambdas com alarme individual** — apenas as que rodam independente do API Gateway:
  - `conversation-process-and-send` — processa mensagens com Bedrock e envia respostas via WhatsApp
  - `scheduled-security-monitor` — validação diária de token WhatsApp e certificado mTLS (via EventBridge)

### Habilitando Alarmes para Novas Lambdas

Por padrão, Lambdas não possuem alarmes individuais. Para habilitar, adicione `enable_alarms = true` na configuração da Lambda em `aws_lambda.tf`:

```hcl
my_new_lambda = {
  name_key      = "my-new-lambda"
  enable_alarms = true
  # ... demais configurações
}
```

### Parâmetros de Avaliação

| Parâmetro | Default | Dev |
|-----------|---------|-----|
| `alarm_evaluation_period_seconds` | 300s (5 min) | 600s (10 min) |
| `cloudwatch_alarms_evaluation_periods` | 3 | 3 |
| `cloudwatch_alarms_datapoints_to_alarm` | 3 | 3 |
| `cloudwatch_alarms_threshold` | 5% | 5% |

`treat_missing_data = "notBreaching"` — sem invocações = sem alerta.

---

## Dashboard

**Nome:** `{projeto}-{ambiente}-dashboard`

### Seções

| Seção | Widgets | Métricas |
|-------|---------|----------|
| **API Gateway** | 6 | Requests, Errors (4XX/5XX), Latency (avg/p99) — Admin e WhatsApp |
| **Step Functions** | 3 | Executions (Started/Succeeded/Failed/TimedOut), Duration (avg/p99), Throttled |
| **Lambda - Conversation Flow** | 5 | Invocations, Errors, Duration — webhook, check-freshness, process-and-send, transcription, archiver |
| **Lambda - CRUD** | 7 | Invocations, Errors, Duration — appointments, professionals, services, clients, attendance, conversations, config |
| **Lambda - Bedrock Agent** | 8 | Invocations, Errors, Duration — todas as action groups |
| **Lambda - Scheduled** | 1 | Invocations, Errors, Duration — security-monitor |
| **DynamoDB** | 6 | Read/Write Capacity Units, Throttled — todas as 6 tabelas |

### Interpretação de Métricas de Negócio

Algumas métricas nativas servem como proxy para indicadores de negócio:

| Métrica Nativa | Proxy Para |
|----------------|------------|
| Step Functions ExecutionsStarted | Mensagens respondidas pelo bot (aproximado) |
| Step Functions ExecutionsFailed | Conversas com erro (aproximado) |
| Lambda conversation-webhook Invocations | Mensagens recebidas do WhatsApp (aproximado) |
| DynamoDB ConversationHistory Writes | Total de mensagens trocadas (aproximado) |
| DynamoDB Clients Writes | Novos clientes ou atualizações de sessão (aproximado) |

---

## Arquivos Terraform

| Arquivo | Conteúdo |
|---------|----------|
| `aws_cloudwatch_alarms.tf` | Metric filters e alarmes (Lambda + API Gateway) |
| `aws_cloudwatch_dashboard.tf` | Dashboard com todas as seções |
| `locals.tf` | `lambdas_with_alarms` — filtra Lambdas com `enable_alarms = true` |
| `variables.tf` | Variáveis de configuração dos alarmes |
