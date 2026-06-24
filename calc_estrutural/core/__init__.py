# core/ - estruturas de resultado unificadas (fonte unica para UI/CLI/memorial)
from .resultado import (
    Verificacao, ResultadoElemento, verif_max, verif_min, OP_MAX, OP_MIN,
)

__all__ = [
    "Verificacao", "ResultadoElemento", "verif_max", "verif_min",
    "OP_MAX", "OP_MIN",
]
