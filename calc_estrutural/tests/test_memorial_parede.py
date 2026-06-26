# Garante que os memoriais de parede hidraulica narram a partir do motor
# canonico (dimensionar_parede_placa) - mesma fonte de dados, mesmos numeros.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from relatorio.passo_a_passo import memorial_reservatorio, memorial_piscina
from dimensionamento.bares import dimensionar_parede_placa


def test_reservatorio_cheio_bate_com_motor_canonico():
    passos, r = memorial_reservatorio("Elevado", "Cheio", 2.4, 4.75, 20,
                                      fck=40, fyk=500, caa="IV")
    esperado = dimensionar_parede_placa(2.4, 4.75, 0.20, 10.0 * 2.4, 40, 500, "IV")
    for k in ("Mx", "Mxe", "My", "Mye", "As_vao_x", "As_eng_x",
              "As_vao_y", "As_eng_y", "As_cm2m", "Nd_anel_kNm"):
        assert r[k] == esperado[k]
    # 7 passos: modelo + 4 momentos + flexo-tracao + flexao + min/ELS + detalhamento
    assert len(passos) == 7
    assert r["carga"].startswith("agua")
    # Passo 7 traz a tabela de aco editavel (varias bitolas por face)
    det = passos[-1]
    assert "Detalhamento" in det.titulo
    assert det.tabela, "detalhamento deve listar opcoes de bitola"
    assert {"Face", "Ø (mm)", "Espac. (cm)", "As prov (cm²/m)"} <= set(det.tabela[0])
    assert any(linha["Rec."] == "★" for linha in det.tabela)


def test_memorial_tem_os_quatro_momentos_e_flexotracao():
    passos, r = memorial_piscina("Cheia", 1.5, 4.0, 20,
                                 fck=40, fyk=500, caa="IV")
    titulos = " | ".join(p.titulo for p in passos)
    assert "Mx, Mxe, My, Mye" in titulos          # os 4 momentos
    assert "flexo-tracao" in titulos.lower()       # horizontal
    assert "VERTICAL" in titulos                    # flexao vertical
    # consistencia com o motor canonico (CAA IV, fck 40 - NBR 6118 sec.21)
    esperado = dimensionar_parede_placa(1.5, 4.0, 0.20, 10.0 * 1.5, 40, 500, "IV")
    assert r["As_cm2m"] == esperado["As_cm2m"]


def test_reservatorio_elevado_vazio_sem_pressao():
    # Elevado vazio: p = 0 -> memorial cai no caso "sem empuxo" + As,min
    passos, r = memorial_reservatorio("Elevado", "Vazio", 2.4, 4.75, 20)
    assert r.get("As_cm2m") == 0
    assert any("Sem empuxo" in p.titulo for p in passos)
