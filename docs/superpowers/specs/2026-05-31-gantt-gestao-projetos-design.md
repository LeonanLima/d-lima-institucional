# D'LIMA ERP — Gestão de Projetos (Gantt MS Project) — Spec de Design

**Data:** 2026-05-31  
**Status:** Aprovado — pronto para implementação  
**Projeto:** `dlima-app` (Next.js 16 + Supabase)

---

## 1. Objetivo

Adicionar ao D'LIMA ERP um módulo de gestão de projetos equivalente ao MS Project, com:

- Gantt interativo por obra (WBS hierárquico, dependências, caminho crítico, recursos)
- Visão de portfólio (`/projetos`) com todas as obras numa linha do tempo única

O módulo é **aditivo** — o cronograma simples existente (`/obras/[id]/cronograma`) permanece intacto.

---

## 2. Rotas Novas

| Rota | Descrição |
|---|---|
| `/projetos` | Portfólio: timeline geral de todas as obras ativas |
| `/obras/[id]/gantt` | Gantt completo da obra |

O hub da obra (`/obras/[id]`) ganha um novo card **"Gestão de Projetos"** que aponta para `/obras/[id]/gantt`.

---

## 3. Banco de Dados

### 3.1 Tabelas novas (Supabase)

```sql
-- Tarefas do WBS
create table projeto_tarefas (
  id                  uuid primary key default gen_random_uuid(),
  obra_id             uuid references obras(id) on delete cascade,
  pai_id              uuid references projeto_tarefas(id) on delete cascade,
  nome                text not null,
  duracao_dias        int not null default 1,
  inicio_previsto     date,
  fim_previsto        date,
  inicio_real         date,
  fim_real            date,
  percentual_concluido numeric default 0 check (percentual_concluido between 0 and 100),
  eh_marco            boolean default false,
  ordem               int default 0,
  criado_em           timestamptz default now()
);

-- Dependências entre tarefas
create table projeto_dependencias (
  id                uuid primary key default gen_random_uuid(),
  tarefa_origem_id  uuid references projeto_tarefas(id) on delete cascade,
  tarefa_destino_id uuid references projeto_tarefas(id) on delete cascade,
  tipo              text default 'FS' check (tipo in ('FS','SS','FF','SF')),
  lag_dias          int default 0
);

-- Recursos da obra (pessoas / equipes)
create table projeto_recursos (
  id                    uuid primary key default gen_random_uuid(),
  obra_id               uuid references obras(id) on delete cascade,
  nome                  text not null,
  funcao                text,
  custo_hora            numeric default 0,
  horas_dia_disponivel  numeric default 8,
  calendario_json       jsonb  -- dias úteis, feriados
);

-- Alocações: quem faz o quê
create table projeto_alocacoes (
  id                   uuid primary key default gen_random_uuid(),
  tarefa_id            uuid references projeto_tarefas(id) on delete cascade,
  recurso_id           uuid references projeto_recursos(id) on delete cascade,
  percentual_alocacao  numeric default 100
);
```

### 3.2 RLS

Mesma política das outras tabelas: `for all to authenticated using (true) with check (true)`.

### 3.3 Tipos TypeScript (adições em `lib/types.ts`)

```ts
export type TipoDependencia = 'FS' | 'SS' | 'FF' | 'SF'

export interface ProjetoTarefa {
  id: string
  obra_id: string
  pai_id?: string
  filhos?: ProjetoTarefa[]        // montado no cliente
  nome: string
  duracao_dias: number
  inicio_previsto?: string
  fim_previsto?: string
  inicio_real?: string
  fim_real?: string
  percentual_concluido: number
  eh_marco: boolean
  ordem: number
  eh_critico?: boolean            // calculado pelo CPM
  folga_total?: number            // calculado pelo CPM
}

export interface ProjetoDependencia {
  id: string
  tarefa_origem_id: string
  tarefa_destino_id: string
  tipo: TipoDependencia
  lag_dias: number
}

export interface ProjetoRecurso {
  id: string
  obra_id: string
  nome: string
  funcao?: string
  custo_hora: number
  horas_dia_disponivel: number
  calendario_json?: object
}

export interface ProjetoAlocacao {
  id: string
  tarefa_id: string
  recurso_id: string
  percentual_alocacao: number
  recurso?: ProjetoRecurso
}
```

---

## 4. Algoritmos (`lib/gantt/`)

### 4.1 `calc-critical-path.ts`

Implementa o **CPM (Critical Path Method)**:

1. **Forward pass** — calcula `ES` (Early Start) e `EF` (Early Finish) de cada tarefa a partir das dependências
2. **Backward pass** — calcula `LS` (Late Start) e `LF` (Late Finish) a partir da data final do projeto
3. **Folga total** = `LS - ES` (tarefa crítica tem folga = 0)

```ts
export function calcCriticalPath(
  tarefas: ProjetoTarefa[],
  dependencias: ProjetoDependencia[]
): ProjetoTarefa[]  // retorna tarefas com eh_critico e folga_total preenchidos
```

### 4.2 `calc-dates.ts`

Propaga datas quando o usuário move/redimensiona uma barra:

```ts
export function propagarDatas(
  tarefaMovida: ProjetoTarefa,
  todas: ProjetoTarefa[],
  dependencias: ProjetoDependencia[]
): ProjetoTarefa[]  // retorna lista atualizada com novas datas
```

