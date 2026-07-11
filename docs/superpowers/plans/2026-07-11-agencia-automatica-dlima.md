# Agência de Marketing Automática D'LIMA — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o motor interno da agência automática D'LIMA: núcleo Python testável (modelos, fila Notion, memória de aprendizado, orquestrador de ciclo) + os prompts dos subagentes de cada squad, com aprovação humana no Notion antes de publicar.

**Architecture:** Caminho A — cada subagente é um prompt markdown em `agencia/agentes/`; a lógica determinística (o que é testável) vive em `agencia/core/` como funções puras sobre dataclasses `frozen`. A publicação e as chamadas a Notion/Metricool acontecem via MCP em tempo de execução, orquestradas pelo Orquestrador; o núcleo Python só prepara os dados (payloads de card, plano de ciclo, memória).

**Tech Stack:** Python 3, pytest, dataclasses (stdlib), json (stdlib). Sem dependências novas. Notion e Metricool via MCP (não via pip).

## Global Constraints

- Python com **type annotations em toda assinatura** (PEP 8, black, ruff).
- Dados imutáveis: dataclasses **`frozen=True`** para modelos.
- **Sem dependências novas** no `requirements.txt` (produção continua só `flask`/`gunicorn`). Tudo do núcleo usa stdlib; `pytest` já está em `requirements-dev.txt`.
- **Nenhuma publicação sem passar por Status `Aprovado`** — trava dura no orquestrador.
- Design das peças é **Claude Design (Artifacts HTML+SVG)**, nunca Canva.
- Testes em `tests/agencia/`, rodados com `pytest tests/agencia/ -v`.
- Marca é fonte-única em `agencia/config/marca.json` — nenhum agente hardcoda paleta/handles.

---

## Estrutura de arquivos

```
agencia/
  __init__.py
  config/
    marca.json                 # paleta, voz, handles — fonte da verdade
  core/
    __init__.py
    modelos.py                 # Formato, StatusPeca, Pauta, Peca (frozen)
    marca.py                   # carrega e valida marca.json
    fila_notion.py             # Peca -> propriedades + markdown do card Notion
    memoria.py                 # store JSON de aprendizado entre ciclos
    ciclo.py                   # orquestrador puro: pautas -> peças, trava de aprovação
  agentes/                     # prompts dos subagentes (markdown)
    orquestrador.md
    marca-brand-designer.md
    marca-brand-voice.md
    marca-brand-guardian.md
    conteudo-estrategista.md
    conteudo-pesquisador.md
    conteudo-copywriter.md
    conteudo-roteirista-video.md
    design-post.md
    design-thumb.md
    dados-analista.md
  README.md                    # runbook: como rodar um ciclo
tests/agencia/
  __init__.py
  test_modelos.py
  test_marca.py
  test_fila_notion.py
  test_memoria.py
  test_ciclo.py
docs/design/                   # saídas do Claude Design (logo, guia)
```

---

### Task 0: Logo nova + guia de marca (Claude Design)

Entregável criativo, não é código. Feito com Claude Design (Artifact HTML+SVG) e a skill `dlima-brand`.

**Files:**
- Create: `docs/design/logo-dlima.html` (Artifact com as variações da logo em SVG)
- Create: `docs/design/guia-marca-dlima.md` (guia aplicado: uso da logo, paleta, tipografia)

- [ ] **Step 1: Ler a identidade atual**

Invocar a skill `dlima-brand` e ler `agencia/config/marca.json` (após Task 1b existir) para paleta/arquétipo. Antes disso, usar a paleta que já está na skill.

- [ ] **Step 2: Gerar a logo como Artifact**

Criar `docs/design/logo-dlima.html` com 4 variações em SVG inline:
1. Logo horizontal (símbolo + "D'LIMA ENGENHARIA")
2. Símbolo isolado (deve evocar construtora/incorporadora + engenharia civil — ex.: monograma "DL" com prumo/esquadro ou linha de nível)
3. Versão monocromática (1 cor)
4. Versão negativa (fundo escuro)

Publicar via ferramenta Artifact e apresentar ao Leonan.

- [ ] **Step 3: Escrever o guia de marca**

`docs/design/guia-marca-dlima.md`: área de proteção, tamanho mínimo, usos proibidos, paleta (hex), tipografia (Montserrat já é a do site).

