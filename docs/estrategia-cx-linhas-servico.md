# D'LIMA Engenharia — Estratégia CX: Modelo de 3 Linhas de Serviço
*Gerado em: 2026-06-15 | Fonte: Conselho + 8 squads de marketing*

---

## Estrutura de Atendimento

| Linha | Metragem | Foco |
|---|---|---|
| **Linha Essencial** | ≤ 70 m² | Eficiência, padronização, custo-benefício |
| **Linha Conforto** | 71 – 130 m² | Equilíbrio, estética, decisões assistidas |
| **Linha Exclusive** | 131 – 250 m² | Concierge de Engenharia, curadoria total |
| **Linha Luxo** | > 250 m² | Gestão de obra integral, alto padrão absoluto |

### Regras de Negócio (invioláveis)
- **Upsell de Conveniência:** Qualquer cliente pode solicitar upgrade para categoria superior pagando a diferença de taxa.
- **Trava Exclusive:** Projetos de 131–250 m² são OBRIGATORIAMENTE Linha Exclusive. Sem exceção.
- **Trava Luxo:** Projetos acima de 250 m² são OBRIGATORIAMENTE Linha Luxo. Sem exceção. Sem negociação.

---

## 1. Matriz de Elegibilidade

| Critério | Linha Essencial | Linha Conforto | Linha Exclusive |
|---|---|---|---|
| **Metragem** | ≤ 70 m² | 71 – 130 m² | 131 – 250 m² *(obrigatório)* | > 250 m² *(obrigatório)* |
| **Periodicidade de Report** | Relatório fotográfico quinzenal | Relatório executivo semanal | Dashboard semanal + reunião conforme necessidade | Dashboard em tempo real + reunião conforme necessidade |
| **Tipo de Entrega** | Projeto técnico com opções pré-definidas | Projeto assistido com customização guiada | Curadoria técnica total do processo | Gestão integral de obra — alto padrão absoluto |
| **Visitas de Obra** | 2x / mês | 4x / mês | Semanal + sob demanda | Presença contínua (escalonada) |
| **Canal de Comunicação** | E-mail + portal digital | WhatsApp dedicado + e-mail | Linha direta com o engenheiro responsável | Linha direta com o engenheiro responsável — prioridade máxima |
| **Gestão de Fornecedores** | Indicação de lista validada | Triagem e negociação assistida | Seleção, negociação e contrato gerenciados pela D'LIMA | Curadoria premium — fornecedores de alto padrão + contratos assinados pela D'LIMA |
| **Disponibilidade de Urgência** | Horário comercial | Horário comercial + urgências críticas | 7 dias, resposta garantida | 24h / 7 dias — disponibilidade total |
| **Benefícios Principais** | Custo-benefício, prazo previsível, padronização | Estética, decisões assistidas, equilíbrio qualidade/preço | Proteção técnica total, curadoria de materiais, gestão de risco | Experiência de obra sem stress — nível construtoras de luxo |
| **Upsell disponível** | → Conforto, Exclusive ou Luxo | → Exclusive ou Luxo | → Luxo | — |
| **Trava de Segurança** | Não aplicável | Não aplicável | **Obrigatório para 131–250 m²** | **Obrigatório para > 250 m²** |

---

## 2. Pitches de Venda

### Pitch A — Upgrade de Conveniência
*Para quem quer fazer upgrade sem parecer que estou cobrando mais*

> "[Nome], antes de fecharmos, quero te mostrar uma coisa.
>
> Seu projeto se enquadra na Linha Essencial — tecnicamente resolvido, prazo previsível, entrega sólida.
>
> Mas ao longo da nossa conversa você mencionou [elemento específico do cliente]. Na Linha Conforto, eu assumo as decisões que mais consomem o seu tempo: escolha de acabamentos, negociação com fornecedores, cronograma detalhado de compras. Você foca no que importa — eu garanto que cada decisão técnica esteja alinhada com o que você quer.
>
> A diferença de investimento é [X]. O que você compra com isso não é 'mais serviço' — é o seu tempo de volta, e a garantia de que nenhuma decisão técnica vai virar arrependimento.
>
> Faz sentido para você?"

**Por que funciona:** Jobs-to-be-Done (cliente quer tranquilidade, não mais serviço). Reciprocidade (usa o que ele mesmo disse). Parece diagnóstico, não upsell.

---

### Pitch B — Trava de Segurança para ≥150m²
*Como comunicar que a Exclusive é obrigatória sem gerar resistência*

