# Exemplos de Teste

Eventos JSON para testar a Lambda no console AWS.

## Arquivos

- `event_basic.json`: Agendamento básico (Carlos, João Silva, Corte)
- `event_different_professional.json`: Outro profissional (Ana, Maria Santos, Corte)
- `event_different_service.json`: Outro serviço (Carlos, João Silva, Combo)

## IDs Fixos

**Profissionais:**
- `prof-001`: João Silva
- `prof-002`: Maria Santos

**Serviços:**
- `svc-001`: Corte de Cabelo
- `svc-002`: Corte de Barba
- `svc-003`: Combo Cabelo + Barba

**Clientes:**
- Carlos Teste: `5511999887766`
- Ana Teste: `5511988776655`

## Como Usar

1. Execute o seed de dados: `cd terraform/environments/dev/scripts/seed-data && python3 seed_data.py`
2. Acesse AWS Lambda Console
3. Selecione `barbearia-silva-dev-agent-create-appointment`
4. Aba "Test"
5. Cole o JSON
6. Clique em "Test"


