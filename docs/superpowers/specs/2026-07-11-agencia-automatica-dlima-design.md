# Agência de Marketing Automática — D'LIMA

**Data:** 2026-07-11
**Status:** Design aprovado (aguardando revisão do spec)
**Autor:** Leonan + Claude

## 1. Objetivo

Construir um **motor interno de marketing automático** para as marcas do Leonan
(começando pela D'LIMA Engenharia/Construtora/Incorporadora). O sistema pesquisa,
cria, desenha, mede e aprende sozinho. O **único ponto manual** é a aprovação do
Leonan numa fila no Notion antes de qualquer publicação.

Não é um SaaS multi-cliente. É uma ferramenta pessoal para as marcas próprias.

## 2. Decisões travadas

| Decisão | Escolha |
|---|---|
| Alvo | Marcas próprias (D'LIMA primeiro) |
| Execução | Humano no meio — Leonan aprova antes de publicar |
| Identidade | D'LIMA existente (skill `dlima-brand`) + **logo nova** a ser criada |
| Painel de aprovação | Notion (calendário editorial + fila) |
| Publicação | Metricool (agendamento nas redes) |
| Design das peças | **Claude Design** (Artifacts / HTML+SVG), sem Canva |
| Implementação | Caminho A — subagentes/skills + orquestração leve em Python |
| Tráfego pago (ads) | **Fase 2** — fora do MVP |

## 3. Arquitetura

```
ORQUESTRADOR (Diretor da Agência)
  ├─ Squad MARCA      → brand-designer, brand-voice, brand-guardian
  ├─ Squad CONTEÚDO   → estrategista, pesquisador, copywriter, roteirista-video
  ├─ Squad DESIGN     → designer-post, designer-thumb   (Claude Design)
  └─ Squad DADOS      → analista
        ↓ peças prontas
   NOTION (fila "Aguardando aprovação") ← LEONAN aprova
        ↓ aprovado
   PUBLICAÇÃO (Metricool) → MÉTRICAS → aprendizado volta ao Orquestrador

(Squad TRÁFEGO/ads = Fase 2)
```

### 3.1 Orquestrador
Dispara o ciclo (agendado via `schedule`/cron), distribui trabalho aos squads,
mantém estado do ciclo e injeta o aprendizado do ciclo anterior. Um script Python
fino + prompt de coordenação; não decide arte nem copy, só coordena.

### 3.2 Squad MARCA *(roda no setup; revisita trimestralmente)*
- **brand-designer** — cria a **logo nova** (deve comunicar construtora +
  incorporadora + engenheiro civil), variações (horizontal, símbolo, monocromática)
  e aplicação da paleta. Saída como Artifact (SVG/HTML) exportável.
- **brand-voice** — consolida tom de voz, arquétipo (Irmão Mais Velho + Professor),
  lista do/don't. Base já existente na skill `dlima-brand`.
- **brand-guardian** — valida toda peça contra o guia de marca antes de ir ao Notion.

### 3.3 Squad CONTEÚDO
- **estrategista** — define 5–7 pautas do ciclo a partir de metas, sazonalidade e
  temas que a obra/engenharia rendem (MCMV, financiamento, bastidor de obra).
- **pesquisador** — tendências, concorrentes, dúvidas reais do público.
- **copywriter** — legendas, roteiros de Reels, carrosséis (frameworks de copy da
  skill `dlima-brand`).
- **roteirista-video** — roteiros de vídeo (geração de vídeo opcional, fase posterior).

### 3.4 Squad DESIGN *(Claude Design)*
- **designer-post** — arte de carrossel/feed/story a partir do copy, como Artifact
  (HTML+SVG na paleta D'LIMA), exportável para imagem.
- **designer-thumb** — capas de Reels/YouTube.

### 3.5 Squad DADOS
- **analista** — puxa métricas do Metricool, monta relatório semanal, aponta o que
  repetir/cortar. Alimenta o próximo ciclo do Orquestrador.

## 4. Fluxo de um ciclo

1. Orquestrador dispara o ciclo (agendado).
2. estrategista + pesquisador definem 5–7 pautas.
3. copywriter escreve → brand-guardian valida → designer gera arte (Artifact).
4. Cada peça vira um card no Notion (preview + arte + legenda + data sugerida) na
   coluna **"Aguardando aprovação"**.
5. Leonan aprova (arrasta p/ "Aprovado") ou comenta ajuste (volta ao copywriter).
6. Publicação agenda no Metricool na data sugerida.
7. analista mede depois e devolve aprendizado ao Orquestrador.

## 5. Componentes técnicos (Caminho A)

- **Subagentes/skills** — cada papel acima é um subagente do Claude Code (ou skill),
  com prompt e responsabilidade única.
- **Cola Python fina** — scripts que integram os MCPs já ligados: Notion (fila),
  Metricool (publicação/métricas). Sem framework pesado.
- **Agendamento** — `schedule`/cron dispara o Orquestrador.
- **Estado** — banco simples (o próprio Notion como fonte da verdade da fila +
  um JSON/DB local para memória de aprendizado entre ciclos).

## 6. Estrutura de dados no Notion

Uma database "Conteúdo D'LIMA" com propriedades:
`Título`, `Pauta`, `Formato` (Reel/Carrossel/Story/Feed), `Legenda`,
`Arte` (anexo), `Data sugerida`, `Status` (Ideação → Aguardando aprovação →
Aprovado → Agendado → Publicado → Medido), `Métricas`, `Aprendizado`.

## 7. Tratamento de erros

- Falha de MCP (Notion/Metricool fora): Orquestrador registra e re-tenta no próximo
  tick; nunca publica sem passar pela coluna "Aprovado".
- brand-guardian reprova: peça volta ao copywriter/designer com o motivo, não sobe
  ao Notion.
- Nenhuma publicação ocorre sem card em "Aprovado" — trava de segurança dura.

## 8. Fora de escopo (MVP)

- Tráfego pago / ads (Fase 2).
- Multi-cliente / SaaS.
- Geração de vídeo automática (fica opcional, posterior).
- Resposta automática a comentários/DMs.

## 9. Ordem de construção sugerida

1. **Fatia 0** — Logo nova + guia de marca aplicado (Squad MARCA).
2. **Fatia 1** — Database Notion + fila de aprovação funcionando.
3. **Fatia 2** — Squad CONTEÚDO gerando pautas + copy → cai no Notion.
4. **Fatia 3** — Squad DESIGN gerando artes (Claude Design) anexadas ao card.
5. **Fatia 4** — Publicação Metricool após aprovação.
6. **Fatia 5** — Squad DADOS + loop de aprendizado + Orquestrador agendado.
7. **Fase 2** — Squad TRÁFEGO (ads).
