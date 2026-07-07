# Mega-Prompt GTM — Bloco único

## Como usar (leia antes de colar)

1. **Conversa NOVA, sem histórico.** Conversa antiga carrega contexto que contamina a estratégia.
2. **Uma única mensagem.** Cole o prompt inteiro abaixo, com o briefing preenchido dentro. Não mande em mensagens separadas: o modelo trata cada mensagem como um pedido novo e a arquitetura das 9 seções se perde. Se preferir, monte num arquivo de texto e anexe.
3. **Use o modelo mais forte que tiver.** Se só houver modelo econômico, use o `03-prompts-por-secao.md` no lugar deste.
4. **Responda as perguntas do modelo com honestidade.** Ele vai fazer até 5 perguntas antes de começar — é ali que a estratégia deixa de ser genérica.
5. Ao final, leia TUDO antes de refinar. O interrogatório (`04-prompts-refino.md`) só funciona em cima de leitura de verdade.

---

## O PROMPT (copie daqui até o final do documento)

```text
Você é um estrategista sênior de go-to-market com 20 anos lançando produtos e serviços no Brasil, e foi contratado por R$ 100 mil para UMA entrega: a estratégia go-to-market completa do produto descrito no briefing abaixo. Quem te contratou é o dono do negócio — a estratégia precisa ser executável pelo time, pelo caixa e pelo tempo declarados no briefing, não por uma multinacional com verba infinita.

BRIEFING:
{cole aqui os 4 blocos preenchidos do 01-briefing.md}

REGRAS DA ENTREGA:
(1) Zero genérico: toda recomendação vem com o porquê, com número estimado e com o primeiro passo concreto — 'invista em conteúdo' não é recomendação, é slogan.
(2) Onde o briefing não der um dado, declare a premissa que você assumiu em vez de fingir certeza; liste todas as premissas numa tabela ao final.
(3) Priorize: em toda seção, deixe claro o que vem PRIMEIRO — estratégia sem ordem de execução é lista de desejos.
(4) Respeite o caixa: cada aposta tem custo estimado em R$ e prazo esperado de retorno.
(5) Antes de começar, me faça até 5 perguntas se algo essencial estiver faltando no briefing; se eu não souber responder, siga com premissas declaradas.
(6) Escreva em português direto, sem jargão de consultoria e sem motivação vazia.

A entrega tem 9 seções, nesta ordem.

SEÇÃO 1 — DIAGNÓSTICO DE MERCADO E TIMING: estime o mercado endereçável em 3 níveis (total, alcançável, capturável em 12 meses) mostrando a LÓGICA do cálculo; mapeie 3 a 5 concorrentes diretos e indiretos com o ângulo de ataque de cada um; e responda: por que lançar isso NESTE momento — o que mudou no mercado que abre a janela?

SEÇÃO 2 — ICP E SEGMENTAÇÃO: o perfil de cliente ideal em detalhe (quem é, o que já tentou, quanto a dor custa pra ele em R$ por mês, qual evento o faz procurar solução); depois o ANTI-ICP: o perfil que parece cliente, compra, e dá prejuízo em suporte, churn ou reputação — e como filtrá-lo antes da venda.

SEÇÃO 3 — POSICIONAMENTO E MENSAGEM: em que categoria competimos (ou que categoria criamos); contra qual status quo nos posicionamos; a promessa central em UMA frase que um leigo entende; e as 3 provas que a sustentam hoje, com o que temos.

SEÇÃO 4 — OFERTA E PRICING: a estrutura completa da oferta (o que entra, bônus que aumentam valor percebido sem aumentar custo, garantia que remove o risco, urgência legítima); o preço recomendado com a lógica de ancoragem; e até 3 degraus — entrada, principal e premium — com o papel estratégico de cada degrau.

SEÇÃO 5 — MOTION DE VENDAS: escolha o jeito principal de vender — fundador vendendo em conversa, time comercial, self-service (a pessoa compra sozinha) ou comunidade/conteúdo — e JUSTIFIQUE pela combinação ticket × perfil do cliente × ativos do briefing. Descreva o passo a passo do motion escolhido, da primeira interação ao dinheiro na conta, e diga em que ponto de faturamento esse motion deixa de servir e qual é o próximo.

SEÇÃO 6 — CANAIS: escolha os 3 canais prioritários pra ESTE produto com ESTE caixa (nada de lista com 10 canais); para cada um: por que ele, a tese de abordagem ou conteúdo, o custo estimado por cliente adquirido e o teste mínimo que valida ou mata o canal em 30 dias.

SEÇÃO 7 — FUNIL E JORNADA: a jornada completa do desconhecido ao cliente pagante — etapas, o que acontece em cada uma, taxa de conversão esperada por etapa com base em referências do mercado — e o gargalo mais provável do MEU funil específico, com o plano B pra ele.

SEÇÃO 8 — PLANO DE 90 DIAS: semana a semana, o que é feito, por quem (dado o time do briefing) e o critério objetivo de 'feito'; organize em 3 ciclos de 30 dias — VALIDAR (provar que alguém paga), AJUSTAR (consertar o que rangeu), ESCALAR (colocar volume no que provou).

SEÇÃO 9 — MÉTRICAS E METAS: os 5 a 7 indicadores que dizem se a estratégia funciona, a meta realista de cada um em 90 dias, e o número-gatilho que, se não vier, manda parar e repensar em vez de insistir.

FORMATO DA ENTREGA: documento estruturado com títulos numerados e tabelas onde couber. Feche com duas coisas: (1) 'AS 5 DECISÕES MAIS ARRISCADAS DESTA ESTRATÉGIA' — a premissa por trás de cada uma e o jeito mais barato de validar cada premissa; (2) 'SEGUNDA-FEIRA DE MANHÃ' — a lista objetiva do que eu executo na primeira semana. Não encerre com resumo motivacional; encerre com trabalho.
```

---

## Por que este prompt funciona

- **Papel com reputação em jogo** (contratado por R$ 100 mil, uma entrega) + **cliente com limites reais** (time, caixa e tempo do briefing) + **regras que proíbem as saídas preguiçosas** (zero genérico, premissas declaradas, custo em R$).
- **As seções 1–3 decidem PRA QUEM e COM QUE CONVERSA. As 4–5 decidem QUANTO e COMO.** Nenhuma consultoria séria pula essa ordem — preço antes de ICP é chute com planilha.
- **A seção mais subestimada é o ANTI-ICP (Seção 2).** Todo negócio pequeno aceita qualquer cliente no início — e o cliente errado custa caro em suporte, cancelamento e reputação, além de ocupar a vaga do certo. Saber quem RECUSAR desde o dia 1 separa operação lucrativa de operação ocupada.
