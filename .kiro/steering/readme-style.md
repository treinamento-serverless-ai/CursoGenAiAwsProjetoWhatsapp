---
inclusion: fileMatch
fileMatchPattern: '**/README.md'
---

# Guia de Estilo para READMEs

Padrão a ser seguido ao criar ou editar qualquer README do projeto Agendente.

## Título

Usar o formato: `# Agendente — <Contexto>`

Exemplos:
- `# Agendente — Backend`
- `# Agendente — Frontend`
- `# Agendente — Lambdas`

Para READMEs de subpastas mais profundas (scripts, lambdas individuais), usar título simples descritivo sem o prefixo "Agendente".

## Navegação

Todo README (exceto o da raiz) deve ter um link de volta para o README pai logo após a primeira linha descritiva:

```
Para uma visão geral do projeto, consulte o [README principal](../README.md).
```

## Idioma

- Texto em português brasileiro
- Termos técnicos AWS em inglês (Lambda, Step Functions, DynamoDB, API Gateway, etc.)
- Nomes de variáveis, funções e código em inglês
- Comentários dentro de blocos de código podem ser em português ou inglês

## Formatação

- Sem emojis
- Sem negrito excessivo — usar negrito apenas para avisos críticos (ex: seção de aviso importante no README raiz)
- Headings hierárquicos (`#`, `##`, `###`) para estruturar seções
- Blocos de código com linguagem especificada (```python, ```hcl, ```bash, ```json)
- Tabelas para dados tabulares (endpoints, serviços, parâmetros)
- Listas com `-` para itens

## Estrutura Geral

1. Título
2. Descrição curta (1-2 linhas)
3. Link para README pai (se aplicável)
4. Estrutura de diretórios
5. Seções específicas do contexto (deploy, configuração, uso, etc.)
6. Limpeza / cleanup (se aplicável)

## Estrutura de Diretórios

Sempre incluir um bloco mostrando a árvore de pastas e/ou arquivos importantes. Isso ajuda o leitor a se orientar rapidamente no projeto.

Usar formato de árvore com comentários inline:

```
pasta/
├── subpasta/           # Descrição curta
│   ├── arquivo.tf      # O que esse arquivo faz
│   └── outro.py        # O que esse arquivo faz
└── README.md
```

Não listar todos os arquivos — focar nos mais relevantes para o contexto do README. Agrupar com wildcards quando fizer sentido (ex: `aws_cloudwatch_*.tf`).

## Tom

- Direto e objetivo
- Sem linguagem promocional ou exagerada
- Frases curtas
- Instruir o leitor com comandos e exemplos práticos
- Não repetir informações que já estão em outro README — referenciar via link

## Anonimização

Este é um projeto público. READMEs e scripts não devem conter:
- IDs de contas AWS
- Nomes de profiles específicos
- URLs de SSO ou endpoints reais
- Emails ou nomes pessoais
- Tokens, senhas ou credenciais

Usar placeholders genéricos quando necessário (ex: `<seu-profile>`, `SEU_APPLICATION_ID`).
