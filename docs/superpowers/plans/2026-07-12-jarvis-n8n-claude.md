# Assistente JARVIS (n8n local + Claude Code) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Montar um assistente pessoal estilo JARVIS: n8n rodando local no Windows, conectado ao WhatsApp Business API (Meta), com três workflows (triagem de mensagens, rotina agendada, disparo de tarefas no Claude Code).

**Architecture:** n8n instalado nativo no Windows (`npm install n8n -g`), sem Docker, escutando em `localhost:5678`. WhatsApp Business API oficial da Meta como canal. Node "Execute Command" do n8n chama `claude -p "<prompt>"` no host pra acionar o Claude Code em modo headless.

**Tech Stack:** n8n (Node.js), WhatsApp Business Cloud API (Meta), Claude Code CLI (`claude -p`), Windows nativo (sem Docker).

## Global Constraints

- n8n roda nativo no Windows (`npm install n8n -g`), não em Docker.
- WhatsApp: API oficial Meta Business (não Evolution API/Baileys). Usar o período gratuito para testar; cancelar antes de virar cobrança se não compensar.
- CNPJ da D'LIMA já verificado na Meta Business — reaproveitar essa verificação.
- Ponte com Claude Code via `claude -p "<prompt>"` (modo print/headless), nunca modo interativo.
- Qualquer falha do `claude -p` ou timeout deve gerar mensagem de erro explícita no WhatsApp, nunca falhar silenciosamente.
- Fora de escopo nesta fase: hospedagem em nuvem, Evolution API, comandos de voz.

---

### Task 1: Instalar e validar n8n local

**Files:**
- Nenhum arquivo de código. Verificação: `n8n` acessível via CLI e UI em `http://localhost:5678`.

**Interfaces:**
- Consumes: nada (primeira task).
- Produces: instância n8n rodando em `localhost:5678`, disponível para as tasks seguintes configurarem workflows.

- [ ] **Step 1: Verificar Node.js instalado**

Run: `node --version`
Expected: versão >= 18.x (n8n exige Node 18+). Se não tiver, instalar Node LTS antes de continuar.

- [ ] **Step 2: Instalar n8n globalmente**

Run: `npm install n8n -g`
Expected: instalação concluída sem erros, `npm ls -g n8n` lista o pacote.

- [ ] **Step 3: Subir o n8n**

Run: `n8n start`
Expected: log mostra `Editor is now accessible via: http://localhost:5678/`

- [ ] **Step 4: Validar acesso à UI**

Abrir `http://localhost:5678` no navegador, criar a conta local de owner (usuário/senha do n8n, primeira vez que abre).
Expected: tela do editor de workflows do n8n carrega normalmente.

- [ ] **Step 5: Commit do registro de setup**

Criar `docs/superpowers/plans/jarvis-setup-notes.md` com a data e confirmação "n8n instalado e rodando em localhost:5678".

```bash
git add docs/superpowers/plans/jarvis-setup-notes.md
git commit -m "docs: registra instalação do n8n local"
```

---

### Task 2: Workflow de teste ping/pong

**Files:**
- Nenhum arquivo de código (workflow configurado na UI do n8n). Exportar o workflow como JSON para versionar: `docs/superpowers/plans/jarvis-workflows/ping-pong.json`.

**Interfaces:**
- Consumes: instância n8n da Task 1.
- Produces: webhook de teste em `http://localhost:5678/webhook/ping`, validando que webhooks funcionam antes de plugar o WhatsApp real.

- [ ] **Step 1: Criar workflow "Ping Pong" na UI do n8n**

Na UI, criar novo workflow com dois nodes:
1. Node "Webhook" (trigger), path: `ping`, método HTTP: POST.
2. Node "Respond to Webhook", body: `{"reply": "pong"}`.

Conectar Webhook → Respond to Webhook. Ativar o workflow (toggle "Active").

- [ ] **Step 2: Testar o webhook**

Run: `curl -X POST http://localhost:5678/webhook/ping -H "Content-Type: application/json" -d "{}"`
Expected: resposta `{"reply": "pong"}`.

- [ ] **Step 3: Exportar o workflow como JSON**

Na UI do n8n, usar "Download" no workflow para baixar o JSON. Salvar em:
`docs/superpowers/plans/jarvis-workflows/ping-pong.json`

- [ ] **Step 4: Commit**

```bash
mkdir -p docs/superpowers/plans/jarvis-workflows
git add docs/superpowers/plans/jarvis-workflows/ping-pong.json
git commit -m "feat(n8n): workflow de teste ping-pong"
```

---

### Task 3: Configurar WhatsApp Business API (Meta) no n8n

