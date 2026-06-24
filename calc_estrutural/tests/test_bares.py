"""Trava a transcricao da tabela de Bares (parede, carga triangular).

Os valores aqui sao os tabelados na imagem fornecida por Leonan (2026-06-24).
Se a transcricao em dados/coef_bares_parede.json mudar, estes testes quebram.
"""
import pytest

from dimensionamento.bares import coeficientes_parede, momentos_parede


def test_razao_unitaria_converge_nas_duas_tabelas():
    # lx == ly -> razao 1,00 ; ambas as sub-tabelas dao o mesmo valor
    c = coeficientes_parede(3.0, 3.0)
    assert c["mxe"] == pytest.approx(-28.3)
    assert c["mye"] == pytest.approx(-34.5)
    assert c["mx"] == pytest.approx(12.2)
    assert c["my"] == pytest.approx(10.6)
    assert c["razao"] == pytest.approx(1.0)
    assert c["l_ref"] == 3.0


def test_tabela_l_lx_extremo_05():
    # lx=2,5 ly=5 -> lx/ly = 0,50 ; tabela l=lx ; l_ref = lx
    c = coeficientes_parede(2.5, 5.0)
    assert c["mxe"] == pytest.approx(-41.3)
    assert c["mye"] == pytest.approx(-45.1)
    assert c["mx"] == pytest.approx(20.6)
    assert c["my"] == pytest.approx(5.8)
    assert c["l_ref"] == 2.5


def test_tabela_l_ly_extremo_05():
    # lx=5 ly=2,5 -> ly/lx = 0,50 ; tabela l=ly ; l_ref = ly
    c = coeficientes_parede(5.0, 2.5)
    assert c["mxe"] == pytest.approx(-36.2)
    assert c["mye"] == pytest.approx(-62.1)
    assert c["mx"] == pytest.approx(9.4)
    assert c["my"] == pytest.approx(26.0)
    assert c["l_ref"] == 2.5


def test_interpolacao_linear_meio_intervalo():
    # lx/ly = 0,925 -> entre 0,90 (-31.9) e 0,95 (-30.1) ; meio = -31.0
    c = coeficientes_parede(0.925, 1.0)
    assert c["mxe"] == pytest.approx(-31.0, abs=1e-6)
    assert c["mx"] == pytest.approx(13.8, abs=1e-6)  # entre 14.3 e 13.3


def test_clamp_fora_do_intervalo():
    # razao < 0,50 deve clampar no extremo 0,50 (sem extrapolar)
    c = coeficientes_parede(1.0, 10.0)  # lx/ly = 0,10 -> clampa em 0,50
    assert c["mxe"] == pytest.approx(-41.3)
    assert c["my"] == pytest.approx(5.8)


def test_momentos_aplica_formula_bares():
    # M = (m/1000) * p * l_ref^2 ; razao 1,0 (l_ref=3), p=30 kN/m2
    m = momentos_parede(3.0, 3.0, 30.0)
    fator = 30.0 * 3.0**2 / 1000.0
    assert m["Mxe"] == pytest.approx(round(-28.3 * fator, 3))
    assert m["My"] == pytest.approx(round(10.6 * fator, 3))
    assert m["l_ref"] == 3.0
