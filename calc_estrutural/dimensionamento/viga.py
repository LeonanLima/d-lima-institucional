# dimensionamento/viga.py - Dimensionamento de Vigas
#
# REFERENCIAS:
#   [1] CARINI, M.R. (MSc, UFSC) Slide 3 - Vigas, 2023
#   [2] BASTOS, P.S.S. (Dr., UNESP) Cortante e Flexao em Vigas. 2017
#   [3] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2. 2014
#   [4] NBR 6118:2023, secoes 14, 17.2, 17.3, 17.4, 18.3
import math

BIBLIOGRAFIA_VIGA = (
    "VIGA - Referencias:\n"
    "  [1] CARINI, M.R. (MSc, UFSC) Vigas - Estrutural na Real, 2023\n"
    "  [2] BASTOS, P.S.S. (Dr., UNESP) Apostilas Cortante e Flexao. 2017\n"
    "  [3] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2. 2014\n"
    "  [4] NBR 6118:2023, sec.14, 17.2, 17.3, 17.4, 18.3\n"
)

AREA_BARRA = {6.3:0.312, 8.0:0.503, 10.0:0.785, 12.5:1.227,
              16.0:2.011, 20.0:3.142, 25.0:4.909, 32.0:8.042}
BITOLAS = [6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0]


def _fck_props(fck):
    fcd = fck / 1.4
    lam = 0.80 if fck <= 50 else 0.80 - (fck-50)/400
    alpha_c = 0.85 if fck <= 50 else 0.85*(1-(fck-50)/200)
    eta_c = 1.0 if fck <= 40 else (40/fck)**(1/3)
    fctm = 0.3*fck**(2/3) if fck <= 50 else 2.12*math.log(1+0.1*fck+8)
    fctd = 0.15*fck**(2/3) / 10.0   # kN/cm2 (Bastos, 2017)
    return dict(fck=fck, fcd=fcd/10, lam=lam, alpha_c=alpha_c, eta_c=eta_c,
                fctm=fctm, fctd=fctd)


# ============================================================
# ELU - CISALHAMENTO (Modelo I - NBR 6118:2023, sec.17.4)
# ============================================================

def verificar_bielas(VSd_kN, bw_cm, d_cm, fck):
    """VRd2 - Resistencia das bielas comprimidas - Ref [2][4]"""
    p = _fck_props(fck)
    alphav2 = 1 - fck/250
    VRd2 = 0.27 * alphav2 * p["fcd"] * bw_cm * d_cm
    ok = VSd_kN <= VRd2
    return dict(VRd2=round(VRd2,2), VSd=VSd_kN, ok=ok,
                alphav2=round(alphav2,4),
                ref="[2] Bastos(UNESP) + [4] NBR 6118:2023, sec.17.4.1.2")


def calcular_parcela_concreto(bw_cm, d_cm, fck):
    """Vc - Parcela absorvida pelo concreto - Ref [2][4]"""
    p = _fck_props(fck)
    Vc = 0.6 * p["fctd"] * bw_cm * d_cm
    return dict(Vc=round(Vc,2), fctd=round(p["fctd"],4),
                ref="[2] Bastos(UNESP) + [4] NBR 6118:2023, sec.17.4.1.2.1")


def dimensionar_estribos(VSd_kN, bw_cm, d_cm, fck, fyk=500.0):
    """Asw/s - Armadura transversal (Modelo I) - Ref [1][2][4]"""
    p = _fck_props(fck)
    fyd = min(fyk/1.15, 435.0) / 10.0   # kN/cm2
    fywk = fyk / 10.0
    fctm = p["fctm"] / 10.0

    Vc = 0.6 * p["fctd"] * bw_cm * d_cm
    # Armadura minima (NBR 6118:2023, Eq.17.8):
    Asw_s_min = 0.2 * fctm / fywk * bw_cm   # cm2/cm

    if VSd_kN <= Vc:
        Asw_s = Asw_s_min
        trecho = "minimo"
    else:
        Asw_s = max((VSd_kN - Vc) / (0.9 * d_cm * fyd), Asw_s_min)
        trecho = "calculado"

    # Converter para bitola e espaçamento (2 ramos)
    sugestoes = []
    for phi in [5.0, 6.3, 8.0, 10.0]:
        Aphi = AREA_BARRA.get(phi, math.pi*phi**2/400)
        s = round(2 * Aphi / Asw_s, 0)
        s_max = min(0.6*d_cm, 30.0)
        s_adot = min(s, s_max)
        if 5 <= s_adot <= 30:
            sugestoes.append({"phi_mm": phi, "s_cm": int(s_adot),
                               "Asw_s_prov": round(2*Aphi/s_adot, 4)})

    return dict(VSd=VSd_kN, Vc=round(Vc,2), Asw_s=round(Asw_s,5),
                trecho=trecho, Asw_s_min=round(Asw_s_min,5),
                sugestoes=sugestoes[:3],
                ref="[1] Carini + [2] Bastos(UNESP) + [4] NBR 6118:2023, sec.17.4")


