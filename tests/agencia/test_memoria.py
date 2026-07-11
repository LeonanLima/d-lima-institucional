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
