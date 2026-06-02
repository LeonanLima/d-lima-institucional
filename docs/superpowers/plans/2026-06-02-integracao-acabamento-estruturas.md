# Integração e Acabamento do App de Estruturas — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tornar o app de estruturas descobrível (hub `/estrutura`) e fechar o ciclo desenhar → calcular → ver resultado dentro do próprio editor, reaproveitando o `resultado` que `POST /api/estrutura` já devolve.

**Architecture:** Uma rota nova no blueprint `estrutura_bp` (`GET /estrutura`) + um template de hub e crosslinks. No frontend, um módulo puro novo (`editor-resultados.js`, testável em `node --test`) formata o `resultado`; o canvas ganha um overlay de reações; o painel ganha um bloco de resultados; o controlador guarda o último `resultado`/`id` e o invalida quando o modelo muda. A API e o motor **não mudam**.

**Tech Stack:** Python 3 / Flask 3, Jinja2, SVG + JavaScript ES modules, `node --test` (lógica pura), pytest (rota). `package.json` já tem `"type":"module"` e `npm test`.

> **STATUS (2026-06-02): TODAS AS 6 TASKS CONCLUÍDAS.** Suítes: 67 pytest + 18 node verdes. Caminho de dados (hub, rota do editor, POST /api/estrutura → fy=25 kN, relatório) verificado via HTTP. Falta apenas a conferência visual no navegador pelo usuário. Branch `feat/integracao-acabamento-estruturas`, ainda não pushada.

**Contrato de `POST /api/estrutura` (já existente, imutável):**
```json
{ "id": "ab12cd34", "status": "ok",
  "resultado": {
    "reacoes":       { "<id_no>": { "fx": 0.0, "fy": 25.0, "mz": 0.0 } },
    "deslocamentos": { "<id_no>": { "ux": 0.0, "uy": -2.3, "rz": 0.001 } },
    "avisos":        [ "..." ],
    "elementos":     { "<id_el>": { } } } }
```
`reacoes` em kN/kN·m; `deslocamentos` ux/uy em **mm**, rz em **rad**. Chaves = id do nó (string).

---

## File Map

| Arquivo | Responsabilidade |
|---|---|
| `engine/rotas.py` | + rota `GET /estrutura` (hub) |
| `templates/estrutura.html` | Hub: 2 cartões (Editor, Referência) |
| `templates/editor.html` | Header ganha link "← Estruturas" |
| `templates/referencia.html` | Header ganha link "← Estruturas" |
| `tests/test_estrutura_hub.py` | pytest da rota do hub |
| `static/editor/editor-resultados.js` | **Puro:** formata `resultado` (reações, desloc. máx., avisos) |
| `static/editor/editor-resultados.test.js` | `node --test` do módulo puro |
| `static/editor/editor-canvas.js` | + `desenharResultados()` (overlay de reações) chamado no fim de `render()` |
| `static/editor/editor-ui.js` | `renderPainel()` aceita `resumo`+`relatorioId` e renderiza o bloco de resultados |
| `static/editor/editor.js` | Estado `resultado`/`relatorioId`; `aoCalcular` guarda o resultado; invalida ao editar |

---

### Task 1: Hub de Estruturas — rota, template e crosslinks ✅ CONCLUÍDA

**Files:**
- Create: `tests/test_estrutura_hub.py`
- Modify: `engine/rotas.py`
- Create: `templates/estrutura.html`
- Modify: `templates/editor.html`
- Modify: `templates/referencia.html`

- [ ] **Step 1: Escrever teste falho `tests/test_estrutura_hub.py`**

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


def test_hub_responde_200(client):
    r = client.get('/estrutura')
    assert r.status_code == 200


def test_hub_tem_links_editor_e_referencia(client):
    html = client.get('/estrutura').data.decode('utf-8')
    assert '/estrutura/editor' in html
    assert '/referencia' in html
```

- [ ] **Step 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_estrutura_hub.py -v`
Esperado: FAIL — 404 em `test_hub_responde_200` (rota inexistente).

- [ ] **Step 3: Adicionar a rota em `engine/rotas.py`**

Adicionar logo **antes** da rota `/estrutura/editor` (após a linha `estrutura_bp = Blueprint("estrutura", __name__)`):

```python
@estrutura_bp.route("/estrutura")
def hub():
    return render_template("estrutura.html")
```

