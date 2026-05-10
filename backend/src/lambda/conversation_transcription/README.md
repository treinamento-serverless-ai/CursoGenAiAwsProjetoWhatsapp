# conversation_transcription

Transcreve mensagens de áudio do WhatsApp usando Amazon Transcribe.

## Funcionalidade

- Faz download do áudio via Meta WhatsApp API
- Armazena o áudio no S3
- Valida tamanho do arquivo (mínimo e máximo configurados no AppConfig)
- Inicia job de transcrição no Amazon Transcribe (pt-BR)
- Aguarda conclusão do job (polling)
- Atualiza o buffer DynamoDB com o texto transcrito
- Em caso de erro, atualiza o buffer com mensagem de falha

## Variáveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `MEDIA_BUCKET_NAME`: Bucket S3 para armazenamento de mídias
- `WHATSAPP_SECRET_NAME`: ARN do secret com credenciais da Meta WhatsApp API
- `APPCONFIG_APP_ID`: ID da aplicação AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuração AppConfig
