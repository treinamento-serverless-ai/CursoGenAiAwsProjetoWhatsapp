# agent_list_professionals

Lista todos os profissionais ativos com informacoes resumidas.

## Funcionalidade

Retorna lista de profissionais disponiveis incluindo:
- Nome
- Especialidade
- Anos de experiencia (calculado automaticamente)
- Link de rede social

## Parametros

Nenhum parametro necessario.

## Variaveis de Ambiente

- `DYNAMODB_PROFESSIONALS_TABLE`: Nome da tabela DynamoDB de profissionais

## Exemplo de Resposta

```json
{
  "professionals": [
    {
      "name": "João Silva",
      "specialty": "Corte de cabelo cacheado",
      "years_experience": 5.2,
      "social_media": "https://instagram.com/joaosilva"
    }
  ]
}
```
