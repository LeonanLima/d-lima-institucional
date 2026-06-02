import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.svg_secao import desenhar_secao


def test_secao_retorna_svg():
    svg = desenhar_secao(bw=14, h=40, cobrimento=3.0,
                         barras_inf=(3, 10.0), barras_sup=(2, 12.5),
                         barras_pele=0, phi_est=5.0)
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")


def test_secao_contem_barras():
    svg = desenhar_secao(bw=14, h=40, cobrimento=3.0,
                         barras_inf=(3, 10.0), barras_sup=(2, 12.5),
                         barras_pele=0, phi_est=5.0)
    # 3 barras inferiores + 2 superiores = 5 circulos
    assert svg.count("<circle") == 5


def test_secao_com_pele():
    svg = desenhar_secao(bw=19, h=70, cobrimento=3.0,
                         barras_inf=(3, 16.0), barras_sup=(3, 16.0),
                         barras_pele=2, phi_est=5.0)
    # 3 + 3 + (2 por face * 2 faces = 4) = 10 circulos
    assert svg.count("<circle") == 10
