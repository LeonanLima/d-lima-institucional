# VIGAS DE CONCRETO ARMADO — Estudo completo do material Musso (UFES, 2014-2)

> Fonte: pasta Google Drive `1NHnBdmS8dpB2u7s7psrS_AuP7jbAyKep` — Prof. Fernando Musso Junior (musso@npd.ufes.br), Estruturas de Concreto Armado, UFES.
> Arquivos estudados: `CAP2-VIGA-2014-2.pdf` (capítulo completo, 41 páginas) e `VIGA-MUSSO-2014-2.xlsm` (planilha de dimensionamento com 3 abas: Principal, Momento, Cortante — fórmulas extraídas integralmente).
> Norma base: NBR 6118:2014 (capítulo) / NBR 6118:2003 nas abas Momento e Cortante da planilha (diferenças anotadas onde relevantes).
> Unidades convencionadas neste documento (iguais às do Musso): comprimentos em cm, forças em kN, momentos em kNm, tensões em MPa ou kN/cm² (indicado), armaduras em cm² (long.) e cm²/m (transv.).

---

## 1. Propriedades dos materiais (fck ≤ 50 MPa)

| Grandeza | Fórmula | C20 | C25 | C30 | C35 |
|---|---|---|---|---|---|
| fcd | fck/γc (γc = 1,4) | 14,29 | 17,86 | 21,43 | 25,00 |
| fctm | 0,3·fck^(2/3) | 2,210 | 2,565 | 2,896 | 3,210 |
| fctk (inf) | 0,7·fctm | 1,547 | 1,795 | 2,027 | 2,247 |
| fctd | fctk/1,4 | 1,105 | 1,282 | 1,448 | 1,605 |
| αi | 0,8 + 0,2·fck/80 | 0,850 | 0,863 | 0,875 | 0,888 |
| Ecs (GPa) | αi·5600·√fck /1000 (arredondado) | 21 | 24 | 27 | 29 |
| αe = Es/Ecs | Es = 210 GPa | 10,00 | 8,75 | 7,78 | 7,24 |

Aço: fyd = fyk/γs (γs = 1,15). Es = 210 GPa. εyd = fyd/Es:

| fyk | 250 MPa | 500 MPa | 600 MPa |
|---|---|---|---|
| εyd | 1,035‰ | 2,070‰ | 2,484‰ |

Diagrama retangular do concreto: λ = 0,8 (altura λx), η = 0,85 (tensão η·fcd).
Coeficientes de redução do concreto fissurado: ν = 0,6(1 − fck/250) (cortante); κ = 0,5(1 − fck/250) (torção), fck em MPa.

Parâmetros de durabilidade (planilha Principal):

| Ambiente | CAA | wlim (mm) | ct (cm) | fck mín (MPa) |
|---|---|---|---|---|
| Rural ou submerso | I | 0,4 | 2,0 | 20 |
| Urbano | II | 0,3 | 2,5 | 25 |
| Marinho ou industrial | III | 0,3 | 3,5 | 30 |
| Ind. químicas / respingos de maré | IV | 0,2 | 4,5 | 40 |

## 2. Combinações de ações

- **ELU (M e V):** pd = γg·g + γq·q, com γg = γq = 1,4.
- **ELS-W (frequente):** pF = g + ψ1·q.
- **ELS-DEF (quase permanente):** pQP = g + ψ2·q.

| Uso | ψ1 | ψ2 |
|---|---|---|
| Edificações residenciais | 0,4 | 0,3 |
| Edificações comerciais | 0,6 | 0,4 |
| Bibliotecas, oficinas, garagens | 0,7 | 0,6 |
| Passarelas | 0,4 | 0,3 |
| Pontes rodoviárias | 0,5 | 0,3 |
| Pontes ferroviárias | 1,0 | 0,6 |

## 3. Esforços e flechas elásticas (tabelas do capítulo + fórmulas exatas da planilha)

Para vão L, abscissa adimensional x̄ = x/L; carga distribuída p; carga concentrada P em a (α = a/L, β = b/L); momentos de extremidade ME (esq.) e MD (dir.).

**Biapoiada — fórmulas usadas na planilha (61 pontos, x̄ de 0 a 1):**

