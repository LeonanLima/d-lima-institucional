# Spec — Motor de Análise Estrutural (Fase 1)

**Data:** 2026-06-01  
**Status:** Aprovado para implementação  
**Escopo:** Engine de análise estrutural pelo Método da Rigidez com dimensionamento NBR 6118:2023, output educativo Carini paralelo, matrizes coloridas e desenhos SVG de detalhamento

---

## 1. Objetivo

Um endpoint Flask que recebe uma estrutura em JSON (nós, elementos, vínculos, cargas) e retorna um relatório HTML + JSON com:
- Matrizes de rigidez elementares e global com código de cores por elemento
- Passo a passo do cálculo manual seguindo a sequência Carini
- Deslocamentos, rotações, reações, diagramas M/V/N
- Flecha imediata e diferida
- Dimensionamento completo (As, Asw, pele) com bitola e quantidade por região
- Desenhos SVG: seção transversal e elevação/planta com armaduras posicionadas
- Avisos automáticos quando resultados saem dos parâmetros NBR 6118

---

## 2. Arquitetura

### Pipeline sequencial

```
POST /api/estrutura (JSON)
        ↓
[1] Parsear modelo (nós, elementos, vínculos, cargas)
        ↓
[2] Montar K_e por elemento → K_global (numpy)
        ↓
[3] Aplicar condições de contorno → resolver [K]{u}={F}
        ↓
[4] Pós-processar: reações, N/V/M por elemento, flechas
        ↓
[5] Dimensionar cada elemento (NBR 6118:2023)
        ↓
[6] Detalhar: bitola, quantidade, zonas de estribo
        ↓
[7] Gerar SVG: seção transversal + elevação
        ↓
[8] Montar output Carini (passo a passo com valores reais)
        ↓
GET /api/relatorio/<id> → HTML renderizado
```

### Arquivos

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Rotas Flask `/api/estrutura` e `/api/relatorio/<id>` |
| `engine/modelo.py` | Dataclasses: No, Elemento, Vinculo, Carga, Estrutura |
| `engine/rigidez.py` | Matrizes K_e, transformação T, montagem K_global |
| `engine/solver.py` | Condições de contorno, solução numpy, reações, M/V/N |
| `engine/dimensionamento.py` | NBR 6118: cortante, flexão, flecha, fissuração |
| `engine/detalhamento.py` | Escolha de bitola, contagem de barras, zonas estribo |
| `engine/svg_secao.py` | SVG da seção transversal com armaduras |
| `engine/svg_elevacao.py` | SVG da elevação/planta com zonas e ancoragem |
| `engine/relatorio.py` | Montar output JSON + HTML educativo Carini |
| `templates/relatorio.html` | Template Jinja2 com matrizes coloridas e SVG inline |
| `tests/test_engine.py` | Testes pytest: pórtico simples com resultado analítico |

---

## 3. Input — Schema JSON

```json
{
  "estrutura": {
    "material": {
      "fck": 25,
      "fyk": 500,
      "CAA": 2,
      "agregado": "basalto"
    },
    "nos": [
      { "id": 1, "x": 0.0, "y": 0.0, "z": 0.0 },
      { "id": 2, "x": 0.0, "y": 3.0, "z": 0.0 },
      { "id": 3, "x": 5.0, "y": 3.0, "z": 0.0 }
    ],
    "elementos": [
      {
        "id": "P1",
        "tipo": "pilar",
        "no_i": 1,
        "no_j": 2,
        "secao": { "bw": 19, "h": 19 },
        "cor": "#3b82f6"
      },
      {
        "id": "V1",
        "tipo": "viga",
        "no_i": 2,
        "no_j": 3,
        "secao": { "bw": 14, "h": 40 },
        "cor": "#22c55e"
      }
    ],
    "vinculos": [
      {
        "no": 1,
        "ux": true, "uy": true, "uz": true,
        "rx": true, "ry": true, "rz": true
      }
    ],
    "cargas": [
      {
        "elemento": "V1",
        "tipo": "distribuida",
        "valor": 15.2,
        "direcao": "y",
        "unidade": "kN/m"
      },
      {
        "no": 2,
        "tipo": "nodal",
        "fx": 0, "fy": -10.0, "mz": 0,
        "unidade": "kN"
      }
    ]
  }
}
```

**Tipos de elemento:** `fundacao`, `pilar`, `viga`, `laje`  
**Tipos de vínculo por GDL:** `true` = restrito (reação gerada), `false` = livre  
**Tipos de carga:** `distribuida` (kN/m), `concentrada` (kN), `nodal` (kN, kNm)  
**Campo `cor`:** hex opcional — se omitido, atribuído automaticamente por ordem

---

## 4. Motor de Análise (Método da Rigidez)

