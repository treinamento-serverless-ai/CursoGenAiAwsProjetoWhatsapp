# conversation_check_freshness

Verifica se as mensagens do buffer estao prontas para processamento pelo Bedrock Agent.

## Funcionalidade

- Busca configuracoes de inatividade no AppConfig
- Verifica o timestamp da mensagem mais recente no buffer
- Calcula tempo decorrido desde a ultima mensagem
- Se o tempo de inatividade nao foi atingido, retorna tempo restante de espera
- Verifica se ha audios pendentes de transcricao (conteudo `None`)
- Gerencia tentativas de transcricao com limite maximo de retries
- Retorna `should_wait: true/false` para o Step Functions decidir se aguarda ou processa

## Variaveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `APPCONFIG_APP_ID`: ID da aplicacao AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuracao AppConfig
