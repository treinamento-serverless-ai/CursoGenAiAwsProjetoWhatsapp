# conversation_webhook

Recebe e processa eventos da Meta WhatsApp Business API.

## Funcionalidade

- Valida requisições de verificação do webhook (GET)
- Processa mensagens recebidas (texto, áudio, imagens)
- Armazena mensagens no buffer DynamoDB
- Registra/atualiza clientes na tabela de clientes
- Inicia execução do Step Functions para processar a conversa
- Verifica se já existe execução ativa para o usuário antes de iniciar nova
- Trata mensagens de áudio: faz download, armazena no S3 e dispara transcrição

## Variáveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `DYNAMODB_CLIENTS_TABLE`: Tabela DynamoDB de clientes
- `STATE_MACHINE_ARN`: ARN do Step Functions
- `SECRET_ARN`: ARN do secret com credenciais da Meta WhatsApp API
- `MEDIA_BUCKET_NAME`: Bucket S3 para armazenamento de mídias
- `APPCONFIG_APP_ID`: ID da aplicação AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuração AppConfig