- [ ] **Step 4: Gate do Leonan**

Apresentar logo + guia. Só seguir após aprovação explícita. Registrar a escolha.

- [ ] **Step 5: Commit**

```bash
git add docs/design/logo-dlima.html docs/design/guia-marca-dlima.md
git commit -m "feat(agencia): logo nova D'LIMA + guia de marca (Claude Design)"
```

---

### Task 1: Modelos do domínio

**Files:**
- Create: `agencia/__init__.py` (vazio)
- Create: `agencia/core/__init__.py` (vazio)
- Create: `agencia/core/modelos.py`
- Test: `tests/agencia/__init__.py` (vazio), `tests/agencia/test_modelos.py`

**Interfaces:**
- Produces:
  - `class Formato(str, Enum)`: `REEL`, `CARROSSEL`, `STORY`, `FEED`
  - `class StatusPeca(str, Enum)`: `IDEACAO`, `AGUARDANDO_APROVACAO`, `APROVADO`, `AGENDADO`, `PUBLICADO`, `MEDIDO`
  - `@dataclass(frozen=True) class Pauta`: `tema: str`, `angulo: str`, `formato: Formato`
  - `@dataclass(frozen=True) class Peca`: `pauta: Pauta`, `legenda: str`, `status: StatusPeca = StatusPeca.IDEACAO`, `arte_path: str | None = None`, `data_sugerida: str | None = None`
  - `def aprovar(peca: Peca) -> Peca` — retorna nova Peca com `status=APROVADO` (imutável)

- [ ] **Step 1: Write the failing test**

```python
# tests/agencia/test_modelos.py
from agencia.core.modelos import Formato, StatusPeca, Pauta, Peca, aprovar


def test_peca_nasce_em_ideacao():
    pauta = Pauta(tema="Financiamento MCMV", angulo="dúvida comum", formato=Formato.CARROSSEL)
    peca = Peca(pauta=pauta, legenda="Como sair do aluguel...")
    assert peca.status == StatusPeca.IDEACAO
    assert peca.arte_path is None


def test_aprovar_retorna_nova_peca_imutavel():
    pauta = Pauta(tema="x", angulo="y", formato=Formato.REEL)
    peca = Peca(pauta=pauta, legenda="z")
    aprovada = aprovar(peca)
    assert aprovada.status == StatusPeca.APROVADO
    assert peca.status == StatusPeca.IDEACAO  # original intacto
    assert aprovada.legenda == "z"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/agencia/test_modelos.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agencia'`

- [ ] **Step 3: Write minimal implementation**

```python
# agencia/core/modelos.py
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class Formato(str, Enum):
    REEL = "Reel"
    CARROSSEL = "Carrossel"
    STORY = "Story"
    FEED = "Feed"


class StatusPeca(str, Enum):
    IDEACAO = "Ideação"
    AGUARDANDO_APROVACAO = "Aguardando aprovação"
    APROVADO = "Aprovado"
    AGENDADO = "Agendado"
    PUBLICADO = "Publicado"
    MEDIDO = "Medido"


@dataclass(frozen=True)
class Pauta:
    tema: str
    angulo: str
    formato: Formato


@dataclass(frozen=True)
class Peca:
    pauta: Pauta
    legenda: str
    status: StatusPeca = StatusPeca.IDEACAO
    arte_path: str | None = None
    data_sugerida: str | None = None


def aprovar(peca: Peca) -> Peca:
    return replace(peca, status=StatusPeca.APROVADO)
```

Criar também os `__init__.py` vazios: `agencia/__init__.py`, `agencia/core/__init__.py`, `tests/agencia/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/agencia/test_modelos.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add agencia/__init__.py agencia/core/__init__.py agencia/core/modelos.py tests/agencia/__init__.py tests/agencia/test_modelos.py
git commit -m "feat(agencia): modelos do domínio (Pauta, Peca, Status) imutáveis"
```

---

### Task 2: Configuração da marca

**Files:**
- Create: `agencia/config/marca.json`
- Create: `agencia/core/marca.py`
- Test: `tests/agencia/test_marca.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `@dataclass(frozen=True) class Marca`: `nome: str`, `paleta: dict[str, str]`, `arquetipo: str`, `voz_do: tuple[str, ...]`, `voz_dont: tuple[str, ...]`, `handles: dict[str, str]`
  - `def carregar_marca(path: str = ".../marca.json") -> Marca` — lê o JSON, valida campos obrigatórios, levanta `ValueError` se faltar chave.

- [ ] **Step 1: Write the failing test**

```python
# tests/agencia/test_marca.py
import json
from pathlib import Path

