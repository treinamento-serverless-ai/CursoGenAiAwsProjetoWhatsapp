# ============================================================================
# AWS Lambda Functions - Agendente Project
# ============================================================================

locals {
  # Mapa consolidado de todas as Lambdas do projeto
  lambdas_config = {
    # -------------------------------------------------------------------------
    # Conversation Lambdas - Interação com WhatsApp API
    # -------------------------------------------------------------------------
    conversation_webhook = {
      name_key                 = "conversation-webhook"
      description              = "Receives and validates WhatsApp messages from Meta API, buffers them in DynamoDB, and triggers Step Functions orchestration - ${var.project_name} ${var.environment}"
      code_path                = "../../src/lambda/conversation_webhook"
      runtime                  = "python3.13"
      memory_size              = 256
      timeout                  = 30
      allow_api_gateway_invoke = true
      environment_variables = {
        MESSAGE_BUFFER_TABLE         = aws_dynamodb_table.message_buffer.name
        CLIENTS_TABLE                = aws_dynamodb_table.clients.name
        CONVERSATION_HISTORY_TABLE   = aws_dynamodb_table.conversation_history.name
        STEP_FUNCTION_ARN            = ""
        SECRET_ARN                   = aws_secretsmanager_secret.whatsapp.arn
        APPCONFIG_APP_ID             = aws_appconfig_application.main.id
        APPCONFIG_ENV_ID             = aws_appconfig_environment.main.environment_id
        APPCONFIG_PROFILE_ID         = aws_appconfig_configuration_profile.main.configuration_profile_id
        WHATSAPP_API_VERSION         = var.whatsapp_api_version
        WHATSAPP_PHONE_NUMBER_ID     = var.whatsapp_phone_number_id
        TRANSCRIPTION_LAMBDA_NAME    = "${var.project_name}-${var.environment}-conversation-transcription"
        PROJECT_NAME                 = var.project_name
        ENVIRONMENT                  = var.environment
      }
    }

    conversation_check_freshness = {
      name_key    = "conversation-check-freshness"
      description = "Checks if messages in buffer are ready to be processed based on inactivity threshold and audio transcription status - ${var.project_name} ${var.environment}"
      code_path   = "../../src/lambda/conversation_check_freshness"
      runtime     = "python3.13"
      memory_size = 128
      timeout     = 30
      environment_variables = {
        MESSAGE_BUFFER_TABLE   = aws_dynamodb_table.message_buffer.name
        APPCONFIG_APP_ID       = aws_appconfig_application.main.id
        APPCONFIG_ENV_ID       = aws_appconfig_environment.main.environment_id
        APPCONFIG_PROFILE_ID   = aws_appconfig_configuration_profile.main.configuration_profile_id
      }
    }

    conversation_process_and_send = {
      name_key      = "conversation-process-and-send"
      enable_alarms = true
      description = "Processes messages with Bedrock Agent and sends responses via WhatsApp - ${var.project_name} ${var.environment}"
      code_path   = "../../src/lambda/conversation_process_and_send"
      runtime     = "python3.13"
      memory_size = 512
      timeout     = 600
      environment_variables = {
        MESSAGE_BUFFER_TABLE       = aws_dynamodb_table.message_buffer.name
        CONVERSATION_HISTORY_TABLE = aws_dynamodb_table.conversation_history.name
        CLIENTS_TABLE              = aws_dynamodb_table.clients.name
        BEDROCK_AGENT_ID           = aws_bedrockagent_agent.agendente.agent_id
        BEDROCK_AGENT_ALIAS_ID     = var.bedrock_agent_alias_id
        WHATSAPP_SECRET_NAME       = aws_secretsmanager_secret.whatsapp.name
        WHATSAPP_API_VERSION       = var.whatsapp_api_version
        WHATSAPP_PHONE_NUMBER_ID   = var.whatsapp_phone_number_id
        APPCONFIG_APP_ID           = aws_appconfig_application.main.id
        APPCONFIG_ENV_ID           = aws_appconfig_environment.main.environment_id
        APPCONFIG_PROFILE_ID       = aws_appconfig_configuration_profile.main.configuration_profile_id
        ALERTS_TOPIC_ARN           = aws_sns_topic.alerts.arn
      }
    }

    conversation_transcription = {
      name_key    = "conversation-transcription"
      description = "Downloads audio files from WhatsApp, stores in S3, and integrates with Amazon Transcribe to convert speech to text - ${var.project_name} ${var.environment}"
      code_path   = "../../src/lambda/conversation_transcription"
      runtime     = "python3.13"
      memory_size = 512
      timeout     = 300
      environment_variables = {
        MEDIA_BUCKET_NAME      = aws_s3_bucket.media.id
        MESSAGE_BUFFER_TABLE   = aws_dynamodb_table.message_buffer.name
        WHATSAPP_SECRET_NAME   = aws_secretsmanager_secret.whatsapp.name
        APPCONFIG_APP_ID       = aws_appconfig_application.main.id
        APPCONFIG_ENV_ID       = aws_appconfig_environment.main.environment_id
        APPCONFIG_PROFILE_ID   = aws_appconfig_configuration_profile.main.configuration_profile_id
      }
    }

    conversation_archiver = {
      name_key    = "conversation-archiver"
      description = "Archives completed conversations from DynamoDB to S3 for long-term storage, triggered by DynamoDB Streams - ${var.project_name} ${var.environment}"
      code_path   = "../../src/lambda/conversation_archiver"
      runtime     = "python3.13"
      memory_size = 256
      timeout     = 60
      environment_variables = {
        S3_ARCHIVE_BUCKET           = aws_s3_bucket.archive.id
        DYNAMODB_CONVERSATION_TABLE = aws_dynamodb_table.conversation_history.name
      }
      permissions = [{
        statement_id = "AllowDynamoDBStream"
        action       = "lambda:InvokeFunction"
        principal    = "dynamodb.amazonaws.com"
        source_arn   = aws_dynamodb_table.conversation_history.stream_arn
      }]
    }

    # -------------------------------------------------------------------------
    # CRUD Lambdas - Operações de dados empresariais
    # -------------------------------------------------------------------------
    crud_appointments = {
      name_key                 = "crud-appointments"
      description              = "Manages appointment CRUD operations (create, read, update, delete) for scheduling system via admin API - ${var.project_name} ${var.environment}"
      code_path                = "../../src/lambda/crud_appointments"
      runtime                  = "python3.13"
      memory_size              = 256
      timeout                  = 30
      allow_api_gateway_invoke = true
      environment_variables = {
        DYNAMODB_APPOINTMENTS_TABLE = aws_dynamodb_table.appointments.name
      }
    }

    crud_professionals = {
      name_key                 = "crud-professionals"
      description              = "Manages professional profiles, working hours, services, and scheduling policies via admin API - ${var.project_name} ${var.environment}"
      code_path                = "../../src/lambda/crud_professionals"
      runtime                  = "python3.13"
      memory_size              = 256
      timeout                  = 30
      allow_api_gateway_invoke = true
      environment_variables = {
        DYNAMODB_PROFESSIONALS_TABLE = aws_dynamodb_table.professionals.name
      }
    }

    crud_services = {
      name_key                 = "crud-services"
      description              = "Manages service catalog (name, description, category) for business offerings via admin API - ${var.project_name} ${var.environment}"
      code_path                = "../../src/lambda/crud_services"
      runtime                  = "python3.13"
      memory_size              = 256
      timeout                  = 30
      allow_api_gateway_invoke = true
      environment_variables = {
        DYNAMODB_SERVICES_TABLE = aws_dynamodb_table.services.name
      }
    }

    crud_clients = {
      name_key                 = "crud-clients"
      description              = "Manages client information and AI settings (ai_enabled, is_banned) via admin API - ${var.project_name} ${var.environment}"
      code_path                = "../../src/lambda/crud_clients"
      runtime                  = "python3.13"
      memory_size              = 256
      timeout                  = 30
      allow_api_gateway_invoke = true
      environment_variables = {
        DYNAMODB_CLIENTS_TABLE = aws_dynamodb_table.clients.name
      }
    }

    crud_attendance = {
      name_key                 = "crud-attendance"
      description              = "Manages human attendance: lists open attendances, sends messages, closes sessions - ${var.project_name} ${var.environment}"
      code_path                = "../../src/lambda/crud_attendance"
      runtime                  = "python3.13"
      memory_size              = 256
      timeout                  = 30
      allow_api_gateway_invoke = true
      dynamodb_tables          = [aws_dynamodb_table.conversation_history.arn]
      environment_variables = {
        DYNAMODB_CLIENTS_TABLE              = aws_dynamodb_table.clients.name
        DYNAMODB_CONVERSATION_HISTORY_TABLE = aws_dynamodb_table.conversation_history.name
        SECRET_ARN                          = aws_secretsmanager_secret.whatsapp.arn
        S3_ARCHIVE_BUCKET                   = aws_s3_bucket.archive.id
      }
    }

    crud_conversations = {
      name_key                 = "crud-conversations"
      description              = "Retrieves conversation history for clients via admin API - ${var.project_name} ${var.environment}"
      code_path                = "../../src/lambda/crud_conversations"
      runtime                  = "python3.13"
      memory_size              = 256
      timeout                  = 30
      allow_api_gateway_invoke = true
      dynamodb_tables          = [aws_dynamodb_table.conversation_history.arn]
      environment_variables = {
        DYNAMODB_CONVERSATION_HISTORY_TABLE = aws_dynamodb_table.conversation_history.name
      }
    }

    crud_config = {
      name_key                 = "crud-config"
      description              = "Manages application configuration via AWS AppConfig for admin API - ${var.project_name} ${var.environment}"
      code_path                = "../../src/lambda/crud_config"
      runtime                  = "python3.13"
      memory_size              = 256
      timeout                  = 30
      allow_api_gateway_invoke = true
      environment_variables = {
        APPCONFIG_APP_ID            = aws_appconfig_application.main.id
        APPCONFIG_ENV_ID            = aws_appconfig_environment.main.environment_id
        APPCONFIG_PROFILE_ID        = aws_appconfig_configuration_profile.main.configuration_profile_id
        APPCONFIG_DEPLOYMENT_STRATEGY_ID = aws_appconfig_deployment_strategy.main.id
      }
    }

    # -------------------------------------------------------------------------
    # Scheduled Lambdas - Rotinas agendadas
    # -------------------------------------------------------------------------
    scheduled_security_monitor = {
      name_key      = "scheduled-security-monitor"
      enable_alarms = true
      description = "Daily security monitoring: validates WhatsApp API token and mTLS certificate expiration, sends SNS alerts when expiring - ${var.project_name} ${var.environment}"
      code_path   = "../../src/lambda/scheduled_security_monitor"
      runtime     = "python3.13"
      memory_size = 128
      timeout     = 60
      environment_variables = merge(
        {
          SECRET_ARN    = aws_secretsmanager_secret.whatsapp.arn
          SNS_TOPIC_ARN = aws_sns_topic.alerts.arn
        },
        local.enable_custom_domain ? {
          MTLS_TRUSTSTORE_BUCKET = aws_s3_bucket.mtls_truststore[0].id
          MTLS_TRUSTSTORE_KEY    = basename(var.meta_ca_cert_path)
        } : {}
      )
    }

    # -------------------------------------------------------------------------
    # Agent Lambdas - Bedrock Agent Action Groups
    # -------------------------------------------------------------------------
    agent_list_professionals = {
      name_key                   = "agent-list-professionals"
      description                = "Lists all active professionals with summary information (name, specialty, experience, social media) - ${var.project_name} ${var.environment}"
      code_path                  = "../../src/lambda/agent_list_professionals"
      runtime                    = "python3.13"
      memory_size                = 256
      timeout                    = 30
      log_retention_days         = 365
      allow_bedrock_agent_invoke = true
      environment_variables = {
        DYNAMODB_PROFESSIONALS_TABLE = aws_dynamodb_table.professionals.name
      }
    }

    agent_check_availability = {
      name_key                   = "agent-check-availability"
      description                = "Checks available appointment slots for professionals within a date range, respects max booking days limit - ${var.project_name} ${var.environment}"
      code_path                  = "../../src/lambda/agent_check_availability"
      runtime                    = "python3.13"
      memory_size                = 256
      timeout                    = 30
      log_retention_days         = 365
      allow_bedrock_agent_invoke = true
      environment_variables = {
        DYNAMODB_APPOINTMENTS_TABLE  = aws_dynamodb_table.appointments.name
        DYNAMODB_PROFESSIONALS_TABLE = aws_dynamodb_table.professionals.name
        APPCONFIG_APPLICATION        = aws_appconfig_application.main.id
        APPCONFIG_ENVIRONMENT        = aws_appconfig_environment.main.environment_id
        APPCONFIG_CONFIGURATION      = aws_appconfig_configuration_profile.main.configuration_profile_id
      }
    }

    agent_create_appointment = {
      name_key                   = "agent-create-appointment"
      description                = "Creates new appointment after validating date limits, professional availability, and service - ${var.project_name} ${var.environment}"
      code_path                  = "../../src/lambda/agent_create_appointment"
      runtime                    = "python3.13"
      memory_size                = 256
      timeout                    = 30
      log_retention_days         = 365
      allow_bedrock_agent_invoke = true
      environment_variables = {
        DYNAMODB_APPOINTMENTS_TABLE  = aws_dynamodb_table.appointments.name
        DYNAMODB_PROFESSIONALS_TABLE = aws_dynamodb_table.professionals.name
        DYNAMODB_CLIENTS_TABLE       = aws_dynamodb_table.clients.name
        DYNAMODB_SERVICES_TABLE      = aws_dynamodb_table.services.name
        APPCONFIG_APPLICATION        = aws_appconfig_application.main.id
        APPCONFIG_ENVIRONMENT        = aws_appconfig_environment.main.environment_id
        APPCONFIG_CONFIGURATION      = aws_appconfig_configuration_profile.main.configuration_profile_id
      }
    }

    agent_list_services = {
      name_key                   = "agent-list-services"
      description                = "Lists all active services offered by the establishment with name, description, and category - ${var.project_name} ${var.environment}"
      code_path                  = "../../src/lambda/agent_list_services"
      runtime                    = "python3.13"
      memory_size                = 256
      timeout                    = 30
      log_retention_days         = 365
      allow_bedrock_agent_invoke = true
      environment_variables = {
        DYNAMODB_SERVICES_TABLE = aws_dynamodb_table.services.name
      }
    }

    agent_get_service_details = {
      name_key                   = "agent-get-service-details"
      description                = "Returns detailed information about a specific service including price and duration by professional - ${var.project_name} ${var.environment}"
      code_path                  = "../../src/lambda/agent_get_service_details"
      runtime                    = "python3.13"
      memory_size                = 256
      timeout                    = 30
      log_retention_days         = 365
      allow_bedrock_agent_invoke = true
      environment_variables = {
        DYNAMODB_SERVICES_TABLE      = aws_dynamodb_table.services.name
        DYNAMODB_PROFESSIONALS_TABLE = aws_dynamodb_table.professionals.name
      }
    }

    agent_list_user_appointments = {
      name_key                   = "agent-list-user-appointments"
      description                = "Lists future appointments for the user based on phone number - ${var.project_name} ${var.environment}"
      code_path                  = "../../src/lambda/agent_list_user_appointments"
      runtime                    = "python3.13"
      memory_size                = 256
      timeout                    = 30
      log_retention_days         = 365
      allow_bedrock_agent_invoke = true
      environment_variables = {
        DYNAMODB_APPOINTMENTS_TABLE = aws_dynamodb_table.appointments.name
      }
    }

    agent_cancel_appointment = {
      name_key                   = "agent-cancel-appointment"
      description                = "Cancels an existing appointment after validating ownership - ${var.project_name} ${var.environment}"
      code_path                  = "../../src/lambda/agent_cancel_appointment"
      runtime                    = "python3.13"
      memory_size                = 256
      timeout                    = 30
      log_retention_days         = 365
      allow_bedrock_agent_invoke = true
      environment_variables = {
        DYNAMODB_APPOINTMENTS_TABLE = aws_dynamodb_table.appointments.name
      }
    }

    agent_resolve_date_reference = {
      name_key                   = "agent-resolve-date-reference"
      description                = "Resolves temporal references into concrete dates using Bedrock LLM - ${var.project_name} ${var.environment}"
      code_path                  = "../../src/lambda/agent_resolve_date_reference"
      runtime                    = "python3.13"
      memory_size                = 128
      timeout                    = 30
      log_retention_days         = 365
      allow_bedrock_agent_invoke = true
      environment_variables = {
        BEDROCK_MODEL_ID = var.bedrock_agent_foundation_model
      }
    }
  }
}

