# Editor de Estrutura (Fase 2) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** UI gráfica (canvas SVG com malha + snap) para desenhar pórticos planos, gerar o JSON do motor da Fase 1 e abrir o relatório de análise.

**Architecture:** Página Flask nova (`GET /estrutura/editor`) no blueprint `estrutura_bp`. Frontend em ES modules vanilla sob `static/editor/`: `editor-modelo.js` (estado puro, testável em Node), `editor-canvas.js` (render SVG + coordenadas), `editor-ui.js` (toolbar/painel), `editor.js` (controlador: eventos, autosave, POST). Sem framework, sem banco.

**Tech Stack:** Python 3 / Flask 3, Jinja2, SVG + JavaScript ES modules, `node --test` (lógica pura), pytest (rota). `package.json` com `"type":"module"`.

**Convenção de unidades:** o editor trabalha em **metros** (x,y dos nós) e **kN / kN·m / kN/m** (cargas); seção em **cm**. Envia exatamente o schema de `Estrutura.from_json` — a conversão para cm/kN internos é feita pelo motor, o editor NÃO converte.

---

## File Map

| Arquivo | Responsabilidade |
|---|---|
| `package.json` | `"type":"module"` + script `test: node --test` |
| `engine/rotas.py` | + rota `GET /estrutura/editor` |
| `templates/editor.html` | Layout: toolbar + `<svg>` + painel; imports dos módulos |
| `static/editor/editor-modelo.js` | Estado puro: criar/add nós/barras/vínculos/cargas, `snap`, `toJson`, `validar`, `fromJson` |
| `static/editor/editor-modelo.test.js` | Testes `node --test` da lógica pura |
| `static/editor/editor-canvas.js` | Render SVG (malha/nós/barras/vínculos/cargas) + transformações de coordenada |
| `static/editor/editor-ui.js` | Toolbar/modos, painel de propriedades, material global, banners |
| `static/editor/editor.js` | Controlador: estado de UI, eventos do canvas, autosave, export/import, Calcular (POST) |
| `tests/test_editor_rota.py` | pytest da rota do editor |

---

### Task 1: Setup — package.json, rota do editor e esqueleto do template

**Files:**
- Create: `package.json`
- Create: `tests/test_editor_rota.py`
- Modify: `engine/rotas.py`
- Create: `templates/editor.html`

- [ ] **Step 1: Criar `package.json` na raiz**

```json
{
  "name": "dlima-editor-estrutura",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test static/editor/"
  }
}
```

- [ ] **Step 2: Escrever teste falho `tests/test_editor_rota.py`**

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_editor_rota_responde_200(client):
    r = client.get('/estrutura/editor')
    assert r.status_code == 200


def test_editor_tem_canvas_e_modulos(client):
    r = client.get('/estrutura/editor')
    html = r.data.decode('utf-8')
    assert 'id="canvas"' in html              # container do canvas
    assert 'editor/editor.js' in html         # import do controlador
    assert 'type="module"' in html            # ES modules
```

- [ ] **Step 3: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_editor_rota.py -v`
Esperado: FAIL — 404 (rota inexistente) em `test_editor_rota_responde_200`.

- [ ] **Step 4: Adicionar a rota em `engine/rotas.py`**

Adicionar logo após a linha `estrutura_bp = Blueprint("estrutura", __name__)`:

```python
@estrutura_bp.route("/estrutura/editor")
def editor():
    return render_template("editor.html")
```