import pytest

from agencia.core.marca import carregar_marca, Marca


def test_carrega_marca_padrao():
    m = carregar_marca()
    assert isinstance(m, Marca)
    assert m.nome == "D'LIMA"
    assert "primaria" in m.paleta
    assert m.handles["instagram"]  # não vazio


def test_marca_invalida_levanta_erro(tmp_path):
    ruim = tmp_path / "ruim.json"
    ruim.write_text(json.dumps({"nome": "X"}), encoding="utf-8")
    with pytest.raises(ValueError):
        carregar_marca(str(ruim))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/agencia/test_marca.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agencia.core.marca'`

- [ ] **Step 3: Create marca.json**

```json
{
  "nome": "D'LIMA",
  "paleta": {
    "primaria": "#0B1F3A",
    "secundaria": "#C8A24B",
    "clara": "#F4F1EA",
    "texto": "#1A1A1A"
  },
  "arquetipo": "Irmão Mais Velho + Professor",
  "voz_do": [
    "Explicar com clareza, como quem ensina",
    "Falar de obra real, bastidor, engenharia de custos",
    "Tom firme e acolhedor"
  ],
  "voz_dont": [
    "Jargão vazio e promessa milagrosa",
    "Tom corporativo distante",
    "Emoji em excesso"
  ],
  "handles": {
    "instagram": "leonan.dlima",
    "site": "dlimaengenharia.org"
  }
}
```

- [ ] **Step 4: Write minimal implementation**

```python
# agencia/core/marca.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_PADRAO = Path(__file__).resolve().parent.parent / "config" / "marca.json"
_OBRIGATORIOS = ("nome", "paleta", "arquetipo", "voz_do", "voz_dont", "handles")


@dataclass(frozen=True)
class Marca:
    nome: str
    paleta: dict[str, str]
    arquetipo: str
    voz_do: tuple[str, ...]
    voz_dont: tuple[str, ...]
    handles: dict[str, str]


def carregar_marca(path: str | None = None) -> Marca:
    p = Path(path) if path else _PADRAO
    dados = json.loads(p.read_text(encoding="utf-8"))
    faltando = [k for k in _OBRIGATORIOS if k not in dados]
    if faltando:
        raise ValueError(f"marca.json inválido, faltam chaves: {faltando}")
    return Marca(
        nome=dados["nome"],
        paleta=dados["paleta"],
        arquetipo=dados["arquetipo"],
        voz_do=tuple(dados["voz_do"]),
        voz_dont=tuple(dados["voz_dont"]),
        handles=dados["handles"],
    )
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/agencia/test_marca.py -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add agencia/config/marca.json agencia/core/marca.py tests/agencia/test_marca.py
git commit -m "feat(agencia): config de marca com validacao (fonte unica)"
```

---

### Task 3: Fila Notion (Peça → card)

**Files:**
- Create: `agencia/core/fila_notion.py`
- Test: `tests/agencia/test_fila_notion.py`

**Interfaces:**
- Consumes: `Peca`, `Formato`, `StatusPeca` de `modelos.py`.
- Produces:
  - `PROPRIEDADES_DB: dict[str, str]` — mapa nome→tipo Notion, para criar o database (`Título`:title, `Formato`:select, `Legenda`:rich_text, `Data sugerida`:date, `Status`:select, `Métricas`:rich_text, `Aprendizado`:rich_text).
  - `def peca_para_propriedades(peca: Peca) -> dict[str, object]` — propriedades do card (chaves = nomes das colunas).
  - `def peca_para_markdown(peca: Peca) -> str` — corpo do card em Notion Markdown (preview: tema, ângulo, legenda, link da arte).

- [ ] **Step 1: Write the failing test**

