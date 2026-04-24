# Project Structure

## Directory Layout

```
CursoGenAiAwsProjetoWhatsapp/          # Monorepo root
├── README.md                           # Project overview, architecture, quick start
├── LICENSE                             # MIT license
├── .gitignore                          # Root-level ignores
├── backend/                            # Terraform IaC + Python Lambda functions
│   ├── README.md                       # Backend overview and deploy instructions
│   ├── terraform/
│   │   ├── infrastructure/             # Terraform module (all AWS resources)
│   │   │   ├── aws_lambda.tf           # All ~25 Lambdas defined in a single map
│   │   │   ├── aws_api_gateway.tf      # Admin REST API
│   │   │   ├── aws_api_gateway_whatsapp.tf  # WhatsApp webhook API
│   │   │   ├── aws_bedrock_agent.tf    # Bedrock Agent + 8 Action Groups
│   │   │   ├── aws_step_functions.tf   # MessageOrchestrator state machine
│   │   │   ├── aws_dynamodb.tf         # 6 DynamoDB tables
│   │   │   ├── aws_cognito.tf          # User Pool + groups
│   │   │   ├── aws_s3.tf              # 3 S3 buckets
│   │   │   ├── aws_cloudwatch_*.tf     # Dashboard and alarms
│   │   │   ├── openapi_*.yaml          # OpenAPI specs for both APIs
│   │   │   ├── variables.tf            # Input variables
│   │   │   └── outputs.tf             # Terraform outputs
│   │   └── environments/
│   │       └── dev/                    # Dev environment config
│   │           ├── config.tf           # S3 backend + providers
│   │           ├── main.tf             # Module invocation with variable values
│   │           ├── bedrock_agent_instruction.txt  # Custom agent prompt
│   │           └── scripts/            # Seed data scripts (Python)
│   └── src/lambda/                     # ~25 Lambda functions (Python 3.13)
│       ├── agent_*                     # 8 Bedrock Agent Action Groups
│       ├── conversation_*              # 7 WhatsApp message processing functions
│       ├── crud_*                      # 7 Admin dashboard CRUD functions
│       └── scheduled_*                 # 2 CRON-triggered functions
├── frontend/                           # Angular 21 dashboard application
│   ├── README.md                       # Frontend overview
│   ├── package.json                    # Dependencies and scripts
│   ├── angular.json                    # Angular CLI configuration
│   ├── tsconfig*.json                  # TypeScript configs
│   ├── src/
│   │   ├── main.ts                     # Bootstrap entry point
│   │   ├── styles.scss                 # Global styles
│   │   ├── index.html                  # HTML shell
│   │   ├── environments/               # Environment configs (not versioned)
│   │   └── app/
│   │       ├── app.ts                  # Root component
│   │       ├── app.routes.ts           # Route definitions with lazy loading
│   │       ├── app.config.ts           # Application providers
│   │       └── agendente/              # Feature module
│   │           ├── components/         # 17+ standalone components
│   │           ├── services/           # 8 HTTP services
│   │           ├── guards/             # Auth and login guards
│   │           ├── interceptors/       # JWT auth interceptor
│   │           └── models/             # TypeScript interfaces
│   └── dist/                           # Build output (deployed to S3)
├── docs/                               # Architecture documentation (Portuguese)
│   ├── arquitetura.jpg                 # Architecture diagram
│   ├── arquitetura.drawio              # Editable diagram source
│   ├── DYNAMODB_TABLE_SCHEMA.md        # Schema for all 6 tables
│   ├── CONFIGURACOES_E_SEGREDOS.md     # AppConfig, SSM, Secrets Manager
│   ├── STEP_FUNCTIONS.md               # Message orchestration flow
│   ├── CLOUDWATCH_ALARMES_DASHBOARD.md # Monitoring setup
│   ├── SESSION_ATTRIBUTES.md           # Bedrock Agent session handling
│   └── PRIVACY_POLICY.md              # WhatsApp/Meta privacy policy
└── .kiro/
    ├── steering/                       # Kiro steering documents
    ├── specs/                          # Kiro specifications
    └── agents/                         # Agent configurations (MCP servers)
```

## Naming Conventions

