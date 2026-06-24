import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from relatorio.passo_a_passo import memorial_laje, memorial_viga, memorial_pilar, memorial_muro, memorial_reservatorio, memorial_piscina

from dimensionamento.predim import predimensionar_laje, predimensionar_viga, predimensionar_pilar
from dimensionamento.pilar import (
    calcular_esbeltez, excentricidade_minima, excentricidade_2a_ordem,
    dimensionar_secao, momento_total_pilar, estribo_pilar, escolher_barras,
    BIBLIOGRAFIA_PILAR,
)
from dimensionamento.viga import (
    verificar_bielas, calcular_parcela_concreto, dimensionar_estribos,
    armadura_simples, calcular_flecha_branson, as_minima_viga, BIBLIOGRAFIA_VIGA,
)
from dimensionamento.laje import calcular_laje_macica, BIBLIOGRAFIA_LAJE
from dimensionamento.muro_arrimo import (
    predimensionar_muro, calcular_empuxo, verificar_estabilidade,
    dimensionar_fuste, BIBLIOGRAFIA_MURO,
)

st.set_page_config(page_title="Calc Estrutural NBR 6118:2023",
                   page_icon="🏗️", layout="wide",
                   initial_sidebar_state="expanded")

with st.sidebar:
    st.title("🏗️ Calc Estrutural")
    st.caption("NBR 6118:2023 · NBR 6120:2019")
    st.divider()
    pagina = st.radio("Módulo", [
        "🏠  Início",
        "⚖️  Levantamento de Cargas",
        "📋  Memorial de Cálculo",
        "📐  Pré-dimensionamento",
        "🏛️  Pilar",
        "🔧  Viga",
        "🟦  Laje Maciça",
        "🧱  Muro de Arrimo",
    ])

# ── helpers gráficos ──────────────────────────────────────────
def _dark_fig(w=5, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    for sp in ax.spines.values(): sp.set_color("#334155")
    ax.tick_params(colors="#94a3b8")
    ax.xaxis.label.set_color("#94a3b8")
    ax.yaxis.label.set_color("#94a3b8")
    ax.title.set_color("#e2e8f0")
    return fig, ax

def fig_secao_pilar(hx, hy, As_adot, escolha):
    fig, ax = _dark_fig(3.5, 3.5)
    ax.add_patch(mpatches.FancyBboxPatch((0,0), hx, hy, boxstyle="square,pad=0",
        linewidth=2, edgecolor="#38bdf8", facecolor="#1e3a5f"))
    c = 3.5
    phi_r = escolha[0][1]/2 if escolha else 4
    for px, py in [(c,c),(hx-c,c),(c,hy-c),(hx-c,hy-c)]:
        ax.add_patch(plt.Circle((px,py), phi_r, color="#f59e0b", zorder=3))
    ax.set_xlim(-8, hx+8); ax.set_ylim(-8, hy+8)
    ax.set_aspect("equal"); ax.axis("off")
    ax.text(hx/2, -5, f"{hx} cm", color="#94a3b8", ha="center", fontsize=9)
    ax.text(-6, hy/2, f"{hy} cm", color="#94a3b8", va="center", rotation=90, fontsize=9)
    ax.set_title(f"Seção  As={As_adot:.2f} cm²", fontsize=10, pad=6)
    plt.tight_layout()
    return fig

def fig_diagrama_viga(L, Md, Vd):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))
    fig.patch.set_facecolor("#0f172a")
    x = np.linspace(0, L, 120)
    for ax in (ax1, ax2):
        ax.set_facecolor("#0f172a"); ax.tick_params(colors="#94a3b8")
        for sp in ax.spines.values(): sp.set_color("#334155")
        ax.axhline(0, color="#475569", lw=0.8)
    M = Md * 4 * x * (L - x) / L**2
    V = Vd * (1 - 2*x/L)
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
    fig, ax = _dark_fig(5, 5)
    B = pm["B_sapata"]; e_sap = pm["esp_sapata"]
    ponta = pm["comprimento_ponta"]
    e_b = pm["espessura_fuste_base"]; e_t = pm["espessura_fuste_topo"]
    ax.fill_betweenx([0,H],[B,B],[B+B*0.4,B+B*0.4],color="#92400e",alpha=0.35,label="Solo")
    ax.add_patch(mpatches.Rectangle((0,0),B,e_sap,color="#38bdf8",alpha=0.8))
    ax.fill([ponta,ponta+e_b,ponta+e_t,ponta],[e_sap,e_sap,H,H],color="#38bdf8",alpha=0.8)
    p_base = Ka * gs * H
    scl = B * 0.5 / max(p_base, 0.1)
    ax.fill_betweenx([0,H],B,[B+p_base*scl,B],color="#f59e0b",alpha=0.6,label=f"Empuxo Ka={Ka:.3f}")
    ax.annotate(f"Pa={Pa:.1f} kN/m\nza={za:.2f} m",xy=(B+p_base*scl*0.4,za),color="#fbbf24",fontsize=9)
    ax.set_xlim(-0.1,B*1.9); ax.set_ylim(-0.15,H*1.1)
    ax.set_xlabel("Largura (m)"); ax.set_ylabel("Altura (m)")
    ax.set_title("Empuxo de Rankine")
    ax.legend(facecolor="#1e293b",labelcolor="#e2e8f0",fontsize=8)
    plt.tight_layout()
    return fig

