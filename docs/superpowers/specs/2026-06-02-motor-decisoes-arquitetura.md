# Decisões de Arquitetura — Motor de Análise Estrutural

**Data:** 2026-06-02
**Contexto:** Resolvidas antes de iniciar a execução do plano
`2026-06-01-motor-analise-estrutural.md`, conforme diagnóstico de arquitetura.

---

## ADR-1 — Estado entre `POST /api/estrutura` e `GET /api/relatorio/<id>`

**Problema:** o fluxo guarda o resultado da análise num request e o lê em outro.
Um `dict` em memória **não é compartilhado entre workers do gunicorn** → 404
intermitente em produção (Render).

**Decisão:** persistir o resultado da análise em **arquivo no filesystem**, num
diretório temporário dedicado (`tempfile.gettempdir()/dlima_estruturas/`),
nomeado por `<id>` (uuid4). `GET /api/relatorio/<id>` lê o arquivo.

**Por quê:** o filesystem é compartilhado entre os workers no mesmo host (caso do
Render single-instance), mantém o contrato `/api/relatorio/<id>` do plano sem
introduzir infra nova (Redis), e é trivial de testar.

**A implementar junto:** limpeza por TTL (apagar arquivos com mais de N horas) na
escrita, para não acumular lixo.

**Alternativas descartadas:** dict em memória (quebra com múltiplos workers);
Redis (infra desnecessária para o MVP); devolver tudo no POST (perde a URL de
relatório compartilhável).

---

## ADR-2 — Rotas do motor isoladas em Blueprint

**Problema:** `app.py` já mistura site institucional + conversor DXF. Somar as
rotas do motor no mesmo arquivo aumenta o acoplamento entre site e engine.

**Decisão:** as rotas do motor (`/api/estrutura`, `/api/relatorio/<id>`) ficam
num **Flask Blueprint** em `engine/rotas.py`, registrado no `app.py` com
`app.register_blueprint(...)`. `app.py` permanece fino.

**Por quê:** mantém o engine autocontido e testável, separa a responsabilidade
do site institucional, e deixa o `app.py` legível.

---

## ADR-3 — Pasta do código: `engine/`, não `src/`

**Problema:** existe um `src/` vazio e órfão; o plano usa `engine/` no root.
Dois lugares possíveis = ambiguidade.

**Decisão:** **remover o `src/` vazio** e usar o pacote `engine/` no root, como o
plano especifica. Site institucional continua em `app.py`/`templates/`.

**Por quê:** elimina ambiguidade antes de espalhar arquivos; consistência com o
plano já aprovado.
