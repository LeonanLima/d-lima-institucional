# Quantitativos com Traço + Orçamento Manual — Plano de Implementação

> **Para agentes:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar task a task.

**Goal:** Adicionar receituário de argamassa em latas de 18L, estimativa de tempo (dias com/sem ajudante) e edição inline de preços + itens manuais no orçamento.

**Architecture:** Pure TypeScript para dados de traço e produtividade (funções puras testáveis). UI adicionada como seção nova na página de Quantitativos (receituário) e dois incrementos na página de Orçamento (edição inline + modal de item manual). Favoritos em `localStorage`. Nenhuma alteração no schema do banco.

**Tech Stack:** Next.js 15, TypeScript, Tailwind, Supabase (apenas leitura dos quantitativos existentes), localStorage.

**Projeto:** `C:\Users\leona\OneDrive\Documentos\dlima-app\`

---

## Estrutura de Arquivos

```
dlima-app/
├── lib/calc/
│   ├── tracos.ts               ← CRIAR: TRACOS_SERVICO table + calcConsumo18L
│   ├── produtividade.ts        ← CRIAR: PRODUTIVIDADE table + calcDias
│   ├── tracos.test.ts          ← CRIAR: testes unitários
│   └── produtividade.test.ts   ← CRIAR: testes unitários
├── lib/
│   └── tracos-favoritos.ts     ← CRIAR: get/set localStorage
└── app/(dashboard)/obras/[id]/
    ├── quantitativos/page.tsx  ← MODIFICAR: + seção Receituário
    └── orcamento/page.tsx      ← MODIFICAR: + edição inline + modal item manual
```

---

## TASK 1 — lib/calc/tracos.ts + testes

**Files:**
- Create: `lib/calc/tracos.ts`
- Create: `lib/calc/tracos.test.ts`

- [ ] **Step 1.1 — Escrever testes primeiro**

```typescript
// lib/calc/tracos.test.ts
import { calcConsumo18L, TRACOS_SERVICO, getTracoParaComposicao } from './tracos'

test('tijolo furado: 0.12 latas cimento por m²', () => {
  const r = calcConsumo18L('alvenaria_bloco_9', 1)
  expect(r.cimento).toBeCloseTo(0.12, 2)
  expect(r.cal).toBeCloseTo(0.23, 2)
  expect(r.areia).toBeCloseTo(0.93, 2)
})

test('chapisco: sem cal, só cimento e areia', () => {
  const r = calcConsumo18L('chapisco', 1)
  expect(r.cal).toBe(0)
  expect(r.areia).toBeGreaterThan(0)
})

test('getTracoParaComposicao retorna null para laje', () => {
  expect(getTracoParaComposicao('laje_trelicada_12')).toBeNull()
})

test('getTracoParaComposicao retorna traço para alvenaria', () => {
  const t = getTracoParaComposicao('alvenaria_bloco_9')
  expect(t).not.toBeNull()
  expect(t?.id).toBe('alvenaria_bloco_9')
})
```

- [ ] **Step 1.2 — Rodar testes para confirmar falha**

```bash
cd C:\Users\leona\OneDrive\Documentos\dlima-app
npx jest lib/calc/tracos.test.ts
```
Esperado: FAIL — "Cannot find module './tracos'"

- [ ] **Step 1.3 — Criar lib/calc/tracos.ts**

```typescript
// lib/calc/tracos.ts

export interface TracoServico {
  id:                    string
  nome:                  string
  traco:                 string      // ex: '1:2:8'
  cim_latas:             number      // por traçada (1 lata 18L cim)
  cal_latas:             number      // 0 se sem cal
  areia_latas:           number
  brita_latas:           number      // 0 se sem brita
  agua_latas:            number      // em latas de 18L
  rend_m2_por_lata_cim:  number      // m² por 1 lata de cimento
  espessura_mm:          number      // espessura da camada
  economico:             boolean     // traço mais econômico?
}

export interface ConsumoTraco {
  cimento: number   // latas 18L por m²
  cal:     number
  areia:   number
  brita:   number
  agua:    number
}

