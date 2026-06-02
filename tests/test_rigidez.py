import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.rigidez import k_local, matriz_T, montar_global
from engine.modelo import Estrutura


def test_k_local_simetrica():
    k = k_local(E=2898.0, A=560.0, I=74666.67, L=300.0)
    assert np.allclose(k, k.T)


def test_k_local_termo_axial():
    k = k_local(E=2898.0, A=560.0, I=74666.67, L=300.0)
    # EA/L = 2898*560/300 = 5409,6
    assert abs(k[0, 0] - 5409.6) < 0.1
    assert abs(k[0, 3] - (-5409.6)) < 0.1


def test_k_local_termo_flexao():
    k = k_local(E=2898.0, A=560.0, I=74666.67, L=300.0)
    EI = 2898.0 * 74666.67
    # 12EI/L^3
    assert abs(k[1, 1] - 12 * EI / 300 ** 3) < 1.0
    # 4EI/L
    assert abs(k[2, 2] - 4 * EI / 300) < 1.0


def test_matriz_T_horizontal_identidade():
    # angulo 0 -> T = identidade
    T = matriz_T(0.0)
    assert np.allclose(T, np.eye(6))


def test_matriz_T_vertical():
    import math
    T = matriz_T(math.pi / 2)  # 90 graus
    # cos90=0, sin90=1
    assert abs(T[0, 0] - 0.0) < 1e-9
    assert abs(T[0, 1] - 1.0) < 1e-9
    assert abs(T[1, 0] - (-1.0)) < 1e-9


def test_montar_global_dimensao():
    # 2 nos, 3 GDL/no -> K 6x6
    entrada = {"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 3, "y": 0}],
        "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                       "secao": {"bw": 14, "h": 40}}],
        "vinculos": [], "cargas": []}}
    est = Estrutura.from_json(entrada)
    K, gdl_map, contrib = montar_global(est)
    assert K.shape == (6, 6)
    assert np.allclose(K, K.T)


def test_montar_global_mapa_contribuicoes():
    entrada = {"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 3, "y": 0},
                {"id": 3, "x": 3, "y": 3}],
        "elementos": [
            {"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
             "secao": {"bw": 14, "h": 40}},
            {"id": "P1", "tipo": "pilar", "no_i": 2, "no_j": 3,
             "secao": {"bw": 19, "h": 19}}],
        "vinculos": [], "cargas": []}}
    est = Estrutura.from_json(entrada)
    K, gdl_map, contrib = montar_global(est)
    # No 2 (GDL 3,4,5) recebe contribuicao de V1 e P1
    assert "V1" in contrib[(3, 3)]
    assert "P1" in contrib[(3, 3)]
    # No 1 (GDL 0,1,2) so de V1
    assert contrib[(0, 0)] == {"V1"}
