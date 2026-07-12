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

## Habilidades (v2)

Antes de acionar o cerebro de IA, o JARVIS tenta resolver comandos conhecidos
de forma direta e segura:

- **Abrir apps e sites**: "abre o WhatsApp", "abre o YouTube", "abre o Gmail",
  "abre a agenda"... (lista fechada e segura de destinos).
- **Anotacoes e lembretes**: "anota que preciso ligar pro cliente",
  "quais sao meus lembretes", "apaga as anotacoes". Salvo em `data/notes.json`.
- **Status dos projetos**: "onde parei no projeto X", "meus projetos" - ele le a
  memoria dos seus projetos e responde falando em que ponto estao.
- **Hora, data e calculo**: "que horas sao", "que dia e hoje", "quanto e 12
  vezes 8" (entende "vezes", "mais", "menos", "dividido por").

Qualquer outra coisa vira conversa normal com o cerebro (Claude).

## Limitacoes

- Push-to-talk: precisa clicar no reator pra falar (sem "Ei JARVIS" sempre ligado).
- As habilidades sao acoes especificas e limitadas (por seguranca, a voz nao
  executa comandos arbitrarios no PC).
- Voz nativa do navegador (nao e voz clonada realista).
- So funciona com o servidor rodando e no seu PC.
