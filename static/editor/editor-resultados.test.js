import { test } from "node:test";
import assert from "node:assert/strict";
import {
  formatarNumero, formatarReacoes, deslocamentoMaximo, resumoResultado,
} from "./editor-resultados.js";

test("formatarNumero usa virgula e 1 casa por padrao", () => {
  assert.equal(formatarNumero(25), "25,0");
  assert.equal(formatarNumero(3.14159, 2), "3,14");
});

test("formatarReacoes ordena por no e ignora componentes despreziveis", () => {
  const r = formatarReacoes({ "2": { fx: 0, fy: 25, mz: 0 }, "1": { fx: 0, fy: 25, mz: 0 } });
  assert.equal(r.length, 2);
  assert.equal(r[0].no, 1);
  assert.equal(r[0].texto, "Fy 25,0 kN");
  assert.equal(r[0].label, "↑ 25,0 kN");
});

test("formatarReacoes: seta para baixo em Fy negativo; ≈0 sem componentes", () => {
  const r = formatarReacoes({ "1": { fx: 0, fy: -8, mz: 0 }, "2": { fx: 0, fy: 0, mz: 0 } });
  assert.equal(r[0].label, "↓ 8,0 kN");
  assert.equal(r[1].texto, "≈ 0");
  assert.equal(r[1].label, "");
});

test("deslocamentoMaximo retorna o no de maior translacao em mm", () => {
  const d = deslocamentoMaximo({ "1": { ux: 0, uy: 0, rz: 0 }, "2": { ux: 3, uy: 4, rz: 0.01 } });
  assert.equal(d.no, 2);
  assert.equal(d.mm, 5);
  assert.equal(d.texto, "Nó 2: 5,00 mm");
});

test("deslocamentoMaximo retorna null sem deslocamentos", () => {
  assert.equal(deslocamentoMaximo({}), null);
});

test("resumoResultado agrega reacoes, desloc e avisos", () => {
  const s = resumoResultado({
    reacoes: { "1": { fx: 0, fy: 25, mz: 0 } },
    deslocamentos: { "1": { ux: 0, uy: 2, rz: 0 } },
    avisos: ["x"],
  });
  assert.equal(s.reacoes.length, 1);
  assert.equal(s.deslocamentoMax.no, 1);
  assert.deepEqual(s.avisos, ["x"]);
});
