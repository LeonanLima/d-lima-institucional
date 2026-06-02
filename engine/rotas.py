"""Blueprint do motor de analise estrutural (ADR-2).

Isola as rotas do motor do site institucional, mantendo o app.py fino.
"""
import uuid
from flask import Blueprint, request, jsonify, render_template

from engine.modelo import Estrutura
from engine.relatorio import gerar_relatorio
from engine import persistencia

estrutura_bp = Blueprint("estrutura", __name__)


@estrutura_bp.route("/estrutura/editor")
def editor():
    return render_template("editor.html")


@estrutura_bp.route("/api/estrutura", methods=["POST"])
def api_estrutura():
    data = request.get_json(silent=True)
    if not data or "estrutura" not in data:
        return jsonify({"error": 'JSON invalido: falta "estrutura"'}), 400
    try:
        est = Estrutura.from_json(data)
        rel = gerar_relatorio(est)
    except Exception as e:
        return jsonify({"error": "Erro na analise: %s" % str(e)}), 400

    aid = uuid.uuid4().hex[:8]
    persistencia.salvar(aid, rel)

    # serializar reacoes/deslocamentos com chaves string
    resultado = {
        "reacoes": {str(k): v for k, v in rel["reacoes"].items()},
        "deslocamentos": {str(k): v for k, v in rel["deslocamentos"].items()},
        "avisos": rel["avisos"],
        "elementos": {k: {kk: vv for kk, vv in v.items()
                          if not kk.startswith("svg")}
                      for k, v in rel["elementos"].items()},
    }
    return jsonify({"id": aid, "status": "ok", "resultado": resultado})


@estrutura_bp.route("/api/relatorio/<aid>")
def api_relatorio(aid):
    rel = persistencia.carregar(aid)
    if rel is None:
        return jsonify({"error": "Analise nao encontrada"}), 404
    return render_template("relatorio.html", rel=rel)
