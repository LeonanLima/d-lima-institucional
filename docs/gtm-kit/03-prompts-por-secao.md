# Mega-Prompt fatiado — versão para modelos econômicos

Modelo econômico entrega qualidade quando a tarefa é pequena e o critério é claro. Esta versão divide a mesma entrega em **11 prompts sequenciais** — mesmo conteúdo, mesma ordem, com critério de aceite por seção para você rejeitar saída fraca na hora.

## Regras de operação

1. **Tudo na MESMA conversa**, na ordem abaixo. Cada seção usa as anteriores como contexto.
2. **Não avance com seção ruim.** Cheque o critério de aceite; se falhar, responda: *"Refaça aplicando as regras da entrega. Está genérico / sem número / sem primeiro passo."* Modelo econômico melhora muito na segunda tentativa com feedback específico.
3. Ao final, monte o documento colando as 9 seções aprovadas + o fechamento num único .md.

---

## PROMPT 0 · Setup (cole com o briefing dentro)

```text
Você é um estrategista sênior de go-to-market com 20 anos lançando produtos e serviços no Brasil, contratado por R$ 100 mil para UMA entrega: a estratégia go-to-market completa do produto descrito no briefing abaixo. A estratégia precisa ser executável pelo time, pelo caixa e pelo tempo declarados no briefing, não por uma multinacional com verba infinita.

BRIEFING:
{cole aqui os 4 blocos preenchidos do 01-briefing.md}

REGRAS DA ENTREGA (valem para TODAS as respostas desta conversa):
(1) Zero genérico: toda recomendação vem com o porquê, com número estimado e com o primeiro passo concreto.
(2) Onde o briefing não der um dado, declare a premissa assumida em vez de fingir certeza. Mantenha uma lista de premissas e me mostre quando eu pedir.
(3) Em toda seção, deixe claro o que vem PRIMEIRO.
(4) Respeite o caixa: cada aposta tem custo estimado em R$ e prazo esperado de retorno.
(5) Português direto, sem jargão de consultoria e sem motivação vazia.

Vamos construir a estratégia em 9 seções, uma por vez, eu peço cada uma. Antes de começar: me faça até 5 perguntas se algo essencial estiver faltando no briefing. Se eu não souber responder, siga com premissas declaradas. Faça as perguntas agora.
```

**Aceite:** o modelo fez perguntas específicas sobre o SEU briefing (não perguntas genéricas de formulário). Responda com honestidade antes de seguir.

---

## PROMPT 1 · Diagnóstico de mercado e timing

```text
SEÇÃO 1 — DIAGNÓSTICO DE MERCADO E TIMING: estime o mercado endereçável em 3 níveis (total, alcançável, capturável em 12 meses) mostrando a LÓGICA do cálculo; mapeie 3 a 5 concorrentes diretos e indiretos com o ângulo de ataque de cada um; e responda: por que lançar isso NESTE momento — o que mudou no mercado que abre a janela?
```

**Aceite:** os 3 níveis têm conta visível (fonte ou premissa × premissa, não número solto); cada concorrente tem um ângulo de ataque acionável; o timing cita uma mudança concreta (regulação, comportamento, tecnologia, preço), não "o mercado está aquecido".

## PROMPT 2 · ICP e anti-ICP

```text
SEÇÃO 2 — ICP E SEGMENTAÇÃO: o perfil de cliente ideal em detalhe (quem é, o que já tentou, quanto a dor custa pra ele em R$ por mês, qual evento o faz procurar solução); depois o ANTI-ICP: o perfil que parece cliente, compra, e dá prejuízo em suporte, churn ou reputação — e como filtrá-lo antes da venda.
```

**Aceite:** a dor tem custo em R$/mês ou horas/semana; existe um "evento-gatilho" que faz o ICP procurar solução; o anti-ICP vem com filtro prático aplicável ANTES da venda (pergunta de triagem, critério objetivo).

## PROMPT 3 · Posicionamento e mensagem

```text
SEÇÃO 3 — POSICIONAMENTO E MENSAGEM: em que categoria competimos (ou que categoria criamos); contra qual status quo nos posicionamos; a promessa central em UMA frase que um leigo entende; e as 3 provas que a sustentam hoje, com o que temos.
```

**Aceite:** a promessa cabe numa frase e um leigo entende sem explicação; as 3 provas usam o que o negócio TEM hoje (não "colete depoimentos futuramente").

