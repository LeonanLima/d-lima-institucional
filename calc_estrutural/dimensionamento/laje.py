# dimensionamento/laje.py - Dimensionamento de Lajes Macicas e Trelicadas
#
# REFERENCIAS:
#   [1] CARINI, M.R. (MSc, UFSC) Slide 2 - Lajes, 2023 (tabelas coeficientes)
#   [2] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.2. 2014
#   [3] BASTOS, P.S.S. (Dr., UNESP) Lajes - Concreto Armado I. 2017
#   [4] NBR 6118:2023, secoes 13.2.4, 14.7, 19.3, 19.4
import math

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


def calcular_laje_macica(lx, ly, h_cm, gk, qk, caso=1, fck=25.0, fyk=500.0, caa="II"):
    """
    Dimensionamento completo de laje macica bidirecional.
    Ref: Carini [1] + Araujo [2] + NBR 6118:2023 [4].
    lx, ly em metros | h_cm em cm | gk, qk em kN/m2
    """
    relacao = round(ly / lx, 3)
    bidirecional = relacao <= 2.0

    # Cargas de calculo - NBR 6118:2023, sec.11.2
    PP = 25.0 * h_cm / 100.0       # kN/m2
    g_total = gk + PP
    fd = 1.4 * g_total + 1.4 * qk  # ELU

    psi2 = {"residencial":0.3, "comercial":0.4, "garagem":0.6}.get("residencial", 0.3)
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
    cobr = {"I":1.5,"II":2.0,"III":3.5,"IV":4.5}.get(caa, 2.0)
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

    # ELS: flecha simplificada (formula aproximada, Araujo [2])
    ai = min(0.8 + 0.2*fck/80, 1.0)
    Ecs = ai * 5600 * math.sqrt(fck)   # MPa (granito alpha_E=1.0)
    D = Ecs * (h_cm/100)**3 / (12 * (1 - 0.04))  # rigidez placa (nu=0.2)
    # Coeficiente de flecha para caso 1 bidirecional (aprox.)
    Md_ser = fd_ser * lx**2 / 8   # kNm/m (valor aproximado)
    w0_aprox = 5 * fd_ser * (lx*100)**4 / (384 * Ecs * b*(h_cm/100)**3/12 * 1e4)
    w_total = w0_aprox * (1 + 2.5)   # fluencia phi=2.5
    wadm = (lx*100) / 250.0

    return dict(
        lx=lx, ly=ly, relacao=relacao, tipo="BIDIRECIONAL" if bidirecional else "UNIDIRECIONAL",
        h_cm=h_cm, PP_kNm2=round(PP,2),
        fd_kNm2=round(fd,2), fd_ser_kNm2=round(fd_ser,2),
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
            "w0_mm": round(w0_aprox*10, 2),
            "w_total_mm": round(w_total*10, 2),
            "wadm_mm": round(wadm, 2),
            "ok": (w_total*10 <= wadm),
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

    cobr = {"I":1.5,"II":2.0,"III":3.5,"IV":4.5}.get(caa, 2.0)
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


def imprimir_laje(res):
    print("\n" + "="*60)
    print(f"DIMENSIONAMENTO - LAJE CASO {res.get('caso','')}")
    print("="*60)
    for k, v in res.items():
        if isinstance(v, dict):
            print(f"\n  --- {k.upper()} ---")
            for kk, vv in v.items(): print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")
    print()
    print(BIBLIOGRAFIA_LAJE)
