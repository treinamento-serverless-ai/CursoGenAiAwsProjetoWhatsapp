# Exemplos de Webhooks do WhatsApp Business API

Esta pasta contém exemplos de payloads recebidos do webhook da Meta (WhatsApp Business API) pela Lambda de orquestração de conversas.

## Estrutura dos Exemplos

Todos os exemplos seguem o formato de evento do API Gateway (Lambda Proxy Integration) e contêm dados anonimizados para fins de documentação e testes.

### Dados Anonimizados

- **Números de telefone**: Substituídos por `5511988887777`
- **Nomes de usuário**: Substituídos por `Example User`
- **Domínios**: Substituídos por `example.serverlessai.click`
- **IDs e hashes**: Mantidos para preservar a estrutura, mas não representam dados reais

## Tipos de Mensagens

### 1. Mensagem de Texto (`text_message.json`)

Exemplo de mensagem de texto simples enviada pelo usuário.

**Características:**
- Tipo: `text`
- Contém o corpo da mensagem no campo `text.body`
- Inclui informações do contato e metadados do WhatsApp Business

### 2. Mensagem de Áudio (`audio_message.json`)

Exemplo de mensagem de áudio/voz enviada pelo usuário.

**Características:**
- Tipo: `audio`
- Formato: `audio/ogg; codecs=opus`
- Contém URL temporária para download do arquivo
- Flag `voice: true` indica que é uma mensagem de voz
- Inclui hash SHA256 para validação do arquivo

### 3. Mensagem de Imagem (`image_message.json`)

Exemplo de mensagem com imagem enviada pelo usuário.

**Características:**
- Tipo: `image`
- Formato: `image/jpeg`
- Contém URL temporária para download do arquivo
- Inclui hash SHA256 para validação do arquivo

## Estrutura Comum

Todos os webhooks compartilham a seguinte estrutura:

```json
{
  "httpMethod": "POST",
  "headers": {
    "X-Hub-Signature": "...",
    "X-Hub-Signature-256": "..."
  },
  "body": "{...}"
}
```

### Headers Importantes

- **X-Hub-Signature**: Assinatura SHA1 para validação do webhook
- **X-Hub-Signature-256**: Assinatura SHA256 para validação do webhook
- **User-Agent**: Sempre `facebookexternalua` para webhooks da Meta

### Body Structure

O campo `body` contém um JSON stringificado com:

- `object`: Sempre `whatsapp_business_account`
- `entry`: Array com as mudanças/eventos
- `entry[].changes`: Array com os detalhes da mensagem
- `entry[].changes[].value.messages`: Array com as mensagens recebidas

## Uso

Estes exemplos podem ser utilizados para:

- Testes locais da Lambda
- Desenvolvimento de parsers de mensagens
- Validação de lógica de processamento
- Documentação da estrutura de dados esperada