- [ ] **Step 4: Criar `templates/estrutura.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>D'LIMA — Estruturas</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:Arial,sans-serif;background:#f4f4f9;color:#1e293b}
    header{background:#0056b3;color:#fff;padding:14px 20px;font-size:18px;font-weight:bold}
    .wrap{max-width:760px;margin:32px auto;padding:0 16px}
    .sub{color:#475569;margin:6px 0 22px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}
    .card{display:block;background:#fff;border:1px solid #e2e8f0;border-left:4px solid #0056b3;
      border-radius:8px;padding:18px;text-decoration:none;color:inherit;
      box-shadow:0 1px 3px rgba(0,0,0,.08);transition:transform .12s,box-shadow .12s}
    .card:hover{transform:translateY(-2px);box-shadow:0 4px 10px rgba(0,0,0,.12)}
    .card .ico{font-size:26px}
    .card .tit{font-weight:bold;font-size:16px;margin:8px 0 4px;color:#0056b3}
    .card .desc{font-size:13px;color:#475569}
  </style>
</head>
<body>
  <header>🏗 D'LIMA — Estruturas</header>
  <div class="wrap">
    <p class="sub">Ferramentas de cálculo e referência em concreto armado.</p>
    <div class="grid">
      <a class="card" href="/estrutura/editor">
        <div class="ico">✏️</div>
        <div class="tit">Editor de Estrutura</div>
        <div class="desc">Desenhe pórticos planos e calcule reações, esforços e detalhamento.</div>
      </a>
      <a class="card" href="/referencia">
        <div class="ico">📐</div>
        <div class="tit">Referência Técnica</div>
        <div class="desc">Consulta rápida de fórmulas e tabelas das normas (NBR).</div>
      </a>
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 5: Adicionar crosslink no header de `templates/editor.html`**

Substituir a linha:

```html
  <header>🏗 D'LIMA — Editor de Estrutura</header>
```

por:

```html
  <header style="display:flex;align-items:center;gap:12px">
    <a href="/estrutura" style="color:#cfe2ff;text-decoration:none;font-weight:normal">← Estruturas</a>
    <span>🏗 D'LIMA — Editor de Estrutura</span>
  </header>
```

- [ ] **Step 6: Adicionar crosslink no header de `templates/referencia.html`**

Substituir a linha:

```html
    <span>🏗 D'LIMA Referência Técnica</span>
```

por:

```html
    <span><a href="/estrutura" style="color:#cfe2ff;text-decoration:none">←</a> 🏗 D'LIMA Referência Técnica</span>
```

- [ ] **Step 7: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_estrutura_hub.py -v`
Esperado: 2 PASSED.

- [ ] **Step 8: Commit**

```bash
git add engine/rotas.py templates/estrutura.html templates/editor.html templates/referencia.html tests/test_estrutura_hub.py
git commit -m "feat: hub /estrutura + crosslinks no editor e na referencia"
```

---

### Task 2: `editor-resultados.js` — módulo puro de formatação (TDD) ✅ CONCLUÍDA

**Files:**
- Create: `static/editor/editor-resultados.test.js`
- Create: `static/editor/editor-resultados.js`

- [ ] **Step 1: Escrever teste falho `static/editor/editor-resultados.test.js`**

```javascript
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
```

- [ ] **Step 2: Rodar teste — verificar FAIL**

Run: `node --test static/editor/editor-resultados.test.js`
Esperado: FAIL — `Cannot find module './editor-resultados.js'`.

- [ ] **Step 3: Implementar `static/editor/editor-resultados.js`**

