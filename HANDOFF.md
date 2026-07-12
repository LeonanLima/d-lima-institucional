# HANDOFF — 2026-07-12 (fim de sessão) — d-lima-institucional (branch feat/agencia-automatica-dlima) + dlima-estrutural (branch master)

## Resumo ultra-curto
Auditoria técnica de cálculo estrutural do `dlima-estrutural` (Lajes →
Vigas → Pilares → Escadas), contra NBR 6118:2023, apostilas Bastos e
curso Estrutural na Real (planilhas Waltner Wagner + 24 vídeos da Trilha
12 transcritos): **100% CONCLUÍDA e corrigida**. Suíte `dlima-estrutural`:
**1012 passed, 2 failed** (pré-existentes, `test_lajes_detalhamento_golden.py`
E5a/E5b, não relacionadas — não mexer).

## Estado atual

### Lajes, Vigas, Pilares — fechados em sessão anterior
- **Vigas**: 2 HIGH corrigidos (fissuração `COEF_ACR`, torção sem mínimo) +
  1 MEDIUM corrigido (teto `he` na torção) + 2 LOW corrigidos + 1 achado de
  rastreabilidade corrigido. Doc: `docs/auditoria-vigas-musso-estrutural-na-real.md`.
- **Lajes**: 2 HIGH corrigidos + 1 MEDIUM implementado do zero (laje maciça
  em balanço, fator γn) + 2 pendentes fechados + 1 achado novo registrado
  não-corrigido (#13, VRd1 sempre usa d_x). Doc:
  `docs/auditoria-lajes-musso-estrutural-na-real.md`.
- **Pilares**: auditoria limpa (0 HIGH). 1 MEDIUM corrigido + 1 LOW
  corrigido + 1 LOW reavaliado como não-bug. Doc:
  `docs/auditoria-pilares-musso-estrutural-na-real.md`.

### Escadas — auditoria CONCLUÍDA e corrigida nesta sessão
Doc: `docs/auditoria-escadas-musso-estrutural-na-real.md` (commits
`c903848`, `d0585a8` em `d-lima-institucional`). 5 achados originais + 1
achado novo (guarda-corpo, surgido ao reconferir contra as aulas).

Reconferência contra 24 vídeos transcritos da Trilha 12 (módulos 85-88,
dimensionamento/análise/cálculo de armaduras/detalhamento/ancoragem —
`faster-whisper` local): **nenhum dos 5 achados foi contraditado**; achado
novo #6 identificado (carga de guarda-corpo não modelada).

Correções aplicadas em `dlima-estrutural` (branch `master`):
- **HIGH corrigido** (`75f4e40`): nenhum dos 3 pipelines de escada (laje
  reta/plissada, viga central espinha/flutuante, degrau em balanço)
  verificava abertura de fissuras (ELS-W) — só flecha. Reaproveitado
  `lajes/els.py`/`vigas/els.py` já validados; adicionado campo
  `classe_agressividade` (default CAA_II) às 3 entradas.
- **MEDIUM corrigido** (`2adb447`): degrau em balanço não verificava
  cortante (VRd1) — adicionado, mesma fórmula NBR 6118:2023 19.4.1 já
  usada em `laje_escada.py`; confirmado que o degrau segue dispensando
  estribo mesmo no caso mais fino (E4), agora com verificação formal.
- **MEDIUM corrigido** (`2adb447`): cobrimento digitado sem checar Tabela
  7.2/CAA — adicionado aviso não bloqueante (mesmo padrão do Blondel) nos
  3 pipelines, comparando contra `COBRIMENTOS_E_FCK_MINIMO[caa]`.
- **Exibição no memorial** (`383bfce`): seções de fissuração wiradas no
  CLI (`cli/escada.py`) e na UI Qt (`ui/paginas/escada.py`) — cobrimento
  e cortante já apareciam automaticamente por já estarem dentro dos
  `ResultadoCalculo` existentes.
- **LOW #3** (torque `mt·L/2` igual nas 3 vinculações assimétricas da viga
  central) — registrado, sem correção (baixo risco de projeto).
