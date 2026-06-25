"""Componentes de UI compartilhados entre os elementos.

Reúne o que antes estava duplicado no monolito app_estrutural.py:
- helpers gráficos matplotlib (tema escuro + figuras por elemento);
- tabelas de cargas da NBR 6120:2019;
- render do memorial passo a passo (antes repetido 6x);
- placeholders das abas ainda não construídas (Fatias B e C).
"""
import traceback

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ── helpers gráficos ──────────────────────────────────────────
def dark_fig(w=5, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    for sp in ax.spines.values():
        sp.set_color("#334155")
    ax.tick_params(colors="#94a3b8")
    ax.xaxis.label.set_color("#94a3b8")
    ax.yaxis.label.set_color("#94a3b8")
    ax.title.set_color("#e2e8f0")
    return fig, ax


def fig_secao_pilar(hx, hy, As_adot, escolha):
    fig, ax = dark_fig(3.5, 3.5)
    ax.add_patch(mpatches.FancyBboxPatch((0, 0), hx, hy, boxstyle="square,pad=0",
        linewidth=2, edgecolor="#38bdf8", facecolor="#1e3a5f"))
    c = 3.5
    phi_r = escolha[0][1] / 2 if escolha else 4
    for px, py in [(c, c), (hx - c, c), (c, hy - c), (hx - c, hy - c)]:
        ax.add_patch(plt.Circle((px, py), phi_r, color="#f59e0b", zorder=3))
    ax.set_xlim(-8, hx + 8); ax.set_ylim(-8, hy + 8)
    ax.set_aspect("equal"); ax.axis("off")
    ax.text(hx / 2, -5, f"{hx} cm", color="#94a3b8", ha="center", fontsize=9)
    ax.text(-6, hy / 2, f"{hy} cm", color="#94a3b8", va="center", rotation=90, fontsize=9)
    ax.set_title(f"Seção  As={As_adot:.2f} cm²", fontsize=10, pad=6)
    plt.tight_layout()
    return fig


def fig_diagrama_viga(L, Md, Vd):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))
    fig.patch.set_facecolor("#0f172a")
    x = np.linspace(0, L, 120)
    for ax in (ax1, ax2):
        ax.set_facecolor("#0f172a"); ax.tick_params(colors="#94a3b8")
        for sp in ax.spines.values():
            sp.set_color("#334155")
        ax.axhline(0, color="#475569", lw=0.8)
    M = Md * 4 * x * (L - x) / L**2
    V = Vd * (1 - 2 * x / L)
    ax1.fill_between(x, M, alpha=0.45, color="#38bdf8")
    ax1.plot(x, M, color="#38bdf8", lw=2)
    ax1.set_title("Momento M (kNm)", color="#e2e8f0", fontsize=9)
    ax1.set_xlabel("x (m)", color="#94a3b8")
    ax2.fill_between(x, V, alpha=0.45, color="#f59e0b")
    ax2.plot(x, V, color="#f59e0b", lw=2)
    ax2.set_title("Cortante V (kN)", color="#e2e8f0", fontsize=9)
    ax2.set_xlabel("x (m)", color="#94a3b8")
    plt.tight_layout()
    return fig


def fig_muro(H, Ka, gs, Pa, za, pm):
    fig, ax = dark_fig(5, 5)
    B = pm["B_sapata"]; e_sap = pm["esp_sapata"]
    ponta = pm["comprimento_ponta"]
    e_b = pm["espessura_fuste_base"]; e_t = pm["espessura_fuste_topo"]
    ax.fill_betweenx([0, H], [B, B], [B + B * 0.4, B + B * 0.4], color="#92400e", alpha=0.35, label="Solo")
    ax.add_patch(mpatches.Rectangle((0, 0), B, e_sap, color="#38bdf8", alpha=0.8))
    ax.fill([ponta, ponta + e_b, ponta + e_t, ponta], [e_sap, e_sap, H, H], color="#38bdf8", alpha=0.8)
    p_base = Ka * gs * H
    scl = B * 0.5 / max(p_base, 0.1)
    ax.fill_betweenx([0, H], B, [B + p_base * scl, B], color="#f59e0b", alpha=0.6, label=f"Empuxo Ka={Ka:.3f}")
    ax.annotate(f"Pa={Pa:.1f} kN/m\nza={za:.2f} m", xy=(B + p_base * scl * 0.4, za), color="#fbbf24", fontsize=9)
    ax.set_xlim(-0.1, B * 1.9); ax.set_ylim(-0.15, H * 1.1)
    ax.set_xlabel("Largura (m)"); ax.set_ylabel("Altura (m)")
    ax.set_title("Empuxo de Rankine")
    ax.legend(facecolor="#1e293b", labelcolor="#e2e8f0", fontsize=8)
    plt.tight_layout()
    return fig