```javascript
// Formatação pura do `resultado` de POST /api/estrutura para exibição.
// Sem DOM, sem canvas — testável em node --test.

const EPS = 0.05; // ignora componentes desprezíveis (kN / kN·m)

export function formatarNumero(v, casas = 1) {
  return Number(v).toFixed(casas).replace(".", ",");
}

// Reações por nó, ordenadas por id. `texto` p/ o painel, `label` compacto p/ o canvas.
export function formatarReacoes(reacoes) {
  return Object.keys(reacoes)
    .map((k) => ({ no: Number(k), ...reacoes[k] }))
    .sort((a, b) => a.no - b.no)
    .map((r) => {
      const partes = [];
      if (Math.abs(r.fx) >= EPS) partes.push(`Fx ${formatarNumero(r.fx)} kN`);
      if (Math.abs(r.fy) >= EPS) partes.push(`Fy ${formatarNumero(r.fy)} kN`);
      if (Math.abs(r.mz) >= EPS) partes.push(`Mz ${formatarNumero(r.mz)} kN·m`);
      const texto = partes.length ? partes.join(", ") : "≈ 0";
      const seta = r.fy > EPS ? "↑" : r.fy < -EPS ? "↓" : "";
      const label = Math.abs(r.fy) >= EPS
        ? `${seta} ${formatarNumero(Math.abs(r.fy))} kN` : "";
      return { no: r.no, fx: r.fx, fy: r.fy, mz: r.mz, texto, label };
    });
}

// Maior deslocamento de translação (mm) entre todos os nós.
export function deslocamentoMaximo(deslocamentos) {
  let melhor = null;
  for (const k of Object.keys(deslocamentos)) {
    const d = deslocamentos[k];
    const mag = Math.hypot(d.ux, d.uy); // mm
    if (melhor === null || mag > melhor.mag) melhor = { no: Number(k), mag };
  }
  if (melhor === null) return null;
  return { no: melhor.no, mm: melhor.mag,
           texto: `Nó ${melhor.no}: ${formatarNumero(melhor.mag, 2)} mm` };
}

// Resumo completo p/ o painel.
export function resumoResultado(resultado) {
  return {
    reacoes: formatarReacoes(resultado.reacoes || {}),
    deslocamentoMax: deslocamentoMaximo(resultado.deslocamentos || {}),
    avisos: resultado.avisos || [],
  };
}
```

- [ ] **Step 4: Rodar teste — verificar PASS**

Run: `node --test static/editor/editor-resultados.test.js`
Esperado: 6 PASSED.

- [ ] **Step 5: Rodar a suíte Node completa (não quebrou nada)**

Run: `npm test`
Esperado: 18 PASSED (12 do modelo + 6 dos resultados).

- [ ] **Step 6: Commit**

```bash
git add static/editor/editor-resultados.js static/editor/editor-resultados.test.js
git commit -m "feat: editor-resultados — formatacao pura de reacoes/deslocamento/avisos"
```

---

### Task 3: `editor-canvas.js` — overlay de reações no canvas ✅ CONCLUÍDA

**Files:**
- Modify: `static/editor/editor-canvas.js`

> Render (DOM/SVG) — verificação por sintaxe + manual. A lógica testável já está na Task 2.

- [ ] **Step 1: Importar o formatador no topo de `static/editor/editor-canvas.js`**

Substituir a linha:

```javascript
import { snap } from "./editor-modelo.js";
```

por:

```javascript
import { snap } from "./editor-modelo.js";
import { formatarReacoes } from "./editor-resultados.js";
```

- [ ] **Step 2: Chamar o overlay no fim de `render()`**

Em `static/editor/editor-canvas.js`, dentro de `render(svg, m, estado)`, logo **antes** do `}` que fecha a função (após o loop `for (const n of m.nos) { ... }`), adicionar:

```javascript
  if (estado.resultado) desenharResultados(svg, m, estado.resultado);
```

- [ ] **Step 3: Adicionar a função `desenharResultados` ao fim do arquivo**

Adicionar no final de `static/editor/editor-canvas.js`:

```javascript
export function desenharResultados(svg, m, resultado) {
  if (!resultado || !resultado.reacoes) return;
  for (const r of formatarReacoes(resultado.reacoes)) {
    if (!r.label) continue;
    const n = m.nos.find((x) => x.id === r.no);
    if (!n) continue;
    const p = metroParaPx(n.x, n.y);
    const t = el("text", { x: p.px + 10, y: p.py + 26,
      fill: "#15803d", "font-size": 12, "font-weight": "bold" });
    t.textContent = r.label;
    svg.appendChild(t);
  }
}
```

- [ ] **Step 4: Verificação de sintaxe**

Run: `node --check static/editor/editor-canvas.js`
Esperado: sem saída (sintaxe OK).

- [ ] **Step 5: Commit**

```bash
git add static/editor/editor-canvas.js
git commit -m "feat: editor-canvas — overlay das reacoes nos nos apoiados"
```

---

### Task 4: `editor-ui.js` — bloco de resultados no painel ✅ CONCLUÍDA

**Files:**
- Modify: `static/editor/editor-ui.js`

> UI (DOM) — verificação por sintaxe + manual. A UI permanece "burra": recebe `resumo` já formatado (objeto plano) e `relatorioId`; não importa `editor-resultados.js`.

- [ ] **Step 1: Estender a assinatura de `renderPainel`**

Em `static/editor/editor-ui.js`, substituir a linha:

```javascript
export function renderPainel(painelEl, m, selecionado, cbs) {
```

por:

