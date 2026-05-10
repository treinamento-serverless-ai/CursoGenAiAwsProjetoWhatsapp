# agent_list_services

Lista todos os serviços ativos oferecidos pelo estabelecimento.

## Funcionalidade

Retorna catálogo de serviços com:
- ID do serviço
- Nome
- Descrição
- Categoria

## Parâmetros

Nenhum parâmetro necessário.

## Variáveis de Ambiente

- `DYNAMODB_SERVICES_TABLE`: Nome da tabela DynamoDB de serviços

## Exemplo de Resposta

```json
{
  "services": [
    {
      "service_id": "svc-001",
      "name": "Corte de Cabelo",
      "description": "Corte masculino tradicional",
      "category": "Cabelo"
    }
  ]
}
```
