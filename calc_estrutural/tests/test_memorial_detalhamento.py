# Tabela de aco editavel no detalhamento de viga, pilar e muro.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from relatorio.passo_a_passo import memorial_viga, memorial_pilar, memorial_muro


def _passo6(passos):
    return next(p for p in passos if p.titulo.startswith("Passo 6"))


def test_viga_simples_tem_tabela_de_arranjos():
    passos, _ = memorial_viga(20, 50, 5.0, 80.0, 90.0, fck=25, fyk=500, caa="II")
    p6 = _passo6(passos)
    assert p6.tabela
    assert {"Arranjo", "As prov (cm²)"} <= set(p6.tabela[0])
    assert any(l["Rec."] == "★" for l in p6.tabela)


def test_pilar_tem_tabela_de_arranjos():
    passos, _ = memorial_pilar(300, 20, 30, 1.0, 800.0, 2000.0, fck=25, fyk=500, caa="II")
    p6 = _passo6(passos)
    assert p6.tabela
    assert any(l["Rec."] == "★" for l in p6.tabela)


def test_muro_fuste_tem_tabela_de_aco():
    passos, _ = memorial_muro(3.0, 30, 18, qs=0.0, fck=25, fyk=500, caa="III")
    p = next(p for p in passos if "Detalhamento do fuste" in p.titulo)
    assert p.tabela
    assert {"Ø (mm)", "Espac. (cm)", "As prov (cm²/m)"} <= set(p.tabela[0])
    assert any(l["Rec."] == "★" for l in p.tabela)
