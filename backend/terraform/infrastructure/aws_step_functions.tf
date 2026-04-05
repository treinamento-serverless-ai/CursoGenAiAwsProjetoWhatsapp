# ============================================================================
# Step Functions - Agendente Project
# ============================================================================

# CloudWatch Log Group para Step Functions
resource "aws_cloudwatch_log_group" "step_functions" {
  name              = "/aws/vendedlogs/states/${var.project_name}-${var.environment}-MessageOrchestrator"
  retention_in_days = var.step_functions_log_retention_days

  tags = {
    Name = "${var.project_name}-${var.environment}-step-functions-logs"
  }
}

# IAM Role para Step Functions
resource "aws_iam_role" "step_functions" {
  name = "${var.project_name}-${var.environment}-step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-step-functions-role"
  }
}

# IAM Policy para Step Functions
resource "aws_iam_role_policy" "step_functions" {
  name = "${var.project_name}-${var.environment}-step-functions-policy"
  role = aws_iam_role.step_functions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          aws_lambda_function.functions["conversation_check_freshness"].arn,
          aws_lambda_function.functions["conversation_process_and_send"].arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.alerts.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogDelivery",
          "logs:GetLogDelivery",
          "logs:UpdateLogDelivery",
          "logs:DeleteLogDelivery",
          "logs:ListLogDeliveries",
          "logs:PutResourcePolicy",
          "logs:DescribeResourcePolicies",
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
      }
    ]
  })
}

# State Machine - Message Orchestrator
resource "aws_sfn_state_machine" "message_orchestrator" {
  name     = "${var.project_name}-${var.environment}-MessageOrchestrator"
  role_arn = aws_iam_role.step_functions.arn

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.step_functions.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  definition = jsonencode({
    Comment        = "WhatsApp Message Orchestrator with Bedrock Agent"
    TimeoutSeconds = 600
    StartAt        = "CheckMessageFreshness"
    States = {
      CheckMessageFreshness = {
        Type       = "Task"
        Resource   = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = aws_lambda_function.functions["conversation_check_freshness"].arn
          Payload = {
            "user_id.$" = "$.user_id"
          }
        }
        ResultPath = "$.checkResult"
        Retry = [{
          ErrorEquals     = ["States.TaskFailed"]
          IntervalSeconds = 2
          MaxAttempts     = 2
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyError"
        }]
        Next = "ShouldWait"
      }

      ShouldWait = {
        Type = "Choice"
        Choices = [{
          Variable      = "$.checkResult.Payload.should_wait"
          BooleanEquals = true
          Next          = "WaitForInactivity"
        }]
        Default = "ProcessAndSendMessage"
      }

      WaitForInactivity = {
        Type        = "Wait"
        SecondsPath = "$.checkResult.Payload.wait_seconds"
        Next        = "CheckMessageFreshness"
      }

      ProcessAndSendMessage = {
        Type       = "Task"
        Resource   = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = aws_lambda_function.functions["conversation_process_and_send"].arn
          Payload = {
            "user_id.$" = "$.user_id"
          }
        }
        ResultPath = "$.processResult"
        Retry = [{
          ErrorEquals     = ["States.TaskFailed"]
          IntervalSeconds = 3
          MaxAttempts     = 2
          BackoffRate     = 2.0
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          ResultPath  = "$.error"
          Next        = "NotifyError"
        }]
        Next = "EndSuccess"
      }

      EndSuccess = {
        Type = "Succeed"
      }

      NotifyError = {
        Type     = "Task"
        Resource = "arn:aws:states:::sns:publish"
        Parameters = {
          TopicArn = aws_sns_topic.alerts.arn
          Subject  = "Erro no Message Orchestrator"
          Message = {
            "error.$"   = "$.error"
            "user_id.$" = "$.user_id"
            "state.$"   = "$$.State.Name"
          }
        }
        End = true
      }
    }
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-MessageOrchestrator"
  }
}
