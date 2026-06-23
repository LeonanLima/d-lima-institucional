# dimensionamento/reservatorio.py - Reservatorios (cheio, vazio, semi-enterrado)
#
# REFERENCIAS:
#   [1] NBR 6118:2023, secao 21 (estruturas sujeitas a liquidos)
#   [2] FUSCO, P.B. (Dr., USP) Estruturas de Concreto: Solicitacoes Tangenciais. 2008
#   [3] CARINI, M.R. (MSc, UFSC) Reservatorios e Piscinas - Notas de Aula. 2023
#   [4] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.3, 2014
import math
from analise.pressoes import (
    pressao_hidrostatica, resultante_hidro,
    combinacoes_reservatorio
)

BIBLIOGRAFIA_RESERVATORIO = (
    "RESERVATORIO - Referencias:\n"
    "  [1] NBR 6118:2023, sec.21 (estruturas em contato c/ liquidos)\n"
    "  [2] FUSCO, P.B. (Dr., USP) Estruturas de Concreto: Sol. Tangenciais. 2008\n"
    "  [3] CARINI, M.R. (MSc, UFSC) Reservatorios - Notas de Aula. 2023\n"
    "  [4] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.3, 2014\n"
)

GAMMA_AGUA = 10.0   # kN/m3

CAA_RESERVATORIO = "IV"   # NBR 6118:2023, sec.21 -> CAA IV obrigatoria
FCK_MIN_RESERVATORIO = 40  # MPa (CAA IV)


def _espessura_parede_minima(H_m, tipo="enterrado"):
    """Espessura minima de paredes (criterio pratico Carini [3])"""
    h = H_m / 10.0   # criterio h >= H/10
    h_min = 0.15 if tipo == "semi" else 0.20
    return round(max(h, h_min), 2)


def predimensionar_reservatorio(Volume_m3, relacao_lh=2.0, n_agua=1.0):
    """
    Pre-dimensionamento de reservatorio retangular.
    relacao_lh = L/H (planta quadrada se L=B)
    Ref: Carini [3] + Araujo [4]
    """
    H = (Volume_m3 / relacao_lh**2) ** (1/3)
    L = relacao_lh * H
    h_parede = _espessura_parede_minima(H, "enterrado")
    h_fundo   = round(max(H / 15, 0.12), 2)
    h_tampa   = round(max(H / 20, 0.10), 2)
    return dict(
        Volume_m3=Volume_m3, H=round(H,2), L=round(L,2), B=round(L,2),
        h_parede_m=h_parede, h_fundo_m=h_fundo, h_tampa_m=h_tampa,
        CAA=CAA_RESERVATORIO, fck_min=FCK_MIN_RESERVATORIO,
        ref="[3] Carini(2023) + [4] Araujo(Dr.,FURG) 2014"
    )


def _pressao_combinacao(comb, z, H):
    """Pressao hidrostatica na cota z (do fundo) para cada combinacao"""
    h_agua = H - z
    p_hidro = max(0, GAMMA_AGUA * h_agua)
    return p_hidro


def paredes_dimensionar(H_m, L_m, h_par_m, fck=40.0, fyk=500.0, caa="IV"):
    """
    Dimensionamento das paredes (modelo de placa plana, solicitacao por pressao
    hidrostatica). NBR 6118:2023, sec.21 | Ref [1][2][3]

    Modelo simplificado: parede vertical com base engastada e topo livre
    (balanço vertical) para combinacao mais desfavoravel.
    """
    fcd = fck / 1.4 / 10.0   # kN/cm2
    fyd = fyk / 1.15 / 10.0
    cobr = {"I":2.0,"II":2.5,"III":4.0,"IV":4.5}.get(caa, 4.5)
    h_cm = h_par_m * 100
    d = h_cm - cobr - 0.625

    # COMB 1 — reservatorio CHEIO, sem solo (pior para parede interna)
    # pressao maxima no fundo: p = gamma * H * gamma_f
    gamma_f = 1.4   # NBR 6118:2023, sec.11.2
    p_max = GAMMA_AGUA * H_m * gamma_f    # kN/m2

    # Momento na base (viga em balanco vertical por metro de largura):
    # M = p_tri * H / 3   (carga triangular)
    Md_kNm = p_max * H_m**2 / 6   # kNm/m (balanço com carga triangular)
    Vd_kN  = p_max * H_m / 2      # kN/m

    # Forca de tracao circunferencial (anel horizontal, raio R=L/2):
    # Nφ = p * R = p * L/2  [kN/m]
    R = L_m / 2.0
    Nd_anel = p_max * R    # kN/m

    # ELU - Flexao vertical (armadura vertical interna)
    Md_cm = Md_kNm * 100  # kNcm
    b = 100.0
    disc = 1 - Md_cm / (0.425 * b * d**2 * fcd)
    x = 1.25 * d * (1 - math.sqrt(max(0, disc)))
    As_vert = 0.85 * fcd * 0.80 * x * b / fyd   # cm2/m

    # ELU - Tracao (anel horizontal) — armadura horizontal
    As_horiz = Nd_anel / fyd * 10  # cm2/m (fyd em kN/cm2)

    # Armadura minima NBR 6118:2023, sec.21.3 — majorada vs. lajes normais
    As_min = max(0.15/100 * b * h_cm, 0.0015 * b * h_cm)

    # ELS - Fissuração (NBR 6118:2023, sec.21.3.3 - wlim=0,1mm CAA IV)
    w_lim = 0.10   # mm (contato com agua)

    return dict(
        combinacao="CHEIO (C1)",
        H=H_m, L=L_m, h_par_m=h_par_m,
        p_max_kNm2=round(p_max,2),
        Md_kNm=round(Md_kNm,2), Vd_kN=round(Vd_kN,2),
        Nd_anel_kNm=round(Nd_anel,2),
        As_vert_cm2m=round(max(As_vert, As_min), 2),
        As_horiz_cm2m=round(max(As_horiz, As_min), 2),
        As_min=round(As_min, 2),
        w_lim=w_lim,
        nota_els="Verificar fissuração wk ≤ 0,10 mm (NBR 6118:2023, sec.21.3.3)",
        ref="[1] NBR 6118:2023, sec.21 | [2] Fusco(Dr.,USP) 2008 | [3] Carini 2023"
    )


