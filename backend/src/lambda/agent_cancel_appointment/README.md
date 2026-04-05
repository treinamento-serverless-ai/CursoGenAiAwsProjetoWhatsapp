# agent_cancel_appointment

Cancela agendamento existente apos validacao de propriedade.

## Funcionalidade

Cancela um agendamento verificando:
- Agendamento existe
- Pertence ao usuario (validacao por telefone)
- Nao esta ja cancelado

Atualiza status para CANCELLED e registra timestamp.

## Parametros

- `appointment_id` (obrigatorio): ID do agendamento a cancelar

## Variaveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Nome da tabela DynamoDB de agendamentos

## Exemplo de Resposta

```json
{
  "message": "Appointment appt-001 cancelled successfully",
  "details": {
    "service": "Corte de Cabelo",
    "professional": "João Silva",
    "date": "2026-02-20T10:00:00"
  }
}
```
