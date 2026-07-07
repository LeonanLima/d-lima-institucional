# Módulo Quantitativo — Fase 1 (Motor de Cálculo) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Motor de cálculo de quantitativo de materiais (alvenaria, revestimentos, concreto armado, pisos, pintura, esquadrias) com entrada manual de medidas, lista de compra consolidada, cronograma executivo e export Excel estilo SINAPI.

**Architecture:** Pacote Python puro (`quantitativo`) com dataclasses imutáveis de domínio, serviços de quantificação por tipo (funções puras que recebem modelos + parâmetros e devolvem `ItemServico`), consolidação em lista de compra, cronograma por produtividades e saída xlsx/CLI. Na Fase 2+ este pacote vira o backend FastAPI do módulo do ERP D'LIMA.

**Tech Stack:** Python 3.11+, pytest, PyYAML, openpyxl. Sem framework web nesta fase.

**Spec:** `d-lima-institucional/docs/superpowers/specs/2026-07-07-modulo-quantitativo-planta-design.md`

## Global Constraints

- Repo alvo: `C:\Users\leona\dlima-quantitativo` (novo, FORA do OneDrive). Todos os comandos rodam a partir dessa pasta.
- Python >= 3.11; dependências de runtime somente `pyyaml>=6.0` e `openpyxl>=3.1`; dev somente `pytest>=8.0`.
- Imutabilidade: todas as dataclasses de domínio são `frozen=True`; funções nunca mutam entradas, sempre retornam valores novos.
- Nomes de domínio em português (`Parede`, `quantificar_alvenaria`); unidades no nome do campo (`comprimento_m`, `esp_chapisco_m`, `cimento_kg_m3`).
- Valores de traço, consumo e produtividade são SEMENTES da literatura (ABCP/TCPO/SINAPI) e levam o comentário `# SEED: validar com Leonan` — os testes golden travam esses valores; mudá-los depois exige atualizar o teste junto (decisão de engenharia do Leonan).
- Medida nunca vem de IA (constraint da spec — nesta fase nem há IA).
- Commit após cada task, formato `<type>: <descrição>` (feat/test/docs/chore), sem linha de atribuição.
- TDD: teste primeiro, ver falhar, implementar mínimo, ver passar, commit.

---

### Task 1: Scaffold do repo + modelos de domínio

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `src/quantitativo/__init__.py`
- Create: `src/quantitativo/modelos.py`
- Create: `src/quantitativo/resultados.py`
- Test: `tests/test_modelos.py`

**Interfaces:**
- Consumes: nada (primeira task)
- Produces: dataclasses `Abertura(tipo, largura_m, altura_m, quantidade)`, `Parede(nome, comprimento_m, pe_direito_m, aberturas, faces_internas, face_externa)` com `.area_bruta_m2`/`.area_liquida_m2`, `Ambiente(nome, area_m2)`, `Armadura(bitola_mm, quantidade_barras, comprimento_barra_m)`, `ElementoConcreto(nome, tipo, largura_m, altura_m, comprimento_m, armaduras)` com `.volume_m3`, `Pavimento(nome, paredes, ambientes, elementos_concreto)`, `Obra(nome, pavimentos)` com propriedades agregadoras `paredes`/`ambientes`/`elementos_concreto`; parâmetros `ParametrosAlvenaria(bloco, junta_m, perda)`, `ParametrosRevestimento(esp_chapisco_m, esp_emboco_m, esp_reboco_m, perda)`, `ParametrosConcreto(fck_mpa, perda)`, `ParametrosPiso(esp_contrapiso_m, perda_ceramica)`, `ParametrosPintura(demaos, rendimento_tinta_m2_por_l)`, `ParametrosObra(alvenaria, revestimento, concreto, piso, pintura)`; e `ItemServico(tipo, descricao, unidade, quantidade, insumos)` em `resultados.py`.

- [ ] **Step 1: Criar repo e estrutura**

```bash
mkdir C:\Users\leona\dlima-quantitativo
cd C:\Users\leona\dlima-quantitativo
git init -b main
mkdir -p src/quantitativo tests exemplos
```

`pyproject.toml`:

```toml
[project]
name = "dlima-quantitativo"
version = "0.1.0"
description = "Motor de quantitativo de materiais - Modulo Quantitativo ERP D'LIMA (Fase 1)"
requires-python = ">=3.11"
dependencies = ["pyyaml>=6.0", "openpyxl>=3.1"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

`.gitignore`:

```
__pycache__/
*.pyc
.pytest_cache/
*.xlsx
.venv/
```

`src/quantitativo/__init__.py`:

```python
"""Motor de quantitativo de materiais - Fase 1 do Modulo Quantitativo D'LIMA."""
```

Instalar dependências de dev:

```bash
pip install pyyaml openpyxl pytest
```

- [ ] **Step 2: Escrever teste que falha**

`tests/test_modelos.py`:

```python
import pytest

from quantitativo.modelos import (
    Abertura, Ambiente, Armadura, ElementoConcreto, Obra, Parede, Pavimento,
)


def test_area_liquida_de_parede_desconta_aberturas():
    parede = Parede(
        nome="P1", comprimento_m=10.0, pe_direito_m=2.8,
        aberturas=(
            Abertura(tipo="porta", largura_m=0.8, altura_m=2.1),
            Abertura(tipo="janela", largura_m=1.2, altura_m=1.0),
        ),
    )
    assert parede.area_bruta_m2 == pytest.approx(28.0)
    assert parede.area_liquida_m2 == pytest.approx(25.12)


def test_area_liquida_nunca_fica_negativa():
    parede = Parede(
        nome="P2", comprimento_m=1.0, pe_direito_m=1.0,
        aberturas=(Abertura(tipo="janela", largura_m=2.0, altura_m=2.0),),
    )
    assert parede.area_liquida_m2 == 0.0


def test_volume_de_elemento_concreto():
    viga = ElementoConcreto(
        nome="V1", tipo="viga", largura_m=0.14, altura_m=0.40, comprimento_m=5.0,
        armaduras=(Armadura(bitola_mm=10.0, quantidade_barras=4, comprimento_barra_m=5.6),),
    )
    assert viga.volume_m3 == pytest.approx(0.28)


def test_obra_agrega_pavimentos():
    terreo = Pavimento(
        nome="Terreo",
        paredes=(Parede(nome="P1", comprimento_m=5.0, pe_direito_m=2.8),),
        ambientes=(Ambiente(nome="Sala", area_m2=20.0),),
    )
    superior = Pavimento(
        nome="Superior",
        paredes=(Parede(nome="P10", comprimento_m=4.0, pe_direito_m=2.6),),
    )
    obra = Obra(nome="Casa", pavimentos=(terreo, superior))
    assert [p.nome for p in obra.paredes] == ["P1", "P10"]
    assert [a.nome for a in obra.ambientes] == ["Sala"]
    assert obra.elementos_concreto == ()
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `python -m pytest tests/test_modelos.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'quantitativo.modelos'`

- [ ] **Step 4: Implementar modelos**

`src/quantitativo/modelos.py`:

```python
"""Modelos de dominio para entrada manual de medidas (Fase 1)."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Abertura:
    tipo: str  # "porta" | "janela"
    largura_m: float
    altura_m: float
    quantidade: int = 1

    @property
    def area_m2(self) -> float:
        return self.largura_m * self.altura_m * self.quantidade


@dataclass(frozen=True)
class Parede:
    nome: str
    comprimento_m: float
    pe_direito_m: float
    aberturas: tuple[Abertura, ...] = ()
    faces_internas: int = 2      # faces que recebem revestimento interno
    face_externa: bool = False   # True se uma das faces recebe revestimento externo

    @property
    def area_bruta_m2(self) -> float:
        return self.comprimento_m * self.pe_direito_m

    @property
    def area_liquida_m2(self) -> float:
        area = self.area_bruta_m2 - sum(a.area_m2 for a in self.aberturas)
        return max(area, 0.0)

    @property
    def faces_revestidas(self) -> int:
        return self.faces_internas + (1 if self.face_externa else 0)


@dataclass(frozen=True)
class Ambiente:
    nome: str
    area_m2: float


@dataclass(frozen=True)
class Armadura:
    bitola_mm: float
    quantidade_barras: int
    comprimento_barra_m: float


@dataclass(frozen=True)
class ElementoConcreto:
    nome: str
    tipo: str  # "viga" | "pilar" | "laje"
    largura_m: float     # laje: largura do pano
    altura_m: float      # laje: espessura
    comprimento_m: float
    armaduras: tuple[Armadura, ...] = ()

    @property
    def volume_m3(self) -> float:
        return self.largura_m * self.altura_m * self.comprimento_m


@dataclass(frozen=True)
class Pavimento:
    nome: str
    paredes: tuple[Parede, ...] = ()
    ambientes: tuple[Ambiente, ...] = ()
    elementos_concreto: tuple[ElementoConcreto, ...] = ()


@dataclass(frozen=True)
class Obra:
    nome: str
    pavimentos: tuple[Pavimento, ...]

    @property
    def paredes(self) -> tuple[Parede, ...]:
        return tuple(p for pav in self.pavimentos for p in pav.paredes)

    @property
    def ambientes(self) -> tuple[Ambiente, ...]:
        return tuple(a for pav in self.pavimentos for a in pav.ambientes)

    @property
    def elementos_concreto(self) -> tuple[ElementoConcreto, ...]:
        return tuple(e for pav in self.pavimentos for e in pav.elementos_concreto)


@dataclass(frozen=True)
class ParametrosAlvenaria:
    bloco: str           # chave do catalogo de blocos
    junta_m: float = 0.01
    perda: float = 0.10


@dataclass(frozen=True)
class ParametrosRevestimento:
    esp_chapisco_m: float = 0.005
    esp_emboco_m: float = 0.020
    esp_reboco_m: float = 0.005
    perda: float = 0.10


@dataclass(frozen=True)
class ParametrosConcreto:
    fck_mpa: int = 25    # 20 | 25 | 30
    perda: float = 0.05


@dataclass(frozen=True)
class ParametrosPiso:
    esp_contrapiso_m: float = 0.03
    perda_ceramica: float = 0.10


@dataclass(frozen=True)
class ParametrosPintura:
    demaos: int = 2
    rendimento_tinta_m2_por_l: float = 10.0  # por demao


@dataclass(frozen=True)
class ParametrosObra:
    alvenaria: ParametrosAlvenaria
    revestimento: ParametrosRevestimento = field(default_factory=ParametrosRevestimento)
    concreto: ParametrosConcreto = field(default_factory=ParametrosConcreto)
    piso: ParametrosPiso = field(default_factory=ParametrosPiso)
    pintura: ParametrosPintura = field(default_factory=ParametrosPintura)
```

