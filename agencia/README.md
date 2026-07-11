# Agência de Marketing Automática — D'LIMA

Motor interno que pesquisa, cria, desenha, mede e aprende sozinho. Único ponto
manual: **Leonan aprova no Notion antes de publicar**. Não é SaaS multi-cliente.

## Arquitetura

- `core/` — lógica determinística e testável (dataclasses `frozen`, stdlib só).
  - `modelos.py` — `Formato`, `StatusPeca`, `Pauta`, `Peca`, `aprovar`.
  - `marca.py` — carrega/valida `config/marca.json` (fonte única de paleta e voz).
  - `fila_notion.py` — serializa `Peca` em propriedades + markdown do card.
  - `memoria.py` — store JSON de aprendizado entre ciclos.
  - `ciclo.py` — orquestrador puro: monta peças, prioriza por memória, **trava de aprovação**.
- `agentes/` — prompts markdown dos subagentes (executados via Claude/MCP em runtime).
- `config/marca.json` — paleta, arquétipo, voz. Nenhum agente hardcoda isso.

## Notion — fila de aprovação

- Página-mãe: **Agência de Marketing Automática — D'LIMA**
  (`39ad02bf-fe3f-81e2-ad75-d5abc8b3e8c1`).
- Database: **Conteúdo D'LIMA**
  - `data_source_id`: `26403ca7-6f18-4db9-b805-86acd08ddcdd`
- Colunas: `Título`(title), `Formato`(select), `Legenda`(text), `Data sugerida`(date),
  `Status`(select), `Métricas`(text), `Aprendizado`(text).
- Status: Ideação → Aguardando aprovação → **Aprovado** → Agendado → Publicado → Medido.

## Como rodar um ciclo (manual)

1. **Orquestrador** dispara o ciclo, injetando `top_temas(agencia/.memoria.json)`.
2. **CONTEÚDO**: estrategista gera 5–7 `Pauta` → pesquisador levanta ganchos →
   copywriter escreve `dict[tema -> legenda]`.
3. **MARCA**: brand-voice ajusta o tom; brand-guardian aprova/reprova cada peça.
4. `montar_pecas(pautas, legendas)` cria as `Peca` em `Aguardando aprovação`.
5. **DESIGN**: designer-post/thumb gera a arte (Claude Design, Artifact HTML+SVG) e
   preenche `Peca.arte_path` (`docs/design/pecas/<slug>.html`).
6. Cada peça vira card no Notion via `peca_para_propriedades` + `peca_para_markdown`.
7. **Leonan aprova** no Notion (Status → Aprovado) ou comenta ajuste.
8. Só as peças que passam por `publicaveis(pecas)` (status `Aprovado`) vão ao Metricool.
9. **DADOS**: analista puxa métricas do Metricool, grava `Aprendizado` via
   `memoria.registrar` — realimenta o próximo ciclo.

## Trava dura

Nada publica sem card em **`Status = Aprovado`**. A função `ciclo.publicaveis`
é o único caminho para a publicação; ela filtra qualquer peça que não esteja aprovada.

## Testes

```bash
pytest tests/agencia/ -v      # núcleo da agência (13 testes)
pytest -v                     # suíte completa (inclui o site)
```

## Memória

`agencia/.memoria.json` (ignorado no git) guarda o aprendizado entre ciclos.
Design das peças é **Claude Design**, nunca Canva.
