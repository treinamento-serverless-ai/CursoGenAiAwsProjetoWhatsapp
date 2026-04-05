# ============================================================================
# Bedrock Agent - IAM Role
# ============================================================================

data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

data "aws_iam_policy_document" "bedrock_agent_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["bedrock.amazonaws.com"]
      type        = "Service"
    }
    condition {
      test     = "StringEquals"
      values   = [data.aws_caller_identity.current.account_id]
      variable = "aws:SourceAccount"
    }
    condition {
      test     = "ArnLike"
      values   = ["arn:${data.aws_partition.current.partition}:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:agent/*"]
      variable = "AWS:SourceArn"
    }
  }
}

data "aws_iam_policy_document" "bedrock_agent_permissions" {
  statement {
    actions   = ["bedrock:InvokeModel"]
    resources = ["arn:aws:bedrock:${var.aws_region}::foundation-model/*"]
  }
}

resource "aws_iam_role" "bedrock_agent_role" {
  name_prefix        = "${var.project_name}-${var.environment}-agent-"
  assume_role_policy = data.aws_iam_policy_document.bedrock_agent_trust.json

  tags = {
    Name = "${var.project_name}-${var.environment}-bedrock-agent-role"
  }
}

resource "aws_iam_role_policy" "bedrock_agent_policy" {
  role   = aws_iam_role.bedrock_agent_role.id
  policy = data.aws_iam_policy_document.bedrock_agent_permissions.json
}

# ============================================================================
# Bedrock Agent
# ============================================================================

resource "aws_bedrockagent_agent" "agendente" {
  agent_name                  = "${var.project_name}-${var.environment}"
  agent_resource_role_arn     = aws_iam_role.bedrock_agent_role.arn
  idle_session_ttl_in_seconds = 600
  foundation_model            = var.bedrock_agent_foundation_model
  description                 = "Agente de agendamento para ${var.project_name}"
  instruction                 = local.bedrock_agent_instruction

  tags = {
    Name = "${var.project_name}-${var.environment}-bedrock-agent"
  }
}

# ============================================================================
# Bedrock Agent Action Groups
# ============================================================================

# Action groups are chained (each depends on the previous) to avoid
# concurrent PrepareAgent calls that would cause race conditions.

resource "aws_bedrockagent_agent_action_group" "list_professionals" {
  action_group_name          = "ListProfessionals"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Use when client asks about available professionals, staff members, or who can provide services"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_list_professionals"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "list_professionals"
        description = "Retrieve list of all active professionals/staff with their details (name, specialty, experience, contact)"
      }
    }
  }
}

resource "aws_bedrockagent_agent_action_group" "check_availability" {
  action_group_name          = "CheckAvailability"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Use when client wants to know available time slots, check schedules, or find open appointments"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_check_availability"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "check_availability"
        description = "Check available appointment time slots for professionals within a date range, optionally filtered by specific professional"
        parameters {
          map_block_key = "start_date"
          type          = "string"
          description   = "Start date in ISO format (YYYY-MM-DD)"
          required      = true
        }
        parameters {
          map_block_key = "end_date"
          type          = "string"
          description   = "End date in ISO format (YYYY-MM-DD). If not provided, uses start_date"
          required      = false
        }
        parameters {
          map_block_key = "professional_id"
          type          = "string"
          description   = "Optional professional ID to filter availability"
          required      = false
        }
      }
    }
  }

  depends_on = [aws_bedrockagent_agent_action_group.list_professionals]
}

resource "aws_bedrockagent_agent_action_group" "create_appointment" {
  action_group_name          = "CreateAppointment"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Use ONLY after confirming all details with client to book/schedule a new appointment"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_create_appointment"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "create_appointment"
        description = "Create a new appointment in the system. Must have explicit confirmation from client before calling this function"
        parameters {
          map_block_key = "appointment_date"
          type          = "string"
          description   = "Appointment date and time in ISO format (YYYY-MM-DDTHH:MM:SS)"
          required      = true
        }
        parameters {
          map_block_key = "professional_id"
          type          = "string"
          description   = "ID of the professional"
          required      = true
        }
        parameters {
          map_block_key = "service_id"
          type          = "string"
          description   = "ID of the service to be performed"
          required      = true
        }
      }
    }
  }

  depends_on = [aws_bedrockagent_agent_action_group.check_availability]
}

resource "aws_bedrockagent_agent_action_group" "list_services" {
  action_group_name          = "ListServices"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Use when client asks what services are offered, available treatments, or wants to browse options"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_list_services"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "list_services"
        description = "Retrieve list of all active services/treatments offered with basic information (name, description, category)"
      }
    }
  }

  depends_on = [aws_bedrockagent_agent_action_group.create_appointment]
}

resource "aws_bedrockagent_agent_action_group" "get_service_details" {
  action_group_name          = "GetServiceDetails"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Use when client asks about pricing, duration, or which professionals offer a specific service"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_get_service_details"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "get_service_details"
        description = "Get detailed information about a specific service including price, duration, and which professionals offer it"
        parameters {
          map_block_key = "service_id"
          type          = "string"
          description   = "ID of the service"
          required      = true
        }
      }
    }
  }

  depends_on = [aws_bedrockagent_agent_action_group.list_services]
}

resource "aws_bedrockagent_agent_action_group" "list_user_appointments" {
  action_group_name          = "ListUserAppointments"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Use when client asks about their existing appointments, bookings, or scheduled visits"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_list_user_appointments"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "list_user_appointments"
        description = "Retrieve all future appointments for the current user (automatically uses their phone number)"
      }
    }
  }

  depends_on = [aws_bedrockagent_agent_action_group.get_service_details]
}

resource "aws_bedrockagent_agent_action_group" "cancel_appointment" {
  action_group_name          = "CancelAppointment"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Use when client wants to cancel or remove an existing appointment"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_cancel_appointment"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "cancel_appointment"
        description = "Cancel an existing appointment. System validates that user owns the appointment before canceling"
        parameters {
          map_block_key = "appointment_id"
          type          = "string"
          description   = "ID of the appointment to cancel"
          required      = true
        }
      }
    }
  }

  depends_on = [aws_bedrockagent_agent_action_group.list_user_appointments]
}

resource "aws_bedrockagent_agent_action_group" "resolve_date_reference" {
  action_group_name          = "ResolveDateReference"
  agent_id                   = aws_bedrockagent_agent.agendente.id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  description                = "Use when client mentions temporal references like 'tomorrow', 'next week', 'in 3 days' to convert them into concrete dates"

  action_group_executor {
    lambda = aws_lambda_function.functions["agent_resolve_date_reference"].arn
  }

  function_schema {
    member_functions {
      functions {
        name        = "resolve_date_reference"
        description = "Converts temporal references (TODAY, TOMORROW, NEXT_WEEK, CURRENT_WEEK, +3 days, +2 weeks, NEXT_MONTH) into concrete ISO dates or date ranges"
        parameters {
          map_block_key = "reference"
          type          = "string"
          description   = "Temporal reference to resolve. Examples: TODAY, TOMORROW, NEXT_WEEK, CURRENT_WEEK, +3 days, +2 weeks, NEXT_MONTH"
          required      = true
        }
      }
    }
  }

  depends_on = [aws_bedrockagent_agent_action_group.cancel_appointment]
}
