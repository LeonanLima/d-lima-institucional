# dimensionamento/predim.py - Pre-dimensionamento Estrutural
#
# REFERENCIAS:
#   [1] NBR 6118:2023, sec.13.2 - Dimensoes minimas
#   [2] CARINI, M.R. (MSc, UFSC) Curso Estrutural na Real, 2023
#   [3] BASTOS, P.S.S. (Dr., UNESP) Apostilas Concreto Armado, 2017
#   [4] FUSCO, P.B. (Dr., USP) Tecnica de Armar Estruturas, 1995
#   [5] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado, 2014
import math

BIBLIOGRAFIA_PREDIM = (
    "PRE-DIMENSIONAMENTO - Referencias:\n"
    "  [1] NBR 6118:2023, sec.13.2\n"
    "  [2] CARINI, M.R. (MSc, UFSC) Curso Estrutural na Real, 2023\n"
    "  [3] BASTOS, P.S.S. (Dr., UNESP) Apostilas CA, 2017\n"
    "  [4] FUSCO, P.B. (Dr., USP) Tecnica de Armar Estruturas, 1995\n"
    "  [5] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado, 2014\n"
)


def predimensionar_laje(lx: float, ly: float, uso: str = "residencial") -> dict:
    # Pre-dimensionamento da espessura da laje.
    # Ref: Carini (2023); NBR 6118:2023, sec.13.2.4.
    relacao = ly / lx
    bidirecional = relacao <= 2.0
    div = 38.0 if bidirecional else 28.0
    h_calc = lx / div   # metros
    h_cm = max(math.ceil(h_calc * 100), 8)
    h_min = {"residencial": 8, "comercial": 8, "cobertura": 7,
             "garagem": 10, "piscina": 15, "reservatorio": 15}.get(uso, 8)
    h_adotado = max(h_cm, h_min)
    return {
        "lx_m": lx, "ly_m": ly,
        "relacao_ly_lx": round(relacao, 2),
        "tipo": "BIDIRECIONAL" if bidirecional else "UNIDIRECIONAL",
        "h_calc_cm": round(h_calc * 100, 1),
        "h_min_norma_cm": h_min,
        "h_adotado_cm": h_adotado,
        "ref": "[2] Carini (2023) + [1] NBR 6118:2023, sec.13.2.4",
    }


def predimensionar_viga(L: float, tipo: str = "continua",
                        bloco_cm: int = 14) -> dict:
    # Pre-dimensionamento da secao da viga.
    # Ref: Carini (2023); Bastos (Dr., UNESP) 2017; NBR 6118:2023, sec.13.2.2.
    div = {"simples": 10, "continua": 12, "balanco": 5}.get(tipo, 10)
    h_calc = L / div
    h_cm = max(math.ceil(h_calc * 100 / 5) * 5, 25)
    bw_cm = bloco_cm
    PP = bw_cm/100 * h_cm/100 * 25.0
    return {
        "L_m": L, "tipo": tipo, "bw_cm": bw_cm,
        "h_calc_cm": round(h_calc * 100, 1),
        "h_adotado_cm": h_cm,
        "PP_kNm": round(PP, 2),
        "relacao_Lh": round(L / (h_cm/100), 1),
        "ref": "[3] Bastos (Dr., UNESP) 2017 + [1] NBR 6118:2023, sec.13.2.2",
    }


def predimensionar_pilar(Nk_kN: float, fck_MPa: float = 25.0,
                          tipo: str = "intermediario") -> dict:
    # Pre-dimensionamento da secao do pilar.
    # Ref: Carini (2023); Araujo, J.M. (Dr., FURG) 2014; NBR 6118:2023, sec.13.2.3.
    fat = {"intermediario": 1.0, "extremidade": 1.4, "canto": 1.8}.get(tipo, 1.0)
    Ac_min = fat * Nk_kN * 10 / (0.42 * fck_MPa)
    secoes = [(14,14),(14,19),(14,30),(14,40),(14,50),
              (19,19),(19,30),(19,40),(19,50),
              (20,20),(20,30),(20,40),(20,50),(20,60),
              (25,25),(25,40),(25,50),(25,60),
              (30,30),(30,40),(30,50),(30,60),(30,70)]
    sug = [(b, h, b*h) for b, h in secoes if b*h >= Ac_min]
    m = sug[0] if sug else (None, None, None)
    return {
        "Nk_kN": Nk_kN, "tipo": tipo, "fat": fat, "fck_MPa": fck_MPa,
        "Ac_min_cm2": round(Ac_min, 0),
        "b_cm": m[0], "h_cm": m[1], "Ac_cm2": m[2],
        "outras": sug[:4],
        "ok_dim_min": m[0] >= 19 if m[0] else False,
        "ref": "[2] Carini (2023) + [5] Araujo (Dr., FURG) 2014 + [1] NBR 6118:2023, sec.13.2.3",
    }


def predimensionar_reservatorio(volume_m3: float,
                                 relacao_l_h: float = 2.0) -> dict:
    # Pre-dimensionamento de reservatorio retangular.
    # Ref: Araujo, J.M. (Dr., FURG) Estruturas de Concreto Armado. 2014.
    H = (volume_m3 / relacao_l_h) ** (1/3)
    L = relacao_l_h * H
    h_par_cm = max(math.ceil(H / 12 * 100 / 5) * 5, 15)
    h_fund_cm = max(math.ceil(H / 15 * 100 / 5) * 5, 15)
    return {
        "volume_m3": volume_m3,
        "H_agua_m": round(H, 2), "L_m": round(L, 2), "B_m": round(H, 2),
        "h_parede_cm": h_par_cm, "h_fundo_cm": h_fund_cm,
        "obs": "CAA IV obrigatoria (NBR 6118:2023, sec.6.4) | wk <= 0,1mm",
        "ref": "[5] Araujo (Dr., FURG) 2014 + [1] NBR 6118:2023, sec.21",
    }


def imprimir_predim(tipo: str, res: dict):
    print("\n" + "="*55)
    print(f"PRE-DIMENSIONAMENTO - {tipo.upper()}")
    print("="*55)
    for k, v in res.items():
        if k != "outras":
            print(f"  {k}: {v}")
    print()
    print(BIBLIOGRAFIA_PREDIM)