# ── tabelas NBR 6120 ──────────────────────────────────────────
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

# ═══════════════════════════════════════════════════════════════
if pagina == "🏠  Início":
    st.title("Sistema de Cálculo Estrutural")
    st.subheader("NBR 6118:2023 + NBR 6120:2019 — Uso local")
    c1, c2, c3 = st.columns(3)
    c1.metric("Norma principal", "NBR 6118:2023")
    c2.metric("Norma de cargas", "NBR 6120:2019")
    c3.metric("Módulos", "6 ativos")
    st.divider()
    st.markdown("""
**Fluxo recomendado:**
1. **⚖️ Levantamento de Cargas** — gk + qk por ambiente, cargas nas vigas
2. **📐 Pré-dimensionamento** — espessura de laje, seção de viga e pilar
3. **🟦 Laje** → **🔧 Viga** → **🏛️ Pilar** → **🧱 Muro**

| Autor | Obra |
|---|---|
| Carini, M.R. (MSc, UFSC) | Tabelas de coeficientes — lajes e pilares |
| Bastos, P.S.S. (Dr., UNESP) | Vigas, pilares, muros |
| Araujo, J.M. (Dr., FURG) | Curso de Concreto Armado v.1–4 |
| Caputo, H.P. (Dr., PUC-Rio) | Mecânica dos Solos |
| Fusco, P.B. (Dr., USP) | Estruturas especiais |
""")

elif pagina == "⚖️  Levantamento de Cargas":
    st.title("⚖️ Levantamento de Cargas")
    st.caption("NBR 6120:2019 · NBR 16868-1:2020 · gf = 1,4 (combinação normal ELU)")
    tab1, tab2, tab3 = st.tabs(["📋 Cargas na Laje","📏 Cargas na Viga","📊 Tabela NBR 6120"])

    with tab1:
        st.subheader("Cargas na laje — por m²")
        c1, c2 = st.columns(2)
        with c1:
            h_laje = st.number_input("Espessura da laje h (cm)", 8, 30, 10, 1)
            pp_l   = round(25.0 * h_laje / 100, 2)
            st.metric("Peso próprio PP", f"{pp_l:.2f} kN/m²")
            rev_tipo = st.selectbox("Tipo de revestimento", list(REVESTIMENTOS.keys()))
            rev = REVESTIMENTOS[rev_tipo]
            st.metric("Revestimento", f"{rev:.2f} kN/m²")
            forro = st.number_input("Forro / instalações (kN/m²)", 0.0, 1.0, 0.15, 0.05)
            gk = round(pp_l + rev + forro, 2)
            st.success(f"**gk total = {gk:.2f} kN/m²**")
        with c2:
            uso = st.selectbox("Uso do ambiente", list(CARGAS_NBR6120.keys()))
            qk  = CARGAS_NBR6120[uso]
            st.metric("qk (NBR 6120:2019)", f"{qk:.1f} kN/m²")
            fd  = round(1.4 * (gk + qk), 2)
            psi2 = st.selectbox("psi2 (ELS)", [0.3, 0.4, 0.6],
                format_func=lambda x: {0.3:"0,3 residencial",0.4:"0,4 comercial",0.6:"0,6 garagem"}[x])
            fd_ser = round(gk + psi2 * qk, 2)
            st.success(f"**fd (ELU) = {fd:.2f} kN/m²**")
            st.info(f"fd,ser (ELS) = {fd_ser:.2f} kN/m²")
            st.divider()
            st.markdown(f"| Parcela | Valor |\n|---|---|\n"
                        f"| PP laje ({h_laje} cm) | {pp_l:.2f} kN/m² |\n"
                        f"| {rev_tipo} | {rev:.2f} kN/m² |\n"
                        f"| Forro/inst. | {forro:.2f} kN/m² |\n"
                        f"| **gk total** | **{gk:.2f} kN/m²** |\n"
                        f"| qk | {qk:.1f} kN/m² |\n"
                        f"| **fd = 1,4(gk+qk)** | **{fd:.2f} kN/m²** |\n"
                        f"| fd,ser | {fd_ser:.2f} kN/m² |")

    with tab2:
        st.subheader("Cargas na viga — por metro linear (kN/m)")
        c1, c2 = st.columns(2)
        with c1:
            bw_v = st.number_input("bw viga (cm)", 10, 50, 14, 1)
            hv_c = st.number_input("h viga (cm)", 20, 120, 40, 5)
            pp_v = round(bw_v/100 * hv_c/100 * 25, 2)
            st.metric("PP viga", f"{pp_v:.2f} kN/m")
            par_tipo = st.selectbox("Tipo de parede", list(PAREDES.keys()))
            gamma_alv = PAREDES[par_tipo]
            h_par = st.number_input("Altura da parede (m)", 0.0, 5.0, 2.75, 0.05)
            q_par = round(gamma_alv * h_par, 2)
            st.metric("Carga de alvenaria", f"{q_par:.2f} kN/m")
        with c2:
            st.markdown("**Reações das lajes sobre a viga**")
            n_lajes = st.number_input("Número de lajes", 1, 4, 1, 1)
            reacoes = []
            for i in range(int(n_lajes)):
                rv = st.number_input(f"Reação laje {i+1} (kN/m)", 0.0, 200.0, 10.0, 0.5, key=f"rl{i}")
                reacoes.append(rv)
            soma_rl = round(sum(reacoes), 2)
            q_total = round(pp_v + q_par + soma_rl, 2)
            fd_v    = round(1.4 * q_total, 2)
            st.success(f"**q total = {q_total:.2f} kN/m**")
            st.success(f"**fd (ELU) = {fd_v:.2f} kN/m**")
            st.divider()
            st.markdown(f"| Parcela | Valor |\n|---|---|\n"
                        f"| PP viga {bw_v}x{hv_c} cm | {pp_v:.2f} kN/m |\n"
                        f"| Alvenaria | {q_par:.2f} kN/m |\n"
                        f"| Reacoes lajes | {soma_rl:.2f} kN/m |\n"
                        f"| **q total** | **{q_total:.2f} kN/m** |\n"
                        f"| **fd = 1,4 x q** | **{fd_v:.2f} kN/m** |")

    with tab3:
        st.subheader("Cargas variáveis mínimas — NBR 6120:2019, Tabela 2")
        st.table([{"Uso / Ambiente": k, "qk (kN/m2)": v} for k, v in CARGAS_NBR6120.items()])

