---
inclusion: fileMatch
fileMatchPattern: '**/README.md'
---

# Guia de Estilo para READMEs

Padrao a ser seguido ao criar ou editar qualquer README do projeto Agendente.

## Titulo

Usar o formato: `# Agendente — <Contexto>`

Exemplos:
- `# Agendente — Backend`
- `# Agendente — Frontend`
- `# Agendente — Lambdas`

Para READMEs de subpastas mais profundas (scripts, lambdas individuais), usar titulo simples descritivo sem o prefixo "Agendente".

## Navegacao

Todo README (exceto o da raiz) deve ter um link de volta para o README pai logo apos a primeira linha descritiva:

```
Para uma visao geral do projeto, consulte o [README principal](../README.md).
```

## Idioma

- Texto em portugues brasileiro
- Termos tecnicos AWS em ingles (Lambda, Step Functions, DynamoDB, API Gateway, etc.)
- Nomes de variaveis, funcoes e codigo em ingles
- Comentarios dentro de blocos de codigo podem ser em portugues ou ingles

## Formatacao

- Sem emojis
- Sem negrito excessivo — usar negrito apenas para avisos criticos (ex: secao de aviso importante no README raiz)
- Headings hierarquicos (`#`, `##`, `###`) para estruturar secoes
- Blocos de codigo com linguagem especificada (```python, ```hcl, ```bash, ```json)
- Tabelas para dados tabulares (endpoints, servicos, parametros)
- Listas com `-` para itens

## Estrutura Geral

1. Titulo
2. Descricao curta (1-2 linhas)
3. Link para README pai (se aplicavel)
4. Estrutura de diretorios
5. Secoes especificas do contexto (deploy, configuracao, uso, etc.)
6. Limpeza / cleanup (se aplicavel)

## Estrutura de Diretorios

Sempre incluir um bloco mostrando a arvore de pastas e/ou arquivos importantes. Isso ajuda o leitor a se orientar rapidamente no projeto.

Usar formato de arvore com comentarios inline:

```
pasta/
├── subpasta/           # Descricao curta
│   ├── arquivo.tf      # O que esse arquivo faz
│   └── outro.py        # O que esse arquivo faz
└── README.md
```

Nao listar todos os arquivos — focar nos mais relevantes para o contexto do README. Agrupar com wildcards quando fizer sentido (ex: `aws_cloudwatch_*.tf`).

## Tom

- Direto e objetivo
- Sem linguagem promocional ou exagerada
- Frases curtas
- Instruir o leitor com comandos e exemplos praticos
- Nao repetir informacoes que ja estao em outro README — referenciar via link

## Anonimizacao

Este e um projeto publico. READMEs e scripts nao devem conter:
- IDs de contas AWS
- Nomes de profiles especificos
- URLs de SSO ou endpoints reais
- Emails ou nomes pessoais
- Tokens, senhas ou credenciais

Usar placeholders genericos quando necessario (ex: `<seu-profile>`, `SEU_APPLICATION_ID`).