`src/quantitativo/resultados.py`:

```python
"""Resultado padrao de cada servico quantificado."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ItemServico:
    tipo: str                 # slug: "alvenaria", "chapisco", "concreto"...
    descricao: str            # "Alvenaria tijolo ceramico 9x19x19, junta 1.0 cm"
    unidade: str              # "m2" | "m3" | "un"
    quantidade: float
    insumos: dict[str, float]  # codigo do insumo -> quantidade (kg, m3, un, L)
```

- [ ] **Step 5: Rodar e ver passar**

Run: `python -m pytest tests/test_modelos.py -v`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: scaffold do pacote + modelos de dominio e parametros"
```

---

### Task 2: Catálogo de blocos + fórmulas de alvenaria

**Files:**
- Create: `src/quantitativo/catalogo/__init__.py`
- Create: `src/quantitativo/catalogo/blocos.py`
- Test: `tests/test_blocos.py`

**Interfaces:**
- Consumes: nada
- Produces: `Bloco(codigo, descricao, comprimento_m, altura_m, espessura_m)`; dict `CATALOGO_BLOCOS: dict[str, Bloco]` (chaves: `tijolo_9x19x19`, `tijolo_115x19x24`, `bloco_concreto_9x19x39`, `bloco_concreto_14x19x39`, `lajota_9x19x29`); `blocos_por_m2(bloco: Bloco, junta_m: float) -> float`; `argamassa_assentamento_m3_por_m2(bloco: Bloco, junta_m: float) -> float`.

Fórmulas (determinísticas, geometria pura):
- `blocos_por_m2 = 1 / ((L + j) * (H + j))` onde L/H são as dimensões do bloco na face da parede e j a junta.
- `argamassa/m² = espessura_da_parede * (1 - n * L * H)` — volume não ocupado pelos blocos em 1 m² de parede, preenchido pela junta em toda a espessura.

- [ ] **Step 1: Escrever teste que falha**

`tests/test_blocos.py`:

```python
import pytest

from quantitativo.catalogo.blocos import (
    CATALOGO_BLOCOS, argamassa_assentamento_m3_por_m2, blocos_por_m2,
)


def test_tijolo_9x19x19_junta_1cm_da_25_blocos_por_m2():
    tijolo = CATALOGO_BLOCOS["tijolo_9x19x19"]
    assert blocos_por_m2(tijolo, junta_m=0.01) == pytest.approx(25.0)


def test_bloco_concreto_14_junta_1cm_da_12_5_por_m2():
    bloco = CATALOGO_BLOCOS["bloco_concreto_14x19x39"]
    assert blocos_por_m2(bloco, junta_m=0.01) == pytest.approx(12.5)


def test_argamassa_assentamento_tijolo_9_junta_1cm():
    tijolo = CATALOGO_BLOCOS["tijolo_9x19x19"]
    # 0.09 * (1 - 25 * 0.19 * 0.19) = 0.09 * 0.0975 = 0.008775 m3/m2 (~8.8 L/m2)
    assert argamassa_assentamento_m3_por_m2(tijolo, junta_m=0.01) == pytest.approx(0.008775)


def test_junta_maior_consome_mais_argamassa_e_menos_blocos():
    tijolo = CATALOGO_BLOCOS["tijolo_9x19x19"]
    assert blocos_por_m2(tijolo, 0.015) < blocos_por_m2(tijolo, 0.01)
    assert argamassa_assentamento_m3_por_m2(tijolo, 0.015) > argamassa_assentamento_m3_por_m2(tijolo, 0.01)


def test_catalogo_tem_os_5_blocos_da_spec():
    assert set(CATALOGO_BLOCOS) == {
        "tijolo_9x19x19", "tijolo_115x19x24", "bloco_concreto_9x19x39",
        "bloco_concreto_14x19x39", "lajota_9x19x29",
    }
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_blocos.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/catalogo/__init__.py` (vazio) e `src/quantitativo/catalogo/blocos.py`:

```python
"""Catalogo de blocos/tijolos e formulas geometricas de alvenaria."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Bloco:
    codigo: str
    descricao: str
    comprimento_m: float  # dimensao horizontal na face da parede
    altura_m: float       # dimensao vertical na face da parede
    espessura_m: float    # espessura resultante da parede (assentamento meia-vez)


CATALOGO_BLOCOS: dict[str, Bloco] = {
    "tijolo_9x19x19": Bloco("tijolo_9x19x19", "Tijolo ceramico furado 9x19x19 cm", 0.19, 0.19, 0.09),
    "tijolo_115x19x24": Bloco("tijolo_115x19x24", "Tijolo ceramico furado 11,5x19x24 cm", 0.24, 0.19, 0.115),
    "bloco_concreto_9x19x39": Bloco("bloco_concreto_9x19x39", "Bloco de concreto 9x19x39 cm", 0.39, 0.19, 0.09),
    "bloco_concreto_14x19x39": Bloco("bloco_concreto_14x19x39", "Bloco de concreto 14x19x39 cm", 0.39, 0.19, 0.14),
    "lajota_9x19x29": Bloco("lajota_9x19x29", "Lajota ceramica 9x19x29 cm", 0.29, 0.19, 0.09),
}


def blocos_por_m2(bloco: Bloco, junta_m: float) -> float:
    return 1.0 / ((bloco.comprimento_m + junta_m) * (bloco.altura_m + junta_m))


def argamassa_assentamento_m3_por_m2(bloco: Bloco, junta_m: float) -> float:
    n = blocos_por_m2(bloco, junta_m)
    fracao_ocupada_por_blocos = n * bloco.comprimento_m * bloco.altura_m
    return bloco.espessura_m * (1.0 - fracao_ocupada_por_blocos)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_blocos.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/catalogo tests/test_blocos.py
git commit -m "feat: catalogo de blocos e formulas de blocos/m2 e argamassa de assentamento"
```

---

### Task 3: Traços de argamassa e conversão volume → insumos

**Files:**
- Create: `src/quantitativo/catalogo/tracos.py`
- Test: `tests/test_tracos.py`

**Interfaces:**
- Consumes: nada
- Produces: `TracoArgamassa(nome, cimento_kg_m3, cal_kg_m3, areia_m3_m3)`; dict `TRACOS_ARGAMASSA: dict[str, TracoArgamassa]` (chaves `"1:3"`, `"1:4"`, `"1:2:8"`, `"1:2:9"`); `insumos_argamassa(volume_m3: float, traco: str) -> dict[str, float]` retornando chaves `"cimento_kg"`, `"cal_kg"`, `"areia_m3"` (cal omitida quando zero).

- [ ] **Step 1: Escrever teste que falha**

`tests/test_tracos.py`:

```python
import pytest

from quantitativo.catalogo.tracos import TRACOS_ARGAMASSA, insumos_argamassa


def test_insumos_de_1m3_de_argamassa_1_2_8():
    insumos = insumos_argamassa(1.0, "1:2:8")
    assert insumos["cimento_kg"] == pytest.approx(130.0)
    assert insumos["cal_kg"] == pytest.approx(130.0)
    assert insumos["areia_m3"] == pytest.approx(1.05)


def test_traco_1_3_nao_tem_cal():
    insumos = insumos_argamassa(2.0, "1:3")
    assert insumos["cimento_kg"] == pytest.approx(920.0)
    assert "cal_kg" not in insumos
    assert insumos["areia_m3"] == pytest.approx(2.18)


def test_traco_desconhecido_levanta_erro():
    with pytest.raises(KeyError):
        insumos_argamassa(1.0, "1:99")


def test_tabela_tem_os_4_tracos():
    assert set(TRACOS_ARGAMASSA) == {"1:3", "1:4", "1:2:8", "1:2:9"}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_tracos.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/catalogo/tracos.py`:

```python
"""Tracos de argamassa com consumos por m3 (referencias TCPO/ABCP).

SEED: validar com Leonan — valores de consumo por m3 sao sementes da
literatura; ao ajustar, atualizar tambem os testes golden.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TracoArgamassa:
    nome: str
    cimento_kg_m3: float
    cal_kg_m3: float
    areia_m3_m3: float


