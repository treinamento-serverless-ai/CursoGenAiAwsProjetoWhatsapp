variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Environment (development, production)"
}

variable "project_name" {
  type        = string
  description = "Project name"
}

variable "enable_api_gateway_logs" {
  type        = bool
  description = "Enable API Gateway CloudWatch logs (useful for debugging)"
  default     = true
}

variable "enable_lambda_traces" {
  type        = bool
  description = "Enable AWS X-Ray tracing for Lambda functions"
  default     = true
}

variable "custom_domain_name" {
  type        = string
  description = "Custom domain name for API Gateway and Frontend (e.g., 'serverlessai.click'). If provided, enables mTLS and custom domains. Domain must be registered and hosted in Route 53."
  default     = null
}

variable "include_environment_in_domain" {
  type        = bool
  description = "Include environment name as prefix in custom domain URLs (e.g., dev.project.domain vs project.domain)"
  default     = true
}

variable "meta_ca_cert_path" {
  type        = string
  description = "Path to the Meta CA certificate .pem file. Required when custom_domain_name is set. Download from: https://developers.facebook.com/docs/graph-api/webhooks/getting-started/#downloadable-root-certificate"
  default     = null
}

variable "bedrock_agent_instruction" {
  type        = string
  description = "Instruction text for Bedrock Agent"
  default     = null
}

variable "bedrock_agent_foundation_model" {
  type        = string
  description = "Foundation model for Bedrock Agent"
  default     = "amazon.nova-lite-v1:0"
}

variable "max_booking_days" {
  type        = number
  description = "Maximum number of days in advance that appointments can be booked"
  default     = 90
}

# ============================================================================
# WhatsApp Configuration Variables
# ============================================================================

variable "whatsapp_phone_number_id" {
  type        = string
  description = "WhatsApp Business Phone Number ID from Meta"
  default     = "PLACEHOLDER_UPDATE_IN_TFVARS"
}

variable "whatsapp_api_version" {
  type        = string
  description = "Meta Graph API version"
  default     = "v22.0"
}

# ============================================================================
# Bedrock Agent Configuration Variables
# ============================================================================

variable "bedrock_agent_alias_id" {
  type        = string
  description = "Bedrock Agent Alias ID (TSTALIASID for draft/dev, PROD for production)"
  default     = "TSTALIASID"
}

# ============================================================================
# CloudWatch Alarms Configuration
# ============================================================================

variable "alarm_evaluation_period_seconds" {
  type        = number
  description = "Period in seconds for CloudWatch alarm evaluation"
  default     = 300 # 5 minutes
}

variable "cloudwatch_alarms_evaluation_periods" {
  type        = number
  description = "Number of periods to evaluate for CloudWatch alarms"
  default     = 3
}

variable "cloudwatch_alarms_datapoints_to_alarm" {
  type        = number
  description = "Number of datapoints that must breach threshold to trigger alarm"
  default     = 3
}

variable "cloudwatch_alarms_threshold" {
  type        = number
  description = "Threshold percentage for error rate alarms"
  default     = 5
}

variable "step_functions_log_retention_days" {
  type        = number
  description = "Number of days to retain Step Functions logs in CloudWatch"
  default     = 7
}

variable "dlq_processor_log_retention_days" {
  type        = number
  description = "Number of days to retain DLQ processor Lambda logs in CloudWatch"
  default     = 7
}

# ============================================================================
# AppConfig Configuration Variables
# ============================================================================

variable "appconfig_settings" {
  type        = map(any)
  description = "AppConfig configuration settings for the application"
  default = {
    business_hours_start          = "08:00"
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

# ============================================================================
# Amazon Cognito Variables
# ============================================================================
variable "cognito_initial_users" {
  description = "Usuários iniciais a serem criados no Cognito organizados por grupo. Usuários já existentes não são afetados."

  type = object({
    admins = optional(list(object({
      name  = string
      email = string
    })), [])

    regular_users = optional(list(object({
      name  = string
      email = string
    })), [])
  })

  default = {
    admins        = []
    regular_users = []
  }
}

# ============================================================================
# CORS Configuration
# ============================================================================
variable "cors_allowed_origins" {
  description = "Allowed origins for CORS. Use '*' for all origins (development), or specific URLs for production (e.g., 'http://localhost:4200' or 'https://meu-app.com')"
  type        = string
  default     = "*"
}

variable "cors_allowed_origins_frontend" {
  description = "Allowed origins for CORS in frontend API endpoints (OpenAPI spec). Comma-separated list or '*' for all origins"
  type        = string
  default     = "*"
}

variable "frontend_dir" {
  description = "Path to the frontend/ directory for automated build and deploy to S3. Relative to the infrastructure/ module directory. Set to null to disable frontend deploy."
  type        = string
  default     = "../../../frontend"
}

variable "frontend_deploy_enabled" {
  description = "Enable automatic frontend build and deploy to S3 on every terraform apply"
  type        = bool
  default     = true
}

# ============================================================================
# Cognito Redirect Configuration
# ============================================================================

variable "cognito_allow_localhost_redirect" {
  description = "Allow Cognito redirect to http://localhost:4200 (for local development with ng serve)"
  type        = bool
  default     = true
}

variable "cognito_allow_public_redirect" {
  description = "Allow Cognito redirect to the public URL (S3 website or CloudFront custom domain)"
  type        = bool
  default     = true
}
