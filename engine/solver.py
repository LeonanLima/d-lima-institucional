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


def reacoes(estrutura, resultado):
    """Reacoes nodais nos apoios: {R} = [K]{u} - {F}.

    Retorna dict no_id -> {'fx','fy','mz'} (kN, kNm) apenas para nos com vinculo.
    """
    K = resultado["K"]
    u = resultado["u_global"]
    F = resultado["F"]
    gdl_map = resultado["gdl_map"]
    R_vec = K @ u - F

    nos_apoio = {v.no for v in estrutura.vinculos}
    out = {}
    for nid in nos_apoio:
        g = gdl_map[nid]
        out[nid] = {
            "fx": R_vec[g[0]],
            "fy": R_vec[g[1]],
            "mz": R_vec[g[2]] / 100.0,   # kN.cm -> kNm
        }
    return out


def esforcos_elemento(estrutura, resultado, elem_id, n_pontos=11):
    """Diagramas N(x), V(x), M(x) ao longo de um elemento.

    Retorna {'x': [cm], 'N': [kN], 'V': [kN], 'M': [kNm]}.
    Considera carga distribuida transversal se houver.
    """
    from engine.rigidez import k_local, matriz_T
    el = next(e for e in estrutura.elementos if e.id == elem_id)
    L = el.comprimento()
    E = estrutura.material.Ecs
    kl = k_local(E, el.secao.area, el.secao.inercia, L)
    T = matriz_T(el.angulo())

    gdl_map = resultado["gdl_map"]
    u = resultado["u_global"]
    g = gdl_map[el.no_i.id] + gdl_map[el.no_j.id]
    u_e_global = np.array([u[i] for i in g])
    u_e_local = T @ u_e_global
    f_local = kl @ u_e_local   # forcas internas nos nos (sem carga de vao)

    # carga distribuida transversal sobre o elemento (kN/cm, para baixo)
    q = 0.0
    for c in estrutura.cargas:
        if c.tipo == "distribuida" and c.elemento == elem_id:
            q += c.valor

    # No no i: N_i = -f_local[0]; V_i = -f_local[1] (porem incluimos a parcela
    # de engastamento ja embutida em u). Para o diagrama usamos as forcas
    # internas nodais corrigidas pela carga de vao (metodo da superposicao).
    feq_local = np.array([0.0, -q * L / 2, -q * L * L / 12,
                          0.0, -q * L / 2, q * L * L / 12])
    f_int = f_local - feq_local   # forcas internas reais nos nos

    N_i = -f_int[0]
    V_i = f_int[1]
    M_i = f_int[2]

    xs, Ns, Vs, Ms = [], [], [], []
    for k in range(n_pontos):
        x = L * k / (n_pontos - 1)
        N = N_i
        V = V_i - q * x
        M = M_i + V_i * x - q * x * x / 2.0
        xs.append(x)
        Ns.append(N)
        Vs.append(V)
        Ms.append(M / 100.0)   # kN.cm -> kNm
    return {"x": xs, "N": Ns, "V": Vs, "M": Ms}


def flecha_viga(estrutura, resultado, elem_id, phi=2.5, balanco=False):
    """Flecha imediata (Estadio I, inercia bruta) e diferida de uma viga.

    Aproximacao: usa a flecha maxima da elastica numerica a partir dos
    deslocamentos verticais interpolados nos nos do elemento, e como
    referencia analitica calcula 5qL^4/(384 E Ig) quando ha carga distribuida.
    Retorna {'imediata','diferida','limite'} em mm.
    """
    el = next(e for e in estrutura.elementos if e.id == elem_id)
    L = el.comprimento()
    E = estrutura.material.Ecs
    Ig = el.secao.inercia

    q = sum(c.valor for c in estrutura.cargas
            if c.tipo == "distribuida" and c.elemento == elem_id)

    if q > 0:
        delta_cm = 5 * q * L ** 4 / (384 * E * Ig)
    else:
        # fallback: maior deslocamento vertical nodal do elemento
        g = resultado["gdl_map"]
        u = resultado["u_global"]
        uyi = abs(u[g[el.no_i.id][1]])
        uyj = abs(u[g[el.no_j.id][1]])
        delta_cm = max(uyi, uyj)

    imediata = delta_cm * 10.0          # mm
    diferida = imediata * (1 + phi)
    limite = (L / (125.0 if balanco else 250.0)) * 10.0  # mm
    return {"imediata": imediata, "diferida": diferida, "limite": limite}