## PROMPT 4 · Oferta e pricing

```text
SEÇÃO 4 — OFERTA E PRICING: a estrutura completa da oferta (o que entra, bônus que aumentam valor percebido sem aumentar custo, garantia que remove o risco, urgência legítima); o preço recomendado com a lógica de ancoragem; e até 3 degraus — entrada, principal e premium — com o papel estratégico de cada degrau.
```

**Aceite:** o preço tem lógica de ancoragem explicada (contra o quê o cliente compara); a urgência é legítima (razão real, não escassez inventada); cada degrau tem papel estratégico, não é só "barato/médio/caro".

## PROMPT 5 · Motion de vendas

```text
SEÇÃO 5 — MOTION DE VENDAS: escolha o jeito principal de vender — fundador vendendo em conversa, time comercial, self-service (a pessoa compra sozinha) ou comunidade/conteúdo — e JUSTIFIQUE pela combinação ticket × perfil do cliente × ativos do briefing. Descreva o passo a passo do motion escolhido, da primeira interação ao dinheiro na conta, e diga em que ponto de faturamento esse motion deixa de servir e qual é o próximo.
```

**Aceite:** confira contra a matriz do `05-matriz-ticket-motion.md`. Se sair fora dela, devolva: *"Justifique esse motion pela conta: quanto custa cada venda nesse formato e quanto sobra do ticket?"*

## PROMPT 6 · Canais

```text
SEÇÃO 6 — CANAIS: escolha os 3 canais prioritários pra ESTE produto com ESTE caixa (nada de lista com 10 canais); para cada um: por que ele, a tese de abordagem ou conteúdo, o custo estimado por cliente adquirido e o teste mínimo que valida ou mata o canal em 30 dias.
```

**Aceite:** exatamente 3 canais; cada um com CAC estimado em R$ e um teste de 30 dias com critério de morte ("se X não acontecer, mata o canal").

## PROMPT 7 · Funil e jornada

```text
SEÇÃO 7 — FUNIL E JORNADA: a jornada completa do desconhecido ao cliente pagante — etapas, o que acontece em cada uma, taxa de conversão esperada por etapa com base em referências do mercado — e o gargalo mais provável do MEU funil específico, com o plano B pra ele.
```

**Aceite:** toda etapa tem taxa de conversão esperada; o gargalo apontado é específico deste funil (não "gerar tráfego é difícil") e tem plano B.

## PROMPT 8 · Plano de 90 dias

```text
SEÇÃO 8 — PLANO DE 90 DIAS: semana a semana, o que é feito, por quem (dado o time do briefing) e o critério objetivo de 'feito'; organize em 3 ciclos de 30 dias — VALIDAR (provar que alguém paga), AJUSTAR (consertar o que rangeu), ESCALAR (colocar volume no que provou).
```

**Aceite:** 13 semanas cobertas; cada semana tem responsável (compatível com o time do briefing) e critério de "feito" verificável; os 3 ciclos têm objetivo distinto.

## PROMPT 9 · Métricas e metas

```text
SEÇÃO 9 — MÉTRICAS E METAS: os 5 a 7 indicadores que dizem se a estratégia funciona, a meta realista de cada um em 90 dias, e o número-gatilho que, se não vier, manda parar e repensar em vez de insistir.
```

**Aceite:** 5 a 7 indicadores (não 15); cada um com meta numérica em 90 dias; existe UM número-gatilho de parada claramente marcado.

---

## PROMPT 10 · Fechamento

```text
Agora feche a entrega com três coisas:
(1) A TABELA DE PREMISSAS: todas as premissas que você assumiu ao longo das 9 seções, numa tabela — premissa, seção onde foi usada, impacto se estiver errada.
(2) 'AS 5 DECISÕES MAIS ARRISCADAS DESTA ESTRATÉGIA' — a premissa por trás de cada uma e o jeito mais barato de validar cada premissa.
(3) 'SEGUNDA-FEIRA DE MANHÃ' — a lista objetiva do que eu executo na primeira semana.
Não encerre com resumo motivacional; encerre com trabalho.
```

**Aceite:** a tabela de premissas bate com o que apareceu nas seções; a "segunda-feira de manhã" é executável por quem está no briefing (tempo e time reais).

---

## Depois do fechamento

Siga para o `04-prompts-refino.md` (red team → zoom → empacotamento), na mesma conversa. Os refinos funcionam igual nas duas versões do método.