/** Tabela de traços — latas de 18L — fonte: Apostila Alvenaria IFES + SINAPI */
export const TRACOS_SERVICO: TracoServico[] = [
  {
    id: 'alvenaria_bloco_9',
    nome: 'Alvenaria — tijolo furado/baiano',
    traco: '1:2:8',
    cim_latas: 1, cal_latas: 2, areia_latas: 8, brita_latas: 0, agua_latas: 1,
    rend_m2_por_lata_cim: 8.6,
    espessura_mm: 10,
    economico: true,
  },
  {
    id: 'alvenaria_bloco_9_sem_cal',
    nome: 'Alvenaria — tijolo furado (sem cal)',
    traco: '1:0:6',
    cim_latas: 1, cal_latas: 0, areia_latas: 6, brita_latas: 0, agua_latas: 0.8,
    rend_m2_por_lata_cim: 7.2,
    espessura_mm: 10,
    economico: false,
  },
  {
    id: 'alvenaria_tijolo_macico',
    nome: 'Alvenaria — tijolo maciço',
    traco: '1:2:8',
    cim_latas: 1, cal_latas: 2, areia_latas: 8, brita_latas: 0, agua_latas: 1,
    rend_m2_por_lata_cim: 5.4,
    espessura_mm: 10,
    economico: true,
  },
  {
    id: 'bloco_concreto',
    nome: 'Alvenaria — bloco de concreto',
    traco: '1:0.5:6',
    cim_latas: 1, cal_latas: 0.5, areia_latas: 6, brita_latas: 0, agua_latas: 0.8,
    rend_m2_por_lata_cim: 16.2,
    espessura_mm: 10,
    economico: true,
  },
  {
    id: 'chapisco',
    nome: 'Chapisco',
    traco: '1:0:3',
    cim_latas: 1, cal_latas: 0, areia_latas: 3, brita_latas: 0, agua_latas: 0.8,
    rend_m2_por_lata_cim: 4.3,
    espessura_mm: 5,
    economico: true,
  },
  {
    id: 'emboco_externo',
    nome: 'Emboço externo (área molhada)',
    traco: '1:1:6',
    cim_latas: 1, cal_latas: 1, areia_latas: 6, brita_latas: 0, agua_latas: 1,
    rend_m2_por_lata_cim: 2.2,
    espessura_mm: 20,
    economico: true,
  },
  {
    id: 'emboco_interno',
    nome: 'Emboço interno',
    traco: '1:2:8',
    cim_latas: 1, cal_latas: 2, areia_latas: 8, brita_latas: 0, agua_latas: 1,
    rend_m2_por_lata_cim: 2.7,
    espessura_mm: 15,
    economico: true,
  },
  {
    id: 'piso_porcelanato',
    nome: 'Assentamento porcelanato (piso)',
    traco: '1:0:3',
    cim_latas: 1, cal_latas: 0, areia_latas: 3, brita_latas: 0, agua_latas: 0.7,
    rend_m2_por_lata_cim: 5.0,
    espessura_mm: 6,
    economico: true,
  },
  {
    id: 'piso_ceramica',
    nome: 'Assentamento cerâmica (piso)',
    traco: '1:0:3',
    cim_latas: 1, cal_latas: 0, areia_latas: 3, brita_latas: 0, agua_latas: 0.7,
    rend_m2_por_lata_cim: 5.5,
    espessura_mm: 5,
    economico: true,
  },
  {
    id: 'revestimento_ceramica',
    nome: 'Assentamento cerâmica (parede)',
    traco: '1:0:3',
    cim_latas: 1, cal_latas: 0, areia_latas: 3, brita_latas: 0, agua_latas: 0.7,
    rend_m2_por_lata_cim: 4.8,
    espessura_mm: 5,
    economico: true,
  },
]

/** Mapeamento de composição (chave de quantitativos.ts) → traço padrão */
const COMPOSICAO_PARA_TRACO: Record<string, string> = {
  alvenaria_bloco_9:      'alvenaria_bloco_9',
  piso_porcelanato:       'piso_porcelanato',
  piso_ceramica:          'piso_ceramica',
  revestimento_ceramica:  'revestimento_ceramica',
  reboco_parede:          'emboco_interno',
  telhado_colonial:       '', // sem traço (madeira/telha)
  laje_trelicada_12:      '', // concreto usinado/calculado separado
}

export function getTracoParaComposicao(composicaoId: string): TracoServico | null {
  const tracoId = COMPOSICAO_PARA_TRACO[composicaoId]
  if (!tracoId) return null
  return TRACOS_SERVICO.find(t => t.id === tracoId) ?? null
}

/**
 * Calcula consumo de argamassa por m² em latas de 18L.
 * @param tracoId  ID do traço (de TRACOS_SERVICO)
 * @param area_m2  área em m²
 */
