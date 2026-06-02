import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.materiais import Material


def test_ecs_c25_basalto():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # Eci = 1,2 * 5600 * sqrt(25) = 33600 MPa; ai = 0,8625; Ecs = 28980 MPa = 2898 kN/cm2
    assert abs(m.Ecs - 2898.0) < 1.0


def test_fcd_c25():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # fcd = 25/1,4/10 = 1,7857 kN/cm2
    assert abs(m.fcd - 1.7857) < 0.001


def test_fyd_ca50():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # fyd = 50/1,15 = 43,478 kN/cm2
    assert abs(m.fyd - 43.478) < 0.01


def test_fctd_c25():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # fctd = 0,15 * 25^(2/3) / 10 = 0,15 * 8,5499 / 10 = 0,12825 kN/cm2
    assert abs(m.fctd - 0.12825) < 0.001


def test_fctm_c25():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # fctm = 0,3 * 25^(2/3) = 2,565 MPa
    assert abs(m.fctm - 2.565) < 0.01
