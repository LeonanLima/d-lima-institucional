# 03 — Contratos dos Agentes (MVP)

Cada agente é uma função pura do ponto de vista de contrato: recebe um dict
validado, devolve um dict validado (pydantic em `growth/schemas.py`). O LLM
é detalhe interno. **Se a saída do LLM não validar contra o schema, o agente
tenta 1 repique com a mensagem de erro; se falhar de novo, aborta com log —
nunca segue com dado inválido.**

Os prompts (em `growth/prompts/*.md`) devem embutir o Master Briefing da
marca (`docs/estrategia-conteudo-dlima.md`, PARTE 3) e as regras de voz da
skill `dlima-brand` (arquétipo Irmão Mais Velho + Professor, lista negra de
palavras, CTAs padrão). Copiar os trechos relevantes para dentro dos
prompts na fatia F6 — o repo novo não pode depender de arquivos fora dele.

---

## Agente 1 — Radar (tendências)

**Função:** transformar dados brutos das fontes em top 10 temas ranqueados.

**Entrada** (montada pelo pipeline a partir de `fontes/`):

```json
{
  "semana": "2026-W28",
  "trends": [{"termo": "minha casa minha vida 2026", "crescimento_pct": 140}],
  "rss": [{"titulo": "...", "fonte": "AECweb", "url": "...", "resumo": "..."}],
  "youtube": [{"titulo": "...", "canal": "...", "views": 120000, "publicado_em": "2026-06-28"}]
}
```

**Fontes (MVP):**
- Google Trends via `pytrends` — termos semente: "construir casa", "minha casa
  minha vida", "financiamento caixa construção", "quanto custa construir",
  "engenheiro civil" (lista em `config.py`, editável)
- RSS: AECweb, Sienge blog, CBIC, Sinduscon-ES (lista em `config.py`)
- YouTube Data API `search.list` (últimos 7 dias, ordenado por viewCount,
  consultas = termos semente)

**Saída** (`RadarOutput`):

```json
{
  "semana": "2026-W28",
  "temas": [
    {
      "rank": 1,
      "titulo": "Novo teto do MCMV e o que muda pra quem quer construir",
      "por_que_em_alta": "Mudança na faixa 3 anunciada dia 30/06",
      "potencial": "alto",
      "formato_ideal": "video",
      "gancho_dlima": "Ligar com a linha Essencial e o financiamento Caixa",
      "fontes": ["https://..."]
    }
  ]
}
```

Regras: exatamente 10 temas; `potencial ∈ {alto, medio, baixo}`;
`formato_ideal ∈ {video, carrossel, post}`; salvar no db (tabela `temas`).

---

## Agente 2 — Estrategista

**Função:** top 10 temas → pauta semanal fechada.

**Entrada:** `RadarOutput` + histórico das últimas 4 semanas (títulos já
usados, vindos do db) para não repetir tema.

**Saída** (`PautaOutput`):

```json
{
  "semana": "2026-W28",
  "itens": [
    {
      "id": "2026-W28-01",
      "tema_rank": 1,
      "formato": "video",
      "objetivo": "autoridade",
      "titulo_trabalho": "O que o novo teto do MCMV muda pra você",
      "angulo": "Explicar a mudança em 60s e mostrar simulação real",
      "dia_sugerido": "terca",
      "linha_servico": "essencial"
    }
  ]
}
```

Regras: exatamente 3 `video` + 5 `carrossel` + 2 `post`;
`objetivo ∈ {autoridade, conexao, conversao}` com no mínimo 2 de conversão;
`linha_servico ∈ {essencial, conforto, exclusive, luxo, geral}`;
distribuir `dia_sugerido` de segunda a sábado.

---

## Agente 3 — Roteirista

**Função:** cada item da pauta → conteúdo completo pronto para aprovar.

**Entrada:** 1 item de `PautaOutput` por chamada (LLM foca melhor em 1 peça
por vez; o pipeline itera os 10).

**Saída** (`ConteudoOutput`) — persistida como arquivo em `fila/`:

```json
{
  "id": "2026-W28-01",
  "formato": "video",
  "roteiro": "GANCHO (0-3s): ...\nDESENVOLVIMENTO: ...\nCTA: ...",
  "slides": null,
  "legenda": "...",
  "cta": "Chama no WhatsApp e simula sem compromisso",
  "hashtags": ["#mcmv", "#construirnoES", "..."],
  "duracao_estimada_s": 60
}
```

- `video`: `roteiro` preenchido (marcações de tempo, fala natural, máx 3 min),
  `slides = null`
- `carrossel`: `slides` = lista de 6-10 strings (1 por slide, com slide 1 =
  gancho e último = CTA), `roteiro = null`
- `post`: `roteiro` = texto corrido técnico-acessível, `slides = null`

**Formato do arquivo na fila** (`fila/2026-W28-01-video.md`):

```markdown
---
id: 2026-W28-01
formato: video
status: PENDENTE        # PENDENTE | APROVADO | REJEITADO | AGENDADO
dia_sugerido: terca
---
# O que o novo teto do MCMV muda pra você
(conteúdo renderizado legível: roteiro/slides, legenda, CTA, hashtags)
```

Regras de voz (embutir no prompt): arquétipo da marca, proibido "clichês de
coach", português direto, sem promessa de prazo/preço fechado, CTA sempre
para o WhatsApp.

---

## Agente 4 — Publicador

**Função:** agendar no Metricool tudo que está `APROVADO`. **Sem LLM.**

**Entrada:** arquivos de `fila/` com `status: APROVADO` + calendário de
melhores horários (constante em `config.py`, ajustável; default: dias
sugeridos às 11h30 e 18h30, alternando).

**Comportamento:**
1. Para cada aprovado: montar payload (legenda + hashtags; vídeo entra como
   rascunho/lembrete com o roteiro em notas — gravação ainda é humana).
2. Chamar a API do Metricool (autoposting). Guardar `metricool_id` no db.
3. Atualizar frontmatter para `status: AGENDADO`.
4. **Fallback CSV:** se `METRICOOL_API=off`, gerar `fila/_importar-metricool.csv`
   no formato de importação em massa do Metricool.

**Saída** (`PublicacaoOutput`): lista de `{id, plataforma, agendado_para,
metricool_id | csv}` + resumo impresso no terminal.

Regras: idempotente (rodar 2x não duplica agendamento — checar `metricool_id`
no db antes); nunca tocar em `PENDENTE`/`REJEITADO`.

---

## Tabelas SQLite (db.py)

```sql
temas(semana, rank, titulo, potencial, formato_ideal, json, criado_em)
pauta(id PK, semana, formato, objetivo, titulo_trabalho, json, criado_em)
conteudos(id PK → pauta.id, status, arquivo, metricool_id, agendado_para, atualizado_em)
execucoes(id PK, etapa, semana, ok, erro, iniciado_em, terminado_em)  -- auditoria
```
