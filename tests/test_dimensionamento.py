import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.materiais import Material
from engine.dimensionamento import cisalhamento_viga, flexao_viga, armadura_pele


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


def test_flexao_armadura_simples():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # Md=50 kNm=5000 kN.cm; bw=14; d=36
    r = flexao_viga(m, bw=14, d=36, Md=50.0)
    # x = 9,085 cm; x/d=0,2524; As=3,55 cm2
    assert abs(r["x"] - 9.085) < 0.1
    assert abs(r["As"] - 3.55) < 0.05
    assert r["tipo"] == "simples"
    assert r["ductil"] is True


def test_flexao_armadura_minima():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # Md pequeno -> As_min governa: 0,15% * 14 * 36 = 0,756 cm2
    r = flexao_viga(m, bw=14, d=36, Md=5.0)
    assert abs(r["As_min"] - 0.756) < 0.01
    assert r["As"] >= r["As_min"]


def test_flexao_armadura_dupla():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # Md muito alto -> dupla. Md=200 kNm em secao 14x36 estoura Md,duc
    r = flexao_viga(m, bw=14, d=36, Md=200.0)
    assert r["tipo"] == "dupla"


def test_armadura_pele_necessaria():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # h=70 > 60 -> pele. As_pele por face = 0,10% * bw * (h util)
    r = armadura_pele(m, bw=14, h=70, cobrimento=3.0, phi_est=0.5)
    assert r["necessaria"] is True
    assert r["As_face"] > 0


def test_armadura_pele_dispensada():
    m = Material(fck=25, fyk=500, agregado='basalto')
    r = armadura_pele(m, bw=14, h=40, cobrimento=3.0, phi_est=0.5)
    assert r["necessaria"] is False
