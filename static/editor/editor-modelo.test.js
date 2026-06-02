import { test } from "node:test";
import assert from "node:assert/strict";
import {
  criarModelo, snap, addNo, addBarra, setVinculo,
  addCargaDistribuida, addCargaNodal, PRESETS_VINCULO,
} from "./editor-modelo.js";

test("snap arredonda para o passo de 0,25 m", () => {
  assert.equal(snap(1.13), 1.25);
  assert.equal(snap(2.0), 2.0);
});

test("addNo aplica snap e gera ids sequenciais", () => {
  const m = criarModelo();
  const a = addNo(m, 0.02, -0.04);
  const b = addNo(m, 3.13, 0.0);
  assert.equal(a.id, 1);
  assert.equal(b.id, 2);
  assert.equal(a.x, 0);
  assert.equal(b.x, 3.25);
});

test("addBarra liga dois nós e nomeia B1, B2", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addNo(m, 5, 0);
  const b = addBarra(m, 1, 2);
  assert.equal(b.id, "B1");
  assert.deepEqual(b.secao, { bw: 14, h: 40 });
});

test("setVinculo aplica preset e atualiza no lugar", () => {
  const m = criarModelo();
  addNo(m, 0, 0);
  setVinculo(m, 1, PRESETS_VINCULO.fixo);
  assert.deepEqual(m.vinculos[0], { no: 1, ux: true, uy: true, rz: false });
  setVinculo(m, 1, PRESETS_VINCULO.engaste);
  assert.equal(m.vinculos.length, 1);
  assert.equal(m.vinculos[0].rz, true);
});

test("cargas distribuida e nodal entram na lista", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addNo(m, 5, 0); addBarra(m, 1, 2);
  addCargaDistribuida(m, "B1", 10);
  addCargaNodal(m, 2, { fy: -8 });
  assert.equal(m.cargas[0].tipo, "distribuida");
  assert.equal(m.cargas[0].valor, 10);
  assert.equal(m.cargas[1].fy, -8);
});
