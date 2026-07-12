# Assistente estilo JARVIS: n8n local + Claude Code

Data: 2026-07-12

## Contexto

Inspirado no vídeo "Como construí o JARVIS do Homem de Ferro no N8N" (youtube.com/watch?v=vTIq4pUR7o0). Objetivo: montar um assistente pessoal que (1) faz triagem de mensagens do WhatsApp, (2) executa rotinas agendadas (métricas, agenda, lembretes) e (3) dispara tarefas técnicas pesadas no Claude Code sob demanda ou em horário fixo, avisando quando terminar.

## Decisões

- **Hospedagem do n8n**: instalação nativa no Windows via `npm install n8n -g` (sem Docker). Roda em `localhost:5678` enquanto o PC estiver ligado. Motivo: uso solo em uma única máquina, evita a complexidade de expor o CLI do host a partir de um container Docker.
- **Canal de mensagens**: WhatsApp Business API oficial (Meta), usando o CNPJ da D'LIMA já verificado. Testar durante o período gratuito; cancelar antes de virar cobrança se não compensar.
- **Ponte com Claude Code**: node "Execute Command" do n8n chamando `claude -p "<prompt>"` (modo headless/print) diretamente no host.

## Arquitetura

```
WhatsApp (Meta Business API)
        │
        ▼
   n8n (localhost:5678, processo nativo Windows)
        │
        ├── Workflow 1: Triagem de mensagens
        ├── Workflow 2: Rotina agendada (cron)
        └── Workflow 3: Disparo sob demanda
                │
                ▼
        Execute Command → `claude -p "<prompt>"`
                │
                ▼
        Resultado devolvido → resposta no WhatsApp
```

## Componentes

### Workflow 1 — Triagem de mensagens
- Trigger: webhook do WhatsApp Business API.
- Classifica a mensagem recebida (lead D'LIMA / cliente franquia J&T / outro assunto).
- Responde automaticamente quando possível (ex: perguntas frequentes) ou notifica o usuário quando precisa de atenção humana.

### Workflow 2 — Rotina agendada
- Trigger: Cron node (ex: todo dia às 8h, horário configurável).
- Busca métricas do Instagram/Metricool, agenda do dia, lembretes pendentes.
- Envia um resumo consolidado por WhatsApp.

### Workflow 3 — Disparo sob demanda + agendado
- Sob demanda: mensagem no formato `/tarefa <descrição>` no WhatsApp aciona o workflow.
- Agendado: também pode rodar em horário fixo para tarefas recorrentes (ex: puxar métricas toda manhã já é coberto pelo Workflow 2; tarefas técnicas recorrentes entram aqui se necessário).
- Executa `claude -p "<descrição>"` via Execute Command, em background.
- Ao terminar, envia o resultado/resumo de volta como mensagem no WhatsApp.

## Tratamento de erro

- Se `claude -p` falhar (erro de execução) ou exceder um timeout definido, o workflow envia uma mensagem de erro explícita pro WhatsApp em vez de falhar silenciosamente.
- Erros de conexão com a API do WhatsApp são logados no próprio n8n (painel de execuções) para diagnóstico manual.

## Teste

1. Workflow de teste isolado: mensagem "ping" → resposta "pong", validando que o webhook do WhatsApp e o n8n estão conectados corretamente.
2. Teste do Workflow 3 com uma tarefa simples e inofensiva (ex: `/tarefa lista os arquivos da pasta docs`) antes de liberar tarefas reais de produção.
3. Validar Workflow 2 rodando manualmente uma vez (trigger manual) antes de deixar o cron ativo.

## Fora de escopo (por agora)

- API não-oficial do WhatsApp (Evolution API/Baileys) — descartada em favor da oficial.
- Hospedagem em nuvem (Render/VPS) — descartada por custo; n8n roda local por enquanto. Pode ser revisitado depois se o uso justificar disponibilidade 24/7 independente do PC.
- Comandos de voz (JARVIS "falado") — não mencionado como requisito; não incluído nesta fase.