| Efeito | M(x̄) | V(x̄) | flecha δ(x̄) (EI = Ecs·Ic) |
|---|---|---|---|
| Distribuída p | p·L²·(x̄ − x̄²)/2 | p·L·(1 − 2x̄)/2 | p·L⁴·(x̄ − 2x̄³ + x̄⁴)/(24EI) |
| Concentrada P em a | x̄≤α: P·L·β·x̄ ; senão P·L·α·(1−x̄) | x̄≤α: P·β ; senão −P·α | x̄≤α: P·L³·β·x̄·(1−β²−x̄²)/(6EI); espelhada no outro trecho |
| Parcial pd (centro k, ext. c) | 3 trechos (antes/dentro/depois) — ver fórmulas PD da planilha | idem | idem |
| ME (apoio esq.) | ME·(1 − x̄) | −ME/L | ME·L²·(1−x̄)·(1−(1−x̄)²)/(6EI) |
| MD (apoio dir.) | MD·x̄ | MD/L | MD·L²·x̄·(1−x̄²)/(6EI) |

**Valores máximos clássicos (tabela do capítulo):**

| Sistema | Mmáx | Vmáx | δmáx |
|---|---|---|---|
| Biapoiada, p | pL²/8 (x̄=0,5) | pL/2 | 5pL⁴/(384EI) |
| Apoiada-engastada, p | vão: pL²/14,22 (x̄=0,375); eng.: −pL²/8 | 5pL/8 (eng.) | pL⁴/(184,6EI) (x̄=0,4215) |
| Biengastada, p | vão: pL²/24; eng.: −pL²/12 | pL/2 | pL⁴/(384EI) |
| Balanço, p | −pL²/2 | pL | pL⁴/(8EI) |
| Biapoiada, P no meio | PL/4 | P/2 | PL³/(48EI) |
| Apoiada-engastada, P meio | vão: 5PL/32; eng.: −3PL/16 | 11P/16 (eng.) | PL³/(48√5·EI)≈PL³/(107,3EI) (x̄=0,447) |
| Biengastada, P meio | vão: PL/8; eng.: −PL/8 | P/2 | PL³/(192EI) |
| Biapoiada, P em a | P·a·b/L | Pβ / −Pα | (P·L³/(48EI))·α·(3−4α²), se α≤0,5 (flecha no meio) |

**Momentos de engastamento (usados pela planilha p/ apoios D):**
- p distribuída: apoiada-engastada M = −pL²/8; biengastada M = −pL²/12.
- P concentrada: biengastada Mesq = −P·L·α·β², Mdir = −P·L·α²·β; apoiada-engastada (engaste à dir.): M = −P·L·α·β·(1+β)/2... (planilha: −P·L·α·β·(1+α)/2 no direito, −P·L·α·β·(1+β)/2 no esquerdo — conferir sinal pela convenção).

Momento torçor (tabela do capítulo): t distribuído biengastado: T = ±tL/2; T concentrado no meio: ±T/2; em a: Tesq = T·β, Tdir = −T·α.

## 4. ELU-M — Flexão em seção retangular

### 4.1 Equações básicas (diagrama retangular, fck ≤ 50 MPa)

Equilíbrio: T = As·fyd = C = b·λx·η·fcd
Momento: Md = b·λx·η·fcd·(d − λx/2)

**Profundidade da linha neutra (armadura simples):**

x = 1,25·d·[1 − √(1 − Md/(0,425·b·d²·fcd))]

**Armadura:** As = 0,68·b·x·fcd/fyd  (equivale a As = b·λx·η·fcd/fyd, com λ·η = 0,68)

Forma adimensional: μ = Md/(b·d²·η·fcd); μ = λξ(1 − λξ/2) → λξ = 1 − √(1 − 2μ), ξ = x/d.

### 4.2 Limites de ductilidade e Md,lim

| Critério | xlim | Md,lim | As,lim |
|---|---|---|---|
| NBR 6118:2014 (dutil, fck≤50) | 0,45·d | 0,25092·b·d²·fcd | 0,306·b·d·fcd/fyd |
| Domínio 3/4 (fyk=500) | 0,62832·d | 0,31988·b·d²·fcd | 0,42726·b·d·fcd/fyd |
| Planilha (NBR 6118:2003) | 0,50·d | μlim = 0,32 → 0,32·b·d²·η·fcd | ρlim = λ·ξlim·η·fcd/fyd |

> Atenção: a planilha usa ξlim = 0,50 (norma 2003); o capítulo 2014 usa 0,45. Para fck > 50: ξlim = 0,35 (capítulo) / 0,40 (planilha). Em implementação nova, usar 0,45 (2014).

