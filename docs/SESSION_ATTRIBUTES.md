# Session Attributes — Propagacao do userId entre Action Groups

## Problema

O Bedrock Agent faz multiplas chamadas a Action Groups (Lambdas) em uma unica turn. Quando o `userId` era passado apenas via `promptSessionAttributes`, o modelo nem sempre propagava esse valor para as chamadas subsequentes, resultando em `userId=None` e falha nas Lambdas.

## Solucao

Passar o `userId` via `sessionAttributes` (alem de `promptSessionAttributes`) na chamada `invoke_agent`:

```python
bedrock_response = bedrock_client.invoke_agent(
    agentId=agent_id,
    agentAliasId=alias_id,
    sessionId=session_id,
    inputText=message,
    sessionState={
        'sessionAttributes': {
            'userId': user_id
        },
        'promptSessionAttributes': {
            'userId': user_id
        }
    }
)
```

## Diferenca entre os dois

| Atributo | Gerenciado por | Propagacao entre Action Groups |
|----------|---------------|-------------------------------|
| `sessionAttributes` | Runtime do Bedrock Agent | Automatica e confiavel |
| `promptSessionAttributes` | Modelo (LLM) | Depende do modelo, nao confiavel |

## Lambdas afetadas

Todas as Lambdas de Action Groups que precisam do `userId` leem de ambos:

```python
user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
```

Lambdas: `agent_check_availability`, `agent_create_appointment`, `agent_cancel_appointment`, `agent_list_user_appointments`.

Lambda que envia: `conversation_process_and_send`.
