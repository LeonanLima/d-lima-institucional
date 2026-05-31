# Quantitativos com Traço + Orçamento Manual — Design Spec

**Data:** 2026-05-31
**Módulo:** `dlima-app` → quantitativos, orçamento
**Status:** Aprovado para implementação

---

## 1. Fonte de dados — Apostila Alvenaria (Drive Leonan)

**Tabela 4.3 — Traço de argamassa em baldes de 12L (adaptado da apostila latas 18L, mesmas proporções):**

| Serviço | Traço (cim:cal:areia) | Rend./saco cimento | Junta/Esp. |
|---|---|---|---|
| Tijolo maciço | 1:2:8 | 10 m² | junta 1cm |
| Tijolo furado/baiano | 1:2:8 | 16 m² | junta 1cm |
| Bloco de concreto | 1:0.5:6 | 30 m² | junta 1-2cm |
| Chapisco | 1:3 (sem cal) | ~8 m² | 5mm |
| Emboço externo | 1:1:6 | ~4 m² | 20mm |
| Emboço interno | 1:2:8 | ~5 m² | 15mm |

**Por m² (balde de 12L):**
- Tijolo furado 1:2:8: 0.17 balde cim + 0.34 balde cal + 1.37 balde areia + ~1.4L água
- Tijolo maciço 1:2:8: 0.27 balde cim + 0.54 balde cal + 2.2 balde areia
- Chapisco 1:3: 0.33 balde cim + 1.0 balde areia

**Concreto armado in loco (por m³) — baldes de 12L:**

| fck | Traço | Cim | Areia | Brita | Água |
|---|---|---|---|---|---|
| C15 | 1:3:4.5 | 1 balde | 3 baldes | 4.5 baldes | 0.6L/kg cim |
| C20 | 1:2.5:3.5 | 1 balde | 2.5 baldes | 3.5 baldes | 0.55L/kg cim |
| C25 | 1:2:3 | 1 balde | 2 baldes | 3 baldes | 0.5L/kg cim |
| C30 | 1:1.5:2.5 | 1 balde | 1.5 baldes | 2.5 baldes | 0.45L/kg cim |

---

## 2. Produtividade (TCPO / padrão mercado ES)

| Serviço | Oficial (h/m²) | Servente (h/m²) |
|---|---|---|
| Alvenaria tijolo furado | 0.70 | 0.35 |
| Alvenaria tijolo maciço | 0.90 | 0.45 |
| Chapisco | 0.15 | 0.10 |
| Emboço/reboco | 0.50 | 0.25 |
| Cerâmica parede | 1.00 | 0.40 |
| Porcelanato piso | 1.00 | 0.40 |
| Cerâmica piso | 0.85 | 0.35 |
| Concreto (por m³) | 3.00 | 3.00 |

Jornada padrão: 8h/dia.

---

## 3. Módulo Quantitativos — Mudanças

### 3.1 Novo campo: Traço por serviço

Cada item de quantitativo que possui argamassa exibe, na linha expandida:

```
▼ Alvenaria tijolo furado — 24.5 m²
  Traço: 1 balde cimento : 2 baldes cal : 8 baldes areia (por traçada de 12L)
  Por m²: 0.17 balde cimento · 0.34 balde cal · 1.37 balde areia · 1.4L água
  ⭐ Definir como traço favorito para este serviço
```

### 3.2 Traço favorito por serviço

- Botão ⭐ salva no `localStorage` o ID do traço escolhido para cada serviço
- Na próxima obra, o favorito é pré-selecionado automaticamente
- Tipo de dado: `Map<servicoId, tracoId>`

### 3.3 Estimativa de tempo

Seção "⏱ Estimativa de produção" ao final da página de quantitativos:

```
Serviço: Alvenaria tijolo furado — 24.5 m²
  Oficial (pedreiro):    17.2 h    ≈ 2.1 dias
  Com ajudante:          17.2 + 8.6 = 25.8 h  → equipe termina em 1.6 dias
```

Fórmula:
- horas_oficial = area_m2 × produtividade_oficial_h_m2
- dias_solo = horas_oficial / 8
- dias_com_ajudante = horas_oficial / (8 + produtividade_servente_h_m2 × area_m2 / horas_oficial × 8)
- Simplificado: dias_equipe = horas_oficial / 8 → mas equipe produz mais → dias_equipe = area_m2 / ((8/oficial + 8/servente) × colaboradores_por_dia)

Fórmula final simples:
- Sem ajudante: dias = (area × h_oficial) / 8
- Com ajudante: dias = (area × h_oficial) / 8 (oficial produz igual, ajudante libera o oficial → assume ganho de 30%)

---

## 4. Módulo Orçamento — Mudanças

### 4.1 Edição de preço inline

Cada linha do orçamento ganha botão ✏️. Ao clicar:
- Campo de input substitui o preço unitário
- Botão ✓ confirma, Esc cancela
- Recalcula total_item e total_obra

### 4.2 Adicionar item manual

Botão "+ Adicionar item" no cabeçalho. Modal com:
- Etapa (dropdown: Serviços Preliminares, Fundação, Estrutura, Alvenaria, Cobertura, etc.)
- Descrição (text)
- Quantidade (number)
- Unidade (dropdown: m², m³, m, un, kg, saco, h)
- Preço unitário (number)
- Salva direto na tabela `orcamento_itens` sem precisar de takeoff

---

## 5. Arquivos Alterados

```
dlima-app/
├── lib/calc/
│   ├── quantitativos.ts       ← adicionar TRACOS_SERVICO e calcTracosPorM2
│   └── produtividade.ts       ← CRIAR: tabela h/m² e cálculo de dias
├── app/(dashboard)/obras/[id]/
│   ├── quantitativos/page.tsx ← expandir rows com traço + estimativa de tempo
│   └── orcamento/page.tsx     ← edição inline + modal de item manual
└── lib/
    └── tracos-favoritos.ts    ← CRIAR: get/set favoritos no localStorage
```

---

## 6. Checklist de Testes

- [ ] Abrir Quantitativos de obra com alvenaria → traço 1:2:8 aparece expandido
- [ ] Clicar ⭐ → traço salvo como favorito; próxima obra pré-seleciona
- [ ] Estimativa de tempo mostra dias corretos para area real medida
- [ ] Orçamento: clicar ✏️ → campo editável → confirmar → preço e total atualizados
- [ ] Orçamento: "Adicionar item" → modal → preencher → item aparece na lista
- [ ] Concreto C25 mostra baldes cim:areia:brita:água corretos
