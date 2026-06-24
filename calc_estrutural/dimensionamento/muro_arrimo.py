# dimensionamento/muro_arrimo.py - Muro de Arrimo em Concreto Armado
#
# REFERENCIAS:
#   [1] BASTOS, P.S.S. (Dr., UNESP) Muros de Arrimo - Apostila CA. 2017
#   [2] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.4, 2014
#   [3] CAPUTO, H.P. (Dr., PUC-Rio) Mecanica dos Solos e suas Aplicacoes. 7.ed, 2008
#   [4] NBR 6118:2023, secao 13.2, 17, 19 | NBR 6120:2019
import math

BIBLIOGRAFIA_MURO = (
    "MURO DE ARRIMO - Referencias:\n"
    "  [1] BASTOS, P.S.S. (Dr., UNESP) Muros de Arrimo - Apostila. 2017\n"
    "  [2] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado. v.4, 2014\n"
    "  [3] CAPUTO, H.P. (Dr., PUC-Rio) Mecanica dos Solos. 7.ed, 2008\n"
    "  [4] NBR 6118:2023, sec.13, 17 | NBR 6120:2019\n"
)

GAMMA_CONCRETO = 25.0  # kN/m3
GAMMA_SOLO_DEFAULT = {
    "areia_solta": 16.0,
    "areia_compacta": 18.0,
    "argila_mole": 15.0,
    "argila_rigida": 18.0,
}


def coef_rankine_ativo(phi_graus):
    """Ka = tan^2(45 - phi/2) | Ref [3] Caputo"""
    phi_rad = math.radians(phi_graus)
    return round(math.tan(math.radians(45 - phi_graus / 2)) ** 2, 4)


def predimensionar_muro(H_m, phi_solo=30.0, gamma_solo=18.0):
    """
    Pre-dimensionamento geometrico do muro de gravidade/flexivel.
    Ref: Bastos [1] + Carini (pratica).
    """
    espessura_base = round(H_m * 0.08 + 0.15, 2)   # h_stem toe
    espessura_topo = round(max(espessura_base * 0.6, 0.15), 2)
    largura_sapata = round(H_m * 0.5, 2)   # B = 0,4 a 0,7 H
    esp_sapata = round(max(H_m * 0.10, 0.20), 2)
    comprimento_calcanheira = round(largura_sapata * 0.55, 2)
    comprimento_ponta = round(largura_sapata - comprimento_calcanheira - espessura_base, 2)
    return dict(
        H=H_m, phi=phi_solo, gamma_solo=gamma_solo,
        espessura_fuste_base=espessura_base,
        espessura_fuste_topo=espessura_topo,
        B_sapata=largura_sapata,
        esp_sapata=esp_sapata,
        comprimento_ponta=comprimento_ponta,
        comprimento_calcanheira=comprimento_calcanheira,
        ref="[1] Bastos(Dr.,UNESP) 2017 + pratica Carini 2023"
    )


def calcular_empuxo(H_m, gamma_solo=18.0, phi=30.0, coesao=0.0, qs_kPa=0.0):
    """
    Empuxo ativo de Rankine (Ref: Caputo [3], Bastos [1]).
    qs = sobrecarga superficial (kN/m2).
    Retorna: resultante Pa, ponto de aplicacao za, distribuicao.
    """
    Ka = coef_rankine_ativo(phi)
    # Triangular (solo sem coesao e sem sobrecarga):
    p_base = Ka * (gamma_solo * H_m + qs_kPa)   # kN/m2
    p_topo = Ka * qs_kPa
    Pa_tri  = 0.5 * Ka * gamma_solo * H_m**2    # kN/m
    Pa_qs   = Ka * qs_kPa * H_m                  # kN/m
    Pa_total = Pa_tri + Pa_qs
    # Ponto de aplicacao
    za_tri = H_m / 3.0
    za_qs  = H_m / 2.0
    za = (Pa_tri * za_tri + Pa_qs * za_qs) / Pa_total if Pa_total > 0 else H_m / 3.0
    return dict(
        Ka=Ka, phi=phi, gamma_solo=gamma_solo,
        p_topo=round(p_topo, 2), p_base=round(p_base, 2),
        Pa_tri=round(Pa_tri, 2), Pa_qs=round(Pa_qs, 2),
        Pa_total=round(Pa_total, 2), za=round(za, 2),
        ref="[3] Caputo(Dr.,PUC-Rio) 2008 + [1] Bastos(Dr.,UNESP) 2017"
    )


