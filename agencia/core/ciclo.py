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
    return sorted(
        pautas,
        key=lambda p: (p.tema not in top, top.index(p.tema) if p.tema in top else 0),
    )
