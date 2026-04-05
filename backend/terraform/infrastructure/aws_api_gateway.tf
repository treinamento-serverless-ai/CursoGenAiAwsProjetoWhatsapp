# ============================================================================
# API Gateway - Agendente Admin API
# ============================================================================

resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.project_name}-${var.environment}-api"
  description = "API Gateway for Agendente admin operations and frontend - ${var.environment}"

  disable_execute_api_endpoint = false

  body = templatefile("${path.module}/openapi_agendente.yaml", {
    # CRUD Lambdas
    lambda_crud_appointments_invoke_arn   = aws_lambda_function.functions["crud_appointments"].invoke_arn
    lambda_crud_professionals_invoke_arn  = aws_lambda_function.functions["crud_professionals"].invoke_arn
    lambda_crud_services_invoke_arn       = aws_lambda_function.functions["crud_services"].invoke_arn
    lambda_crud_clients_invoke_arn        = aws_lambda_function.functions["crud_clients"].invoke_arn
    lambda_crud_conversations_invoke_arn  = aws_lambda_function.functions["crud_conversations"].invoke_arn
    lambda_crud_config_invoke_arn         = aws_lambda_function.functions["crud_config"].invoke_arn
    lambda_crud_attendance_invoke_arn     = aws_lambda_function.functions["crud_attendance"].invoke_arn
    cognito_user_pool_arn                 = aws_cognito_user_pool.main.arn
    cors_allowed_origins                  = var.cors_allowed_origins_frontend
  })

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-api"
  }
}

resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id

  triggers = {
    redeployment = sha256(file("${path.module}/openapi_agendente.yaml"))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "main" {
  stage_name    = var.environment
  rest_api_id   = aws_api_gateway_rest_api.main.id
  deployment_id = aws_api_gateway_deployment.main.id

  tags = {
    Name = "${var.project_name}-${var.environment}-api-stage"
  }
}

resource "aws_api_gateway_method_settings" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = aws_api_gateway_stage.main.stage_name
  method_path = "*/*"

  depends_on = [aws_api_gateway_account.main]

  settings {
    metrics_enabled        = true
    logging_level          = var.enable_api_gateway_logs ? "INFO" : "OFF"
    data_trace_enabled     = var.enable_api_gateway_logs
    throttling_burst_limit = 100
    throttling_rate_limit  = 50
  }
}

# CloudWatch Logs role para API Gateway
resource "aws_iam_role" "api_gateway_cloudwatch" {
  count = var.enable_api_gateway_logs ? 1 : 0
  name  = "${var.project_name}-${var.environment}-api-gateway-cloudwatch"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "apigateway.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" {
  count      = var.enable_api_gateway_logs ? 1 : 0
  role       = aws_iam_role.api_gateway_cloudwatch[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

resource "aws_api_gateway_account" "main" {
  count               = var.enable_api_gateway_logs ? 1 : 0
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch[0].arn
}

# CloudWatch Log Group para API Gateway (retenção de 3 dias)
resource "aws_cloudwatch_log_group" "api_gateway" {
  count             = var.enable_api_gateway_logs ? 1 : 0
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.main.id}/${var.environment}"
  retention_in_days = 3
}

