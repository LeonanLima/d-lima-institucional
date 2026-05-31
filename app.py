# app.py
from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
from flask_cors import CORS
import os, tempfile

app = Flask(__name__)
CORS(app, origins=[
    "https://app.dlima.eng.br",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

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
        import ezdxf
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from io import BytesIO

        try:
            doc = ezdxf.readfile(tmp_path)
        except ezdxf.DXFError as e:
            msg = str(e)
            if 'version' in msg.lower() or 'AC1' in msg:
                return jsonify({
                    'error': 'Formato DWG muito antigo (anterior a R2004). '
                             'Abra no AutoCAD/LibreCAD e salve como DXF.'
                }), 400
            return jsonify({'error': f'Erro ao ler arquivo: {msg}'}), 400

        fig = plt.figure(figsize=(20, 20), facecolor='white')
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor('white')

        ctx_render = RenderContext(doc)
        backend = MatplotlibBackend(ax)
        Frontend(ctx_render, backend).draw_layout(doc.modelspace())

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)

        return send_file(buf, mimetype='image/png',
                         download_name='drawing.png',
                         as_attachment=False)

    except Exception as e:
        return jsonify({'error': f'Erro inesperado: {str(e)}'}), 500
    finally:
        os.unlink(tmp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
