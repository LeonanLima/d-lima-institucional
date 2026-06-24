# analise/pressoes.py - Pressoes de Terra e Hidrostaticas
#
# REFERENCIAS:
#   DAS, B.M. (Dr.) Principios de Engenharia Geotecnica. 8.ed. Cengage, 2014.
#   MASSAD, F. (Dr., POLI-USP) Obras de Terra. 2.ed. Oficina de Textos, 2010.
#   PORTO, R.M. (Dr., USP-SCC) Hidraulica Basica. 4.ed. EESC-USP, 2006.
#   NBR 6118:2023, secao 21 - Estruturas em contato com liquidos.
#   NBR 6120:2019, Tabela 2 - Pesos especificos de materiais.
import math


# Peso especifico da agua [kN/m3] - NBR 6120:2019
GAMMA_AGUA = 10.0

# Pesos especificos de solos tipicos [kN/m3] - Das (2014)
GAMMA_SOLO = {
    "areia_solta":   17.0,
    "areia_compacta": 20.0,
    "argila_mole":   15.0,
    "argila_rigida": 19.0,
    "solo_natural":  18.0,    # valor tipico para calculo
}


# ============================================================
# PRESSAO DE TERRA - TEORIA DE RANKINE (Das, 2014, Cap. 13)
# ============================================================

def coef_rankine_ativo(phi_graus: float) -> float:
    # Coeficiente de empuxo ativo de Rankine.
    # Ka = tan^2(45 - phi/2)
    # Ref: Das (2014), equacao 13.4.
    # phi = angulo de atrito interno do solo [graus]
    phi = math.radians(phi_graus)
    Ka = math.tan(math.radians(45) - phi/2) ** 2
    return round(Ka, 4)


def coef_rankine_passivo(phi_graus: float) -> float:
    # Coeficiente de empuxo passivo de Rankine.
    # Kp = tan^2(45 + phi/2)
    phi = math.radians(phi_graus)
    Kp = math.tan(math.radians(45) + phi/2) ** 2
    return round(Kp, 4)


def pressao_ativa_rankine(z: float, gamma_solo: float, Ka: float,
                           coesao: float = 0.0) -> float:
    # Pressao ativa de terra na profundidade z [m].
    # sigma_a = Ka * gamma * z - 2c * sqrt(Ka)
    # Ref: Das (2014), equacao 13.5.
    # Retorna pressao [kN/m2] (positiva = empuxo sobre a estrutura)
    sigma = Ka * gamma_solo * z - 2 * coesao * math.sqrt(Ka)
    return max(0.0, round(sigma, 3))   # pressao nao pode ser negativa


def perfil_pressao_terra(H: float, gamma_solo: float, phi_graus: float,
                          coesao: float = 0.0, n_pontos: int = 20) -> list:
    # Perfil da pressao de terra ao longo da altura H [m].
    # Retorna lista de (z, sigma_a) para plotagem e calculo.
    Ka = coef_rankine_ativo(phi_graus)
    pontos = []
    for i in range(n_pontos + 1):
        z = H * i / n_pontos
        s = pressao_ativa_rankine(z, gamma_solo, Ka, coesao)
        pontos.append((round(z, 3), s))
    return pontos


def resultante_empuxo(H: float, gamma_solo: float, phi_graus: float,
                       coesao: float = 0.0) -> dict:
    # Resultante do empuxo ativo sobre altura H [m].
    # Para solo sem coesao: Pa = Ka * gamma * H^2 / 2, a H/3 da base.
    # Ref: Das (2014), equacao 13.11.
    Ka = coef_rankine_ativo(phi_graus)

    # Verificar profundidade de tensao nula (para solos coesivos)
    if coesao > 0:
        z0 = 2 * coesao / (gamma_solo * math.sqrt(Ka))
    else:
        z0 = 0.0

    H_ativo = max(0.0, H - z0)   # altura com pressao positiva
    Pa = 0.5 * Ka * gamma_solo * H_ativo**2   # [kN/m]
    y_Pa = H_ativo / 3.0                       # ponto de aplicacao acima da base

    return {
        "Ka": Ka,
        "z0_m": round(z0, 3),
        "H_ativo_m": round(H_ativo, 3),
        "Pa_kNm": round(Pa, 3),
        "y_Pa_m": round(y_Pa, 3),
    }