# ============================================================
# ELU - FLEXAO (NBR 6118:2023, sec.17.2)
# ============================================================

def momento_limite_simples(b_cm, d_cm, fck):
    """Md,duc - Momento limite para armadura simples - Ref [1][3][4]"""
    p = _fck_props(fck)
    x_duc = 0.45 * d_cm if fck <= 50 else 0.35 * d_cm
    Md_duc = p["alpha_c"]*p["eta_c"]*p["fcd"]*p["lam"]*x_duc*b_cm*(d_cm - p["lam"]*x_duc/2)
    return dict(x_duc=round(x_duc,2), Md_duc=round(Md_duc,2),
                ref="[4] NBR 6118:2023, sec.17.2.2")


def armadura_simples(Md_kNcm, b_cm, d_cm, fck, fyk=500.0):
    """As (flexao simples) - Ref [1][2][3][4]"""
    p = _fck_props(fck)
    fyd = fyk / 1.15 / 10.0
    lim = momento_limite_simples(b_cm, d_cm, fck)
    if Md_kNcm > lim["Md_duc"]:
        return {"erro": "Md > Md,duc - usar armadura dupla",
                "Md_duc": lim["Md_duc"]}
    # x pela formula direta (parabolico-retangular)
    disc = 1 - Md_kNcm / (0.425 * b_cm * d_cm**2 * p["fcd"])
    if disc < 0:
        return {"erro": "Secao insuficiente"}
    x = 1.25 * d_cm * (1 - math.sqrt(disc))
    As = p["alpha_c"]*p["eta_c"]*p["fcd"]*p["lam"]*x*b_cm / fyd
    x_lim = 0.45 * d_cm if fck <= 50 else 0.35 * d_cm
    return dict(Md=Md_kNcm, x_cm=round(x,2), x_lim=round(x_lim,2),
                ok_ductil=x<=x_lim, As_cm2=round(As,2),
                ref="[1][3] Carini/Araujo(FURG) + [4] NBR 6118:2023, sec.17.2.2")


def armadura_dupla(Md_kNcm, b_cm, d_cm, fck, fyk=500.0, caa="II"):
    """As1, As2 (armadura dupla) quando Md > Md,duc - Ref [3][4]"""
    p = _fck_props(fck)
    fyd = fyk / 1.15 / 10.0
    cobr = {"I":2.5,"II":3.0,"III":4.0,"IV":5.0}.get(caa, 3.0)
    dl = cobr + 0.625   # d'
    lim = momento_limite_simples(b_cm, d_cm, fck)
    x_duc = lim["x_duc"]

    # As2 (comprimida) para resistir ao excedente
    ecu = 3.5e-3 if fck <= 50 else (2.6+35*((90-fck)/100)**4)*1e-3
    Es = 21000.0
    eps_s2 = ecu * (x_duc - dl) / x_duc
    sig_s2 = max(-fyd, min(fyd, eps_s2 * Es))
    As2 = (Md_kNcm - lim["Md_duc"]) / (sig_s2 * (d_cm - dl))

    # As1 total
    Fc = p["alpha_c"]*p["eta_c"]*p["fcd"]*p["lam"]*x_duc*b_cm
    As1 = (Fc + As2 * sig_s2) / fyd

    return dict(Md=Md_kNcm, x_duc=round(x_duc,2), dl=round(dl,2),
                sig_s2=round(sig_s2,3),
                As1_cm2=round(As1,2), As2_cm2=round(max(0,As2),2),
                ref="[3] Araujo(Dr.,FURG) 2014 + [4] NBR 6118:2023, sec.17.2.2")


