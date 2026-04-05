# Configurações e Segredos

## Visão Geral

O projeto utiliza três serviços AWS para gerenciamento de configurações e segredos, cada um otimizado para um caso de uso específico:

- **AWS Secrets Manager** — credenciais sensíveis que requerem proteção rigorosa
- **AWS Systems Manager Parameter Store** — dados técnicos não-sensíveis (IDs de recursos, ARNs)
- **AWS AppConfig** — configurações de comportamento da aplicação com deployment controlado

A escolha do serviço depende da natureza dos dados (sensíveis vs. não-sensíveis), frequência de mudança e necessidade de deployment controlado.

**Convenção de nomenclatura do projeto:**
- `PROJECT_NAME="barbearia-silva"`
- `ENVIRONMENT="prod"`
- Padrão de recursos: `{PROJECT_NAME}-{ENVIRONMENT}-{RESOURCE_ID}`

---

## AWS Secrets Manager

Serviço especializado em gerenciamento de credenciais sensíveis. Oferece criptografia automática via AWS KMS, rotação automática de credenciais, e auditoria detalhada via CloudTrail.

**Estrutura do secret:** `{PROJECT_NAME}/{ENVIRONMENT}/whatsapp`

**Dados armazenados neste projeto:**

| Campo | Descrição |
|-------|-----------|
| `ACCESS_TOKEN` | Token de acesso da Meta WhatsApp API |
| `VERIFY_TOKEN` | Token de verificação do webhook usado pela Meta |
| `APP_ID` | Identificador da aplicação WhatsApp Business |
| `APP_SECRET` | Chave secreta da aplicação Meta |
| `API_VERSION` | Versão da Graph API (ex: "v22.0") |
| `PHONE_NUMBER_ID` | ID do número de telefone WhatsApp Business |

**Exemplo:** `barbearia-silva/dev/whatsapp`
```json
{
  "ACCESS_TOKEN": "EAAxxxxx...",
  "VERIFY_TOKEN": "meu-token-secreto-123",
  "APP_ID": "1234567890123456",
  "APP_SECRET": "abc123def456...",
  "API_VERSION": "v22.0",
  "PHONE_NUMBER_ID": "609253768946096"
}
```

**Nota sobre design:** Todos os dados da Meta ficam juntos no Secrets Manager para simplicidade. Tecnicamente, `API_VERSION` e `PHONE_NUMBER_ID` poderiam estar no Parameter Store (não são sensíveis), mas mantê-los no secret facilita o gerenciamento: todas as credenciais de terceiros ficam em um único lugar.

---

## AWS Systems Manager Parameter Store

Serviço de armazenamento hierárquico para dados de configuração e strings simples. Oferece versionamento, notificações de mudança via EventBridge, e tier gratuito (Standard) para até 10.000 parâmetros.

**Estrutura hierárquica:** `/{PROJECT_NAME}/{ENVIRONMENT}/{SERVICE}/{PARAMETER_NAME}`

**Dados armazenados neste projeto:**

| Parâmetro | Descrição |
|-----------|-----------|
| `/{proj}/{env}/bedrock/agent_id` | ID do agente Bedrock (injetado pelo Terraform) |
| `/{proj}/{env}/bedrock/agent_alias_id` | Alias do agente Bedrock |
| `/{proj}/{env}/dynamodb/appointments_table` | ARN da tabela Appointments |
| `/{proj}/{env}/dynamodb/professionals_table` | ARN da tabela Professionals |
| `/{proj}/{env}/dynamodb/services_table` | ARN da tabela Services |
| `/{proj}/{env}/dynamodb/clients_table` | ARN da tabela Clients |
| `/{proj}/{env}/dynamodb/message_buffer_table` | ARN da tabela MessageBuffer |
| `/{proj}/{env}/dynamodb/conversation_history_table` | ARN da tabela ConversationHistory |

**Exemplo:**
```
/barbearia-silva/dev/bedrock/agent_id = "XVYWK3SS4K"
/barbearia-silva/dev/bedrock/agent_alias_id = "TSTALIASID"
/barbearia-silva/dev/dynamodb/appointments_table = "barbearia-silva-dev-Appointments"
```

**Nota:** Neste projeto, o Parameter Store é usado apenas para recursos AWS gerenciados pelo Terraform. Dados da Meta WhatsApp ficam no Secrets Manager.

---

## AWS AppConfig

Serviço especializado em gerenciamento de configurações de aplicação com deployment controlado. Oferece estratégias de deployment gradual (canary, linear), validação de configurações antes do deployment, e rollback automático em caso de erros.

**Estrutura:** Application `{PROJECT_NAME}-{ENVIRONMENT}`, Environment `{ENVIRONMENT}`, Configuration Profile `agent-config`

**Dados armazenados neste projeto:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `business_hours_start` | String | Horário de início do atendimento (ex: "08:00") |
| `business_hours_end` | String | Horário de fim do atendimento (ex: "18:00") |
| `max_booking_days` | Number | Dias máximos no futuro para agendamento (ex: 90) |
| `inactivity_threshold_seconds` | Number | Tempo para aguardar antes de processar mensagens agrupadas (ex: 30) |
| `audio_processing_grace_period` | Number | Tempo adicional para aguardar transcrição de áudios (ex: 15) |
| `closed_message` | String | Texto enviado fora do horário de atendimento |
| `transcribe_enabled` | Boolean | Habilitar/desabilitar Amazon Transcribe |
| `transcribe_disabled_message` | String | Mensagem quando transcrição está desabilitada |
| `audio_min_size_kb` | Number | Tamanho mínimo aceito para áudio (ex: 10) |
| `audio_max_size_kb` | Number | Tamanho máximo aceito para áudio (ex: 275) |
| `bedrock_model_id` | String | ID do modelo Bedrock (ex: "amazon.nova-lite-v1:0") |
| `bedrock_temperature` | Number | Temperatura do modelo (ex: 0.7) |

**Exemplo de configuração JSON:**
```json
{
  "business_hours_start": "08:00",
  "business_hours_end": "18:00",
  "max_booking_days": 90,
  "inactivity_threshold_seconds": 30,
  "audio_processing_grace_period": 15,
  "closed_message": "Olá! Nosso horário de atendimento é das 8h às 18h...",
  "transcribe_enabled": true,
  "transcribe_disabled_message": "Desculpe, não consigo processar áudios no momento.",
  "audio_min_size_kb": 10,
  "audio_max_size_kb": 275,
  "bedrock_model_id": "amazon.nova-lite-v1:0",
  "bedrock_temperature": 0.7
}
```

---

## Resumo de Decisão

| Tipo de Dado | Serviço | Justificativa |
|--------------|---------|---------------|
| Tokens e credenciais sensíveis | Secrets Manager | Rotação automática, criptografia, auditoria |
| IDs de recursos e ARNs | Parameter Store | Dados técnicos não-sensíveis, versionamento simples |
| Configurações de comportamento | AppConfig | Deployment controlado, rollback, feature flags |
| Horários e limites de negócio | AppConfig | Mudanças frequentes sem redeploy |

## Benefícios da Abordagem

- **Segurança:** credenciais sensíveis isoladas e criptografadas no Secrets Manager
- **Auditoria:** CloudTrail registra todos os acessos a secrets e parâmetros
- **Deployment seguro:** AppConfig permite mudanças graduais com rollback automático
- **Separação de responsabilidades:** cada serviço otimizado para seu caso de uso
- **Custo-efetivo:** Parameter Store tier gratuito para dados não-sensíveis
- **Sem downtime:** mudanças de configuração sem necessidade de redeploy de código
