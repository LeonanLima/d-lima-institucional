from agencia.core.modelos import Formato, StatusPeca, Pauta, Peca, aprovar


def test_peca_nasce_em_ideacao():
    pauta = Pauta(tema="Financiamento MCMV", angulo="dúvida comum", formato=Formato.CARROSSEL)
    peca = Peca(pauta=pauta, legenda="Como sair do aluguel...")
    assert peca.status == StatusPeca.IDEACAO
    assert peca.arte_path is None


def test_aprovar_retorna_nova_peca_imutavel():
    pauta = Pauta(tema="x", angulo="y", formato=Formato.REEL)
    peca = Peca(pauta=pauta, legenda="z")
    aprovada = aprovar(peca)
    assert aprovada.status == StatusPeca.APROVADO
    assert peca.status == StatusPeca.IDEACAO  # original intacto
    assert aprovada.legenda == "z"
