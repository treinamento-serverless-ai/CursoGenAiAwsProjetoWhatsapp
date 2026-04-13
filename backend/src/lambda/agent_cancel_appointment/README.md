# agent_cancel_appointment

Cancela agendamento existente do usuario, identificado por nome do servico e/ou data.

## Funcionalidade

- Busca agendamentos futuros do usuario via GSI `client_phone-appointment_date-index`
- Filtra por nome do servico (busca fuzzy com `difflib.SequenceMatcher`) e/ou data
- Valida que existe exatamente um match antes de cancelar
- Atualiza status para `CANCELLED`

## Parametros

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| service_name | string | Nao | Nome do servico (busca fuzzy) |
| appointment_date | string | Nao | Data do agendamento (YYYY-MM-DD) |

Pelo menos um dos parametros deve ser fornecido. O `userId` vem via `sessionAttributes`.

## Variaveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
