# tests/test_fissuracao.py - Motor de abertura de fissuras wk (NBR 6118:2023, 17.3.3.2)
import math

import pytest

from core.fissuracao import (
    fctm, ecs, tensao_aco_estadio2, tensao_aco_flexotracao,
    area_envolvente_por_metro, abertura_wk, verificar_fissuracao,
    verificar_fissuracao_flexotracao, ETA1_NERVURADA, ES_MPA,
)


# --- Propriedades dos materiais ------------------------------------------------

def test_fctm_c40():
    # fctm = 0,3 * 40^(2/3) ~ 3,51 MPa
    assert fctm(40.0) == pytest.approx(3.509, abs=1e-3)


def test_ecs_c40_granito():
    # Eci = 5600*sqrt(40)=35418; alpha_i=0,9; Ecs ~ 31876 MPa
    assert ecs(40.0, 1.0) == pytest.approx(31876.0, rel=1e-3)


# --- Tensao no aco (Estadio II) ------------------------------------------------

def test_tensao_estadio2_exemplo_conferido():
    # b=100, d=16, As=5 cm2, M_serv=800 kN.cm, C40 -> conferido a mao:
    # x_II~2,93 cm; sigma_s~106,5 MPa.
    t2 = tensao_aco_estadio2(800.0, 5.0, 100.0, 16.0, 40.0)
    assert t2.x_ii_cm == pytest.approx(2.93, abs=0.05)
    assert t2.sigma_s_mpa == pytest.approx(106.5, rel=0.02)
    assert t2.alpha_e == pytest.approx(6.588, rel=0.01)


def test_tensao_estadio2_cresce_com_momento():
    base = tensao_aco_estadio2(800.0, 5.0, 100.0, 16.0, 40.0)
    maior = tensao_aco_estadio2(1200.0, 5.0, 100.0, 16.0, 40.0)
    # sigma_s e linear em M (mesma secao/I_II) -> proporcional.
    assert maior.sigma_s_mpa == pytest.approx(base.sigma_s_mpa * 1.5, rel=1e-3)


def test_tensao_estadio2_mais_armadura_reduz_tensao():
    pouca = tensao_aco_estadio2(800.0, 5.0, 100.0, 16.0, 40.0)
    muita = tensao_aco_estadio2(800.0, 10.0, 100.0, 16.0, 40.0)
    assert muita.sigma_s_mpa < pouca.sigma_s_mpa


def test_tensao_estadio2_rejeita_entrada_invalida():
    with pytest.raises(ValueError):
        tensao_aco_estadio2(800.0, 0.0, 100.0, 16.0, 40.0)


# --- Tensao no aco em FLEXO-TRACAO (Estadio II, N+M) ---------------------------

def test_flexotracao_sem_normal_reduz_a_flexao_pura():
    # Nd=0 -> deve coincidir com a flexao simples (mesmo sigma_s).
    flex = tensao_aco_estadio2(800.0, 5.0, 100.0, 16.0, 40.0)
    ft = tensao_aco_flexotracao(800.0, 0.0, 5.0, 100.0, 16.0, 20.0, 40.0)
    assert ft.caso == "flexao"
    assert ft.sigma_s_mpa == pytest.approx(flex.sigma_s_mpa, abs=0.1)


def test_flexotracao_grande_excentricidade():
    # b=100, d=16, h=20, d'=4 -> z=12; M=800 kNcm, N=20 kN -> e0=40 > z/2=6.
    # Solucao numerica (Estadio II): x~2,48 cm; sigma_s ~130 MPa (> 106,5 da flexao).
    ft = tensao_aco_flexotracao(800.0, 20.0, 5.0, 100.0, 16.0, 20.0, 40.0)
    assert ft.caso == "grande"
    assert ft.x_ii_cm == pytest.approx(2.48, abs=0.1)
    assert ft.sigma_s_mpa == pytest.approx(129.6, rel=0.04)
    # tracao adicionada eleva a tensao no aco frente a flexao pura.
    assert ft.sigma_s_mpa > tensao_aco_estadio2(800.0, 5.0, 100.0, 16.0, 40.0).sigma_s_mpa


def test_flexotracao_pequena_excentricidade_secao_toda_tracionada():
    # M=60 kNcm, N=20 kN -> e0=3 <= z/2=6 -> secao toda tracionada.
    # e2 = z/2+e0 = 9; sigma_s = N*e2/(z*As1) = 20*9/(12*5) = 3 kN/cm2 = 30 MPa.
    ft = tensao_aco_flexotracao(60.0, 20.0, 5.0, 100.0, 16.0, 20.0, 40.0)
    assert ft.caso == "pequena"
    assert ft.x_ii_cm == 0.0
    assert ft.sigma_s_mpa == pytest.approx(30.0, abs=0.1)