# ── tabelas NBR 6120:2019 ─────────────────────────────────────
CARGAS_NBR6120 = {
    "Dormitório / Sala / Corredor interno": 1.5,
    "Banheiro / Cozinha / Copa": 1.5,
    "Área de serviço / Lavanderia": 2.0,
    "Corredor de uso comum": 3.0,
    "Escada de uso comum": 3.0,
    "Garagem (veículos até 30 kN)": 3.0,
    "Sacada / Balcão": 2.5,
    "Cobertura sem acesso": 1.0,
    "Cobertura com acesso": 2.0,
    "Escritório": 2.0,
    "Sala de reuniões": 3.0,
    "Loja comercial (térreo)": 4.0,
    "Biblioteca — depósito": 4.0,
    "Hospital — enfermaria": 2.0,
    "Industrial leve": 5.0,
}
REVESTIMENTOS = {
    "Cerâmica + contrapiso (4 cm)": 1.0,
    "Porcelanato + contrapiso (5 cm)": 1.25,
    "Só contrapiso (3 cm)": 0.6,
    "Madeira + contrapiso": 0.9,
    "Cobertura (telha)": 0.5,
    "Impermeabilização + brita": 1.5,
}
PAREDES = {
    "Sem parede": 0.0,
    "Divisória gesso / drywall": 0.5,
    "Bloco cerâmico 9 cm sem reboco": 1.2,
    "Bloco cerâmico 9 cm com reboco": 1.9,
    "Bloco cerâmico 14 cm com reboco": 2.4,
    "Bloco de concreto 14 cm com reboco": 3.0,
    "Bloco de concreto 19 cm com reboco": 4.0,
    "Tijolo comum com reboco": 2.8,
}


# ── memorial passo a passo (antes duplicado 6x) ───────────────
def render_passos(passos):
    """Renderiza uma lista de Passo (titulo, norma, formula, substituicao,
    resultado, obs) com LaTeX. Antes este loop estava copiado em cada
    elemento da página Memorial."""
    st.divider()
    for p in passos:
        st.markdown("#### " + p.titulo)
        if p.norma:
            st.caption("📖 " + p.norma)
        if p.formula:
            st.latex(p.formula)
        for linha in p.substituicao:
            st.latex(linha)
        if p.resultado:
            st.success(p.resultado)
        if p.obs:
            st.info("💡 " + p.obs)
        st.divider()


def linhas_verificacoes(verificacoes):
    """Monta as linhas do painel valor x LIMITE x status (sem Streamlit).

    Separada do render para ser testavel sem UI. Cada linha traz valor,
    limite, unidade, folga, utilizacao (%) e status legivel. Ref. campos
    de core.resultado.Verificacao (duck typing: nome/valor/limite/unidade/
    operador/status/folga/utilizacao/passou).
    """
    linhas = []
    for v in verificacoes:
        u = f" {v.unidade}" if v.unidade else ""
        op = "≤" if getattr(v, "operador", "<=") == "<=" else "≥"
        util = v.utilizacao
        util_txt = "—" if util == float("inf") else f"{util * 100:.0f}%"
        linhas.append({
            "Verificação": v.nome,
            "Valor": f"{v.valor:.3g}{u}",
            "Limite": f"{op} {v.limite:.3g}{u}",
            "Folga": f"{v.folga:.3g}{u}",
            "Uso": util_txt,
            "Status": "✅ OK" if v.passou else "❌ NÃO OK",
        })
    return linhas


def _tabela_markdown(linhas):
    """Converte as linhas (list de dict) numa tabela markdown.

    Renderizada via st.markdown para NAO depender de pandas/numpy (st.table
    importa pandas, que quebra com ABI numpy incompativel). Tabela pequena e
    so texto, entao markdown e suficiente e robusto.
    """
    if not linhas:
        return ""
    cols = list(linhas[0].keys())
    cabecalho = "| " + " | ".join(cols) + " |"
    separador = "| " + " | ".join("---" for _ in cols) + " |"
    corpo = [
        "| " + " | ".join(str(linha[c]) for c in cols) + " |"
        for linha in linhas
    ]
    return "\n".join([cabecalho, separador, *corpo])


def render_tabela(linhas):
    """Renderiza uma list[dict] como tabela, SEM pandas (via markdown).

    Substituto direto de st.table para list de dicts: st.table importa pandas,
    que quebra com ABI numpy incompativel. Use para qualquer tabela simples de
    texto/numeros (cargas, bitolas, combinacoes...).
    """
    if not linhas:
        return
    st.markdown(_tabela_markdown(linhas))


def render_verificacoes(verificacoes, titulo="Verificações (valor × LIMITE × status)"):
    """Painel unico de verificacoes normativas para qualquer elemento.

    Recebe uma lista de Verificacao (core.resultado) e desenha:
      - banner verde/vermelho com o veredito global;
      - tabela valor x limite x folga x uso x status (markdown, sem pandas).
    Centraliza o que antes era markdown solto e dessincronizado por pagina.
    """
    if not verificacoes:
        return
    st.subheader(titulo)
    reprovadas = [v for v in verificacoes if not v.passou]
    if reprovadas:
        nomes = ", ".join(v.nome for v in reprovadas)
        st.error(f"❌ {len(reprovadas)} verificação(ões) NÃO atendida(s): {nomes}")
    else:
        st.success("✅ Todas as verificações atendidas (ELU + ELS).")
    st.markdown(_tabela_markdown(linhas_verificacoes(verificacoes)))


def show_erro(e):
    """Exibe exceção com traceback — padrão único de erro nas abas."""
    st.error("Erro: " + str(e))
    st.code(traceback.format_exc())


def placeholder(fatia, texto):
    """Aba ainda não construída — sinaliza em qual fatia será entregue."""
    st.info(f"🚧 {texto}\n\n_Em construção — chega na Fatia {fatia}._")
