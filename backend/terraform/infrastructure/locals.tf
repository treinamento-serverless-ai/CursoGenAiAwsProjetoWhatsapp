locals {
  api_name      = "${var.project_name}-${var.environment}-api"
  lambda_prefix = "${var.project_name}_${var.environment}_"

  # Comentado temporariamente até criar API Gateway
  # api_gateway_execution_arn = aws_api_gateway_rest_api.whatsapp_api.execution_arn

  lambda_names = {
    webhook_handler       = "webhook-handler"
    token_monitor         = "token-monitor"
    transcription_handler = "transcription-handler"
    conversation_archiver = "conversation-archiver"
  }

  bedrock_agent_id = aws_bedrockagent_agent.agendente.id

  # Instrução padrão do Bedrock Agent (usada quando var.bedrock_agent_instruction é null)
  default_bedrock_agent_instruction = file("${path.module}/default_bedrock_agent_instruction.txt")
  bedrock_agent_instruction         = coalesce(var.bedrock_agent_instruction, local.default_bedrock_agent_instruction)

  # Lambdas com alarmes CloudWatch habilitados (enable_alarms = true)
  lambdas_with_alarms = {
    for key, config in local.lambdas_config :
    key => config if try(config.enable_alarms, false)
  }
}
