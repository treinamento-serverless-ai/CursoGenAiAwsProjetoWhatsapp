---
inclusion: fileMatch
fileMatchPattern: 'backend/**'
---

# Guia de Operações - Backend (Terraform + Lambdas Python)

Este guia deve ser seguido ao trabalhar com o backend do projeto Agendente.

## Visão Geral

O backend é composto por infraestrutura Terraform e funções Lambda em Python 3.13. O projeto é um sistema de agendamento via WhatsApp com IA Generativa (Amazon Bedrock).

## Estrutura do Projeto

```
backend/
├── terraform/
│   ├── environments/dev/       # Configuração do ambiente dev
│   │   ├── config.tf           # Backend S3 + providers
│   │   ├── main.tf             # Módulo principal com variáveis
│   │   ├── bedrock_agent_instruction.txt  # Instruções do agente
│   │   └── terraform.tfvars    # Variáveis sensíveis (não versionado)
│   └── infrastructure/         # Recursos AWS compartilhados
│       ├── aws_lambda.tf       # Todas as Lambdas (mapa único)
│       ├── aws_api_gateway.tf  # API Gateway principal
│       ├── aws_bedrock_agent.tf # Bedrock Agent + Action Groups
│       ├── aws_dynamodb.tf     # Tabelas DynamoDB
│       ├── aws_step_functions.tf # Step Functions
│       ├── aws_cognito.tf      # Cognito User Pool
│       ├── aws_sqs.tf          # Filas SQS
│       ├── aws_s3.tf           # Buckets S3
│       ├── aws_appconfig.tf    # AppConfig
│       ├── aws_cloudwatch_*.tf # Dashboard e alarmes
│       ├── openapi_agendente.yaml  # OpenAPI spec (admin API)
│       ├── openapi_whatsapp.yaml   # OpenAPI spec (webhook)
│       └── variables.tf        # Variáveis de entrada
└── src/lambda/                 # Código Python das Lambdas
    ├── agent_*                 # Action Groups do Bedrock Agent
    ├── conversation_*          # Processamento de mensagens WhatsApp
    ├── crud_*                  # CRUD para dashboard admin
    └── scheduled_*             # Tarefas agendadas (CRON)
```

## Categorias de Lambdas

### Agent Action Groups (`agent_*`)
Executam ações solicitadas pelo Bedrock Agent durante conversas WhatsApp. Recebem eventos no formato Bedrock Agent e retornam `messageVersion: "1.0"`.

### Conversation (`conversation_*`)
Processam o fluxo de mensagens WhatsApp: webhook, transcrição de áudio, invocação do agente, envio de resposta, arquivamento.

### CRUD (`crud_*`)
Operações de administração via dashboard Angular. Recebem eventos do API Gateway com autenticação Cognito JWT.

### Scheduled (`scheduled_*`)
Tarefas executadas via EventBridge (CRON): monitoramento de segurança, processamento de DLQ.

## Padrão de Implementação de Lambdas

Cada Lambda segue a estrutura:

```
src/lambda/{nome}/
├── lambda_function.py      # Handler principal (obrigatório)
├── README.md               # Documentação (obrigatório)
├── requirements.txt        # Dependências externas (opcional)
└── examples/               # Test events JSON (obrigatório)
```

### Action Groups do Bedrock

```python
def convert_params_to_dict(params_list):
    return {param.get("name"): param.get("value") for param in params_list if param.get("name")}

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = convert_params_to_dict(event.get('parameters', []))
    user_id = event.get('promptSessionAttributes', {}).get('userId')
    # ...
```

### CRUD Lambdas

Recebem contexto de autenticação via `event['requestContext']['authorizer']` (Cognito JWT).

## Terraform

### Nomenclatura

Todos os recursos seguem: `{project_name}-{environment}-{resource_id}`

### Lambdas

Todas as Lambdas são definidas em `aws_lambda.tf` via mapa único. O Terraform detecta automaticamente `requirements.txt` e faz build do ZIP.

### Adicionar Nova Lambda

1. Criar pasta em `src/lambda/{nome}/` com `lambda_function.py`, `README.md` e `examples/`
2. Adicionar entrada no mapa em `aws_lambda.tf`
3. Se for Action Group: adicionar em `aws_bedrock_agent.tf`
4. Se for endpoint admin: adicionar na OpenAPI spec
5. `terraform plan && terraform apply`

### Deploy

```bash
cd backend/terraform/environments/dev
terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

## Serviços AWS Integrados

- **DynamoDB**: 6 tabelas (Clients, ConversationHistory, MessageBuffer, Services, Professionals, Appointments)
- **Bedrock**: Agent com Action Groups para agendamento via linguagem natural
- **Step Functions**: Orquestração do fluxo de mensagens
- **Transcribe**: Conversão de áudio em texto
- **AppConfig**: Configurações dinâmicas (horário, modo agente, etc.)
- **Secrets Manager**: Token da Meta WhatsApp API
- **SQS**: Filas com DLQ para resiliência
- **Cognito**: Autenticação do dashboard admin
- **API Gateway**: REST API com mTLS (webhook) e Cognito JWT (admin)

## Boas Práticas

- Inicializar recursos AWS (boto3) fora do handler para reutilização
- Usar `logger.info()` / `logger.error()` com contexto (user_id, request_id)
- Nunca logar informações sensíveis (tokens, senhas)
- Validar todos os inputs antes de processar
- Retornar resposta estruturada mesmo em caso de erro
