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

## Task 3 (continuacao): receber mensagens - BLOQUEADO

- Instalado cloudflared; tunel rapido publico ativo: https://palestinian-roses-places-defines.trycloudflare.com -> localhost:5678 (ngrok foi descartado: Leonan nao conseguiu criar conta).
- n8n reiniciado com WEBHOOK_URL apontando pro tunel.
- Credencial OAuth do gatilho criada no n8n (App ID 27920056227597687 + App Secret do app DLima Social).
- Workflow "eco" (so o gatilho WhatsApp Trigger por enquanto) publicado.
- Webhook cadastrado no painel Meta (produto: Conta comercial do WhatsApp) com a URL de producao do n8n + verify token "dlima2026".
- FALHA na verificacao do webhook pela Meta. Causa provavel: o WhatsApp Trigger do n8n valida o proprio verify token (nao ecoa o challenge com token arbitrario), entao "dlima2026" nao bate.

### Fragilidade estrutural identificada
- O tunel rapido da Cloudflare tem URL efemera: muda a cada reinicio do PC/tunel, quebrando o cadastro do webhook na Meta toda vez.
- Conclusao: receber mensagens em tempo real com n8n LOCAL + tunel efemero e fragil. So vale a pena quando o n8n estiver hospedado com URL fixa (VPS/Render/Cloudflare Tunnel nomeado com dominio).

### O que JA funciona
- n8n instalado e rodando; workflow ping/pong ok.
- ENVIO de mensagens WhatsApp: credencial "Conta do WhatsApp" testada com sucesso.
- Infra de tunel e OAuth prontas para quando migrar pra host fixo.
