import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_editor_rota_responde_200(client):
    r = client.get('/estrutura/editor')
    assert r.status_code == 200


def test_editor_tem_canvas_e_modulos(client):
    r = client.get('/estrutura/editor')
    html = r.data.decode('utf-8')
    assert 'id="canvas"' in html              # container do canvas
    assert 'editor/editor.js' in html         # import do controlador
    assert 'type="module"' in html            # ES modules
