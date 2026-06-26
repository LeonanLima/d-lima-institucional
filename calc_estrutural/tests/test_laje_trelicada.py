"""Golden tests da LAJE TRELICADA (nervura = viga T, considerações do Musso).

Congela um exemplo verificavel por primeiros principios (PP pela geometria,
Md = fd*lx^2/alpha, secao T) e exercita os 3 ramos do criterio de cisalhamento
do Musso (§13.4.2) e a secao T real (LN na nervura).
"""
import pytest

from dimensionamento.laje_trelicada import (
    calcular_laje_trelicada, _criterio_cisalhamento, _inercia_T, _armar_secao_T,
)


class TestTrelicadaBiapoiada:
    """lx=4,0 m | e=50 | capa=4 | h=12 | bw=9 | gk=1,0 qk=2,0 | apoio/apoio."""

    @pytest.fixture(scope="class")
    def r(self):
        return calcular_laje_trelicada(lx=4.0, e_cm=50, h_capa_cm=4, h_total_cm=12,
                                       bw_cm=9, gk=1.0, qk=2.0,
                                       vinculacao="apoio_apoio")

    def test_pp_geometrico(self, r):
        # A_c = 50*4 + 9*8 = 272 cm2 ; PP = 25*(272/1e4)/0,5 = 1,36 kN/m2
        assert r["PP_kNm2"] == pytest.approx(1.36, abs=0.01)

    def test_carga_calculo(self, r):
        # fd = 1,4*(1,0+1,36) + 1,4*2,0 = 6,104
        assert r["fd_kNm2"] == pytest.approx(6.104, abs=0.01)

    def test_momento_positivo(self, r):
        # Md+ = fd*lx^2/8 = 6,104*16/8 = 12,208 kNm/m ; por nervura *0,5
        assert r["momentos"]["Md_pos_kNm_m"] == pytest.approx(12.208, abs=0.01)
        assert r["momentos"]["Md_pos_nerv"] == pytest.approx(6.104, abs=0.01)
        assert r["momentos"]["Md_neg_kNm_m"] == pytest.approx(0.0, abs=0.001)

    def test_armadura_LN_na_mesa(self, r):
        a = r["armaduras"]["As_pos"]
        assert a["secao"] == "retangular (LN na mesa)"
        assert a["As_cm2"] == pytest.approx(1.65, abs=0.02)
        assert a["ok_ductil"] is True

    def test_criterio_cisalhamento_laje(self, r):
        assert r["cisalhamento"]["criterio"] == "laje"
        assert r["cisalhamento"]["VRd1_nerv_kN"] == pytest.approx(5.194, abs=0.02)

    def test_flecha(self, r):
        assert r["els_flecha"]["I_T_cm4"] == pytest.approx(2556.5, abs=1.0)
        assert r["els_flecha"]["w0_mm"] == pytest.approx(7.99, abs=0.05)
        # h=12 em 4 m reprova flecha (esperado p/ trelicada esbelta)
        assert r["els_flecha"]["ok"] is False


class TestCriterioCisalhamentoMusso:
    """Tabela §13.4.2 a/b/c do Musso por espacamento e."""

    def test_ate_65_laje(self):
        assert _criterio_cisalhamento(60, 9)[0] == "laje"

    def test_entre_65_90_bw_largo_laje(self):
        assert _criterio_cisalhamento(80, 13)[0] == "laje"

    def test_entre_65_110_viga(self):
        assert _criterio_cisalhamento(80, 9)[0] == "viga"
        assert _criterio_cisalhamento(100, 13)[0] == "viga"

    def test_acima_110_mesa_macica(self):
        assert _criterio_cisalhamento(120, 13)[0] == "mesa_macica"


class TestSecaoT_LN_na_nervura:
    """Ramo da secao T real: Md acima da capacidade da mesa -> LN na alma.

    Numa trelicada usual a LN cai na mesa (bf largo); o ramo T so e exercitado
    com Md alto e secao profunda, testado direto na funcao de armadura.
    """

    def test_armar_secao_T(self):
        fcd = 25.0 / 1.4 / 10.0      # 1,786 kN/cm2
        fyd = 500.0 / 1.15 / 10.0    # 43,48 kN/cm2
        # Md = 8000 kNcm > M_mesa (~6800) com bf=40, hf=4, bw=9, d=30 -> T real
        a = _armar_secao_T(8000.0, bf=40.0, bw=9.0, hf=4.0, d=30.0, fcd=fcd, fyd=fyd)
        assert a["secao"] == "T (LN na nervura)"
        assert a["As_cm2"] == pytest.approx(6.73, abs=0.1)
        assert a["ok_ductil"] is True

    def test_armar_LN_mesa_quando_Md_baixo(self):
        fcd, fyd = 25.0 / 1.4 / 10.0, 500.0 / 1.15 / 10.0
        a = _armar_secao_T(600.0, bf=40.0, bw=9.0, hf=4.0, d=30.0, fcd=fcd, fyd=fyd)
        assert a["secao"] == "retangular (LN na mesa)"


def test_inercia_T_retangular_degenera():
    # se bf==bw e hf==h, secao T degenera p/ retangulo: I = b*h^3/12
    I, yt = _inercia_T(10.0, 10.0, 20.0, 20.0)
    assert I == pytest.approx(10.0 * 20.0**3 / 12.0, rel=1e-6)
    assert yt == pytest.approx(10.0, abs=1e-6)
