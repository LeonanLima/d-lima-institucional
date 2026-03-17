import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    # O Flask busca automaticamente na pasta 'templates'
    return render_template('index.html')

# Rota para servir o manifesto na raiz
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

# Rota para servir o service worker na raiz
@app.route('/sw.js')
def sw():
    return send_from_directory('static', 'sw.js')

if __name__ == '__main__':
    # Porta configurada para rodar localmente ou em servidores como Render/Heroku
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)