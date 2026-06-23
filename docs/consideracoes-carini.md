# Considerações das aulas do Prof. Carini (MSc, UFSC)

Observações extraídas da planilha de aula do professor. Servem de base para o
módulo "Memorial de Cálculo" e para o dimensionamento de cada elemento.

## 1. Materiais (C25, São Mateus/ES)

| Grandeza | Valor |
|---|---|
| fck | 25 MPa (2,5 kN/cm²) |
| fct,m | 2,565 MPa |
| fctk,inf | 1,795 MPa |
| fctk,sup | 3,334 MPa |
| fcd | 25/1,4 = 17,9 MPa |
| αE (basalto, São Mateus) | 1,2 |
| Eci | 33.600 MPa |
| αi | 0,863 |
| Ecs | 28.980 MPa |

- αE por agregado: basalto/diabásio = 1,2 ; granito/gnaisse = 1,0 ; calcário = 0,9 ; arenito = 0,7.
- Para São Mateus usar αE = 1,2 (basalto).
- Eci = módulo tangente na origem. Ecs = módulo secante (~40% da resistência).

## 2. Diagrama tensão-deformação e bloco retangular

- αc = 0,85 (efeito Rüsch) ; ηc = 1,0 (fator de fragilidade, novo na norma) ; λ = 0,80.
- n = 2,0 ; εc2 = 2,00 por mil ; εcu = 3,50 por mil (alterados para concretos acima de 50 MPa).
- Regra do bloco de compressão na altura λx:
  - se λx **dentro** da seção (LN): tensão = αc·ηc·fcd
  - se λx **ultrapassa** a seção: tensão = 0,9·αc·ηc·fcd

## 3. Lajes

### Classificação
- Vão maior / vão menor ≤ 2 → laje armada em **duas direções**.
- Vão maior / vão menor > 2 → laje armada em **uma direção**.

### Interpolação dos coeficientes (IMPORTANTE)
Carini interpola os coeficientes de momento/reação para λ = ly/lx diferente de 1,0.
Exemplo real da planilha (λ = 0,532, interpolando entre 0,50 e 0,55):

```
mxe = ((-36,0-(-36,2))/(0,55-0,50))*(0,532-0,5)+(-36,2) = -36,072
mye = ((-60,3-(-62,1))/(0,55-0,50))*(0,532-0,5)+(-62,1) = -60,948
mx  = ((10,3-9,4)/(0,55-0,50))*(0,532-0,5)+9,4        = 9,976
my  = ((24,6+26,0)/(0,55-0,50))*(0,532-0,5)+26        = 25,104
```

LIMITACAO atual do programa: a tabela COEF_CARINI usa só λ = 1,0. Para lajes
retangulares o valor real difere; implementar tabela completa + interpolação linear.

### Vão efetivo
lef = l0 + a1 + a2, com a1 = a2 = metade da largura da viga de apoio.
Exemplo: a1 = a2 = 7 cm, l0 = 311,5 → lx = 325,5 ; l0 = 361 → ly = 375.

### Vinculação
- Laje com rebaixo: tratar como **apoiada** (por conta dos níveis).
- Laje em balanço: a borda interna é **apoiada** e o balanço é **engastado**.

### Peso de parede sobre a laje (bidirecional)
Distribuir o peso da parede em toda a área da laje:
```
q = (γ_alv * (h_parede - h_laje) * comprimento_parede) / area_laje
ex.: (1,9 * (3,15-0,12) * 2,21) / 3,707 / ... = 1,46 kN/m²
```

## 4. Cargas (exemplo residencial)

Permanentes:
| Item | Cálculo | kN/m² |
|---|---|---|
| PP laje | 0,12 · 25 | 3,00 |
| Revestimento de piso | — | 1,00 |
| Forro de gesso em placas | — | 0,15 |
| **gk total** | | **4,15** |

Variável: dormitório qk = 1,5 kN/m².
Cobertura com acesso só para manutenção: qk = 1,0 kN/m².

## 5. Reservatórios

Ordem didática do professor:
1. Reservatório **elevado** (mais simples, NÃO tem empuxo de solo).
2. Muro de arrimo.

### Reservatório elevado — cargas na laje de fundo
| Item | Cálculo | kN/m² |
|---|---|---|
| PP | 0,15 · 25 | 3,75 |
| Revestimento | — | 1,00 |
| Água | 10 · 2,4 (γ_água · h_água) | 24,00 |
| **Total** | | **28,75** |

### Pressão da água nas paredes
Empuxo da água na base = γ_água · h = 10 · 2,4 = 24 kN/m².
Momento na parede pela carga triangular equivalente:
```
(P*L²)/1000, com P = carga na base
ex.: (24 * 2,525²)/1000 = 0,153 kN*m/m
(adota carga retangular e divide por 2 para equivaler ao triângulo)
```

