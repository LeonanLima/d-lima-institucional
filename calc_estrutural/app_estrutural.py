# app_estrutural.py - Interface grafica Streamlit
# Sistema de Calculo Estrutural - NBR 6118:2023
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from dimensionamento.predim import predimensionar_laje, predimensionar_viga, predimensionar_pilar
from dimensionamento.pilar import (calcular_esbeltez, excentricidade_minima,
    excentricidade_2a_ordem, dimensionar_secao, estribo_pilar, escolher_barras, BIBLIOGRAFIA_PILAR)
from dimensionamento.viga import (verificar_bielas, calcular_parcela_concreto,
    dimensionar_estribos, armadura_simples, calcular_flecha_branson, BIBLIOGRAFIA_VIGA)
from dimensionamento.laje import calcular_laje_macica, BIBLIOGRAFIA_LAJE
from dimensionamento.muro_arrimo import (predimensionar_muro, calcular_empuxo,
    verificar_estabilidade, dimensionar_fuste, BIBLIOGRAFIA_MURO)

st.set_page_config(
    page_title="Calc Estrutural - NBR 6118:2023",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.result-box { background:#1e293b; border-radius:8px; padding:16px; margin:8px 0; color:#e2e8f0; }
.ok { color:#22c55e; font-weight:bold; }
.err { color:#ef4444; font-weight:bold; }
.ref { color:#94a3b8; font-size:0.8em; }
h1 { color:#38bdf8; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.title("🏗️ Calc Estrutural")
    st.caption("NBR 6118:2023 | Bastos · Araujo · Caputo")
    st.divider()
    pagina = st.radio("Modulo", [
        "🏠 Inicio",
        "📐 Pre-dimensionamento",
        "🏛️ Pilar",
        "🔧 Viga",
        "🟦 Laje Macica",
        "🧱 Muro de Arrimo",
    ])

# ─── Graficos auxiliares ───────────────────────────────────────
def fig_secao_pilar(hx, hy, As_total, escolha):
    fig, ax = plt.subplots(figsize=(4, 4))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    rect = mpatches.FancyBboxPatch((0, 0), hx, hy,
        boxstyle="square,pad=0", linewidth=2,
        edgecolor="#38bdf8", facecolor="#1e3a5f")
    ax.add_patch(rect)
    # barras nos cantos (simplificado)
    c = 3.5  # cobrimento + estribo + meia barra
    posicoes = [(c, c), (hx-c, c), (c, hy-c), (hx-c, hy-c)]
    if escolha:
        phi = escolha[0][1]
        r = phi / 2
        for i, (px, py) in enumerate(posicoes):
            circ = plt.Circle((px, py), r, color="#f59e0b", zorder=3)
            ax.add_patch(circ)
    ax.set_xlim(-5, hx+5); ax.set_ylim(-5, hy+5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.text(hx/2, -3.5, f"{hx} cm", color="#94a3b8", ha="center", fontsize=9)
    ax.text(-3, hy/2, f"{hy} cm", color="#94a3b8", va="center", rotation=90, fontsize=9)
    ax.set_title("Secao Transversal", color="#e2e8f0", fontsize=10, pad=8)
    plt.tight_layout()
    return fig

def fig_diagrama_muro(H, Ka, gamma, Pa, za, predim):
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    B = predim["B_sapata"]
    e_sap = predim["esp_sapata"]
    e_fuste = predim["espessura_fuste_base"]
    e_topo = predim["espessura_fuste_topo"]
    ponta = predim["comprimento_ponta"]

    # Solo (fundo)
    ax.fill_betweenx([0, H], [B, B], [B+H*0.15, B+H*0.15],
                     color="#92400e", alpha=0.5, label="Solo")
    ax.fill_between([B, B+H*0.15], 0, H, color="#92400e", alpha=0.3)

    # Sapata
    sap = mpatches.Rectangle((0, 0), B, e_sap, color="#38bdf8", alpha=0.8)
    ax.add_patch(sap)
    # Fuste (trapézio)
    fuste_xs = [ponta, ponta+e_fuste, ponta+e_topo, ponta]
    fuste_ys = [e_sap, e_sap, H, H]
    ax.fill(fuste_xs, fuste_ys, color="#38bdf8", alpha=0.8)

    # Diagrama de pressao
    p_base = Ka * gamma * H
    scale = B * 0.6 / max(p_base, 1)
    ax.fill_betweenx([0, H], [B, B], [B + p_base*scale, B],
                     color="#f59e0b", alpha=0.7, label=f"Empuxo (Ka={Ka:.3f})")
    ax.annotate(f"Pa={Pa:.1f} kN/m\nza={za:.2f} m",
                xy=(B + p_base*scale*0.5, za),
                color="#fbbf24", fontsize=9, ha="left")

    ax.set_xlim(-0.1, B*1.8); ax.set_ylim(-0.1, H*1.1)
    ax.set_xlabel("Largura (m)", color="#94a3b8"); ax.set_ylabel("Altura (m)", color="#94a3b8")
    ax.tick_params(colors="#94a3b8")
    ax.set_title("Diagrama de Empuxo - Rankine", color="#e2e8f0", fontsize=10)
    ax.legend(loc="upper right", fontsize=8, facecolor="#1e293b", labelcolor="#e2e8f0")
    for spine in ax.spines.values(): spine.set_color("#334155")
    plt.tight_layout()
    return fig

def fig_diagrama_viga(L, Md_kNm, Vd_kN):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))
    fig.patch.set_facecolor("#0f172a")
    for ax in (ax1, ax2):
        ax.set_facecolor("#0f172a")
        ax.tick_params(colors="#94a3b8")
        for sp in ax.spines.values(): sp.set_color("#334155")

    x = np.linspace(0, L, 100)
    M = Md_kNm * 4 * x * (L - x) / L**2  # parabola
    V = Vd_kN * (1 - 2*x/L)

    ax1.fill_between(x, M, alpha=0.5, color="#38bdf8")
    ax1.plot(x, M, color="#38bdf8", lw=2)
    ax1.axhline(0, color="#475569", lw=0.8)
    ax1.set_title("Diagrama M (kNm)", color="#e2e8f0", fontsize=9)
    ax1.set_xlabel("x (m)", color="#94a3b8")

    ax2.fill_between(x, V, alpha=0.5, color="#f59e0b")
    ax2.plot(x, V, color="#f59e0b", lw=2)
    ax2.axhline(0, color="#475569", lw=0.8)
    ax2.set_title("Diagrama V (kN)", color="#e2e8f0", fontsize=9)
    ax2.set_xlabel("x (m)", color="#94a3b8")

    plt.tight_layout()
    return fig

# ─── Paginas ───────────────────────────────────────────────────

if pagina == "🏠 Inicio":
    st.title("Sistema de Calculo Estrutural")
    st.subheader("NBR 6118:2023 | Uso local")
    st.markdown("""
    **Modulos disponíveis:**
    - 📐 **Pre-dimensionamento** — laje, viga e pilar
    - 🏛️ **Pilar** — esbeltez, pilar-padrao, flexo-compressao, secao grafica
    - 🔧 **Viga** — Modelo I (cortante), flexao simples/dupla, flecha Branson
    - 🟦 **Laje Macica** — Casos 1-6 Carini, armaduras + verificacao flecha
    - 🧱 **Muro de Arrimo** — Rankine, estabilidade FST/FSD, fuste

    **Referencias:**
    - Carini, M.R. (MSc, UFSC) — Metodologia e tabelas
    - Bastos, P.S.S. (Dr., UNESP) — Vigas, pilares, muros
    - Araujo, J.M. (Dr., FURG) — Flecha Branson, detalhamento
    - Caputo, H.P. (Dr., PUC-Rio) — Mecanica dos solos / Rankine
    - Fusco, P.B. (Dr., USP) — Reservatorios, elementos especiais

    Selecione um modulo na barra lateral.
    """)
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Norma principal", "NBR 6118:2023")
    col2.metric("Norma de cargas", "NBR 6120:2019")
    col3.metric("Modulos ativos", "7")

# ─── Pre-dimensionamento ───────────────────────────────────────
elif pagina == "📐 Pre-dimensionamento":
    st.title("📐 Pre-dimensionamento")
    tipo = st.selectbox("Elemento", ["Laje", "Viga", "Pilar"])
    col1, col2 = st.columns(2)
    with col1:
        if tipo == "Laje":
            lx = st.number_input("lx - menor vao (m)", 2.0, 10.0, 4.0, 0.1)
            ly = st.number_input("ly - maior vao (m)", 2.0, 12.0, 5.0, 0.1)
            if st.button("Calcular"):
                r = predimensionar_laje(lx, ly)
                with col2:
                    st.markdown(f"**h adotado:** {r['h_adotado_cm']} cm")
                    st.markdown(f"**Tipo:** {r.get('tipo','')}")
                    st.markdown(f"*{r.get('ref','')}*")
        elif tipo == "Viga":
            L = st.number_input("Vao (m)", 2.0, 12.0, 5.0, 0.1)
            tp = st.selectbox("Tipo", ["continua","simples","balanco"])
            if st.button("Calcular"):
                r = predimensionar_viga(L, tp)
                with col2:
                    st.markdown(f"**Secao:** {r['bw_cm']} x {r['h_adotado_cm']} cm")
                    st.markdown(f"*{r.get('ref','')}*")
        else:
            Nk = st.number_input("Nk acumulado (kN)", 50.0, 5000.0, 500.0, 50.0)
            fck = st.number_input("fck (MPa)", 20, 50, 25)
            tp2 = st.selectbox("Tipo", ["intermediario","extremidade","canto"])
            if st.button("Calcular"):
                r = predimensionar_pilar(Nk, fck, tp2)
                with col2:
                    st.markdown(f"**Ac minima:** {r.get('Ac_min_cm2','?')} cm²")
                    st.markdown(f"*{r.get('ref','')}*")

# ─── Pilar ─────────────────────────────────────────────────────
elif pagina == "🏛️ Pilar":
    st.title("🏛️ Dimensionamento de Pilar")
    st.caption("Metodo Pilar-Padrao | Flexo-compressao Normal | NBR 6118:2023 §11, §17, §18")

    with st.form("form_pilar"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Geometria")
            H  = st.number_input("Altura livre H (cm)", 100, 800, 300, 10)
            hx = st.number_input("hx - dimensao x (cm)", 12, 120, 19, 1)
            hy = st.number_input("hy - dimensao y (cm)", 12, 120, 40, 1)
            beta = st.number_input("beta (coef. flambagem)", 0.5, 2.0, 1.0, 0.1)
        with col2:
            st.subheader("Esforcos")
            Nd = st.number_input("Nd (kN)", 10.0, 10000.0, 450.0, 10.0)
            Md = st.number_input("Md (kNcm)", 0.0, 50000.0, 1200.0, 100.0)
        with col3:
            st.subheader("Material")
            fck = st.number_input("fck (MPa)", 20, 50, 25)
            fyk = st.number_input("fyk (MPa)", 250, 600, 500)
            caa = st.selectbox("CAA", ["I","II","III","IV"])
        calcular = st.form_submit_button("▶ Calcular", use_container_width=True)

    if calcular:
        esb = calcular_esbeltez(H, hx, hy, beta)
        exc = excentricidade_minima(hx, hy)
        nu  = Nd / (hx * hy * fck / 1.4)
        e2x = excentricidade_2a_ordem(esb["lam_x"], hx, nu)
        e2y = excentricidade_2a_ordem(esb["lam_y"], hy, nu)
        dim = dimensionar_secao(Nd, Md, hx, hy, fck, fyk, caa)
        est = estribo_pilar(16.0, min(hx, hy))
        escolha = escolher_barras(dim["As_adot"])

        col1, col2 = st.columns([1, 2])
        with col1:
            st.pyplot(fig_secao_pilar(hx, hy, dim["As_adot"], escolha))

        with col2:
            st.subheader("Esbeltez")
            c1, c2 = st.columns(2)
            c1.metric("λx", f"{esb['lam_x']}", delta=esb['status_x'], delta_color="off")
            c2.metric("λy", f"{esb['lam_y']}", delta=esb['status_y'], delta_color="off")

            st.subheader("Excentricidades")
            st.markdown(f"e1x_min = **{exc['e1x_min']} cm** | e1y_min = **{exc['e1y_min']} cm**")
            st.markdown(f"e2x (2ª ordem) = **{e2x} cm** | e2y = **{e2y} cm**")

            st.subheader("Armadura")
            st.markdown(f"As calculado = **{dim['As_calc']} cm²** | As mínimo = **{dim['As_min']} cm²**")
            st.success(f"✅ As adotado = **{dim['As_adot']} cm²** | Domínio {dim['dominio']}")

            st.subheader("Sugestoes de armadura")
            rows = []
            for n, phi, ap in escolha:
                rows.append({"Qtd": n, "Diametro (mm)": phi, "As_prov (cm²)": ap})
            st.table(rows)

            st.subheader("Estribos")
            st.markdown(f"Ø{est['phi_est_mm']}mm | s = {est['s_max_cm']} cm | s_red = {est['s_red_cm']} cm")

        with st.expander("Referencias bibliograficas"):
            st.text(BIBLIOGRAFIA_PILAR)

# ─── Viga ──────────────────────────────────────────────────────
elif pagina == "🔧 Viga":
    st.title("🔧 Dimensionamento de Viga")
    st.caption("Modelo I (cortante) | Flexao simples | Flecha Branson | NBR 6118:2023 §17, §18")

    with st.form("form_viga"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Geometria")
            bw = st.number_input("bw - largura (cm)", 10, 60, 14, 1)
            h  = st.number_input("h - altura (cm)", 20, 120, 40, 5)
            L  = st.number_input("L - vao (m)", 1.0, 12.0, 4.0, 0.1)
        with col2:
            st.subheader("Esforcos (ELU)")
            Md_kNm = st.number_input("Md (kNm)", 1.0, 1000.0, 45.0, 1.0)
            Vd_kN  = st.number_input("Vd (kN)", 1.0, 500.0, 55.0, 1.0)
        with col3:
            st.subheader("Material")
            fck  = st.number_input("fck (MPa)", 20, 50, 25)
            fyk  = st.number_input("fyk (MPa)", 250, 600, 500)
            caa2 = st.selectbox("CAA", ["I","II","III","IV"])
            q_ser = st.number_input("q serv. (kN/m, ELS)", 0.0, 200.0, 18.0, 1.0)
        calcular2 = st.form_submit_button("▶ Calcular", use_container_width=True)

    if calcular2:
        d = h - 5.0
        biel = verificar_bielas(Vd_kN, bw, d, fck)
        Vc   = calcular_parcela_concreto(bw, d, fck)
        est2 = dimensionar_estribos(Vd_kN, bw, d, fck, fyk)
        flex = armadura_simples(Md_kNm*100, d, bw, fck)
        ela  = calcular_flecha_branson(q_ser, flex["As_cm2"], d, h, bw, L, fck)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.pyplot(fig_diagrama_viga(L, Md_kNm, Vd_kN))

        with col2:
            ok = "✅" if biel["ok"] else "❌"
            st.subheader(f"Bielas comprimidas {ok}")
            st.markdown(f"VRd2 = **{biel['VRd2']:.1f} kN** | Vd = {Vd_kN:.1f} kN | αv2 = {biel['alphav2']:.3f}")

            st.subheader("Cisalhamento — Estribos")
            st.markdown(f"Vc = **{Vc:.1f} kN** | Asw/s = **{est2['Asw_s']:.4f} cm²/cm**")
            st.success(f"Sugestao: {est2['sugestao']}")

            st.subheader("Flexao")
            st.markdown(f"As = **{flex['As_cm2']:.2f} cm²** | x = {flex['x_cm']:.2f} cm | x/d = {flex['x_cm']/d:.3f}")

            st.subheader("Flecha ELS (Branson)")
            ok_f = "✅" if ela["ok"] else "❌"
            st.markdown(f"δ_t = **{ela['delta_t']:.3f} cm** | lim = {ela['lim_cm']:.3f} cm | {ok_f}")

        with st.expander("Referencias"):
            st.text(BIBLIOGRAFIA_VIGA)

# ─── Laje ──────────────────────────────────────────────────────
elif pagina == "🟦 Laje Macica":
    st.title("🟦 Laje Macica Bidirecional")
    st.caption("Tabela de coeficientes Carini — Casos 1-6 | NBR 6118:2023 §19")

    casos_desc = {
        1:"Caso 1 — 4 bordas apoiadas",
        2:"Caso 2 — 3 ap. + 1 eng. (ly)",
        "2A":"Caso 2A — 3 ap. + 1 eng. (lx)",
        3:"Caso 3 — 2 ap. + 2 eng. opostos (ly)",
        "3A":"Caso 3A — 2 ap. + 2 eng. opostos (lx)",
        4:"Caso 4 — 2 ap. + 2 eng. adjacentes",
        5:"Caso 5 — 1 ap. + 3 eng.",
        "5A":"Caso 5A — 1 ap. + 3 eng. (alt.)",
        6:"Caso 6 — 4 bordas engastadas",
    }

    with st.form("form_laje"):
        col1, col2, col3 = st.columns(3)
        with col1:
            lx = st.number_input("lx - menor vao (m)", 1.5, 8.0, 3.5, 0.1)
            ly = st.number_input("ly - maior vao (m)", 1.5, 10.0, 4.5, 0.1)
            h_cm = st.number_input("h - espessura (cm)", 8, 30, 10, 1)
        with col2:
            gk = st.number_input("gk (kN/m²)", 0.5, 20.0, 1.5, 0.1)
            qk = st.number_input("qk (kN/m²)", 0.5, 20.0, 1.5, 0.1)
            caso_str = st.selectbox("Caso de vinculacao", list(casos_desc.keys()),
                                    format_func=lambda x: casos_desc[x])
        with col3:
            fck3 = st.number_input("fck (MPa)", 20, 50, 25)
            fyk3 = st.number_input("fyk (MPa)", 250, 600, 500)
            caa3 = st.selectbox("CAA", ["I","II","III","IV"])
        calcular3 = st.form_submit_button("▶ Calcular", use_container_width=True)

    if calcular3:
        try:
            caso_key = int(caso_str) if str(caso_str).isdigit() else caso_str
            r = calcular_laje_macica(lx, ly, h_cm, gk, qk, caso_key, fck3, fyk3, caa3)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Momentos (kNm/m)")
                mts = {
                    "Mdx (+)": r.get("Mdx",0),
                    "Mdy (+)": r.get("Mdy",0),
                    "Mdxe (-)": r.get("Mdxe",0),
                    "Mdye (-)": r.get("Mdye",0),
                }
                for k, v in mts.items():
                    if v: st.metric(k, f"{v:.2f}")
            with col2:
                st.subheader("Armaduras (cm²/m)")
                arm = r.get("armaduras", {})
                for nome, dados in arm.items():
                    if isinstance(dados, dict):
                        As = dados.get("As_cm2", 0)
                        st.metric(nome, f"{As:.2f}" if As else "As_min")
                st.subheader("Flecha ELS")
                els = r.get("els_flecha", {})
                ok_l = "✅" if els.get("ok") else "❌"
                st.markdown(f"δ_t = **{els.get('delta_t_cm',0):.3f} cm** {ok_l}")
        except Exception as e:
            st.error(f"Erro: {e}")

        with st.expander("Referencias"):
            st.text(BIBLIOGRAFIA_LAJE)

# ─── Muro ──────────────────────────────────────────────────────
elif pagina == "🧱 Muro de Arrimo":
    st.title("🧱 Muro de Arrimo")
    st.caption("Empuxo de Rankine | Estabilidade FST/FSD | NBR 6118:2023 | Caputo · Bastos · Araujo")

    with st.form("form_muro"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Geometria / Solo")
            H_m = st.number_input("H - altura do muro (m)", 1.0, 8.0, 3.0, 0.5)
            phi  = st.number_input("phi - angulo de atrito (°)", 15.0, 45.0, 30.0, 1.0)
            gs   = st.number_input("gamma solo (kN/m³)", 14.0, 22.0, 18.0, 0.5)
            qs   = st.number_input("Sobrecarga qs (kN/m²)", 0.0, 30.0, 0.0, 1.0)
        with col2:
            st.subheader("Concreto")
            fck4 = st.number_input("fck (MPa)", 20, 40, 25)
            fyk4 = st.number_input("fyk (MPa)", 250, 600, 500)
            caa4 = st.selectbox("CAA", ["II","III","IV"])
        with col3:
            st.subheader("")
        calcular4 = st.form_submit_button("▶ Calcular", use_container_width=True)

    if calcular4:
        pm  = predimensionar_muro(H_m, phi, gs)
        emp = calcular_empuxo(H_m, gs, phi, 0.0, qs)
        est = verificar_estabilidade(pm, emp, gs)
        fus = dimensionar_fuste(pm, emp, fck4, fyk4, caa4)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.pyplot(fig_diagrama_muro(H_m, emp["Ka"], gs, emp["Pa_total"], emp["za"], pm))

        with col2:
            st.subheader("Empuxo (Rankine)")
            c1, c2, c3 = st.columns(3)
            c1.metric("Ka", f"{emp['Ka']:.4f}")
            c2.metric("Pa total", f"{emp['Pa_total']:.1f} kN/m")
            c3.metric("za", f"{emp['za']:.2f} m")

            st.subheader("Estabilidade")
            c1, c2 = st.columns(2)
            fst_ok = "✅" if est["FST_ok"] else "❌"
            fsd_ok = "✅" if est["FSD_ok"] else "❌"
            c1.metric(f"FST (tombamento) {fst_ok}", f"{est['FST']:.3f}", delta="≥ 1.5")
            c2.metric(f"FSD (deslizamento) {fsd_ok}", f"{est['FSD']:.3f}", delta="≥ 1.5")

            if not est["FSD_ok"]:
                st.warning("⚠️ FSD < 1.5 — aumentar a base B (calcanheira maior) ou adicionar chave de cisalhamento.")

            st.subheader("Dimensionamento do Fuste")
            if "erro" in fus:
                st.error(fus["erro"])
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Md", f"{fus['Md_kNm']:.2f} kNm/m")
                c2.metric("Vd", f"{fus['Vd_kN']:.2f} kN/m")
                c3.metric("As vertical", f"{fus['As_cm2m']:.2f} cm²/m")

        with st.expander("Pre-dimensionamento geometrico"):
            st.json(pm)

        with st.expander("Referencias bibliograficas"):
            st.text(BIBLIOGRAFIA_MURO)
