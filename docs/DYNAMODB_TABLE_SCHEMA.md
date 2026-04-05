# DynamoDB - Schema das Tabelas

## Visão Geral

O projeto utiliza 6 tabelas DynamoDB, todas configuradas no modo **PAY_PER_REQUEST** (on-demand), sem necessidade de provisionar capacidade. As definições de infraestrutura estão em `backend/terraform/infrastructure/aws_dynamodb.tf`.

---

## Tabelas

### 1. Clients

Armazena informações dos clientes que interagem via WhatsApp.

**Chave Primária**: `phone_number` (String)

**Índices Secundários**:
- `validation_token-index`: GSI com hash key `validation_token`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `phone_number` | String | Sim | Número de telefone do cliente (formato: 5511999887766) |
| `name` | String | Não | Nome do cliente extraído do perfil WhatsApp |
| `email` | String | Não | Email do cliente (se fornecido) |
| `session_id` | String | Sim | UUID da sessão atual de conversa |
| `last_message_at` | Number | Sim | Timestamp Unix da última mensagem |
| `ai_enabled` | Boolean | Sim | Se o atendimento por IA está ativo (default: true) |
| `last_unavailable_message_date` | String | Não | Data da última mensagem automática enviada (YYYY-MM-DD) |
| `is_banned` | Boolean | Não | Se o cliente está banido |
| `validation_token` | String | Não | Token para validação do cliente |
| `created_at` | String | Não | Timestamp de criação (YYYY-MM-DDTHH:MM:SS) |

**Exemplo**:
```json
{
  "phone_number": "5511999887766",
  "name": "Carlos Silva",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "last_message_at": 1771357074,
  "ai_enabled": true,
  "last_unavailable_message_date": "2026-02-17",
  "is_banned": false,
  "created_at": "2026-02-17T10:30:00"
}
```

**Notas**:
- `last_message_at`: usado para controlar timeout de sessão (30 minutos)
- `last_unavailable_message_date`: rate limiting para mensagens automáticas (1x por dia), usado tanto para "loja fechada" quanto para "usuário banido"

---

### 2. ConversationHistory

Armazena o histórico completo de mensagens trocadas entre clientes e o sistema.

**Chave Primária**:
- Partition Key: `phone_number` (String)
- Sort Key: `timestamp` (Number)

**TTL**: habilitado no atributo `ttl`

**DynamoDB Streams**: habilitado com `NEW_AND_OLD_IMAGES`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `phone_number` | String | Sim | Número de telefone do cliente |
| `timestamp` | Number | Sim | Timestamp Unix da mensagem |
| `sender` | String | Sim | Quem enviou: `user`, `ai`, `human`, `system` |
| `content` | String | Sim | Conteúdo da mensagem |
| `message_id` | String | Não | ID da mensagem do WhatsApp (se aplicável) |
| `error` | String | Não | Descrição de erro (se sender='system') |
| `ttl` | Number | Não | Timestamp Unix para expiração automática do registro |
| `created_at` | String | Sim | Timestamp ISO de criação |

**Valores de `sender`**:
- `user`: mensagem enviada pelo cliente
- `ai`: resposta gerada pelo Bedrock Agent
- `human`: resposta de atendente humano
- `system`: mensagem do sistema (erros, notificações)

**Exemplo**:
```json
{
  "phone_number": "5511999887766",
  "timestamp": 1771357074,
  "sender": "user",
  "content": "Ola, gostaria de agendar um corte",
  "message_id": "wamid.HBgNNTUxMTk3MjgyNDE0NRU...",
  "created_at": "2026-02-17T19:37:54Z"
}
```

---

### 3. MessageBuffer

Buffer temporário para acumular mensagens antes do processamento pelo Bedrock Agent.

**Chave Primária**: `phone_number` (String)

**TTL**: habilitado no atributo `ttl`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `phone_number` | String | Sim | Número de telefone do cliente |
| `messages` | Map | Sim | Mapa de mensagens indexadas por timestamp |
| `session_id` | String | Sim | UUID da sessão atual |
| `updated_at` | Number | Sim | Timestamp Unix da última atualização |
| `ttl` | Number | Não | Timestamp Unix para expiração automática do registro |
| `transcription_attempts` | Map | Não | Contador de tentativas de transcrição de áudio |

**Estrutura de `messages`**:
```json
{
  "1771357074": {
    "id": "wamid.ABC123",
    "content": "Ola, gostaria de agendar",
    "timestamp": 1771357074
  },
  "1771357080": {
    "id": "wamid.DEF456",
    "content": null,
    "timestamp": 1771357080
  }
}
```

**Nota**: `content: null` indica mensagem de áudio pendente de transcrição.

