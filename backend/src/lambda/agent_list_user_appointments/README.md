# agent_list_user_appointments

Lista agendamentos futuros do usuário baseado no telefone.

## Funcionalidade

- Busca agendamentos futuros (não cancelados) do usuário via GSI `client_phone-appointment_date-index`
- Retorna dados legíveis (sem IDs internos): data, profissional, serviço, status

## Parâmetros

Nenhum parâmetro necessário. O `userId` vem via `sessionAttributes`.

## Variáveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
