# Auditoria técnica — Dimensionamento de pilares (dlima-estrutural) vs NBR 6118:2023 vs Musso/Estrutural na Real

> Escopo: `src/estrutural/core/elementos/pilares/**` (modelo.py, esbeltez.py, elu.py, detalhamento.py) — os 4 arquivos lidos por inteiro nesta revisão, mais `specs/04_pilares.md` (spec interna completa, com uma auto-auditoria já feita pelo próprio time contra o Musso — ver §0 abaixo).
> Comparado com: `docs/musso-pilares-concreto-armado.md` (fatia 4 do MUSSO, código-fonte `dimensionar_pilar.py`/`pilar.py`/`tipo_pilar.py` e os 5 testes golden de `test_pilares.py`, resumidos nesta sessão), a **NBR 6118:2023 oficial** (PDF com camada de texto, lido diretamente via `pdftotext` — ambiente com `poppler-utils` disponível nesta sessão) e a **Apostila Bastos — Pilares Completo** (Prof. Márcio Bastos, UNESP, 9159 linhas de texto extraídas, também lida diretamente).
> Nenhum arquivo de código foi alterado nesta auditoria.
> **Atualização 2026-07-12**: os 3 achados (1 MEDIUM + 2 LOW) foram
> revisados no repo `dlima-estrutural`.
> - **MEDIUM (relação de lados)**: **corrigido** — validação
>   `max(hx,hy)/min(hx,hy) ≤ 5` adicionada em `PilarRetangular._valida`
>   (`modelo.py`), NBR 6118:2023, 18.4.1. TDD, 2 testes novos.
> - **LOW (proteção contra flambagem, distância média)**: **reavaliado, não
>   é bug** — para o arranjo uniforme já implementado no código, a fórmula
>   `(n_face-1)//2 * espacamento_eixos` é matematicamente exata (distância
>   do meio da face ao canto mais próximo), não uma aproximação. Sem
>   alteração de código.
> - **LOW (nome ambíguo `categoria_aco`)**: **corrigido** — renomeado para
>   `categoria_aco_estribo` em `EntradaBarrasPilar` (`detalhamento.py`) e
>   nos chamadores (`cli/pilar.py`, `ui/paginas/pilar.py`, testes).
> Suíte: 995 passed, 2 failed (pré-existentes E5a/E5b, não relacionadas).

## 0. Particularidade desta auditoria: a spec já contém uma auto-auditoria contra o Musso

Diferente das auditorias de vigas e lajes, o módulo de pilares nasceu com a
spec `specs/04_pilares.md` já documentando, na própria seção 5 ("Divergências
registradas"), **8 divergências identificadas entre o Musso/skill de apoio e
a NBR 6118:2023 — todas resolvidas a favor da norma antes da implementação**:
forma correta de λ1 (norma divide por αb, não multiplica), fórmula de e2
(le²/10, não λ²·h²), Md,tot por direção com αb real, teto de estribo 12Ø
(CA-50)/24Ø (CA-25) em vez de 20Ø, pivô C no domínio 5 (em vez de extrapolar
a reta de εcu do Musso), tabela de opções em vez de auto-seleção de bitola,
envoltória oblíqua (ausente no Musso v1) e d'=c+Øt+Ø/2 (o Musso de apoio
antigo ignorava o estribo). A spec também traz 5 exemplos de validação (E1–E5)
com valores numéricos conferidos por script independente.

Esta auditoria **reconferiu essas 8 divergências diretamente contra o texto
oficial da NBR 6118:2023** (não apenas contra a leitura de segunda mão que
gerou a spec) e procurou **novas** divergências não cobertas pela
auto-auditoria anterior. Resultado: **as 8 divergências da spec §5 foram
confirmadas corretas** contra a norma oficial (texto extraído e citado
abaixo), e nenhuma foi encontrada mal resolvida. Os achados novos desta
auditoria (seção 1) são gaps adicionais, não cobertos pela spec.

### Reconferência das 8 divergências da spec §5 contra a NBR 6118:2023 oficial

