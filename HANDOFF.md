# HANDOFF — 2026-07-12 — Agência Automática D'LIMA — branch feat/agencia-automatica-dlima

## Objetivo da sessão
Rodar o 1º ciclo real da agência ponta a ponta: pautas → copy → artes → aprovação no
Notion → export PNG/MP4 → agendamento no Metricool. **Concluído.**

## Estado atual
- **Feito e commitado (branch pushada em github.com/LeonanLima/d-lima-institucional, PÚBLICA):**
  - Motor Python `agencia/` (núcleo + 11 prompts) — 13 testes pytest passando.
  - 5 cards no Notion (database "Conteúdo D'LIMA", `data_source_id` `26403ca7-6f18-4db9-b805-86acd08ddcdd`), Status **Aprovado**, cada um com legenda + arte + imagens embutidas (URLs raw).
  - 18 PNGs 1080 + 1 Reel MP4 em `docs/design/pecas/png|video/`. Fonte Montserrat subsetada (`agencia/config/fonts-mont.css`).
  - **5 posts agendados no Metricool como RASCUNHO** (blogId 6413932, IG @leonan.dlima, draft=true, autoPublish=false):
    - Sair do aluguel (carrossel) 15/07 · uuid 4579518231945364485
    - Por que a obra estoura (Reel c/ trilha) 17/07 · uuid -4301832842765646043 · id 348504965
    - Quanto custa o m² (carrossel) 21/07 · uuid -1866535704249873287
    - 3 erros na fundação (feed) 24/07 · uuid 613835428435021409
    - Casa pronta ou construir (carrossel) 28/07 · uuid -2532165691179054746
- **Não commitado:** nada da agência (só pastas de outras tarefas: mestrado, transcricoes-trilha12, scratchpad de outra frente — não mexer).

## Próximos passos (em ordem)
1. Leonan abre cada rascunho no Metricool, revisa e muda de rascunho → agendado (ou publica).
2. (Opcional) trocar a minha trilha do Reel por áudio em alta do Instagram, no próprio app.
3. Após os posts saírem: fechar o loop — analista puxa métricas do Metricool e grava
   `Aprendizado` via `agencia.core.memoria.registrar` (arquivo `agencia/.memoria.json`).
4. 2º ciclo: gerar novas pautas já com `top_temas` da memória.

## Arquivos-chave
- `scratchpad/build_reel.py` + `build_reel_mp4.py` — roteiro do Reel + montagem MP4 (Edge screenshot + ffmpeg zoompan + trilha Dm sintetizada).
- `scratchpad/build_artes.py` / `build_carrossel.py` / `build_shots.py` — artes e export PNG.
- `agencia/README.md` — runbook do ciclo e trava de aprovação.

## Comandos / verificação
- Testes: `python -m pytest tests/agencia/ -v` → 13 passed.
- Reexportar imagens: `python scratchpad/build_artes.py && build_carrossel.py && build_shots.py`.
- Rebuild Reel: `python scratchpad/build_reel.py && python scratchpad/build_reel_mp4.py` (ffmpeg via WinGet Gyan).

## Armadilhas / decisões
- Metricool exige mídia em URL pública → resolvido com **GitHub raw** (repo é público; imagens de marketing, sem segredo). Para atualizar mídia num rascunho existente, use `?v=N` na URL raw pra furar cache do Metricool (foi assim que troquei o Reel).
- Export page precisa de `font-family:'Mont'` em body/.frame senão cai pra serif.
- **Chrome faz handoff pra instância aberta e não captura → usar Edge headless.**
- Screenshot exige caminho de saída absoluto Windows; render via `subprocess.run` sequencial com `--user-data-dir` único e `--virtual-time-budget=4000`.
- Decisão de marca: Reel é **texto-movimento** no visual D'LIMA + **trilha original** (acorde Dm gerado por ffmpeg, sem direito de terceiro). NÃO fabricar filmagem de obra com IA.
- Custo desta sessão: ~US$315. Próximo ciclo/ajustes: sessão limpa.
