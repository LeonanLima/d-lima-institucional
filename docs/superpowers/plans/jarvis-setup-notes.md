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

## Task 3: Credencial WhatsApp Business API no n8n

- App Meta "DLima Social" (Business: DLIMA Engenharia) ja tinha o caso de uso WhatsApp habilitado e empresa verificada.
- Numero de teste solicitado: +1 (555) 609-3606. Phone Number ID: 1261190323735420. WhatsApp Business Account ID: 2818234398529467.
- Numero pessoal do Leonan (+55 28 99964-6592) verificado como destinatario de teste.
- Token de acesso gerado manualmente pelo Leonan (geracao via automacao de navegador nao funcionou - so registrava clique de analytics, sem chamar a API real).
- Credencial "Conta do WhatsApp" (tipo API do WhatsApp) criada no n8n com token de acesso + ID da conta comercial (2818234398529467). Conexao testada com sucesso.
- Token de acesso NAO foi salvo em nenhum arquivo do repositorio (fica apenas dentro do n8n, criptografado no banco local).
