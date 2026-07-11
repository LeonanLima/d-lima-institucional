# HANDOFF — Agência Automática D'LIMA — branch feat/agencia-automatica-dlima

## Estado atual (2026-07-11)
Motor da agência 100% implementado + 1º ciclo real rodado. Tudo commitado.

- **Núcleo Python** (`agencia/core/`): 13 testes pytest passando. `pytest.ini` com `pythonpath=.` + `--import-mode=importlib`.
- **Notion** database "Conteúdo D'LIMA", `data_source_id` `26403ca7-6f18-4db9-b805-86acd08ddcdd`. 5 cards **Aprovados**, cada um com link da arte + status de mídia.
- **Artes** (Claude Design, fonte Montserrat subsetada ~47KB) em `docs/design/pecas/`: sair-do-aluguel, obra-estoura-orcamento (Reel), quanto-custa-m2, erros-fundacao, casa-pronta-ou-construir.
- **Metricool**: marca DLIMA Engenharia, **blogId 6413932**, tz America/Sao_Paulo, IG @leonan.dlima.

## Próximo passo — CAMINHO 1 do Metricool

### FEITO
1. **PNG 1080 exportados** ✅ 18 imagens em `docs/design/pecas/png/` (commitadas). Fonte Montserrat OK.
   - Pipeline: `scratchpad/build_artes.py` + `build_carrossel.py` emitem export pages em `docs/design/pecas/export/`; `scratchpad/build_shots.py` roda Edge headless (`--headless=new --force-device-scale-factor=2 --window-size=540,540 --virtual-time-budget`, `subprocess.run` sequencial, `--user-data-dir` único por run) → PNG 1080.
   - Gotcha resolvido: export page precisa de `font-family:'Mont'` em body/.frame (só existia em .wrap) senão cai pra serif. Chrome faz handoff p/ instância aberta → usar Edge.
   - Por peça: sair-do-aluguel=6, quanto-custa-m2=5, erros-fundacao=1, casa-pronta=5, obra-estoura(Reel)=1 capa.

### PENDENTE (bloqueio que só o Leonan resolve)
2. **Confirmar Google Drive linkado no Metricool** (Config → Conexões). SEM isso o Metricool não importa as imagens.
3. **Hospedar**: subir os PNG no Google Drive do Leonan (MCP Google Drive) e pegar as URLs.
4. **Agendar**: `createScheduledPost` blogId **6413932**, instagramData type POST, media=[urls Drive na ordem dos slides], draft:true, autoPublish:false. Datas nos cards (15/21/24/28-07 às 19:00 -03:00). Carrossel = várias imagens no media[] em ordem.
5. Reel (obra-estoura): precisa de MP4, adiar.
6. Depois de publicar: analista puxa métricas → `agencia.core.memoria.registrar`.

## Armadilhas
- Metricool NÃO cria post IG sem mídia, nem como draft (`INSTAGRAM:MISSING_MEDIA`).
- Notion `create-pages` cai com payload grande → lotes de 1-2 páginas.
- Artes: sempre fonte subsetada `agencia/config/fonts-mont.css` (regenera: `scratchpad/build_fonts.py`).

## Custo
Sessão anterior chegou a ~US$128. Fazer o export em sessão limpa.
