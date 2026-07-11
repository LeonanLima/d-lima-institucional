# HANDOFF — 2026-07-11 — Agência Automática D'LIMA — branch feat/agencia-automatica-dlima

## Objetivo da sessão
Implementar o motor da agência de marketing automática D'LIMA, rodar o 1º ciclo real
(pautas → copy → cards no Notion → aprovação → artes) e agendar as peças no Metricool.

## Estado atual
- **Feito e commitado:**
  - Núcleo Python `agencia/core/` (modelos, marca, fila_notion, memoria, ciclo) — 13 testes pytest passando.
  - Prompts dos 11 subagentes em `agencia/agentes/` + `agencia/README.md` (runbook).
  - Notion: database "Conteúdo D'LIMA" (`data_source_id` `26403ca7-6f18-4db9-b805-86acd08ddcdd`), 5 cards **Aprovados** com link da arte + status de mídia.
  - 5 artes (Claude Design, Montserrat subsetada ~47KB) publicadas como Artifact + arquivos em `docs/design/pecas/`.
  - **18 PNGs 1080** exportados em `docs/design/pecas/png/` (Montserrat OK, print-ready).
- **Em andamento:** nada aberto. Parada limpa após exportar os PNGs.
- **Não commitado:** nada relevante (só a pasta `docs/mestrado-*` intocada, de outra tarefa).

## Próximos passos (em ordem)
1. **Leonan confirma** se o Google Drive está linkado no Metricool (Config → Conexões). Bloqueio duro.
2. Subir os PNGs de `docs/design/pecas/png/` no Google Drive (MCP) e pegar as URLs.
3. Agendar via `createScheduledPost` blogId **6413932**, instagramData type POST, media=[urls na ordem dos slides], draft:true, autoPublish:false. Datas: 15/21/24/28-07 às 19:00 -03:00. Carrossel = várias imagens no media[].
4. Reel (obra-estoura): precisa de MP4 → adiar.
5. Pós-publicação: analista puxa métricas Metricool → `agencia.core.memoria.registrar`.

## Arquivos-chave
- `scratchpad/build_shots.py` — Edge headless → PNG 1080 (subprocess sequencial, user-data-dir único).
- `scratchpad/build_artes.py:78` / `build_carrossel.py:171` — geram as export pages por slide.
- `agencia/config/fonts-mont.css` — Montserrat subsetada; regenera com `scratchpad/build_fonts.py`.
- `agencia/core/ciclo.py:publicaveis` — trava dura (só publica Status=Aprovado).

## Comandos / verificação
- Testes agência: `python -m pytest tests/agencia/ -v` → último resultado: 13 passed.
- Reexportar PNGs: `python scratchpad/build_artes.py && python scratchpad/build_carrossel.py && python scratchpad/build_shots.py`.

## Armadilhas / decisões
- Metricool **não cria post IG sem mídia**, nem draft (`INSTAGRAM:MISSING_MEDIA`). Precisa de PNG/MP4 em URL pública.
- Export page precisa de `font-family:'Mont'` em body/.frame (só existia em `.wrap`) senão cai pra serif.
- Chrome faz handoff pra instância já aberta e sai sem capturar → usar **Edge** headless.
- `--screenshot` do browser exige caminho de saída absoluto (Windows).
- Notion `create-pages` cai com payload grande → lotes de 1-2 páginas.
- Custo desta sessão chegou a ~US$193. Fazer o agendamento em sessão limpa.