> "[Nome], preciso te contar algo importante antes de continuarmos.
>
> Projetos a partir de 150m² na D'LIMA são classificados automaticamente como Linha Exclusive. Não é uma questão de preferência — é uma questão de risco técnico.
>
> Obras nessa escala têm pontos críticos de decisão — estrutura, instalações, subempreiteiros simultâneos, cronograma em cascata — que, se mal gerenciados, custam muito mais do que qualquer taxa de serviço. São riscos que eu não consigo mitigar com o protocolo de um projeto menor, e que não vou assumir dessa forma.
>
> A Linha Exclusive existe precisamente para isso: garantir que cada ponto crítico tenha o nível de atenção que um investimento desse tamanho exige. O protocolo que aplicamos aqui é o que evita que seu maior investimento vire um projeto de reforma permanente.
>
> Posso te detalhar o que está incluído no Concierge de Engenharia?"

**Por que funciona:** Accusation Audit (antecipa objeção de preço). Authority Bias (o engenheiro define o protocolo). Transforma trava em proteção. Loss Aversion ética.

---

### Pitch C — Público Aspiracional
*Para vender exclusividade para quem não tem a metragem*

> "[Nome], seu projeto tem [X]m² — pela nossa estrutura, ele se enquadra na Linha Conforto.
>
> Mas antes de seguirmos: a Linha Exclusive está disponível como upgrade para qualquer metragem.
>
> Se o nível de atenção que você quer para este projeto — curadoria de fornecedores, relatório semanal, disponibilidade direta comigo nos momentos críticos — é o mesmo que aplicamos em obras de 200m²+, é exatamente isso que a Exclusive entrega.
>
> A diferença entre o que você pagaria na Conforto e o que investiria na Exclusive é [X]. Nos próximos [duração da obra] meses, isso representa [X por semana/mês].
>
> A pergunta não é se seu projeto tem a metragem. A pergunta é: qual é o nível de tranquilidade que você quer ter durante a obra?"

**Por que funciona:** Reframing de preço (converte em custo temporal). Identificação aspiracional (cliente se alinha com perfil Exclusive). Pergunta calibrada (Voss) ativa autoconsciência sem pressão.

---

## 3. Simulador de Categoria (Python)

```python
def classificar_projeto(metragem_m2: float, desejo_cliente: str = None) -> dict:
    """
    Simulador de Categoria D'LIMA Engenharia — 4 Linhas

    Args:
        metragem_m2: Área do projeto em m²
        desejo_cliente: 'essencial' | 'conforto' | 'exclusive' | 'luxo' | None

    Returns:
        dict com categoria, justificativa, trava_ativa, upsell_aplicado
    """

    LINHAS = ["essencial", "conforto", "exclusive", "luxo"]
    TAXAS_BASE = {
        "essencial": {"base": 0, "por_m2": 0},   # preencher com valores reais
        "conforto":  {"base": 0, "por_m2": 0},
        "exclusive": {"base": 0, "por_m2": 0},
        "luxo":      {"base": 0, "por_m2": 0},
    }

    # ─── TRAVA LUXO (inviolável — primeira guarda) ───────────────────
    if metragem_m2 > 250:
        return {
            "categoria": "Linha Luxo",
            "categoria_base": "Linha Luxo",
            "trava_ativa": True,
            "upsell_aplicado": False,
            "justificativa": (
                "Projetos acima de 250m² requerem protocolo "
                "Luxo — gestão integral de obra. "
                "Trava de Segurança ativa."
            ),
            "taxa_estimada": calcular_taxa("luxo", metragem_m2, TAXAS_BASE),
        }

    # ─── TRAVA EXCLUSIVE (segunda guarda) ────────────────────────────
    if metragem_m2 >= 131:
        return {
            "categoria": "Linha Exclusive",
            "categoria_base": "Linha Exclusive",
            "trava_ativa": True,
            "upsell_aplicado": False,
            "justificativa": (
                "Projetos de 131m² a 250m² requerem protocolo "
                "Concierge de Engenharia obrigatoriamente. "
                "Trava de Segurança ativa."
            ),
            "taxa_estimada": calcular_taxa("exclusive", metragem_m2, TAXAS_BASE),
        }

    # ─── CLASSIFICAÇÃO BASE POR METRAGEM ────────────────────────────
    if metragem_m2 <= 70:
        categoria_base = "essencial"
    else:  # 71–130
        categoria_base = "conforto"

    # ─── UPSELL DE CONVENIÊNCIA ─────────────────────────────────────
    upsell_map = {
        "essencial": ["conforto", "exclusive", "luxo"],
        "conforto":  ["exclusive", "luxo"],
        "exclusive": ["luxo"],
        "luxo":      [],
    }

    categoria_final = categoria_base
    upsell_aplicado = False

    if desejo_cliente and desejo_cliente.lower() in LINHAS:
        desejo = desejo_cliente.lower()

        if desejo in upsell_map[categoria_base]:
            categoria_final = desejo
            upsell_aplicado = True

        elif LINHAS.index(desejo) < LINHAS.index(categoria_base):
            return {
                "categoria": categoria_base.capitalize(),
                "alerta": (
                    f"Seu projeto ({metragem_m2}m²) exige no mínimo "
                    f"a Linha {categoria_base.capitalize()}. "
                    "Downgrade não disponível."
                ),
                "trava_ativa": False,
                "upsell_aplicado": False,
            }

    # ─── OUTPUT FINAL ────────────────────────────────────────────────
    nome_linha = {
        "essencial": "Linha Essencial",
        "conforto":  "Linha Conforto",
        "exclusive": "Linha Exclusive",
        "luxo":      "Linha Luxo",
    }

    return {
        "categoria": nome_linha[categoria_final],
        "categoria_base": nome_linha[categoria_base],
        "trava_ativa": False,
        "upsell_aplicado": upsell_aplicado,
        "diferencial_upsell": (
            calcular_taxa(categoria_final, metragem_m2, TAXAS_BASE)
            - calcular_taxa(categoria_base, metragem_m2, TAXAS_BASE)
            if upsell_aplicado else 0
        ),
        "taxa_estimada": calcular_taxa(categoria_final, metragem_m2, TAXAS_BASE),
    }


def calcular_taxa(categoria: str, metragem: float, taxas: dict) -> float:
    t = taxas[categoria]
    return t["base"] + (metragem * t["por_m2"])


# Exemplos de uso:
# classificar_projeto(65)               → Linha Essencial
# classificar_projeto(65, "conforto")   → Linha Conforto (upsell)
# classificar_projeto(150)              → Linha Exclusive OBRIGATÓRIO (trava)
# classificar_projeto(100, "exclusive") → Linha Exclusive (aspiracional)
# classificar_projeto(300)              → Linha Luxo OBRIGATÓRIO (trava)
```

