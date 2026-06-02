import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.modelo import Estrutura
from engine.relatorio import gerar_relatorio


ENTRADA = {"estrutura": {
    "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
    "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 5, "y": 0}],
    "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                   "secao": {"bw": 14, "h": 40}}],
    "vinculos": [{"no": 1, "ux": True, "uy": True}, {"no": 2, "uy": True}],
    "cargas": [{"elemento": "V1", "tipo": "distribuida", "valor": 10.0}]}}


def test_relatorio_tem_passos():
    rel = gerar_relatorio(Estrutura.from_json(ENTRADA))
    # ao menos os passos-chave presentes
    titulos = [p["titulo"] for p in rel["passos"]]
    assert any("Pre-dimensionamento" in t or "Pré-dimensionamento" in t
               for t in titulos)
    assert any("rea" in t.lower() and "o" in t.lower() for t in titulos)  # reacoes
    assert len(rel["passos"]) >= 12


def test_relatorio_tem_resultados():
    rel = gerar_relatorio(Estrutura.from_json(ENTRADA))
    assert "deslocamentos" in rel
    assert "reacoes" in rel
    assert "matriz_global" in rel  # serializada para o template


def test_relatorio_detalhamento_viga():
    rel = gerar_relatorio(Estrutura.from_json(ENTRADA))
    det = rel["elementos"]["V1"]
    # tem regiao de vao com armadura positiva
    assert "regioes" in det
    assert "meio" in det["regioes"]


def test_relatorio_aviso_flecha():
    # viga muito esbelta para forcar flecha alta
    entrada = {"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 8, "y": 0}],
        "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                       "secao": {"bw": 12, "h": 25}}],
        "vinculos": [{"no": 1, "ux": True, "uy": True}, {"no": 2, "uy": True}],
        "cargas": [{"elemento": "V1", "tipo": "distribuida", "valor": 20.0}]}}
    rel = gerar_relatorio(Estrutura.from_json(entrada))
    assert len(rel["avisos"]) >= 1
