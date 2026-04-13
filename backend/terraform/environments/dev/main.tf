module "whatsapp_agendente" {
  source = "../../infrastructure"

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  # Região AWS (definida no terraform.tfvars)
  aws_region = var.aws_region

  # Nome do ambiente (dev, staging, prod)
  environment = "dev"

  # Nome do projeto (usado como prefixo em todos os recursos)
  project_name = "barbearia-silva"

  # Deploy automático do frontend Angular para S3 a cada terraform apply
  frontend_deploy_enabled = false #true

  # Certificado CA da Meta para mTLS nos webhooks do WhatsApp
  # Download: https://developers.facebook.com/docs/graph-api/webhooks/getting-started/#downloadable-root-certificate
  meta_ca_cert_path = "${path.module}/certs/meta-outbound-api-ca-2025-12.pem"

  # Domínio customizado (opcional, definido no terraform.tfvars)
  custom_domain_name = var.custom_domain_name

  # Instrução customizada do Bedrock Agent (sobrescreve a instrução padrão do módulo)
  bedrock_agent_instruction = file("${path.module}/bedrock_agent_instruction.txt")

  # Usuários iniciais do Cognito (definidos no terraform.tfvars)
  cognito_initial_users = {
    admins        = var.cognito_admin_users
    regular_users = var.cognito_regular_users
  }


  appconfig_settings = {
    business_hours_start          = "05:00"
    business_hours_end            = "23:00"
    business_hours_timezone       = "America/Sao_Paulo"
    max_booking_days              = 90
    inactivity_threshold_seconds  = 5
    audio_processing_grace_period = 15
    closed_message                = "Olá! Nosso horário de atendimento é das __HORARIO_INICIO__ às __HORARIO_FIM__. Por favor, retorne durante o horário de funcionamento."
    banned_message                = "Desculpe, não conseguimos processar sua mensagem no momento. Por favor, entre em contato via telefone para atendimento."
    transcribe_enabled            = false
    transcribe_disabled_message   = "Desculpe, não consigo processar mensagens de áudio no momento. Por favor, envie sua mensagem em texto."
    audio_min_size_kb             = 10
    audio_max_size_kb             = 275
    ai_error_message              = "Desculpe, estou com dificuldades técnicas no momento. Um atendente humano entrará em contato em breve."
    save_messages_after_hours     = true
    reply_with_context            = true
    reply_context_use_last        = true
  }


}
