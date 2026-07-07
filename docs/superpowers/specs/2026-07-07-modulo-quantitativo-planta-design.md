# Módulo Quantitativo — ERP D'LIMA
**Spec de design — 2026-07-07**
**Status:** aprovada pelo Leonan em 2026-07-07

Upload de planta baixa → extração de geometria → conferência visual → parâmetros de engenharia → planilha de quantidades estilo SINAPI (composição própria) + lista de compra + cronograma executivo da obra.

> Nota de localização: esta spec nasce no repo `d-lima-institucional`, mas o módulo será implementado no repositório do ERP D'LIMA (app.dlimaengenharia.org). Mover/copiar a spec para lá quando a implementação começar.

---

## 1. Decisões da entrevista

| Decisão | Escolha |
|---|---|
| Formatos de entrada | DWG/DXF (via conversão), PDF vetorial, Revit/IFC. **Sem foto/escaneado** |
| Onde mora | Módulo do ERP D'LIMA (Supabase, login e estrutura SINAPI existentes) |
| Escopo v1 | Alvenaria + revestimentos; concreto armado; pisos/contrapiso/cerâmica; pintura + esquadrias |
| Fluxo | Extrai → usuário confere na tela (overlay editável) → só então calcula |
| Planilha | Estilo SINAPI, composições próprias editáveis, **só quantidades** (preço fica para fase futura) |
| Tipo de obra | Térrea + sobrado (até 2 pavimentos, com escada e laje entre pavimentos) |
| Motor de leitura | Determinístico (geometria 100% do arquivo) + IA apenas para classificar entidades ambíguas. **Medida nunca vem de IA** |
| Extra | Cronograma executivo da obra por etapas, com quantitativo, duração (1 pedreiro + 1 ajudante) e checklist |

## 2. Contexto de mercado (varredura 2026-07-07)

- **Brasil** (Vobi, OrçaFascio, i9 Orçamentos, Concretu, eCustos, Sienge): fortes em orçamento/planilha SINAPI, mas **nenhum extrai quantitativo automaticamente da planta** — o usuário digita medidas. A extração automática é o diferencial.
- **Exterior** (Togal.AI, Kreo, Beam AI, Civils.ai, PlanSwift): takeoff automático com IA já é maduro — prova de viabilidade — mas são SaaS em dólar, sem SINAPI, sem traço NBR, sem fluxo brasileiro de compra.

## 3. Reaproveitamento

| Fonte | O que reaproveita |
|---|---|
| `C:\Users\leona\dlima-estrutural` | Materiais NBR 6118 (fck, classes), bitolas e massas de aço, elementos, normas — vira o núcleo de concreto/aço do motor de cálculo (185 testes existentes) |
| `C:\Users\leona\MUSSO` | Fórmulas e valores golden para validação cruzada dos cálculos de concreto |
| ERP D'LIMA | Supabase, autenticação, estrutura de tabelas SINAPI pendente |
| `C:\Users\leona\dlima-obras` | Padrões FastAPI (auth JWT, Alembic, deploy Render) |
| Open source | `ezdxf` (DXF), ODA File Converter (DWG→DXF, grátis), `PyMuPDF` (PDF vetorial), `IfcOpenShell` (IFC) |

## 4. Arquitetura

```
Upload ─► [1] EXTRAÇÃO ─► [2] CLASSIFICAÇÃO IA ─► [3] CONFERÊNCIA ─► [4] MOTOR DE CÁLCULO ─► [5] SAÍDAS
```

### 4.1 Serviço de extração (Python/FastAPI)
Três parsers desembocam num modelo único:

- **DXF:** DWG convertido via ODA File Converter → `ezdxf` lê polylines, blocos (portas/janelas), textos e cotas, usando camadas quando existirem.
- **PDF vetorial:** `PyMuPDF` extrai paths vetoriais + textos; heurísticas detectam paredes (pares de linhas paralelas com espessura típica) e escala (a partir das cotas).
- **IFC:** `IfcOpenShell` entrega paredes, aberturas e ambientes com quantidades quase prontas.

**Modelo normalizado `PlantaNormalizada`:**
- `Pavimento` (nome, pé-direito — informado pelo usuário na conferência)
- `Parede` (comprimento, espessura, pavimento, faces interna/externa)
- `Abertura` (porta/janela, largura × altura, parede associada)
- `Ambiente` (nome, área, perímetro, pavimento)
- `Escada` (quando sobrado)

### 4.2 Classificação IA (Claude API)
Acionada apenas quando o arquivo não traz semântica (camadas bagunçadas, PDF sem padrão). Recebe as entidades geométricas extraídas e devolve rótulos: parede / porta / janela / nome de ambiente. Restrição dura: a IA **classifica**, nunca mede. Toda medida vem do arquivo.

