# app.py
from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import os
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

CORS(app, origins=[
    "https://app.dlima.eng.br",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
])

# Motor de analise estrutural — rotas isoladas em blueprint (ADR-2)
from engine.rotas import estrutura_bp
app.register_blueprint(estrutura_bp)


@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Arquivo muito grande. Limite: 50 MB'}), 413


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    renda = request.form.get('renda')
    print(f"Novo Cadastro D'LIMA - MCMV: {nome}, Tel: {telefone}, Renda: {renda}")
    return render_template('index.html', sucesso=True)


@app.route('/referencia')
def referencia():
    return render_template('referencia.html')


@app.route('/api/convert-drawing', methods=['POST'])
def convert_drawing():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    name = file.filename.lower() if file.filename else ''
    if not (name.endswith('.dxf') or name.endswith('.dwg')):
        return jsonify({'error': 'Envie um arquivo .dxf ou .dwg'}), 400

    suffix = os.path.splitext(name)[1]
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    file.save(tmp.name)
    tmp_path = tmp.name
    tmp.close()

    try:
        try:
            doc = ezdxf.readfile(tmp_path)
        except (ezdxf.DXFError, OSError) as e:
            msg = str(e)
            if 'not a DXF file' in msg:
                return jsonify({
                    'error': 'Arquivo DWG não pode ser lido diretamente. '
                             'Salve como DXF no AutoCAD/LibreCAD e tente novamente.'
                }), 400
            if 'version' in msg.lower() or 'AC1' in msg:
                return jsonify({
                    'error': 'Formato DWG muito antigo (anterior a R2004). '
                             'Abra no AutoCAD/LibreCAD e salve como DXF.'
                }), 400
            return jsonify({'error': f'Erro ao ler arquivo: {msg}'}), 400

        fig = plt.figure(figsize=(20, 20), facecolor='white')
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor('white')

        try:
            ctx_render = RenderContext(doc)
            backend = MatplotlibBackend(ax)
            Frontend(ctx_render, backend).draw_layout(doc.modelspace())

            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            buf.seek(0)
        finally:
            plt.close(fig)

        return send_file(buf, mimetype='image/png',
                         download_name='drawing.png',
                         as_attachment=False)

    except Exception as e:
        return jsonify({'error': f'Erro inesperado: {str(e)}'}), 500
    finally:
        os.unlink(tmp_path)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
