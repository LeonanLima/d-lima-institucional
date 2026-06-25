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

from core.tabelas import interp_linear

BIBLIOGRAFIA_LAJE = (
    "LAJE - Referencias:\n"
    "  [1] CARINI, M.R. (MSc, UFSC) Lajes - Estrutural na Real, 2023\n"
    "  [2] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2. 2014\n"
    "  [3] BASTOS, P.S.S. (Dr., UNESP) Apostilas CA - Lajes. 2017\n"
    "  [4] NBR 6118:2023, sec.13.2.4, 14.7, 19.3, 19.4\n"
)

# Tabela de coeficientes de Carini para lajes macicas bidirecionais
# Casos 1-9 para lambda = ly/lx = 1.0
# Formato: {caso: {mx, my, mxe, mye, rx, ry, rxe, rye}}
# Ref: Carini [1], extraido das planilhas P01_Lajes.xlsx
COEF_CARINI = {
    1:  {"mx":0.1075,"my":0.0434,"mxe":None, "mye":None, "rx":0.1103,"ry":0.4299,"rxe":None, "rye":None},
    2:  {"mx":0.0660,"my":0.0190,"mxe":None, "mye":-0.1173,"rx":0.0482,"ry":0.3520,"rxe":None, "rye":0.5867},
    "2A":{"mx":0.0749,"my":0.0505,"mxe":-0.0896,"mye":None,"rx":0.1709,"ry":0.2988,"rxe":0.2849,"rye":None},
    3:  {"mx":0.0404,"my":0.0098,"mxe":None, "mye":-0.0807,"rx":None, "ry":0.2485,"rxe":None, "rye":0.4842},
    "3A":{"mx":0.0689,"my":0.0463,"mxe":-0.0927,"mye":None,"rx":None, "ry":0.2754,"rxe":0.3534,"rye":None},
    4:  {"mx":0.0605,"my":0.0244,"mxe":-0.1075,"mye":-0.0434,"rx":0.0827,"ry":0.3224,"rxe":0.1379,"rye":0.5374},
    5:  {"mx":0.0385,"my":0.0131,"mxe":-0.0771,"mye":-0.0233,"rx":0.0445,"ry":None, "rxe":0.0742,"rye":0.4623},
    "5A":{"mx":0.0531,"my":0.0254,"mxe":-0.0943,"mye":-0.0508,"rx":None, "ry":0.2828,"rxe":0.1935,"rye":0.4713},
    6:  {"mx":0.0359,"my":0.0143,"mxe":-0.0716,"mye":-0.0289,"rx":None, "ry":None, "rxe":0.1103,"rye":0.4299},
}

# Coeficiente de flecha de placa retangular APOIADA nos 4 bordos sob carga
# uniforme (Timoshenko [5], Tab.35; mesma familia dos wc do Carini):
#   w0 = alpha * fd_ser * lx^4 / D , com D = Ecs*h^3 / [12*(1-nu^2)] , nu=0,2.
# Indexado por lambda = ly/lx in [1,0 ; 2,0]; fora do intervalo o interp clampa.
# Para casos com engaste (2-6) a placa e mais rigida -> usar este alpha (caso 1)
# e CONSERVADOR (superestima a flecha, a favor da seguranca).
ALPHA_FLECHA_4APOIOS = [
    [1.0, 0.00406], [1.1, 0.00485], [1.2, 0.00564], [1.3, 0.00638],
    [1.4, 0.00705], [1.5, 0.00772], [1.6, 0.00830], [1.7, 0.00883],
    [1.8, 0.00931], [1.9, 0.00974], [2.0, 0.01013],
]


def calcular_laje_macica(lx, ly, h_cm, gk, qk, caso=1, fck=25.0, fyk=500.0,
                         caa="II", psi2=0.3):
    """
    Dimensionamento completo de laje macica bidirecional.
    Ref: Carini [1] + Araujo [2] + NBR 6118:2023 [4].
    lx, ly em metros | h_cm em cm | gk, qk em kN/m2
    psi2: fator de combinacao quase-permanente (NBR 6118:2023, Tabela 11.2):
          residencial 0,3 | comercial/escritorio 0,4 | garagem/biblioteca 0,6.
    """
    relacao = round(ly / lx, 3)
    bidirecional = relacao <= 2.0

    # Cargas de calculo - NBR 6118:2023, sec.11.2
    PP = 25.0 * h_cm / 100.0       # kN/m2
    g_total = gk + PP
    fd = 1.4 * g_total + 1.4 * qk  # ELU
    fd_ser = g_total + psi2 * qk    # ELS

    # Momentos e reacoes (Carini [1], Tabela coeficientes)
    coef = COEF_CARINI.get(caso, COEF_CARINI[1])
    Mdx  = coef["mx"]  * fd * lx**2 if coef["mx"]  else 0
    Mdy  = coef["my"]  * fd * lx**2 if coef["my"]  else 0
    Mdxe = coef["mxe"] * fd * lx**2 if coef["mxe"] else 0
    Mdye = coef["mye"] * fd * lx**2 if coef["mye"] else 0
    Rdx  = coef["rx"]  * fd * lx    if coef["rx"]   else 0
    Rdy  = coef["ry"]  * fd * lx    if coef["ry"]   else 0
    Rdxe = coef["rxe"] * fd * lx    if coef["rxe"]  else 0
    Rdye = coef["rye"] * fd * lx    if coef["rye"]  else 0

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

    # ELS: flecha de placa (NBR 6118:2023 sec.17.3.2 + Timoshenko [5] / Carini [1])
    #   w0 = alpha(lambda) * fd_ser * lx^4 / D   (placa retangular, carga uniforme)
    #   D  = Ecs * h^3 / [12*(1-nu^2)] , nu=0,2 (NBR 6118:2023 sec.8.2.9)
    ai = min(0.8 + 0.2*fck/80, 1.0)              # NBR 6118:2023 sec.8.2.8
    Ecs_MPa = ai * 5600 * math.sqrt(fck)         # MPa (granito alpha_E=1.0)
    Ecs = Ecs_MPa * 1000.0                        # kN/m2 (1 MPa = 1000 kN/m2)
    h_m = h_cm / 100.0
    nu = 0.20
    D = Ecs * h_m**3 / (12 * (1 - nu**2))         # kNm (rigidez de placa)
    lam_fl = min(max(ly / lx, 1.0), 2.0)          # tabela vale em [1,0 ; 2,0]
    alpha_fl = interp_linear(ALPHA_FLECHA_4APOIOS, lam_fl)[0]
    w0_m = alpha_fl * fd_ser * lx**4 / D          # flecha imediata [m]
    w_total_m = w0_m * (1 + 2.5)                  # fluencia phi=2,5 (NBR 6118 simplif.)
    wadm_m = lx / 250.0                            # NBR 6118:2023 Tabela 13.3
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
            "lambda_flecha": round(lam_fl, 3),
            "alpha_flecha": round(alpha_fl, 5),
            "ok": (w_total <= wadm),
        },
        ref="[1] Carini(2023) + [2] Araujo(Dr.,FURG) 2014 + [4] NBR 6118:2023"
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