TRACOS_ARGAMASSA: dict[str, TracoArgamassa] = {
    "1:3": TracoArgamassa("1:3 cimento/areia (chapisco)", 460.0, 0.0, 1.09),
    "1:4": TracoArgamassa("1:4 cimento/areia (contrapiso)", 365.0, 0.0, 1.08),
    "1:2:8": TracoArgamassa("1:2:8 cimento/cal/areia (assentamento e emboco)", 130.0, 130.0, 1.05),
    "1:2:9": TracoArgamassa("1:2:9 cimento/cal/areia (reboco)", 112.0, 112.0, 1.06),
}


def insumos_argamassa(volume_m3: float, traco: str) -> dict[str, float]:
    t = TRACOS_ARGAMASSA[traco]
    insumos = {
        "cimento_kg": volume_m3 * t.cimento_kg_m3,
        "areia_m3": volume_m3 * t.areia_m3_m3,
    }
    if t.cal_kg_m3 > 0:
        insumos["cal_kg"] = volume_m3 * t.cal_kg_m3
    return insumos
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_tracos.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/catalogo/tracos.py tests/test_tracos.py
git commit -m "feat: tracos de argamassa com consumos seed e conversao volume->insumos"
```

---

### Task 4: Serviço de alvenaria

**Files:**
- Create: `src/quantitativo/servicos/__init__.py`
- Create: `src/quantitativo/servicos/alvenaria.py`
- Test: `tests/test_alvenaria.py`

**Interfaces:**
- Consumes: `Parede`, `ParametrosAlvenaria` (Task 1); `CATALOGO_BLOCOS`, `blocos_por_m2`, `argamassa_assentamento_m3_por_m2` (Task 2); `insumos_argamassa` (Task 3); `ItemServico` (Task 1)
- Produces: `quantificar_alvenaria(paredes: tuple[Parede, ...], params: ParametrosAlvenaria) -> ItemServico` — `tipo="alvenaria"`, `unidade="m2"`, `quantidade=` área líquida total; insumos: `"bloco:<codigo>"` (un, arredondado p/ cima), `"cimento_kg"`, `"cal_kg"`, `"areia_m3"`. Argamassa de assentamento usa traço `"1:2:8"`.

- [ ] **Step 1: Escrever teste que falha**

`tests/test_alvenaria.py`:

```python
import pytest

from quantitativo.modelos import Abertura, Parede, ParametrosAlvenaria
from quantitativo.servicos.alvenaria import quantificar_alvenaria

PAREDE_10M = Parede(
    nome="P1", comprimento_m=10.0, pe_direito_m=2.8,
    aberturas=(
        Abertura(tipo="porta", largura_m=0.8, altura_m=2.1),
        Abertura(tipo="janela", largura_m=1.2, altura_m=1.0),
    ),
)


def test_alvenaria_tijolo_9_com_perda_10pct():
    params = ParametrosAlvenaria(bloco="tijolo_9x19x19", junta_m=0.01, perda=0.10)
    item = quantificar_alvenaria((PAREDE_10M,), params)

    assert item.tipo == "alvenaria"
    assert item.unidade == "m2"
    assert item.quantidade == pytest.approx(25.12)
    # 25.12 m2 * 25 blocos/m2 * 1.10 = 690.8 -> 691
    assert item.insumos["bloco:tijolo_9x19x19"] == 691
    # argamassa: 25.12 * 0.008775 * 1.10 = 0.2424715 m3 -> traco 1:2:8
    assert item.insumos["cimento_kg"] == pytest.approx(0.2424715 * 130.0, rel=1e-4)
    assert item.insumos["cal_kg"] == pytest.approx(0.2424715 * 130.0, rel=1e-4)
    assert item.insumos["areia_m3"] == pytest.approx(0.2424715 * 1.05, rel=1e-4)


def test_alvenaria_soma_varias_paredes():
    p2 = Parede(nome="P2", comprimento_m=5.0, pe_direito_m=2.8)
    params = ParametrosAlvenaria(bloco="tijolo_9x19x19")
    item = quantificar_alvenaria((PAREDE_10M, p2), params)
    assert item.quantidade == pytest.approx(25.12 + 14.0)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_alvenaria.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/servicos/__init__.py` (vazio) e `src/quantitativo/servicos/alvenaria.py`:

```python
"""Quantificacao de alvenaria: blocos + argamassa de assentamento."""
import math

from quantitativo.catalogo.blocos import (
    CATALOGO_BLOCOS, argamassa_assentamento_m3_por_m2, blocos_por_m2,
)
from quantitativo.catalogo.tracos import insumos_argamassa
from quantitativo.modelos import Parede, ParametrosAlvenaria
from quantitativo.resultados import ItemServico

TRACO_ASSENTAMENTO = "1:2:8"


def quantificar_alvenaria(
    paredes: tuple[Parede, ...], params: ParametrosAlvenaria
) -> ItemServico:
    bloco = CATALOGO_BLOCOS[params.bloco]
    area_m2 = sum(p.area_liquida_m2 for p in paredes)
    fator_perda = 1.0 + params.perda

    n_blocos = math.ceil(area_m2 * blocos_por_m2(bloco, params.junta_m) * fator_perda)
    volume_argamassa = (
        area_m2 * argamassa_assentamento_m3_por_m2(bloco, params.junta_m) * fator_perda
    )

    insumos = {f"bloco:{bloco.codigo}": float(n_blocos)}
    insumos.update(insumos_argamassa(volume_argamassa, TRACO_ASSENTAMENTO))

    return ItemServico(
        tipo="alvenaria",
        descricao=f"Alvenaria {bloco.descricao}, junta {params.junta_m * 100:.1f} cm",
        unidade="m2",
        quantidade=area_m2,
        insumos=insumos,
    )
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_alvenaria.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/servicos tests/test_alvenaria.py
git commit -m "feat: servico de alvenaria (blocos + argamassa de assentamento com perdas)"
```

---

### Task 5: Serviço de revestimento (chapisco, emboço, reboco)

**Files:**
- Create: `src/quantitativo/servicos/revestimento.py`
- Test: `tests/test_revestimento.py`

**Interfaces:**
- Consumes: `Parede.faces_revestidas`/`area_liquida_m2`, `ParametrosRevestimento`, `insumos_argamassa`, `ItemServico`
- Produces: `quantificar_revestimentos(paredes: tuple[Parede, ...], params: ParametrosRevestimento) -> list[ItemServico]` — devolve exatamente 3 itens, tipos `"chapisco"` (traço `"1:3"`), `"emboco"` (`"1:2:8"`), `"reboco"` (`"1:2:9"`); `quantidade` de cada = área revestida total (área líquida × faces revestidas), insumos pelo volume = área × espessura × (1+perda).

- [ ] **Step 1: Escrever teste que falha**

`tests/test_revestimento.py`:

```python
import pytest

from quantitativo.modelos import Abertura, Parede, ParametrosRevestimento
from quantitativo.servicos.revestimento import quantificar_revestimentos

# Parede com 1 face interna + 1 face externa = 2 faces revestidas, 25.12 m2 liquidos
PAREDE = Parede(
    nome="P1", comprimento_m=10.0, pe_direito_m=2.8,
    aberturas=(
        Abertura(tipo="porta", largura_m=0.8, altura_m=2.1),
        Abertura(tipo="janela", largura_m=1.2, altura_m=1.0),
    ),
    faces_internas=1, face_externa=True,
)
AREA_REVESTIDA = 25.12 * 2  # 50.24 m2


def test_gera_tres_camadas_com_areas_iguais():
    itens = quantificar_revestimentos((PAREDE,), ParametrosRevestimento())
    assert [i.tipo for i in itens] == ["chapisco", "emboco", "reboco"]
    for item in itens:
        assert item.unidade == "m2"
        assert item.quantidade == pytest.approx(AREA_REVESTIDA)


def test_insumos_do_chapisco_traco_1_3():
    itens = quantificar_revestimentos((PAREDE,), ParametrosRevestimento(perda=0.10))
    chapisco = itens[0]
    volume = AREA_REVESTIDA * 0.005 * 1.10  # 0.27632 m3
    assert chapisco.insumos["cimento_kg"] == pytest.approx(volume * 460.0, rel=1e-4)
    assert chapisco.insumos["areia_m3"] == pytest.approx(volume * 1.09, rel=1e-4)
    assert "cal_kg" not in chapisco.insumos


def test_emboco_e_o_maior_volume():
    itens = quantificar_revestimentos((PAREDE,), ParametrosRevestimento())
    emboco = itens[1]
    volume = AREA_REVESTIDA * 0.020 * 1.10
    assert emboco.insumos["cimento_kg"] == pytest.approx(volume * 130.0, rel=1e-4)
    assert emboco.insumos["cal_kg"] == pytest.approx(volume * 130.0, rel=1e-4)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_revestimento.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/servicos/revestimento.py`:

```python
"""Quantificacao de chapisco, emboco e reboco por face revestida."""
from quantitativo.catalogo.tracos import insumos_argamassa
from quantitativo.modelos import Parede, ParametrosRevestimento
from quantitativo.resultados import ItemServico

CAMADAS = (
    ("chapisco", "Chapisco", "1:3"),
    ("emboco", "Emboco", "1:2:8"),
    ("reboco", "Reboco", "1:2:9"),
)


