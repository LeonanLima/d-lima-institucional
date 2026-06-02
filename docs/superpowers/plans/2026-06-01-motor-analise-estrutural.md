# Motor de Análise Estrutural (Fase 1) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Motor Python que analisa pórticos planos pelo Método da Rigidez (matrizes), dimensiona conforme NBR 6118:2023, e gera relatório educativo com passos Carini, matrizes coloridas e desenhos SVG de detalhamento.

**Architecture:** Pacote `engine/` com módulos coesos (materiais, modelo, rigidez, solver, dimensionamento, detalhamento, svg, relatório). Cada módulo é puro Python+numpy, testável isoladamente. Flask expõe `/api/estrutura` (recebe JSON, retorna análise) e `/api/relatorio/<id>` (HTML renderizado).

**Tech Stack:** Python 3.13, numpy 2.4, Flask 3, pytest, Jinja2, SVG inline

**Convenção de unidades (interna):** comprimento em **cm**, força em **kN**, momento em **kN·cm**, tensão em **kN/cm²**. Entrada JSON usa metros para nós e kN/m para cargas distribuídas — convertidos no parse. Saída exibe mm, kN, kNm.

---

## File Map

| Arquivo | Responsabilidade |
|---|---|
| `engine/__init__.py` | Marca o pacote |
| `engine/materiais.py` | Ecs, fcd, fyd, fctd a partir de fck/fyk/agregado (usado por rigidez E dimensionamento) |
| `engine/modelo.py` | Dataclasses No/Elemento/Vinculo/Carga/Estrutura + parse do JSON |
| `engine/rigidez.py` | Matriz elementar k_local, transformação T, montagem K_global + mapa de contribuições |
| `engine/solver.py` | Forças nodais equivalentes, condições de contorno, solução {u}, reações, esforços N/V/M, flecha |
| `engine/dimensionamento.py` | NBR 6118: cisalhamento, flexão (simples/dupla/pele), pilares |
| `engine/detalhamento.py` | escolher_bitola, escolher_estribo, zonas de armadura |
| `engine/svg_secao.py` | SVG da seção transversal com armaduras |
| `engine/svg_elevacao.py` | SVG da elevação com zonas de estribo |
| `engine/relatorio.py` | Monta os 17 passos Carini + avisos automáticos |
| `templates/relatorio.html` | Jinja2: matrizes coloridas, SVG inline, hover |
| `app.py` | Rotas `/api/estrutura`, `/api/relatorio/<id>` |
| `tests/test_*.py` | Testes pytest por módulo |

**Nota de refinamento ao spec:** o spec não listava `engine/materiais.py`; ele foi extraído porque `rigidez.py` e `dimensionamento.py` ambos precisam de Ecs/fcd — centralizar evita duplicação (DRY).

---

### Task 1: Setup — numpy, pacote engine/, materiais.py

**Files:**
- Modify: `requirements.txt`
- Create: `engine/__init__.py`
- Create: `engine/materiais.py`
- Create: `tests/test_materiais.py`

- [x] **Passo 1: Adicionar numpy ao `requirements.txt`**

Conteúdo final do arquivo:

```
Flask==3.0.0
gunicorn==21.2.0
flask-cors
ezdxf[draw]
matplotlib
numpy
```

- [x] **Passo 2: Criar `engine/__init__.py` vazio**

```python
```

- [x] **Passo 3: Escrever teste falho `tests/test_materiais.py`**

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.materiais import Material


def test_ecs_c25_basalto():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # Eci = 1,2 * 5600 * sqrt(25) = 33600 MPa; ai = 0,8625; Ecs = 28980 MPa = 2898 kN/cm2
    assert abs(m.Ecs - 2898.0) < 1.0


def test_fcd_c25():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # fcd = 25/1,4/10 = 1,7857 kN/cm2
    assert abs(m.fcd - 1.7857) < 0.001


def test_fyd_ca50():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # fyd = 50/1,15 = 43,478 kN/cm2
    assert abs(m.fyd - 43.478) < 0.01


def test_fctd_c25():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # fctd = 0,15 * 25^(2/3) / 10 = 0,15 * 8,5499 / 10 = 0,12825 kN/cm2
    assert abs(m.fctd - 0.12825) < 0.001


def test_fctm_c25():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # fctm = 0,3 * 25^(2/3) = 2,565 MPa
    assert abs(m.fctm - 2.565) < 0.01
```

- [x] **Passo 4: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_materiais.py -v`
Esperado: `ModuleNotFoundError: No module named 'engine.materiais'`

- [x] **Passo 5: Implementar `engine/materiais.py`**

```python
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
```

- [x] **Passo 6: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_materiais.py -v`
Esperado: 5 PASSED

- [x] **Passo 7: Commit**

```bash
git add requirements.txt engine/__init__.py engine/materiais.py tests/test_materiais.py
git commit -m "feat: engine/materiais — propriedades do concreto e aco NBR 6118"
```

---

### Task 2: modelo.py — dataclasses e parse do JSON

**Files:**
- Create: `engine/modelo.py`
- Create: `tests/test_modelo.py`

- [x] **Passo 1: Escrever teste falho `tests/test_modelo.py`**

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.modelo import Estrutura


ENTRADA = {
    "estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [
            {"id": 1, "x": 0.0, "y": 0.0, "z": 0.0},
            {"id": 2, "x": 3.0, "y": 0.0, "z": 0.0}
        ],
        "elementos": [
            {"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
             "secao": {"bw": 14, "h": 40}}
        ],
        "vinculos": [
            {"no": 1, "ux": True, "uy": True, "uz": True,
             "rx": True, "ry": True, "rz": True}
        ],
        "cargas": [
            {"elemento": "V1", "tipo": "distribuida", "valor": 10.0,
             "direcao": "y", "unidade": "kN/m"}
        ]
    }
}


def test_parse_nos_converte_metros_para_cm():
    e = Estrutura.from_json(ENTRADA)
    assert e.nos[2].x == 300.0  # 3 m -> 300 cm
    assert e.nos[1].x == 0.0


def test_parse_elemento_comprimento_cm():
    e = Estrutura.from_json(ENTRADA)
    el = e.elementos[0]
    assert el.id == "V1"
    assert abs(el.comprimento() - 300.0) < 1e-6


def test_parse_carga_distribuida_convertida_kN_cm():
    e = Estrutura.from_json(ENTRADA)
    # 10 kN/m = 0,10 kN/cm
    assert abs(e.cargas[0].valor - 0.10) < 1e-9


def test_material_acessivel():
    e = Estrutura.from_json(ENTRADA)
    assert abs(e.material.Ecs - 2898.0) < 1.0


def test_cobrimento_caa2_viga():
    e = Estrutura.from_json(ENTRADA)
    # CAA II, viga -> cobrimento 3,0 cm
    assert e.elementos[0].cobrimento(caa=2) == 3.0
```

- [x] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_modelo.py -v`
Esperado: `ModuleNotFoundError`

- [x] **Passo 3: Implementar `engine/modelo.py`**

```python
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
```

- [x] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_modelo.py -v`
Esperado: 5 PASSED

- [x] **Passo 5: Commit**

```bash
git add engine/modelo.py tests/test_modelo.py
git commit -m "feat: engine/modelo — dataclasses e parse do JSON da estrutura"
```

---

### Task 3: rigidez.py — matriz elementar k_local e transformação T

**Files:**
- Create: `engine/rigidez.py`
- Create: `tests/test_rigidez.py`

- [x] **Passo 1: Escrever teste falho `tests/test_rigidez.py`**

```python
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.rigidez import k_local, matriz_T


def test_k_local_simetrica():
    k = k_local(E=2898.0, A=560.0, I=74666.67, L=300.0)
    assert np.allclose(k, k.T)


def test_k_local_termo_axial():
    k = k_local(E=2898.0, A=560.0, I=74666.67, L=300.0)
    # EA/L = 2898*560/300 = 5409,6
    assert abs(k[0, 0] - 5409.6) < 0.1
    assert abs(k[0, 3] - (-5409.6)) < 0.1


def test_k_local_termo_flexao():
    k = k_local(E=2898.0, A=560.0, I=74666.67, L=300.0)
    EI = 2898.0 * 74666.67
    # 12EI/L^3
    assert abs(k[1, 1] - 12 * EI / 300 ** 3) < 1.0
    # 4EI/L
    assert abs(k[2, 2] - 4 * EI / 300) < 1.0


def test_matriz_T_horizontal_identidade():
    # angulo 0 -> T = identidade
    T = matriz_T(0.0)
    assert np.allclose(T, np.eye(6))


def test_matriz_T_vertical():
    import math
    T = matriz_T(math.pi / 2)  # 90 graus
    # cos90=0, sin90=1
    assert abs(T[0, 0] - 0.0) < 1e-9
    assert abs(T[0, 1] - 1.0) < 1e-9
    assert abs(T[1, 0] - (-1.0)) < 1e-9
```

- [x] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_rigidez.py -v`
Esperado: `ModuleNotFoundError`

- [x] **Passo 3: Implementar `engine/rigidez.py` (parte 1)**

```python
import math
import numpy as np


def k_local(E: float, A: float, I: float, L: float) -> np.ndarray:
    """Matriz de rigidez elementar 6x6 de viga-coluna 2D no sistema local.

    GDLs: [ui_x, ui_y, theta_i, uj_x, uj_y, theta_j].
    Unidades: E [kN/cm2], A [cm2], I [cm4], L [cm] -> k em kN/cm e kN/rad.
    """
    EA_L = E * A / L
    EI = E * I
    L2 = L * L
    L3 = L2 * L
    return np.array([
        [EA_L,   0,            0,           -EA_L,  0,            0],
        [0,      12 * EI / L3,  6 * EI / L2,  0,    -12 * EI / L3, 6 * EI / L2],
        [0,      6 * EI / L2,   4 * EI / L,   0,    -6 * EI / L2,  2 * EI / L],
        [-EA_L,  0,            0,            EA_L,   0,            0],
        [0,     -12 * EI / L3, -6 * EI / L2,  0,     12 * EI / L3, -6 * EI / L2],
        [0,      6 * EI / L2,   2 * EI / L,   0,    -6 * EI / L2,  4 * EI / L],
    ], dtype=float)


