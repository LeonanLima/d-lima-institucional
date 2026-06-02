import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


ENTRADA = {"estrutura": {
    "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
    "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 5, "y": 0}],
    "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                   "secao": {"bw": 14, "h": 40}}],
    "vinculos": [{"no": 1, "ux": True, "uy": True}, {"no": 2, "uy": True}],
    "cargas": [{"elemento": "V1", "tipo": "distribuida", "valor": 10.0}]}}


def test_post_estrutura_retorna_id(client):
    r = client.post('/api/estrutura', json=ENTRADA)
    assert r.status_code == 200
    data = r.get_json()
    assert "id" in data
    assert data["status"] == "ok"


def test_post_estrutura_tem_reacoes(client):
    r = client.post('/api/estrutura', json=ENTRADA)
    data = r.get_json()
    # reacoes presentes e proximas de 25 kN por apoio
    rs = data["resultado"]["reacoes"]
    assert abs(rs["1"]["fy"] - 25.0) < 0.5


def test_post_estrutura_json_invalido(client):
    r = client.post('/api/estrutura', json={"foo": "bar"})
    assert r.status_code == 400


def test_get_relatorio_html(client):
    r = client.post('/api/estrutura', json=ENTRADA)
    aid = r.get_json()["id"]
    r2 = client.get('/api/relatorio/%s' % aid)
    assert r2.status_code == 200
    assert b"<svg" in r2.data  # contem desenho


def test_get_relatorio_inexistente(client):
    r = client.get('/api/relatorio/naoexiste')
    assert r.status_code == 404


def test_index_intocado(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b"D'LIMA" in r.data


# --- ADR-1: estado no filesystem (nao em memoria), seguro entre workers ---

def test_persistencia_roundtrip():
    from engine import persistencia
    rel = {"teste": 123, "avisos": []}
    persistencia.salvar("abc12345", rel)
    assert persistencia.carregar("abc12345") == rel


def test_persistencia_rejeita_id_invalido():
    # path traversal / ids nao-alfanumericos sao bloqueados
    from engine import persistencia
    assert persistencia.carregar("../etc") is None
    assert persistencia.carregar("abc.def") is None
