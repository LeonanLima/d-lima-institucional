import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sw.js")
def service_worker():
    # Servido na raiz (escopo "/") para desinstalar o SW antigo do site institucional.
    resp = send_from_directory("static", "sw.js", mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.route("/politica-privacidade")
def privacidade():
    return render_template("privacidade.html")


@app.route("/contato")
def contato():
    return render_template("contato.html")


@app.route("/v2")
def v2():
    return render_template("v2.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
