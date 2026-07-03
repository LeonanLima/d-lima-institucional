# 01 — Visão e Escopo

## O que é

Sistema de agentes de IA que opera o marketing de conteúdo da D'LIMA
Engenharia de forma quase autônoma: encontra temas em alta, decide a pauta
da semana, escreve roteiros/carrosséis/legendas na voz da marca e agenda a
publicação — com o Leonan aprovando antes de ir ao ar.

**Não é** um site novo, nem uma agência, nem um chatbot. É um **pipeline
semanal de conteúdo** que roda sozinho e entrega trabalho pronto para
aprovar.

## O que a D'LIMA já tem (reusar, não reconstruir)

| Ativo | Estado | Papel no sistema |
|---|---|---|
| Site dlimaengenharia.org (Flask, este repo) | No ar | Destino de tráfego. **Não refazer em Next.js/WordPress** |
| ERP app.dlimaengenharia.org (Supabase) | No ar | Supabase já existente — reusar projeto na Fase 2 se precisar |
| PWA obras.dlimaengenharia.org | No ar | Fora de escopo aqui |
| Skill `dlima-brand` | Pronta | Voz, paleta, arquétipo, frameworks de copy — base dos prompts |
| `docs/estrategia-conteudo-dlima.md` | Pronto | Master briefing de geração de conteúdo (PARTE 3) |
| `docs/agente-meta-business-treinamento.md` | Pronto | Agente comercial WhatsApp — já cobre o "Agente Comercial" da Fase 2 |
| Metricool (conta conectada) | Ativo | Publicação/agendamento + métricas — substitui integração direta com Instagram API |
| Claude (assinatura) + Claude Code | Ativo | Motor LLM do MVP sem custo de API |

## Objetivos do MVP (30 dias)

1. Toda segunda-feira o sistema entrega uma pauta semanal pronta:
   **3 roteiros de vídeo + 5 carrosséis + 2 posts técnicos**, cada um com
   legenda, CTA e hashtags, na voz da D'LIMA.
2. Aprovação em menos de 30 min/semana: Leonan lê a fila, aprova/edita/rejeita.
3. Aprovados são agendados automaticamente no Metricool.
4. Custo mensal adicional: **R$ 0** no modo padrão (roda no PC com a
   assinatura Claude; sem VPS, sem API paga).

## Fora de escopo do MVP (Fase 2+)

- Vídeo com avatar (HeyGen) — Fase 2
- Geração de imagem/carrossel visual (templates com a paleta da marca) — Fase 2
- Chatbot do site / orçamento estimado — Fase 2 (o WhatsApp já cobre parte)
- Agente de investidores — Fase 3
- CKO (cérebro de métricas que realimenta a pauta) — Fase 2, usando
  Metricool analytics
- n8n, VPS, Supabase novo — só quando houver motivo concreto (ver 02-arquitetura)

## Fases

```
Fase 1 (MVP, 30 dias)   Radar → Estrategista → Roteirista → [APROVAÇÃO] → Publicador (Metricool)
Fase 2 (60-90 dias)     + Design (imagens), + CKO (métricas→pauta), + vídeo HeyGen
Fase 3 (90+ dias)       + Chatbot site, + Investidores, migração p/ VPS/API se precisar 24h
```

## Métricas de sucesso do MVP

- 10 conteúdos/semana entregues na fila, 4 semanas seguidas
- ≥ 70% dos conteúdos aprovados sem edição grande
- 100% dos aprovados agendados sem intervenção manual no Metricool
- Tempo do Leonan ≤ 30 min/semana
