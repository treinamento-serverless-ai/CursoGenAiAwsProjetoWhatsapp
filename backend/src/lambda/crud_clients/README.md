# crud_clients

Gerencia clientes do sistema via dashboard administrativo.

## Funcionalidade

- Lista clientes com paginacao e filtros (ai_enabled, is_banned)
- Busca cliente especifico por telefone
- Atualiza dados do cliente (nome, email, flags)
- Controla habilitacao de IA por cliente
- Gerencia bloqueio de clientes

## Endpoints

- `GET /api/clients`: Lista clientes com paginacao
- `GET /api/clients?phone_number={phone}`: Busca cliente especifico
- `PUT /api/clients?phone_number={phone}`: Atualiza dados do cliente

## Variaveis de Ambiente

- `DYNAMODB_CLIENTS_TABLE`: Tabela DynamoDB de clientes
