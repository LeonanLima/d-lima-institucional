# core/fissuracao.py - Abertura de fissuras wk (ELS-W), NBR 6118:2023 sec.17.3.3.2
#
# Motor PURO e testavel: nao depende de Streamlit nem de I/O. Consumido por
# reservatorio/piscina (onde o limite e wk <= 0,10 mm, CAA IV / sec.21.3.3)
# e disponivel para vigas/lajes (wlim por CAA, Tabela 13.4).
#
# Separa duas responsabilidades:
#   1) tensao_aco_estadio2 -> sigma_s no Estadio II (secao fissurada, flexao).
#   2) abertura_wk          -> wk a partir de sigma_s, phi e rho_r (a fisica da
#                              norma, independente da geometria de envolvimento).
# A geometria do concreto de envolvimento (Acri) fica em helper separado para
# que a formula da norma seja testavel isoladamente.
#
# REFERENCIAS:
#   [1] NBR 6118:2023, sec.17.3.3.2 (controle da fissuracao / abertura wk)
#   [2] NBR 6118:2023, sec.21.3.3 (estruturas em contato c/ liquidos: wk<=0,10mm)
#   [3] CARINI, M.R. (MSc, UFSC) - Notas de aula (Estadio II)
#   [4] ARAUJO, J.M. (Dr., FURG) Curso de Concreto Armado, v.2, 2014
from __future__ import annotations

import math
from dataclasses import dataclass

ES_MPA = 210_000.0          # modulo de elasticidade do aco (NBR 6118, 8.3.6)
ETA1_NERVURADA = 2.25       # coef. de conformacao superficial (CA-50/CA-60 nervurada)
WLIM_CAA = {                # abertura limite por CAA (NBR 6118, Tabela 13.4) [mm]
    "I": 0.40, "II": 0.30, "III": 0.20, "IV": 0.30,
}
WLIM_LIQUIDO = 0.10         # estruturas em contato c/ liquidos (sec.21.3.3) [mm]


def fctm(fck_mpa: float) -> float:
    """Resistencia media a tracao do concreto [MPa] (NBR 6118, 8.2.5).

    fctm = 0,3 * fck^(2/3) para fck <= 50 MPa.
    """
    return 0.3 * fck_mpa ** (2.0 / 3.0)


def ecs(fck_mpa: float, alpha_e_agreg: float = 1.0) -> float:
    """Modulo de elasticidade secante do concreto [MPa] (NBR 6118, 8.2.8).

    Eci = alpha_e * 5600 * sqrt(fck); Ecs = alpha_i * Eci,
    com alpha_i = 0,8 + 0,2*fck/80 <= 1,0.
    alpha_e_agreg: 1,2 basalto; 1,0 granito/gnaisse (padrao); 0,9 calcario; 0,7 arenito.
    """
    eci = alpha_e_agreg * 5600.0 * math.sqrt(fck_mpa)
    alpha_i = min(0.8 + 0.2 * fck_mpa / 80.0, 1.0)
    return alpha_i * eci


@dataclass(frozen=True)
class TensaoEstadio2:
    """Estado da secao fissurada (Estadio II) sob momento de servico."""
    sigma_s_mpa: float    # tensao no aco tracionado [MPa]
    x_ii_cm: float        # linha neutra no Estadio II [cm]
    i_ii_cm4: float       # inercia da secao fissurada [cm4]
    alpha_e: float        # relacao modular Es/Ecs


def tensao_aco_estadio2(m_serv_kncm: float, as_cm2: float, b_cm: float,
                        d_cm: float, fck_mpa: float,
                        alpha_e_agreg: float = 1.0) -> TensaoEstadio2:
    """Tensao no aco no Estadio II para flexao simples (secao retangular).

    Linha neutra (equilibrio de momentos estaticos, secao homogeneizada):
        b*x^2/2 - alpha_e*As*(d-x) = 0
        => x = (alpha_e*As/b) * (sqrt(1 + 2*b*d/(alpha_e*As)) - 1)
    Inercia fissurada:  I_II = b*x^3/3 + alpha_e*As*(d-x)^2
    Tensao no aco:      sigma_s = alpha_e * M*(d-x) / I_II

    m_serv_kncm: momento de servico [kN.cm] (combinacao ELS, ja sem gamma_f).
    Retorna sigma_s em MPa (positivo = tracao).
    """
    if as_cm2 <= 0 or b_cm <= 0 or d_cm <= 0:
        raise ValueError("As, b e d devem ser positivos")
    e_cs = ecs(fck_mpa, alpha_e_agreg)
    alpha_e = ES_MPA / e_cs
    k = alpha_e * as_cm2 / b_cm
    x = k * (math.sqrt(1.0 + 2.0 * b_cm * d_cm / (alpha_e * as_cm2)) - 1.0)
    i_ii = b_cm * x ** 3 / 3.0 + alpha_e * as_cm2 * (d_cm - x) ** 2
    sigma_s_kncm2 = alpha_e * abs(m_serv_kncm) * (d_cm - x) / i_ii
    return TensaoEstadio2(
        sigma_s_mpa=round(sigma_s_kncm2 * 10.0, 2),   # kN/cm2 -> MPa
        x_ii_cm=round(x, 3),
        i_ii_cm4=round(i_ii, 1),
        alpha_e=round(alpha_e, 3),
    )