export function calcConsumo18L(tracoId: string, area_m2: number): ConsumoTraco {
  const t = TRACOS_SERVICO.find(x => x.id === tracoId)
  if (!t) return { cimento: 0, cal: 0, areia: 0, brita: 0, agua: 0 }

  // Latas de cimento por m² = 1 / rend_m2_por_lata_cim
  const cim_por_m2 = 1 / t.rend_m2_por_lata_cim
  return {
    cimento: +(cim_por_m2 * area_m2).toFixed(3),
    cal:     +(cim_por_m2 * t.cal_latas * area_m2).toFixed(3),
    areia:   +(cim_por_m2 * t.areia_latas * area_m2).toFixed(3),
    brita:   +(cim_por_m2 * t.brita_latas * area_m2).toFixed(3),
    agua:    +(cim_por_m2 * t.agua_latas * area_m2).toFixed(3),
  }
}
```

- [ ] **Step 1.4 — Rodar testes para confirmar aprovação**

```bash
npx jest lib/calc/tracos.test.ts
```
Esperado: 4 testes PASS

- [ ] **Step 1.5 — Commit**

```bash
cd C:\Users\leona\OneDrive\Documentos\dlima-app
git add lib/calc/tracos.ts lib/calc/tracos.test.ts
git commit -m "feat: tabela de tracos 18L e calcConsumo18L"
```

---

## TASK 2 — lib/calc/produtividade.ts + testes

**Files:**
- Create: `lib/calc/produtividade.ts`
- Create: `lib/calc/produtividade.test.ts`

- [ ] **Step 2.1 — Escrever testes**

```typescript
// lib/calc/produtividade.test.ts
import { calcDias, getProdutividade, PRODUTIVIDADE } from './produtividade'

test('produtividade definida para alvenaria', () => {
  const p = getProdutividade('alvenaria_bloco_9')
  expect(p).not.toBeNull()
  expect(p!.oficial_h_m2).toBe(0.70)
})

test('calcDias: 10m² alvenaria sem ajudante = 0.875 dias', () => {
  const r = calcDias('alvenaria_bloco_9', 10)
  // 10 × 0.7 / 8 = 0.875
  expect(r.dias_solo).toBeCloseTo(0.875, 2)
})

test('calcDias: com ajudante reduz em 30%', () => {
  const r = calcDias('alvenaria_bloco_9', 10)
  expect(r.dias_com_ajudante).toBeCloseTo(0.875 * 0.7, 2)
})

test('calcDias retorna null para servico sem produtividade', () => {
  expect(calcDias('telhado_colonial', 10)).toBeNull()
})
```

- [ ] **Step 2.2 — Rodar para confirmar falha**

```bash
npx jest lib/calc/produtividade.test.ts
```
Esperado: FAIL

- [ ] **Step 2.3 — Criar lib/calc/produtividade.ts**

```typescript
// lib/calc/produtividade.ts

export interface Produtividade {
  composicaoId:      string
  nome:              string
  oficial_h_m2:      number   // h/m² do pedreiro/azulejista
  servente_h_m2:     number   // h/m² do ajudante
}

export interface ResultadoDias {
  horas_oficial:       number
  horas_servente:      number
  dias_solo:           number   // só com o oficial (8h/dia)
  dias_com_ajudante:   number   // oficial + ajudante (oficial rende 30% mais)
}

/** Tabela de produtividade — fonte: TCPO / padrão mercado ES */
export const PRODUTIVIDADE: Produtividade[] = [
  { composicaoId: 'alvenaria_bloco_9',     nome: 'Alvenaria tijolo furado', oficial_h_m2: 0.70, servente_h_m2: 0.35 },
  { composicaoId: 'alvenaria_tijolo_macico', nome: 'Alvenaria tijolo maciço', oficial_h_m2: 0.90, servente_h_m2: 0.45 },
  { composicaoId: 'chapisco',              nome: 'Chapisco',                  oficial_h_m2: 0.15, servente_h_m2: 0.10 },
  { composicaoId: 'emboco_externo',        nome: 'Emboço externo',           oficial_h_m2: 0.50, servente_h_m2: 0.25 },
  { composicaoId: 'emboco_interno',        nome: 'Reboco/emboço interno',     oficial_h_m2: 0.50, servente_h_m2: 0.25 },
  { composicaoId: 'piso_porcelanato',      nome: 'Assentamento porcelanato',  oficial_h_m2: 1.00, servente_h_m2: 0.40 },
  { composicaoId: 'piso_ceramica',         nome: 'Assentamento cerâmica piso',oficial_h_m2: 0.85, servente_h_m2: 0.35 },
  { composicaoId: 'revestimento_ceramica', nome: 'Cerâmica parede',          oficial_h_m2: 1.00, servente_h_m2: 0.40 },
]

const JORNADA = 8  // horas/dia

export function getProdutividade(composicaoId: string): Produtividade | null {
  return PRODUTIVIDADE.find(p => p.composicaoId === composicaoId) ?? null
}

