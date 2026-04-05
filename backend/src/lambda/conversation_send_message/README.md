# conversation_send_message

Envia mensagens via WhatsApp API da Meta e marca mensagens como lidas.

## Funcionalidade

- Busca credenciais da Meta API no Secrets Manager
- Envia resposta do agente para o usuario via WhatsApp
- Marca mensagens processadas como lidas na Meta API

Nota: esta Lambda foi substituida por `conversation_process_and_send` que consolida invocacao do agente e envio da resposta em uma unica funcao.

## Variaveis de Ambiente

- `SECRET_ARN`: ARN do secret com credenciais da Meta WhatsApp API
