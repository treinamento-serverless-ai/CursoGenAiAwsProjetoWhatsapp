# agent_check_availability

Verifica disponibilidade de horários para agendamento.

## Funcionalidade

- Consulta agendamentos existentes no período solicitado
- Filtra por profissional (busca fuzzy por nome com `difflib.SequenceMatcher`)
- Respeita limite de dias para agendamento (AppConfig)
- Se `start_date` estiver no passado, ajusta automaticamente para hoje

## Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| start_date | string | Sim | Data início (YYYY-MM-DD) |
| end_date | string | Não | Data fim (YYYY-MM-DD), default = start_date |
| professional_name | string | Não | Nome do profissional (busca fuzzy) |

O `userId` vem via `sessionAttributes`.

## Variáveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
- `DYNAMODB_PROFESSIONALS_TABLE`: Tabela de profissionais
- `APPCONFIG_APPLICATION`: ID da aplicação AppConfig
- `APPCONFIG_ENVIRONMENT`: ID do ambiente AppConfig
- `APPCONFIG_CONFIGURATION`: ID do perfil de configuração
