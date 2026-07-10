# Estudo das planilhas — Curso Estrutural na Real (Eng. Waltner Wagner)

> Fórmulas extraídas integralmente das 43 planilhas únicas (de 54) em `material/estrutural-na-real/`. Unidades originais: tf, tf/m², tf/cm² (planilhas Waltner) e kN (planilhas de metálica). Convenção Waltner: KMD/KX/KZ adimensionais estilo tabela de dimensionamento; fck em MPa; conversão p/ tf: fck·100 = tf/m², fyk/100 = tf/cm².
> Este doc registra o MÉTODO de cálculo (engenharia NBR 6118/8800, não protegida); não reproduz texto autoral do curso.

## 1. Núcleo comum de flexão (padrão Waltner, aparece em todas as planilhas de concreto)

Parâmetros (fck ≤ 50 MPa; fórmulas gerais p/ C55+ incluídas nas planilhas):
- εcu = 3,5‰ (se fck>50: 2,6+35·((90−fck)/100)⁴); fctm = 0,3·fck^(2/3) (se >50: 2,12·ln(1+0,11fck)); fctk,sup = 1,3·fctm; fctk,inf = 0,7·fctm; αc = 0,85 (se >50: 0,85(1−(fck−50)/200)); λ = 0,8 (se >50: 0,8−(fck−50)/400).
- σcd = αc·fcd = 0,85·fck/1,4; fyd = fyk/1,15; εyd = fyd/Es; Es = 210 GPa (2100 tf/cm²); εsu = 10‰.
- E do concreto: Ecs = αi·5600·√fck, αi = 0,8+0,2·fck/80 (idem Musso).