elif pagina == "📐  Pré-dimensionamento":
    st.title("📐 Pré-dimensionamento")
    st.caption("NBR 6118:2023 §13.2 | Carini 2023")
    tipo = st.selectbox("Elemento", ["Laje","Viga","Pilar"])
    c1, c2 = st.columns(2)
    with c1:
        if tipo == "Laje":
            lx = st.number_input("lx (m)", 1.5, 10.0, 4.0, 0.1)
            ly = st.number_input("ly (m)", 1.5, 12.0, 5.0, 0.1)
            if st.button("Calcular"):
                r = predimensionar_laje(lx, ly)
                with c2:
                    st.metric("h adotado", f"{r['h_adotado_cm']} cm")
                    st.markdown(f"Tipo: **{r.get('tipo','')}**"); st.caption(r.get("ref",""))
        elif tipo == "Viga":
            L  = st.number_input("Vão (m)", 1.0, 12.0, 5.0, 0.1)
            tp = st.selectbox("Tipo", ["continua","simples","balanco"])
            if st.button("Calcular"):
                r = predimensionar_viga(L, tp)
                with c2:
                    st.metric("Seção", f"{r['bw_cm']} x {r['h_adotado_cm']} cm"); st.caption(r.get("ref",""))
        else:
            Nk  = st.number_input("Nk (kN)", 50.0, 8000.0, 500.0, 50.0)
            fck = st.number_input("fck (MPa)", 20, 50, 25)
            tp2 = st.selectbox("Tipo", ["intermediario","extremidade","canto"])
            if st.button("Calcular"):
                r = predimensionar_pilar(Nk, fck, tp2)
                with c2:
                    st.metric("Ac mínima", f"{r.get('Ac_min_cm2','?')} cm²"); st.caption(r.get("ref",""))

