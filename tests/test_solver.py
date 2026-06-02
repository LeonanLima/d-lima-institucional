import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.solver import forcas_equivalentes_distribuida, resolver
from engine.modelo import Estrutura


def test_forcas_equivalentes_carga_para_baixo():
    # q = 0,10 kN/cm para baixo, L = 500 cm, barra horizontal (angulo 0)
    # Reacoes de engaste: V = qL/2 = 25 kN; M = qL^2/12 = 2083,33 kN.cm
    f = forcas_equivalentes_distribuida(q=0.10, L=500.0, angulo=0.0)
    assert abs(f[1] - (-25.0)) < 0.01   # fy no no i
    assert abs(f[4] - (-25.0)) < 0.01   # fy no no j
    assert abs(f[2] - (-2083.333)) < 0.1  # Mz no no i
    assert abs(f[5] - (2083.333)) < 0.1   # Mz no no j


def test_forcas_equivalentes_soma_vertical():
    f = forcas_equivalentes_distribuida(q=0.10, L=500.0, angulo=0.0)
    # soma das forcas verticais = -qL = -50 kN
    assert abs((f[1] + f[4]) - (-50.0)) < 0.01


def _estrutura_cantilever():
    # Engaste no no 1, carga P=10 kN para baixo no no 2 (ponta livre)
    # Barra horizontal L=300cm, secao 14x40, fck=25 basalto
    return Estrutura.from_json({"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 3, "y": 0}],
        "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                       "secao": {"bw": 14, "h": 40}}],
        "vinculos": [{"no": 1, "ux": True, "uy": True, "rz": True}],
        "cargas": [{"no": 2, "tipo": "nodal", "fy": -10.0}]}})


def test_cantilever_deslocamento_ponta():
    est = _estrutura_cantilever()
    res = resolver(est)
    # delta = P L^3 / (3 EI); EI = 2898*74666,67; L=300
    # delta = -10*300^3/(3*2898*74666,67) = -0,4159 cm = -4,159 mm
    uy2 = res["deslocamentos"][2]["uy"]   # em mm
    assert abs(uy2 - (-4.159)) < 0.05


def test_cantilever_rotacao_ponta():
    est = _estrutura_cantilever()
    res = resolver(est)
    # theta = P L^2 / (2 EI) = -0,00208 rad
    rz2 = res["deslocamentos"][2]["rz"]
    assert abs(rz2 - (-0.00208)) < 0.0001
