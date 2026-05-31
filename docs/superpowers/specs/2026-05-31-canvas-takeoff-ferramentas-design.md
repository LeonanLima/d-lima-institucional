# Canvas Takeoff — Ferramentas Avançadas — Design Spec

**Data:** 2026-05-31
**Módulo:** `dlima-app` → `app/(dashboard)/obras/[id]/takeoff/`
**Status:** Aprovado para implementação

---

## 1. Visão Geral

Adicionar ao módulo Takeoff Digital as seguintes ferramentas de interação com plantas (PDF e DWG/DXF de qualquer versão):

| Ferramenta | Descrição |
|---|---|
| Lupa arrastável | Círculo overlay que amplia a região abaixo do cursor |
| Linha Interna / Medial / Externa | Escolha da face de referência para medir paredes |
| Contorno completo (3 modos) | Auto-detect, fechar polígono, unir linhas selecionadas |
| Seleção por retângulo | Drag para selecionar múltiplos objetos de uma vez |
| Apagar exedentes | Remove objetos selecionados do canvas |
| Zoom PDF e DWG | Scroll + botões, fit-to-screen, pan |

---

## 2. Arquitetura

### Camadas do canvas

```
┌─────────────────────────────────────────────────┐
│  UI (React)                                     │
│  toolbar.tsx · magnifier.tsx · painel offset    │
├─────────────────────────────────────────────────┤
│  Canvas (Fabric.js)                             │
│  Seleção · Contorno · Delete · Zoom             │
├─────────────────────────────────────────────────┤
│  Leitura de arquivos                            │
│  pdf-loader.ts (pdf.js) · dxf-loader.ts        │
│  Flask /api/convert-drawing (ezdxf Python)      │
├─────────────────────────────────────────────────┤
│  Cálculo                                        │
│  Offset int/med/ext · Área (Shoelace) · Perímetro│
└─────────────────────────────────────────────────┘
```

### Fluxo DWG / DXF (qualquer versão)

```
Upload DWG ou DXF
       ↓
POST /api/convert-drawing  (Flask + ezdxf)
       ↓
ezdxf lê o arquivo (DXF R12–R2018; DWG R2004+)
       ↓
JSON normalizado: { entities: [ {type, points}... ] }
       ↓
dxf-loader.ts converte entities → Fabric Line/Polyline
       ↓
Renderiza no canvas (vetorial, zoom infinito)
```

### Fluxo PDF

```
Upload PDF
       ↓
pdf-loader.ts (pdf.js, browser)
       ↓
Renderiza página selecionada como imagem de fundo
       ↓
Zoom reprocessa em resolução atual (nitidez mantida)
```

---

## 3. Backend — Novo Endpoint Flask

**Arquivo:** `app.py` (projeto `d-lima-institucional`, Flask existente)

```
POST /api/convert-drawing
Content-Type: multipart/form-data
Body: file=<arquivo .dwg ou .dxf>

Response 200:
{
  "entities": [
    { "type": "LINE",     "start": [x, y], "end": [x, y] },
    { "type": "LWPOLYLINE", "points": [[x,y], ...], "closed": true },
    { "type": "ARC",      "center": [x,y], "radius": r, "start_angle": a, "end_angle": b }
  ],
  "bounds": { "min_x": n, "min_y": n, "max_x": n, "max_y": n }
}

Response 400: { "error": "mensagem" }
```

**Dependência Python:** `ezdxf` (pip install ezdxf) + `flask-cors` (pip install flask-cors)

**Nota de versão DWG:** ezdxf lê DWG nativamente a partir do R2004. Para DWG anteriores ao R2004, o usuário deve abrir no AutoCAD/LibreCAD e salvar como DXF — isso é coberto pelo fallback de erro.

**CORS:** O `dlima-app` (Vercel) chama o Flask de outro domínio. Configurar `flask-cors` para permitir origin `https://app.dlima.eng.br` (produção) e `http://localhost:3000` (desenvolvimento).

**Entidades suportadas:** LINE, LWPOLYLINE, POLYLINE, ARC, CIRCLE, SPLINE (simplificado para segmentos)

---

## 4. Componentes e Hooks

### 4.1 `toolbar.tsx`
Barra de ferramentas horizontal (ou lateral em mobile) com grupos de botões:

- **Lupa** — toggle on/off
- **Tipo de linha** — 3 botões exclusivos: Interna / Medial / Externa
- **Contorno** — dropdown com 3 sub-modos: Auto-detect / Fechar polígono / Unir seleção
- **Seleção** — Retângulo de seleção
- **Apagar** — Delete selecionados (também responde à tecla Delete)
- **Zoom** — botões + / − / Fit, percentual atual

### 4.2 `magnifier.tsx`
Componente `div` overlay posicionado absolutamente sobre o canvas. Contém um `<canvas>` interno de 120×120px com borda arredondada dourada. Não captura eventos de mouse do canvas principal (pointer-events: none exceto na borda de arraste).

### 4.3 `useMagnifier.ts`
- Estado: `{ active, x, y, zoom: 2|3|4 }`
- `onMouseMove` → atualiza posição + executa `drawImage` do canvas principal recortado e ampliado
- Arraste pela borda da lupa reposiciona sem ativar ferramentas do canvas

### 4.4 `useLineOffset.ts`
- Estado: `offsetMode: 'internal' | 'medial' | 'external'`
- `wallThickness`: padrão 0.15m, editável por obra
- Ao clicar numa linha/parede: calcula vetor normal, aplica offset (−t/2, 0, +t/2)
- Exibe preview da linha de referência em azul antes de confirmar medição

