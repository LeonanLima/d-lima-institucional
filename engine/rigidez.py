import math
import numpy as np


def k_local(E: float, A: float, I: float, L: float) -> np.ndarray:
    """Matriz de rigidez elementar 6x6 de viga-coluna 2D no sistema local.

    GDLs: [ui_x, ui_y, theta_i, uj_x, uj_y, theta_j].
    Unidades: E [kN/cm2], A [cm2], I [cm4], L [cm] -> k em kN/cm e kN/rad.
    """
    EA_L = E * A / L
    EI = E * I
    L2 = L * L
    L3 = L2 * L
    return np.array([
        [EA_L,   0,            0,           -EA_L,  0,            0],
        [0,      12 * EI / L3,  6 * EI / L2,  0,    -12 * EI / L3, 6 * EI / L2],
        [0,      6 * EI / L2,   4 * EI / L,   0,    -6 * EI / L2,  2 * EI / L],
        [-EA_L,  0,            0,            EA_L,   0,            0],
        [0,     -12 * EI / L3, -6 * EI / L2,  0,     12 * EI / L3, -6 * EI / L2],
        [0,      6 * EI / L2,   2 * EI / L,   0,    -6 * EI / L2,  4 * EI / L],
    ], dtype=float)


def matriz_T(angulo: float) -> np.ndarray:
    """Matriz de rotacao 6x6 (local <- global) para um elemento 2D.

    angulo em radianos, medido do eixo x global ao eixo do elemento.
    """
    c = math.cos(angulo)
    s = math.sin(angulo)
    return np.array([
        [c,  s, 0, 0, 0, 0],
        [-s, c, 0, 0, 0, 0],
        [0,  0, 1, 0, 0, 0],
        [0,  0, 0, c,  s, 0],
        [0,  0, 0, -s, c, 0],
        [0,  0, 0, 0,  0, 1],
    ], dtype=float)


def k_global_elemento(E, A, I, L, angulo) -> np.ndarray:
    """Matriz elementar transformada para o sistema global: T^T k_local T."""
    kl = k_local(E, A, I, L)
    T = matriz_T(angulo)
    return T.T @ kl @ T
