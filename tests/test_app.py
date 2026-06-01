import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_referencia_returns_200(client):
    r = client.get('/referencia')
    assert r.status_code == 200

def test_referencia_contains_search_input(client):
    r = client.get('/referencia')
    assert b'id="search"' in r.data

def test_index_still_works(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b"D'LIMA" in r.data
