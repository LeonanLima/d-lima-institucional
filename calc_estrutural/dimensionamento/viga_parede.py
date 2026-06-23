# dimensionamento/viga_parede.py - Viga-Parede (Deep Beam)
#
# REFERENCIAS:
#   [1] NBR 6118:2023, secao 22.6 (vigas-parede)
#   [2] FUSCO, P.B. (Dr., USP) Tecnica de Armar as Estruturas de Concreto. 2013
#   [3] BASTOS, P.S.S. (Dr., UNESP) Modelos Biela-Tirante. 2017
#   [4] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2. 2014
import math

BIBLIOGRAFIA_VP = (
    "VIGA-PAREDE - Referencias:\n"
    "  [1] NBR 6118:2023, sec.22.6\n"
    "  [2] FUSCO, P.B. (Dr., USP) Tecnica de Armar as Estruturas. 2013\n"
    "  [3] BASTOS, P.S.S. (Dr., UNESP) Modelos Biela-Tirante. 2017\n"
    "  [4] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2. 2014\n"
)


def classificar_viga_parede(L_m, h_m):
    """
    NBR 6118:2023, sec.22.6.1: viga-parede quando l/h < 2 (simplesmente apoiada)
    ou l/h < 2,5 (continua). Ref [1]
    """
    ratio = L_m / h_m
    eh_viga_parede = ratio < 2.0
    return dict(
        L=L_m, h=h_m, lh=round(ratio, 2),
        eh_viga_parede=eh_viga_parede,
        criterio="l/h < 2,0 (SA) ou < 2,5 (continua) — NBR 6118:2023, sec.22.6.1",
        ref="[1] NBR 6118:2023, sec.22.6.1"
    )


def modelo_biela_tirante(L_m, h_m, Fd_kN, bw_cm=20.0, fck=25.0, fyk=500.0, caa="II"):
    """
    Modelo biela-tirante simplificado para viga-parede biapoiada.
    Ref: Fusco [2] + Bastos [3] + NBR 6118:2023 [1]

    Modelo: carga aplicada no topo; tirante horizontal na base.
    Angulo das bielas comprimidas: theta (tg = h / (L/2))
    """
    fcd = fck / 1.4 / 10.0     # kN/cm2
    fyd = fyk / 1.15 / 10.0    # kN/cm2
    cobr = {"I":2.5,"II":3.0,"III":4.0,"IV":5.0}.get(caa, 3.0)

    # Angulo das bielas
    theta = math.atan(h_m / (L_m / 2))
    theta_graus = math.degrees(theta)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # Reacoes verticais (biapoiada, carga central)
    Vd = Fd_kN / 2.0

    # Forca nas bielas (por equilibrio):
    Fbiela = Vd / sin_t    # kN

    # Forca no tirante horizontal (banco inferior):
    Ft = Vd / math.tan(theta)   # kN = Vd * cot(theta)

    # Verificar tensao nas bielas:
    alphav2 = 1 - fck / 250
    bw = bw_cm
    w_biela = bw * 10    # largura da biela = bw (estimativa)
    sigma_biela = Fbiela / (w_biela * bw)  # kN/cm2
    sigma_biela_lim = 0.60 * alphav2 * fcd
    biela_ok = sigma_biela <= sigma_biela_lim

    # Armadura do tirante:
    As_tirante = Ft / fyd   # cm2

    # Armadura distribuida horizontal e vertical (construtiva min. NBR 22.6):
    As_horiz_min = 0.15/100 * bw_cm * 100    # cm2/m (0,15% da secao)
    As_vert_min  = 0.10/100 * bw_cm * 100    # cm2/m (0,10% da secao)

    # Posicao do tirante: h/5 a h/3 da base
    y_tirante = round(h_m / 4.0, 2)

    return dict(
        L=L_m, h=h_m, Fd=Fd_kN, bw=bw_cm,
        theta_graus=round(theta_graus, 1),
        Vd=round(Vd, 2), Fbiela=round(Fbiela, 2), Ft=round(Ft, 2),
        sigma_biela=round(sigma_biela, 4),
        sigma_biela_lim=round(sigma_biela_lim, 4),
        biela_ok=biela_ok,
        As_tirante_cm2=round(As_tirante, 2),
        y_tirante_m=y_tirante,
        As_horiz_min=round(As_horiz_min, 2),
        As_vert_min=round(As_vert_min, 2),
        nota_dist="Armaduras horiz. e vert. distribuidas nas 2 faces da viga-parede",
        ref="[1][2][3] NBR 6118:2023, sec.22.6 | Fusco(USP) | Bastos(UNESP) 2017"
    )


def armadura_tirante_escolher(As_cm2, fyd_MPa=435.0):
    """Sugestoes de bitola para o tirante"""
    AREA = {10:0.785, 12.5:1.227, 16:2.011, 20:3.142, 25:4.909, 32:8.042}
    sugs = []
    for phi, A in AREA.items():
        n = math.ceil(As_cm2 / A)
        if 2 <= n <= 12:
            sugs.append({"n": n, "phi_mm": phi, "As_prov": round(n*A, 2)})
    return sugs[:4]


def imprimir_viga_parede(classif, modelo):
    print("\n" + "="*60)
    print("DIMENSIONAMENTO - VIGA-PAREDE | NBR 6118:2023, sec.22.6")
    print("="*60)
    print("\n--- CLASSIFICACAO ---")
    for k, v in classif.items(): print(f"  {k}: {v}")
    print("\n--- MODELO BIELA-TIRANTE ---")
    for k, v in modelo.items(): print(f"  {k}: {v}")
    print("\n  Sugestoes tirante:")
    for s in armadura_tirante_escolher(modelo["As_tirante_cm2"]):
        print(f"    {s}")
    print()
    print(BIBLIOGRAFIA_VP)
