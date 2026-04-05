import json
from lambda_function import lambda_handler

# Carregar evento de teste
with open('test_event.json', 'r') as f:
    event = json.load(f)

# Simular contexto Lambda
class Context:
    def __init__(self):
        self.function_name = "test-function"
        self.memory_limit_in_mb = 256
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
        self.aws_request_id = "test-request-id"

context = Context()

# Executar Lambda
print("Executando Lambda...")
response = lambda_handler(event, context)

# Exibir resultado
print("\nResposta:")
print(json.dumps(response, indent=2))

if response.get("statusCode") == 200:
    body = json.loads(response["body"])
    print("\nDetalhes do Token:")
    print(f"  Válido: {body.get('is_valid')}")
    print(f"  Expira em: {body.get('expires_at')}")
    print(f"  Dias restantes: {body.get('days_remaining')}")
