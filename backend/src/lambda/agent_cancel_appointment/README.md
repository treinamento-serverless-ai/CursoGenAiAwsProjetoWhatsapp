# agent_cancel_appointment

Cancela agendamento existente do usuário, identificado por nome do serviço e/ou data.

## Funcionalidade

- Busca agendamentos futuros do usuário via GSI `client_phone-appointment_date-index`
- Filtra por nome do serviço (busca fuzzy com `difflib.SequenceMatcher`) e/ou data
- Valida que existe exatamente um match antes de cancelar
- Atualiza status para `CANCELLED`

## Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| service_name | string | Não | Nome do serviço (busca fuzzy) |
| appointment_date | string | Não | Data do agendamento (YYYY-MM-DD) |

Pelo menos um dos parâmetros deve ser fornecido. O `userId` vem via `sessionAttributes`.

## Variáveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
