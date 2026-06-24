"""Testes das estruturas de resultado (core/resultado.py - Fatia 3/A1).

Validam a logica de status/folga/utilizacao nas DUAS direcoes de comparacao,
usando numeros dos exemplos golden (muro Rankine, viga, pilar) para garantir
que o painel valor x limite x status casa com a fisica ja congelada.
"""
import pytest

from core.resultado import (
    Verificacao, ResultadoElemento, verif_max, verif_min, OP_MIN,
)


# ── OP_MAX: valor <= limite e OK ──────────────────────────────────────────
class TestOperadorMax:
    def test_passa_com_folga(self):
        # Flecha de laje: 6,85 mm <= L/250 = 14 mm -> OK
        v = verif_max("Flecha (ELS)", 6.85, 14.0, "mm")
        assert v.passou is True
        assert v.status == "OK"
        assert v.folga == pytest.approx(7.15)
        assert v.utilizacao == pytest.approx(0.4893, abs=1e-3)

    def test_reprova_quando_excede(self):
        v = verif_max("Flecha (ELS)", 20.0, 14.0, "mm")
        assert v.passou is False
        assert v.status == "NAO OK"
        assert v.folga == pytest.approx(-6.0)      # folga negativa = estourou
        assert v.utilizacao > 1.0

    def test_limite_exato_passa(self):
        # Ductilidade no limite: x/d = 0,45 exatamente -> OK (tolerancia)
        v = verif_max("Ductilidade x/d", 0.45, 0.45)
        assert v.passou is True

    def test_pequena_ultrapassagem_de_ponto_flutuante_passa(self):
        v = verif_max("Ductilidade x/d", 0.45 + 1e-12, 0.45)
        assert v.passou is True


# ── OP_MIN: valor >= limite e OK (estabilidade de muro) ───────────────────
class TestOperadorMin:
    def test_fst_passa(self):
        # Muro golden: FST = 2,302 >= 1,5 -> OK
        v = verif_min("FST (tombamento)", 2.302, 1.5)
        assert v.passou is True
        assert v.status == "OK"
        assert v.operador == OP_MIN
        assert v.folga == pytest.approx(0.802)

    def test_fsd_reprova(self):
        # Muro golden: FSD = 0,978 < 1,5 -> NAO OK (geometria escorrega)
        v = verif_min("FSD (deslizamento)", 0.978, 1.5)
        assert v.passou is False
        assert v.status == "NAO OK"
        assert v.utilizacao > 1.0   # demanda acima da capacidade


# ── ResultadoElemento: agregacao ──────────────────────────────────────────
class TestResultadoElemento:
    def test_tudo_ok_quando_todas_passam(self):
        r = ResultadoElemento("viga")
        r.add(verif_max("Bielas Vsd<=VRd2", 55.0, 212.63, "kN"))
        r.add(verif_max("Ductilidade x/d", 0.239, 0.45))
        assert r.tudo_ok is True
        assert r.reprovadas == []

    def test_reprovadas_lista_so_as_que_falham(self):
        r = ResultadoElemento("muro")
        r.add(verif_min("FST", 2.302, 1.5))
        r.add(verif_min("FSD", 0.978, 1.5))
        assert r.tudo_ok is False
        assert len(r.reprovadas) == 1
        assert r.reprovadas[0].nome == "FSD"

    def test_sem_verificacoes_e_tudo_ok(self):
        # vacuamente verdadeiro - elemento sem checagens nao reprova
        assert ResultadoElemento("laje").tudo_ok is True

    def test_imutabilidade_da_verificacao(self):
        v = verif_max("x", 1.0, 2.0)
        with pytest.raises(Exception):
            v.valor = 9.0  # frozen -> deve falhar