```javascript
export function renderPainel(painelEl, m, selecionado, cbs, resumo = null, relatorioId = null) {
```

- [ ] **Step 2: Inserir o bloco de resultados antes da seção "Arquivo"**

Em `renderPainel`, substituir o trecho:

```javascript
  html += `<h3>Arquivo</h3>
```

por:

```javascript
  if (resumo) {
    html += `<h3>Resultados</h3>`;
    if (resumo.deslocamentoMax)
      html += `<p><b>Desloc. máx:</b> ${resumo.deslocamentoMax.texto}</p>`;
    html += `<div style="font-size:12px;line-height:1.6">` +
      resumo.reacoes.map((r) => `<div>Nó ${r.no}: ${r.texto}</div>`).join("") +
      `</div>`;
    if (resumo.avisos && resumo.avisos.length)
      html += resumo.avisos.map((a) =>
        `<div style="color:#991b1b;margin-top:4px">⚠ ${a}</div>`).join("");
    if (relatorioId)
      html += `<button class="primary" id="p-rel" style="background:#0056b3;margin-top:8px">Ver relatório completo →</button>`;
  }

  html += `<h3>Arquivo</h3>
```

- [ ] **Step 3: Religar o botão do relatório**

Em `renderPainel`, logo **após** a linha:

```javascript
  on("#p-calc", "click", () => cbs.aoCalcular());
```

adicionar:

```javascript
  on("#p-rel", "click", () => cbs.aoAbrirRelatorio());
```

- [ ] **Step 4: Verificação de sintaxe**

Run: `node --check static/editor/editor-ui.js`
Esperado: sem saída (sintaxe OK).

- [ ] **Step 5: Commit**

```bash
git add static/editor/editor-ui.js
git commit -m "feat: editor-ui — bloco de resultados e botao do relatorio no painel"
```

---

### Task 5: `editor.js` — guardar resultado, exibir e invalidar ✅ CONCLUÍDA

**Files:**
- Modify: `static/editor/editor.js`

> Controlador. Verificação por sintaxe + manual end-to-end (Task 6).

- [ ] **Step 1: Importar `editor-resultados` no topo**

Em `static/editor/editor.js`, substituir:

```javascript
import * as UI from "./editor-ui.js";
```

por:

```javascript
import * as UI from "./editor-ui.js";
import * as Resultados from "./editor-resultados.js";
```

- [ ] **Step 2: Adicionar `resultado`/`relatorioId` ao estado**

Substituir:

```javascript
const estado = { modelo: carregarAutosave(), modo: "selecionar",
                 selecionado: null, primeiroNo: null };
```

por:

```javascript
const estado = { modelo: carregarAutosave(), modo: "selecionar",
                 selecionado: null, primeiroNo: null,
                 resultado: null, relatorioId: null };

function invalidarResultado() { estado.resultado = null; estado.relatorioId = null; }
```

- [ ] **Step 3: Passar `resumo`+`relatorioId` ao painel em `redesenhar`**

Substituir a função `redesenhar`:

```javascript
function redesenhar() {
  Canvas.render(svg, estado.modelo, estado);
  UI.renderPainel(painel, estado.modelo, estado.selecionado, cbs);
  autosave();
}
```

por:

```javascript
function redesenhar() {
  Canvas.render(svg, estado.modelo, estado);
  const resumo = estado.resultado ? Resultados.resumoResultado(estado.resultado) : null;
  UI.renderPainel(painel, estado.modelo, estado.selecionado, cbs, resumo, estado.relatorioId);
  autosave();
}
```

- [ ] **Step 4: Invalidar o resultado quando o modelo muda no canvas**

No handler `svg.addEventListener("click", ...)`, substituir a primeira linha do corpo:

```javascript
  const rect = svg.getBoundingClientRect();
```

por:

```javascript
  if (estado.modo !== "selecionar") invalidarResultado();
  const rect = svg.getBoundingClientRect();
```

- [ ] **Step 5: `aoCalcular` guarda o resultado em vez de abrir a aba; novo callback `aoAbrirRelatorio`**

Substituir o callback `aoCalcular` inteiro:

```javascript
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
```

por:

```javascript
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
```

- [ ] **Step 6: Invalidar o resultado ao editar material/elemento e ao importar**

Substituir os callbacks `aoEditarMaterial`, `aoEditarElemento` e `aoImportar`:

