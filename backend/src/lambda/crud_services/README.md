# crud_services

Gerencia servicos oferecidos via dashboard administrativo.

## Funcionalidade

Esta Lambda fornece operações CRUD completas para serviços:
- Listar serviços com filtros (categoria, status ativo/inativo)
- Buscar serviço específico por ID
- Criar novo serviço (ID gerado automaticamente)
- Atualizar dados do serviço
- Deletar serviço
- Ativar/desativar serviço

Utilizada pelo dashboard administrativo para gerenciar o catálogo de serviços da barbearia.

## Parâmetros

### GET - Listar serviços

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| page_size | number | Não | Quantidade de itens por página (padrão: 25) |
| is_active | number | Não | Filtrar por status (1=ativo, 0=inativo) |
| category | string | Não | Filtrar por categoria |
| last_evaluated_key | string | Não | Token de paginação |

### GET - Buscar serviço específico

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do serviço (formato: svc-xxxxxxxxxxxx) |

### POST - Criar serviço

Corpo da requisição (JSON):

```json
{
  "name": "Corte de Cabelo",
  "description": "Corte masculino tradicional",
  "category": "Cabelo",
  "is_active": true
}
```

**Nota:** O campo `service_id` é gerado automaticamente pela Lambda.

### PUT - Atualizar serviço

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do serviço (query parameter) |

Corpo: Qualquer campo do serviço pode ser atualizado.

### DELETE - Deletar serviço

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id | string | Sim | ID do serviço |

## Variáveis de Ambiente

- `DYNAMODB_SERVICES_TABLE`: Nome da tabela DynamoDB de serviços

## Resposta

### POST - Criação (201)

```json
{
  "message": "Service created",
  "service_id": "svc-a1b2c3d4e5f6"
}
```

### GET - Lista (200)

```json
{
  "items": [
    {
      "service_id": "svc-001",
      "name": "Corte de Cabelo",
      "description": "Corte masculino tradicional",
      "category": "Cabelo",
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
- `404`: Serviço não encontrado
- `500`: Erro interno

## Testes

Veja a pasta `examples/` para eventos de teste prontos.
