# Technical Stack

## Languages and Runtimes

- **Python 3.13**: All Lambda functions (~25 functions). No external frameworks — uses boto3 and standard library only.
- **TypeScript ~5.9**: Frontend Angular application and build tooling.
- **HCL (Terraform)**: All infrastructure definitions. Single module in `backend/terraform/infrastructure/` consumed by environment configs.

## Frameworks and Libraries

### Backend (Python Lambdas)
- **boto3**: AWS SDK for DynamoDB, S3, Bedrock, Transcribe, SQS, SSM, Secrets Manager, AppConfig interactions
- No web frameworks — Lambdas receive events directly from API Gateway, Step Functions, EventBridge, or Bedrock Agent

### Frontend (Angular Dashboard)
- **Angular ^21.1.0**: Standalone components (no NgModules), lazy-loaded routes, SCSS styling
- **Angular Material ^21.1.5** + **Angular CDK ^21.1.5**: UI component library
- **amazon-cognito-identity-js ^6.3.12**: Cognito authentication (OAuth2 Hosted UI flow)
- **RxJS ~7.8**: Reactive programming for HTTP and async operations
- **Express ^5.1.0**: SSR server (Angular SSR support, though `outputMode: "static"` is used for production)

### Frontend Dev Dependencies
- **@angular/build ^21.1.2**: Vite-based build system (replaces Webpack)
- **@angular/cli ^21.1.2**: CLI tooling for scaffolding, serving, building
- **TypeScript ~5.9.2**: Strict TypeScript compilation

## Infrastructure and Cloud Services

### IaC
- **Terraform**: Single module architecture with environment-specific configs. Backend state stored in S3. Provider version constraints in `versions.tf`.

### AWS Services Used

| Layer | Services |
|-------|----------|
| API | API Gateway (REST) with mTLS + Cognito JWT authorizer. Two separate APIs: admin (OpenAPI spec) and WhatsApp webhook. |
| Compute | Lambda (Python 3.13, ~25 functions), Step Functions (MessageOrchestrator state machine) |
| AI/ML | Bedrock (Agent with 8 Action Groups, foundation model: amazon.nova-lite-v1:0), Transcribe (audio-to-text) |
| Data | DynamoDB (6 tables, PAY_PER_REQUEST mode), S3 (3 buckets: frontend hosting, media, archive) |
| Configuration | AppConfig (runtime behavior config), SSM Parameter Store (resource IDs/ARNs), Secrets Manager (Meta WhatsApp credentials) |
| Auth | Cognito User Pool with admin/regular groups, OAuth2 Hosted UI |
| Observability | CloudWatch (dashboard, alarms, logs), X-Ray (Lambda tracing), SNS (alert notifications) |
| Scheduling | EventBridge (CRON rules for security monitoring and DLQ processing) |
| Queues | SQS with Dead Letter Queues |
| DNS/CDN | Route 53, CloudFront (optional), ACM (certificates) |

## Development Tools

- **Angular CLI**: `ng serve` for local dev, `ng build --configuration=production` for deploy
- **npm 10.9.4**: Package manager (lockfile committed)
- **Prettier**: Code formatting (configured in package.json — single quotes, 100 char width, Angular HTML parser)
- **Terraform CLI**: `terraform init/plan/apply/destroy` workflow
- **AWS CLI**: Used by Terraform for S3 sync (frontend deploy) and by seed scripts
- **Python 3**: Local Lambda testing via direct script execution (no test framework)
- **Vitest**: Angular test runner (configured via `ng test`, though tests are skipped by default in schematics)

## Technical Constraints

- **Vibe Coding origin**: The entire codebase was generated via AI-assisted development. It is explicitly not production-ready and may contain security flaws. All code should be reviewed before any real-world use.
- **Region**: Default deployment region is `us-east-1`. Bedrock model availability may constrain region choice.
- **Bedrock model**: Uses `amazon.nova-lite-v1:0` by default. Requires Bedrock access enabled in the AWS account.
- **WhatsApp Business API**: Requires a Meta Business account with WhatsApp Business API configured. Meta CA certificate needed for mTLS.
- **No unit test coverage**: Angular schematics have `skipTests: true` for all generators. Lambda functions have example test events but no automated test suite.
- **Single environment**: Only `dev` environment is configured. Production would need separate `terraform.tfvars` and potentially different AppConfig deployment strategies.
- **Frontend deploy coupling**: By default, `terraform apply` triggers frontend build and S3 deploy. Can be disabled via `frontend_deploy_enabled = false`.
- **Language**: All documentation, UI text, and Bedrock Agent instructions are in Brazilian Portuguese. Code identifiers and variable names are in English.
