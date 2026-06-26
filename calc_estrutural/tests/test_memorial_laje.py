# Detalhamento da laje: barras avulsas por face + malha POP (tela soldada).
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from relatorio.passo_a_passo import memorial_laje


def test_laje_detalha_barras_e_malha_pop():
    passos, _res = memorial_laje(4.0, 5.0, 12, gk=1.0, qk=2.0, caso=1,
                                 fck=25, fyk=500, caa="II")
    titulos = [p.titulo for p in passos]
    assert any("barras avulsas" in t for t in titulos)
    assert any("malha POP" in t for t in titulos)

    barras = next(p for p in passos if "barras avulsas" in p.titulo)
    assert barras.tabela
    assert {"Face", "Ø (mm)", "Espac. (cm)", "As prov (cm²/m)"} <= set(barras.tabela[0])
    assert any(l["Rec."] == "★" for l in barras.tabela)

    tela = next(p for p in passos if "malha POP" in p.titulo)
    assert tela.tabela                                   # As tipico cabe em tela Q
    assert tela.tabela[0]["Tela (malha POP)"].startswith("Q-")
    assert any(l["Rec."] == "★" for l in tela.tabela)
