# tests/test_esforcos.py - trava o solver 1D contra solucoes fechadas classicas
import math

from analise.esforcos import (
    CargaDistribuida,
    CargaPontual,
    resolver_viga_biapoiada,
)


def test_udl_momento_e_reacoes():
    # Viga biapoiada com carga uniforme: M_max = q L^2 / 8, RA = RB = q L / 2.
    L, q = 5.0, 10.0
    r = resolver_viga_biapoiada(L, distribuidas=[CargaDistribuida(q)], n=401)

    assert math.isclose(r["RA_kN"], q * L / 2, rel_tol=1e-3)
    assert math.isclose(r["RB_kN"], q * L / 2, rel_tol=1e-3)
    assert math.isclose(r["M_max_kNm"], q * L**2 / 8, rel_tol=2e-3)
    # momento nas extremidades ~ 0
    assert abs(r["M"][0]) < 1e-6
    assert abs(r["M"][-1]) < 1e-2


def test_udl_flecha_maxima():
    # Flecha max de UDL: 5 q L^4 / (384 EI), no meio do vao.
    L, q, EI = 5.0, 10.0, 20000.0
    r = resolver_viga_biapoiada(L, distribuidas=[CargaDistribuida(q)],
                                EI=EI, n=401)
    esperado = 5 * q * L**4 / (384 * EI)
    assert math.isclose(r["delta_max_m"], esperado, rel_tol=3e-3)
    assert r["delta_max_m"] > 0   # flecha para baixo e positiva


def test_pontual_central_momento_e_flecha():
    # Carga central P: M_max = P L / 4, flecha = P L^3 / (48 EI).
    L, P, EI = 4.0, 20.0, 15000.0
    r = resolver_viga_biapoiada(L, pontuais=[CargaPontual(P, L / 2)],
                                EI=EI, n=401)
    assert math.isclose(r["RA_kN"], P / 2, rel_tol=1e-3)
    assert math.isclose(r["M_max_kNm"], P * L / 4, rel_tol=3e-3)
    esperado = P * L**3 / (48 * EI)
    assert math.isclose(r["delta_max_m"], esperado, rel_tol=5e-3)


def test_pontual_excentrica_reacoes():
    # Carga em a: RA = P b / L, RB = P a / L (b = L - a).
    L, P, a = 6.0, 30.0, 2.0
    b = L - a
    r = resolver_viga_biapoiada(L, pontuais=[CargaPontual(P, a)], n=601)
    assert math.isclose(r["RA_kN"], P * b / L, rel_tol=1e-3)
    assert math.isclose(r["RB_kN"], P * a / L, rel_tol=1e-3)
    # M_max sob a carga = P a b / L
    assert math.isclose(r["M_max_kNm"], P * a * b / L, rel_tol=3e-3)


def test_superposicao_udl_mais_pontual():
    # Linearidade: resultado combinado = soma das reacoes isoladas.
    L = 5.0
    ud = CargaDistribuida(8.0)
    pt = CargaPontual(12.0, 2.0)
    r_ud = resolver_viga_biapoiada(L, distribuidas=[ud])
    r_pt = resolver_viga_biapoiada(L, pontuais=[pt])
    r_comb = resolver_viga_biapoiada(L, distribuidas=[ud], pontuais=[pt])
    assert math.isclose(r_comb["RA_kN"], r_ud["RA_kN"] + r_pt["RA_kN"],
                        rel_tol=1e-3)
    assert math.isclose(r_comb["RB_kN"], r_ud["RB_kN"] + r_pt["RB_kN"],
                        rel_tol=1e-3)


def test_sem_carga_e_seguro():
    # Sem cargas: tudo zero, sem flecha quando EI ausente.
    r = resolver_viga_biapoiada(4.0, n=11)
    assert r["RA_kN"] == 0.0 and r["RB_kN"] == 0.0
    assert max(abs(v) for v in r["V"]) == 0.0
    assert r["delta"] is None