- [ ] **Step 5: Criar `templates/editor.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>D'LIMA — Editor de Estrutura</title>
  <style>
    body{font-family:Arial,sans-serif;margin:0;color:#1e293b;background:#f4f4f9}
    header{background:#0056b3;color:#fff;padding:12px 18px;font-weight:bold}
    .app{display:flex;height:calc(100vh - 46px)}
    .toolbar{display:flex;flex-direction:column;gap:6px;padding:10px;background:#fff;border-right:1px solid #e2e8f0}
    .toolbar button{padding:8px 10px;border:1px solid #cbd5e1;background:#fff;border-radius:6px;cursor:pointer;font-size:13px}
    .toolbar button.ativo{background:#0056b3;color:#fff;border-color:#0056b3}
    .canvas-wrap{flex:1;position:relative;overflow:hidden}
    #canvas{width:100%;height:100%;background:#fff}
    .painel{width:260px;padding:12px;background:#fff;border-left:1px solid #e2e8f0;overflow:auto;font-size:13px}
    .painel h3{margin:6px 0;color:#0056b3}
    .painel label{display:block;margin:6px 0 2px}
    .painel input,.painel select{width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:4px;box-sizing:border-box}
    .banner{position:absolute;top:10px;left:50%;transform:translateX(-50%);background:#fef2f2;color:#991b1b;border:1px solid #fecaca;padding:8px 14px;border-radius:6px;display:none;max-width:80%}
    .row{display:flex;gap:6px}.row>*{flex:1}
    button.primary{background:#16a34a;color:#fff;border:none;padding:9px;border-radius:6px;cursor:pointer;width:100%;margin-top:8px}
  </style>
</head>
<body>
  <header>🏗 D'LIMA — Editor de Estrutura</header>
  <div class="app">
    <div class="toolbar" id="toolbar">
      <button data-modo="selecionar" class="ativo">▖ Selecionar</button>
      <button data-modo="no">● Nó</button>
      <button data-modo="barra">／ Barra</button>
      <button data-modo="vinculo">▲ Vínculo</button>
      <button data-modo="carga">↓ Carga</button>
      <button data-modo="apagar">✕ Apagar</button>
    </div>
    <div class="canvas-wrap">
      <svg id="canvas"></svg>
      <div class="banner" id="banner"></div>
    </div>
    <div class="painel" id="painel"></div>
  </div>
  <script type="module" src="/static/editor/editor.js"></script>
</body>
</html>
```

- [ ] **Step 6: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_editor_rota.py -v`
Esperado: 2 PASSED.

- [ ] **Step 7: Commit**

```bash
git add package.json tests/test_editor_rota.py engine/rotas.py templates/editor.html
git commit -m "feat: rota e esqueleto do editor de estrutura"
```

---

### Task 2: editor-modelo — estado, snap e adições

**Files:**
- Create: `static/editor/editor-modelo.js`
- Create: `static/editor/editor-modelo.test.js`

- [ ] **Step 1: Escrever teste falho `static/editor/editor-modelo.test.js`**

```javascript
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
```

- [ ] **Step 2: Rodar teste — verificar FAIL**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: FAIL — `Cannot find module './editor-modelo.js'`.

- [ ] **Step 3: Implementar `static/editor/editor-modelo.js` (parte 1)**

```javascript
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
```

- [ ] **Step 4: Rodar teste — verificar PASS**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: 5 PASSED.

- [ ] **Step 5: Commit**

```bash
git add static/editor/editor-modelo.js static/editor/editor-modelo.test.js
git commit -m "feat: editor-modelo — estado, snap e adicoes (node test)"
```

---

### Task 3: editor-modelo — `toJson()` no schema do motor

**Files:**
- Modify: `static/editor/editor-modelo.js`
- Modify: `static/editor/editor-modelo.test.js`

- [ ] **Step 1: Adicionar teste falho em `static/editor/editor-modelo.test.js`**

```javascript
import { toJson } from "./editor-modelo.js";

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
  // sem campos internos
  assert.equal(j.estrutura.nos[0]._seqNo, undefined);
});
```

- [ ] **Step 2: Rodar teste — verificar FAIL**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: FAIL — `toJson is not a function`.

- [ ] **Step 3: Adicionar `toJson` em `static/editor/editor-modelo.js`**

```javascript
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
```

- [ ] **Step 4: Rodar teste — verificar PASS**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: 6 PASSED.

- [ ] **Step 5: Commit**

```bash
git add static/editor/editor-modelo.js static/editor/editor-modelo.test.js
git commit -m "feat: editor-modelo — toJson no schema do motor"
```

---

### Task 4: editor-modelo — `validar()`

**Files:**
- Modify: `static/editor/editor-modelo.js`
- Modify: `static/editor/editor-modelo.test.js`

- [ ] **Step 1: Adicionar teste falho em `static/editor/editor-modelo.test.js`**

```javascript
import { validar } from "./editor-modelo.js";

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
```

- [ ] **Step 2: Rodar teste — verificar FAIL**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: FAIL — `validar is not a function`.

- [ ] **Step 3: Adicionar `validar` em `static/editor/editor-modelo.js`**

```javascript
export function validar(m) {
  const erros = [];
  if (m.vinculos.length === 0) erros.push("Adicione ao menos um vínculo (apoio).");
  if (m.elementos.length === 0) erros.push("Adicione ao menos uma barra.");
  const ids = new Set(m.nos.map((n) => n.id));
  for (const e of m.elementos) {
    if (!ids.has(e.no_i) || !ids.has(e.no_j) || e.no_i === e.no_j) {
      erros.push(`Barra ${e.id}: nós inválidos.`);
    }
    if (!(e.secao.bw > 0) || !(e.secao.h > 0)) {
      erros.push(`Barra ${e.id}: seção inválida (bw e h devem ser > 0).`);
    }
  }
  if (!(m.material.fck > 0) || !(m.material.fyk > 0)) {
    erros.push("Material: fck e fyk devem ser > 0.");
  }
  return erros;
}
```

- [ ] **Step 4: Rodar teste — verificar PASS**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: 10 PASSED.

- [ ] **Step 5: Commit**

```bash
git add static/editor/editor-modelo.js static/editor/editor-modelo.test.js
git commit -m "feat: editor-modelo — validacao local antes do envio"
```

---

### Task 5: editor-modelo — `fromJson()` e round-trip

**Files:**
- Modify: `static/editor/editor-modelo.js`
- Modify: `static/editor/editor-modelo.test.js`

- [ ] **Step 1: Adicionar teste falho em `static/editor/editor-modelo.test.js`**

```javascript
import { fromJson } from "./editor-modelo.js";

