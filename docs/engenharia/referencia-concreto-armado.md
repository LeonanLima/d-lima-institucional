# Referência Técnica — Concreto Armado

**Fontes consolidadas:**
- Prof. Matheus Roman Carini — Slides 1–4, Planilhas (Estrutural na Real)
- Prof. Dr. Paulo Sérgio dos Santos Bastos — UNESP Bauru, Apostilas Fundamentos, Vigas, Força Cortante e Torção (2017)
- **NBR 6118:2023** | NBR 7480:2024 | NBR 6120:2019 | NBR 16868-1:2020

> **Legenda:** `[C]` = Carini (como calcular) · `[B]` = Bastos (por que funciona) · `[N]` = NBR

---

## 1. MATERIAIS

### 1.1 Concreto — Resistências

```
[C] fck — resistência característica à compressão (28 dias, cilíndrico 10×20 cm)
  Estimativa: fck = fcm − 1,65s   (fcm = média, s = desvio padrão)
  Classes: C20 C25 C30 C35 C40 C45 C50 | C55 C60 C70 C80 C90 C100
  fck mínimo por CAA: I→20 | II→25 | III→30 | IV→40 MPa

[C] Resistência à tração (fck ≤ 50 MPa):
  fct,m    = 0,3 × fck^(2/3)    [MPa]
  fctk,inf = 0,7 × fct,m         (cálculo ELU geral)
  fctk,sup = 1,3 × fct,m         (ancoragem, armadura mínima)
  fctd     = fctk,inf / γc = 0,15 × fck^(2/3)   [MPa]

  fck=25: fct,m=2,565 | fctk,inf=1,795 | fctk,sup=3,334 MPa

[B] POR QUE o concreto precisa do aço:
  fct,m ≈ 1/10 × fck → concreto resiste pouco à tração
  Em flexão: fibra inferior tracionada → fissura → aço assume a tração
  Sem armadura: ruptura frágil e súbita após primeira fissura
```

### 1.2 Concreto — Módulo de Elasticidade

```
[C] Módulo inicial (tangente na origem):
  fck ≤ 50 MPa:  Eci = αE × 5600 × √fck   [MPa]
  
  αE por agregado:
    Basalto/diabásio: 1,2 | Granito/gnaisse: 1,0 | Calcário: 0,9 | Arenito: 0,7

[C] Módulo secante (usado em ELS e rigidezes):
  αi = 0,8 + 0,2 × (fck/80) ≤ 1,0
  Ecs = αi × Eci

  fck=25, basalto: Eci=33.600 MPa | αi=0,863 | Ecs=28.980 MPa
  fck=25, granito: Eci=28.000 MPa | αi=0,863 | Ecs=24.150 MPa

[B] POR QUE αE varia com o agregado:
  O módulo do concreto depende da microestrutura da pasta + do agregado.
  Basalto é mais rígido → partículas transmitem tensão mais eficientemente → Eci maior.
  Arenito é mais poroso → menor transmissão → Eci menor.

[C] Módulo de distorção (cisalhamento):
  G = Ecs / 2,4   (ν=0,2 → G = Ecs/[2(1+ν)])
```

### 1.3 Concreto — Diagramas Tensão-Deformação

```
[C] PARÁBOLA-RETÂNGULO (fck ≤ 50 MPa, análise não-linear):
  εc ≤ εc2:  σc = 0,85 × fcd × [1 − (1 − εc/2,0‰)²]
  εc > εc2:  σc = 0,85 × fcd   (patamar plástico)
  εcu = 3,5‰ (deformação máxima de ruptura)

[C] BLOCO RETANGULAR (ELU — NBR 6118, 17.2.2):
  λ = 0,80 | αc = 0,85 | ηc = 1,0  (fck ≤ 50 MPa)
  Tensão uniforme: αc × ηc × fcd sobre altura λx
  fcd = fck / 1,4

[B] POR QUE εcu = 3,5‰:
  É a deformação máxima do concreto comprimido antes do esmagamento.
  Define o domínio 3 (seção dúctil): aço escoa ANTES do concreto esmagar → viga "avisa".
  x/d ≤ 0,45 garante εs > εyd quando εc = εcu → ruptura com aviso.

[C] Efeito Rüsch (cargas permanentes):
  Resistência de longa duração ≈ 85% da de curta duração → αc = 0,85
```

### 1.4 Concreto — Propriedades Reológicas