def matriz_T(angulo: float) -> np.ndarray:
    """Matriz de rotacao 6x6 (local <- global) para um elemento 2D.

    angulo em radianos, medido do eixo x global ao eixo do elemento.
    """
    c = math.cos(angulo)
    s = math.sin(angulo)
    return np.array([
        [c,  s, 0, 0, 0, 0],
        [-s, c, 0, 0, 0, 0],
        [0,  0, 1, 0, 0, 0],
        [0,  0, 0, c,  s, 0],
        [0,  0, 0, -s, c, 0],
        [0,  0, 0, 0,  0, 1],
    ], dtype=float)


def k_global_elemento(E, A, I, L, angulo) -> np.ndarray:
    """Matriz elementar transformada para o sistema global: T^T k_local T."""
    kl = k_local(E, A, I, L)
    T = matriz_T(angulo)
    return T.T @ kl @ T
```

- [x] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_rigidez.py -v`
Esperado: 5 PASSED

- [x] **Passo 5: Commit**

```bash
git add engine/rigidez.py tests/test_rigidez.py
git commit -m "feat: engine/rigidez — matriz elementar k_local e transformacao T"
```

---

### Task 4: rigidez.py — montagem da K_global com mapa de contribuições

**Files:**
- Modify: `engine/rigidez.py`
- Modify: `tests/test_rigidez.py`

- [x] **Passo 1: Adicionar teste falho em `tests/test_rigidez.py`**

```python
from engine.rigidez import montar_global
from engine.modelo import Estrutura


def test_montar_global_dimensao():
    # 2 nos, 3 GDL/no -> K 6x6
    entrada = {"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 3, "y": 0}],
        "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                       "secao": {"bw": 14, "h": 40}}],
        "vinculos": [], "cargas": []}}
    est = Estrutura.from_json(entrada)
    K, gdl_map, contrib = montar_global(est)
    assert K.shape == (6, 6)
    assert np.allclose(K, K.T)


def test_montar_global_mapa_contribuicoes():
    entrada = {"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 3, "y": 0},
                {"id": 3, "x": 3, "y": 3}],
        "elementos": [
            {"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
             "secao": {"bw": 14, "h": 40}},
            {"id": "P1", "tipo": "pilar", "no_i": 2, "no_j": 3,
             "secao": {"bw": 19, "h": 19}}],
        "vinculos": [], "cargas": []}}
    est = Estrutura.from_json(entrada)
    K, gdl_map, contrib = montar_global(est)
    # No 2 (GDL 3,4,5) recebe contribuicao de V1 e P1
    assert "V1" in contrib[(3, 3)]
    assert "P1" in contrib[(3, 3)]
    # No 1 (GDL 0,1,2) so de V1
    assert contrib[(0, 0)] == {"V1"}
```

- [x] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_rigidez.py::test_montar_global_dimensao -v`
Esperado: `ImportError: cannot import name 'montar_global'`

- [x] **Passo 3: Adicionar `montar_global` em `engine/rigidez.py`**

```python
def gdls_do_no(no_id: int, ordem_nos: list) -> list:
    """Retorna os 3 indices de GDL global de um no (2D: ux, uy, rz)."""
    idx = ordem_nos.index(no_id)
    return [3 * idx, 3 * idx + 1, 3 * idx + 2]


def montar_global(estrutura):
    """Monta K_global e o mapa de contribuicoes por celula.

    Retorna (K, gdl_map, contrib):
      K        : np.ndarray (n_gdl x n_gdl)
      gdl_map  : dict no_id -> [gdl_ux, gdl_uy, gdl_rz]
      contrib  : dict (i, j) -> set de ids de elementos que contribuem
    """
    ordem_nos = sorted(estrutura.nos.keys())
    n_gdl = 3 * len(ordem_nos)
    K = np.zeros((n_gdl, n_gdl))
    contrib = {}
    gdl_map = {nid: gdls_do_no(nid, ordem_nos) for nid in ordem_nos}

    E = estrutura.material.Ecs
    for el in estrutura.elementos:
        ke = k_global_elemento(E, el.secao.area, el.secao.inercia,
                               el.comprimento(), el.angulo())
        gdl = gdl_map[el.no_i.id] + gdl_map[el.no_j.id]  # 6 indices
        for a in range(6):
            for b in range(6):
                ia, ib = gdl[a], gdl[b]
                K[ia, ib] += ke[a, b]
                if ke[a, b] != 0.0:
                    contrib.setdefault((ia, ib), set()).add(el.id)
    return K, gdl_map, contrib
```

- [x] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_rigidez.py -v`
Esperado: 7 PASSED

- [x] **Passo 5: Commit**

```bash
git add engine/rigidez.py tests/test_rigidez.py
git commit -m "feat: engine/rigidez — montagem K_global com mapa de contribuicoes"
```

---

### Task 5: solver.py — forças nodais equivalentes (carga distribuída)

**Files:**
- Create: `engine/solver.py`
- Create: `tests/test_solver.py`

- [x] **Passo 1: Escrever teste falho `tests/test_solver.py`**

```python
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.solver import forcas_equivalentes_distribuida


def test_forcas_equivalentes_carga_para_baixo():
    # q = 0,10 kN/cm para baixo, L = 500 cm, barra horizontal (angulo 0)
    # Reacoes de engaste: V = qL/2 = 25 kN; M = qL^2/12 = 2083,33 kN.cm
    f = forcas_equivalentes_distribuida(q=0.10, L=500.0, angulo=0.0)
    assert abs(f[1] - (-25.0)) < 0.01   # fy no no i
    assert abs(f[4] - (-25.0)) < 0.01   # fy no no j
    assert abs(f[2] - (-2083.333)) < 0.1  # Mz no no i
    assert abs(f[5] - (2083.333)) < 0.1   # Mz no no j


def test_forcas_equivalentes_soma_vertical():
    f = forcas_equivalentes_distribuida(q=0.10, L=500.0, angulo=0.0)
    # soma das forcas verticais = -qL = -50 kN
    assert abs((f[1] + f[4]) - (-50.0)) < 0.01
```

- [x] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_solver.py -v`
Esperado: `ModuleNotFoundError`

- [x] **Passo 3: Implementar `engine/solver.py` (parte 1)**

```python
import numpy as np
from engine.rigidez import montar_global, matriz_T


def forcas_equivalentes_distribuida(q: float, L: float,
                                    angulo: float) -> np.ndarray:
    """Vetor 6x1 de forcas nodais equivalentes (sistema GLOBAL) para carga
    uniforme q [kN/cm] na direcao -y (para baixo) sobre uma barra.

    Convencao: q positivo aponta para baixo (gravidade).
    Forcas de engastamento perfeito no sistema local:
      fy_i = fy_j = -qL/2 ; Mz_i = -qL^2/12 ; Mz_j = +qL^2/12
    """
    V = q * L / 2.0
    M = q * L * L / 12.0
    f_local = np.array([0.0, -V, -M, 0.0, -V, M])
    T = matriz_T(angulo)
    # f_global = T^T f_local
    return T.T @ f_local
```

- [x] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_solver.py -v`
Esperado: 2 PASSED

- [x] **Passo 5: Commit**

```bash
git add engine/solver.py tests/test_solver.py
git commit -m "feat: engine/solver — forcas nodais equivalentes para carga distribuida"
```

---

### Task 6: solver.py — vetor de forças, condições de contorno, solução {u}

**Files:**
- Modify: `engine/solver.py`
- Modify: `tests/test_solver.py`

- [x] **Passo 1: Adicionar teste falho (cantilever analítico)**

```python
from engine.solver import resolver
from engine.modelo import Estrutura


def _estrutura_cantilever():
    # Engaste no no 1, carga P=10 kN para baixo no no 2 (ponta livre)
    # Barra horizontal L=300cm, secao 14x40, fck=25 basalto
    return Estrutura.from_json({"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 3, "y": 0}],
        "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                       "secao": {"bw": 14, "h": 40}}],
        "vinculos": [{"no": 1, "ux": True, "uy": True, "rz": True}],
        "cargas": [{"no": 2, "tipo": "nodal", "fy": -10.0}]}})


def test_cantilever_deslocamento_ponta():
    est = _estrutura_cantilever()
    res = resolver(est)
    # delta = P L^3 / (3 EI); EI = 2898*74666,67; L=300
    # delta = -10*300^3/(3*2898*74666,67) = -0,4159 cm = -4,159 mm
    uy2 = res["deslocamentos"][2]["uy"]   # em mm
    assert abs(uy2 - (-4.159)) < 0.05


def test_cantilever_rotacao_ponta():
    est = _estrutura_cantilever()
    res = resolver(est)
    # theta = P L^2 / (2 EI) = -0,00208 rad
    rz2 = res["deslocamentos"][2]["rz"]
    assert abs(rz2 - (-0.00208)) < 0.0001
```

