import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.modelo import Estrutura


ENTRADA = {
    "estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [
            {"id": 1, "x": 0.0, "y": 0.0, "z": 0.0},
            {"id": 2, "x": 3.0, "y": 0.0, "z": 0.0}
        ],
        "elementos": [
            {"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
             "secao": {"bw": 14, "h": 40}}
        ],
        "vinculos": [
            {"no": 1, "ux": True, "uy": True, "uz": True,
             "rx": True, "ry": True, "rz": True}
        ],
        "cargas": [
            {"elemento": "V1", "tipo": "distribuida", "valor": 10.0,
             "direcao": "y", "unidade": "kN/m"}
        ]
    }
}


def test_parse_nos_converte_metros_para_cm():
    e = Estrutura.from_json(ENTRADA)
    assert e.nos[2].x == 300.0  # 3 m -> 300 cm
    assert e.nos[1].x == 0.0


def test_parse_elemento_comprimento_cm():
    e = Estrutura.from_json(ENTRADA)
    el = e.elementos[0]
    assert el.id == "V1"
    assert abs(el.comprimento() - 300.0) < 1e-6


def test_parse_carga_distribuida_convertida_kN_cm():
    e = Estrutura.from_json(ENTRADA)
    # 10 kN/m = 0,10 kN/cm
    assert abs(e.cargas[0].valor - 0.10) < 1e-9


def test_material_acessivel():
    e = Estrutura.from_json(ENTRADA)
    assert abs(e.material.Ecs - 2898.0) < 1.0


def test_cobrimento_caa2_viga():
    e = Estrutura.from_json(ENTRADA)
    # CAA II, viga -> cobrimento 3,0 cm
    assert e.elementos[0].cobrimento(caa=2) == 3.0
