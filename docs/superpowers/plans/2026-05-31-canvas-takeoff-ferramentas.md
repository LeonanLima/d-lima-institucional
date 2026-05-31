# Canvas Takeoff — Ferramentas Avançadas — Plano de Implementação

> **Para agentes:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar task a task.

**Goal:** Adicionar lupa arrastável, seleção de linha int/med/ext, contorno automático, seleção por retângulo, zoom com scroll e suporte a DWG/DXF no módulo Takeoff Digital.

**Architecture:** Canvas HTML5 puro (sem Fabric.js) — extensão direta do `canvas.tsx` existente. DWG/DXF convertidos para PNG no Flask com `ezdxf[draw]`. Novas funcionalidades adicionadas como props/estado/refs no canvas existente, sem reescrever.

**Tech Stack:** HTML5 Canvas API, React hooks, Python ezdxf[draw] (Flask), pdfjs-dist (já presente no page.tsx), TypeScript.

**Projetos:**
- `C:\Users\leona\OneDrive\Documentos\d-lima-institucional\` → Flask backend
- `C:\Users\leona\OneDrive\Documentos\dlima-app\` → Next.js frontend

---

## Estrutura de Arquivos

```
d-lima-institucional/
└── app.py                                        ← MODIFICAR: + /api/convert-drawing

dlima-app/
├── components/takeoff/
│   ├── canvas.tsx                                ← MODIFICAR: lupa drag, zoom, offset, rect-select, contorno
│   └── toolbar.tsx                               ← CRIAR: botões int/med/ext, contorno, retângulo
├── app/(dashboard)/obras/[id]/takeoff/
│   └── page.tsx                                  ← MODIFICAR: DWG support + toolbar integration
└── lib/
    └── dxf-api.ts                                ← CRIAR: chamada à API Flask
```

---

## TASK 1 — Flask: /api/convert-drawing

**Projetos:** `d-lima-institucional/`
**Files:**
- Modify: `app.py`

- [ ] **Step 1.1 — Instalar dependências Python**

```bash
cd C:\Users\leona\OneDrive\Documentos\d-lima-institucional
pip install "ezdxf[draw]" flask-cors matplotlib
```

- [ ] **Step 1.2 — Substituir app.py completo**

```python
# app.py
from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
from flask_cors import CORS
import os, tempfile