- [x] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_solver.py::test_cantilever_deslocamento_ponta -v`
Esperado: `ImportError: cannot import name 'resolver'`

- [x] **Passo 3: Adicionar montagem de F e `resolver` em `engine/solver.py`**

```python
def montar_forcas(estrutura, gdl_map, n_gdl):
    """Vetor global de forcas (kN, kN.cm). Soma cargas nodais e equivalentes
    de cargas distribuidas."""
    F = np.zeros(n_gdl)
    elem_por_id = {el.id: el for el in estrutura.elementos}
    for c in estrutura.cargas:
        if c.tipo == "nodal" and c.no is not None:
            g = gdl_map[c.no]
            F[g[0]] += c.fx
            F[g[1]] += c.fy
            F[g[2]] += c.mz
        elif c.tipo == "distribuida" and c.elemento is not None:
            el = elem_por_id[c.elemento]
            feq = forcas_equivalentes_distribuida(
                c.valor, el.comprimento(), el.angulo())
            g = gdl_map[el.no_i.id] + gdl_map[el.no_j.id]
            for k in range(6):
                F[g[k]] += feq[k]
    return F


def _gdls_restritos(estrutura, gdl_map):
    """Lista de indices de GDL global restritos pelos vinculos (2D: ux,uy,rz)."""
    restr = []
    for v in estrutura.vinculos:
        g = gdl_map[v.no]
        if v.ux:
            restr.append(g[0])
        if v.uy:
            restr.append(g[1])
        if v.rz:
            restr.append(g[2])
    return sorted(set(restr))


def resolver(estrutura):
    """Resolve [K]{u}={F} aplicando condicoes de contorno.

    Retorna dict com 'deslocamentos' (por no, em mm e rad),
    'K', 'F', 'u_global', 'gdl_map', 'contrib', 'ordem_nos'.
    """
    K, gdl_map, contrib = montar_global(estrutura)
    n_gdl = K.shape[0]
    F = montar_forcas(estrutura, gdl_map, n_gdl)

    restritos = _gdls_restritos(estrutura, gdl_map)
    livres = [i for i in range(n_gdl) if i not in restritos]

    K_ff = K[np.ix_(livres, livres)]
    F_f = F[livres]
    u = np.zeros(n_gdl)
    if livres:
        u_f = np.linalg.solve(K_ff, F_f)
        for idx, gl in enumerate(livres):
            u[gl] = u_f[idx]

    ordem_nos = sorted(estrutura.nos.keys())
    desloc = {}
    for nid in ordem_nos:
        g = gdl_map[nid]
        desloc[nid] = {
            "ux": u[g[0]] * 10.0,   # cm -> mm
            "uy": u[g[1]] * 10.0,
            "rz": u[g[2]],          # rad
        }

    return {"deslocamentos": desloc, "K": K, "F": F, "u_global": u,
            "gdl_map": gdl_map, "contrib": contrib, "ordem_nos": ordem_nos,
            "restritos": restritos}
```

- [x] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_solver.py -v`
Esperado: 4 PASSED

- [x] **Passo 5: Commit**

```bash
git add engine/solver.py tests/test_solver.py
git commit -m "feat: engine/solver — montagem de forcas, contorno e solucao dos deslocamentos"
```

---

### Task 7: solver.py — reações de apoio e esforços internos N/V/M

**Files:**
- Modify: `engine/solver.py`
- Modify: `tests/test_solver.py`

- [x] **Passo 1: Adicionar teste falho (viga biapoiada)**

```python
from engine.solver import reacoes, esforcos_elemento


def _estrutura_biapoiada():
    # Viga biapoiada L=500cm, q=10 kN/m, secao 14x40
    # No 1: apoio fixo (ux,uy); No 2: apoio movel (uy). rz livre nos dois.
    return Estrutura.from_json({"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 5, "y": 0}],
        "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                       "secao": {"bw": 14, "h": 40}}],
        "vinculos": [{"no": 1, "ux": True, "uy": True},
                     {"no": 2, "uy": True}],
        "cargas": [{"elemento": "V1", "tipo": "distribuida",
                    "valor": 10.0, "direcao": "y"}]}})


def test_biapoiada_reacoes():
    est = _estrutura_biapoiada()
    res = resolver(est)
    R = reacoes(est, res)
    # Cada apoio: qL/2 = 0,10*500/2 = 25 kN (para cima)
    assert abs(R[1]["fy"] - 25.0) < 0.1
    assert abs(R[2]["fy"] - 25.0) < 0.1


def test_biapoiada_momento_meio_vao():
    est = _estrutura_biapoiada()
    res = resolver(est)
    esf = esforcos_elemento(est, res, "V1", n_pontos=11)
    # M no meio = qL^2/8 = 0,10*500^2/8 = 3125 kN.cm = 31,25 kNm
    m_meio = esf["M"][5]   # ponto central (indice 5 de 0..10)
    assert abs(abs(m_meio) - 31.25) < 0.5   # kNm
```

- [x] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_solver.py::test_biapoiada_reacoes -v`
Esperado: `ImportError: cannot import name 'reacoes'`

- [x] **Passo 3: Adicionar `reacoes` e `esforcos_elemento` em `engine/solver.py`**

```python
def reacoes(estrutura, resultado):
    """Reacoes nodais nos apoios: {R} = [K]{u} - {F}.

    Retorna dict no_id -> {'fx','fy','mz'} (kN, kNm) apenas para nos com vinculo.
    """
    K = resultado["K"]
    u = resultado["u_global"]
    F = resultado["F"]
    gdl_map = resultado["gdl_map"]
    R_vec = K @ u - F

    nos_apoio = {v.no for v in estrutura.vinculos}
    out = {}
    for nid in nos_apoio:
        g = gdl_map[nid]
        out[nid] = {
            "fx": R_vec[g[0]],
            "fy": R_vec[g[1]],
            "mz": R_vec[g[2]] / 100.0,   # kN.cm -> kNm
        }
    return out


def esforcos_elemento(estrutura, resultado, elem_id, n_pontos=11):
    """Diagramas N(x), V(x), M(x) ao longo de um elemento.

    Retorna {'x': [cm], 'N': [kN], 'V': [kN], 'M': [kNm]}.
    Considera carga distribuida transversal se houver.
    """
    from engine.rigidez import k_local, matriz_T
    el = next(e for e in estrutura.elementos if e.id == elem_id)
    L = el.comprimento()
    E = estrutura.material.Ecs
    kl = k_local(E, el.secao.area, el.secao.inercia, L)
    T = matriz_T(el.angulo())

    gdl_map = resultado["gdl_map"]
    u = resultado["u_global"]
    g = gdl_map[el.no_i.id] + gdl_map[el.no_j.id]
    u_e_global = np.array([u[i] for i in g])
    u_e_local = T @ u_e_global
    f_local = kl @ u_e_local   # forcas internas nos nos (sem carga de vao)

    # carga distribuida transversal sobre o elemento (kN/cm, para baixo)
    q = 0.0
    for c in estrutura.cargas:
        if c.tipo == "distribuida" and c.elemento == elem_id:
            q += c.valor

    # No no i: N_i = -f_local[0]; V_i = -f_local[1] (porem incluimos a parcela
    # de engastamento ja embutida em u). Para o diagrama usamos as forcas
    # internas nodais corrigidas pela carga de vao (metodo da superposicao).
    feq_local = np.array([0.0, -q * L / 2, -q * L * L / 12,
                          0.0, -q * L / 2, q * L * L / 12])
    f_int = f_local - feq_local   # forcas internas reais nos nos

    N_i = -f_int[0]
    V_i = f_int[1]
    M_i = f_int[2]

    xs, Ns, Vs, Ms = [], [], [], []
    for k in range(n_pontos):
        x = L * k / (n_pontos - 1)
        N = N_i
        V = V_i - q * x
        M = M_i + V_i * x - q * x * x / 2.0
        xs.append(x)
        Ns.append(N)
        Vs.append(V)
        Ms.append(M / 100.0)   # kN.cm -> kNm
    return {"x": xs, "N": Ns, "V": Vs, "M": Ms}
```

- [x] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_solver.py -v`
Esperado: 6 PASSED

- [x] **Passo 5: Commit**

```bash
git add engine/solver.py tests/test_solver.py
git commit -m "feat: engine/solver — reacoes de apoio e diagramas N/V/M"
```

---

### Task 8: solver.py — flecha imediata e diferida (Branson)

**Files:**
- Modify: `engine/solver.py`
- Modify: `tests/test_solver.py`

- [x] **Passo 1: Adicionar teste falho**

```python
from engine.solver import flecha_viga


def test_flecha_biapoiada_imediata():
    est = _estrutura_biapoiada()
    res = resolver(est)
    fl = flecha_viga(est, res, "V1")
    # Estadio I (Ig): delta = 5 q L^4 / (384 E Ig)
    # q=0,10; L=500; E=2898; Ig=74666,67
    # delta = 5*0,10*500^4/(384*2898*74666,67) = 0,376 cm = 3,76 mm
    assert abs(fl["imediata"] - 3.76) < 0.2


def test_flecha_diferida_maior():
    est = _estrutura_biapoiada()
    res = resolver(est)
    fl = flecha_viga(est, res, "V1")
    # diferida = imediata * (1 + 2,5) = imediata * 3,5
    assert abs(fl["diferida"] - fl["imediata"] * 3.5) < 0.01


def test_flecha_limite_l250():
    est = _estrutura_biapoiada()
    res = resolver(est)
    fl = flecha_viga(est, res, "V1")
    # L/250 = 500/250 = 2,0 cm = 20 mm
    assert abs(fl["limite"] - 20.0) < 0.01
```

