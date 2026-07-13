/* J.A.R.V.I.S — interface holografica (design original inspirado em HUD sci-fi).
   Tudo self-contained: canvas + Web Audio + Web Speech. Sem dependencias externas. */
"use strict";

const TOKEN = window.JARVIS_TOKEN || "";
const BACKEND = "/jarvis";

const els = {
  hud: document.getElementById("hud"),
  status: document.getElementById("status"),
  sub: document.getElementById("sub"),
  log: document.getElementById("log"),
  warn: document.getElementById("warn"),
  telemL: document.getElementById("telemL"),
  telemR: document.getElementById("telemR"),
  voiceSel: document.getElementById("voiceSel"),
  voiceTest: document.getElementById("voiceTest"),
  boot: document.getElementById("boot"),
  bootLine: document.getElementById("bootLine"),
};

/* ------------------------------------------------------------------ estado */
let state = "boot";            // boot | idle | armed | thinking | speaking
let energy = 0;                // 0..1 nivel de audio que anima o reator
let smoothEnergy = 0;
let armed = false;             // ouviu a wake word, aguardando comando
let speaking = false;
let stopped = false;

function setState(s, text) {
  state = s;
  if (text !== undefined) els.status.textContent = text;
}

/* --------------------------------------------------------------- audio in */
let audioCtx = null, analyser = null, freqData = null;

async function initAudioInput() {
  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const src = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 128;
    analyser.smoothingTimeConstant = 0.75;
    freqData = new Uint8Array(analyser.frequencyBinCount);
    src.connect(analyser);
  } catch (e) {
    analyser = null;   // segue com energia sintetica
  }
}

function sampleEnergy() {
  if (state === "speaking") {
    // fala do JARVIS: onda sintetica viva (nao da p/ capturar o audio do TTS)
    const t = performance.now() / 1000;
    return 0.45 + 0.35 * Math.abs(Math.sin(t * 6.0)) + 0.12 * Math.random();
  }
  if (analyser) {
    analyser.getByteFrequencyData(freqData);
    let sum = 0;
    for (let i = 0; i < freqData.length; i++) sum += freqData[i];
    const avg = sum / freqData.length / 255;   // 0..1
    return Math.min(1, avg * 1.8);
  }
  return 0.06 + 0.03 * Math.sin(performance.now() / 700);  // respiracao idle
}

/* ----------------------------------------------------------------- blips */
function blip(freq, dur, vol) {
  if (!audioCtx) return;
  try {
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.type = "sine"; o.frequency.value = freq;
    g.gain.setValueAtTime(0, audioCtx.currentTime);
    g.gain.linearRampToValueAtTime(vol || 0.06, audioCtx.currentTime + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + (dur || 0.12));
    o.connect(g); g.connect(audioCtx.destination);
    o.start(); o.stop(audioCtx.currentTime + (dur || 0.12) + 0.02);
  } catch (e) {}
}

/* ------------------------------------------------------------- HUD canvas */
const ctx = els.hud.getContext("2d");
let W = 0, H = 0, DPR = 1;
function resize() {
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  W = els.hud.clientWidth = window.innerWidth;
  H = els.hud.clientHeight = window.innerHeight;
  els.hud.width = W * DPR; els.hud.height = H * DPR;
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}
window.addEventListener("resize", resize);
resize();

const RINGS = [
  { r: 1.00, w: 1.5, dash: [2, 10], speed: 0.10, dir: 1,  op: 0.55 },
  { r: 0.86, w: 1.0, dash: [30, 14], speed: -0.18, dir: -1, op: 0.75 },
  { r: 0.70, w: 2.0, dash: [60, 22], speed: 0.28, dir: 1,  op: 0.9 },
  { r: 0.54, w: 1.0, dash: [4, 8], speed: -0.5, dir: -1, op: 0.6 },
];

function accent() {
  if (state === "armed") return "#ffb648";
  if (state === "thinking") return "#8be9ff";
  if (state === "speaking") return "#9ff6ff";
  return "#4fe6ff";
}