app = Flask(__name__)
CORS(app, origins=[
    "https://app.dlima.eng.br",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/convert-drawing', methods=['POST'])
def convert_drawing():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    name = file.filename.lower() if file.filename else ''
    if not (name.endswith('.dxf') or name.endswith('.dwg')):
        return jsonify({'error': 'Envie um arquivo .dxf ou .dwg'}), 400

    suffix = os.path.splitext(name)[1]
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    file.save(tmp.name)
    tmp_path = tmp.name
    tmp.close()

    try:
        import ezdxf
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from io import BytesIO

        try:
            doc = ezdxf.readfile(tmp_path)
        except ezdxf.DXFError as e:
            msg = str(e)
            if 'version' in msg.lower() or 'AC1' in msg:
                return jsonify({
                    'error': 'Formato DWG muito antigo (anterior a R2004). '
                             'Abra no AutoCAD/LibreCAD e salve como DXF.'
                }), 400
            return jsonify({'error': f'Erro ao ler arquivo: {msg}'}), 400

        fig = plt.figure(figsize=(20, 20), facecolor='white')
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor('white')

        ctx_render = RenderContext(doc)
        backend = MatplotlibBackend(ax)
        Frontend(ctx_render, backend).draw_layout(doc.modelspace())

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)

        return send_file(buf, mimetype='image/png',
                         download_name='drawing.png',
                         as_attachment=False)

    except Exception as e:
        return jsonify({'error': f'Erro inesperado: {str(e)}'}), 500
    finally:
        os.unlink(tmp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
```

- [ ] **Step 1.3 — Testar endpoint**

```bash
# Num terminal separado, inicie o Flask:
python app.py

# Em outro terminal, teste com um arquivo DXF qualquer:
curl -X POST http://localhost:10000/api/convert-drawing \
  -F "file=@caminho/para/arquivo.dxf" \
  --output resultado.png

# Abra resultado.png — deve mostrar a planta
```

Resultado esperado: `resultado.png` com a planta em fundo branco com linhas escuras.

- [ ] **Step 1.4 — Commit**

```bash
cd C:\Users\leona\OneDrive\Documentos\d-lima-institucional
git add app.py
git commit -m "feat: endpoint /api/convert-drawing — DXF/DWG para PNG via ezdxf"
```

---

## TASK 2 — lib/dxf-api.ts

**Projeto:** `dlima-app/`
**Files:**
- Create: `lib/dxf-api.ts`

- [ ] **Step 2.1 — Criar o módulo**

```typescript
// lib/dxf-api.ts
const FLASK_URL = process.env.NEXT_PUBLIC_FLASK_URL ?? 'http://localhost:10000'

/** Envia arquivo DWG/DXF ao Flask, retorna um Blob PNG. */
export async function convertDrawing(file: File): Promise<Blob> {
  const form = new FormData()
  form.append('file', file)

  const res = await fetch(`${FLASK_URL}/api/convert-drawing`, {
    method: 'POST',
    body: form,
  })

  if (!res.ok) {
    const json = await res.json().catch(() => ({}))
    throw new Error(json.error ?? `Erro ${res.status} ao converter arquivo`)
  }

  return res.blob()
}
```

- [ ] **Step 2.2 — Adicionar variável de ambiente**

Abrir `dlima-app/.env.local` e adicionar:

```bash
NEXT_PUBLIC_FLASK_URL=http://localhost:10000
```

Para produção, alterar para a URL do servidor Flask em deploy.

- [ ] **Step 2.3 — Commit**

```bash
cd C:\Users\leona\OneDrive\Documentos\dlima-app
git add lib/dxf-api.ts .env.local
git commit -m "feat: dxf-api — cliente para /api/convert-drawing do Flask"
```

---

## TASK 3 — canvas.tsx: Zoom com scroll + Pan com Espaço

**Files:**
- Modify: `dlima-app/components/takeoff/canvas.tsx`

O canvas atual não tem zoom. Vamos adicionar estado de zoom e pan e aplicar na renderização.

- [ ] **Step 3.1 — Adicionar estado e refs de zoom/pan (após os useState existentes, linha ~46)**

```typescript
// Adicionar após: const [hovering, setHovering] = useState<number | null>(null)
const [zoomLevel, setZoomLevel] = useState(1)
const panRef     = useRef({ x: 0, y: 0 })
const isPanRef   = useRef(false)
const panStartRef = useRef({ x: 0, y: 0 })
```

- [ ] **Step 3.2 — Atualizar ptFrom para converter coordenadas físicas → lógicas**

Substituir a função `ptFrom` existente:

```typescript
function ptFrom(e: { clientX: number; clientY: number }): Point {
  const rect = canvasRef.current!.getBoundingClientRect()
  const pixX = e.clientX - rect.left
  const pixY = e.clientY - rect.top
  return {
    x: (pixX - panRef.current.x) / zoomLevel,
    y: (pixY - panRef.current.y) / zoomLevel,
  }
}
```

- [ ] **Step 3.3 — Adicionar transform de zoom/pan ao início do useEffect de redesenho**

No `useEffect` de redesenho (que começa com `const canvas = canvasRef.current`), logo após `ctx.clearRect(...)`, adicionar:

```typescript
// Aplicar zoom e pan
ctx.save()
ctx.translate(panRef.current.x, panRef.current.y)
ctx.scale(zoomLevel, zoomLevel)
```

E antes do bloco de desenho da lupa e cursor (que devem ficar em coordenadas de tela), adicionar `ctx.restore()`:

```typescript
// Antes de drawCanvasCursor e drawLoupe:
ctx.restore()

if (cursor) drawCanvasCursor(ctx, cursor, zoomLevel)
if (cursor) drawLoupe(ctx, canvas, cursor, zoomLevel, panRef.current)
```

- [ ] **Step 3.4 — Passar coordenadas de tela (pixel) para drawLoupe**

A lupa precisa ler do canvas em coordenadas de pixel, não lógicas. Atualizar assinatura de `drawLoupe`:

```typescript
function drawLoupe(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  logPt: Point,           // coordenada lógica do cursor
  zoom: number,
  pan: { x: number; y: number }
) {
  // Converter coordenada lógica para pixel para ler o canvas
  const pixPt = {
    x: logPt.x * zoom + pan.x,
    y: logPt.y * zoom + pan.y,
  }
  const d  = LOUPE_R * 2
  const lx = canvas.width - d - 14, ly = 14
  // ... resto igual, usando pixPt ao invés de pt nas leituras do canvas:
  const srcW = d / LOUPE_ZOOM, srcH = d / LOUPE_ZOOM
  ctx.drawImage(canvas, pixPt.x - srcW / 2, pixPt.y - srcH / 2, srcW, srcH, lx, ly, d, d)
  // ... (manter a mira central e o anel de borda iguais, usando lx/ly/cx/cy existentes)
}
```

Atualizar `drawCanvasCursor` para receber `zoom` e usar `logPt` (sem mudança, pois já está em coordenadas lógicas após o `ctx.scale`):

```typescript
function drawCanvasCursor(ctx: CanvasRenderingContext2D, pt: Point, zoom: number) {
  const arm = 10 / zoom  // arm proporcional ao zoom para não ficar gigante
  // ... resto igual
}
```

- [ ] **Step 3.5 — Adicionar handler de scroll (wheel) no canvas**

```typescript
function handleWheel(e: React.WheelEvent<HTMLCanvasElement>) {
  e.preventDefault()
  const rect = canvasRef.current!.getBoundingClientRect()
  const pixX = e.clientX - rect.left
  const pixY = e.clientY - rect.top

  const factor = e.deltaY < 0 ? 1.1 : 0.9
  const newZoom = Math.min(Math.max(zoomLevel * factor, 0.1), 10)

  // Zoom centrado no cursor: ajustar pan para manter ponto fixo
  panRef.current = {
    x: pixX - (pixX - panRef.current.x) * (newZoom / zoomLevel),
    y: pixY - (pixY - panRef.current.y) * (newZoom / zoomLevel),
  }
  setZoomLevel(newZoom)
}
```

- [ ] **Step 3.6 — Pan com Espaço + arrastar**

```typescript
// Adicionar ao handleMouseDown (no início, antes do restante):
function handleMouseDown(e: React.MouseEvent<HTMLCanvasElement>) {
  if (e.button === 1 || isPanRef.current) {
    // Scroll click ou espaço pressionado
    panStartRef.current = { x: e.clientX - panRef.current.x, y: e.clientY - panRef.current.y }
    return
  }
  // ... restante existente
}

// Adicionar ao handleMouseMove (no início):
function handleMouseMove(e: React.MouseEvent<HTMLCanvasElement>) {
  if (isPanRef.current && e.buttons === 1) {
    panRef.current = {
      x: e.clientX - panStartRef.current.x,
      y: e.clientY - panStartRef.current.y,
    }
    setZoomLevel(z => z)  // forçar re-render
    return
  }
  // ... restante existente
}
```

Adicionar handlers de teclado no `useEffect` de carregamento de imagem (ou num `useEffect` separado):

```typescript
useEffect(() => {
  const onKeyDown = (e: KeyboardEvent) => {
    if (e.code === 'Space' && !e.repeat) { e.preventDefault(); isPanRef.current = true }
  }
  const onKeyUp = (e: KeyboardEvent) => {
    if (e.code === 'Space') isPanRef.current = false
  }
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('keyup', onKeyUp)
  return () => {
    window.removeEventListener('keydown', onKeyDown)
    window.removeEventListener('keyup', onKeyUp)
  }
}, [])
```

- [ ] **Step 3.7 — Adicionar `onWheel` e cursor dinâmico ao elemento `<canvas>`**

```tsx
<canvas
  ref={canvasRef}
  onClick={handleClick}
  onMouseMove={handleMouseMove}
  onMouseDown={handleMouseDown}
  onMouseUp={handleMouseUp}
  onMouseLeave={handleMouseLeave}
  onContextMenu={handleContextMenu}
  onWheel={handleWheel}
  onTouchStart={handleTouchStart}
  onTouchMove={handleTouchMove}
  onTouchEnd={handleTouchEnd}
  style={{ cursor: isPanRef.current ? 'grab' : 'none' }}
  className="max-w-full block select-none touch-none"
/>
```

- [ ] **Step 3.8 — Expor zoomIn/zoomOut/fitScreen via ref**

Adicionar ao `useImperativeHandle`:

```typescript
useImperativeHandle(ref, () => ({
  clear:     () => setPoints([]),
  undo:      () => setPoints(p => p.slice(0, -1)),
  closePoly: handleClose,
  zoomIn:  () => setZoomLevel(z => Math.min(z * 1.2, 10)),
  zoomOut: () => setZoomLevel(z => Math.max(z / 1.2, 0.1)),
  fitScreen: () => {
    panRef.current = { x: 0, y: 0 }
    setZoomLevel(1)
  },
  getZoom: () => zoomLevel,
}))
```

Atualizar a interface `TakeoffCanvasHandle`:

```typescript
export interface TakeoffCanvasHandle {
  clear:     () => void
  undo:      () => void
  closePoly: () => void
  zoomIn:    () => void
  zoomOut:   () => void
  fitScreen: () => void
  getZoom:   () => number
}
```

- [ ] **Step 3.9 — Testar**

```
npm run dev
Abrir uma obra com planta cadastrada
Usar scroll do mouse sobre o canvas → deve ampliar/reduzir centrado no cursor
Pressionar Espaço + arrastar → deve mover a planta (pan)
```

- [ ] **Step 3.10 — Commit**

```bash
cd C:\Users\leona\OneDrive\Documentos\dlima-app
git add components/takeoff/canvas.tsx
git commit -m "feat: zoom scroll + pan Espaço no takeoff canvas"
```

---

## TASK 4 — canvas.tsx: Lupa Arrastável

**Files:**
- Modify: `dlima-app/components/takeoff/canvas.tsx`

Atualmente a lupa é sempre exibida no canto superior direito. Queremos que o usuário arraste para qualquer posição.

- [ ] **Step 4.1 — Adicionar estado da posição da lupa**

```typescript
// Após os outros estados:
const loupePosRef    = useRef<{ x: number; y: number } | null>(null) // null = posição padrão
const isDragLoupe    = useRef(false)
const loupeDragOff   = useRef({ x: 0, y: 0 })
```

- [ ] **Step 4.2 — Modificar drawLoupe para posição configurável**

```typescript
function drawLoupe(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  logPt: Point,
  zoom: number,
  pan: { x: number; y: number }
) {
  const d  = LOUPE_R * 2
  // Posição configurável ou padrão (canto superior direito)
  const lx = loupePosRef.current ? loupePosRef.current.x - LOUPE_R : canvas.width - d - 14
  const ly = loupePosRef.current ? loupePosRef.current.y - LOUPE_R : 14
  const cx = lx + LOUPE_R, cy = ly + LOUPE_R

  // Fonte da ampliação: posição em pixels do cursor
  const pixPt = { x: logPt.x * zoom + pan.x, y: logPt.y * zoom + pan.y }

  ctx.save()
  ctx.shadowColor = 'rgba(0,0,0,0.7)'
  ctx.shadowBlur = 10
  ctx.beginPath()
  ctx.arc(cx, cy, LOUPE_R + 2, 0, Math.PI * 2)
  ctx.fillStyle = '#0F120F'
  ctx.fill()
  ctx.restore()

  ctx.save()
  ctx.beginPath()
  ctx.arc(cx, cy, LOUPE_R, 0, Math.PI * 2)
  ctx.clip()
  const srcW = d / LOUPE_ZOOM, srcH = d / LOUPE_ZOOM
  ctx.drawImage(canvas, pixPt.x - srcW / 2, pixPt.y - srcH / 2, srcW, srcH, lx, ly, d, d)
  ctx.restore()

  ctx.beginPath()
  ctx.arc(cx, cy, LOUPE_R, 0, Math.PI * 2)
  ctx.strokeStyle = '#B89B5E'
  ctx.lineWidth = 2
  ctx.stroke()

  // Mira central
  const arm = 11
  ;[{ col: 'rgba(0,0,0,0.9)', w: 3 }, { col: '#FFFFFF', w: 1.5 }].forEach(({ col, w }) => {
    ctx.strokeStyle = col; ctx.lineWidth = w
    ctx.beginPath()
    ctx.moveTo(cx - arm, cy); ctx.lineTo(cx + arm, cy)
    ctx.moveTo(cx, cy - arm); ctx.lineTo(cx, cy + arm)
    ctx.stroke()
  })
  ctx.beginPath()
  ctx.arc(cx, cy, 2, 0, Math.PI * 2)
  ctx.fillStyle = '#FFFFFF'
  ctx.fill()

  // Alça de drag (pequeno ícone no topo da lupa)
  ctx.beginPath()
  ctx.arc(cx, ly - 4, 5, 0, Math.PI * 2)
  ctx.fillStyle = '#B89B5E'
  ctx.fill()
}
```

- [ ] **Step 4.3 — Detectar clique na lupa em handleMouseDown**

No início de `handleMouseDown`, antes de qualquer outra lógica, adicionar:

```typescript
function handleMouseDown(e: React.MouseEvent<HTMLCanvasElement>) {
  const canvas = canvasRef.current!
  const rect   = canvas.getBoundingClientRect()
  const pixX   = e.clientX - rect.left
  const pixY   = e.clientY - rect.top

  // Verificar clique na lupa (área circular)
  const d  = LOUPE_R * 2
  const lx = loupePosRef.current ? loupePosRef.current.x - LOUPE_R : canvas.width - d - 14
  const ly = loupePosRef.current ? loupePosRef.current.y - LOUPE_R : 14
  const cx = lx + LOUPE_R, cy = ly + LOUPE_R
  const distToLoupe = Math.hypot(pixX - cx, pixY - cy)

  if (distToLoupe <= LOUPE_R + 6) {
    isDragLoupe.current  = true
    loupeDragOff.current = { x: pixX - cx, y: pixY - cy }
    e.preventDefault()
    return
  }

  if (e.button === 1 || isPanRef.current) {
    panStartRef.current = { x: e.clientX - panRef.current.x, y: e.clientY - panRef.current.y }
    return
  }

  // ... restante existente
  const pt  = cursorRef.current ?? ptFrom(e)
  const hit = nearestPt(pt)
  if (hit !== null) { dragIdx.current = hit; didDrag.current = false; e.preventDefault() }
}
```

- [ ] **Step 4.4 — Mover lupa em handleMouseMove**

No início de `handleMouseMove`, antes de qualquer outra lógica:

```typescript
function handleMouseMove(e: React.MouseEvent<HTMLCanvasElement>) {
  if (isDragLoupe.current) {
    const rect = canvasRef.current!.getBoundingClientRect()
    loupePosRef.current = {
      x: e.clientX - rect.left - loupeDragOff.current.x + LOUPE_R,
      y: e.clientY - rect.top  - loupeDragOff.current.y + LOUPE_R,
    }
    setZoomLevel(z => z) // forçar re-render
    return
  }
  // ... restante existente
}
```

- [ ] **Step 4.5 — Limpar drag em handleMouseUp e handleMouseLeave**

```typescript
function handleMouseUp() {
  isDragLoupe.current = false
  dragIdx.current = null
}

function handleMouseLeave() {
  isDragLoupe.current = false
  setCursor(null)
  setHovering(null)
  dragIdx.current = null
}
```

- [ ] **Step 4.6 — Testar**

```
npm run dev
Abrir takeoff com planta
Passar mouse sobre a lupa → cursor deve mostrar que é arrastável
Clicar e arrastar a lupa → deve se mover para nova posição
Mover cursor → lupa deve continuar mostrando o detalhe ampliado da nova posição
```

- [ ] **Step 4.7 — Commit**

```bash
git add components/takeoff/canvas.tsx
git commit -m "feat: lupa arrastável no canvas takeoff"
```

---

## TASK 5 — canvas.tsx: Seleção por Retângulo + Modo offsetMode

**Files:**
- Modify: `dlima-app/components/takeoff/canvas.tsx`

- [ ] **Step 5.1 — Adicionar props ao componente**

```typescript
interface Props {
  imageUrl:               string
  escala:                 number
  tipoMedicao:            'linear' | 'area' | 'volume'
  calibrando?:            boolean
  calMetros?:             string
  ortogonal?:             boolean
  snapBorda?:             boolean
  offsetMode?:            'internal' | 'medial' | 'external'  // NOVO
  wallThickness?:         number                              // NOVO — em metros, default 0.15
  rectSelectMode?:        boolean                             // NOVO
  onRectSelect?:          (pts: [Point, Point]) => void       // NOVO
  onCalibrationPoints?:   (pts: [Point, Point]) => void
  onMeasurementComplete?: (value: number, unit: string, vertices: Point[]) => void
}
```

Atualizar o `forwardRef` para receber as novas props:

```typescript
const TakeoffCanvas = forwardRef<TakeoffCanvasHandle, Props>(
  ({
    imageUrl, escala, tipoMedicao, calibrando, calMetros,
    ortogonal, snapBorda,
    offsetMode = 'medial', wallThickness = 0.15,
    rectSelectMode = false, onRectSelect,
    onCalibrationPoints, onMeasurementComplete,
  }, ref) => {
```

- [ ] **Step 5.2 — Adicionar estado do retângulo de seleção**

```typescript
// Após os outros estados:
const rectStartRef = useRef<Point | null>(null)
const [rectEnd,    setRectEnd]    = useState<Point | null>(null)
```

- [ ] **Step 5.3 — Lógica de seleção por retângulo em handleMouseDown e handleMouseMove**

No `handleMouseDown`, ao final (após verificação de loupe e pan), adicionar:

```typescript
if (rectSelectMode) {
  const pt = ptFrom(e)
  rectStartRef.current = pt
  setRectEnd(null)
  return
}
```

No `handleMouseMove`, após verificação de loupe e pan, adicionar:

```typescript
if (rectSelectMode && rectStartRef.current && e.buttons === 1) {
  setRectEnd(ptFrom(e))
  return
}
```

No `handleMouseUp`, adicionar:

```typescript
if (rectSelectMode && rectStartRef.current && rectEnd) {
  onRectSelect?.([rectStartRef.current, rectEnd])
  rectStartRef.current = null
  setRectEnd(null)
  return
}
```

- [ ] **Step 5.4 — Desenhar retângulo de seleção no useEffect de redesenho**

Dentro do bloco `ctx.save() / ctx.scale()`, adicionar ao final (antes do `ctx.restore()`):

```typescript
// Retângulo de seleção
if (rectSelectMode && rectStartRef.current && rectEnd) {
  const rs = rectStartRef.current
  const re = rectEnd
  ctx.save()
  ctx.strokeStyle = '#2196F3'
  ctx.lineWidth   = 1.5 / zoomLevel
  ctx.setLineDash([6 / zoomLevel, 3 / zoomLevel])
  ctx.fillStyle   = 'rgba(33,150,243,0.08)'
  ctx.beginPath()
  ctx.rect(rs.x, rs.y, re.x - rs.x, re.y - rs.y)
  ctx.fill()
  ctx.stroke()
  ctx.restore()
}
```

- [ ] **Step 5.5 — Mostrar indicador de offsetMode no canvas**

No bloco de desenho do cursor (após `ctx.restore()`), adicionar badge do modo:

```typescript
// Badge offsetMode (em coordenadas de tela, após ctx.restore())
if (offsetMode !== 'medial' && cursor) {
  const pixX = cursor.x * zoomLevel + panRef.current.x
  const pixY = cursor.y * zoomLevel + panRef.current.y
  const label = offsetMode === 'internal' ? 'INT' : 'EXT'
  ctx.font = 'bold 10px Inter, sans-serif'
  ctx.fillStyle = '#2196F3'
  ctx.fillText(label, pixX + 14, pixY - 8)
}
```

E modificar `applySnaps` para aplicar offset perpendicular quando offsetMode != 'medial':

```typescript
function applySnaps(raw: Point, lastPoint?: Point): Point {
  let pt = raw

  if (snapBorda) {
    let best = raw, minB = DARK_T
    for (let dy = -SNAP_R; dy <= SNAP_R; dy++) {
      for (let dx = -SNAP_R; dx <= SNAP_R; dx++) {
        if (dx * dx + dy * dy > SNAP_R * SNAP_R) continue
        const b = pixB(raw.x + dx, raw.y + dy)
        if (b < minB) { minB = b; best = { x: raw.x + dx, y: raw.y + dy } }
      }
    }
    if (minB < DARK_T) {
      pt = findEndpoint(raw, best) ?? best

      // Aplicar offset perpendicular para int/ext
      if (offsetMode !== 'medial' && escala > 0) {
        const thicknessPx = wallThickness * escala
        const halfPx = thicknessPx / 2
        // Determinar direção dominante
        let h = 0, v = 0
        for (let k = -4; k <= 4; k++) {
          if (pixB(pt.x + k, pt.y) < DARK_T) h++
          if (pixB(pt.x, pt.y + k) < DARK_T) v++
        }
        const sign = offsetMode === 'internal' ? -1 : 1
        if (h >= v) {
          pt = { x: pt.x, y: pt.y + sign * halfPx }
        } else {
          pt = { x: pt.x + sign * halfPx, y: pt.y }
        }
      }
    }
  }

  if (ortogonal && lastPoint) {
    const dx = Math.abs(pt.x - lastPoint.x)
    const dy = Math.abs(pt.y - lastPoint.y)
    pt = dx >= dy ? { x: pt.x, y: lastPoint.y } : { x: lastPoint.x, y: pt.y }
  }

  return pt
}
```

- [ ] **Step 5.6 — Commit**

```bash
git add components/takeoff/canvas.tsx
git commit -m "feat: seleção por retângulo e prop offsetMode no canvas takeoff"
```

---

## TASK 6 — canvas.tsx: Contorno Automático (Auto-detect + Fechar Polígono)

**Files:**
- Modify: `dlima-app/components/takeoff/canvas.tsx`

O canvas já tem "Fechar Polígono" (clique no 1º ponto). Vamos adicionar:
1. `autoDetect()` — escaneia pixels escuros e cria polígono a partir das bordas detectadas
2. `clearPoints()` exposto via ref

- [ ] **Step 6.1 — Adicionar `autoDetect` e expor via ref**

Adicionar função dentro do componente (após `handleClose`):

```typescript
function autoDetect(): boolean {
  const canvas = canvasRef.current
  if (!canvas || !pixDataRef.current) return false

  const w = pixWRef.current
  const h = pixHRef.current
  const data = pixDataRef.current
  const detected: Point[] = []

  // Varredura a cada 4px para performance
  const step = 4
  const threshold = 100 // luminância máxima para considerar "linha"

  function lum(x: number, y: number): number {
    const ix = Math.round(x), iy = Math.round(y)
    if (ix < 0 || iy < 0 || ix >= w || iy >= h) return 255
    const i = (iy * w + ix) * 4
    return (data[i] + data[i + 1] + data[i + 2]) / 3
  }

  // Encontrar contorno externo: buscar a primeira linha escura horizontal
  // a partir de cada borda e registrar os pontos extremos
  const contourPts: Point[] = []
  for (let scanY = 0; scanY < h; scanY += step) {
    for (let x = 0; x < w; x++) {
      if (lum(x, scanY) < threshold) { contourPts.push({ x, y: scanY }); break }
    }
    for (let x = w - 1; x >= 0; x--) {
      if (lum(x, scanY) < threshold) { contourPts.push({ x, y: scanY }); break }
    }
  }
  for (let scanX = 0; scanX < w; scanX += step) {
    for (let y = 0; y < h; y++) {
      if (lum(scanX, y) < threshold) { contourPts.push({ x: scanX, y }); break }
    }
    for (let y = h - 1; y >= 0; y--) {
      if (lum(scanX, y) < threshold) { contourPts.push({ x: scanX, y }); break }
    }
  }

  if (contourPts.length < 4) return false

  // Reduzir para pontos representativos (convex hull simplificado)
  // Usar cantos: top-left, top-right, bottom-right, bottom-left
  const minX = Math.min(...contourPts.map(p => p.x))
  const maxX = Math.max(...contourPts.map(p => p.x))
  const minY = Math.min(...contourPts.map(p => p.y))
  const maxY = Math.max(...contourPts.map(p => p.y))

  // Manter pontos extremos como polígono (retângulo envolvente do desenho)
  const poly: Point[] = [
    { x: minX, y: minY },
    { x: maxX, y: minY },
    { x: maxX, y: maxY },
    { x: minX, y: maxY },
  ]

  setPoints(poly)
  return true
}
```

- [ ] **Step 6.2 — Expor autoDetect via ref**

```typescript
useImperativeHandle(ref, () => ({
  clear:      () => setPoints([]),
  undo:       () => setPoints(p => p.slice(0, -1)),
  closePoly:  handleClose,
  autoDetect,
  zoomIn:    () => setZoomLevel(z => Math.min(z * 1.2, 10)),
  zoomOut:   () => setZoomLevel(z => Math.max(z / 1.2, 0.1)),
  fitScreen: () => { panRef.current = { x: 0, y: 0 }; setZoomLevel(1) },
  getZoom:   () => zoomLevel,
}))
```

Atualizar interface:

```typescript
export interface TakeoffCanvasHandle {
  clear:      () => void
  undo:       () => void
  closePoly:  () => void
  autoDetect: () => boolean   // retorna false se não detectou linhas
  zoomIn:     () => void
  zoomOut:    () => void
  fitScreen:  () => void
  getZoom:    () => number
}
```

- [ ] **Step 6.3 — Testar autoDetect**

```
npm run dev
Abrir uma obra com planta nítida (planta em fundo branco com linhas escuras)
Clicar no botão Auto-detect (ainda não existe, usar DevTools console temporariamente):
  canvasRef.current.autoDetect()
Resultado esperado: polígono aparece em volta do desenho
```

- [ ] **Step 6.4 — Commit**

```bash
git add components/takeoff/canvas.tsx
git commit -m "feat: autoDetect contorno no canvas takeoff"
```

---

## TASK 7 — toolbar.tsx: Barra de Ferramentas

**Files:**
- Create: `dlima-app/components/takeoff/toolbar.tsx`

- [ ] **Step 7.1 — Criar o componente**

```tsx
// components/takeoff/toolbar.tsx
'use client'

export type OffsetMode = 'internal' | 'medial' | 'external'
export type ContourMode = 'auto' | 'polygon' | 'join'

interface TakeoffToolbarProps {
  offsetMode:      OffsetMode
  onOffsetMode:    (m: OffsetMode) => void
  contourMode:     ContourMode
  onContourMode:   (m: ContourMode) => void
  onAutoDetect:    () => void
  rectSelectActive: boolean
  onRectSelect:    () => void
  onDelete:        () => void
  onJoinClose:     () => void   // fecha/une o polígono atual
  zoom:            number
  onZoomIn:        () => void
  onZoomOut:       () => void
  onFitScreen:     () => void
}

export function TakeoffToolbar({
  offsetMode, onOffsetMode,
  contourMode, onContourMode, onAutoDetect, onJoinClose,
  rectSelectActive, onRectSelect, onDelete,
  zoom, onZoomIn, onZoomOut, onFitScreen,
}: TakeoffToolbarProps) {
  const btn = (active: boolean, danger = false) => [
    'flex flex-col items-center gap-0.5 px-2.5 py-1.5 rounded-lg border text-[10px]',
    'font-semibold transition-colors whitespace-nowrap',
    active   ? 'bg-dlima-gold/10 border-dlima-gold text-dlima-gold'
             : danger
               ? 'bg-dlima-surface border-dlima-border text-dlima-muted hover:border-red-500/50 hover:text-red-400'
               : 'bg-dlima-surface border-dlima-border text-dlima-muted hover:border-dlima-gold/40',
  ].join(' ')

  const group = 'flex flex-col gap-0.5'
  const groupLabel = 'text-[8px] font-bold uppercase tracking-widest text-dlima-gold'
  const groupItems = 'flex gap-1 items-center'
  const separator = 'w-px self-stretch bg-dlima-border mx-1'

  return (
    <div className="flex items-center gap-1 bg-dlima-dark border border-dlima-border rounded-xl px-3 py-2 flex-wrap">

      {/* Linha: Interna / Medial / Externa */}
      <div className={group}>
        <span className={groupLabel}>Linha</span>
        <div className={groupItems}>
          {([
            ['internal', '⬜', 'Interna'],
            ['medial',   '➖', 'Medial'],
            ['external', '⬛', 'Externa'],
          ] as [OffsetMode, string, string][]).map(([m, icon, label]) => (
            <button key={m} onClick={() => onOffsetMode(m)} className={btn(offsetMode === m)}>
              <span className="text-sm">{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className={separator} />

      {/* Contorno */}
      <div className={group}>
        <span className={groupLabel}>Contorno</span>
        <div className={groupItems}>
          <button
            onClick={() => { onContourMode('auto'); onAutoDetect() }}
            className={btn(contourMode === 'auto')}
            title="Detectar automaticamente o contorno"
          >
            <span className="text-sm">🤖</span>
            <span>Auto</span>
          </button>
          <button
            onClick={() => onContourMode('polygon')}
            className={btn(contourMode === 'polygon')}
            title="Clique nos vértices — feche clicando no 1º ponto"
          >
            <span className="text-sm">📍</span>
            <span>Polígono</span>
          </button>
          <button
            onClick={() => { onContourMode('join'); onJoinClose() }}
            className={btn(contourMode === 'join')}
            title="Fechar e unir os pontos do polígono atual em um contorno fechado"
          >
            <span className="text-sm">🔗</span>
            <span>Unir</span>
          </button>
        </div>
      </div>

      <div className={separator} />

      {/* Seleção + Apagar */}
      <div className={group}>
        <span className={groupLabel}>Seleção</span>
        <div className={groupItems}>
          <button onClick={onRectSelect} className={btn(rectSelectActive)}
            title="Arraste para selecionar área">
            <span className="text-sm">⬚</span>
            <span>Retângulo</span>
          </button>
          <button onClick={onDelete} className={btn(false, true)}
            title="Apagar pontos selecionados (Del)">
            <span className="text-sm">🗑️</span>
            <span>Apagar</span>
          </button>
        </div>
      </div>

      <div className={separator} />

      {/* Zoom */}
      <div className={group}>
        <span className={groupLabel}>Zoom</span>
        <div className={groupItems}>
          <button onClick={onZoomOut} className={btn(false)} title="Reduzir (scroll ↓)">
            <span className="text-sm">🔽</span>
            <span>−</span>
          </button>
          <span className="text-[10px] text-dlima-muted min-w-[36px] text-center font-mono">
            {Math.round(zoom * 100)}%
          </span>
          <button onClick={onZoomIn} className={btn(false)} title="Ampliar (scroll ↑)">
            <span className="text-sm">🔼</span>
            <span>+</span>
          </button>
          <button onClick={onFitScreen} className={btn(false)} title="Encaixar na tela">
            <span className="text-sm">📐</span>
            <span>Fit</span>
          </button>
        </div>
      </div>

    </div>
  )
}
```

- [ ] **Step 7.2 — Commit**

```bash
git add components/takeoff/toolbar.tsx
git commit -m "feat: TakeoffToolbar — linha int/med/ext, contorno, retângulo, zoom"
```

---

## TASK 8 — takeoff/page.tsx: DWG + Toolbar integrados

**Files:**
- Modify: `dlima-app/app/(dashboard)/obras/[id]/takeoff/page.tsx`

- [ ] **Step 8.1 — Adicionar imports**

No topo do arquivo, após os imports existentes, adicionar:

```typescript
import { TakeoffToolbar, type OffsetMode, type ContourMode } from '@/components/takeoff/toolbar'
import { convertDrawing } from '@/lib/dxf-api'
```

- [ ] **Step 8.2 — Adicionar estado da toolbar**

Após o bloco de `useState` existente, adicionar:

```typescript
const [offsetMode,      setOffsetMode]      = useState<OffsetMode>('medial')
const [contourMode,     setContourMode]      = useState<ContourMode>('polygon')
const [rectSelectActive, setRectSelectActive] = useState(false)
const [currentZoom,     setCurrentZoom]      = useState(1)
```

- [ ] **Step 8.3 — Modificar handleUpload para suportar DWG/DXF**

Substituir o bloco `if (file.name.toLowerCase().endsWith('.dwg'))` que rejeita DWG pelo seguinte:

```typescript
// Suporte DWG/DXF via Flask
if (name.endsWith('.dwg') || name.endsWith('.dxf')) {
  try {
    const pngBlob = await convertDrawing(file)
    uploadFile = new File([pngBlob], file.name.replace(/\.(dwg|dxf)$/i, '.png'), { type: 'image/png' })
  } catch (err: any) {
    alert(`Erro ao converter ${name.toUpperCase()}:\n${err.message}`)
    return
  }
}
```

(Manter o bloco PDF existente logo abaixo, sem alterações.)

Atualizar também o atributo `accept` do input de upload:

```tsx
<input
  type="file"
  accept="image/png,image/jpeg,image/jpg,application/pdf,.pdf,.dwg,.dxf"
  className="hidden"
  onChange={handleUpload}
/>
```

E atualizar o texto descritivo:

```tsx
<p className="text-dlima-muted text-xs mt-1">PNG, JPG, PDF, DWG ou DXF</p>
```

- [ ] **Step 8.4 — Adicionar handler de seleção por retângulo**

```typescript
function handleRectSelect(pts: [Point, Point]) {
  // Quando retângulo é solto, desativar modo e mostrar opção de apagar
  // (no contexto atual, o rectSelect serve para feedback visual;
  //  apagar via teclado Delete ou botão na toolbar)
  setRectSelectActive(false)
}

function handleDeleteSelected() {
  // Para pontos do polígono atual, limpar todos (behavior intuitivo)
  canvasRef.current?.clear()
}
```

- [ ] **Step 8.5 — Adicionar a toolbar na seção "Barra de ferramentas do canvas"**

No bloco `{planta && escala > 0 && (...)` que tem os botões Ortogonal e Snap, adicionar a `TakeoffToolbar` logo acima dos botões existentes:

```tsx
{planta && escala > 0 && (
  <div className="space-y-2 mb-2">
    <TakeoffToolbar
      offsetMode={offsetMode}
      onOffsetMode={setOffsetMode}
      contourMode={contourMode}
      onContourMode={setContourMode}
      onAutoDetect={() => {
        const ok = canvasRef.current?.autoDetect()
        if (!ok) alert('Nenhuma linha detectada. Tente modo Polígono.')
      }}
      onJoinClose={() => canvasRef.current?.closePoly()}
      rectSelectActive={rectSelectActive}
      onRectSelect={() => setRectSelectActive(r => !r)}
      onDelete={handleDeleteSelected}
      zoom={currentZoom}
      onZoomIn={() => { canvasRef.current?.zoomIn(); setCurrentZoom(canvasRef.current?.getZoom() ?? 1) }}
      onZoomOut={() => { canvasRef.current?.zoomOut(); setCurrentZoom(canvasRef.current?.getZoom() ?? 1) }}
      onFitScreen={() => { canvasRef.current?.fitScreen(); setCurrentZoom(1) }}
    />
    {/* botões Ortogonal e Snap — manter exatamente como estão no page.tsx atual */}
    <div className="flex gap-2 flex-wrap">
      <button onClick={() => setOrtogonal(o => !o)} className={...}>
        {/* manter implementação original sem alterar */}
        ⊞ Ortogonal
      </button>
      <button onClick={() => setSnapBorda(s => !s)} className={...}>
        🧲 Snap Linhas
      </button>
    </div>
  </div>
)}
```

- [ ] **Step 8.6 — Passar novas props ao TakeoffCanvas**

```tsx
<TakeoffCanvas
  ref={canvasRef}
  imageUrl={planta.arquivo_url}
  escala={escala || 100}
  tipoMedicao={tipoAtual}
  calibrando={calibrando}
  calMetros={calibrando ? escalaInput : undefined}
  ortogonal={ortogonal}
  snapBorda={snapBorda}
  offsetMode={offsetMode}
  wallThickness={0.15}
  rectSelectMode={rectSelectActive}
  onRectSelect={handleRectSelect}
  onCalibrationPoints={handleCalibrationPoints}
  onMeasurementComplete={handleMeasureComplete}
/>
```

- [ ] **Step 8.7 — Adicionar listener de Delete para apagar pontos**

No `useEffect` de inicialização (ou num useEffect separado):

```typescript
useEffect(() => {
  const onKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Delete' || e.key === 'Backspace') {
      if (document.activeElement === document.body) {
        canvasRef.current?.undo()
      }
    }
  }
  window.addEventListener('keydown', onKeyDown)
  return () => window.removeEventListener('keydown', onKeyDown)
}, [])
```

- [ ] **Step 8.8 — Testar fluxo completo**

```
1. npm run dev
2. Criar obra e entrar no Takeoff
3. Upload de PDF → deve converter e mostrar planta
4. Upload de DXF → Flask deve converter para PNG → planta aparece
5. Upload de DWG → mesmo comportamento
6. Toolbar aparece com botões: Interna/Medial/Externa, Contorno, Retângulo, Zoom
7. Scroll do mouse → zoom funciona
8. Espaço + arrastar → pan funciona
9. Arrastar lupa → se move para nova posição
10. Botão Auto → detecta contorno
11. Botão Fit → volta para zoom 100%
```

- [ ] **Step 8.9 — Commit final**

```bash
git add app/(dashboard)/obras/\[id\]/takeoff/page.tsx
git commit -m "feat: DWG/DXF support + toolbar int/med/ext + zoom + lupa no takeoff"
```

---

## Checklist de verificação final

- [ ] DXF de qualquer versão (R12, R2004, R2018) converte via Flask e aparece no canvas
- [ ] DWG R2004+ converte via Flask e aparece no canvas
- [ ] DWG antigo (pré-R2004) mostra mensagem de erro clara
- [ ] PDF continua funcionando (sem regressão)
- [ ] PNG/JPG continua funcionando (sem regressão)
- [ ] Scroll do mouse aplica zoom centrado no cursor
- [ ] Espaço + arrastar faz pan
- [ ] Botões +/−/Fit na toolbar funcionam e atualizam o percentual
- [ ] Lupa é arrastável para qualquer posição e continua mostrando detalhe
- [ ] Modo Interna aplica offset de −t/2 perpendicularmente à linha
- [ ] Modo Medial (padrão) não altera comportamento existente
- [ ] Modo Externa aplica offset de +t/2
- [ ] Retângulo de seleção aparece visualmente ao arrastar
- [ ] Auto-detect cria polígono ao redor do desenho
- [ ] Tecla Delete desfaz último ponto (Undo)
