# detalhamento/armaduras.py - Detalhamento de armaduras estilo TQS
#
# Converte a area de aco calculada (As) em BARRAS NOMEADAS (N1, N2...) com
# bitola comercial, quantidade ou espacamento, area provida e comprimento -
# a linguagem que o ferreiro/pedreiro entende.
#
# Dois modos:
#   - CONCENTRADA (viga, pilar): As total [cm2] -> n barras de uma bitola.
#   - DISTRIBUIDA (laje, parede): As por metro [cm2/m] -> bitola @ espacamento.
#
# REFERENCIAS:
#   NBR 6118:2023, sec.18 (detalhamento) e NBR 7480:2022 (bitolas comerciais).
from dataclasses import dataclass
from typing import Optional
import math

# Bitolas comerciais [mm] e area da secao [cm2] - NBR 7480:2022
AREA_BARRA = {
    5.0: 0.196, 6.3: 0.312, 8.0: 0.503, 10.0: 0.785, 12.5: 1.227,
    16.0: 2.011, 20.0: 3.142, 25.0: 4.909, 32.0: 8.042,
}
BITOLAS = sorted(AREA_BARRA)

# Espacamento maximo padrao da armadura principal [cm] - NBR 6118 sec.20.1
S_MAX_CM = 20.0
# Espacamento minimo construtivo entre barras [cm]
S_MIN_CM = 7.5


def area_barra(phi_mm: float) -> float:
    # Area da secao de uma barra de diametro phi_mm [cm2].
    if phi_mm not in AREA_BARRA:
        raise ValueError(f"Bitola {phi_mm} mm fora da NBR 7480.")
    return AREA_BARRA[phi_mm]


@dataclass(frozen=True)
class Barra:
    # Uma posicao de armadura detalhada.
    #   nome         : etiqueta sequencial (N1, N2...)
    #   posicao      : descricao (ex.: "armadura positiva", "estribo")
    #   phi_mm       : bitola comercial
    #   quantidade   : numero de barras
    #   As_prov_cm2  : area provida (por metro, se distribuida)
    #   espacamento_cm: espacamento (None p/ armadura concentrada)
    #   comprimento_cm: comprimento de corte (None se nao informado)
    nome: str
    posicao: str
    phi_mm: float
    quantidade: int
    As_prov_cm2: float
    espacamento_cm: Optional[float] = None
    comprimento_cm: Optional[float] = None

    def descricao(self) -> str:
        # Linha curta no formato de planta (ex.: "N2 8 Ø10.0 c/15 - 320cm").
        if self.espacamento_cm is not None:
            corpo = f"Ø{self.phi_mm:g} c/{self.espacamento_cm:g}"
        else:
            corpo = f"Ø{self.phi_mm:g}"
        comp = f" - {self.comprimento_cm:g}cm" if self.comprimento_cm else ""
        return f"{self.nome}  {self.quantidade} {corpo}{comp}"


def _proximo_nome(seq: int) -> str:
    return f"N{seq}"


def detalhar_por_quantidade(As_cm2: float, nome_seq: int = 1,
                            posicao: str = "armadura",
                            phi_mm: Optional[float] = None,
                            n_min: int = 2,
                            comprimento_cm: Optional[float] = None) -> Barra:
    # Armadura CONCENTRADA (viga/pilar): As total [cm2] -> n barras.
    # Se phi_mm e dado, fixa a bitola; senao escolhe a menor que precise de
    # no maximo ~8 barras (evita bitola muito fina com barra demais).
    if As_cm2 <= 0:
        raise ValueError("As deve ser positivo.")
    candidatas = [phi_mm] if phi_mm else BITOLAS
    escolha = None
    for phi in candidatas:
        a = area_barra(phi)
        n = max(n_min, math.ceil(As_cm2 / a))
        if phi_mm or n <= 8:
            escolha = (phi, n, round(n * a, 2))
            break
    if escolha is None:                       # As muito grande p/ <=8 barras
        phi = BITOLAS[-1]
        n = max(n_min, math.ceil(As_cm2 / area_barra(phi)))
        escolha = (phi, n, round(n * area_barra(phi), 2))
    phi, n, As_prov = escolha
    return Barra(_proximo_nome(nome_seq), posicao, phi, n, As_prov,
                 None, comprimento_cm)


