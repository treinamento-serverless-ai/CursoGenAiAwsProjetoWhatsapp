# crud_conversations

Gerencia historico de conversas do WhatsApp via dashboard administrativo.

## Funcionalidade

Esta Lambda fornece acesso ao histórico completo de mensagens trocadas entre clientes e o sistema (IA ou humano) via WhatsApp. É utilizada pelo dashboard administrativo para:
- Visualizar conversas de um cliente específico
- Auditar interações do sistema
- Analisar qualidade do atendimento
- Suporte ao cliente

## Parâmetros

### GET - Listar conversas

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| phone_number | string | Sim | Número de telefone do cliente (formato: 5511999887766) |
| limit | number | Não | Quantidade máxima de mensagens (padrão: 50) |
| last_evaluated_key | string | Não | Token de paginação para próxima página |

## Variáveis de Ambiente

- `DYNAMODB_CONVERSATION_HISTORY_TABLE`: Nome da tabela DynamoDB com histórico de conversas

## Resposta

### Sucesso (200)

```json
{
  "items": [
    {
      "phone_number": "5511988776655",
      "timestamp": 1708876543,
      "sender": "user",
      "content": "Olá, gostaria de agendar um corte",
      "created_at": "2024-02-25T10:15:43Z"
    },
    {
      "phone_number": "5511988776655",
      "timestamp": 1708876550,
      "sender": "ai",
      "content": "Olá! Claro, posso te ajudar com isso...",
      "created_at": "2024-02-25T10:15:50Z"
    }
  ],
  "last_evaluated_key": {...}
}
```

### Campos da resposta

- `sender`: Origem da mensagem
  - `user`: Cliente
  - `ai`: Bedrock Agent
  - `human`: Atendente humano
  - `system`: Sistema (notificações automáticas)

## Erros

- `400`: Parâmetro `phone_number` ausente
- `500`: Erro ao consultar DynamoDB

## Testes

Veja a pasta `examples/` para eventos de teste prontos.