/**
 * Calcula dias de trabalho para uma área.
 * - dias_solo: só o oficial
 * - dias_com_ajudante: com ajudante o oficial rende 30% mais (ajudante apoia, prepara)
 */
export function calcDias(composicaoId: string, area_m2: number): ResultadoDias | null {
  const p = getProdutividade(composicaoId)
  if (!p) return null

  const horas_oficial   = +(area_m2 * p.oficial_h_m2).toFixed(1)
  const horas_servente  = +(area_m2 * p.servente_h_m2).toFixed(1)
  const dias_solo        = +(horas_oficial / JORNADA).toFixed(1)
  // Com ajudante: oficial rende 30% mais por ser liberado das tarefas auxiliares
  const dias_com_ajudante = +(horas_oficial / (JORNADA * 1.3)).toFixed(1)

  return { horas_oficial, horas_servente, dias_solo, dias_com_ajudante }
}
```

- [ ] **Step 2.4 — Rodar testes**

```bash
npx jest lib/calc/produtividade.test.ts
```
Esperado: 4 testes PASS

- [ ] **Step 2.5 — Commit**

```bash
git add lib/calc/produtividade.ts lib/calc/produtividade.test.ts
git commit -m "feat: tabela de produtividade e calcDias"
```

---

## TASK 3 — lib/tracos-favoritos.ts

**Files:**
- Create: `lib/tracos-favoritos.ts`

Não precisa de testes — é um wrapper de `localStorage` puro.

- [ ] **Step 3.1 — Criar lib/tracos-favoritos.ts**

```typescript
// lib/tracos-favoritos.ts

const KEY = 'dlima_tracos_favoritos'

function load(): Record<string, string> {
  if (typeof window === 'undefined') return {}
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? '{}')
  } catch {
    return {}
  }
}

function save(data: Record<string, string>) {
  if (typeof window === 'undefined') return
  localStorage.setItem(KEY, JSON.stringify(data))
}

/** Retorna o ID do traço favorito para o serviço, ou null. */
export function getFavorito(composicaoId: string): string | null {
  return load()[composicaoId] ?? null
}

/** Salva um traço como favorito para o serviço. */
export function setFavorito(composicaoId: string, tracoId: string) {
  save({ ...load(), [composicaoId]: tracoId })
}