Fluxo de dimensionamento (seção retangular b×h, d = h−d'):
1. **KMD** (=μ) = Md/(b·d²·σcd)
2. **KX** (=ξ) = [1−√(1−2·KMD/0,85)]/0,8 — (na variante com αc/λ genéricos: [1−√(1−2μ/αc)]/λ)
3. x = KX·d; **domínios**: KX2-3 = εcu/(εcu+εsu) = 0,259; KX,lim = 0,45 (fck≤50) / 0,35; KX3-4 = εcu/(εcu+εyd)
4. **KZ** = 1−0,4·KX; z = KZ·d
5. **As = Md/(z·fyd)**; deformações: εcd = εsu·ξ/(1−ξ) no dom. 2; εsd = εcu·(1−ξ)/ξ no dom. 3/4
6. **Md,mín = 0,8·W0·fctk,sup** (W0 = b·h²/6) → As,mín correspondente; **ρmín** tabelado: 0,15% até C30; 0,164% C35; 0,179% C40; 0,194% C45; 0,208% C50 → As,mín = ρmín·b·h
7. Se KX > KX,lim: exige armadura dupla (mensagem na planilha).

Detalhamento padrão: espaçamento = área_barra/As·100, limitado a **mín(20 cm; 2h)** p/ armadura principal de laje; secundária ≥ máx(As/5; 0,9 cm²/m; 0,5·ρmín·h) com s ≤ 30 cm (padrão NBR de lajes; usado tb nas escadas).

## 2. Escadas (Formação Escadas na Real + planilhas bônus)

### 2.1 Escada reta e plissada (bi-apoiadas, por metro de largura ou largura real)
- **Espessura real p/ peso próprio**: reta: e_real = e·L_incl/L + espelho/2 (L_incl = √(L²+H²)); **plissada: e_real = e·(L+H)/L** (dobras somam horizontal+vertical).
- pp = 25·e_real/100 [tf/m²? kN? — planilha usa tf: 2,5·e_real(cm)/100]; q_total = pp + G(rev=0,1 tf/m²) + SC(0,25 tf/m²).
- Mk = q·L²/8; μ = 1,4·Mk/(d²·σcd·b); ξ = 1−√(1−2μ); **As = máx(ξ·d·b·σcd/fyd; 0,15%·b·h)**.
- Flecha: δ = (5/384)·q·b·L⁴/(E·I)·**3,5** (fator 3,5 = fluência embutida ≈ 1+αf com αf=2,5? na prática (1+2,5)); E = 0,85·5600√fck; I = b·h³/12 bruto; δlim = L/250.
- Cortante (laje sem estribo, modelo NBR 6118 19.4.1): τRd = 0,0375·fck^(2/3) [tf/cm² /100]; ρ1 = As/(b·d); k = 1,6−d(m) — na planilha (160−d_cm)/100; **VRd1 = τRd·(1,2+40ρ1)·k·b·d** ≥ Vsd = 1,4·q·b·L/2.

### 2.2 Escada espinha de peixe e flutuante (viga central + degraus em balanço)
- Sistema: viga-espinha (b×h) no eixo (espinha de peixe) ou longarina lateral (flutuante) + degraus engastados.
- Tabela de vinculação (α p/ M+ = qL²/α; β p/ M−; γ p/ flecha = qL⁴/(γEI); δ p/ V = coef·qL): Apoio/Apoio (8; ∞; 76,8; 0,5), Apoio/Engaste (14,2; 8; 184,8; 0,625), Eng/Eng (24; 12; 384; 0,5), Livre/Balanço (∞; 2; 8; 1,0), Eng.Red/Eng.Red (16; 16; 172; 0,5), Apoio/Eng.Red (12; 10,67; 137; 0,6), EngRed/Eng (21,05; 10,7; 277,4; 0,531).
- Carga na viga: pp_viga_inclinada = (b·h)·2,5·L_incl/L + pp_degraus; + (SC+G)·largura.
- Degrau (balanço): vão = largura/2 (espinha) ou largura+b_viga/2 (flutuante); Mk_degrau = pp_deg·a²/2 + SC·a; Md = 1,4·Mk; dimensiona por μ/ξ como laje; As,mín = 0,15%.
- **Torção na viga** (degraus alternados): Td = 1,4·máx(0,25·a; a·L·SC·a/4); TRd2 = 0,5·(1−fck/250)·σcd·(b/2)·h·mín(b,h)/100; armadura A90 = Td/2/(braço) somada ao estribo; As,pele ≥ 0,1%·b·h por face (2×).
- Cortante viga: Vd com coef δ da vinculação; VRd2 = 0,27·(1−fck/250)·σcd·b·d [αv2 embutido]; Vc = 0,6·fctd·b·d (fctd = 0,21·fck^(2/3)/1,4/100 tf/cm²); Asw = máx((Vd−Vc)/(0,9·d·fyd) + A90_torção; ρsw,mín·b) com ρsw,mín = 0,2·fctm/fywk; s ≤ mín(30; 0,6d; Asw_estribo/Asw_nec).
- Flecha da viga: seção fissurada — x da seção homogeneizada com As_comprimida equivalente, I_fissurada = b·x³/3-ish (planilha usa centroide aço+concreto), **EI_eq de Branson**: mín(E·[(Mr/Mk)³·Ic + (1−(Mr/Mk)³)·I_fiss]; E·Ic), Mr = (b²/6)·fctd(!); flecha imediata = q·L⁴/(EI_eq·γ_vinculação); **diferida: αf = (2−ξ(t0))/(1+50ρ')**, ξ(t) = mín(2; 0,68·0,996^t·t^0,32), t0 = tempo de escoramento em meses (dias·12/365); flecha_total = δi + δ_dif + 0,3·δ_SC − contraflecha; δlim = L/250; contraflecha ≤ 0,8·δlim + δi.
- Ancoragem: fbd = 2,25·η1·fctd; lb = (φ/4)·(fyd/fbd)·(As,calc/As,ef).

### 2.3 Escada helicoidal (flexo-tração) e lances com tração/compressão (flexão composta)
- Planilha de **flexão composta** (Nsd + Msd, por metro): momento transportado p/ armadura: ys = h/2−d'; **MRd_arm = Msd − Nsd·ys** (tração reduz/aumenta conforme sinal); μ com MRd_arm; ξ; Rcd = força no concreto; **Rsd = Rcd + Nsd**; σsd = fyd se εsd ≥ εyd, senão εsd·Es; **As = Rsd/σsd** ≥ As,mín(=ρmín·b·h, Md,mín=0,8·W0·fctk,sup).
- **Helicoidal**: mesma flexão composta na seção + **armadura de borda p/ tração** Nsd_borda: As_borda = Nsd(tf)·10·1,15/50 = Nsd·γf... (na prática Nd/fyd em cm²) — barras concentradas na borda externa (ex.: 28 tf → 6φ12,5).
- Degrau de flutuante/espinha (planilha FLEXÃO SIMPLES DEGRAU): dimensiona o degrau-viga b=0,30 m e verifica estribo mínimo Asw,mín = 0,2·(fctm/fyk)·b [cm²/m] com espaçamento por barra dupla.

### 2.4 Flexão simples de laje de escada (FLEXÃO SIMPLES LAJE)
- Idem núcleo comum, b = 1 m; verificação de cisalhamento VRd1 como em 2.1; armadura secundária = 0,2·As ≥ 0,9 cm²/m.

## 3. Reservatórios (Módulo 5 / Estruturas Especiais — série do prof. da pós)

### 3.1 01_Flexo-Tracao.xlsx (lajes/paredes com N de tração + M)
- Unidades: tf, cm; b = 100 cm. e0 = Md/Nd; **e1 = |e0 − (d−d')/2|; e2 = e0 + (d−d')/2**.
- Classificação: **F.T.G.E.** (grande excentricidade, e0 > (d−d')/2): flexão com linha neutra: x = d/λ·(1−√(1−2·Nd·e1... )) — na planilha: x = (d/λ)·[1−√(1−2·Nd·e2/(αc·ηc·fcd·b·d²))]; domínio por x/d; se Md,duc excedido → armadura dupla; **As1 = (αc·ηc·fcd·b·λ·x + As2·σ2 + Nd)/fyd** (tração soma) ≥ 0,15%·b·h; **F.T.P.E.** (pequena exc.): As1 = Nd·e2/(fyd·(d−d')); As2 = Nd·e1/(fyd·(d−d')) (2 lonas tracionadas).
- ηc = (4/fck_kN)^(1/3) se fck>40... (planilha: se fck(kN/cm²)≤4 → 1). Md,mín = 2·b·h²·0,39·fck^(2/3)/15 (forma interna da planilha).
- Tabela de As por φ (4,2 a 10 mm) × s (5 a 15 cm) embutida p/ escolha (padrão "tabela de aço").

### 3.2 02_Fissuracao.xlsx (ELS-W de reservatório — método da tirante/flexo-tração, EC2-like)
Por região (Tampa x/y, Fundo x/y, Paredes, ligações parede-parede e fundo-parede):
- Estádio 2 com N: e1 = e0−(d−3)/2; x por flexo-compressão equivalente; As nec e As adotada (φ, s).
- **wk,lim = 0,2 mm** (estanqueidade), ligações: wlim reduzido = (225−5·h_cm·240/15)/1000-ish (fórmula da planilha p/ ligação).
- Retração+temperatura: εcs = 0,5‰, εcT = 0,2‰, εcn = Bs·εcs+εcT; coeficiente Bs = √((90−7)/(350·(h/100)²+90−7)) p/ fundo.
- Seção fissurada: ρ = As/(b·d); n = Es/Ecs (=210000/28980 C25); **ξ = −nρ+√((nρ)²+2nρ)** (LN adimensional); k2 = ξ²/6·(3−ξ); **σs = n·(1−ξ)/k2·Ms/(b·d²) + N/As + Es·0,5·εcn** (parcela de retração!).
- Área efetiva: h0 = mín(2,5(h−d); (h−x·d)/3); Ace = b·h0; ρse = As/Ace; **σsr = (1+n·ρse)/ρse·fctm** (tensão de fissuração); β = 0,6 (curta) / 0,38; τbm = 1,35·fctm / 1,8·fctm.
- **εsm−εcm = máx(σs/Es − β·τbm/(ρse·Es)·(1+n·ρse); 0)**; **wk = σs/(2τbm)·φ/(1+nρse)·(εsm+0,5εcn)** (formulação de espaçamento de fissura por aderência — método EC2/MC90 adaptado) ≤ wlim.

### 3.3 03_Flexao_Simples_AE.xlsx (flexão simples "água-empuxo", tf/cm, b=100)
- Kfd = fpk·0,7·K/2 (fator de resistência do concreto com K de compressão na flexão — planilha genérica p/ σcd), x = (d/0,8)·[1−√(1−2Md/(Kfd·b·d²))] limitado a xduc = 0,45d; domínio; armadura simples/dupla com Md,duc = Kfd·0,8·b·xduc·(d−0,4xduc); As1 = (0,8·Kfd·b·x + As2σ2)/fsd ≥ 0,15%bd; equilíbrio verificado (ΣFx=0, ΣM=0); tabela de barras 6,3–25 p/ N barras.

## 4. Lajes treliçadas (Waltner) — complementa musso-lajes

- Geometria: treliça h_tr × b_vigota 12/13/14 cm, espaçamento s (50 cm típico), capa hc; % enchimento = (s−b)·h_tr/((h_tr+hc)·s); **pp = [(h_tr+hc)·2,5·(1−%ench) + (h_tr+hc)·γ_ench·%ench]/100** tf/m²; EPS γ=0,01 tf/m³, cerâmico 1,3.
- Vinculação (αx p/ M+= pL²/αx; βx p/ M−; γ flecha; δ cortante): Ap/Ap (8; –; 25,6; 0,5), Ap/Eng (14,2; 8; 61,6; 0,65), Eng/Eng (24; 12; 128; 0,5), Balanço (–; 2; 2,67; 1,0).
- Flexão por nervura→por metro: μ, ξ, As = ξ·s·d·σcd/fyd_treliça; base da treliça (2φ5 CA-60 + sinker) + **reforço**: As_ref = (As_calc − As_base)·fyk_treliça/fyk_reforço (compatibiliza CA-60/CA-50).
- Cortante por nervura (sem estribo): Vd = q·L·δ·s·1,4; **Vres = τRd·(1,2+40ρ1)·k·b_vigota·(h_tr+hc)** com τRd = 0,0375fck^(2/3), k = (160−d)/100.
- Verificação CYPE (planilha 2): idem + contribuição das **diagonais da treliça** ao cortante: Vsw_diag = As_diag/20·0,9·d·fyd·(sen+cos do ângulo)·(h_tr/comp_diag)·100/s; Vr = máx(VRd1; Vc+Vsw).
- Flecha: I da seção T-nervura homogênea por metro; δ = q·L⁴/(E·I·γ) ≤ L/250; **tempo mínimo de escora: fck_mín_retirada = fck/√(δlim/δ) ≥ 20 → t = 28/(4·ln(fck_t/fck)−1)² dias** (curva de crescimento fck(t) invertida).
- Catálogo de treliças (Gerdau/ArcelorMittal): TR8L(6/4,2/4,2, 0,735 kg/m), TR8M(6/5/4,2, 0,825), TR12M(6/5/4,2, 0,886), TR12R, TR16L/R, TR20L/R, TR25L/R (topo/base/diag mm, kg/m) — tabela completa na planilha QUANT. VIGOTAS.

## 5. Viga (DIM VIGA Waltner — pré-dimensionamento rápido)

- Vão eixo-a-eixo = L_livre + mín(ap1/2; 0,3h) + mín(ap2/2; 0,3h).
- Md± = q·Lef²/α_vinc·1,4 (tabela α/β: Ap/Ap 8/∞; Livre/Balanço ∞/2; + reação δ, δ2 e ζ).
- μ, ξ (limite 0,36 = aviso "momento acima do limite"), As = ξ·d·b·σcd/fyd; d = h − c − φt − φl/2.
- Cortante: Vd = (reação − q·d)·1,4 (redução no apoio!); VRd2 = 0,27·(1−?)·σcd·b·d (0,27 = 0,45·0,6·(1−fck/250) embutido? planilha usa direto 0,27·σcd·b·d); Vc = 0,6·fctd·b·d; **Asw = máx((Vd−Vc)/(0,9d·fyd); ρw,mín·b)** com ρw,mín = 0,2·fctm/fyk; s = mín(Asw_estribo/Asw; 0,6d; 30).
- Flecha: bruta δ = q·Lef⁴/(E·I·γ) com fluência ×(1+2); "flecha relativa 1/x ≥ 250" OK. Taxa de aço total ≤ 4%.
- Armadura de pele se h > 60: 0,10%·b·h por face.

## 6. Metálica — Módulo 11 (galpões/mezaninos/escadas NR12; cargas p/ modelagem)

- **Telhas**: verificação σ_atuante vs σ_adm do catálogo (interpolação linear no vão entre terças); correção de flecha **σ_adm(L/200) = K_forn/K_ABCEM·σ_adm_forn** (K=120 forn / 200 ABCEM); combinações: (a) PP+SC (SC mín 0,25 kN/m²); (b) PP−vento (q·Cpe, sucção); (c) zona crítica de arrancamento: Cpe,máx = −1,4 na faixa y = mín(h; 0,15b); conversão 1 kN/m² = 101,97 kgf/m².
- **Coberturas 2 águas (treliça banzo inferior plano)**: geometria (vão, nº nós, altura), decomposição de cargas por nó (PP telha+terças+SC+vento por área de influência) → esforços axiais nas barras (planilha resolve a treliça por seções/nós — grande, 26k chars, com verificação de barras por esbeltez/compressão).
- **Escadas NR12**: geometria (inclinação = atan(Z/X); degrau t≥?; h ≤ 0,25; projeção r ≥ 0,015; **verificação 0,60 ≤ g+2h ≤ 0,66**); distância entre degraus na longarina = √(t²+h²); cargas: chapa xadrez 0,27 kN/m², SC pessoas 2,5 kN/m² → carga por nó/viga.
- **Mezanino**: painel wall 0,32 + contrapiso 19·e + porcelanato 0,16 kN/m²; SC 2,0; carga linear na viga secundária = q·d_vigas.
- **Platibanda**: F = Ae·C·q com C_barlavento = 1,3, C_sotavento = 0,8 (força no beiral por montante).
- **Reações de Base**: organizador das envoltórias de reações por placa (máx. compressão / máx. tração por combinação, "concreto em fundações" e "tensões sobre o terreno", estilo saída CYPE3D) p/ pilares treliçados e de mezanino — alimenta o dimensionamento da placa de base. Convenção: compressão + nas reações, − nas barras.
- **Placa de base engastada (método AISC-ASD, perfis H/W, mín. 4 chumbadores)**:
  - Regras construtivas: furo = φ_chumb + 3,2 mm; assentar sobre grout; chumbador engastado 300–500 mm; nunca concreto simples; enrijecedores reduzem espessura.
  - Chumbadores: d_furo-furo ≥ 6,5·φ; d_borda ≥ 2·φ; braço de alavanca d_alav = C − 2·d_borda; **tração nos chumbadores N_t = MSd/d_alav** (kN, com MSd em kNm); por barra = N_t/n_t; **resistência N_Rd,t/barra = 0,33·fu·A_barra** (ASD); cisalhamento análogo com fração de fu.
  - Geometria da placa (B×C): m = (C − 0,95·d_perfil)/2; n = (B − 0,8·bf)/2; n' = √(d·bf)/4.
  - **Espessura**: por flexão da aba tracionada: M_chapa = N_t,chapa·d_furo-perfil → **t = √(6·M_chapa/(fb·C))** com fb = 0,75·fy; e pelo lado comprimido: t = 2·m·√(fc/fy); adotar comercial (tabela de chapas).
  - Concreto: **fc = N/(B·C) ≤ 0,35·fck** (kN/cm², sem confinamento).
  - Solda (filete 45°): verificação metal-solda vs metal-base: (bw·0,3·fu_solda)/(tf·0,4·fy) ≤ 1; resistência do cordão R_w = n·L·(0,7·bw)·0,3·fu_solda; aba: L = bf; alma: L = d − 6·tf, 2 cordões.
- **Coberturas 2 águas / vento**: planilha completa de **NBR 6123** — V0, S1 (topográfico, com interpolação talude/morro), S2 (rugosidade por categoria + classe por dimensões + fator de rajada por altura), S3 (estatístico) → Vk = V0·S1·S2·S3, **q = 0,613·Vk² (N/m²)**; sobrecarga mínima de cobertura metálica 0,25 kN/m² (NBR 8800 anexo B.5.1); geometria da tesoura (inclinação %→graus, banzo superior, montantes por terça, segmentos) e decomposição de cargas por nó p/ resolver a treliça.

## 7. Gestão / negócio (Waltner)

- **Precificação de projeto**: preço_base = área·R$/m² + acréscimos % por complexidade (balanço 2-4m +10%, >4m +20%; viga de transição 10/15/20%; vão 6-9m +10%, >9m +15%; escada moderna +7%; desnível de terreno 10/15%; fundação profunda +15%, excêntrica +10%; piscina na cobertura +20%; detalhe extra +10%) + NF 11%.
- **Estimativa de custo de estrutura** (sem fundação): parâmetros base — aço 10 kg/m² (×1,15 alto padrão, ×0,9 baixo), concreto 0,15 m³/m², fôrmas 1,2 m²/m² (vigas+pilares) × coef. reaproveitamento 0,6; preços de referência (2020): armador 1,8 R$/kg, carpinteiro 25 R$/m² vigas/pilares + 11 R$/m² laje, concreto bombeado 19 R$/m³ MO + 320 R$/m³ material, aço 4,8 R$/kg, fôrma 60 R$/m², laje treliçada TR8 26 R$/m² (TR12+ 36).
- **Quantitativo de aço**: por bitola, comprimento total × peso linear (πφ²/4·7850/10⁴ kg/m) × 1,10 (perda 10%); vigotas por laje com kg/m do catálogo × 1,10.
- **Checklists** (inicial de projeto, pré-pilares, inicial de prédio, finalização): listas de conferência de dados de entrada, compatibilização e entregáveis. [Conteúdo nas planilhas; não são cálculo.]

## 7b. Série da pós (TRILHA 1/Módulo 1 — planilhas 01–10 e P01–P04)

Série acadêmica (estilo Carini) em kN/cm; confirma e refina o que o dlima-estrutural já implementa via MUSSO:

- **01_Lajes_Maciças**: casos 1–10 de vinculação com **repartição de rigidez kx = λ⁴/(1+λ⁴)** (λ = ly/lx, variantes por caso: 5λ⁴/(2+5λ⁴) etc.) → coeficientes wc, mx, my, mxe, mye, rx, ry, rxe, rye derivados dos casos unidirecionais (8; 14,22; 24; 384/5...); flecha W0 = wc·q·lx⁴/D·1000 com **D = Ecs·h³/12(1−ν²)**, ν=0,2; W∞ = W0·(1+φ), φ=2,5; Wadm = mín(lx,ly)/250 (balanço: lx/125); majoração de carga em balanço 1,4·máx(1,95−0,05·h·100; 1); reações pelas áreas de influência (45°/60°).
- **05_Corte_Retangulares**: modelos I e II idênticos ao estudo Musso (VRd2 = 0,27·αv2·fcd·b·d no I; 0,54·αv2·fcd·b·d·sen²θ·(cotα+cotθ) no II; **Vc1 interpolado = Vc0·(1 − (Vsd−Vc0)/(VRd2−Vc0))**), Asw mín = 0,2·fctm·b/fywk; tabela Asw/s por φ×s.
- **07_Vigas_ELS**: Branson com **Mr = 0,25·fctm·b·h²** (rigidez; α=1,5 p/ retangular → 0,25 = 1,5/6) e **Mr com fctk,inf** na fissuração; x2 por equação quadrática homogeneizada (A = b/2; B = ΣαAs; C = −Σα·As·d); I2; σs = αe·Ma·(d−x)/I2; Acr; **wk = mín(w1;w2)** idêntico ao Musso; h_eq = (12·Ieq/b)^⅓.
- **10_Flexo-Compressão (xlsm)**: pilar retangular — equilíbrio por domínios (1 a 5) com x iterado (Solver/macro), tensões por barra (ε1..ε4 conforme camadas ny=2/3/4), **αc·ηc com ηc = (4/fck)^⅓ p/ fck>40**; As,mín = máx(0,4%·Ac; 0,15·Nd/fyd); flexo-oblíqua com Mrdxx/Mrdyy e **envoltória (ex/exd)^1,2 + (ey/eyd)^1,2 ≤ 1**; caso "dispensa armar" verificado.
- **P01–P04**: aplicação em projeto (todas as lajes de um pavimento, cargas de vigas por quinhões, momentos em pilares por rigidez, projeto de pilar completo). P01 tem 144k chars de fórmulas (uma linha por laje) — consultar dump sob demanda.
- **02_Lajes_Armaduras/03_Flexão_T/04_Flexão_Retangulares/06/08/09**: tabelas de detalhamento e casos já cobertos pelo estudo Musso (seção T com bf colaborante, KMD/KX, cargas por área de influência).

## 8. Divergências e cuidados p/ implementação no dlima-estrutural

1. Planilhas Waltner usam **tf** (toneladas-força) — converter p/ kN (×9,81 ou ×10 conforme adotado) ao portar; núcleo dlima já é kN.
2. Flecha da escada reta/plissada usa fator de fluência fixo ×3,5 sobre a elástica bruta (sem Branson); a espinha de peixe usa Branson completo + αf — preferir o segundo (e o padrão Musso já implementado).
3. VRd2 "0,27·σcd·b·d" = 0,45·0,6(1−fck/250)... com αv2 (1−fck/250) DENTRO do 0,27 apenas em algumas células — conferir caso a caso; adotar forma NBR explícita 0,54·(1−fck/250)·... como no estudo Musso (docs/musso-vigas-concreto-armado.md §6).
4. τRd de laje 0,0375·fck^(2/3) e k = 1,6−d: é o **modelo NBR 6118 item 19.4.1** (lajes sem estribo) — mesmo do VRd1; usar p/ escadas-laje e nervuras.
5. Método de fissuração dos reservatórios (§3.2) inclui **retração/temperatura** e tensão de fissuração σsr — mais completo que o wk padrão de vigas; é a referência p/ o módulo reservatório (junto com Carini).
6. Fórmulas de vinculação (α, β, γ, δ) das planilhas Waltner são as clássicas de tabela — já cobertas com mais precisão pelo motor de diagramas do estudo Musso (61 pontos); usar tabelas só p/ pré-dimensionamento.