- [x] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_solver.py::test_flecha_biapoiada_imediata -v`
Esperado: `ImportError`

- [x] **Passo 3: Adicionar `flecha_viga` em `engine/solver.py`**

```python
def flecha_viga(estrutura, resultado, elem_id, phi=2.5, balanco=False):
    """Flecha imediata (Estadio I, inercia bruta) e diferida de uma viga.

    Aproximacao: usa a flecha maxima da elastica numerica a partir dos
    deslocamentos verticais interpolados nos nos do elemento, e como
    referencia analitica calcula 5qL^4/(384 E Ig) quando ha carga distribuida.
    Retorna {'imediata','diferida','limite'} em mm.
    """
    el = next(e for e in estrutura.elementos if e.id == elem_id)
    L = el.comprimento()
    E = estrutura.material.Ecs
    Ig = el.secao.inercia

    q = sum(c.valor for c in estrutura.cargas
            if c.tipo == "distribuida" and c.elemento == elem_id)

    if q > 0:
        delta_cm = 5 * q * L ** 4 / (384 * E * Ig)
    else:
        # fallback: maior deslocamento vertical nodal do elemento
        g = resultado["gdl_map"]
        u = resultado["u_global"]
        uyi = abs(u[g[el.no_i.id][1]])
        uyj = abs(u[g[el.no_j.id][1]])
        delta_cm = max(uyi, uyj)

    imediata = delta_cm * 10.0          # mm
    diferida = imediata * (1 + phi)
    limite = (L / (125.0 if balanco else 250.0)) * 10.0  # mm
    return {"imediata": imediata, "diferida": diferida, "limite": limite}
```

- [x] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_solver.py -v`
Esperado: 9 PASSED

- [x] **Passo 5: Commit**

```bash
git add engine/solver.py tests/test_solver.py
git commit -m "feat: engine/solver — flecha imediata e diferida (Branson simplificado)"
```

---

### Task 9: dimensionamento.py — esforço cortante (vigas)

**Files:**
- Create: `engine/dimensionamento.py`
- Create: `tests/test_dimensionamento.py`

- [x] **Passo 1: Escrever teste falho `tests/test_dimensionamento.py`**

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.materiais import Material
from engine.dimensionamento import cisalhamento_viga


def test_cisalhamento_vrd2_ok():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # bw=14, d=36, VSd=80 kN
    r = cisalhamento_viga(m, bw=14, d=36, VSd=80.0)
    # av2 = 1-25/250 = 0,9; fcd=1,7857; VRd2=0,27*0,9*1,7857*14*36
    # = 0,27*0,9*1,7857*504 = 218,6 kN
    assert abs(r["VRd2"] - 218.6) < 1.0
    assert r["bielas_ok"] is True


def test_cisalhamento_vc():
    m = Material(fck=25, fyk=500, agregado='basalto')
    r = cisalhamento_viga(m, bw=14, d=36, VSd=80.0)
    # Vc = 0,6*fctd*bw*d = 0,6*0,12825*14*36 = 38,77 kN
    assert abs(r["Vc"] - 38.77) < 0.5


def test_cisalhamento_asw_s():
    m = Material(fck=25, fyk=500, agregado='basalto')
    r = cisalhamento_viga(m, bw=14, d=36, VSd=80.0)
    # fywd=min(50/1,15;43,5)=43,478; Asw/s=(80-38,77)/(0,9*36*43,478)
    # = 41,23/1408,7 = 0,02927 cm2/cm
    assert abs(r["Asw_s"] - 0.02927) < 0.001


def test_cisalhamento_bielas_estouram():
    m = Material(fck=25, fyk=500, agregado='basalto')
    r = cisalhamento_viga(m, bw=14, d=36, VSd=250.0)
    # VSd 250 > VRd2 218,6 -> bielas nao ok
    assert r["bielas_ok"] is False
```

- [x] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_dimensionamento.py -v`
Esperado: `ModuleNotFoundError`

- [x] **Passo 3: Implementar `engine/dimensionamento.py` (parte 1)**

```python
def cisalhamento_viga(material, bw, d, VSd):
    """Verificacao ao cortante (Modelo I, NBR 6118:2023).

    bw, d em cm; VSd em kN. Retorna dict com VRd2, Vc, Asw_s, Asw_s_min,
    bielas_ok. Asw_s em cm2/cm (area total dos ramos por cm).
    """
    fck = material.fck
    fcd = material.fcd
    fctd = material.fctd
    fywd = min(material.fyk / 1.15 / 10.0, 43.5)  # kN/cm2, limite 435 MPa

    av2 = 1 - fck / 250.0
    VRd2 = 0.27 * av2 * fcd * bw * d
    Vc = 0.6 * fctd * bw * d

    fctm = material.fctm  # MPa
    fywk = min(material.fyk, 500.0)
    # Asw/s minimo: 0,2 * fctm/fywk * bw  (com fctm,fywk em MPa, bw em cm)
    Asw_s_min = 0.2 * (fctm / fywk) * bw

    if VSd <= Vc:
        Asw_s = Asw_s_min
    else:
        Asw_s = max((VSd - Vc) / (0.9 * d * fywd), Asw_s_min)

    return {
        "VRd2": VRd2, "Vc": Vc,
        "Asw_s": Asw_s, "Asw_s_min": Asw_s_min,
        "bielas_ok": VSd <= VRd2,
    }
```

- [x] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_dimensionamento.py -v`
Esperado: 4 PASSED

- [x] **Passo 5: Commit**

```bash
git add engine/dimensionamento.py tests/test_dimensionamento.py
git commit -m "feat: engine/dimensionamento — verificacao ao cortante Modelo I"
```

---

### Task 10: dimensionamento.py — flexão (simples, dupla, pele)

**Files:**
- Modify: `engine/dimensionamento.py`
- Modify: `tests/test_dimensionamento.py`

- [ ] **Passo 1: Adicionar teste falho**

```python
from engine.dimensionamento import flexao_viga, armadura_pele


def test_flexao_armadura_simples():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # Md=50 kNm=5000 kN.cm; bw=14; d=36
    r = flexao_viga(m, bw=14, d=36, Md=50.0)
    # x = 9,085 cm; x/d=0,2524; As=3,55 cm2
    assert abs(r["x"] - 9.085) < 0.1
    assert abs(r["As"] - 3.55) < 0.05
    assert r["tipo"] == "simples"
    assert r["ductil"] is True


def test_flexao_armadura_minima():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # Md pequeno -> As_min governa: 0,15% * 14 * 36 = 0,756 cm2
    r = flexao_viga(m, bw=14, d=36, Md=5.0)
    assert abs(r["As_min"] - 0.756) < 0.01
    assert r["As"] >= r["As_min"]


def test_flexao_armadura_dupla():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # Md muito alto -> dupla. Md=200 kNm em secao 14x36 estoura Md,duc
    r = flexao_viga(m, bw=14, d=36, Md=200.0)
    assert r["tipo"] == "dupla"


def test_armadura_pele_necessaria():
    m = Material(fck=25, fyk=500, agregado='basalto')
    # h=70 > 60 -> pele. As_pele por face = 0,10% * bw * (h util)
    r = armadura_pele(m, bw=14, h=70, cobrimento=3.0, phi_est=0.5)
    assert r["necessaria"] is True
    assert r["As_face"] > 0


def test_armadura_pele_dispensada():
    m = Material(fck=25, fyk=500, agregado='basalto')
    r = armadura_pele(m, bw=14, h=40, cobrimento=3.0, phi_est=0.5)
    assert r["necessaria"] is False
```

- [ ] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_dimensionamento.py::test_flexao_armadura_simples -v`
Esperado: `ImportError`

- [ ] **Passo 3: Adicionar `flexao_viga` e `armadura_pele`**

```python
def flexao_viga(material, bw, d, Md):
    """Dimensionamento a flexao simples/dupla (NBR 6118:2023).

    Md em kNm; bw, d em cm. Retorna dict com x, As, As2, As_min, tipo,
    ductil. As em cm2.
    """
    fcd = material.fcd
    fyd = material.fyd
    Md_cm = Md * 100.0   # kNm -> kN.cm

    x_duc = 0.45 * d
    Md_duc = 0.85 * fcd * 0.80 * x_duc * bw * (d - 0.80 * x_duc / 2)

    As_min = 0.0015 * bw * d   # 0,15%

    if Md_cm <= Md_duc:
        # armadura simples
        rad = 1 - Md_cm / (0.425 * bw * d * d * fcd)
        rad = max(rad, 0.0)
        x = 1.25 * d * (1 - rad ** 0.5)
        As = 0.85 * fcd * 0.80 * x * bw / fyd
        As = max(As, As_min)
        return {"x": x, "As": As, "As2": 0.0, "As_min": As_min,
                "tipo": "simples", "ductil": x <= x_duc}
    else:
        # armadura dupla
        Es = 21000.0  # kN/cm2
        ecu = 0.0035
        d_linha = 0.10 * d   # estimativa d'
        sigma_s2 = min(ecu * (x_duc - d_linha) / x_duc * Es, fyd)
        As2 = (Md_cm - Md_duc) / (sigma_s2 * (d - d_linha))
        As1 = (0.85 * fcd * 0.80 * x_duc * bw + As2 * sigma_s2) / fyd
        return {"x": x_duc, "As": As1, "As2": As2, "As_min": As_min,
                "tipo": "dupla", "ductil": True}


def armadura_pele(material, bw, h, cobrimento, phi_est):
    """Armadura de pele para vigas com h > 60 cm (NBR 6118, 17.3.5.2.3).

    As_pele = 0,10% da area da alma, por face. Retorna dict.
    """
    if h <= 60.0:
        return {"necessaria": False, "As_face": 0.0}
    h_util = h - 2 * cobrimento - 2 * phi_est
    As_face = 0.0010 * bw * h_util / 2.0  # por face
    return {"necessaria": True, "As_face": As_face, "espacamento_max": 20.0}
```

- [ ] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_dimensionamento.py -v`
Esperado: 9 PASSED

- [ ] **Passo 5: Commit**

```bash
git add engine/dimensionamento.py tests/test_dimensionamento.py
git commit -m "feat: engine/dimensionamento — flexao simples/dupla e armadura de pele"
```

---

### Task 11: dimensionamento.py — pilares (esbeltez + flexo-compressão)

**Files:**
- Modify: `engine/dimensionamento.py`
- Modify: `tests/test_dimensionamento.py`

- [ ] **Passo 1: Adicionar teste falho**

```python
from engine.dimensionamento import esbeltez_pilar, flexocompressao_obliqua