def test_flexotracao_continua_na_fronteira_e0_igual_z_meios():
    # e0 = z/2 = 6 -> ambas as formulas dao sigma_s = N/As1 = 20/5 = 4 kN/cm2 = 40 MPa.
    ft = tensao_aco_flexotracao(120.0, 20.0, 5.0, 100.0, 16.0, 20.0, 40.0)
    assert ft.sigma_s_mpa == pytest.approx(40.0, abs=0.5)


def test_flexotracao_mais_normal_eleva_tensao():
    pouca = tensao_aco_flexotracao(800.0, 20.0, 5.0, 100.0, 16.0, 20.0, 40.0)
    muita = tensao_aco_flexotracao(800.0, 60.0, 5.0, 100.0, 16.0, 20.0, 40.0)
    assert muita.sigma_s_mpa > pouca.sigma_s_mpa


def test_flexotracao_rejeita_entrada_invalida():
    with pytest.raises(ValueError):
        tensao_aco_flexotracao(800.0, 20.0, 0.0, 100.0, 16.0, 20.0, 40.0)


def test_verificar_fissuracao_flexotracao_encadeia():
    ab, ft = verificar_fissuracao_flexotracao(
        m_serv_kncm=800.0, n_serv_kn=20.0, as1_cm2=5.0, b_cm=100.0,
        d_cm=16.0, h_cm=20.0, fck_mpa=40.0, phi_mm=12.5,
    )
    assert ft.sigma_s_mpa > 0
    assert ab.wk_mm > 0
    # com tracao, wk e maior que na flexao pura de mesmo M.
    ab_flex, _ = verificar_fissuracao(800.0, 5.0, 100.0, 16.0, 20.0, 40.0, 12.5)
    assert ab.wk_mm > ab_flex.wk_mm


# --- Area de envolvimento ------------------------------------------------------

def test_acri_limitada_por_75phi():
    # h=20, d=16 -> 2*(h-d)=8 cm; 2*7,5*phi(10mm)=15 cm -> vence 8 -> Acri=800 cm2
    assert area_envolvente_por_metro(20.0, 16.0, 10.0) == pytest.approx(800.0)


def test_acri_limitada_pelo_envelope_quando_cobrimento_grande():
    # h=40, d=20 -> 2*(h-d)=40 cm; 2*7,5*phi(8mm)=12 cm -> vence 12 -> Acri=1200 cm2
    assert area_envolvente_por_metro(40.0, 20.0, 8.0) == pytest.approx(1200.0)


# --- Abertura wk (formula da norma) -------------------------------------------

def test_wk_exemplo_conferido():
    # phi=10, sigma_s=106,5 MPa, fctm(C40)=3,509, rho_r=5/800=0,00625
    # -> w1~0,0164 (governa), w2~0,123 -> wk=0,0164 mm
    ab = abertura_wk(10.0, 106.5, fctm(40.0), 5.0 / 800.0)
    assert ab.w1_mm == pytest.approx(0.0164, abs=5e-4)
    assert ab.w2_mm == pytest.approx(0.1235, abs=2e-3)
    assert ab.wk_mm == ab.w1_mm
    assert ab.wk_mm == pytest.approx(0.0164, abs=5e-4)


def test_wk_pega_o_menor_dos_dois():
    ab = abertura_wk(10.0, 250.0, fctm(40.0), 0.002)
    assert ab.wk_mm == min(ab.w1_mm, ab.w2_mm)


def test_wk_cresce_com_bitola():
    fina = abertura_wk(8.0, 150.0, fctm(40.0), 0.006)
    grossa = abertura_wk(16.0, 150.0, fctm(40.0), 0.006)
    assert grossa.wk_mm > fina.wk_mm


def test_wk_rejeita_rho_invalido():
    with pytest.raises(ValueError):
        abertura_wk(10.0, 150.0, 3.5, 0.0)


# --- Encadeamento de conveniencia ---------------------------------------------

def test_verificar_fissuracao_reservatorio_ok():
    # Parede de reservatorio bem armada -> wk << 0,10 mm
    ab, t2 = verificar_fissuracao(
        m_serv_kncm=800.0, as_cm2=5.0, b_cm=100.0, d_cm=16.0,
        h_cm=20.0, fck_mpa=40.0, phi_mm=10.0, w_lim_mm=0.10,
    )
    assert t2.sigma_s_mpa > 0
    assert ab.wk_mm < 0.10


def test_verificar_fissuracao_reprova_secao_subarmada():
    # Pouca armadura + momento alto -> sigma_s alta -> wk pode estourar 0,10 mm
    ab, _ = verificar_fissuracao(
        m_serv_kncm=2500.0, as_cm2=3.0, b_cm=100.0, d_cm=16.0,
        h_cm=20.0, fck_mpa=40.0, phi_mm=12.5, w_lim_mm=0.10,
    )
    assert ab.wk_mm > 0.10
