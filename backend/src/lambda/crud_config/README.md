# crud_config

Gerencia configurações da aplicação via AWS AppConfig.

## Funcionalidade

- Busca configuração atual do AppConfig (GET)
- Atualiza configurações no AppConfig com deploy automático (PUT)
- Todos os valores são armazenados como strings no AppConfig

## Endpoints

- `GET /api/config`: Retorna configuração atual
- `PUT /api/config`: Atualiza configurações (aceita atualização parcial)

## Variáveis de Ambiente

- `APPCONFIG_APP_ID`: ID da aplicação AppConfig
- `APPCONFIG_ENV_ID`: ID do ambiente AppConfig
- `APPCONFIG_PROFILE_ID`: ID do perfil de configuração AppConfig
