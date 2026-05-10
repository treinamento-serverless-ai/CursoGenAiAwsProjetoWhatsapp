# conversation_process_and_send

Lambda consolidada que processa mensagens do buffer, invoca o Bedrock Agent e envia a resposta via WhatsApp.

## Funcionalidade

- Busca mensagens pendentes na tabela MessageBuffer
- Salva mensagens do usuário no histórico de conversas
- Invoca o Bedrock Agent com o texto consolidado, passando `userId` via `sessionAttributes` e `promptSessionAttributes`
- Envia resposta da IA para o usuário via Meta WhatsApp API
- Salva resposta da IA no histórico de conversas
- Limpa mensagens processadas do buffer
- Em caso de falha: envia mensagem de erro configurável (AppConfig) e alerta via SNS

## Session Attributes

O `userId` (telefone do cliente) é passado ao Bedrock Agent via:
- `sessionAttributes`: persistido pelo runtime do Agent, propagado automaticamente para todos os Action Groups
- `promptSessionAttributes`: injetado no prompt do modelo (redundância para userId, essencial para contexto temporal)

Além do `userId`, os seguintes atributos temporais são injetados em `promptSessionAttributes` a cada turn:
- `currentDate`: data atual no fuso America/Sao_Paulo (YYYY-MM-DD)
- `currentDayOfWeek`: dia da semana em inglês (e.g. "Monday")

Isso permite que o agente resolva referências temporais relativas ("amanhã", "próxima segunda") sem precisar de um Action Group dedicado.

## Variáveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `DYNAMODB_CLIENTS_TABLE`: Tabela DynamoDB de clientes
- `DYNAMODB_CONVERSATION_HISTORY_TABLE`: Tabela DynamoDB de histórico de conversas
- `BEDROCK_AGENT_ID`: ID do Bedrock Agent
- `BEDROCK_AGENT_ALIAS_ID`: Alias ID do Bedrock Agent
- `SECRET_ARN`: ARN do secret com credenciais da Meta WhatsApp API
- `SNS_TOPIC_ARN`: ARN do tópico SNS para alertas de erro
- `APPCONFIG_APP_ID`: ID da aplicação AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuração AppConfig