```
[C] RETRAÇÃO:
  Redução de volume por perda de água → independente de carga
  → Fissuras em lajes de piso e peças de grande comprimento
  Controle: juntas de dilatação + cura adequada + a/c baixo

[C] FLUÊNCIA (Creep):
  Aumento de deformação ao longo do tempo sob tensão constante
  φ = 2,5  (simplificado NBR 6118 para flechas diferidas)
  w∞ = (1 + φ) × w0 = 3,5 × w0
  Cálculo rigoroso: φ = 8,2 × βRH / (fck + 8)

[B] POR QUE a fluência importa nas vigas:
  Carga permanente (peso próprio + alvenaria) age por décadas.
  Deformação final ≈ 3,5× a deformação imediata → flecha pode ultrapassar L/250.
  Por isso verificar flecha diferida, não só imediata.
```

### 1.5 Aço — CA-25, CA-50, CA-60, CA-70

```
[C] Propriedades gerais (todos):
  ρ = 7850 kg/m³  |  αt = 10⁻⁵/°C  |  Es = 210.000 MPa = 210 GPa

[B] POR QUE αt do aço ≈ αt do concreto:
  Aço: 10⁻⁵/°C | Concreto: 10⁻⁵/°C → dilatam juntos → sem tensões térmicas internas.
  Se diferissem muito → a peça se destruiria após poucos ciclos térmicos.

[C] Categorias e resistências:
  CA-25: fyk=250 MPa | fyd=217 MPa  (barras lisas, pouco usado)
  CA-50: fyk=500 MPa | fyd=435 MPa  ← padrão de projeto
  CA-60: fyk=600 MPa | fyd=522 MPa  (vigotas pré-moldadas)
  CA-70: fyk=700 MPa | fyd=609 MPa

  fyd = fyk / γs = fyk / 1,15  |  εyd = fyd / Es = 2,07‰ (CA-50)

[C] Bitolas CA-50 (áreas em cm²):
  Ø6,3: 0,312  |  Ø8: 0,503  |  Ø10: 0,785  |  Ø12,5: 1,227
  Ø16:  2,011  |  Ø20: 3,142 |  Ø25: 4,909  |  Ø32: 8,042

[C] Pesos lineares (kg/m):
  Ø6,3: 0,245 | Ø8: 0,395 | Ø10: 0,617 | Ø12,5: 0,963
  Ø16: 1,578  | Ø20: 2,466 | Ø25: 3,853
```

### 1.6 CAA — Cobrimentos e fck mínimo

```
[N] NBR 6118, Tabela 6.1 + 7.2, 2023 | ∆c = 5 mm (controle padrão)

  CAA I   — fraca:     fck≥20 | c_laje=2,0 | c_viga/pilar=2,5 cm
  CAA II  — moderada:  fck≥25 | c_laje=2,5 | c_viga/pilar=3,0 cm  ← residencial padrão
  CAA III — forte:     fck≥30 | c_laje=3,5 | c_viga/pilar=4,0 cm  ← litoral
  CAA IV  — muito forte: fck≥40 | c_laje=4,5 | c_viga/pilar=5,0 cm

[B] POR QUE o cobrimento protege o aço:
  Em pH > 12 (concreto íntegro), o aço forma uma camada passivante de Fe₂O₃
  que impede corrosão. Carbonatação e cloretos reduzem o pH → corrosão → 
  expansão → fissuras → spalling. O cobrimento é a primeira barreira.
```

### 1.7 Coeficientes de Ponderação

```
[N] ELU — combinação NORMAL:
  γc = 1,4 (concreto) | γs = 1,15 (aço) | γf = 1,4 (ações desfavoráveis)

[N] ELS — combinação quase permanente (flechas):
  Fd,qp = Σgk + Σ(ψ2i × qk)
  ψ2: residencial=0,3 | escritórios=0,4 | garagem=0,6
```

---

## 2. CARGAS E AÇÕES

```
[C] Pesos específicos (kN/m³) — NBR 6120:2019:
  Concreto armado: 25,0 | Argamassa cimento+areia: 21,0
  Argamassa cal+cimento: 19,0 | Aço: 77,8

[C] Sobrecargas mínimas (kN/m²) — edificações residenciais:
  Dormitórios, salas: 1,5 | Área de serviço: 2,0
  Corredores comuns: 3,0 | Garagem (PBT ≤ 30 kN): 3,0
  Cobertura (só manutenção): 1,0 | Sacadas: 2,5

[C] Paredes sobre vigas (NBR 16868-1:2020):
  q_parede = γ_alv × h_parede   [kN/m]
  Bloco cerâmico 9cm c/reboco: γ_alv ≈ 1,9 kN/m²
  Bloco cerâmico 14cm c/reboco: γ_alv ≈ 2,4 kN/m²
  Bloco concreto 19cm c/reboco: γ_alv ≈ 4,0 kN/m²

[C] Carga de cálculo ELU (combinação normal, 1 ação variável):
  fd = 1,4×gk + 1,4×qk
```

