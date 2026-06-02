# Spec — Editor de Estrutura (Fase 2)

**Data:** 2026-06-02
**Status:** Aprovado para implementação
**Escopo:** UI gráfica (canvas com malha + snap) para desenhar a estrutura, gerar o
JSON consumido pelo motor da Fase 1 e abrir o relatório de análise. Sem banco de dados.

Depende do motor da Fase 1 (`engine/`) e das rotas `POST /api/estrutura` /
`GET /api/relatorio/<id>`. Respeita as ADRs em
`2026-06-02-motor-decisoes-arquitetura.md` (rotas no blueprint, app.py fino).

---

## 1. Objetivo

Permitir que o usuário **desenhe** um pórtico plano (nós, barras, vínculos e cargas)
numa malha com snap, sem escrever JSON na mão, e obtenha o relatório de análise/
dimensionamento da Fase 1 com um clique.

---

## 2. Escopo

**No v1:**
- Canvas SVG com malha e snap (default 0,25 m), pan e zoom.
- Modos: Selecionar/mover, Nó, Barra, Vínculo, Carga, Apagar.
- Cargas: distribuída na barra (kN/m), concentrada no nó (Fx, Fy), momento no nó (Mz).
- Vínculos: presets (engaste, apoio fixo 2º gênero, apoio móvel) **e** checkboxes 3-GDL (ux, uy, rz).
- Painel de propriedades: seção (bw, h) e tipo do elemento; material global (fck, fyk, CAA, agregado).
- Export/Import do JSON da estrutura + autosave em `localStorage`.
- Validação local antes do envio; banner de erro do motor.
- "Calcular" → `POST /api/estrutura` → abre `/api/relatorio/<id>` em nova aba.

**Fora do v1 (futuro):**
- Lajes como placa, 3D, P-delta, vento/sismo (já fora do escopo do motor).
- Edição colaborativa, múltiplos projetos, banco de dados.
- Dimensionamento de pilar detalhado no relatório (peça separada da Fase 2).
- Cotas automáticas e impressão dedicada do desenho.

---

## 3. Arquitetura

### Backend (mínimo)
- Nova rota no blueprint `engine/rotas.py`:
  `GET /estrutura/editor` → `render_template("editor.html")`.
- Nenhuma lógica nova de cálculo no backend — reusa `/api/estrutura` e `/api/relatorio/<id>`.

### Frontend — `static/editor/` (SVG + JS vanilla, ES modules)

| Arquivo | Responsabilidade | Testável |
|---|---|---|
| `editor-modelo.js` | Estado puro da estrutura (nós, elementos, vínculos, cargas, material); `to_json()` no schema do motor; `validar()` | **Sim (node --test)** |
| `editor-canvas.js` | Render SVG (malha, nós, barras, cargas, vínculos); pan/zoom; snap; hit-testing | Manual |
| `editor-ui.js` | Toolbar/modos, painel de propriedades, material global, export/import, autosave | Manual |
| `editor.js` | Orquestra módulos; POST e abertura do relatório | Manual |
| `templates/editor.html` | Layout (toolbar + canvas + painel) e imports dos módulos | Manual |

`editor-modelo.js` não conhece o DOM — recebe/retorna dados puros, o que o torna
testável em Node e mantém o canvas (DOM) separado da lógica de modelo.

---

## 4. Modelo e serialização

Estado interno (unidades de tela em **metros**, como o schema de entrada do motor):

```js
{
  material: { fck: 25, fyk: 500, CAA: 2, agregado: "basalto" },
  nos:       [ { id, x, y } ],                       // metros
  elementos: [ { id, tipo, no_i, no_j, secao:{bw,h} } ],  // bw,h em cm
  vinculos:  [ { no, ux, uy, rz } ],
  cargas:    [ { tipo:"distribuida", elemento, valor, direcao }   // kN/m
             | { tipo:"nodal", no, fx, fy, mz } ]                 // kN, kNm
}
```

`to_json()` embrulha em `{ "estrutura": {...} }` — exatamente o schema que
`Estrutura.from_json` espera (conversão de unidades já é feita no motor: m→cm,
kN/m→kN/cm). O editor **não** converte unidades; envia metros e kN/m.

IDs: nós inteiros sequenciais (1,2,3…); elementos "B1","B2"… (renomeáveis no painel).

---

## 5. Fluxo de dados

```
desenho no canvas
   → editor-canvas atualiza editor-modelo (estado)
   → autosave localStorage a cada mudança
[Calcular]
   → editor-modelo.validar()  (local; se falhar, banner e para)
   → editor-modelo.to_json()
   → POST /api/estrutura
   → { id }  → window.open('/api/relatorio/' + id)
```

Export = baixar `estrutura.json` (saída de `to_json()`); Import = ler arquivo e
reconstruir o estado (valida o formato antes de aplicar).

---

## 6. Validação local (antes do POST)

`validar()` retorna lista de erros (vazia = ok):
- Pelo menos 1 vínculo e pelo menos 1 barra.
- Toda barra referencia 2 nós existentes e distintos.
- Toda barra tem seção com `bw > 0` e `h > 0`.
- Material com `fck > 0` e `fyk > 0`.

Erros são exibidos num banner; o envio só ocorre com a lista vazia.

---

## 7. Tratamento de erros

- POST com falha (400/500): banner mostra `error` retornado pelo motor; o desenho
  permanece (autosave).
- Import de JSON inválido: banner "arquivo inválido", estado atual preservado.
- localStorage indisponível: editor funciona sem autosave (degradação suave).

---

## 8. Testes

- **`node --test`** em `static/editor/editor-modelo.test.js` (lógica pura):
  - `to_json()` produz o schema esperado para uma viga biapoiada.
  - `validar()` acusa: sem vínculo, barra sem seção, barra com nó inexistente.
  - Import → estado → `to_json()` é idempotente (round-trip).
- **pytest** (`tests/test_editor_rota.py`): `GET /estrutura/editor` retorna 200 e o
  HTML contém o container do canvas e os imports dos módulos.
- **Checklist manual** (no navegador): criar viga biapoiada, lançar carga, Calcular,
  ver relatório; export/import; autosave ao recarregar.

`package.json` mínimo na raiz só para rodar `node --test` (sem dependências externas).

---

## 9. Critérios de aceite

- [ ] `GET /estrutura/editor` retorna 200 com canvas e toolbar.
- [ ] Desenhar 2 nós + 1 barra com snap; barra conecta os nós.
- [ ] Aplicar apoio fixo no nó 1 e móvel no nó 2 via preset.
- [ ] Lançar carga distribuída de 10 kN/m na barra.
- [ ] "Calcular" → relatório abre com reações ≈ 25 kN por apoio (viga 5 m).
- [ ] `validar()` bloqueia envio sem vínculo e mostra banner.
- [ ] Export gera JSON aceito pelo `/api/estrutura`; Import recria o desenho.
- [ ] Autosave restaura o desenho após recarregar a página.
- [ ] `node --test` e `pytest` passam.
- [ ] Site institucional e rotas da Fase 1 intactos.
```