---

### 4. Services

Catálogo de serviços oferecidos pelo estabelecimento.

**Chave Primária**: `service_id` (String)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `service_id` | String | Sim | Identificador único do serviço |
| `name` | String | Sim | Nome do serviço |
| `description` | String | Não | Descrição detalhada |
| `category` | String | Não | Categoria (Cabelo, Barba, Combo, etc.) |
| `is_active` | Boolean | Sim | Se o serviço está ativo |

**Exemplo**:
```json
{
  "service_id": "svc-001",
  "name": "Corte de Cabelo",
  "description": "Corte masculino tradicional",
  "category": "Cabelo",
  "is_active": true
}
```

---

### 5. Professionals

Informações dos profissionais que atendem no estabelecimento.

**Chave Primária**: `professional_id` (String)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `professional_id` | String | Sim | Identificador único do profissional |
| `name` | String | Sim | Nome do profissional |
| `specialty` | String | Não | Especialidade |
| `career_start_date` | String | Não | Data de início da carreira (YYYY-MM-DD) |
| `social_media_link` | String | Não | Link para rede social |
| `working_days` | List | Sim | Dias da semana que trabalha |
| `working_hours` | Map | Sim | Horário de trabalho (start, end) |
| `services` | List | Sim | Lista de serviços oferecidos com preços |
| `scheduling_policy` | Map | Sim | Política de agendamento |

**Exemplo**:
```json
{
  "professional_id": "prof-001",
  "name": "Joao Silva",
  "specialty": "Corte de cabelo cacheado",
  "working_days": ["monday", "tuesday", "wednesday"],
  "working_hours": {
    "start": "09:00",
    "end": "18:00"
  },
  "services": [
    {
      "service_id": "svc-001",
      "service_name": "Corte de Cabelo",
      "duration_hours": 0.5,
      "price": 50.00
    }
  ],
  "scheduling_policy": {
    "type": "FLEXIBLE_MINUTES",
    "allowed_start_minutes": [0, 15, 30, 45]
  }
}
```

---

### 6. Appointments

Agendamentos realizados pelos clientes.

**Chave Primária**:
- Partition Key: `appointment_id` (String)
- Sort Key: `appointment_date` (String)

**Índices Secundários**:
- `client_phone-appointment_date-index`: GSI com hash key `client_phone` e range key `appointment_date`
- `professional_id-appointment_date-index`: GSI com hash key `professional_id` e range key `appointment_date`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `appointment_id` | String | Sim | Identificador único do agendamento |
| `appointment_date` | String | Sim | Data do agendamento (YYYY-MM-DD) |
| `client_phone` | String | Sim | Telefone do cliente |
| `client_name` | String | Sim | Nome do cliente |
| `professional_id` | String | Sim | ID do profissional |
| `professional_name` | String | Sim | Nome do profissional |
| `service_id` | String | Sim | ID do serviço |
| `service_name` | String | Sim | Nome do serviço |
| `scheduled_time` | String | Sim | Hora do agendamento (HH:MM) |
| `duration_hours` | Number | Sim | Duração em horas |
| `price` | Number | Sim | Preço do serviço |
| `status` | String | Sim | Status: `scheduled`, `completed`, `cancelled`, `no_show` |
| `created_at` | String | Sim | Timestamp ISO de criação |
| `updated_at` | String | Não | Timestamp ISO da última atualização |

**Exemplo**:
```json
{
  "appointment_id": "appt-001",
  "appointment_date": "2026-02-20",
  "client_phone": "5511999887766",
  "client_name": "Carlos Silva",
  "professional_id": "prof-001",
  "professional_name": "Joao Silva",
  "service_id": "svc-001",
  "service_name": "Corte de Cabelo",
  "scheduled_time": "14:00",
  "duration_hours": 0.5,
  "price": 50.00,
  "status": "scheduled",
  "created_at": "2026-02-17T10:30:00Z"
}
```

---

## Notas Gerais

### Capacidade
Todas as tabelas usam modo **PAY_PER_REQUEST** (on-demand), sem necessidade de provisionar capacidade.

### TTL (Time To Live)
- **MessageBuffer**: TTL habilitado no atributo `ttl` para limpeza automática de registros expirados
- **ConversationHistory**: TTL habilitado no atributo `ttl` para arquivamento automático de mensagens antigas

### DynamoDB Streams
- **ConversationHistory**: Streams habilitado com `NEW_AND_OLD_IMAGES` para captura de alterações em tempo real

### Consistência
Todas as operações de leitura usam consistência eventual por padrão. Para operações críticas (agendamentos), considere usar `ConsistentRead=True`.