### 4.1 Graus de liberdade

**Pórtico plano 2D:** 3 GDL por nó — `[ux, uy, rz]`  
**Extensão 3D (fase futura):** 6 GDL por nó — `[ux, uy, uz, rx, ry, rz]`  

GDL global numerado sequencialmente: nó 1 → GDL 1,2,3; nó 2 → GDL 4,5,6; etc.

### 4.2 Matriz de rigidez elementar (sistema local, 2D)

Para viga-coluna com seção retangular:

```
       EA/L    0        0      -EA/L    0        0
       0    12EI/L³   6EI/L²    0    -12EI/L³  6EI/L²
k_e =  0     6EI/L²  4EI/L     0     -6EI/L²  2EI/L
      -EA/L   0        0       EA/L    0        0
       0   -12EI/L³  -6EI/L²   0     12EI/L³  -6EI/L²
       0     6EI/L²  2EI/L     0     -6EI/L²  4EI/L

Com:
  E   = Ecs (módulo secante) = αi × αE × 5600 × √fck  [kN/cm²]
  I   = bw × h³ / 12  [cm⁴]
  A   = bw × h         [cm²]
  L   = comprimento do elemento [cm]
```

### 4.3 Transformação local → global

```python
T = matriz de rotação 6×6
  θ = arctan((yj−yi)/(xj−xi))  # ângulo do elemento
K_global_e = T.T @ k_e @ T
```

### 4.4 Montagem da K_global

Cada K_global_e acumulado nas posições corretas da K_global `(n_gdl × n_gdl)` conforme GDLs do elemento. Registrar qual elemento contribui para cada célula (para coloração).

### 4.5 Condições de contorno e solução

```python
# Particionar K em livres (f) e restritos (r)
K_ff, K_fr, K_rr = particionar(K_global, gdl_livres, gdl_restritos)

# Resolver: K_ff × u_f = F_f − K_fr × u_r
u_f = numpy.linalg.solve(K_ff, F_f - K_fr @ u_r)

# Reações nos apoios
R = K_global @ u_total − F_total
```

### 4.6 Esforços internos

Para cada elemento, 10 seções ao longo do comprimento:

```python
u_e = T @ u_global[gdls_elemento]  # deslocamentos no sistema local
f_e = k_e @ u_e                     # forças internas nos nós

# Diagramas: N(x), V(x), M(x) para x em [0, L]
N(x) = f_e[0] + carga_axial_distribuida(x)
V(x) = f_e[1] + carga_transversal_distribuida(x)
M(x) = f_e[2] − V(x)·x + momento_distribuido(x)
```

### 4.7 Flecha

```python
# Flecha imediata (Branson)
Ie = (Mr/Ma)³·Ig + (1−(Mr/Ma)³)·Iii
δ_imediata = 5·q·L⁴ / (384·Ecs·Ie)   # mm

# Flecha diferida
δ_diferida = δ_imediata × (1 + φ)     # φ = 2,5

# Limite NBR 6118
δ_lim = L / 250   # mm
```

---

## 5. Dimensionamento (NBR 6118:2023)

### 5.1 Vigas — Cisalhamento (Modelo I)

```
αv2 = 1 − fck/250
fcd = fck/1,4/10              [kN/cm²]
fctd = 0,15×fck^(2/3)/10     [kN/cm²]
d   = h − cnom − φ_est − φ_long/2

VRd2 = 0,27×αv2×fcd×bw×d    → se VSd > VRd2: ERRO "aumentar seção"
Vc   = 0,6×fctd×bw×d

# Zonas de estribo (3 zonas: apoio_esq, meio, apoio_dir)
# Limites das zonas: 2d a partir de cada apoio
Para cada zona:
  Asw/s = max(Asw/s_min, (VSd_zona − Vc)/(0,9d×fywd))
  Bitola, espaçamento, quantidade = escolher_estribo(Asw/s, bw, d)
```

### 5.2 Vigas — Flexão

```
Md,duc = 0,85×fcd×0,80×(0,45d)×bw×(d − 0,80×(0,45d)/2)

Se Md ≤ Md,duc:  # armadura simples
  x = 1,25d × [1 − √(1 − Md/(0,425×bw×d²×fcd))]
  As = 0,85×fcd×0,80×x×bw / fyd

Se Md > Md,duc:  # armadura dupla
  As2 = (Md − Md,duc) / (σs2×(d − d'))
  As1 = (αc×fcd×λ×x_duc×bw + As2×σs2) / fyd

Armadura mínima: As_min = max(0,15%×bw×d, 0,9cm²)

# Armadura de pele (h > 60 cm)
As_pele = 0,10%×(bw×(h−2cnom−2φ_est))/2  por face
```

