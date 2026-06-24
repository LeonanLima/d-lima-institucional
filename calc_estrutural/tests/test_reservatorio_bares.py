"""Parede de reservatorio como placa de Bares (mesma tabela da piscina)."""
import pytest

from dimensionamento.reservatorio import paredes_dimensionar, GAMMA_AGUA
from dimensionamento.bares import momentos_parede


def test_parede_reservatorio_usa_bares():
    H, L, h = 2.0, 3.0, 0.20
    r = paredes_dimensionar(H, L, h, fck=40, fyk=500, caa="IV")
    pd = GAMMA_AGUA * H * 1.4
    M = momentos_parede(L, H, pd)
    assert r["Mye"] == pytest.approx(M["Mye"])
    assert r["Mx"] == pytest.approx(M["Mx"])
    # 4 armaduras + governante = a maior
    assert r["As_cm2m"] == max(r["As_vao_x"], r["As_vao_y"],
                               r["As_eng_x"], r["As_eng_y"])
    assert r["As_cm2m"] >= r["As_min"]
    assert r["w_lim"] == 0.10


def test_mesma_tabela_que_piscina():
    # reservatorio e piscina compartilham o mesmo grid de Bares
    from dimensionamento.piscina import dimensionar_parede, combinacoes_piscina
    H, L, h = 2.0, 3.0, 0.20
    C1, _C2, _C3 = combinacoes_piscina(H)  # cheia: p = 10*H
    r_res = paredes_dimensionar(H, L, h, fck=40, fyk=500, caa="IV")
    r_pisc = dimensionar_parede(H, L, h, C1, fck=40, fyk=500, caa="IV")
    # mesma pressao de calculo (10*H*1.4) e mesma geometria -> mesmos momentos
    assert r_res["Mye"] == pytest.approx(r_pisc["Mye"])
    assert r_res["As_cm2m"] == pytest.approx(r_pisc["As_cm2m"])
