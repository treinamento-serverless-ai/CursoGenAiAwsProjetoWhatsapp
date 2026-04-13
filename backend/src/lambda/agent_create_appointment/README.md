# agent_create_appointment

Cria um novo agendamento no sistema.

## Funcionalidade

- Resolve profissional e servico por nome via busca fuzzy (`difflib.SequenceMatcher`)
- Valida que o profissional oferece o servico solicitado
- Verifica limite de dias para agendamento (AppConfig)
- Gera `appointment_id` automaticamente (UUID)
- Cria registro na tabela de agendamentos com status `scheduled`

## Parametros

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| appointment_date | string | Sim | Data/hora (YYYY-MM-DDTHH:MM:SS) |
| professional_name | string | Sim | Nome do profissional (busca fuzzy) |
| service_name | string | Sim | Nome do servico (busca fuzzy) |

O `userId` vem via `sessionAttributes`.

## Variaveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
- `DYNAMODB_PROFESSIONALS_TABLE`: Tabela de profissionais
- `DYNAMODB_SERVICES_TABLE`: Tabela de servicos
- `DYNAMODB_CLIENTS_TABLE`: Tabela de clientes
- `APPCONFIG_APPLICATION`: ID da aplicacao AppConfig
- `APPCONFIG_ENVIRONMENT`: ID do ambiente AppConfig
- `APPCONFIG_CONFIGURATION`: ID do perfil de configuracao
