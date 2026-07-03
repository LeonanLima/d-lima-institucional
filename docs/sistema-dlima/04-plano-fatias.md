# 04 — Plano de Execução em Fatias (para o Sonnet)

Regras de execução (skill `incremental-execution`):
- **1 fatia por vez.** Implementar → rodar `pytest` → commit → próxima.
- Commit convencional por fatia (mensagem sugerida em cada uma).
- Se uma fatia falhar na verificação, corrigir antes de avançar. Nunca
  empilhar duas fatias sem commit.
- LLM sempre mockado nos testes (fixtures em `tests/golden/`). Nenhum teste
  chama LLM ou API externa de verdade.

Repo: `C:\Users\leona\dlima-growth` (criar fora do OneDrive).

---

## F0 — Esqueleto do repo
Criar estrutura do `02-arquitetura.md`: pastas, `requirements.txt`
(pytrends, feedparser, httpx, pydantic, python-dotenv, pytest), `.env.example`,
`.gitignore` (.env, *.db, fila/, __pycache__), `README.md` com setup,
`config.py` (carrega .env, valida chaves do modo ativo, listas de termos
semente e feeds RSS), `schemas.py` com todos os modelos pydantic do
`03-contratos-agentes.md`.
**Aceite:** `pip install -r requirements.txt` ok; `pytest` roda (0 testes ok);
`python -c "from growth import config, schemas"` ok; validação de schema
testada com 2 exemplos (1 válido, 1 inválido).
**Commit:** `feat: esqueleto do dlima-growth (config, schemas, estrutura)`

## F1 — db.py
Schema SQLite do doc 03 + funções: `salvar_temas`, `salvar_pauta`,
`registrar_conteudo`, `atualizar_status`, `ja_agendado(id)`,
`titulos_ultimas_semanas(n=4)`, `registrar_execucao`. Banco criado on-demand.
**Aceite:** testes com banco temporário cobrindo cada função.
**Commit:** `feat(db): schema sqlite + funcoes de acesso`

## F2 — Fontes: Google Trends + RSS
`fontes/google_trends.py` (pytrends, termos de `config.py`, saída = lista de
dicts `{termo, crescimento_pct}`; erro de rede → lista vazia + warning
logado, nunca exceção) e `fontes/rss.py` (feedparser, últimos 7 dias,
`{titulo, fonte, url, resumo}`).
**Aceite:** testes com respostas mockadas (fixture de feed XML e de payload
pytrends); teste do caso "fonte fora do ar" retorna vazio sem quebrar.
**Commit:** `feat(fontes): google trends + rss com tolerancia a falha`

## F3 — Fonte: YouTube
`fontes/youtube.py` via YouTube Data API v3 `search.list` + `videos.list`
(httpx, chave em `.env`), últimos 7 dias, ordenar por views, máx 15 vídeos.
Sem chave configurada → lista vazia + warning (fonte opcional).
**Aceite:** testes com resposta JSON mockada; teste sem chave.
**Commit:** `feat(fontes): youtube data api (opcional)`

## F4 — llm.py (motor dos dois modos)
`gerar(prompt: str, schema: type[BaseModel]) -> BaseModel`:
- `LLM_MODE=cli`: subprocess `claude -p <prompt> --output-format json`
  (timeout 300s), extrair JSON da resposta.
- `LLM_MODE=api`: SDK `anthropic`, modelo `claude-sonnet-5`, tool-use ou
  prefill para JSON.
- Nos dois modos: validar contra o schema; se inválido, 1 repique anexando o
  erro de validação ao prompt; se falhar de novo, `LLMError`.
**Aceite:** testes mockando subprocess e SDK: caminho feliz, repique que
corrige, repique que falha; teste de JSON cercado de texto (extração).
**Commit:** `feat(llm): motor cli/api com validacao pydantic e repique`

## F5 — Agente Radar
`agentes/radar.py`: coleta das 3 fontes → monta entrada → `prompts/radar.md`
→ `gerar(..., RadarOutput)` → salva no db. Prompt pede os 10 temas com
`gancho_dlima` amarrado às linhas de serviço.
**Aceite:** golden test — entrada fixa + resposta LLM mockada de
`tests/golden/radar.json` → 10 temas válidos no db.
**Commit:** `feat(agentes): radar de tendencias`

## F6 — Agentes Estrategista + Roteirista + prompts de marca
`agentes/estrategista.py` (inclui `titulos_ultimas_semanas` no prompt para
não repetir) e `agentes/roteirista.py` (1 item por chamada; escreve `.md` na
`fila/` no formato do doc 03). Escrever `prompts/estrategista.md` e
`prompts/roteirista.md` **embutindo o Master Briefing** (copiar de
`docs/estrategia-conteudo-dlima.md` PARTE 3 do repo d-lima-institucional) e
as regras de voz da skill `dlima-brand`.
**Aceite:** golden tests dos dois agentes; validação 3+5+2 da pauta; arquivo
gerado na fila com frontmatter parseável (`status: PENDENTE`).
**Commit:** `feat(agentes): estrategista + roteirista com voz da marca`

## F7 — Agente Publicador (Metricool)
`agentes/publicador.py`: parsear frontmatter da `fila/`, agendar APROVADOs
via API Metricool (token/blog id em `.env`), idempotência via
`ja_agendado()`, fallback CSV com `METRICOOL_API=off`, atualizar status.
Antes de implementar a chamada real, verificar na doc da API Metricool o
endpoint de autoposting vigente e registrar no código a URL da doc.
**Aceite:** testes com httpx mockado (agenda, não duplica, ignora PENDENTE);
teste do CSV gerado.
**Commit:** `feat(agentes): publicador metricool com fallback csv`

## F8 — pipeline.py + agendamento + runbook
CLI `python -m growth.pipeline <comando>`:
- `semana` — radar → estrategista → roteirista → `fila/_RESUMO-SEMANA.md`
- `publicar` — publicador
- `status` — imprime fila e últimas execuções
Cada etapa registrada em `execucoes` (auditoria); falha em uma etapa não
esconde as anteriores (log claro, exit code ≠ 0).
Gerar `scripts/agendar-windows.ps1` que registra as duas tarefas no
Agendador do Windows (SEG 07:00 `semana`; TER 09:00 `publicar`).
Atualizar README com o runbook completo (rodar, aprovar, publicar, custos).
**Aceite:** `pipeline semana` end-to-end com LLM e fontes mockados gera 10
arquivos na fila; `pipeline status` legível; script ps1 com `-WhatIf` testado.
**Commit:** `feat(pipeline): cli semanal + agendamento windows + runbook`

---

## Depois do MVP (não implementar agora)

| Fase 2 | Spec a gerar com Fable 5 antes |
|---|---|
| CKO: puxar métricas do Metricool → realimentar prompt do Estrategista | sim |
| Design: imagens de carrossel com Pillow + paleta `dlima-brand` (sem CDN) | sim |
| Vídeo HeyGen a partir do roteiro aprovado | sim |
| Migração VPS + `LLM_MODE=api` + cron | não (só runbook) |
