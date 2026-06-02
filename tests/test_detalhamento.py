import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.detalhamento import escolher_bitola, escolher_estribo


def test_escolher_bitola_menor_desperdicio():
    # As=3,55 -> 3 Ø12,5 (3,68) tem menor desperdicio entre validos
    r = escolher_bitola(3.55)
    assert r["n"] == 3
    assert r["phi"] == 12.5
    assert abs(r["As_fornecido"] - 3.68) < 0.01
    assert "3" in r["descricao"] and "12,5" in r["descricao"]


def test_escolher_bitola_minimo_duas_barras():
    # As pequeno -> minimo 2 barras
    r = escolher_bitola(0.5)
    assert r["n"] >= 2


def test_escolher_estribo_2_ramos():
    # Asw/s = 0,02927 cm2/cm; estribo 2 ramos
    r = escolher_estribo(0.02927, comprimento_zona=80)
    # Ø5=0,196cm2; 2 ramos -> 0,392; s = 0,392/0,02927 = 13,4 -> arredonda p/ baixo
    assert r["phi"] == 5.0
    assert r["n_ramos"] == 2
    assert r["espacamento"] <= 13.4
    assert r["quantidade"] >= 1


def test_escolher_estribo_respeita_smax():
    # Asw/s minimo -> espacamento limitado a 30cm (ou menos)
    r = escolher_estribo(0.005, comprimento_zona=200)
    assert r["espacamento"] <= 30
