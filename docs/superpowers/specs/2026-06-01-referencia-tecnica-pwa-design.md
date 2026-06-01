# Spec — D'LIMA Referência Técnica PWA

**Data:** 2026-06-01  
**Status:** Aprovado para implementação  
**Escopo:** PWA de referência técnica de concreto armado com busca por palavra-chave, instalável em PC e celular

---

## 1. Objetivo

Criar uma página web instalável como PWA (`/referencia`) que serve como referência técnica offline do documento consolidado Carini + Bastos. O engenheiro digita uma palavra-chave (ex: "fck", "torção", "estribo") e vê imediatamente as seções relevantes com conteúdo completo, rankeadas por relevância.

---

## 2. Arquitetura

### Componentes

| Arquivo | Papel | Mudança |
|---|---|---|
| `app.py` | Serve a rota `GET /referencia` | +2 linhas |
| `templates/referencia.html` | App completo (HTML + CSS + JS inline) | Novo arquivo |
| `static/manifest.json` | Manifesto PWA atualizado para `/referencia` | Atualizado |
| `static/sw.js` | Service worker com cache offline | Atualizado |

### Princípio de funcionamento

- Conteúdo do documento embutido no HTML como `const SECTIONS = [...]`
- Busca e ranking acontecem 100% no browser (sem roundtrip ao servidor)
- Após primeiro acesso, o service worker cacheia o arquivo — funciona offline
- O formulário MCMV em `/` permanece intocado

---

## 3. Estrutura de Dados

Cada seção é um objeto JavaScript:

```js
{
  id: "string",           // slug kebab-case único
  title: "string",        // título exibido no card
  parent: "string",       // capítulo pai (ex: "5. Vigas")
  badge: "C" | "B" | "N" | "CB", // fonte: Carini, Bastos, NBR, ambos
  tags: ["string"],       // palavras-chave explícitas para busca
  content: "string"       // texto completo da seção (markdown simplificado)
}
```

**~28 seções** mapeadas a partir de `docs/engenharia/referencia-concreto-armado.md`:

| id | title | badge |
|---|---|---|
| `materiais-resistencias` | 1.1 Concreto — Resistências | C |
| `materiais-modulo` | 1.2 Módulo de Elasticidade | C |
| `materiais-diagramas` | 1.3 Diagramas Tensão-Deformação | CB |
| `materiais-reologicas` | 1.4 Retração e Fluência | CB |
| `materiais-aco` | 1.5 Aço CA-25/50/60/70 | CB |
| `materiais-caa` | 1.6 CAA e Cobrimentos | CB |
| `materiais-coeficientes` | 1.7 Coeficientes de Ponderação | N |
| `cargas` | 2. Cargas e Ações | C |
| `predim` | 3. Pré-dimensionamento | C |
| `lajes-vao` | 4.1–4.2 Vão Efetivo e Casos | C |
| `lajes-momentos` | 4.3 Momentos Fletores (tabela) | C |
| `lajes-armadura` | 4.4 ELU — Armadura | C |
| `lajes-flecha` | 4.5 ELS — Flecha | C |
| `vigas-fundamento` | 5.1 Fundamento Físico — Bastos | B |
| `vigas-vao` | 5.2 Vão Efetivo | N |
| `vigas-cargas` | 5.3 Cargas na Viga | C |
| `vigas-modelo` | 5.4 Modelo Estrutural Contínua | CB |
| `vigas-esforcos` | 5.5 Esforços (modelos simples) | C |
| `vigas-cortante` | 5.6 ELU — Cisalhamento | CB |
| `vigas-flexao` | 5.7 ELU — Flexão | C |
| `vigas-flecha` | 5.8 ELS — Flecha (Branson) | C |
| `vigas-fissuracao` | 5.9 ELS — Fissuração | C |
| `pilares-esbeltez` | 6.1 Esbeltez | C |
| `pilares-momentos` | 6.2 Distribuição de Momentos | C |
| `pilares-excentricidades` | 6.3 Excentricidades | C |
| `pilares-armadura` | 6.4 Armadura | C |
| `torcao` | 7. Torção (completo) | B |
| `detalhamento` | 8. Detalhamento | C |
| `sintese` | 9. Síntese Carini × Bastos | CB |

---

## 4. Algoritmo de Busca

### Pontuação por seção

```
score = 0

para cada termo em query.split(" "):
  título contém termo (case-insensitive)  → score += 3
  tag exata == termo                      → score += 2
  tag contém termo (parcial)              → score += 1
  conteúdo contém termo                  → score += min(ocorrências, 3)
```

### Classificação dos resultados

