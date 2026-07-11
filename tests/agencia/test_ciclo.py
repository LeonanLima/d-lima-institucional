import pytest

from agencia.core.modelos import Formato, Pauta, Peca, StatusPeca, aprovar
from agencia.core.ciclo import montar_pecas, publicaveis, priorizar_pautas
from agencia.core.memoria import Aprendizado, registrar


def test_montar_pecas_casa_legenda_por_tema():
    pautas = [Pauta(tema="MCMV", angulo="a", formato=Formato.REEL)]
    pecas = montar_pecas(pautas, {"MCMV": "legenda do reel"})
    assert len(pecas) == 1
    assert pecas[0].legenda == "legenda do reel"
    assert pecas[0].status == StatusPeca.AGUARDANDO_APROVACAO


def test_montar_pecas_sem_legenda_falha():
    pautas = [Pauta(tema="MCMV", angulo="a", formato=Formato.REEL)]
    with pytest.raises(ValueError):
        montar_pecas(pautas, {})


def test_trava_so_publica_aprovado():
    pauta = Pauta(tema="x", angulo="y", formato=Formato.FEED)
    aguardando = Peca(pauta=pauta, legenda="z", status=StatusPeca.AGUARDANDO_APROVACAO)
    aprovada = aprovar(Peca(pauta=pauta, legenda="w"))
    saida = publicaveis([aguardando, aprovada])
    assert saida == [aprovada]


def test_prioriza_por_memoria(tmp_path):
    arq = str(tmp_path / "m.json")
    registrar(arq, Aprendizado(tema="Bastidor", formato="Reel", engajamento=9.0, nota=""))
    pautas = [
        Pauta(tema="MCMV", angulo="a", formato=Formato.REEL),
        Pauta(tema="Bastidor", angulo="b", formato=Formato.REEL),
    ]
    ordenadas = priorizar_pautas(pautas, arq)
    assert ordenadas[0].tema == "Bastidor"