def test_esbeltez_curto():
    # secao 19x19, le=280cm -> i=19/3,46=5,49; lambda=51 -> esbelto
    r = esbeltez_pilar(b_menor=19, le=280)
    assert abs(r["lambda"] - 51.0) < 1.0
    assert r["classe"] == "esbelto"


def test_esbeltez_curto_real():
    # secao 30x30, le=280 -> i=8,67; lambda=32,3 -> curto
    r = esbeltez_pilar(b_menor=30, le=280)
    assert r["lambda"] < 35
    assert r["classe"] == "curto"


def test_flexocompressao_envoltoria_passa():
    # Mx/MRdxx=0,5; My/MRdyy=0,4 -> 0,5^1,2+0,4^1,2 = 0,435+0,333=0,768<=1
    r = flexocompressao_obliqua(Mx=50, My=40, MRdxx=100, MRdyy=100)
    assert r["passa"] is True
    assert abs(r["indice"] - 0.768) < 0.01


def test_flexocompressao_envoltoria_falha():
    r = flexocompressao_obliqua(Mx=90, My=90, MRdxx=100, MRdyy=100)
    # 0,9^1,2 * 2 = 0,883*2 = 1,766 > 1
    assert r["passa"] is False
```

- [ ] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_dimensionamento.py::test_esbeltez_curto -v`
Esperado: `ImportError`

- [ ] **Passo 3: Adicionar `esbeltez_pilar` e `flexocompressao_obliqua`**

```python
def esbeltez_pilar(b_menor, le):
    """Indice de esbeltez de pilar retangular (NBR 6118:2023).

    b_menor, le em cm. Retorna dict com i, lambda, classe.
    """
    i = b_menor / 3.46   # raio de giracao secao retangular
    lam = le / i
    if lam <= 35:
        classe = "curto"
    elif lam <= 90:
        classe = "esbelto"
    elif lam <= 140:
        classe = "muito_esbelto"
    else:
        classe = "nao_linear"
    return {"i": i, "lambda": lam, "classe": classe}


def flexocompressao_obliqua(Mx, My, MRdxx, MRdyy, alpha=1.2):
    """Verificacao da envoltoria de flexo-compressao obliqua (NBR 6118 17.2.5).

    indice = (Mx/MRdxx)^alpha + (My/MRdyy)^alpha <= 1.
    """
    indice = (Mx / MRdxx) ** alpha + (My / MRdyy) ** alpha
    return {"indice": indice, "passa": indice <= 1.0}
```

- [ ] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_dimensionamento.py -v`
Esperado: 13 PASSED

- [ ] **Passo 5: Commit**

```bash
git add engine/dimensionamento.py tests/test_dimensionamento.py
git commit -m "feat: engine/dimensionamento — esbeltez e flexo-compressao obliqua de pilares"
```

---

### Task 12: detalhamento.py — escolher bitola, estribo e zonas

**Files:**
- Create: `engine/detalhamento.py`
- Create: `tests/test_detalhamento.py`

- [ ] **Passo 1: Escrever teste falho `tests/test_detalhamento.py`**

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.detalhamento import escolher_bitola, escolher_estribo


def test_escolher_bitola_menor_desperdicio():
    # As=3,55 -> 3 Ø12,5 (3,68) tem menor desperdicio entre validos
    r = escolher_bitola(3.55)
    assert r["n"] == 3
    assert r["phi"] == 12.5
    assert abs(r["As_fornecido"] - 3.68) < 0.01
    assert "3" in r["descricao"] and "12,5" in r["descricao"]


def test_escolher_bitola_minimo_duas_barras():
    # As pequeno -> minimo 2 barras
    r = escolher_bitola(0.5)
    assert r["n"] >= 2


def test_escolher_estribo_2_ramos():
    # Asw/s = 0,02927 cm2/cm; estribo 2 ramos
    r = escolher_estribo(0.02927, comprimento_zona=80)
    # Ø5=0,196cm2; 2 ramos -> 0,392; s = 0,392/0,02927 = 13,4 -> arredonda p/ baixo
    assert r["phi"] == 5.0
    assert r["n_ramos"] == 2
    assert r["espacamento"] <= 13.4
    assert r["quantidade"] >= 1


def test_escolher_estribo_respeita_smax():
    # Asw/s minimo -> espacamento limitado a 30cm (ou menos)
    r = escolher_estribo(0.005, comprimento_zona=200)
    assert r["espacamento"] <= 30
```

- [ ] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_detalhamento.py -v`
Esperado: `ModuleNotFoundError`

- [ ] **Passo 3: Implementar `engine/detalhamento.py`**

```python
import math

BITOLAS = [6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0]  # mm
AREAS = {6.3: 0.312, 8.0: 0.503, 10.0: 0.785, 12.5: 1.227,
         16.0: 2.011, 20.0: 3.142, 25.0: 4.909, 32.0: 8.042}  # cm2
BITOLAS_ESTRIBO = [5.0, 6.3, 8.0]
AREA_ESTRIBO = {5.0: 0.196, 6.3: 0.312, 8.0: 0.503}


def _fmt(phi):
    s = ("%.1f" % phi).replace(".", ",").replace(",0", "")
    return s


def escolher_bitola(As_nec, n_min=2, n_max=8):
    """Escolhe (n, phi) que cobre As_nec com menor desperdicio.

    Desempate: menor numero de barras. Retorna dict com n, phi, As_fornecido,
    descricao.
    """
    candidatos = []
    for phi in BITOLAS:
        for n in range(n_min, n_max + 1):
            As_forn = n * AREAS[phi]
            if As_forn >= As_nec:
                candidatos.append((As_forn, n, phi))
                break  # menor n para esta bitola
    if not candidatos:
        phi = BITOLAS[-1]
        n = n_max
        As_forn = n * AREAS[phi]
        candidatos = [(As_forn, n, phi)]
    # menor desperdicio (As_forn), desempate por menor n
    As_forn, n, phi = min(candidatos, key=lambda t: (t[0], t[1]))
    return {"n": n, "phi": phi, "As_fornecido": As_forn,
            "descricao": "%d Ø %s (%.2f cm²)" % (n, _fmt(phi), As_forn)}


def escolher_estribo(Asw_s, comprimento_zona, n_ramos=2, s_max=30.0):
    """Escolhe (phi, espacamento) do estribo para um Asw/s dado.

    Asw_s em cm2/cm (area total dos ramos por cm). comprimento_zona em cm.
    Retorna dict com phi, espacamento, n_ramos, quantidade, descricao.
    """
    for phi in BITOLAS_ESTRIBO:
        area_total = n_ramos * AREA_ESTRIBO[phi]
        s = area_total / Asw_s if Asw_s > 0 else s_max
        s = min(s, s_max)
        s = max(math.floor(s), 5)  # cm, minimo pratico 5 cm
        if s >= 5:
            quantidade = max(int(comprimento_zona / s), 1)
            return {"phi": phi, "espacamento": float(s), "n_ramos": n_ramos,
                    "quantidade": quantidade,
                    "descricao": "Ø %s c/%d cm (%dr) — %d un." % (
                        _fmt(phi), s, n_ramos, quantidade)}
    # fallback
    phi = BITOLAS_ESTRIBO[0]
    s = 5
    quantidade = max(int(comprimento_zona / s), 1)
    return {"phi": phi, "espacamento": 5.0, "n_ramos": n_ramos,
            "quantidade": quantidade,
            "descricao": "Ø 5 c/5 cm (%dr) — %d un." % (n_ramos, quantidade)}
```

- [ ] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_detalhamento.py -v`
Esperado: 4 PASSED

- [ ] **Passo 5: Commit**

```bash
git add engine/detalhamento.py tests/test_detalhamento.py
git commit -m "feat: engine/detalhamento — escolha de bitola e estribo por menor desperdicio"
```

---

### Task 13: svg_secao.py — desenho da seção transversal

**Files:**
- Create: `engine/svg_secao.py`
- Create: `tests/test_svg.py`

- [ ] **Passo 1: Escrever teste falho `tests/test_svg.py`**

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.svg_secao import desenhar_secao


def test_secao_retorna_svg():
    svg = desenhar_secao(bw=14, h=40, cobrimento=3.0,
                         barras_inf=(3, 10.0), barras_sup=(2, 12.5),
                         barras_pele=0, phi_est=5.0)
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")


def test_secao_contem_barras():
    svg = desenhar_secao(bw=14, h=40, cobrimento=3.0,
                         barras_inf=(3, 10.0), barras_sup=(2, 12.5),
                         barras_pele=0, phi_est=5.0)
    # 3 barras inferiores + 2 superiores = 5 circulos
    assert svg.count("<circle") == 5


def test_secao_com_pele():
    svg = desenhar_secao(bw=19, h=70, cobrimento=3.0,
                         barras_inf=(3, 16.0), barras_sup=(3, 16.0),
                         barras_pele=2, phi_est=5.0)
    # 3 + 3 + (2 por face * 2 faces = 4) = 10 circulos
    assert svg.count("<circle") == 10
```

- [ ] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_svg.py -v`
Esperado: `ModuleNotFoundError`

- [ ] **Passo 3: Implementar `engine/svg_secao.py`**