let sweep = 0;
function render() {
  const raw = sampleEnergy();
  smoothEnergy += (raw - smoothEnergy) * 0.18;
  energy = smoothEnergy;

  ctx.clearRect(0, 0, W, H);
  const cx = W / 2, cy = H * 0.46;
  const base = Math.min(W, H) * 0.28;
  const col = accent();
  const t = performance.now() / 1000;

  // grade sutil de fundo
  ctx.save();
  ctx.globalAlpha = 0.05; ctx.strokeStyle = col; ctx.lineWidth = 1;
  const g = 46;
  for (let x = (cx % g); x < W; x += g) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = (cy % g); y < H; y += g) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.restore();

  // aneis rotativos tracejados
  RINGS.forEach((ring, i) => {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(t * ring.speed + i);
    ctx.beginPath();
    ctx.arc(0, 0, base * ring.r, 0, Math.PI * 2);
    ctx.setLineDash(ring.dash);
    ctx.lineWidth = ring.w;
    ctx.strokeStyle = col;
    ctx.globalAlpha = ring.op * (0.7 + 0.3 * energy);
    ctx.shadowBlur = 12; ctx.shadowColor = col;
    ctx.stroke();
    ctx.restore();
  });

  // equalizador circular reativo (a "onda" do JARVIS)
  const bins = analyser ? freqData.length : 48;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.globalAlpha = 0.9;
  for (let i = 0; i < bins; i++) {
    let amp;
    if (state !== "speaking" && analyser) amp = freqData[i] / 255;
    else amp = 0.3 + 0.5 * Math.abs(Math.sin(t * 5 + i * 0.5)) * energy;
    const a = (i / bins) * Math.PI * 2;
    const r0 = base * 0.40;
    const r1 = r0 + amp * base * 0.28;
    ctx.beginPath();
    ctx.moveTo(Math.cos(a) * r0, Math.sin(a) * r0);
    ctx.lineTo(Math.cos(a) * r1, Math.sin(a) * r1);
    ctx.lineWidth = 2;
    ctx.strokeStyle = col;
    ctx.globalAlpha = 0.35 + 0.6 * amp;
    ctx.stroke();
  }
  ctx.restore();

  // linha de varredura girando
  sweep += 0.02;
  ctx.save();
  ctx.translate(cx, cy); ctx.rotate(sweep);
  const grad = ctx.createLinearGradient(0, 0, base, 0);
  grad.addColorStop(0, "rgba(79,230,255,0)");
  grad.addColorStop(1, col);
  ctx.strokeStyle = grad; ctx.lineWidth = 2; ctx.globalAlpha = 0.5;
  ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(base * 0.95, 0); ctx.stroke();
  ctx.restore();

  // nucleo (reator) pulsando com a energia
  const coreR = base * (0.16 + 0.06 * energy);
  const cg = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreR * 2.2);
  cg.addColorStop(0, "#eaffff");
  cg.addColorStop(0.4, col);
  cg.addColorStop(1, "rgba(79,230,255,0)");
  ctx.fillStyle = cg;
  ctx.globalAlpha = 1;
  ctx.beginPath(); ctx.arc(cx, cy, coreR * 2.2, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#f4ffff";
  ctx.beginPath(); ctx.arc(cx, cy, coreR * 0.5, 0, Math.PI * 2); ctx.fill();

  requestAnimationFrame(render);
}
requestAnimationFrame(render);

/* -------------------------------------------------------------- telemetria */
function pad(n, d) { return n.toFixed(d); }
setInterval(() => {
  const up = 96 + Math.random() * 4;
  const lat = 8 + Math.random() * 40;
  const pw = 82 + Math.random() * 16;
  const nuc = 36 + Math.random() * 3;
  els.telemL.innerHTML =
    `UPLINK <b>${pad(up,1)}%</b><br>NUCLEO <b>${pad(nuc,1)}C</b><br>MEM <b>${(50+Math.random()*30|0)}%</b>`;
  els.telemR.innerHTML =
    `POTENCIA <b>${pad(pw,0)}%</b><br>LATENCIA <b>${pad(lat,0)}ms</b><br>MODO <b>${state.toUpperCase()}</b>`;
}, 600);

/* ------------------------------------------------------------------- log */
function addLine(who, text) {
  const p = document.createElement("p");
  p.className = who === "you" ? "you" : "jarvis";
  const span = document.createElement("span");
  span.className = "lbl";
  span.textContent = (who === "you" ? "VOCE" : "JARVIS") + " ";
  p.appendChild(span);
  p.appendChild(document.createTextNode(text));
  els.log.appendChild(p);
  while (els.log.childNodes.length > 4) els.log.removeChild(els.log.firstChild);
}

/* --------------------------------------------------------------------- TTS */
let ptVoice = null;
const SAVED_VOICE = "jarvis_voice";

function loadVoices() {
  const voices = window.speechSynthesis.getVoices();
  if (!voices.length) return;
  els.voiceSel.innerHTML = "";
  voices.forEach(v => {
    const o = document.createElement("option");
    o.value = v.name; o.textContent = `${v.name} (${v.lang})`;
    els.voiceSel.appendChild(o);
  });
  const salvo = localStorage.getItem(SAVED_VOICE);
  const pt = voices.filter(v => v.lang && v.lang.toLowerCase().startsWith("pt"));
  const masc = pt.find(v => /male|masculin|ricardo|daniel|felipe|antonio|joao/i.test(v.name));
  ptVoice = voices.find(v => v.name === salvo) || masc || pt[0] || voices[0];
  if (ptVoice) els.voiceSel.value = ptVoice.name;
}
loadVoices();
window.speechSynthesis.onvoiceschanged = loadVoices;

