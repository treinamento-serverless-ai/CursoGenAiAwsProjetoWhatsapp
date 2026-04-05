# conversation_invoke_agent

Invoca o Bedrock Agent com mensagens acumuladas no buffer do usuario.

## Funcionalidade

- Busca mensagens pendentes na tabela MessageBuffer
- Ordena por timestamp e concatena o conteudo
- Invoca o Bedrock Agent com o texto consolidado
- Limpa o buffer apos processamento
- Retorna a resposta do agente para o Step Functions

Nota: esta Lambda foi substituida por `conversation_process_and_send` que consolida invocacao do agente e envio da resposta em uma unica funcao.

## Variaveis de Ambiente

- `MESSAGE_BUFFER_TABLE`: Tabela DynamoDB do buffer de mensagens
- `BEDROCK_AGENT_ID`: ID do Bedrock Agent
- `BEDROCK_AGENT_ALIAS_ID`: Alias ID do Bedrock Agent