# ============================================================
# PRESSAO HIDROSTATICA (Porto, 2006; NBR 6118:2023 sec.21)
# ============================================================

def pressao_hidrostatica(h: float, gamma_liq: float = None) -> float:
    # Pressao hidrostatica na profundidade h [m].
    # p = gamma_liq * h
    # Ref: Porto (2006), cap. 2.
    if gamma_liq is None:
        gamma_liq = GAMMA_AGUA
    return round(gamma_liq * h, 3)   # [kN/m2]


def perfil_pressao_hidro(H: float, gamma_liq: float = None,
                          n_pontos: int = 20) -> list:
    # Perfil triangular de pressao hidrostatica de 0 ate H.
    if gamma_liq is None:
        gamma_liq = GAMMA_AGUA
    return [(round(H * i/n_pontos, 3),
             round(gamma_liq * H * i/n_pontos, 3))
            for i in range(n_pontos + 1)]


def resultante_hidro(H: float, L: float = 1.0,
                     gamma_liq: float = None) -> dict:
    # Resultante da pressao hidrostatica sobre parede de altura H.
    # Fh = gamma * H^2 / 2 [kN/m] (por metro de largura)
    # Ponto de aplicacao: H/3 da base.
    # Ref: Porto (2006), cap. 2 | NBR 6118:2023 sec.21.
    if gamma_liq is None:
        gamma_liq = GAMMA_AGUA
    Fh = 0.5 * gamma_liq * H**2 * L   # [kN]
    y_Fh = H / 3.0

    return {
        "gamma_liq": gamma_liq,
        "H_m": H,
        "Fh_kN": round(Fh, 3),
        "y_Fh_m": round(y_Fh, 3),
    }


# ============================================================
# COMBINACOES PARA ESTRUTURAS HIDRAULICAS (NBR 6118:2023 sec.21)
# ============================================================

def combinacoes_reservatorio(H_agua: float,
                              H_solo: float = 0.0,
                              phi_solo: float = 30.0,
                              gamma_solo_val: float = 18.0) -> dict:
    # Combinacoes criticas para reservatorio (NBR 6118:2023, sec.21):
    #   Combinacao 1 (CHEIO): pressao interna + sem empuxo externo
    #   Combinacao 2 (VAZIO): sem pressao interna + empuxo externo de terra
    #   Combinacao 3 (CHEIO + SOLO): pressao interna + empuxo externo
    # Ref: ARAUJO, J.M. (Dr., FURG) Estruturas de Concreto Armado. 2014.

    hidro_interno = resultante_hidro(H_agua)
    empuxo_externo = resultante_empuxo(H_solo, gamma_solo_val, phi_solo) if H_solo > 0 else None

    return {
        "C1_cheio": {
            "descricao": "RESERVATORIO CHEIO - sem empuxo externo (critico para trecao interna)",
            "pressao_interna": hidro_interno,
            "empuxo_externo": None,
            "gamma_f1": 1.4,   # gamma_f1 para liquidos (NBR 6120:2019 Tab.6)
        },
        "C2_vazio": {
            "descricao": "RESERVATORIO VAZIO - so empuxo de terra (critico para tracao externa)",
            "pressao_interna": None,
            "empuxo_externo": empuxo_externo,
            "gamma_f1": 1.4,
        },
        "C3_cheio_solo": {
            "descricao": "RESERVATORIO CHEIO + empuxo de solo",
            "pressao_interna": hidro_interno,
            "empuxo_externo": empuxo_externo,
            "gamma_f1": 1.4,
        },
    }
