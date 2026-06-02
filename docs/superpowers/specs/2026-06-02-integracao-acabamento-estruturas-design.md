# Integração e Acabamento do App de Estruturas — Design

> **Status:** aprovado (2026-06-02). Próximo passo: plano de implementação (writing-plans).

## Problema

O motor de análise (Fase 1) e o editor de pórtico plano (Fase 2) estão completos e
mergeados, mas:

1. A rota `GET /estrutura/editor` é **órfã** — não há link para ela em nenhuma página.
   A home `/` é a landing comercial do MCMV; a `/referencia` é a PWA de referência técnica.
2. Ao "Calcular", o editor descarta o `resultado` que **já vem na resposta** de
   `POST /api/estrutura` (reações, deslocamentos, avisos, elementos) e apenas abre o
   relatório completo em uma nova aba. O usuário não vê nada no próprio editor.

**Objetivo:** tornar o app de estruturas descobrível e fechar o ciclo
desenhar → calcular → ver resultado **sem sair do editor**, reaproveitando o que já existe.

## Contrato existente (não muda)

`POST /api/estrutura` já retorna:

```json
{
  "id": "ab12cd34",
  "status": "ok",
  "resultado": {
    "reacoes":        { "<id_no>": { "fx": 0.0, "fy": 25.0, "mz": 0.0 }, ... },
    "deslocamentos":  { "<id_no>": { "ux": ..., "uy": ..., "rz": ... }, ... },
    "avisos":         [ "..." ],
    "elementos":      { "<id_el>": { ... sem chaves svg* ... } }
  }
}
```

As reações são keyed por **id do nó** (string) — basta cruzar com `m.nos` para posicioná-las
no canvas. A API e o motor **não mudam**.

## Componentes

### 1. Hub de Estruturas — `GET /estrutura`

Nova rota no blueprint `estrutura_bp` + `templates/estrutura.html`. Página simples no mesmo
padrão visual (header `#0056b3` com `🏗`), com dois cartões:

- **Editor de Estrutura** → `/estrutura/editor`
- **Referência Técnica** → `/referencia`

A landing comercial `/` (MCMV) permanece intocada. Crosslinks: o header do editor e o da
referência ganham um link "← Estruturas" para `/estrutura`.

> *Alternativa descartada:* adicionar links de engenharia na home `/` — mistura o comercial
> com a ferramenta técnica.

### 2. Resultados inline no editor (peça principal)

Ao "Calcular" (sucesso), o editor passa a consumir `data.resultado` em vez de descartá-lo:

- **Módulo puro `static/editor/editor-resultados.js`** (testável em `node --test`):
  funções que formatam o `resultado` para exibição — lista de reações por nó
  (texto tipo `↑ 25,0 kN`), deslocamento máximo (nó + valor em mm), e os avisos.
  Sem DOM, sem dependência do canvas. É a unidade isolável e testada desta frente.
- **Overlay no canvas** (`editor-canvas.js`): função `desenharResultados(svg, m, resultado)`
  que desenha o valor da reação ao lado de cada nó apoiado. Render manual (verificação no
  navegador), seguindo o padrão das funções de render existentes.
- **Painel de resultados** (`editor-ui.js` + `editor.js`): após calcular, um bloco no painel
  direito mostra reações, deslocamento máximo e avisos, com o botão
  **"Ver relatório completo →"** que abre `/api/relatorio/<id>` em nova aba (mantém o detalhe a
  um clique). Recalcular ou editar o modelo limpa o overlay/painel de resultados.

> Quase tudo frontend. Estado novo no controlador: `estado.resultado` (último resultado) e
> `estado.relatorioId`. Editar o modelo zera `estado.resultado` para não exibir resultado obsoleto.

### 3. Acabamento

- Header do editor (`templates/editor.html`) ganha o link "← Estruturas".
- Títulos/ícones consistentes com as demais páginas.

## Testes

| O quê | Como |
|---|---|
| Rota `GET /estrutura` responde 200 e contém os 2 links | pytest (`tests/test_estrutura_hub.py`) |
| `editor-resultados.js` formata reações/deslocamento/avisos | `node --test` |
| Overlay no canvas + painel de resultados | verificação manual no navegador |
| Suítes existentes continuam verdes | `pytest tests/` (65) + `npm test` (12) |

## Fora de escopo (YAGNI)

- Editar coordenadas de nó por campo / arrastar nós.
- Pilares e lajes no motor e no editor.
- PWA/manifest para o editor.

Cada item acima é uma frente futura própria, com spec → plano dedicados.