@dataclass(frozen=True)
class TensaoFlexoTracao:
    """Estado da secao fissurada (Estadio II) sob N (tracao) + M de servico."""
    sigma_s_mpa: float    # tensao na armadura mais tracionada [MPa]
    x_ii_cm: float        # linha neutra no Estadio II [cm] (0 = secao toda tracionada)
    caso: str             # "flexao" | "grande" | "pequena"
    e0_cm: float          # excentricidade M/N [cm] (None quando N ~ 0)
    alpha_e: float        # relacao modular Es/Ecs


def tensao_aco_flexotracao(m_serv_kncm: float, n_serv_kn: float, as1_cm2: float,
                           b_cm: float, d_cm: float, h_cm: float, fck_mpa: float,
                           d_linha_cm: float | None = None,
                           alpha_e_agreg: float = 1.0) -> TensaoFlexoTracao:
    """Tensao no aco no Estadio II para FLEXO-TRACAO normal (secao retangular).

    Generaliza tensao_aco_estadio2 para um esforco normal de TRACAO N combinado
    com o momento de servico M. Classifica pela excentricidade e0 = M/N frente a
    z/2 (mesmo criterio do dimensionamento, dimensionar_flexo_tracao):

      * N ~ 0          -> flexao simples pura (delega a tensao_aco_estadio2).
      * e0 <= z/2      -> PEQUENA excentricidade: secao toda tracionada, concreto
                          desprezado. As duas armaduras tracionam; a face mais
                          solicitada tem sigma_s = N*(z/2 + e0) / (z * As1).
      * e0 > z/2       -> GRANDE excentricidade: existe banzo comprimido. Resolve
                          o equilibrio elastico da secao fissurada (concreto
                          triangular + As tracionada) com a normal:
                              Cc*(d - x/3) = Ms,  Ms = M - N*(d - h/2)
                              Ts = Cc + N,        sigma_s = Ts / As1
                          A linha neutra x sai da compatibilidade elastica
                          (sigma_s = 2*alpha_e*Cc*(d-x)/(b*x^2)), resolvida por
                          bisseccao em (0, d). No limite N->0 recai exatamente na
                          flexao pura (b*x^2/2 = alpha_e*As*(d-x)).

    m_serv_kncm: momento de servico [kN.cm] (sem gamma_f). n_serv_kn: tracao de
    servico [kN] (positiva). d_linha_cm: d' da face oposta (padrao h - d).
    """
    if as1_cm2 <= 0 or b_cm <= 0 or d_cm <= 0:
        raise ValueError("As1, b e d devem ser positivos")
    e_cs = ecs(fck_mpa, alpha_e_agreg)
    alpha_e = ES_MPA / e_cs
    m_cm = abs(m_serv_kncm)
    n = abs(n_serv_kn)

    if n < 1e-9:
        t2 = tensao_aco_estadio2(m_serv_kncm, as1_cm2, b_cm, d_cm, fck_mpa, alpha_e_agreg)
        return TensaoFlexoTracao(sigma_s_mpa=t2.sigma_s_mpa, x_ii_cm=t2.x_ii_cm,
                                 caso="flexao", e0_cm=None, alpha_e=t2.alpha_e)

    d_linha = (h_cm - d_cm) if d_linha_cm is None else d_linha_cm
    z = d_cm - d_linha
    e0 = m_cm / n

    if e0 <= z / 2.0:
        # PEQUENA excentricidade: secao integralmente tracionada (sem concreto).
        e2 = z / 2.0 + e0          # braco da face mais tracionada (As1)
        sigma_s_kncm2 = n * e2 / (z * as1_cm2)
        return TensaoFlexoTracao(sigma_s_mpa=round(sigma_s_kncm2 * 10.0, 2),
                                 x_ii_cm=0.0, caso="pequena",
                                 e0_cm=round(e0, 2), alpha_e=round(alpha_e, 3))

    # GRANDE excentricidade: banzo comprimido + As tracionada.
    ms = n * (e0 - z / 2.0)        # momento reduzido em torno da armadura tracionada
    coef = 2.0 * alpha_e * as1_cm2

    def f(x: float) -> float:
        cc = ms / (d_cm - x / 3.0)            # resultante de compressao [kN]
        a = coef * (d_cm - x) / (b_cm * x ** 2)
        return cc * (a - 1.0) - n             # zero no equilibrio

    lo, hi = 1e-4, d_cm - 1e-4
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    x = 0.5 * (lo + hi)
    cc = ms / (d_cm - x / 3.0)
    sigma_s_kncm2 = (cc + n) / as1_cm2
    return TensaoFlexoTracao(sigma_s_mpa=round(sigma_s_kncm2 * 10.0, 2),
                             x_ii_cm=round(x, 3), caso="grande",
                             e0_cm=round(e0, 2), alpha_e=round(alpha_e, 3))


