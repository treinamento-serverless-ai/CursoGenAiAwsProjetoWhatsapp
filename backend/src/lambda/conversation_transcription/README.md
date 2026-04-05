# conversation_transcription

Transcreve mensagens de audio do WhatsApp usando Amazon Transcribe.

## Funcionalidade

- Faz download do audio via Meta WhatsApp API
- Armazena o audio no S3
- Valida tamanho do arquivo (minimo e maximo configurados no AppConfig)
- Inicia job de transcricao no Amazon Transcribe (pt-BR)
- Aguarda conclusao do job (polling)
- Atualiza o buffer DynamoDB com o texto transcrito
- Em caso de erro, atualiza o buffer com mensagem de falha

## Variaveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `MEDIA_BUCKET_NAME`: Bucket S3 para armazenamento de midias
- `WHATSAPP_SECRET_NAME`: ARN do secret com credenciais da Meta WhatsApp API
- `APPCONFIG_APP_ID`: ID da aplicacao AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuracao AppConfig
