# Editor — 3-GDL, Cargas Fx/Fy/Mz e Arrastar Nós — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expor vínculos 3-GDL (ux/uy/rz) e cargas nodais Fx/Fy/Mz num painel por seleção, permitir arrastar nós no canvas, e eliminar os `prompt()` e os modos Vínculo/Carga da toolbar.

**Architecture:** Tudo no frontend `static/editor/`. O modelo (`editor-modelo.js`) ganha funções puras de upsert/move (`moverNo`, `setVinculo` com remoção, `setCargaNodal`, `setCargaDistribuida`). O painel (`editor-ui.js`) renderiza propriedades conforme o selecionado seja nó ou barra. O controlador (`editor.js`) trata seleção de nó/barra e uma máquina de arrasto (mousedown/move/up). O canvas (`editor-canvas.js`) destaca o nó selecionado. Sem mudanças no motor/API.

**Tech Stack:** JavaScript ES modules, SVG, `node --test` (lógica pura), pytest (rota intocada), Playwright/`playwright-core` + Chrome (verificação visual).

**Convenção:** metros (x,y), kN/kN·m (cargas), cm (seção). O editor não converte unidade.

**Branch:** `feat/editor-melhorias-no` (já criada, com a spec commitada).

> **CUIDADO (ambiente):** `node_modules` é versionado e está com ~1008 arquivos sujos de uma sessão anterior. **Nunca usar `git add .` nem `git add -A`** — sempre adicionar arquivos por caminho explícito. **Não rodar `npm install`** (faz prune do vendor). Ver memória `project-estruturas-env-gotcha`.

---

## File Map

| Arquivo | Mudança |
|---|---|
| `static/editor/editor-modelo.js` | + `moverNo`, `setCargaNodal`, `setCargaDistribuida`; `setVinculo` passa a remover em all-false |
| `static/editor/editor-modelo.test.js` | + testes das novas funções |
| `templates/editor.html` | toolbar perde os botões Vínculo e Carga |
| `static/editor/editor-canvas.js` | destaque do nó selecionado |
| `static/editor/editor-ui.js` | painel do nó (coords/vínculo/cargas) + campo distribuída na barra + callbacks |
| `static/editor/editor.js` | seleção nó/barra, arrasto, callbacks novos, remove prompts |

---

### Task 1: Modelo — moverNo, setVinculo (remoção), setCargaNodal, setCargaDistribuida

**Files:**
- Modify: `static/editor/editor-modelo.test.js`
- Modify: `static/editor/editor-modelo.js`

- [ ] **Step 1: Adicionar imports e testes falhos em `static/editor/editor-modelo.test.js`**

Adicionar este import junto aos imports existentes do topo (que já trazem `criarModelo, addNo, setVinculo, PRESETS_VINCULO`):

```javascript
import { moverNo, setCargaNodal, setCargaDistribuida } from "./editor-modelo.js";
```

Adicionar ao final do arquivo:

```javascript
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
```

> Nota: `addBarra` já está importado no topo do arquivo de testes (Task 2 da Fase 2).

- [ ] **Step 2: Rodar teste — verificar FAIL**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: FAIL — `moverNo is not a function` (e as demais novas).

- [ ] **Step 3: Substituir `setVinculo` em `static/editor/editor-modelo.js`**

Substituir a função `setVinculo` inteira (atualmente upsert sem remoção) por:

```javascript
export function setVinculo(m, no, { ux = false, uy = false, rz = false }) {
  const i = m.vinculos.findIndex((x) => x.no === no);
  if (!ux && !uy && !rz) {
    if (i >= 0) m.vinculos.splice(i, 1);
    return null;
  }
  if (i >= 0) {
    m.vinculos[i].ux = ux; m.vinculos[i].uy = uy; m.vinculos[i].rz = rz;
    return m.vinculos[i];
  }
  const v = { no, ux, uy, rz };
  m.vinculos.push(v);
  return v;
}
```

- [ ] **Step 4: Adicionar `moverNo`, `setCargaNodal`, `setCargaDistribuida`**

Adicionar logo após `addNo` (para `moverNo`) e junto às funções de carga (as demais). Para simplicidade, adicionar este bloco logo após a função `addCargaNodal` existente:

```javascript
export function moverNo(m, no, x, y) {
  no.x = snap(x);
  no.y = snap(y);
  return no;
}

export function setCargaNodal(m, no, { fx = 0, fy = 0, mz = 0 }) {
  const i = m.cargas.findIndex((c) => c.tipo === "nodal" && c.no === no);
  if (fx === 0 && fy === 0 && mz === 0) {
    if (i >= 0) m.cargas.splice(i, 1);
    return null;
  }
  if (i >= 0) {
    m.cargas[i].fx = fx; m.cargas[i].fy = fy; m.cargas[i].mz = mz;
    return m.cargas[i];
  }
  const c = { tipo: "nodal", no, fx, fy, mz };
  m.cargas.push(c);
  return c;
}

export function setCargaDistribuida(m, elementoId, valor, direcao = "y") {
  const i = m.cargas.findIndex((c) => c.tipo === "distribuida" && c.elemento === elementoId);
  const v = typeof valor === "number" ? valor : NaN;
  if (!Number.isFinite(v) || v === 0) {
    if (i >= 0) m.cargas.splice(i, 1);
    return null;
  }
  if (i >= 0) {
    m.cargas[i].valor = v; m.cargas[i].direcao = direcao;
    return m.cargas[i];
  }
  const c = { tipo: "distribuida", elemento: elementoId, valor: v, direcao };
  m.cargas.push(c);
  return c;
}
```

- [ ] **Step 5: Rodar teste — verificar PASS**

Run: `node --test static/editor/editor-modelo.test.js`
Esperado: PASS em todos (12 antigos + 6 novos = 18).

- [ ] **Step 6: Rodar a suíte Node completa (não quebrou resultados nem modelo)**

Run: `npm test`
Esperado: 24 PASSED (18 modelo + 6 resultados).

- [ ] **Step 7: Commit**

```bash
git add static/editor/editor-modelo.js static/editor/editor-modelo.test.js
git commit -m "feat: editor-modelo — moverNo, setCargaNodal/Distribuida e setVinculo com remocao"
```

---

### Task 2: Toolbar — remover modos Vínculo e Carga

**Files:**
- Modify: `templates/editor.html`

- [ ] **Step 1: Remover os dois botões em `templates/editor.html`**

Substituir o bloco da toolbar:

```html
    <div class="toolbar" id="toolbar">
      <button data-modo="selecionar" class="ativo">▖ Selecionar</button>
      <button data-modo="no">● Nó</button>
      <button data-modo="barra">／ Barra</button>
      <button data-modo="vinculo">▲ Vínculo</button>
      <button data-modo="carga">↓ Carga</button>
      <button data-modo="apagar">✕ Apagar</button>
    </div>
```

por:

```html
    <div class="toolbar" id="toolbar">
      <button data-modo="selecionar" class="ativo">▖ Selecionar</button>
      <button data-modo="no">● Nó</button>
      <button data-modo="barra">／ Barra</button>
      <button data-modo="apagar">✕ Apagar</button>
    </div>
```

- [ ] **Step 2: Confirmar que a rota do editor segue servindo (pytest intocado)**

Run: `.venv/Scripts/python -m pytest tests/test_editor_rota.py -q`
Esperado: 2 passed (o teste checa `id="canvas"`, `editor/editor.js`, `type="module"` — todos preservados).

- [ ] **Step 3: Commit**

```bash
git add templates/editor.html
git commit -m "feat: editor — toolbar sem modos Vinculo/Carga (edicao via painel)"
```

---

### Task 3: Canvas — destaque do nó selecionado

**Files:**
- Modify: `static/editor/editor-canvas.js`

- [ ] **Step 1: Destacar o nó selecionado no loop de nós**

Em `render(svg, m, estado)`, substituir o loop de nós:

```javascript
  for (const n of m.nos) {
    const p = metroParaPx(n.x, n.y);
    svg.appendChild(el("circle", { cx: p.px, cy: p.py, r: 6,
      fill: "#1e293b", "data-no": n.id }));
  }
```

por:

```javascript
  for (const n of m.nos) {
    const p = metroParaPx(n.x, n.y);
    const sel = estado.selecionado === n;
    svg.appendChild(el("circle", { cx: p.px, cy: p.py, r: sel ? 8 : 6,
      fill: sel ? "#dc2626" : "#1e293b", "data-no": n.id }));
  }
```

- [ ] **Step 2: Verificação de sintaxe**

Run: `node --check static/editor/editor-canvas.js`
Esperado: sem saída.

- [ ] **Step 3: Commit**

```bash
git add static/editor/editor-canvas.js
git commit -m "feat: editor-canvas — destaque do no selecionado"
```

---

