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


def montar_forcas(estrutura, gdl_map, n_gdl):
    """Vetor global de forcas (kN, kN.cm). Soma cargas nodais e equivalentes
    de cargas distribuidas."""
    F = np.zeros(n_gdl)
    elem_por_id = {el.id: el for el in estrutura.elementos}
    for c in estrutura.cargas:
        if c.tipo == "nodal" and c.no is not None:
            g = gdl_map[c.no]
            F[g[0]] += c.fx
            F[g[1]] += c.fy
            F[g[2]] += c.mz
        elif c.tipo == "distribuida" and c.elemento is not None:
            el = elem_por_id[c.elemento]
            feq = forcas_equivalentes_distribuida(
                c.valor, el.comprimento(), el.angulo())
            g = gdl_map[el.no_i.id] + gdl_map[el.no_j.id]
            for k in range(6):
                F[g[k]] += feq[k]
    return F


def _gdls_restritos(estrutura, gdl_map):
    """Lista de indices de GDL global restritos pelos vinculos (2D: ux,uy,rz)."""
    restr = []
    for v in estrutura.vinculos:
        g = gdl_map[v.no]
        if v.ux:
            restr.append(g[0])
        if v.uy:
            restr.append(g[1])
        if v.rz:
            restr.append(g[2])
    return sorted(set(restr))


def resolver(estrutura):
    """Resolve [K]{u}={F} aplicando condicoes de contorno.

    Retorna dict com 'deslocamentos' (por no, em mm e rad),
    'K', 'F', 'u_global', 'gdl_map', 'contrib', 'ordem_nos'.
    """
    K, gdl_map, contrib = montar_global(estrutura)
    n_gdl = K.shape[0]
    F = montar_forcas(estrutura, gdl_map, n_gdl)

    restritos = _gdls_restritos(estrutura, gdl_map)
    livres = [i for i in range(n_gdl) if i not in restritos]

    K_ff = K[np.ix_(livres, livres)]
    F_f = F[livres]
    u = np.zeros(n_gdl)
    if livres:
        u_f = np.linalg.solve(K_ff, F_f)
        for idx, gl in enumerate(livres):
            u[gl] = u_f[idx]

    ordem_nos = sorted(estrutura.nos.keys())
    desloc = {}
    for nid in ordem_nos:
        g = gdl_map[nid]
        desloc[nid] = {
            "ux": u[g[0]] * 10.0,   # cm -> mm
            "uy": u[g[1]] * 10.0,
            "rz": u[g[2]],          # rad
        }

    return {"deslocamentos": desloc, "K": K, "F": F, "u_global": u,
            "gdl_map": gdl_map, "contrib": contrib, "ordem_nos": ordem_nos,
            "restritos": restritos}
