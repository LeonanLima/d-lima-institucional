# Resumo Musso — Pilares de concreto armado (fatia 4, `MUSSO`)

> Fonte: `C:\Users\leona\MUSSO\docs\fatias\04-pilares.md` (teoria/fórmulas),
> `src\estrutural\domain\pilares\services\dimensionar_pilar.py`,
> `entities\pilar.py`, `value_objects\tipo_pilar.py` e
> `tests\unit\pilares\test_pilares.py` (oráculo/valores golden). Escopo v1 do
> Musso: **pilar curto intermediário, flexo-compressão NORMAL** (uma direção
> de cada vez, sem envoltória oblíqua, sem 2ª ordem, sem fluência) — mais
> restrito que o `dlima-estrutural`, que já implementa 2ª ordem (pilar-padrão)
> e envoltória oblíqua (α=1,2).

## 1. Fórmulas principais (Musso v1)

### Esbeltez e dispensa de 2ª ordem
```
lₑ = altura do lance (simplificação lₑ = H; §15.6)
λ_i = lₑ·√12/h_i
e1 = γf·Mk_i·100/Nd   [cm]  (1ª ordem, sem parcela acidental — só se Nd>0)
λ1_i = (25 + 12,5·e1/h_i)/αb ,  35 ≤ λ1 ≤ 90
```
> O Musso adota **αb = 1,0 fixo** no v1 (`_ALPHA_B = 1.0`, comentário
> "coeficiente αb conservador para o v1") — não calcula αb real a partir dos
> momentos de topo/base. Isso é uma simplificação consciente do Musso
> (documentada como fora de escopo v1), não um erro: usar αb=1 é sempre igual
> ou mais conservador que o αb real (αb ≤ 1 sempre reduz λ1, tornando mais
> fácil classificar o pilar como esbelto) — na prática Musso tende a mandar
> pilares para "esbelto/aviso" com mais frequência do que a formulação
> completa. λ > λ1 → pilar esbelto → **aviso "fora do escopo v1"**, sem
> calcular e2 nem Md,tot (2ª ordem não implementada no v1 do Musso).

### Momento mínimo de 1ª ordem — §11.3.3.4.3
```
e1,mín_i = 1,5 + 0,03·h_i   [cm]
Md_i = max(γf·Mk_i ; Nd·e1,mín_i)   [kN·m]
```

### Flexo-compressão normal — armadura simétrica em duas faces
Bloco retangular (αc=0,85, λ=0,80, εcu=3,5‰), sem distinção de pivô A/B/C —
**o Musso usa sempre a mesma reta de deformação a partir da borda comprimida**
(`σsc = clamp(Es·εcu·(x−d')/x; ±fyd)`, mesma expressão para σst), mesmo
quando x > h (domínio 5). Isso é a **divergência 5** já registrada e corrigida
no `dlima-estrutural` (spec §5, item 5): a NBR exige pivô C (rotação em
ξ=3h/7, εc2=2‰) no domínio 5, não a extrapolação da reta de εcu na borda.

```
d = h − d'      z = h/2 − d'      y = min(λ·x; h)      Rcc = αc·fcd·b·y
As,face(x) = [Md − Rcc·(h/2 − y/2)] / [z·(σsc − σst)]     (equilíbrio de momento, linear em As,face)
g(x) = Rcc + As,face(x)·(σsc + σst) − Nd = 0                (resíduo de força normal, busca em x por varredura + bisseção)
As,tot = 2·As,face
```
Domínios (fronteiras x/d): x≤0,259d → 2; ≤0,628d → 3; ≤d → 4; ≤h → 4a; >h → 5.

**Direção governante**: a de maior As calculado entre x e y — **não há
verificação oblíqua** no v1 (a envoltória (Mx/MRdx)^1,2+(My/MRdy)^1,2≤1 é
"Extensão A", fora do escopo). O `dlima-estrutural` já implementa essa
extensão.

### Armaduras limite — §17.3.5.3
```
As,mín = max(0,15·Nd/fyd ; 0,004·Ac)      As,máx = 0,08·Ac
```
Idêntica ao `dlima-estrutural`.

