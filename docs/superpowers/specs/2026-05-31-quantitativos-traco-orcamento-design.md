# Quantitativos com Traço + Orçamento Manual — Design Spec

**Data:** 2026-05-31
**Módulo:** `dlima-app` → quantitativos, orçamento
**Status:** Aprovado para implementação

---

## 1. Fonte de dados — Apostila Alvenaria (Drive Leonan)

**Tabela 4.3 — Traço de argamassa em LATAS DE 18L (Apostila Alvenaria, conforme Carini):**

Rendimento por saco de cimento (50kg = 1.85 latas 18L):

| Serviço | Traço (cim:cal:areia) | Rend./saco | Rend./lata 18L cim | Junta/Esp. |
|---|---|---|---|---|
| Tijolo maciço | 1:2:8 | 10 m² | ~5.4 m² | junta 1cm |
| Tijolo furado/baiano | 1:2:8 | 16 m² | ~8.6 m² | junta 1cm |
| Bloco de concreto | 1:0.5:6 | 30 m² | ~16.2 m² | junta 1-2cm |
| Chapisco | 1:3 (sem cal) | ~8 m² | ~4.3 m² | 5mm |
| Emboço externo | 1:1:6 | ~4 m² | ~2.2 m² | 20mm |
| Emboço interno | 1:2:8 | ~5 m² | ~2.7 m² | 15mm |

**Por traçada (1 lata 18L de cimento):**
- Traço 1:2:8: 1 lata cimento + 2 latas cal + 8 latas areia + ~1 lata água (18L)
- Traço 1:3: 1 lata cimento + 3 latas areia + ~0.8 lata água (14L)
- Traço 1:0.5:6: 1 lata cimento + 0.5 lata cal + 6 latas areia + ~1 lata água (18L)

**Por m² (em latas de 18L) — tijolo furado:**
- Cimento: 0.12 lata · Cal: 0.23 lata · Areia: 0.93 lata · Água: ~0.09 lata (≈1.7L)

**Concreto armado in loco — LATAS DE 18L (por traçada, adicionar conforme volume):**

| fck | Traço (cim:areia:brita) | Água/lata cim |
|---|---|---|
| C15 | 1 lata : 3 latas : 4.5 latas | ~1 lata (18L) |
| C20 | 1 lata : 2.5 latas : 3.5 latas | ~0.9 lata (16L) |
| C25 | 1 lata : 2 latas : 3 latas | ~0.8 lata (14L) |
| C30 | 1 lata : 1.5 latas : 2.5 latas | ~0.7 lata (13L) |

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
  Traço: 1 lata cimento (18L) : 2 latas cal : 8 latas areia : ~1 lata água (por traçada)
  Por m²: 0.12 lata cimento · 0.23 lata cal · 0.93 lata areia · ~0.09 lata água
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