```python
# tests/agencia/test_fila_notion.py
from agencia.core.modelos import Formato, Pauta, Peca, StatusPeca
from agencia.core.fila_notion import (
    PROPRIEDADES_DB,
    peca_para_propriedades,
    peca_para_markdown,
)


def _peca():
    pauta = Pauta(tema="Sair do aluguel", angulo="passo a passo", formato=Formato.CARROSSEL)
    return Peca(
        pauta=pauta,
        legenda="Você paga aluguel há anos? Veja como a casa própria...",
        status=StatusPeca.AGUARDANDO_APROVACAO,
        arte_path="docs/design/pecas/sair-do-aluguel.html",
        data_sugerida="2026-07-15",
    )


def test_schema_tem_status_e_formato():
    assert PROPRIEDADES_DB["Status"] == "select"
    assert PROPRIEDADES_DB["Formato"] == "select"


def test_propriedades_do_card():
    props = peca_para_propriedades(_peca())
    assert props["Título"] == "Sair do aluguel"
    assert props["Formato"] == "Carrossel"
    assert props["Status"] == "Aguardando aprovação"
    assert props["Data sugerida"] == "2026-07-15"


def test_markdown_mostra_legenda_e_angulo():
    md = peca_para_markdown(_peca())
    assert "passo a passo" in md
    assert "Você paga aluguel" in md
    assert "sair-do-aluguel.html" in md
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/agencia/test_fila_notion.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agencia.core.fila_notion'`

- [ ] **Step 3: Write minimal implementation**

```python
# agencia/core/fila_notion.py
from __future__ import annotations

from agencia.core.modelos import Peca

PROPRIEDADES_DB: dict[str, str] = {
    "Título": "title",
    "Formato": "select",
    "Legenda": "rich_text",
    "Data sugerida": "date",
    "Status": "select",
    "Métricas": "rich_text",
    "Aprendizado": "rich_text",
}


def peca_para_propriedades(peca: Peca) -> dict[str, object]:
    return {
        "Título": peca.pauta.tema,
        "Formato": peca.pauta.formato.value,
        "Legenda": peca.legenda,
        "Data sugerida": peca.data_sugerida,
        "Status": peca.status.value,
    }


def peca_para_markdown(peca: Peca) -> str:
    arte = peca.arte_path or "_(arte pendente)_"
    return (
        f"## {peca.pauta.tema}\n\n"
        f"**Ângulo:** {peca.pauta.angulo}\n\n"
        f"**Formato:** {peca.pauta.formato.value}\n\n"
        f"**Legenda:**\n\n{peca.legenda}\n\n"
        f"**Arte:** {arte}\n"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/agencia/test_fila_notion.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add agencia/core/fila_notion.py tests/agencia/test_fila_notion.py
git commit -m "feat(agencia): serializacao de Peca para card do Notion"
```

---

### Task 4: Memória de aprendizado

**Files:**
- Create: `agencia/core/memoria.py`
- Test: `tests/agencia/test_memoria.py`

**Interfaces:**
- Consumes: nada (só stdlib).
- Produces:
  - `@dataclass(frozen=True) class Aprendizado`: `tema: str`, `formato: str`, `engajamento: float`, `nota: str`
  - `def registrar(path: str, ap: Aprendizado) -> None` — anexa (append) ao arquivo JSON (cria se não existir).
  - `def top_temas(path: str, n: int = 3) -> list[str]` — lê o JSON e devolve os `n` temas de maior engajamento médio, ordem decrescente.

- [ ] **Step 1: Write the failing test**

```python
# tests/agencia/test_memoria.py
from agencia.core.memoria import Aprendizado, registrar, top_temas


def test_registra_e_ranqueia(tmp_path):
    arq = str(tmp_path / "memoria.json")
    registrar(arq, Aprendizado(tema="MCMV", formato="Carrossel", engajamento=8.0, nota="ok"))
    registrar(arq, Aprendizado(tema="MCMV", formato="Reel", engajamento=6.0, nota="ok"))
    registrar(arq, Aprendizado(tema="Bastidor de obra", formato="Reel", engajamento=9.5, nota="forte"))
    top = top_temas(arq, n=2)
    assert top == ["Bastidor de obra", "MCMV"]  # 9.5 > média(8,6)=7.0


def test_top_temas_arquivo_inexistente(tmp_path):
    assert top_temas(str(tmp_path / "nao-existe.json")) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/agencia/test_memoria.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agencia.core.memoria'`

- [ ] **Step 3: Write minimal implementation**