### Detalhamento — §18.4
```
Ø_long: 10 mm ≤ Ø ≤ min(hx,hy)/8       n ≥ 4 (par, simétrico)
Øt ≥ max(5 mm; Ø_long/4)                s ≤ min(menor dimensão; 20·Ø_long[cm]; 30 cm)
```
> **Divergência 4 já registrada** (spec `04_pilares.md` §5): o Musso usa
> `s ≤ min(b; 20·Ø_long; 30 cm)`, mas a NBR 6118:2023, 18.4.3 pede
> `s ≤ min(20 cm; b; 12Ø para CA-50 / 24Ø para CA-25)` — o teto certo é
> **12Ø para CA-50** (bem mais restritivo que "20Ø"), confirmado por leitura
> direta da norma nesta auditoria (ver `docs/auditoria-pilares-...md`). O
> Musso auto-seleciona também a bitola de menor sobra (`_detalhar`), diferente
> do requisito de produto do `dlima-estrutural` (tabela de opções, escolha do
> usuário) — divergência 6 da spec.

## 2. Valores golden (oráculo por equilíbrio inverso, `test_pilares.py`)

Seção 20×20 cm, C25, CA-50, CAA II, c=3,0 cm, Øt=5 mm, Ø_long=16 mm →
d'=4,3 cm, z=5,7 cm. Construção do oráculo: escolhe-se x=12 cm e
As,face=2,0 cm² e retro-calcula-se (Nd, Md):

| Grandeza | Valor |
|---|---|
| y = λ·x | 9,6 cm |
| Rcc = αc·fcd·b·y | 291,43 kN |
| σsc (escoa, +fyd) | +43,478 kN/cm² |
| σst | −22,66 kN/cm² |
| Nd = Rcc + 2·(σsc+σst) | 333,06 kN → Nk = Nd/1,4 = 237,90 kN |
| Md = Rcc·5,2 + 2·5,7·(σsc+σst)... | 2269,4 kN·cm → Mk = 16,210 kN·m |

O motor deve **recuperar**: Nd=333,06 kN; λ=le·√12/h=200·3,4641/20=**34,64**
≤ λ1=35 (curto nas duas direções); direção x governa; **x≈12 cm, domínio 4**;
**As,tot = 2×2,0 = 4,0 cm²**; As,mín=1,6 cm² (0,4%·Ac); As,máx=32 cm² (8%·Ac);
seção OK. Testes adicionais: pilar esbelto quando altura=400 cm (λ≈69,3>λ1=35
→ aviso "esbelto"); validação de dimensão mínima (`hx=10` → erro `b_mín`);
validação de Nk>0 obrigatório.

> Este mesmo caso 20×20 é reaproveitado como **golden E2** na spec
> `04_pilares.md` do `dlima-estrutural` (§6), estendido com a verificação
> oblíqua (que eleva As,adotada de 4,00 para 6,09 cm² quando M1d,y de mínimo
> entra no par da oblíqua) — a spec confirma explicitamente que o resultado
> "reto" (x=12,00; As=4,00; domínio 4) bate com o oráculo do Musso antes de
> aplicar a extensão oblíqua.

## 3. Limitações do escopo v1 do Musso (não é bug, é fatia menor)

- Só pilar **intermediário** (`TipoPilar.INTERMEDIARIO` é o único valor do
  enum) — extremidade/canto (que exigem oblíqua) ficam para "Extensão A".
- Só pilar **curto** com 2ª ordem dispensada — pilar esbelto só gera aviso,
  sem calcular e2/Md,tot ("Extensão B").
- Fluência (λ>90) não implementada ("Extensão C").
- `comprimento_equivalente` = altura do lance direto (lₑ = H), sem o
  refinamento de `lₑ = min(l0+h; l0+t)` do §15.6 que o `dlima-estrutural`
  já recebe como entrada externa (`le_x_cm`/`le_y_cm`, calculado fora do
  motor de pilares).
- αb fixo em 1,0 (não calcula αb real a partir de M_topo/M_base) — sempre a
  favor da segurança quanto à classificação de esbeltez, mas menos preciso.

## 4. O que o `dlima-estrutural` já superou em relação ao Musso v1

O módulo de pilares do `dlima-estrutural` (`src/estrutural/core/elementos/pilares/`)
implementa **mais** do que a fatia v1 do Musso: 2ª ordem pelo pilar-padrão com
curvatura aproximada (§15.8.3.3.2), αb real por direção (não fixo em 1,0),
verificação pela envoltória oblíqua (§17.2.5.2, α=1,2) e pivô C correto no
domínio 5 (Fig. 17.1). As 8 divergências entre o Musso/skill de apoio e a
norma já foram identificadas e resolvidas a favor da norma na própria spec
interna (`specs/04_pilares.md`, §5) antes mesmo desta auditoria — o Musso
serve aqui como referência de fórmulas e valores golden para conferência
aritmética, não como fonte de correção do código.
