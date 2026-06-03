import * as M from "./editor-modelo.js";
import * as Canvas from "./editor-canvas.js";
import * as UI from "./editor-ui.js";
import * as Resultados from "./editor-resultados.js";

const CHAVE_AUTOSAVE = "dlima.editor.estrutura";

const svg = document.getElementById("canvas");
const painel = document.getElementById("painel");
const banner = document.getElementById("banner");

const estado = { modelo: carregarAutosave(), modo: "selecionar",
                 selecionado: null, primeiroNo: null,
                 resultado: null, relatorioId: null, suprimirClick: false };

let arrasto = null;  // { no, startX, startY, moveu }

function invalidarResultado() { estado.resultado = null; estado.relatorioId = null; }

function carregarAutosave() {
  try {
    const raw = localStorage.getItem(CHAVE_AUTOSAVE);
    if (raw) return M.fromJson(JSON.parse(raw));
  } catch (_) { /* ignora */ }
  return M.criarModelo();
}
function autosave() {
  try { localStorage.setItem(CHAVE_AUTOSAVE, JSON.stringify(M.toJson(estado.modelo))); }
  catch (_) { /* localStorage indisponivel: degrada sem autosave */ }
}

function redesenhar() {
  Canvas.render(svg, estado.modelo, estado);
  const resumo = estado.resultado ? Resultados.resumoResultado(estado.resultado) : null;
  UI.renderPainel(painel, estado.modelo, estado.selecionado, cbs, resumo, estado.relatorioId);
  autosave();
}

function noEm(ev) {
  const alvo = ev.target;
  if (alvo && alvo.dataset && alvo.dataset.no)
    return estado.modelo.nos.find((n) => n.id === +alvo.dataset.no);
  return null;
}
function barraEm(ev) {
  const alvo = ev.target;
  if (alvo && alvo.dataset && alvo.dataset.barra)
    return estado.modelo.elementos.find((e) => e.id === alvo.dataset.barra);
  return null;
}

svg.addEventListener("click", (ev) => {
  if (estado.suprimirClick) { estado.suprimirClick = false; return; }
  if (estado.modo !== "selecionar") invalidarResultado();
  const rect = svg.getBoundingClientRect();
  const px = ev.clientX - rect.left, py = ev.clientY - rect.top;
  const noClicado = noEm(ev);
  const barraClicada = barraEm(ev);

  if (estado.modo === "no") {
    const { x, y } = Canvas.pxParaMetro(px, py);
    M.addNo(estado.modelo, x, y);
  } else if (estado.modo === "barra") {
    if (noClicado && !estado.primeiroNo) { estado.primeiroNo = noClicado; }
    else if (noClicado && estado.primeiroNo && noClicado.id !== estado.primeiroNo.id) {
      M.addBarra(estado.modelo, estado.primeiroNo.id, noClicado.id);
      estado.primeiroNo = null;
    }
  } else if (estado.modo === "apagar") {
    apagar(noClicado, barraClicada);
  } else if (estado.modo === "selecionar") {
    estado.selecionado = noClicado || barraClicada || null;
  }
  redesenhar();
});

svg.addEventListener("mousedown", (ev) => {
  if (estado.modo !== "selecionar") return;
  const no = noEm(ev);
  if (no) arrasto = { no, startX: ev.clientX, startY: ev.clientY, moveu: false };
});

svg.addEventListener("mousemove", (ev) => {
  if (!arrasto) return;
  if (!arrasto.moveu) {
    if (Math.hypot(ev.clientX - arrasto.startX, ev.clientY - arrasto.startY) < 3) return;
    arrasto.moveu = true;
    estado.selecionado = arrasto.no;
    invalidarResultado();
  }
  const rect = svg.getBoundingClientRect();
  const { x, y } = Canvas.pxParaMetro(ev.clientX - rect.left, ev.clientY - rect.top);
  M.moverNo(estado.modelo, arrasto.no, x, y);
  redesenhar();
});

