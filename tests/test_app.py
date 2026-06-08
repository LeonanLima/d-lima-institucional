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


def test_seo_and_fonts(client):
    html = client.get("/").get_data(as_text=True)
    assert 'property="og:title"' in html
    assert "GeneralContractor" in html          # Schema.org JSON-LD
    assert "Montserrat" in html                  # Google Fonts
    assert "GA4_ID" in html                      # slot analytics comentado


def test_hero_form(client):
    html = client.get("/").get_data(as_text=True)
    assert 'id="simulacao"' in html
    assert "aluguel" in html.lower()
    assert 'id="leadForm"' in html
    assert "Faixa" in html or "renda" in html.lower()


def test_diferenciais_passos(client):
    html = client.get("/").get_data(as_text=True)
    assert "Burocracia Zero" in html
    assert "Engenheiro Civil" in html
    assert 'id="como-funciona"' in html


def test_subsidios_projetos(client):
    html = client.get("/").get_data(as_text=True)
    assert "Faixa" in html and "FGTS" in html
    assert 'id="projetos"' in html