```python
# agencia/core/memoria.py
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Aprendizado:
    tema: str
    formato: str
    engajamento: float
    nota: str


def registrar(path: str, ap: Aprendizado) -> None:
    p = Path(path)
    registros = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    registros.append(asdict(ap))
    p.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")


def top_temas(path: str, n: int = 3) -> list[str]:
    p = Path(path)
    if not p.exists():
        return []
    registros = json.loads(p.read_text(encoding="utf-8"))
    somas: dict[str, float] = defaultdict(float)
    contagem: dict[str, int] = defaultdict(int)
    for r in registros:
        somas[r["tema"]] += r["engajamento"]
        contagem[r["tema"]] += 1
    medias = {t: somas[t] / contagem[t] for t in somas}
    return sorted(medias, key=lambda t: medias[t], reverse=True)[:n]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/agencia/test_memoria.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add agencia/core/memoria.py tests/agencia/test_memoria.py
git commit -m "feat(agencia): memoria de aprendizado entre ciclos"
```

---

### Task 5: Orquestrador do ciclo (com trava de aprovação)

**Files:**
- Create: `agencia/core/ciclo.py`
- Test: `tests/agencia/test_ciclo.py`

**Interfaces:**
- Consumes: `Pauta`, `Peca`, `StatusPeca` de `modelos.py`; `top_temas` de `memoria.py`.
- Produces:
  - `def montar_pecas(pautas: list[Pauta], legendas: dict[str, str]) -> list[Peca]` — casa cada pauta com sua legenda (por `tema`) e devolve peças em `AGUARDANDO_APROVACAO`. Se faltar legenda para um tema, levanta `ValueError`.
  - `def publicaveis(pecas: list[Peca]) -> list[Peca]` — **a trava**: devolve só as peças com `status == APROVADO`. Nunca publica outra coisa.
  - `def priorizar_pautas(pautas: list[Pauta], memoria_path: str) -> list[Pauta]` — reordena pondo primeiro as pautas cujo tema está no `top_temas`.

- [ ] **Step 1: Write the failing test**

```python
# tests/agencia/test_ciclo.py
import pytest

from agencia.core.modelos import Formato, Pauta, Peca, StatusPeca, aprovar
from agencia.core.ciclo import montar_pecas, publicaveis, priorizar_pautas
from agencia.core.memoria import Aprendizado, registrar


def test_montar_pecas_casa_legenda_por_tema():
    pautas = [Pauta(tema="MCMV", angulo="a", formato=Formato.REEL)]
    pecas = montar_pecas(pautas, {"MCMV": "legenda do reel"})
    assert len(pecas) == 1
    assert pecas[0].legenda == "legenda do reel"
    assert pecas[0].status == StatusPeca.AGUARDANDO_APROVACAO


def test_montar_pecas_sem_legenda_falha():
    pautas = [Pauta(tema="MCMV", angulo="a", formato=Formato.REEL)]
    with pytest.raises(ValueError):
        montar_pecas(pautas, {})


def test_trava_so_publica_aprovado():
    pauta = Pauta(tema="x", angulo="y", formato=Formato.FEED)
    aguardando = Peca(pauta=pauta, legenda="z", status=StatusPeca.AGUARDANDO_APROVACAO)
    aprovada = aprovar(Peca(pauta=pauta, legenda="w"))
    saida = publicaveis([aguardando, aprovada])
    assert saida == [aprovada]


def test_prioriza_por_memoria(tmp_path):
    arq = str(tmp_path / "m.json")
    registrar(arq, Aprendizado(tema="Bastidor", formato="Reel", engajamento=9.0, nota=""))
    pautas = [
        Pauta(tema="MCMV", angulo="a", formato=Formato.REEL),
        Pauta(tema="Bastidor", angulo="b", formato=Formato.REEL),
    ]
    ordenadas = priorizar_pautas(pautas, arq)
    assert ordenadas[0].tema == "Bastidor"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/agencia/test_ciclo.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agencia.core.ciclo'`

- [ ] **Step 3: Write minimal implementation**