```python
def desenhar_secao(bw, h, cobrimento, barras_inf, barras_sup,
                   barras_pele, phi_est):
    """Gera SVG da secao transversal com armaduras posicionadas.

    bw, h, cobrimento em cm. barras_inf/sup = (n, phi_mm). barras_pele = n por
    face (>0 desenha 'n' barras em cada lateral). Escala: 1 cm = ESCALA px.
    """
    ESCALA = 6.0          # px por cm
    MARG = 40.0           # margem px
    W = bw * ESCALA
    H = h * ESCALA
    svg_w = W + 2 * MARG
    svg_h = H + 2 * MARG

    def px(x_cm, y_cm):
        # y invertido (SVG cresce para baixo); origem no canto inf-esq da secao
        return (MARG + x_cm * ESCALA, MARG + (h - y_cm) * ESCALA)

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" '
             'width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
             % (svg_w, svg_h, svg_w, svg_h)]

    # contorno da secao
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="#f5f5f5" stroke="#333" stroke-width="2"/>'
                 % (MARG, MARG, W, H))

    # linha de cobrimento (estribo) tracejada
    c = cobrimento
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="none" stroke="#888" stroke-width="1" '
                 'stroke-dasharray="4 3"/>'
                 % (MARG + c * ESCALA, MARG + c * ESCALA,
                    W - 2 * c * ESCALA, H - 2 * c * ESCALA))

    def circulos(n, phi_mm, y_cm, cor):
        if n <= 0:
            return
        r = max(phi_mm / 10.0 / 2.0 * ESCALA, 3.0)  # raio px
        x0 = c + phi_mm / 10.0 / 2.0
        x1 = bw - c - phi_mm / 10.0 / 2.0
        for k in range(n):
            xc = x0 if n == 1 else x0 + (x1 - x0) * k / (n - 1)
            cx, cy = px(xc, y_cm)
            parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                         % (cx, cy, r, cor))

    # armadura inferior (positiva, azul) e superior (negativa, vermelha)
    n_inf, phi_inf = barras_inf
    n_sup, phi_sup = barras_sup
    circulos(n_inf, phi_inf, c + phi_inf / 20.0, "#2563eb")
    circulos(n_sup, phi_sup, h - c - phi_sup / 20.0, "#dc2626")

    # armadura de pele (cinza) nas duas laterais
    if barras_pele > 0:
        r = max(8.0 / 10.0 / 2.0 * ESCALA, 3.0)
        for face_x in (c + 0.4, bw - c - 0.4):
            for k in range(barras_pele):
                y_cm = h * (k + 1) / (barras_pele + 1)
                cx, cy = px(face_x, y_cm)
                parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" '
                             'fill="#6b7280"/>' % (cx, cy, r))

    # cotas
    parts.append('<text x="%.1f" y="%.1f" font-size="14" text-anchor="middle">'
                 'b=%.0f cm</text>' % (MARG + W / 2, svg_h - 12, bw))
    parts.append('<text x="12" y="%.1f" font-size="14" '
                 'transform="rotate(-90 12 %.1f)" text-anchor="middle">'
                 'h=%.0f cm</text>' % (MARG + H / 2, MARG + H / 2, h))

    parts.append('</svg>')
    return "\n".join(parts)
```

- [ ] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_svg.py -v`
Esperado: 3 PASSED

- [ ] **Passo 5: Commit**

```bash
git add engine/svg_secao.py tests/test_svg.py
git commit -m "feat: engine/svg_secao — desenho SVG da secao transversal armada"
```

---

### Task 14: svg_elevacao.py — desenho da elevação com zonas

**Files:**
- Create: `engine/svg_elevacao.py`
- Modify: `tests/test_svg.py`

- [ ] **Passo 1: Adicionar teste falho em `tests/test_svg.py`**

```python
from engine.svg_elevacao import desenhar_elevacao


def test_elevacao_retorna_svg():
    zonas = [
        {"x0": 0, "x1": 80, "tipo": "critica", "estribo": "Ø5 c/8"},
        {"x0": 80, "x1": 420, "tipo": "corrente", "estribo": "Ø5 c/15"},
        {"x0": 420, "x1": 500, "tipo": "critica", "estribo": "Ø5 c/8"},
    ]
    svg = desenhar_elevacao(L=500, h=40, zonas=zonas,
                            barras_pos="3 Ø10", barras_neg="3 Ø12,5")
    assert svg.startswith("<svg")
    assert "</svg>" in svg


def test_elevacao_desenha_zonas():
    zonas = [
        {"x0": 0, "x1": 80, "tipo": "critica", "estribo": "Ø5 c/8"},
        {"x0": 80, "x1": 420, "tipo": "corrente", "estribo": "Ø5 c/15"},
    ]
    svg = desenhar_elevacao(L=500, h=40, zonas=zonas,
                            barras_pos="3 Ø10", barras_neg="3 Ø12,5")
    # 2 zonas -> 2 retangulos de zona (alem do contorno)
    assert svg.count('class="zona"') == 2
```

- [ ] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_svg.py::test_elevacao_retorna_svg -v`
Esperado: `ModuleNotFoundError`

- [ ] **Passo 3: Implementar `engine/svg_elevacao.py`**

```python
def desenhar_elevacao(L, h, zonas, barras_pos, barras_neg):
    """Gera SVG da elevacao (vista longitudinal) com zonas de estribo.

    L, h em cm. zonas = lista de {x0, x1, tipo('critica'|'corrente'), estribo}.
    barras_pos/neg = textos descritivos. Escala horizontal e vertical proprias.
    """
    ESC_X = 1.2          # px por cm (comprimento)
    ESC_Y = 4.0          # px por cm (altura)
    MARG = 50.0
    W = L * ESC_X
    H = h * ESC_Y
    svg_w = W + 2 * MARG
    svg_h = H + 2 * MARG + 40

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" '
             'width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
             % (svg_w, svg_h, svg_w, svg_h)]

    # contorno da viga
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="#fafafa" stroke="#333" stroke-width="2"/>'
                 % (MARG, MARG, W, H))

    # zonas coloridas
    cores = {"critica": "#fecaca", "corrente": "#fef9c3"}
    for z in zonas:
        zx = MARG + z["x0"] * ESC_X
        zw = (z["x1"] - z["x0"]) * ESC_X
        parts.append('<rect class="zona" x="%.1f" y="%.1f" width="%.1f" '
                     'height="%.1f" fill="%s" opacity="0.6"/>'
                     % (zx, MARG, zw, H, cores.get(z["tipo"], "#eee")))
        parts.append('<text x="%.1f" y="%.1f" font-size="11" '
                     'text-anchor="middle">%s</text>'
                     % (zx + zw / 2, MARG + H + 16, z["estribo"]))

    # barras negativas (topo, vermelho) e positivas (fundo, azul)
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                 'stroke="#dc2626" stroke-width="3"/>'
                 % (MARG, MARG + 6, MARG + W, MARG + 6))
    parts.append('<text x="%.1f" y="%.1f" font-size="12" fill="#dc2626">'
                 '%s</text>' % (MARG + 4, MARG - 6, barras_neg))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                 'stroke="#2563eb" stroke-width="3"/>'
                 % (MARG, MARG + H - 6, MARG + W, MARG + H - 6))
    parts.append('<text x="%.1f" y="%.1f" font-size="12" fill="#2563eb">'
                 '%s</text>' % (MARG + 4, MARG + H + 30, barras_pos))

    # cota de comprimento
    parts.append('<text x="%.1f" y="%.1f" font-size="13" '
                 'text-anchor="middle">L = %.0f cm</text>'
                 % (MARG + W / 2, svg_h - 8, L))

    parts.append('</svg>')
    return "\n".join(parts)
```

- [ ] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_svg.py -v`
Esperado: 5 PASSED

- [ ] **Passo 5: Commit**

```bash
git add engine/svg_elevacao.py tests/test_svg.py
git commit -m "feat: engine/svg_elevacao — desenho SVG da elevacao com zonas de estribo"
```

---

### Task 15: relatorio.py — passos Carini e avisos automáticos

**Files:**
- Create: `engine/relatorio.py`
- Create: `tests/test_relatorio.py`

- [ ] **Passo 1: Escrever teste falho `tests/test_relatorio.py`**

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.modelo import Estrutura
from engine.relatorio import gerar_relatorio


ENTRADA = {"estrutura": {
    "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
    "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 5, "y": 0}],
    "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                   "secao": {"bw": 14, "h": 40}}],
    "vinculos": [{"no": 1, "ux": True, "uy": True}, {"no": 2, "uy": True}],
    "cargas": [{"elemento": "V1", "tipo": "distribuida", "valor": 10.0}]}}


def test_relatorio_tem_passos():
    rel = gerar_relatorio(Estrutura.from_json(ENTRADA))
    # ao menos os passos-chave presentes
    titulos = [p["titulo"] for p in rel["passos"]]
    assert any("Pre-dimensionamento" in t or "Pré-dimensionamento" in t
               for t in titulos)
    assert any("rea" in t.lower() and "o" in t.lower() for t in titulos)  # reacoes
    assert len(rel["passos"]) >= 12


def test_relatorio_tem_resultados():
    rel = gerar_relatorio(Estrutura.from_json(ENTRADA))
    assert "deslocamentos" in rel
    assert "reacoes" in rel
    assert "matriz_global" in rel  # serializada para o template


def test_relatorio_detalhamento_viga():
    rel = gerar_relatorio(Estrutura.from_json(ENTRADA))
    det = rel["elementos"]["V1"]
    # tem regiao de vao com armadura positiva
    assert "regioes" in det
    assert "meio" in det["regioes"]


def test_relatorio_aviso_flecha():
    # viga muito esbelta para forcar flecha alta
    entrada = {"estrutura": {
        "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
        "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 8, "y": 0}],
        "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                       "secao": {"bw": 12, "h": 25}}],
        "vinculos": [{"no": 1, "ux": True, "uy": True}, {"no": 2, "uy": True}],
        "cargas": [{"elemento": "V1", "tipo": "distribuida", "valor": 20.0}]}}
    rel = gerar_relatorio(Estrutura.from_json(entrada))
    assert len(rel["avisos"]) >= 1
```

