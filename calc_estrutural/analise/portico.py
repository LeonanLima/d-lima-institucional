# analise/portico.py - Portico Espacial: Metodo da Rigidez Direta
#
# REFERENCIAS:
#   MCGUIRE, W.; GALLAGHER, R.H.; ZIEMIAN, R.D. Matrix Structural Analysis. 2.ed. 2000.
#   BASTOS, P.S.S. (Dr., UNESP) Apostilas de Analise Estrutural, 2017.
#   ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.1. 2014.
#
# DOF por no: [ux, uy, uz, theta_x, theta_y, theta_z] - indices 0..5
# DOF por barra: 12 = 6 no_i (0..5) + 6 no_j (6..11)
import numpy as np
import math
from modelo import Estrutura, Barra, No


def _matriz_rigidez_local(barra: Barra) -> np.ndarray:
    # Matriz 12x12 para elemento de portico espacial 3D (Euler-Bernoulli).
    # Ref: McGuire et al. (2000), equacao 4.20.
    # Forcas locais: [N_i, Vy_i, Vz_i, T_i, My_i, Mz_i, N_j, Vy_j, Vz_j, T_j, My_j, Mz_j]
    s = barra.secao
    L = barra.L * 100.0   # m -> cm
    E = s.E      # [kN/cm2]
    G = s.G
    A = s.A
    Iy = s.Iy
    Iz = s.Iz
    J = s.J

    EA   = E * A   / L
    EIy  = E * Iy  / L
    EIy2 = E * Iy  / L**2
    EIy3 = E * Iy  / L**3
    EIz  = E * Iz  / L
    EIz2 = E * Iz  / L**2
    EIz3 = E * Iz  / L**3
    GJ   = G * J   / L

    k = np.zeros((12, 12))
    # axial
    k[0,0]= EA;   k[0,6]=-EA;   k[6,6]= EA;   k[6,0]=-EA
    # torcao
    k[3,3]= GJ;   k[3,9]=-GJ;   k[9,9]= GJ;   k[9,3]=-GJ
    # flexao XY: v(1), tz(5), v(7), tz(11)
    k[1,1]=12*EIz3;  k[1,5]=6*EIz2;   k[1,7]=-12*EIz3; k[1,11]=6*EIz2
    k[5,1]=6*EIz2;   k[5,5]=4*EIz;    k[5,7]=-6*EIz2;  k[5,11]=2*EIz
    k[7,1]=-12*EIz3; k[7,5]=-6*EIz2;  k[7,7]=12*EIz3;  k[7,11]=-6*EIz2
    k[11,1]=6*EIz2;  k[11,5]=2*EIz;   k[11,7]=-6*EIz2; k[11,11]=4*EIz
    # flexao XZ: w(2), ty(4), w(8), ty(10)
    k[2,2]=12*EIy3;  k[2,4]=-6*EIy2;  k[2,8]=-12*EIy3; k[2,10]=-6*EIy2
    k[4,2]=-6*EIy2;  k[4,4]=4*EIy;    k[4,8]=6*EIy2;   k[4,10]=2*EIy
    k[8,2]=-12*EIy3; k[8,4]=6*EIy2;   k[8,8]=12*EIy3;  k[8,10]=6*EIy2
    k[10,2]=-6*EIy2; k[10,4]=2*EIy;   k[10,8]=6*EIy2;  k[10,10]=4*EIy
    return k


def _matriz_transformacao(barra: Barra) -> np.ndarray:
    # Matriz de transformacao 12x12 do sistema local para global.
    # Ref: McGuire et al. (2000), secao 4.4.
    #
    # Convencao de eixos locais:
    #   x_local: direcao no_i -> no_j
    #   y_local: perpendicular a x_local e ao eixo Z global
    #   z_local: regra da mao direita (x x y)
    ex = np.array(barra.vetor_eixo)

    # Vetor auxiliar para montar o plano local
    if abs(ex[0]) < 1e-10 and abs(ex[1]) < 1e-10:
        aux = np.array([1.0, 0.0, 0.0])   # barra vertical: usar X global
    else:
        aux = np.array([0.0, 0.0, 1.0])   # demais: usar Z global

    ez = np.cross(ex, aux)
    ez = ez / np.linalg.norm(ez)
    ey = np.cross(ez, ex)
    ey = ey / np.linalg.norm(ey)

    lam = np.array([ex, ey, ez])   # matriz de rotacao 3x3

    T = np.zeros((12, 12))
    for i in range(4):
        T[3*i:3*i+3, 3*i:3*i+3] = lam
    return T


def _carga_distribuida_nos(barra: Barra) -> np.ndarray:
    # Forcas equivalentes nos nos para carga distribuida uniforme.
    # q_distribuida: lista de (q_kNm, fracInicio, fracFim) no eixo local y.
    # Retorna vetor local de 12 componentes.
    f = np.zeros(12)
    for (q_kNm, _ini, _fim) in barra.q_distribuida:
        q = q_kNm / 100.0     # kN/m -> kN/cm
        L = barra.L * 100.0   # m -> cm
        # Engastamento perfeito em y (Fy e Mz nos dois nos)
        f[1]  += q * L / 2
        f[5]  += q * L**2 / 12
        f[7]  += q * L / 2
        f[11] -= q * L**2 / 12
    return f


