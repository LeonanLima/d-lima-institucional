import { test } from "node:test";
import assert from "node:assert/strict";
import {
  criarModelo, snap, addNo, addBarra, setVinculo,
  addCargaDistribuida, addCargaNodal, PRESETS_VINCULO, toJson, validar,
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

test("toJson produz o schema do motor para viga biapoiada", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addNo(m, 5, 0);
  addBarra(m, 1, 2, { bw: 14, h: 40 });
  setVinculo(m, 1, PRESETS_VINCULO.fixo);
  setVinculo(m, 2, PRESETS_VINCULO.movel);
  addCargaDistribuida(m, "B1", 10);

  const j = toJson(m);
  assert.ok(j.estrutura, "embrulha em estrutura");
  assert.equal(j.estrutura.nos.length, 2);
  assert.equal(j.estrutura.nos[1].x, 5);
  assert.deepEqual(j.estrutura.elementos[0].secao, { bw: 14, h: 40 });
  assert.equal(j.estrutura.elementos[0].no_i, 1);
  assert.equal(j.estrutura.vinculos[0].uy, true);
  assert.equal(j.estrutura.cargas[0].valor, 10);
  assert.equal(j.estrutura.material.fck, 25);
  assert.equal(j.estrutura.nos[0]._seqNo, undefined);
});

test("validar aceita viga biapoiada completa", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addNo(m, 5, 0); addBarra(m, 1, 2);
  setVinculo(m, 1, PRESETS_VINCULO.fixo);
  assert.deepEqual(validar(m), []);
});

test("validar acusa ausencia de vinculo e de barra", () => {
  const m = criarModelo();
  const erros = validar(m);
  assert.ok(erros.some((e) => /vínculo/.test(e)));
  assert.ok(erros.some((e) => /barra/.test(e)));
});

test("validar acusa barra com no inexistente", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addBarra(m, 1, 99);
  setVinculo(m, 1, PRESETS_VINCULO.fixo);
  assert.ok(validar(m).some((e) => /B1/.test(e)));
});

test("validar acusa secao invalida", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addNo(m, 5, 0); addBarra(m, 1, 2, { bw: 0, h: 40 });
  setVinculo(m, 1, PRESETS_VINCULO.fixo);
  assert.ok(validar(m).some((e) => /seção/.test(e)));
});