### Task 4: Painel — propriedades do nó e carga distribuída na barra

**Files:**
- Modify: `static/editor/editor-ui.js`

> A UI permanece "burra": lê o estado de `m` e dispara callbacks com os valores completos.
> Detecção: barra = `selecionado.secao`; nó = `selecionado.x !== undefined`.

- [ ] **Step 1: Adicionar o campo de carga distribuída ao bloco da barra**

Substituir o bloco `if (selecionado && selecionado.secao) { ... }` por:

```javascript
  if (selecionado && selecionado.secao) {
    const cd = m.cargas.find((c) => c.tipo === "distribuida" && c.elemento === selecionado.id);
    html += `<h3>Barra ${selecionado.id}</h3>
      <label>Tipo</label>
      <select id="p-tipo">${["viga","pilar","fundacao"].map((t)=>`<option ${t===selecionado.tipo?"selected":""}>${t}</option>`).join("")}</select>
      <div class="row"><div><label>bw (cm)</label><input id="p-bw" type="number" value="${selecionado.secao.bw}"></div>
      <div><label>h (cm)</label><input id="p-h" type="number" value="${selecionado.secao.h}"></div></div>
      <label>Carga distribuída (kN/m)</label><input id="p-cd" type="number" value="${cd ? cd.valor : ""}">`;
  }
```

- [ ] **Step 2: Adicionar o bloco do nó (após o bloco da barra)**

Imediatamente após o `if (selecionado && selecionado.secao) { ... }` editado acima, adicionar:

```javascript
  if (selecionado && selecionado.x !== undefined) {
    const v = m.vinculos.find((x) => x.no === selecionado.id) || { ux: false, uy: false, rz: false };
    const cn = m.cargas.find((c) => c.tipo === "nodal" && c.no === selecionado.id) || { fx: 0, fy: 0, mz: 0 };
    const chk = (k) => (v[k] ? "checked" : "");
    html += `<h3>Nó ${selecionado.id}</h3>
      <div class="row"><div><label>x (m)</label><input id="p-nx" type="number" step="0.25" value="${selecionado.x}"></div>
      <div><label>y (m)</label><input id="p-ny" type="number" step="0.25" value="${selecionado.y}"></div></div>
      <label>Vínculo (apoio)</label>
      <div class="row" style="align-items:center">
        <label style="font-weight:normal"><input type="checkbox" id="p-ux" ${chk("ux")} style="width:auto"> ux</label>
        <label style="font-weight:normal"><input type="checkbox" id="p-uy" ${chk("uy")} style="width:auto"> uy</label>
        <label style="font-weight:normal"><input type="checkbox" id="p-rz" ${chk("rz")} style="width:auto"> rz</label>
      </div>
      <label>Cargas nodais</label>
      <div class="row"><div><label style="font-weight:normal">Fx (kN)</label><input id="p-fx" type="number" value="${cn.fx}"></div>
      <div><label style="font-weight:normal">Fy (kN)</label><input id="p-fy" type="number" value="${cn.fy}"></div>
      <div><label style="font-weight:normal">Mz (kN·m)</label><input id="p-mz" type="number" value="${cn.mz}"></div></div>`;
  }
```

- [ ] **Step 3: Religar os handlers do nó/distribuída**

Logo após a linha `on("#p-h", "change", (e) => cbs.aoEditarElemento({ secao: { h: +e.target.value } }));`, adicionar:

```javascript
  on("#p-cd", "change", (e) => cbs.aoSetCargaDistribuida(e.target.value === "" ? null : +e.target.value));
  on("#p-nx", "change", (e) => cbs.aoEditarNo({ x: +e.target.value }));
  on("#p-ny", "change", (e) => cbs.aoEditarNo({ y: +e.target.value }));
  const lerVinculo = () => cbs.aoSetVinculo({
    ux: painelEl.querySelector("#p-ux").checked,
    uy: painelEl.querySelector("#p-uy").checked,
    rz: painelEl.querySelector("#p-rz").checked,
  });
  ["#p-ux", "#p-uy", "#p-rz"].forEach((id) => on(id, "change", lerVinculo));
  const lerCargaNodal = () => cbs.aoSetCargaNodal({
    fx: +painelEl.querySelector("#p-fx").value,
    fy: +painelEl.querySelector("#p-fy").value,
    mz: +painelEl.querySelector("#p-mz").value,
  });
  ["#p-fx", "#p-fy", "#p-mz"].forEach((id) => on(id, "change", lerCargaNodal));
```

