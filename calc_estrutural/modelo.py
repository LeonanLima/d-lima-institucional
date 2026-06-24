"""
modelo.py - Estruturas de dados do programa DLIMA Estrutural
Representa secoes, lajes e paredes para dimensionamento de elementos.
"""
from dataclasses import dataclass, field
import math


@dataclass
class Material:
    """Propriedades do concreto e aco - NBR 6118:2023"""
    fck: float = 25.0    # [MPa] resistencia caracteristica do concreto
    tipo_aco: str = "CA-50"
    fyk: float = 500.0   # [MPa] escoamento do aco
    alphaE: float = 1.0  # coef. do agregado (basalto=1.2, granito=1.0, calc=0.9)

    @property
    def fcd(self): return round(self.fck / 1.4, 2)

    @property
    def fyd(self): return round(self.fyk / 1.15, 2)

    @property
    def Es(self): return 210_000.0  # MPa

    @property
    def Eci(self): return round(self.alphaE * 5600 * math.sqrt(self.fck), 0)

    @property
    def Ecs(self):
        ai = min(0.8 + 0.2 * self.fck / 80, 1.0)
        return round(ai * self.Eci, 0)

    @property
    def G(self): return round(self.Ecs / 2.4, 0)

    @property
    def fctm(self): return round(0.3 * self.fck ** (2/3), 3)


@dataclass
class Secao:
    """Secao transversal retangular de uma barra - NBR 6118:2023"""
    b: float      # [cm] largura (ou menor dimensao)
    h: float      # [cm] altura (ou maior dimensao)
    material: Material = field(default_factory=Material)
    caa: str = "II"   # classe de agressividade ambiental

    @property
    def A(self): return self.b * self.h

    @property
    def Iy(self): return self.h * self.b**3 / 12

    @property
    def Iz(self): return self.b * self.h**3 / 12

    @property
    def J(self):
        """Constante de torcao para secao retangular (aprox. Saint-Venant)"""
        a, b = max(self.b, self.h), min(self.b, self.h)
        return a * b**3 * (1/3 - 0.21*(b/a)*(1 - (b/a)**4/12))

    @property
    def cobrimento(self):
        tab = {"I": {"viga": 2.0, "pilar": 2.5, "laje": 1.5},
               "II": {"viga": 2.5, "pilar": 3.0, "laje": 2.0},
               "III": {"viga": 4.0, "pilar": 4.0, "laje": 3.5},
               "IV": {"viga": 5.0, "pilar": 5.0, "laje": 4.5}}
        return tab.get(self.caa, tab["II"])

    @property
    def E(self): return self.material.Ecs

    @property
    def G(self): return self.material.G


@dataclass
class Laje:
    """Laje macica ou trelicada - dados de projeto"""
    id: str
    lx: float          # [m] menor vao
    ly: float          # [m] maior vao
    h: float           # [m] espessura total
    caso: int = 1      # caso de vinculacao (1-10)
    gk: float = 0.0   # [kN/m2] cargas permanentes (sem PP)
    qk: float = 1.5   # [kN/m2] carga variavel
    uso: str = "residencial"
    material: Material = field(default_factory=Material)
    tipo: str = "macica"   # "macica" | "trelicada"
    caa: str = "II"

    @property
    def relacao(self): return round(self.ly / self.lx, 3)

    @property
    def eh_bidirecional(self): return self.relacao <= 2.0

    @property
    def pp(self): return round(25.0 * self.h, 2)  # [kN/m2]

    @property
    def fd(self): return round(1.4 * (self.gk + self.pp) + 1.4 * self.qk, 2)

    @property
    def fd_ser(self):
        psi2 = {"residencial": 0.3, "comercial": 0.4, "garagem": 0.6}.get(self.uso, 0.3)
        return round(self.gk + self.pp + psi2 * self.qk, 2)


@dataclass
class Parede:
    """
    Parede/laje de reservatorio, muro de arrimo ou piscina
    Usada para calcular elementos especiais submetidos a pressao hidraulica ou de terra
    """
    id: str
    tipo: str        # "reservatorio" | "muro_arrimo" | "piscina"
    lx: float        # [m] menor vao / largura
    ly: float        # [m] maior vao / altura
    h: float         # [m] espessura
    vinculacao: str = "EAAE"  # E=engaste, A=apoio, L=livre (sentido horario a partir do fundo)
    material: Material = field(default_factory=Material)
    caa: str = "IV"  # estruturas hidraulicas = CAA IV por norma

    @property
    def pp(self): return round(25.0 * self.h, 2)
