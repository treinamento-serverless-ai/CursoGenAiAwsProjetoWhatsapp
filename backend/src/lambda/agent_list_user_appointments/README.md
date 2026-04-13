# agent_list_user_appointments

Lista agendamentos futuros do usuario baseado no telefone.

## Funcionalidade

- Busca agendamentos futuros (nao cancelados) do usuario via GSI `client_phone-appointment_date-index`
- Retorna dados legiveis (sem IDs internos): data, profissional, servico, status

## Parametros

Nenhum parametro necessario. O `userId` vem via `sessionAttributes`.

## Variaveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
