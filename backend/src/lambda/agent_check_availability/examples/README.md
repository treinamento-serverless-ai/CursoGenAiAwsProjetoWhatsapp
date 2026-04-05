# Exemplos de Teste

Eventos JSON para testar a Lambda no console AWS.

## Arquivos

- `event_basic.json`: Consulta básica (Carlos Teste, próximos 7 dias)
- `event_date_range.json`: Período específico (Carlos Teste, 18-20 fev)
- `event_specific_professional.json`: Consulta simples (Ana Teste)

## Números de Telefone

- Carlos Teste: `5511999887766`
- Ana Teste: `5511988776655`

## Como Usar

1. Acesse AWS Lambda Console
2. Selecione `barbearia-silva-dev-agent-check-availability`
3. Aba "Test"
4. Cole o conteúdo de um dos arquivos JSON
5. Clique em "Test"

## Nota

Os números de telefone correspondem aos clientes criados pelo script de seed em `terraform/environments/dev/scripts/seed-data/`.