- [ ] **Step 4: Verificação de sintaxe**

Run: `node --check static/editor/editor-ui.js`
Esperado: sem saída.

- [ ] **Step 5: Commit**

```bash
git add static/editor/editor-ui.js
git commit -m "feat: editor-ui — painel do no (coords/vinculo/cargas) e distribuida na barra"
```

---

### Task 5: Controlador — seleção de nó, arrasto e callbacks

**Files:**
- Modify: `static/editor/editor.js`

- [ ] **Step 1: Adicionar `suprimirClick` ao estado e variável de arrasto**

Substituir o objeto `estado` e o helper `invalidarResultado`:

```javascript
const estado = { modelo: carregarAutosave(), modo: "selecionar",
                 selecionado: null, primeiroNo: null,
                 resultado: null, relatorioId: null };

function invalidarResultado() { estado.resultado = null; estado.relatorioId = null; }
```

por:

```javascript
const estado = { modelo: carregarAutosave(), modo: "selecionar",
                 selecionado: null, primeiroNo: null,
                 resultado: null, relatorioId: null, suprimirClick: false };

let arrasto = null;  // { no, startX, startY, moveu }

function invalidarResultado() { estado.resultado = null; estado.relatorioId = null; }
```

- [ ] **Step 2: Substituir o handler de `click` (remove prompts, seleciona nó/barra)**

Substituir o `svg.addEventListener("click", ...)` inteiro por:

```javascript
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
```

- [ ] **Step 3: Adicionar a máquina de arrasto (após o handler de click)**

Adicionar logo após o `svg.addEventListener("click", ...)`:

```javascript
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
  if (arrasto && arrasto.moveu) estado.suprimirClick = true;
  arrasto = null;
});
```

- [ ] **Step 4: Adicionar os novos callbacks em `cbs`**

Logo após o callback `aoEditarElemento: (patch) => { ... },` (que trata a barra), adicionar:

```javascript
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
```

- [ ] **Step 5: Verificação de sintaxe**

Run: `node --check static/editor/editor.js`
Esperado: sem saída.

- [ ] **Step 6: Commit**

```bash
git add static/editor/editor.js
git commit -m "feat: editor.js — selecao de no, arrasto e edicao via painel (sem prompts)"
```

---

### Task 6: Verificação end-to-end

**Files:** nenhum novo.

- [ ] **Step 1: Suítes completas**

Run: `.venv/Scripts/python -m pytest tests/ -q`
Esperado: 67 passed (inalterado — só a rota do editor é tocada, e os asserts seguem válidos).

Run: `npm test`
Esperado: 24 PASSED (18 modelo + 6 resultados).

- [ ] **Step 2: Verificação visual (Playwright + Chrome, sem `npm install`)**

Pré-checagem (não instalar nada):

Run: `node -e "require('playwright-core'); console.log('OK')"`
- Se imprimir `OK`: criar `verify_no.mjs` (abaixo) e rodar `node verify_no.mjs`.
- Se falhar (`Cannot find module`): pular para o **checklist manual** (Step 3) — **não rodar `npm install`** (faz prune do vendor versionado).

Conteúdo de `verify_no.mjs` (apaga ao final):

```javascript
import { chromium } from "playwright-core";
const BASE = "http://127.0.0.1:10066";
const MODELO = { estrutura: {
  material: { fck: 25, fyk: 500, CAA: 2, agregado: "basalto" },
  nos: [{ id: 1, x: 0, y: 0 }, { id: 2, x: 5, y: 0 }],
  elementos: [{ id: "B1", tipo: "viga", no_i: 1, no_j: 2, secao: { bw: 14, h: 40 } }],
  vinculos: [{ no: 1, ux: true, uy: true, rz: false }],
  cargas: [] } };
const browser = await chromium.launch({ channel: "chrome", headless: true });
const ctx = await browser.newContext({ viewport: { width: 1100, height: 720 } });
const page = await ctx.newPage();
page.on("pageerror", (e) => console.log("[pageerror]", e.message));
await page.addInitScript((m) => localStorage.setItem("dlima.editor.estrutura", JSON.stringify(m)), MODELO);
await page.goto(`${BASE}/estrutura/editor`, { waitUntil: "networkidle" });
await page.waitForSelector('#canvas [data-no="1"]', { state: "attached" });
// selecionar o nó 1
await page.locator('#canvas [data-no="1"]').click({ force: true });
await page.waitForSelector("#p-ux", { state: "attached" });
console.log("painel do nó abriu:", await page.locator("#painel h3:has-text('Nó 1')").count() === 1);
// marcar rz (3-GDL) e Mz
await page.locator("#p-rz").check();
await page.locator("#p-mz").fill("4"); await page.locator("#p-mz").dispatchEvent("change");
await page.waitForTimeout(150);
await page.screenshot({ path: "verify_no_painel.png" });
// arrastar o nó 2
const box = await page.locator('#canvas [data-no="2"]').boundingBox();
await page.mouse.move(box.x + box.width/2, box.y + box.height/2);
await page.mouse.down();
await page.mouse.move(box.x + 80, box.y - 80, { steps: 6 });
await page.mouse.up();
await page.waitForTimeout(150);
await page.screenshot({ path: "verify_no_arrasto.png" });
const n2 = await page.evaluate(() => JSON.parse(localStorage.getItem("dlima.editor.estrutura")).estrutura.nos.find(n => n.id === 2));
console.log("nó 2 após arrasto:", JSON.stringify(n2));
await browser.close();
console.log("DONE");
```

