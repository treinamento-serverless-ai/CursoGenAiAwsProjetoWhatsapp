# conversation_archiver

Lambda placeholder para arquivamento de conversas no S3.

## Funcionalidade

Responsavel por arquivar conversas finalizadas do DynamoDB para o S3 em formato JSON com particionamento Hive-style (otimizado para consultas no AWS Athena).

Atualmente contem apenas um handler placeholder. A logica de arquivamento via dashboard esta implementada em `crud_attendance`.

## Variaveis de Ambiente

Nenhuma variavel de ambiente configurada (placeholder).