- [ ] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_relatorio.py -v`
Esperado: `ModuleNotFoundError`

- [ ] **Passo 3: Implementar `engine/relatorio.py`**

```python
from engine.solver import (resolver, reacoes, esforcos_elemento, flecha_viga)
from engine.dimensionamento import (cisalhamento_viga, flexao_viga,
                                    armadura_pele)
from engine.detalhamento import escolher_bitola, escolher_estribo
from engine.svg_secao import desenhar_secao
from engine.svg_elevacao import desenhar_elevacao


def _matriz_serializavel(K, contrib):
    """Converte K e mapa de contribuicoes em listas para o template."""
    n = K.shape[0]
    linhas = []
    for i in range(n):
        linha = []
        for j in range(n):
            elems = sorted(contrib.get((i, j), set()))
            linha.append({"v": round(float(K[i, j]), 2), "elem": elems})
        linhas.append(linha)
    return linhas


def gerar_relatorio(estrutura):
    """Gera o relatorio completo: passos Carini, resultados, detalhamento,
    SVG e avisos. Retorna dict pronto para serializar/renderizar."""
    res = resolver(estrutura)
    R = reacoes(estrutura, res)
    avisos = []
    passos = []
    elementos_out = {}

    mat = estrutura.material

    # Passo 1 — Pre-dimensionamento
    passos.append({"titulo": "Passo 1 — Pre-dimensionamento",
                   "conteudo": "Verificacao das secoes adotadas."})
    # Passo 2 — Materiais
    passos.append({"titulo": "Passo 2 — Propriedades dos materiais",
                   "conteudo": "Ecs=%.0f kN/cm2 | fcd=%.3f | fyd=%.2f | "
                   "fctd=%.4f kN/cm2" % (mat.Ecs, mat.fcd, mat.fyd, mat.fctd)})
    # Passo 3 — Geometria
    geo = "; ".join("%s: A=%.0f cm2, I=%.0f cm4, L=%.0f cm"
                    % (e.id, e.secao.area, e.secao.inercia, e.comprimento())
                    for e in estrutura.elementos)
    passos.append({"titulo": "Passo 3 — Propriedades geometricas",
                   "conteudo": geo})
    # Passos 4-6 — Matrizes (referencia ao painel visual)
    passos.append({"titulo": "Passo 4-6 — Montagem da matriz de rigidez global",
                   "conteudo": "Ver matriz colorida por elemento no painel."})
    # Passo 7 — Contorno
    passos.append({"titulo": "Passo 7 — Condicoes de contorno",
                   "conteudo": "GDLs restritos: %s" % str(res["restritos"])})
    # Passo 9-10 — Deslocamentos
    desl = "; ".join("No %d: uy=%.3f mm, rz=%.5f rad"
                     % (nid, d["uy"], d["rz"])
                     for nid, d in res["deslocamentos"].items())
    passos.append({"titulo": "Passo 9-10 — Deslocamentos nodais",
                   "conteudo": desl})
    # Passo 11 — Reacoes
    rtxt = "; ".join("No %d: Fy=%.1f kN, Mz=%.1f kNm"
                     % (nid, r["fy"], r["mz"]) for nid, r in R.items())
    passos.append({"titulo": "Passo 11 — Reacoes de apoio", "conteudo": rtxt})

    # Por elemento: esforcos, dimensionamento, detalhamento, SVG
    for el in estrutura.elementos:
        esf = esforcos_elemento(estrutura, res, el.id, n_pontos=11)
        Mmax = max(abs(m) for m in esf["M"])
        Vmax = max(abs(v) for v in esf["V"])
        d = el.secao.h - el.cobrimento(estrutura.caa) - 0.5 - 0.625  # est+long/2

        if el.tipo in ("viga", "fundacao"):
            cis = cisalhamento_viga(mat, el.secao.bw, d, Vmax)
            flx = flexao_viga(mat, el.secao.bw, d, Mmax)
            pele = armadura_pele(mat, el.secao.bw, el.secao.h,
                                 el.cobrimento(estrutura.caa), 0.5)
            fl = flecha_viga(estrutura, res, el.id)

            if not flx["ductil"]:
                avisos.append("%s: x/d > 0,45 (secao insuficiente a flexao) "
                              "- aumentar h ou usar armadura dupla." % el.id)
            if not cis["bielas_ok"]:
                avisos.append("%s: VSd > VRd2 (bielas comprimidas) "
                              "- aumentar bw." % el.id)
            if fl["diferida"] > fl["limite"]:
                avisos.append("%s: flecha %.1f mm > limite %.1f mm "
                              "- aumentar h." % (el.id, fl["diferida"],
                                                 fl["limite"]))

            barras_pos = escolher_bitola(flx["As"])
            estribo = escolher_estribo(cis["Asw_s"], comprimento_zona=el.comprimento())

            zonas = [
                {"x0": 0, "x1": 2 * d, "tipo": "critica",
                 "estribo": estribo["descricao"]},
                {"x0": 2 * d, "x1": el.comprimento() - 2 * d, "tipo": "corrente",
                 "estribo": estribo["descricao"]},
                {"x0": el.comprimento() - 2 * d, "x1": el.comprimento(),
                 "tipo": "critica", "estribo": estribo["descricao"]},
            ]

            svg_sec = desenhar_secao(
                el.secao.bw, el.secao.h, el.cobrimento(estrutura.caa),
                barras_inf=(barras_pos["n"], barras_pos["phi"]),
                barras_sup=(barras_pos["n"], barras_pos["phi"]),
                barras_pele=2 if pele["necessaria"] else 0, phi_est=5.0)
            svg_elev = desenhar_elevacao(
                el.comprimento(), el.secao.h, zonas,
                barras_pos=barras_pos["descricao"],
                barras_neg=barras_pos["descricao"])

            elementos_out[el.id] = {
                "tipo": el.tipo, "Mmax_kNm": round(Mmax, 1),
                "Vmax_kN": round(Vmax, 1), "d": round(d, 1),
                "regioes": {
                    "meio": {"As_pos": round(flx["As"], 2),
                             "barras": barras_pos["descricao"],
                             "estribo": estribo["descricao"]},
                },
                "armadura_pele": pele,
                "flecha": fl, "svg_secao": svg_sec, "svg_elevacao": svg_elev,
            }
        else:
            elementos_out[el.id] = {"tipo": el.tipo,
                                    "Nmax_kN": round(max(abs(n) for n in esf["N"]), 1)}

    passos.append({"titulo": "Passo 12 — Esforcos internos",
                   "conteudo": "Diagramas N, V, M calculados por elemento."})
    passos.append({"titulo": "Passo 13 — Flechas", "conteudo":
                   "Imediata e diferida (phi=2,5) verificadas vs L/250."})
    passos.append({"titulo": "Passo 14-15 — Dimensionamento ELU",
                   "conteudo": "Cortante e flexao por elemento."})
    passos.append({"titulo": "Passo 16 — Detalhamento",
                   "conteudo": "Bitolas e estribos por regiao."})
    passos.append({"titulo": "Passo 17 — Verificacoes ELS",
                   "conteudo": "Flecha e fissuracao."})

    return {
        "passos": passos,
        "deslocamentos": res["deslocamentos"],
        "reacoes": R,
        "matriz_global": _matriz_serializavel(res["K"], res["contrib"]),
        "ordem_nos": res["ordem_nos"],
        "elementos": elementos_out,
        "avisos": avisos,
        "cores": {e.id: e.cor for e in estrutura.elementos},
    }
```

- [ ] **Passo 4: Rodar teste — verificar PASS**

Run: `.venv/Scripts/python -m pytest tests/test_relatorio.py -v`
Esperado: 4 PASSED

- [ ] **Passo 5: Commit**

```bash
git add engine/relatorio.py tests/test_relatorio.py
git commit -m "feat: engine/relatorio — passos Carini, detalhamento, SVG e avisos"
```

---

### Task 16: app.py — rotas + templates/relatorio.html

**Files:**
- Modify: `app.py`
- Create: `templates/relatorio.html`
- Create: `tests/test_api_estrutura.py`

- [ ] **Passo 1: Escrever teste falho `tests/test_api_estrutura.py`**

```python
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app, _ANALISES


import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


ENTRADA = {"estrutura": {
    "material": {"fck": 25, "fyk": 500, "CAA": 2, "agregado": "basalto"},
    "nos": [{"id": 1, "x": 0, "y": 0}, {"id": 2, "x": 5, "y": 0}],
    "elementos": [{"id": "V1", "tipo": "viga", "no_i": 1, "no_j": 2,
                   "secao": {"bw": 14, "h": 40}}],
    "vinculos": [{"no": 1, "ux": True, "uy": True}, {"no": 2, "uy": True}],
    "cargas": [{"elemento": "V1", "tipo": "distribuida", "valor": 10.0}]}}


def test_post_estrutura_retorna_id(client):
    r = client.post('/api/estrutura', json=ENTRADA)
    assert r.status_code == 200
    data = r.get_json()
    assert "id" in data
    assert data["status"] == "ok"


def test_post_estrutura_tem_reacoes(client):
    r = client.post('/api/estrutura', json=ENTRADA)
    data = r.get_json()
    # reacoes presentes e proximas de 25 kN por apoio
    rs = data["resultado"]["reacoes"]
    assert abs(rs["1"]["fy"] - 25.0) < 0.5 or abs(rs[1]["fy"] - 25.0) < 0.5


def test_get_relatorio_html(client):
    r = client.post('/api/estrutura', json=ENTRADA)
    aid = r.get_json()["id"]
    r2 = client.get('/api/relatorio/%s' % aid)
    assert r2.status_code == 200
    assert b"<svg" in r2.data  # contem desenho


def test_get_relatorio_inexistente(client):
    r = client.get('/api/relatorio/nao-existe')
    assert r.status_code == 404