### 4.3 Armadura dupla (Md > Md,lim)

1. ΔM = Md − Md,lim
2. A's = ΔM/[σ'sd·(d − d')]  (armadura comprimida)
3. As = As,lim + ΔM/[fyd·(d − d')] = As,lim + A's·σ'sd/fyd
4. Tensão na armadura comprimida: ε's = 3,5‰·(xlim − d')/xlim; se xlim = 0,45d → ε's = 7,78‰·(0,45 − d'/d); se xlim = 0,62832d → ε's = 5,57‰·(0,63 − d'/d).
   σ'sd = fyd se ε's ≥ εyd; senão σ'sd = Es·ε's.

### 4.4 Armadura mínima e máxima

- **As,mín = máx(0,15%; 0,25·fctm/fyk)·b·h** (dedução: Md,mín = 0,8·W0·fctk,sup = 1,04·W0·fctm; z ≈ 0,8h).
  Por fck (fyk=500): C20-C30 → 0,15%; C35 → 0,16%; C40 → 0,18%; C45 → 0,19%; C50 → 0,20%; C60 → 0,21%; C70 → 0,23%; C80 → 0,24%; C90 → 0,25%.
  (Planilha usa aproximação máx(0,15%; 0,035·fcd/fyd)·b·h.)
- **As,máx:** As + A's ≤ 4%·b·h.
- **Armadura de pele:** As,pele = 0,10%·b·h **por face lateral**, obrigatória se h > 60 cm.

## 5. ELU-M — Seção T

**Largura colaborante** (NBR 6118 14.6.2.2): bf = bw + abas; aba ≤ 0,10·a (a = distância entre pontos de momento nulo) e ≤ metade da distância livre até a viga vizinha (mesa interna) / ≤ b3 real (mesa externa). Para vigas biapoiadas a = L; apoiada-engastada a = 0,75L; biengastada a = 0,60L; balanço a = 2L.

Com mesa comprimida (Md positivo), 3 casos:

**Momento resistido pela mesa:** MRf = bf·hf·η·fcd·(d − hf/2)

- **CASO 1 — Md ≤ MRf** (LN na mesa, λx ≤ hf): dimensionar como retangular com b = bf.
  x = 1,25d[1−√(1−Md/(0,425·bf·d²·fcd))]; As = 0,68·bf·x·fcd/fyd ≥ As,mín.
- **CASO 2 — MRf < Md ≤ Md,lim** (LN na alma, armadura simples): superposição abas + alma.
  - Abas: Ma = (bf − bw)·hf·η·fcd·(d − hf/2); Aa = 0,68·(bf − bw)·(1,25hf)·fcd/fyd = (bf−bw)·hf·η·fcd/fyd.
  - Alma: Mw = Md − Ma; x = 1,25d[1−√(1−Mw/(0,425·bw·d²·fcd))]; Aw = 0,68·bw·x·fcd/fyd.
  - As = Aa + Aw.
