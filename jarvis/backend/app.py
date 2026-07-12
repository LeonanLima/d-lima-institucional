"""JARVIS de voz - backend Flask.

Recebe o texto que o navegador transcreveu, manda pro cerebro (claude CLI)
e devolve a resposta em texto para o navegador falar.
"""
import os
import subprocess
import shutil
from collections import deque

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import skills

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__)
CORS(app)

# Persona do JARVIS. Vira audio, entao: portugues, direto, sem markdown/emoji.
PERSONA = (
    "Voce e o JARVIS, um assistente pessoal de voz do Leonan, no estilo do "
    "assistente do Homem de Ferro. Fale sempre em portugues do Brasil, de forma "
    "educada, elegante e direta. Suas respostas viram audio falado, entao: "
    "nunca use markdown, listas, asteriscos, emojis ou simbolos; escreva como "
    "quem fala em voz alta; seja conciso (1 a 3 frases quando possivel). "
    "Trate o usuario com respeito. Se nao souber algo, diga com naturalidade."
)

# Historico curto em memoria para dar continuidade dentro da sessao.
MAX_TURNS = 6
_history = deque(maxlen=MAX_TURNS)

CLAUDE_TIMEOUT_S = 60
TASK_TIMEOUT_S = 300  # tarefas em projeto podem demorar mais

# Tarefa aguardando confirmacao falada (v3). So executa apos "confirma".
_pending_task = None


def _run_task_in_project(project_dir, task_text):
    """Executa a tarefa dentro da pasta do projeto com poder total (o usuario
    escolheu esse nivel e ja confirmou por voz). Guardrails: so roda apos
    confirmacao E so em pasta da lista branca. Devolve resumo falado."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        return "O cerebro nao esta disponivel."
    prompt = (
        task_text
        + "\n\nAo terminar, responda em 1 ou 2 frases faladas (sem markdown, "
          "sem simbolos) o que voce fez."
    )
    try:
        resultado = subprocess.run(
            [claude_bin, "-p", "--dangerously-skip-permissions"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=TASK_TIMEOUT_S,
            encoding="utf-8",
            cwd=project_dir,
        )
    except subprocess.TimeoutExpired:
        return "A tarefa demorou demais e eu interrompi. Talvez seja grande demais para uma vez."
    except Exception:
        return "Tive um problema ao executar a tarefa."
    if resultado.returncode != 0:
        return "Tentei executar, mas deu erro. Melhor conferir no computador."
    reply = (resultado.stdout or "").strip()
    return reply or "Feito."


def _build_prompt(user_text):
    """Monta o prompt com os ultimos turnos para dar contexto."""
    linhas = []
    for turno in _history:
        linhas.append(f"Leonan: {turno['user']}")
        linhas.append(f"JARVIS: {turno['reply']}")
    linhas.append(f"Leonan: {user_text}")
    linhas.append("JARVIS:")
    return "\n".join(linhas)


def _ask_claude(user_text, extra_context=None):
    """Chama o claude CLI em modo headless e devolve a resposta em texto.

    extra_context: texto opcional (ex: memoria dos projetos) que fundamenta a
    resposta sem virar parte do historico de conversa.
    """
    claude_bin = shutil.which("claude")
    if not claude_bin:
        return "O cerebro nao esta disponivel: o comando claude nao foi encontrado."

    prompt = _build_prompt(user_text)
    if extra_context:
        prompt = (
            "Use estas anotacoes de projetos do Leonan para responder por voz, "
            "em 1 ou 2 frases, dizendo em que ponto o projeto esta:\n"
            + extra_context + "\n\n" + prompt
        )
    try:
        # Prompt vai pelo stdin (nao como argumento): o Windows tem limite de
        # tamanho de linha de comando e a memoria dos projetos estoura isso.
        resultado = subprocess.run(
            [claude_bin, "-p", "--append-system-prompt", PERSONA],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT_S,
            encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        return "Desculpe, demorei demais para pensar nisso. Pode repetir?"
    except Exception:
        return "Desculpe, tive um problema para processar isso."

    if resultado.returncode != 0:
        return "Desculpe, tive um problema para processar isso."

    reply = (resultado.stdout or "").strip()
    if not reply:
        return "Desculpe, nao consegui formular uma resposta."
    return reply


@app.route("/", methods=["GET"])
def index():
    """Serve a pagina do JARVIS a partir do proprio backend (localhost = contexto
    seguro, necessario para o microfone e o reconhecimento de voz do Chrome)."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/jarvis", methods=["POST"])
def jarvis():
    data = request.get_json(silent=True) or {}
    user_text = (data.get("text") or "").strip()
    if not user_text:
        return jsonify({"reply": "Nao entendi. Pode falar de novo?"})

    global _pending_task
    n = skills._norm(user_text)

    # 0) Ha uma tarefa aguardando confirmacao? So "confirma"/"cancela" contam.
    if _pending_task is not None:
        if skills.is_confirm(n):
            tarefa = _pending_task
            _pending_task = None
            reply = _run_task_in_project(tarefa["dir"], tarefa["task"])
            _history.append({"user": user_text, "reply": reply})
            return jsonify({"reply": reply})
        if skills.is_cancel(n):
            _pending_task = None
            return jsonify({"reply": "Tarefa cancelada."})
        # Qualquer outra coisa mantem a tarefa pendente e reforca o pedido.
        return jsonify({"reply": "Tenho uma tarefa aguardando. Diga confirma para executar, ou cancela."})

    # 1) Habilidade direta e segura (abrir, anotar, hora/data/calculo).
    direct = skills.handle(user_text)
    if direct is not None:
        _history.append({"user": user_text, "reply": direct})
        return jsonify({"reply": direct})

    # 2) Pergunta sobre STATUS de projetos (read-only): fundamenta o cerebro.
    contexto = skills.project_context(user_text, n)
    if contexto is not None:
        reply = _ask_claude(user_text, extra_context=contexto)
        _history.append({"user": user_text, "reply": reply})
        return jsonify({"reply": reply})

    # 3) Comando de EXECUCAO em projeto: exige confirmacao falada antes de rodar.
    alvo = skills.match_project(n)
    if alvo is not None:
        nome, pasta = alvo
        _pending_task = {"project": nome, "dir": pasta, "task": user_text}
        return jsonify({"reply": f"Entendi. Vou executar isso no projeto {nome}. Confirma?"})

    # 4) Conversa/pergunta geral: cerebro (claude).
    reply = _ask_claude(user_text)
    _history.append({"user": user_text, "reply": reply})
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8756, debug=False)