def analisar(estrutura: Estrutura) -> dict:
    # Analise elastica linear do portico espacial.
    # Ref: McGuire et al. (2000), Cap. 4-5.
    #
    # Retorna:
    #   deslocamentos: {no_id: {ux,uy,uz,tx,ty,tz}} em [cm] e [mrad]
    #   esforcos:      {barra_id: {N_i,Vy_i,...,Mz_j}} em [kN] e [kNm]
    nos = estrutura.nos
    barras = estrutura.barras
    n_dof = len(nos) * 6

    mapa_no = {n.id: i for i, n in enumerate(nos)}

    # Vetor de cargas nodais
    F = np.zeros(n_dof)
    for no in nos:
        b = mapa_no[no.id] * 6
        for j, f in enumerate(no.cargas):
            F[b + j] = f

    # Montar rigidez global K e cargas equivalentes
    K = np.zeros((n_dof, n_dof))
    F_eq = np.zeros(n_dof)

    for barra in barras:
        k_loc = _matriz_rigidez_local(barra)
        T = _matriz_transformacao(barra)
        k_glob = T.T @ k_loc @ T

        ii = mapa_no[barra.no_i.id] * 6
        jj = mapa_no[barra.no_j.id] * 6
        idx = list(range(ii, ii+6)) + list(range(jj, jj+6))

        for r in range(12):
            for c in range(12):
                K[idx[r], idx[c]] += k_glob[r, c]

        if barra.q_distribuida:
            f_glob = T.T @ _carga_distribuida_nos(barra)
            for r in range(12):
                F_eq[idx[r]] += f_glob[r]

    F = F + F_eq

    # Indices DOF livres e fixos
    livres = []
    fixos = []
    for no in nos:
        b = mapa_no[no.id] * 6
        for j, rest in enumerate(no.restricoes):
            (fixos if rest else livres).append(b + j)

    # Resolver sistema reduzido
    K_ff = K[np.ix_(livres, livres)]
    F_f = F[livres]
    try:
        u_livres = np.linalg.solve(K_ff, F_f)
    except np.linalg.LinAlgError:
        raise ValueError("Rigidez singular - verificar restricoes de apoio")

    u = np.zeros(n_dof)
    for i, d in enumerate(livres):
        u[d] = u_livres[i]

    # Recuperar esforcos por barra
    esforcos = {}
    for barra in barras:
        ii = mapa_no[barra.no_i.id] * 6
        jj = mapa_no[barra.no_j.id] * 6
        idx = list(range(ii, ii+6)) + list(range(jj, jj+6))

        T = _matriz_transformacao(barra)
        k_loc = _matriz_rigidez_local(barra)
        u_local = T @ u[idx]
        f_local = k_loc @ u_local

        if barra.q_distribuida:
            f_local -= _carga_distribuida_nos(barra)

        esforcos[barra.id] = {
            "N_i":  round(f_local[0], 3),
            "Vy_i": round(f_local[1], 3),
            "Vz_i": round(f_local[2], 3),
            "T_i":  round(f_local[3] / 100, 3),
            "My_i": round(f_local[4] / 100, 3),
            "Mz_i": round(f_local[5] / 100, 3),
            "N_j":  round(f_local[6], 3),
            "Vy_j": round(f_local[7], 3),
            "Vz_j": round(f_local[8], 3),
            "T_j":  round(f_local[9] / 100, 3),
            "My_j": round(f_local[10] / 100, 3),
            "Mz_j": round(f_local[11] / 100, 3),
        }

    deslocamentos = {}
    for no in nos:
        b = mapa_no[no.id] * 6
        deslocamentos[no.id] = {
            "ux": round(u[b+0]*100, 4),    # cm
            "uy": round(u[b+1]*100, 4),
            "uz": round(u[b+2]*100, 4),
            "tx": round(u[b+3]*1000, 4),   # mrad
            "ty": round(u[b+4]*1000, 4),
            "tz": round(u[b+5]*1000, 4),
        }

    return {"deslocamentos": deslocamentos, "esforcos": esforcos}


def imprimir_resultados(resultado: dict):
    print("\n" + "="*65)
    print("ANALISE - PORTICO ESPACIAL")
    print("Ref: McGuire, Gallagher e Ziemian (2000)")
    print("="*65)
    print("\nDESLOCAMENTOS:")
    print(f"{'No':>4} {'ux(cm)':>8} {'uy(cm)':>8} {'uz(cm)':>8} "
          f"{'tx(mrad)':>9} {'ty(mrad)':>9} {'tz(mrad)':>9}")
    for nid, d in resultado["deslocamentos"].items():
        print(f"{nid:>4} {d['ux']:>8.4f} {d['uy']:>8.4f} {d['uz']:>8.4f} "
              f"{d['tx']:>9.4f} {d['ty']:>9.4f} {d['tz']:>9.4f}")

    print("\nESFORCOS NAS BARRAS (extremidade no_i):")
    print(f"{'Barra':>6} {'N_i(kN)':>9} {'Vy_i':>8} {'Vz_i':>8} "
          f"{'T_i(kNm)':>9} {'My_i':>8} {'Mz_i':>8}")
    for bid, e in resultado["esforcos"].items():
        print(f"{bid:>6} {e['N_i']:>9.3f} {e['Vy_i']:>8.3f} {e['Vz_i']:>8.3f} "
              f"{e['T_i']:>9.3f} {e['My_i']:>8.3f} {e['Mz_i']:>8.3f}")
    print("="*65)