def quantificar_revestimentos(
    paredes: tuple[Parede, ...], params: ParametrosRevestimento
) -> list[ItemServico]:
    area_m2 = sum(p.area_liquida_m2 * p.faces_revestidas for p in paredes)
    espessuras = {
        "chapisco": params.esp_chapisco_m,
        "emboco": params.esp_emboco_m,
        "reboco": params.esp_reboco_m,
    }
    fator_perda = 1.0 + params.perda

    itens = []
    for tipo, nome, traco in CAMADAS:
        espessura = espessuras[tipo]
        volume = area_m2 * espessura * fator_perda
        itens.append(
            ItemServico(
                tipo=tipo,
                descricao=f"{nome} traco {traco}, esp. {espessura * 1000:.0f} mm",
                unidade="m2",
                quantidade=area_m2,
                insumos=insumos_argamassa(volume, traco),
            )
        )
    return itens
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_revestimento.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/servicos/revestimento.py tests/test_revestimento.py
git commit -m "feat: servico de revestimento com chapisco, emboco e reboco por face"
```

---

### Task 6: Concreto armado (traço por fck + aço por bitola)

**Files:**
- Create: `src/quantitativo/catalogo/concreto.py`
- Create: `src/quantitativo/servicos/concreto.py`
- Test: `tests/test_concreto.py`

**Interfaces:**
- Consumes: `ElementoConcreto`, `Armadura`, `ParametrosConcreto`, `ItemServico`
- Produces: em `catalogo/concreto.py`: `TracoConcreto(fck_mpa, cimento_kg_m3, areia_m3_m3, brita_m3_m3, agua_l_m3)`, `TRACOS_CONCRETO: dict[int, TracoConcreto]` (20, 25, 30), `MASSA_ACO_KG_M: dict[float, float]` (bitolas NBR 7480: 5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0), `PERDA_ACO = 0.10`; em `servicos/concreto.py`: `quantificar_concreto(elementos: tuple[ElementoConcreto, ...], params: ParametrosConcreto) -> ItemServico` — `tipo="concreto"`, `unidade="m3"`, insumos `"cimento_kg"`, `"areia_m3"`, `"brita_m3"`, `"agua_l"` e `"aco_<bitola>mm_kg"` por bitola usada.

- [ ] **Step 1: Escrever teste que falha**

`tests/test_concreto.py`:

```python
import pytest

from quantitativo.modelos import Armadura, ElementoConcreto, ParametrosConcreto
from quantitativo.servicos.concreto import quantificar_concreto

VIGA = ElementoConcreto(
    nome="V1", tipo="viga", largura_m=0.14, altura_m=0.40, comprimento_m=5.0,
    armaduras=(Armadura(bitola_mm=10.0, quantidade_barras=4, comprimento_barra_m=5.6),),
)
PILAR = ElementoConcreto(
    nome="P1", tipo="pilar", largura_m=0.14, altura_m=0.30, comprimento_m=2.8,
    armaduras=(Armadura(bitola_mm=8.0, quantidade_barras=4, comprimento_barra_m=3.2),),
)
LAJE = ElementoConcreto(nome="L1", tipo="laje", largura_m=4.0, altura_m=0.10, comprimento_m=5.0)


def test_volume_com_perda_e_traco_fck25():
    item = quantificar_concreto((VIGA, PILAR, LAJE), ParametrosConcreto(fck_mpa=25, perda=0.05))
    volume = (0.28 + 0.1176 + 2.0) * 1.05  # 2.517480 m3
    assert item.tipo == "concreto"
    assert item.unidade == "m3"
    assert item.quantidade == pytest.approx(volume, rel=1e-6)
    assert item.insumos["cimento_kg"] == pytest.approx(volume * 350.0, rel=1e-4)
    assert item.insumos["areia_m3"] == pytest.approx(volume * 0.82, rel=1e-4)
    assert item.insumos["brita_m3"] == pytest.approx(volume * 0.83, rel=1e-4)
    assert item.insumos["agua_l"] == pytest.approx(volume * 185.0, rel=1e-4)


def test_aco_por_bitola_com_perda_10pct():
    item = quantificar_concreto((VIGA, PILAR), ParametrosConcreto(fck_mpa=25))
    # V1: 0.617 kg/m * 4 * 5.6 = 13.8208 kg -> *1.10 = 15.20288
    assert item.insumos["aco_10.0mm_kg"] == pytest.approx(15.20288, rel=1e-5)
    # P1: 0.395 * 4 * 3.2 = 5.056 -> *1.10 = 5.5616
    assert item.insumos["aco_8.0mm_kg"] == pytest.approx(5.5616, rel=1e-5)


