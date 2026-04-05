# conversation_webhook

Recebe e processa eventos da Meta WhatsApp Business API.

## Funcionalidade

- Valida requisicoes de verificacao do webhook (GET)
- Processa mensagens recebidas (texto, audio, imagens)
- Armazena mensagens no buffer DynamoDB
- Registra/atualiza clientes na tabela de clientes
- Inicia execucao do Step Functions para processar a conversa
- Verifica se ja existe execucao ativa para o usuario antes de iniciar nova
- Trata mensagens de audio: faz download, armazena no S3 e dispara transcricao

## Variaveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `DYNAMODB_CLIENTS_TABLE`: Tabela DynamoDB de clientes
- `STATE_MACHINE_ARN`: ARN do Step Functions
- `SECRET_ARN`: ARN do secret com credenciais da Meta WhatsApp API
- `MEDIA_BUCKET_NAME`: Bucket S3 para armazenamento de midias
- `APPCONFIG_APP_ID`: ID da aplicacao AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuracao AppConfig
