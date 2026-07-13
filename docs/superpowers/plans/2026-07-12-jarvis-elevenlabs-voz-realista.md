# Brief de implementação: voz realista (ElevenLabs) no JARVIS

> **Direção para o Sonnet executar.** Trabalho mecânico bem definido. Pré-requisito
> externo (do Leonan): conta ElevenLabs + API key + escolher um `voice_id` (voz
> masculina, de preferência com sotaque britânico, pro clima JARVIS do filme).

**Objetivo:** trocar a voz sintética do navegador (`speechSynthesis`) por áudio
realista da ElevenLabs, mantendo fallback automático pro navegador quando a chave
não estiver configurada.

## Regras inegociáveis (segurança)

- A API key fica **só no servidor**, lida de variável de ambiente
  `ELEVENLABS_API_KEY`. **Nunca** hardcode, **nunca** commit, **nunca** exposta no
  frontend. Adicionar `.env` ao `.gitignore` se usado.
- O endpoint novo `/speak` exige o **mesmo token de sessão** (`X-JARVIS-Token`) que
  o `/jarvis`, e corpo JSON (mesma função `_authorized()`).
- Se `ELEVENLABS_API_KEY` não existir no ambiente → o backend responde 501 e o
  frontend cai no `speechSynthesis` atual (degradação graciosa, nada quebra).

## Backend — `jarvis/backend/app.py`

1. Config (topo):
   ```python
   ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
   ELEVEN_VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "")   # id da voz escolhida
   ELEVEN_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
   ```

2. Novo endpoint (usa `requests`; já é dependência comum, senão adicionar):
   ```python
   import requests

   @app.route("/speak", methods=["POST"])
   def speak():
       if not _authorized():
           abort(403)
       if not (ELEVEN_KEY and ELEVEN_VOICE):
           return jsonify({"error": "eleven_not_configured"}), 501
       text = (request.get_json(silent=True) or {}).get("text", "").strip()
       if not text:
           return jsonify({"error": "empty"}), 400
       url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE}/stream"
       r = requests.post(
           url,
           headers={"xi-api-key": ELEVEN_KEY, "accept": "audio/mpeg",
                    "content-type": "application/json"},
           json={"text": text, "model_id": ELEVEN_MODEL,
                 "voice_settings": {"stability": 0.4, "similarity_boost": 0.8,
                                    "style": 0.3, "use_speaker_boost": True}},
           timeout=30, stream=True,
       )
       if r.status_code != 200:
           return jsonify({"error": "eleven_failed", "status": r.status_code}), 502
       return Response(r.iter_content(chunk_size=4096), mimetype="audio/mpeg")
   ```
   - Importar `Response` de flask. O endpoint `/stream` da ElevenLabs devolve o
     áudio conforme gera → começa a tocar antes (menos latência).
   - Adicionar `requests` ao `jarvis/requirements.txt`.

## Frontend — `jarvis/frontend/app.js`

Trocar a função `speak(text)` por: tenta ElevenLabs (áudio real); se falhar/501,
usa o `speechSynthesis` atual como fallback.

```javascript
let jarvisAudio = null;      // <audio> reutilizado
let audioSrcNode = null;     // liga o audio ao analyser (visualizador reativo)

async function speak(text) {
  // 1) tenta voz realista no servidor
  try {
    const res = await fetch("/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-JARVIS-Token": TOKEN },
      body: JSON.stringify({ text })
    });
    if (res.status === 501) return speakBrowser(text);   // sem chave -> fallback
    if (!res.ok) return speakBrowser(text);
    const blob = await res.blob();
    playRealAudio(URL.createObjectURL(blob));
    return;
  } catch (e) {
    return speakBrowser(text);
  }
}

function playRealAudio(src) {
  if (!jarvisAudio) jarvisAudio = new Audio();
  jarvisAudio.src = src;
  jarvisAudio.onplay = () => { speaking = true; setState("speaking", "Falando"); };
  jarvisAudio.onended = () => { speaking = false; setState("idle", "Diga: Ei JARVIS"); };
  // BONUS: liga o audio real ao analyser -> o equalizador reage a voz de verdade
  try {
    if (audioCtx && !audioSrcNode) {
      audioSrcNode = audioCtx.createMediaElementSource(jarvisAudio);
      const an = audioCtx.createAnalyser(); an.fftSize = 128;
      audioSrcNode.connect(an); audioSrcNode.connect(audioCtx.destination);
      window._jarvisSpeakAnalyser = an;   // usar em sampleEnergy quando speaking
    }
  } catch (e) {}
  jarvisAudio.play();
}

// renomear a função atual `speak` (speechSynthesis) para `speakBrowser`.
```

Ajuste em `sampleEnergy()`: quando `state === "speaking"` e existir
`window._jarvisSpeakAnalyser`, ler dele em vez do sintético — o visualizador passa
a pulsar com a **voz real** do JARVIS. Se não existir, mantém o sintético.

## Passos do Leonan (uma vez)

1. Criar conta em elevenlabs.io e gerar a API key.
2. Escolher uma voz (Voice Library) masculina/britânica e copiar o `voice_id`.
3. Definir as variáveis antes de subir o servidor (PowerShell):
   ```powershell
   $env:ELEVENLABS_API_KEY = "<sua-chave>"
   $env:ELEVENLABS_VOICE_ID = "<id-da-voz>"
   python app.py
   ```

## Verificação (Sonnet, após implementar)

1. Sem as env vars: `/speak` retorna 501 e o front fala pelo navegador (fallback ok).
2. Com as env vars: `curl -s -X POST /speak -H "X-JARVIS-Token: <tok>" -H "Content-Type: application/json" -d '{"text":"teste"}' -o teste.mp3` gera um mp3 tocável.
3. No Chrome: falar "Ei JARVIS" → resposta sai com a voz realista e o equalizador
   reage à voz real.

## Fora de escopo deste brief

- Clonagem da voz específica do ator do filme (voz de pessoa real — não fazer).
- Cache de áudios / limites de uso da conta ElevenLabs.