---

## 3. PRÉ-DIMENSIONAMENTO

```
[C] LAJES MACIÇAS:
  h ≈ lx / 40  (residencial, lx em m → h em m) | h_mín = 8 cm
  h ≈ lx / 30  (balanço)
  
  Classificação: ly/lx ≤ 2 → bidirecional | ly/lx > 2 → unidirecional

[C] LAJES TRELIÇADAS:
  h ≈ lx / 20  (total, inclui capa) | capa mínima: 4 cm
  Alturas comerciais: 12, 14, 16, 20, 25 cm

[C+B] VIGAS:
  h ≈ L / 10   (simplesmente apoiada)
  h ≈ L / 12   (contínua)  [Carini e Bastos coincidem: L/12 para C20–C25]
  h ≈ L / 5    (balanço)
  h mínima: 25 cm | modulada de 5 em 5 cm
  b = largura do bloco de alvenaria (14, 19 ou 25 cm)

[C] PILARES (NBR 6118, 13.2.3):
  b_mín = 19 cm
  Intermediário: Ac ≥ 0,6×Nk / (0,42×fck)   [cm²]
  Extremidade/canto: Ac ≥ 0,6×(1,4×Nk) / (0,42×fck)

[C] Taxas de aço para orçamento:
  Vigas: 80–120 kg/m³ | Pilares: 60–100 kg/m³ | Lajes: 50–80 kg/m³
```

---

## 4. LAJES

### 4.1 Vão Efetivo (NBR 6118, 14.7.2.2)
```
lef = l0 + a1 + a2
  a1 = min(t1/2 ; 0,3h) | a2 = min(t2/2 ; 0,3h)
```

### 4.2 Casos de Vinculação
```
[N] Casos 1–6: lajes BIDIRECIONAIS (ly/lx ≤ 2)
  Caso 1: 4 apoiadas | Caso 2: 3ap+1eng(ly) | Caso 2A: 3ap+1eng(lx)
  Caso 3: 2ap+2eng opostos(ly) | Caso 4: 2ap+2eng adjacentes
  Caso 5: 1ap+3eng | Caso 6: 4 engastadas
  
  Critério: engastada = laje adjacente do outro lado (mesma espessura)

Casos 7–10: lajes UNIDIRECIONAIS (ly/lx > 2)
  Caso 7: biapoiada | Caso 8: ap+eng | Caso 9: bi-engastada | Caso 10: balanço
```

### 4.3 Momentos Fletores

**Lajes bidirecionais (λ = ly/lx = 1,0 — tabela para λ = 1):**

| Caso | mx | my | mxe | mye | rx | ry |
|---|---|---|---|---|---|---|
| 1 | 0,1075 | 0,0434 | — | — | 0,1103 | 0,4299 |
| 2 | 0,0660 | 0,0190 | — | -0,1173 | 0,0482 | 0,3520 |
| 4 | 0,0605 | 0,0244 | -0,1075 | -0,0434 | 0,0827 | 0,3224 |
| 6 | 0,0359 | 0,0143 | -0,0716 | -0,0289 | — | — |

```
Mdx  = mx  × fd × lx²  |  Mdy  = my  × fd × lx²  (positivos)
Mdxe = mxe × fd × lx²  |  Mdye = mye × fd × lx²  (negativos)
Rdx  = rx  × fd × lx   |  Rdy  = ry  × fd × lx   (reações)
```

**Lajes unidirecionais:**
```
Caso 7: Md = fd×lx²/8    Rd = fd×lx/2
Caso 8: Md+ = fd×lx²/14,22  Md- = fd×lx²/8   Rd_ap = 3fd×lx/8
Caso 9: Md+ = fd×lx²/24  Md- = fd×lx²/12  Rd = fd×lx/2
Caso 10: Md = fd×lx²/2   Rd = fd×lx
```

