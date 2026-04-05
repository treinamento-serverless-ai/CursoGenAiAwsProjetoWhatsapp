# ============================================================================
# EventBridge Scheduler - Token Validation
# ============================================================================

# IAM Role para o Scheduler invocar a Lambda
resource "aws_iam_role" "scheduler_token_validation" {
  name = "${var.project_name}-${var.environment}-scheduler-token-validation"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "scheduler.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-scheduler-token-validation"
  }
}

resource "aws_iam_role_policy" "scheduler_token_validation" {
  name = "invoke-lambda-and-sns"
  role = aws_iam_role.scheduler_token_validation.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "lambda:InvokeFunction"
        Resource = aws_lambda_function.functions["scheduled_security_monitor"].arn
      },
      {
        Effect   = "Allow"
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.scheduler_dlq.arn
      }
    ]
  })
}

# EventBridge Scheduler
resource "aws_scheduler_schedule" "token_validation" {
  name        = "${var.project_name}-${var.environment}-token-validation"
  description = "Daily validation of WhatsApp API token expiration"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 0 * * ? *)"
  schedule_expression_timezone = "America/Sao_Paulo"

  target {
    arn      = aws_lambda_function.functions["scheduled_security_monitor"].arn
    role_arn = aws_iam_role.scheduler_token_validation.arn

    retry_policy {
      maximum_retry_attempts = 0
    }

    dead_letter_config {
      arn = aws_sqs_queue.scheduler_dlq.arn
    }
  }
}

