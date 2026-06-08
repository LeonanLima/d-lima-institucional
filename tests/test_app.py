import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_ok(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "D'LIMA" in r.get_data(as_text=True)


def test_whatsapp_number_present(client):
    html = client.get("/").get_data(as_text=True)
    assert "5528999646592" in html
