# tests/test_painel_verificacoes.py - trava as linhas do painel de verificacoes
from core.resultado import verif_max, verif_min
from ui.componentes import linhas_verificacoes, _tabela_markdown


def test_linha_ok_max():
    v = verif_max("Flecha (ELS)", 12.0, 16.0, "mm", "NBR 6118 §13")
    (linha,) = linhas_verificacoes([v])
    assert linha["Verificação"] == "Flecha (ELS)"
    assert linha["Valor"] == "12 mm"
    assert linha["Limite"] == "≤ 16 mm"
    assert linha["Status"] == "✅ OK"
    assert linha["Uso"] == "75%"


def test_linha_reprova_max():
    v = verif_max("Ductilidade x/d", 0.50, 0.45)
    (linha,) = linhas_verificacoes([v])
    assert linha["Status"] == "❌ NÃO OK"
    assert linha["Limite"] == "≤ 0.45"      # sem unidade -> sem sufixo


def test_linha_min_usa_simbolo_maior():
    v = verif_min("FS deslizamento", 1.8, 1.5)
    (linha,) = linhas_verificacoes([v])
    assert linha["Limite"].startswith("≥")
    assert linha["Status"] == "✅ OK"


def test_lista_vazia():
    assert linhas_verificacoes([]) == []


def test_tabela_markdown_estrutura():
    # tabela markdown sem pandas (imune a ABI numpy/pandas): cabecalho + sep + 1 linha
    linhas = linhas_verificacoes([verif_max("Flecha (ELS)", 12.0, 16.0, "mm")])
    md = _tabela_markdown(linhas)
    partes = md.split("\n")
    assert partes[0].startswith("| Verificação |")
    assert set(partes[1].replace(" ", "")) <= {"|", "-"}   # linha separadora
    assert "Flecha (ELS)" in partes[2]
    assert "✅ OK" in partes[2]


def test_tabela_markdown_vazia():
    assert _tabela_markdown([]) == ""
