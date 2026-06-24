"""
NBR 6118:2023 - Constantes, tabelas e formulas normativas
Material do Prof. Matheus Roman Carini - Estrutural na Real
"""
import math

# COEFICIENTES DE MINORACAO (NBR 6118:2023, par.12.3)
GAMMA_C = 1.4   # concreto
GAMMA_S = 1.15  # aco

def concreto(fck_MPa: float) -> dict:
    """
    Propriedades do concreto para fck ate 50 MPa.
    fck  [MPa] - Resistencia caracteristica a compressao (NBR 6118:2023, par.8.2.3.1)
    fcd  [MPa] - Resistencia de calculo = fck / gamma_c
    fctm [MPa] - Resistencia media a tracao = 0,3 x fck^(2/3)
    fctk_inf [MPa] - Resistencia inferior = 0,7 x fctm
    fctd [MPa] - Resistencia de calculo a tracao = fctk_inf / gamma_c
    Eci  [MPa] - Modulo tangente inicial = 5600 x sqrt(fck)   (eq.8.3)
    Ecs  [MPa] - Modulo secante = alpha_E x Eci
    ecu  [prom] - Deformacao ultima = 3,5 por mil  (diagrama parabola-retangulo)
    ec2  [prom] - Inicio do patamar plastico = 2,0 por mil
    """
    fck = fck_MPa
    fcd = round(fck / GAMMA_C, 2)
    fctm = round(0.3 * fck**(2/3), 3)
    fctk_inf = round(0.7 * fctm, 3)
    fctd = round(fctk_inf / GAMMA_C, 3)
    Eci = round(5600 * math.sqrt(fck), 0)
    alphaE = 1.0 if fck <= 45 else round(0.9 - 0.01*(fck - 45), 2)
    Ecs = round(alphaE * Eci, 0)
    return dict(fck=fck, fcd=fcd, fctm=fctm, fctk_inf=fctk_inf, fctd=fctd,
                Eci=Eci, Ecs=Ecs, ecu=3.5, ec2=2.0,
                lambda_coef=0.8, alpha_c=1.0, alphaE=alphaE)

def aco(tipo: str = "CA-50") -> dict:
    """
    Propriedades do aco (NBR 6118:2023, par.8.3.6):
    fyk  [MPa] - Resistencia caracteristica de escoamento
    fyd  [MPa] - Resistencia de calculo = fyk / gamma_s
    Es   [MPa] - Modulo de elasticidade = 210.000 MPa
    eyd  [prom] - Deformacao de escoamento = fyd / Es (em por mil)
    """
    dados = {"CA-50": 500, "CA-60": 600}
    fyk = dados.get(tipo, 500)
    Es = 210_000
    fyd = round(fyk / GAMMA_S, 2)
    eyd = round(fyd / Es * 1000, 4)
    return dict(tipo=tipo, fyk=fyk, fyd=fyd, Es=Es, eyd=eyd)

# COBRIMENTO NOMINAL (NBR 6118:2023, Tabela 7.2)
# CAA: (cobrimento_viga_laje_cm, cobrimento_pilar_cm)
COBRIMENTO_NOMINAL = {
    "I":   {"laje_viga": 2.0, "pilar": 2.5},
    "II":  {"laje_viga": 2.5, "pilar": 3.0},
    "III": {"laje_viga": 3.5, "pilar": 4.0},
    "IV":  {"laje_viga": 4.5, "pilar": 5.0},
}

# AREAS DE BARRAS [cm2] (CA-50 e CA-60)
AREA_BARRA = {
    6.3: 0.312, 8.0: 0.503, 10.0: 0.785, 12.5: 1.227,
    16.0: 2.011, 20.0: 3.142, 22.0: 3.801, 25.0: 4.909, 32.0: 8.042,
}
BITOLAS = sorted(AREA_BARRA.keys())

def escolher_barras(As_cm2: float) -> list:
    """Sugere combinacoes de barras para atingir As_cm2."""
    sugestoes = []
    for phi in BITOLAS:
        a = AREA_BARRA[phi]
        n = max(1, math.ceil(As_cm2 / a))
        As_tot = round(n * a, 3)
        exc = round((As_tot - As_cm2) / As_cm2 * 100, 1)
        sugestoes.append({"n": n, "phi": phi, "As": As_tot, "excesso_pct": exc})
    return sorted(sugestoes, key=lambda x: abs(x["excesso_pct"]))[:6]

# COMBINACAO DE ACOES - ELU NORMAL (NBR 6118:2023, par.11.7)
GAMMA_G = 1.4
GAMMA_Q = 1.4

def fd_elu(gk: float, qk: float) -> float:
    """fd = 1,4 gk + 1,4 qk  (ELU, combinacao normal)"""
    return GAMMA_G * gk + GAMMA_Q * qk

PSI2 = {"residencial": 0.3, "comercial": 0.4, "biblioteca": 0.6,
        "garagem": 0.6, "cobertura": 0.0}

def fd_els(gk: float, qk: float, uso: str = "residencial") -> float:
    """fd,ser = gk + psi2 x qk  (ELS quase-permanente)"""
    return gk + PSI2.get(uso, 0.3) * qk

# ADERENCIA - fbd (NBR 6118:2023, par.9.3.2.1)
def fbd_calc(fck_MPa: float, boa_aderencia: bool = True) -> float:
    """
    Resistencia de aderencia de calculo [MPa]
    fbd = eta1 x eta2 x eta3 x fctd
    eta1 = 1,0 (boa) | 0,7 (ma aderencia)
    """
    fctd = concreto(fck_MPa)["fctd"]
    eta1 = 1.0 if boa_aderencia else 0.7
    return round(eta1 * 1.0 * 1.0 * fctd, 4)

