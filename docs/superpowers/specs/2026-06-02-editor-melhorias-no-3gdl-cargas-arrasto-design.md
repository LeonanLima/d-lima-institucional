# Editor — 3-GDL, Cargas Fx/Fy/Mz e Arrastar Nós — Design

> **Status:** aprovado (2026-06-02). Próximo passo: plano de implementação (writing-plans).
> Empilha sobre a branch `feat/integracao-acabamento-estruturas`.

## Problema

O editor define vínculos e cargas nodais por `prompt()` em modos da toolbar
(clica nó → digita "fixo" / "Fy"). Isso limita:

- **Vínculos:** só os 3 presets (engaste/fixo/movel); não dá para montar combinações
  arbitrárias dos 3 GDL (ux/uy/rz) — embora `setVinculo` no modelo já as aceite.
- **Cargas nodais:** só `Fy` é exposto; `Fx` e `Mz` ficam inacessíveis — embora
  `addCargaNodal` já aceite os três.
- **Posição dos nós:** depois de criado, um nó não pode ser movido.

**Objetivo:** expor 3-GDL e Fx/Fy/Mz, permitir arrastar nós, e eliminar os `prompt()`,
movendo a edição para um painel de propriedades por seleção.

## Princípio

Quase tudo é interação/UI. O modelo já suporta o conteúdo; o trabalho é expor na tela.
O editor continua em **metros** (x,y) e **kN / kN·m** (cargas); nenhuma conversão de unidade.

## Componentes

### 1. `editor-modelo.js` — funções puras (testáveis em `node --test`)

- `moverNo(m, no, x, y)` — reposiciona um nó **existente** aplicando `snap`. Retorna o nó.
- `setVinculo(m, no, {ux,uy,rz})` — passa a ter **upsert + remoção**: se `ux=uy=rz=false`,
  remove o vínculo do nó e retorna `null`; senão atualiza/insere e retorna o vínculo.
  (Os presets continuam não-all-false, então os testes atuais seguem válidos.)
- `setCargaNodal(m, no, {fx,fy,mz})` — **um carregamento nodal por nó**: localiza a carga
  nodal existente do nó e atualiza no lugar; se `fx=fy=mz=0`, remove; senão cria. Retorna a
  carga ou `null`. (Substitui o uso de `addCargaNodal`, que empilha duplicatas — inadequado
  para campos editáveis. `addCargaNodal` permanece exportada para compatibilidade/round-trip,
  mas o controlador passa a usar `setCargaNodal`.)

> Leitura para o painel: o controlador deriva o estado atual de um nó com
> `m.vinculos.find(v => v.no === id)` e `m.cargas.find(c => c.tipo === "nodal" && c.no === id)`
> — não precisa de getters novos.

### 2. `editor-ui.js` — painel por seleção

`renderPainel` distingue o tipo do selecionado:
- **Barra** (`selecionado.secao`): mantém Tipo + bw + h, e **ganha** o campo
  **Carga distribuída (kN/m)** (move o último fluxo de prompt para cá).
- **Nó** (`selecionado.x !== undefined`): novo bloco "Nó N" com
  - **Coordenadas:** campos `x` / `y` (m);
  - **Vínculo (apoio):** checkboxes `ux` / `uy` / `rz`;
  - **Cargas nodais:** campos `Fx` / `Fy` / `Mz`.

Novos callbacks consumidos pelo painel: `aoEditarNo({x?,y?})`,
`aoSetVinculo({ux,uy,rz})`, `aoSetCargaNodal({fx?,fy?,mz?})`,
`aoSetCargaDistribuida(valor)`.

### 3. `editor-canvas.js` — destaque do nó selecionado

`render` desenha o nó selecionado destacado (raio maior + cor de seleção `#dc2626`),
espelhando o destaque que as barras já têm via `estado.selecionado`.

### 4. `editor.js` — toolbar enxuta, seleção de nó e arrasto

- **Toolbar:** remove os modos **Vínculo** e **Carga**. Fica: `Selecionar · Nó · Barra · Apagar`.
  (Edição de `templates/editor.html` para tirar os dois botões.)
- **Seleção:** no modo Selecionar, clique em nó **ou** barra seleciona (define
  `estado.selecionado`) e o painel renderiza as propriedades correspondentes.
- **Arrastar nós (modo Selecionar):** máquina de estados com eventos de ponteiro:
  - `mousedown` sobre um nó → registra candidato a arrasto (nó + posição inicial), `arrastando=false`.
  - `mousemove` → se o movimento passar de um limiar (~3 px) e houver candidato, `arrastando=true`,
    `moverNo` para a posição do cursor (com snap), `redesenhar` ao vivo.
  - `mouseup` → se `arrastando`, finaliza e **invalida o resultado**; senão (sem movimento)
    trata como seleção do nó. Um flag suprime o `click` seguinte quando houve arrasto real.
- Os modos `no` / `barra` / `apagar` continuam no handler de `click` como hoje.
- Mover nó ou editar vínculo/carga **invalida** o resultado calculado (overlay/painel de
  resultados somem), reusando `invalidarResultado()`.

## Testes

| O quê | Como |
|---|---|
| `moverNo` aplica snap e altera o nó no lugar | `node --test` |
| `setVinculo` com all-false remove o vínculo; com GDL parcial faz upsert | `node --test` |
| `setCargaNodal` upsert (um por nó) e remove quando tudo zero | `node --test` |
| Painel do nó (checkboxes/campos), arrasto, destaque | verificação visual (Playwright + Chrome) |
| Suítes existentes seguem verdes | `pytest` + `npm test` |

## Fora de escopo (YAGNI)

- Multi-seleção, desfazer/refazer, arrastar barras inteiras, vínculo inclinado, snap configurável.
