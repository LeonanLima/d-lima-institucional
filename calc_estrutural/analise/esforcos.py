# analise/esforcos.py - Solver 1D de viga biapoiada (esforcos + linha elastica)
#
# Calcula reacoes, cortante V(x), momento fletor M(x) e a linha elastica
# (flecha ao longo do vao) de uma viga simplesmente apoiada submetida a
# cargas distribuidas (cheias ou parciais) e cargas pontuais, por
# superposicao numerica - vale para QUALQUER combinacao de cargas sem
# catalogar caso a caso.
#
# CONVENCAO DE SINAIS:
#   - carga para baixo  -> positiva (q > 0, P > 0)
#   - flecha para baixo -> positiva (delta > 0)
#   - momento positivo  -> tracao na fibra inferior (sagging)
#
# METODO:
#   1. Reacoes por equilibrio (Sum M = 0, Sum F = 0).
#   2. V(x) = RA - (carga a esquerda de x).
#   3. M(x) = integral de V(x) de 0 ate x (trapezio cumulativo).
#   4. Linha elastica: EI*y'' = M -> dupla integracao de M/EI com as duas
#      condicoes de contorno y(0) = y(L) = 0, que fixam a constante de
#      integracao. Flecha para baixo delta = -y.
#
# REFERENCIAS:
#   HIBBELER, R.C. Resistencia dos Materiais. 7.ed. Pearson, 2010 (cap. 6, 12).
#   TIMOSHENKO, S.P. Resistencia dos Materiais. Vol.1. (linha elastica).
from dataclasses import dataclass
from typing import Optional

# Numero padrao de pontos da malha (impar -> inclui o meio do vao)
N_PONTOS_PADRAO = 201


@dataclass(frozen=True)
class CargaDistribuida:
    # Carga uniformemente distribuida [kN/m], positiva para baixo.
    # Atua de x_ini ate x_fim (None = ate o fim do vao L).
    q: float
    x_ini: float = 0.0
    x_fim: Optional[float] = None


@dataclass(frozen=True)
class CargaPontual:
    # Carga concentrada [kN], positiva para baixo, na posicao a [m]
    # medida a partir do apoio esquerdo.
    P: float
    a: float


def _trecho(carga: CargaDistribuida, L: float) -> tuple:
    # Retorna (x_ini, x_fim) da carga distribuida resolvendo x_fim=None.
    x_ini = max(0.0, carga.x_ini)
    x_fim = L if carga.x_fim is None else min(L, carga.x_fim)
    return x_ini, x_fim


def _reacoes(L: float, distribuidas: list, pontuais: list) -> tuple:
    # Reacoes RA (apoio esquerdo) e RB (apoio direito) por equilibrio.
    # Sum M_B = 0 -> RA*L = Sum( F_i * (L - x_i) ).
    momento_B = 0.0
    carga_total = 0.0
    for c in distribuidas:
        x_ini, x_fim = _trecho(c, L)
        comp = x_fim - x_ini
        if comp <= 0:
            continue
        F = c.q * comp
        x_c = (x_ini + x_fim) / 2.0       # centroide do trecho
        momento_B += F * (L - x_c)
        carga_total += F
    for p in pontuais:
        momento_B += p.P * (L - p.a)
        carga_total += p.P
    RA = momento_B / L
    RB = carga_total - RA
    return RA, RB


def _cortante_em(x: float, RA: float, distribuidas: list,
                 pontuais: list, L: float) -> float:
    # V(x) = RA - resultante das cargas a esquerda de x.
    V = RA
    for c in distribuidas:
        x_ini, x_fim = _trecho(c, L)
        if x <= x_ini:
            continue
        comp = min(x, x_fim) - x_ini      # parte do trecho a esquerda de x
        if comp > 0:
            V -= c.q * comp
    for p in pontuais:
        if p.a < x:                       # pontual ja ultrapassada
            V -= p.P
    return V


def _integral_cumulativa(y: list, x: list) -> list:
    # Integral cumulativa por regra do trapezio. Retorna lista do mesmo
    # tamanho, comecando em 0.
    out = [0.0]
    for i in range(1, len(x)):
        dx = x[i] - x[i - 1]
        out.append(out[-1] + (y[i] + y[i - 1]) / 2.0 * dx)
    return out


def _linha_elastica(x: list, M: list, EI: float, L: float) -> list:
    # Resolve EI*y'' = M por dupla integracao numerica com y(0)=y(L)=0.
    # Retorna a flecha para baixo delta = -y.
    curvatura = [m / EI for m in M]           # y''
    theta_raw = _integral_cumulativa(curvatura, x)   # y' a menos de C1
    y_raw = _integral_cumulativa(theta_raw, x)       # y a menos de C1*x (C2=0)
    # y(L) = y_raw(L) + C1*L = 0 -> C1 = -y_raw(L)/L
    C1 = -y_raw[-1] / L
    return [-(y_raw[i] + C1 * x[i]) for i in range(len(x))]


def resolver_viga_biapoiada(L: float,
                            distribuidas: Optional[list] = None,
                            pontuais: Optional[list] = None,
                            EI: Optional[float] = None,
                            n: int = N_PONTOS_PADRAO) -> dict:
    # Resolve uma viga biapoiada de vao L [m].
    #   distribuidas : lista de CargaDistribuida [kN/m]
    #   pontuais     : lista de CargaPontual [kN]
    #   EI           : rigidez a flexao [kN.m2]. Se None, nao calcula flecha.
    #   n            : numero de pontos da malha.
    # Retorna dict com x, V, M, delta (ou None) e os valores extremos +
    # reacoes, no formato de 'diagramas' do ResultadoElemento.
    distribuidas = distribuidas or []
    pontuais = pontuais or []
    if L <= 0:
        raise ValueError("Vao L deve ser positivo.")
    if n < 3:
        raise ValueError("n deve ser >= 3.")

    RA, RB = _reacoes(L, distribuidas, pontuais)

    x = [L * i / (n - 1) for i in range(n)]
    V = [_cortante_em(xi, RA, distribuidas, pontuais, L) for xi in x]
    M = _integral_cumulativa(V, x)            # M(x) = integral de V, M(0)=0

    delta = None
    delta_max = None
    if EI is not None and EI > 0:
        delta = _linha_elastica(x, M, EI, L)
        delta_max = max(delta, key=abs)

    return {
        "x": x,
        "V": V,
        "M": M,
        "delta": delta,
        "RA_kN": round(RA, 4),
        "RB_kN": round(RB, 4),
        "M_max_kNm": max(M),
        "M_min_kNm": min(M),
        "V_max_kN": max(V, key=abs),
        "delta_max_m": delta_max,
    }
