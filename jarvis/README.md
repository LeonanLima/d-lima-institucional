# JARVIS de voz (local)

Assistente de voz estilo Homem de Ferro que roda 100% no seu PC. Voce fala,
ele pensa (cerebro = Claude Code CLI) e responde falando, em portugues.

## Como rodar

1. Instale as dependencias (uma vez):

   ```
   pip install -r requirements.txt
   ```

2. Suba o servidor (o cerebro):

   ```
   python backend/app.py
   ```

   Deve mostrar algo como `Running on http://127.0.0.1:8756`.

3. Abra o **Google Chrome** e acesse: `http://127.0.0.1:8756/`
   (a propria pagina e servida pelo servidor, para o microfone funcionar).

4. Clique no reator (o circulo azul) e fale. Permita o uso do microfone quando
   o Chrome pedir.

## Requisitos

- Google Chrome (o reconhecimento de voz usa a Web Speech API dele).
- Internet (o reconhecimento de voz do Chrome roda na nuvem).
- Microfone e alto-falante.
- O comando `claude` disponivel no PATH (Claude Code instalado).

## Como funciona

```
Voce fala -> Chrome transcreve (pt-BR) -> POST /jarvis ->
backend chama `claude -p` -> resposta em texto -> Chrome fala de volta
```

## Limitacoes (v1)

- Push-to-talk: precisa clicar no reator pra falar (sem "Ei JARVIS" sempre ligado).
- So conversa/responde. Executar tarefas de verdade fica pra v2.
- Voz nativa do navegador (nao e voz clonada realista).
- So funciona com o servidor rodando e no seu PC.
