# agent_resolve_date_reference

Resolve referencias temporais genericas em datas concretas.

## Funcionalidade

- Converte expressoes temporais relativas em datas ISO
- Interpreta referencias como "amanha", "proxima semana", "daqui a 3 dias"
- Retorna datas unicas ou ranges de datas
- Calcula baseado no timezone America/Sao_Paulo
- Suporta semanas comerciais (segunda a domingo)

## Parametros

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| reference | string | Sim | Referencia temporal (TODAY, TOMORROW, NEXT_WEEK, +N days, etc) |

Referencias suportadas:
- Datas unicas: `TODAY`, `TOMORROW`, `+N days`, `-N days`
- Semanas: `CURRENT_WEEK`, `NEXT_WEEK`, `+N weeks`
- Meses: `CURRENT_MONTH`, `NEXT_MONTH`

## Variaveis de Ambiente

Nenhuma variavel de ambiente necessaria.