def test_fck_sem_traco_cadastrado_levanta_erro():
    with pytest.raises(KeyError):
        quantificar_concreto((VIGA,), ParametrosConcreto(fck_mpa=40))
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_concreto.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/catalogo/concreto.py`:

```python
"""Tracos de concreto por fck (metodo ABCP / NBR 12655) e massas de aco NBR 7480.

SEED: validar com Leonan — consumos por m3 sao sementes da literatura ABCP;
massas de aco sao valores nominais exatos da NBR 7480.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TracoConcreto:
    fck_mpa: int
    cimento_kg_m3: float
    areia_m3_m3: float
    brita_m3_m3: float
    agua_l_m3: float


TRACOS_CONCRETO: dict[int, TracoConcreto] = {
    20: TracoConcreto(20, 320.0, 0.86, 0.83, 185.0),
    25: TracoConcreto(25, 350.0, 0.82, 0.83, 185.0),
    30: TracoConcreto(30, 395.0, 0.77, 0.82, 185.0),
}

# Massa nominal (kg/m) por bitola — NBR 7480 (valores exatos de norma)
MASSA_ACO_KG_M: dict[float, float] = {
    5.0: 0.154, 6.3: 0.245, 8.0: 0.395, 10.0: 0.617,
    12.5: 0.963, 16.0: 1.578, 20.0: 2.466, 25.0: 3.853,
}

PERDA_ACO = 0.10  # perdas + transpasses simplificados
```

`src/quantitativo/servicos/concreto.py`:

```python
"""Quantificacao de concreto armado: volume, traco por fck e aco por bitola."""
from collections import defaultdict

from quantitativo.catalogo.concreto import MASSA_ACO_KG_M, PERDA_ACO, TRACOS_CONCRETO
from quantitativo.modelos import ElementoConcreto, ParametrosConcreto
from quantitativo.resultados import ItemServico


def quantificar_concreto(
    elementos: tuple[ElementoConcreto, ...], params: ParametrosConcreto
) -> ItemServico:
    traco = TRACOS_CONCRETO[params.fck_mpa]
    volume = sum(e.volume_m3 for e in elementos) * (1.0 + params.perda)

    insumos: dict[str, float] = {
        "cimento_kg": volume * traco.cimento_kg_m3,
        "areia_m3": volume * traco.areia_m3_m3,
        "brita_m3": volume * traco.brita_m3_m3,
        "agua_l": volume * traco.agua_l_m3,
    }

    aco_por_bitola: dict[float, float] = defaultdict(float)
    for elemento in elementos:
        for arm in elemento.armaduras:
            kg = MASSA_ACO_KG_M[arm.bitola_mm] * arm.quantidade_barras * arm.comprimento_barra_m
            aco_por_bitola[arm.bitola_mm] += kg
    for bitola, kg in sorted(aco_por_bitola.items()):
        insumos[f"aco_{bitola}mm_kg"] = kg * (1.0 + PERDA_ACO)

    return ItemServico(
        tipo="concreto",
        descricao=f"Concreto armado fck {params.fck_mpa} MPa (traco ABCP/NBR 12655)",
        unidade="m3",
        quantidade=volume,
        insumos=insumos,
    )
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_concreto.py -v`
Expected: 3 passed

- [ ] **Step 5: Validação cruzada com MUSSO (manual)**

Conferir `MASSA_ACO_KG_M` contra a tabela de bitolas usada em `C:\Users\leona\MUSSO` (e/ou `C:\Users\leona\dlima-estrutural\src\estrutural\core\materiais`). Os valores NBR 7480 devem bater exatamente. Se houver divergência, a norma manda — corrigir aqui e anotar no commit.

- [ ] **Step 6: Commit**

```bash
git add src/quantitativo/catalogo/concreto.py src/quantitativo/servicos/concreto.py tests/test_concreto.py
git commit -m "feat: concreto armado com traco por fck e aco por bitola NBR 7480"
```

---

### Task 7: Pisos (contrapiso + cerâmica)

**Files:**
- Create: `src/quantitativo/servicos/pisos.py`
- Test: `tests/test_pisos.py`

**Interfaces:**
- Consumes: `Ambiente`, `ParametrosPiso`, `insumos_argamassa`, `ItemServico`
- Produces: `quantificar_pisos(ambientes: tuple[Ambiente, ...], params: ParametrosPiso) -> list[ItemServico]` — 2 itens: `"contrapiso"` (traço `"1:4"`, volume = área × espessura, sem perda adicional — a espessura já é nominal) e `"ceramica"` (insumos: `"ceramica_m2"` = área × (1+perda_ceramica), `"argamassa_colante_kg"` = área × 4.5, `"rejunte_kg"` = área × 0.5). Constantes `COLANTE_KG_M2 = 4.5` e `REJUNTE_KG_M2 = 0.5` (`# SEED: validar com Leonan`).

- [ ] **Step 1: Escrever teste que falha**

`tests/test_pisos.py`:

```python
import pytest

from quantitativo.modelos import Ambiente, ParametrosPiso
from quantitativo.servicos.pisos import quantificar_pisos

AMBIENTES = (Ambiente(nome="Sala", area_m2=20.0), Ambiente(nome="Quarto", area_m2=12.0))


def test_contrapiso_1_4_por_espessura():
    itens = quantificar_pisos(AMBIENTES, ParametrosPiso(esp_contrapiso_m=0.03))
    contrapiso = itens[0]
    assert contrapiso.tipo == "contrapiso"
    assert contrapiso.quantidade == pytest.approx(32.0)
    volume = 32.0 * 0.03  # 0.96 m3
    assert contrapiso.insumos["cimento_kg"] == pytest.approx(volume * 365.0, rel=1e-4)
    assert contrapiso.insumos["areia_m3"] == pytest.approx(volume * 1.08, rel=1e-4)


def test_ceramica_com_perda_colante_e_rejunte():
    itens = quantificar_pisos(AMBIENTES, ParametrosPiso(perda_ceramica=0.10))
    ceramica = itens[1]
    assert ceramica.tipo == "ceramica"
    assert ceramica.insumos["ceramica_m2"] == pytest.approx(35.2)
    assert ceramica.insumos["argamassa_colante_kg"] == pytest.approx(144.0)
    assert ceramica.insumos["rejunte_kg"] == pytest.approx(16.0)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_pisos.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/servicos/pisos.py`:

```python
"""Quantificacao de contrapiso e piso ceramico."""
from quantitativo.catalogo.tracos import insumos_argamassa
from quantitativo.modelos import Ambiente, ParametrosPiso
from quantitativo.resultados import ItemServico

COLANTE_KG_M2 = 4.5  # SEED: validar com Leonan
REJUNTE_KG_M2 = 0.5  # SEED: validar com Leonan


def quantificar_pisos(
    ambientes: tuple[Ambiente, ...], params: ParametrosPiso
) -> list[ItemServico]:
    area_m2 = sum(a.area_m2 for a in ambientes)

    contrapiso = ItemServico(
        tipo="contrapiso",
        descricao=f"Contrapiso traco 1:4, esp. {params.esp_contrapiso_m * 100:.0f} cm",
        unidade="m2",
        quantidade=area_m2,
        insumos=insumos_argamassa(area_m2 * params.esp_contrapiso_m, "1:4"),
    )
    ceramica = ItemServico(
        tipo="ceramica",
        descricao="Piso ceramico com argamassa colante e rejunte",
        unidade="m2",
        quantidade=area_m2,
        insumos={
            "ceramica_m2": area_m2 * (1.0 + params.perda_ceramica),
            "argamassa_colante_kg": area_m2 * COLANTE_KG_M2,
            "rejunte_kg": area_m2 * REJUNTE_KG_M2,
        },
    )
    return [contrapiso, ceramica]
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_pisos.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/servicos/pisos.py tests/test_pisos.py
git commit -m "feat: servico de pisos com contrapiso 1:4 e ceramica com colante/rejunte"
```

---

### Task 8: Pintura + esquadrias

**Files:**
- Create: `src/quantitativo/servicos/pintura.py`
- Create: `src/quantitativo/servicos/esquadrias.py`
- Test: `tests/test_pintura_esquadrias.py`

**Interfaces:**
- Consumes: `Parede`, `Ambiente`, `ParametrosPintura`, `ItemServico`
- Produces: `quantificar_pintura(paredes, ambientes, params: ParametrosPintura) -> ItemServico` — `tipo="pintura"`, área = Σ(área líquida × faces_internas) + Σ(área ambientes, tetos); insumos `"selador_l"` (0.1 L/m²), `"massa_corrida_kg"` (1.0 kg/m²), `"tinta_l"` (área × demãos ÷ rendimento). `quantificar_esquadrias(paredes) -> ItemServico` — `tipo="esquadrias"`, `unidade="un"`, insumos `"<tipo> <larg>x<alt> m"` → contagem.

- [ ] **Step 1: Escrever teste que falha**

`tests/test_pintura_esquadrias.py`:

```python
import pytest

from quantitativo.modelos import Abertura, Ambiente, Parede, ParametrosPintura
from quantitativo.servicos.esquadrias import quantificar_esquadrias
from quantitativo.servicos.pintura import quantificar_pintura

PAREDE = Parede(
    nome="P1", comprimento_m=10.0, pe_direito_m=2.8,
    aberturas=(
        Abertura(tipo="porta", largura_m=0.8, altura_m=2.1),
        Abertura(tipo="janela", largura_m=1.2, altura_m=1.0),
    ),
    faces_internas=1, face_externa=True,
)
AMBIENTES = (Ambiente(nome="Sala", area_m2=20.0), Ambiente(nome="Quarto", area_m2=12.0))


def test_pintura_paredes_internas_mais_tetos():
    item = quantificar_pintura((PAREDE,), AMBIENTES, ParametrosPintura(demaos=2))
    area = 25.12 * 1 + 32.0  # 57.12 m2
    assert item.quantidade == pytest.approx(area)
    assert item.insumos["selador_l"] == pytest.approx(area * 0.1)
    assert item.insumos["massa_corrida_kg"] == pytest.approx(area * 1.0)
    assert item.insumos["tinta_l"] == pytest.approx(area * 2 / 10.0)


def test_esquadrias_contadas_por_tipo_e_dimensao():
    p2 = Parede(
        nome="P2", comprimento_m=4.0, pe_direito_m=2.8,
        aberturas=(Abertura(tipo="porta", largura_m=0.8, altura_m=2.1, quantidade=2),),
    )
    item = quantificar_esquadrias((PAREDE, p2))
    assert item.unidade == "un"
    assert item.insumos["porta 0.80x2.10 m"] == 3
    assert item.insumos["janela 1.20x1.00 m"] == 1
    assert item.quantidade == 4
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_pintura_esquadrias.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/servicos/pintura.py`:

```python
"""Quantificacao de pintura interna (paredes + tetos)."""
from quantitativo.modelos import Ambiente, Parede, ParametrosPintura
from quantitativo.resultados import ItemServico

SELADOR_L_M2 = 0.1        # SEED: validar com Leonan
MASSA_CORRIDA_KG_M2 = 1.0  # SEED: validar com Leonan (total p/ 2 demaos)


def quantificar_pintura(
    paredes: tuple[Parede, ...],
    ambientes: tuple[Ambiente, ...],
    params: ParametrosPintura,
) -> ItemServico:
    area_paredes = sum(p.area_liquida_m2 * p.faces_internas for p in paredes)
    area_tetos = sum(a.area_m2 for a in ambientes)
    area = area_paredes + area_tetos

    return ItemServico(
        tipo="pintura",
        descricao=f"Pintura latex {params.demaos} demaos sobre selador e massa corrida",
        unidade="m2",
        quantidade=area,
        insumos={
            "selador_l": area * SELADOR_L_M2,
            "massa_corrida_kg": area * MASSA_CORRIDA_KG_M2,
            "tinta_l": area * params.demaos / params.rendimento_tinta_m2_por_l,
        },
    )
```

`src/quantitativo/servicos/esquadrias.py`:

```python
"""Contagem de esquadrias (portas e janelas) por tipo e dimensao."""
from collections import defaultdict

from quantitativo.modelos import Parede
from quantitativo.resultados import ItemServico


def quantificar_esquadrias(paredes: tuple[Parede, ...]) -> ItemServico:
    contagem: dict[str, float] = defaultdict(float)
    for parede in paredes:
        for ab in parede.aberturas:
            chave = f"{ab.tipo} {ab.largura_m:.2f}x{ab.altura_m:.2f} m"
            contagem[chave] += ab.quantidade

    return ItemServico(
        tipo="esquadrias",
        descricao="Esquadrias (portas e janelas) por tipo e dimensao",
        unidade="un",
        quantidade=sum(contagem.values()),
        insumos=dict(sorted(contagem.items())),
    )
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_pintura_esquadrias.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/servicos/pintura.py src/quantitativo/servicos/esquadrias.py tests/test_pintura_esquadrias.py
git commit -m "feat: servicos de pintura e contagem de esquadrias"
```

---

### Task 9: Lista de compra consolidada

**Files:**
- Create: `src/quantitativo/consolidacao.py`
- Test: `tests/test_consolidacao.py`

**Interfaces:**
- Consumes: `ItemServico`
- Produces: `LinhaCompra(insumo, descricao, unidade_compra, quantidade)`; `consolidar_lista_compra(itens: list[ItemServico]) -> list[LinhaCompra]` — agrega os dicts `insumos` de todos os itens e converte para unidade de compra: `cimento_kg`→sacos 50 kg (ceil), `cal_kg`→sacos 20 kg (ceil), `areia_m3`/`brita_m3`→m³ arredondado p/ cima em passos de 0,5, `bloco:*`→un, `aco_*`→kg (1 casa), demais mantêm unidade original. Ordenação alfabética por `insumo`.

- [ ] **Step 1: Escrever teste que falha**

`tests/test_consolidacao.py`:

```python
import pytest

from quantitativo.consolidacao import consolidar_lista_compra
from quantitativo.resultados import ItemServico


def _item(tipo, insumos):
    return ItemServico(tipo=tipo, descricao=tipo, unidade="m2", quantidade=1.0, insumos=insumos)


def test_agrega_cimento_de_varios_servicos_em_sacos():
    itens = [
        _item("alvenaria", {"cimento_kg": 31.5, "areia_m3": 0.25}),
        _item("concreto", {"cimento_kg": 881.1, "areia_m3": 2.06, "brita_m3": 2.09}),
    ]
    compras = {linha.insumo: linha for linha in consolidar_lista_compra(itens)}
    # 912.6 kg / 50 = 18.25 -> 19 sacos
    assert compras["cimento_kg"].quantidade == 19
    assert compras["cimento_kg"].unidade_compra == "saco 50 kg"
    # 2.31 m3 -> arredonda p/ 2.5
    assert compras["areia_m3"].quantidade == pytest.approx(2.5)
    assert compras["brita_m3"].quantidade == pytest.approx(2.5)


def test_cal_em_sacos_de_20kg_e_blocos_em_unidades():
    itens = [_item("alvenaria", {"cal_kg": 31.5, "bloco:tijolo_9x19x19": 691.0})]
    compras = {linha.insumo: linha for linha in consolidar_lista_compra(itens)}
    assert compras["cal_kg"].quantidade == 2  # 31.5/20 = 1.575 -> 2 sacos
    assert compras["bloco:tijolo_9x19x19"].quantidade == 691
    assert compras["bloco:tijolo_9x19x19"].unidade_compra == "un"


def test_aco_mantem_kg_com_uma_casa():
    itens = [_item("concreto", {"aco_10.0mm_kg": 15.20288})]
    (linha,) = consolidar_lista_compra(itens)
    assert linha.quantidade == pytest.approx(15.2)
    assert linha.unidade_compra == "kg"
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_consolidacao.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/consolidacao.py`:

```python
"""Consolidacao dos insumos de todos os servicos em lista de compra."""
import math
from dataclasses import dataclass

from quantitativo.resultados import ItemServico

DESCRICOES = {
    "cimento_kg": "Cimento CP II",
    "cal_kg": "Cal hidratada",
    "areia_m3": "Areia media lavada",
    "brita_m3": "Brita 1",
    "agua_l": "Agua",
    "ceramica_m2": "Piso ceramico",
    "argamassa_colante_kg": "Argamassa colante AC-I",
    "rejunte_kg": "Rejunte",
    "selador_l": "Selador acrilico",
    "massa_corrida_kg": "Massa corrida PVA",
    "tinta_l": "Tinta latex",
}


@dataclass(frozen=True)
class LinhaCompra:
    insumo: str
    descricao: str
    unidade_compra: str
    quantidade: float


def _arredonda_meio_m3(valor: float) -> float:
    return math.ceil(valor * 2.0) / 2.0


def _converter(insumo: str, total: float) -> tuple[str, float]:
    if insumo == "cimento_kg":
        return "saco 50 kg", float(math.ceil(total / 50.0))
    if insumo == "cal_kg":
        return "saco 20 kg", float(math.ceil(total / 20.0))
    if insumo in ("areia_m3", "brita_m3"):
        return "m3", _arredonda_meio_m3(total)
    if insumo.startswith("bloco:"):
        return "un", float(math.ceil(total))
    if insumo.startswith("aco_"):
        return "kg", round(total, 1)
    unidade = insumo.rsplit("_", 1)[-1] if "_" in insumo else "un"
    return unidade, round(total, 2)


def _descricao(insumo: str) -> str:
    if insumo.startswith("bloco:"):
        return insumo.split(":", 1)[1].replace("_", " ")
    if insumo.startswith("aco_"):
        return f"Aco CA-50 bitola {insumo.removeprefix('aco_').removesuffix('mm_kg')} mm"
    return DESCRICOES.get(insumo, insumo)


def consolidar_lista_compra(itens: list[ItemServico]) -> list[LinhaCompra]:
    totais: dict[str, float] = {}
    for item in itens:
        for insumo, qtd in item.insumos.items():
            totais[insumo] = totais.get(insumo, 0.0) + qtd

    linhas = []
    for insumo in sorted(totais):
        unidade, quantidade = _converter(insumo, totais[insumo])
        linhas.append(LinhaCompra(insumo, _descricao(insumo), unidade, quantidade))
    return linhas
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_consolidacao.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/consolidacao.py tests/test_consolidacao.py
git commit -m "feat: lista de compra consolidada com unidades de compra (sacos, m3, un)"
```

---

### Task 10: Produtividades + cronograma executivo com checklist

**Files:**
- Create: `src/quantitativo/catalogo/produtividade.py`
- Create: `src/quantitativo/cronograma.py`
- Test: `tests/test_cronograma.py`

**Interfaces:**
- Consumes: `ItemServico`
- Produces: `PRODUTIVIDADE_H_POR_UN: dict[str, float]` (horas de pedreiro por unidade do serviço, equipe 1 pedreiro + 1 ajudante); `Etapa(nome, ordem, servicos, dias, checklist)`; `montar_cronograma(itens: list[ItemServico], horas_dia: float = 8.0) -> list[Etapa]` — 11 etapas fixas na ordem executiva; etapas com serviços quantificados ganham `dias = ceil(Σ quantidade × h_un / horas_dia)`; etapas sem quantitativo (fundação, cobertura, instalações, limpeza) ganham `dias=None` e checklist.

- [ ] **Step 1: Escrever teste que falha**

`tests/test_cronograma.py`:

```python
from quantitativo.cronograma import montar_cronograma
from quantitativo.resultados import ItemServico


def _item(tipo, quantidade):
    return ItemServico(tipo=tipo, descricao=tipo, unidade="m2", quantidade=quantidade, insumos={})


def test_ordem_executiva_das_11_etapas():
    etapas = montar_cronograma([])
    assert [e.nome for e in etapas] == [
        "Servicos preliminares", "Fundacao", "Estrutura de concreto", "Alvenaria",
        "Cobertura", "Instalacoes embutidas", "Revestimentos", "Pisos",
        "Pintura", "Esquadrias e acabamentos", "Limpeza final e entrega",
    ]


def test_duracao_da_alvenaria_com_equipe_1_mais_1():
    # 25.12 m2 * 1.0 h/m2 / 8 h/dia = 3.14 -> 4 dias
    etapas = montar_cronograma([_item("alvenaria", 25.12)])
    alvenaria = next(e for e in etapas if e.nome == "Alvenaria")
    assert alvenaria.dias == 4


def test_revestimentos_somam_as_tres_camadas():
    itens = [_item("chapisco", 50.24), _item("emboco", 50.24), _item("reboco", 50.24)]
    etapas = montar_cronograma(itens)
    rev = next(e for e in etapas if e.nome == "Revestimentos")
    # 50.24*(0.10 + 0.55 + 0.45) = 55.264 h / 8 = 6.9 -> 7 dias
    assert rev.dias == 7


def test_etapas_sem_quantitativo_tem_checklist_e_dias_none():
    etapas = montar_cronograma([])
    fundacao = next(e for e in etapas if e.nome == "Fundacao")
    assert fundacao.dias is None
    assert len(fundacao.checklist) >= 3
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_cronograma.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/catalogo/produtividade.py`:

```python
"""Produtividades (horas de pedreiro por unidade) para equipe 1 pedreiro + 1 ajudante.

