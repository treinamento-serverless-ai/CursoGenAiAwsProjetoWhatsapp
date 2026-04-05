module "whatsapp_agendente" {
  source = "../../infrastructure"

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  # Região AWS (definida no terraform.tfvars)
  aws_region = var.aws_region

  # Nome do ambiente (dev, staging, prod)
  environment = "prod"

  # Nome do projeto (usado como prefixo em todos os recursos)
  project_name = "barbearia-silva"

  # Deploy automático do frontend Angular para S3 a cada terraform apply
  frontend_deploy_enabled = true

  # Certificado CA da Meta para mTLS nos webhooks do WhatsApp
  # Download: https://developers.facebook.com/docs/graph-api/webhooks/getting-started/#downloadable-root-certificate
  meta_ca_cert_path = "${path.module}/certs/meta-outbound-api-ca-2025-12.pem"

  # Domínio customizado (opcional, definido no terraform.tfvars)
  custom_domain_name = var.custom_domain_name

  # Instrução customizada do Bedrock Agent (sobrescreve a instrução padrão do módulo)
  # bedrock_agent_instruction = file("${path.module}/bedrock_agent_instruction.txt")

  # Usuários iniciais do Cognito (definidos no terraform.tfvars)
  cognito_initial_users = {
    admins        = var.cognito_admin_users
    regular_users = var.cognito_regular_users
  }
}