### 4.4 ELU — Armadura (lajes maciças)
```
[C] d = h - c - φ/2  (φ≈1cm) | b = 100 cm/m
    fcd = fck/1,4 | fyd = fyk/1,15

    x = 1,25d × [1 - √(1 - Md/(0,425×b×d²×fcd))]
    Verificar: x/d ≤ 0,45  (ductilidade)
    As = 0,85×fcd×0,80×x×b / fyd   [cm²/m]

[C] Armadura mínima CA-50, fck=25:
    ρmín = 0,15%  →  As,mín = 1,5×h  [cm²/m, h em cm]

[C] As por espaçamento (cm²/m):
       s=10  s=12  s=15  s=20  s=25
  Ø5: 1,96  1,78  1,64  1,40  1,31
  Ø6,3: 3,12  2,83  2,60  2,23  2,08
  Ø8:  5,03  4,57  4,19  3,59  3,35
  Ø10: 7,85  7,14  6,54  5,61  5,24
```

### 4.5 ELS — Flecha (lajes)
```
[C] Ecs = αi × αE × 5600 × √fck  (ver Seção 1.2)

    Flecha imediata (unidirecional — caso 7):
      w0 = 5 × fd,ser × lx⁴ / (384 × Ecs × Ig)   Ig = 100×h³/12 por metro

    Flecha diferida (fluência):
      w∞ = (1 + φ) × w0 = 3,5 × w0

    Limites NBR 6118, Tabela 13.3:
      Balanço: L/125 | Demais: L/250
```

---

## 5. VIGAS

### 5.1 Fundamento Físico — Bastos (o "por que")

```
[B] Definição: viga = flexão preponderante | comprimento > 3× maior dimensão seção

[B] Análise estrutural:
  Linear (lei de Hooke, Ecs) → válida para ELS e como base do ELU
  Linear com redistribuição → reduz M nos apoios, aumenta no vão → mais econômico
  Plástica → rígido-plástico perfeito, só ELU

[B] Ductilidade e x/d ≤ 0,45:
  Quanto menor x/d, maior a rotação plástica disponível.
  x/d = 0,45 → εs ≈ 3,5‰ quando εcu = 3,5‰ → aço NO LIMITE de escoamento.
  x/d < 0,45 → aço escoa ANTES do concreto esmagar → viga AVISA antes de romper.
  x/d > 0,45 → concreto esmaga SEM aviso → ruptura frágil → proibido.

[B] Redistribuição:
  δ = M_redistribuído / M_original ≥ 0,75 (geral) ou 0,90 (nós móveis)
  x/d ≤ (δ - 0,44)/1,25  para fck ≤ 50 MPa

[B] Instabilidade lateral (NBR 6118, 15.10):
  b ≥ L₀/50  e  b ≥ βfl×h  (βfl=0,40 para retangular simples)
  → Com laje solidária no flange comprimido: estabilidade garantida
```

### 5.2 Vão Efetivo (NBR 6118, 14.6.2.4)
```
lef = l0 + a1 + a2
  a1 = min(t1/2 ; 0,3h) | a2 = min(t2/2 ; 0,3h)
  (t = largura do pilar/apoio)
```

### 5.3 Levantamento de Cargas
```
PP = b × h × 25   [kN/m]
q_alv = γ_alv × h_parede   [kN/m]
q_laje = reações Rdx ou Rdy calculadas na Seção 4.3
gk = PP + q_alv + q_laje
fd = 1,4 × gk   (combinação normal ELU)
```

### 5.4 Modelo Estrutural para Vigas Contínuas (NBR 6118, 14.6.6.1)

```
[B+C] Regra a) M_vão ≥ fd×L²/16  (mínimo engastamento perfeito no vão)

[B+C] Regra b) Pilar interno: se b_int > ie/4 → M_neg ≥ M_ep (pilar engastado)

[B+C] Regra c) Apoios extremos — método das rigidezes:
  K_mola = K_sup + K_inf  |  K = 4EI/i  (i = comprimento equivalente/2)
  
  Rigidezes (I = momento de inércia, L = comprimento/2):
    r_sup = 2×I_pilar_sup / L_pilar_sup
    r_inf = 2×I_pilar_inf / L_pilar_inf
    r_vig = I_viga / L_viga (vão extremo)
  
  M_lig = M_ep × r_vig / (r_inf + r_sup + r_vig)
  M_pilar_sup = M_ep × r_sup / (r_inf + r_sup + r_vig)

[B] Armadura de suspensão (apoio indireto, NBR 6118, 18.3.6):
  R_tt = R_apoio × h₁/h₂   (h₁ = viga apoiada, h₂ = viga suporte)
  Dimensionar estribo de suspensão para R_tt.
```

