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
