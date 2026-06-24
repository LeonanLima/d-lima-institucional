"""Golden tests — congelam exemplos resolvidos do Prof. Carini e cálculos de
mão verificáveis por primeiros princípios (NBR 6118/6120).

Objetivo: rede de segurança ANTES de refatorar (unificação memorial↔canônico,
core/resultado, tabelas-como-dado). Se um refactor mudar a física, estes testes
quebram. Testes marcados `xfail` documentam bugs conhecidos — viram verde quando
o bug for corrigido (Fatia 2 / R4).
"""
import pytest

from dimensionamento.laje import calcular_laje_macica
from dimensionamento.viga import (
    verificar_bielas, dimensionar_estribos, armadura_simples,
)
from dimensionamento.pilar import calcular_esbeltez, dimensionar_secao
from dimensionamento.muro_arrimo import (
    predimensionar_muro, calcular_empuxo, verificar_estabilidade, dimensionar_fuste,
)


# ── MURO — textbook-correto (Rankine), verificável por primeiros princípios ──
class TestMuroRankine:
    """H=3 m, φ=30°, γ=18 kN/m³, qs=0, fck25/fyk500/CAA II."""

    @pytest.fixture(scope="class")
    def res(self):
        pm = predimensionar_muro(3.0, 30.0, 18.0)
        emp = calcular_empuxo(3.0, 18.0, 30.0, 0.0, 0.0)
        est = verificar_estabilidade(pm, emp, 18.0)
        fus = dimensionar_fuste(pm, emp, 25, 500, "II")
        return emp, est, fus

    def test_ka_textbook(self, res):
        # Ka = tan²(45 - φ/2) = tan²(30°) = 1/3
        assert res[0]["Ka"] == pytest.approx(0.3333, abs=1e-3)

    def test_pa_textbook(self, res):
        # Pa = ½·Ka·γ·H² = ½·(1/3)·18·9 = 27,0 kN/m
        assert res[0]["Pa_total"] == pytest.approx(27.0, abs=0.1)

    def test_za_textbook(self, res):
        # za = H/3 = 1,0 m (resultante do diagrama triangular)
        assert res[0]["za"] == pytest.approx(1.0, abs=0.01)

    def test_estabilidade(self, res):
        est = res[1]
        assert est["FST"] == pytest.approx(2.302, abs=0.01)
        assert est["FSD"] == pytest.approx(0.978, abs=0.01)
        assert est["FST_ok"] is True
        assert est["FSD_ok"] is False  # geometria escorrega — app avisa

    def test_fuste(self, res):
        fus = res[2]
        assert fus["Md_kNm"] == pytest.approx(27.55, abs=0.1)
        assert fus["Vd_kN"] == pytest.approx(30.61, abs=0.1)
        assert fus["As_cm2m"] == pytest.approx(5.85, abs=0.05)


# ── VIGA — flexão simples + cortante (Modelo I) ──
class TestViga:
    """bw=14, d=35, fck25/fyk500, Md=45 kNm, Vd=55 kN."""

    def test_bielas(self):
        b = verificar_bielas(55, 14, 35, 25)
        assert b["VRd2"] == pytest.approx(212.63, abs=0.5)
        assert b["alphav2"] == pytest.approx(0.9, abs=1e-3)  # 1 - 25/250
        assert b["ok"] is True

    def test_flexao(self):
        f = armadura_simples(45 * 100, 14, 35, 25, 500)
        assert f["As_cm2"] == pytest.approx(3.27, abs=0.02)
        assert f["x_cm"] == pytest.approx(8.36, abs=0.05)
        assert f["ok_ductil"] is True

    def test_estribos(self):
        e = dimensionar_estribos(55, 14, 35, 25, 500)
        assert e["Asw_s"] == pytest.approx(0.01436, abs=1e-4)


# ── PILAR — esbeltez + flexo-compressão ──
class TestPilar:
    """H=300, hx=19, hy=40, β=1, Nd=450, Md=1200 kNcm, fck25/fyk500 II."""

    def test_esbeltez(self):
        # ix = hx/√12 → λx = le/ix
        e = calcular_esbeltez(300, 19, 40, 1.0)
        assert e["lam_x"] == pytest.approx(54.7, abs=0.2)
        assert e["lam_y"] == pytest.approx(26.0, abs=0.2)

    def test_armadura(self):
        d = dimensionar_secao(450, 1200, 19, 40, 25, 500, "II")
        assert d["As_adot"] == pytest.approx(3.04, abs=0.02)
        assert d["dominio"] == 2
        assert d["As_min"] == pytest.approx(3.04, abs=0.02)  # 0,4% Ac
        assert d["As_max"] == pytest.approx(60.8, abs=0.2)   # 8% Ac
        assert d["ok_ductil"] is True


# ── LAJE — momentos (caracterização) + flecha (bug conhecido) ──
class TestLaje:
    """Caso 1 (4 apoiadas), lx=3.5, ly=4.5, h=10, gk=1.5, qk=1.5, fck25/fyk500 II."""

    @pytest.fixture(scope="class")
    def res(self):
        return calcular_laje_macica(3.5, 4.5, 10, 1.5, 1.5, 1, 25, 500, "II")

    def test_momentos(self, res):
        # Caracterização: trava o valor atual. NOTA: COEF_CARINI só tem λ=1,0;
        # aqui λ=ly/lx=1,29 → coeficiente aproximado (a corrigir na Fatia 4/A4).
        m = res["momentos"]
        assert m["Mdx_pos"] == pytest.approx(10.14, abs=0.05)
        assert m["Mdy_pos"] == pytest.approx(4.094, abs=0.05)

    @pytest.mark.xfail(reason="BUG: flecha unidirecional aproximada devolve valores "
                              "absurdos (w_total ~15000 mm) e wadm rotulado em mm mas "
                              "vale ~L/250 em cm. Corrigir e remover o xfail.",
                       strict=True)
    def test_flecha_sanidade(self, res):
        els = res["els_flecha"]
        # Para esta laje, L/250 = 3500/250 = 14 mm e a flecha real deve ser < wadm.
        assert els["wadm_mm"] == pytest.approx(14.0, abs=1.0)
        assert els["w_total_mm"] < els["wadm_mm"]
