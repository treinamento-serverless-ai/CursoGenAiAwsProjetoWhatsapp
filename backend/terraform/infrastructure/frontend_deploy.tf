# ============================================================================
# Automated Frontend Deploy
# ============================================================================
# When frontend_deploy_enabled = true (default), after terraform apply:
# 1. Generates environment.aws.ts and environment.localhost.ts
# 2. Runs ng build (production)
# 3. Syncs build output to S3 frontend bucket
# ============================================================================

resource "null_resource" "frontend_deploy" {
  count = var.frontend_deploy_enabled ? 1 : 0

  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "bash ${abspath("${path.module}/scripts/deploy_frontend.sh")}"

    environment = {
      API_URL              = local.enable_custom_domain ? "https://${local.api_domain}" : aws_api_gateway_stage.main.invoke_url
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
      COGNITO_CLIENT_ID    = aws_cognito_user_pool_client.web.id
      COGNITO_DOMAIN       = "${aws_cognito_user_pool_domain.main.domain}.auth.${var.aws_region}.amazoncognito.com"
      FRONTEND_DOMAIN      = local.enable_custom_domain ? local.frontend_domain : ""
      S3_BUCKET            = aws_s3_bucket.frontend.id
      FRONTEND_DIR         = "${abspath(path.module)}/${var.frontend_dir}"
      AWS_REGION           = var.aws_region
    }
  }
}
