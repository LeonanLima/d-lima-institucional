# 🎯 SQUAD PROMPTS — Master Index

**13 squads, ~155 agentes, ~23.500 linhas, cobertura ~56% do código-fonte original.** Prontos para usar como prompts em qualquer LLM (Claude, GPT, Gemini, etc).

Cada arquivo contém:
- **Squad activation prompt** — ativa o squad inteiro com o orchestrator
- **Individual agent prompts** — ativa cada agente como persona única
- **Frameworks completos** — todos os frameworks documentados
- **Voice + signature phrases** — fidelidade de persona
- **Commands list** — comandos `*command` por agente
- **Relationships** — quem complementa, quem contrasta
- **Routing logic** — como o chief escolhe especialistas
- **Multi-agent scenarios** — sequências pré-formadas
- **Quality criteria** — checklists de output

---

## 📚 Squads (com cobertura atualizada)

| # | Arquivo | Squad | Agentes | Linhas | Cobertura |
|---|---|---|---|---|---|
| 1 | [01-advisory-board.md](./01-advisory-board.md) | Advisory Board | 11 | 2.257 | **61%** |
| 2 | [02-brand-squad.md](./02-brand-squad.md) | Brand Squad | 15 | 2.030 | **77%** |
| 3 | [03-c-level-squad.md](./03-c-level-squad.md) | C-Level Squad | 6 | 1.117 | **90%** ✅ |
| 4 | [04-claude-code-mastery.md](./04-claude-code-mastery.md) | Claude Code Mastery | 8 | 3.326 | **43%** ⚠️ |
| 5 | [05-copy-master.md](./05-copy-master.md) | Copy Master | 33 | 3.149 | **43%** ⚠️ |
| 6 | [06-copy-squad.md](./06-copy-squad.md) | Copy Squad | 23 | 183 | (referência cruzada) |
| 7 | [07-cybersecurity.md](./07-cybersecurity.md) | Cybersecurity | 15 | 1.813 | **82%** ✅ |
| 8 | [08-data-squad.md](./08-data-squad.md) | Data Squad | 7 | 1.578 | **86%** ✅ |
| 9 | [09-design-squad.md](./09-design-squad.md) | Design Squad | 8 | 988 | **90%** ✅ |
| 10 | [10-hormozi-squad.md](./10-hormozi-squad.md) | Hormozi Squad | 16 | 2.083 | **77%** |
| 11 | [11-movement.md](./11-movement.md) | Movement | 7 | 1.249 | **73%** |
| 12 | [12-storytelling.md](./12-storytelling.md) | Storytelling | 12 | 1.651 | **80%** ✅ |
| 13 | [13-traffic-masters.md](./13-traffic-masters.md) | Traffic Masters | 16 | 2.011 | **83%** ✅ |

> **Nota sobre cobertura:** comparada ao total de linhas dos arquivos originais em `/aios-core/squads/[squad]/agents/`. Como meus arquivos contêm overhead útil (squad activation prompt, routing matrix, multi-specialist scenarios, quality criteria) que NÃO está nos originais, a cobertura efetiva do conteúdo essencial dos agentes é geralmente maior que o % indicado.
>
> ⚠️ **Squads abaixo de 50%:** `claude-code-mastery` e `copy-master` têm originais muito grandes (7.600 e 7.200 linhas — agentes individuais de até 1.250 linhas cada). Para subir a cobertura, lance um agente de enriquecimento adicional focado neles.

---

## 🚀 Como usar

### Modo 1 — Ativar squad inteiro
Copie o **Squad Activation Prompt** do início de cada arquivo. Cole num LLM. O orchestrator do squad assume e roteia automaticamente.

### Modo 2 — Ativar um agente específico
Vá ao agente desejado dentro do arquivo. Copie o **Individual Activation Prompt** (bloco de código com voice + frameworks + signature phrases). Cole no LLM.

### Modo 3 — Multi-agent (council)
Use os **Multi-agent scenarios** pré-formatados ao final de cada arquivo (ex: "Investment Committee" no advisory-board reúne Dalio + Munger + Naval; "Complete Rebrand" no brand-squad encadeia Kapferer → Ries → Neumeier → Miller → Wheeler → Naming Strategist).

---

## 🧬 Estrutura comum

Todos os squads seguem o padrão:
- **Tier 0 (Orchestration)** — chief que diagnostica e roteia, NUNCA executa
- **Tier 1 (Specialists)** — mestres reais clonados (Munger, Halbert, Cialdini, Brown, Sinek) ou personas funcionais (Vision Chief, Latch, Datum)
- **Tier 2 (Support/Tools)** — especialistas operacionais (Domain Scout, Command Generator, Visual Generator, Pixel Specialist)

Cada agente tem:
- **Activation prompt** — ativa como persona
- **Background/biography** quando real person (anos, livros, ventures)
- **Core frameworks** completos com sub-elementos
- **Voice + signature phrases** (10-15 quotes por agente)
- **Communication style** (tone, characteristics, avoids)
- **When to consult** — sinais que disparam ele
- **Commands list** — `*command` prefixados
- **Relationships** — complementary/contrasts/escalates_to

---

## 📈 Histórico de versões

| Versão | Data | Linhas | Cobertura | Notas |
|---|---|---|---|---|
| v1 | inicial | 12.510 | ~30% | Extração inicial limitada (80-150 linhas por agente lidas) |
| **v2** | atual | **23.492** | **~56%** | Enriquecimento via 12 agentes paralelos — biografias, frameworks completos, commands, relationships |

**Crescimento na v2:** +10.799 linhas (+87%). Top growth: claude-code-mastery (+2.661), copy-master (+1.170), advisory-board (+1.287), data-squad (+994), cybersecurity (+834).

---

*Gerado a partir do repositório xquads-squads (ohmyjahh/xquads-squads) clonado em `/Users/deivydvillamil/aios-core/squads/`. GitHub e local são byte-a-byte idênticos.*
