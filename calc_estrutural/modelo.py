"""
modelo.py - Estruturas de dados do programa DLIMA Estrutural
Representa nos, barras, secoes, lajes e paredes para analise estrutural
"""
from dataclasses import dataclass, field
from typing import Optional, List
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
class No:
    """
    No do portico espacial - 6 graus de liberdade (DOF)
    DOF: [ux, uy, uz, theta_x, theta_y, theta_z]
    Coordenadas em metros, restricoes boolean (True = fixo)
    """
    id: int
    x: float = 0.0   # [m]
    y: float = 0.0   # [m]
    z: float = 0.0   # [m]
    # restricoes: True = deslocamento/rotacao impedido
    restricoes: List[bool] = field(default_factory=lambda: [False]*6)
    # cargas nodais: [Fx, Fy, Fz, Mx, My, Mz] em [kN, kNm]
    cargas: List[float] = field(default_factory=lambda: [0.0]*6)

    def apoio_engastado(self):
        self.restricoes = [True]*6

    def apoio_articulado(self):
        self.restricoes = [True, True, True, False, False, False]

    def apoio_deslizante_x(self):
        self.restricoes = [False, True, True, False, False, False]

    def aplicar_carga(self, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0):
        self.cargas = [Fx, Fy, Fz, Mx, My, Mz]


@dataclass
class Barra:
    """
    Barra de portico espacial - conecta dois nos
    Tipo: "pilar", "viga_x", "viga_y", "diagonal"
    Cargas distribuidas: [(tipo, valor, posicao)] - em desenvolvimento
    """
    id: int
    no_i: No
    no_j: No
    secao: Secao
    tipo: str = "viga"
    # cargas distribuidas: [(intensidade_kNm, ax_ini, ax_fim)] no eixo local
    q_distribuida: List[tuple] = field(default_factory=list)

    @property
    def L(self):
        dx = self.no_j.x - self.no_i.x
        dy = self.no_j.y - self.no_i.y
        dz = self.no_j.z - self.no_i.z
        return math.sqrt(dx**2 + dy**2 + dz**2)

    @property
    def vetor_eixo(self):
        L = self.L
        dx = (self.no_j.x - self.no_i.x) / L
        dy = (self.no_j.y - self.no_i.y) / L
        dz = (self.no_j.z - self.no_i.z) / L
        return (dx, dy, dz)


@dataclass
class Estrutura:
    """Estrutura completa do portico espacial"""
    nome: str = "Estrutura"
    nos: List[No] = field(default_factory=list)
    barras: List[Barra] = field(default_factory=list)

    def adicionar_no(self, no: No):
        self.nos.append(no)
        return no

    def adicionar_barra(self, barra: Barra):
        self.barras.append(barra)
        return barra

    def no_por_id(self, id: int) -> Optional[No]:
        return next((n for n in self.nos if n.id == id), None)

    @property
    def n_dof(self): return len(self.nos) * 6


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
