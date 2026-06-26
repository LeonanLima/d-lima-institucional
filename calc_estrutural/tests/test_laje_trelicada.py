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


class TestTrelicadaRomanioViga:
    """Caso ancorado em FORMA COMERCIAL real (Romanio RO80, Musso slides 24-25).

    Os slides 23-25 do Musso NAO trazem um exemplo numerico transcrivel: o slide 23
    ("dimensionamento automatico" da nervurada) e uma IMAGEM de planilha (sem camada
    de texto, igual ao exemplo automatico da macica no slide 20) e os slides 24-25
    sao catalogos de formas Romanio (RO 600x600x180, RO 650x650x210, RO 800x800).
    Em vez de travar um exemplo inexistente, este golden usa a geometria da forma
    real RO80 (intereixo e=80 cm) e confere por primeiros principios.

    Valor do caso: e=80 cm com bw=9 cm (<=12) cai no ramo b) do Musso (§13.4.2) e
    exercita o criterio de cisalhamento "viga" END-TO-END por calcular_laje_trelicada
    (os outros goldens so testam o ramo "viga" no helper _criterio_cisalhamento),
    chegando a precisa_estribo=True.

    lx=5,0 | e=80 | capa=5 | h=25 | bw=9 | gk=1,5 qk=2,0 | apoio/apoio.
    """

    @pytest.fixture(scope="class")
    def r(self):
        return calcular_laje_trelicada(lx=5.0, e_cm=80, h_capa_cm=5, h_total_cm=25,
                                       bw_cm=9, gk=1.5, qk=2.0,
                                       vinculacao="apoio_apoio")

    def test_pp_e_carga(self, r):
        # A_c = 80*5 + 9*20 = 580 cm2 ; PP = 25*(580/1e4)/0,80 = 1,8125 kN/m2
        assert r["PP_kNm2"] == pytest.approx(1.81, abs=0.01)
        # fd = 1,4*(1,5+1,8125+2,0) = 7,4375
        assert r["fd_kNm2"] == pytest.approx(7.44, abs=0.01)

    def test_esforcos(self, r):
        assert r["momentos"]["Md_pos_kNm_m"] == pytest.approx(23.242, abs=0.01)
        assert r["momentos"]["Md_pos_nerv"] == pytest.approx(18.594, abs=0.01)
        assert r["momentos"]["Vd_nerv"] == pytest.approx(14.875, abs=0.01)

    def test_armadura_LN_na_mesa(self, r):
        a = r["armaduras"]["As_pos"]
        assert a["secao"] == "retangular (LN na mesa)"
        assert a["As_cm2"] == pytest.approx(1.98, abs=0.02)
        assert a["ok_ductil"] is True

    def test_criterio_viga_end_to_end(self, r):
        # e=80, bw=9 (<=12): ramo b) -> "viga"; VRd1 < VSd -> exige estribo
        c = r["cisalhamento"]
        assert c["criterio"] == "viga"
        assert c["VRd1_nerv_kN"] == pytest.approx(10.16, abs=0.05)
        assert c["ok"] is False
        assert c["precisa_estribo"] is True

    def test_flecha_passa(self, r):
        f = r["els_flecha"]
        assert f["I_T_cm4"] == pytest.approx(26229.9, abs=2.0)
        assert f["yt_cm"] == pytest.approx(6.38, abs=0.02)
        assert f["w0_mm"] == pytest.approx(4.02, abs=0.05)
        # h=25 em 5 m c/ capa 5 passa na flecha (w_total=14,1 mm < L/250=20 mm)
        assert f["ok"] is True


def test_inercia_T_retangular_degenera():
    # se bf==bw e hf==h, secao T degenera p/ retangulo: I = b*h^3/12
    I, yt = _inercia_T(10.0, 10.0, 20.0, 20.0)
    assert I == pytest.approx(10.0 * 20.0**3 / 12.0, rel=1e-6)
    assert yt == pytest.approx(10.0, abs=1e-6)
