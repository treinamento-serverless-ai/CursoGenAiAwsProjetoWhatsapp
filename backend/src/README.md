# Agendente — Lambdas

Todas as funções Lambda do projeto Agendente (Python 3.13), organizadas por categoria.

Para uma visão geral do backend, consulte o [README do backend](../../README.md).

## Estrutura

```
src/lambda/
├── agent_*                 # Action Groups do Bedrock Agent
├── conversation_*          # Processamento de mensagens WhatsApp
├── crud_*                  # Operações CRUD (admin dashboard)
└── scheduled_*             # Tarefas agendadas (CRON jobs)
```

Cada Lambda segue a estrutura:

```
src/lambda/{lambda_name}/
├── lambda_function.py      # Implementação principal (obrigatório)
├── README.md               # Documentação (obrigatório)
├── requirements.txt        # Dependências Python (opcional)
└── examples/               # Test events JSON (obrigatório)
```

## Categorias

### Agent Action Groups

Executam ações solicitadas pelo Bedrock Agent durante conversas WhatsApp:

- `agent_cancel_appointment`: Cancela agendamento existente
- `agent_check_availability`: Verifica horários disponíveis
- `agent_create_appointment`: Cria novo agendamento
- `agent_get_service_details`: Detalhes de um serviço específico
- `agent_list_professionals`: Lista profissionais disponíveis
- `agent_list_services`: Lista serviços oferecidos
- `agent_list_user_appointments`: Lista agendamentos do usuário

### Conversation

Processam mensagens do WhatsApp e orquestram o fluxo de conversa:

- `conversation_archiver`: Arquiva conversas antigas no S3
- `conversation_check_freshness`: Verifica se mensagens estão prontas para processar
- `conversation_process_and_send`: Invoca Bedrock Agent e envia resposta
- `conversation_transcription`: Transcreve áudios com Amazon Transcribe
- `conversation_webhook`: Recebe mensagens da Meta API

### CRUD

Operações de administração via dashboard:

- `crud_appointments`: CRUD de agendamentos
- `crud_attendance`: CRUD de atendimentos
- `crud_clients`: CRUD de clientes
- `crud_config`: CRUD de configurações
- `crud_conversations`: CRUD de conversas
- `crud_professionals`: CRUD de profissionais
- `crud_services`: CRUD de serviços

### Scheduled

Tarefas executadas periodicamente:

- `scheduled_dlq_processor`: Processa mensagens da Dead Letter Queue
- `scheduled_security_monitor`: Monitora segurança e valida tokens

## Padrão de Implementação

### Action Groups do Bedrock

```python
import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def convert_params_to_dict(params_list):
    return {param.get("name"): param.get("value") for param in params_list if param.get("name")}

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = convert_params_to_dict(event.get('parameters', []))
    user_id = event.get('promptSessionAttributes', {}).get('userId')

    try:
        result = {"status": "success"}
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": json.dumps(result, ensure_ascii=False)}}
                }
            }
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": f"Error: {str(e)}"}}
                }
            }
        }
```

### Test Events (examples/)

Arquivos JSON com eventos de teste para o console AWS Lambda. Use nomes descritivos em snake_case (ex: `valid_request.json`, `missing_parameter.json`).

Estrutura para Action Groups:

```json
{
  "actionGroup": "ActionGroupName",
  "function": "function_name",
  "parameters": [
    {
      "name": "param1",
      "type": "string",
      "value": "example_value"
    }
  ],
  "promptSessionAttributes": {
    "userId": "5511999887766"
  }
}
```

Mínimo recomendado por Lambda:
- 1 exemplo de caso de sucesso
- 1 exemplo de caso de erro (parâmetro faltando)
- 1 exemplo de caso extremo (edge case)

### requirements.txt (opcional)

Liste apenas dependências externas. Bibliotecas padrão (boto3, json, os) não precisam ser listadas.

## Integração com Terraform

Após criar uma nova Lambda, adicione-a em `terraform/infrastructure/aws_lambda.tf`:

```hcl
agent_new_function = {
  name_key                   = "agent-new-function"
  description                = "Descrição da função - ${var.project_name} ${var.environment}"
  code_path                  = "../../src/lambda/agent_new_function"
  runtime                    = "python3.13"
  memory_size                = 256
  timeout                    = 30
  log_retention_days         = 365
  allow_bedrock_agent_invoke = true
  environment_variables = {
    DYNAMODB_TABLE = aws_dynamodb_table.table_name.name
  }
}
```

Se for Action Group, adicione também em `terraform/infrastructure/aws_bedrock_agent.tf`:

```hcl
resource "aws_bedrockagent_agent_action_group" "new_function" {
  action_group_name          = "NewFunction"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Descrição de quando usar este action group"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_new_function"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "new_function"
        description = "Descrição da função para o Bedrock Agent"
        parameters {
          map_block_key = "param1"
          type          = "string"
          description   = "Descrição do parâmetro"
          required      = true
        }
      }
    }
  }
}
```

## Deploy

```bash
cd backend/terraform/environments/dev
terraform plan
terraform apply
```

O Terraform automaticamente:
1. Detecta se há `requirements.txt` e instala dependências
2. Cria o pacote ZIP da Lambda
3. Cria a função Lambda na AWS
4. Configura IAM roles e permissões
5. Cria test events no AWS Schemas
6. Registra action group no Bedrock Agent (se aplicável)

## Testes Locais

```bash
cd src/lambda/{lambda_name}
python3 -c "
import json
from lambda_function import lambda_handler

with open('examples/example1.json') as f:
    event = json.load(f)

result = lambda_handler(event, None)
print(json.dumps(result, indent=2))
"
```

## Boas Práticas

- Inicialize recursos AWS fora do handler (reutilização de conexões)
- Use `logger.info()` para eventos importantes e `logger.error()` para erros com stack trace
- Inclua contexto relevante nos logs (user_id, request_id)
- Nunca logue informações sensíveis (tokens, senhas)
- Valide todos os inputs antes de processar
- Retorne resposta estruturada mesmo em caso de erro
- Configure timeout adequado (30s para operações simples, 300s para processamento pesado)

## Referências

- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Bedrock Agent Action Groups](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-groups.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