### 5.3 Pilares — Flexo-compressão

```
λ = le/i   (i = h/3,46)
Se λ > 35: e2 = 0,0005×λ²×h/(0,5+ν)  (pilar-padrão)

# Flexo-compressão oblíqua (NBR 6118, 17.2.5)
(Mx/MRdxx)^1,2 + (My/MRdyy)^1,2 ≤ 1

As_total = resultado do dimensionamento
As_min   = max(0,15×Nd/fyd, 0,40%×Ac)
As_max   = 8%×Ac

# Estribos
φ_est = max(5mm, φ_long/4)
s     = min(b_min, 20×φ_long, 30cm)
s_red = 0,6×s  (fundação, emendas, nós)
```

### 5.4 Escolha de Bitola (função `escolher_bitola`)

```python
BITOLAS_CA50 = [6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0]  # mm
AREAS = {6.3: 0.312, 8.0: 0.503, ...}  # cm²

def escolher_bitola(As_necessario, n_min=2, n_max=6):
    """Retorna (n, φ, As_fornecido) minimizando desperdício."""
    for φ in BITOLAS_CA50:
        for n in range(n_min, n_max+1):
            if n * AREAS[φ] >= As_necessario:
                return n, φ, n * AREAS[φ]

def escolher_estribo(Asw_s, bw, d):
    """Retorna (φ, s, n_ramos, quantidade_total, Asw_s_fornecido)."""
    ...
```

---

## 6. Detalhamento — Saída por Região

Para cada elemento, a resposta JSON inclui:

```json
{
  "id": "V1",
  "tipo": "viga",
  "regioes": {
    "apoio_esq": {
      "As_neg_necessario": 3.84,
      "As_neg_barras": { "n": 4, "phi": 12.5, "As_fornecido": 4.91,
                         "descricao": "4 Ø 12,5 (4,91 cm²)" },
      "estribo": { "phi": 5, "espacamento": 8, "n_ramos": 2,
                   "quantidade": 12, "descricao": "Ø 5 c/8 cm (2r) — 12 un." },
      "comprimento_zona_cm": 80
    },
    "meio": {
      "As_pos_necessario": 2.21,
      "As_pos_barras": { "n": 3, "phi": 10, "As_fornecido": 2.36,
                         "descricao": "3 Ø 10 (2,36 cm²)" },
      "estribo": { "phi": 5, "espacamento": 15, "n_ramos": 2,
                   "quantidade": 18, "descricao": "Ø 5 c/15 cm (2r) — 18 un." },
      "comprimento_zona_cm": 340
    },
    "apoio_dir": { "...": "igual apoio_esq" }
  },
  "armadura_pele": {
    "necessaria": true,
    "barras_por_face": { "n": 2, "phi": 8,
                         "descricao": "2 Ø 8 por face, s = 20 cm" }
  },
  "ancoragem": {
    "lb_nec_apoio_ext_cm": 26.4,
    "lb_nec_apoio_int_cm": 10.0,
    "gancho_necessario": true
  }
}
```

---

## 7. Desenhos SVG

### 7.1 Seção Transversal (`engine/svg_secao.py`)

Gerado automaticamente para cada elemento. Escala proporcional à seção real.

**Elementos desenhados:**
- Retângulo externo = contorno da seção (bw × h)
- Retângulo tracejado interno = linha de cobrimento (cnom)
- Círculos = barras longitudinais (diâmetro proporcional)
  - Topo: armadura negativa (vermelha)
  - Fundo: armadura positiva (azul)
  - Laterais: armadura de pele (cinza), se h > 60 cm
- Retângulo = estribo (preto, espessura = φ_est proporcional)
- Cotas: b, h, cnom, posições das barras

**Viewport SVG:** 300×400 px para seção típica, escalado proporcionalmente.

### 7.2 Elevação / Planta (`engine/svg_elevacao.py`)

Vista longitudinal do elemento com zonas de armadura.

**Elementos desenhados:**
- Linha base = eixo do elemento (comprimento real proporcional)
- Barras negativas: linhas no topo, comprimento = zona + ancoragem
- Barras positivas: linhas no fundo, comprimento total ou por trecho
- Zonas de estribo: retângulos coloridos
  - Vermelho = zona crítica (apoios, 2d)
  - Amarelo = zona corrente (meio do vão)
- Anotações: `4 Ø 12,5`, `Ø 5 c/8cm`, comprimentos de ancoragem (lb)
- Pilares de apoio: retângulos cinza nas extremidades com largura real

---

## 8. Output Educativo — Cálculo Manual Carini

O módulo `engine/relatorio.py` gera um dict com os passos do cálculo manual usando os valores reais calculados. Cada passo tem `titulo`, `formula`, `valores`, `resultado` e `aviso` (se houver).

