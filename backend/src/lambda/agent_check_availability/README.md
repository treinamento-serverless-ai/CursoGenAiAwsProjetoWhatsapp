# agent_check_availability

Verifica disponibilidade de horarios para agendamento.

## Funcionalidade

- Consulta agendamentos existentes no periodo solicitado
- Filtra por profissional especifico (opcional)
- Respeita horario de funcionamento (AppConfig)
- Respeita limite de dias para agendamento (AppConfig)
- Retorna lista de slots disponiveis

## Parametros

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| start_date | string | Sim | Data inicio (YYYY-MM-DD) |
| end_date | string | Nao | Data fim (YYYY-MM-DD) |
| professional_id | string | Nao | ID do profissional |

## Variaveis de Ambiente

- `DYNAMODB_APPOINTMENTS_TABLE`: Tabela de agendamentos
- `DYNAMODB_PROFESSIONALS_TABLE`: Tabela de profissionais
- `APPCONFIG_APPLICATION`: ID da aplicacao AppConfig
- `APPCONFIG_ENVIRONMENT`: ID do ambiente AppConfig
- `APPCONFIG_CONFIGURATION`: ID do perfil de configuracao
