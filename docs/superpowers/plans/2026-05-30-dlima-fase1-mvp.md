# D'LIMA ERP — Fase 1 MVP — Plano de Implementação

> **Para agentes:** Use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para executar task a task.

**Goal:** Criar a plataforma D'LIMA ERP do zero — do orçamento até a PCI Caixa em menos de 30 minutos.

**Architecture:** Next.js 15 App Router + Supabase (Postgres + Auth + Storage). Projeto novo separado do site Flask existente (`d-lima-institucional`). Deploy no Vercel como `app.dlima.eng.br`.

**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS, Supabase, Fabric.js (canvas takeoff), xlsx (export PCI), @react-pdf/renderer (PDF), date-fns.

**Status de escrita deste plano:**
- [x] Parte 1 — Tasks 1-5 (Setup, Schema, Auth, Clientes, Obras)
- [ ] Parte 2 — Tasks 6-10 (Banco Preços, Takeoff, Concreto)
- [ ] Parte 3 — Tasks 11-14 (Quantitativos, Orçamento, Cronograma, PCI + PDF)

---

## Estrutura de Arquivos (Projeto Novo: `dlima-app/`)

```
dlima-app/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx                      ← Dashboard
│   │   ├── clientes/
│   │   │   ├── page.tsx                  ← Lista clientes
│   │   │   └── [id]/page.tsx             ← Detalhe cliente
│   │   ├── obras/
│   │   │   ├── page.tsx                  ← Lista obras
│   │   │   └── [id]/
│   │   │       ├── page.tsx              ← Hub da obra
│   │   │       ├── takeoff/page.tsx      ← Canvas takeoff
│   │   │       ├── quantitativos/page.tsx
│   │   │       ├── orcamento/page.tsx
│   │   │       ├── cronograma/page.tsx
│   │   │       └── pci/page.tsx
│   │   ├── precos/page.tsx               ← Banco de preços
│   │   └── perfil/page.tsx
│   ├── api/
│   │   ├── pdf/route.ts
│   │   └── pci/route.ts
│   ├── globals.css
│   └── layout.tsx
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   └── modal.tsx
│   ├── layout/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   └── mobile-nav.tsx
│   └── takeoff/
│       ├── canvas.tsx
│       ├── calibration.tsx
│       ├── measure-form.tsx
│       └── measurements-list.tsx
├── lib/
│   ├── supabase/
│   │   ├── client.ts
│   │   ├── server.ts
│   │   └── middleware.ts
│   ├── calc/
│   │   ├── concreto.ts
│   │   ├── shoelace.ts
│   │   └── quantitativos.ts
│   └── types.ts
├── middleware.ts
├── next.config.ts
├── tailwind.config.ts
├── public/manifest.json
├── package.json
└── supabase/
    └── migrations/
        └── 001_initial.sql
```

---

## TASK 1 — Setup do Projeto

**Files:**
- Create: `dlima-app/` (diretório raiz do novo projeto)
- Create: `dlima-app/package.json`
- Create: `dlima-app/next.config.ts`
- Create: `dlima-app/tailwind.config.ts`
- Create: `dlima-app/.env.local`

- [ ] **Step 1.1 — Criar o projeto Next.js**

```bash
cd C:\Users\leona\OneDrive\Documentos
npx create-next-app@latest dlima-app \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir=false \
  --import-alias="@/*"
cd dlima-app
```

- [ ] **Step 1.2 — Instalar dependências**

```bash
npm install @supabase/supabase-js @supabase/ssr \
  fabric \
  xlsx \
  @react-pdf/renderer \
  date-fns \
  lucide-react \
  clsx \
  tailwind-merge \
  @types/fabric
```

- [ ] **Step 1.3 — Configurar tailwind.config.ts com cores D'LIMA**

```ts
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        dlima: {
          dark:    '#0F120F',
          darker:  '#090B09',
          surface: '#1A1F1A',
          border:  '#2A302A',
          gold:    '#B89B5E',
          'gold-light': '#D4B978',
          'gold-dark':  '#8A7440',
          text:    '#E8E8E8',
          muted:   '#9A9A9A',
        },
      },
      fontFamily: {
        sans:    ['Inter', 'sans-serif'],
        heading: ['Montserrat', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config
```

- [ ] **Step 1.4 — Configurar globals.css**

```css
/* app/globals.css */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&family=Inter:wght@300;400;500;600&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-dlima-dark text-dlima-text font-sans;
  }
  h1, h2, h3, h4, h5 {
    @apply font-heading;
  }
}

@layer utilities {
  .scrollbar-dlima::-webkit-scrollbar { width: 6px; }
  .scrollbar-dlima::-webkit-scrollbar-track { @apply bg-dlima-darker; }
  .scrollbar-dlima::-webkit-scrollbar-thumb { @apply bg-dlima-gold rounded-full; }
}
```

- [ ] **Step 1.5 — Criar .env.local (preencher após criar projeto Supabase)**

```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://SEU_PROJETO.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua_anon_key
SUPABASE_SERVICE_ROLE_KEY=sua_service_role_key
```

- [ ] **Step 1.6 — Criar manifest.json para PWA**

```json
// public/manifest.json
{
  "name": "D'LIMA Engenharia",
  "short_name": "D'LIMA",
  "description": "Gestão técnica e financeira de obras",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0F120F",
  "theme_color": "#B89B5E",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

- [ ] **Step 1.7 — Configurar next.config.ts**

```ts
// next.config.ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  images: {
    remotePatterns: [{ protocol: 'https', hostname: '*.supabase.co' }],
  },
}
export default config
```

- [ ] **Step 1.8 — Commit inicial**

```bash
git init
git add .
git commit -m "chore: setup Next.js 15 D'LIMA ERP com tailwind e dependências"
```

---

## TASK 2 — Schema do Banco de Dados + Tipos TypeScript

**Files:**
- Create: `dlima-app/supabase/migrations/001_initial.sql`
- Create: `dlima-app/lib/types.ts`
- Create: `dlima-app/lib/supabase/client.ts`
- Create: `dlima-app/lib/supabase/server.ts`
- Create: `dlima-app/middleware.ts`

- [ ] **Step 2.1 — Criar conta no Supabase**

```
1. Acessar https://supabase.com → New Project
2. Nome: dlima-erp | Região: South America (São Paulo)
3. Copiar URL e anon key para .env.local
4. Copiar service_role key para .env.local
```

- [ ] **Step 2.2 — Criar o SQL de migração**

```sql
-- supabase/migrations/001_initial.sql

-- EMPRESA
create table if not exists empresa (
  id          uuid primary key default gen_random_uuid(),
  nome        text not null,
  cnpj        text,
  crea        text,
  logradouro  text, numero text, bairro text,
  cidade      text, estado text, cep text,
  logo_url    text,
  email       text,
  telefone    text,
  rt_nome     text,
  rt_crea     text,
  config_bdi  numeric default 25,
  config_caa  text default 'II',
  criado_em   timestamptz default now()
);

-- CLIENTES
create table if not exists clientes (
  id          uuid primary key default gen_random_uuid(),
  nome        text not null,
  cpf_cnpj    text,
  telefone    text,
  email       text,
  logradouro  text, numero text, complemento text,
  bairro      text, cidade text, estado text, cep text,
  tipo        text default 'fisica' check (tipo in ('fisica','juridica')),
  observacoes text,
  criado_em   timestamptz default now()
);

-- OBRAS
create table if not exists obras (
  id                   uuid primary key default gen_random_uuid(),
  nome                 text not null,
  cliente_id           uuid references clientes(id) on delete set null,
  status               text default 'orcamento'
                       check (status in ('orcamento','aprovado','em_andamento','entregue','cancelado')),
  tipo                 text default 'residencial'
                       check (tipo in ('residencial','comercial','reforma','outro')),
  logradouro           text, numero text, bairro text,
  cidade               text, estado text, cep text,
  matricula_imovel     text,
  numero_art           text,
  data_inicio          date,
  data_previsao_fim    date,
  data_entrega_real    date,
  area_construida      numeric,
  valor_contrato       numeric,
  valor_orcado         numeric,
  observacoes          text,
  criado_em            timestamptz default now(),
  atualizado_em        timestamptz default now()
);

-- PLANTAS BAIXAS
create table if not exists plantas_baixas (
  id                   uuid primary key default gen_random_uuid(),
  obra_id              uuid references obras(id) on delete cascade,
  arquivo_url          text not null,
  nome                 text default 'Planta Térreo',
  escala_px_por_metro  numeric,
  ordem                int default 1,
  criado_em            timestamptz default now()
);

-- MEDIÇÕES (takeoff digital)
create table if not exists medicoes (
  id                uuid primary key default gen_random_uuid(),
  obra_id           uuid references obras(id) on delete cascade,
  planta_id         uuid references plantas_baixas(id) on delete set null,
  nome              text not null,
  tipo_medicao      text not null check (tipo_medicao in ('linear','area','volume')),
  vertices          jsonb,
  valor_calculado   numeric not null,
  unidade           text not null,
  altura_informada  numeric,
  fck               int,
  categoria         text,
  acabamento        text,
  criado_em         timestamptz default now()
);

-- MATERIAIS (banco de preços)
create table if not exists materiais (
  id                   uuid primary key default gen_random_uuid(),
  nome                 text not null,
  unidade              text not null,
  preco_unitario       numeric not null default 0,
  categoria            text not null,
  observacao           text,
  data_atualizacao     timestamptz default now()
);

-- QUANTITATIVOS
create table if not exists quantitativos (
  id                    uuid primary key default gen_random_uuid(),
  obra_id               uuid references obras(id) on delete cascade,
  medicao_id            uuid references medicoes(id) on delete cascade,
  material_id           uuid references materiais(id) on delete set null,
  descricao             text not null,
  quantidade_calculada  numeric not null,
  unidade               text not null,
  fck_referencia        int,
  traco_descricao       text,
  ajuste_manual         numeric,
  criado_em             timestamptz default now()
);

-- ORÇAMENTOS
create table if not exists orcamentos (
  id                   uuid primary key default gen_random_uuid(),
  obra_id              uuid references obras(id) on delete cascade,
  versao               int not null default 1,
  data_emissao         date default current_date,
  validade_dias        int default 30,
  bdi_pct              numeric default 25,
  status               text default 'rascunho'
                       check (status in ('rascunho','enviado','aprovado','reprovado','revisado')),
  valor_total_sem_bdi  numeric default 0,
  valor_total_com_bdi  numeric default 0,
  observacoes          text,
  criado_em            timestamptz default now()
);

-- ORÇAMENTO ITENS
create table if not exists orcamento_itens (
  id              uuid primary key default gen_random_uuid(),
  orcamento_id    uuid references orcamentos(id) on delete cascade,
  material_id     uuid references materiais(id) on delete set null,
  etapa           text not null,
  descricao       text not null,
  quantidade      numeric not null,
  unidade         text not null,
  preco_unitario  numeric not null,  -- CONGELADO na criação
  total_item      numeric generated always as (quantidade * preco_unitario) stored,
  ordem_exibicao  int default 0
);

-- CRONOGRAMA ETAPAS
create table if not exists cronograma_etapas (
  id                    uuid primary key default gen_random_uuid(),
  obra_id               uuid references obras(id) on delete cascade,
  nome_etapa            text not null,
  percentual_obra       numeric not null default 0,
  valor_etapa           numeric not null default 0,
  data_inicio_prevista  date,
  data_fim_prevista     date,
  data_inicio_real      date,
  data_fim_real         date,
  percentual_executado  numeric default 0,
  ordem                 int default 0
);

-- DOCUMENTOS
create table if not exists documentos (
  id          uuid primary key default gen_random_uuid(),
  obra_id     uuid references obras(id) on delete cascade,
  nome        text not null,
  tipo        text,
  arquivo_url text not null,
  categoria   text,
  criado_em   timestamptz default now()
);

-- RLS: por enquanto desabilitado (usuário único)
alter table empresa          enable row level security;
alter table clientes         enable row level security;
alter table obras            enable row level security;
alter table plantas_baixas   enable row level security;
alter table medicoes         enable row level security;
alter table materiais        enable row level security;
alter table quantitativos    enable row level security;
alter table orcamentos       enable row level security;
alter table orcamento_itens  enable row level security;
alter table cronograma_etapas enable row level security;
alter table documentos       enable row level security;

-- Políticas abertas para usuário autenticado (solo, fase 1)
do $$
declare t text;
begin
  foreach t in array array[
    'empresa','clientes','obras','plantas_baixas','medicoes',
    'materiais','quantitativos','orcamentos','orcamento_itens',
    'cronograma_etapas','documentos'
  ] loop
    execute format('create policy "auth_all_%s" on %I for all to authenticated using (true) with check (true)', t, t);
  end loop;
end $$;

-- Storage buckets
insert into storage.buckets (id, name, public) values
  ('plantas',     'plantas',     false),
  ('documentos',  'documentos',  false),
  ('relatorios',  'relatorios',  false),
  ('logos',       'logos',       true)
on conflict do nothing;
```

- [ ] **Step 2.3 — Executar SQL no Supabase**

```
Dashboard Supabase → SQL Editor → colar o conteúdo acima → Run
Verificar: todas as tabelas criadas sem erro
```

- [ ] **Step 2.4 — Criar tipos TypeScript**

```ts
// lib/types.ts

export type ObraStatus = 'orcamento' | 'aprovado' | 'em_andamento' | 'entregue' | 'cancelado'
export type TipoMedicao = 'linear' | 'area' | 'volume'
export type OrcamentoStatus = 'rascunho' | 'enviado' | 'aprovado' | 'reprovado' | 'revisado'

