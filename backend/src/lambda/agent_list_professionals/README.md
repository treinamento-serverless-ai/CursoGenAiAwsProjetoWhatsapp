# agent_list_professionals

Lista todos os profissionais ativos com informações resumidas.

## Funcionalidade

Retorna lista de profissionais disponíveis incluindo:
- Nome
- Especialidade
- Anos de experiência (calculado automaticamente)
- Link de rede social

## Parâmetros

Nenhum parâmetro necessário.

## Variáveis de Ambiente

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