### 4.3 `calc-resource-load.ts`

Calcula % de ocupação por recurso por semana:

```ts
export function calcCargaRecursos(
  tarefas: ProjetoTarefa[],
  alocacoes: ProjetoAlocacao[],
  semana: Date
): Record<string, number>  // recurso_id → % utilização
```

---

## 5. Componentes (`components/gantt/`)

### 5.1 `wbs-table.tsx`
- Tabela hierárquica com indentação por nível (`pai_id`)
- Colunas: **Nome** | **Dias** | **%**
- Linha de tarefa crítica com borda esquerda vermelha
- Linha de sumário (pai) em dourado
- Drag-and-drop para reordenar (`@dnd-kit`)
- Botões: `+` subtarefa, `↑↓` mover nível, lixeira

### 5.2 `gantt-canvas.tsx`
- SVG gerado em React — uma `<rect>` por tarefa
- Escala: eixo X = tempo (dias), largura dinâmica
- Cores: dourado (sumário) · verde (normal) · vermelho (crítico) · cinza (concluído)
- **Drag horizontal**: move `inicio_previsto` + `fim_previsto`
- **Drag extremidade direita**: altera `duracao_dias`
- Linha vertical dourada = hoje
- Grid de semanas/meses no cabeçalho

### 5.3 `dependency-arrows.tsx`
- SVG overlay sobre o `gantt-canvas`
- Desenha setas curvas entre barras conforme tipo (FS/SS/FF/SF)
- Setas vermelhas nas dependências do caminho crítico

### 5.4 `task-panel.tsx`
- Painel lateral direito fixo (240px) — abre ao clicar numa tarefa
- Campos: Nome · Início · Fim · Duração · % Concluído · Predecessora · Tipo dep. · Recursos · Observação
- Seletor de recursos com chips
- Botão Salvar (persiste no Supabase) · Botão Excluir

### 5.5 `resource-strip.tsx`
- Faixa sempre visível abaixo do Gantt
- Uma linha por recurso: nome + barra de utilização + %
- Verde ≤ 85% · Amarelo 85–100% · Vermelho > 100% com ⚠

### 5.6 `portfolio-timeline.tsx`
- Página `/projetos`
- Cards resumo no topo: total ativas · no prazo · em risco · atrasadas
- Filtros: ano · status
- Linha por obra: nome/cliente à esquerda + barra de progresso colorida à direita
- Linha dourada vertical = hoje
- Clique na obra → navega para `/obras/[id]/gantt`

---

## 6. Página `/obras/[id]/gantt`

Layout em três camadas verticais:

```
┌─────────────────────────────────────────────────────┐
│  Header: nome da obra · botões importar / + tarefa  │
├───────────────────────────┬─────────────────────────┤
│  WBSTable (240px)         │  GanttCanvas + Arrows   │
│  Nome | Dias | %          │  SVG barras + setas      │
│                           │                          │
├───────────────────────────┴─────────────────────────┤
│  ResourceStrip — utilização por recurso              │
├─────────────────────────────────────────────────────┤
│  TaskPanel (240px lateral direita — abre ao clicar) │
└─────────────────────────────────────────────────────┘
```

**Fluxo de primeiro acesso:**
1. Verificar se existem `projeto_tarefas` para esta obra
2. Se não: mostrar dois botões — "Importar do Orçamento" e "Começar do Zero"
3. Importar do Orçamento: busca `orcamento_itens`, agrupa por etapa → cria tarefa de nível 1 para cada etapa, duração padrão de 7 dias
4. Começar do Zero: abre tabela vazia com botão `+ Adicionar tarefa`

---

## 7. Restrições e Comportamentos

- **Datas auto-calculadas**: ao mudar duração ou mover barra, `propagarDatas` atualiza dependentes automaticamente
- **CPM recalculado** a cada mudança de tarefa/dependência
- **Sobrecarga de recurso**: alerta visual (vermelho) quando `calcCargaRecursos > 100%`
- **Marco**: `eh_marco = true` renderiza diamante ♦ no lugar da barra
- **Lag em dependências**: suporte a `lag_dias` positivo (folga) ou negativo (sobreposição)
- **Scroll sincronizado**: WBSTable e GanttCanvas scrollam juntos verticalmente

---

## 8. Mapa de Implementação — 4 Fases / 9 Tasks

### Fase 1 — Fundação (sequencial)
- **T1** Schema Supabase + tipos TypeScript
- **T2** Algoritmos: `calcCriticalPath`, `propagarDatas`, `calcCargaRecursos`

### Fase 2 — Componentes (paralelo, 4 agentes)
- **T3** `WBSTable`
- **T4** `GanttCanvas` + `DependencyArrows`
- **T5** `TaskPanel`
- **T6** `ResourceStrip`

### Fase 3 — Páginas (paralelo, 2 agentes)
- **T7** Página `/obras/[id]/gantt` (integra componentes + importar orçamento)
- **T8** Página `/projetos` (portfólio)

### Fase 4 — Integração
- **T9** Card no hub da obra + testes ponta a ponta + deploy

---

## 9. Skills por Task

| Task | Skills |
|---|---|
| T1–T2 | `incremental-execution` |
| T3–T6 | `dispatching-parallel-agents` · `incremental-execution` · `verification-before-completion` |
| T7–T8 | `dispatching-parallel-agents` · `incremental-execution` |
| T9 | `systematic-debugging` · `verification-before-completion` |
