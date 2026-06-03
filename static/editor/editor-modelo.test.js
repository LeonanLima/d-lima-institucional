import { test } from "node:test";
import assert from "node:assert/strict";
import {
  criarModelo, snap, addNo, addBarra, setVinculo,
  addCargaDistribuida, addCargaNodal, PRESETS_VINCULO, toJson, validar, fromJson,
  moverNo, setCargaNodal, setCargaDistribuida,
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

test("fromJson reconstroi o modelo e toJson e idempotente", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addNo(m, 5, 0); addBarra(m, 1, 2);
  setVinculo(m, 1, PRESETS_VINCULO.fixo);
  setVinculo(m, 2, PRESETS_VINCULO.movel);
  addCargaDistribuida(m, "B1", 10);
  const j1 = toJson(m);

  const m2 = fromJson(j1);
  const j2 = toJson(m2);
  assert.deepEqual(j2, j1);
});

test("fromJson continua a sequencia de ids", () => {
  const m2 = fromJson({ estrutura: {
    material: { fck: 25, fyk: 500, CAA: 2, agregado: "basalto" },
    nos: [{ id: 1, x: 0, y: 0 }, { id: 2, x: 5, y: 0 }],
    elementos: [{ id: "B1", tipo: "viga", no_i: 1, no_j: 2, secao: { bw: 14, h: 40 } }],
    vinculos: [], cargas: [],
  }});
  const novo = addNo(m2, 8, 0);
  const novaBarra = addBarra(m2, 2, 3);
  assert.equal(novo.id, 3);
  assert.equal(novaBarra.id, "B2");
});

test("moverNo reposiciona o no existente com snap (nao cria novo)", () => {
  const m = criarModelo();
  const a = addNo(m, 0, 0);
  const r = moverNo(m, a, 3.13, 2.02);
  assert.equal(r, a);
  assert.equal(a.x, 3.25);
  assert.equal(a.y, 2.0);
  assert.equal(m.nos.length, 1);
});

test("setVinculo com todos GDL falsos remove o vinculo", () => {
  const m = criarModelo();
  addNo(m, 0, 0);
  setVinculo(m, 1, PRESETS_VINCULO.fixo);
  assert.equal(m.vinculos.length, 1);
  const r = setVinculo(m, 1, { ux: false, uy: false, rz: false });
  assert.equal(r, null);
  assert.equal(m.vinculos.length, 0);
});

test("setVinculo com GDL parcial faz upsert", () => {
  const m = criarModelo();
  addNo(m, 0, 0);
  setVinculo(m, 1, { ux: true, uy: false, rz: false });
  assert.equal(m.vinculos.length, 1);
  assert.deepEqual(m.vinculos[0], { no: 1, ux: true, uy: false, rz: false });
});

test("setCargaNodal mantem uma carga por no e atualiza no lugar", () => {
  const m = criarModelo();
  addNo(m, 0, 0);
  setCargaNodal(m, 1, { fy: -10 });
  setCargaNodal(m, 1, { fx: 5, fy: -8, mz: 2 });
  const nodais = m.cargas.filter((c) => c.tipo === "nodal" && c.no === 1);
  assert.equal(nodais.length, 1);
  assert.deepEqual(nodais[0], { tipo: "nodal", no: 1, fx: 5, fy: -8, mz: 2 });
});

test("setCargaNodal remove a carga quando tudo zero", () => {
  const m = criarModelo();
  addNo(m, 0, 0);
  setCargaNodal(m, 1, { fy: -10 });
  const r = setCargaNodal(m, 1, { fx: 0, fy: 0, mz: 0 });
  assert.equal(r, null);
  assert.equal(m.cargas.filter((c) => c.tipo === "nodal").length, 0);
});

test("setCargaDistribuida upsert por barra e remove quando vazio/zero", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addNo(m, 5, 0); addBarra(m, 1, 2);
  setCargaDistribuida(m, "B1", 10);
  setCargaDistribuida(m, "B1", 14);
  const ds = m.cargas.filter((c) => c.tipo === "distribuida" && c.elemento === "B1");
  assert.equal(ds.length, 1);
  assert.equal(ds[0].valor, 14);
  assert.equal(setCargaDistribuida(m, "B1", null), null);
  assert.equal(m.cargas.filter((c) => c.tipo === "distribuida").length, 0);
});
