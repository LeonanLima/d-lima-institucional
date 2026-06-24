"""Testes do motor de interpolacao de tabelas (core/tabelas.py - Fatia 4/A4)."""
import pytest

from core.tabelas import interp_linear

# Recorte da tabela de reservatorio (razao, mx, my) - dados reais.
T = [(0.50, 9.4, 26.0), (1.00, 12.2, 10.6)]


def test_ponto_medio():
    assert interp_linear(T, 0.75) == pytest.approx([10.8, 18.3])


def test_chave_exata_no_no():
    assert interp_linear(T, 0.50) == pytest.approx([9.4, 26.0])
    assert interp_linear(T, 1.00) == pytest.approx([12.2, 10.6])


def test_clampa_abaixo_e_acima():
    assert interp_linear(T, 0.30) == pytest.approx([9.4, 26.0])   # nao extrapola
    assert interp_linear(T, 1.50) == pytest.approx([12.2, 10.6])


def test_tabela_desordenada_funciona():
    desord = [(1.00, 12.2, 10.6), (0.50, 9.4, 26.0)]
    assert interp_linear(desord, 0.75) == pytest.approx([10.8, 18.3])


def test_retorna_dict_com_nomes():
    r = interp_linear(T, 0.75, nomes=["mx", "my"])
    assert r == pytest.approx({"mx": 10.8, "my": 18.3})


def test_tabela_vazia_levanta():
    with pytest.raises(ValueError):
        interp_linear([], 0.5)
