# ============================================================================
# AWS Systems Manager Parameter Store - Agendente Project
# ============================================================================

# WhatsApp Configuration Parameters
resource "aws_ssm_parameter" "whatsapp_phone_number_id" {
  name        = "/${var.project_name}/${var.environment}/whatsapp/phone_number_id"
  description = "WhatsApp Business Phone Number ID from Meta"
  type        = "String"
  value       = var.whatsapp_phone_number_id

  tags = {
    Name = "${var.project_name}-${var.environment}-whatsapp-phone-number-id"
  }
}

resource "aws_ssm_parameter" "whatsapp_api_version" {
  name        = "/${var.project_name}/${var.environment}/whatsapp/api_version"
  description = "Meta Graph API version"
  type        = "String"
  value       = var.whatsapp_api_version

  tags = {
    Name = "${var.project_name}-${var.environment}-whatsapp-api-version"
  }
}

# Bedrock Agent Parameters (auto-injected)
resource "aws_ssm_parameter" "bedrock_agent_id" {
  name        = "/${var.project_name}/${var.environment}/bedrock/agent_id"
  description = "Bedrock Agent ID"
  type        = "String"
  value       = aws_bedrockagent_agent.agendente.id

  tags = {
    Name = "${var.project_name}-${var.environment}-bedrock-agent-id"
  }
}

resource "aws_ssm_parameter" "bedrock_agent_alias_id" {
  name        = "/${var.project_name}/${var.environment}/bedrock/agent_alias_id"
  description = "Bedrock Agent Alias ID"
  type        = "String"
  value       = var.bedrock_agent_alias_id

  tags = {
    Name = "${var.project_name}-${var.environment}-bedrock-agent-alias-id"
  }
}

# DynamoDB Table Names (auto-injected)
resource "aws_ssm_parameter" "dynamodb_appointments_table" {
  name        = "/${var.project_name}/${var.environment}/dynamodb/appointments_table"
  description = "DynamoDB Appointments table name"
  type        = "String"
  value       = aws_dynamodb_table.appointments.name

  tags = {
    Name = "${var.project_name}-${var.environment}-dynamodb-appointments"
  }
}

resource "aws_ssm_parameter" "dynamodb_professionals_table" {
  name        = "/${var.project_name}/${var.environment}/dynamodb/professionals_table"
  description = "DynamoDB Professionals table name"
  type        = "String"
  value       = aws_dynamodb_table.professionals.name

  tags = {
    Name = "${var.project_name}-${var.environment}-dynamodb-professionals"
  }
}

resource "aws_ssm_parameter" "dynamodb_services_table" {
  name        = "/${var.project_name}/${var.environment}/dynamodb/services_table"
  description = "DynamoDB Services table name"
  type        = "String"
  value       = aws_dynamodb_table.services.name

  tags = {
    Name = "${var.project_name}-${var.environment}-dynamodb-services"
  }
}

resource "aws_ssm_parameter" "dynamodb_clients_table" {
  name        = "/${var.project_name}/${var.environment}/dynamodb/clients_table"
  description = "DynamoDB Clients table name"
  type        = "String"
  value       = aws_dynamodb_table.clients.name

  tags = {
    Name = "${var.project_name}-${var.environment}-dynamodb-clients"
  }
}

resource "aws_ssm_parameter" "dynamodb_message_buffer_table" {
  name        = "/${var.project_name}/${var.environment}/dynamodb/message_buffer_table"
  description = "DynamoDB Message Buffer table name"
  type        = "String"
  value       = aws_dynamodb_table.message_buffer.name

  tags = {
    Name = "${var.project_name}-${var.environment}-dynamodb-message-buffer"
  }
}

resource "aws_ssm_parameter" "dynamodb_conversation_history_table" {
  name        = "/${var.project_name}/${var.environment}/dynamodb/conversation_history_table"
  description = "DynamoDB Conversation History table name"
  type        = "String"
  value       = aws_dynamodb_table.conversation_history.name

  tags = {
    Name = "${var.project_name}-${var.environment}-dynamodb-conversation-history"
  }
}

# Step Functions ARN (auto-injected)
resource "aws_ssm_parameter" "step_function_arn" {
  name        = "/${var.project_name}/${var.environment}/stepfunctions/message_orchestrator_arn"
  description = "Step Functions Message Orchestrator ARN"
  type        = "String"
  value       = aws_sfn_state_machine.message_orchestrator.arn

  tags = {
    Name = "${var.project_name}-${var.environment}-stepfunctions-arn"
  }
}
