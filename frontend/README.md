# Agendente — Frontend

Dashboard Angular para o dono do estabelecimento gerenciar agendamentos, profissionais, serviços, clientes e configurações do sistema.

Para uma visão geral do projeto, consulte o [README principal](../README.md).

## Funcionalidades

- Calendário de agendamentos
- Cadastro de profissionais e serviços
- Lista de clientes com histórico de conversas
- Painel de atendimento WhatsApp (visualização de conversas)
- Configurações do sistema (horário de funcionamento, modo agente IA on/off)
- Autenticação via Amazon Cognito (OAuth2)

## Estrutura

```
frontend/src/app/
├── app.routes.ts               # Rotas com lazy loading
├── app.config.ts               # Providers (router, http, animations)
└── agendente/
    ├── components/             # 17 componentes standalone
    │   ├── login/              # Tela de login (Cognito Hosted UI)
    │   ├── callback/           # OAuth2 callback
    │   ├── layout/             # Layout principal (sidebar + content)
    │   ├── home/               # Dashboard inicial
    │   ├── calendar-view/      # Calendário de agendamentos
    │   ├── appointments-list/  # Lista de agendamentos
    │   ├── professionals-list/ # Lista de profissionais
    │   ├── professional-form/  # Formulário de profissional
    │   ├── services-list/      # Lista de serviços
    │   ├── service-form/       # Formulário de serviço
    │   ├── clients-list/       # Lista de clientes
    │   ├── client-details/     # Detalhes do cliente
    │   ├── client-appointments/# Agendamentos do cliente
    │   ├── config-panel/       # Configurações do sistema
    │   ├── whatsapp-panel/     # Painel de atendimento WhatsApp
    │   ├── conversation-viewer/# Visualizador de conversas
    │   └── appointment-form/   # Formulário de agendamento
    ├── services/               # Services HTTP (auth, appointments, professionals, etc.)
    ├── guards/                 # Auth guards (authGuard, loginGuard)
    ├── interceptors/           # HTTP interceptor (injeta JWT nas requisições)
    └── models/                 # Interfaces TypeScript
```

## Configuração de Ambiente

Os arquivos de ambiente não são versionados pois contêm credenciais. Para configurar:

```bash
cp src/environments/environment.example.ts src/environments/environment.localhost.ts
cp src/environments/environment.example.ts src/environments/environment.aws.ts
```

Edite cada arquivo com os valores gerados pelo `terraform output` do backend:
- `environment.localhost.ts` — usado por `ng serve` (desenvolvimento local)
- `environment.aws.ts` — usado por `ng build` (deploy na AWS)

## Desenvolvimento Local

```bash
npm install
ng serve
```

Acesse `http://localhost:4200/`. A aplicação recarrega automaticamente ao modificar arquivos.

## Build para Deploy

```bash
ng build
```

Os artefatos são gerados em `dist/` e podem ser enviados para o bucket S3 do frontend.

## Testes

```bash
ng test
```

Utiliza [Vitest](https://vitest.dev/) como test runner.

## Tecnologias

- Angular 21 com standalone components
- Lazy loading em todas as rotas
- SCSS para estilos
- Amazon Cognito para autenticação (OAuth2 + JWT)
