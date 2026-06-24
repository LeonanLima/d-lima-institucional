# dimensionamento/pilar.py - Dimensionamento de Pilares Contraventados
#
# REFERENCIAS:
#   [1] CARINI, M.R. (MSc, UFSC) Pilares Contraventados, 2023
#   [2] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2, cap.10. 2014
#   [3] BASTOS, P.S.S. (Dr., UNESP) Pilares - Concreto Armado I. 2017
#   [4] NBR 6118:2023, secoes 11.4, 13.2.3, 17.2.5, 18.4
import math

BIBLIOGRAFIA_PILAR = (
    "PILAR - Referencias:\n"
    "  [1] CARINI, M.R. (MSc, UFSC) Pilares Contraventados, 2023\n"
    "  [2] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2, 2014\n"
    "  [3] BASTOS, P.S.S. (Dr., UNESP) Pilar-Padrao. 2017\n"
    "  [4] NBR 6118:2023, sec.11.4, 13.2.3, 17.2.5, 18.4\n"
)

BITOLAS = [6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0]
AREA_BARRA = {6.3:0.312, 8.0:0.503, 10.0:0.785, 12.5:1.227,
              16.0:2.011, 20.0:3.142, 25.0:4.909, 32.0:8.042}


def _fck_props(fck):
    fcd = fck / 1.4
    if fck <= 50:
        fctm = 0.3 * fck**(2/3)
        lam, alpha_c, eta_c = 0.80, 0.85, 1.0
    else:
        fctm = 2.12 * math.log(1 + 0.1*fck + 8)
        lam = 0.80 - (fck - 50)/400
        alpha_c = 0.85 * (1 - (fck - 50)/200)
        eta_c = (40/fck)**(1/3)
    ecu = 3.5e-3 if fck <= 50 else (2.6 + 35*((90-fck)/100)**4)*1e-3
    return dict(fck=fck, fcd=fcd, fctm=fctm, lam=lam, alpha_c=alpha_c,
                eta_c=eta_c, ecu=ecu)


def calcular_esbeltez(H_cm, hx_cm, hy_cm, beta=1.0):
    """Esbeltez do pilar - NBR 6118:2023, sec.11.3.2 | Ref [1][3]"""
    le = beta * H_cm
    lam_x = le / (hx_cm / math.sqrt(12))
    lam_y = le / (hy_cm / math.sqrt(12))
    def status(l): return "CURTO" if l <= 35 else "ESBELTO" if l <= 90 else "MUITO_ESBELTO"
    return dict(le_cm=round(le,1),
                lam_x=round(lam_x,1), status_x=status(lam_x),
                lam_y=round(lam_y,1), status_y=status(lam_y),
                ref="[1][3] Carini/Bastos + [4] NBR 6118:2023, sec.11.3.2")


def excentricidade_minima(hx_cm, hy_cm):
    """Excentricidade minima 1a ordem - NBR 6118:2023, sec.11.4.1"""
    return dict(e1x_min=round(1.5 + 0.03*hx_cm, 2),
                e1y_min=round(1.5 + 0.03*hy_cm, 2),
                ref="[4] NBR 6118:2023, sec.11.4.1")


def lambda1_limite(e1A_cm, h_cm, alpha_b):
    """Limite lambda1 - NBR 6118:2023, sec.11.3.3 | Ref [1][2]"""
    lam1 = 25 + 12.5 * (alpha_b * e1A_cm / h_cm)
    return round(max(35.0, min(90.0, lam1)), 1)


def excentricidade_2a_ordem(lam, h_cm, nu):
    """Pilar-Padrao: excentricidade 2a ordem - NBR 6118:2023, sec.11.4.2 | Ref [1][2][3]"""
    if lam <= 35:
        return 0.0
    return round(0.0005 * lam**2 * h_cm / (0.5 + nu), 3)


def momento_total_pilar(Nd_kN, Md_kNcm, H_cm, hx_cm, hy_cm, beta=1.0, fck=25.0):
    """Momento total de calculo do pilar-padrao (direcao y governante).

    Soma a excentricidade de 1a ordem (max entre e0 e e1,min) com a de 2a ordem
    e devolve Md,tot = Nd*(e1+e2). A pagina Pilar deve dimensionar com ESTE
    momento (antes usava o Md cru, ignorando e1,min e e2 - bug catalogado).
    Fonte unica: memorial_pilar consome esta mesma funcao.
    NBR 6118:2023, sec.11.4 / 15.8 | Ref [1][2][3].
    """
    fcd = _fck_props(fck)["fcd"] / 10.0   # kN/cm2
    Ac = hx_cm * hy_cm
    nu = Nd_kN / (Ac * fcd) if Ac * fcd > 0 else 0.0
    esb = calcular_esbeltez(H_cm, hx_cm, hy_cm, beta)
    exc = excentricidade_minima(hx_cm, hy_cm)
    e0 = Md_kNcm / Nd_kN if Nd_kN > 0.1 else 0.0
    e2y = excentricidade_2a_ordem(esb["lam_y"], hy_cm, nu)
    e2x = excentricidade_2a_ordem(esb["lam_x"], hx_cm, nu)
    e_design = max(e0, exc["e1y_min"]) + e2y
    Md_design = Nd_kN * e_design
    return dict(nu=round(nu,3), e0=round(e0,2),
                e1x_min=exc["e1x_min"], e1y_min=exc["e1y_min"],
                e2x=round(e2x,2), e2y=round(e2y,2),
                e_design=round(e_design,2), Md_design=round(Md_design,1),
                lam_x=esb["lam_x"], lam_y=esb["lam_y"],
                ref="[1][2][3] + [4] NBR 6118:2023, sec.15.8")


