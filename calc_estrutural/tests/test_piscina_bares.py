"""Parede de piscina como placa de Bares (laterais apoiadas + base engastada; topo livre)."""
import pytest

from dimensionamento.piscina import combinacoes_piscina, dimensionar_parede
from dimensionamento.bares import momentos_parede


def test_parede_usa_momentos_de_bares():
    H, largura, esp = 1.5, 8.0, 0.15
    C1, _C2, _C3 = combinacoes_piscina(H)          # cheia: p_net_base = 10*1.5 = 15
    r = dimensionar_parede(H, largura, esp, C1, fck=40, fyk=500, caa="IV")
    # momentos batem com a tabela de Bares para pd = 1,4 * 15 = 21 kN/m2
    M = momentos_parede(largura, H, 1.4 * C1["p_net_base"])
    assert r["Mye"] == pytest.approx(M["Mye"])
    assert r["My"] == pytest.approx(M["My"])
    # 4 armaduras presentes e governante = a maior delas
    assert r["As_cm2m"] == max(r["As_vao_x"], r["As_vao_y"],
                               r["As_eng_x"], r["As_eng_y"])
    assert r["As_cm2m"] >= r["As_min"]


def test_combinacao_sem_pressao_nao_arma():
    H, largura, esp = 1.5, 8.0, 0.15
    sem_p = {"p_net_base": 0.0}
    r = dimensionar_parede(H, largura, esp, sem_p)
    assert r["As_cm2m"] == 0


def test_solo_inverte_sinal_mas_mantem_engaste():
    # C2 (vazia+solo) usa a MESMA tabela; muda a magnitude de p, nao o vinculo.
    H, largura, esp = 2.0, 4.0, 0.20
    _C1, C2, _C3 = combinacoes_piscina(H, phi_solo=30, gamma_solo=18)
    r = dimensionar_parede(H, largura, esp, C2, fck=40, fyk=500, caa="IV")
    assert "As_cm2m" in r and r["As_cm2m"] >= r["As_min"]