**Files:**
- `docs/superpowers/plans/jarvis-workflows/whatsapp-echo.json` (workflow exportado).

**Interfaces:**
- Consumes: n8n da Task 1, credencial de app da Meta Business (criada fora do n8n, no painel developers.facebook.com).
- Produces: credencial "WhatsApp Business Cloud API" configurada no n8n, reutilizável pelos Workflows 1, 2 e 3.

- [ ] **Step 1: Criar app no Meta for Developers**

No painel `developers.facebook.com`, criar um app tipo "Business", adicionar o produto "WhatsApp". Associar ao CNPJ da D'LIMA já verificado.
Expected: app criado, número de teste do WhatsApp disponível (fornecido pela Meta no sandbox), token de acesso temporário gerado.

- [ ] **Step 2: Configurar credencial no n8n**

Na UI do n8n, ir em Credentials → New → "WhatsApp Business Cloud API". Preencher com o token de acesso e o Phone Number ID do app criado no Step 1.
Expected: teste de credencial no n8n retorna sucesso (botão "Test" na tela de credencial).

- [ ] **Step 3: Criar workflow de eco simples**

Novo workflow: node "WhatsApp Trigger" (recebe mensagens) → node "WhatsApp" (envia mensagem) devolvendo o mesmo texto recebido, prefixado com "Recebi: ".

- [ ] **Step 4: Testar enviando mensagem real**

Enviar uma mensagem de teste do seu celular para o número de teste do WhatsApp Business.
Expected: resposta automática "Recebi: <sua mensagem>" chega no WhatsApp em poucos segundos.

- [ ] **Step 5: Exportar e commitar o workflow**

```bash
git add docs/superpowers/plans/jarvis-workflows/whatsapp-echo.json
git commit -m "feat(n8n): credencial e workflow eco do WhatsApp Business API"
```

---

### Task 4: Workflow 1 — Triagem de mensagens

**Files:**
- `docs/superpowers/plans/jarvis-workflows/triagem-mensagens.json`

**Interfaces:**
- Consumes: credencial WhatsApp da Task 3 (WhatsApp Trigger + node WhatsApp de envio).
- Produces: workflow ativo que classifica mensagens recebidas e responde ou notifica.

- [ ] **Step 1: Adicionar node de classificação por palavra-chave**

Após o "WhatsApp Trigger", adicionar node "Switch" com 3 saídas baseadas no texto da mensagem (`{{$json.messages[0].text.body}}`):
- Contém "orçamento", "obra", "projeto" → rota "lead_dlima"
- Contém "entrega", "encomenda", "pacote" → rota "cliente_jt"
- Caso contrário → rota "outro"

- [ ] **Step 2: Configurar resposta automática por rota**

Rota "lead_dlima": node WhatsApp envia mensagem fixa "Obrigado pelo contato! Vou te responder em breve com mais detalhes sobre o orçamento." e adiciona node "Set" marcando a mensagem para revisão manual (grava em um Google Sheet ou arquivo local de log, coluna: telefone, mensagem, timestamp).

Rota "cliente_jt": node WhatsApp envia mensagem fixa "Recebemos sua mensagem sobre entrega, aguarde retorno."

Rota "outro": node WhatsApp envia mensagem fixa "Mensagem recebida, vou verificar e te retorno."

- [ ] **Step 3: Testar as 3 rotas**

Enviar 3 mensagens de teste (uma com "orçamento", uma com "entrega", uma neutra tipo "oi").
Expected: cada uma recebe a resposta automática correspondente à sua rota.

- [ ] **Step 4: Exportar e commitar**

```bash
git add docs/superpowers/plans/jarvis-workflows/triagem-mensagens.json
git commit -m "feat(n8n): workflow de triagem de mensagens WhatsApp"
```

---

### Task 5: Workflow 2 — Rotina agendada

**Files:**
- `docs/superpowers/plans/jarvis-workflows/rotina-agendada.json`

**Interfaces:**
- Consumes: credencial WhatsApp da Task 3.
- Produces: workflow com Cron Trigger que roda diariamente e envia resumo por WhatsApp.

- [ ] **Step 1: Criar node Cron Trigger**

Node "Schedule Trigger", configurado para rodar todo dia às 8h (`0 8 * * *`).

- [ ] **Step 2: Adicionar node de composição do resumo**

Node "Set" montando uma mensagem de texto simples com placeholders manuais por enquanto (ex: "Bom dia! Resumo do dia: [confira métricas e agenda manualmente por enquanto — integração completa com Metricool fica pra uma iteração futura]").

- [ ] **Step 3: Enviar o resumo via WhatsApp**

