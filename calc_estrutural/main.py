#!/usr/bin/env python3
# main.py - Smoke-test de terminal do Sistema de Calculo Estrutural
# NBR 6118:2023 | NBR 6120:2019 | Prof. Carini / Bastos / Araujo / Fusco
#
# A interface de uso e o app Streamlit (app_estrutural.py). Este modulo
# existe apenas como sanity-check rapido pela linha de comando: roda um
# exemplo representativo de cada elemento e reporta PASS/FAIL, sem depender
# da camada de apresentacao. A fisica esta congelada nos golden tests
# (tests/test_golden.py); aqui so verificamos que nada quebra na chamada.

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dimensionamento.predim import (
    predimensionar_laje, predimensionar_viga, predimensionar_pilar,
)
from dimensionamento.pilar import (
    calcular_esbeltez, excentricidade_minima, dimensionar_secao,
)
from dimensionamento.viga import (
    verificar_bielas, dimensionar_estribos, armadura_simples,
    calcular_flecha_branson,
)
from dimensionamento.laje import calcular_laje_macica
from dimensionamento.reservatorio import (
    predimensionar_reservatorio as predim_res,
    paredes_dimensionar, fundo_dimensionar,
)
from dimensionamento.muro_arrimo import (
    predimensionar_muro, calcular_empuxo,
    verificar_estabilidade, dimensionar_fuste,
)
from dimensionamento.piscina import (
    combinacoes_piscina, dimensionar_parede as dim_par_pisc,
    dimensionar_fundo as dim_fundo_pisc,
)
from dimensionamento.viga_parede import (
    classificar_viga_parede, modelo_biela_tirante,
)


def _predim():
    predimensionar_laje(4.0, 5.0, "residencial")
    predimensionar_viga(4.0, "continua")
    predimensionar_pilar(500, 25, "intermediario")


def _laje():
    calcular_laje_macica(3.5, 4.5, 10, 1.5, 1.5, 1, 25, 500, "II")


def _viga():
    bw, h, d, L, fck, fyk = 14, 40, 36.875, 4.0, 25, 500
    verificar_bielas(30, bw, d, fck)
    dimensionar_estribos(30, bw, d, fck, fyk)
    flex = armadura_simples(1200, bw, d, fck, fyk)
    calcular_flecha_branson(800, flex.get("As_cm2", 1), bw, h, d, L, fck)


def _pilar():
    H, hx, hy = 300, 19, 19
    calcular_esbeltez(H, hx, hy, 1.0)
    excentricidade_minima(hx, hy)
    dimensionar_secao(300, 150, hx, hy, 25, 500, "II")


def _reservatorio():
    predim_res(10)
    paredes_dimensionar(2.0, 3.0, 0.20, 40, 500, "IV")
    fundo_dimensionar(2.0, 3.0, 3.0, 0.15, 40, 500, "IV")


def _muro():
    predim = predimensionar_muro(3.0, 30, 18)
    emp = calcular_empuxo(3.0, 18, 30, 0.0, 0)
    verificar_estabilidade(predim, emp, 18)
    dimensionar_fuste(predim, emp, 25, 500, "II")


def _piscina():
    combs = combinacoes_piscina(1.5, 30, 18)
    dim_par_pisc(1.5, 8.0, 0.15, combs[0], 40, 500, "IV")
    dim_fundo_pisc(1.5, 8.0, 4.0, 0.15, 40, 500, "IV")


def _viga_parede():
    classificar_viga_parede(4.0, 2.5)
    modelo_biela_tirante(4.0, 2.5, 300, 20, 25, 500, "II")


SMOKES = {
    "Pre-dimensionamento": _predim,
    "Laje macica":         _laje,
    "Viga":                _viga,
    "Pilar":               _pilar,
    "Reservatorio":        _reservatorio,
    "Muro de arrimo":      _muro,
    "Piscina":             _piscina,
    "Viga-parede":         _viga_parede,
}


def main():
    print("=" * 60)
    print("SMOKE-TEST - SISTEMA DE CALCULO ESTRUTURAL - NBR 6118:2023")
    print("=" * 60)
    falhas = 0
    for nome, fn in SMOKES.items():
        try:
            fn()
            print(f"  [PASS] {nome}")
        except Exception as e:
            falhas += 1
            print(f"  [FAIL] {nome}: {type(e).__name__}: {e}")
    print("-" * 60)
    if falhas:
        print(f"  {falhas} elemento(s) com falha.")
        return 1
    print("  Todos os elementos rodaram sem erro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
