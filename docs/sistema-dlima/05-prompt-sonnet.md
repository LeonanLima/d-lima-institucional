# 05 — Prompt pronto para o Sonnet (Prompt A)

Como usar:
1. Criar a pasta e copiar as specs:
   ```powershell
   mkdir C:\Users\leona\dlima-growth\docs
   copy "C:\Users\leona\OneDrive\Documentos\d-lima-institucional\docs\sistema-dlima\*.md" C:\Users\leona\dlima-growth\docs\
   copy "C:\Users\leona\OneDrive\Documentos\d-lima-institucional\docs\estrategia-conteudo-dlima.md" C:\Users\leona\dlima-growth\docs\
   ```
2. Abrir o Claude Code em `C:\Users\leona\dlima-growth` com o modelo Sonnet.
3. Colar o prompt abaixo.

---

```
Você vai implementar o dlima-growth, o sistema de agentes de IA de marketing
da D'LIMA Engenharia. TODAS as decisões de arquitetura já foram tomadas —
não as rediscuta, não proponha stack diferente, não adicione dependência
fora do requirements especificado.

Leia, nesta ordem, antes de escrever qualquer código:
1. docs/02-arquitetura.md  — stack, estrutura de pastas, camadas, regras
2. docs/03-contratos-agentes.md — contratos JSON de cada agente e schema do banco
3. docs/04-plano-fatias.md — as fatias F0 a F8 com critérios de aceite

Regras de execução (obrigatórias):
- git init + primeiro commit já na F0.
- Execute UMA fatia por vez: implementar → pytest verde → commit com a
  mensagem sugerida na fatia → só então seguir para a próxima.
- Se um teste falhar, corrija antes de avançar. Nunca pule a verificação.
- LLM e APIs externas SEMPRE mockados nos testes. Nenhum teste faz rede.
- Prompts dos agentes em growth/prompts/*.md, nunca hardcoded em .py.
- Na F6, embuta no prompt do roteirista o Master Briefing que está em
  docs/estrategia-conteudo-dlima.md (PARTE 3) e as regras de voz descritas
  no 03-contratos-agentes.md.
- Código e comentários em português, nomes de funções descritivos.
- Windows: paths com pathlib, encoding utf-8 explícito ao ler/escrever
  arquivos, nada de comandos unix em scripts.

Comece agora pela fatia F0 e siga em sequência até a F8 sem me perguntar
"posso continuar?". Só pare se: (a) um critério de aceite for impossível de
cumprir como especificado, ou (b) precisar de uma credencial que não está
no .env.example. Ao final de cada fatia, reporte em 2 linhas o que foi
feito e o resultado do pytest.
```

---

## Depois que o Sonnet terminar (checklist do Leonan)

- [ ] Preencher `.env` (copiar de `.env.example`): `LLM_MODE=cli`,
      `YOUTUBE_API_KEY` (criar grátis no Google Cloud Console — opcional),
      token do Metricool (ou `METRICOOL_API=off` para usar o CSV)
- [ ] Rodar manualmente 1ª vez: `python -m growth.pipeline semana`
- [ ] Revisar a `fila/`, aprovar os bons (mudar `status:` para APROVADO)
- [ ] `python -m growth.pipeline publicar` e conferir no Metricool
- [ ] Se a semana 1 for boa: rodar `scripts\agendar-windows.ps1` para
      automatizar toda segunda 07:00
- [ ] Após 4 semanas: voltar ao Fable 5 para especificar a Fase 2 (CKO +
      design de carrossel)