test("fromJson reconstroi o modelo e toJson e idempotente", () => {
  const m = criarModelo();
  addNo(m, 0, 0); addNo(m, 5, 0); addBarra(m, 1, 2);
  setVinculo(m, 1, PRESETS_VINCULO.fixo);
  setVinculo(m, 2, PRESETS_VINCULO.movel);
  addCargaDistribuida(m, "B1", 10);
  const j1 = toJson(m);

  const m2 = fromJson(j1);
  const j2 = toJson(m2);
  assert.deepEqual(j2, j1);  // round-trip preserva tudo
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
  assert.equal(novo.id, 3);       // nao colide com 1,2
  assert.equal(novaBarra.id, "B2"); // continua apos B1
});
```

- [ ] **Step 2: Rodar teste — verificar FAIL**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: FAIL — `fromJson is not a function`.

- [ ] **Step 3: Adicionar `fromJson` em `static/editor/editor-modelo.js`**

```javascript
export function fromJson(data) {
  const e = data.estrutura;
  const m = criarModelo();
  m.material = {
    fck: e.material.fck, fyk: e.material.fyk,
    CAA: e.material.CAA, agregado: e.material.agregado,
  };
  for (const n of e.nos) {
    m.nos.push({ id: n.id, x: n.x, y: n.y });
    m._seqNo = Math.max(m._seqNo, n.id);
  }
  for (const el of e.elementos) {
    m.elementos.push({ id: el.id, tipo: el.tipo, no_i: el.no_i, no_j: el.no_j,
                       secao: { bw: el.secao.bw, h: el.secao.h } });
    const num = parseInt(String(el.id).replace(/\D/g, ""), 10);
    if (!Number.isNaN(num)) m._seqEl = Math.max(m._seqEl, num);
  }
  for (const v of e.vinculos || []) {
    m.vinculos.push({ no: v.no, ux: !!v.ux, uy: !!v.uy, rz: !!v.rz });
  }
  for (const c of e.cargas || []) m.cargas.push({ ...c });
  return m;
}
```

- [ ] **Step 4: Rodar teste — verificar PASS**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: 12 PASSED.

- [ ] **Step 5: Commit**

```bash
git add static/editor/editor-modelo.js static/editor/editor-modelo.test.js
git commit -m "feat: editor-modelo — fromJson e round-trip"
```

---

### Task 6: editor-canvas — render SVG e coordenadas

**Files:**
- Create: `static/editor/editor-canvas.js`

> Módulo de render (DOM/SVG) — verificação manual no navegador, sem teste automatizado (o canvas depende do DOM). A lógica numérica testável (`snap`) já está coberta na Task 2.

- [ ] **Step 1: Implementar `static/editor/editor-canvas.js`**

```javascript
import { snap } from "./editor-modelo.js";

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
    svg.appendChild(el("circle", { cx: p.px, cy: p.py, r: 6,
      fill: "#1e293b", "data-no": n.id }));
  }
}

