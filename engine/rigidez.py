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


def gdls_do_no(no_id: int, ordem_nos: list) -> list:
    """Retorna os 3 indices de GDL global de um no (2D: ux, uy, rz)."""
    idx = ordem_nos.index(no_id)
    return [3 * idx, 3 * idx + 1, 3 * idx + 2]


def montar_global(estrutura):
    """Monta K_global e o mapa de contribuicoes por celula.

    Retorna (K, gdl_map, contrib):
      K        : np.ndarray (n_gdl x n_gdl)
      gdl_map  : dict no_id -> [gdl_ux, gdl_uy, gdl_rz]
      contrib  : dict (i, j) -> set de ids de elementos que contribuem
    """
    ordem_nos = sorted(estrutura.nos.keys())
    n_gdl = 3 * len(ordem_nos)
    K = np.zeros((n_gdl, n_gdl))
    contrib = {}
    gdl_map = {nid: gdls_do_no(nid, ordem_nos) for nid in ordem_nos}

    E = estrutura.material.Ecs
    for el in estrutura.elementos:
        ke = k_global_elemento(E, el.secao.area, el.secao.inercia,
                               el.comprimento(), el.angulo())
        gdl = gdl_map[el.no_i.id] + gdl_map[el.no_j.id]  # 6 indices
        for a in range(6):
            for b in range(6):
                ia, ib = gdl[a], gdl[b]
                K[ia, ib] += ke[a, b]
                if ke[a, b] != 0.0:
                    contrib.setdefault((ia, ib), set()).add(el.id)
    return K, gdl_map, contrib