```python
# agencia/core/ciclo.py
from __future__ import annotations

from agencia.core.memoria import top_temas
from agencia.core.modelos import Pauta, Peca, StatusPeca


def montar_pecas(pautas: list[Pauta], legendas: dict[str, str]) -> list[Peca]:
    pecas: list[Peca] = []
    for pauta in pautas:
        if pauta.tema not in legendas:
            raise ValueError(f"sem legenda para o tema: {pauta.tema}")
        pecas.append(
            Peca(
                pauta=pauta,
                legenda=legendas[pauta.tema],
                status=StatusPeca.AGUARDANDO_APROVACAO,
            )
        )
    return pecas


def publicaveis(pecas: list[Peca]) -> list[Peca]:
    return [p for p in pecas if p.status == StatusPeca.APROVADO]


def priorizar_pautas(pautas: list[Pauta], memoria_path: str) -> list[Pauta]:
    top = top_temas(memoria_path)
    return sorted(pautas, key=lambda p: (p.tema not in top, top.index(p.tema) if p.tema in top else 0))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/agencia/test_ciclo.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Run all agency tests**

Run: `pytest tests/agencia/ -v`
Expected: PASS (todos — 13 testes)

- [ ] **Step 6: Commit**

```bash
git add agencia/core/ciclo.py tests/agencia/test_ciclo.py
git commit -m "feat(agencia): orquestrador do ciclo com trava de aprovacao"
```

---

### Task 6: Database Notion + runbook do ciclo

Ação de runtime (via MCP) + documentação. Não há teste pytest; a verificação é buscar o database de volta.

**Files:**
- Create: `agencia/README.md`

- [ ] **Step 1: Criar o database no Notion**

Sob a página "Agência de Marketing Automática — D'LIMA" (id `39ad02bf-fe3f-81e2-ad75-d5abc8b3e8c1`), criar uma database "Conteúdo D'LIMA" com exatamente as colunas de `PROPRIEDADES_DB` (Task 3): `Título`(title), `Formato`(select: Reel/Carrossel/Story/Feed), `Legenda`(rich_text), `Data sugerida`(date), `Status`(select: Ideação/Aguardando aprovação/Aprovado/Agendado/Publicado/Medido), `Métricas`(rich_text), `Aprendizado`(rich_text).

- [ ] **Step 2: Verificar**

Fazer `fetch` do database criado e conferir que as 7 propriedades e as opções de `Status` existem. Guardar o `data_source_id` retornado no `agencia/README.md`.

- [ ] **Step 3: Escrever o runbook**

`agencia/README.md` documentando: (1) o `data_source_id` do database; (2) como rodar um ciclo manualmente (sequência dos squads); (3) que nada publica sem card em `Aprovado`; (4) onde fica a memória (`agencia/.memoria.json`, no `.gitignore`).

- [ ] **Step 4: Ignorar a memória local**

Adicionar `agencia/.memoria.json` ao `.gitignore`.

- [ ] **Step 5: Commit**

```bash
git add agencia/README.md .gitignore
git commit -m "feat(agencia): database Notion Conteudo D'LIMA + runbook do ciclo"
```

---

### Task 7: Squad MARCA — prompts dos subagentes

**Files:**
- Create: `agencia/agentes/orquestrador.md`
- Create: `agencia/agentes/marca-brand-designer.md`
- Create: `agencia/agentes/marca-brand-voice.md`
- Create: `agencia/agentes/marca-brand-guardian.md`

- [ ] **Step 1: Escrever orquestrador.md**

Papel: dispara o ciclo, chama squads na ordem (estrategista→pesquisador→copywriter→brand-guardian→designer→fila Notion), injeta `top_temas` da memória, respeita a trava `publicaveis`. Entradas: metas do mês + memória. Saídas: cards no Notion. Regra dura: nunca acionar publicação sem status `Aprovado`.

- [ ] **Step 2: Escrever marca-brand-designer.md**

Papel: gerar logo e artes-mãe da marca via Claude Design (Artifact SVG). Deve ler `agencia/config/marca.json`. Já produziu a logo na Task 0; aqui vira o agente reutilizável para futuras variações.

- [ ] **Step 3: Escrever marca-brand-voice.md**

Papel: dado um rascunho de copy, reescreve na voz D'LIMA (arquétipo + voz_do/voz_dont de `marca.json`). Sem travessão/aspas/tom de IA (regra de escrita humanizada do Leonan).

- [ ] **Step 4: Escrever marca-brand-guardian.md**

Papel: validação binária (aprova/reprova) de cada peça contra `marca.json` e o guia. Reprovou → devolve motivo objetivo, peça não sobe ao Notion.

- [ ] **Step 5: Commit**

```bash
git add agencia/agentes/orquestrador.md agencia/agentes/marca-brand-designer.md agencia/agentes/marca-brand-voice.md agencia/agentes/marca-brand-guardian.md
git commit -m "feat(agencia): prompts do Orquestrador e Squad MARCA"
```

---

### Task 8: Squad CONTEÚDO — prompts dos subagentes

**Files:**
- Create: `agencia/agentes/conteudo-estrategista.md`
- Create: `agencia/agentes/conteudo-pesquisador.md`
- Create: `agencia/agentes/conteudo-copywriter.md`
- Create: `agencia/agentes/conteudo-roteirista-video.md`

- [ ] **Step 1: conteudo-estrategista.md**

Papel: gerar 5–7 `Pauta` (tema, ângulo, formato) por ciclo a partir das metas, sazonalidade e `top_temas`. Saída no formato que `montar_pecas` consome (temas únicos).

- [ ] **Step 2: conteudo-pesquisador.md**

Papel: pra cada pauta, levantar dúvidas reais do público, dados e ganchos (usa Metricool/Apify/web). Alimenta o copywriter.

- [ ] **Step 3: conteudo-copywriter.md**

Papel: escrever a legenda/roteiro de cada pauta usando os frameworks de copy da skill `dlima-brand`. Saída: `dict[tema -> legenda]` pro `montar_pecas`.

- [ ] **Step 4: conteudo-roteirista-video.md**

Papel: roteiro de Reels/vídeo (cena a cena) quando o formato for `REEL`. Geração de vídeo (Allgrow) fica opcional.

- [ ] **Step 5: Commit**

```bash
git add agencia/agentes/conteudo-estrategista.md agencia/agentes/conteudo-pesquisador.md agencia/agentes/conteudo-copywriter.md agencia/agentes/conteudo-roteirista-video.md
git commit -m "feat(agencia): prompts do Squad CONTEUDO"
```

---

### Task 9: Squads DESIGN e DADOS — prompts + fechamento

**Files:**
- Create: `agencia/agentes/design-post.md`
- Create: `agencia/agentes/design-thumb.md`
- Create: `agencia/agentes/dados-analista.md`

- [ ] **Step 1: design-post.md**

Papel: gerar a arte do post (carrossel/feed/story) como Artifact HTML+SVG na paleta de `marca.json`, salvando em `docs/design/pecas/<slug>.html`; devolve o caminho pra `Peca.arte_path`. Claude Design, nunca Canva.

- [ ] **Step 2: design-thumb.md**

Papel: capa de Reel/YouTube como Artifact, mesmo padrão de saída.

- [ ] **Step 3: dados-analista.md**

Papel: puxar métricas do Metricool após publicação, montar relatório semanal e gravar `Aprendizado` (via `memoria.registrar`) pra realimentar o Orquestrador. Define o `engajamento` (0–10) por peça.

- [ ] **Step 4: Rodar a suíte inteira do projeto**

Run: `pytest -v`
Expected: PASS (testes do site em `tests/test_app.py` + 13 da agência).

- [ ] **Step 5: Commit**

```bash
git add agencia/agentes/design-post.md agencia/agentes/design-thumb.md agencia/agentes/dados-analista.md
git commit -m "feat(agencia): prompts dos Squads DESIGN e DADOS"
```

---

## Cobertura do spec (self-review)

- Objetivo / motor interno → Tasks 1–5 (núcleo) + 6 (Notion) + 7–9 (agentes).
- Aprovação humana no Notion → Task 3 (card) + Task 5 (`publicaveis`, trava) + Task 6 (database + fluxo).
- Logo nova → Task 0.
- D'LIMA existente (voz/arquétipo) → Task 2 (`marca.json`) + Task 7 (brand-voice/guardian).
- Squad MARCA/CONTEÚDO/DESIGN/DADOS → Tasks 7/8/9.
- Design via Claude Design → Task 0, Task 9 (design-post/thumb).
- Publicação Metricool → Task 6 runbook + Task 9 (analista puxa métricas); a ação de agendar é runtime via MCP pelo Orquestrador.
- Loop de aprendizado → Task 4 (memória) + Task 5 (`priorizar_pautas`) + Task 9 (analista grava).
- Ads = Fase 2 → fora deste plano, como no spec.