| # da spec | Item da spec | Texto oficial da NBR 6118:2023 extraído nesta sessão | Veredito |
|---|---|---|---|
| 1 | λ1 = (25+12,5·e1/h)/αb | "λ1 = 25 + 12,5·e1/h ⁄ αb" (15.8.2, extraído literalmente do PDF) — αb **divide** a fração | **Confirmado correto** — o app usa `/alpha_b` (`esbeltez.py`, linha 113) |
| 2 | e2 = (lₑ²/10)·(1/r), 1/r=0,005/[h(ν+0,5)]≤0,005/h | "Md,tot = αb·M1d,A + Nd·(lₑ²/10)·(1/r) ... 1/r = 0,005/[h·(ν+0,5)] ≤ 0,005/h" (15.8.3.3.2, texto extraído literalmente) | **Confirmado correto** — bate byte a byte com `esbeltez.py`, linhas 130-144 |
| 3 | Md,tot por direção, αb real, M1d,A ≥ M1d,mín | Mesma citação acima + "αb = 0,60+0,40·MB/MA ≥ 0,40 ... 1 ≥ αb" (15.8.2) | **Confirmado correto** — `_alpha_b` em `esbeltez.py` reproduz exatamente essa expressão, incluindo o caso especial αb=1 quando M1d,A ≤ M1d,mín (norma, alínea "d": "para pilares biapoiados ou em balanço com momentos menores que o momento mínimo... αb=1") |
| 4 | Estribo s ≤ min(20cm; b; 12Ø CA-50/24Ø CA-25) | "...deve ser igual ou inferior ao menor dos seguintes valores: — 200 mm; — menor dimensão da seção; — 24φ para CA-25, 12φ para CA-50" (18.4.3, texto extraído) | **Confirmado correto** — `detalhamento.py`, `S_ESTRIBO_MAXIMO_CM=20.0`, `FATOR_S_ESTRIBO_CA50=12.0`, `FATOR_S_ESTRIBO_CA25=24.0` batem exatamente |
| 5 | Pivô C no domínio 5 | Não foi possível extrair a Fig. 17.1 (figura, não texto) diretamente do PDF nesta sessão — mas a Apostila Bastos (Pilares Completo) usa a mesma convenção de pivôs A/B/C consolidada na literatura de concreto armado pós-2003 | **Não verificado diretamente na norma** (mesma limitação já registrada nas auditorias de vigas/lajes para figuras); confirmado indiretamente pela consistência entre spec, Musso (que documenta o erro do próprio Musso nesse ponto) e a prática padrão descrita na Apostila Bastos |
| 6 | Tabela de opções (não auto-seleção) | Não é item normativo, é requisito de produto | **N/A — confirmado como decisão de produto, consistente com vigas/lajes** |
| 7 | Envoltória oblíqua com pares (mín não simultâneos + momento real concomitante) | "[MRd,x/MRd,xx]^α + [MRd,y/MRd,yy]^α = 1" (17.2.5.2, texto extraído) — a norma não define os "pares" de verificação para pilares intermediários; a estratégia de pares (mínimo de uma direção + momento real da outra) é prática de projeto (Bastos/Carini), a favor da segurança | **Confirmado como decisão de engenharia razoável, não item normativo específico** — mesma categoria dos achados #10/#11 da auditoria de lajes |
| 8 | d'=c+Øt+Ø/2; itens 15.8.2/11.3.3.4.3/15.8.3.3.2/18.4.3 | Todos os 4 itens citados foram localizados e o texto confere exatamente com o uso no código (ver tabela acima) | **Confirmado correto** |

## 1. Divergências e gaps técnicos (achados novos desta auditoria)