- **LOW #5** (sem compatibilização lance/patamar em escadas L/U) — fora de
  escopo já documentado na spec 07.
- **LOW #6 novo** (carga horizontal de guarda-corpo, 1 kN/m a 1,10 m,
  ensinada no curso mas não modelada em nenhum pipeline de escada) —
  lacuna de escopo documentada, sem correção nesta rodada (decisão de
  produto pendente: se o público depende do software pro parapeito
  também, vale um módulo dedicado numa sessão futura).

## Próximos passos
Auditoria original (Lajes→Vigas→Pilares→Escadas) está **100% fechada**.
Nada pendente de correção crítica. Em aberto, sem urgência:
1. Decidir se vale implementar o achado LOW #6 (guarda-corpo) — módulo
   novo, não é gap de conformidade normativa (é ação de uso/NBR 6120, não
   item da 6118), então é decisão de produto, não de auditoria.
2. Perguntar ao Leonan o que vem depois: próximo módulo do
   `dlima-estrutural` (ver `docs/estrutural-na-real-*.md` e
   `docs/musso-vigas-concreto-armado.md` pra ideias de fontes já
   estudadas) ou outra frente (Agência D'LIMA marketing, mestrado da
   Mayara, concurso Perito ES — ver `MEMORY.md`).
3. As transcrições da Trilha 12 (`docs/transcricoes-trilha12-escadas/`,
   26 arquivos, módulos 84-88) são de curso pago de terceiro — **nunca
   fazer push público**; seguem locais/privadas. Não terminei a
   transcrição dos 50 vídeos completos (só os 26 relevantes pra
   dimensionamento/detalhamento/ancoragem foram feitos, por pedido do
   Leonan — módulos 89 (helicoidal, não implementado), 90 (bônus CYPE) e
   91 (aulão) ficaram de fora, e os vídeos de modelagem em software
   SAP2000/FTOOL também foram pulados, sem prejuízo pra auditoria).

## Arquivos-chave
- `docs/auditoria-escadas-musso-estrutural-na-real.md` — auditoria
  completa de escadas, todos os achados corrigidos ou com decisão
  registrada.
- `C:\Users\leona\dlima-estrutural\src\estrutural\core\elementos\escadas\`
  — `laje_escada.py`, `viga_escada.py`, `degrau.py` corrigidos nesta
  sessão (fissuração + cortante + aviso de cobrimento).
- `C:\Users\leona\dlima-estrutural\src\estrutural\cli\escada.py` e
  `ui\paginas\escada.py` — memorial atualizado com as novas seções.
- `docs/transcricoes-trilha12-escadas/` — 26 transcrições (módulos
  84-88), locais/privadas, não commitadas para push público.

## Comandos / verificação
- Rodar suíte do `dlima-estrutural`: `cd C:\Users\leona\dlima-estrutural &&
  rtk proxy python -m pytest tests -q` (⚠️ nunca `pytest` puro — hook rtk
  intercepta e retorna "No tests collected").
- Último resultado: **1012 passed, 2 failed** (pré-existentes, E5a/E5b).

## Armadilhas / decisões
- **`rtk proxy python -m pytest` sempre**, nunca `pytest` puro.
- **`pdftotext -enc UTF-8`** sempre — sem a flag, acentos saem quebrados.
- **Preferência do Leonan (memória `feedback_auditoria_calculo_devagar.md`)**:
  auditoria de cálculo estrutural vai devagar, um módulo por vez, com
  checkpoint humano antes de corrigir HIGH — seguido em Escadas.
- **Nunca inventar número de item de norma ou fórmula sem fonte primária
  confirmada.**
- **Material do curso Estrutural na Real é pago/de terceiro** — nunca
  fazer push público de transcrições, planilhas ou PDFs do curso.
- Sessão ficou cara (~$30+ na parte de auditoria + custo desta sessão de
  correção) — intencional, autorizado pelo Leonan ("corrige tudo").
