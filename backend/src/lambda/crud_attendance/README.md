# crud_attendance

Gerencia atendimentos humanos via dashboard administrativo.

## Funcionalidade

- Lista clientes com conversas ativas (aguardando atendimento humano)
- Envia mensagens como atendente humano via WhatsApp
- Encerra atendimento: arquiva conversa no S3, limpa historico no DynamoDB

## Endpoints

- `GET /api/attendance`: Lista atendimentos abertos com ultima mensagem de cada cliente
- `POST /api/attendance/message`: Envia mensagem como atendente humano
- `POST /api/attendance/close`: Encerra atendimento, arquiva conversa no S3 e limpa historico

## Variaveis de Ambiente

- `DYNAMODB_CLIENTS_TABLE`: Tabela DynamoDB de clientes
- `DYNAMODB_CONVERSATION_HISTORY_TABLE`: Tabela DynamoDB de historico de conversas
- `SECRET_ARN`: ARN do secret com credenciais da Meta WhatsApp API
- `S3_ARCHIVE_BUCKET`: Bucket S3 para arquivamento de conversas
