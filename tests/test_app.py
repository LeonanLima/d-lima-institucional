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
    assert "modelo-contemporaneo.jpg" in html
    assert "modelo-familia.jpg" in html
    assert "modelo-compacto.jpg" in html
    assert "Modelo em breve" not in html  # placeholders substituidos por fotos reais


def test_provasocial_faq(client):
    html = client.get("/").get_data(as_text=True)
    assert "Especialista em engenharia de custos" in html
    assert 'id="faq"' in html
    # placeholders de programacao nao podem aparecer para o visitante
    for ph in ("[FAIXA_PRECO]", "[PRAZO_MEDIO]", "[GARANTIA]", "[AREA_ATENDIMENTO]"):
        assert ph not in html


def test_cta_footer(client):
    html = client.get("/").get_data(as_text=True)
    assert "leonan.dlima" in html                 # instagram
    assert "politica-privacidade" in html         # link footer
    assert 'id="whatsapp-float"' in html


def test_css_no_cdn(client):
    html = client.get("/").get_data(as_text=True)
    assert "/static/styles.css" in html
    assert "cdn.tailwindcss.com" not in html      # sem CDN de CSS


def test_privacidade(client):
    r = client.get("/politica-privacidade")
    assert r.status_code == 200
    assert "Privacidade" in r.get_data(as_text=True)
