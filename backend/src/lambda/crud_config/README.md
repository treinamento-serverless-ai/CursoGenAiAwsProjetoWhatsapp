# crud_config

Gerencia configuracoes da aplicacao via AWS AppConfig.

## Funcionalidade

- Busca configuracao atual do AppConfig (GET)
- Atualiza configuracoes no AppConfig com deploy automatico (PUT)
- Todos os valores sao armazenados como strings no AppConfig

## Endpoints

- `GET /api/config`: Retorna configuracao atual
- `PUT /api/config`: Atualiza configuracoes (aceita atualizacao parcial)

## Variaveis de Ambiente

- `APPCONFIG_APP_ID`: ID da aplicacao AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuracao AppConfig
