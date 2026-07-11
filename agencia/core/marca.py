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
