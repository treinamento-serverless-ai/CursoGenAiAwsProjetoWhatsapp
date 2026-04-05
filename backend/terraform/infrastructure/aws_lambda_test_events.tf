# ============================================================================
# Lambda Test Events - Shareable
# ============================================================================
# Cria test events automaticamente a partir dos arquivos JSON na pasta examples/
# Segue o padrão do console AWS: um schema por Lambda com múltiplos examples

locals {
  # Para cada Lambda, verifica se tem pasta examples/ com JSONs
  lambdas_with_tests = {
    for key, config in local.lambdas_config :
    key => {
      function_name    = aws_lambda_function.functions[key].function_name
      examples_path    = "${path.module}/${config.code_path}/examples"
      test_event_files = try(fileset("${path.module}/${config.code_path}/examples", "*.json"), [])
    }
    if length(try(fileset("${path.module}/${config.code_path}/examples", "*.json"), [])) > 0
  }

  # Monta examples para cada Lambda
  test_schemas = {
    for key, lambda in local.lambdas_with_tests :
    key => {
      for filename in lambda.test_event_files :
      trimsuffix(filename, ".json") => {
        value = jsondecode(file("${lambda.examples_path}/${filename}"))
        x-metadata = {
          invocationType = "RequestResponse"
        }
      }
    }
  }
}

# Schema único por Lambda contendo todos os test events
resource "aws_schemas_schema" "lambda_test_events" {
  for_each = local.lambdas_with_tests

  name          = "_${each.value.function_name}-schema"
  registry_name = "lambda-testevent-schemas"
  type          = "OpenApi3"
  description   = "Test events for ${each.value.function_name}"

  content = jsonencode({
    openapi = "3.0.0"
    info = {
      version = "1.0.0"
      title   = "Event"
    }
    paths = {}
    components = {
      schemas = {
        Event = {
          type = "object"
        }
      }
      examples = local.test_schemas[each.key]
    }
  })

  tags = {
    Name        = "_${each.value.function_name}-schema"
    Project     = var.project_name
    Environment = var.environment
  }
}
