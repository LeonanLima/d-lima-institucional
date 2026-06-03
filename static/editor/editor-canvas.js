import { snap } from "./editor-modelo.js";
import { formatarReacoes } from "./editor-resultados.js";

const SVG_NS = "http://www.w3.org/2000/svg";
export const ESCALA = 40;            // px por metro
export const ORIGEM = { x: 70, y: 380 };  // px de (0,0); y cresce para cima

export function metroParaPx(x, y) {
  return { px: ORIGEM.x + x * ESCALA, py: ORIGEM.y - y * ESCALA };
}
export function pxParaMetro(px, py) {
  return { x: snap((px - ORIGEM.x) / ESCALA), y: snap((ORIGEM.y - py) / ESCALA) };
}

function el(tag, attrs) {
  const e = document.createElementNS(SVG_NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  return e;
}

function noPorId(m, id) { return m.nos.find((n) => n.id === id); }

export function render(svg, m, estado) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  const w = svg.clientWidth || 800, h = svg.clientHeight || 500;
  // malha
  for (let gx = ORIGEM.x % ESCALA; gx < w; gx += ESCALA)
    svg.appendChild(el("line", { x1: gx, y1: 0, x2: gx, y2: h, stroke: "#eef2f7" }));
  for (let gy = ORIGEM.y % ESCALA; gy < h; gy += ESCALA)
    svg.appendChild(el("line", { x1: 0, y1: gy, x2: w, y2: gy, stroke: "#eef2f7" }));
  // eixos
  svg.appendChild(el("line", { x1: 0, y1: ORIGEM.y, x2: w, y2: ORIGEM.y, stroke: "#cbd5e1" }));
  svg.appendChild(el("line", { x1: ORIGEM.x, y1: 0, x2: ORIGEM.x, y2: h, stroke: "#cbd5e1" }));

  for (const e of m.elementos) {
    const a = metroParaPx(noPorId(m, e.no_i).x, noPorId(m, e.no_i).y);
    const b = metroParaPx(noPorId(m, e.no_j).x, noPorId(m, e.no_j).y);
    const cor = estado.selecionado === e ? "#dc2626" : "#2563eb";
    svg.appendChild(el("line", { x1: a.px, y1: a.py, x2: b.px, y2: b.py,
      stroke: cor, "stroke-width": 4, "data-barra": e.id }));
  }
  for (const c of m.cargas) desenharCarga(svg, m, c);
  for (const v of m.vinculos) desenharVinculo(svg, m, v);
  for (const n of m.nos) {
    const p = metroParaPx(n.x, n.y);
    const sel = estado.selecionado === n;
    svg.appendChild(el("circle", { cx: p.px, cy: p.py, r: sel ? 8 : 6,
      fill: sel ? "#dc2626" : "#1e293b", "data-no": n.id }));
  }
  if (estado.resultado) desenharResultados(svg, m, estado.resultado);
}

export function desenharResultados(svg, m, resultado) {
  if (!resultado || !resultado.reacoes) return;
  for (const r of formatarReacoes(resultado.reacoes)) {
    if (!r.label) continue;
    const n = noPorId(m, r.no);
    if (!n) continue;
    const p = metroParaPx(n.x, n.y);
    const t = el("text", { x: p.px + 10, y: p.py + 26,
      fill: "#15803d", "font-size": 12, "font-weight": "bold" });
    t.textContent = r.label;
    svg.appendChild(t);
  }
}

function desenharVinculo(svg, m, v) {
  const n = noPorId(m, v.no); if (!n) return;
  const p = metroParaPx(n.x, n.y);
  if (v.ux && v.uy && v.rz) {  // engaste: base hachurada
    svg.appendChild(el("rect", { x: p.px - 12, y: p.py + 6, width: 24, height: 6,
      fill: "#64748b" }));
  } else if (v.ux && v.uy) {   // apoio fixo: triangulo
    svg.appendChild(el("polygon", { points: `${p.px},${p.py} ${p.px-9},${p.py+14} ${p.px+9},${p.py+14}`,
      fill: "#64748b" }));
  } else {                      // movel: triangulo + base
    svg.appendChild(el("polygon", { points: `${p.px},${p.py} ${p.px-9},${p.py+14} ${p.px+9},${p.py+14}`,
      fill: "#94a3b8" }));
    svg.appendChild(el("line", { x1: p.px-11, y1: p.py+17, x2: p.px+11, y2: p.py+17, stroke: "#94a3b8" }));
  }
}

function desenharCarga(svg, m, c) {
  if (c.tipo === "distribuida") {
    const e = m.elementos.find((x) => x.id === c.elemento); if (!e) return;
    const a = metroParaPx(noPorId(m, e.no_i).x, noPorId(m, e.no_i).y);
    const b = metroParaPx(noPorId(m, e.no_j).x, noPorId(m, e.no_j).y);
    for (let t = 0; t <= 1.0001; t += 0.2) {
      const x = a.px + (b.px - a.px) * t, y = a.py + (b.py - a.py) * t;
      svg.appendChild(el("line", { x1: x, y1: y - 18, x2: x, y2: y - 3, stroke: "#ef4444" }));
      svg.appendChild(el("polygon", { points: `${x},${y} ${x-3},${y-5} ${x+3},${y-5}`, fill: "#ef4444" }));
    }
  } else if (c.tipo === "nodal") {
    const n = noPorId(m, c.no); if (!n) return;
    const p = metroParaPx(n.x, n.y);
    if (c.fy) svg.appendChild(el("line", { x1: p.px, y1: p.py - 28, x2: p.px, y2: p.py - 4,
      stroke: "#b91c1c", "stroke-width": 2 }));
    if (c.fx) svg.appendChild(el("line", { x1: p.px - 28, y1: p.py, x2: p.px - 4, y2: p.py,
      stroke: "#b91c1c", "stroke-width": 2 }));
  }
}
