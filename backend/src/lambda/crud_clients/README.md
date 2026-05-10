# crud_clients

Gerencia clientes do sistema via dashboard administrativo.

## Funcionalidade

- Lista clientes com paginação e filtros (ai_enabled, is_banned)
- Busca cliente específico por telefone
- Atualiza dados do cliente (nome, email, flags)
- Controla habilitação de IA por cliente
- Gerencia bloqueio de clientes

## Endpoints

- `GET /api/clients`: Lista clientes com paginação
- `GET /api/clients?phone_number={phone}`: Busca cliente específico
- `PUT /api/clients?phone_number={phone}`: Atualiza dados do cliente

## Variáveis de Ambiente

- `DYNAMODB_CLIENTS_TABLE`: Tabela DynamoDB de clientes