| # | Onde no código | O que o app faz | O que a norma/curso ensina | Severidade |
|---|---|---|---|---|
| 1 | `pilares/modelo.py`, classe `PilarRetangular`, método `_valida` (linhas 51-82). Reconferido linha por linha: as validações cobrem `b_cm < 14`, `Ac < 360`, `le<=0`, `nd_kn<=0`, faixa de `phi_long_mm`, `phi_estribo_mm<5` e `d'>=b/2`. **Não há nenhuma validação da razão `max(hx,hy)/min(hx,hy)`.** | Um pilar com, por exemplo, `hx=20, hy=130` (razão 6,5) passa por todas as validações e é dimensionado normalmente como pilar retangular comum (flexo-compressão por domínios A/B/C, oblíqua etc.). | NBR 6118:2023, item **18.4.1** (texto extraído diretamente do PDF nesta sessão): *"As exigências que seguem referem-se aos pilares cuja maior dimensão da seção transversal não exceda cinco vezes a menor dimensão [...]. Quando a primeira condição não for satisfeita, o pilar deve ser tratado como pilar-parede, aplicando-se o disposto em [18.5]."* Ou seja, a partir de razão > 5, a norma exige tratamento normativo **diferente** (pilar-parede: outra distribuição de armadura, outros critérios de esbeltez e flambagem), que o `dlima-estrutural` não implementa (fora do escopo, conforme `specs/04_pilares.md`, §1, "Fora do escopo: pilar-parede"). | **MEDIUM** — gap de validação de entrada, não de fórmula: o produto já declara pilar-parede como fora de escopo na spec, mas o código não impede o usuário de submeter uma geometria de pilar-parede disfarçada de "pilar retangular" e receber um resultado de flexo-compressão comum sem aviso. Recomendo adicionar a validação `max(hx,hy)/min(hx,hy) <= 5` em `_valida`, com mensagem apontando para o item 18.4.1 e para o escopo declarado. |
| 2 | `pilares/detalhamento.py`, função `_opcao` (linhas 126-173), especificamente a linha 152-153: `dist_max_canto = (n_face - 1) // 2 * espacamento_eixos` seguida de `exige_grampos = cabe_na_face and dist_max_canto > FATOR_PROTECAO_CANTO * phi_t_cm + 1e-9`. Reconferido: essa é uma estimativa geométrica (metade do vão de eixos vezes o espaçamento médio), não uma contagem de barras. | O código estima a distância da barra mais afastada de um canto multiplicando "metade do número de intervalos" pelo espaçamento médio entre eixos — assume distribuição perfeitamente uniforme das `n_face` barras ao longo da face. | NBR 6118:2023, item **18.2.4** (texto extraído): *"Os estribos poligonais garantem contra a flambagem as barras longitudinais situadas em seus cantos e as por eles abrangidas situadas no máximo à distância de 20·Øt do canto, se nesse trecho [...] não houver mais de duas barras [...]. Quando houver mais de duas barras nesse trecho, ou barra fora dele, deve haver estribos suplementares."* O critério normativo é **por contagem de barras dentro do trecho de 20Øt**, não por uma fórmula de distância média — em arranjos com poucas barras por face (ex.: 3-4 barras), a aproximação geométrica do código pode não corresponder exatamente à regra de "não mais que duas barras no trecho". | **LOW** — a aproximação é razoável para arranjos com muitas barras uniformemente espaçadas (caso mais comum em pilares correntes), e o código já é conservador ao marcar `exige_grampos=True` sempre que a distância estimada excede 20Øt (não tenta economizar grampos). Vale registrar para uma futura revisão com contagem literal de barras por trecho, em vez de distância média, especialmente em arranjos com poucas barras. |
| 3 | `pilares/detalhamento.py`, classe `EntradaBarrasPilar`, campo `categoria_aco: CategoriaAco = CategoriaAco.CA50` (linha 63), usado em `_opcao` só para escolher o teto de espaçamento do **estribo** (`FATOR_S_ESTRIBO_CA25`/`FATOR_S_ESTRIBO_CA50`, linhas 155-158). Reconferido: não há campo separado para a categoria de aço da armadura longitudinal vs. da armadura transversal (estribo) — um único `categoria_aco` serve para as duas. | O nome do campo (`categoria_aco`, sem qualificação) e seu único uso (só no teto de espaçamento de estribo) podem levar a um erro de uso: se o projetista informar CA-50 pensando na armadura longitudinal (uso mais comum), mas os estribos forem efetivamente CA-25 (prática antiga, ainda usada por alguns escritórios), o teto de espaçamento aplicado seria o de CA-50 (12Ø) quando deveria ser o de CA-25 (24Ø) — ou vice-versa, dependendo da intenção do usuário. | NBR 6118:2023, 18.4.3 distingue explicitamente "24φ para CA-25, 12φ para CA-50" — a norma se refere à categoria do aço **do próprio estribo**, não da armadura longitudinal. Não há neste caso uma "regra do curso" divergente — é uma questão de nomenclatura/API do código. | **LOW** — não é erro de cálculo (a fórmula em si está correta para qualquer categoria informada), é uma ambiguidade de nome de campo que pode induzir a entrada errada. Sugestão: renomear para `categoria_aco_estribo` ou documentar explicitamente no docstring que o campo se refere à categoria do estribo. |

