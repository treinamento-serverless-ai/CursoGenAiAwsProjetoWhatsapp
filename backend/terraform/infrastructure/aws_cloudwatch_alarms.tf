# ============================================================================
# CloudWatch Alarms - Lambda Error Rate Monitoring
# ============================================================================

# Metric Filter para capturar logger.error() em cada Lambda
resource "aws_cloudwatch_log_metric_filter" "lambda_error_logs" {
  for_each = local.lambdas_with_alarms

  name           = "${var.project_name}-${var.environment}-lambda-${each.value.name_key}-error-logs"
  log_group_name = aws_cloudwatch_log_group.lambda_logs[each.key].name
  pattern        = "[ERROR]"

  metric_transformation {
    name      = "${each.value.name_key}-ErrorLogCount"
    namespace = "${var.project_name}/${var.environment}/Lambda"
    value     = "1"
  }
}

# Alarme para logger.error() - qualquer erro logado dispara alerta
resource "aws_cloudwatch_metric_alarm" "lambda_error_logs" {
  for_each = local.lambdas_with_alarms

  alarm_name          = "${var.project_name}-${var.environment}-lambda-${each.value.name_key}-error-logs"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.cloudwatch_alarms_evaluation_periods
  datapoints_to_alarm = var.cloudwatch_alarms_datapoints_to_alarm
  threshold           = 0
  treat_missing_data  = "notBreaching"

  alarm_description = "Logger.error() detected in Lambda: ${aws_lambda_function.functions[each.key].function_name}"
  alarm_actions     = [aws_sns_topic.alerts.arn]

  metric_name = "${each.value.name_key}-ErrorLogCount"
  namespace   = "${var.project_name}/${var.environment}/Lambda"
  period      = var.alarm_evaluation_period_seconds
  statistic   = "Sum"

  depends_on = [aws_cloudwatch_log_metric_filter.lambda_error_logs]
}

# Alarme de taxa de erro para cada Lambda (> 5%)
resource "aws_cloudwatch_metric_alarm" "lambda_error_rate" {
  for_each = local.lambdas_with_alarms

  alarm_name          = "${var.project_name}-${var.environment}-lambda-${each.value.name_key}-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.cloudwatch_alarms_evaluation_periods
  datapoints_to_alarm = var.cloudwatch_alarms_datapoints_to_alarm
  threshold           = var.cloudwatch_alarms_threshold
  treat_missing_data  = "notBreaching"

  alarm_description = "Error rate above ${var.cloudwatch_alarms_threshold}% for Lambda: ${aws_lambda_function.functions[each.key].function_name}"
  alarm_actions     = [aws_sns_topic.alerts.arn]

  metric_query {
    id          = "error_rate"
    expression  = "(errors / invocations) * 100"
    label       = "Error Rate (%)"
    return_data = true
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = var.alarm_evaluation_period_seconds
      stat        = "Sum"
      dimensions = {
        FunctionName = aws_lambda_function.functions[each.key].function_name
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = var.alarm_evaluation_period_seconds
      stat        = "Sum"
      dimensions = {
        FunctionName = aws_lambda_function.functions[each.key].function_name
      }
    }
  }

  tags = {
    Name         = "${var.project_name}-${var.environment}-lambda-${each.value.name_key}-error-rate"
    LambdaName   = aws_lambda_function.functions[each.key].function_name
  }
}

# ============================================================================
# CloudWatch Alarms - API Gateway Error Rate Monitoring
# ============================================================================

# Alarme de taxa de erro para API Gateway Admin (> 5% de 4XX/5XX)
resource "aws_cloudwatch_metric_alarm" "api_gateway_error_rate" {
  count = var.enable_api_gateway_logs ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-apigateway-admin-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.cloudwatch_alarms_evaluation_periods
  datapoints_to_alarm = var.cloudwatch_alarms_datapoints_to_alarm
  threshold           = var.cloudwatch_alarms_threshold
  treat_missing_data  = "notBreaching"

  alarm_description = "API Gateway error rate above ${var.cloudwatch_alarms_threshold}% (4XX + 5XX responses)"
  alarm_actions     = [aws_sns_topic.alerts.arn]

  metric_query {
    id          = "error_rate"
    expression  = "((m4xx + m5xx) / requests) * 100"
    label       = "Error Rate (%)"
    return_data = true
  }

  metric_query {
    id = "requests"
    metric {
      metric_name = "Count"
      namespace   = "AWS/ApiGateway"
      period      = 300
      stat        = "Sum"
      dimensions = {
        ApiName = aws_api_gateway_rest_api.main.name
        Stage   = var.environment
      }
    }
  }

  metric_query {
    id = "m4xx"
    metric {
      metric_name = "4XXError"
      namespace   = "AWS/ApiGateway"
      period      = 300
      stat        = "Sum"
      dimensions = {
        ApiName = aws_api_gateway_rest_api.main.name
        Stage   = var.environment
      }
    }
  }

  metric_query {
    id = "m5xx"
    metric {
      metric_name = "5XXError"
      namespace   = "AWS/ApiGateway"
      period      = 300
      stat        = "Sum"
      dimensions = {
        ApiName = aws_api_gateway_rest_api.main.name
        Stage   = var.environment
      }
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-apigateway-admin-error-rate"
  }
}

# Alarme de taxa de erro para API Gateway WhatsApp (> 5% de 4XX/5XX)
resource "aws_cloudwatch_metric_alarm" "api_gateway_whatsapp_error_rate" {
  count = var.enable_api_gateway_logs ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-apigateway-whatsapp-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.cloudwatch_alarms_evaluation_periods
  datapoints_to_alarm = var.cloudwatch_alarms_datapoints_to_alarm
  threshold           = var.cloudwatch_alarms_threshold
  treat_missing_data  = "notBreaching"

  alarm_description = "WhatsApp API Gateway error rate above ${var.cloudwatch_alarms_threshold}% (4XX + 5XX responses)"
  alarm_actions     = [aws_sns_topic.alerts.arn]

  metric_query {
    id          = "error_rate"
    expression  = "((m4xx + m5xx) / requests) * 100"
    label       = "Error Rate (%)"
    return_data = true
  }

  metric_query {
    id = "requests"
    metric {
      metric_name = "Count"
      namespace   = "AWS/ApiGateway"
      period      = 300
      stat        = "Sum"
      dimensions = {
        ApiName = aws_api_gateway_rest_api.whatsapp.name
        Stage   = var.environment
      }
    }
  }

  metric_query {
    id = "m4xx"
    metric {
      metric_name = "4XXError"
      namespace   = "AWS/ApiGateway"
      period      = 300
      stat        = "Sum"
      dimensions = {
        ApiName = aws_api_gateway_rest_api.whatsapp.name
        Stage   = var.environment
      }
    }
  }

  metric_query {
    id = "m5xx"
    metric {
      metric_name = "5XXError"
      namespace   = "AWS/ApiGateway"
      period      = 300
      stat        = "Sum"
      dimensions = {
        ApiName = aws_api_gateway_rest_api.whatsapp.name
        Stage   = var.environment
      }
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-apigateway-whatsapp-error-rate"
  }
}
