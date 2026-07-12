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


def _build_prompt(user_text):
    """Monta o prompt com os ultimos turnos para dar contexto."""
    linhas = []
    for turno in _history:
        linhas.append(f"Leonan: {turno['user']}")
        linhas.append(f"JARVIS: {turno['reply']}")
    linhas.append(f"Leonan: {user_text}")
    linhas.append("JARVIS:")
    return "\n".join(linhas)


def _ask_claude(user_text):
    """Chama o claude CLI em modo headless e devolve a resposta em texto."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        return "O cerebro nao esta disponivel: o comando claude nao foi encontrado."

    prompt = _build_prompt(user_text)
    try:
        resultado = subprocess.run(
            [claude_bin, "-p", prompt, "--append-system-prompt", PERSONA],
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

    reply = _ask_claude(user_text)
    _history.append({"user": user_text, "reply": reply})
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8756, debug=False)