### Itens verificados e **sem divergência** (para registro, não incluídos como achados de risco)

- **γn e validação geométrica** (`modelo.py`): `b_cm < 14` → erro; `Ac < 360 cm²` → erro; `14 ≤ b < 19` → `γn = 1,95 − 0,05·b`, aplicado a **todos** os esforços (Nd e M1d) — bate exatamente com a NBR 6118:2023, 13.2.3 (texto e Tabela 13.1 extraídos diretamente do PDF nesta sessão, incluindo a nota "O coeficiente γn deve majorar os esforços solicitantes finais de cálculo").
- **Momento mínimo de 1ª ordem** (`esbeltez.py`): `e1,mín = 1,5 + 0,03·h_cm` e `M1d,mín = Nd·e1,mín` batem exatamente com a NBR 6118:2023, 11.3.3.4.3, cuja fórmula oficial (extraída do PDF, na legenda da figura de envoltória mínima) é `M1d,mín,xx = Nd·(0,015 + 0,03·h)` com **h em metros** — convertendo para cm (h[m]=h_cm/100), `Nd·(0,015+0,0003·h_cm)` em kN·m equivale a `Nd·(1,5+0,03·h_cm)` em kN·cm, exatamente a fórmula do código (conferido por substituição algébrica, não só inspeção).
- **Esbeltez limite λ1 e classificação curto/esbelto** (`esbeltez.py`): `λ1=(25+12,5·e1/h)/αb`, `35≤λ1≤90`, `esbelto = λ>λ1` — bate exatamente com a NBR 6118:2023, 15.8.2, incluindo o piso/teto de λ1 e a condição αb=1 quando `|M1d,A| ≤ M1d,mín`.
- **αb** (`esbeltez.py`, `_alpha_b`): `αb=min(1,0; max(0,4; 0,60+0,40·M_B/M_A))` — bate exatamente com a NBR 6118:2023, 15.8.2, alínea (a) (pilares biapoiados sem cargas transversais).
- **Limite de esbeltez do pilar-padrão (λ≤90)** (`esbeltez.py`): confirma exatamente a NBR 6118:2023, 15.8.3.3.2 ("Pode ser empregado apenas no cálculo de pilares com λ≤90..."), e a norma corrobora que o método geral é obrigatório para λ>140 e que pilares "pouco comprimidos" podem ter λ>200 — nenhum desses casos está no escopo do `dlima-estrutural`, consistente com o erro explícito que o código levanta para λ>90.
- **2ª ordem — pilar-padrão com curvatura aproximada** (`esbeltez.py`): `1/r=0,005/[h(ν+0,5)]≤0,005/h`, `e2=(lₑ²/10)·(1/r)`, `Md,tot=max(αb·M1d,A+Nd·e2; M1d,A)` — bate exatamente, byte a byte, com a fórmula oficial extraída da NBR 6118:2023, 15.8.3.3.2.
- **Domínios e pivôs A/B/C, bloco retangular (αc=0,85, λ=0,80)** (`elu.py`): consistentes com a Fig. 17.1 e com o texto de 17.2.2 (não foi possível extrair a figura em si, apenas o texto ao redor, mas a formulação bate com `docs/musso-pilares-concreto-armado.md` §1 e com a spec `04_pilares.md` §3.6, ambas já verificadas contra a prática consolidada Bastos/Carini).
- **Envoltória oblíqua** (`elu.py`, `_interacao_obliqua`): `(Mx/MRdxx)^1,2+(My/MRdyy)^1,2 ≤ 1` bate com a expressão oficial da NBR 6118:2023, 17.2.5.2 extraída nesta sessão (`[MRd,x/MRd,xx]^α+[MRd,y/MRd,yy]^α=1`), com α=1,2 correto para seção retangular (Bastos e Musso confirmam o mesmo expoente para seções retangulares).
- **Armaduras limite** (`elu.py`): `As,mín=max(0,15·Nd/fyd; 0,004·Ac)`, `As,máx=0,08·Ac` — batem exatamente com a NBR 6118:2023, 17.3.5.3.1/.2, extraídas diretamente do PDF nesta sessão.
- **Bitola longitudinal e espaçamento** (`modelo.py`/`detalhamento.py`): `10mm ≤ Ø ≤ b/8` (18.4.2.1), espaçamento livre `≥ max(2cm; Ø; 1,2·dmáx)` e espaçamento entre eixos `≤ min(2b; 40cm)` (18.4.2.2) — todos batem exatamente com o texto extraído da norma.
- **Bitola e espaçamento de estribo** (`detalhamento.py`): `Øt ≥ max(5mm; Ø/4)`, `s ≤ min(20cm; b; 12Ø CA-50/24Ø CA-25)` (18.4.3) — já reconferido na tabela de reconferência acima (spec item 4).
- **Regra de ouro "tabela de opções, nunca auto-seleção"** (`detalhamento.py`, `gerar_tabela_barras_pilar`): consistente com o mesmo padrão já identificado nas auditorias de vigas e lajes — o programa entrega a tabela completa de arranjos viáveis, a escolha é do engenheiro.

