# tests/test_detalhamento.py - trava o detalhamento de armaduras
import math

import pytest

from detalhamento.armaduras import (
    Barra,
    area_barra,
    detalhar_por_quantidade,
    detalhar_por_espacamento,
    texto_para_obra,
    S_MIN_CM,
    S_MAX_CM,
)


def test_area_barra_nbr7480():
    assert area_barra(10.0) == 0.785
    assert area_barra(12.5) == 1.227
    with pytest.raises(ValueError):
        area_barra(11.0)


def test_por_quantidade_provê_area():
    # Viga As=8 cm2: n barras devem cobrir a area.
    b = detalhar_por_quantidade(8.0, nome_seq=1, posicao="positiva")
    assert b.As_prov_cm2 >= 8.0
    assert b.quantidade >= 2
    assert b.espacamento_cm is None
    assert b.nome == "N1"


def test_por_quantidade_bitola_fixa():
    b = detalhar_por_quantidade(8.0, phi_mm=16.0)
    n_esperado = math.ceil(8.0 / area_barra(16.0))
    assert b.phi_mm == 16.0
    assert b.quantidade == max(2, n_esperado)


def test_por_espacamento_provê_area_e_respeita_smax():
    # Laje As=2,5 cm2/m: As_prov/m >= 2,5 e s <= S_MAX.
    b = detalhar_por_espacamento(2.5, largura_cm=100, nome_seq=2)
    assert b.As_prov_cm2 >= 2.5
    assert b.espacamento_cm is not None
    assert S_MIN_CM <= b.espacamento_cm <= S_MAX_CM
    assert b.nome == "N2"


def test_por_espacamento_as_alto_usa_bitola_maior():
    # As alto -> espacamento nao pode cair abaixo do minimo construtivo.
    b = detalhar_por_espacamento(20.0, largura_cm=100)
    assert b.espacamento_cm >= S_MIN_CM
    assert b.As_prov_cm2 >= 20.0 or b.espacamento_cm == S_MIN_CM


def test_descricao_e_texto_para_obra():
    b1 = detalhar_por_espacamento(2.0, nome_seq=1, posicao="positiva x",
                                  comprimento_cm=320)
    b2 = detalhar_por_quantidade(6.0, nome_seq=2, posicao="negativa")
    txt = texto_para_obra([b1, b2])
    assert "N1" in txt and "N2" in txt
    assert "Ø" in b1.descricao()
    assert "c/" in b1.descricao()        # distribuida mostra espacamento
    assert "c/" not in b2.descricao()    # concentrada nao
