from dataclasses import dataclass, field

ALPHA_E = {'basalto': 1.2, 'diabasio': 1.2, 'granito': 1.0,
           'gnaisse': 1.0, 'calcario': 0.9, 'arenito': 0.7}


@dataclass
class Material:
    """Propriedades do concreto e aco em kN/cm2 (NBR 6118:2023).

    fck, fyk em MPa. agregado define alpha_E para o modulo de elasticidade.
    """
    fck: float = 25.0
    fyk: float = 500.0
    agregado: str = 'basalto'

    Ecs: float = field(init=False)
    Eci: float = field(init=False)
    fcd: float = field(init=False)
    fyd: float = field(init=False)
    fctm: float = field(init=False)
    fctd: float = field(init=False)

    def __post_init__(self):
        aE = ALPHA_E.get(self.agregado.lower(), 1.0)
        eci_mpa = aE * 5600 * self.fck ** 0.5          # MPa
        ai = min(0.8 + 0.2 * (self.fck / 80), 1.0)
        ecs_mpa = ai * eci_mpa                          # MPa
        self.Eci = eci_mpa / 10.0                       # kN/cm2
        self.Ecs = ecs_mpa / 10.0                       # kN/cm2
        self.fcd = self.fck / 1.4 / 10.0                # kN/cm2
        self.fyd = self.fyk / 1.15 / 10.0               # kN/cm2
        self.fctm = 0.3 * self.fck ** (2 / 3)           # MPa
        self.fctd = (0.15 * self.fck ** (2 / 3)) / 10.0 # kN/cm2