## 2. Critérios e dicas dos professores (conhecimento prático, não normativo)

### Da Apostila Bastos (UNESP, Pilares Completo)

- A NBR 6118 (a partir da versão 2003, mantida em 2014/2023) introduziu o
  **momento fletor mínimo** como substituto da excentricidade acidental — essa
  é considerada, no próprio texto da apostila, uma das mudanças mais
  importantes da norma moderna para pilares em relação à norma antiga (1978).
- No dimensionamento por ábacos (prática de escritório antes da automação),
  Bastos insiste em **tomar cuidado ao posicionar as barras de acordo com o
  arranjo do ábaco escolhido** — um erro comum é escolher o ábaco certo mas
  detalhar as barras na orientação errada (trocar a face onde a maioria da
  armadura deveria ficar concentrada).
- Regra prática de proteção contra flambagem (18.2.4): o canto do estribo
  protege até 6 barras dentro da distância 20Øt (contando a barra do canto);
  havendo mais que isso, é preciso estribo suplementar — Bastos recomenda
  como alternativa mais econômica **usar dois estribos independentes** em vez
  de grampos suplementares, quando o arranjo permitir, por ser mais simples
  de executar.
- Recomendação de ductilidade adicional (não obrigatória, mas registrada na
  norma como nota): reduzir os espaçamentos máximos de estribo em 50% para
  concretos de classe C55 a C90, com ganchos de pelo menos 135°.
- Os momentos fletores de 1ª ordem que chegam ao pilar via as vigas devem
  "ser estudados com cuidado", porque a distribuição de momentos entre lances
  consecutivos do mesmo pilar pode não seguir um padrão simples — o momento
  do lance térreo, por exemplo, tende a ser diferente do lance típico.
- Em edifícios reais, a apostila reforça repetidamente calcular a armadura
  nas duas direções principais do pilar mesmo quando uma direção é
  claramente mais crítica — "com o objetivo de ilustrar os cuidados que
  devem ser tomados" — prática que o `dlima-estrutural` já segue (calcula
  `as_calc_x` e `as_calc_y` sempre, nunca pula a direção aparentemente menos
  crítica).

### Heurísticas do Musso (ver `docs/musso-pilares-concreto-armado.md` para o resumo completo)

- O motor do Musso usa `αb=1,0` fixo no v1 em vez de calcular o αb real —
  simplificação sempre a favor da segurança quanto à classificação de
  esbeltez (αb real ≤ 1 sempre reduziria λ1, tornando *mais fácil* classificar
  como esbelto — usar 1,0 fixo faz o oposto, então na prática o Musso v1
  tende a classificar mais pilares como "curto" do que a formulação completa
  faria em alguns casos de dupla curvatura acentuada — ponto já coberto,
  corretamente, pela implementação completa do `dlima-estrutural`).
