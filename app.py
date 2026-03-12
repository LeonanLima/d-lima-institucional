import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # O Flask procura o arquivo dentro da pasta /templates
    return render_template('index.html')

if __name__ == '__main__':
    # A porta é definida automaticamente pelo servidor de hospedagem
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)