svg.addEventListener("mouseup", () => {
  if (arrasto && arrasto.moveu) {
    // Suprime apenas o `click` que dispara no mesmo tick (se disparar); um arrasto
    // real geralmente nao gera click, entao limpamos o flag no proximo tick para
    // nao engolir o proximo clique de verdade.
    estado.suprimirClick = true;
    setTimeout(() => { estado.suprimirClick = false; }, 0);
  }
  arrasto = null;
});

function apagar(no, barra) {
  if (barra) {
    estado.modelo.elementos = estado.modelo.elementos.filter((e) => e !== barra);
    estado.modelo.cargas = estado.modelo.cargas.filter((c) => c.elemento !== barra.id);
  } else if (no) {
    estado.modelo.elementos = estado.modelo.elementos.filter((e) => e.no_i !== no.id && e.no_j !== no.id);
    estado.modelo.vinculos = estado.modelo.vinculos.filter((v) => v.no !== no.id);
    estado.modelo.cargas = estado.modelo.cargas.filter((c) => c.no !== no.id);
    estado.modelo.nos = estado.modelo.nos.filter((n) => n !== no);
  }
}

const cbs = {
  aoMudarModo: (modo) => { estado.modo = modo; estado.primeiroNo = null; redesenhar(); },
  aoEditarMaterial: (patch) => { invalidarResultado(); Object.assign(estado.modelo.material, patch); redesenhar(); },
  aoEditarElemento: (patch) => {
    if (!estado.selecionado) return;
    invalidarResultado();
    if (patch.secao) Object.assign(estado.selecionado.secao, patch.secao);
    if (patch.tipo) estado.selecionado.tipo = patch.tipo;
    redesenhar();
  },
  aoEditarNo: (patch) => {
    if (!estado.selecionado || estado.selecionado.x === undefined) return;
    invalidarResultado();
    M.moverNo(estado.modelo, estado.selecionado,
      patch.x !== undefined ? patch.x : estado.selecionado.x,
      patch.y !== undefined ? patch.y : estado.selecionado.y);
    redesenhar();
  },
  aoSetVinculo: ({ ux, uy, rz }) => {
    if (!estado.selecionado || estado.selecionado.x === undefined) return;
    invalidarResultado();
    M.setVinculo(estado.modelo, estado.selecionado.id, { ux, uy, rz });
    redesenhar();
  },
  aoSetCargaNodal: ({ fx, fy, mz }) => {
    if (!estado.selecionado || estado.selecionado.x === undefined) return;
    invalidarResultado();
    M.setCargaNodal(estado.modelo, estado.selecionado.id, { fx, fy, mz });
    redesenhar();
  },
  aoSetCargaDistribuida: (valor) => {
    if (!estado.selecionado || !estado.selecionado.secao) return;
    invalidarResultado();
    M.setCargaDistribuida(estado.modelo, estado.selecionado.id, valor);
    redesenhar();
  },
  aoExportar: () => {
    const blob = new Blob([JSON.stringify(M.toJson(estado.modelo), null, 2)],
      { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "estrutura.json"; a.click();
    URL.revokeObjectURL(a.href);
  },
  aoImportar: (file) => {
    if (!file) return;
    const r = new FileReader();
    r.onload = () => {
      try {
        estado.modelo = M.fromJson(JSON.parse(r.result));
        estado.selecionado = null; invalidarResultado(); redesenhar();
      } catch (_) { UI.mostrarBanner(banner, "Arquivo inválido."); }
    };
    r.readAsText(file);
  },
  aoCalcular: async () => {
    const erros = M.validar(estado.modelo);
    if (erros.length) { UI.mostrarBanner(banner, erros); return; }
    try {
      const resp = await fetch("/api/estrutura", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(M.toJson(estado.modelo)),
      });
      const data = await resp.json();
      if (!resp.ok) { UI.mostrarBanner(banner, data.error || "Erro na análise."); return; }
      estado.resultado = data.resultado;
      estado.relatorioId = data.id;
      redesenhar();
    } catch (e) { UI.mostrarBanner(banner, "Falha de rede: " + e.message); }
  },
  aoAbrirRelatorio: () => {
    if (estado.relatorioId) window.open("/api/relatorio/" + estado.relatorioId, "_blank");
  },
};

UI.ligarToolbar(document.getElementById("toolbar"), cbs);
redesenhar();
