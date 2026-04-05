# ============================================================================
# AWS Secrets Manager - Agendente Project
# ============================================================================

resource "aws_secretsmanager_secret" "whatsapp" {
  name        = "${var.project_name}/${var.environment}/whatsapp-${random_id.unique_suffix.hex}"
  description = "WhatsApp API credentials and tokens"

  tags = {
    Name = "${var.project_name}-${var.environment}-whatsapp-secret"
  }
}

# Placeholder - usuário deve atualizar manualmente via console
resource "aws_secretsmanager_secret_version" "whatsapp" {
  secret_id = aws_secretsmanager_secret.whatsapp.id
  secret_string = jsonencode({
    ACCESS_TOKEN    = "PLACEHOLDER_UPDATE_VIA_CONSOLE"
    API_VERSION     = "PLACEHOLDER_UPDATE_VIA_CONSOLE"
    APP_ID          = "PLACEHOLDER_UPDATE_VIA_CONSOLE"
    APP_SECRET      = "PLACEHOLDER_UPDATE_VIA_CONSOLE"
    PHONE_NUMBER_ID = "PLACEHOLDER_UPDATE_VIA_CONSOLE"
    VERIFY_TOKEN    = "PLACEHOLDER_UPDATE_VIA_CONSOLE"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}
