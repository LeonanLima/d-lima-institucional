import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.materiais import Material
from engine.dimensionamento import cisalhamento_viga


def test_cisalhamento_vrd2_ok():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # bw=14, d=36, VSd=80 kN
    r = cisalhamento_viga(m, bw=14, d=36, VSd=80.0)
    # av2 = 1-25/250 = 0,9; fcd=1,7857; VRd2=0,27*0,9*1,7857*14*36
    # = 0,27*0,9*1,7857*504 = 218,6 kN
    assert abs(r["VRd2"] - 218.6) < 1.0
    assert r["bielas_ok"] is True


def test_cisalhamento_vc():
    m = Material(fck=25, fyk=500, agregado='basalto')
    r = cisalhamento_viga(m, bw=14, d=36, VSd=80.0)
    # Vc = 0,6*fctd*bw*d = 0,6*0,12825*14*36 = 38,77 kN
    assert abs(r["Vc"] - 38.77) < 0.5


def test_cisalhamento_asw_s():
    m = Material(fck=25, fyk=500, agregado='basalto')
    r = cisalhamento_viga(m, bw=14, d=36, VSd=80.0)
    # fywd=min(50/1,15;43,5)=43,478; Asw/s=(80-38,77)/(0,9*36*43,478)
    # = 41,23/1408,7 = 0,02927 cm2/cm
    assert abs(r["Asw_s"] - 0.02927) < 0.001


def test_cisalhamento_bielas_estouram():
    m = Material(fck=25, fyk=500, agregado='basalto')
    r = cisalhamento_viga(m, bw=14, d=36, VSd=250.0)
    # VSd 250 > VRd2 218,6 -> bielas nao ok
    assert r["bielas_ok"] is False
