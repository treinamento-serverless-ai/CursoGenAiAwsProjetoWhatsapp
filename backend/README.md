# Agendente — Backend

Infraestrutura como código (Terraform) e funções Lambda (Python 3.13) que compõem o backend serverless do projeto Agendente.

Para uma visão geral do projeto, consulte o [README principal](../README.md).

## Estrutura

```
backend/
├── terraform/
│   ├── infrastructure/             # Recursos AWS (módulo principal)
│   │   ├── aws_lambda.tf          # Todas as Lambdas
│   │   ├── aws_api_gateway.tf     # API Gateway (admin)
│   │   ├── aws_api_gateway_whatsapp.tf  # API Gateway (webhook)
│   │   ├── aws_bedrock_agent.tf   # Bedrock Agent + Action Groups
│   │   ├── aws_step_functions.tf  # Orquestração de mensagens
│   │   ├── aws_dynamodb.tf        # 6 tabelas DynamoDB
│   │   ├── aws_cognito.tf         # Autenticação (User Pool)
│   │   ├── aws_s3.tf             # Buckets (frontend, mídia, arquivo)
│   │   ├── aws_sqs.tf            # Filas com DLQ
│   │   ├── aws_appconfig.tf      # Configurações dinâmicas
│   │   ├── aws_secrets.tf        # Secrets Manager
│   │   ├── aws_ssm_parameters.tf # SSM Parameters
│   │   ├── aws_eventbridge.tf    # CRON jobs
│   │   ├── aws_sns.tf            # Notificações
│   │   ├── aws_cloudwatch_*.tf   # Dashboard e alarmes
│   │   ├── aws_custom_domains.tf # Route 53, CloudFront, ACM
│   │   ├── aws_s3_mtls.tf       # Truststore mTLS
│   │   ├── openapi_agendente.yaml # OpenAPI spec (admin)
│   │   ├── openapi_whatsapp.yaml  # OpenAPI spec (webhook)
│   │   ├── variables.tf          # Variáveis de entrada
│   │   └── outputs.tf            # Outputs
│   └── environments/
│       └── dev/                   # Ambiente de desenvolvimento
│           ├── config.tf          # Backend S3 + providers
│           ├── main.tf            # Módulo principal com variáveis
│           ├── bedrock_agent_instruction.txt  # Instruções do agente IA
│           ├── terraform.tfvars   # Variáveis sensíveis (não versionado)
│           └── scripts/           # Scripts auxiliares (seed data, etc.)
└── src/lambda/                    # ~25 funções Lambda (Python)
    ├── agent_*                    # Action Groups do Bedrock Agent
    ├── conversation_*             # Processamento de mensagens WhatsApp
    ├── crud_*                     # CRUD para o dashboard admin
    └── scheduled_*                # Tarefas agendadas (CRON)
```

Para detalhes sobre as Lambdas (padrões, categorias e como criar novas), consulte o [README das Lambdas](./src/README.md).

## Deploy

### Pré-requisitos

- Terraform instalado
- AWS CLI configurado com credenciais
- Bucket S3 para armazenar o state do Terraform

### 1. Configurar Backend e Variáveis

```bash
cd terraform/environments/dev

cp backend.hcl.example backend.hcl
cp terraform.tfvars.example terraform.tfvars
```

Edite `backend.hcl` com os dados do seu bucket S3 e `terraform.tfvars` com suas variáveis.

> Os arquivos `backend.hcl` e `terraform.tfvars` são ignorados pelo git por segurança.

### 2. Inicializar e Aplicar

```bash
terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

### 3. Ver Outputs

```bash
terraform output
```

Os outputs incluem URLs do API Gateway, IDs do Cognito e outros valores necessários para configurar o frontend.

## Popular Tabelas com Dados de Teste

Após o deploy, você pode popular as tabelas DynamoDB com dados iniciais:

```bash
cd terraform/environments/dev/scripts

# Edite config.json com os dados do seu projeto
python3 seed_data.py
```

O script cria automaticamente serviços, profissionais, clientes e agendamentos de exemplo.

## Nomenclatura

Todos os recursos seguem o padrão: `{project_name}-{environment}-{resource_id}`

Exemplos:
- API Gateway: `barbearia-silva-dev-api`
- Lambda: `barbearia-silva-dev-conversation-webhook`
- DynamoDB: `barbearia-silva-dev-Appointments`

## Tags

Todos os recursos recebem automaticamente:
- `project`: Nome do projeto
- `managedby`: terraform
- `environment`: Ambiente (dev, prod)

## Limpeza

```bash
cd terraform/environments/dev
terraform destroy
```
