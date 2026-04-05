# agent_create_appointment

Cria um novo agendamento no sistema.

## Funcionalidade

- Valida disponibilidade do horario solicitado
- Verifica limite de dias para agendamento (AppConfig)
- Valida existencia do profissional e servico
- Cria registro na tabela de agendamentos
- Retorna confirmacao com ID do agendamento

## Parametros

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| appointment_date | string | Sim | Data/hora (YYYY-MM-DDTHH:MM:SS) |
| professional_id | string | Sim | ID do profissional |
| service_id | string | Sim | ID do servico |

## Variaveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
- `DYNAMODB_PROFESSIONALS_TABLE`: Tabela de profissionais
- `DYNAMODB_CLIENTS_TABLE`: Tabela de clientes
- `APPCONFIG_APPLICATION`: ID da aplicacao AppConfig
- `APPCONFIG_ENVIRONMENT`: ID do ambiente AppConfig
- `APPCONFIG_CONFIGURATION`: ID do perfil de configuracao
