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
