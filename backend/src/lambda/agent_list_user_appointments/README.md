# agent_list_user_appointments

Lista agendamentos futuros do usuario baseado no telefone.

## Funcionalidade

Busca todos os agendamentos futuros (nao cancelados) do usuario incluindo:
- ID do agendamento
- Data e horario
- Profissional
- Servico
- Status

## Parametros

Nenhum parametro necessario (usa userId da sessao).

## Variaveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Nome da tabela DynamoDB de agendamentos

## Exemplo de Resposta

```json
{
  "appointments": [
    {
      "appointment_id": "appt-001",
      "date": "2026-02-20T10:00:00",
      "professional": "João Silva",
      "service": "Corte de Cabelo",
      "status": "PENDING"
    }
  ]
}
```
