# conversation_process_and_send

Lambda consolidada que processa mensagens do buffer, invoca o Bedrock Agent e envia a resposta via WhatsApp.

## Funcionalidade

- Busca mensagens pendentes na tabela MessageBuffer
- Salva mensagens do usuario no historico de conversas
- Invoca o Bedrock Agent com o texto consolidado
- Envia resposta da IA para o usuario via Meta WhatsApp API
- Salva resposta da IA no historico de conversas
- Limpa mensagens processadas do buffer
- Em caso de falha do Bedrock ou da Meta API: desabilita IA para o cliente e envia alerta via SNS

Substitui as Lambdas `conversation_invoke_agent` e `conversation_send_message`.

## Variaveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `DYNAMODB_CLIENTS_TABLE`: Tabela DynamoDB de clientes
- `DYNAMODB_CONVERSATION_HISTORY_TABLE`: Tabela DynamoDB de historico de conversas
- `BEDROCK_AGENT_ID`: ID do Bedrock Agent
- `BEDROCK_AGENT_ALIAS_ID`: Alias ID do Bedrock Agent
- `SECRET_ARN`: ARN do secret com credenciais da Meta WhatsApp API
- `SNS_TOPIC_ARN`: ARN do topico SNS para alertas de erro
- `APPCONFIG_APP_ID`: ID da aplicacao AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuracao AppConfig
