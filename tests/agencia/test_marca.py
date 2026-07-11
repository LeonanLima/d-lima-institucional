import json

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
