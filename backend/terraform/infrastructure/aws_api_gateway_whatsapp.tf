# ============================================================================
# API Gateway - WhatsApp Webhook (mTLS)
# ============================================================================

resource "aws_api_gateway_rest_api" "whatsapp" {
  name        = "${var.project_name}-${var.environment}-whatsapp-api"
  description = "API Gateway for WhatsApp webhook (Meta communication only) - ${var.environment}"

  disable_execute_api_endpoint = var.custom_domain_name != null

  body = templatefile("${path.module}/openapi_whatsapp.yaml", {
    lambda_conversation_webhook_invoke_arn = aws_lambda_function.functions["conversation_webhook"].invoke_arn
  })

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-whatsapp-api"
  }
}

resource "aws_api_gateway_deployment" "whatsapp" {
  rest_api_id = aws_api_gateway_rest_api.whatsapp.id

  triggers = {
    redeployment                 = sha256(file("${path.module}/openapi_whatsapp.yaml"))
    disable_execute_api_endpoint = var.custom_domain_name != null
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "whatsapp" {
  stage_name    = var.environment
  rest_api_id   = aws_api_gateway_rest_api.whatsapp.id
  deployment_id = aws_api_gateway_deployment.whatsapp.id

  tags = {
    Name = "${var.project_name}-${var.environment}-whatsapp-api-stage"
  }
}

resource "aws_api_gateway_method_settings" "whatsapp" {
  rest_api_id = aws_api_gateway_rest_api.whatsapp.id
  stage_name  = aws_api_gateway_stage.whatsapp.stage_name
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

# CloudWatch Log Group para WhatsApp API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_whatsapp" {
  count             = var.enable_api_gateway_logs ? 1 : 0
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.whatsapp.id}/${var.environment}"
  retention_in_days = 3
}

# Lambda permission para WhatsApp API Gateway
resource "aws_lambda_permission" "whatsapp_api_gateway" {
  statement_id  = "AllowExecutionFromWhatsAppAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.functions["conversation_webhook"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.whatsapp.execution_arn}/*/*"
}