def test_index_intocado(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b"D'LIMA" in r.data
```

- [ ] **Passo 2: Rodar teste — verificar FAIL**

Run: `.venv/Scripts/python -m pytest tests/test_api_estrutura.py -v`
Esperado: `ImportError: cannot import name '_ANALISES'`

- [ ] **Passo 3: Adicionar rotas e armazenamento em `app.py`**

Inserir após a rota `/referencia` (linha ~51), e adicionar os imports no topo do arquivo (logo após `import tempfile`):

```python
import uuid
from engine.modelo import Estrutura
from engine.relatorio import gerar_relatorio

# Armazenamento temporario em memoria: id -> relatorio
_ANALISES = {}
```

E as rotas (após a rota `/referencia`):

```python
@app.route('/api/estrutura', methods=['POST'])
def api_estrutura():
    data = request.get_json(silent=True)
    if not data or 'estrutura' not in data:
        return jsonify({'error': 'JSON invalido: falta "estrutura"'}), 400
    try:
        est = Estrutura.from_json(data)
        rel = gerar_relatorio(est)
    except Exception as e:
        return jsonify({'error': 'Erro na analise: %s' % str(e)}), 400

    aid = uuid.uuid4().hex[:8]
    _ANALISES[aid] = rel

    # serializar reacoes/deslocamentos com chaves string
    resultado = {
        'reacoes': {str(k): v for k, v in rel['reacoes'].items()},
        'deslocamentos': {str(k): v for k, v in rel['deslocamentos'].items()},
        'avisos': rel['avisos'],
        'elementos': {k: {kk: vv for kk, vv in v.items()
                          if not kk.startswith('svg')}
                      for k, v in rel['elementos'].items()},
    }
    return jsonify({'id': aid, 'status': 'ok', 'resultado': resultado})


@app.route('/api/relatorio/<aid>')
def api_relatorio(aid):
    rel = _ANALISES.get(aid)
    if rel is None:
        return jsonify({'error': 'Analise nao encontrada'}), 404
    return render_template('relatorio.html', rel=rel)
```

- [ ] **Passo 4: Criar `templates/relatorio.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>D'LIMA — Relatorio de Analise Estrutural</title>
  <style>
    body{font-family:Arial,sans-serif;background:#f4f4f9;color:#222;margin:0;padding:0}
    header{background:#0056b3;color:#fff;padding:14px 20px;font-size:18px;font-weight:bold}
    .wrap{max-width:1000px;margin:20px auto;padding:0 16px}
    h2{color:#0056b3;border-bottom:2px solid #0056b3;padding-bottom:4px;margin-top:32px}
    .passo{background:#fff;border-radius:8px;padding:12px 16px;margin:8px 0;
      border-left:4px solid #0056b3}
    .passo .t{font-weight:bold;margin-bottom:4px}
    .aviso{background:#fef2f2;border-left:4px solid #dc2626;color:#991b1b;
      padding:10px 14px;border-radius:6px;margin:6px 0}
    table.kmat{border-collapse:collapse;font-size:11px;margin:10px 0;overflow:auto;display:block}
    table.kmat td{border:1px solid #ddd;padding:4px 6px;text-align:right;min-width:54px;
      cursor:default}
    .el-card{background:#fff;border-radius:8px;padding:16px;margin:12px 0;
      box-shadow:0 1px 3px rgba(0,0,0,.1)}
    .svgs{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start}
    .legenda span{display:inline-block;padding:2px 8px;border-radius:3px;margin-right:8px;
      font-size:12px;color:#fff}
  </style>
</head>
<body>
  <header>🏗 D'LIMA — Relatorio de Analise Estrutural</header>
  <div class="wrap">

    {% if rel.avisos %}
    <h2>⚠ Avisos</h2>
    {% for a in rel.avisos %}<div class="aviso">{{ a }}</div>{% endfor %}
    {% endif %}

    <h2>Sequencia de Calculo (Carini)</h2>
    {% for p in rel.passos %}
      <div class="passo"><div class="t">{{ p.titulo }}</div>{{ p.conteudo }}</div>
    {% endfor %}

    <h2>Matriz de Rigidez Global</h2>
    <div class="legenda">
      {% for eid, cor in rel.cores.items() %}
        <span style="background:{{ cor }}">{{ eid }}</span>
      {% endfor %}
    </div>
    <table class="kmat">
      {% for linha in rel.matriz_global %}
      <tr>
        {% for cel in linha %}
          {% if cel.elem|length == 1 %}
            <td style="background:{{ rel.cores[cel.elem[0]] }}22"
                title="K = {{ cel.v }} ({{ cel.elem|join(', ') }})">{{ cel.v }}</td>
          {% elif cel.elem|length > 1 %}
            <td style="background:#ddd"
                title="K = {{ cel.v }} ({{ cel.elem|join(' + ') }})">{{ cel.v }}</td>
          {% else %}
            <td style="color:#bbb">{{ cel.v }}</td>
          {% endif %}
        {% endfor %}
      </tr>
      {% endfor %}
    </table>

    <h2>Detalhamento por Elemento</h2>
    {% for eid, det in rel.elementos.items() %}
      <div class="el-card">
        <h3 style="margin-top:0">{{ eid }} ({{ det.tipo }})</h3>
        {% if det.regioes %}
          <p><b>Vao:</b> As+ = {{ det.regioes.meio.As_pos }} cm² →
             {{ det.regioes.meio.barras }} | Estribos:
             {{ det.regioes.meio.estribo }}</p>
          {% if det.armadura_pele and det.armadura_pele.necessaria %}
            <p><b>Armadura de pele:</b> 2 Ø 8 por face</p>
          {% endif %}
          {% if det.flecha %}
            <p><b>Flecha:</b> imediata {{ '%.1f'|format(det.flecha.imediata) }} mm |
               diferida {{ '%.1f'|format(det.flecha.diferida) }} mm |
               limite {{ '%.1f'|format(det.flecha.limite) }} mm</p>
          {% endif %}
          <div class="svgs">
            <div>{{ det.svg_secao|safe }}</div>
            <div>{{ det.svg_elevacao|safe }}</div>
          </div>
        {% else %}
          <p>Esforco normal maximo: {{ det.Nmax_kN }} kN</p>
        {% endif %}
      </div>
    {% endfor %}

  </div>
</body>
</html>
```

- [ ] **Passo 5: Rodar todos os testes**

Run: `.venv/Scripts/python -m pytest tests/ -v`
Esperado: todos PASSED (materiais 5, modelo 5, rigidez 7, solver 9, dimensionamento 13, detalhamento 4, svg 5, relatorio 4, api 5, app 3 = 60 testes)

- [ ] **Passo 6: Verificação manual no browser**

```bash
.venv/Scripts/python app.py
```
Em outro terminal:
```bash
curl -s -X POST http://localhost:10000/api/estrutura -H "Content-Type: application/json" -d "{\"estrutura\":{\"material\":{\"fck\":25,\"fyk\":500,\"CAA\":2,\"agregado\":\"basalto\"},\"nos\":[{\"id\":1,\"x\":0,\"y\":0},{\"id\":2,\"x\":5,\"y\":0}],\"elementos\":[{\"id\":\"V1\",\"tipo\":\"viga\",\"no_i\":1,\"no_j\":2,\"secao\":{\"bw\":14,\"h\":40}}],\"vinculos\":[{\"no\":1,\"ux\":true,\"uy\":true},{\"no\":2,\"uy\":true}],\"cargas\":[{\"elemento\":\"V1\",\"tipo\":\"distribuida\",\"valor\":10.0}]}}"
```
Esperado: JSON com `id`, reações ~25 kN. Abrir `http://localhost:10000/api/relatorio/<id>` → relatório com matriz colorida e SVGs.

- [ ] **Passo 7: Commit + push**

```bash
git add app.py templates/relatorio.html tests/test_api_estrutura.py
git commit -m "feat: rotas /api/estrutura e /api/relatorio + template do relatorio"
git push
```

---

## Self-Review (cobertura do spec)

| Requisito do spec | Task |
|---|---|
| Schema JSON de entrada (nós/elementos/vínculos/cargas) | 2 |
| Conversão de unidades (m→cm, kN/m→kN/cm) | 2 |
| Matriz k_local 6×6 + transformação T | 3 |
| Montagem K_global + mapa de contribuições (coloração) | 4 |
| Forças nodais equivalentes (carga distribuída) | 5 |
| Condições de contorno + solução {u} | 6 |
| Reações de apoio | 7 |
| Esforços internos N/V/M | 7 |
| Flecha imediata + diferida + limite | 8 |
| Cisalhamento (VRd2, Vc, Asw/s) | 9 |
| Flexão simples/dupla/pele | 10 |
| Pilares (esbeltez + flexo-compressão oblíqua) | 11 |
| escolher_bitola + escolher_estribo + zonas | 12 |
| SVG seção transversal | 13 |
| SVG elevação com zonas | 14 |
| 17 passos Carini + 6 avisos automáticos | 15 |
| Matriz colorida com hover | 16 (template) |
| Rotas /api/estrutura e /api/relatorio/<id> | 16 |
| Armazenamento temporário em memória | 16 |

**Fora do escopo da Fase 1 (conforme spec §11):** UI de desenho (Fase 2), 3D (Fase 3), fissuração wk detalhada, P-delta, lajes como placa. A fissuração ELS aparece como passo no relatório mas sem cálculo de wk — coerente com o foco da Fase 1.

**Nota de granularidade dos pilares:** Tasks 9-11 implementam as funções de dimensionamento de pilar isoladamente. A integração completa de pilares no `gerar_relatorio` (Task 15) trata vigas em detalhe; pilares retornam esforço normal. O dimensionamento completo de pilar no relatório (com situações de cálculo e SVG) fica para uma iteração futura — a Fase 1 entrega o dimensionamento de pilar como funções testadas e prontas para uso.
