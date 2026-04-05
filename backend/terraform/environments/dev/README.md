# Ambiente de Desenvolvimento

Configuração do ambiente `dev` do projeto Agendente.

## Pré-requisitos

- Terraform >= 1.6.0
- AWS CLI v2 configurado com credenciais válidas

## Configuração de Credenciais AWS

O Terraform precisa de credenciais AWS para provisionar os recursos. Você pode autenticar de diversas formas:

- **AWS SSO (IAM Identity Center):** `aws sso login --profile <seu-profile>`
- **Access Keys:** Configuradas via `aws configure`
- **Environment Variables:** `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`

Após autenticar, exporte o profile (se aplicável):

```bash
export AWS_PROFILE=<seu-profile>
```

> Para mais detalhes sobre autenticação, consulte a [documentação oficial da AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html).

## Deploy

### 1. Configurar Backend State

```bash
cp backend.hcl.example backend.hcl
```

Edite `backend.hcl` com os dados do seu bucket S3 para armazenar o state do Terraform.

### 2. Configurar Variáveis

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edite `terraform.tfvars` com seus valores (região, usuários Cognito, domínio customizado se desejado).

### 3. Executar

```bash
terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

### 4. Ver Outputs

```bash
terraform output
```

Os outputs incluem URLs do API Gateway, IDs do Cognito e outros valores necessários para configurar o frontend.

> Os arquivos `backend.hcl` e `terraform.tfvars` são ignorados pelo git por segurança.

## Domínio Customizado e mTLS (Opcional)

Para habilitar mTLS no webhook do WhatsApp e domínios customizados:

1. Registre um domínio no Route 53
2. Baixe o [certificado CA da Meta](https://developers.facebook.com/docs/graph-api/webhooks/getting-started/#downloadable-root-certificate) e coloque em `certs/`
3. Descomente `custom_domain_name` no `terraform.tfvars`

Para mais detalhes, consulte a [documentação de Custom Domain e mTLS](../../../docs/CUSTOM_DOMAIN_MTLS.md).

## Dados de Teste

Após o deploy, você pode popular as tabelas DynamoDB com dados iniciais:

```bash
cd scripts
python3 seed_data.py
```

Consulte `scripts/README.md` para mais detalhes.

## Limpeza

```bash
terraform destroy
```
