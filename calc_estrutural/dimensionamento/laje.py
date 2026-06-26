# dimensionamento/laje.py - Dimensionamento de Lajes Macicas e Trelicadas
#
# REFERENCIAS:
#   [1] CARINI, M.R. (MSc, UFSC) Slide 2 - Lajes, 2023 (tabelas coeficientes)
#   [2] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2. 2014
#   [3] BASTOS, P.S.S. (Dr., UNESP) Lajes - Concreto Armado I. 2017
#   [4] NBR 6118:2023, secoes 13.2.4, 14.7, 19.3, 19.4
#   [5] TIMOSHENKO & WOINOWSKY-KRIEGER, Theory of Plates and Shells, Tab.35
#       (coef. de flecha de placa retangular apoiada nos 4 bordos, carga uniforme)
import math

from dimensionamento.tabela_musso import coef_musso, TIPOS_MUSSO

BIBLIOGRAFIA_LAJE = (
    "LAJE - Referencias:\n"
    "  [1'] MUSSO Jr., F. (UFES) CAP3-LAJE, slide 7 - momentos/flechas/reacoes\n"
    "  [2] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2. 2014\n"
    "  [3] BASTOS, P.S.S. (Dr., UNESP) Apostilas CA - Lajes. 2017\n"
    "  [4] NBR 6118:2023, sec.13.2.4, 14.7, 19.3, 19.4\n"
)


def calcular_laje_macica(lx, ly, h_cm, gk, qk, caso=1, fck=25.0, fyk=500.0,
                         caa="II", psi2=0.3):
    """
    Dimensionamento completo de laje macica bidirecional.
    Ref: Carini [1] + Araujo [2] + NBR 6118:2023 [4].
    lx, ly em metros | h_cm em cm | gk, qk em kN/m2
    psi2: fator de combinacao quase-permanente (NBR 6118:2023, Tabela 11.2):
          residencial 0,3 | comercial/escritorio 0,4 | garagem/biblioteca 0,6.
    """
    # Convencao Musso: a = MENOR vao, b = MAIOR vao, beta = b/a (>= 1).
    a = min(lx, ly)
    b = max(lx, ly)
    relacao = round(b / a, 3)
    bidirecional = relacao <= 2.0

    # Cargas de calculo - NBR 6118:2023, sec.11.2
    PP = 25.0 * h_cm / 100.0       # kN/m2
    g_total = gk + PP
    fd = 1.4 * g_total + 1.4 * qk  # ELU
    fd_ser = g_total + psi2 * qk    # ELS

    # Momentos e reacoes (tabela do Musso [1'], interpolada por beta = b/a).
    # M = coef * fd * a^2 ; R = coef * fd * a   (a = menor vao). Eixo x = menor vao.
    cf = coef_musso(caso, relacao)
    Mdx  = cf["ma"]  * fd * a**2   # positivo, vao menor (armadura principal)
    Mdy  = cf["mb"]  * fd * a**2   # positivo, vao maior
    Mdxe = -cf["mae"] * fd * a**2  # negativo, engaste que restringe o vao menor
    Mdye = -cf["mbe"] * fd * a**2  # negativo, engaste que restringe o vao maior
    Rdx  = cf["va"]  * fd * a
    Rdy  = cf["vb"]  * fd * a
    Rdxe = cf["vae"] * fd * a
    Rdye = cf["vbe"] * fd * a

    # ELU: dimensionamento da armadura (Carini [1], Araujo [2])
    # Cobrimento nominal de LAJE - NBR 6118:2023 Tabela 7.2 (Dc=10mm padrao).
    cobr = {"I":2.0,"II":2.5,"III":3.5,"IV":4.5}.get(caa, 2.5)
    d = h_cm - cobr - 0.5    # d estimado (cobrimento + Phi10/2)
    b = 100.0                 # largura unitaria [cm/m]
    fcd = fck / 1.4 / 10.0   # kN/cm2
    fyd = fyk / 1.15 / 10.0

    def armar(Md):
        if abs(Md) < 0.001: return {"As_cm2": 0, "x_cm": 0}
        Md_abs = abs(Md) * 100  # kNm -> kNcm
        disc = 1 - Md_abs / (0.425 * b * d**2 * fcd)
        if disc < 0: return {"As_cm2": -1, "erro": "Md muito grande, aumentar h"}
        x = 1.25 * d * (1 - math.sqrt(max(0, disc)))
        As = 0.85 * fcd * 0.80 * x * b / fyd
        # Armadura minima (NBR 6118:2023, Tabela 19.1)
        rho_min = 0.15 if fyk <= 500 else 0.12  # %
        As_min = rho_min/100 * b * h_cm
        return {"As_cm2": round(max(As, As_min), 2),
                "x_cm": round(x, 2),
                "ok_ductil": x <= 0.45*d}

    # ELS: flecha de placa (Musso [1'], slide 7 — Poisson=0,2 ja embutido no coef):
    #   f0 = coef_f(beta) * fd_ser * a^4 / (Ecs * h^3)   [m]  (a = menor vao)
    ai = min(0.8 + 0.2*fck/80, 1.0)              # NBR 6118:2023 sec.8.2.8
    Ecs_MPa = ai * 5600 * math.sqrt(fck)         # MPa (granito alpha_E=1.0)
    Ecs = Ecs_MPa * 1000.0                        # kN/m2 (1 MPa = 1000 kN/m2)
    h_m = h_cm / 100.0
    coef_fl = cf["f"]                             # coef. de flecha do tipo, interp. por beta
    w0_m = coef_fl * fd_ser * a**4 / (Ecs * h_m**3)  # flecha imediata [m]
    w_total_m = w0_m * (1 + 2.5)                  # fluencia phi=2,5 (NBR 6118 simplif.)
    wadm_m = a / 250.0                             # NBR 6118:2023 Tabela 13.3 (menor vao)
    w0_aprox, w_total, wadm = w0_m, w_total_m, wadm_m

    return dict(
        lx=lx, ly=ly, relacao=relacao, tipo="BIDIRECIONAL" if bidirecional else "UNIDIRECIONAL",
        h_cm=h_cm, PP_kNm2=round(PP,2),
        fd_kNm2=round(fd,2), fd_ser_kNm2=round(fd_ser,2), psi2=psi2,
        caso=caso,
        momentos={
            "Mdx_pos":  round(Mdx,  3),
            "Mdy_pos":  round(Mdy,  3),
            "Mdxe_neg": round(Mdxe, 3),
            "Mdye_neg": round(Mdye, 3),
        },
        reacoes={
            "Rdx": round(Rdx, 3), "Rdy": round(Rdy, 3),
            "Rdxe": round(Rdxe,3), "Rdye": round(Rdye,3),
        },
        armaduras={
            "Asx_pos": armar(Mdx),
            "Asy_pos": armar(Mdy),
            "Asxe_neg": armar(Mdxe),
            "Asye_neg": armar(Mdye),
        },
        els_flecha={
            "w0_mm": round(w0_aprox*1000, 2),
            "w_total_mm": round(w_total*1000, 2),
            "wadm_mm": round(wadm*1000, 2),
            "lambda_flecha": round(relacao, 3),
            "coef_flecha": round(coef_fl, 5),
            "ok": (w_total <= wadm),
        },
        a_menor=a, b_maior=b, beta=relacao,
        tipo_descr=TIPOS_MUSSO.get(caso, TIPOS_MUSSO[1]),
        ref="[1'] Musso (UFES) slide 7 (interp. por beta) + [4] NBR 6118:2023"
    )


