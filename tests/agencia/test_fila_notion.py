from agencia.core.modelos import Formato, Pauta, Peca, StatusPeca
from agencia.core.fila_notion import (
    PROPRIEDADES_DB,
    peca_para_propriedades,
    peca_para_markdown,
)


def _peca():
    pauta = Pauta(tema="Sair do aluguel", angulo="passo a passo", formato=Formato.CARROSSEL)
    return Peca(
        pauta=pauta,
        legenda="Você paga aluguel há anos? Veja como a casa própria...",
        status=StatusPeca.AGUARDANDO_APROVACAO,
        arte_path="docs/design/pecas/sair-do-aluguel.html",
        data_sugerida="2026-07-15",
    )


def test_schema_tem_status_e_formato():
    assert PROPRIEDADES_DB["Status"] == "select"
    assert PROPRIEDADES_DB["Formato"] == "select"


def test_propriedades_do_card():
    props = peca_para_propriedades(_peca())
    assert props["Título"] == "Sair do aluguel"
    assert props["Formato"] == "Carrossel"
    assert props["Status"] == "Aguardando aprovação"
    assert props["Data sugerida"] == "2026-07-15"


def test_markdown_mostra_legenda_e_angulo():
    md = peca_para_markdown(_peca())
    assert "passo a passo" in md
    assert "Você paga aluguel" in md
    assert "sair-do-aluguel.html" in md