def dimensionar_secao(Nd_kN, Md_kNcm, b_cm, h_cm,
                       fck=25.0, fyk=500.0, caa="II"):
    """
    Flexo-compressao normal com armadura simetrica - Ref [1][2][3][4]
    NBR 6118:2023, sec.17.2 + Araujo (Dr., FURG) v.2, cap.10
    """
    p = _fck_props(fck)
    fcd = p["fcd"] / 10.0       # MPa -> kN/cm2
    fyd = fyk / 1.15 / 10.0    # kN/cm2
    Es = 21000.0
    cobr = {"I":2.5,"II":3.0,"III":4.0,"IV":5.0}.get(caa, 3.0)
    d = h_cm - cobr - 0.625    # d (cobrimento + Phi12.5/2)
    dl = cobr + 0.625           # d' (cobrimento comprimida)
    lam = p["lam"]; alpha_c = p["alpha_c"]; eta_c = p["eta_c"]
    ecu = p["ecu"]

    e0 = Md_kNcm / Nd_kN if Nd_kN > 0.1 else 0.0

    # Busca binaria para encontrar x
    x_lo, x_hi = 0.001, 2.0 * h_cm
    for _ in range(80):
        x = (x_lo + x_hi) / 2
        Fc = alpha_c * eta_c * fcd * lam * x * b_cm
        eps1 = ecu * (d - x) / x
        eps2 = ecu * (x - dl) / x
        s1 = max(-fyd, min(fyd, eps1 * Es))
        s2 = max(-fyd, min(fyd, eps2 * Es))
        den = s2 - s1
        if abs(den) < 1e-8:
            x_hi = x; continue
        As = (Nd_kN - Fc) / den
        # verificar eq de momentos
        M_res = Fc*(d - lam*x/2) + As*(s2*dl - s1*d) - Nd_kN*e0
        if M_res > 0: x_hi = x
        else:          x_lo = x

    x = (x_lo + x_hi) / 2
    Fc = alpha_c * eta_c * fcd * lam * x * b_cm
    eps1 = ecu*(d-x)/x; eps2 = ecu*(x-dl)/x
    s1 = max(-fyd, min(fyd, eps1*Es)); s2 = max(-fyd, min(fyd, eps2*Es))
    As_cada = max(0, (Nd_kN - Fc) / (s2 - s1 + 1e-9))
    As_total = 2 * As_cada

    Ac = b_cm * h_cm
    As_min = max(0.15 * Nd_kN / fyd, 0.004 * Ac)
    As_max = 0.08 * Ac
    As_adot = max(As_total, As_min)

    x_lim = 0.628 * d
    dom_lim = 0.259 * d
    if x < 0:        dom = 1
    elif x < dom_lim: dom = 2
    elif x < x_lim:   dom = 3
    elif x < d:        dom = 4
    elif x < h_cm:     dom = "4a"
    else:               dom = 5

    return dict(
        Nd=Nd_kN, Md=Md_kNcm, e0=round(e0,2),
        x_cm=round(x,2), x_lim_cm=round(x_lim,2),
        dominio=dom, ok_ductil=(x <= x_lim),
        As_calc=round(As_total,2), As_min=round(As_min,2),
        As_max=round(As_max,2), As_adot=round(As_adot,2),
        ref="[1][2][3] Carini/Araujo(FURG)/Bastos(UNESP) + [4] NBR 6118:2023, sec.17.2"
    )


def verificacao_obliqua(Mx, My, MRdxx, MRdyy):
    """Flexo-compressao obliqua - NBR 6118:2023, sec.17.2.5 | Ref [1][4]"""
    ratio = (abs(Mx)/MRdxx)**1.2 + (abs(My)/MRdyy)**1.2 if MRdxx > 0 and MRdyy > 0 else 999
    return dict(Mx=Mx, My=My, MRdxx=MRdxx, MRdyy=MRdyy,
                interacao=round(ratio,4), ok=ratio<=1.0,
                ref="[4] NBR 6118:2023, sec.17.2.5")


def estribo_pilar(phi_long_mm, b_min_cm):
    """Estribos do pilar - NBR 6118:2023, sec.18.4.2.2 | Ref [1][3]"""
    phi = max(5.0, math.ceil(phi_long_mm/4.0))
    s = round(min(b_min_cm, phi_long_mm/10*20, 30), 1)
    return dict(phi_est_mm=phi, s_max_cm=s, s_red_cm=round(0.6*s,1),
                ref="[4] NBR 6118:2023, sec.18.4.2.2")


def escolher_barras(As_cm2):
    """Sugestoes de bitola e numero de barras para As_cm2"""
    sugestoes = []
    for phi in BITOLAS:
        Aphi = AREA_BARRA[phi]
        n = math.ceil(As_cm2 / Aphi)
        if n >= 4:
            sugestoes.append((n, phi, round(n*Aphi,2)))
    return sugestoes[:5]


def imprimir_pilar(esb, dim, est=None):
    print("\n" + "="*60)
    print("DIMENSIONAMENTO - PILAR | NBR 6118:2023")
    print("="*60)
    print("\n--- ESBELTEZ ---")
    for k, v in esb.items(): print(f"  {k}: {v}")
    print("\n--- FLEXO-COMPRESSAO ---")
    for k, v in dim.items(): print(f"  {k}: {v}")
    if est:
        print("\n--- ESTRIBOS ---")
        for k, v in est.items(): print(f"  {k}: {v}")
    print()
    print(BIBLIOGRAFIA_PILAR)
