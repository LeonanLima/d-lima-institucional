"""Estruturas de resultado unificadas (fonte unica para UI, CLI e memorial).

Motivacao (refactor R4/A1): hoje cada pagina monta seus proprios dicts e textos.
Aqui centralizamos DOIS objetos que todo dimensionamento deve devolver:

  Verificacao        - um item do painel "valor calculado x LIMITE normativo x status".
  ResultadoElemento  - o pacote completo (esforcos + verificacoes + diagramas + armadura).

A direcao da comparacao varia por verificacao, entao ela e explicita no objeto:
  OP_MAX ("<=")  valor <= limite -> OK   (flecha<=wadm, x/d<=0,45, wk<=wlim, Vsd<=VRd2, lambda<=lambda1)
  OP_MIN (">=")  valor >= limite -> OK   (FST>=1,5, FSD>=1,5)

status/folga/utilizacao sao DERIVADOS do operador - nao existe string de status solta
para dessincronizar (fonte unica). Ref. requisitos NBR 6118:2023 sec.13/15/17.
"""
from __future__ import annotations

from dataclasses import dataclass, field

OP_MAX = "<="   # valor <= limite -> OK
OP_MIN = ">="   # valor >= limite -> OK

# Tolerancia relativa para nao reprovar no limite exato por erro de ponto flutuante
# (ex.: x/d = 0,450000001 vs 0,45 deve contar como OK).
_TOL = 1e-6


@dataclass(frozen=True)
class Verificacao:
    """Um item do painel de verificacoes (valor calculado x limite normativo).

    nome      : descricao curta (ex.: "Flecha (ELS)", "Ductilidade x/d").
    valor     : valor calculado.
    limite    : limite normativo a comparar.
    unidade   : unidade do par valor/limite (ex.: "mm", "cm2/m", "").
    operador  : OP_MAX (valor<=limite OK) ou OP_MIN (valor>=limite OK).
    ref       : referencia da norma/secao.
    """
    nome: str
    valor: float
    limite: float
    unidade: str = ""
    operador: str = OP_MAX
    ref: str = ""

    @property
    def passou(self) -> bool:
        tol = _TOL * max(1.0, abs(self.limite))
        if self.operador == OP_MIN:
            return self.valor >= self.limite - tol
        return self.valor <= self.limite + tol

    @property
    def status(self) -> str:
        return "OK" if self.passou else "NAO OK"

    @property
    def folga(self) -> float:
        """Margem disponivel na unidade do item (positiva = passa com sobra)."""
        if self.operador == OP_MIN:
            return round(self.valor - self.limite, 4)
        return round(self.limite - self.valor, 4)

    @property
    def utilizacao(self) -> float:
        """Aproveitamento da capacidade (>1,0 reprova). Adimensional."""
        if self.operador == OP_MIN:
            return round(self.limite / self.valor, 4) if self.valor else float("inf")
        return round(self.valor / self.limite, 4) if self.limite else float("inf")


def verif_max(nome: str, valor: float, limite: float,
              unidade: str = "", ref: str = "") -> Verificacao:
    """Verificacao do tipo 'valor <= limite e OK' (a mais comum)."""
    return Verificacao(nome, valor, limite, unidade, OP_MAX, ref)


def verif_min(nome: str, valor: float, limite: float,
              unidade: str = "", ref: str = "") -> Verificacao:
    """Verificacao do tipo 'valor >= limite e OK' (estabilidade: FST, FSD)."""
    return Verificacao(nome, valor, limite, unidade, OP_MIN, ref)


@dataclass
class ResultadoElemento:
    """Pacote que um dimensionamento devolve - consumido por UI, CLI e memorial.

    elemento     : nome do elemento ("laje", "viga", "pilar", ...).
    esforcos     : dict de esforcos de calculo (M, V, N, reacoes, ...).
    verificacoes : lista de Verificacao (o painel valor x limite x status).
    diagramas    : dict para os graficos (ex.: {"x": [...], "M": [...], "V": [...]}).
    armadura     : dict do detalhamento (As, barras, estribos, ...).
    meta         : dict livre (geometria, materiais, referencias).
    """
    elemento: str
    esforcos: dict = field(default_factory=dict)
    verificacoes: list = field(default_factory=list)
    diagramas: dict = field(default_factory=dict)
    armadura: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    @property
    def tudo_ok(self) -> bool:
        """True se todas as verificacoes passaram."""
        return all(v.passou for v in self.verificacoes)

    @property
    def reprovadas(self) -> list:
        """Verificacoes que NAO passaram (para destacar em vermelho na UI)."""
        return [v for v in self.verificacoes if not v.passou]

    def add(self, v: Verificacao) -> "ResultadoElemento":
        """Acrescenta uma verificacao e devolve self (encadeavel)."""
        self.verificacoes.append(v)
        return self
