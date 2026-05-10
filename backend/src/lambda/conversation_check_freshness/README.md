# conversation_check_freshness

Verifica se as mensagens do buffer estão prontas para processamento pelo Bedrock Agent.

## Funcionalidade

- Busca configurações de inatividade no AppConfig
- Verifica o timestamp da mensagem mais recente no buffer
- Calcula tempo decorrido desde a última mensagem
- Se o tempo de inatividade não foi atingido, retorna tempo restante de espera
- Verifica se há áudios pendentes de transcrição (conteúdo `None`)
- Gerencia tentativas de transcrição com limite máximo de retries
- Retorna `should_wait: true/false` para o Step Functions decidir se aguarda ou processa

## Variáveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `APPCONFIG_APP_ID`: ID da aplicação AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuração AppConfig