### 5.5 Esforços — Modelos simples
```
Biapoiada: Md = fd×L²/8  | Vd = fd×L/2

Contínua (modelo simplificado):
  M_vão  = fd×L²/10  (apoios internos)
  M_eng  = fd×L²/12  (apoios internos — base para redistribuição)
  Vd = fd×L/2 (simplificado)

[N] Redução de cortante (NBR 6118, 17.4.1.2.1):
  VSd,red = VSd - fd×d   (cargas distribuídas, verificar na FACE do apoio)
```

### 5.6 ELU — Cisalhamento (Modelo de Cálculo I)

```
[B] POR QUE 5 mecanismos compõem Vc:
  1. Ação de arco:  banzo comprimido inclinado — 20–40% de VRd
  2. Concreto comprimido (Vcz): zona não fissurada
  3. Engrenamento dos agregados: atrito nas fissuras — 33–50% de VRd
  4. Ação de pino (armadura longitudinal): 15–25% de VRd
  5. Tensões residuais de tração: fissuras < 0,15mm
  → Vc da NBR captura tudo isso de forma simplificada.

[B] Treliça Ritter-Mörsch (θ=45°) → Modelo I: conservador, mais aço em estribos.
[B] Treliça Generalizada (30°≤θ≤45°) → Modelo II: menos estribos, mais armadura longitudinal.

[C] Verificação das bielas (NBR 6118, 17.4.2.2):
  αv2 = 1 - fck/250       (fck em MPa)
  fcd = fck / 1,4 / 10    (kN/cm²)
  VRd2 = 0,27 × αv2 × fcd × bw × d

  d ≈ h - 5 cm  (estimativa inicial)
  Se VSd ≤ VRd2 → OK; se VSd > VRd2 → aumentar seção

[C] Parcela do concreto:
  fctd = 0,15 × fck^(2/3) / 10   (kN/cm²)
  Vc   = 0,6 × fctd × bw × d     (kN)

[C] Armadura mínima:
  fctm = 0,3×fck^(2/3)  (MPa) | fywd = min(fyk/1,15 ; 435 MPa)
  Asw/s_mín = 0,2×fctm/fywd × bw   (cm²/cm)
  VRd3_mín = Asw/s_mín × 0,9d × fywd + Vc

[C] Armadura de projeto:
  Se VSd ≤ VRd3_mín → usar Asw/s_mín
  Se VSd > VRd3_mín → Asw/s = (VSd - Vc) / (0,9d × fywd)

[C] Conversão para estribo (2 ramos):
  s = (2×Aφ) / (Asw/s)
  s ≤ min(0,6d ; 30 cm)
```

### 5.7 ELU — Flexão

```
[C] fcd = fck/1,4/10  | fyd = fyk/1,15/10   (kN/cm²)
    d = h - c - φ_est - φ_long/2   (estimativa: d ≈ h - 5 cm)

[C] Limite dúctil (fck ≤ 50 MPa):
    x_duc = 0,45×d  →  λ=0,80, αc=0,85
    Md,duc = 0,85×fcd×0,80×x_duc×b×(d - 0,80×x_duc/2)

[C] ARMADURA SIMPLES (Md ≤ Md,duc):
    x = 1,25d × [1 - √(1 - Md/(0,425×b×d²×fcd))]
    As = 0,85×fcd×0,80×x×b / fyd   [cm²]
    As,mín: ρmín=0,15% (CA-50, C25) → As,mín = 0,15/100 × bw × d

[C] ARMADURA DUPLA (Md > Md,duc):
    d' = c + φ_est + φ_long/2
    σs2 = εcu×(x_duc - d')/x_duc × Es  (tensão na armadura comprimida)
    As2 = (Md - Md,duc) / (σs2×(d - d'))   (armadura comprimida)
    As1 = (αc×fcd×λ×x_duc×b + As2×σs2) / fyd  (armadura tracionada)

[C] SEÇÃO T (laje colaborante):
    bf = bw + 2×b0   onde b0 ≤ min(lef/10 ; dist_vigas/2)
    Tentar x = 1,25d×[1-√(1-Md/(0,425×bf×d²×fcd))]
    Se λx ≤ hf (laje) → LN na mesa → As = 0,85×fcd×0,80×x×bf/fyd
    Se λx > hf → seção T real (equilíbrio com hf separado)
```

### 5.8 ELS — Flecha (Método de Branson)