### Coeficientes de ponderação no reservatório
- **Md (momento fletor): γf = 1,4** — vem do peso próprio da laje, sobrecarga e impermeabilização.
- **Nd (normal de tração): poderia usar γf = 1,2** — é o empuxo da água (força da água na parede).
Exemplo: Md = 1,4·3,82 = 5,35 kN·m/m = 535 kN·cm/m ; Nd = 1,4·9,77 = 13,68 kN/m.

### Flexo-tração nas paredes (armadura mínima)
A norma só define armadura mínima para flexão e tração simples, NÃO para flexo-tração.
Sugestão do professor:
- Se x > 0 (flexo-tração com **grande** excentricidade): usar armadura mínima de **flexão simples**.
- Se **pequena** excentricidade: a favor da segurança, usar armadura de **tração simples**.

Excentricidades (exemplo):
```
e0 = Md/Nd = 535/13,68 = 39,11 cm
d' = h - d = 10 - 7 = 3 cm ; (d-d')/2 = 2 cm
e1 = e0 - (d-d')/2 = 39,11 - 2 = 37,11 cm
Nd*e1 = 13,68*37,11 = 508 kN*cm/m < Md,lim = 2196 kN*cm/m → Armadura SIMPLES
(empregar sistema de equações do Slide 28)
```
## 6. Parede de reservatorio - tabela de Carini (painel com carga triangular)

Fonte: Carini, "Reservatorios Elevados", slides 13-15.

Modelo de calculo do reservatorio:
- TAMPA: laje com carga uniformemente distribuida (4 bordas apoiadas).
- FUNDO: laje com carga uniforme + momentos nas bordas (4 bordas engastadas).
- PAREDES: painel com carga TRIANGULAR, bordas laterais e base ENGASTADAS, topo APOIADO.

Momentos (caracteristicos):
```
Mx = (mx/1000)*p*l^2     Mxe = (mxe/1000)*p*l^2
My = (my/1000)*p*l^2     Mye = (mye/1000)*p*l^2
p = pressao no pico (base) = gamma*H ; l = menor dimensao
Md = 1,4 * M  (ELU flexao)   |   tracao do anel: Nd = 1,2 * p_agua * L/2
```
- Tabela SUPERIOR -> l = lx (usar quando lx <= ly), indexada por lx/ly.
- Tabela INFERIOR -> l = ly (usar quando ly <= lx), indexada por ly/lx.
- ly = altura da parede (= altura da agua) ; lx = comprimento da parede.
- Interpolar linearmente entre as razoes.

Tabela SUPERIOR (l = lx), colunas: lx/ly | mxe | mye | mx | my
```
1,00  -28,3  -34,5  12,2  10,6
0,95  -30,1  -35,5  13,3  10,6
0,90  -31,9  -36,5  14,3  10,5
0,85  -33,6  -37,6  15,3  10,4
0,80  -35,2  -38,7  16,2  10,1
0,75  -36,6  -39,9  17,2   9,5
0,70  -37,8  -41,0  18,0   8,7
0,65  -38,9  -42,1  18,8   8,0
0,60  -39,8  -43,1  19,5   7,2
0,55  -40,6  -44,1  20,1   6,4
0,50  -41,3  -45,1  20,6   5,8
```
Tabela INFERIOR (l = ly), colunas: ly/lx | mxe | mye | mx | my
```
0,50  -36,2  -62,1   9,4  26,0
0,55  -36,0  -60,3  10,3  24,6
0,60  -35,6  -57,8  11,1  23,1
0,65  -35,2  -54,8  11,9  21,4
0,70  -34,6  -51,6  12,5  19,7
0,75  -33,8  -48,2  12,8  18,0
0,80  -32,9  -45,0  13,0  16,3
0,85  -31,9  -42,2  13,0  14,8
0,90  -30,7  -39,5  12,9  13,3
0,95  -29,5  -37,0  12,6  11,9
1,00  -28,3  -34,5  12,2  10,6
```
Validacao: ly/lx = 0,532 -> mxe=-36,07 mye=-60,95 mx=9,98 my=25,10 (bate com a planilha do Leonan).

Implementado em relatorio/passo_a_passo.py (TAB_RESERV_SUP / TAB_RESERV_INF / memorial_reservatorio).
Para reservatorio ENTERRADO: mesma tabela, trocando a pressao p -> agua (gamma*H) na face interna
ou solo (Ka*gamma_s*H) na face externa, conforme a combinacao cheio/vazio.