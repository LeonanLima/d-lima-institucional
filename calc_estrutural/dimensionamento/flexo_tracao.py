# dimensionamento/flexo_tracao.py - Flexo-tracao normal com armaduras assimetricas
#
# Metodo do Prof. Matheus Carini, "Reservatorios Elevados", slides 25-31.
# Usado nas paredes de reservatorio/piscina: a flexao da placa (Bares) combina
# com a tracao do anel -> flexo-tracao. Reduz-se a flexao simples quando Nd->0.
#
# Convencao: Md [kNm/m] = modulo do momento de calculo na direcao analisada;
#            Nd [kN/m]  = forca normal de TRACAO de calculo (positiva).
import math

ALPHA_C = 0.85   # efeito Rusch
ETA_C = 1.0      # fator de fragilidade (fck <= 50 MPa)
LAMBDA = 0.80    # altura do bloco retangular (fck <= 50 MPa)

# Taxa minima de armadura rho_min (%) - NBR 6118:2023 / Carini slide 31 (CA-50, gamma_c=1,4)
RHO_MIN = {20: 0.150, 25: 0.150, 30: 0.150, 35: 0.164, 40: 0.179,
           45: 0.194, 50: 0.208, 55: 0.211, 60: 0.219}


def as_min_flexo_tracao(fck, b_cm, h_cm):
    """As,min [cm2] = rho_min * Ac (Carini slide 31). Interpola rho_min se preciso."""
    chaves = sorted(RHO_MIN)
    if fck <= chaves[0]:
        rho = RHO_MIN[chaves[0]]
    elif fck >= chaves[-1]:
        rho = RHO_MIN[chaves[-1]]
    else:
        lo = max(k for k in chaves if k <= fck)
        hi = min(k for k in chaves if k >= fck)
        rho = RHO_MIN[lo] if lo == hi else (
            RHO_MIN[lo] + (RHO_MIN[hi] - RHO_MIN[lo]) * (fck - lo) / (hi - lo))
    return round(rho / 100.0 * b_cm * h_cm, 2)


def dimensionar_flexo_tracao(Md_kNm, Nd_kN, b_cm, d_cm, d_linha_cm,
                             fck, fyk=500.0):
    """Armadura de flexo-tracao normal (armaduras assimetricas), Carini slides 25-31.

    Retorna dict com:
      caso     : "flexao_simples" | "grande_simples" | "grande_dupla" | "pequena"
      As1_cm2  : armadura da face mais tracionada [cm2/m]
      As2_cm2  : armadura da face oposta [cm2/m] (0 quando nao requerida)
      e0, e1, x_cm, Md_lim : grandezas intermediarias (cm / kNcm)
    """
    fcd = fck / 1.4 / 10.0   # kN/cm2
    fyd = fyk / 1.15 / 10.0  # kN/cm2
    Md_cm = abs(Md_kNm) * 100.0   # kN*cm/m
    Nd = abs(Nd_kN)               # kN/m (tracao)
    z = d_cm - d_linha_cm         # (d - d')
    K = ALPHA_C * ETA_C * LAMBDA * fcd * b_cm   # = 0,68*fcd*b

    # Tracao desprezivel -> flexao simples pura
    if Nd < 1e-6:
        disc = d_cm**2 - 2 * LAMBDA * Md_cm / K
        if disc < 0:
            return {"caso": "flexao_simples", "erro": "Secao insuficiente"}
        x = (d_cm - math.sqrt(disc)) / LAMBDA
        return dict(caso="flexao_simples", e0=None, e1=None, x_cm=round(x, 3),
                    As1_cm2=round(K * x / fyd, 2), As2_cm2=0.0, Md_lim=None)

    e0 = Md_cm / Nd   # cm

    if e0 > z / 2:
        # GRANDE excentricidade (slides 27-29)
        e1 = e0 - z / 2
        xlim = 0.45 * d_cm if fck <= 50 else 0.35 * d_cm
        Md_lim = ALPHA_C * ETA_C * fcd * b_cm * LAMBDA * xlim * (d_cm - LAMBDA * xlim / 2)
        if Nd * e1 <= Md_lim:
            # armadura SIMPLES (slide 28): Nd*e1 = K*x*(d - 0,5*lambda*x)
            disc = d_cm**2 - 2 * LAMBDA * (Nd * e1) / K
            if disc < 0:
                return {"caso": "grande_simples", "erro": "Secao insuficiente"}
            x = (d_cm - math.sqrt(disc)) / LAMBDA
            As1 = (Nd + K * x) / fyd
            return dict(caso="grande_simples", e0=round(e0, 2), e1=round(e1, 2),
                        x_cm=round(x, 3), Md_lim=round(Md_lim, 1),
                        As1_cm2=round(As1, 2), As2_cm2=0.0)
        # armadura DUPLA (slide 29) - parede fina raramente cai aqui
        return {"caso": "grande_dupla", "e0": round(e0, 2), "e1": round(e1, 2),
                "Md_lim": round(Md_lim, 1),
                "nota": "Nd*e1 > Md,lim: requer armadura dupla - aumentar espessura"}

    # PEQUENA excentricidade (slide 30): secao toda tracionada
    e1 = z / 2 - e0
    e2 = z / 2 + e0
    As1 = Nd * e2 / (fyd * z)   # face mais tracionada
    As2 = Nd * e1 / (fyd * z)
    return dict(caso="pequena", e0=round(e0, 2), e1=round(e1, 2),
                As1_cm2=round(As1, 2), As2_cm2=round(As2, 2), Md_lim=None)
