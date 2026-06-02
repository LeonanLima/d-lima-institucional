import numpy as np
from engine.rigidez import montar_global, matriz_T


def forcas_equivalentes_distribuida(q: float, L: float,
                                    angulo: float) -> np.ndarray:
    """Vetor 6x1 de forcas nodais equivalentes (sistema GLOBAL) para carga
    uniforme q [kN/cm] na direcao -y (para baixo) sobre uma barra.

    Convencao: q positivo aponta para baixo (gravidade).
    Forcas de engastamento perfeito no sistema local:
      fy_i = fy_j = -qL/2 ; Mz_i = -qL^2/12 ; Mz_j = +qL^2/12
    """
    V = q * L / 2.0
    M = q * L * L / 12.0
    f_local = np.array([0.0, -V, -M, 0.0, -V, M])
    T = matriz_T(angulo)
    # f_global = T^T f_local
    return T.T @ f_local
