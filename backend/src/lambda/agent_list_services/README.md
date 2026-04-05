# agent_list_services

Lista todos os servicos ativos oferecidos pelo estabelecimento.

## Funcionalidade

Retorna catalogo de servicos com:
- ID do servico
- Nome
- Descricao
- Categoria

## Parametros

Nenhum parametro necessario.

## Variaveis de Ambiente

- `DYNAMODB_SERVICES_TABLE`: Nome da tabela DynamoDB de servicos

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
