# Terraform - Infraestrutura

## Estrutura

```
terraform/
├── environments/
│   └── dev/                      # Ambiente de desenvolvimento
│       ├── config.tf             # Backend S3 + providers
│       ├── main.tf               # Módulo + variáveis do ambiente
│       ├── terraform.tfvars      # Valores das variáveis (não versionado)
│       └── certs/                # Certificado Meta CA para mTLS (não versionado)
│           └── meta-outbound-api-ca-2025-12.pem
└── infrastructure/               # Módulo compartilhado
    ├── variables.tf
    ├── aws_api_gateway.tf
    ├── aws_api_gateway_whatsapp.tf
    ├── aws_custom_domains.tf
    ├── aws_s3_mtls.tf
    ├── aws_lambda.tf
    └── ...
```

## Deploy

```bash
cd terraform/environments/dev

# 1. Copiar templates
cp backend.hcl.example backend.hcl
cp terraform.tfvars.example terraform.tfvars

# 2. Editar backend.hcl e terraform.tfvars com seus valores

# 3. Inicializar e aplicar
terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

## Custom Domain + mTLS

O projeto suporta dois modos de operação:

### Sem custom domain (padrão)

Não requer domínio registrado nem certificado Meta. A API usa a URL padrão do API Gateway:

```
https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/
```

No `terraform.tfvars`, deixe `custom_domain_name` comentado ou não defina.

### Com custom domain + mTLS

Habilita domínios customizados e mTLS (Mutual TLS) para o webhook WhatsApp:

| Subdomínio | Uso |
|---|---|
| `whatsapp.{env}.{project}.{domain}` | Webhook WhatsApp (com mTLS) |
| `api.{env}.{project}.{domain}` | API admin |
| `{env}.{project}.{domain}` | Frontend (CloudFront) |

#### Pré-requisitos

1. Domínio registrado com hosted zone no Route 53
2. Certificado Meta CA para mTLS do webhook WhatsApp

#### Configurar certificado Meta CA

A Meta assina os webhooks com certificado mTLS. Desde 31 de março de 2026, a Meta usa seu próprio CA (`Meta Outbound API CA 2025-12`).

1. Baixe o certificado em: https://developers.facebook.com/docs/graph-api/webhooks/getting-started/#downloadable-root-certificate
2. Extraia o `.pem` e coloque em `terraform/environments/<env>/certs/`
3. No `terraform.tfvars`, defina:

```hcl
custom_domain_name = "seu-dominio.com"
```

4. Execute `terraform apply`

#### Desabilitar custom domain

Para voltar ao modo sem custom domain, comente ou remova a variável:

```hcl
# custom_domain_name = "seu-dominio.com"
```

Isso remove: custom domains, certificados ACM, registros Route 53, CloudFront, bucket mTLS e o truststore. A API passa a usar a URL padrão do API Gateway.
