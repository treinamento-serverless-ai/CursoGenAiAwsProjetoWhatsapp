# crud_appointments

Gerencia agendamentos via dashboard administrativo.

## Funcionalidade

Esta Lambda fornece operações CRUD completas para agendamentos:
- Listar agendamentos com filtros (profissional, status, data)
- Buscar agendamento específico por ID
- Atualizar status do agendamento (PENDING, CONFIRMED, CANCELLED)
- Deletar agendamento

Utilizada pelo dashboard administrativo para gerenciar a agenda da barbearia.

## Parâmetros

### GET - Listar agendamentos

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| page_size | number | Não | Quantidade de itens por página (padrão: 25) |
| professional_id | string | Não | Filtrar por profissional específico |
| status | string | Não | Filtrar por status (PENDING, CONFIRMED, CANCELLED) |
| last_evaluated_key | string | Não | Token de paginação |

### GET - Buscar agendamento específico

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do agendamento (UUID) |

### PUT - Atualizar agendamento

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do agendamento (query parameter) |
| status | string | Não | Novo status (body) |
| scheduled_time | string | Não | Novo horário (body) |

### DELETE - Deletar agendamento

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do agendamento |

## Variáveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Nome da tabela DynamoDB de agendamentos

## Resposta

### GET - Lista (200)

```json
{
  "items": [
    {
      "appointment_id": "f6078c6c-f9a3-48c0-a5e1-b17ec620a8c2",
      "appointment_date": "2024-02-25T10:00:00Z",
      "client_name": "João Silva",
      "client_phone": "5511988776655",
      "professional_id": "prof-123",
      "professional_name": "Maria Santos",
      "service_id": "svc-001",
      "service_name": "Corte de Cabelo",
      "status": "CONFIRMED",
      "created_at": "2024-02-20T15:30:00Z"
    }
  ],
  "page_size": 25,
  "last_evaluated_key": {...}
}
```

### PUT - Atualização (200)

```json
{
  "message": "Appointment updated"
}
```

## Erros

- `400`: Parâmetro obrigatório ausente
- `404`: Agendamento não encontrado
- `500`: Erro interno (ValidationException para palavra reservada 'status' - já corrigido com ExpressionAttributeNames)

## Testes

Veja a pasta `examples/` para eventos de teste prontos.
