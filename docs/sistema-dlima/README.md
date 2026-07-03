# Sistema D'LIMA — Empresa Digital Autônoma (specs de implementação)

Specs completas para implementar o sistema de agentes de IA da D'LIMA
(marketing, conteúdo e comercial) **com o Sonnet**, em fatias pequenas com
commit por fatia.

## Documentos

| Doc | Conteúdo | Quem usa |
|---|---|---|
| [01-visao.md](01-visao.md) | Visão, objetivos, escopo do MVP, fases | Você (decisão) |
| [02-arquitetura.md](02-arquitetura.md) | Stack, estrutura de pastas, decisões e trade-offs | Você + Sonnet |
| [03-contratos-agentes.md](03-contratos-agentes.md) | Contrato de entrada/saída de cada agente (JSON) | Sonnet (implementação) |
| [04-plano-fatias.md](04-plano-fatias.md) | Fatias F0–F8 com critérios de aceite e commits | Sonnet (execução) |
| [05-prompt-sonnet.md](05-prompt-sonnet.md) | Prompt pronto para colar no Sonnet | Você (copiar/colar) |

## Como usar (fluxo de modelo já combinado)

1. **Fable 5** (este trabalho): specs, contratos e plano — feito.
2. **Sonnet**: implementação. Abra o Claude Code no repo novo e cole o
   conteúdo de `05-prompt-sonnet.md`. Ele executa fatia por fatia, com
   verificação e commit após cada uma.
3. **Fable 5 de novo**: quando for especificar módulo novo (Fase 2 — vídeo,
   design, CKO), volte aqui para gerar a spec antes de codar.

## Regra de ouro do projeto

Nenhum conteúdo é publicado sem aprovação humana no MVP. O sistema
**prepara e agenda**; quem aperta o botão final é o Leonan (fila de
aprovação). Automação total só depois que a qualidade estiver comprovada.
