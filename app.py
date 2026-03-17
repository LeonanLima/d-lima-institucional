import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # O Render exige host 0.0.0.0 e a porta da variável de ambiente
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)