function desenharVinculo(svg, m, v) {
  const n = noPorId(m, v.no); if (!n) return;
  const p = metroParaPx(n.x, n.y);
  if (v.ux && v.uy && v.rz) {  // engaste: hachura
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
      stroke: "#b91c1c", "stroke-width": 2, "marker-end": "url(#seta)" }));
    if (c.fx) svg.appendChild(el("line", { x1: p.px - 28, y1: p.py, x2: p.px - 4, y2: p.py,
      stroke: "#b91c1c", "stroke-width": 2 }));
  }
}
```

- [ ] **Step 2: Verificação manual (rápida)**

A verificação completa ocorre na Task 8 (com o controlador ligado). Aqui só confirme que o arquivo não tem erro de sintaxe:

Run: `node --check static/editor/editor-canvas.js`
Esperado: sem saída (sintaxe OK).

- [ ] **Step 3: Commit**

```bash
git add static/editor/editor-canvas.js
git commit -m "feat: editor-canvas — render SVG de malha, barras, nos, vinculos e cargas"
```

---

### Task 7: editor-ui — toolbar, painel de propriedades e material

**Files:**
- Create: `static/editor/editor-ui.js`

> Módulo de UI (DOM) — verificação manual. Recebe callbacks do controlador; não conhece o canvas.

- [ ] **Step 1: Implementar `static/editor/editor-ui.js`**

```javascript
// Liga a toolbar e renderiza o painel de propriedades.
// `cbs` = { aoMudarModo, aoEditarElemento, aoEditarMaterial,
//           aoSetVinculo, aoExportar, aoImportar, aoCalcular }

export function ligarToolbar(toolbarEl, cbs) {
  toolbarEl.querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", () => {
      toolbarEl.querySelectorAll("button").forEach((x) => x.classList.remove("ativo"));
      b.classList.add("ativo");
      cbs.aoMudarModo(b.dataset.modo);
    });
  });
}

export function mostrarBanner(bannerEl, msgs) {
  if (!msgs || msgs.length === 0) { bannerEl.style.display = "none"; return; }
  bannerEl.innerHTML = Array.isArray(msgs) ? msgs.join("<br>") : msgs;
  bannerEl.style.display = "block";
  clearTimeout(bannerEl._t);
  bannerEl._t = setTimeout(() => { bannerEl.style.display = "none"; }, 6000);
}

export function renderPainel(painelEl, m, selecionado, cbs) {
  const mat = m.material;
  let html = `<h3>Material</h3>
    <label>fck (MPa)</label><input id="p-fck" type="number" value="${mat.fck}">
    <label>fyk (MPa)</label><input id="p-fyk" type="number" value="${mat.fyk}">
    <label>CAA</label><select id="p-caa">${[1,2,3,4].map((c)=>`<option ${c===mat.CAA?"selected":""}>${c}</option>`).join("")}</select>
    <label>Agregado</label>
    <select id="p-agr">${["basalto","granito","gnaisse","calcario","arenito"].map((a)=>`<option ${a===mat.agregado?"selected":""}>${a}</option>`).join("")}</select>`;

  if (selecionado && selecionado.secao) {
    html += `<h3>Barra ${selecionado.id}</h3>
      <label>Tipo</label>
      <select id="p-tipo">${["viga","pilar","fundacao"].map((t)=>`<option ${t===selecionado.tipo?"selected":""}>${t}</option>`).join("")}</select>
      <div class="row"><div><label>bw (cm)</label><input id="p-bw" type="number" value="${selecionado.secao.bw}"></div>
      <div><label>h (cm)</label><input id="p-h" type="number" value="${selecionado.secao.h}"></div></div>`;
  }

  html += `<h3>Arquivo</h3>
    <div class="row"><button id="p-export">Exportar</button><button id="p-import">Importar</button></div>
    <input id="p-file" type="file" accept="application/json" style="display:none">
    <button class="primary" id="p-calc">Calcular →</button>`;
  painelEl.innerHTML = html;

  const on = (id, ev, fn) => { const e = painelEl.querySelector(id); if (e) e.addEventListener(ev, fn); };
  on("#p-fck", "change", (e) => cbs.aoEditarMaterial({ fck: +e.target.value }));
  on("#p-fyk", "change", (e) => cbs.aoEditarMaterial({ fyk: +e.target.value }));
  on("#p-caa", "change", (e) => cbs.aoEditarMaterial({ CAA: +e.target.value }));
  on("#p-agr", "change", (e) => cbs.aoEditarMaterial({ agregado: e.target.value }));
  on("#p-tipo", "change", (e) => cbs.aoEditarElemento({ tipo: e.target.value }));
  on("#p-bw", "change", (e) => cbs.aoEditarElemento({ secao: { bw: +e.target.value } }));
  on("#p-h", "change", (e) => cbs.aoEditarElemento({ secao: { h: +e.target.value } }));
  on("#p-export", "click", () => cbs.aoExportar());
  on("#p-import", "click", () => painelEl.querySelector("#p-file").click());
  on("#p-file", "change", (e) => cbs.aoImportar(e.target.files[0]));
  on("#p-calc", "click", () => cbs.aoCalcular());
}
```

- [ ] **Step 2: Verificação de sintaxe**

Run: `node --check static/editor/editor-ui.js`
Esperado: sem saída (sintaxe OK).

- [ ] **Step 3: Commit**

```bash
git add static/editor/editor-ui.js
git commit -m "feat: editor-ui — toolbar, painel de propriedades, material e banner"
```

---

### Task 8: editor.js — controlador (eventos, autosave, export/import, Calcular)

**Files:**
- Create: `static/editor/editor.js`

> Controlador que liga modelo + canvas + ui e trata eventos do canvas. Verificação manual no navegador.

- [ ] **Step 1: Implementar `static/editor/editor.js`**

```javascript
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
```

- [ ] **Step 2: Verificação de sintaxe**

Run: `node --check static/editor/editor.js`
Esperado: sem saída (sintaxe OK).

- [ ] **Step 3: Commit**

```bash
git add static/editor/editor.js
git commit -m "feat: editor.js — controlador, eventos do canvas, autosave e Calcular"
```

---

### Task 9: Verificação manual end-to-end e fechamento

**Files:** nenhum novo (validação integrada).

- [ ] **Step 1: Rodar a suíte completa (Python + Node)**

Run: `.venv/Scripts/python -m pytest tests/ -q`
Esperado: todos passando (motor 63 + rota editor 2 = 65).

Run: `node --test static/editor/`
Esperado: 12 PASSED.

- [ ] **Step 2: Subir o app e testar no navegador**

Run: `.venv/Scripts/python app.py`
Abrir `http://localhost:10000/estrutura/editor` e seguir o checklist:
- [ ] Modo Nó: clicar duas vezes cria 2 nós alinhados (snap visível na malha).
- [ ] Modo Barra: clicar nó 1 → nó 2 cria a barra azul.
- [ ] Modo Vínculo: clicar nó 1 → "fixo" (triângulo); nó 2 → "movel" (triângulo + base).
- [ ] Modo Carga: clicar na barra → "10" desenha setas distribuídas.
- [ ] Painel: definir bw=14, h=40 na barra selecionada; material fck=25.
- [ ] Botão "Calcular →": abre nova aba com o relatório; reações ≈ 25 kN por apoio.
- [ ] Exportar baixa `estrutura.json`; recarregar a página mantém o desenho (autosave); Importar recria.
- [ ] Validação: apagar o vínculo e Calcular → banner "Adicione ao menos um vínculo".