```
[C] αe = Es/Ecs   (relação modular)
    Mr = 1,2×fctm×Ig/(Yt×1000)  [kNm]  | Ig = bw×h³/12 | Yt = h/2
    
    LN no Estádio II (fissurada):
      bw/2×x² + αe×As2×(x-d') - αe×As1×(d-x) = 0
      Iii = bw×x³/3 + αe×As2×(x-d')² + αe×As1×(d-x)²
    
    Inércia equivalente (Branson):
      Ie = (Mr/Ma)³×Ig + [1-(Mr/Ma)³]×Iii   (Ma = M serviço)
    
    Flecha imediata:
      δi = 5×q_ser×L⁴ / (384×Ecs×Ie)   [mm]
    
    Flecha diferida (fluência):
      δt = δi × (1 + 2,0)   (φ≈2,0)
    
    Limite: δf = δt ≤ L/250
```

### 5.9 ELS — Fissuração

```
[C] σs = Ma×(d-x)/Iii/10   (tensão no aço, Estádio II)
    ρr = As/Acr  | Acr = bw×(c + φ_est + φ_long/2 + 3,5×φ_long)
    wk = φ_long × σs/(12,5×ηi×Es) × (4/ρr + 45)   [mm]

    Limites wlim: CAA I=0,4mm | CAA II=0,3mm | CAA III=0,2mm
```

---

## 6. PILARES

### 6.1 Esbeltez
```
[C] λ = le / i   (i = h/3,46 para seção retangular)
    le = H  (pilar biapoiado) | le = 2H  (balanço no topo)
    
    λ ≤ 35       → CURTO (e2=0)
    35 < λ ≤ 90  → ESBELTO (método pilar-padrão)
    90 < λ ≤ 140 → MUITO ESBELTO
    λ > 140      → análise não-linear rigorosa

    λ1 = 25 + 12,5×(αb×e1,A/h)  (35 ≤ λ1 ≤ 90)
    αb = 0,60 + 0,40×(e1,B/e1,A) ≥ 0,40
```

### 6.2 Distribuição de Momentos — Método das Rigidezes
```
[C] Mep = fd×L²/12  (viga com carga uniforme)
    r = 2I/L_equiv  (rigidez de cada elemento no nó)
    
    M_pilar_sup = Mep × r_sup / (r_sup + r_inf + Σr_vig)
    M_pilar_inf = Mep × r_inf / (r_sup + r_inf + Σr_vig)
```

### 6.3 Excentricidades
```
[C] De 1ª ordem:
    e1 = M / Nd
    e1,mín = 1,5 + 0,03×h  [cm]
    e1,C = max(0,6×e1,A + 0,4×e1,B ; 0,4×e1,A)

[C] De 2ª ordem (pilar-padrão, λ ≤ 90):
    ν = Nd/(Ac×fcd)
    e2 = 0,0005×λ²×h/(0,5+ν)   [cm]  (só na seção C)
```

### 6.4 Armadura (Flexo-Compressão)
```
[C] Oblíqua — envoltória (NBR 6118, 17.2.5):
    (Mx/MRdxx)^1,2 + (My/MRdyy)^1,2 ≤ 1

[C] As,mín = max(0,15×Nd/fyd ; 0,40%×Ac)
    As,máx = 8%×Ac (seção corrente) | 4%×Ac (emendas)
    Ø_long: 10mm ≤ Ø ≤ min(hx;hy)/8

[C] Estribos:
    Ø_est ≥ max(5mm ; Ø_long/4)
    s ≤ min(b_mín ; 20×Ø_long ; 30 cm)
    s_red = 0,6×s  (fundação, emendas, nós)
```

---

## 7. TORÇÃO

### 7.1 Fundamento Físico — Bastos

```
[B] Torção → tensões de cisalhamento helicoidais (45° em torno da seção).
    Fissuras em hélice nas 4 faces → estribo ABERTO não fecha o fluxo → ineficaz.
    Ensaios Mörsch: armadura longitudinal OU transversal isolada → pouco ganho.
    Ambas juntas → resistência ×1,6 | Armadura helicoidal (45°) → ×3 ou mais.

[B] Após fissuração: apenas casca externa resiste → seção cheia ≈ seção oca parede fina.
    Analogia de Bredt: fluxo de cisalhamento τ×t = T/(2Ae) = constante.
    Treliça espacial generalizada: bielas em hélice (ângulo θ variável), banzos
    longitudinais + estribos fechados como montantes verticais.
```

### 7.2 Classificação — Equilíbrio vs Compatibilidade

