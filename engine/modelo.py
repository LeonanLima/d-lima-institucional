from dataclasses import dataclass, field
from typing import Optional
from engine.materiais import Material

# Cobrimento nominal por CAA (cm): {CAA: (laje, viga_pilar)}
COBRIMENTO = {1: (2.0, 2.5), 2: (2.5, 3.0), 3: (3.5, 4.0), 4: (4.5, 5.0)}


@dataclass
class No:
    id: int
    x: float  # cm
    y: float  # cm
    z: float = 0.0  # cm


@dataclass
class Secao:
    bw: float  # cm
    h: float   # cm

    @property
    def area(self) -> float:
        return self.bw * self.h

    @property
    def inercia(self) -> float:
        return self.bw * self.h ** 3 / 12.0


@dataclass
class Elemento:
    id: str
    tipo: str          # fundacao | pilar | viga | laje
    no_i: No
    no_j: No
    secao: Secao
    cor: str = "#3b82f6"

    def comprimento(self) -> float:
        dx = self.no_j.x - self.no_i.x
        dy = self.no_j.y - self.no_i.y
        dz = self.no_j.z - self.no_i.z
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    def angulo(self) -> float:
        import math
        dx = self.no_j.x - self.no_i.x
        dy = self.no_j.y - self.no_i.y
        return math.atan2(dy, dx)

    def cobrimento(self, caa: int) -> float:
        laje_c, viga_pilar_c = COBRIMENTO[caa]
        return laje_c if self.tipo == 'laje' else viga_pilar_c


@dataclass
class Vinculo:
    no: int
    ux: bool = False
    uy: bool = False
    uz: bool = False
    rx: bool = False
    ry: bool = False
    rz: bool = False


@dataclass
class Carga:
    tipo: str                      # distribuida | concentrada | nodal
    valor: float = 0.0             # kN/cm (distribuida) ou kN (concentrada)
    direcao: str = "y"
    elemento: Optional[str] = None
    no: Optional[int] = None
    fx: float = 0.0
    fy: float = 0.0
    mz: float = 0.0


_PALETA = ["#3b82f6", "#22c55e", "#ef4444", "#f59e0b",
           "#8b5cf6", "#ec4899", "#14b8a6", "#a855f7"]


@dataclass
class Estrutura:
    material: Material
    caa: int
    nos: dict = field(default_factory=dict)        # id -> No
    elementos: list = field(default_factory=list)
    vinculos: list = field(default_factory=list)
    cargas: list = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict) -> "Estrutura":
        e = data["estrutura"]
        mat_data = e["material"]
        material = Material(
            fck=mat_data["fck"], fyk=mat_data["fyk"],
            agregado=mat_data.get("agregado", "basalto"))
        caa = mat_data.get("CAA", 2)

        nos = {}
        for n in e["nos"]:
            nos[n["id"]] = No(id=n["id"],
                              x=n["x"] * 100.0,           # m -> cm
                              y=n["y"] * 100.0,
                              z=n.get("z", 0.0) * 100.0)

        elementos = []
        for i, el in enumerate(e["elementos"]):
            sec = Secao(bw=el["secao"]["bw"], h=el["secao"]["h"])
            cor = el.get("cor", _PALETA[i % len(_PALETA)])
            elementos.append(Elemento(
                id=el["id"], tipo=el["tipo"],
                no_i=nos[el["no_i"]], no_j=nos[el["no_j"]],
                secao=sec, cor=cor))

        vinculos = [Vinculo(no=v["no"],
                            ux=v.get("ux", False), uy=v.get("uy", False),
                            uz=v.get("uz", False), rx=v.get("rx", False),
                            ry=v.get("ry", False), rz=v.get("rz", False))
                    for v in e.get("vinculos", [])]

        cargas = []
        for c in e.get("cargas", []):
            valor = c.get("valor", 0.0)
            if c["tipo"] == "distribuida":
                valor = valor / 100.0   # kN/m -> kN/cm
            cargas.append(Carga(
                tipo=c["tipo"], valor=valor,
                direcao=c.get("direcao", "y"),
                elemento=c.get("elemento"), no=c.get("no"),
                fx=c.get("fx", 0.0), fy=c.get("fy", 0.0),
                mz=c.get("mz", 0.0)))

        return cls(material=material, caa=caa, nos=nos,
                   elementos=elementos, vinculos=vinculos, cargas=cargas)
