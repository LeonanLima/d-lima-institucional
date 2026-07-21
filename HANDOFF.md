# HANDOFF — 2026-07-13 — feat/agencia-automatica-dlima (trabalho: JARVIS)

## Objetivo da sessão
Construir um assistente pessoal estilo JARVIS (Homem de Ferro). Começou tentando via
n8n+WhatsApp (bloqueou), pivotou para um JARVIS de voz local com o Claude Code como
cérebro, evoluído até HUD holográfico + wake word + execução de tarefas nos projetos.

## Estado atual
- **Feito e commitado** (tudo verde, servidor testado):
  - JARVIS de voz local em `jarvis/` — v1 (voz), v2 (habilidades), v3 (executar
    tarefas nos projetos), segurança (token+sem CORS), wake word "Ei JARVIS",
    persona/voz estilo filme, seletor de voz, e HUD holográfico (canvas: reator,
    anéis, visualizador de áudio reativo, boot, telemetria, barge-in, blips).
    Último commit JARVIS: `21dc678`.
  - Brief da voz realista ElevenLabs: `docs/superpowers/plans/2026-07-12-jarvis-elevenlabs-voz-realista.md` (commit `48c2e17`) — pronto p/ execução.
  - Fix no repo `dlima-estrutural` (fora deste repo): golden da malha regenerado p/
    cm inteiro; suíte 1080 passed. Commit lá: `79db2b5` (branch feat/api-fastapi-ponte).
- **Em andamento:** nada aberto.
- **Não commitado:** nada do JARVIS. (Só untracked de outros assuntos: docs/mestrado-*,
  docs/transcricoes-*, scratchpad/* — ignorar.)

## Próximos passos (em ordem)
1. (Quando Leonan tiver conta+API key ElevenLabs) Implementar o brief
   `docs/superpowers/plans/2026-07-12-jarvis-elevenlabs-voz-realista.md` — endpoint
   `/speak` no backend + `speak()` no frontend com fallback. Mecânico.
2. (Opcional) Cérebro por API rápida no lugar de `claude -p` p/ respostas mais ágeis
   (precisa de chave/custo — decidir com Leonan).
3. (Opcional) Voz masculina: se o seletor não listar voz masculina pt-BR, instalar
   vozes no Windows (Config → Hora e Idioma → Fala) — ou seguir p/ ElevenLabs.
4. Pendências antigas não-JARVIS: ver memória project_assistente_jarvis_n8n
   (recebimento WhatsApp bloqueado até hospedar n8n em URL fixa).

## Arquivos-chave
- `jarvis/backend/app.py` — Flask: serve HUD, token de sessão, `/jarvis` (cérebro via
  `claude -p` por stdin), `/app.js`, roteamento skills + execução em projeto c/ confirmação.
- `jarvis/backend/skills.py` — habilidades diretas (abrir/notas/hora/cálculo) + lista
  branca de projetos + confirmação falada.
- `jarvis/frontend/app.js` — HUD canvas, wake word, TTS, visualizador reativo.
- `jarvis/data/projects.json` — lista branca (nome falado→pasta); `notes.json` é gitignored.

## Comandos / verificação
- Rodar: `pip install -r jarvis/requirements.txt` (flask); `python jarvis/backend/app.py`
  (porta 8756); abrir `http://127.0.0.1:8756/` no **Chrome**; permitir microfone.
- Usar: falar "Ei JARVIS, <comando>"; p/ tarefa em projeto: "no projeto <nome>, <tarefa>"
  → ele pede "Confirma?" → dizer "confirma".
- Último teste: backend `/health` 200; `/app.js` 200 (13KB); persona respondeu
  "...senhor..."; tarefa real no estrutural rodou os testes (achou os 2 golden, já corrigidos).

## Armadilhas / decisões
- `claude -p` recebe o prompt por **stdin** (arg estoura o limite de linha do Windows).
- n8n **local** não serve p/ receber WhatsApp (túnel efêmero); só com host fixo.
- Voz idêntica ao ator do filme: não fazer (voz de pessoa real). HUD é design
  **original** inspirado (não copiar assets Marvel).
- `--dangerously-skip-permissions` na execução em projeto é intencional (Leonan escolheu
  poder total), protegido por token + lista branca + confirmação falada. Manter guardrails.
- Sessão ficou cara por automação de navegador — na próxima, guiar Leonan por passos
  em vez de controlar o browser quando possível.
