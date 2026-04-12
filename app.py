import os
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cadastro', methods=['POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        renda = request.form.get('renda')
        
        print(f"Novo Cadastro D'LIMA - MCMV: {nome}, Tel: {telefone}, Renda: {renda}")
        
        return render_template('index.html', sucesso=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