| Score | Classe | Exibição |
|---|---|---|
| ≥ 3 | PRIMARY | Card expandido, borda azul `#0056b3` |
| 1–2 | SECONDARY | Card colapsado, borda cinza, clique para abrir |
| 0 | — | Oculto |

### Comportamento

- **Debounce 300ms** — busca dispara 300ms após parar de digitar
- **Multi-termo:** "fck C25" busca ambos os termos; scores somados por seção
- **Query vazia:** exibe todas as seções agrupadas por capítulo, todas colapsadas
- **Sem resultado:** mensagem "Nenhuma seção encontrada para `<query>`"

---

## 5. Interface

### Layout (mobile-first, 1 coluna)

```
┌─────────────────────────────────┐
│  🏗 D'LIMA Referência Técnica   │  ← header fixo, #0056b3
├─────────────────────────────────┤
│  🔍 [ buscar...                ]│  ← input sticky
├─────────────────────────────────┤
│  PRIMÁRIO                       │
│  ┌─────────────────────────────┐│
│  │ 1.1 Concreto — Resistências ││  ← expandido por padrão
│  │ [C]  Materiais              ││  ← badge fonte + capítulo
│  │ fck = fcm − 1,65s ...       ││
│  └─────────────────────────────┘│
│  SECUNDÁRIO                     │
│  ┌─────────────────────────────┐│
│  │ ▶ 5.7 ELU — Flexão    [C]  ││  ← colapsado
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

### Badges de fonte

| Badge | Cor | Significado |
|---|---|---|
| `C` | azul escuro | Carini (como calcular) |
| `B` | verde | Bastos (por que funciona) |
| `N` | cinza | NBR (normativo) |
| `CB` | azul + verde (lado a lado) | Ambos |

### Renderização do conteúdo

Markdown simplificado via replace no JS (sem biblioteca):
- ` ```...``` ` → `<pre><code>` com fundo `#f8f8f8`
- `**texto**` → `<strong>`
- `| col |` → `<table>` responsiva com scroll horizontal
- Quebras de linha preservadas

### Botão de instalação PWA

- Aparece no header quando browser dispara `beforeinstallprompt`
- Texto: "⬇ Instalar"
- No iOS: tooltip "No Safari: Compartilhar → Adicionar à Tela de Início"

---

## 6. PWA

### `static/manifest.json` (substituição completa)

```json
{
  "name": "D'LIMA Referência Técnica",
  "short_name": "Referência",
  "description": "Referência de concreto armado NBR 6118 — Carini + Bastos",
  "start_url": "/referencia",
  "display": "standalone",
  "theme_color": "#0056b3",
  "background_color": "#f4f4f9",
  "icons": [
    { "src": "/static/minha-logo.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/static/minha-logo.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### `static/sw.js` (substituição completa)

```js
const CACHE_NAME = 'dlima-ref-v1'
const ASSETS = ['/', '/referencia', '/static/manifest.json', '/static/minha-logo.png']

// install: cacheia assets
self.addEventListener('install', e => e.waitUntil(
  caches.open(CACHE_NAME).then(c => c.addAll(ASSETS))
))

// fetch: cache-first
self.addEventListener('fetch', e => e.respondWith(
  caches.match(e.request).then(r => r || fetch(e.request))
))

// activate: remove caches antigos
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(keys => Promise.all(
    keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
  ))
))
```

### Meta tags em `referencia.html`

```html
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#0056b3">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
```

---

## 7. Rotas Flask

```python
# app.py — adicionar após a rota /cadastro
@app.route('/referencia')
def referencia():
    return render_template('referencia.html')
```

---

## 8. Fora do Escopo

- Autenticação / login
- Busca fuzzy (typo tolerance) — busca literal é suficiente para termos técnicos
- Edição do conteúdo pelo usuário
- Sincronização de conteúdo com o servidor após instalação
- Versioning automático do service worker (incrementar `CACHE_NAME` manualmente a cada atualização)

---

## 9. Critérios de Aceite

- [ ] `GET /referencia` retorna 200
- [ ] Digitar "fck" retorna seção 1.1 como PRIMARY e ≥3 seções SECONDARY
- [ ] Digitar "torção" retorna seção 7 como PRIMARY
- [ ] Digitar "fck C25" retorna intersecção rankeada
- [ ] Query vazia exibe todas as seções agrupadas por capítulo
- [ ] Conteúdo com fórmulas (`<pre>`) renderiza corretamente no mobile
- [ ] App instalável no Chrome Android (banner aparece)
- [ ] Após instalado, funciona sem internet
- [ ] Página MCMV em `/` permanece intocada
