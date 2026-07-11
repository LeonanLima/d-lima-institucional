# HANDOFF — Agência Automática D'LIMA — branch feat/agencia-automatica-dlima

## Estado atual (2026-07-11)
Motor da agência 100% implementado + 1º ciclo real rodado. Tudo commitado.

- **Núcleo Python** (`agencia/core/`): 13 testes pytest passando. `pytest.ini` com `pythonpath=.` + `--import-mode=importlib`.
- **Notion** database "Conteúdo D'LIMA", `data_source_id` `26403ca7-6f18-4db9-b805-86acd08ddcdd`. 5 cards **Aprovados**, cada um com link da arte + status de mídia.
- **Artes** (Claude Design, fonte Montserrat subsetada ~47KB) em `docs/design/pecas/`: sair-do-aluguel, obra-estoura-orcamento (Reel), quanto-custa-m2, erros-fundacao, casa-pronta-ou-construir.
- **Metricool**: marca DLIMA Engenharia, **blogId 6413932**, tz America/Sao_Paulo, IG @leonan.dlima.

## Próximo passo — CAMINHO 1 do Metricool (retomar aqui, sessão limpa)
Objetivo: agendar as 5 no Metricool. IG exige mídia como arquivo (PNG/MP4) em URL pública.

1. **Exportar PNG 1080**: cada slide `.frame` das artes vira PNG 1080x1080 (carrossel = 1 PNG por slide). Opção barata: gerar páginas export standalone 1080px via builder e screenshot com Playwright (ou headless). Frames por peça: sair-do-aluguel=6, quanto-custa-m2=5, erros-fundacao=1, casa-pronta=5. obra-estoura = Reel, precisa de MP4 (adiar).
2. **Hospedar**: subir PNGs no Google Drive do Leonan (MCP Google Drive). Metricool importa de Drive SE o Leonan tiver o Drive linkado na conta Metricool (verificar antes).
3. **Agendar**: `createScheduledPost` blogId 6413932, instagramData type POST (carrossel/feed), media=[urls do Drive], draft:true, autoPublish:false. Datas sugeridas nos cards (15/17/21/24/28-07 às 19:00 -03:00).
4. Ao publicar depois: analista puxa métricas Metricool → `agencia.core.memoria.registrar`.

## Armadilhas
- Metricool NÃO cria post IG sem mídia, nem como draft (`INSTAGRAM:MISSING_MEDIA`).
- Notion `create-pages` cai com payload grande → lotes de 1-2 páginas.
- Artes: sempre fonte subsetada `agencia/config/fonts-mont.css` (regenera: `scratchpad/build_fonts.py`).

## Custo
Sessão anterior chegou a ~US$128. Fazer o export em sessão limpa.
