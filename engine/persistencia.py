"""Persistencia de relatorios de analise no filesystem (ADR-1).

Um dict em memoria nao e compartilhado entre os workers do gunicorn, o que
causaria 404 intermitente em producao. Aqui o relatorio e gravado em arquivo
num diretorio temporario compartilhado pelo host, com limpeza por TTL.
"""
import os
import time
import pickle
import tempfile

_DIR = os.path.join(tempfile.gettempdir(), "dlima_estruturas")
_TTL_SEGUNDOS = 6 * 3600  # 6 horas


def _garantir_dir():
    os.makedirs(_DIR, exist_ok=True)


def _limpar_expirados():
    """Remove arquivos de analise mais antigos que o TTL."""
    if not os.path.isdir(_DIR):
        return
    agora = time.time()
    for nome in os.listdir(_DIR):
        caminho = os.path.join(_DIR, nome)
        try:
            if agora - os.path.getmtime(caminho) > _TTL_SEGUNDOS:
                os.remove(caminho)
        except OSError:
            pass


def _caminho(aid):
    """Caminho do arquivo de um id, ou None se o id for invalido.

    Aceita apenas ids alfanumericos — bloqueia path traversal vindo da URL.
    """
    if not aid or not aid.isalnum():
        return None
    return os.path.join(_DIR, aid + ".pkl")


def salvar(aid, relatorio):
    """Persiste o relatorio no filesystem (seguro entre workers do gunicorn)."""
    caminho = _caminho(aid)
    if caminho is None:
        raise ValueError("id invalido: %r" % aid)
    _garantir_dir()
    _limpar_expirados()
    with open(caminho, "wb") as f:
        pickle.dump(relatorio, f)


def carregar(aid):
    """Le um relatorio persistido. Retorna None se nao existir ou id invalido."""
    caminho = _caminho(aid)
    if caminho is None or not os.path.isfile(caminho):
        return None
    try:
        with open(caminho, "rb") as f:
            return pickle.load(f)
    except (OSError, pickle.PickleError):
        return None
