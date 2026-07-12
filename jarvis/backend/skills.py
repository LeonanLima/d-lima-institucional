"""Habilidades do JARVIS (v2).

Roteador de intencao: tenta resolver comandos conhecidos de forma segura e
direta (abrir apps/sites, anotacoes, hora/data/calculo, status de projetos).
Se nenhum casar, retorna None e o app cai no cerebro (claude) para conversar.

Todas as habilidades sao acoes ESPECIFICAS e limitadas - nunca executam
comandos arbitrarios vindos da voz.
"""
import os
import re
import ast
import json
import operator
import webbrowser
import unicodedata
from datetime import datetime

# Operadores permitidos no avaliador de calculo (seguro, sem eval).
_MATH_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _safe_eval(node):
    """Avalia apenas expressoes aritmeticas simples via AST (sem eval)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _MATH_OPS:
        return _MATH_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _MATH_OPS:
        return _MATH_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("expressao nao permitida")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")

MEMORY_FILE = os.path.join(
    os.path.expanduser("~"),
    ".claude", "projects",
    "C--Users-leona-OneDrive-Documentos-d-lima-institucional",
    "memory", "MEMORY.md",
)

# Sites/apps conhecidos que o JARVIS pode abrir (seguro: lista fechada).
SITES = {
    "whatsapp": "https://web.whatsapp.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "email": "https://mail.google.com",
    "instagram": "https://www.instagram.com",
    "notion": "https://www.notion.so",
    "google": "https://www.google.com",
    "chatgpt": "https://chat.openai.com",
    "claude": "https://claude.ai",
    "drive": "https://drive.google.com",
    "agenda": "https://calendar.google.com",
    "calendario": "https://calendar.google.com",
    "maps": "https://maps.google.com",
    "metricool": "https://app.metricool.com",
}

DIAS = ["segunda-feira", "terca-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sabado", "domingo"]
MESES = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def _norm(texto):
    """Minusculas e sem acento, para casar palavras-chave."""
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


# ---------------------------------------------------------------- hora / data
def _skill_hora_data(texto, n):
    agora = datetime.now()
    if "que horas" in n or "hora agora" in n or ("horas" in n and "sao" in n):
        return f"Sao {agora.hour} horas e {agora.minute} minutos."
    if "que dia" in n or "data de hoje" in n or "dia e hoje" in n or "hoje e" in n:
        dia_semana = DIAS[agora.weekday()]
        mes = MESES[agora.month - 1]
        return f"Hoje e {dia_semana}, {agora.day} de {mes} de {agora.year}."
    return None


# ------------------------------------------------------------------- calculo
def _skill_calculo(texto, n):
    if not any(p in n for p in ["quanto e", "calcula", "quanto da"]):
        return None
    # Traduz palavras faladas para operadores (a gente fala "vezes", nao "*").
    base = n
    for palavra, simbolo in [
        ("multiplicado por", "*"), ("dividido por", "/"), ("vezes", "*"),
        ("dividido", "/"), ("sobre", "/"), ("mais", "+"), ("menos", "-"),
    ]:
        base = base.replace(palavra, f" {simbolo} ")
    # Extrai so a parte que parece expressao matematica.
    expr = re.sub(r"[^0-9+\-*/().,]", " ", base)
    expr = expr.replace(",", ".").strip()
    if not expr or not re.search(r"\d", expr):
        return None
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expr):
        return None
    try:
        resultado = _safe_eval(ast.parse(expr, mode="eval").body)
    except Exception:
        return "Nao consegui fazer essa conta."
    if isinstance(resultado, float) and resultado.is_integer():
        resultado = int(resultado)
    return f"O resultado e {resultado}."


# --------------------------------------------------------------- abrir sites
def _skill_abrir(texto, n):
    if not (n.startswith("abre") or n.startswith("abrir") or "abre o " in n
            or "abre a " in n or "abrir o " in n or "abrir a " in n):
        return None
    for chave, url in SITES.items():
        if chave in n:
            webbrowser.open(url)
            return f"Abrindo o {chave}."
    return "Nao sei abrir isso ainda. Posso abrir WhatsApp, YouTube, Gmail, Instagram, Notion, Drive, Agenda ou Google."


# ------------------------------------------------------------------- notas
def _load_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_notes(notes):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def _skill_notas(texto, n):
    # Adicionar
    for gatilho in ["anota que ", "anotar que ", "anota ", "anotar ",
                    "lembra que ", "lembrar que ", "lembrete "]:
        if n.startswith(gatilho):
            corte = len(gatilho)
            conteudo = texto[corte:].strip()
            if not conteudo:
                return "O que voce quer que eu anote?"
            notes = _load_notes()
            notes.append({"texto": conteudo, "quando": datetime.now().isoformat(timespec="minutes")})
            _save_notes(notes)
            return "Anotado."
    # Listar
    if any(p in n for p in ["meus lembretes", "minhas anotacoes", "o que eu anotei",
                            "meus recados", "minhas notas", "quais lembretes"]):
        notes = _load_notes()
        if not notes:
            return "Voce nao tem nenhuma anotacao no momento."
        itens = "; ".join(x["texto"] for x in notes)
        qtd = len(notes)
        plural = "anotacao" if qtd == 1 else "anotacoes"
        return f"Voce tem {qtd} {plural}: {itens}."
    # Limpar
    if any(p in n for p in ["apaga os lembretes", "apagar os lembretes",
                            "limpa as anotacoes", "limpar as anotacoes",
                            "apaga as anotacoes"]):
        _save_notes([])
        return "Pronto, apaguei todas as anotacoes."
    return None


# --------------------------------------------------------- status de projetos
def project_context(texto, n):
    """Se for pergunta sobre projetos, devolve o conteudo do indice de memoria
    para o cerebro responder de forma fundamentada. Retorna None se nao casar."""
    gatilhos = ["onde parei", "status do projeto", "como esta o projeto",
                "como estao meus projetos", "meus projetos", "no que eu estava",
                "status dos projetos", "andamento do projeto"]
    if not any(g in n for g in gatilhos):
        return None
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


# --------------------------------------------------- execucao em projetos (v3)
def load_projects():
    """Lista branca: nome falado -> pasta absoluta. Fora dela o JARVIS nao age."""
    try:
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def match_project(n):
    """Se o texto menciona 'projeto' + um nome da lista branca, devolve
    (nome, pasta). Senao, None."""
    if "projeto" not in n:
        return None
    projetos = load_projects()
    for nome, pasta in projetos.items():
        if nome in n and os.path.isdir(pasta):
            return nome, pasta
    return None


CONFIRM_WORDS = ["confirma", "confirmo", "confirmado", "pode", "pode sim",
                 "sim", "isso", "manda", "manda ver", "vai", "faz", "faca"]
CANCEL_WORDS = ["cancela", "cancelar", "nao", "deixa", "esquece", "para"]


def is_confirm(n):
    return any(re.fullmatch(rf"{re.escape(w)}[.! ]*", n) or n == w for w in CONFIRM_WORDS)


def is_cancel(n):
    return any(re.fullmatch(rf"{re.escape(w)}[.! ]*", n) or n == w for w in CANCEL_WORDS)


# ------------------------------------------------------------------- roteador
def handle(texto):
    """Tenta resolver com uma habilidade direta. Retorna a resposta em texto,
    ou None se nenhuma habilidade casar (o app cai no cerebro)."""
    n = _norm(texto)
    for skill in (_skill_hora_data, _skill_calculo, _skill_abrir, _skill_notas):
        resposta = skill(texto, n)
        if resposta is not None:
            return resposta
    return None
