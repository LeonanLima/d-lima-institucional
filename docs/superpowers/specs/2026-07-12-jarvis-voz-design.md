# JARVIS de voz (assistente pessoal estilo Homem de Ferro)

Data: 2026-07-12

## Contexto

Leonan quer um assistente de voz estilo JARVIS (Homem de Ferro): fala com ele e ele responde falando. Inspirado num vídeo onde o criador pediu ao Claude Code pra construir. Como o Claude Code não consegue assistir ao vídeo nem acessar o template, esta versão é criada do zero, com o `claude` CLI como cérebro. Roda 100% local no PC do Leonan (Windows), sem depender de hospedagem/webhook (evita o bloqueio que travou a versão WhatsApp/n8n).

## Objetivo

v1: falar com o assistente e receber respostas faladas, em português, com um visual estilo JARVIS. Conversa e responde de verdade (o cérebro é o Claude). "Fazer tarefas pesadas" (controlar apps, rodar projetos) fica para v2, no mesmo esqueleto.

## Arquitetura

```
Você fala
   │  (microfone)
   ▼
Navegador (Chrome) — página local index.html
   │  Web Speech API: SpeechRecognition (fala → texto, pt-BR)
   ▼
POST /jarvis  {text}
   │
   ▼
Backend Flask (localhost:8756)
   │  chama:  claude -p "<texto>" --append-system-prompt "<persona JARVIS>"
   ▼
Resposta em texto  {reply}
   │
   ▼
Navegador — speechSynthesis (texto → fala, voz pt-BR)  →  Você ouve
```

## Componentes

### Backend — `jarvis/backend/app.py`
- Flask com CORS liberado para localhost.
- Rota `POST /jarvis`: recebe JSON `{"text": "..."}`, chama o `claude` CLI em modo headless (`claude -p`) com um system prompt que define a persona JARVIS (educado, direto, trata o Leonan por "senhor" opcional, responde em português, respostas curtas e faladas — sem markdown/emoji porque vai virar áudio).
- Mantém histórico simples em memória (lista de turnos) para dar continuidade dentro da sessão; monta o prompt incluindo os últimos N turnos.
- Timeout de 60s na chamada do `claude`; se falhar, retorna `{"reply": "Desculpe, tive um problema para processar isso."}` com status 200 (para o front sempre falar algo).
- Rota `GET /health`: retorna `{"status": "ok"}`.

### Frontend — `jarvis/frontend/index.html`
- Página única, self-contained (HTML+CSS+JS inline), visual escuro estilo JARVIS: fundo escuro, círculo/"reator" central com glow azul-ciano que pulsa quando ouve/fala.
- Botão grande de microfone (push-to-talk / toggle): clica para começar a ouvir, transcreve com `webkitSpeechRecognition` (lang `pt-BR`).
- Mostra na tela: o que ele ouviu ("você:") e o que está respondendo ("JARVIS:").
- Ao receber a resposta do backend, fala com `speechSynthesis` usando uma voz pt-BR (escolhe a primeira voz pt-BR disponível).
- Estados visuais: ocioso, ouvindo (glow pulsa), pensando (spinner), falando (glow forte).

### `jarvis/requirements.txt`
- flask, flask-cors

### `jarvis/README.md`
- Como rodar: instalar deps, `python backend/app.py`, abrir `frontend/index.html` no Chrome (ou servir via o próprio Flask), permitir microfone.

## Decisões

- **STT e TTS pelo navegador** (Web Speech API): zero instalação pesada, sem baixar modelos (Whisper). Requer Chrome + internet (o STT do Chrome usa nuvem Google) + permissão de microfone.
- **Cérebro via `claude` CLI** (`claude -p`): usa a assinatura existente do Leonan, sem API key nova nem custo por conversa. Aceita-se que cada resposta leve alguns segundos.
- **Push-to-talk** (clicar no microfone) em vez de wake word sempre-ligada: mais confiável no navegador.
- **Local only**: nada de hospedagem/webhook nesta fase.

## Tratamento de erro

- Se o `claude` CLI falhar/estourar timeout: backend retorna uma frase de desculpa (o assistente sempre fala algo, nunca trava mudo).
- Se o navegador não suportar Web Speech API (ex: Firefox): a página mostra aviso pedindo pra usar o Chrome.
- Se não houver voz pt-BR instalada: usa a voz padrão e avisa no console.

## Teste

1. `GET /health` retorna `{"status":"ok"}`.
2. `POST /jarvis` com `{"text":"que horas são no Japão"}` (ou algo simples) retorna um `{"reply": "..."}` em texto.
3. Abrir a página no Chrome, clicar no microfone, falar uma frase e confirmar que: (a) aparece o texto reconhecido, (b) o backend responde, (c) o assistente fala a resposta.

## Fora de escopo (v1)

- Wake word sempre-ligada ("Ei JARVIS").
- Executar tarefas reais (controlar apps, rodar projetos) — v2.
- Voz clonada/realista (ElevenLabs etc.) — usa a voz nativa do navegador por enquanto.
- Hospedagem / acesso fora do PC.