SEED: validar com Leonan — coeficientes baseados em composicoes SINAPI/TCPO.
"""

PRODUTIVIDADE_H_POR_UN: dict[str, float] = {
    "alvenaria": 1.00,    # h/m2
    "chapisco": 0.10,     # h/m2
    "emboco": 0.55,       # h/m2
    "reboco": 0.45,       # h/m2
    "concreto": 10.0,     # h/m3 (forma + armacao + concretagem simplificado)
    "contrapiso": 0.35,   # h/m2
    "ceramica": 0.65,     # h/m2
    "pintura": 0.30,      # h/m2 (preparo + 2 demaos)
    "esquadrias": 2.00,   # h/un
}
```

`src/quantitativo/cronograma.py`:

```python
"""Cronograma executivo da obra: etapas na ordem, duracoes e checklists."""
import math
from dataclasses import dataclass

from quantitativo.catalogo.produtividade import PRODUTIVIDADE_H_POR_UN
from quantitativo.resultados import ItemServico


@dataclass(frozen=True)
class Etapa:
    nome: str
    ordem: int
    servicos: tuple[str, ...]     # tipos de ItemServico que compoem a etapa
    dias: int | None              # None = sem quantitativo na v1 (so checklist)
    checklist: tuple[str, ...]


# (nome, servicos quantificados, checklist)
_ETAPAS = (
    ("Servicos preliminares", (), (
        "Alvara de construcao aprovado", "ART/RRT recolhida",
        "Ligacoes provisorias de agua e luz", "Locacao da obra conferida (gabarito)",
        "Placa de obra instalada",
    )),
    ("Fundacao", (), (
        "Gabarito conferido com projeto", "Escavacao na cota do projeto",
        "Lastro/concreto magro executado", "Armaduras conforme projeto de fundacao",
        "Impermeabilizacao do baldrame",
    )),
    ("Estrutura de concreto", ("concreto",), (
        "Formas conferidas (prumo, nivel, esquadro)", "Armaduras conferidas antes da concretagem",
        "Espaculadores/cobrimento conforme NBR 6118", "Cura umida por no minimo 7 dias",
    )),
    ("Alvenaria", ("alvenaria",), (
        "Primeira fiada nivelada e alinhada", "Prumo conferido a cada fiada",
        "Vergas e contravergas nas aberturas", "Encunhamento apos deformacao da estrutura",
    )),
    ("Cobertura", (), (
        "Estrutura do telhado conforme projeto", "Telhas com recobrimento correto",
        "Rufos e calhas instalados", "Teste de estanqueidade (chuva/mangueira)",
    )),
    ("Instalacoes embutidas", (), (
        "Eletrodutos e caixas embutidos antes do revestimento",
        "Tubulacao hidraulica testada sob pressao",
        "Esgoto com caimento conferido", "Pontos conferidos com projeto",
    )),
    ("Revestimentos", ("chapisco", "emboco", "reboco"), (
        "Chapisco curado antes do emboco", "Taliscas e mestras niveladas",
        "Requadros de aberturas conferidos",
    )),
    ("Pisos", ("contrapiso", "ceramica"), (
        "Contrapiso curado e nivelado", "Caimento para ralos conferido",
        "Juntas de assentamento uniformes", "Rejunte apos 72h",
    )),
    ("Pintura", ("pintura",), (
        "Reboco curado (30 dias) antes de pintar", "Selador aplicado",
        "Massa lixada entre demaos", "Demaos com intervalo do fabricante",
    )),
    ("Esquadrias e acabamentos", ("esquadrias",), (
        "Portas e janelas no prumo e esquadro", "Vedacao das esquadrias externas",
        "Ferragens e fechaduras testadas",
    )),
    ("Limpeza final e entrega", (), (
        "Limpeza fina executada", "Teste de todos os pontos eletricos e hidraulicos",
        "Vistoria final com checklist de entrega", "Habite-se solicitado",
    )),
)


def montar_cronograma(itens: list[ItemServico], horas_dia: float = 8.0) -> list[Etapa]:
    quantidades = {item.tipo: item.quantidade for item in itens}

    etapas = []
    for ordem, (nome, servicos, checklist) in enumerate(_ETAPAS, start=1):
        horas = sum(
            quantidades[s] * PRODUTIVIDADE_H_POR_UN[s]
            for s in servicos if s in quantidades
        )
        dias = math.ceil(horas / horas_dia) if horas > 0 else None
        etapas.append(Etapa(nome, ordem, servicos, dias, checklist))
    return etapas
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_cronograma.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/catalogo/produtividade.py src/quantitativo/cronograma.py tests/test_cronograma.py
git commit -m "feat: cronograma executivo com 11 etapas, duracoes 1+1 e checklists"
```

---

### Task 11: Export Excel estilo SINAPI

**Files:**
- Create: `src/quantitativo/saidas/__init__.py`
- Create: `src/quantitativo/saidas/planilha.py`
- Test: `tests/test_planilha.py`

**Interfaces:**
- Consumes: `ItemServico`, `LinhaCompra`, `Etapa`
- Produces: `gerar_planilha(itens: list[ItemServico], compras: list[LinhaCompra], etapas: list[Etapa], caminho: str | Path) -> None` — xlsx com 3 abas: `Servicos` (Codigo, Descricao, Un, Quantidade + linhas de insumo indentadas), `Lista de Compra` (Insumo, Descricao, Unidade, Quantidade), `Cronograma` (Ordem, Etapa, Dias, Checklist).

- [ ] **Step 1: Escrever teste que falha**

`tests/test_planilha.py`:

```python
from openpyxl import load_workbook

from quantitativo.consolidacao import LinhaCompra
from quantitativo.cronograma import Etapa
from quantitativo.resultados import ItemServico
from quantitativo.saidas.planilha import gerar_planilha


def test_gera_xlsx_com_tres_abas(tmp_path):
    itens = [ItemServico("alvenaria", "Alvenaria tijolo 9x19x19", "m2", 25.12,
                         {"bloco:tijolo_9x19x19": 691.0, "cimento_kg": 31.5})]
    compras = [LinhaCompra("cimento_kg", "Cimento CP II", "saco 50 kg", 1.0)]
    etapas = [Etapa("Alvenaria", 4, ("alvenaria",), 4, ("Prumo conferido",))]
    caminho = tmp_path / "quantitativo.xlsx"

    gerar_planilha(itens, compras, etapas, caminho)

    wb = load_workbook(caminho)
    assert wb.sheetnames == ["Servicos", "Lista de Compra", "Cronograma"]

    servicos = wb["Servicos"]
    assert servicos["A1"].value == "Codigo"
    assert servicos["B2"].value == "Alvenaria tijolo 9x19x19"
    assert servicos["D2"].value == 25.12

    compra = wb["Lista de Compra"]
    assert compra["B2"].value == "Cimento CP II"
    assert compra["D2"].value == 1.0

    crono = wb["Cronograma"]
    assert crono["B2"].value == "Alvenaria"
    assert crono["C2"].value == 4
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_planilha.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implementar**

`src/quantitativo/saidas/__init__.py` (vazio) e `src/quantitativo/saidas/planilha.py`:

```python
"""Export xlsx estilo SINAPI: servicos com insumos, lista de compra e cronograma."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from quantitativo.consolidacao import LinhaCompra
from quantitativo.cronograma import Etapa
from quantitativo.resultados import ItemServico