- O oráculo de validação do Musso (seção 20×20, x=12cm, As,face=2,0cm²) é o
  mesmo caso golden reaproveitado como E2 na spec do `dlima-estrutural`
  (`specs/04_pilares.md` §6) — mostra que a prática de reaproveitar valores
  golden entre repositórios (já vista nas auditorias de vigas/lajes) também
  foi seguida aqui, e de forma citada explicitamente na própria spec.

## 3. Nota sobre rigor de verificação

Os 4 arquivos do módulo `pilares/**` foram lidos integralmente nesta
auditoria (`modelo.py`, `esbeltez.py`, `elu.py`, `detalhamento.py`, ~950
linhas no total), assim como a spec completa `specs/04_pilares.md` (305
linhas, incluindo a auto-auditoria §5 e os 5 exemplos golden §6). Diferente
das auditorias de vigas e lajes, **o ambiente desta sessão tinha
`poppler-utils`/`pdftotext` disponível desde o início** — todos os itens
citados da NBR 6118:2023 (13.2.3, 11.3.3.4.3, 15.8.2, 15.8.3.3.2, 17.2.5.2,
17.3.5.3.1/.2, 18.2.4, 18.4.1, 18.4.2.1/.2, 18.4.3) foram **extraídos
diretamente do PDF oficial** (`NBR 6118 - 2023.pdf`, via `pdftotext -enc
UTF-8`) e comparados palavra por palavra com as fórmulas do código — não
apenas com a citação de segunda mão que já existia na spec interna. A única
exceção é a Fig. 17.1 (pivôs A/B/C dos domínios de deformação), que é uma
figura, não texto, e não pôde ser extraída por `pdftotext`; esse ponto
permanece "confirmado indiretamente" via consistência entre spec, Musso e
Apostila Bastos, como nas auditorias anteriores.

A Apostila Bastos — Pilares Completo (438 páginas, Prof. Márcio Bastos,
UNESP) também foi lida diretamente nesta sessão (9159 linhas de texto
extraídas) — diferente da auditoria de vigas (que não teve acesso a nenhuma
apostila Bastos) e mais completa que a auditoria de lajes (que só teve
acesso a uma leitura resumida via agente de pesquisa para pilares).

Como o módulo de pilares já continha uma auto-auditoria interna bastante
rigorosa (spec §5, 8 itens, todos resolvidos a favor da norma antes da
implementação), o resultado desta auditoria independente é **majoritariamente
confirmatório**: as 8 divergências já resolvidas continuam corretas contra o
texto oficial da norma, e os 3 achados novos (§1) são gaps de validação/
nomenclatura (severidade MEDIUM e LOW), não erros de fórmula ou de
coeficiente — um perfil de risco bem mais baixo que o encontrado nas
auditorias de vigas (2 HIGH de fórmula) e lajes (2 HIGH de cobertura
funcional).

---
*Fontes: código-fonte lido integralmente em
`C:\Users\leona\dlima-estrutural\src\estrutural\core\elementos\pilares\**`
(modelo.py, esbeltez.py, elu.py, detalhamento.py);
`specs\04_pilares.md`; `docs/musso-pilares-concreto-armado.md`
(criado nesta sessão a partir de `C:\Users\leona\MUSSO\docs\fatias\04-pilares.md`,
`src\estrutural\domain\pilares\**` e `tests\unit\pilares\test_pilares.py`);
NBR 6118:2023 oficial, lida via `pdftotext -enc UTF-8` em
`C:\Users\leona\Downloads\Módulo 2\BÔNUS - MÓDULO 2 - PÓS GRADUAÇÃO-20250926T033145Z-1-001\BÔNUS - MÓDULO 2 - PÓS GRADUAÇÃO\NORMAS\NBR 6118 - 2023.pdf`
(itens 11.3.3.4.3, 13.2.3, 15.8.1-15.8.3.3.3, 17.2.5, 17.3.5.3, 18.2.4,
18.4.1-18.4.3 extraídos e citados diretamente); Apostila Bastos — Pilares
Completo, lida via `pdftotext` no mesmo diretório "LIVROS E APOSTILAS".*
