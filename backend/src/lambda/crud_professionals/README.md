# crud_professionals

Gerencia profissionais via dashboard administrativo.

## Funcionalidade

Esta Lambda fornece operações CRUD completas para profissionais:
- Listar profissionais com filtros (nome, status ativo/inativo)
- Buscar profissional específico por ID
- Criar novo profissional (ID gerado automaticamente)
- Atualizar dados do profissional
- Deletar profissional
- Ativar/desativar profissional

Utilizada pelo dashboard administrativo para gerenciar a equipe da barbearia.

## Parâmetros

### GET - Listar profissionais

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| page_size | number | Não | Quantidade de itens por página (padrão: 25) |
| is_active | number | Não | Filtrar por status (1=ativo, 0=inativo) |
| name | string | Não | Filtrar por nome (case-insensitive) |
| last_evaluated_key | string | Não | Token de paginação |

### GET - Buscar profissional específico

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do profissional (formato: prof-xxxxxxxxxxxx) |

### POST - Criar profissional

Corpo da requisição (JSON):

```json
{
  "name": "João Silva",
  "specialty": "Cabelereiro",
  "working_days": ["monday", "tuesday", "wednesday"],
  "working_hours": {
    "start": "09:00",
    "end": "18:00"
  },
  "services": [
    {
      "service_id": "svc-001",
      "service_name": "Corte de Cabelo",
      "duration_hours": 0.5,
      "price": 50
    }
  ],
  "scheduling_policy": {
    "type": "FLEXIBLE_MINUTES",
    "allowed_start_minutes": [0, 30],
    "slot_window_hours": 1
  },
  "is_active": true
}
```

**Nota:** O campo `professional_id` é gerado automaticamente pela Lambda.

### PUT - Atualizar profissional

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do profissional (query parameter) |

Corpo: Qualquer campo do profissional pode ser atualizado.

### DELETE - Deletar profissional

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do profissional |

## Variáveis de Ambiente

- `DYNAMODB_PROFESSIONALS_TABLE`: Nome da tabela DynamoDB de profissionais

## Resposta

### POST - Criação (201)

```json
{
  "message": "Professional created",
  "professional_id": "prof-edacee77edd0"
}
```

### GET - Lista (200)

```json
{
  "items": [
    {
      "professional_id": "prof-123",
      "name": "Maria Santos",
      "specialty": "Barba e acabamento",
      "working_days": ["tuesday", "wednesday", "thursday", "friday", "saturday"],
      "working_hours": {
        "start": "10:00",
        "end": "19:00"
      },
      "is_active": true,
      "created_at": "2024-02-20T10:00:00Z"
    }
  ],
  "page_size": 25,
  "last_evaluated_key": {...}
}
```

## Erros

- `400`: Campos obrigatórios ausentes
- `404`: Profissional não encontrado
- `500`: Erro interno (ex: Float types not supported - já corrigido com conversão para Decimal)

## Testes

Veja a pasta `examples/` para eventos de teste prontos.