| Tipo | Definição | Ação |
|---|---|---|
| **Equilíbrio** | Torção necessária para equilíbrio estático (laje em balanço sem continuidade, viga em L) | OBRIGATÓRIO dimensionar |
| **Compatibilidade** | Torção por compatibilidade de deformações (laje sobre viga de borda com continuidade interna) | Pode DESPREZAR |

```
[N] Torção de compatibilidade pode ser desprezada (NBR 6118, 17.5.1.2) se:
    VSd ≤ 0,7×VRd2   (garantia mínima de ductilidade)
```

### 7.3 Geometria da Seção Resistente

```
[C] Para seção retangular cheia:
    A  = bw × h  |  u = 2(bw + h)
    he = A/u   → deve ser ≥ 2c₁  (c₁ = c_nom + Ø_est)
    Ae = (bw - he)×(h - he)
    ue = 2[(bw-he)+(h-he)]
```

### 7.4 Verificação das Bielas (TRd,2)

```
[C] αv2 = 1 - fck/250  |  fcd = fck/1,4/10  (kN/cm²)
    TRd,2 = 0,5 × αv2 × fcd × Ae × he × sen2θ   [kN·m]
    θ = 45°: TRd,2 = 0,5 × αv2 × fcd × Ae × he
    Se TSd ≤ TRd,2 → OK; se não → aumentar seção
```

### 7.5 Armadura Transversal (Estribos)

```
[C] As,90/s = TSd×tgθ / (2×Ae×fywd)   → θ=45°: As,90/s = TSd/(2×Ae×fywd)
    → As,90 = área de UM ramo vertical do estribo (não total!)
    s_máx: VSd ≤ 0,67VRd2 → 0,6d ≤ 30cm | VSd > 0,67VRd2 → 0,3d ≤ 20cm
    Estribos FECHADOS com ganchos 45°. Barra em cada vértice.
```

### 7.6 Armadura Longitudinal

```
[C] Asi/ue = TSd×tgθ/(2×Ae×fywd)   → θ=45°: Asi/ue = TSd/(2×Ae×fywd)
    Asi = armadura total longitudinal
    Distribuída ao longo do perímetro | espaçamento ≤ 35 cm | mín. 4 barras
```

### 7.7 Armadura Mínima

```
[C] fct,m = 0,3×fck^(2/3)  (MPa) → /10 para kN/cm²
    Asi,mín/ue ≥ 20×fct,m/fywk × he   [cm²/m]
    As,90mín/s ≥ 20×fct,m/fywk × bw   [cm²/m]
```

### 7.8 Combinação T + Cortante (NBR 6118, 17.7.2)

```
[C] Bielas: VSd/VRd2 + TSd/TRd2 ≤ 1
    Armadura transversal total = Asw/s (cortante, ramos totais) + 2×As,90/s (torção, 2 ramos)
    θ deve ser o mesmo para cortante e torção.
```

### 7.9 Momento de Inércia à Torção

```
[C] J = j × b × h³   [cm⁴]  (b = menor dimensão)
    G = Ecs/2,4   →   Rigidez à torção = G×J

    n=b/h:  1,0→j=0,141 | 0,8→j=0,171 | 0,7→j=0,189 | 0,5→j=0,229
```

---

## 8. DETALHAMENTO

### 8.1 Ancoragem (NBR 6118, §9.4)

```
[C] fbd = η1×η2×η3×fctd  | fctd = 0,15×fck^(2/3)  (MPa)
    η1 = 1,0 (boa aderência) | η1 = 0,7 (má aderência)
    Boa aderência: barra na metade inferior | h ≤ 30 cm: qualquer posição

    lb,bas = (φ/4)×(fyd/fbd)   [cm]
    lb,nec = lb,bas × (As,calc/As,ef)  ≥ max(0,3×lb,bas ; 10Ø ; 10cm)

[C] Tabela lb,nec (cm) — CA-50, C25, As,calc=As,ef:
    Boa aderência:  Ø10=37,7 | Ø12,5=47,1 | Ø16=60,3 | Ø20=75,3
    Com gancho:     Ø10=26,4 | Ø12,5=33,0 | Ø16=42,2 | Ø20=52,7
```

### 8.2 Emendas por Traspasse (NBR 6118, §9.5)

```
[C] lt = α1 × lb,nec
    α1 = 1,0 (≤25% na mesma seção) | α1 = 1,4 (25–50%) | α1 = 2,0 (>50%)
    "Mesma seção": emendas a menos de 1,3×lt entre si
    Ø > 32mm: emenda mecânica ou solda
```

### 8.3 Detalhamento de Lajes

