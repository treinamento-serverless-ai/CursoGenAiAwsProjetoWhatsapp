# ============================================================================
# Outputs
# ============================================================================

locals {
  frontend_url  = local.enable_custom_domain ? "https://${local.frontend_domain}" : "http://${aws_s3_bucket.frontend.bucket}.s3-website-${var.aws_region}.amazonaws.com"
  webhook_url   = local.enable_custom_domain ? "https://${local.whatsapp_domain}" : aws_api_gateway_stage.whatsapp.invoke_url
  privacy_url   = "${local.frontend_url}/privacy-policy"

  output_site_section  = var.cognito_allow_public_redirect ? "\n  Site:             ${local.frontend_url}" : ""
  output_local_section = var.cognito_allow_localhost_redirect ? "\n  Teste local:      Abra o terminal no diretório do repositório\n                    cd frontend\n                    ng serve\n                    http://localhost:4200" : ""

  deploy_output = <<-EOT
  ============================================================
  Deploy concluído com sucesso!
  ============================================================
${local.output_site_section}${local.output_local_section}
  Webhook (Meta):   ${local.webhook_url}

  Privacidade:      ${local.privacy_url}
  ============================================================
EOT
}

output "deploy_info" {
  description = "Informações úteis após o deploy"
  value       = local.deploy_output
}