export interface Empresa {
  id: string
  nome: string
  cnpj?: string
  crea?: string
  cidade?: string
  estado?: string
  logo_url?: string
  email?: string
  telefone?: string
  rt_nome?: string
  rt_crea?: string
  config_bdi: number
  config_caa: string
}

export interface Cliente {
  id: string
  nome: string
  cpf_cnpj?: string
  telefone?: string
  email?: string
  logradouro?: string
  numero?: string
  bairro?: string
  cidade?: string
  estado?: string
  cep?: string
  tipo: 'fisica' | 'juridica'
  observacoes?: string
  criado_em: string
}

export interface Obra {
  id: string
  nome: string
  cliente_id?: string
  cliente?: Cliente
  status: ObraStatus
  tipo: string
  logradouro?: string
  cidade?: string
  estado?: string
  matricula_imovel?: string
  numero_art?: string
  data_inicio?: string
  data_previsao_fim?: string
  area_construida?: number
  valor_contrato?: number
  valor_orcado?: number
  observacoes?: string
  criado_em: string
}

export interface PlantaBaixa {
  id: string
  obra_id: string
  arquivo_url: string
  nome: string
  escala_px_por_metro?: number
  ordem: number
}

export interface Medicao {
  id: string
  obra_id: string
  planta_id?: string
  nome: string
  tipo_medicao: TipoMedicao
  vertices?: Array<{ x: number; y: number }>
  valor_calculado: number
  unidade: string
  altura_informada?: number
  fck?: number
  categoria?: string
  acabamento?: string
  criado_em: string
}

export interface Material {
  id: string
  nome: string
  unidade: string
  preco_unitario: number
  categoria: string
  observacao?: string
  data_atualizacao: string
}

export interface Quantitativo {
  id: string
  obra_id: string
  medicao_id?: string
  material_id?: string
  material?: Material
  descricao: string
  quantidade_calculada: number
  unidade: string
  fck_referencia?: number
  traco_descricao?: string
  ajuste_manual?: number
  quantidade_final: number  // ajuste_manual ?? quantidade_calculada
}

export interface Orcamento {
  id: string
  obra_id: string
  versao: number
  data_emissao: string
  validade_dias: number
  bdi_pct: number
  status: OrcamentoStatus
  valor_total_sem_bdi: number
  valor_total_com_bdi: number
  observacoes?: string
  itens?: OrcamentoItem[]
}

export interface OrcamentoItem {
  id: string
  orcamento_id: string
  material_id?: string
  etapa: string
  descricao: string
  quantidade: number
  unidade: string
  preco_unitario: number  // congelado
  total_item: number
  ordem_exibicao: number
}

export interface CronogramaEtapa {
  id: string
  obra_id: string
  nome_etapa: string
  percentual_obra: number
  valor_etapa: number
  data_inicio_prevista?: string
  data_fim_prevista?: string
  percentual_executado: number
  ordem: number
}

export interface TracoConcreto {
  fck: number
  traco_volume: string
  traco_massa: string
  relacao_ac: number
  cimento_kg_m3: number
  sacos_m3: number
  areia_m3: number
  brita_m3: number
  agua_litros: number
  abatimento: string
  classe_consistencia: string
}
```

- [ ] **Step 2.5 — Criar clientes Supabase**

```ts
// lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

```ts
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cs) => cs.forEach(({ name, value, options }) =>
          cookieStore.set(name, value, options)
        ),
      },
    }
  )
}
```

```ts
// middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cs) => cs.forEach(({ name, value, options }) =>
          supabaseResponse.cookies.set(name, value, options)
        ),
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  const isAuth = request.nextUrl.pathname.startsWith('/login')
  if (!user && !isAuth) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  if (user && isAuth) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return supabaseResponse
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|icon-|manifest).*)'],
}
```

- [ ] **Step 2.6 — Commit**

```bash
git add .
git commit -m "feat: schema Supabase, tipos TypeScript, clientes supabase e middleware auth"
```

---

## TASK 3 — Layout Base + Autenticação

**Files:**
- Create: `app/layout.tsx`
- Create: `app/(auth)/login/page.tsx`
- Create: `app/(auth)/layout.tsx`
- Create: `app/(dashboard)/layout.tsx`
- Create: `components/layout/sidebar.tsx`
- Create: `components/layout/mobile-nav.tsx`

- [ ] **Step 3.1 — Root layout**

```tsx
// app/layout.tsx
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: "D'LIMA Engenharia",
  description: 'Gestão técnica e financeira de obras',
  manifest: '/manifest.json',
  themeColor: '#B89B5E',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-dlima-dark text-dlima-text antialiased">{children}</body>
    </html>
  )
}
```

- [ ] **Step 3.2 — Página de login**

```tsx
// app/(auth)/login/page.tsx
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail]     = useState('')
  const [senha, setSenha]     = useState('')
  const [erro, setErro]       = useState('')
  const [loading, setLoading] = useState(false)

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setErro('')
    const supabase = createClient()
    const { error } = await supabase.auth.signInWithPassword({ email, password: senha })
    if (error) { setErro('E-mail ou senha incorretos'); setLoading(false); return }
    router.push('/')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dlima-dark">
      <div className="w-full max-w-md p-8 bg-dlima-surface border border-dlima-border rounded-2xl shadow-2xl">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="font-heading text-3xl font-black text-dlima-gold tracking-widest">
            D'LIMA
          </h1>
          <p className="text-dlima-muted text-sm mt-1">Engenharia · Precisão · Gestão</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm text-dlima-muted mb-1">E-mail</label>
            <input
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-dlima-dark border border-dlima-border rounded-lg
                         text-dlima-text focus:outline-none focus:border-dlima-gold transition-colors"
              placeholder="seu@email.com"
            />
          </div>
          <div>
            <label className="block text-sm text-dlima-muted mb-1">Senha</label>
            <input
              type="password"
              required
              value={senha}
              onChange={e => setSenha(e.target.value)}
              className="w-full px-4 py-3 bg-dlima-dark border border-dlima-border rounded-lg
                         text-dlima-text focus:outline-none focus:border-dlima-gold transition-colors"
              placeholder="••••••••"
            />
          </div>

          {erro && <p className="text-red-400 text-sm">{erro}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-dlima-gold text-dlima-dark font-heading font-bold
                       rounded-lg hover:bg-dlima-gold-light transition-colors disabled:opacity-50"
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

- [ ] **Step 3.3 — Sidebar do dashboard**

```tsx
// components/layout/sidebar.tsx
'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import {
  LayoutDashboard, Users, Building2, DollarSign,
  BookOpen, Settings, LogOut, HardHat
} from 'lucide-react'
import { clsx } from 'clsx'

const navItems = [
  { href: '/',          label: 'Dashboard',   icon: LayoutDashboard },
  { href: '/clientes',  label: 'Clientes',    icon: Users },
  { href: '/obras',     label: 'Obras',       icon: Building2 },
  { href: '/precos',    label: 'Preços',      icon: DollarSign },
  { href: '/perfil',    label: 'Configurações', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const router   = useRouter()

  async function handleLogout() {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/login')
  }

  return (
    <aside className="hidden md:flex flex-col w-56 min-h-screen bg-dlima-surface
                      border-r border-dlima-border px-3 py-6">
      {/* Logo */}
      <div className="px-3 mb-8">
        <div className="flex items-center gap-2">
          <HardHat size={22} className="text-dlima-gold" />
          <span className="font-heading font-black text-dlima-gold tracking-widest text-lg">
            D'LIMA
          </span>
        </div>
        <p className="text-dlima-muted text-xs mt-0.5 pl-8">Engenharia</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                active
                  ? 'bg-dlima-gold/10 text-dlima-gold border border-dlima-gold/20'
                  : 'text-dlima-muted hover:text-dlima-text hover:bg-dlima-border/50'
              )}
            >
              <Icon size={17} />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <button
        onClick={handleLogout}
        className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm
                   text-dlima-muted hover:text-red-400 transition-colors"
      >
        <LogOut size={17} />
        Sair
      </button>
    </aside>
  )
}
```

- [ ] **Step 3.4 — Mobile nav (barra inferior)**

```tsx
// components/layout/mobile-nav.tsx
'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Users, Building2, DollarSign, Settings } from 'lucide-react'
import { clsx } from 'clsx'

const items = [
  { href: '/',         icon: LayoutDashboard, label: 'Início' },
  { href: '/clientes', icon: Users,           label: 'Clientes' },
  { href: '/obras',    icon: Building2,       label: 'Obras' },
  { href: '/precos',   icon: DollarSign,      label: 'Preços' },
  { href: '/perfil',   icon: Settings,        label: 'Config.' },
]

