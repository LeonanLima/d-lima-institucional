import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_hub_responde_200(client):
    r = client.get('/estrutura')
    assert r.status_code == 200


def test_hub_tem_links_editor_e_referencia(client):
    html = client.get('/estrutura').data.decode('utf-8')
    assert '/estrutura/editor' in html
    assert '/referencia' in html