```javascript
  aoEditarMaterial: (patch) => { Object.assign(estado.modelo.material, patch); autosave(); },
  aoEditarElemento: (patch) => {
    if (!estado.selecionado) return;
    if (patch.secao) Object.assign(estado.selecionado.secao, patch.secao);
    if (patch.tipo) estado.selecionado.tipo = patch.tipo;
    redesenhar();
  },
```

por:

```javascript
  aoEditarMaterial: (patch) => { invalidarResultado(); Object.assign(estado.modelo.material, patch); redesenhar(); },
  aoEditarElemento: (patch) => {
    if (!estado.selecionado) return;
    invalidarResultado();
    if (patch.secao) Object.assign(estado.selecionado.secao, patch.secao);
    if (patch.tipo) estado.selecionado.tipo = patch.tipo;
    redesenhar();
  },
```

e substituir, dentro de `aoImportar`, a linha:

```javascript
        estado.modelo = M.fromJson(JSON.parse(r.result));
        estado.selecionado = null; redesenhar();
```

por:

```javascript
        estado.modelo = M.fromJson(JSON.parse(r.result));
        estado.selecionado = null; invalidarResultado(); redesenhar();
```

- [ ] **Step 7: Verificação de sintaxe**

Run: `node --check static/editor/editor.js`
Esperado: sem saída (sintaxe OK).

- [ ] **Step 8: Commit**

```bash
git add static/editor/editor.js
git commit -m "feat: editor.js — exibe resultado inline e invalida ao editar"
```

---

### Task 6: Verificação end-to-end e fechamento ✅ CONCLUÍDA (suítes + caminho de dados via HTTP; render visual no navegador pendente de conferência do usuário)

**Files:** nenhum novo.

- [ ] **Step 1: Suíte completa (Python + Node)**

Run: `.venv/Scripts/python -m pytest tests/ -q`
Esperado: 67 passed (65 antigos + 2 do hub).

Run: `npm test`
Esperado: 18 PASSED.

- [ ] **Step 2: Subir o app e validar no navegador**

Run: `.venv/Scripts/python app.py`
Abrir `http://localhost:10000/estrutura` e seguir o checklist:
- [ ] Hub mostra 2 cartões; "Editor de Estrutura" abre `/estrutura/editor`; "Referência Técnica" abre `/referencia`.
- [ ] Header do editor e da referência têm "← Estruturas" e voltam ao hub.
- [ ] Desenhar viga biapoiada (2 nós, 1 barra, fixo+móvel, carga distribuída 10 kN/m) e clicar "Calcular →":
  - [ ] Aparecem rótulos verdes de reação (≈ `↑ 25,0 kN`) ao lado dos apoios no canvas.
  - [ ] Painel mostra bloco "Resultados" com reações por nó, "Desloc. máx" em mm e (se houver) avisos.
  - [ ] Botão "Ver relatório completo →" abre `/api/relatorio/<id>` em nova aba.
- [ ] Editar a seção da barra ou adicionar um nó **limpa** os rótulos de reação (resultado obsoleto some).
- [ ] Recalcular reexibe os resultados.

- [ ] **Step 3: Commit de eventuais ajustes**

Se algum passo manual exigir correção: corrigir, re-rodar e commitar com mensagem específica. Se tudo passou, nada a commitar.

- [ ] **Step 4: Push e PR**

```bash
git push -u origin feat/integracao-acabamento-estruturas
```
Abrir PR com base `main`.

---

## Self-Review (cobertura da spec)

| Requisito da spec | Task |
|---|---|
| Hub `GET /estrutura` com cartões Editor + Referência | 1 |
| Crosslinks "← Estruturas" no editor e na referência | 1 (Steps 5–6) |
| Landing `/` (MCMV) intocada | — (nenhuma task altera `index.html`) |
| Módulo puro `editor-resultados.js` (reações, desloc. máx., avisos) | 2 |
| Testes `node --test` do módulo puro | 2 |
| Overlay de reações no canvas | 3 |
| Painel de resultados + botão "Ver relatório completo →" | 4 |
| Estado `resultado`/`relatorioId`; `aoCalcular` consome o retorno | 5 |
| Editar o modelo invalida o resultado obsoleto | 5 (Steps 4, 6) |
| API e motor não mudam | — (nenhuma task toca `engine/` exceto a rota do hub) |
| Suítes existentes verdes + pytest do hub + checklist manual | 6 |

**Nota sobre unidades:** o módulo de resultados não converte nada — usa kN das reações e mm dos deslocamentos exatamente como o motor já serializa (`solver.py` converte cm→mm internamente). Mantém a convenção "o editor não converte unidade".
