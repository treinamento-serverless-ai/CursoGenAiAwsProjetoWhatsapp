# agent_check_availability

Verifica disponibilidade de horarios para agendamento.

## Funcionalidade

- Consulta agendamentos existentes no periodo solicitado
- Filtra por profissional (busca fuzzy por nome com `difflib.SequenceMatcher`)
- Respeita limite de dias para agendamento (AppConfig)
- Se `start_date` estiver no passado, ajusta automaticamente para hoje

## Parametros

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| start_date | string | Sim | Data inicio (YYYY-MM-DD) |
| end_date | string | Nao | Data fim (YYYY-MM-DD), default = start_date |
| professional_name | string | Nao | Nome do profissional (busca fuzzy) |

O `userId` vem via `sessionAttributes`.

## Variaveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
- `DYNAMODB_PROFESSIONALS_TABLE`: Tabela de profissionais
- `APPCONFIG_APPLICATION`: ID da aplicacao AppConfig
- `APPCONFIG_ENVIRONMENT`: ID do ambiente AppConfig
- `APPCONFIG_CONFIGURATION`: ID do perfil de configuracao
