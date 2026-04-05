---
inclusion: fileMatch
fileMatchPattern: 'docs/**'
---

# Guia de Operações - Documentação do Projeto

Este guia deve ser seguido ao trabalhar com a documentação do projeto Agendente.

## Visão Geral

A pasta `docs/` contém a documentação técnica e de arquitetura do projeto. Todos os documentos são escritos em português brasileiro (exceto termos técnicos).

## Estrutura

```
docs/
├── arquitetura.jpg                     # Diagrama de arquitetura
├── DESCRICAO_ARQUITETURA.md            # Visão completa da arquitetura e serviços
├── FLUXO_CONVERSA_PADRAO.md            # Fluxo de negócio do agendamento
├── FLUXO_PROCESSAMENTO_MENSAGENS.md    # Fluxo técnico (Step Functions)
├── DYNAMODB_TABLE_SCHEMA.md            # Schema das 6 tabelas DynamoDB
├── BEDROCK_AGENT_CONFIGURATION.md      # Boas práticas para configurar o agente
├── API_FRONTEND_ENDPOINTS.md           # Endpoints REST do dashboard
├── API_DEVELOPMENT_WORKFLOW.md         # Workflow de desenvolvimento da API
├── CONFIGURACOES_E_SEGREDOS.md         # AppConfig, SSM, Secrets Manager
├── CUSTOM_DOMAIN_MTLS.md              # Domínio customizado e mTLS
├── CLOUDWATCH_ALARMES_DASHBOARD.md     # Alarmes e dashboard CloudWatch
└── ACTION_GROUP_RESOLVE_DATE.md        # Action Group de resolução de datas
```

## Regras de Edição

### Consistência
- Manter documentos sincronizados com o código. Se uma Lambda, tabela ou endpoint mudar, atualizar o documento correspondente.
- Nomes de recursos devem usar a convenção `{project_name}-{environment}-{resource_id}`.

### Formato
- Usar Markdown com headings hierárquicos (`#`, `##`, `###`)
- Tabelas para parâmetros, endpoints e schemas
- Blocos de código com linguagem especificada (```python, ```hcl, ```json, ```bash)
- Emojis para destaques: ⚠️ avisos, ✅ boas práticas, ❌ anti-patterns, 💡 dicas

### Idioma
- Texto em português brasileiro
- Termos técnicos AWS em inglês (Lambda, Step Functions, DynamoDB, etc.)
- Nomes de variáveis e código em inglês

## Quando Atualizar

- Nova Lambda criada → atualizar `DESCRICAO_ARQUITETURA.md` e `FLUXO_PROCESSAMENTO_MENSAGENS.md` se aplicável
- Novo endpoint → atualizar `API_FRONTEND_ENDPOINTS.md`
- Nova tabela ou GSI → atualizar `DYNAMODB_TABLE_SCHEMA.md`
- Mudança no fluxo do Step Functions → atualizar `FLUXO_PROCESSAMENTO_MENSAGENS.md`
- Nova configuração AppConfig → atualizar `CONFIGURACOES_E_SEGREDOS.md`