- [ ] **Step 3: Commit do registro de verificação (se houver ajustes)**

Caso algum passo manual exija correção, corrigir, re-rodar e commitar com mensagem específica. Se tudo passou sem ajustes, nada a commitar neste step.

- [ ] **Step 4: Marcar plano e abrir PR**

```bash
git push -u origin feat/editor-estrutura
```
Abrir PR (base `main` ou sobre o PR #1 do motor, conforme ordem de merge).

---

## Self-Review (cobertura da spec)

| Requisito da spec | Task |
|---|---|
| Rota `GET /estrutura/editor` + template | 1 |
| `package.json` para `node --test` | 1 |
| Estado, snap (0,25 m), add nós/barras/vínculos/cargas | 2 |
| `toJson()` no schema do motor (sem conversão de unidade) | 3 |
| `validar()` (≥1 vínculo, ≥1 barra, nós/seção válidos, material) | 4 |
| `fromJson()` + round-trip (import) | 5 |
| Canvas SVG: malha, nós, barras, vínculos (presets), cargas | 6 |
| Toolbar/modos, painel seção+tipo, material global, banner | 7 |
| Cargas distribuída + nodal (Fx, Fy, Mz) | 6 (render) + 8 (entrada) |
| Vínculos presets + (checkbox 3-GDL via prompt no v1) | 7/8 |
| Autosave localStorage + Export/Import JSON | 8 |
| Calcular → POST `/api/estrutura` → abrir `/api/relatorio/<id>` | 8 |
| Validação bloqueia POST e mostra banner | 8 (usa Task 4) |
| Testes: node --test + pytest rota + checklist manual | 2–5, 1, 9 |
| Critérios de aceite | 9 |

**Nota sobre vínculos 3-GDL:** o v1 usa presets via `prompt` (engaste/fixo/movel) no controlador. Os checkboxes ux/uy/rz dos casos especiais ficam como melhoria de UI rápida pós-v1 — `setVinculo` já aceita qualquer combinação dos 3 GDL (testado na Task 2/4), então a capacidade existe no modelo; só a entrada por checkbox no painel fica para um incremento. Isso mantém o v1 enxuto sem perder a capacidade de fundo.

**Nota sobre cargas Mz:** `addCargaNodal` aceita `mz` (Task 2) e `toJson` o serializa; o v1 expõe Fy via prompt no canvas. Entrada de Fx/Mz por painel é incremento rápido sobre a mesma função.
```