**Sequência dos passos:**

```
Passo 1 — Pré-dimensionamento
Passo 2 — Propriedades dos materiais (Ecs, fcd, fyd, fctd)
Passo 3 — Propriedades geométricas dos elementos (I, A, L)
Passo 4 — Matrizes de rigidez elementares (k_e por elemento)
Passo 5 — Transformação local→global (matriz T por elemento)
Passo 6 — Montagem da K_global (com mapa de contribuições)
Passo 7 — Condições de contorno (GDLs restritos eliminados)
Passo 8 — Vetor de forças (F_global)
Passo 9 — Resolução do sistema [K_red]{u}={F_red}
Passo 10 — Deslocamentos e rotações nodais
Passo 11 — Reações nos apoios
Passo 12 — Esforços internos (N, V, M por elemento, 10 seções)
Passo 13 — Flechas (imediata + diferida + limite NBR)
Passo 14 — Dimensionamento à força cortante
Passo 15 — Dimensionamento à flexão
Passo 16 — Detalhamento (bitolas, quantidades, zonas)
Passo 17 — Verificações ELS (flecha, fissuração)
```

**Avisos automáticos** (campo `aviso` em cada passo):

| Condição | Aviso |
|---|---|
| x/d > 0,45 | "Seção insuficiente → aumentar h de Xcm para Ycm ou usar armadura dupla" |
| δ > L/250 | "Flecha Xmm > limite Ymm → aumentar h ou adicionar contraflecha" |
| wk > wlim | "Fissuração wk=Xmm > 0,30mm → aumentar As ou reduzir espaçamento" |
| λ > 90 | "Pilar muito esbelto (λ=X) → análise não-linear obrigatória" |
| VSd > VRd2 | "Bielas comprimidas insuficientes → aumentar bw de Xcm para Ycm" |
| As < As_min | "Armadura mínima não atendida → usar As_min = X cm²" |

---

## 9. Rotas Flask

```python
# Submeter estrutura para análise
POST /api/estrutura
  Body: JSON (schema seção 3)
  Response: { "id": "abc123", "status": "ok", "resultado": {...} }

# Obter relatório HTML renderizado
GET /api/relatorio/<id>
  Response: HTML completo com matrizes coloridas, SVG, passos Carini

# Listar análises recentes (opcional)
GET /api/estruturas
  Response: [{ "id", "timestamp", "elementos", "status" }]
```

**Armazenamento temporário:** dict em memória (sem banco de dados na Fase 1). Cada análise tem um ID UUID e expira após 1h.

---

## 10. Matrizes Coloridas — Implementação

A K_global é armazenada com metadados de contribuição:

```python
# Para cada célula [i,j] da K_global, registrar qual elemento contribuiu
K_contribuicoes[i][j] = ["P1", "V1"]  # lista de elementos

# No template HTML, renderizar como tabela com CSS
# Uma célula com 2 elementos: dividida diagonalmente com as 2 cores
```

Hover via JavaScript: ao passar o mouse sobre uma célula, tooltip mostra:
```
K[3,3] = K_P1[3,3] + K_V1[1,1]
       = 234,5 + 1.820,3
       = 2.054,8 kN/m
```

---

## 11. Fora do Escopo (Fase 1)

- UI gráfica para desenhar a estrutura (Fase 2)
- Visualização 3D deformada (Fase 3)
- Análise não-linear (λ > 140)
- Lajes como elementos de placa (apenas viga-laje simplificado)
- Efeitos de segunda ordem (P-delta)
- Cargas de vento e sismo
- Fundações (nó com vínculos elásticos representa apoio de fundação)
- Banco de dados persistente

---

## 12. Critérios de Aceite

- [ ] `POST /api/estrutura` com pórtico simples retorna 200 com resultado
- [ ] Viga biapoiada L=5m q=10kN/m: δ_max = 5×10×500⁴/(384×Ecs×I) ± 1%
- [ ] Pórtico com engaste basal: reações satisfazem equilíbrio ΣFx=0, ΣFy=0, ΣM=0
- [ ] Dimensionamento: viga com Md=50kNm → As dentro de ±2% do cálculo manual
- [ ] SVG seção transversal gerado para viga 14×40 com 3Ø10 no fundo
- [ ] SVG elevação com 3 zonas de estribo coloridas
- [ ] Passo a passo Carini com 17 passos presentes na resposta
- [ ] Aviso automático quando x/d > 0,45
- [ ] Aviso automático quando δ > L/250
- [ ] K_global colorida: células com contribuição de P1 em azul, V1 em verde
- [ ] Hover na K_global mostra decomposição da célula
- [ ] `GET /api/relatorio/<id>` retorna HTML navegável
