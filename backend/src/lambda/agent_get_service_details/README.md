# agent_get_service_details

Retorna detalhes completos de um serviço específico incluindo preço e duração por profissional.

## Funcionalidade

Busca informações detalhadas de um serviço mostrando:
- Nome e descrição do serviço
- Categoria
- Lista de profissionais que oferecem o serviço
- Preço e duração por profissional

## Parâmetros

- `service_id` (obrigatório): ID do serviço

## Variáveis de Ambiente

- `DYNAMODB_SERVICES_TABLE`: Nome da tabela DynamoDB de serviços
- `DYNAMODB_PROFESSIONALS_TABLE`: Nome da tabela DynamoDB de profissionais

## Exemplo de Resposta

```json
{
  "service_name": "Corte de Cabelo",
  "description": "Corte masculino tradicional",
  "category": "Cabelo",
  "professionals": [
    {
      "professional_name": "João Silva",
      "professional_id": "prof-001",
      "duration_hours": 0.5,
      "price": 50.00
    }
  ]
}
```
