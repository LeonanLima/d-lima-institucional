# Setup do Assistente JARVIS (n8n local + Claude Code)

## 2026-07-12

- n8n instalado globalmente via `npm install n8n -g` (v2.29.10).
- Rodando com `n8n start`, UI acessível em http://localhost:5678.
- Conta local de owner criada na primeira execução.

## Task 2: Workflow de teste ping/pong

- Workflow criado no n8n: Webhook (POST, path `ping`) -> Respond to Webhook (JSON `{"reply":"pong"}`).
- Publicado/ativado com sucesso.
- Teste `curl -X POST http://localhost:5678/webhook/ping` retornou `{"reply":"pong"}`.
- JSON exportado em `docs/superpowers/plans/jarvis-workflows/ping-pong.json`.
