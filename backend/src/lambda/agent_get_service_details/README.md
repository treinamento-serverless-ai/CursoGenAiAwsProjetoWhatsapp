# agent_get_service_details

Retorna detalhes completos de um servico especifico incluindo preco e duracao por profissional.

## Funcionalidade

Busca informacoes detalhadas de um servico mostrando:
- Nome e descricao do servico
- Categoria
- Lista de profissionais que oferecem o servico
- Preco e duracao por profissional

## Parametros

- `service_id` (obrigatorio): ID do servico

## Variaveis de Ambiente

- `DYNAMODB_SERVICES_TABLE`: Nome da tabela DynamoDB de servicos
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
