# ============================================================================
# SQS Queue - Dead Letter Queue for Schedulers
# ============================================================================

resource "aws_sqs_queue" "scheduler_dlq" {
  name = "${var.project_name}-${var.environment}-scheduler-dlq"

  tags = {
    Name = "${var.project_name}-${var.environment}-scheduler-dlq"
  }
}

# Lambda para processar mensagens da DLQ e enviar para SNS
resource "aws_lambda_function" "scheduler_dlq_processor" {
  function_name = "${var.project_name}-${var.environment}-scheduler-dlq-processor"
  description   = "Processes scheduler DLQ messages and forwards to SNS - ${var.project_name} ${var.environment}"

  filename         = data.archive_file.dlq_processor_zip.output_path
  source_code_hash = data.archive_file.dlq_processor_zip.output_base64sha256

  role    = aws_iam_role.dlq_processor.arn
  handler = "lambda_function.lambda_handler"
  runtime = "python3.13"

  architectures = ["arm64"]
  memory_size   = 128
  timeout       = 30

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.alerts.arn
      PROJECT_NAME  = var.project_name
      ENVIRONMENT   = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-scheduler-dlq-processor"
  }
}

data "archive_file" "dlq_processor_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src/lambda/scheduled_dlq_processor"
  output_path = "${path.module}/.terraform/lambda_packages/scheduled_dlq_processor.zip"
}

resource "aws_iam_role" "dlq_processor" {
  name = "${var.project_name}-${var.environment}-dlq-processor-role"

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
    Name = "${var.project_name}-${var.environment}-dlq-processor-role"
  }
}

resource "aws_iam_role_policy" "dlq_processor" {
  name = "dlq-processor-policy"
  role = aws_iam_role.dlq_processor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-${var.environment}-scheduler-dlq-processor:*"
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.scheduler_dlq.arn
      },
      {
        Effect   = "Allow"
        Action   = "sns:Publish"
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}

resource "aws_lambda_event_source_mapping" "dlq_processor" {
  event_source_arn = aws_sqs_queue.scheduler_dlq.arn
  function_name    = aws_lambda_function.scheduler_dlq_processor.arn
  batch_size       = 1
}

resource "aws_cloudwatch_log_group" "dlq_processor" {
  name              = "/aws/lambda/${aws_lambda_function.scheduler_dlq_processor.function_name}"
  retention_in_days = var.dlq_processor_log_retention_days

  tags = {
    Name = "${var.project_name}-${var.environment}-dlq-processor-logs"
  }
}