- **CASO 3 — Md > Md,lim** (armadura dupla na alma): Ma e Aa como no caso 2; Mw,lim = bw·λxlim·η·fcd·(d − λxlim/2); ΔM = Mw − Mw,lim; A's = ΔM/[σ'sd(d−d')]; Aw = Aw,lim + A's·σ'sd/fyd; As = Aa + Aw.

As,mín para seção T usa b = bw: As,mín = máx(0,15%; 0,25fctm/fyk)·bw·h.

## 6. ELU-V — Força cortante (analogia de treliça)

### 6.1 Verificação da biela comprimida

**VRd2 = 0,45·ν·fcd·b·d·sen(2θ)**, com ν = 0,6(1 − fck/250).
- Modelo I (simplificado): θ = 45° → VRd2 = 0,45·ν·fcd·b·d.
- Modelo II (refinado): 30° ≤ θ ≤ 45°.

Forma geral da planilha (α = inclinação do estribo, 90° usual):
VRd2 = 0,6(1−fck/250)·(fck/(10γc))·b·(0,9d)·(cotθ + cotα)·sen²θ  [kN, cm]

Valores de VRd2/(b·d) em kN/cm²: C20: 0,355 (45°)/0,307 (30°); C25: 0,434/0,376; C30: 0,509/0,441; C35: 0,581/0,503.

### 6.2 Parcela do concreto Vc

**Vc0 = 0,6·fctd·b·d** = 0,0126·fck^(2/3)·b·d/γc  [kN, cm, fck MPa]
- Modelo I: Vc = Vc0 (constante).
- Modelo II (interpolação da planilha): Vc = Vc0 se Vd ≤ Vc0; senão **Vc = Vc0·(VRd2 − Vd)/(VRd2 − Vc0)** (decai linearmente a zero quando Vd → VRd2).

Vc0/(b·d) em kN/cm²: C20: 0,0663; C25: 0,0769; C30: 0,0869; C35: 0,0963.

### 6.3 Armadura transversal

**Asw = (Vd − Vc)·s/(0,9·d·fywd·cotθ)** [s = 100 cm → Asw em cm²/m]
Geral (planilha): VRd3 = Vc + (Asw/100)·fywd·(0,9d)·(cotθ + cotα)·senα ≥ Vd.

**Asw,mín = 0,2·fctm·b·s/fywk** → ρw,mín = 0,2fctm/fywk:

| fck | 20 | 25 | 30 | 35 |
|---|---|---|---|---|
| ρw,mín CA-50 | 0,088% | 0,103% | 0,116% | 0,128% |
| ρw,mín CA-60 | 0,074% | 0,085% | 0,097% | 0,107% |

**Espaçamentos e bitolas:**
- sl,máx = mín(0,6d; 30 cm) se Vd ≤ 0,67·VRd2; senão mín(0,3d; 20 cm).
- st,máx (entre ramos) = mín(d; 80 cm) se Vd ≤ 0,2·VRd2; senão mín(0,6d; 35 cm).
- 5 mm ≤ φt ≤ b/10.
- Asw,máx (planilha): tal que Vsw ≤ VRd2 − Vc.

## 7. ELU-T — Torção (seção vazada equivalente)

- Espessura da parede: **te = máx(A/u; 2c1)**, com te ≤ b/2 e ≤ h/2 (a planilha usa te = mín(2c1; A/u) no exemplo com A/u = 2c1 = 10 — na prática te = A/u limitado; c1 = ct + φt + φ/2 ≈ 5 cm).
- Área e perímetro do fluxo: be = b − te; he = h − te; **Ae = be·he; ue = 2(be + he)**.
- Fluxo de cisalhamento: τ·te = Td/(2Ae).

**Biela:** TRd2 = κ·Ae·te·fcd·sen(2θ), κ = 0,5(1 − fck/250). TRd2/(Ae·te) kN/cm²: C25: 0,804 (45°)/0,696 (30°).

**Armaduras (por parede / total no perímetro):**
- Transversal (1 perna, por parede): **Asw,T = Td·s/(2·Ae·fyd·cotθ)** [cm²/m]
- Longitudinal total no perímetro ue: **As,T = Td·ue·tanθ/(2·Ae·fyd)** — distribuir proporcional ao trecho: face be → As,T·be/ue; face he → As,T·he/ue.
- Mínimas: Asw,T,mín = 0,2·fctm·te·s/fyk; As,T,mín = 0,2·fctm·te·ue/fyk.

**Superposições:**
- V + T (bielas): **Vd/VRd2 + Td/TRd2 ≤ 1**.
- Transversal total: Asw,total = Asw,V + 2·Asw,T (estribo de 2 ramos resiste V com os 2 ramos, T com 1 parede de cada lado).
- M + T (longitudinal): face tracionada por M: As = As,M + As,T·b_e/ue; face comprimida: As,T·be/ue (pode-se reduzir pela compressão); cada face lateral: As,T·he/ue.
- Espaçamento com torção: sl,máx = mín(0,6d; 30) se Vd/VRd2 + Td/TRd2 ≤ 0,67, senão mín(0,3d; 20); estribo fechado, ≤ 35 cm entre barras longitudinais de canto.

## 8. Ligação alma-mesa da seção T (armadura de costura)

- Δx = metade da distância entre seção de momento nulo e de momento máximo (limitado à distância entre cargas concentradas).
- Variação da força na aba: **Vfd = ΔFa = (ΔMd/z)·(ba/bf)** com z = 0,9d e ba = (bf − bw)/2 → Vfd = ΔMd·(bf−bw)/(2·bf·0,9d)... (na prática planilha/capítulo: Vfd = [(bf − bw)/(2bf)]·ΔMd/(0,9d)).
- Biela da mesa: VRd2 = 0,5·ν·fcd·hf·Δx·sen(2θ) ≥ Vfd.
- **Asf = Vfd·s/(Δx·fyd·cotθ)** [cm²/m, por face de corte].
- Dispensa (Eurocódigo 2): se Vfd ≤ Vfd,mín = 0,4·fctd·hf·Δx → basta armadura de flexão da mesa.
- Mínima de flexão da mesa: As,mín = máx(0,15%; 0,25·fctm/fyk)·100·hf [cm²/m] ≥ 1,5 cm²/m.

## 9. ELS-W — Abertura de fissuras (combinação frequente)

1. **Momento de fissuração:** Mr = Wc·fctf, com Wc = Ic/yt (retangular: b·h²/6) e fctf = fctm. Se MF ≤ Mr: não fissura, dispensa verificação.
2. **Estádio 2 puro** (seção retangular, com A's):
   x2 = [−a2 + √(a2² − 4·a1·a3)]/(2·a1), com a1 = b/2; a2 = αe·As + (αe−1)·A's; a3 = −d·αe·As − d'·(αe−1)·A's.
   I2 = b·x2³/3 + αe·As·(d − x2)² + (αe−1)·A's·(x2 − d')².
3. **Tensão no aço:** σs = αe·MF·(d − x2)/I2 (MPa com M em kNcm, cm → multiplicar ×10; a planilha faz ×1000 com M em kNm).
4. **Área de envolvimento:** Acr = b·mín(y + 7,5φ; h/2), onde y = dc = ct + φt + φ/2 + (camadas acima)·(φ + av) — distância da face tracionada ao centro da 1ª camada (planilha soma o desnível de camadas). **ρr = As/Acr**.
5. **Abertura característica: wk = mín(w1; w2) ≤ wlim** (η1 = 2,25 barra nervurada; 1,4 entalhada; 1,0 lisa):
   - w1 = [φ/(12,5·η1)]·(σs/Es)·(3·σs/fctm)
   - w2 = [φ/(12,5·η1)]·(σs/Es)·(4/ρr + 45)
   (φ em mm, σs e Es em MPa → wk em mm.)
6. wlim por CAA: I → 0,4 mm; II/III → 0,3 mm; IV → 0,2 mm.

## 10. ELS-DEF — Flechas (combinação quase permanente)

1. **Flecha elástica** δel com p = pQP, E = Ecs, I = Ic (curvas analíticas da seção 3).
2. **Rigidez efetiva (Branson):** se MQP ≥ Mr:
   **Ie = (Mr/MQP)³·Ic + [1 − (Mr/MQP)³]·I2 ≤ Ic**; senão Ie = Ic.
   Nota: para Mr no ELS-DEF o Musso usa fctf = fctm (mesmo Mr do ELS-W). A planilha calcula Ie separadamente para as combinações G, G+Q e QP (cada uma com seu M máximo).
3. **Flecha imediata:** δi = δel·(Ic/Ie).
4. **Flecha diferida (fluência):** δd = αf·δi(QP), com
   **αf = [ξ(t) − ξ(t0)]/(1 + 50ρ')**, ρ' = A's/(b·d);
   ξ(t) = 0,68·(0,996^t)·t^0,32 para t ≤ 70 meses; ξ = 2,0 para t > 70.
   ξ: 1 mês → 0,68; 3 → 0,95; 6 → 1,18; 12 → 1,44; >70 → 2,00.
5. **Verificações (planilha, Tabela 13.3 da NBR 6118):**
   - ΔT (total) = Δcontraflecha + δi(QP) + δd ≤ **L/250** (aceitabilidade visual);
   - ΔQ (parcela da carga variável) = δi(G+Q) − δi(G) ≤ **L/350** (vibração);
   - ΔA (após construção das paredes, se aplicável) = δd (ou δiQ + δd) ≤ **mín(L/500; 10 mm)** (alvenaria);
   - contraflecha ≤ L/350.
   - Em balanço, usar L = 2·Lbal.
6. A planilha computa δiQ como diferença δi(G+Q) − δi(G), cada uma com seu próprio Ie — mais preciso que aplicar Ie único.

## 11. Detalhamento da armadura longitudinal

### 11.1 Na seção

- Espaçamentos livres mínimos: **ah ≥ máx(20 mm; φ; 1,2·dag)**; **av ≥ máx(20 mm; φ; 0,5·dag)** (dag: brita 0 = 9,5; brita 1 = 19; brita 2 = 25 mm).
- **Nº máx de barras por camada: nb = INT[1 + (b − 2ct − 2φt − φ)/(ah + φ)]**.
- **Nº máx de camadas: nc = INT[1 + (2×10%·h)/(av + φ)]** — o centroide da armadura deve ficar a dc ≤ 10%·h da face tracionada.
- Altura útil real: d = h − (ct + φt + φ/2 + desnível do centroide das camadas). Planilha (por camadas iguais): d = h − [ct + φt + φ/2 + (av + φ)·(Q1·(n² − n)/2 + Q2·n)/Qtotal], onde n = camadas cheias com Q1 barras e Q2 = resto. Alternativa rápida: d = 0,9h.
- Área de Q barras: As = Q·π·φ²/4 (tabela T1 do capítulo, φ 5 a 25 mm).

### 11.2 Ao longo do elemento (ancoragem)

- **Zonas de aderência:** boa = barras a menos de 30 cm do fundo (h ≤ 60) / fora dos 30 cm superiores; má = topo de vigas altas (h > 60) e camadas superiores.
- **fbd = 2,25·fctd** (boa, nervurada, φ ≤ 32): C20: 2,487; C25: 2,886; C30: 3,259; C35: 3,611 MPa. Zona má: ×0,7.
- **lb,bás = (φ/4)·(fyd/fbd)** (fyk=500): boa: C20 43,7φ; C25 37,7φ; C30 33,4φ; C35 30,1φ. Má: C25 53,8φ.
- **lb,nec = α1·lb,bás·(As,calc/As,ef) ≥ lb,mín = máx(0,3·lb,bás; 10φ; 10 cm)**; α1 = 1,0 reta, 0,7 com gancho.
- **Decalagem: al = 0,5·z·cotθ = 0,45d (θ=45°) ou 0,78d (θ=30°)** — desloca o diagrama de momentos.
- **Ancoragem no apoio extremo:** As,apoio ≥ As,vão/3; ancorar Rd = Vd (regra: As,anc ≥ Vd·cotθ/(2fyd)... capítulo: al/d) com lb,nec a partir da face; gancho se necessário.
- **Apoio interno:** As,apoio ≥ As,vão/4 se |Mint| > Mvão/2; senão As,vão/3; estender ≥ 10φ além da face.
- Ganchos: raio interno ≥ 5φ (φ<20) / 8φ (φ≥20); prolongamento reto 8φ.

### 11.3 Armadura de suspensão (apoio indireto — viga sobre viga)

Quando a viga v2 (apoiada) descarrega na v1 (suporte): **As,sus = Rd·(h2/h1)/fyd** se h2 ≤ h1 (caso geral As,sus = Rd/fyd), concentrada na interseção, majoritariamente na viga suporte.

## 12. Motor da planilha VIGA-MUSSO-2014-2.xlsm (algoritmo)

### Aba Principal (entrada + esforços + ELS)
1. Entrada: b, h, L, apoios esq/dir (1 = apoiado I, senão engaste D), cargas (PP automático 25·b·h opcional; UD g/q; até 4 CC concentradas P em a; 2 PD parciais; momentos de apoio Mesq/Mdir com parcelas G e Q — vindos p.ex. de análise global).
2. Momentos de engastamento automáticos quando o apoio é D (fórmulas seção 3).
3. Gera 61 pontos (x̄ = 0…1 passo 1/60) de M e V por caso de carga e por combinação: ELU (1,4G+1,4Q), QP (G+ψ2Q), F (G+ψ1Q).
4. ELS-DEF e ELS-W calculados como nas seções 9-10.
5. Painel de resultados: 4 verificações com razão Sd/Rd e "OK!/NÃO!" — ELU-M = máx |Md|/MRd das 3 seções; ELU-V idem; ELS-DEF = ΔT/ΔT,lim; ELS-W = wk/wlim.

### Aba Momento (dimensionamento automático à flexão)
1. MSd por seção (apoio esq, vão, apoio dir) = máximo do diagrama ELU.
2. Tabela de candidatos: para cada bitola (6,3/8/10/12,5/16/20) e Q = 2…30 barras, calcula camadas (nb por camada, resto), As, d real (pelo centroide) e **MRd = As·fyd·[d − As·fyd/(2·b·η·fcd)]**, invalidando arranjos que violem: As ≤ ρlim·b·d (ductilidade); As ≥ As,mín; dc ≤ 10%h (planilha: 5%h no critério da última camada); ≥ 2 barras por camada.
3. Para cada bitola: menor Q com MRd ≥ MSd (busca decrescente); entre bitolas viáveis: **menor As**. Sai: "Q φ bitola, camadas Q1×n+resto, As, d, MRd, MRd,máx".

### Aba Cortante (dimensionamento automático ao cisalhamento)
1. VSd por trecho (apoio esq = V(0); vão = maior |V| em x̄=0,25/0,75; apoio dir = |V(L)|), d = 0,9h.
2. Modelo I (θ=45°) ou II (θ=30°, default), α = 90°, 2 ramos.
3. VRd2, Vc0 e Vc (interpolado por trecho no modelo II), Asw,mín, Asw,máx, sl,máx, st,máx, φt ≤ b/10.
4. Tabela de candidatos: φt ∈ {5; 6,3; 8; 10; 12,5} × s ∈ {7…30 cm} → Asw = ramos·(100/s)·π·φt²/4; VRd3 = Vc + Vsw; invalida se viola limites; escolhe **menor Asw** com VRd3 ≥ VSd. Sai: "φt c/ s, Asw, VRd3, VRd3,máx".

## 13. Valores golden para testes (casos resolvidos)

### 13.1 Viga V2 do capítulo — contínua 2 vãos de 5 m, seção 15×50 (d=45), fck 25, CA-50/CA-60, g=20,24, q=6,34 kN/m (pd=37,21; pF=24,04; pQP=22,78)

| Verificação | Local | Entrada | Resultado esperado |
|---|---|---|---|
| ELU-M | vão | Md=65,4 kNm | x=8,64 cm < xlim=20,25 → As=3,62 cm² → 2φ16 (4,02) |
| ELU-M | apoio central | Md=116,3 kNm | x=16,65 cm → As=6,98 cm² → 4φ16 (8,04) |
| ELU-V (θ=45°, CA-60 fywk=600) | trecho 1 | Vd=69,8 kN | VRd2=292,9; Vc=51,9 → Asw=0,85 < mín 1,28 cm²/m → φ5 c/27 |
| ELU-V | trecho 2 | Vd=116,3 kN | Asw=3,05 cm²/m → φ5 c/12; sl,máx=27 cm |
| ELS-W (φ16, η1=2,25, ct=3) | vão | MF=42,3 kNm; Mr=16,0 | x2=12,37; I2=46916; σs=257 MPa; Acr=245 cm²; ρr=1,64%; w1=0,21; w2=0,20 → wk=0,20 ≤ 0,3 |
| ELS-W | apoio | MF=75,1 kNm | x2=16,38; I2=79598; σs=236 MPa; Acr=299; ρr=2,69%; w1=0,18; w2=0,12 → wk=0,12 |
| ELS-DEF (ψ2=0,4; t=70; t0=1 mês) | vão | MQP=40,0; Mr=16,0; δel=2,10 mm | Ie=53913 cm⁴; δi=6,09; αf=1,32; δd=8,04; δT=14,13 ≤ L/250=20 mm |

### 13.2 Exemplos seção T do capítulo (fck 25, CA-50)

| Ex. | Seção (cm) | Esforço | Resultado |
|---|---|---|---|
| 1 flexão | bf150 hf10 h70 d65 bw30 | Md=791 kNm | x=6,98; λx=5,58<hf (caso 1); As=29,3 cm² → 10φ20 |
| 1 cortante θ45 | idem | Vd=421,9 kN | VRd2=846,2; Vc=150 → Asw=10,7 cm²/m → φ10 c/14 (2R) |
| 2 costura θ45 | idem | Δx=1,875 m; ΔMd=593,3 | Vfd=405,7 < VRd2=904; Asf=4,97 cm²/m → φ6,3 c/12 (2R); Vfd,mín=93,6 |
| 3 flexão | bf180 hf10 h80 d75 bw50 | Md=1894,5 kNm | x=12,37; As=62,2 cm² → 20φ20 |
| 3 cortante θ30 | idem | Vd=801 kN | VRd2=1409,2; Vc0=288,5; Vc=156,6 → Asw=12,68 → φ8 c/15 (4R) |
| 4 costura θ30 | idem | Δx=2 m; ΔMd=1368 | Vfd=731,9 < VRd2=835,1; Asf=4,86 cm²/m |

### 13.3 Exemplo torção do capítulo — balanço 2 m, 30×60 (d=55), fck 25, CA-50, Fd=200 kN excêntrico 20 cm (Md=400 kNm; Vd=200 kN; Td=40 kNm), θ=45°, c1=5

| Item | Valor |
|---|---|
| As,M | 20,3 cm² (x=24,24 < xlim) |
| VRd2 / Asw,V | 716 kN / 3,39 cm²/m (Vc=127) |
| te / Ae / ue | 10 cm / 1000 cm² (20×50) / 140 cm |
| TRd2 / Asw,T / As,T | 80,4 kNm / 4,60 cm²/m por parede / 6,44 cm² |
| Vd/VRd2 + Td/TRd2 | 0,78 ≤ 1 OK |
| Asw,total | 3,39 + 2·4,60 = 12,6 cm²/m → φ10 c/12 (2R) |
| As,inf (compr.) / As,sup (trac.) / As,lat | 0,92 / 20,3+6,44·20/140 = 21,2 / 2,30 cm² por face |

### 13.4 Caso default da planilha — biapoiada 7,5 m, 30×60, fck 25, CA-50, ct 2,5, brita 19; UD g=34,1, q=14,26 kN/m; Mesq = −74,9(G) −31,3(Q); Mdir = −202,9(G) −84,8(Q); ψ1=0,6; ψ2=0,4

| Verificação | Seção | Sd | Dimensionamento | Rd | Sd/Rd |
|---|---|---|---|---|---|
| ELU-M | apoio esq | 148,68 kNm | 4φ16 (1×4), As=8,04, d=54 | MRd=175,40 (máx 417,73) | 0,356 |
| ELU-M | vão (x=3,25 m) | 208,79 kNm | 5φ16 (1×5), As=10,05, d=54 | MRd=215,05 | 0,500 |
| ELU-M | apoio dir | 402,78 kNm | 11φ16 (1×6+5), As=22,12, d=54 | MRd=417,73 | 0,964 |
| ELU-V (mod. II θ30) | apoio esq | 220,01 kN | φ6,3 c/19 (Asw=3,28) | VRd3=220,20 (máx 426,07) | 0,516 |
| ELU-V | vão | 160,83 kN | φ6,3 c/20 (Asw=3,12) | VRd3=229,43 | 0,364 |
| ELU-V | apoio dir | 287,77 kN | φ6,3 c/11 (Asw=5,67) | VRd3=290,09 | 0,704 |
| ELS-DEF | vão | ΔT=26,29 mm | Ie: G=199080, G+Q=178589, QP=187364; I2=167538; x2=15,10; Mr=46,17; αf=1,3227 | ΔT,lim=30 (L/250); ΔQ=5,31≤21,4 | 0,876 |
| ELS-W | apoio esq | MF=93,68 | x2=13,74; I2=140003; σs=235,7; ρr=1,68%; w1=0,176; w2=0,181 | wk=0,176 ≤ 0,3 | 0,587 |
| ELS-W | vão | MF=131,54 | x2=15,10; I2=167538; σs=267,2; ρr=2,10%; w1=0,226; w2=0,170 | wk=0,170 | 0,567 |
| ELS-W | apoio dir | MF=253,78 | x2=20,72; I2=303292; σs=243,7; ρr=3,77%; w1=0,188; w2=0,0996 | wk=0,0996 | 0,332 |

Constantes deriváveis conferidas: fcd=17,86; fctm=2,565; Ecs=24 GPa; αe=8,75; η1=2,25; εyd=2,070‰; VRd2 (mod. II 30°, α90) = 608,78 kN; Vc0 = 124,66 kN; Asw,mín = 3,08 cm²/m; μlim=0,32 (ξlim 0,50, norma 2003); Ic=540000 cm⁴; Wc... Mr=46,17 kNm.

## 14. Notas para implementação no dlima-estrutural

1. O módulo de vigas atual (Clapeyron/isostáticas) pode ganhar: **decalagem al**, **ancoragem nos apoios (As/3, As/4, lb)**, **seção T (3 casos + costura)**, **torção com superposições**, e o **seletor automático de arranjo** (bitola × quantidade × camadas com d real) da aba Momento — é o mesmo padrão "tabela de opções para o Leonan escolher" já adotado.
2. Divergências 2003 → 2014 a padronizar: ξlim = 0,45 (não 0,50); As,mín pela tabela 0,15%+ (não 0,035·fcd/fyd).
3. O cálculo de flecha da planilha (Ie por combinação + δiQ por diferença) é mais fiel que o simplificado; adotar.
4. Golden values das seções 13.1–13.4 servem de suíte de testes de regressão (tolerância <1%, mesmo padrão usado nos exemplos Musso de lajes).
