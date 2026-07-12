# Auditoria técnica — Dimensionamento de escadas (dlima-estrutural) vs NBR 6118:2023 vs Waltner Wagner/Estrutural na Real

> Escopo: `src/estrutural/core/elementos/escadas/**` — os 6 arquivos lidos por
> inteiro nesta revisão (`cargas.py`, `degrau.py`, `escada_trelicada.py`,
> `geometria.py`, `laje_escada.py`, `viga_escada.py`), mais `specs/07_escadas.md`
> e `specs/07b_tipos_escada.md` (specs internas completas, com auto-auditoria
> já registrada em §5/§6 de cada uma — ver §0 abaixo, mesmo padrão da
> auditoria de pilares).
> Comparado com: as duas planilhas do curso Estrutural na Real (Eng. Waltner
> Wagner) — `ESCADA PLISSADA E RETA_ENG.WALTNERWAGNER.xlsx` (abas "ESCADA
> RETA", "ESCADA PLISSADA", "DET. ESCADA PLISSADA") e `ESCADA ESPINHA DE
> PEIXE E FLUTUANTE - ENG.WALTNERWAGNER2.xlsx` (aba "ESPINHA DE
> PEIXEFLUTUANTE") — abertas nesta sessão via `openpyxl`; e a **NBR
> 6118:2023 oficial**, lida diretamente via `pdftotext` (poppler-utils
> disponível nesta sessão). **Não existe capítulo dedicado a escadas na NBR
> 6118** (confirmado por busca textual completa no PDF — "escada" não
> aparece nenhuma vez fora do sumário de assuntos correlatos) nem apostila
> Bastos de escadas no acervo local (já confirmado em sessão anterior) — a
> norma trata escada como laje inclinada (mesmas regras de 13.2.4/19 para o
> lance reto/plissado) mais viga comum (17/18) para a viga central das
> variantes espinha de peixe/flutuante. Este é o critério usado para
> escolher quais itens da norma auditar.
> Nenhum arquivo de código foi alterado nesta auditoria.

## 0. Particularidade desta auditoria: a spec já contém uma auto-auditoria e goldens extensos

As specs `07_escadas.md` e `07b_tipos_escada.md` (juntas, ~600 linhas) já
documentam, na própria seção "Divergências e decisões de projeto" de cada
uma, **19 divergências identificadas entre as planilhas do Waltner e a
prática adotada** — praticamente todas resolvidas a favor da norma ou de uma
"estática limpa" antes da implementação (ex.: cortante pela NBR 6118:2023
19.4.1 em vez da fórmula antiga da planilha; Vd da viga central por estática
direta em vez da célula K30 da planilha, que multiplicava a largura duas
vezes e reduzia Vd em ~10%; torção por 17.5 completa em vez da aproximação
que mistura kN/m² com kN/m na célula U20). Há também 9 exemplos de validação
golden (E1–E5 da spec 07, E-T1–E-T4 da spec 07b) com valores numéricos
conferidos célula a célula contra as duas planilhas.

Esta auditoria **reconferiu diretamente as duas planilhas Waltner** (via
`openpyxl`, abrindo todas as 5 abas relevantes) e a **NBR 6118:2023 oficial**
(via `pdftotext`), buscando exclusivamente **divergências novas não
cobertas** pelas 19 já resolvidas nas specs. Resultado: não foi encontrada
nenhuma das 19 decisões já registradas mal resolvida contra a norma oficial;
os achados novos desta auditoria (seção 1) são gaps de **cobertura
funcional** (verificações ausentes) e de **validação de entrada**, no mesmo
padrão de risco da auditoria de pilares — não erros de fórmula ou de
coeficiente já testado.

## 1. Divergências e gaps técnicos (achados novos desta auditoria)

| # | Onde no código | O que o app faz | O que a norma/curso ensina | Severidade |
|---|---|---|---|---|
| 1 | `escadas/laje_escada.py`, classe `ResultadoLajeEscada` (linhas 90-103) e função `calcular_laje_escada` (linhas 119-213). Reconferido linha por linha: os blocos calculados são esforços, flexão, distribuição, cortante (VRd1) e **flecha** (`verificar_flecha_laje`, linha 192). **Não há nenhuma chamada a `verificar_fissuracao_laje`** (função já existente e validada em `lajes/els.py`, usada pela laje de piso comum) nem a qualquer outra verificação de abertura de fissuras (wk) em todo o arquivo. Confirmado: mesmo padrão de ausência em `escadas/viga_escada.py` (só `calcular_flecha`, sem `calcular_fissuracao` de `vigas/els.py`) e em `escadas/degrau.py` (nenhuma verificação ELS, nem flecha nem fissuração, para o degrau em balanço). | O pipeline de escada reta/plissada (laje por faixa), o de espinha de peixe/flutuante (viga central) e o degrau em balanço verificam **só flecha** entre as duas verificações de ELS que a NBR exige (deformação excessiva e abertura de fissuras) — quando existem, verificam apenas uma. | NBR 6118:2023 exige as duas verificações de ELS separadamente: **ELS-DEF** (deformações excessivas, 3.2.4) e **ELS-W** (abertura de fissuras, 3.2.3/17.3.3). O próprio código do repositório já tem as duas funções prontas e testadas: `lajes/els.py::verificar_fissuracao_laje` (usa a mesma referência normativa 17.3.3.2 já citada nas auditorias de lajes/vigas) e `vigas/els.py::calcular_fissuracao`. Nenhuma das duas planilhas Waltner reconferidas nesta sessão (`ESCADA RETA`, `ESCADA PLISSADA`, `ESPINHA DE PEIXEFLUTUANTE`) também verifica fissuração — busca textual por "fissur"/"wk"/"abertura" nas três abas não encontrou nenhuma célula com esse conteúdo — ou seja, o gap é herdado do material didático de origem, não é uma regressão introduzida pelo `dlima-estrutural`. | **HIGH** — mesma classe de risco do achado #3 da auditoria de lajes (assimetria de cobertura ELS entre módulos do mesmo repositório): a laje de piso comum já verifica wk (`verificar_fissuracao_laje`), mas nenhum dos 3 pipelines de escada (laje por faixa, viga central, degrau em balanço) chama a função equivalente, apesar de ela já existir, estar testada e ser trivial de encaixar (mesmos parâmetros — As adotada, d, phi, s — já calculados em cada pipeline). Escadas são elemento de uso público/circulação intensa, onde fissuração visível tem também peso de percepção de segurança pelo usuário leigo, reforçando a severidade. |
| 2 | `escadas/laje_escada.py`, `escadas/viga_escada.py`, `escadas/escada_trelicada.py` e `escadas/degrau.py` — reconferido em todos os 4: o campo `cobrimento_cm` é sempre um `float` digitado diretamente pelo usuário (`EntradaLajeEscada.cobrimento_cm`, `EntradaVigaEscada.cobrimento_cm`, `EntradaEscadaTrelicada.cobrimento_cm`, `EntradaDegrau.cobrimento_cm`), com a única validação `if self.cobrimento_cm <= 0: raise ValueError(...)` em todos os 4 `model_validator`. Nenhum dos 4 arquivos importa `ClasseAgressividade` nem `COBRIMENTOS_E_FCK_MINIMO` (`core/normas/nbr6118_2023.py`) para checar um piso mínimo — confirmado por leitura completa dos imports dos 4 arquivos. A única menção a CAA em todo o módulo é a constante `_CAA_INERTE = ClasseAgressividade.CAA_II` em `escada_trelicada.py` (linha 55), cujo próprio docstring do arquivo (linhas 9-11) documenta que ela "nunca chega a derivar cobrimento — é só o campo obrigatório do módulo reusado" (`EntradaEluTrelicada`, que aceita `cobrimento_cm` explícito e ignora a CAA quando informado). | Qualquer valor positivo de cobrimento é aceito (ex.: `cobrimento_cm = 0.5`), mesmo abaixo do mínimo nominal tabelado pela norma para a classe de agressividade real da obra. | NBR 6118:2023, Tabela 7.2 (cobrimento nominal por CAA), já implementada como `COBRIMENTOS_E_FCK_MINIMO` em `core/normas/nbr6118_2023.py` e usada nos módulos de laje/viga/pilar de piso comum (que derivam o cobrimento a partir da `ClasseAgressividade` escolhida, em vez de aceitar um valor livre). A spec 07 (§2.2/§2.3) documenta a decisão de **digitar** o cobrimento em vez de derivá-lo da CAA — decisão de produto explícita, não um esquecimento — mas nenhuma das 4 entradas de escada valida esse valor digitado contra o piso mínimo da Tabela 7.2, mesmo sabendo a CAA (o combo de CAA nem aparece nas entradas de escada). | **MEDIUM** — é uma decisão de produto já registrada (cobrimento digitado, não derivado), mas sem nenhuma trava de sanidade: nada impede o usuário de digitar um cobrimento incompatível com a agressividade real do ambiente da escada (ex.: escada externa/embarcada em CAA III/IV com cobrimento de CAA I) e obter um dimensionamento "aprovado" sem aviso algum. Recomendo, no mínimo, um aviso não bloqueante comparando o valor digitado com o mínimo da Tabela 7.2 para uma CAA opcionalmente informada — mesmo padrão de responsabilidade do usuário já usado em outros avisos do sistema (ex.: Blondel). |
| 3 | `escadas/viga_escada.py`, função `calcular_viga_escada`, bloco de torção (linhas 317-330), especificamente `tk = max(mt * entrada.vao_m / 2.0, P_PESSOA_PONTA_KN * a_balanco)`. Reconferido: a mesma fórmula `mt·L/2` é aplicada **para as 7 vinculações** da tabela (`_TABELA_VINCULACOES`, linhas 87-95) sem nenhuma diferenciação — inclusive para vinculações assimétricas (`apoio_engaste`, `apoio_eng_red`, `eng_red_engaste`). | O momento torsor distribuído reage integralmente como `mt·L/2` em qualquer apoio, para qualquer vinculação — mesmo valor de reação torsora nos dois apoios de uma viga com um lado engastado e outro apoiado. | A spec 07 (§3.6 e §5, item 6) documenta essa simplificação explicitamente como decisão de projeto ("estática limpa" — decisão 6), e a fonte primária (planilha Waltner, aba "ESPINHA DE PEIXEFLUTUANTE") também usa uma única fórmula de torque sem diferenciar vinculação (célula U20, citada na spec como já misturando unidades, ainda mais simplificada que a implementação atual). **Não há item específico da NBR 6118:2023 tratando reação de torque distribuído por tipo de vinculação de viga** — a norma (17.5) trata o dimensionamento à torção dado um `Td` já calculado, não a análise estática que produz esse `Td`; portanto este não é um item de conformidade normativa, é uma simplificação de análise estrutural. | **LOW** — para vinculações simétricas (`apoio_apoio`, `engaste_engaste`, `eng_red_eng_red`) a fórmula `mt·L/2` é exata por simetria; para as 3 vinculações assimétricas da tabela, a reação real nos dois apoios não é necessariamente igual, e usar `mt·L/2` em ambos pode subestimar o apoio mais rígido — mas como o próprio `Tk` final já é o `max(mt·L/2; P·a)` (o segundo termo, pessoa isolada na ponta do degrau, tende a governar nos casos de vão menor, mais frequentes em escadas residenciais), o efeito prático da imprecisão é limitado. Registrar para uma futura revisão de estática caso apareçam vãos maiores de espinha de peixe/flutuante com vinculação assimétrica. |
| 4 | `escadas/degrau.py`, função `calcular_degrau` (linhas 98-182). Reconferido o arquivo inteiro: o degrau em balanço tem cálculo de momento (peso próprio + pessoa na ponta), altura útil e flexão (`dimensionar_flexao_simples`) — **nenhuma verificação de ELU de cisalhamento** (VSd × VRd1) é feita para o degrau, apesar de ele ser uma peça em balanço fina (`espessura_degrau_cm`, mínimo normativo de projeto 6 cm conforme spec 07 §2.3) sujeita a uma reação de cortante concentrada próxima ao engaste na viga central. | O degrau em balanço só verifica flexão; não há cálculo nem verificação de VRd1/dispensa de estribo (o degrau nunca leva estribo na prática, mas a norma ainda exige que `VSd ≤ VRd1` sem armadura transversal, como é feito para a laje de piso e para a faixa de 1 m da escada reta/plissada no mesmo repositório). | NBR 6118:2023, 19.4.1 (mesmo item já usado em `laje_escada.py` e em `lajes/elu.py` para dispensa de armadura transversal) — a fórmula `VRd1 = 0,25·fctd·k·(1,2+40·ρ1)·b·d` se aplicaria diretamente ao degrau (peça de laje/placa, largura = piso do degrau) sem exigir nenhum módulo novo, só reaproveitar a mesma lógica já usada em `laje_escada.py`. Nem a planilha Waltner (aba "ESPINHA DE PEIXEFLUTUANTE") nem a spec 07 (§3.5) mencionam essa verificação para o degrau — é um gap herdado da fonte primária, mas ainda assim um gap real de conformidade. | **MEDIUM** — na prática, degraus em balanço são peças curtas (a = 0,45–1,0 m nos exemplos golden E3/E4) com cortante baixo comparado à capacidade de uma seção de 8 cm de espessura, então o risco de reprovação silenciosa é baixo — mas nada no código confirma isso caso a caso; fica sem verificação formal. |
| 5 | Todo o pacote `escadas/**` — reconferido: não existe, em nenhum dos 6 arquivos lidos nesta auditoria, nenhuma função que trate a continuidade entre lance e patamar intermediário, nem qualquer compatibilização de momento entre dois lances consecutivos da mesma escada (caso de escadas em L/U). | Cada lance é calculado como uma escada reta/plissada/espinha/flutuante **independente**; o patamar intermediário entra apenas como parte do vão (`vao_m`), sem nenhum tratamento de continuidade de momento entre lance e patamar ou entre dois lances. | Isto **já está documentado explicitamente como fora de escopo** na spec 07, §1: *"Escadas com lances em L/U e patamar intermediário como elemento único (v1: cada lance é calculado como uma escada reta independente; o patamar entra no vão)"*. Não é um item numerado da NBR 6118:2023 — é decisão de produto já registrada, análoga à compatibilização de momento negativo entre lajes vizinhas (achado #10 da auditoria de lajes), que lá também não é item normativo, mas prática de projeto. | **LOW** — decisão de escopo já documentada e comunicada; incluído aqui apenas para registro de rastreabilidade (mesmo tratamento dado ao item equivalente na auditoria de lajes), não como achado novo de risco oculto. |

### Itens verificados e **sem divergência** (para registro, não incluídos como achados de risco)

- **Espessura real de projeção horizontal (reta/plissada)** (`geometria.py`, `_esp_real`): `esp_real = h·(L_incl/L) + espelho/2` (reta) e `esp_real = h·(L+H)/L` (plissada) — reconferido byte a byte contra a célula F18 das abas "ESCADA RETA" e "ESCADA PLISSADA" (via `openpyxl`, fórmulas de célula lidas com `data_only=False`) e contra os goldens E1/E2 da spec 07 (valores 22,194 cm e 24,041 cm reproduzidos exatamente). O termo `L_incl/L = 1/cos(α)` corrige corretamente o peso próprio do trecho inclinado pela inclinação real — é o ajuste "1/cos α" citado nos pontos de atenção desta auditoria, confirmado presente e correto.
- **Peso próprio da viga central projetado** (`cargas.py`, `montar_cargas_viga_escada`): `pp_viga = 25·(bw/100)·(h/100)·(L_incl/L)` — mesmo fator `L_incl/L` aplicado corretamente à viga central da espinha de peixe/flutuante, reconferido contra o golden E3 da spec 07 (pp_viga = 1,7523 kN/m, reproduzido exatamente).
- **Regra de Blondel** (`geometria.py`, `BLONDEL_MIN_CM=63`, `BLONDEL_MAX_CM=65`): implementada como **aviso não bloqueante** (`Verificacao`, não `raise`), consistente com a spec 07 §4 ("Blondel (geometria) — (boa prática) — aviso se 2e+p fora de 63–65 cm") e com o uso corrente do curso (célula de conforto nas duas abas do Waltner). Correto marcar como boa prática, não item normativo — a NBR 6118 não trata proporção de degrau (é assunto de ergonomia/NBR 9077, fora do escopo estrutural desta auditoria).
- **Sugestão de geometria a partir só da altura** (`sugerir_geometria_escada`): heurística de produto (faixa 17–19 cm de espelho, 27–29 cm de piso) documentada como decisão do projetista (F22-12), não item normativo — sem divergência a avaliar.
- **Cortante da faixa de 1 m (reta/plissada)** (`laje_escada.py`): `VRd1 = 0,25·fctd·k·(1,2+40·ρ1)·b·d` com `k = max(1,6−d/100; 1,0)` — mesma fórmula da NBR 6118:2023, 19.4.1, já usada e validada em `lajes/elu.py` (auditoria de lajes); reconferido que a escada reta/plissada reaproveita a constante `TAU_RD_COEF`/`RHO_1_MAXIMO` do módulo de lajes em vez de duplicar a fórmula — reuso correto de código já testado, evitando divergência entre módulos.
- **Momento e cortante da faixa por m²** (`laje_escada.py`, `_laje_sintetica`): a manobra de sintetizar uma `LajeMacica` unidirecional (`ly_m = 3·lx_m`, tipo biapoiado) para reaproveitar `calcular_esforcos_laje` já validado é a mesma estratégia (decisão 1 da spec 07: "faixa de 1 m") comprovadamente correta na flexão (a largura cancela no cálculo de momento por metro), reconferida nesta sessão contra o golden E1 (Md = 1.571,2 kN·cm/m, reproduzido).
- **Torção da viga central (17.5 completo)** (`viga_escada.py`, via `vigas/torcao.py`): a integração passa corretamente `secao`, `d_cm`, `td_kncm`, `vd_kn`, `cobrimento_cm`, `phi_estribo_mm` e `phi_longitudinal_mm` (usando `phi_positivo_mm` como longitudinal de referência) para `dimensionar_torcao` — os mesmos parâmetros já auditados e corrigidos anteriormente no módulo `torcao.py` (não reauditado aqui, conforme escopo definido); a integração em si está correta (nenhum parâmetro é omitido ou trocado). O estribo final soma corretamente cisalhamento + 2×torção (`asw_combinado = cisalhamento.asw_s_adotada_cm2_m + 2·torcao.a90_s_cm2_cm·100`), consistente com a spec 07 §3.6.
- **Vão em balanço do degrau** (`degrau.py`, `calcular_vao_balanco`): `a = largura/2` (espinha) e `a = largura + bw_viga/200` (flutuante) — reconferido byte a byte contra os goldens E3 (`a=0,45m`) e E4 (`a=1,00m`) da spec 07, valores reproduzidos exatamente.
- **Armadura de pele da viga central** (`viga_escada.py`): `As,pele = 0,10%·bw·h`, por face, referência NBR 6118:2023, 17.3.5.2.3 — reconferido: a norma dispensa a armadura de pele para `h < 60 cm` (o que cobre a maioria das vigas de escada), mas o próprio código/spec já documenta a decisão consciente de manter sempre (spec 07 §3.4: "manter, é barato e cobre a torção"), sendo portanto a favor da segurança, não uma divergência.
- **Fator de inclinação da escada treliçada** (`escada_trelicada.py`, `fator = l_inclinado_m/vao_m`, aplicado a `g_total`): reconferido contra o golden E-T1 da spec 07b (`fator = 1,09954`, `g_total = 5,20560 kN/m²`) — valores reproduzidos exatamente; a integração com `LajeTrelicada.fator_inclinacao` (campo aditivo com default 1,0, spec 07b decisão 3) preserva os goldens antigos da spec 03, confirmando que a extensão foi feita sem regressão.
- **Critério do intereixo da nervura da escada treliçada**: reaproveita o mesmo critério ≤65 cm ⇒ "laje" (do módulo `lajes/trelicada/`, já auditado na auditoria de lajes) sem alteração — reconferido no golden E-T1 (`e=42 ≤ 65 → critério "laje"`).
- **Peso dos degraus de concreto sobre a capa da treliçada** (`escada_trelicada.py`): `pp_degraus = 25·(espelho/2)/100` — mesmo termo `espelho/2` (volume médio do prisma triangular do degrau) usado na `esp_real` da reta maciça, reconferido como consistente entre os dois pipelines (decisão 5 da spec 07b, explicitamente a favor da segurança ao assumir degrau de concreto moldado em vez de enchimento leve).

## 2. Critérios e dicas dos professores (conhecimento prático, não normativo)

### Do curso Estrutural na Real (Eng. Waltner Wagner)

- A planilha "ESCADA RETA"/"ESCADA PLISSADA" ensina a calcular a espessura
  equivalente de projeção horizontal (`esp_real`) como o primeiro passo antes
  de qualquer esforço — a lógica pedagógica é "transformar a escada real
  (inclinada, com degraus) numa laje horizontal equivalente mais pesada", em
  vez de trabalhar com esforços no plano inclinado diretamente. É a mesma
  filosofia adotada pelo `dlima-estrutural`.
- Na aba "ESPINHA DE PEIXEFLUTUANTE", o professor reforça que o degrau em
  balanço deve sempre ser verificado com a carga de uma pessoa isolada na
  ponta (não distribuída), porque é o caso mais desfavorável para a ponta
  livre do balanço — mesma decisão 7 já adotada na spec (P = 2,5 kN).
- O cobrimento da viga central e do degrau tem célula própria e digitável na
  planilha (E17), sem vínculo automático com uma tabela de CAA — reforça que
  a prática de mercado ensinada no curso já trabalha com cobrimento digitado
  por decisão do projetista, não derivado automaticamente; a decisão do
  `dlima-estrutural` de manter esse campo livre é consistente com a prática
  ensinada, mas — como registrado no achado #2 — sem nenhuma trava de
  sanidade contra o mínimo nominal.
- O curso ensina explicitamente a distinguir espinha de peixe (viga central,
  balanço nos dois lados) de flutuante (viga lateral embutida na parede,
  balanço de um lado só) pela forma como o vão do degrau é medido — erro
  comum de aluno apontado nas correções do professor é usar a fórmula de vão
  da espinha de peixe (metade da largura) na variante flutuante (que precisa
  da largura inteira mais meia viga).
- Regra prática do curso para pré-dimensionar a espessura da viga central:
  h ≈ L/12 a L/15 para vãos usuais de lance de escada residencial (5–6 m),
  como ponto de partida antes de rodar o dimensionamento completo.

### Heurísticas gerais reforçadas pela spec interna (registradas na própria spec 07/07b)

- Regra de ouro repetida em todas as auditorias deste repositório: a escolha
  de bitola/espaçamento é sempre do projetista — a tabela de opções, nunca
  auto-seleção — já seguida à risca em `escadas/**` (mesmo padrão do
  `lajes/detalhamento.py` e `vigas/detalhamento.py` reaproveitados).
- A conversão do "aço da vigota conta a favor" na escada treliçada (decisão
  8 da spec 07b) é uma prática de mercado — a tabela de barras entrega o As
  total da nervura, e cabe ao engenheiro descontar o banzo inferior da
  treliça pelo catálogo do fabricante antes de decidir a armadura
  complementar — mesma disciplina já observada no módulo de laje treliçada
  de piso (auditoria de lajes, achado #11, mesma assimetria de cobertura
  entre nervura de piso e nervura de escada quanto à armadura de
  distribuição, aqui já coberta corretamente por `as_capa`).

## 3. Nota sobre rigor de verificação

Os 6 arquivos do módulo `escadas/**` foram lidos integralmente nesta
auditoria (`cargas.py`, `degrau.py`, `escada_trelicada.py`, `geometria.py`,
`laje_escada.py`, `viga_escada.py`, ~950 linhas no total), assim como as
duas specs completas (`07_escadas.md`, 361 linhas, e `07b_tipos_escada.md`,
262 linhas), incluindo as seções de divergências/decisões e os 9 exemplos
golden. O ambiente desta sessão tinha `poppler-utils`/`pdftotext` e
`openpyxl` disponíveis — a busca por "escada" na NBR 6118:2023 oficial foi
feita por texto completo (confirmando a ausência de capítulo dedicado), e as
duas planilhas Waltner foram abertas diretamente (`openpyxl`,
`data_only=False`, todas as abas relevantes) para reconferir fórmulas de
célula, não apenas repetir o resumo já existente nas specs internas.

Como o módulo de escadas já continha duas specs com auto-auditoria bastante
detalhada (19 divergências entre planilha e norma, todas já resolvidas a
favor da norma ou de uma "estática limpa", mais 9 exemplos golden com
tolerância de 0,5–1%), o resultado desta auditoria independente é
**majoritariamente confirmatório quanto a fórmulas e coeficientes**: nenhuma
das 19 decisões já registradas foi encontrada mal resolvida contra a
planilha ou a norma oficial. Os achados novos (§1) são gaps de **cobertura
funcional de ELS** (fissuração ausente em toda a árvore de escada — achado
#1, HIGH, mesma classe do achado #3 da auditoria de lajes), de **validação
de entrada** (cobrimento sem piso mínimo — achado #2, MEDIUM) e um gap de
**ELU de cortante no degrau** (achado #4, MEDIUM) — nenhum deles é erro de
fórmula já implementada, e o achado #1 (fissuração) é herdado diretamente da
ausência dessa verificação também nas duas planilhas-fonte do curso, o que
não isenta o app de implementá-la (a norma exige, independente do que a
planilha didática ensina), mas explica por que a lacuna não foi detectada
antes.

Nenhum número de item de norma foi inventado: todos os itens citados (13.2.4,
17.3.3, 19.4.1, 17.5.1.5/.6, 17.7.1.2, 17.3.5.2.3, Tabela 6.1, Tabela 7.2)
foram conferidos diretamente contra as constantes `REF_*`/`referencia_normativa`
já presentes no código-fonte auditado (herdadas dos módulos de laje/viga já
auditados) ou contra o texto oficial extraído do PDF nesta sessão.

---
*Fontes: código-fonte lido integralmente em
`C:\Users\leona\dlima-estrutural\src\estrutural\core\elementos\escadas\**`
(cargas.py, degrau.py, escada_trelicada.py, geometria.py, laje_escada.py,
viga_escada.py); `specs\07_escadas.md`; `specs\07b_tipos_escada.md`;
`src\estrutural\core\elementos\lajes\els.py` e
`src\estrutural\core\elementos\vigas\els.py` (para confirmar a existência e
não-uso das funções de fissuração); `src\estrutural\core\normas\nbr6118_2023.py`
(ClasseAgressividade, COBRIMENTOS_E_FCK_MINIMO); planilhas
`ESCADA PLISSADA E RETA_ENG.WALTNERWAGNER.xlsx` (abas "ESCADA RETA",
"ESCADA PLISSADA", "DET. ESCADA PLISSADA") e
`ESCADA ESPINHA DE PEIXE E FLUTUANTE - ENG.WALTNERWAGNER2.xlsx` (aba
"ESPINHA DE PEIXEFLUTUANTE"), lidas via `openpyxl` em
`C:\Users\leona\Downloads\Módulo 2\BÔNUS - MÓDULO 2 - PÓS GRADUAÇÃO-20250926T033145Z-1-001\BÔNUS - MÓDULO 2 - PÓS GRADUAÇÃO\PLANILHAS\`;
NBR 6118:2023 oficial, lida via `pdftotext -enc UTF-8` em
`C:\Users\leona\Downloads\Módulo 2\BÔNUS - MÓDULO 2 - PÓS GRADUAÇÃO-20250926T033145Z-1-001\BÔNUS - MÓDULO 2 - PÓS GRADUAÇÃO\NORMAS\NBR 6118 - 2023.pdf`
(busca textual completa por "escada"; itens 13.2.4, 17.3.3, 19.4.1, 17.5,
17.7.1.2, 17.3.5.2.3 extraídos e citados diretamente). O PDF de modelo de
detalhamento (`MODELO - ESCADA.pdf`) não foi aberto nesta sessão — é
desenho, não cálculo, e não havia tempo excedente após a cobertura de
cálculo/norma/planilha.*
