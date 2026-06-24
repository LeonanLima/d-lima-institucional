"""A parede (reservatorio/piscina) usa FLEXO-TRACAO na horizontal e flexao na vertical."""
import pytest

from dimensionamento.reservatorio import paredes_dimensionar, GAMMA_AGUA
from dimensionamento.bares import momentos_parede, as_flexao_simples
from dimensionamento.flexo_tracao import dimensionar_flexo_tracao


def test_horizontal_soma_tracao_do_anel():
    H, L, h, fck, fyk, caa = 2.5, 4.0, 0.20, 40, 500, "IV"
    r = paredes_dimensionar(H, L, h, fck=fck, fyk=fyk, caa=caa)

    p = GAMMA_AGUA * H
    M = momentos_parede(L, H, 1.4 * p)
    Nd_anel = 1.2 * p * L / 2.0
    cobr = 4.5
    d = h * 100 - cobr - 0.625
    d_linha = cobr + 0.625
    fcd, fyd = fck / 1.4 / 10.0, fyk / 1.15 / 10.0

    # engaste horizontal: flexo-tracao deve dar MAIS aco que so flexao do Mxe
    ft = dimensionar_flexo_tracao(M["Mxe"], Nd_anel, 100, d, d_linha, fck, fyk)
    as_flex_so = as_flexao_simples(M["Mxe"], 100, d, fcd, fyd)
    assert ft["As1_cm2"] > as_flex_so          # o anel acrescenta tracao
    assert r["As_eng_x"] == pytest.approx(round(max(ft["As1_cm2"], r["As_min"]), 2))
    assert r["Nd_anel_kNm"] == pytest.approx(round(Nd_anel, 2))


def test_vertical_e_flexao_simples_pura():
    H, L, h, fck = 2.5, 4.0, 0.20, 40
    r = paredes_dimensionar(H, L, h, fck=fck, fyk=500, caa="IV")
    M = momentos_parede(L, H, 1.4 * GAMMA_AGUA * H)
    cobr = 4.5
    d = h * 100 - cobr - 0.625
    fcd, fyd = fck / 1.4 / 10.0, 500 / 1.15 / 10.0
    as_ey = as_flexao_simples(M["Mye"], 100, d, fcd, fyd)
    assert r["As_eng_y"] == pytest.approx(round(max(as_ey, r["As_min"]), 2))
