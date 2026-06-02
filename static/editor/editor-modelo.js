export const PASSO_SNAP = 0.25;  // metros

export function snap(v, passo = PASSO_SNAP) {
  return Math.round(v / passo) * passo;
}

export function criarModelo() {
  return {
    material: { fck: 25, fyk: 500, CAA: 2, agregado: "basalto" },
    nos: [], elementos: [], vinculos: [], cargas: [],
    _seqNo: 0, _seqEl: 0,
  };
}

export function addNo(m, x, y) {
  const no = { id: ++m._seqNo, x: snap(x), y: snap(y) };
  m.nos.push(no);
  return no;
}

export function addBarra(m, noI, noJ, secao = { bw: 14, h: 40 }, tipo = "viga") {
  const el = { id: "B" + (++m._seqEl), tipo, no_i: noI, no_j: noJ,
               secao: { bw: secao.bw, h: secao.h } };
  m.elementos.push(el);
  return el;
}

export const PRESETS_VINCULO = {
  engaste: { ux: true, uy: true, rz: true },
  fixo:    { ux: true, uy: true, rz: false },
  movel:   { ux: false, uy: true, rz: false },
};

export function setVinculo(m, no, { ux = false, uy = false, rz = false }) {
  let v = m.vinculos.find((x) => x.no === no);
  if (v) { v.ux = ux; v.uy = uy; v.rz = rz; return v; }
  v = { no, ux, uy, rz };
  m.vinculos.push(v);
  return v;
}

export function addCargaDistribuida(m, elementoId, valor, direcao = "y") {
  const c = { tipo: "distribuida", elemento: elementoId, valor, direcao };
  m.cargas.push(c);
  return c;
}

export function addCargaNodal(m, no, { fx = 0, fy = 0, mz = 0 }) {
  const c = { tipo: "nodal", no, fx, fy, mz };
  m.cargas.push(c);
  return c;
}

export function toJson(m) {
  return {
    estrutura: {
      material: { fck: m.material.fck, fyk: m.material.fyk,
                  CAA: m.material.CAA, agregado: m.material.agregado },
      nos: m.nos.map((n) => ({ id: n.id, x: n.x, y: n.y })),
      elementos: m.elementos.map((e) => ({
        id: e.id, tipo: e.tipo, no_i: e.no_i, no_j: e.no_j,
        secao: { bw: e.secao.bw, h: e.secao.h },
      })),
      vinculos: m.vinculos.map((v) => ({ no: v.no, ux: v.ux, uy: v.uy, rz: v.rz })),
      cargas: m.cargas.map((c) => ({ ...c })),
    },
  };
}