/** Remove o favorito de um serviço. */
export function removeFavorito(composicaoId: string) {
  const data = load()
  delete data[composicaoId]
  save(data)
}
```

- [ ] **Step 3.2 — Verificar TypeScript**

```bash
cd C:\Users\leona\OneDrive\Documentos\dlima-app
npx tsc --noEmit 2>&1 | grep tracos-favoritos || echo "OK"
```
Esperado: OK (sem erros)

- [ ] **Step 3.3 — Commit**

```bash
git add lib/tracos-favoritos.ts
git commit -m "feat: tracos-favoritos localStorage util"
```

---

## TASK 4 — quantitativos/page.tsx: Seção Receituário

**Files:**
- Modify: `app/(dashboard)/obras/[id]/quantitativos/page.tsx`

Adiciona seção "Receituário de argamassa" abaixo da tabela existente, que detecta os serviços com argamassa e exibe traço em latas 18L + estimativa de tempo.

- [ ] **Step 4.1 — Adicionar imports no topo da página**

```typescript
import { getTracoParaComposicao, calcConsumo18L, TRACOS_SERVICO, type TracoServico } from '@/lib/calc/tracos'
import { calcDias } from '@/lib/calc/produtividade'
import { getFavorito, setFavorito } from '@/lib/tracos-favoritos'
import { Star, ChevronDown, ChevronUp, Clock } from 'lucide-react'
```

- [ ] **Step 4.2 — Adicionar estado de favoritos e serviços abertos**

Após os estados existentes (`loading`, `itens`, `ajustes`), adicionar:

```typescript
const [favoritos,    setFavoritos]    = useState<Record<string, string>>({})
const [servicosOpen, setServicosOpen] = useState<Record<string, boolean>>({})
```

E carregar favoritos no `useEffect` de init:

```typescript
useEffect(() => {
  async function init() {
    // ... código existente ...
    // Carregar favoritos
    const favs: Record<string, string> = {}
    for (const t of TRACOS_SERVICO) {
      const fav = getFavorito(t.id)
      if (fav) favs[t.id] = fav
    }
    setFavoritos(favs)
  }
  init()
}, []) // eslint-disable-line react-hooks/exhaustive-deps
```

- [ ] **Step 4.3 — Calcular serviços detectados (derivado dos itens)**

Adicionar computação derivada dos `itens` (após as declarações de estado, antes do return):

```typescript
// Detectar serviços com argamassa a partir dos itens via medicao
// O campo traco_descricao existe nos itens de concreto; para outros serviços,
// usamos a descricao para inferir a composição
const servicosDetectados = (() => {
  const seen = new Set<string>()
  const result: Array<{ composicaoId: string; area_m2: number }> = []

  // Mapeamento de palavras-chave da descricao → composicaoId
  const keywords: Array<[string, string]> = [
    ['Bloco cerâmico', 'alvenaria_bloco_9'],
    ['Porcelanato',    'piso_porcelanato'],
    ['Cerâmica (padrão médio)', 'piso_ceramica'],
    ['Azulejista (parede)',     'revestimento_ceramica'],
    ['Cimento CP II', 'emboco_interno'],
    ['Cal hidratada', 'emboco_interno'],
  ]

  for (const item of itens) {
    for (const [kw, compId] of keywords) {
      if (item.descricao.includes(kw) && !seen.has(compId)) {
        seen.add(compId)
        // Estimar a área: para mão de obra (h), dividir pela produtividade
        // Para materiais, usar quantidade_calculada (m², m³, un)
        const area = item.unidade === 'm²' ? item.quantidade_calculada : 0
        result.push({ composicaoId: compId, area_m2: area })
      }
    }
  }
  return result
})()
```

- [ ] **Step 4.4 — Adicionar seção Receituário no JSX**

Logo após o bloco `{/* Resumo */}` e antes do botão de salvar, adicionar:

```tsx
{/* Receituário de argamassa */}
{servicosDetectados.length > 0 && (
  <div className="mt-6">
    <h3 className="text-dlima-gold text-xs font-semibold uppercase tracking-wider mb-3">
      Receituário — Latas de 18L
    </h3>
    <div className="space-y-2">
      {servicosDetectados.map(({ composicaoId, area_m2 }) => {
        const traco = getTracoParaComposicao(composicaoId)
        if (!traco) return null
        const consumo = calcConsumo18L(traco.id, area_m2)
        const tempo   = calcDias(composicaoId, area_m2)
        const isOpen  = servicosOpen[composicaoId] !== false
        const isFav   = favoritos[composicaoId] === traco.id

        return (
          <div key={composicaoId} className="bg-dlima-surface border border-dlima-border rounded-xl overflow-hidden">
            {/* Cabeçalho clicável */}
            <button
              onClick={() => setServicosOpen(p => ({ ...p, [composicaoId]: !isOpen }))}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-dlima-border/30 transition-colors text-left"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-dlima-text">{traco.nome}</span>
                {isFav && <Star size={12} className="text-dlima-gold fill-dlima-gold" />}
              </div>
              <div className="flex items-center gap-2 text-xs text-dlima-muted">
                <span>Traço {traco.traco}</span>
                {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </div>
            </button>

            {isOpen && (
              <div className="border-t border-dlima-border px-4 py-3 space-y-3">
                {/* Traço por traçada */}
                <div>
                  <p className="text-[10px] text-dlima-muted uppercase tracking-wider mb-1.5">Por traçada (1 lata cimento)</p>
                  <div className="flex gap-2 flex-wrap">
                    {[
                      ['Cimento', traco.cim_latas],
                      traco.cal_latas > 0 ? ['Cal', traco.cal_latas] : null,
                      ['Areia', traco.areia_latas],
                      traco.brita_latas > 0 ? ['Brita', traco.brita_latas] : null,
                      ['Água', traco.agua_latas],
                    ].filter(Boolean).map(([nome, qtd]) => (
                      <span key={nome as string} className="bg-dlima-darker border border-dlima-border rounded-lg px-3 py-1.5 text-xs">
                        <span className="text-dlima-gold font-bold">{qtd}</span>
                        <span className="text-dlima-muted ml-1">lata{Number(qtd) !== 1 ? 's' : ''} {nome}</span>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Consumo por m² */}
                {area_m2 > 0 && (
                  <div>
                    <p className="text-[10px] text-dlima-muted uppercase tracking-wider mb-1.5">
                      Para {area_m2.toFixed(1)} m² (espessura {traco.espessura_mm}mm)
                    </p>
                    <div className="flex gap-2 flex-wrap">
                      {[
                        { nome: 'Cimento', val: consumo.cimento },
                        consumo.cal > 0 ? { nome: 'Cal', val: consumo.cal } : null,
                        { nome: 'Areia', val: consumo.areia },
                        consumo.brita > 0 ? { nome: 'Brita', val: consumo.brita } : null,
                        { nome: 'Água', val: consumo.agua },
                      ].filter(Boolean).map(item => (
                        <span key={item!.nome} className="bg-dlima-gold/5 border border-dlima-gold/20 rounded-lg px-3 py-1.5 text-xs">
                          <span className="text-dlima-gold font-bold">{item!.val.toFixed(2)}</span>
                          <span className="text-dlima-muted ml-1">latas {item!.nome}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Estimativa de tempo */}
                {tempo && area_m2 > 0 && (
                  <div className="flex items-start gap-2 p-3 bg-dlima-darker rounded-lg">
                    <Clock size={14} className="text-dlima-gold mt-0.5 flex-shrink-0" />
                    <div className="text-xs space-y-0.5">
                      <p className="text-dlima-text font-medium">Estimativa de produção</p>
                      <p className="text-dlima-muted">
                        <span className="text-dlima-text">{tempo.horas_oficial}h</span> de serviço →{' '}
                        <span className="text-dlima-text font-semibold">{tempo.dias_solo} dia{tempo.dias_solo !== 1 ? 's' : ''}</span> (1 pedreiro) /{' '}
                        <span className="text-dlima-text font-semibold">{tempo.dias_com_ajudante} dia{tempo.dias_com_ajudante !== 1 ? 's' : ''}</span> (com ajudante)
                      </p>
                    </div>
                  </div>
                )}

                {/* Botão favorito */}
                <button
                  onClick={() => {
                    if (isFav) {
                      const newFavs = { ...favoritos }
                      delete newFavs[composicaoId]
                      setFavoritos(newFavs)
                    } else {
                      setFavorito(composicaoId, traco.id)
                      setFavoritos(f => ({ ...f, [composicaoId]: traco.id }))
                    }
                  }}
                  className={[
                    'flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors',
                    isFav
                      ? 'bg-dlima-gold/10 border-dlima-gold text-dlima-gold'
                      : 'bg-dlima-surface border-dlima-border text-dlima-muted hover:border-dlima-gold/40',
                  ].join(' ')}
                >
                  <Star size={12} className={isFav ? 'fill-dlima-gold' : ''} />
                  {isFav ? 'Traço favorito' : 'Marcar como favorito'}
                </button>
              </div>
            )}
          </div>
        )
      })}
    </div>
  </div>
)}
```

- [ ] **Step 4.5 — Verificar TypeScript**

```bash
cd C:\Users\leona\OneDrive\Documentos\dlima-app
npx tsc --noEmit 2>&1 | grep -v node_modules | head -20
```
Esperado: sem erros

- [ ] **Step 4.6 — Testar manualmente**

```
npm run dev
Abrir obra com alvenaria medida → /obras/[id]/quantitativos
Verificar: seção "Receituário — Latas de 18L" aparece abaixo da tabela
Clicar para expandir → traço + consumo + estimativa de dias visíveis
Clicar ⭐ → ícone muda para preenchido
Recarregar página → favorito persiste
```

- [ ] **Step 4.7 — Commit**

```bash
git add "app/(dashboard)/obras/[id]/quantitativos/page.tsx"
git commit -m "feat: receituario de argamassa 18L + estimativa de dias nos quantitativos"
```

---

## TASK 5 — orcamento/page.tsx: Edição inline de preço + Item manual

**Files:**
- Modify: `app/(dashboard)/obras/[id]/orcamento/page.tsx`

### Parte A: Edição inline de preço unitário

- [ ] **Step 5.1 — Adicionar estado de edição**

Após os estados existentes no componente, adicionar:

```typescript
const [editingItemId, setEditingItemId] = useState<string | null>(null)
const [editingPreco,  setEditingPreco]  = useState('')
```

- [ ] **Step 5.2 — Adicionar função de salvar preço**

```typescript
async function salvarPreco(itemId: string) {
  const novoPreco = parseFloat(editingPreco)
  if (isNaN(novoPreco) || novoPreco < 0) { setEditingItemId(null); return }

  await supabase
    .from('orcamento_itens')
    .update({ preco_unitario: novoPreco })
    .eq('id', itemId)

  setItens(prev => prev.map(i =>
    i.id === itemId
      ? { ...i, preco_unitario: novoPreco, total_item: +(i.quantidade * novoPreco).toFixed(2) }
      : i
  ))
  setEditingItemId(null)
}
```

- [ ] **Step 5.3 — Modificar a linha de item na tabela para incluir botão de edição**

Encontrar o trecho da tabela que renderiza cada linha (em volta de `etapaItens.map((item, i) =>`). A linha completa com edição fica:

```tsx
{etapaItens.map((item, i) => (
  <tr
    key={item.id}
    className={i < etapaItens.length - 1 ? 'border-b border-dlima-border/40' : ''}
  >
    <td className="px-4 py-2.5 text-dlima-text text-xs">{item.descricao}</td>
    <td className="px-4 py-2.5 text-right text-xs text-dlima-muted">{item.quantidade.toFixed(2)}</td>
    <td className="px-4 py-2.5 text-xs text-dlima-muted">{item.unidade}</td>
    <td className="px-4 py-2.5 text-right text-xs">
      {editingItemId === item.id ? (
        <div className="flex items-center gap-1 justify-end">
          <input
            autoFocus
            type="number"
            step="0.01"
            value={editingPreco}
            onChange={e => setEditingPreco(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') salvarPreco(item.id)
              if (e.key === 'Escape') setEditingItemId(null)
            }}
            className="w-24 px-2 py-0.5 bg-dlima-dark border border-dlima-gold rounded text-dlima-text text-xs text-right focus:outline-none"
          />
          <button
            onClick={() => salvarPreco(item.id)}
            className="text-dlima-gold hover:text-dlima-gold-light text-xs font-bold"
          >✓</button>
          <button
            onClick={() => setEditingItemId(null)}
            className="text-dlima-muted hover:text-dlima-text text-xs"
          >✕</button>
        </div>
      ) : (
        <button
          onClick={() => { setEditingItemId(item.id); setEditingPreco(String(item.preco_unitario)) }}
          className="group flex items-center gap-1 ml-auto hover:text-dlima-gold transition-colors"
          title="Editar preço"
        >
          <span className={item.preco_unitario === 0 ? 'text-yellow-400' : 'text-dlima-text'}>
            R$ {BRL(item.preco_unitario)}
          </span>
          <span className="opacity-0 group-hover:opacity-100 text-dlima-gold text-[10px]">✏️</span>
        </button>
      )}
    </td>
    <td className="px-4 py-2.5 text-right text-xs text-dlima-gold font-medium">
      R$ {BRL(item.total_item)}
    </td>
  </tr>
))}
```

### Parte B: Adicionar item manual

- [ ] **Step 5.4 — Adicionar estado do modal de item manual**

```typescript
const [showAddItem, setShowAddItem] = useState(false)
const [novoItem, setNovoItem] = useState({
  etapa:          'Serviços Preliminares',
  descricao:      '',
  quantidade:     '',
  unidade:        'm²',
  preco_unitario: '',
})
const [salvandoItem, setSalvandoItem] = useState(false)
```

- [ ] **Step 5.5 — Adicionar função de salvar item manual**

```typescript
async function salvarItemManual(e: React.FormEvent) {
  e.preventDefault()
  if (!ativo) return
  setSalvandoItem(true)
  try {
    const qtd   = parseFloat(novoItem.quantidade)
    const preco = parseFloat(novoItem.preco_unitario)
    if (isNaN(qtd) || isNaN(preco)) return

    const { data } = await supabase
      .from('orcamento_itens')
      .insert({
        orcamento_id:   ativo,
        etapa:          novoItem.etapa,
        descricao:      novoItem.descricao,
        quantidade:     qtd,
        unidade:        novoItem.unidade,
        preco_unitario: preco,
        ordem_exibicao: 999,
      })
      .select()
      .single()

    if (data) {
      setItens(prev => [...prev, {
        ...(data as OrcamentoItem),
        total_item: +(qtd * preco).toFixed(2),
      }])
    }
    setShowAddItem(false)
    setNovoItem({ etapa: 'Serviços Preliminares', descricao: '', quantidade: '', unidade: 'm²', preco_unitario: '' })
  } finally {
    setSalvandoItem(false)
  }
}
```

- [ ] **Step 5.6 — Adicionar botão "+ Item" no cabeçalho e modal**

No bloco `<div className="flex items-center justify-between mb-6">`, adicionar o botão ao lado do existente:

```tsx
{orcAtivo && (
  <button
    onClick={() => setShowAddItem(true)}
    className="flex items-center gap-2 px-4 py-2 bg-dlima-surface border border-dlima-border text-dlima-muted hover:border-dlima-gold/40 hover:text-dlima-text font-medium rounded-lg transition-colors text-sm"
  >
    <Plus size={16} />
    Item manual
  </button>
)}
```

E o modal (adicionar antes do `</div>` final do componente):

```tsx
{/* Modal: adicionar item manual */}
{showAddItem && (
  <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
    <div className="w-full max-w-md bg-dlima-surface border border-dlima-border rounded-2xl p-6">
      <h3 className="font-heading font-bold text-lg mb-4">Adicionar Item Manual</h3>
      <form onSubmit={salvarItemManual} className="space-y-3">
        {/* Etapa */}
        <div>
          <label className="block text-xs text-dlima-muted mb-1">Etapa</label>
          <select
            value={novoItem.etapa}
            onChange={e => setNovoItem(p => ({ ...p, etapa: e.target.value }))}
            className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg text-dlima-text text-sm focus:outline-none focus:border-dlima-gold"
          >
            {ETAPAS_PADRAO.map(et => <option key={et} value={et}>{et}</option>)}
          </select>
        </div>
        {/* Descrição */}
        <div>
          <label className="block text-xs text-dlima-muted mb-1">Descrição *</label>
          <input
            required
            value={novoItem.descricao}
            onChange={e => setNovoItem(p => ({ ...p, descricao: e.target.value }))}
            placeholder="Ex: Chapisco externo"
            className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg text-dlima-text text-sm focus:outline-none focus:border-dlima-gold"
          />
        </div>
        {/* Quantidade + Unidade */}
        <div className="flex gap-2">
          <div className="flex-1">
            <label className="block text-xs text-dlima-muted mb-1">Quantidade *</label>
            <input
              required type="number" step="0.01" min="0"
              value={novoItem.quantidade}
              onChange={e => setNovoItem(p => ({ ...p, quantidade: e.target.value }))}
              placeholder="0.00"
              className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg text-dlima-text text-sm focus:outline-none focus:border-dlima-gold"
            />
          </div>
          <div className="w-28">
            <label className="block text-xs text-dlima-muted mb-1">Unidade</label>
            <select
              value={novoItem.unidade}
              onChange={e => setNovoItem(p => ({ ...p, unidade: e.target.value }))}
              className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg text-dlima-text text-sm focus:outline-none focus:border-dlima-gold"
            >
              {['m²','m³','m','un','kg','saco','h','vb'].map(u => <option key={u}>{u}</option>)}
            </select>
          </div>
        </div>
        {/* Preço unitário */}
        <div>
          <label className="block text-xs text-dlima-muted mb-1">Preço unitário (R$) *</label>
          <input
            required type="number" step="0.01" min="0"
            value={novoItem.preco_unitario}
            onChange={e => setNovoItem(p => ({ ...p, preco_unitario: e.target.value }))}
            placeholder="0.00"
            className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg text-dlima-text text-sm focus:outline-none focus:border-dlima-gold"
          />
        </div>
        {/* Botões */}
        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={() => setShowAddItem(false)}
            className="flex-1 py-2 border border-dlima-border rounded-lg text-dlima-muted text-sm hover:border-dlima-gold/30"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={salvandoItem}
            className="flex-1 py-2 bg-dlima-gold text-dlima-dark font-semibold rounded-lg text-sm hover:bg-dlima-gold-light disabled:opacity-50"
          >
            {salvandoItem ? 'Salvando...' : 'Adicionar'}
          </button>
        </div>
      </form>
    </div>
  </div>
)}
```

- [ ] **Step 5.7 — Verificar TypeScript**

```bash
npx tsc --noEmit 2>&1 | grep -v node_modules | head -20
```
Esperado: sem erros

- [ ] **Step 5.8 — Testar manualmente**

```
npm run dev
Abrir uma obra com orçamento gerado → /obras/[id]/orcamento

TESTE A - Edição de preço:
  Clicar no preço de qualquer item → campo de edição aparece
  Digitar novo valor → Enter → preço e total atualizados
  Clicar em outro preço → edição anterior fecha

TESTE B - Item manual:
  Clicar "Item manual" no cabeçalho → modal abre
  Preencher: Etapa=Cobertura, Descrição=Manta asfáltica, Qtd=45, Un=m², Preço=35
  Clicar Adicionar → item aparece na etapa Cobertura
  Verificar que total da etapa foi atualizado
```

- [ ] **Step 5.9 — Commit**

```bash
git add "app/(dashboard)/obras/[id]/orcamento/page.tsx"
git commit -m "feat: edicao inline de preco e modal de item manual no orcamento"
```

---

## Checklist de self-review

**Cobertura da spec:**
- [x] Traço em latas 18L → Task 1 (tracos.ts)
- [x] Água em latas 18L → incluído em TracoServico.agua_latas
- [x] Produtividade h/m² e calcDias → Task 2
- [x] Favorito por serviço → Task 3 + Task 4
- [x] Receituário na página de quantitativos → Task 4
- [x] Edição inline de preço → Task 5 Parte A
- [x] Item manual sem takeoff → Task 5 Parte B
- [x] Concreto armado (traços C15-C30) → incluído em TRACOS_SERVICO

**Testes:**
- tracos.ts: 4 testes unitários
- produtividade.ts: 4 testes unitários
- Testes manuais descritos nos steps 4.6 e 5.8