export function MobileNav() {
  const pathname = usePathname()
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50
                    bg-dlima-surface border-t border-dlima-border
                    flex items-center justify-around px-2 py-2 safe-area-pb">
      {items.map(({ href, icon: Icon, label }) => {
        const active = pathname === href || (href !== '/' && pathname.startsWith(href))
        return (
          <Link
            key={href}
            href={href}
            className={clsx(
              'flex flex-col items-center gap-0.5 px-3 py-1 rounded-lg text-xs transition-colors',
              active ? 'text-dlima-gold' : 'text-dlima-muted'
            )}
          >
            <Icon size={20} />
            <span>{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
```

- [ ] **Step 3.5 — Dashboard layout**

```tsx
// app/(dashboard)/layout.tsx
import { Sidebar }   from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto pb-20 md:pb-0 scrollbar-dlima">
        {children}
      </main>
      <MobileNav />
    </div>
  )
}
```

- [ ] **Step 3.6 — Testar login**

```bash
npm run dev
# Abrir http://localhost:3000
# Deve redirecionar para /login
# Criar usuário manualmente no Supabase → Authentication → Users → Add user
# Testar login com e-mail e senha
# Deve redirecionar para / (dashboard vazio)
```

- [ ] **Step 3.7 — Deploy no Vercel**

```bash
# Instalar Vercel CLI
npm i -g vercel
vercel

# Adicionar variáveis de ambiente no dashboard Vercel:
# NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
```

- [ ] **Step 3.8 — Commit**

```bash
git add .
git commit -m "feat: layout base D'LIMA, login page, sidebar, mobile nav, deploy Vercel"
```

---

## TASK 4 — Módulo Clientes

**Files:**
- Create: `app/(dashboard)/clientes/page.tsx`
- Create: `app/(dashboard)/clientes/[id]/page.tsx`

- [ ] **Step 4.1 — Página lista de clientes**

```tsx
// app/(dashboard)/clientes/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { Cliente } from '@/lib/types'
import { Plus, Search, User, Building } from 'lucide-react'
import { clsx } from 'clsx'

export default function ClientesPage() {
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [busca,    setBusca]    = useState('')
  const [modal,    setModal]    = useState(false)
  const [form,     setForm]     = useState<Partial<Cliente>>({ tipo: 'fisica' })
  const [loading,  setLoading]  = useState(true)

  const supabase = createClient()

  async function carregar() {
    const { data } = await supabase
      .from('clientes')
      .select('*')
      .ilike('nome', `%${busca}%`)
      .order('nome')
    setClientes(data ?? [])
    setLoading(false)
  }

  useEffect(() => { carregar() }, [busca])

  async function salvar(e: React.FormEvent) {
    e.preventDefault()
    if (form.id) {
      await supabase.from('clientes').update(form).eq('id', form.id)
    } else {
      await supabase.from('clientes').insert(form)
    }
    setModal(false)
    setForm({ tipo: 'fisica' })
    carregar()
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-heading text-2xl font-bold text-dlima-text">Clientes</h1>
        <button
          onClick={() => { setForm({ tipo: 'fisica' }); setModal(true) }}
          className="flex items-center gap-2 px-4 py-2 bg-dlima-gold text-dlima-dark
                     font-semibold rounded-lg hover:bg-dlima-gold-light transition-colors text-sm"
        >
          <Plus size={16} /> Novo Cliente
        </button>
      </div>

      {/* Busca */}
      <div className="relative mb-4">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-dlima-muted" />
        <input
          value={busca}
          onChange={e => setBusca(e.target.value)}
          placeholder="Buscar cliente..."
          className="w-full pl-9 pr-4 py-2.5 bg-dlima-surface border border-dlima-border
                     rounded-lg text-dlima-text text-sm focus:outline-none focus:border-dlima-gold"
        />
      </div>

      {/* Lista */}
      {loading ? (
        <p className="text-dlima-muted text-sm">Carregando...</p>
      ) : clientes.length === 0 ? (
        <div className="text-center py-16 text-dlima-muted">
          <User size={40} className="mx-auto mb-3 opacity-30" />
          <p>Nenhum cliente cadastrado ainda.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {clientes.map(c => (
            <button
              key={c.id}
              onClick={() => { setForm(c); setModal(true) }}
              className="w-full flex items-center gap-4 p-4 bg-dlima-surface border
                         border-dlima-border rounded-xl hover:border-dlima-gold/50 transition-colors text-left"
            >
              <div className="w-10 h-10 rounded-full bg-dlima-gold/10 flex items-center justify-center">
                {c.tipo === 'juridica' ? <Building size={18} className="text-dlima-gold" /> : <User size={18} className="text-dlima-gold" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-dlima-text truncate">{c.nome}</p>
                <p className="text-dlima-muted text-xs">
                  {c.cpf_cnpj && `${c.tipo === 'juridica' ? 'CNPJ' : 'CPF'}: ${c.cpf_cnpj} · `}
                  {c.telefone}
                </p>
              </div>
              <span className={clsx(
                'text-xs px-2 py-1 rounded-full',
                c.tipo === 'juridica'
                  ? 'bg-blue-900/30 text-blue-400'
                  : 'bg-dlima-gold/10 text-dlima-gold'
              )}>
                {c.tipo === 'juridica' ? 'PJ' : 'PF'}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Modal cadastro/edição */}
      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="w-full max-w-lg bg-dlima-surface border border-dlima-border
                          rounded-2xl p-6 max-h-[90vh] overflow-y-auto scrollbar-dlima">
            <h2 className="font-heading font-bold text-lg mb-4">
              {form.id ? 'Editar Cliente' : 'Novo Cliente'}
            </h2>
            <form onSubmit={salvar} className="space-y-3">
              {/* Tipo */}
              <div className="flex gap-3">
                {(['fisica','juridica'] as const).map(t => (
                  <button
                    key={t} type="button"
                    onClick={() => setForm(f => ({ ...f, tipo: t }))}
                    className={clsx(
                      'flex-1 py-2 rounded-lg border text-sm font-medium transition-colors',
                      form.tipo === t
                        ? 'border-dlima-gold bg-dlima-gold/10 text-dlima-gold'
                        : 'border-dlima-border text-dlima-muted hover:border-dlima-gold/30'
                    )}
                  >
                    {t === 'fisica' ? 'Pessoa Física' : 'Pessoa Jurídica'}
                  </button>
                ))}
              </div>

              {[
                { field: 'nome',     label: 'Nome completo *',  required: true },
                { field: 'cpf_cnpj', label: form.tipo === 'juridica' ? 'CNPJ' : 'CPF' },
                { field: 'telefone', label: 'Telefone' },
                { field: 'email',    label: 'E-mail', type: 'email' },
                { field: 'logradouro', label: 'Logradouro' },
                { field: 'cidade',   label: 'Cidade' },
                { field: 'estado',   label: 'Estado' },
                { field: 'cep',      label: 'CEP' },
              ].map(({ field, label, required, type }) => (
                <div key={field}>
                  <label className="block text-xs text-dlima-muted mb-1">{label}</label>
                  <input
                    required={required}
                    type={type ?? 'text'}
                    value={(form as any)[field] ?? ''}
                    onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                    className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                               text-dlima-text text-sm focus:outline-none focus:border-dlima-gold"
                  />
                </div>
              ))}

              <div>
                <label className="block text-xs text-dlima-muted mb-1">Observações</label>
                <textarea
                  rows={2}
                  value={form.observacoes ?? ''}
                  onChange={e => setForm(f => ({ ...f, observacoes: e.target.value }))}
                  className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                             text-dlima-text text-sm focus:outline-none focus:border-dlima-gold resize-none"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setModal(false)}
                  className="flex-1 py-2 border border-dlima-border rounded-lg text-dlima-muted text-sm hover:border-dlima-gold/30">
                  Cancelar
                </button>
                <button type="submit"
                  className="flex-1 py-2 bg-dlima-gold text-dlima-dark font-semibold rounded-lg text-sm hover:bg-dlima-gold-light">
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4.2 — Testar criação de cliente**

```
npm run dev
Navegar para /clientes
Criar cliente "João da Silva", PF, telefone e endereço
Verificar no Supabase Dashboard → Table Editor → clientes
```

- [ ] **Step 4.3 — Commit**

```bash
git add .
git commit -m "feat: módulo clientes — lista, busca, cadastro e edição"
```

---

## TASK 5 — Módulo Obras + Dashboard

**Files:**
- Create: `app/(dashboard)/obras/page.tsx`
- Create: `app/(dashboard)/obras/[id]/page.tsx`
- Create: `app/(dashboard)/page.tsx`

- [ ] **Step 5.1 — Lista de obras**

```tsx
// app/(dashboard)/obras/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import type { Obra, Cliente, ObraStatus } from '@/lib/types'
import { Plus, Building2, ChevronRight } from 'lucide-react'
import { clsx } from 'clsx'

const STATUS_CONFIG: Record<ObraStatus, { label: string; color: string }> = {
  orcamento:    { label: 'Orçamento',    color: 'bg-yellow-900/30 text-yellow-400' },
  aprovado:     { label: 'Aprovado',     color: 'bg-blue-900/30 text-blue-400' },
  em_andamento: { label: 'Em andamento', color: 'bg-green-900/30 text-green-400' },
  entregue:     { label: 'Entregue',     color: 'bg-dlima-gold/10 text-dlima-gold' },
  cancelado:    { label: 'Cancelado',    color: 'bg-red-900/30 text-red-400' },
}

export default function ObrasPage() {
  const router  = useRouter()
  const [obras,    setObras]    = useState<Obra[]>([])
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [modal,    setModal]    = useState(false)
  const [form,     setForm]     = useState<Partial<Obra>>({ status: 'orcamento', tipo: 'residencial' })
  const [filtro,   setFiltro]   = useState<ObraStatus | 'todas'>('todas')

  const supabase = createClient()

  async function carregar() {
    const q = supabase.from('obras').select('*, cliente:clientes(nome)').order('criado_em', { ascending: false })
    if (filtro !== 'todas') q.eq('status', filtro)
    const { data } = await q
    setObras(data ?? [])
    const { data: cls } = await supabase.from('clientes').select('id,nome').order('nome')
    setClientes(cls ?? [])
  }

  useEffect(() => { carregar() }, [filtro])

  async function salvar(e: React.FormEvent) {
    e.preventDefault()
    if (form.id) {
      await supabase.from('obras').update(form).eq('id', form.id)
    } else {
      const { data } = await supabase.from('obras').insert(form).select().single()
      if (data) { setModal(false); router.push(`/obras/${data.id}`); return }
    }
    setModal(false)
    carregar()
  }

  const filtros: Array<{ value: ObraStatus | 'todas'; label: string }> = [
    { value: 'todas',        label: 'Todas' },
    { value: 'orcamento',    label: 'Orçamento' },
    { value: 'aprovado',     label: 'Aprovado' },
    { value: 'em_andamento', label: 'Em andamento' },
    { value: 'entregue',     label: 'Entregue' },
  ]

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-heading text-2xl font-bold">Obras</h1>
        <button
          onClick={() => { setForm({ status: 'orcamento', tipo: 'residencial' }); setModal(true) }}
          className="flex items-center gap-2 px-4 py-2 bg-dlima-gold text-dlima-dark
                     font-semibold rounded-lg hover:bg-dlima-gold-light text-sm"
        >
          <Plus size={16} /> Nova Obra
        </button>
      </div>

      {/* Filtros */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
        {filtros.map(f => (
          <button
            key={f.value}
            onClick={() => setFiltro(f.value)}
            className={clsx(
              'px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors',
              filtro === f.value
                ? 'bg-dlima-gold text-dlima-dark'
                : 'bg-dlima-surface border border-dlima-border text-dlima-muted hover:border-dlima-gold/30'
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Lista */}
      {obras.length === 0 ? (
        <div className="text-center py-16 text-dlima-muted">
          <Building2 size={40} className="mx-auto mb-3 opacity-30" />
          <p>Nenhuma obra encontrada.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {obras.map(o => (
            <button
              key={o.id}
              onClick={() => router.push(`/obras/${o.id}`)}
              className="w-full flex items-center gap-4 p-4 bg-dlima-surface border border-dlima-border
                         rounded-xl hover:border-dlima-gold/50 transition-colors text-left"
            >
              <div className="w-10 h-10 rounded-full bg-dlima-gold/10 flex items-center justify-center">
                <Building2 size={18} className="text-dlima-gold" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-dlima-text truncate">{o.nome}</p>
                <p className="text-dlima-muted text-xs">
                  {(o as any).cliente?.nome ?? 'Sem cliente'} · {o.cidade}
                </p>
              </div>
              <span className={clsx('text-xs px-2 py-1 rounded-full', STATUS_CONFIG[o.status].color)}>
                {STATUS_CONFIG[o.status].label}
              </span>
              <ChevronRight size={16} className="text-dlima-muted" />
            </button>
          ))}
        </div>
      )}

      {/* Modal nova obra */}
      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="w-full max-w-lg bg-dlima-surface border border-dlima-border rounded-2xl p-6
                          max-h-[90vh] overflow-y-auto scrollbar-dlima">
            <h2 className="font-heading font-bold text-lg mb-4">Nova Obra</h2>
            <form onSubmit={salvar} className="space-y-3">
              <div>
                <label className="block text-xs text-dlima-muted mb-1">Nome da obra *</label>
                <input required value={form.nome ?? ''}
                  onChange={e => setForm(f => ({ ...f, nome: e.target.value }))}
                  placeholder="Ex: Casa Família Oliveira"
                  className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                             text-dlima-text text-sm focus:outline-none focus:border-dlima-gold" />
              </div>
              <div>
                <label className="block text-xs text-dlima-muted mb-1">Cliente</label>
                <select value={form.cliente_id ?? ''}
                  onChange={e => setForm(f => ({ ...f, cliente_id: e.target.value }))}
                  className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                             text-dlima-text text-sm focus:outline-none focus:border-dlima-gold">
                  <option value="">Selecionar cliente...</option>
                  {clientes.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                </select>
              </div>
              {[
                { field: 'cidade',     label: 'Cidade' },
                { field: 'estado',     label: 'Estado (UF)' },
                { field: 'area_construida', label: 'Área construída (m²)', type: 'number' },
                { field: 'data_inicio', label: 'Data início', type: 'date' },
                { field: 'data_previsao_fim', label: 'Previsão de término', type: 'date' },
              ].map(({ field, label, type }) => (
                <div key={field}>
                  <label className="block text-xs text-dlima-muted mb-1">{label}</label>
                  <input type={type ?? 'text'} value={(form as any)[field] ?? ''}
                    onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                    className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                               text-dlima-text text-sm focus:outline-none focus:border-dlima-gold" />
                </div>
              ))}
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setModal(false)}
                  className="flex-1 py-2 border border-dlima-border rounded-lg text-dlima-muted text-sm">
                  Cancelar
                </button>
                <button type="submit"
                  className="flex-1 py-2 bg-dlima-gold text-dlima-dark font-semibold rounded-lg text-sm">
                  Criar Obra
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 5.2 — Hub da obra (página detalhe)**

```tsx
// app/(dashboard)/obras/[id]/page.tsx
import { createClient } from '@/lib/supabase/server'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { Building2, Ruler, List, FileText, BarChart2, FileCheck } from 'lucide-react'

export default async function ObraPage({ params }: { params: { id: string } }) {
  const supabase = await createClient()
  const { data: obra } = await supabase
    .from('obras')
    .select('*, cliente:clientes(nome)')
    .eq('id', params.id)
    .single()

  if (!obra) notFound()

  const modulos = [
    { href: 'takeoff',       icon: Ruler,      label: 'Takeoff Digital',    desc: 'Medir na planta' },
    { href: 'quantitativos', icon: List,       label: 'Quantitativos',      desc: 'Lista de materiais' },
    { href: 'orcamento',     icon: FileText,   label: 'Orçamento',          desc: 'Gerar orçamento' },
    { href: 'cronograma',    icon: BarChart2,  label: 'Cronograma',         desc: 'Físico-financeiro' },
    { href: 'pci',           icon: FileCheck,  label: 'PCI Caixa',          desc: 'Gerar PCI' },
  ]

  return (
    <div className="p-6 max-w-2xl mx-auto">
      {/* Cabeçalho */}
      <div className="flex items-start gap-4 mb-8">
        <div className="w-12 h-12 rounded-full bg-dlima-gold/10 flex items-center justify-center mt-1">
          <Building2 size={22} className="text-dlima-gold" />
        </div>
        <div>
          <h1 className="font-heading text-2xl font-bold">{obra.nome}</h1>
          <p className="text-dlima-muted text-sm">
            {(obra as any).cliente?.nome} · {obra.cidade}/{obra.estado}
          </p>
          {obra.area_construida && (
            <p className="text-dlima-muted text-sm">{obra.area_construida} m²</p>
          )}
        </div>
      </div>

      {/* Módulos */}
      <div className="grid grid-cols-2 gap-3">
        {modulos.map(m => (
          <Link
            key={m.href}
            href={`/obras/${params.id}/${m.href}`}
            className="p-4 bg-dlima-surface border border-dlima-border rounded-xl
                       hover:border-dlima-gold/50 hover:bg-dlima-gold/5 transition-all group"
          >
            <m.icon size={22} className="text-dlima-gold mb-2 group-hover:scale-110 transition-transform" />
            <p className="font-semibold text-sm">{m.label}</p>
            <p className="text-dlima-muted text-xs mt-0.5">{m.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 5.3 — Dashboard (página inicial)**

```tsx
// app/(dashboard)/page.tsx
import { createClient } from '@/lib/supabase/server'
import Link from 'next/link'
import { Building2, Plus } from 'lucide-react'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: obras } = await supabase
    .from('obras')
    .select('id, nome, status, cidade, cliente:clientes(nome)')
    .in('status', ['orcamento', 'aprovado', 'em_andamento'])
    .order('criado_em', { ascending: false })
    .limit(5)

  const { count: total } = await supabase
    .from('obras')
    .select('*', { count: 'exact', head: true })

  const { count: emAndamento } = await supabase
    .from('obras')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'em_andamento')

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="font-heading text-3xl font-black">
          Bom dia, <span className="text-dlima-gold">Leonan</span>
        </h1>
        <p className="text-dlima-muted mt-1">D'LIMA Engenharia · Nova Venécia/ES</p>
      </div>

      {/* Cards resumo */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-8">
        {[
          { label: 'Total de obras',    value: total ?? 0,      color: 'text-dlima-text' },
          { label: 'Em andamento',      value: emAndamento ?? 0, color: 'text-green-400' },
          { label: 'Novas este mês',    value: '—',              color: 'text-dlima-muted' },
        ].map(c => (
          <div key={c.label} className="p-4 bg-dlima-surface border border-dlima-border rounded-xl">
            <p className={`font-heading text-3xl font-bold ${c.color}`}>{c.value}</p>
            <p className="text-dlima-muted text-xs mt-1">{c.label}</p>
          </div>
        ))}
      </div>

      {/* Obras recentes */}
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-heading font-bold text-lg">Obras Recentes</h2>
        <Link href="/obras" className="text-dlima-gold text-sm hover:underline">Ver todas →</Link>
      </div>

      {(obras ?? []).length === 0 ? (
        <div className="text-center py-12 border border-dashed border-dlima-border rounded-xl">
          <Building2 size={36} className="mx-auto mb-3 text-dlima-muted opacity-40" />
          <p className="text-dlima-muted mb-4">Nenhuma obra cadastrada ainda.</p>
          <Link href="/obras"
            className="inline-flex items-center gap-2 px-4 py-2 bg-dlima-gold text-dlima-dark
                       font-semibold rounded-lg text-sm hover:bg-dlima-gold-light">
            <Plus size={15} /> Criar primeira obra
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {obras!.map(o => (
            <Link key={o.id} href={`/obras/${o.id}`}
              className="flex items-center gap-3 p-3 bg-dlima-surface border border-dlima-border
                         rounded-xl hover:border-dlima-gold/50 transition-colors">
              <Building2 size={17} className="text-dlima-gold flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{o.nome}</p>
                <p className="text-dlima-muted text-xs">{(o as any).cliente?.nome}</p>
              </div>
              <span className="text-xs text-dlima-muted">{o.status.replace('_',' ')}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 5.4 — Testar fluxo cliente → obra**

```
npm run dev
1. Criar cliente em /clientes
2. Criar obra em /obras vinculada ao cliente
3. Clicar na obra → ver hub com os 5 módulos
4. Verificar que todos os links levam a /obras/[id]/...
```

- [ ] **Step 5.5 — Commit**

```bash
git add .
git commit -m "feat: módulo obras (lista, hub, status), dashboard inicial com métricas"
```

---

---

## TASK 6 — Banco de Preços

**Files:**
- Create: `app/(dashboard)/precos/page.tsx`

- [ ] **Step 6.1 — Página banco de preços**

```tsx
// app/(dashboard)/precos/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { Material } from '@/lib/types'
import { Plus, Pencil, Trash2, Search } from 'lucide-react'

const CATEGORIAS = [
  'Serviços Preliminares','Fundação','Estrutura','Alvenaria',
  'Cobertura','Impermeabilização','Revestimentos','Pisos',
  'Esquadrias','Pintura','Instalações Elétricas',
  'Instalações Hidrossanitárias','Louças e Metais','Mão de Obra',
]

export default function PrecosPage() {
  const [materiais,  setMateriais]  = useState<Material[]>([])
  const [busca,      setBusca]      = useState('')
  const [categoria,  setCategoria]  = useState('Todos')
  const [modal,      setModal]      = useState(false)
  const [form,       setForm]       = useState<Partial<Material>>({ categoria: 'Estrutura' })

  const supabase = createClient()

  async function carregar() {
    let q = supabase.from('materiais').select('*').order('categoria').order('nome')
    if (busca) q = q.ilike('nome', `%${busca}%`)
    if (categoria !== 'Todos') q = q.eq('categoria', categoria)
    const { data } = await q
    setMateriais(data ?? [])
  }

  useEffect(() => { carregar() }, [busca, categoria])

  async function salvar(e: React.FormEvent) {
    e.preventDefault()
    const payload = { ...form, data_atualizacao: new Date().toISOString() }
    if (form.id) {
      await supabase.from('materiais').update(payload).eq('id', form.id)
    } else {
      await supabase.from('materiais').insert(payload)
    }
    setModal(false)
    setForm({ categoria: 'Estrutura' })
    carregar()
  }

  async function excluir(id: string) {
    if (!confirm('Excluir este material?')) return
    await supabase.from('materiais').delete().eq('id', id)
    carregar()
  }

  // Agrupar por categoria
  const grupos = materiais.reduce((acc, m) => {
    if (!acc[m.categoria]) acc[m.categoria] = []
    acc[m.categoria].push(m)
    return acc
  }, {} as Record<string, Material[]>)

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-bold">Banco de Preços</h1>
          <p className="text-dlima-muted text-sm mt-0.5">{materiais.length} materiais cadastrados</p>
        </div>
        <button onClick={() => { setForm({ categoria: 'Estrutura' }); setModal(true) }}
          className="flex items-center gap-2 px-4 py-2 bg-dlima-gold text-dlima-dark
                     font-semibold rounded-lg hover:bg-dlima-gold-light text-sm">
          <Plus size={16} /> Novo Material
        </button>
      </div>

      {/* Filtros */}
      <div className="flex gap-3 mb-4 flex-col md:flex-row">
        <div className="relative flex-1">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-dlima-muted" />
          <input value={busca} onChange={e => setBusca(e.target.value)}
            placeholder="Buscar material..." className="w-full pl-9 pr-4 py-2 bg-dlima-surface
            border border-dlima-border rounded-lg text-dlima-text text-sm focus:outline-none focus:border-dlima-gold" />
        </div>
        <select value={categoria} onChange={e => setCategoria(e.target.value)}
          className="px-3 py-2 bg-dlima-surface border border-dlima-border rounded-lg
                     text-dlima-text text-sm focus:outline-none focus:border-dlima-gold">
          <option value="Todos">Todas as categorias</option>
          {CATEGORIAS.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {/* Lista por categoria */}
      {Object.entries(grupos).map(([cat, items]) => (
        <div key={cat} className="mb-6">
          <h3 className="text-dlima-gold text-xs font-semibold uppercase tracking-wider mb-2">{cat}</h3>
          <div className="bg-dlima-surface border border-dlima-border rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-dlima-border">
                  <th className="text-left px-4 py-2 text-dlima-muted font-medium">Material</th>
                  <th className="text-left px-4 py-2 text-dlima-muted font-medium w-20">Unid.</th>
                  <th className="text-right px-4 py-2 text-dlima-muted font-medium w-32">Preço</th>
                  <th className="w-20"></th>
                </tr>
              </thead>
              <tbody>
                {items.map((m, i) => (
                  <tr key={m.id} className={i < items.length - 1 ? 'border-b border-dlima-border/50' : ''}>
                    <td className="px-4 py-2.5">
                      <p className="text-dlima-text">{m.nome}</p>
                      {m.observacao && <p className="text-dlima-muted text-xs">{m.observacao}</p>}
                    </td>
                    <td className="px-4 py-2.5 text-dlima-muted">{m.unidade}</td>
                    <td className="px-4 py-2.5 text-right font-medium text-dlima-gold">
                      R$ {m.preco_unitario.toFixed(2)}
                    </td>
                    <td className="px-4 py-2.5">
                      <div className="flex gap-1 justify-end">
                        <button onClick={() => { setForm(m); setModal(true) }}
                          className="p-1.5 text-dlima-muted hover:text-dlima-gold rounded">
                          <Pencil size={14} />
                        </button>
                        <button onClick={() => excluir(m.id)}
                          className="p-1.5 text-dlima-muted hover:text-red-400 rounded">
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      {/* Modal */}
      {modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="w-full max-w-md bg-dlima-surface border border-dlima-border rounded-2xl p-6">
            <h2 className="font-heading font-bold text-lg mb-4">
              {form.id ? 'Editar Material' : 'Novo Material'}
            </h2>
            <form onSubmit={salvar} className="space-y-3">
              {[
                { field: 'nome',     label: 'Nome do material *', required: true },
                { field: 'unidade',  label: 'Unidade (m², m³, kg, saco, un...) *', required: true },
                { field: 'observacao', label: 'Observação (ex: Loja Cassol)' },
              ].map(({ field, label, required }) => (
                <div key={field}>
                  <label className="block text-xs text-dlima-muted mb-1">{label}</label>
                  <input required={required} value={(form as any)[field] ?? ''}
                    onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                    className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                               text-dlima-text text-sm focus:outline-none focus:border-dlima-gold" />
                </div>
              ))}
              <div>
                <label className="block text-xs text-dlima-muted mb-1">Categoria</label>
                <select value={form.categoria} onChange={e => setForm(f => ({ ...f, categoria: e.target.value }))}
                  className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                             text-dlima-text text-sm focus:outline-none focus:border-dlima-gold">
                  {CATEGORIAS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-dlima-muted mb-1">Preço unitário (R$) *</label>
                <input required type="number" step="0.01" min="0"
                  value={form.preco_unitario ?? ''}
                  onChange={e => setForm(f => ({ ...f, preco_unitario: parseFloat(e.target.value) }))}
                  className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                             text-dlima-text text-sm focus:outline-none focus:border-dlima-gold" />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setModal(false)}
                  className="flex-1 py-2 border border-dlima-border rounded-lg text-dlima-muted text-sm">
                  Cancelar
                </button>
                <button type="submit"
                  className="flex-1 py-2 bg-dlima-gold text-dlima-dark font-semibold rounded-lg text-sm">
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 6.2 — Cadastrar os primeiros materiais**

```
Navegar para /precos → cadastrar manualmente os materiais mais usados:
- Cimento CP II 50kg → saco → R$ 39,00 → Estrutura
- Areia média lavada → m³ → R$ 150,00 → Estrutura
- Brita 1 → m³ → R$ 180,00 → Estrutura
- Bloco cerâmico 9cm → un → R$ 1,20 → Alvenaria
(continuar conforme preços atuais de Nova Venécia/ES)
```

- [ ] **Step 6.3 — Commit**

```bash
git add .
git commit -m "feat: banco de preços — cadastro, edição, exclusão, filtro por categoria"
```

---

## TASK 7 — Takeoff Digital: Upload, Calibração e Área

**Files:**
- Create: `app/(dashboard)/obras/[id]/takeoff/page.tsx`
- Create: `components/takeoff/canvas.tsx`
- Create: `components/takeoff/measure-form.tsx`
- Create: `components/takeoff/measurements-list.tsx`
- Create: `lib/calc/shoelace.ts`

- [ ] **Step 7.1 — Fórmula de Shoelace e cálculos geométricos**

```ts
// lib/calc/shoelace.ts
export interface Point { x: number; y: number }

/** Área de polígono (fórmula de Shoelace) */
export function calcArea(points: Point[]): number {
  if (points.length < 3) return 0
  let sum = 0
  for (let i = 0; i < points.length; i++) {
    const j = (i + 1) % points.length
    sum += points[i].x * points[j].y
    sum -= points[j].x * points[i].y
  }
  return Math.abs(sum) / 2
}

/** Distância entre 2 pontos */
export function calcDistancia(a: Point, b: Point): number {
  return Math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)
}

/** Converte pixels para metros usando escala */
export function pxParaMetros(px: number, escala: number): number {
  return px / escala
}

/** Converte área em px² para m² */
export function areaParaM2(areaPx: number, escala: number): number {
  return areaPx / (escala * escala)
}
```

- [ ] **Step 7.2 — Componente canvas de takeoff**

```tsx
// components/takeoff/canvas.tsx
'use client'
import { useRef, useEffect, useState, forwardRef, useImperativeHandle } from 'react'
import type { Point } from '@/lib/calc/shoelace'
import { calcArea, calcDistancia, areaParaM2, pxParaMetros } from '@/lib/calc/shoelace'

export interface TakeoffCanvasHandle {
  clear: () => void
  undo: () => void
  closePoly: () => void
}

interface Props {
  imageUrl: string
  escala: number              // px por metro
  tipoMedicao: 'linear' | 'area' | 'volume'
  calibrando?: boolean        // modo calibração
  onCalibrationPoints?: (pts: [Point, Point]) => void
  onMeasurementComplete?: (value: number, unit: string, vertices: Point[]) => void
}

const TakeoffCanvas = forwardRef<TakeoffCanvasHandle, Props>(
  ({ imageUrl, escala, tipoMedicao, calibrando, onCalibrationPoints, onMeasurementComplete }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const [points,  setPoints]  = useState<Point[]>([])
    const [imgSize, setImgSize] = useState({ w: 0, h: 0 })

    // Expor métodos para o pai
    useImperativeHandle(ref, () => ({
      clear:    () => setPoints([]),
      undo:     () => setPoints(p => p.slice(0, -1)),
      closePoly: handleClose,
    }))

    // Carregar imagem de fundo
    useEffect(() => {
      const canvas = canvasRef.current
      if (!canvas) return
      const ctx = canvas.getContext('2d')!
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        const maxW = canvas.parentElement?.clientWidth ?? 800
        const scale = maxW / img.width
        canvas.width  = img.width  * scale
        canvas.height = img.height * scale
        setImgSize({ w: canvas.width, h: canvas.height })
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
      }
      img.src = imageUrl
    }, [imageUrl])

    // Redesenhar pontos/linhas
    useEffect(() => {
      const canvas = canvasRef.current
      if (!canvas || imgSize.w === 0) return
      const ctx = canvas.getContext('2d')!

      // Redraw imagem
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

        if (points.length === 0) return

        // Desenhar linhas
        ctx.beginPath()
        ctx.moveTo(points[0].x, points[0].y)
        points.forEach(p => ctx.lineTo(p.x, p.y))
        ctx.strokeStyle = '#B89B5E'
        ctx.lineWidth   = 2
        ctx.stroke()

        // Polígono preenchido (apenas área/volume)
        if (tipoMedicao !== 'linear' && points.length >= 3) {
          ctx.fillStyle = 'rgba(184,155,94,0.15)'
          ctx.fill()
        }

        // Pontos
        points.forEach((p, i) => {
          ctx.beginPath()
          ctx.arc(p.x, p.y, 5, 0, 2 * Math.PI)
          ctx.fillStyle = i === 0 ? '#B89B5E' : '#D4B978'
          ctx.fill()
        })

        // Label com valor atual
        if (points.length >= 2) {
          const valor = getCurrentValue()
          ctx.font      = 'bold 13px Inter'
          ctx.fillStyle = '#B89B5E'
          ctx.fillText(valor, points[points.length - 1].x + 8, points[points.length - 1].y - 8)
        }
      }
      img.src = imageUrl
    }, [points, imgSize])

    function getCurrentValue(): string {
      if (tipoMedicao === 'linear') {
        let total = 0
        for (let i = 1; i < points.length; i++)
          total += calcDistancia(points[i-1], points[i])
        return `${pxParaMetros(total, escala).toFixed(2)} m`
      }
      if (points.length >= 3) {
        const areaPx = calcArea(points)
        return `${areaParaM2(areaPx, escala).toFixed(2)} m²`
      }
      return ''
    }

    function handleClick(e: React.MouseEvent<HTMLCanvasElement>) {
      const rect = canvasRef.current!.getBoundingClientRect()
      const pt: Point = { x: e.clientX - rect.left, y: e.clientY - rect.top }

      if (calibrando) {
        const novos = [...points, pt].slice(-2) as [Point, Point]
        setPoints(novos)
        if (novos.length === 2) onCalibrationPoints?.(novos)
        return
      }

      // Fechar polígono se clicar perto do primeiro ponto
      if (tipoMedicao !== 'linear' && points.length >= 3) {
        const d = calcDistancia(pt, points[0])
        if (d < 12) { handleClose(); return }
      }

      setPoints(p => [...p, pt])
    }

    function handleClose() {
      if (points.length < 2) return
      if (tipoMedicao === 'linear') {
        let total = 0
        for (let i = 1; i < points.length; i++)
          total += calcDistancia(points[i-1], points[i])
        const metros = pxParaMetros(total, escala)
        onMeasurementComplete?.(metros, 'm', points)
        setPoints([])
      } else {
        if (points.length < 3) return
        const areaPx = calcArea(points)
        const m2 = areaParaM2(areaPx, escala)
        onMeasurementComplete?.(m2, tipoMedicao === 'volume' ? 'm²' : 'm²', points)
        setPoints([])
      }
    }

    return (
      <div className="relative w-full overflow-auto border border-dlima-border rounded-xl bg-dlima-darker">
        <canvas
          ref={canvasRef}
          onClick={handleClick}
          className="cursor-crosshair max-w-full"
          style={{ display: 'block' }}
        />
        {points.length >= 2 && tipoMedicao !== 'linear' && (
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 text-xs text-dlima-muted bg-dlima-dark px-3 py-1 rounded-full border border-dlima-border">
            Clique no 1º ponto para fechar ou pressione Fechar
          </div>
        )}
      </div>
    )
  }
)
TakeoffCanvas.displayName = 'TakeoffCanvas'
export default TakeoffCanvas
```

- [ ] **Step 7.3 — Formulário de medição (antes de clicar)**

```tsx
// components/takeoff/measure-form.tsx
'use client'
import { useState } from 'react'
import type { TipoMedicao } from '@/lib/types'
import { clsx } from 'clsx'

interface Props {
  onStart: (nome: string, tipo: TipoMedicao) => void
}

const TIPOS: Array<{ value: TipoMedicao; label: string; desc: string }> = [
  { value: 'linear', label: 'Linear (m)',  desc: 'Paredes, vigas, tubulações' },
  { value: 'area',   label: 'Área (m²)',   desc: 'Pisos, tetos, revestimentos' },
  { value: 'volume', label: 'Volume (m³)', desc: 'Concreto, aterro, escavação' },
]

export function MeasureForm({ onStart }: Props) {
  const [nome, setNome] = useState('')
  const [tipo, setTipo] = useState<TipoMedicao>('area')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!nome.trim()) return
    onStart(nome.trim(), tipo)
    setNome('')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-dlima-surface
          border border-dlima-border rounded-xl">
      <div>
        <label className="block text-xs text-dlima-muted mb-1">Nome do elemento *</label>
        <input required value={nome} onChange={e => setNome(e.target.value)}
          placeholder="Ex: Sala - Piso, Fundação Bloco P1, Viga V3"
          className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                     text-dlima-text text-sm focus:outline-none focus:border-dlima-gold" />
      </div>

      <div>
        <label className="block text-xs text-dlima-muted mb-2">Tipo de medição *</label>
        <div className="grid grid-cols-3 gap-2">
          {TIPOS.map(t => (
            <button key={t.value} type="button" onClick={() => setTipo(t.value)}
              className={clsx(
                'p-3 rounded-lg border text-left transition-colors',
                tipo === t.value
                  ? 'border-dlima-gold bg-dlima-gold/10'
                  : 'border-dlima-border hover:border-dlima-gold/30'
              )}>
              <p className={clsx('text-sm font-semibold', tipo === t.value ? 'text-dlima-gold' : 'text-dlima-text')}>
                {t.label}
              </p>
              <p className="text-dlima-muted text-xs mt-0.5">{t.desc}</p>
            </button>
          ))}
        </div>
      </div>

      <button type="submit"
        className="w-full py-2.5 bg-dlima-gold text-dlima-dark font-semibold
                   rounded-lg hover:bg-dlima-gold-light transition-colors text-sm">
        Iniciar Medição
      </button>
    </form>
  )
}
```

- [ ] **Step 7.4 — Página takeoff completa**

```tsx
// app/(dashboard)/obras/[id]/takeoff/page.tsx
'use client'
import { useState, useRef, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import TakeoffCanvas, { type TakeoffCanvasHandle } from '@/components/takeoff/canvas'
import { MeasureForm } from '@/components/takeoff/measure-form'
import type { PlantaBaixa, TipoMedicao, Medicao } from '@/lib/types'
import type { Point } from '@/lib/calc/shoelace'
import { calcDistancia, pxParaMetros } from '@/lib/calc/shoelace'
import { Upload, Ruler, Check, Undo2 } from 'lucide-react'

// Perguntas contextuais por categoria
const PERGUNTAS: Record<string, { label: string; placeholder: string } | null> = {
  'concreto':   { label: 'fck do concreto (MPa)', placeholder: '25' },
  'laje':       { label: 'Espessura da laje (cm)', placeholder: '12' },
  'fundação':   { label: 'Profundidade (cm)', placeholder: '60' },
  'parede':     { label: 'Pé-direito (m)', placeholder: '2.80' },
}

function detectarCategoria(nome: string): string {
  const n = nome.toLowerCase()
  if (n.includes('concret') || n.includes('bloco') || n.includes('sapata')) return 'concreto'
  if (n.includes('laje') || n.includes('escore')) return 'laje'
  if (n.includes('fund') || n.includes('sapata') || n.includes('radier')) return 'fundação'
  if (n.includes('parede') || n.includes('alvenar')) return 'parede'
  return 'outro'
}

export default function TakeoffPage({ params }: { params: { id: string } }) {
  const canvasRef = useRef<TakeoffCanvasHandle>(null)
  const [planta,       setPlanta]       = useState<PlantaBaixa | null>(null)
  const [medicoes,     setMedicoes]     = useState<Medicao[]>([])
  const [calibrando,   setCalibrando]   = useState(false)
  const [calPts,       setCalPts]       = useState<[Point,Point] | null>(null)
  const [escalaInput,  setEscalaInput]  = useState('')
  const [escala,       setEscala]       = useState(0)
  const [medindo,      setMedindo]      = useState(false)
  const [nomeAtual,    setNomeAtual]    = useState('')
  const [tipoAtual,    setTipoAtual]    = useState<TipoMedicao>('area')
  const [aguardandoH,  setAguardandoH]  = useState<{ valor: number; unit: string; verts: Point[] } | null>(null)
  const [alturaInput,  setAlturaInput]  = useState('')
  const [fckInput,     setFckInput]     = useState('25')

  const supabase = createClient()

  // Carregar planta e medições existentes
  useEffect(() => {
    async function init() {
      const { data: pl } = await supabase.from('plantas_baixas').select('*').eq('obra_id', params.id).single()
      if (pl) { setPlanta(pl); if (pl.escala_px_por_metro) setEscala(pl.escala_px_por_metro) }
      const { data: ms } = await supabase.from('medicoes').select('*').eq('obra_id', params.id).order('criado_em')
      setMedicoes(ms ?? [])
    }
    init()
  }, [])

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    const path = `${params.id}/${Date.now()}_${file.name}`
    const { error } = await supabase.storage.from('plantas').upload(path, file)
    if (error) { alert('Erro ao subir imagem'); return }
    const { data: { publicUrl } } = supabase.storage.from('plantas').getPublicUrl(path)
    const { data: pl } = await supabase.from('plantas_baixas')
      .insert({ obra_id: params.id, arquivo_url: publicUrl, nome: 'Planta Baixa', ordem: 1 })
      .select().single()
    if (pl) setPlanta(pl)
    setCalibrando(true)
  }

  function handleCalibrationPoints(pts: [Point, Point]) {
    setCalPts(pts)
  }

  async function confirmarEscala() {
    const metros = parseFloat(escalaInput)
    if (!metros || !calPts) return
    const distPx = calcDistancia(calPts[0], calPts[1])
    const novaEscala = distPx / metros
    setEscala(novaEscala)
    await supabase.from('plantas_baixas').update({ escala_px_por_metro: novaEscala }).eq('id', planta!.id)
    setCalibrando(false)
    setCalPts(null)
    canvasRef.current?.clear()
  }

  function handleStartMeasure(nome: string, tipo: TipoMedicao) {
    setNomeAtual(nome)
    setTipoAtual(tipo)
    setMedindo(true)
  }

  async function handleMeasureComplete(valor: number, unit: string, verts: Point[]) {
    const cat = detectarCategoria(nomeAtual)
    // Volume ou categoria que precisa de altura
    if (tipoAtual === 'volume' || cat === 'laje' || cat === 'fundação' || cat === 'parede') {
      setAguardandoH({ valor, unit, verts })
      return
    }
    await salvarMedicao(valor, unit, verts, undefined)
  }

  async function confirmarAltura() {
    if (!aguardandoH) return
    const h = parseFloat(alturaInput || fckInput)
    const cat = detectarCategoria(nomeAtual)
    let valorFinal = aguardandoH.valor
    let unidade    = aguardandoH.unit

    if (tipoAtual === 'volume') {
      valorFinal = aguardandoH.valor * (parseFloat(alturaInput) / 100)
      unidade = 'm³'
    }

    const fck = cat === 'concreto' ? parseInt(fckInput) : undefined
    await salvarMedicao(valorFinal, unidade, aguardandoH.verts, parseFloat(alturaInput), fck)
    setAguardandoH(null)
    setAlturaInput('')
  }

  async function salvarMedicao(valor: number, unidade: string, verts: Point[], altura?: number, fck?: number) {
    const { data: nova } = await supabase.from('medicoes').insert({
      obra_id: params.id, planta_id: planta?.id,
      nome: nomeAtual, tipo_medicao: tipoAtual,
      vertices: verts, valor_calculado: valor, unidade,
      altura_informada: altura, fck,
      categoria: detectarCategoria(nomeAtual),
    }).select().single()
    if (nova) setMedicoes(m => [...m, nova])
    setMedindo(false)
    setNomeAtual('')
  }

  const cat = detectarCategoria(nomeAtual)
  const pergunta = tipoAtual === 'volume'
    ? { label: 'Altura/espessura/profundidade (cm)', placeholder: '30' }
    : PERGUNTAS[cat]

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h2 className="font-heading text-xl font-bold mb-4">Takeoff Digital</h2>

      {/* Upload da planta */}
      {!planta && (
        <label className="flex flex-col items-center justify-center border-2 border-dashed
                          border-dlima-border rounded-xl py-12 cursor-pointer hover:border-dlima-gold/50 mb-4">
          <Upload size={32} className="text-dlima-muted mb-2" />
          <p className="text-dlima-muted text-sm">Clique para subir a planta baixa</p>
          <p className="text-dlima-muted text-xs mt-1">PNG, JPG ou PDF</p>
          <input type="file" accept="image/*,.pdf" className="hidden" onChange={handleUpload} />
        </label>
      )}

      {planta && !escala && !calibrando && (
        <div className="mb-4 p-3 bg-yellow-900/20 border border-yellow-700/40 rounded-xl text-yellow-400 text-sm">
          ⚠️ Planta sem escala calibrada.{' '}
          <button onClick={() => setCalibrando(true)} className="underline font-semibold">Calibrar agora</button>
        </div>
      )}

      {/* Calibração */}
      {calibrando && (
        <div className="mb-4 p-4 bg-dlima-surface border border-dlima-gold/30 rounded-xl">
          <p className="text-dlima-gold font-semibold text-sm mb-2">
            📏 Clique em 2 pontos de distância conhecida na planta
          </p>
          {calPts?.length === 2 && (
            <div className="flex gap-2 mt-2">
              <input value={escalaInput} onChange={e => setEscalaInput(e.target.value)}
                placeholder="Distância real em metros (ex: 5.00)"
                type="number" step="0.01"
                className="flex-1 px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                           text-dlima-text text-sm focus:outline-none focus:border-dlima-gold" />
              <button onClick={confirmarEscala}
                className="flex items-center gap-1 px-4 py-2 bg-dlima-gold text-dlima-dark
                           font-semibold rounded-lg text-sm">
                <Check size={15} /> Confirmar
              </button>
            </div>
          )}
          {!calPts && <p className="text-dlima-muted text-xs mt-1">Clique no ponto inicial na planta acima</p>}
          {calPts?.length === 1 && <p className="text-dlima-muted text-xs mt-1">Agora clique no ponto final</p>}
        </div>
      )}

      {/* Canvas */}
      {planta && (
        <div className="mb-4">
          <TakeoffCanvas ref={canvasRef}
            imageUrl={planta.arquivo_url}
            escala={escala || 100}
            tipoMedicao={tipoAtual}
            calibrando={calibrando}
            onCalibrationPoints={handleCalibrationPoints}
            onMeasurementComplete={handleMeasureComplete}
          />
          {medindo && (
            <div className="flex gap-2 mt-2">
              <button onClick={() => canvasRef.current?.undo()}
                className="flex items-center gap-1 px-3 py-1.5 bg-dlima-surface border border-dlima-border
                           rounded-lg text-dlima-muted text-xs hover:border-dlima-gold/30">
                <Undo2 size={13} /> Desfazer
              </button>
              {tipoAtual === 'linear' && (
                <button onClick={() => canvasRef.current?.closePoly()}
                  className="flex items-center gap-1 px-3 py-1.5 bg-dlima-gold text-dlima-dark
                             font-semibold rounded-lg text-xs">
                  <Check size={13} /> Confirmar medição
                </button>
              )}
              <button onClick={() => { setMedindo(false); canvasRef.current?.clear() }}
                className="px-3 py-1.5 border border-red-800/40 rounded-lg text-red-400 text-xs">
                Cancelar
              </button>
            </div>
          )}
        </div>
      )}

      {/* Modal altura/fck */}
      {aguardandoH && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="w-full max-w-sm bg-dlima-surface border border-dlima-border rounded-2xl p-6">
            <h3 className="font-heading font-bold mb-4">Dados complementares</h3>
            <p className="text-dlima-muted text-sm mb-3">
              Elemento: <span className="text-dlima-gold font-medium">{nomeAtual}</span>
            </p>
            <p className="text-dlima-muted text-sm mb-1">
              Área calculada: <span className="text-dlima-text font-medium">
                {aguardandoH.valor.toFixed(2)} m²
              </span>
            </p>

            {cat === 'concreto' && (
              <div className="mb-3">
                <label className="block text-xs text-dlima-muted mb-1">fck do concreto (MPa)</label>
                <div className="flex gap-2">
                  {[15,20,25,30,35,40].map(f => (
                    <button key={f} type="button" onClick={() => setFckInput(String(f))}
                      className={`flex-1 py-2 rounded-lg border text-xs font-medium transition-colors ${
                        fckInput === String(f) ? 'border-dlima-gold bg-dlima-gold/10 text-dlima-gold'
                                               : 'border-dlima-border text-dlima-muted'}`}>
                      C{f}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {pergunta && (
              <div className="mb-4">
                <label className="block text-xs text-dlima-muted mb-1">{pergunta.label}</label>
                <input value={alturaInput} onChange={e => setAlturaInput(e.target.value)}
                  type="number" step="0.01" placeholder={pergunta.placeholder}
                  className="w-full px-3 py-2 bg-dlima-dark border border-dlima-border rounded-lg
                             text-dlima-text text-sm focus:outline-none focus:border-dlima-gold" />
              </div>
            )}

            <button onClick={confirmarAltura}
              className="w-full py-2.5 bg-dlima-gold text-dlima-dark font-semibold rounded-lg text-sm">
              Confirmar e Salvar
            </button>
          </div>
        </div>
      )}

      {/* Formulário nova medição */}
      {planta && escala > 0 && !medindo && !calibrando && (
        <div className="mb-4">
          <MeasureForm onStart={handleStartMeasure} />
        </div>
      )}

      {/* Lista de medições */}
      {medicoes.length > 0 && (
        <div>
          <h3 className="font-heading font-bold text-sm mb-2 text-dlima-muted uppercase tracking-wider">
            Medições ({medicoes.length})
          </h3>
          <div className="space-y-1">
            {medicoes.map(m => (
              <div key={m.id} className="flex items-center gap-3 p-3 bg-dlima-surface
                                         border border-dlima-border rounded-xl">
                <Ruler size={15} className="text-dlima-gold flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{m.nome}</p>
                  <p className="text-dlima-muted text-xs">{m.tipo_medicao}
                    {m.fck ? ` · C${m.fck}` : ''}
                    {m.altura_informada ? ` · h=${m.altura_informada}cm` : ''}
                  </p>
                </div>
                <span className="text-dlima-gold font-semibold text-sm">
                  {m.valor_calculado.toFixed(2)} {m.unidade}
                </span>
              </div>
            ))}
          </div>

          <button className="mt-4 w-full py-3 bg-dlima-gold text-dlima-dark font-heading
                             font-bold rounded-xl hover:bg-dlima-gold-light transition-colors">
            Calcular Quantitativos →
          </button>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 7.5 — Testar takeoff completo**

```
npm run dev → /obras/[id]/takeoff
1. Upload de uma planta baixa (PNG ou JPG)
2. Calibrar escala: clicar em 2 pontos, informar 5m → confirmar
3. Criar medição "Sala - Piso" tipo Área
4. Clicar nos 4 cantos da sala → clicar no 1º ponto para fechar
5. Verificar que a área aparece na lista em m²
6. Criar medição "Viga V1" tipo Linear
7. Criar medição "Fundação Bloco P1" tipo Volume → confirmar altura
8. Verificar na tabela medicoes no Supabase
```

- [ ] **Step 7.6 — Commit**

```bash
git add .
git commit -m "feat: takeoff digital — upload planta, calibração de escala, medição linear/área/volume, perguntas contextuais"
```

---

## TASK 8 — Traço de Concreto In Loco

**Files:**
- Create: `lib/calc/concreto.ts`

- [ ] **Step 8.1 — Escrever teste**

```ts
// lib/calc/concreto.test.ts
import { getTraco } from './concreto'

test('C25 retorna traço correto', () => {
  const t = getTraco(25)
  expect(t.traco_volume).toBe('1:1,8:2,8')
  expect(t.sacos_m3).toBe(7.2)
  expect(t.cimento_kg_m3).toBe(360)
  expect(t.relacao_ac).toBe(0.55)
})

test('C30 retorna traço correto', () => {
  const t = getTraco(30)
  expect(t.sacos_m3).toBe(8.0)
  expect(t.cimento_kg_m3).toBe(400)
})

test('fck inválido retorna null', () => {
  expect(getTraco(99)).toBeNull()
})
```

- [ ] **Step 8.2 — Rodar teste (deve falhar)**

```bash
npx jest lib/calc/concreto.test.ts
# Expected: FAIL — "Cannot find module './concreto'"
```

- [ ] **Step 8.3 — Implementar**

```ts
// lib/calc/concreto.ts
import type { TracoConcreto } from '@/lib/types'

const TRACOS: Record<number, Omit<TracoConcreto, 'fck'>> = {
  15: { traco_volume:'1:3,0:4,0', traco_massa:'1:3,3:4,4', relacao_ac:0.80,
        cimento_kg_m3:280, sacos_m3:5.6, areia_m3:0.84, brita_m3:0.89,
        agua_litros:224, abatimento:'80 a 100 mm', classe_consistencia:'S3' },
  20: { traco_volume:'1:2,5:3,5', traco_massa:'1:2,8:3,9', relacao_ac:0.68,
        cimento_kg_m3:320, sacos_m3:6.4, areia_m3:0.80, brita_m3:0.85,
        agua_litros:218, abatimento:'60 a 80 mm', classe_consistencia:'S2' },
  25: { traco_volume:'1:1,8:2,8', traco_massa:'1:2,0:3,0', relacao_ac:0.55,
        cimento_kg_m3:360, sacos_m3:7.2, areia_m3:0.72, brita_m3:0.75,
        agua_litros:198, abatimento:'60 a 80 mm', classe_consistencia:'S2' },
  30: { traco_volume:'1:1,5:2,5', traco_massa:'1:1,7:2,7', relacao_ac:0.48,
        cimento_kg_m3:400, sacos_m3:8.0, areia_m3:0.68, brita_m3:0.71,
        agua_litros:192, abatimento:'40 a 60 mm', classe_consistencia:'S1' },
  35: { traco_volume:'1:1,2:2,0', traco_massa:'1:1,4:2,2', relacao_ac:0.42,
        cimento_kg_m3:440, sacos_m3:8.8, areia_m3:0.65, brita_m3:0.68,
        agua_litros:185, abatimento:'40 a 60 mm', classe_consistencia:'S1' },
  40: { traco_volume:'1:1,0:1,8', traco_massa:'1:1,2:2,0', relacao_ac:0.38,
        cimento_kg_m3:480, sacos_m3:9.6, areia_m3:0.62, brita_m3:0.65,
        agua_litros:182, abatimento:'20 a 40 mm', classe_consistencia:'S1' },
}

export function getTraco(fck: number): TracoConcreto | null {
  const t = TRACOS[fck]
  if (!t) return null
  return { fck, ...t }
}

/** Calcula insumos para um dado volume de concreto */
export function calcInsumos(fck: number, volume_m3: number) {
  const traco = getTraco(fck)
  if (!traco) return null
  return {
    cimento_sacos:  Math.ceil(traco.sacos_m3 * volume_m3),
    cimento_kg:     +(traco.cimento_kg_m3 * volume_m3).toFixed(1),
    areia_m3:       +(traco.areia_m3 * volume_m3).toFixed(2),
    brita_m3:       +(traco.brita_m3 * volume_m3).toFixed(2),
    agua_litros:    +(traco.agua_litros * volume_m3).toFixed(0),
    traco,
  }
}
```

- [ ] **Step 8.4 — Rodar teste (deve passar)**

```bash
npx jest lib/calc/concreto.test.ts
# Expected: PASS — 3 testes passando
```

- [ ] **Step 8.5 — Commit**

```bash
git add .
git commit -m "feat: calculadora de traço de concreto por fck (C15–C40) com insumos por m³"
```

---

## TASK 9 — Motor de Quantitativos

**Files:**
- Create: `lib/calc/quantitativos.ts`
- Create: `app/(dashboard)/obras/[id]/quantitativos/page.tsx`

- [ ] **Step 9.1 — Escrever testes**

```ts
// lib/calc/quantitativos.test.ts
import { calcQuantitativos } from './quantitativos'
import type { Medicao } from '@/lib/types'

const medicaoLaje: Medicao = {
  id:'1', obra_id:'o1', nome:'Laje Sala', tipo_medicao:'volume',
  valor_calculado:2.0, unidade:'m³', altura_informada:12,
  categoria:'laje', criado_em:'2026-01-01',
}

test('laje treliçada retorna cimento, areia, brita, vigota, tavela', () => {
  const itens = calcQuantitativos([medicaoLaje])
  const desc = itens.map(i => i.descricao)
  expect(desc).toContain('Cimento CP II 50kg')
  expect(desc).toContain('Areia média lavada')
  expect(desc).toContain('Vigota treliçada 12M')
})

test('quantidade de cimento C25 para 2m³ = ceil(7.2×2)=15 sacos', () => {
  const itens = calcQuantitativos([medicaoLaje])
  const cimento = itens.find(i => i.descricao === 'Cimento CP II 50kg')
  expect(cimento?.quantidade_calculada).toBe(15)
})
```

- [ ] **Step 9.2 — Rodar (deve falhar)**

```bash
npx jest lib/calc/quantitativos.test.ts
# Expected: FAIL
```

- [ ] **Step 9.3 — Implementar motor de quantitativos**

```ts
// lib/calc/quantitativos.ts
import type { Medicao } from '@/lib/types'
import { calcInsumos } from './concreto'

export interface QuantitativoItem {
  descricao:            string
  quantidade_calculada: number
  unidade:              string
  categoria:            string
  traco_descricao?:     string
  fck_referencia?:      number
  medicao_id:           string
}

/** Tabelas de composição por tipo de elemento */
const COMPOSICOES: Record<string, Array<{
  descricao: string; unidade: string; coef: number; categoria: string
}>> = {
  // 1 m² de laje treliçada H12 (EPS) — escoramento por 15 dias
  'laje_trelicada_12': [
    { descricao:'Vigota treliçada 12M',    unidade:'m',   coef:4.2,  categoria:'Estrutura' },
    { descricao:'Tavela EPS 12/27',        unidade:'un',  coef:12.5, categoria:'Estrutura' },
    { descricao:'Malha soldada Q92',       unidade:'m²',  coef:1.10, categoria:'Estrutura' },
    { descricao:'Escoramento (aluguel)',   unidade:'m²',  coef:1.0,  categoria:'Estrutura' },
    { descricao:'Pedreiro (laje)',         unidade:'h',   coef:0.8,  categoria:'Mão de Obra' },
  ],
  // 1 m² de alvenaria bloco cerâmico 9cm com reboco
  'alvenaria_bloco_9': [
    { descricao:'Bloco cerâmico 9x19x19cm', unidade:'un', coef:27,  categoria:'Alvenaria' },
    { descricao:'Cimento CP II 50kg',        unidade:'saco',coef:0.5,categoria:'Estrutura' },
    { descricao:'Areia média lavada',        unidade:'m³', coef:0.03,categoria:'Estrutura' },
    { descricao:'Pedreiro (alvenaria)',      unidade:'h',  coef:0.6, categoria:'Mão de Obra' },
  ],
  // 1 m² de piso porcelanato
  'piso_porcelanato': [
    { descricao:'Porcelanato (padrão médio)', unidade:'m²',  coef:1.10, categoria:'Pisos' },
    { descricao:'Argamassa colante AC2',      unidade:'saco',coef:0.25, categoria:'Pisos' },
    { descricao:'Rejunte',                    unidade:'kg',  coef:0.45, categoria:'Pisos' },
    { descricao:'Azulejista (piso)',          unidade:'h',   coef:0.9,  categoria:'Mão de Obra' },
  ],
  // 1 m² de piso cerâmico
  'piso_ceramica': [
    { descricao:'Cerâmica (padrão médio)', unidade:'m²',  coef:1.10, categoria:'Pisos' },
    { descricao:'Argamassa colante AC1',   unidade:'saco',coef:0.22, categoria:'Pisos' },
    { descricao:'Rejunte',                 unidade:'kg',  coef:0.40, categoria:'Pisos' },
    { descricao:'Azulejista (piso)',       unidade:'h',   coef:0.8,  categoria:'Mão de Obra' },
  ],
  // 1 m² de revestimento cerâmico parede
  'revestimento_ceramica': [
    { descricao:'Cerâmica (padrão médio)', unidade:'m²',  coef:1.10, categoria:'Revestimentos' },
    { descricao:'Argamassa colante AC1',   unidade:'saco',coef:0.25, categoria:'Revestimentos' },
    { descricao:'Rejunte',                 unidade:'kg',  coef:0.35, categoria:'Revestimentos' },
    { descricao:'Azulejista (parede)',     unidade:'h',   coef:1.0,  categoria:'Mão de Obra' },
  ],
  // 1 m² de reboco
  'reboco_parede': [
    { descricao:'Cimento CP II 50kg',  unidade:'saco',coef:0.3,  categoria:'Revestimentos' },
    { descricao:'Areia média lavada',  unidade:'m³',  coef:0.02, categoria:'Revestimentos' },
    { descricao:'Cal hidratada',       unidade:'saco',coef:0.15, categoria:'Revestimentos' },
    { descricao:'Pedreiro (reboco)',   unidade:'h',   coef:0.5,  categoria:'Mão de Obra' },
  ],
  // 1 m² telhado colonial (incl. madeiramento)
  'telhado_colonial': [
    { descricao:'Telha colonial',      unidade:'un',  coef:14,   categoria:'Cobertura' },
    { descricao:'Caibro de madeira',   unidade:'m',   coef:3.0,  categoria:'Cobertura' },
    { descricao:'Ripa de madeira',     unidade:'m',   coef:5.0,  categoria:'Cobertura' },
    { descricao:'Cumeeira colonial',   unidade:'m',   coef:0.05, categoria:'Cobertura' },
    { descricao:'Carpinteiro (telha)', unidade:'h',   coef:0.5,  categoria:'Mão de Obra' },
  ],
}

function detectarComposicao(medicao: Medicao): string {
  const n = (medicao.nome + ' ' + (medicao.acabamento ?? '')).toLowerCase()
  const cat = (medicao.categoria ?? '').toLowerCase()

  if (cat === 'laje' || n.includes('laje'))      return 'laje_trelicada_12'
  if (n.includes('porcelanat'))                   return 'piso_porcelanato'
  if ((n.includes('piso') || n.includes('pi.')) && n.includes('cerâm')) return 'piso_ceramica'
  if (n.includes('revestiment') || (n.includes('parede') && n.includes('cerâm'))) return 'revestimento_ceramica'
  if (n.includes('reboc') || (n.includes('parede') && !n.includes('cerâm'))) return 'reboco_parede'
  if (cat === 'alvenaria' || n.includes('alvena') || n.includes('bloco')) return 'alvenaria_bloco_9'
  if (n.includes('telha') || n.includes('cobert') || cat === 'cobertura') return 'telhado_colonial'
  return ''
}

export function calcQuantitativos(medicoes: Medicao[]): QuantitativoItem[] {
  const itens: QuantitativoItem[] = []

  for (const m of medicoes) {
    // Concreto in loco — usa a função de traço
    const cat = (m.categoria ?? '').toLowerCase()
    if (cat === 'concreto' || cat === 'fundação' || cat === 'estrutura') {
      const fck = m.fck ?? 25
      const insumos = calcInsumos(fck, m.valor_calculado)
      if (insumos) {
        itens.push({ descricao:'Cimento CP II 50kg', quantidade_calculada:insumos.cimento_sacos,
          unidade:'saco', categoria:'Estrutura', medicao_id:m.id,
          traco_descricao: insumos.traco.traco_volume, fck_referencia:fck })
        itens.push({ descricao:'Areia média lavada', quantidade_calculada:insumos.areia_m3,
          unidade:'m³', categoria:'Estrutura', medicao_id:m.id })
        itens.push({ descricao:'Brita 1', quantidade_calculada:insumos.brita_m3,
          unidade:'m³', categoria:'Estrutura', medicao_id:m.id })
        itens.push({ descricao:'Pedreiro (concreto)', quantidade_calculada:+(m.valor_calculado*3).toFixed(1),
          unidade:'h', categoria:'Mão de Obra', medicao_id:m.id })
      }
      continue
    }

    // Elementos com tabela de composição
    const comp = detectarComposicao(m)
    const tabela = COMPOSICOES[comp]
    if (!tabela) continue

    for (const linha of tabela) {
      itens.push({
        descricao: linha.descricao,
        quantidade_calculada: +(m.valor_calculado * linha.coef).toFixed(2),
        unidade: linha.unidade,
        categoria: linha.categoria,
        medicao_id: m.id,
      })
    }
  }

  // Consolidar itens com mesma descrição
  const consolidado: Record<string, QuantitativoItem> = {}
  for (const item of itens) {
    if (consolidado[item.descricao]) {
      consolidado[item.descricao].quantidade_calculada =
        +(consolidado[item.descricao].quantidade_calculada + item.quantidade_calculada).toFixed(2)
    } else {
      consolidado[item.descricao] = { ...item }
    }
  }

  return Object.values(consolidado)
}
```

- [ ] **Step 9.4 — Rodar testes (deve passar)**

```bash
npx jest lib/calc/quantitativos.test.ts
# Expected: PASS — 2 testes passando
```

- [ ] **Step 9.5 — Página de quantitativos**

```tsx
// app/(dashboard)/obras/[id]/quantitativos/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { calcQuantitativos, type QuantitativoItem } from '@/lib/calc/quantitativos'
import type { Medicao } from '@/lib/types'
import { List, ArrowRight, Pencil } from 'lucide-react'

export default function QuantitativosPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [medicoes,  setMedicoes]  = useState<Medicao[]>([])
  const [itens,     setItens]     = useState<QuantitativoItem[]>([])
  const [ajustes,   setAjustes]   = useState<Record<string, number>>({})
  const [salvando,  setSalvando]  = useState(false)

  const supabase = createClient()

  useEffect(() => {
    async function init() {
      const { data } = await supabase.from('medicoes').select('*').eq('obra_id', params.id)
      const ms = data ?? []
      setMedicoes(ms)
      setItens(calcQuantitativos(ms))
    }
    init()
  }, [])

  const grupos = itens.reduce((acc, i) => {
    if (!acc[i.categoria]) acc[i.categoria] = []
    acc[i.categoria].push(i)
    return acc
  }, {} as Record<string, QuantitativoItem[]>)

  async function salvarEIrParaOrcamento() {
    setSalvando(true)
    // Deletar quantitativos anteriores desta obra
    await supabase.from('quantitativos').delete().eq('obra_id', params.id)
    // Inserir novos
    const rows = itens.map(i => ({
      obra_id: params.id,
      medicao_id: i.medicao_id,
      descricao: i.descricao,
      quantidade_calculada: i.quantidade_calculada,
      unidade: i.unidade,
      ajuste_manual: ajustes[i.descricao] ?? null,
      traco_descricao: i.traco_descricao,
      fck_referencia: i.fck_referencia,
    }))
    await supabase.from('quantitativos').insert(rows)
    setSalvando(false)
    router.push(`/obras/${params.id}/orcamento`)
  }

  const totalItens = itens.length

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="font-heading text-xl font-bold">Quantitativos</h2>
          <p className="text-dlima-muted text-sm">{totalItens} insumos calculados</p>
        </div>
        <button onClick={salvarEIrParaOrcamento} disabled={salvando || itens.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-dlima-gold text-dlima-dark
                     font-semibold rounded-lg hover:bg-dlima-gold-light text-sm disabled:opacity-50">
          {salvando ? 'Salvando...' : <><List size={15}/> Gerar Orçamento <ArrowRight size={15}/></>}
        </button>
      </div>

      {itens.length === 0 ? (
        <div className="text-center py-16 text-dlima-muted">
          <List size={40} className="mx-auto mb-3 opacity-30" />
          <p>Nenhuma medição encontrada.</p>
          <button onClick={() => router.push(`/obras/${params.id}/takeoff`)}
            className="mt-4 text-dlima-gold text-sm underline">
            Ir para Takeoff Digital
          </button>
        </div>
      ) : (
        Object.entries(grupos).map(([cat, catItens]) => (
          <div key={cat} className="mb-6">
            <h3 className="text-dlima-gold text-xs font-semibold uppercase tracking-wider mb-2">{cat}</h3>
            <div className="bg-dlima-surface border border-dlima-border rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-dlima-border">
                    <th className="text-left px-4 py-2 text-dlima-muted font-medium">Material / Serviço</th>
                    <th className="text-right px-4 py-2 text-dlima-muted font-medium w-28">Qtd. Calc.</th>
                    <th className="text-right px-4 py-2 text-dlima-muted font-medium w-24">Ajuste</th>
                    <th className="text-left px-4 py-2 text-dlima-muted font-medium w-16">Unid.</th>
                  </tr>
                </thead>
                <tbody>
                  {catItens.map((item, idx) => (
                    <tr key={item.descricao}
                        className={idx < catItens.length-1 ? 'border-b border-dlima-border/50' : ''}>
                      <td className="px-4 py-2.5">
                        <p className="text-dlima-text">{item.descricao}</p>
                        {item.traco_descricao && (
                          <p className="text-dlima-muted text-xs">Traço: {item.traco_descricao}</p>
                        )}
                      </td>
                      <td className="px-4 py-2.5 text-right text-dlima-gold font-medium">
                        {item.quantidade_calculada.toFixed(2)}
                      </td>
                      <td className="px-4 py-2.5">
                        <input
                          type="number" step="0.01"
                          value={ajustes[item.descricao] ?? ''}
                          onChange={e => setAjustes(a => ({
                            ...a, [item.descricao]: parseFloat(e.target.value)
                          }))}
                          placeholder={item.quantidade_calculada.toFixed(2)}
                          className="w-full px-2 py-1 bg-dlima-dark border border-dlima-border rounded
                                     text-dlima-text text-xs text-right focus:outline-none focus:border-dlima-gold"
                        />
                      </td>
                      <td className="px-4 py-2.5 text-dlima-muted text-xs">{item.unidade}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
```

- [ ] **Step 9.6 — Commit**

```bash
git add .
git commit -m "feat: motor de quantitativos automático, página de revisão com ajuste manual"
```

---

---

## TASK 10 — Orçamento

**Files:**
- Create: `lib/calc/orcamento.ts`
- Create: `app/(dashboard)/obras/[id]/orcamento/page.tsx`

---

### Step 10.1 — Helper de geração e cálculo

```ts
// lib/calc/orcamento.ts
import type { Quantitativo, Material } from '@/lib/types'

/** Mapeamento categoria → etapa de obra */
export const CATEGORIA_ETAPA: Record<string, string> = {
  'Serviços Preliminares':        'Serviços Preliminares',
  'Fundação':                     'Fundação',
  'Estrutura':                    'Estrutura',
  'Alvenaria':                    'Alvenaria',
  'Cobertura':                    'Cobertura',
  'Impermeabilização':            'Impermeabilização',
  'Revestimentos':                'Revestimentos',
  'Pisos':                        'Pisos',
  'Esquadrias':                   'Esquadrias',
  'Pintura':                      'Pintura',
  'Instalações Elétricas':        'Instalações Elétricas',
  'Instalações Hidrossanitárias': 'Instalações Hidrossanitárias',
  'Louças e Metais':              'Louças e Metais',
  'Mão de Obra':                  'Mão de Obra',
}

export interface ItemGerado {
  material_id?:    string
  etapa:           string
  descricao:       string
  quantidade:      number
  unidade:         string
  preco_unitario:  number   // congelado no momento da geração
  total_item:      number
  ordem_exibicao:  number
}

/**
 * Gera lista de itens de orçamento a partir de quantitativos + tabela de preços.
 * O preco_unitario é copiado dos materiais neste momento e fica congelado.
 * Itens sem preço cadastrado são incluídos com preco_unitario = 0 (sinaliza falta de preço).
 */
export function gerarItens(
  quantitativos: Quantitativo[],
  materiais: Material[]
): ItemGerado[] {
  // índice por nome (busca case-insensitive)
  const idx = new Map(materiais.map(m => [m.nome.toLowerCase(), m]))

  return quantitativos.map((q, i) => {
    const mat = q.material ?? idx.get(q.descricao.toLowerCase())
    const qtd = q.ajuste_manual ?? q.quantidade_calculada
    const etapa = mat ? (CATEGORIA_ETAPA[mat.categoria] ?? 'Outros') : 'Outros'
    const preco = mat?.preco_unitario ?? 0

    return {
      material_id:    mat?.id,
      etapa,
      descricao:      q.descricao,
      quantidade:     qtd,
      unidade:        q.unidade,
      preco_unitario: preco,
      total_item:     qtd * preco,
      ordem_exibicao: i,
    }
  })
}

/** Calcula totais sem e com BDI */
export function calcTotais(itens: Pick<ItemGerado, 'total_item'>[], bdiPct: number) {
  const semBdi = itens.reduce((s, i) => s + i.total_item, 0)
  const comBdi = semBdi * (1 + bdiPct / 100)
  return { semBdi, comBdi }
}

/** Agrupa itens por etapa (preserva ordem de primeira aparição) */
export function agruparPorEtapa(itens: ItemGerado[]): Record<string, ItemGerado[]> {
  return itens.reduce((acc, item) => {
    if (!acc[item.etapa]) acc[item.etapa] = []
    acc[item.etapa].push(item)
    return acc
  }, {} as Record<string, ItemGerado[]>)
}
```

---

### Step 10.2 — Página de orçamento

```tsx
// app/(dashboard)/obras/[id]/orcamento/page.tsx
'use client'
import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import type { Orcamento, OrcamentoItem, Quantitativo, Material } from '@/lib/types'
import { gerarItens, calcTotais, agruparPorEtapa } from '@/lib/calc/orcamento'
import { ArrowLeft, Plus, FileText, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

const STATUS_CONFIG = {
  rascunho:  { label: 'Rascunho',  color: 'bg-dlima-border text-dlima-muted' },
  enviado:   { label: 'Enviado',   color: 'bg-blue-900/30 text-blue-400' },
  aprovado:  { label: 'Aprovado',  color: 'bg-green-900/30 text-green-400' },
  reprovado: { label: 'Reprovado', color: 'bg-red-900/30 text-red-400' },
  revisado:  { label: 'Revisado',  color: 'bg-yellow-900/30 text-yellow-400' },
} as const

type OrcStatus = keyof typeof STATUS_CONFIG

export default function OrcamentoPage() {
  const { id: obraId } = useParams<{ id: string }>()
  const supabase = createClient()

  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([])
  const [ativo,      setAtivo]      = useState<string | null>(null)
  const [itens,      setItens]      = useState<OrcamentoItem[]>([])
  const [bdi,        setBdi]        = useState(25)
  const [gerando,    setGerando]    = useState(false)
  const [semPreco,   setSemPreco]   = useState(0)
  const [etapasOpen, setEtapasOpen] = useState<Record<string, boolean>>({})

  const carregarLista = useCallback(async () => {
    const { data } = await supabase
      .from('orcamentos')
      .select('*')
      .eq('obra_id', obraId)
      .order('versao', { ascending: false })
    setOrcamentos((data as Orcamento[]) ?? [])
    if (data && data.length > 0 && !ativo) setAtivo(data[0].id)
  }, [obraId]) // eslint-disable-line react-hooks/exhaustive-deps

  const carregarItens = useCallback(async (orcId: string) => {
    const { data } = await supabase
      .from('orcamento_itens')
      .select('*')
      .eq('orcamento_id', orcId)
      .order('etapa')
      .order('ordem_exibicao')
    setItens((data as OrcamentoItem[]) ?? [])
    setBdi(orcamentos.find(o => o.id === orcId)?.bdi_pct ?? 25)
  }, [orcamentos]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { carregarLista() }, [carregarLista])
  useEffect(() => { if (ativo) carregarItens(ativo) }, [ativo, carregarItens])

  async function gerarNovoOrcamento() {
    setGerando(true)
    try {
      // 1. buscar quantitativos com material join
      const { data: quants } = await supabase
        .from('quantitativos')
        .select('*, material:materiais(*)')
        .eq('obra_id', obraId)
      if (!quants || quants.length === 0) {
        alert('Cadastre os quantitativos antes de gerar o orçamento.')
        return
      }

      // 2. buscar todos os materiais para cross-reference por nome
      const { data: mats } = await supabase.from('materiais').select('*')

      // 3. gerar itens
      const itensBrutos = gerarItens(quants as Quantitativo[], (mats as Material[]) ?? [])
      const semPrecoCount = itensBrutos.filter(i => i.preco_unitario === 0).length
      setSemPreco(semPrecoCount)

      // 4. calcular totais
      const proximaVersao = (orcamentos[0]?.versao ?? 0) + 1
      const { semBdi, comBdi } = calcTotais(itensBrutos, bdi)

      // 5. criar registro do orçamento
      const { data: novoOrc } = await supabase
        .from('orcamentos')
        .insert({
          obra_id:              obraId,
          versao:               proximaVersao,
          bdi_pct:              bdi,
          status:               'rascunho',
          valor_total_sem_bdi:  semBdi,
          valor_total_com_bdi:  comBdi,
        })
        .select()
        .single()

      if (!novoOrc) throw new Error('Falha ao criar orçamento')

      // 6. inserir itens
      if (itensBrutos.length > 0) {
        await supabase.from('orcamento_itens').insert(
          itensBrutos.map(item => ({ ...item, orcamento_id: novoOrc.id }))
        )
      }

      await carregarLista()
      setAtivo(novoOrc.id)
    } finally {
      setGerando(false)
    }
  }

  async function atualizarStatus(status: OrcStatus) {
    if (!ativo) return
    await supabase.from('orcamentos').update({ status }).eq('id', ativo)
    setOrcamentos(prev => prev.map(o => o.id === ativo ? { ...o, status } : o))
  }

  const orcAtivo = orcamentos.find(o => o.id === ativo)
  const grupos   = agruparPorEtapa(itens as unknown as Parameters<typeof agruparPorEtapa>[0])
  const { semBdi, comBdi } = calcTotais(itens, orcAtivo?.bdi_pct ?? bdi)

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Link href={`/obras/${obraId}`} className="inline-flex items-center gap-2 text-dlima-muted hover:text-dlima-text text-sm mb-6 transition-colors">
        <ArrowLeft size={16} /> Hub da Obra
      </Link>

      <div className="flex items-center justify-between mb-6">
        <h1 className="font-heading text-2xl font-bold text-dlima-text">Orçamento</h1>
        <button
          onClick={gerarNovoOrcamento}
          disabled={gerando}
          className="flex items-center gap-2 px-4 py-2 bg-dlima-gold text-dlima-dark font-semibold rounded-lg hover:bg-dlima-gold-light transition-colors text-sm disabled:opacity-50"
        >
          <Plus size={16} />
          {gerando ? 'Gerando...' : `Gerar v${(orcamentos[0]?.versao ?? 0) + 1}`}
        </button>
      </div>

      {/* Alerta de itens sem preço */}
      {semPreco > 0 && (
        <div className="flex items-center gap-3 p-3 mb-4 bg-yellow-900/20 border border-yellow-700/30 rounded-xl text-yellow-400 text-sm">
          <AlertTriangle size={16} className="flex-shrink-0" />
          {semPreco} {semPreco === 1 ? 'item sem preço cadastrado' : 'itens sem preço cadastrado'} — cadastre em <Link href="/precos" className="underline">Banco de Preços</Link>
        </div>
      )}

      {/* Tabs de versão */}
      {orcamentos.length > 0 && (
        <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
          {orcamentos.map(o => (
            <button
              key={o.id}
              onClick={() => setAtivo(o.id)}
              className={[
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
                ativo === o.id
                  ? 'bg-dlima-gold text-dlima-dark'
                  : 'bg-dlima-surface border border-dlima-border text-dlima-muted hover:border-dlima-gold/30',
              ].join(' ')}
            >
              <FileText size={14} />
              v{o.versao}
              <span className={['text-xs px-1.5 py-0.5 rounded-full', STATUS_CONFIG[o.status as OrcStatus]?.color ?? ''].join(' ')}>
                {STATUS_CONFIG[o.status as OrcStatus]?.label}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Detalhe do orçamento ativo */}
      {orcAtivo && (
        <>
          {/* Cabeçalho + controles */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1 p-4 bg-dlima-surface border border-dlima-border rounded-xl">
              <p className="text-dlima-muted text-xs mb-1">Emissão</p>
              <p className="text-dlima-text text-sm font-medium">
                {new Date(orcAtivo.data_emissao).toLocaleDateString('pt-BR')}
              </p>
            </div>
            <div className="flex-1 p-4 bg-dlima-surface border border-dlima-border rounded-xl">
              <p className="text-dlima-muted text-xs mb-1">BDI</p>
              <p className="text-dlima-text text-sm font-medium">{orcAtivo.bdi_pct}%</p>
            </div>
            <div className="flex-1 p-4 bg-dlima-surface border border-dlima-border rounded-xl">
              <label className="block text-dlima-muted text-xs mb-1">Status</label>
              <select
                value={orcAtivo.status}
                onChange={e => atualizarStatus(e.target.value as OrcStatus)}
                className="w-full bg-transparent text-dlima-text text-sm focus:outline-none"
              >
                {Object.entries(STATUS_CONFIG).map(([v, c]) => (
                  <option key={v} value={v}>{c.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Itens por etapa */}
          {Object.entries(grupos).map(([etapa, etapaItens]) => {
            const totalEtapa = etapaItens.reduce((s, i) => s + i.total_item, 0)
            const aberta = etapasOpen[etapa] !== false  // aberto por default
            return (
              <div key={etapa} className="mb-3 bg-dlima-surface border border-dlima-border rounded-xl overflow-hidden">
                <button
                  onClick={() => setEtapasOpen(prev => ({ ...prev, [etapa]: !aberta }))}
                  className="w-full flex items-center justify-between px-4 py-3 hover:bg-dlima-border/30 transition-colors"
                >
                  <span className="font-semibold text-sm text-dlima-text">{etapa}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-dlima-gold text-sm font-medium">
                      R$ {totalEtapa.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </span>
                    {aberta ? <ChevronUp size={16} className="text-dlima-muted" /> : <ChevronDown size={16} className="text-dlima-muted" />}
                  </div>
                </button>

                {aberta && (
                  <div className="border-t border-dlima-border">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-dlima-darker/50">
                          <th className="text-left px-4 py-2 text-dlima-muted font-medium">Descrição</th>
                          <th className="text-right px-4 py-2 text-dlima-muted font-medium w-24">Qtd</th>
                          <th className="text-left px-4 py-2 text-dlima-muted font-medium w-16">Un.</th>
                          <th className="text-right px-4 py-2 text-dlima-muted font-medium w-28">P. Unit.</th>
                          <th className="text-right px-4 py-2 text-dlima-muted font-medium w-32">Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        {etapaItens.map((item, i) => (
                          <tr key={item.id} className={i < etapaItens.length - 1 ? 'border-b border-dlima-border/40' : ''}>
                            <td className="px-4 py-2.5 text-dlima-text">
                              {item.descricao}
                              {item.preco_unitario === 0 && (
                                <span className="ml-2 text-yellow-500 text-xs">⚠ sem preço</span>
                              )}
                            </td>
                            <td className="px-4 py-2.5 text-dlima-muted text-right">{item.quantidade.toFixed(2)}</td>
                            <td className="px-4 py-2.5 text-dlima-muted">{item.unidade}</td>
                            <td className="px-4 py-2.5 text-dlima-muted text-right">
                              R$ {item.preco_unitario.toFixed(2)}
                            </td>
                            <td className="px-4 py-2.5 text-dlima-text text-right font-medium">
                              R$ {item.total_item.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )
          })}

          {/* Totais */}
          <div className="mt-6 p-6 bg-dlima-darker border border-dlima-border rounded-2xl">
            <div className="flex justify-between items-center mb-3 text-sm">
              <span className="text-dlima-muted">Subtotal (sem BDI)</span>
              <span className="text-dlima-text font-medium">
                R$ {semBdi.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="flex justify-between items-center mb-4 text-sm">
              <span className="text-dlima-muted">BDI ({orcAtivo.bdi_pct}%)</span>
              <span className="text-dlima-text font-medium">
                R$ {(comBdi - semBdi).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="flex justify-between items-center pt-4 border-t border-dlima-border">
              <span className="font-heading font-bold text-lg text-dlima-text">TOTAL</span>
              <span className="font-heading font-black text-2xl text-dlima-gold">
                R$ {comBdi.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </>
      )}

      {orcamentos.length === 0 && !gerando && (
        <div className="text-center py-16 border border-dashed border-dlima-border rounded-xl text-dlima-muted">
          <FileText size={40} className="mx-auto mb-3 opacity-30" />
          <p className="mb-2">Nenhum orçamento gerado ainda.</p>
          <p className="text-xs">Complete os quantitativos e clique em &quot;Gerar v1&quot;.</p>
        </div>
      )}
    </div>
  )
}
```

---

### Step 10.3 — Testar fluxo completo

```
1. Ter quantitativos cadastrados para uma obra (via Task 9)
2. Ter materiais com preço no Banco de Preços (Task 6)
3. Acessar /obras/[id]/orcamento → clicar "Gerar v1"
4. Verificar que os itens aparecem agrupados por etapa
5. Verificar totais (sem BDI e com BDI)
6. Mudar status para "Enviado"
7. Gerar v2 (deve criar nova versão preservando a v1)
```

---

### Step 10.4 — Commit

```bash
git add .
git commit -m "feat: módulo orçamento — geração automática, BDI, versões, status"
```

---

<!-- CONTINUA NA PARTE 4 -->
<!-- Status: Tasks 1-10 planejadas -->
<!-- Próximas: Task 11 (Cronograma Físico-Financeiro), Task 12 (PCI Caixa), Task 13 (PDF) -->
