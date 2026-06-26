# Laje nervurada / treliçada — material e considerações do Prof. Musso (UFES)

Fonte: Prof. Fernando Musso Jr. (UFES), `CAP3-LAJE-2014-2.pdf`, slide 3
(§13.4 "Dimensões Limites para Lajes") + slides 23-25 (exemplos nervurada /
formas Romanio). Drive id `1BGIbv77Kt88Ggz32JF_72CPPTYPjciHc`. Base normativa:
NBR 6118:2023 §13.2.4.2 (Musso cita NBR 6118:2014, texto equivalente).

Usado para construir o cálculo de **laje treliçada (vigotas + tavelas)** seguindo
as considerações do Musso — par com [tabela maciça do Musso](../calc_estrutural/dimensionamento/tabela_musso.py).

## §13.4.2 — Lajes nervuradas (considerações do Musso, transcrito do slide 3)

**Espessura da mesa (capa):**
- Quando NÃO houver tubulações horizontais embutidas: mesa ≥ 1/15 da distância
  entre faces das nervuras (l0) **e** ≥ 4 cm.
- Mínimo absoluto 5 cm quando houver tubulações de Ø ≤ 10 mm.
- Tubulações Ø > 10 mm: mesa ≥ 4 cm + Øc (ou 4 cm + 2Ø se houver cruzamento).

**Nervuras:**
- Espessura da nervura (bw) ≥ 5 cm.
- Nervura com bw < 8 cm NÃO pode conter armadura de compressão.

**Projeto conforme o espaçamento entre eixos de nervuras (e):**
- a) `e ≤ 65 cm`: dispensa verificação da flexão da mesa; cisalhamento das
  nervuras pode ser verificado **como laje** (critérios de laje, sem estribo).
- b) `65 cm < e ≤ 110 cm`: exige verificação da flexão da mesa; nervuras
  verificadas ao cisalhamento **como viga**. Permite-se verificar como laje se
  `e ≤ 90 cm` E largura média da nervura > 12 cm.
- c) `e > 110 cm`: a mesa deve ser projetada **como laje maciça** apoiada na
  grelha de vigas (respeitando espessura mínima).

## §13.4.1 — Lajes maciças (limites mínimos, para referência)
- 7 cm cobertura sem balanço; 8 cm piso sem balanço; 10 cm com balanço;
- 10 cm para veículos ≤ 30 kN; 12 cm para veículos > 30 kN;
- 15 cm p/ lajes com protensão (vigas) e mín. l/42 p/ lajes de piso biapoiadas
  e l/50 p/ lajes de piso contínuas;
- 16 cm p/ base de pilares (l ≥ 14 cm).
- **Tabela 13.2 — γn (coef. adicional p/ lajes em balanço)**, indexado por h(cm):
  h≥19→γn=1,00 | 18→1,05 | 17→1,10 | 16→1,15 | 15→1,20 | 14→1,25 | 13→1,30 |
  12→1,35 | 11→1,40 | 10→1,45 (γn = 1,95 − 0,05·h).

## Status da implementação (2026-06-26)
- [x] **Fatia trel-1** `dimensionamento/laje_trelicada.py` — `calcular_laje_trelicada`
  (nervura=viga T; PP pela geometria real; M+/M-/V por coef. de vinculação;
  ELU seção T com LN mesa/alma; cisalhamento pelo critério `e` do Musso; flecha
  seção T bruta c/ fluência φ=2,5). Commit feat(laje) trel-1.
- [x] **Fatia trel-2** `tests/test_laje_trelicada.py` — golden (PP geométrico,
  Md, seção T, 3 ramos do critério de cisalhamento). 13 testes; suíte 108 passed.
- [x] **Fatia trel-3** `relatorio/memorial_trelicada.py` — `memorial_laje_trelicada`
  (6 passos, lê do canônico, tabela de aço editável da vigota). Em arquivo próprio
  porque passo_a_passo.py já passou de 800 linhas.
- [x] **Fatia trel-4** UI Streamlit: página "Laje Treliçada" em app_estrutural.py
  (sidebar 🟨; inputs lx/e/capa/h/bw/vinculação/gk/qk/enchimento + materiais;
  abas Dimensionamento [esforços, armadura, painel de verificações flecha/cortante/
  ductilidade, critério Musso, tabela da vigota] + Memorial passo a passo). Default
  lx=3,5 e=40 bw=9 passa limpo. py_compile OK; suíte 108 passed. Falta só verificação
  visual no navegador (streamlit run).
- [ ] **Fatia trel-5** (opcional) golden com EXEMPLO numérico real dos slides 23-25
  do Musso, se Leonan fornecer (hoje o golden usa caso verificável por 1os princípios).

## Plano de implementação (laje treliçada, método do Musso) — referência

Modelo: cada nervura = **viga T** (alma bw da vigota, mesa = capa + tavela
adjacente até e/2 de cada lado). Faixa de cálculo = 1 nervura, depois As por metro.

Fatias sugeridas (1 commit cada, padrão incremental do projeto):
1. `dimensionamento/laje_trelicada.py`: `calcular_laje_trelicada(lx, ly, e_cm,
   h_capa_cm, h_total_cm, bw_cm, gk, qk, vao_tipo, fck, fyk, caa)`:
   - classifica uni/bidirecional (β=b/a, mesma convenção do Musso);
   - momento por nervura (M·e), seção T (bf efetivo NBR §14.6.2.2), ELU flexão
     (LN na mesa vs na alma), As da vigota;
   - cisalhamento: escolhe critério laje vs viga conforme `e` (§13.4.2 a/b/c);
   - flecha (mesma família de coef. do Musso / seção T fissurada);
   - ELS fissuração se aplicável.
2. `relatorio/passo_a_passo.py`: `memorial_laje_trelicada` (passos: classificação,
   limites §13.4.2, cargas, momento por nervura, seção T, As vigota, cisalhamento
   pelo critério do `e`, flecha) — re-deriva e confere com a função canônica.
3. UI Streamlit: nova página/elemento "Laje Treliçada" (e, capa, h, bw, tavela).
4. Tabela de aço editável + detalhamento (padrão [[feedback_detalhamento_tabela_aco]]).
5. Testes golden travando um exemplo do Musso.

CONFERIR antes de implementar a fatia 1: pegar nos slides 23-25 do Musso o
EXEMPLO numérico de nervurada (dimensionamento automático) para travar o golden;
o método de cisalhamento (laje vs viga) sai direto do §13.4.2 acima.
