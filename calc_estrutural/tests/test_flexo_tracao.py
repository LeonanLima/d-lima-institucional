"""Flexo-tracao normal (Carini, Reservatorios Elevados, slides 25-31).

Valida contra o exemplo da planilha do Leonan (consideracoes-carini.md sec.5)
e a equivalencia com flexao simples quando Nd -> 0.
"""
import pytest

from dimensionamento.flexo_tracao import dimensionar_flexo_tracao
from dimensionamento.bares import as_flexao_simples


def test_exemplo_planilha_carini_grande_excentricidade():
    # Md=5,35 kNm/m (535 kNcm), Nd=13,68 kN/m, d=7, d'=3, C25
    r = dimensionar_flexo_tracao(5.35, 13.68, b_cm=100, d_cm=7, d_linha_cm=3, fck=25)
    assert r["caso"] == "grande_simples"
    assert r["e0"] == pytest.approx(39.11, abs=0.05)   # 535/13,68
    assert r["e1"] == pytest.approx(37.11, abs=0.05)   # e0 - (d-d')/2 = e0 - 2
    assert r["Md_lim"] == pytest.approx(2196, abs=2)    # bate com a planilha
    assert 13.68 * r["e1"] < r["Md_lim"]                # -> armadura simples
    assert r["As1_cm2"] > 0 and r["As2_cm2"] == 0.0


def test_reduz_a_flexao_simples_quando_Nd_pequeno():
    # Nd ~ 0 -> As1 deve coincidir com a flexao simples pura
    Md, b, d = 12.0, 100, 16.0
    fcd = 25 / 1.4 / 10.0
    fyd = 500 / 1.15 / 10.0
    As_flex = as_flexao_simples(Md, b, d, fcd, fyd)
    r = dimensionar_flexo_tracao(Md, 1e-9, b_cm=b, d_cm=d, d_linha_cm=4, fck=25)
    assert r["As1_cm2"] == pytest.approx(round(As_flex, 2), abs=0.02)


def test_pequena_excentricidade_arma_as_duas_faces():
    # Md pequeno, Nd grande -> e0 < (d-d')/2 -> secao toda tracionada
    r = dimensionar_flexo_tracao(0.5, 200.0, b_cm=100, d_cm=16, d_linha_cm=4, fck=40)
    assert r["caso"] == "pequena"
    assert r["As1_cm2"] > r["As2_cm2"] > 0   # face mais tracionada arma mais


def test_grande_excentricidade_secao_insuficiente():
    # Md enorme em secao fina -> secao insuficiente (sem extrapolar)
    r = dimensionar_flexo_tracao(500.0, 10.0, b_cm=100, d_cm=8, d_linha_cm=3, fck=25)
    assert r.get("erro") or r["caso"] == "grande_dupla"