NEGRITO = Font(bold=True)


def _cabecalho(ws, colunas: list[str]) -> None:
    ws.append(colunas)
    for celula in ws[1]:
        celula.font = NEGRITO


def gerar_planilha(
    itens: list[ItemServico],
    compras: list[LinhaCompra],
    etapas: list[Etapa],
    caminho: str | Path,
) -> None:
    wb = Workbook()

    ws = wb.active
    ws.title = "Servicos"
    _cabecalho(ws, ["Codigo", "Descricao", "Un", "Quantidade"])
    for i, item in enumerate(itens, start=1):
        ws.append([f"DL-{i:03d}", item.descricao, item.unidade, round(item.quantidade, 2)])
        ws[ws.max_row][0].font = NEGRITO
        for insumo, qtd in item.insumos.items():
            ws.append(["", f"    {insumo}", "", round(qtd, 2)])

    ws = wb.create_sheet("Lista de Compra")
    _cabecalho(ws, ["Insumo", "Descricao", "Unidade", "Quantidade"])
    for linha in compras:
        ws.append([linha.insumo, linha.descricao, linha.unidade_compra, linha.quantidade])

    ws = wb.create_sheet("Cronograma")
    _cabecalho(ws, ["Ordem", "Etapa", "Dias", "Checklist"])
    for etapa in etapas:
        ws.append([etapa.ordem, etapa.nome, etapa.dias, "; ".join(etapa.checklist)])

    wb.save(caminho)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_planilha.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add src/quantitativo/saidas tests/test_planilha.py
git commit -m "feat: export xlsx com abas de servicos, lista de compra e cronograma"
```

---

### Task 12: Pipeline + CLI YAML → xlsx + obra exemplo (golden de ponta a ponta)

**Files:**
- Create: `src/quantitativo/pipeline.py`
- Create: `src/quantitativo/carregador.py`
- Create: `src/quantitativo/__main__.py`
- Create: `exemplos/casa_terrea.yaml`
- Create: `README.md`
- Test: `tests/test_pipeline.py`

**Interfaces:**
- Consumes: tudo das tasks anteriores
- Produces: `quantificar_obra(obra: Obra, params: ParametrosObra) -> list[ItemServico]` (ordem: alvenaria, chapisco, emboço, reboco, concreto, contrapiso, cerâmica, pintura, esquadrias — serviços sem dados são omitidos); `carregar_obra(caminho) -> tuple[Obra, ParametrosObra]`; CLI `python -m quantitativo exemplos/casa_terrea.yaml -o saida.xlsx`.

- [ ] **Step 1: Criar obra exemplo**

`exemplos/casa_terrea.yaml`:

```yaml
obra: Casa terrea exemplo D'LIMA
parametros:
  alvenaria: {bloco: tijolo_9x19x19, junta_m: 0.01, perda: 0.10}
  revestimento: {esp_chapisco_m: 0.005, esp_emboco_m: 0.020, esp_reboco_m: 0.005}
  concreto: {fck_mpa: 25}
  piso: {esp_contrapiso_m: 0.03}
  pintura: {demaos: 2}
pavimentos:
  - nome: Terreo
    paredes:
      - nome: P1 (frente)
        comprimento_m: 8.0
        pe_direito_m: 2.8
        faces_internas: 1
        face_externa: true
        aberturas:
          - {tipo: porta, largura_m: 0.9, altura_m: 2.1}
          - {tipo: janela, largura_m: 1.5, altura_m: 1.2}
      - nome: P2 (fundos)
        comprimento_m: 8.0
        pe_direito_m: 2.8
        faces_internas: 1
        face_externa: true
        aberturas:
          - {tipo: porta, largura_m: 0.8, altura_m: 2.1}
          - {tipo: janela, largura_m: 1.2, altura_m: 1.0}
      - {nome: P3 (lateral esq), comprimento_m: 10.0, pe_direito_m: 2.8, faces_internas: 1, face_externa: true}
      - {nome: P4 (lateral dir), comprimento_m: 10.0, pe_direito_m: 2.8, faces_internas: 1, face_externa: true}
      - nome: P5 (interna sala/quartos)
        comprimento_m: 8.0
        pe_direito_m: 2.8
        aberturas:
          - {tipo: porta, largura_m: 0.8, altura_m: 2.1, quantidade: 3}
    ambientes:
      - {nome: Sala/cozinha, area_m2: 30.0}
      - {nome: Quarto 1, area_m2: 12.0}
      - {nome: Quarto 2, area_m2: 10.0}
      - {nome: Banheiro, area_m2: 4.0}
    elementos_concreto:
      - nome: Vigas baldrame
        tipo: viga
        largura_m: 0.14
        altura_m: 0.30
        comprimento_m: 36.0
        armaduras:
          - {bitola_mm: 10.0, quantidade_barras: 4, comprimento_barra_m: 36.0}
          - {bitola_mm: 5.0, quantidade_barras: 180, comprimento_barra_m: 0.80}
      - nome: Pilares
        tipo: pilar
        largura_m: 0.14
        altura_m: 0.30
        comprimento_m: 22.4   # 8 pilares x 2.8 m
        armaduras:
          - {bitola_mm: 10.0, quantidade_barras: 32, comprimento_barra_m: 3.2}