### Resource Naming (Terraform)
All AWS resources follow: `{project_name}-{environment}-{resource_id}` (e.g., `barbearia-silva-dev-conversation-webhook`).

### Lambda Functions
- Directory names use `snake_case` with category prefix: `agent_`, `conversation_`, `crud_`, `scheduled_`
- Each Lambda directory contains: `lambda_function.py` (required), `README.md` (required), `examples/` (required), `requirements.txt` (optional)
- Terraform key names use the same `snake_case` directory name

### Frontend Components
- Angular CLI conventions: `kebab-case` directory and file names
- Component classes use `PascalCase` (e.g., `CalendarView`, `WhatsappPanel`)
- Services use `camelCase` filenames (e.g., `auth.ts`, `appointments.ts`)
- All components are standalone (no NgModules)

### Documentation
- `docs/` files use `SCREAMING_SNAKE_CASE.md` for technical documents
- READMEs follow the pattern: `# Agendente — <Context>` at root and backend level

### Code Language
- Variable names, function names, and code identifiers: English
- Documentation text, UI strings, Bedrock Agent instructions: Brazilian Portuguese
- AWS service names always in English

## Architectural Patterns

### Monorepo with Independent Deployables
The repository contains three independent concerns that share no runtime code:
- **backend/**: Deployed via `terraform apply` from `environments/dev/`. Produces AWS infrastructure and Lambda functions.
- **frontend/**: Angular SPA deployed to S3. Can be built independently (`ng build`) or automatically via Terraform.
- **docs/**: Reference documentation only — not deployed, serves as context for developers and AI assistants.

### Backend: Single Terraform Module
All infrastructure is defined in one module (`backend/terraform/infrastructure/`) consumed by environment configs. This avoids module nesting complexity. All Lambdas are defined in a single map in `aws_lambda.tf` with shared IAM, logging, and packaging logic.

### Backend: Lambda Categories as Bounded Contexts
Lambda functions are organized by their trigger source and responsibility:
- `agent_*` → invoked by Bedrock Agent (Action Groups)
- `conversation_*` → invoked by API Gateway webhook, Step Functions, or EventBridge
- `crud_*` → invoked by API Gateway admin endpoints (Cognito-authenticated)
- `scheduled_*` → invoked by EventBridge CRON rules

### Backend: Step Functions for Message Orchestration
WhatsApp message processing uses a Step Functions state machine (MessageOrchestrator) that handles inactivity detection, message batching, audio transcription, and Bedrock Agent invocation — rather than doing this in a single Lambda.

### Frontend: Standalone Components with Lazy Loading
All Angular components are standalone. Routes use `loadComponent` for code splitting. Authentication flows through Cognito OAuth2 Hosted UI with an HTTP interceptor injecting JWT tokens.

### Configuration Hierarchy
Runtime configuration is split across three AWS services by sensitivity and change frequency:
- **Secrets Manager**: Sensitive credentials (Meta WhatsApp tokens)
- **SSM Parameter Store**: Resource identifiers (Bedrock Agent ID, DynamoDB table names)
- **AppConfig**: Business behavior settings (hours, thresholds, AI model config)

## Import and Dependency Patterns

### Backend (Python Lambdas)
- Each Lambda is self-contained with no shared code between functions
- AWS resources (boto3 clients, DynamoDB tables) are initialized at module level (outside the handler) for connection reuse
- Environment variables provide resource names/ARNs injected by Terraform
- No shared utility layer or Lambda layers — each function packages its own dependencies

### Frontend (Angular)
- Feature code lives under `src/app/agendente/` — components, services, guards, interceptors, and models
- Services are `providedIn: 'root'` singletons injected via Angular DI
- Environment config imported from `src/environments/environment.localhost.ts` (swapped to `environment.aws.ts` in production build via `fileReplacements`)
- HTTP calls go through `authInterceptor` which attaches Cognito JWT tokens
- Angular Material components imported directly in each standalone component

### Cross-Concern Dependencies
- Frontend depends on backend outputs (API URL, Cognito IDs) — provided via Terraform-generated environment files or manual configuration
- Backend Lambdas depend on infrastructure (DynamoDB tables, S3 buckets, Bedrock Agent) — wired via Terraform environment variables
- `docs/` has no runtime dependencies — it is consumed by humans and AI assistants for context