# ============================================================================
# Lambda Function Resources
# ============================================================================

locals {
  # Detecta quais Lambdas têm requirements.txt
  lambdas_with_deps = {
    for key, config in local.lambdas_config :
    key => config
    if fileexists("${path.module}/${config.code_path}/requirements.txt")
  }
  
  lambdas_without_deps = {
    for key, config in local.lambdas_config :
    key => config
    if !fileexists("${path.module}/${config.code_path}/requirements.txt")
  }
}

# Build com dependências
resource "null_resource" "lambda_build_with_deps" {
  for_each = local.lambdas_with_deps

  triggers = {
    code_hash = sha256(join("", [
      filesha256("${path.module}/${each.value.code_path}/lambda_function.py"),
      filesha256("${path.module}/${each.value.code_path}/requirements.txt")
    ]))
  }

  provisioner "local-exec" {
    command = <<-EOT
      mkdir -p ${path.module}/.terraform/lambda_packages
      mkdir -p ${path.module}/.terraform/builds/${each.key}
      cd ${path.module}/.terraform/builds/${each.key}
      rm -rf *
      pip3 install --platform manylinux2014_x86_64 \
        --target . --implementation cp --python-version 3.13 \
        --only-binary=:all: -r ${abspath(path.module)}/${each.value.code_path}/requirements.txt
      cp -r ${abspath(path.module)}/${each.value.code_path}/* .
      find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
      find . -type f -name "*.pyc" -delete 2>/dev/null || true
      find . -type f -name ".DS_Store" -delete 2>/dev/null || true
      rm -rf test tests 2>/dev/null || true
      zip -r ${abspath(path.module)}/.terraform/lambda_packages/${each.key}.zip . -q
    EOT
  }
}

# Build sem dependências
data "archive_file" "lambda_zip" {
  for_each = local.lambdas_without_deps

  type        = "zip"
  source_dir  = "${path.module}/${each.value.code_path}"
  output_path = "${path.module}/.terraform/lambda_packages/${each.key}.zip"
  
  excludes = ["__pycache__", "*.pyc", ".DS_Store", "test", "tests"]
}

# IAM Role para execução das Lambdas
resource "aws_iam_role" "lambda_execution" {
  for_each = local.lambdas_config

  name = "${var.project_name}-${var.environment}-${each.value.name_key}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-${each.value.name_key}-role"
  }
}

# Attach AWS managed policy para logs básicos
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  for_each = local.lambdas_config

  role       = aws_iam_role.lambda_execution[each.key].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach AWS managed policy para X-Ray (quando habilitado)
resource "aws_iam_role_policy_attachment" "lambda_xray" {
  for_each = var.enable_lambda_traces ? toset(keys(local.lambdas_config)) : toset([])

  role       = aws_iam_role.lambda_execution[each.key].name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

# Política para acessar Secrets Manager (apenas para lambdas que precisam)
resource "aws_iam_role_policy" "lambda_secrets_access" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if contains(keys(lookup(config, "environment_variables", {})), "SECRET_ARN") || contains(keys(lookup(config, "environment_variables", {})), "WHATSAPP_SECRET_NAME")
  }

  name = "secrets-access"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue"
      ]
      Resource = aws_secretsmanager_secret.whatsapp.arn
    }]
  })
}

# Política para disparar Step Functions (apenas para webhook)
resource "aws_iam_role_policy" "lambda_stepfunctions_start" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if key == "conversation_webhook"
  }

  name = "stepfunctions-start"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:ListExecutions"
        ]
        Resource = aws_sfn_state_machine.message_orchestrator.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter"
        ]
        Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/${var.environment}/stepfunctions/*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = aws_lambda_function.functions["conversation_transcription"].arn
      }
    ]
  })
}

# Política para publicar no SNS (apenas para lambdas que precisam)
resource "aws_iam_role_policy" "lambda_sns_publish" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if contains(keys(lookup(config, "environment_variables", {})), "SNS_TOPIC_ARN") || contains(keys(lookup(config, "environment_variables", {})), "ALERTS_TOPIC_ARN")
  }

  name = "sns-publish"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "sns:Publish"
      ]
      Resource = aws_sns_topic.alerts.arn
    }]
  })
}

# Política para acessar S3 mTLS truststore (apenas para security monitor)
resource "aws_iam_role_policy" "lambda_s3_mtls_access" {
  for_each = local.enable_custom_domain ? {
    for key, config in local.lambdas_config : key => config
    if contains(keys(lookup(config, "environment_variables", {})), "MTLS_TRUSTSTORE_BUCKET")
  } : {}

  name = "s3-mtls-access"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:GetObjectMetadata",
        "s3:HeadObject"
      ]
      Resource = "${aws_s3_bucket.mtls_truststore[0].arn}/*"
    }]
  })
}

# Política para acessar S3 archive bucket (para arquivamento de conversas)
resource "aws_iam_role_policy" "lambda_s3_archive_access" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if contains(keys(lookup(config, "environment_variables", {})), "S3_ARCHIVE_BUCKET")
  }

  name = "s3-archive-access"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject"
      ]
      Resource = "${aws_s3_bucket.archive.arn}/*"
    }]
  })
}

# Política para acessar DynamoDB (para Lambdas do agente e conversation)
resource "aws_iam_role_policy" "lambda_dynamodb_access" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if contains(keys(lookup(config, "environment_variables", {})), "DYNAMODB_APPOINTMENTS_TABLE") ||
       contains(keys(lookup(config, "environment_variables", {})), "DYNAMODB_SERVICES_TABLE") ||
       contains(keys(lookup(config, "environment_variables", {})), "DYNAMODB_PROFESSIONALS_TABLE") ||
       contains(keys(lookup(config, "environment_variables", {})), "DYNAMODB_CLIENTS_TABLE") ||
       contains(keys(lookup(config, "environment_variables", {})), "DYNAMODB_CONVERSATION_HISTORY_TABLE") ||
       contains(keys(lookup(config, "environment_variables", {})), "MESSAGE_BUFFER_TABLE") ||
       contains(keys(lookup(config, "environment_variables", {})), "CLIENTS_TABLE") ||
       contains(keys(lookup(config, "environment_variables", {})), "CONVERSATION_HISTORY_TABLE")
  }

  name = "dynamodb-access"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ]
      Resource = [
        aws_dynamodb_table.appointments.arn,
        "${aws_dynamodb_table.appointments.arn}/index/*",
        aws_dynamodb_table.professionals.arn,
        aws_dynamodb_table.clients.arn,
        "${aws_dynamodb_table.clients.arn}/index/*",
        aws_dynamodb_table.message_buffer.arn,
        aws_dynamodb_table.services.arn,
        aws_dynamodb_table.conversation_history.arn
      ]
    }]
  })
}

# Política para acessar AppConfig (para Lambdas do agente)
resource "aws_iam_role_policy" "lambda_appconfig_access" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if contains(keys(lookup(config, "environment_variables", {})), "APPCONFIG_APP_ID") || contains(keys(lookup(config, "environment_variables", {})), "APPCONFIG_APPLICATION")
  }

  name = "appconfig-access"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = each.key == "crud_config" ? [
        "appconfig:GetConfiguration",
        "appconfig:GetLatestConfiguration",
        "appconfig:StartConfigurationSession",
        "appconfig:CreateHostedConfigurationVersion",
        "appconfig:GetHostedConfigurationVersion",
        "appconfig:ListHostedConfigurationVersions",
        "appconfig:DeleteHostedConfigurationVersion",
        "appconfig:StartDeployment"
      ] : [
        "appconfig:GetConfiguration",
        "appconfig:GetLatestConfiguration",
        "appconfig:StartConfigurationSession"
      ]
      Resource = "*"
    }]
  })
}

# Política para invocar Bedrock Agent (para conversation_invoke_agent)
resource "aws_iam_role_policy" "lambda_bedrock_invoke" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if contains(keys(lookup(config, "environment_variables", {})), "BEDROCK_AGENT_ID")
  }

  name = "bedrock-invoke"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "bedrock:InvokeAgent"
      ]
      Resource = "arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:agent-alias/${aws_bedrockagent_agent.agendente.agent_id}/*"
    }]
  })
}

# Política para invocar modelos Bedrock (para lambdas com BEDROCK_MODEL_ID)
resource "aws_iam_role_policy" "lambda_bedrock_model_invoke" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if contains(keys(lookup(config, "environment_variables", {})), "BEDROCK_MODEL_ID")
  }

  name = "bedrock-model-invoke"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["bedrock:InvokeModel", "bedrock:Converse"]
      Resource = "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/*"
    }]
  })
}

# Política para acessar S3 e Transcribe (para conversation_transcription)
resource "aws_iam_role_policy" "lambda_transcribe_access" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if key == "conversation_transcription"
  }

  name = "transcribe-s3-access"
  role = aws_iam_role.lambda_execution[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:HeadObject"
        ]
        Resource = "${aws_s3_bucket.media.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob"
        ]
        Resource = "*"
      }
    ]
  })
}

# Função Lambda
resource "aws_lambda_function" "functions" {
  for_each = local.lambdas_config

  depends_on = [
    null_resource.lambda_build_with_deps
  ]

  function_name = "${var.project_name}-${var.environment}-${each.value.name_key}"
  description   = lookup(each.value, "description", "Lambda function for ${var.project_name} - ${var.environment}")

  filename         = "${path.module}/.terraform/lambda_packages/${each.key}.zip"
  source_code_hash = contains(keys(local.lambdas_with_deps), each.key) ? null_resource.lambda_build_with_deps[each.key].triggers.code_hash : data.archive_file.lambda_zip[each.key].output_base64sha256

  role    = aws_iam_role.lambda_execution[each.key].arn
  handler = "lambda_function.lambda_handler"
  runtime = each.value.runtime

  architectures     = [lookup(each.value, "architectures", "arm64")]
  memory_size       = each.value.memory_size
  timeout           = each.value.timeout
  ephemeral_storage {
    size = lookup(each.value, "ephemeral_storage", 512)
  }

  environment {
    variables = merge(
      {
        ENVIRONMENT  = var.environment
        PROJECT_NAME = var.project_name
      },
      each.value.environment_variables != null ? each.value.environment_variables : {}
    )
  }

  tracing_config {
    mode = var.enable_lambda_traces ? "Active" : "PassThrough"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-${each.value.name_key}"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "lambda_logs" {
  for_each = local.lambdas_config

  name              = "/aws/lambda/${aws_lambda_function.functions[each.key].function_name}"
  retention_in_days = lookup(each.value, "log_retention_days", 7)

  tags = {
    Name = "${var.project_name}-${var.environment}-${each.value.name_key}-logs"
  }
}

# Permissões resource-based
resource "aws_lambda_permission" "invoke_permissions" {
  for_each = {
    for item in flatten([
      for lambda_key, lambda_config in local.lambdas_config : [
        for idx, permission in lookup(lambda_config, "permissions", []) : {
          key          = "${lambda_key}-${idx}"
          lambda_key   = lambda_key
          statement_id = permission.statement_id
          action       = permission.action
          principal    = permission.principal
          source_arn   = permission.source_arn
        }
      ]
    ]) : item.key => item
  }

  statement_id  = each.value.statement_id
  action        = each.value.action
  function_name = aws_lambda_function.functions[each.value.lambda_key].function_name
  principal     = each.value.principal
  source_arn    = each.value.source_arn
}

# Permissão para API Gateway (quando allow_api_gateway_invoke = true)
resource "aws_lambda_permission" "api_gateway_invoke" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if lookup(config, "allow_api_gateway_invoke", false)
  }

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.functions[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Permissão para Bedrock Agent (quando allow_bedrock_agent_invoke = true)
resource "aws_lambda_permission" "bedrock_agent_invoke" {
  for_each = {
    for key, config in local.lambdas_config : key => config
    if lookup(config, "allow_bedrock_agent_invoke", false)
  }

  statement_id  = "AllowBedrockAgentInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.functions[each.key].function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = aws_bedrockagent_agent.agendente.agent_arn
}
