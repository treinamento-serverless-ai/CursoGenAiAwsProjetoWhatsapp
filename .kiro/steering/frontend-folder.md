---
inclusion: fileMatch
fileMatchPattern: 'frontend/**'
---

# Guia de Operações - Frontend Angular

Este guia deve ser seguido ao trabalhar com o frontend do projeto Agendente.

## Visão Geral

Dashboard Angular 21 para o dono do estabelecimento gerenciar agendamentos, profissionais, serviços, clientes e configurações. Autenticação via Amazon Cognito (OAuth2 Hosted UI).

## Estrutura do Projeto

```
frontend/src/app/
├── app.ts                  # Componente raiz
├── app.routes.ts           # Rotas com lazy loading
├── app.config.ts           # Providers (router, http, animations)
└── agendente/
    ├── components/         # 17 componentes standalone
    │   ├── login/          # Tela de login (Cognito)
    │   ├── callback/       # OAuth2 callback
    │   ├── layout/         # Layout principal (sidebar + content)
    │   ├── home/           # Dashboard inicial
    │   ├── calendar-view/  # Calendário de agendamentos
    │   ├── appointments-list/  # Lista de agendamentos
    │   ├── professionals-list/ # Lista de profissionais
    │   ├── professional-form/  # Formulário de profissional
    │   ├── services-list/      # Lista de serviços
    │   ├── service-form/       # Formulário de serviço
    │   ├── clients-list/       # Lista de clientes
    │   ├── client-details/     # Detalhes do cliente
    │   ├── client-appointments/ # Agendamentos do cliente
    │   ├── config-panel/       # Configurações do sistema
    │   ├── whatsapp-panel/     # Painel de atendimento WhatsApp
    │   ├── conversation-viewer/ # Visualizador de conversas
    │   └── appointment-form/   # Formulário de agendamento
    ├── services/           # 8 services HTTP
    │   ├── auth.ts         # Autenticação Cognito
    │   ├── appointments.ts
    │   ├── professionals.ts
    │   ├── services.ts
    │   ├── clients.ts
    │   ├── config.ts
    │   ├── conversations.ts
    │   └── attendance.ts
    ├── guards/             # Auth guards (authGuard, loginGuard)
    ├── interceptors/       # HTTP interceptor (JWT token)
    └── models/             # Interfaces TypeScript
```

## Padrões do Projeto

### Componentes
- Todos os componentes são **standalone** (sem NgModules)
- Lazy loading via `loadComponent` nas rotas
- Estilo: SCSS

### Autenticação
- OAuth2 via Cognito Hosted UI
- `authInterceptor` injeta token JWT em todas as requisições HTTP
- `authGuard` protege rotas autenticadas
- `loginGuard` redireciona usuários já autenticados

### Ambientes
- `environment.localhost.ts` — desenvolvimento local (`ng serve`)
- `environment.aws.ts` — build para deploy na AWS (`ng build`)
- Ambos não são versionados; usar `environment.example.ts` como template

### API
- Todas as chamadas HTTP passam pelo `authInterceptor`
- Base URL configurada em `environment.apiUrl`
- Endpoints REST mapeados nos services

## Criar Novo Componente

```bash
cd frontend
ng generate component agendente/components/novo-componente --standalone
```

Depois adicionar rota em `app.routes.ts`:

```typescript
{
  path: 'novo',
  loadComponent: () =>
    import('./agendente/components/novo-componente/novo-componente').then(
      (m) => m.NovoComponente,
    ),
},
```

## Criar Novo Service

```bash
cd frontend
ng generate service agendente/services/novo
```

Injetar `HttpClient` e usar `environment.apiUrl` como base:

```typescript
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class NovoService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;
}
```

## Build e Deploy

```bash
# Desenvolvimento local
ng serve

# Build para AWS
ng build --configuration=production
# Arquivos gerados em dist/ para upload no S3
```

## Testes

```bash
ng test  # Vitest
```