Antes de rodar o script, subir o app:

Run: `PORT=10066 .venv/Scripts/python app.py` (em background)
Depois: `node verify_no.mjs`
Esperado no console: `painel do nó abriu: true`, `nó 2 após arrasto:` com x/y diferentes de (5,0) e múltiplos de 0,25, `DONE`.
Inspecionar `verify_no_painel.png` (checkbox rz marcado, campos Fx/Fy/Mz) e `verify_no_arrasto.png` (nó 2 reposicionado).

- [ ] **Step 3: Checklist manual (fallback se Playwright indisponível)**

Subir `PORT=10066 .venv/Scripts/python app.py`, abrir `http://localhost:10066/estrutura/editor`:
- [ ] Toolbar tem só Selecionar / Nó / Barra / Apagar.
- [ ] Criar 2 nós + barra; selecionar um nó → painel mostra x/y, checkboxes ux/uy/rz, campos Fx/Fy/Mz.
- [ ] Marcar ux+uy → aparece apoio fixo (triângulo); marcar rz também → engaste (base).
- [ ] Desmarcar os 3 → o vínculo some.
- [ ] Pôr Fy=-10 → seta de carga nodal aparece no nó.
- [ ] Selecionar a barra → campo "Carga distribuída"; pôr 10 → setas distribuídas.
- [ ] Arrastar um nó → ele se move com snap; o resultado calculado (se houver) some.

- [ ] **Step 4: Limpeza dos artefatos de verificação**

Run: `rm -f verify_no.mjs verify_no_painel.png verify_no_arrasto.png`
Parar o app (processo `app.py`).
Não há nada a commitar deste step (artefatos efêmeros).

- [ ] **Step 5: Push e PR**

```bash
git push -u origin feat/editor-melhorias-no
```
Abrir PR com base `feat/integracao-acabamento-estruturas` (empilhado) ou `main`, conforme a ordem de merge desejada.

---

## Self-Review (cobertura da spec)

| Requisito da spec | Task |
|---|---|
| `moverNo` (snap) | 1 |
| `setVinculo` upsert + remoção em all-false | 1 |
| `setCargaNodal` um-por-nó + remove-em-zero | 1 |
| `setCargaDistribuida` (campo da barra) | 1 |
| Toolbar sem Vínculo/Carga | 2 |
| Destaque do nó selecionado | 3 |
| Painel do nó: coords, vínculo 3-GDL, Fx/Fy/Mz | 4 |
| Campo distribuída na barra | 4 |
| Seleção de nó ou barra no modo Selecionar | 5 |
| Arrasto de nós com snap + limiar clique/arrasto | 5 |
| Invalidar resultado ao mover/editar | 5 (callbacks + arrasto) |
| Sem `prompt()` | 5 (remoção dos branches) |
| Testes node + suites verdes + visual | 1, 6 |

**Consistência de nomes (verificada):** callbacks `aoEditarNo`/`aoSetVinculo`/`aoSetCargaNodal`/`aoSetCargaDistribuida` definidos na Task 5 e consumidos na Task 4; ids de DOM `p-nx/p-ny/p-ux/p-uy/p-rz/p-fx/p-fy/p-mz/p-cd` definidos e religados na Task 4; funções de modelo `moverNo/setVinculo/setCargaNodal/setCargaDistribuida` definidas na Task 1 e usadas na Task 5.
```