def calcular_laje_unid(lx, h_cm, gk, qk, caso=7, fck=25.0, fyk=500.0, caa="II"):
    """
    Dimensionamento de laje unidirecional - Casos 7 a 10.
    Ref: Carini [1] + NBR 6118:2023 [4].
    """
    PP = 25.0 * h_cm / 100.0
    g_total = gk + PP
    fd = 1.4 * g_total + 1.4 * qk

    # Momentos por caso
    momentos_casos = {
        7:  {"Md_vao":  fd*lx**2/8,  "Md_eng": 0,            "Rd": fd*lx/2},
        8:  {"Md_vao":  fd*lx**2/14.22,"Md_eng":-fd*lx**2/8,"Rd_ap":3*fd*lx/8,"Rd_eng":5*fd*lx/8},
        9:  {"Md_vao":  fd*lx**2/24, "Md_eng":-fd*lx**2/12,  "Rd": fd*lx/2},
        10: {"Md_vao":  0,            "Md_eng":-fd*lx**2/2,   "Rd": fd*lx},
    }
    m = momentos_casos.get(caso, momentos_casos[7])

    # Cobrimento nominal de LAJE - NBR 6118:2023 Tabela 7.2 (Dc=10mm padrao).
    cobr = {"I":2.0,"II":2.5,"III":3.5,"IV":4.5}.get(caa, 2.5)
    d = h_cm - cobr - 0.5
    b = 100.0
    fcd = fck / 1.4 / 10.0
    fyd = fyk / 1.15 / 10.0

    def armar(Md):
        if abs(Md) < 0.001: return {"As_cm2": 0}
        Md_cm = abs(Md) * 100
        disc = 1 - Md_cm / (0.425*b*d**2*fcd)
        if disc < 0: return {"As_cm2": -1, "erro": "Aumentar h"}
        x = 1.25*d*(1 - math.sqrt(max(0,disc)))
        As = 0.85*fcd*0.80*x*b / fyd
        As_min = 0.15/100 * b * h_cm
        return {"As_cm2": round(max(As, As_min), 2), "x_cm": round(x,2)}

    return dict(
        caso=caso, lx=lx, h_cm=h_cm, fd=round(fd,2),
        momentos={k: round(v,3) for k,v in m.items()},
        armaduras={"Asvao": armar(m.get("Md_vao",0)),
                   "Aseng": armar(m.get("Md_eng",0))},
        ref="[1] Carini(2023) + [4] NBR 6118:2023, sec.19"
    )
