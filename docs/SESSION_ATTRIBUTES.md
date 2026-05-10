# Session Attributes — Propagação do userId e contexto temporal entre Action Groups

## Problema

O Bedrock Agent faz múltiplas chamadas a Action Groups (Lambdas) em uma única turn. Quando o `userId` era passado apenas via `promptSessionAttributes`, o modelo nem sempre propagava esse valor para as chamadas subsequentes, resultando em `userId=None` e falha nas Lambdas.

Além disso, o agente não sabe a data atual por conta própria. Sem essa informação, referências temporais relativas como "próxima segunda" ou "amanhã" causavam alucinações.

## Solução

Passar o `userId` via `sessionAttributes` (para propagação confiável entre Action Groups) e injetar `currentDate` + `currentDayOfWeek` via `promptSessionAttributes` (para que o agente tenha contexto temporal no prompt):

```python
from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/Sao_Paulo")

now = datetime.now(TIMEZONE)
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
            'userId': user_id,
            'currentDate': now.strftime("%Y-%m-%d"),
            'currentDayOfWeek': now.strftime("%A")
        }
    }
)
```

## Diferença entre os dois

| Atributo | Gerenciado por | Propagação entre Action Groups | Visível no prompt do agente |
|----------|---------------|-------------------------------|----------------------------|
| `sessionAttributes` | Runtime do Bedrock Agent | Automática e confiável | Não |
| `promptSessionAttributes` | Modelo (LLM) | Depende do modelo, não confiável | Sim (via placeholder) |

## Por que currentDate vai em promptSessionAttributes

O agente precisa **ler a data no prompt** para resolver expressões como "amanhã", "próxima segunda", "semana que vem". Dados em `sessionAttributes` não aparecem no prompt — servem apenas para as Lambdas dos Action Groups.

Referência AWS: https://aws-samples.github.io/amazon-bedrock-samples/agents-and-function-calling/bedrock-agents/features-examples/06-prompt-and-session-attributes/06-prompt-and-session-attributes/

## Lambdas afetadas

Todas as Lambdas de Action Groups que precisam do `userId` leem de ambos:

```python
user_id = event.get('sessionAttributes', {}).get('userId') or event.get('promptSessionAttributes', {}).get('userId')
```

Lambdas: `agent_check_availability`, `agent_create_appointment`, `agent_cancel_appointment`, `agent_list_user_appointments`.

Lambda que envia: `conversation_process_and_send`.