```
[C] Ø_max ≤ h/8  |  s_max ≤ min(2h ; 20 cm)
    Armadura negativa: comprimento = Lm/4 de cada lado do apoio
    Armadura de borda: As,borda = 0,67×As,mín ≥ 1 cm²/m
    Armadura de distribuição (1 direção): ≥ 20%×As_positiva | s ≤ 33 cm
    Abertura ≤ 10%×lx: distribuir armadura nas bordas (metade de cada lado)
```

### 8.4 Detalhamento de Vigas

```
[C] Espaçamento livre entre barras ≥ max(1,2×Dagreg ; Ø ; 20mm)
    Apoios externos: lb,nec ou gancho se largura insuficiente
    Apoios intermediários: lb = 10Ø (sem M positivo)
    Armadura de pele (h > 60 cm): As,pele = 0,10%×Ac/face | s ≤ 20 cm
    
[C] Comprimento total do estribo = 2(A+B) + ΔC
    ΔC: Ø5=8,3cm | Ø6,3=8,6cm | Ø8=10,0cm | Ø10=12,5cm
```

### 8.5 Detalhamento de Pilares

```
[C] Ø_long: 10mm ≤ Ø ≤ min(hx;hy)/8
    Espaç. entre barras ≥ max(20mm ; Ø_long ; 1,2×Dagreg)
    Espaç. máximo entre eixos perp.: ≤ min(2×b_mín ; 40cm)
    Estribos: Ø ≥ max(5mm ; Ø_long/4) | s ≤ min(b_mín ; 20×Ø_long ; 30cm)
    s_red = 0,6×s: fundação (≥50cm acima), emendas, nós viga-pilar
    Ganchos dos estribos: 135° (preferencial)
    Mudança de seção: inclinação máxima 1:6
```

---

## 9. SÍNTESE CARINI × BASTOS

| Tópico | Carini — COMO calcular | Bastos — POR QUE funciona |
|---|---|---|
| fck | 95% de probabilidade → fck = fcm - 1,65s | Ruptura estatística; poucos cc abaixo de fck |
| fct,m = 0,3×fck^(2/3) | Fórmula empírica NBR | Concreto resiste 1/10× à tração → PRECISA de aço |
| Ecs = αi×Eci | αi = 0,8 + 0,2×(fck/80) | Fissuração prévia reduz rigidez → usar secante no ELS |
| αE varia | Basalto=1,2, Granito=1,0 | Microestrutura do agregado controla transmissão de tensão |
| αt = 10⁻⁵/°C | Mesmo valor aço e concreto | Dilatam juntos → sem tensões térmicas → não se separam |
| αc = 0,85 | Redução de resistência para ELU | Efeito Rüsch: longa duração reduz 15% a resistência |
| Cobrimento por CAA | c_mín por tabela | Passivação do aço em pH alto; CAA define agressividade |
| x/d ≤ 0,45 | Limite de ductilidade ELU | Viga AVISA antes de romper (aço escoa primeiro) |
| Redistribuição δ ≥ 0,75 | Fórmulas de x/d por δ | Capacidade de rotação plástica nos apoios |
| h = L/12 | Estimativa prática | Deformabilidade e flecha diferida (φ=2,5) |
| Vc = 0,6×fctd×bw×d | Fórmula NBR Modelo I | 5 mecanismos: arco, concreto comprimido, agregado, pino, residual |
| VRd2 (bielas) | 0,27×αv2×fcd×bw×d | Bielas comprimidas esmag. se σcd > αv2×fcd → limite superior |
| Treliça θ=45° (MC I) | Modelo simplificado | Fissuras a 45° na alma = trajetória de tração principal |
| Torção equilíbrio | TSd ≤ TRd,2, TRd,3, TRd,4 | Torção necessária → fissuras helicoidais nas 4 faces |
| Torção compatibilidade | Pode desprezar | Fissuração reduz rigidez → redistribuição automática |
| Estribo fechado (torção) | Obrigatório | Fluxo de Bredt precisa de circuito fechado |
| Armadura de suspensão | R_tt = R × h₁/h₂ | Apoio indireto: carga chega ao banzo inferior → precisa subir |
| Fluência φ=2,5 | w∞ = 3,5×w0 | Deformação cresce décadas → flecha final ≫ flecha imediata |

---

*Referências normativas:* NBR 6118:2023 | NBR 7480:2024 | NBR 6120:2019 | NBR 16868-1:2020  
*Referências bibliográficas:* Carini (Estrutural na Real) | Bastos, P.S.S. — UNESP Bauru (2017) | Araújo (2014)