def detalhar_por_espacamento(As_cm2_m: float, largura_cm: float = 100.0,
                             nome_seq: int = 1, posicao: str = "armadura",
                             phi_mm: Optional[float] = None,
                             s_max_cm: float = S_MAX_CM,
                             comprimento_cm: Optional[float] = None) -> Barra:
    # Armadura DISTRIBUIDA (laje/parede): As por metro [cm2/m] -> bitola @ s.
    # As_prov por metro = area_barra(phi) * 100 / s. Procura a menor bitola
    # cujo espacamento necessario fique entre S_MIN e s_max (passo de 0,5 cm).
    if As_cm2_m <= 0:
        raise ValueError("As/m deve ser positivo.")
    candidatas = [phi_mm] if phi_mm else BITOLAS
    escolha = None
    for phi in candidatas:
        a = area_barra(phi)
        s_nec = a * 100.0 / As_cm2_m              # espacamento que iguala As
        s = math.floor(min(s_nec, s_max_cm) / 0.5) * 0.5   # arredonda p/ baixo
        if s < S_MIN_CM:
            continue                               # bitola grossa demais
        As_prov = round(a * 100.0 / s, 2)
        n = math.floor(largura_cm / s) + 1
        escolha = (phi, s, As_prov, n)
        break
    if escolha is None:                            # nenhuma serve no s_min
        phi = candidatas[-1] if phi_mm else BITOLAS[-1]
        a = area_barra(phi)
        s = S_MIN_CM
        As_prov = round(a * 100.0 / s, 2)
        n = math.floor(largura_cm / s) + 1
        escolha = (phi, s, As_prov, n)
    phi, s, As_prov, n = escolha
    return Barra(_proximo_nome(nome_seq), posicao, phi, n, As_prov,
                 s, comprimento_cm)


def tabela_espacamento(As_cm2_m: float, largura_cm: float = 100.0,
                       s_max_cm: float = S_MAX_CM) -> list:
    """Tabela de opcoes de armadura DISTRIBUIDA (laje/parede) p/ As exigido [cm2/m].

    Para cada bitola comercial cujo espacamento pratico fique entre S_MIN e
    s_max, devolve {phi_mm, s_cm, As_prov_cm2m, n, recomendada}. A bitola
    recomendada e a mais fina que atende (barras finas, espacamento mais justo);
    o projetista escolhe na lista a que melhor se enquadra na obra.

    As linhas vao da bitola mais fina viavel (espacamento mais justo) ate a
    primeira cujo espacamento bate no maximo (s_max); bitolas mais grossas so
    repetiriam o espacamento maximo e sao omitidas.
    """
    if As_cm2_m <= 0:
        raise ValueError("As/m deve ser positivo.")
    linhas = []
    for phi in BITOLAS:
        a = area_barra(phi)
        s_nec = a * 100.0 / As_cm2_m                       # s que iguala o As
        s = math.floor(min(s_nec, s_max_cm) / 0.5) * 0.5   # arredonda p/ baixo
        if s < S_MIN_CM:
            continue                                        # bitola fina demais
        As_prov = round(a * 100.0 / s, 2)
        n = math.floor(largura_cm / s) + 1
        linhas.append({"phi_mm": phi, "s_cm": s,
                       "As_prov_cm2m": As_prov, "n": n})
        if s_nec >= s_max_cm:
            break                                           # ja bateu no s_max
    if linhas:
        linhas[0]["recomendada"] = True
    return linhas


# Telas soldadas nervuradas (malha POP) - NBR 7481:2020, serie Q (malha quadrada).
# (designacao, As [cm2/m em cada direcao], espacamento [cm], bitola do fio [mm]).
# O numero da designacao ~ As em mm2/m (Q-196 -> 1,96 cm2/m).
TELAS_Q = [
    ("Q-61", 0.61, 15, 3.4), ("Q-75", 0.75, 15, 3.8), ("Q-92", 0.92, 15, 4.2),
    ("Q-113", 1.13, 10, 3.8), ("Q-138", 1.38, 10, 4.2), ("Q-159", 1.59, 10, 4.5),
    ("Q-196", 1.96, 10, 5.0), ("Q-246", 2.46, 10, 5.6), ("Q-283", 2.83, 10, 6.0),
    ("Q-335", 3.35, 10, 6.5), ("Q-396", 3.96, 10, 7.1), ("Q-503", 5.03, 10, 8.0),
    ("Q-636", 6.36, 10, 9.0), ("Q-785", 7.85, 10, 10.0),
]


def tabela_telas(As_cm2_m: float, n_opcoes: int = 3) -> list:
    """Opcoes de tela soldada (malha POP, serie Q) que atendem o As [cm2/m].

    Alternativa industrializada as barras avulsas em lajes. Devolve as ate
    n_opcoes telas mais leves cujo As cobre o exigido, marcando a primeira
    (mais leve) como recomendada. Lista vazia se nenhuma tela alcanca o As
    (nesse caso usar barras avulsas).
    """
    if As_cm2_m <= 0:
        raise ValueError("As/m deve ser positivo.")
    cobrem = [t for t in TELAS_Q if t[1] >= As_cm2_m - 1e-9]
    linhas = []
    for i, (desig, As, esp, phi) in enumerate(cobrem[:n_opcoes]):
        linhas.append({"tela": desig, "As_cm2m": As, "malha_cm": esp,
                       "phi_mm": phi, "recomendada": i == 0})
    return linhas


def texto_para_obra(barras: list) -> str:
    # Lista de barras formatada para a planta de ferragem (uma por linha).
    return "\n".join(b.descricao() for b in barras)