```

- [ ] **Step 2: Escrever teste que falha**

`tests/test_pipeline.py`:

```python
from quantitativo.carregador import carregar_obra
from quantitativo.consolidacao import consolidar_lista_compra
from quantitativo.cronograma import montar_cronograma
from quantitativo.pipeline import quantificar_obra
from quantitativo.saidas.planilha import gerar_planilha


def test_pipeline_de_ponta_a_ponta_na_obra_exemplo(tmp_path):
    obra, params = carregar_obra("exemplos/casa_terrea.yaml")
    assert obra.nome == "Casa terrea exemplo D'LIMA"
    assert len(obra.paredes) == 5

    itens = quantificar_obra(obra, params)
    tipos = [i.tipo for i in itens]
    assert tipos == ["alvenaria", "chapisco", "emboco", "reboco", "concreto",
                     "contrapiso", "ceramica", "pintura", "esquadrias"]

    compras = consolidar_lista_compra(itens)
    por_insumo = {c.insumo: c for c in compras}
    assert por_insumo["cimento_kg"].quantidade >= 1      # sacos > 0
    assert por_insumo["areia_m3"].quantidade > 0
    assert "bloco:tijolo_9x19x19" in por_insumo

    etapas = montar_cronograma(itens)
    alvenaria = next(e for e in etapas if e.nome == "Alvenaria")
    assert alvenaria.dias is not None and alvenaria.dias > 0

    caminho = tmp_path / "casa_terrea.xlsx"
    gerar_planilha(itens, compras, etapas, caminho)
    assert caminho.exists()


def test_obra_sem_concreto_omite_o_servico():
    obra, params = carregar_obra("exemplos/casa_terrea.yaml")
    from dataclasses import replace
    pavimentos_sem_concreto = tuple(
        replace(p, elementos_concreto=()) for p in obra.pavimentos
    )
    obra_sem = replace(obra, pavimentos=pavimentos_sem_concreto)
    tipos = [i.tipo for i in quantificar_obra(obra_sem, params)]
    assert "concreto" not in tipos
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `python -m pytest tests/test_pipeline.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implementar pipeline, carregador e CLI**

`src/quantitativo/pipeline.py`:

```python
"""Orquestra todos os servicos de quantificacao de uma obra."""
from quantitativo.modelos import Obra, ParametrosObra
from quantitativo.resultados import ItemServico
from quantitativo.servicos.alvenaria import quantificar_alvenaria
from quantitativo.servicos.concreto import quantificar_concreto
from quantitativo.servicos.esquadrias import quantificar_esquadrias
from quantitativo.servicos.pintura import quantificar_pintura
from quantitativo.servicos.pisos import quantificar_pisos
from quantitativo.servicos.revestimento import quantificar_revestimentos


def quantificar_obra(obra: Obra, params: ParametrosObra) -> list[ItemServico]:
    itens: list[ItemServico] = []
    if obra.paredes:
        itens.append(quantificar_alvenaria(obra.paredes, params.alvenaria))
        itens.extend(quantificar_revestimentos(obra.paredes, params.revestimento))
    if obra.elementos_concreto:
        itens.append(quantificar_concreto(obra.elementos_concreto, params.concreto))
    if obra.ambientes:
        itens.extend(quantificar_pisos(obra.ambientes, params.piso))
    if obra.paredes or obra.ambientes:
        itens.append(quantificar_pintura(obra.paredes, obra.ambientes, params.pintura))
    if any(p.aberturas for p in obra.paredes):
        itens.append(quantificar_esquadrias(obra.paredes))
    return itens
```

`src/quantitativo/carregador.py`:

```python
"""Carrega uma obra + parametros a partir de arquivo YAML."""
from pathlib import Path

import yaml

from quantitativo.modelos import (
    Abertura, Ambiente, Armadura, ElementoConcreto, Obra, Parede,
    ParametrosAlvenaria, ParametrosConcreto, ParametrosObra,
    ParametrosPintura, ParametrosPiso, ParametrosRevestimento, Pavimento,
)


def _parede(d: dict) -> Parede:
    aberturas = tuple(Abertura(**a) for a in d.pop("aberturas", []))
    return Parede(aberturas=aberturas, **d)


def _elemento(d: dict) -> ElementoConcreto:
    armaduras = tuple(Armadura(**a) for a in d.pop("armaduras", []))
    return ElementoConcreto(armaduras=armaduras, **d)


def _pavimento(d: dict) -> Pavimento:
    return Pavimento(
        nome=d["nome"],
        paredes=tuple(_parede(p) for p in d.get("paredes", [])),
        ambientes=tuple(Ambiente(**a) for a in d.get("ambientes", [])),
        elementos_concreto=tuple(_elemento(e) for e in d.get("elementos_concreto", [])),
    )


def carregar_obra(caminho: str | Path) -> tuple[Obra, ParametrosObra]:
    dados = yaml.safe_load(Path(caminho).read_text(encoding="utf-8"))
    obra = Obra(
        nome=dados["obra"],
        pavimentos=tuple(_pavimento(p) for p in dados["pavimentos"]),
    )
    p = dados.get("parametros", {})
    params = ParametrosObra(
        alvenaria=ParametrosAlvenaria(**p["alvenaria"]),
        revestimento=ParametrosRevestimento(**p.get("revestimento", {})),
        concreto=ParametrosConcreto(**p.get("concreto", {})),
        piso=ParametrosPiso(**p.get("piso", {})),
        pintura=ParametrosPintura(**p.get("pintura", {})),
    )
    return obra, params
```

`src/quantitativo/__main__.py`:

```python
"""CLI: python -m quantitativo obra.yaml -o quantitativo.xlsx"""
import argparse

from quantitativo.carregador import carregar_obra
from quantitativo.consolidacao import consolidar_lista_compra
from quantitativo.cronograma import montar_cronograma
from quantitativo.pipeline import quantificar_obra
from quantitativo.saidas.planilha import gerar_planilha


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantitativo de materiais D'LIMA")
    parser.add_argument("obra", help="arquivo YAML da obra")
    parser.add_argument("-o", "--saida", default="quantitativo.xlsx", help="arquivo xlsx de saida")
    args = parser.parse_args()

    obra, params = carregar_obra(args.obra)
    itens = quantificar_obra(obra, params)
    compras = consolidar_lista_compra(itens)
    etapas = montar_cronograma(itens)
    gerar_planilha(itens, compras, etapas, args.saida)

    print(f"Obra: {obra.nome}")
    print(f"{len(itens)} servicos quantificados, {len(compras)} insumos na lista de compra.")
    print(f"Planilha gerada em: {args.saida}")


if __name__ == "__main__":
    main()
```

`README.md`:

```markdown
# dlima-quantitativo

Motor de quantitativo de materiais do Modulo Quantitativo D'LIMA (Fase 1 — entrada manual).

## Uso

    python -m quantitativo exemplos/casa_terrea.yaml -o quantitativo.xlsx

Gera planilha com 3 abas: Servicos (estilo SINAPI, composicao propria),
Lista de Compra (sacos, m3, unidades) e Cronograma (etapas + checklist,
equipe 1 pedreiro + 1 ajudante).

## Testes

    python -m pytest

## Avisos de engenharia

- Tracos e consumos marcados com `SEED` sao sementes da literatura
  (ABCP/TCPO/SINAPI) e devem ser validados pelo engenheiro responsavel.
- Traco de concreto por fck segue metodo ABCP / NBR 12655 (a NBR 6118
  define a classe de resistencia, nao o traco).
- Fase 2+: extracao automatica de plantas (DXF/PDF/IFC) e integracao ERP.
```

- [ ] **Step 5: Rodar todos os testes**

Run: `python -m pytest -v`
Expected: todos passam (Tasks 1-12, ~35 testes)

- [ ] **Step 6: Rodar o CLI de verdade (verificação end-to-end)**

Run: `python -m quantitativo exemplos/casa_terrea.yaml -o casa_terrea.xlsx`
Expected: imprime obra, nº de serviços e insumos, gera `casa_terrea.xlsx`. Abrir o xlsx e conferir visualmente as 3 abas.

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: pipeline completo, CLI YAML->xlsx e obra exemplo de ponta a ponta"
```

---

## Pós-plano (não são tasks de código)

1. **Validação de engenharia pelo Leonan:** revisar todos os valores `SEED` (traços, consumos, produtividades) e rodar o CLI numa obra real dele, conferindo contra levantamento manual. Ajustes viram commits `fix: ajusta seed X conforme validacao`.
2. **Fase 2 (plano separado):** parser DXF + tela de conferência visual.
3. **Publicar repo no GitHub** (`gh repo create dlima-quantitativo --private`).