def verificar_estabilidade(predim, empuxo, gamma_solo=18.0):
    """
    Verificacao de estabilidade: tombamento e deslizamento.
    Ref: Bastos [1] + Araujo [2]
    """
    H = predim["H"]
    B = predim["B_sapata"]
    Bponta = predim["comprimento_ponta"]
    Bcalc = predim["comprimento_calcanheira"]
    e_fuste = predim["espessura_fuste_base"]
    e_sap = predim["esp_sapata"]

    Pa = empuxo["Pa_total"]
    za = empuxo["za"]

    # Volumes e pesos (por metro linear)
    # Fuste (trapezoidal): area media * gamma
    A_fuste = ((predim["espessura_fuste_base"] + predim["espessura_fuste_topo"]) / 2.0) * (H - e_sap)
    W_fuste = A_fuste * GAMMA_CONCRETO
    x_fuste = Bponta + e_fuste / 2.0  # baricentro

    # Sapata
    W_sap = B * e_sap * GAMMA_CONCRETO
    x_sap = B / 2.0

    # Solo sobre calcanheira
    h_solo = H - e_sap
    W_solo = Bcalc * h_solo * gamma_solo
    x_solo = Bponta + e_fuste + Bcalc / 2.0

    W_total = W_fuste + W_sap + W_solo
    Mt_resist = W_fuste * x_fuste + W_sap * x_sap + W_solo * x_solo
    Mt_acao   = Pa * za  # momento tombador em relacao a ponta da sapata

    FST = Mt_resist / Mt_acao if Mt_acao > 0 else 999

    # Deslizamento (mu aprox. = tg(2/3 * phi))
    phi_r = math.radians(empuxo["phi"])
    mu = math.tan(2/3 * phi_r)
    FSD = (mu * W_total) / Pa if Pa > 0 else 999

    return dict(
        W_total=round(W_total,2), Pa=round(Pa,2),
        FST=round(FST,3), FST_ok=FST>=1.5,
        FSD=round(FSD,3), FSD_ok=FSD>=1.5,
        Mt_resist=round(Mt_resist,2), Mt_acao=round(Mt_acao,2),
        ref="[1] Bastos(Dr.,UNESP) 2017 + [2] Araujo(Dr.,FURG) 2014"
    )


def dimensionar_fuste(predim, empuxo, fck=25.0, fyk=500.0, caa="III"):
    """
    Dimensionamento do fuste do muro (viga em balanco com carga triangular).
    Ref: Bastos [1] + NBR 6118:2023 [4]
    """
    H = predim["H"]
    h_sap = predim["esp_sapata"]
    h_fuste = H - h_sap
    e_base = predim["espessura_fuste_base"] * 100  # cm

    fcd = fck / 1.4 / 10.0
    fyd = fyk / 1.15 / 10.0
    cobr = {"I":2.5,"II":3.0,"III":4.0,"IV":5.0}.get(caa, 4.0)
    d = e_base - cobr - 0.625

    Ka = empuxo["Ka"]
    gamma_solo = empuxo["gamma_solo"]

    # Momento na base do fuste (carga triangular em balanco):
    # Pa = Ka*gamma*h^2/2  (kN/m)  aplicada em h/3
    # Md = Pa * h/3 = Ka*gamma*h^3/6  (kNm/m)  <- Bastos [1] eq.4.12
    gamma_f = 1.4
    Md = gamma_f * Ka * gamma_solo * h_fuste**3 / 6   # kNm/m
    Vd = gamma_f * Ka * gamma_solo * h_fuste**2 / 2   # kN/m

    # Dimensionar armadura vertical
    Md_cm = Md * 100
    b = 100.0
    disc = 1 - Md_cm / (0.425 * b * d**2 * fcd)
    if disc < 0:
        return {"erro": "Fuste muito esbelto - aumentar espessura"}
    x = 1.25 * d * (1 - math.sqrt(max(0, disc)))
    As = 0.85 * fcd * 0.80 * x * b / fyd
    As_min = 0.15/100 * b * e_base
    As_adot = round(max(As, As_min), 2)

    return dict(
        h_fuste=h_fuste, e_base_cm=e_base, d_cm=round(d,1),
        Md_kNm=round(Md,2), Vd_kN=round(Vd,2),
        As_cm2m=As_adot,
        ref="[1] Bastos(Dr.,UNESP) 2017 + [4] NBR 6118:2023, sec.17"
    )
