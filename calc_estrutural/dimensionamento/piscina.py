# dimensionamento/piscina.py - Piscinas em Concreto Armado
#
# REFERENCIAS:
#   [1] NBR 6118:2023, sec.21 (estruturas em contato com liquidos)
#   [2] FUSCO, P.B. (Dr., USP) Estruturas de Concreto: Sol. Tangenciais. 2008
#   [3] CARINI, M.R. (MSc, UFSC) Piscinas e Reservatorios - Notas. 2023
#   [4] BASTOS, P.S.S. (Dr., UNESP) Apostila Elementos Especiais. 2017
import math

BIBLIOGRAFIA_PISCINA = (
    "PISCINA - Referencias:\n"
    "  [1] NBR 6118:2023, sec.21 (contato com liquidos)\n"
    "  [2] FUSCO, P.B. (Dr., USP) Estruturas de Concreto. 2008\n"
    "  [3] CARINI, M.R. (MSc, UFSC) Piscinas - Notas. 2023\n"
    "  [4] BASTOS, P.S.S. (Dr., UNESP) Elementos Especiais. 2017\n"
)

GAMMA_AGUA = 10.0  # kN/m3
CAA_PISCINA = "IV"  # NBR 6118:2023, sec.21 — CAA IV piscinas
FCK_MIN = 40       # MPa


def combinacoes_piscina(H_agua, phi_solo=30.0, gamma_solo=18.0, qs_kPa=0.0):
    """
    Combinacoes de carregamento (NBR 6118:2023, sec.21.2) | Ref [1][3]
    C1 - Cheia + sem solo
    C2 - Vazia + solo externo (pior para paredes laterais)
    C3 - Cheia + solo externo (semi-enterrada)
    """
    Ka = math.tan(math.radians(45 - phi_solo/2))**2
    p_agua_base = GAMMA_AGUA * H_agua     # kN/m2 (pressao na base)
    p_solo_base = Ka * (gamma_solo * H_agua + qs_kPa)   # kN/m2

    C1 = {"desc": "CHEIA, sem solo externo",
          "p_int_base": round(p_agua_base, 2),
          "p_ext_base": 0.0,
          "p_net_base": round(p_agua_base, 2),
          "critica_para": "paredes (pressao de dentro para fora)"}
    C2 = {"desc": "VAZIA, com solo externo (piscina enterrada)",
          "p_int_base": 0.0,
          "p_ext_base": round(p_solo_base, 2),
          "p_net_base": round(p_solo_base, 2),
          "critica_para": "paredes (pressao de fora para dentro)"}
    C3 = {"desc": "CHEIA + solo externo (semi-enterrada)",
          "p_int_base": round(p_agua_base, 2),
          "p_ext_base": round(p_solo_base, 2),
          "p_net_base": round(abs(p_agua_base - p_solo_base), 2),
          "critica_para": "verifica compensacao"}
    return C1, C2, C3


def dimensionar_parede(H_agua, espessura_m, combin, fck=40.0, fyk=500.0, caa="IV"):
    """
    Dimensionamento da parede de piscina (modelo balanco vertical).
    Ref: Bastos [4] + NBR 6118:2023, sec.21 [1]
    """
    fcd = fck / 1.4 / 10.0
    fyd = fyk / 1.15 / 10.0
    cobr = {"I":2.0,"II":2.5,"III":4.0,"IV":4.5}.get(caa, 4.5)
    h_cm = espessura_m * 100
    d = h_cm - cobr - 0.625

    p_base = combin.get("p_net_base", 0)   # kN/m2
    gamma_f = 1.4

    # Momento no engaste da base (carga triangular):
    Md = gamma_f * p_base * H_agua**2 / 6   # kNm/m
    Vd = gamma_f * p_base * H_agua / 2      # kN/m

    # Forca de tracao horizontal (anel, raio = L/2 se for circular ou retang.)
    # Simplificacao: usar como viga em balanco e ignorar efeito anel
    Md_cm = Md * 100
    b = 100.0
    if Md_cm < 0.01:
        return {"As_cm2m": 0, "Md": 0, "nota": "Sem momento nesta comb."}
    disc = 1 - Md_cm / (0.425 * b * d**2 * fcd)
    if disc < 0:
        return {"erro": "Seção insuficiente - aumentar espessura"}
    x = 1.25 * d * (1 - math.sqrt(max(0, disc)))
    As = 0.85 * fcd * 0.80 * x * b / fyd
    As_min = max(0.15/100 * b * h_cm, 0.0015 * b * h_cm)
    As_adot = round(max(As, As_min), 2)

    return dict(
        H=H_agua, h_cm=h_cm, d_cm=round(d,1),
        p_base=round(p_base,2), Md_kNm=round(Md,2), Vd_kN=round(Vd,2),
        As_cm2m=As_adot, As_min=round(As_min,2),
        w_lim=0.1,  # mm (NBR 6118:2023, sec.21.3 - CAA IV)
        ref="[1] NBR 6118:2023, sec.21 | [4] Bastos(Dr.,UNESP) 2017"
    )


def dimensionar_fundo(H_agua, Lx, Ly, h_fundo_m, fck=40.0, fyk=500.0, caa="IV"):
    """
    Dimensionamento do fundo da piscina (laje macica, pressao de baixo p/ cima).
    Ref: Carini [3] + NBR 6118:2023, sec.21 [1]
    """
    fcd = fck / 1.4 / 10.0
    fyd = fyk / 1.15 / 10.0
    cobr = {"I":2.0,"II":2.5,"III":4.0,"IV":4.5}.get(caa, 4.5)
    h_cm = h_fundo_m * 100
    d = h_cm - cobr - 0.625
    b = 100.0
    gamma_f = 1.4

    PP = 25.0 * h_fundo_m  # kN/m2
    p_agua = GAMMA_AGUA * H_agua   # pressao hidrostatica na base

    # Comb 1 CHEIA: tracao no fundo (p_agua para cima > PP para baixo)
    p_net = gamma_f * (p_agua - PP)  # kN/m2

    lx = min(Lx, Ly)
    Md = p_net * lx**2 / 8   # kNm/m (biapoiada simplificada)

    Md_cm = Md * 100
    if Md_cm < 0.01:
        return {"As_cm2m": 0, "Md": 0, "nota": "PP >= pressao agua"}
    disc = 1 - Md_cm / (0.425 * b * d**2 * fcd)
    if disc < 0:
        return {"erro": "Seção fundo insuficiente"}
    x = 1.25 * d * (1 - math.sqrt(max(0, disc)))
    As = 0.85 * fcd * 0.80 * x * b / fyd
    As_min = max(0.15/100 * b * h_cm, 0.0015 * b * h_cm)

    return dict(
        H_agua=H_agua, lx=lx, h_fundo_m=h_fundo_m,
        p_agua=round(p_agua,2), PP=round(PP,2),
        p_net=round(p_net,2), Md_kNm=round(Md,2),
        As_cm2m=round(max(As, As_min), 2),
        ref="[1] NBR 6118:2023, sec.21 | [3] Carini 2023"
    )
