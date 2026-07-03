# 02 — Arquitetura

## Decisão central: pipeline Python, não n8n (por enquanto)

O plano original propunha n8n self-host como orquestrador. Decisão registrada:

| Critério | Pipeline Python (escolhido) | n8n self-host |
|---|---|---|
| Custo | R$ 0 (roda no PC) | VPS ~R$ 30-50/mês desde o dia 1 |
| Quem implementa | Sonnet escreve/testa/versiona código Python muito bem | Workflows n8n são clicados na UI — Sonnet não consegue construir nem testar direito |
| Testabilidade | pytest + golden tests (padrão que você já usa) | Teste manual na interface |
| Versionamento | git, diff, rollback | Export JSON frágil |
| Manutenção | Você já mantém 3 projetos Python/Flask | Ferramenta nova para aprender |
| Quando n8n vence | — | Muitas integrações ponta-a-ponta sem lógica própria, equipe não-dev |

n8n entra na Fase 3 **se** o sistema precisar rodar 24/7 com dezenas de
integrações. O código Python migra para VPS sem reescrita (é só um cron).

## Decisão: motor LLM em dois modos

```
Modo A (padrão do MVP): Claude Code headless — `claude -p "<prompt>" --output-format json`
                        Usa a assinatura existente. Custo adicional: R$ 0.
                        Roda no PC via Agendador de Tarefas do Windows.

Modo B (Fase 3):        API Anthropic (claude-sonnet-5) via SDK python `anthropic`.
                        Para quando migrar p/ VPS 24/7. Custo estimado do volume
                        do MVP: ~US$ 3-8/mês.
```

O módulo `growth/llm.py` abstrai os dois modos atrás da mesma função
(`gerar(prompt, schema) -> dict`), escolhidos por env var `LLM_MODE=cli|api`.
Trocar de modo não toca nos agentes.

## Decisão: publicação via Metricool, não Instagram API

Instagram Graph API exige app Meta, Business verification e app review —
semanas de burocracia. O Metricool (conta já conectada) tem API própria de
agendamento e cobre Instagram, TikTok, LinkedIn e YouTube de uma vez, além
de devolver as métricas que a Fase 2 (CKO) vai consumir.

Fallback se a API do Metricool não estiver disponível no plano atual: o
Publicador gera um CSV de importação em massa do Metricool (formato oficial
deles) e o Leonan importa em 2 cliques. O contrato do agente é o mesmo.

## Decisão: estado em SQLite, não Supabase (no MVP)

Um único usuário, um único PC, dados pequenos (temas, pautas, posts,
status). SQLite resolve com zero configuração. O schema já nasce com nomes
compatíveis com Postgres; migrar para o Supabase existente na Fase 2 é um
script. **Não criar projeto Supabase novo agora.**

## Repo novo: `C:\Users\leona\dlima-growth`

Fora do OneDrive (gotcha conhecido: OneDrive corrompe operações git em massa).
Repo separado deste institucional porque tem ciclo de vida e deploy próprios.

## Estrutura de pastas

```
dlima-growth/
├── README.md               # setup + runbook (como rodar, como aprovar)
├── requirements.txt        # pytrends, feedparser, httpx, pydantic, pytest
├── .env.example            # LLM_MODE, METRICOOL_*, YOUTUBE_API_KEY
├── .gitignore              # .env, *.db, fila/ (conteúdo é artefato, não código)
├── growth/
│   ├── __init__.py
│   ├── config.py           # carrega .env, valida chaves na inicialização
│   ├── db.py               # SQLite: schema + funções de acesso (única porta p/ o banco)
│   ├── llm.py              # gerar(prompt, schema) — modo cli | api
│   ├── fontes/             # coleta de dados brutos (IO puro, sem LLM)
│   │   ├── google_trends.py
│   │   ├── rss.py
│   │   └── youtube.py
│   ├── agentes/            # 1 arquivo = 1 agente; recebe dict, devolve dict validado
│   │   ├── radar.py
│   │   ├── estrategista.py
│   │   ├── roteirista.py
│   │   └── publicador.py
│   ├── prompts/            # prompts em .md versionados (nunca hardcoded no .py)
│   │   ├── radar.md
│   │   ├── estrategista.md
│   │   └── roteirista.md
│   ├── schemas.py          # modelos pydantic = contratos do 03-contratos-agentes.md
│   └── pipeline.py         # CLI: `python -m growth.pipeline semana|aprovar|publicar`
├── fila/                   # saída do roteirista: 1 .md por conteúdo (aprovação humana)
├── tests/
│   ├── test_fontes.py
│   ├── test_agentes.py     # golden tests com respostas LLM mockadas
│   └── golden/             # JSONs de referência
└── docs/                   # cópia destas specs
```

### Camadas e direção de dependência

```
pipeline.py (orquestração/CLI)
    ↓
agentes/  (lógica de negócio — depende de schemas, llm, db)
    ↓                ↓
fontes/ (IO externo)   llm.py (motor)   db.py (estado)
    ↓
schemas.py (domínio puro — não depende de nada)
```

Regra: `fontes/` nunca chama LLM; `agentes/` nunca faz HTTP direto (usa
`fontes/` e `llm.py`); `prompts/` são dados, não código.

## Fluxo semanal (MVP)

```
SEG 07:00  Agendador Windows → python -m growth.pipeline semana
           1. Radar: coleta Trends+RSS+YouTube → top 10 temas (JSON no db)
           2. Estrategista: top 10 → pauta (3 vídeos, 5 carrosséis, 2 posts)
           3. Roteirista: pauta → 10 arquivos .md em fila/ (status: PENDENTE)
           4. Notificação: resumo no terminal + arquivo fila/_RESUMO-SEMANA.md

SEG (você, ~30 min)
           Abre fila/, edita o que quiser, muda status p/ APROVADO ou REJEITADO
           (campo `status:` no frontmatter de cada .md)

SEG/TER    python -m growth.pipeline publicar
           5. Publicador: lê APROVADOs → agenda no Metricool nos melhores
              horários → status: AGENDADO (id do Metricool salvo no db)
```

## Segurança e segredos

- Chaves só em `.env` (nunca commitadas); `config.py` falha na inicialização
  se faltar chave obrigatória do modo ativo.
- `fila/` e `*.db` no `.gitignore` — conteúdo de marca e tokens não vão pro git.
- O Publicador só age sobre `status: APROVADO`. Nunca publica direto — sempre
  **agenda**, deixando janela para cancelar no próprio Metricool.

## Custos

| Item | MVP | Fase 3 (se migrar) |
|---|---|---|
| LLM | R$ 0 (assinatura) | ~US$ 3-8/mês (API) |
| Orquestração | R$ 0 (Agendador Windows) | VPS ~R$ 30-50/mês |
| Publicação | Plano Metricool atual | idem |
| YouTube Data API | R$ 0 (cota gratuita) | R$ 0 |
| Google Trends (pytrends) | R$ 0 | R$ 0 |
| **Total adicional** | **R$ 0/mês** | ~R$ 50-90/mês |