els.voiceSel.addEventListener("change", () => {
  const voices = window.speechSynthesis.getVoices();
  ptVoice = voices.find(v => v.name === els.voiceSel.value) || ptVoice;
  if (ptVoice) localStorage.setItem(SAVED_VOICE, ptVoice.name);
});
els.voiceTest.addEventListener("click", () => speak("Bom dia, senhor. Sistemas em ordem."));

function speak(text) {
  if (!window.speechSynthesis) return;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "pt-BR";
  if (ptVoice) u.voice = ptVoice;
  u.rate = 0.98; u.pitch = 0.85;
  u.onstart = () => { speaking = true; setState("speaking", "Falando"); };
  u.onend = () => { speaking = false; setState("idle", "Diga: Ei JARVIS"); };
  window.speechSynthesis.speak(u);
}

/* ------------------------------------------------------------------ cerebro */
async function sendToBrain(text) {
  setState("thinking", "Processando"); blip(520, 0.09, 0.05);
  try {
    const res = await fetch(BACKEND, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-JARVIS-Token": TOKEN },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    const reply = (data && data.reply) ? data.reply : "Desculpe, nao recebi resposta.";
    addLine("jarvis", reply);
    speak(reply);
  } catch (e) {
    const msg = "Nao consegui falar com o meu nucleo, senhor. O servidor esta ativo?";
    addLine("jarvis", msg); speak(msg);
  }
}

/* ------------------------------------------------------- reconhecimento/wake */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SR) els.warn.textContent = "Seu navegador nao suporta reconhecimento de voz. Use o Google Chrome.";

const WAKE = /\b(e|ei|hey)\s*,?\s*(jarvis|jarves|djarvis)\b/i;
function afterWake(text) {
  const m = text.match(WAKE);
  if (!m) return null;
  return text.slice(m.index + m[0].length).replace(/^[\s,.:!?]+/, "").trim();
}

function processTranscript(raw) {
  const text = (raw || "").trim();
  if (!text) return;
  if (armed) {
    armed = false;
    addLine("you", text); sendToBrain(text);
    return;
  }
  const cmd = afterWake(text);
  if (cmd === null) return;
  // barge-in: se estava falando, interrompe para atender
  if (speaking) { window.speechSynthesis.cancel(); speaking = false; }
  if (cmd) { addLine("you", cmd); sendToBrain(cmd); }
  else { armed = true; setState("armed", "Pois nao, senhor?"); blip(680, 0.1, 0.06); speak("Pois nao, senhor?"); }
}

let wakeRec = null;
function startWake() {
  if (!SR) return;
  wakeRec = new SR();
  wakeRec.lang = "pt-BR";
  wakeRec.continuous = true;
  wakeRec.interimResults = false;
  wakeRec.maxAlternatives = 1;
  wakeRec.onresult = (ev) => {
    if (speaking) {  // so reage a wake word durante a fala (barge-in)
      const r0 = ev.results[ev.results.length - 1];
      if (r0 && r0.isFinal && WAKE.test(r0[0].transcript)) processTranscript(r0[0].transcript);
      return;
    }
    const r = ev.results[ev.results.length - 1];
    if (r && r.isFinal) processTranscript(r[0].transcript);
  };
  wakeRec.onerror = () => {};
  wakeRec.onend = () => { if (!stopped) { try { wakeRec.start(); } catch (e) {} } };
  try { wakeRec.start(); } catch (e) {}
}

// clicar em qualquer lugar arma manualmente (fala o comando sem a wake word)
document.addEventListener("click", (e) => {
  if (e.target.closest(".voicebar")) return;   // nao arma ao mexer nos controles
  if (state === "boot") return;
  if (speaking) { window.speechSynthesis.cancel(); speaking = false; }
  armed = true; setState("armed", "Ouvindo"); blip(680, 0.1, 0.06);
});

/* -------------------------------------------------------------------- boot */
const BOOT_LINES = [
  "Inicializando nucleo...",
  "Calibrando matriz de voz...",
  "Sincronizando modulos...",
  "Verificando protocolos de seguranca...",
  "Estabelecendo uplink...",
  "Sistemas online.",
];
async function boot() {
  for (const line of BOOT_LINES) {
    els.bootLine.textContent = line;
    blip(300 + Math.random() * 200, 0.05, 0.03);
    await new Promise(r => setTimeout(r, 380));
  }
  await initAudioInput();          // pede microfone (contexto seguro localhost)
  blip(760, 0.18, 0.07);
  els.boot.classList.add("gone");
  setTimeout(() => els.boot.remove(), 900);
  setState("idle", "Diga: Ei JARVIS");
  startWake();
  addLine("jarvis", "Bom dia, senhor. Estou a sua disposicao.");
  speak("Bom dia, senhor. Estou a sua disposicao.");
}
boot();
