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
import os

from core.tabelas import interp_linear

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