def as_minima_viga(bw_cm, d_cm, fck, fyk=500.0):
    """As,min para vigas - NBR 6118:2023, Tabela 17.3 | Ref [4]

    rho_min = max(0,26 fctm/fyk ; 0,15%). fctm e fyk em MPa -> rho ja e fracao;
    As_min = rho_min * bw * d (NAO dividir por 100 de novo).
    """
    fctm = 0.3*fck**(2/3) if fck <= 50 else 2.12*math.log(1+0.1*fck+8)
    rho_min = max(0.26 * fctm / fyk, 0.0015)   # piso 0,15% (NBR Tabela 17.3)
    As_min = rho_min * bw_cm * d_cm
    return dict(As_min=round(As_min,3), rho_min=round(rho_min,5),
                ref="[4] NBR 6118:2023, Tabela 17.3")


# ============================================================
# ELS - FLECHA (Branson) - Ref [3][4]
# ============================================================

def calcular_flecha_branson(Md_ser_kNcm, As_cm2, bw_cm, h_cm, d_cm,
                             L_m, fck, Es_MPa=210000.0):
    """Flecha por Branson (ELS) - Ref [3] Araujo(FURG) 2014 + [4] NBR 6118:2023"""
    ai = min(0.8 + 0.2*fck/80, 1.0)
    Eci = 1.0 * 5600 * math.sqrt(fck)   # granito alpha_E=1.0
    Ecs = ai * Eci
    fctm = 0.3*fck**(2/3) if fck <= 50 else 2.12*math.log(1+0.1*fck+8)
    ae = Es_MPa / Ecs
    # Inercia bruta
    Ig = bw_cm * h_cm**3 / 12
    Yt = h_cm / 2
    Mr = 1.2 * fctm/10 * Ig / (Yt * 100)   # kNm
    Mr_kNcm = Mr * 100
    # Inercia fissurada: quadratica bw*x^2/2 + ae*As*(x-d) = 0
    A_quad = bw_cm / 2
    B_quad = ae * As_cm2
    C_quad = -ae * As_cm2 * d_cm
    disc = B_quad**2 - 4*A_quad*C_quad
    x_II = (-B_quad + math.sqrt(disc)) / (2*A_quad)
    Iii = bw_cm*x_II**3/3 + ae*As_cm2*(d_cm - x_II)**2
    # Inercia de Branson
    Ma = Md_ser_kNcm
    if Ma <= Mr_kNcm:
        Ie = Ig
    else:
        Ie = (Mr_kNcm/Ma)**3 * Ig + (1 - (Mr_kNcm/Ma)**3) * Iii
    # Flecha imediata (viga biapoiada carga uniforme)
    # q_ser = 8*Ma/L^2 [kN/m] -> delta = 5qL^4/(384EI)
    L_cm = L_m * 100
    q_ser = 8 * Md_ser_kNcm / L_cm**2
    delta_i = 5 * q_ser * L_cm**4 / (384 * Ecs * Ie)   # cm
    delta_t = delta_i * (1 + 2.5)   # fluencia phi=2.5 (NBR 6118:2023)
    wadm = L_cm / 250
    return dict(Mr=round(Mr_kNcm,1), Ig=round(Ig,0), Iii=round(Iii,0),
                Ie=round(Ie,0), x_II=round(x_II,2),
                delta_i=round(delta_i,3), delta_t=round(delta_t,3),
                wadm=round(wadm,2), ok=(delta_t<=wadm),
                ref="[3] Araujo(Dr.,FURG) 2014 + [4] NBR 6118:2023, sec.17.3.2")


def escolher_barras(As_cm2):
    sugs = []
    for phi in BITOLAS:
        n = math.ceil(As_cm2 / AREA_BARRA[phi])
        if 2 <= n <= 10:
            sugs.append((n, phi, round(n*AREA_BARRA[phi], 2)))
    return sugs[:5]
