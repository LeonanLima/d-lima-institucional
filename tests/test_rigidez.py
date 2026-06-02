import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.rigidez import k_local, matriz_T


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