def fundo_dimensionar(H_m, L_m, B_m, h_fundo_m, fck=40.0, fyk=500.0, caa="IV"):
    """
    Dimensionamento do fundo do reservatorio (laje macica).
    Combinacoes cheio e vazio (NBR 6118:2023, sec.21) | Ref [1][3]
    """
    fcd = fck / 1.4 / 10.0
    fyd = fyk / 1.15 / 10.0
    h_cm = h_fundo_m * 100
    cobr = {"I":2.0,"II":2.5,"III":4.0,"IV":4.5}.get(caa, 4.5)
    d = h_cm - cobr - 0.625

    # Carga no fundo: pressao da agua
    gamma_f = 1.4
    p_agua = GAMMA_AGUA * H_m * gamma_f   # kN/m2

    # Peso proprio da laje de fundo
    PP = 25.0 * h_fundo_m * gamma_f   # kN/m2

    # COMB 1 CHEIO: p_agua (para cima) - PP (para baixo) → Tensao de tracao na fibra inf.
    p_net_cheio = p_agua - PP   # carga liquida de tracao no fundo

    # COMB 2 VAZIO: apenas PP (compressao, sem pressao hidro) → laje carregada pelo solo
    # (para reservatorio enterrado, solo empurra de baixo) - conservador: apenas PP
    p_net_vazio = PP

    # Momento simples para laje biapoiada:
    lx = min(L_m, B_m)
    Md_cheio = p_net_cheio * lx**2 / 8  # kNm/m
    Md_vazio  = p_net_vazio  * lx**2 / 8

    def armar(Md):
        Md_cm = abs(Md) * 100
        if Md_cm < 0.1: return {"As_cm2": 0}
        disc = 1 - Md_cm / (0.425*100*d**2*fcd)
        if disc < 0: return {"As_cm2": -1, "erro": "Aumentar h_fundo"}
        x = 1.25*d*(1-math.sqrt(max(0,disc)))
        As = 0.85*fcd*0.80*x*100/fyd
        As_min = max(0.15/100*100*h_cm, 0.0015*100*h_cm)
        return {"As_cm2": round(max(As, As_min), 2), "x_cm": round(x,2)}

    return dict(
        lx=lx, h_fundo_m=h_fundo_m,
        Md_cheio=round(Md_cheio,2), arm_cheio=armar(Md_cheio),
        Md_vazio=round(Md_vazio,2),  arm_vazio=armar(Md_vazio),
        ref="[1] NBR 6118:2023, sec.21 | [3] Carini 2023"
    )


def imprimir_reservatorio(predim, par, fund):
    print("\n" + "="*60)
    print("DIMENSIONAMENTO - RESERVATORIO | NBR 6118:2023, sec.21")
    print("="*60)
    print("\n--- PRE-DIMENSIONAMENTO ---")
    for k, v in predim.items(): print(f"  {k}: {v}")
    print("\n--- PAREDES ---")
    for k, v in par.items(): print(f"  {k}: {v}")
    print("\n--- FUNDO ---")
    for k, v in fund.items(): print(f"  {k}: {v}")
    print()
    print(BIBLIOGRAFIA_RESERVATORIO)