---

## 4. Justificativas de Valor — 5 Argumentos

### 1. Risco técnico não-linear (técnico)
Projetos acima de 200m² não são "obras maiores" — são obras com geometria de risco diferente. Uma decisão equivocada em estrutura, instalações ou sequenciamento em 250m² tem impacto em cascata que pode comprometer prazos, orçamento e segurança. O custo de retrabalho ultrapassa em múltiplas vezes o custo da taxa de serviço.

**Argumento de venda:** "A diferença entre o custo do Exclusive e o custo de um retrabalho estrutural em 200m²+ não é percentual. É uma ordem de grandeza."

### 2. Responsabilidade técnica registrada (técnico-legal)
O engenheiro responsável assina a ART/RRT de projeto e execução. Gerir uma obra de 220m² com protocolo de projeto de 80m² é risco legal que o Conselho de Engenharia materializa em responsabilidade civil e profissional.

**Argumento de venda:** "Quando eu assino a responsabilidade técnica, estou formalmente comprometido com cada decisão. O Exclusive é o protocolo que torna esse comprometimento sustentável."

### 3. Ancoragem no custo total do projeto (financeiro)
Uma obra de 150m²+ raramente representa menos de R$600k–R$1,5M em custo de construção. A diferença entre Conforto e Exclusive representa um percentual pequeno do custo total — e garante gestão especializada de 100% desse orçamento.

**Argumento de venda:** "Você está investindo R$800k em construção. O custo do Exclusive representa X% desse investimento. Qual é o custo de não ter esse protocolo?"

### 4. Psicologia da perda, não do ganho (psicológico)
A pergunta certa não é "quanto custa a Exclusive?" — é "quanto custa não ter o protocolo Exclusive?" Atraso tem custo de hospedagem/aluguel. Retrabalho tem custo material. Conflito de fornecedores tem custo de tempo e estresse.

**Argumento de venda:** "Cada dia de atraso em obra tem custo real — aluguel, hospedagem, stress. O Exclusive é o protocolo que protege o seu cronograma, não apenas a obra."

### 5. Sinal de mercado e proteção de reputação mútua (estratégico)
Toda construtora do mercado faz "qualquer projeto de qualquer tamanho". A D'LIMA é a única que declara publicamente que projetos >200m² têm classificação obrigatória. Isso afasta clientes que buscam o menor preço em obra complexa — os mais problemáticos — e atrai quem paga por segurança.

**Argumento de venda:** "Qualquer empresa aceita qualquer obra. Nós estabelecemos o padrão mínimo que garante que o seu projeto seja entregue da forma que merece."

---

## Alertas do Conselho

- **Fronteira 130→131m²:** Prepare comunicação proativa para clientes na faixa 100–130m² sobre o protocolo Exclusive antes da objeção chegar.
- **Fronteira 250→251m²:** Prepare comunicação proativa para clientes na faixa 220–250m² sobre o protocolo Luxo antes da objeção chegar.
- **Operacionalização primeiro:** Documente o que muda entre linhas (quem atende, quantas reuniões, prazo de resposta, entregáveis) ANTES de qualquer material de marketing.
- **Metragem é triagem, complexidade é o critério real:** Para projetos na zona cinza, a entrevista de escopo deve complementar a metragem.
- **A Trava é inegociável:** Nunca abra exceção. A força do modelo depende de ela ser absoluta.
