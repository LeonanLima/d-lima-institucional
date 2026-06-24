"""Interpolacao linear em tabelas de coeficientes (Fatia 4/A4).

Motor generico para "tabela como dado": recebe uma tabela ordenavel pela 1a
coluna (a chave, ex.: ly/lx) e devolve os demais valores interpolados. Fora do
intervalo, CLAMPA nos extremos (nunca extrapola coeficiente estrutural).

Generaliza o _interp_tab que estava embutido em relatorio/passo_a_passo.py, para
que Carini/Bares/Czerny e a tabela de reservatorio passem a viver como DADO e
compartilhem um unico interpolador testado.
"""
from __future__ import annotations

from bisect import bisect_left


def interp_linear(tabela, chave, nomes=None):
    """Interpolacao linear 1-D numa tabela ordenada pela 1a coluna.

    tabela : sequencia de linhas (chave, v1, v2, ...). Nao precisa vir ordenada.
    chave  : valor da 1a coluna a procurar (ex.: razao ly/lx).
    nomes  : se dado, zipa os valores num dict {nome: valor}.
    Retorna lista de valores interpolados (ou dict se 'nomes' for passado).
    Fora dos limites: clampa no extremo correspondente (sem extrapolar).
    """
    if not tabela:
        raise ValueError("tabela vazia")
    linhas = sorted(tabela, key=lambda r: r[0])
    xs = [r[0] for r in linhas]

    if chave <= xs[0]:
        vals = list(linhas[0][1:])
    elif chave >= xs[-1]:
        vals = list(linhas[-1][1:])
    else:
        i = bisect_left(xs, chave)
        x0, x1 = xs[i - 1], xs[i]
        r0, r1 = linhas[i - 1], linhas[i]
        f = (chave - x0) / (x1 - x0)
        vals = [a + f * (b - a) for a, b in zip(r0[1:], r1[1:])]

    if nomes is not None:
        return dict(zip(nomes, vals))
    return vals
