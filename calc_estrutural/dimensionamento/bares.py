# dimensionamento/bares.py - Coeficientes de Bares para paredes (carga triangular)
#
# Le a tabela em dados/coef_bares_parede.json e devolve os momentos de placa
# (vao e engaste) interpolados, usando o motor unico core.tabelas.interp_linear.
#
# REFERENCIA: Tabela de Bares (NBR 6118:2023 / notas Prof. Carini, MSc UFSC).
#   Momentos:  M = (m / 1000) * p * l^2
#   p [kN/m2] = pressao na base (carga triangular hidrostatica)
#   l [m]     = vao de referencia (lx ou ly, conforme a tabela selecionada)
import json
import math
import os

from core.tabelas import interp_linear
from dimensionamento.flexo_tracao import (
    dimensionar_flexo_tracao, as_min_flexo_tracao,
)


def as_flexao_simples(Md_kNm, b_cm, d_cm, fcd_kNcm2, fyd_kNcm2):
    """As [cm2] de flexao simples para |Md|. O sinal de Md so define a FACE
    (engaste negativo = face externa; vao positivo = face interna).
    Retorna 0 se nao ha momento e None se a secao for insuficiente.
    Usado por paredes/placas de piscina e reservatorio (mesmo modelo de Bares)."""
    Md_cm = abs(Md_kNm) * 100
    if Md_cm < 0.01:
        return 0.0
    disc = 1 - Md_cm / (0.425 * b_cm * d_cm**2 * fcd_kNcm2)
    if disc < 0:
        return None
    x = 1.25 * d_cm * (1 - math.sqrt(max(0.0, disc)))
    return 0.85 * fcd_kNcm2 * 0.80 * x * b_cm / fyd_kNcm2

_JSON = os.path.join(os.path.dirname(__file__), "..", "dados", "coef_bares_parede.json")
_NOMES = ("mxe", "mye", "mx", "my")

with open(_JSON, encoding="utf-8") as _f:
    _DADOS = json.load(_f)


def coeficientes_parede(lx_m, ly_m):
    """Coeficientes m de Bares para a parede de dimensoes lx x ly.

    Seleciona a sub-tabela conforme a imagem da fonte:
      - lx <= ly  -> tabela 'l = lx', indice razao = lx/ly
      - ly <  lx  -> tabela 'l = ly', indice razao = ly/lx
    Retorna dict {mxe, mye, mx, my, razao, l_ref}.
    """
    if lx_m <= 0 or ly_m <= 0:
        raise ValueError("lx e ly devem ser positivos")

    if lx_m <= ly_m:
        razao = lx_m / ly_m
        tabela = _DADOS["tabela_l_lx"]
        l_ref = lx_m
    else:
        razao = ly_m / lx_m
        tabela = _DADOS["tabela_l_ly"]
        l_ref = ly_m

    coef = interp_linear(tabela, razao, nomes=_NOMES)
    coef["razao"] = round(razao, 4)
    coef["l_ref"] = l_ref
    return coef


def momentos_parede(lx_m, ly_m, p_base_kN_m2):
    """Momentos fletores da parede [kNm/m] a partir dos coeficientes de Bares.

    M = (m / 1000) * p * l_ref^2, com p = pressao na base (carga triangular).
    Retorna dict {Mxe, Mye, Mx, My, ...} mantendo o sinal da tabela
    (engastes negativos, vaos positivos).
    """
    c = coeficientes_parede(lx_m, ly_m)
    fator = p_base_kN_m2 * c["l_ref"] ** 2 / 1000.0
    return dict(
        Mxe=round(c["mxe"] * fator, 3),
        Mye=round(c["mye"] * fator, 3),
        Mx=round(c["mx"] * fator, 3),
        My=round(c["my"] * fator, 3),
        razao=c["razao"], l_ref=c["l_ref"],
        coef=c,
    )


def dimensionar_parede_placa(H_m, L_m, espessura_m, p_base_carac,
                             fck=40.0, fyk=500.0, caa="IV"):
    """Parede de reservatorio/piscina como PLACA de Bares + tracao do anel.

    Modelo do Prof. Carini (Reservatorios Elevados):
    - HORIZONTAL (x): flexo-tracao = momento da placa (Mx vao / Mxe engaste) +
      tracao do anel Nd = 1,2 * p * L/2 (gamma_f=1,2 p/ normal).
    - VERTICAL (y): flexao simples (My vao / Mye engaste); gamma_f=1,4 nos momentos.
    p_base_carac = pressao caracteristica na base [kN/m2] (agua=gamma*H ou solo).
    Retorna dict com as 4 armaduras + governante, ou {erro:...} / {As_cm2m:0}.
    """
    fcd = fck / 1.4 / 10.0   # kN/cm2
    fyd = fyk / 1.15 / 10.0  # kN/cm2
    cobr = {"I": 2.0, "II": 2.5, "III": 4.0, "IV": 4.5}.get(caa, 4.5)
    h_cm = espessura_m * 100
    d = h_cm - cobr - 0.625
    d_linha = cobr + 0.625    # d' (face oposta)
    b = 100.0

    if p_base_carac <= 0:
        return {"As_cm2m": 0, "nota": "Sem pressao liquida nesta combinacao."}

    pd_mom = 1.4 * p_base_carac                  # momento (gamma_f=1,4)
    Nd_anel = 1.2 * p_base_carac * L_m / 2.0     # tracao do anel (gamma_f=1,2)
    M = momentos_parede(L_m, H_m, pd_mom)
    Vd = pd_mom * H_m / 2.0

    As_min = as_min_flexo_tracao(fck, b, h_cm)

    # Horizontal: flexo-tracao (placa + anel)
    ft_vx = dimensionar_flexo_tracao(M["Mx"], Nd_anel, b, d, d_linha, fck, fyk)
    ft_ex = dimensionar_flexo_tracao(M["Mxe"], Nd_anel, b, d, d_linha, fck, fyk)
    if any(r.get("erro") or r.get("caso") == "grande_dupla" for r in (ft_vx, ft_ex)):
        return {"erro": "Secao insuficiente (flexo-tracao horizontal) - aumentar espessura"}

    # Vertical: flexao simples
    as_vy = as_flexao_simples(M["My"], b, d, fcd, fyd)
    as_ey = as_flexao_simples(M["Mye"], b, d, fcd, fyd)
    if as_vy is None or as_ey is None:
        return {"erro": "Secao insuficiente (flexao vertical) - aumentar espessura"}

    arm = dict(
        As_vao_x=round(max(ft_vx["As1_cm2"], As_min), 2),
        As_eng_x=round(max(ft_ex["As1_cm2"], As_min), 2),
        As_vao_y=round(max(as_vy, As_min), 2),
        As_eng_y=round(max(as_ey, As_min), 2),
    )
    return dict(
        H=H_m, L=L_m, h_cm=h_cm, d_cm=round(d, 1),
        razao=M["razao"], l_ref=M["l_ref"],
        p_base=round(p_base_carac, 2), Nd_anel_kNm=round(Nd_anel, 2), Vd_kN=round(Vd, 2),
        Mx=M["Mx"], My=M["My"], Mxe=M["Mxe"], Mye=M["Mye"],
        ft_vao_x=ft_vx, ft_eng_x=ft_ex,
        As_vao_x=arm["As_vao_x"], As_vao_y=arm["As_vao_y"],
        As_eng_x=arm["As_eng_x"], As_eng_y=arm["As_eng_y"],
        As_cm2m=max(arm.values()), As_min=As_min,
        w_lim=0.10,
    )