def lb_basico(phi_mm: float, fck_MPa: float, tipo_aco: str = "CA-50",
              boa_aderencia: bool = True) -> float:
    """
    Comprimento basico de ancoragem [cm] - NBR 6118:2023, par.9.4.2.2
    lb,bas = (phi/4) x (fyd / fbd)
    phi [mm], resultado em [cm]
    """
    a = aco(tipo_aco)
    fb = fbd_calc(fck_MPa, boa_aderencia)
    return round((phi_mm / 10 / 4) * (a["fyd"] / (fb * 10)), 1)

def lb_necessario(phi_mm: float, fck_MPa: float, tipo_aco: str = "CA-50",
                  boa_aderencia: bool = True,
                  As_calc: float = None, As_ef: float = None) -> float:
    """
    Comprimento necessario de ancoragem [cm] - NBR 6118:2023, par.9.4.2.5
    lb,nec = lb,bas x (As,calc / As,ef)  >= minimo
    """
    lb = lb_basico(phi_mm, fck_MPa, tipo_aco, boa_aderencia)
    ratio = (As_calc / As_ef) if (As_calc and As_ef and As_ef > 0) else 1.0
    lb_n = lb * ratio
    phi_cm = phi_mm / 10
    lb_min = max(0.3 * lb, 10 * phi_cm, 10.0)
    return round(max(lb_n, lb_min), 1)

# ESBELTEZ - PILAR (NBR 6118:2023, par.15.8.2)
def indice_esbeltez(le_cm: float, h_cm: float) -> float:
    """
    lambda = le / i    onde i = h / sqrt(12) = h / 3,464
    le  [cm] - comprimento equivalente de flambagem
    h   [cm] - dimensao da secao na direcao analisada
    """
    i = h_cm / math.sqrt(12)
    return round(le_cm / i, 2)

def lambda1_limite(e1A_cm: float, h_cm: float, alpha_b: float = 1.0) -> float:
    """
    lambda1 = 25 + 12,5 x (alpha_b x e1A / h)   com 35 <= lambda1 <= 90
    alpha_b = 0,6 + 0,4 x (e1B / e1A)  >= 0,40  (pilar biapoiado)
    alpha_b = 1,0  (pilar em balanco ou com excentricidade minima)
    """
    val = 25 + 12.5 * (alpha_b * e1A_cm / h_cm)
    return round(max(35.0, min(90.0, val)), 2)

def e1_minima(h_cm: float) -> float:
    """
    Excentricidade minima de 1a ordem [cm] - NBR 6118:2023, par.15.8.3.3.1
    e1,min = 1,5 + 0,03 x h  [cm]
    """
    return round(1.5 + 0.03 * h_cm, 2)

def e2_pilar_padrao(lambda_: float, h_cm: float, nu: float) -> float:
    """
    Excentricidade de 2a ordem pelo metodo pilar-padrao [cm]
    NBR 6118:2023, par.15.8.3.3.2
    e2 = 0,0005 x lambda^2 x h / (0,5 + nu)
    nu = Nd / (Ac x fcd) - forca normal adimensionalizada
    """
    return round(0.0005 * lambda_**2 * h_cm / (0.5 + nu), 2)

def as_min_pilar(Nd_kN: float, fyd_MPa: float, Ac_cm2: float) -> float:
    """
    Armadura minima no pilar [cm2] - NBR 6118:2023, par.18.4.1.1
    As,min = max(0,15 x Nd/fyd ; 0,4% x Ac)
    Nd [kN], fyd [MPa], resultado em [cm2]
    """
    a = 0.15 * (Nd_kN * 10) / fyd_MPa
    b = 0.004 * Ac_cm2
    return round(max(a, b), 2)

def as_max_pilar(Ac_cm2: float, emenda: bool = False) -> float:
    """
    Armadura maxima no pilar [cm2] - NBR 6118:2023, par.18.4.1.1
    As,max = 8% x Ac (secao corrente) | 4% x Ac (emendas)
    """
    return round((0.04 if emenda else 0.08) * Ac_cm2, 2)

def estribo_pilar(phi_long_mm: float, b_min_cm: float) -> dict:
    """
    Estribos de pilares - NBR 6118:2023, par.18.4.2
    phi_e >= max(5mm ; phi_long/4)
    s <= min(b_menor ; 20 x phi_long ; 30 cm)
    s_red = 0,6 x s (emendas, nos, fundacao)
    """
    phi_e = max(5.0, round(phi_long_mm / 4, 1))
    s_max = min(b_min_cm, 20 * phi_long_mm / 10, 30.0)
    s_red = round(0.6 * s_max, 0)
    return {"phi_estribo_mm": phi_e, "s_max_cm": round(s_max, 0), "s_red_cm": s_red}

def secao_retangular(b_cm: float, h_cm: float) -> dict:
    """Propriedades geometricas de secao retangular [cm / cm2]."""
    A = b_cm * h_cm
    Iy = h_cm * b_cm**3 / 12
    Iz = b_cm * h_cm**3 / 12
    iy = math.sqrt(Iy / A)
    iz = math.sqrt(Iz / A)
    return dict(A=A, Iy=Iy, Iz=Iz, iy=round(iy,3), iz=round(iz,3),
                b=b_cm, h=h_cm)

# ABERTURA LIMITE DE FISSURA (NBR 6118:2023, Tabela 13.4)
WK_LIM = {"I": 0.40, "II": 0.30, "III": 0.20, "IV": 0.10}
