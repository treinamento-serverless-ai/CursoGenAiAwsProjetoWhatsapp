# ============================================================================
# AWS AppConfig - Application Configuration Management
# ============================================================================

resource "aws_appconfig_application" "main" {
  name        = "${var.project_name}-${var.environment}"
  description = "Configuration management for ${var.project_name} ${var.environment} environment"

  tags = {
    Name = "${var.project_name}-${var.environment}-appconfig"
  }
}

resource "aws_appconfig_environment" "main" {
  name           = var.environment
  application_id = aws_appconfig_application.main.id
  description    = "Environment for ${var.environment}"

  tags = {
    Name = "${var.project_name}-${var.environment}-appconfig-env"
  }
}

resource "aws_appconfig_configuration_profile" "main" {
  application_id = aws_appconfig_application.main.id
  name           = "agent-config"
  description    = "Configuration for Bedrock Agent and Lambda functions"
  location_uri   = "hosted"

  tags = {
    Name = "${var.project_name}-${var.environment}-agent-config"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_appconfig_hosted_configuration_version" "main" {
  application_id           = aws_appconfig_application.main.id
  configuration_profile_id = aws_appconfig_configuration_profile.main.configuration_profile_id
  description              = "Initial configuration"
  content_type             = "application/json"

  content = jsonencode(var.appconfig_settings)
}

resource "aws_appconfig_deployment_strategy" "main" {
  name                           = "${var.project_name}-${var.environment}-immediate"
  description                    = "Immediate deployment strategy"
  deployment_duration_in_minutes = 0
  growth_factor                  = 100
  replicate_to                   = "NONE"
  final_bake_time_in_minutes     = 0

  tags = {
    Name = "${var.project_name}-${var.environment}-deployment-strategy"
  }
}

resource "aws_appconfig_deployment" "main" {
  application_id           = aws_appconfig_application.main.id
  environment_id           = aws_appconfig_environment.main.environment_id
  configuration_profile_id = aws_appconfig_configuration_profile.main.configuration_profile_id
  configuration_version    = aws_appconfig_hosted_configuration_version.main.version_number
  deployment_strategy_id   = aws_appconfig_deployment_strategy.main.id
  description              = "Initial deployment"

  tags = {
    Name = "${var.project_name}-${var.environment}-deployment"
  }
}