elif pagina == "🏛️  Pilar":
    st.title("🏛️ Pilar — Flexo-compressão")
    st.caption("Método Pilar-Padrão | NBR 6118:2023 §11, §17, §18 | Carini · Bastos · Araujo")
    with st.form("pilar"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Geometria")
            H    = st.number_input("H livre (cm)", 100, 800, 300, 10)
            hx   = st.number_input("hx (cm)", 12, 120, 19, 1)
            hy   = st.number_input("hy (cm)", 12, 120, 40, 1)
            beta = st.number_input("beta flambagem", 0.5, 2.0, 1.0, 0.1)
        with c2:
            st.subheader("Esforços (ELU)")
            Nd = st.number_input("Nd (kN)", 10.0, 10000.0, 450.0, 10.0)
            Md = st.number_input("Md (kNcm)", 0.0, 50000.0, 1200.0, 100.0)
        with c3:
            st.subheader("Material")
            fck = st.number_input("fck (MPa)", 20, 50, 25)
            fyk = st.number_input("fyk (MPa)", 250, 600, 500)
            caa = st.selectbox("CAA", ["I","II","III","IV"])
        ok_p = st.form_submit_button("Calcular", use_container_width=True)
    if ok_p:
        try:
            esb     = calcular_esbeltez(H, hx, hy, beta)
            exc     = excentricidade_minima(hx, hy)
            mt      = momento_total_pilar(Nd, Md, H, hx, hy, beta, fck)
            e2x, e2y = mt["e2x"], mt["e2y"]
            # Dimensiona com o momento TOTAL (e1+e2), nao com o Md cru
            dim     = dimensionar_secao(Nd, mt["Md_design"], hx, hy, fck, fyk, caa)
            est     = estribo_pilar(16.0, min(hx, hy))
            escolha = escolher_barras(dim["As_adot"])
            col1, col2 = st.columns([1, 2])
            with col1:
                st.pyplot(fig_secao_pilar(hx, hy, dim["As_adot"], escolha))
            with col2:
                st.subheader("Esbeltez")
                ca, cb = st.columns(2)
                ca.metric("lambda_x", f"{esb['lam_x']:.1f}", delta=esb["status_x"], delta_color="off")
                cb.metric("lambda_y", f"{esb['lam_y']:.1f}", delta=esb["status_y"], delta_color="off")
                st.subheader("Excentricidades")
                st.markdown(f"e1x_min={exc['e1x_min']} cm | e1y_min={exc['e1y_min']} cm | e2x={e2x} cm | e2y={e2y} cm")
                st.caption(f"Md informado={Md:.0f} kNcm → **Md,tot (e₁+e₂)={mt['Md_design']:.0f} kNcm** (dimensiona com este)")
                st.subheader("Armadura longitudinal")
                duc = "✅" if dim["ok_ductil"] else "⚠️"
                st.success(f"**As = {dim['As_adot']:.2f} cm²** | Domínio {dim['dominio']} {duc} | As_min={dim['As_min']:.2f} | As_max={dim['As_max']:.2f} cm²")
                st.subheader("Sugestões de barras")
                st.table([{"n": n, "Ø mm": phi, "As prov cm2": ap} for n, phi, ap in escolha])
                st.subheader("Estribos")
                st.markdown(f"Ø{est['phi_est_mm']:.0f} mm | s={est['s_max_cm']} cm | s_red={est['s_red_cm']} cm")
            with st.expander("Referências"):
                st.text(BIBLIOGRAFIA_PILAR)
        except Exception as e:
            st.error(f"Erro: {e}")
            import traceback; st.code(traceback.format_exc())

elif pagina == "🔧  Viga":
    st.title("🔧 Viga — Cisalhamento + Flexão + Flecha")
    st.caption("Modelo I (cortante) | Armadura simples | Branson ELS | NBR 6118:2023 §17, §18")
    with st.form("viga"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Geometria")
            bw  = st.number_input("bw (cm)", 10, 60, 14, 1)
            hv  = st.number_input("h (cm)", 20, 120, 40, 5)
            L_m = st.number_input("L vão (m)", 1.0, 12.0, 4.0, 0.1)
        with c2:
            st.subheader("Esforços (ELU)")
            Md_kNm = st.number_input("Md (kNm)", 1.0, 2000.0, 45.0, 1.0)
            Vd_kN  = st.number_input("Vd (kN)", 1.0, 1000.0, 55.0, 1.0)
        with c3:
            st.subheader("Material + ELS")
            fck   = st.number_input("fck (MPa)", 20, 50, 25)
            fyk   = st.number_input("fyk (MPa)", 250, 600, 500)
            caa   = st.selectbox("CAA", ["I","II","III","IV"])
            q_ser = st.number_input("q serv. ELS (kN/m)", 0.5, 300.0, 18.0, 0.5)
        ok_v = st.form_submit_button("Calcular", use_container_width=True)
    if ok_v:
        try:
            d = hv - 5.0
            biel  = verificar_bielas(Vd_kN, bw, d, fck)
            Vc    = calcular_parcela_concreto(bw, d, fck)["Vc"]
            est2  = dimensionar_estribos(Vd_kN, bw, d, fck, fyk)
            # armadura_simples(Md_kNcm, b_cm, d_cm, fck, fyk)
            flex  = armadura_simples(Md_kNm * 100, bw, d, fck, fyk)
            # flecha bi-apoiada: Md_ser = q*L^2/8 em kNcm
            Md_ser = q_ser * L_m**2 / 8 * 100
            As_ok  = flex.get("As_cm2", 0.01)
            # calcular_flecha_branson(Md_ser_kNcm, As_cm2, bw_cm, h_cm, d_cm, L_m, fck)
            ela = calcular_flecha_branson(Md_ser, As_ok, bw, hv, d, L_m, fck)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.pyplot(fig_diagrama_viga(L_m, Md_kNm, Vd_kN))
            with col2:
                biel_s = "✅ OK" if biel["ok"] else "❌ Aumentar seção"
                st.subheader("Bielas comprimidas")
                st.markdown(f"VRd2={biel['VRd2']:.1f} kN | Vd={Vd_kN:.1f} kN | av2={biel['alphav2']:.3f}  {biel_s}")
                st.subheader("Estribos (Modelo I)")
                st.markdown(f"Vc={Vc:.1f} kN | Asw/s={est2['Asw_s']:.4f} cm²/cm")
                sug = est2.get("sugestoes",[])
                if sug:
                    st.table([{"Ø mm": s["phi_mm"],"s cm": s["s_cm"],"Asw/s prov": s["Asw_s_prov"]} for s in sug])
                st.subheader("Flexão")
                if "erro" in flex:
                    st.warning(f"Armadura dupla necessária — Md={Md_kNm:.1f} kNm > Md,duc={flex['Md_duc']/100:.1f} kNm")
                else:
                    duc = "✅" if flex["ok_ductil"] else "⚠️ x>xlim"
                    asm = as_minima_viga(bw, d, fck, fyk)
                    As_adot = max(flex["As_cm2"], asm["As_min"])
                    st.success(f"**As={As_adot:.2f} cm²** (As,mín={asm['As_min']:.2f}) | x={flex['x_cm']:.2f} cm | xlim={flex['x_lim']:.2f} cm  {duc}")
                st.subheader("Flecha ELS (Branson)")
                wt   = ela.get("w_total_mm", ela.get("delta_t", 0))
                wlim = ela.get("wadm_mm", ela.get("lim_cm", 0))
                f_ok = "✅" if ela.get("ok") else "❌ Aumentar h"
                st.markdown(f"delta_total={wt:.2f} mm | lim={wlim:.2f} mm  {f_ok}")
            with st.expander("Referências"):
                st.text(BIBLIOGRAFIA_VIGA)
        except Exception as e:
            st.error(f"Erro: {e}")
            import traceback; st.code(traceback.format_exc())

elif pagina == "🟦  Laje Maciça":
    st.title("🟦 Laje Maciça Bidirecional")
    st.caption("Coeficientes Carini — Casos 1-6 | NBR 6118:2023 §19")
    CASOS = {1:"Caso 1 — 4 bordas apoiadas",2:"Caso 2 — 3 ap.+1 eng.(ly)",
             "2A":"Caso 2A — 3 ap.+1 eng.(lx)",3:"Caso 3 — 2 ap.+2 eng. opostos (ly)",
             "3A":"Caso 3A — 2 ap.+2 eng. opostos (lx)",4:"Caso 4 — 2 ap.+2 eng. adjacentes",
             5:"Caso 5 — 1 ap.+3 eng.","5A":"Caso 5A — 1 ap.+3 eng.(alt.)",
             6:"Caso 6 — 4 bordas engastadas"}
    with st.form("laje"):
        c1, c2, c3 = st.columns(3)
        with c1:
            lx   = st.number_input("lx (m)", 1.5, 8.0, 3.5, 0.1)
            ly   = st.number_input("ly (m)", 1.5, 10.0, 4.5, 0.1)
            h_cm = st.number_input("h (cm)", 8, 30, 10, 1)
        with c2:
            gk   = st.number_input("gk (kN/m²)", 0.5, 20.0, 1.5, 0.1)
            qk   = st.number_input("qk (kN/m²)", 0.5, 20.0, 1.5, 0.1)
            caso = st.selectbox("Caso", list(CASOS.keys()), format_func=lambda k: CASOS[k])
        with c3:
            fck  = st.number_input("fck (MPa)", 20, 50, 25)
            fyk  = st.number_input("fyk (MPa)", 250, 600, 500)
            caa  = st.selectbox("CAA", ["I","II","III","IV"])
            psi2 = st.selectbox("ψ₂ (ELS)", [0.3, 0.4, 0.6],
                                format_func=lambda v: {0.3:"0,3 residencial",
                                0.4:"0,4 comercial/escritório",
                                0.6:"0,6 garagem/biblioteca"}[v])
        ok_l = st.form_submit_button("Calcular", use_container_width=True)
    if ok_l:
        try:
            r = calcular_laje_macica(lx, ly, h_cm, gk, qk, caso, fck, fyk, caa, psi2)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Momentos (kNm/m)")
                for nome, val in r.get("momentos",{}).items():
                    if val: st.metric(nome.replace("_"," "), f"{val:.2f}")
                st.subheader("Reações (kN/m)")
                for nome, val in r.get("reacoes",{}).items():
                    if val: st.metric(nome, f"{val:.2f}")
            with col2:
                st.subheader("Armaduras (cm²/m)")
                for nome, dados in r.get("armaduras",{}).items():
                    if isinstance(dados, dict):
                        As = dados.get("As_cm2",0)
                        if As: st.metric(nome.replace("_"," "), f"{As:.2f} cm²/m")
                st.subheader("Flecha ELS")
                els = r.get("els_flecha",{})
                wt   = els.get("w_total_mm",0)
                wadm = els.get("wadm_mm",0)
                f_ok = "✅" if els.get("ok") else "❌ Aumentar espessura"
                st.metric("delta_total", f"{wt:.2f} mm")
                st.metric("delta_adm L/250", f"{wadm:.2f} mm")
                st.markdown(f"**{f_ok}**")
            with st.expander("Referências"):
                st.text(BIBLIOGRAFIA_LAJE)
        except Exception as e:
            st.error(f"Erro: {e}")
            import traceback; st.code(traceback.format_exc())

elif pagina == "🧱  Muro de Arrimo":
    st.title("🧱 Muro de Arrimo")
    st.caption("Rankine | FST >= 1,5 | FSD >= 1,5 | Caputo · Bastos · NBR 6118:2023")
    with st.form("muro"):
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Solo / Geometria")
            H_m = st.number_input("H muro (m)", 1.0, 8.0, 3.0, 0.5)
            phi = st.number_input("fi atrito (graus)", 15.0, 45.0, 30.0, 1.0)
            gs  = st.number_input("gama solo (kN/m3)", 14.0, 22.0, 18.0, 0.5)
            qs  = st.number_input("Sobrecarga qs (kN/m2)", 0.0, 30.0, 0.0, 1.0)
        with c2:
            st.subheader("Concreto")
            fck4 = st.number_input("fck (MPa)", 20, 40, 25)
            fyk4 = st.number_input("fyk (MPa)", 250, 600, 500)
            caa4 = st.selectbox("CAA", ["II","III","IV"])
        ok_m = st.form_submit_button("Calcular", use_container_width=True)
    if ok_m:
        try:
            pm  = predimensionar_muro(H_m, phi, gs)
            emp = calcular_empuxo(H_m, gs, phi, 0.0, qs)
            est = verificar_estabilidade(pm, emp, gs)
            fus = dimensionar_fuste(pm, emp, fck4, fyk4, caa4)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.pyplot(fig_muro(H_m, emp["Ka"], gs, emp["Pa_total"], emp["za"], pm))
            with col2:
                st.subheader("Empuxo (Rankine)")
                ca, cb, cc = st.columns(3)
                ca.metric("Ka", f"{emp['Ka']:.4f}")
                cb.metric("Pa (kN/m)", f"{emp['Pa_total']:.1f}")
                cc.metric("za (m)", f"{emp['za']:.2f}")
                st.subheader("Estabilidade global")
                ca, cb = st.columns(2)
                ca.metric("FST tombamento"+(" ✅" if est["FST_ok"] else " ❌"), f"{est['FST']:.3f}", delta="min 1,5")
                cb.metric("FSD deslizamento"+(" ✅" if est["FSD_ok"] else " ❌"), f"{est['FSD']:.3f}", delta="min 1,5")
                if not est["FSD_ok"]:
                    st.warning("FSD < 1,5 — aumente a base B para 0,6 a 0,7 x H ou adicione chave de cisalhamento.")
                st.subheader("Fuste")
                if "erro" in fus:
                    st.error(fus["erro"])
                else:
                    ca, cb, cc = st.columns(3)
                    ca.metric("Md (kNm/m)", f"{fus['Md_kNm']:.2f}")
                    cb.metric("Vd (kN/m)", f"{fus['Vd_kN']:.2f}")
                    cc.metric("As vert. (cm2/m)", f"{fus['As_cm2m']:.2f}")
            with st.expander("Geometria do pré-dimensionamento"):
                st.json({k:v for k,v in pm.items() if k!="ref"})
            with st.expander("Referências"):
                st.text(BIBLIOGRAFIA_MURO)
        except Exception as e:
            st.error(f"Erro: {e}")
            import traceback; st.code(traceback.format_exc())

elif pagina == "📋  Memorial de Cálculo":
    st.title("📋 Memorial de Cálculo — passo a passo")
    st.caption("Metodologia Prof. M.R. Carini (MSc, UFSC) — fórmula, substituição e norma em cada passo")
    elem_m = st.selectbox("Elemento", [
        "Laje Maciça", "Viga", "Pilar",
        "Muro de Arrimo", "Reservatório", "Piscina",
    ])
    if elem_m == "Laje Maciça":
        CASOS_M = {1: "Caso 1 - 4 apoiadas", 2: "Caso 2 - 3 ap.+1 eng.(ly)",
                   "2A": "Caso 2A", 3: "Caso 3", "3A": "Caso 3A", 4: "Caso 4",
                   5: "Caso 5", "5A": "Caso 5A", 6: "Caso 6 - 4 engastadas"}
        with st.form("mem_laje"):
            c1, c2, c3 = st.columns(3)
            with c1:
                lx_m = st.number_input("lx — menor vão (m)", 1.5, 8.0, 3.5, 0.1)
                ly_m = st.number_input("ly — maior vão (m)", 1.5, 10.0, 4.5, 0.1)
                h_m = st.number_input("h — espessura (cm)", 8, 30, 10, 1)
            with c2:
                gk_m = st.number_input("gk revestimentos+forro (kN/m²)", 0.0, 20.0, 1.15, 0.05)
                qk_m = st.number_input("qk (kN/m²)", 0.5, 20.0, 1.5, 0.1)
                caso_m = st.selectbox("Caso de vinculação", list(CASOS_M.keys()),
                                      format_func=lambda k: CASOS_M[k])
            with c3:
                fck_m = st.number_input("fck (MPa)", 20, 50, 25)
                fyk_m = st.number_input("fyk (MPa)", 250, 600, 500)
                caa_m = st.selectbox("CAA", ["I", "II", "III", "IV"], index=1)
            ok_mem = st.form_submit_button("📋 Gerar memorial passo a passo", use_container_width=True)
        if ok_mem:
            try:
                passos, _res = memorial_laje(lx_m, ly_m, h_m, gk_m, qk_m, caso_m, fck_m, fyk_m, caa_m)
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
            except Exception as e:
                st.error("Erro: " + str(e))
                import traceback
                st.code(traceback.format_exc())
    elif elem_m == "Viga":
        with st.form("mem_viga"):
            c1, c2, c3 = st.columns(3)
            with c1:
                bw_v = st.number_input("bw — largura (cm)", 10, 60, 14, 1, key="bwv")
                hv_v = st.number_input("h — altura (cm)", 20, 120, 40, 5, key="hvv")
                L_v = st.number_input("L — vão (m)", 1.0, 12.0, 4.0, 0.1, key="lvv")
            with c2:
                Md_v = st.number_input("Md — momento ELU (kNm)", 1.0, 2000.0, 45.0, 1.0, key="mdv")
                Vd_v = st.number_input("Vd — cortante ELU (kN)", 1.0, 1000.0, 55.0, 1.0, key="vdv")
                qser_v = st.number_input("q serviço ELS (kN/m)", 0.5, 300.0, 18.0, 0.5, key="qsv")
            with c3:
                fck_v = st.number_input("fck (MPa)", 20, 50, 25, key="fckv")
                fyk_v = st.number_input("fyk (MPa)", 250, 600, 500, key="fykv")
                caa_v = st.selectbox("CAA", ["I", "II", "III", "IV"], index=1, key="caav")
            ok_v = st.form_submit_button("📋 Gerar memorial passo a passo", use_container_width=True)
        if ok_v:
            try:
                passos, _r = memorial_viga(bw_v, hv_v, L_v, Md_v, Vd_v, fck_v, fyk_v, caa_v, qser_v)
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
            except Exception as e:
                st.error("Erro: " + str(e))
                import traceback
                st.code(traceback.format_exc())
    elif elem_m == "Pilar":
        with st.form("mem_pilar"):
            c1, c2, c3 = st.columns(3)
            with c1:
                H_p = st.number_input("H — altura livre (cm)", 100, 800, 300, 10, key="hp")
                hx_p = st.number_input("hx (cm)", 12, 120, 19, 1, key="hxp")
                hy_p = st.number_input("hy (cm)", 12, 120, 40, 1, key="hyp")
                beta_p = st.number_input("β flambagem", 0.5, 2.0, 1.0, 0.1, key="betap")
            with c2:
                Nd_p = st.number_input("Nd (kN)", 10.0, 10000.0, 450.0, 10.0, key="ndp")
                Md_p = st.number_input("Md (kNcm)", 0.0, 50000.0, 1200.0, 100.0, key="mdp")
            with c3:
                fck_p = st.number_input("fck (MPa)", 20, 50, 25, key="fckp")
                fyk_p = st.number_input("fyk (MPa)", 250, 600, 500, key="fykp")
                caa_p = st.selectbox("CAA", ["I", "II", "III", "IV"], index=1, key="caap")
            ok_p = st.form_submit_button("📋 Gerar memorial passo a passo", use_container_width=True)
        if ok_p:
            try:
                passos, _r = memorial_pilar(H_p, hx_p, hy_p, beta_p, Nd_p, Md_p, fck_p, fyk_p, caa_p)
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
            except Exception as e:
                st.error("Erro: " + str(e))
                import traceback
                st.code(traceback.format_exc())
    elif elem_m == "Muro de Arrimo":
        with st.form("mem_muro"):
            c1, c2, c3 = st.columns(3)
            with c1:
                H_mu = st.number_input("H — altura do muro (m)", 1.0, 8.0, 3.0, 0.5, key="hmu")
                phi_mu = st.number_input("φ — atrito do solo (graus)", 15.0, 45.0, 30.0, 1.0, key="phimu")
            with c2:
                gs_mu = st.number_input("γ solo (kN/m³)", 14.0, 22.0, 18.0, 0.5, key="gsmu")
                qs_mu = st.number_input("Sobrecarga qs (kN/m²)", 0.0, 30.0, 0.0, 1.0, key="qsmu")
            with c3:
                fck_mu = st.number_input("fck (MPa)", 20, 40, 25, key="fckmu")
                fyk_mu = st.number_input("fyk (MPa)", 250, 600, 500, key="fykmu")
                caa_mu = st.selectbox("CAA", ["II", "III", "IV"], index=1, key="caamu")
            ok_mu = st.form_submit_button("📋 Gerar memorial passo a passo", use_container_width=True)
        if ok_mu:
            try:
                passos, _r = memorial_muro(H_mu, phi_mu, gs_mu, qs_mu, fck_mu, fyk_mu, caa_mu)
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
            except Exception as e:
                st.error("Erro: " + str(e))
                import traceback
                st.code(traceback.format_exc())
    elif elem_m == "Reservatório":
        with st.form("mem_reserv"):
            c1, c2, c3 = st.columns(3)
            with c1:
                tipo_r = st.selectbox("Tipo", ["Elevado", "Enterrado"], key="tipor")
                estado_r = st.selectbox("Estado", ["Cheio", "Vazio"], key="estr")
                H_r = st.number_input("H — altura da água (m)", 1.0, 8.0, 2.4, 0.1, key="hr")
            with c2:
                L_r = st.number_input("L — maior vão da parede (m)", 1.0, 12.0, 4.75, 0.05, key="lr")
                hpar_r = st.number_input("h — espessura da parede (cm)", 12, 40, 20, 1, key="hparr")
                phi_r = st.number_input("φ solo (graus, só enterrado)", 15.0, 45.0, 30.0, 1.0, key="phir")
            with c3:
                gs_r = st.number_input("γ solo (kN/m³, só enterrado)", 14.0, 22.0, 18.0, 0.5, key="gsr")
                fck_r = st.number_input("fck (MPa, mín 40)", 40, 50, 40, key="fckr")
                fyk_r = st.number_input("fyk (MPa)", 250, 600, 500, key="fykr")
            ok_r = st.form_submit_button("📋 Gerar memorial passo a passo", use_container_width=True)
        if ok_r:
            try:
                passos, _r = memorial_reservatorio(tipo_r, estado_r, H_r, L_r, hpar_r, phi_r, gs_r, fck_r, fyk_r, "IV")
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
            except Exception as e:
                st.error("Erro: " + str(e))
                import traceback
                st.code(traceback.format_exc())
    elif elem_m == "Piscina":
        with st.form("mem_pisc"):
            c1, c2, c3 = st.columns(3)
            with c1:
                estado_pi = st.selectbox("Estado", ["Cheia", "Vazia"], key="estpi")
                H_pi = st.number_input("H — altura da água (m)", 1.0, 6.0, 1.5, 0.1, key="hpi")
                L_pi = st.number_input("L — maior vão da parede (m)", 1.0, 12.0, 4.0, 0.1, key="lpi")
            with c2:
                hpar_pi = st.number_input("h — espessura da parede (cm)", 12, 40, 20, 1, key="hparpi")
                phi_pi = st.number_input("φ solo (graus)", 15.0, 45.0, 30.0, 1.0, key="phipi")
                gs_pi = st.number_input("γ solo (kN/m³)", 14.0, 22.0, 18.0, 0.5, key="gspi")
            with c3:
                qs_pi = st.number_input("Sobrecarga no solo qs (kN/m²)", 0.0, 30.0, 0.0, 1.0, key="qspi")
                fck_pi = st.number_input("fck (MPa)", 25, 50, 30, key="fckpi")
                fyk_pi = st.number_input("fyk (MPa)", 250, 600, 500, key="fykpi")
            ok_pi = st.form_submit_button("📋 Gerar memorial passo a passo", use_container_width=True)
        if ok_pi:
            try:
                passos, _r = memorial_piscina(estado_pi, H_pi, L_pi, hpar_pi, phi_pi, gs_pi, qs_pi, fck_pi, fyk_pi, "III")
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
            except Exception as e:
                st.error("Erro: " + str(e))
                import traceback
                st.code(traceback.format_exc())
    else:
        st.info("Falta apenas a Viga-parede (proxima fatia).")