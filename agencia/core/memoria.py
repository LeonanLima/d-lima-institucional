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
