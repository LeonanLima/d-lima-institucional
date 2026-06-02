import * as M from "./editor-modelo.js";
import * as Canvas from "./editor-canvas.js";
import * as UI from "./editor-ui.js";

const CHAVE_AUTOSAVE = "dlima.editor.estrutura";

const svg = document.getElementById("canvas");
const painel = document.getElementById("painel");
const banner = document.getElementById("banner");

const estado = { modelo: carregarAutosave(), modo: "selecionar",
                 selecionado: null, primeiroNo: null };

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
  UI.renderPainel(painel, estado.modelo, estado.selecionado, cbs);
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
  } else if (estado.modo === "vinculo" && noClicado) {
    const nome = prompt("Vínculo (engaste / fixo / movel):", "fixo");
    if (M.PRESETS_VINCULO[nome]) M.setVinculo(estado.modelo, noClicado.id, M.PRESETS_VINCULO[nome]);
  } else if (estado.modo === "carga") {
    if (barraClicada) {
      const v = parseFloat(prompt("Carga distribuída (kN/m, + para baixo):", "10"));
      if (!Number.isNaN(v)) M.addCargaDistribuida(estado.modelo, barraClicada.id, v);
    } else if (noClicado) {
      const fy = parseFloat(prompt("Força vertical Fy (kN, - para baixo):", "-10"));
      if (!Number.isNaN(fy)) M.addCargaNodal(estado.modelo, noClicado.id, { fy });
    }
  } else if (estado.modo === "apagar") {
    apagar(noClicado, barraClicada);
  } else if (estado.modo === "selecionar") {
    estado.selecionado = barraClicada || null;
  }
  redesenhar();
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
  aoEditarMaterial: (patch) => { Object.assign(estado.modelo.material, patch); autosave(); },
  aoEditarElemento: (patch) => {
    if (!estado.selecionado) return;
    if (patch.secao) Object.assign(estado.selecionado.secao, patch.secao);
    if (patch.tipo) estado.selecionado.tipo = patch.tipo;
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
        estado.selecionado = null; redesenhar();
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
      window.open("/api/relatorio/" + data.id, "_blank");
    } catch (e) { UI.mostrarBanner(banner, "Falha de rede: " + e.message); }
  },
};

UI.ligarToolbar(document.getElementById("toolbar"), cbs);
redesenhar();