def area_envolvente_por_metro(h_cm: float, d_cm: float, phi_mm: float) -> float:
    """Area de concreto de envolvimento Acri p/ faixa de 1 m (NBR 6118, 17.3.3.2).

    A regiao de envolvimento e um retangulo cujos lados distam no maximo 7,5*phi
    do eixo da barra. Para placa/parede (faixa b=100 cm), a altura efetiva e
    2*(h-d) [duas vezes o cobrimento ao eixo da barra], limitada a 2*7,5*phi.
    """
    phi_cm = phi_mm / 10.0
    altura = min(2.0 * (h_cm - d_cm), 2.0 * 7.5 * phi_cm)
    return 100.0 * altura


@dataclass(frozen=True)
class AberturaFissura:
    """Resultado do calculo de abertura de fissura wk (NBR 6118, 17.3.3.2)."""
    wk_mm: float          # abertura caracteristica adotada = min(w1, w2)
    w1_mm: float          # controle pela aderencia (3*sigma_s/fctm)
    w2_mm: float          # controle pelo elemento (4/rho_r + 45)
    rho_r: float          # taxa de armadura na regiao de envolvimento


def abertura_wk(phi_mm: float, sigma_s_mpa: float, fctm_mpa: float,
                rho_r: float, eta1: float = ETA1_NERVURADA,
                es_mpa: float = ES_MPA) -> AberturaFissura:
    """Abertura caracteristica de fissura wk [mm] (NBR 6118:2023, 17.3.3.2).

    wk e o MENOR de dois valores (phi em mm => wk em mm):
        w1 = (phi/(12,5*eta1)) * (sigma_s/Es) * (3*sigma_s/fctm)
        w2 = (phi/(12,5*eta1)) * (sigma_s/Es) * (4/rho_r + 45)

    sigma_s: tensao no aco no Estadio II [MPa]; rho_r = As/Acri.
    """
    if rho_r <= 0:
        raise ValueError("rho_r deve ser positivo")
    base = (phi_mm / (12.5 * eta1)) * (sigma_s_mpa / es_mpa)
    w1 = base * (3.0 * sigma_s_mpa / fctm_mpa)
    w2 = base * (4.0 / rho_r + 45.0)
    return AberturaFissura(
        wk_mm=round(min(w1, w2), 4),
        w1_mm=round(w1, 4),
        w2_mm=round(w2, 4),
        rho_r=round(rho_r, 5),
    )


def verificar_fissuracao(m_serv_kncm: float, as_cm2: float, b_cm: float,
                         d_cm: float, h_cm: float, fck_mpa: float,
                         phi_mm: float, w_lim_mm: float = WLIM_LIQUIDO,
                         alpha_e_agreg: float = 1.0):
    """Encadeia Estadio II -> Acri -> wk e devolve (AberturaFissura, TensaoEstadio2).

    Conveniencia para os elementos (reservatorio/piscina): a partir do momento
    de servico e da armadura efetiva, calcula wk pronto para comparar com w_lim.
    """
    t2 = tensao_aco_estadio2(m_serv_kncm, as_cm2, b_cm, d_cm, fck_mpa, alpha_e_agreg)
    acri = area_envolvente_por_metro(h_cm, d_cm, phi_mm)
    rho_r = as_cm2 / acri
    abertura = abertura_wk(phi_mm, t2.sigma_s_mpa, fctm(fck_mpa), rho_r)
    return abertura, t2


def verificar_fissuracao_flexotracao(m_serv_kncm: float, n_serv_kn: float,
                                     as1_cm2: float, b_cm: float, d_cm: float,
                                     h_cm: float, fck_mpa: float, phi_mm: float,
                                     d_linha_cm: float | None = None,
                                     w_lim_mm: float = WLIM_LIQUIDO,
                                     alpha_e_agreg: float = 1.0):
    """Encadeia Estadio II (N+M) -> Acri -> wk e devolve (AberturaFissura, TensaoFlexoTracao).

    Versao de flexo-tracao do verificar_fissuracao: usada na direcao horizontal
    das paredes (momento da placa + tracao do anel). rho_r usa a armadura da face
    mais tracionada (As1), consistente com a tensao sigma_s calculada.
    """
    ft = tensao_aco_flexotracao(m_serv_kncm, n_serv_kn, as1_cm2, b_cm, d_cm, h_cm,
                                fck_mpa, d_linha_cm, alpha_e_agreg)
    acri = area_envolvente_por_metro(h_cm, d_cm, phi_mm)
    rho_r = as1_cm2 / acri
    abertura = abertura_wk(phi_mm, ft.sigma_s_mpa, fctm(fck_mpa), rho_r)
    return abertura, ft