Node "WhatsApp" enviando a mensagem montada no Step 2 para o seu próprio número.

- [ ] **Step 4: Testar disparo manual**

Na UI do n8n, usar o botão "Execute Workflow" manualmente (sem esperar o cron).
Expected: mensagem de resumo chega no seu WhatsApp.

- [ ] **Step 5: Ativar o workflow e commitar**

Ativar o toggle "Active" do workflow (agora o cron passa a rodar sozinho todo dia).

```bash
git add docs/superpowers/plans/jarvis-workflows/rotina-agendada.json
git commit -m "feat(n8n): workflow de rotina agendada diária"
```

---

### Task 6: Workflow 3 — Disparo de tarefas no Claude Code

**Files:**
- `docs/superpowers/plans/jarvis-workflows/disparo-claude.json`

**Interfaces:**
- Consumes: credencial WhatsApp da Task 3, Claude Code CLI instalado no PATH do host (`claude --version` deve funcionar no terminal).
- Produces: workflow que recebe `/tarefa <descrição>` no WhatsApp, executa `claude -p` e devolve o resultado.

- [ ] **Step 1: Validar Claude Code CLI acessível**

Run: `claude --version`
Expected: retorna a versão instalada sem erro.

- [ ] **Step 2: Adicionar filtro de comando no workflow de triagem**

No workflow "WhatsApp Trigger" (pode ser um novo trigger dedicado ou reaproveitar o node Switch da Task 4), adicionar uma condição: texto da mensagem começa com `/tarefa `.
Se verdadeiro, extrair a descrição (texto após `/tarefa `) em um node "Set" (campo `descricao`).

- [ ] **Step 3: Adicionar node Execute Command**

Node "Execute Command", comando:
```
claude -p "{{$json.descricao}}"
```
Configurar timeout do node para 300 segundos (5 min) — tarefas maiores devem ser quebradas em partes menores pelo próprio prompt.

- [ ] **Step 4: Tratar erro do Execute Command**

Adicionar node "IF" checando se o Execute Command retornou erro (`{{$json.error}}` existe ou exit code != 0).
- Se erro: node WhatsApp envia "Erro ao rodar a tarefa: {{$json.error}}".
- Se sucesso: node WhatsApp envia o `stdout` do comando como resposta.

- [ ] **Step 5: Testar com tarefa inofensiva**

Enviar no WhatsApp: `/tarefa lista os arquivos da pasta docs deste repositório`
Expected: dentro de alguns segundos/minutos, a resposta com a listagem de arquivos chega no WhatsApp.

- [ ] **Step 6: Testar caso de erro**

Enviar: `/tarefa` (sem descrição) ou uma descrição que force erro (ex: caminho inexistente).
Expected: mensagem de erro clara chega no WhatsApp, sem o workflow travar.

- [ ] **Step 7: Exportar e commitar**

```bash
git add docs/superpowers/plans/jarvis-workflows/disparo-claude.json
git commit -m "feat(n8n): workflow de disparo de tarefas no Claude Code via WhatsApp"
```

---

### Task 7: Documentação final e checklist de uso

**Files:**
- Modify: `docs/superpowers/plans/jarvis-setup-notes.md`

**Interfaces:**
- Consumes: todas as tasks anteriores concluídas e testadas.
- Produces: guia rápido de uso e manutenção do assistente.

- [ ] **Step 1: Escrever checklist de start diário**

Adicionar em `jarvis-setup-notes.md` uma seção "Como usar":
```markdown
## Como usar

1. Ligar o PC e rodar `n8n start` (ou configurar para iniciar com o Windows, se desejar).
2. Confirmar que os 3 workflows estão com o toggle "Active" ligado na UI (localhost:5678).
3. Comandos disponíveis no WhatsApp:
   - Mensagem normal: passa pela triagem automática (Workflow 1).
   - `/tarefa <descrição>`: roda a descrição no Claude Code e devolve o resultado (Workflow 3).
4. Resumo diário chega sozinho às 8h (Workflow 2).
```

- [ ] **Step 2: Registrar limitações conhecidas**

Adicionar seção "Limitações":
```markdown
## Limitações conhecidas

- n8n só funciona com o PC ligado e online (sem hospedagem em nuvem nesta fase).
- WhatsApp Business API está no período de teste gratuito da Meta — verificar prazo antes que vire cobrança.
- Tarefas via `/tarefa` têm timeout de 5 minutos; tarefas maiores devem ser quebradas em partes.
```

- [ ] **Step 3: Commit final**

```bash
git add docs/superpowers/plans/jarvis-setup-notes.md
git commit -m "docs: checklist de uso e limitações do assistente JARVIS"
```