### 4.5 `useContour.ts`
Três modos:

**Auto-detect:**
1. Chama `canvas.toDataURL()` para obter imagem atual
2. `getImageData` → varre pixels escuros (luminância < 80)
3. Agrupa pixels contínuos em segmentos horizontais e verticais
4. Cria `Fabric.Line` para cada segmento detectado
5. Se nenhuma linha detectada → exibe mensagem de erro inline

**Fechar polígono:**
1. Cada clique no canvas adiciona um vértice (círculo pequeno verde)
2. Botão "Fechar" → une último ponto ao primeiro com `Fabric.Polygon`
3. Mínimo de 3 pontos para fechar

**Unir seleção:**
1. Lê `canvas.getActiveObjects()`
2. Extrai endpoints de cada linha
3. Cria `Fabric.Polyline` conectando todos os pontos em ordem
4. Remove as linhas originais
5. Se contorno não fechado → aviso "Contorno aberto"

### 4.6 `useRectSelect.ts`
- Ativa `canvas.selection = true` e `selectionColor` azul semitransparente
- Mouse up → `canvas.getActiveObjects()` retorna seleção
- Cursor muda para crosshair no modo ativo

### 4.7 `useCanvasZoom.ts`
- Scroll do mouse → `canvas.zoomToPoint(pointer, zoom * factor)`
- Botões +/− → step de 10% centrado no viewport
- Fit → `canvas.setZoom(fitZoom)` + `canvas.viewportTransform` para centralizar
- Pan → Espaço + arraste (cursor grab)
- Range: 10% – 1000%
- Percentual exibido em tempo real na barra inferior

### 4.8 `dxf-loader.ts`
- Recebe JSON do endpoint Flask
- Converte cada entidade em objeto Fabric correspondente
- Normaliza coordenadas usando `bounds` para centralizar no canvas
- Retorna `FabricObject[]` prontos para `canvas.add()`

### 4.9 `pdf-loader.ts`
- Usa `pdfjs-dist` para renderizar página como `ImageBitmap`
- Se PDF com múltiplas páginas → retorna `pageCount` e exibe seletor antes de renderizar
- Define como `canvas.backgroundImage` do Fabric
- Ao zoom alto (>200%) → re-renderiza a página na resolução atual para manter nitidez

---

## 5. Tratamento de Erros

| Situação | Comportamento |
|---|---|
| DWG/DXF inválido | Toast: "Arquivo não reconhecido. Verifique se é um arquivo DWG ou DXF válido." Canvas intacto. |
| DWG anterior ao R2004 | Toast: "Formato DWG muito antigo. Abra no AutoCAD e salve como DXF antes de importar." |
| PDF com múltiplas páginas | Seletor de página (1 de N) antes de renderizar |
| Auto-detect sem resultado | Mensagem inline: "Nenhuma linha detectada. Tente Fechar Polígono." Nada criado. |
| Contorno aberto ao calcular | Alerta: "Contorno não fechado." Botão "Fechar" aparece automaticamente. |
| Arquivo maior que 50MB | Aviso de confirmação antes do upload. PDF processado página a página. |
| Falha na API /api/convert-drawing | Toast de erro + fallback: orienta usuário a exportar como DXF R2010 no AutoCAD |

---

## 6. Novos Arquivos

```
dlima-app/
├── components/takeoff/
│   ├── canvas.tsx              ← MODIFICAR: monta toolbar + hooks
│   ├── toolbar.tsx             ← CRIAR
│   └── magnifier.tsx           ← CRIAR
├── hooks/takeoff/
│   ├── useMagnifier.ts         ← CRIAR
│   ├── useLineOffset.ts        ← CRIAR
│   ├── useContour.ts           ← CRIAR
│   ├── useRectSelect.ts        ← CRIAR
│   ├── useCanvasZoom.ts        ← CRIAR
│   └── useAutoDetect.ts        ← CRIAR (parte do useContour)
└── lib/
    ├── dxf-loader.ts           ← CRIAR
    └── pdf-loader.ts           ← CRIAR

d-lima-institucional/  (Flask existente)
└── app.py                      ← MODIFICAR: + endpoint /api/convert-drawing

Dependências novas:
  dlima-app:    pdfjs-dist
  Flask:        ezdxf (pip)
```

---

## 7. Checklist de Testes

- [ ] Upload PDF → planta renderizada como fundo, zoom sem distorção
- [ ] Upload DXF R12 → linhas vetoriais no canvas
- [ ] Upload DXF R2018 → linhas vetoriais no canvas
- [ ] Upload DWG → conversão via Flask + renderização correta
- [ ] Lupa: arrastar sobre paredes mostra detalhe ampliado em tempo real
- [ ] Linha Medial: resultado coincide com eixo das paredes no DXF
- [ ] Linha Interna / Externa: offset visível e correto em relação à medial
- [ ] Retângulo: selecionar 3 linhas → apagar → apenas as 3 somem
- [ ] Auto-detect em planta nítida → linhas geradas sobre as paredes
- [ ] Fechar polígono: 4 cliques → polígono fechado corretamente
- [ ] Unir seleção: 4 linhas selecionadas → polyline fechado
- [ ] Ctrl+Z desfaz cada ação (apagar, mover, criar linha)
- [ ] PDF com múltiplas páginas → seletor aparece antes de carregar
- [ ] Arquivo +50MB → aviso de confirmação exibido
