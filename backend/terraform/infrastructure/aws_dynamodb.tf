# ============================================================================
# DynamoDB Tables - Agendente Project
# ============================================================================

# Tabela 1: MessageBuffer - Buffer temporário de mensagens
resource "aws_dynamodb_table" "message_buffer" {
  name         = "${var.project_name}-${var.environment}-MessageBuffer"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "phone_number"

  attribute {
    name = "phone_number"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-MessageBuffer"
  }
}

# Tabela 2: Appointments - Agendamentos
resource "aws_dynamodb_table" "appointments" {
  name         = "${var.project_name}-${var.environment}-Appointments"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "appointment_id"
  range_key    = "appointment_date"

  attribute {
    name = "appointment_id"
    type = "S"
  }

  attribute {
    name = "appointment_date"
    type = "S"
  }

  attribute {
    name = "client_phone"
    type = "S"
  }

  attribute {
    name = "professional_id"
    type = "S"
  }

  global_secondary_index {
    name            = "client_phone-appointment_date-index"
    hash_key        = "client_phone"
    range_key       = "appointment_date"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "professional_id-appointment_date-index"
    hash_key        = "professional_id"
    range_key       = "appointment_date"
    projection_type = "ALL"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-Appointments"
  }
}

# Tabela 3: Professionals - Profissionais
resource "aws_dynamodb_table" "professionals" {
  name         = "${var.project_name}-${var.environment}-Professionals"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "professional_id"

  attribute {
    name = "professional_id"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-Professionals"
  }
}

# Tabela 4: Services - Serviços
resource "aws_dynamodb_table" "services" {
  name         = "${var.project_name}-${var.environment}-Services"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "service_id"

  attribute {
    name = "service_id"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-Services"
  }
}

# Tabela 5: Clients - Clientes
resource "aws_dynamodb_table" "clients" {
  name         = "${var.project_name}-${var.environment}-Clients"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "phone_number"

  attribute {
    name = "phone_number"
    type = "S"
  }

  attribute {
    name = "validation_token"
    type = "S"
  }

  global_secondary_index {
    name            = "validation_token-index"
    hash_key        = "validation_token"
    projection_type = "ALL"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-Clients"
  }
}

# Tabela 6: ConversationHistory - Histórico de conversas
resource "aws_dynamodb_table" "conversation_history" {
  name         = "${var.project_name}-${var.environment}-ConversationHistory"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "phone_number"
  range_key    = "timestamp"

  attribute {
    name = "phone_number"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  tags = {
    Name = "${var.project_name}-${var.environment}-ConversationHistory"
  }
}
