# ============================================================================
# CloudWatch Dashboard - Agendente Project
# ============================================================================

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-${var.environment}-dashboard"

  dashboard_body = jsonencode({
    widgets = concat(
      # ----- Row 1: API Gateway Overview -----
      [
        {
          type   = "text"
          x      = 0
          y      = 0
          width  = 24
          height = 1
          properties = {
            markdown = "## API Gateway"
          }
        },
        {
          type   = "metric"
          x      = 0
          y      = 1
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "Admin API - Requests"
            region  = var.aws_region
            stat    = "Sum"
            period  = 300
            metrics = [
              ["AWS/ApiGateway", "Count", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment, { label = "Total Requests" }],
            ]
          }
        },
        {
          type   = "metric"
          x      = 8
          y      = 1
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "Admin API - Errors"
            region  = var.aws_region
            stat    = "Sum"
            period  = 300
            metrics = [
              ["AWS/ApiGateway", "4XXError", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment, { label = "4XX", color = "#ff9900" }],
              ["AWS/ApiGateway", "5XXError", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment, { label = "5XX", color = "#d13212" }],
            ]
          }
        },
        {
          type   = "metric"
          x      = 16
          y      = 1
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "Admin API - Latency"
            region  = var.aws_region
            period  = 300
            metrics = [
              ["AWS/ApiGateway", "Latency", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment, { stat = "Average", label = "Avg" }],
              ["AWS/ApiGateway", "Latency", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment, { stat = "p99", label = "p99" }],
            ]
          }
        },
        {
          type   = "metric"
          x      = 0
          y      = 7
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "WhatsApp API - Requests"
            region  = var.aws_region
            stat    = "Sum"
            period  = 300
            metrics = [
              ["AWS/ApiGateway", "Count", "ApiName", aws_api_gateway_rest_api.whatsapp.name, "Stage", var.environment, { label = "Total Requests" }],
            ]
          }
        },
        {
          type   = "metric"
          x      = 8
          y      = 7
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "WhatsApp API - Errors"
            region  = var.aws_region
            stat    = "Sum"
            period  = 300
            metrics = [
              ["AWS/ApiGateway", "4XXError", "ApiName", aws_api_gateway_rest_api.whatsapp.name, "Stage", var.environment, { label = "4XX", color = "#ff9900" }],
              ["AWS/ApiGateway", "5XXError", "ApiName", aws_api_gateway_rest_api.whatsapp.name, "Stage", var.environment, { label = "5XX", color = "#d13212" }],
            ]
          }
        },
        {
          type   = "metric"
          x      = 16
          y      = 7
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "WhatsApp API - Latency"
            region  = var.aws_region
            period  = 300
            metrics = [
              ["AWS/ApiGateway", "Latency", "ApiName", aws_api_gateway_rest_api.whatsapp.name, "Stage", var.environment, { stat = "Average", label = "Avg" }],
              ["AWS/ApiGateway", "Latency", "ApiName", aws_api_gateway_rest_api.whatsapp.name, "Stage", var.environment, { stat = "p99", label = "p99" }],
            ]
          }
        },
      ],

      # ----- Row 2: Step Functions -----
      [
        {
          type   = "text"
          x      = 0
          y      = 13
          width  = 24
          height = 1
          properties = {
            markdown = "## Step Functions - Message Orchestrator"
          }
        },
        {
          type   = "metric"
          x      = 0
          y      = 14
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "Executions (≈ Bot Responses)"
            region  = var.aws_region
            stat    = "Sum"
            period  = 300
            metrics = [
              ["AWS/States", "ExecutionsStarted", "StateMachineArn", aws_sfn_state_machine.message_orchestrator.arn, { label = "Started", color = "#1f77b4" }],
              ["AWS/States", "ExecutionsSucceeded", "StateMachineArn", aws_sfn_state_machine.message_orchestrator.arn, { label = "Succeeded", color = "#2ca02c" }],
              ["AWS/States", "ExecutionsFailed", "StateMachineArn", aws_sfn_state_machine.message_orchestrator.arn, { label = "Failed", color = "#d13212" }],
              ["AWS/States", "ExecutionsTimedOut", "StateMachineArn", aws_sfn_state_machine.message_orchestrator.arn, { label = "Timed Out", color = "#ff9900" }],
            ]
          }
        },
        {
          type   = "metric"
          x      = 8
          y      = 14
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "Execution Duration"
            region  = var.aws_region
            period  = 300
            metrics = [
              ["AWS/States", "ExecutionTime", "StateMachineArn", aws_sfn_state_machine.message_orchestrator.arn, { stat = "Average", label = "Avg (ms)" }],
              ["AWS/States", "ExecutionTime", "StateMachineArn", aws_sfn_state_machine.message_orchestrator.arn, { stat = "p99", label = "p99 (ms)" }],
            ]
          }
        },
        {
          type   = "metric"
          x      = 16
          y      = 14
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "Throttled Executions"
            region  = var.aws_region
            stat    = "Sum"
            period  = 300
            metrics = [
              ["AWS/States", "ExecutionThrottled", "StateMachineArn", aws_sfn_state_machine.message_orchestrator.arn, { label = "Throttled", color = "#d13212" }],
            ]
          }
        },
      ],

      # ----- Row 3: Lambda - Conversation Flow -----
      [
        {
          type   = "text"
          x      = 0
          y      = 20
          width  = 24
          height = 1
          properties = {
            markdown = "## Lambda - Conversation Flow"
          }
        },
      ],
      [
        for i, name_key in ["conversation-webhook", "conversation-check-freshness", "conversation-process-and-send", "conversation-transcription", "conversation-archiver"] :
        {
          type   = "metric"
          x      = (i % 3) * 8
          y      = 21 + floor(i / 3) * 6
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = name_key
            region  = var.aws_region
            period  = 300
            metrics = [
              ["AWS/Lambda", "Invocations", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Sum", label = "Invocations", color = "#2ca02c" }],
              ["AWS/Lambda", "Errors", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Sum", label = "Errors", color = "#d13212" }],
              ["AWS/Lambda", "Duration", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Average", label = "Avg Duration (ms)", yAxis = "right" }],
            ]
          }
        }
      ],

      # ----- Row 4: Lambda - CRUD -----
      [
        {
          type   = "text"
          x      = 0
          y      = 33
          width  = 24
          height = 1
          properties = {
            markdown = "## Lambda - CRUD"
          }
        },
      ],
      [
        for i, name_key in ["crud-appointments", "crud-professionals", "crud-services", "crud-clients", "crud-attendance", "crud-conversations", "crud-config"] :
        {
          type   = "metric"
          x      = (i % 3) * 8
          y      = 34 + floor(i / 3) * 6
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = name_key
            region  = var.aws_region
            period  = 300
            metrics = [
              ["AWS/Lambda", "Invocations", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Sum", label = "Invocations", color = "#2ca02c" }],
              ["AWS/Lambda", "Errors", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Sum", label = "Errors", color = "#d13212" }],
              ["AWS/Lambda", "Duration", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Average", label = "Avg Duration (ms)", yAxis = "right" }],
            ]
          }
        }
      ],

      # ----- Row 5: Lambda - Bedrock Agent -----
      [
        {
          type   = "text"
          x      = 0
          y      = 52
          width  = 24
          height = 1
          properties = {
            markdown = "## Lambda - Bedrock Agent"
          }
        },
      ],
      [
        for i, name_key in ["agent-list-professionals", "agent-check-availability", "agent-create-appointment", "agent-list-services", "agent-get-service-details", "agent-list-user-appointments", "agent-cancel-appointment", "agent-resolve-date-reference"] :
        {
          type   = "metric"
          x      = (i % 3) * 8
          y      = 53 + floor(i / 3) * 6
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = name_key
            region  = var.aws_region
            period  = 300
            metrics = [
              ["AWS/Lambda", "Invocations", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Sum", label = "Invocations", color = "#2ca02c" }],
              ["AWS/Lambda", "Errors", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Sum", label = "Errors", color = "#d13212" }],
              ["AWS/Lambda", "Duration", "FunctionName", "${var.project_name}-${var.environment}-${name_key}", { stat = "Average", label = "Avg Duration (ms)", yAxis = "right" }],
            ]
          }
        }
      ],

      # ----- Row 6: Lambda - Scheduled -----
      [
        {
          type   = "text"
          x      = 0
          y      = 71
          width  = 24
          height = 1
          properties = {
            markdown = "## Lambda - Scheduled"
          }
        },
        {
          type   = "metric"
          x      = 0
          y      = 72
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = "scheduled-security-monitor"
            region  = var.aws_region
            period  = 300
            metrics = [
              ["AWS/Lambda", "Invocations", "FunctionName", "${var.project_name}-${var.environment}-scheduled-security-monitor", { stat = "Sum", label = "Invocations", color = "#2ca02c" }],
              ["AWS/Lambda", "Errors", "FunctionName", "${var.project_name}-${var.environment}-scheduled-security-monitor", { stat = "Sum", label = "Errors", color = "#d13212" }],
              ["AWS/Lambda", "Duration", "FunctionName", "${var.project_name}-${var.environment}-scheduled-security-monitor", { stat = "Average", label = "Avg Duration (ms)", yAxis = "right" }],
            ]
          }
        },
      ],

      # ----- Row 7: DynamoDB -----
      [
        {
          type   = "text"
          x      = 0
          y      = 78
          width  = 24
          height = 1
          properties = {
            markdown = "## DynamoDB"
          }
        },
      ],
      [
        for i, table in [
          { label = "ConversationHistory", name = aws_dynamodb_table.conversation_history.name },
          { label = "MessageBuffer", name = aws_dynamodb_table.message_buffer.name },
          { label = "Clients", name = aws_dynamodb_table.clients.name },
          { label = "Appointments", name = aws_dynamodb_table.appointments.name },
          { label = "Professionals", name = aws_dynamodb_table.professionals.name },
          { label = "Services", name = aws_dynamodb_table.services.name },
        ] :
        {
          type   = "metric"
          x      = (i % 3) * 8
          y      = 79 + floor(i / 3) * 6
          width  = 8
          height = 6
          properties = {
            view    = "timeSeries"
            stacked = false
            title   = table.label
            region  = var.aws_region
            stat    = "Sum"
            period  = 300
            metrics = [
              ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", table.name, { label = "Reads", color = "#2ca02c" }],
              ["AWS/DynamoDB", "ConsumedWriteCapacityUnits", "TableName", table.name, { label = "Writes", color = "#1f77b4" }],
              ["AWS/DynamoDB", "ThrottledRequests", "TableName", table.name, { label = "Throttled", color = "#d13212" }],
            ]
          }
        }
      ],
    )
  })
}