### 4.3 Tela de conferência
Planta renderizada em SVG no navegador com overlay do que foi detectado. O usuário:
- corrige/remove/adiciona paredes e aberturas;
- informa pé-direito por pavimento;
- nomeia ambientes não identificados;
- confirma para liberar o cálculo.

### 4.4 Motor de cálculo (Python puro, TDD)

| Serviço | Regra |
|---|---|
| Alvenaria | Área = Σ(comprimento × pé-direito) − aberturas; blocos/m² pela dimensão escolhida + junta informada; argamassa de assentamento em função da junta; perda configurável (padrão 5–10%) |
| Chapisco/emboço/reboco | Por face (interna/externa) × espessura informada → volume de argamassa → traço → cimento/cal/areia |
| Concreto armado | Usuário informa seções e armadura (ou pré-dimensiona via dlima-estrutural); volume → **traço por fck via tabela ABCP / NBR 12655** (NBR 6118 define a classe; a dosagem vem do método ABCP) → cimento/areia/brita; aço em kg por bitola |
| Contrapiso + cerâmica | Área dos ambientes → contrapiso por espessura, placas + rejunte |
| Pintura | Paredes/tetos − aberturas → selador, massa, tinta por demãos |
| Esquadrias | Contagem por tipo e dimensão extraída |
| Tempo | Coeficientes de produtividade SINAPI (h/m² ou h/m³) → duração por etapa e total, equipe fixa de 1 pedreiro + 1 ajudante |

**Catálogo de blocos (lista para o usuário escolher):** tijolo cerâmico 9×19×19, 11,5×19×24, 14×19×29; bloco de concreto 9/14/19×19×39; lajota cerâmica; extensível via cadastro.

**Composições próprias:** tabela editável no Supabase (serviço → insumos, coeficiente, unidade), estilo SINAPI. Usuário ajusta coeficientes com a realidade das próprias obras.

### 4.5 Saídas
- Planilha estilo SINAPI por serviço (tela + export Excel via openpyxl)
- Lista de compra consolidada (sacos de cimento, milheiros de tijolo, m³ de areia/brita, latas de tinta…)
- Cronograma executivo: fundação → alvenaria → laje → cobertura → revestimento → piso → pintura, cada etapa com quantitativo, duração e checklist de itens para não esquecer

### 4.6 Persistência (Supabase)
Tabelas novas: `qtv_obras`, `qtv_plantas`, `qtv_extracoes` (JSON do modelo normalizado + correções do usuário), `qtv_composicoes`, `qtv_insumos`, `qtv_parametros` (bloco escolhido, junta, fck, espessuras), `qtv_resultados`.

## 5. Fluxo de uso

1. Criar obra → upload da(s) planta(s) (térreo e superior, se sobrado)
2. Conferir extração na tela; informar pé-direito
3. Responder parâmetros: bloco (lista), junta de assentamento, espessuras chapisco/emboço/reboco por face, fck, seções + armadura dos elementos de concreto
4. Ver planilha de quantidades + lista de compra
5. Ver cronograma executivo com etapas, durações (1+1) e checklists

## 6. Fases de construção

| Fase | Entrega | Valor |
|---|---|---|
| 1 | Motor de cálculo completo com entrada manual de medidas (composições, traços, tempo, planilha, lista de compra) | Ferramenta já usável em obra real; 100% testável com golden values |
| 2 | Parser DXF + tela de conferência visual | Automatiza o caso mais preciso |
| 3 | Parser PDF vetorial + classificador IA | Cobre o formato mais comum recebido de arquitetos |
| 4 | IFC + cronograma executivo com checklist completo | Fecha o escopo v1 |

Execução em fatias pequenas com commit após cada uma (padrão incremental já adotado).

## 7. Testes

- TDD no motor de cálculo; golden values de uma obra real do Leonan conferida à mão
- Validação cruzada com MUSSO nos cálculos de concreto
- Fixtures de plantas reais (DXF e PDF) para os parsers
- Cobertura mínima 80%

## 8. Fora de escopo da v1

- Preços/orçamento em R$ (fase futura: preço próprio cadastrado e/ou SINAPI de referência)
- Foto/planta escaneada (exigiria IA de visão medindo — vetado por precisão)
- Mais de 2 pavimentos, edificações comerciais
- Fundação e cobertura quantificadas a partir da planta (entram no cronograma executivo como etapas com checklist; quantitativo delas depende de projetos específicos)
- Instalações elétricas/hidráulicas
