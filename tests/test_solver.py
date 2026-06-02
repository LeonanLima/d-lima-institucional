import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.solver import forcas_equivalentes_distribuida


def test_forcas_equivalentes_carga_para_baixo():
    # q = 0,10 kN/cm para baixo, L = 500 cm, barra horizontal (angulo 0)
    # Reacoes de engaste: V = qL/2 = 25 kN; M = qL^2/12 = 2083,33 kN.cm
    f = forcas_equivalentes_distribuida(q=0.10, L=500.0, angulo=0.0)
    assert abs(f[1] - (-25.0)) < 0.01   # fy no no i
    assert abs(f[4] - (-25.0)) < 0.01   # fy no no j
    assert abs(f[2] - (-2083.333)) < 0.1  # Mz no no i
    assert abs(f[5] - (2083.333)) < 0.1   # Mz no no j


def test_forcas_equivalentes_soma_vertical():
    f = forcas_equivalentes_distribuida(q=0.10, L=500.0, angulo=0.0)
    # soma das forcas verticais = -qL = -50 kN
    assert abs((f[1] + f[4]) - (-50.0)) < 0.01
