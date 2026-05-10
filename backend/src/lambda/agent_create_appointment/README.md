# agent_create_appointment

Cria um novo agendamento no sistema.

## Funcionalidade

- Resolve profissional e serviço por nome via busca fuzzy (`difflib.SequenceMatcher`)
- Valida que o profissional oferece o serviço solicitado
- Verifica limite de dias para agendamento (AppConfig)
- Gera `appointment_id` automaticamente (UUID)
- Cria registro na tabela de agendamentos com status `scheduled`

## Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| appointment_date | string | Sim | Data/hora (YYYY-MM-DDTHH:MM:SS) |
| professional_name | string | Sim | Nome do profissional (busca fuzzy) |
| service_name | string | Sim | Nome do serviço (busca fuzzy) |

O `userId` vem via `sessionAttributes`.

## Variáveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
- `DYNAMODB_PROFESSIONALS_TABLE`: Tabela de profissionais
- `DYNAMODB_SERVICES_TABLE`: Tabela de serviços
- `DYNAMODB_CLIENTS_TABLE`: Tabela de clientes
- `APPCONFIG_APPLICATION`: ID da aplicação AppConfig
- `APPCONFIG_ENVIRONMENT`: ID do ambiente AppConfig
- `APPCONFIG_CONFIGURATION`: ID do perfil de configuração
