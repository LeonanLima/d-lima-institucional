# relatorio/passo_a_passo.py - Memorial de calculo passo a passo
# Metodologia: Prof. M.R. Carini (MSc, UFSC) - notas de aula
# Cada funcao retorna (lista de Passo, dict resultado canonico para conferencia).
import math
from dataclasses import dataclass, field
from dimensionamento.laje import calcular_laje_macica, COEF_CARINI

COBR_CAA = {"I": 1.5, "II": 2.0, "III": 3.5, "IV": 4.5}


@dataclass
class Passo:
    titulo: str
    formula: str = ""
    substituicao: list = field(default_factory=list)
    resultado: str = ""
    norma: str = ""
    obs: str = ""


def _v(x, dec=2):
    return ("{:." + str(dec) + "f}").format(x).replace(".", ",")


def memorial_laje(lx, ly, h_cm, gk, qk, caso=1, fck=25.0, fyk=500.0, caa="II", psi2=0.3):
    res = calcular_laje_macica(lx, ly, h_cm, gk, qk, caso, fck, fyk, caa)
    passos = []

    # Passo 1 - classificacao
    lam = ly / lx
    bidir = lam <= 2.0
    tipo = "BIDIRECIONAL" if bidir else "UNIDIRECIONAL"
    passos.append(Passo(
        titulo="Passo 1 - Classificacao da laje",
        formula=r"\lambda = \dfrac{l_y}{l_x}",
        substituicao=[r"\lambda = \dfrac{" + _v(ly) + r"}{" + _v(lx) + r"} = " + _v(lam, 3)],
        resultado="lambda = " + _v(lam, 3) + ("  (<= 2) -> " if bidir else "  (> 2) -> ") + tipo,
        norma="NBR 6118:2023 sec.13.2 | Carini, Slide 2",
        obs="" if bidir else "Para lambda > 2 o correto e laje unidirecional (casos 7-10).",
    ))

    # Passo 2 - cargas
    PP = 25.0 * h_cm / 100.0
    g_total = gk + PP
    fd = 1.4 * g_total + 1.4 * qk
    fd_ser = g_total + psi2 * qk
    passos.append(Passo(
        titulo="Passo 2 - Cargas de calculo",
        formula=r"f_d = 1{,}4\,(g_k + PP) + 1{,}4\,q_k \qquad f_{d,ser} = (g_k + PP) + \psi_2\,q_k",
        substituicao=[
            r"PP = 25 \cdot " + _v(h_cm / 100.0) + r" = " + _v(PP) + r"\ \mathrm{kN/m^2}",
            r"f_d = 1{,}4\,(" + _v(gk) + r" + " + _v(PP) + r") + 1{,}4 \cdot " + _v(qk) + r" = " + _v(fd) + r"\ \mathrm{kN/m^2}",
            r"f_{d,ser} = (" + _v(gk) + r" + " + _v(PP) + r") + " + _v(psi2, 1) + r" \cdot " + _v(qk) + r" = " + _v(fd_ser) + r"\ \mathrm{kN/m^2}",
        ],
        resultado="fd = " + _v(fd) + " kN/m2 (ELU)  |  fd,ser = " + _v(fd_ser) + " kN/m2 (ELS)",
        norma="NBR 6118:2023 sec.11.2, Tabela 11.2 (psi2 residencial = 0,3)",
    ))

    # Passo 3 - coeficientes de Carini
    coef = COEF_CARINI.get(caso, COEF_CARINI[1])

    def cf(k):
        v = coef.get(k)
        return _v(v, 4) if v is not None else "-"

    passos.append(Passo(
        titulo="Passo 3 - Coeficientes de Carini (caso " + str(caso) + ")",
        formula=r"M_d = m \cdot f_d \cdot l_x^2 \qquad R_d = r \cdot f_d \cdot l_x",
        substituicao=[
            r"m_x = " + cf("mx") + r",\quad m_y = " + cf("my") + r",\quad m_{xe} = " + cf("mxe") + r",\quad m_{ye} = " + cf("mye"),
            r"r_x = " + cf("rx") + r",\quad r_y = " + cf("ry") + r",\quad r_{xe} = " + cf("rxe") + r",\quad r_{ye} = " + cf("rye"),
        ],
        resultado="Coeficientes tabelados do caso " + str(caso) + " (lambda = 1,0)",
        norma="Carini (MSc, UFSC), Slide 2 - Tabela de coeficientes",
        obs="LIMITACAO: a tabela atual usa lambda = ly/lx = 1,0. Carini interpola os coeficientes para lambda diferente de 1,0 (ver docs/consideracoes-carini.md). Em lajes retangulares o valor real difere.",
    ))

    # Passo 4 - momentos
    mts = res["momentos"]
    sub_m = []
    if coef.get("mx"):
        sub_m.append(r"M_{dx} = " + cf("mx") + r" \cdot " + _v(fd) + r" \cdot " + _v(lx) + r"^2 = " + _v(mts["Mdx_pos"], 3) + r"\ \mathrm{kNm/m}")
    if coef.get("my"):
        sub_m.append(r"M_{dy} = " + cf("my") + r" \cdot " + _v(fd) + r" \cdot " + _v(lx) + r"^2 = " + _v(mts["Mdy_pos"], 3) + r"\ \mathrm{kNm/m}")
    if coef.get("mxe"):
        sub_m.append(r"M_{dxe} = " + cf("mxe") + r" \cdot " + _v(fd) + r" \cdot " + _v(lx) + r"^2 = " + _v(mts["Mdxe_neg"], 3) + r"\ \mathrm{kNm/m}")
    if coef.get("mye"):
        sub_m.append(r"M_{dye} = " + cf("mye") + r" \cdot " + _v(fd) + r" \cdot " + _v(lx) + r"^2 = " + _v(mts["Mdye_neg"], 3) + r"\ \mathrm{kNm/m}")
    passos.append(Passo(
        titulo="Passo 4 - Momentos fletores de calculo",
        formula=r"M_d = m \cdot f_d \cdot l_x^2",
        substituicao=sub_m,
        resultado="Mdx=" + _v(mts["Mdx_pos"]) + " Mdy=" + _v(mts["Mdy_pos"]) + " Mdxe=" + _v(mts["Mdxe_neg"]) + " Mdye=" + _v(mts["Mdye_neg"]) + " kNm/m",
        norma="Carini, Slide 2 | NBR 6118:2023 sec.14.7.6",
    ))

    # Passo 5 - geometria e resistencias
    cobr = COBR_CAA.get(caa, 2.0)
    d = h_cm - cobr - 0.5
    fcd = fck / 1.4 / 10.0
    fyd = fyk / 1.15 / 10.0
    passos.append(Passo(
        titulo="Passo 5 - Altura util e resistencias de calculo",
        formula=r"d = h - c - \dfrac{\phi}{2} \qquad f_{cd} = \dfrac{f_{ck}}{1{,}4} \qquad f_{yd} = \dfrac{f_{yk}}{1{,}15}",
        substituicao=[
            r"d = " + _v(h_cm) + r" - " + _v(cobr) + r" - 0{,}5 = " + _v(d) + r"\ \mathrm{cm}",
            r"f_{cd} = " + _v(fck) + r"/1{,}4 = " + _v(fcd, 3) + r"\ \mathrm{kN/cm^2}",
            r"f_{yd} = " + _v(fyk) + r"/1{,}15 = " + _v(fyd, 3) + r"\ \mathrm{kN/cm^2}",
        ],
        resultado="d = " + _v(d) + " cm (cobrimento CAA " + caa + " = " + _v(cobr) + " cm)",
        norma="NBR 6118:2023 sec.8.2 | Tabela 7.2 (cobrimento)",
    ))

    # Passo 6 - armaduras
    b = 100.0
    rho_min = 0.15 if fyk <= 500 else 0.12
    As_min = rho_min / 100.0 * b * h_cm
    pares = [
        ("Mdx_pos", "positiva x"),
        ("Mdy_pos", "positiva y"),
        ("Mdxe_neg", "negativa x (engaste)"),
        ("Mdye_neg", "negativa y (engaste)"),
    ]
    letras = "abcd"
    idx = 0
    for mk, nome in pares:
        Md = mts[mk]
        if abs(Md) < 0.001:
            continue
        Md_abs = abs(Md) * 100.0
        disc = 1 - Md_abs / (0.425 * b * d ** 2 * fcd)
        x = 1.25 * d * (1 - math.sqrt(max(0, disc)))
        As = 0.85 * fcd * 0.80 * x * b / fyd
        As_adot = max(As, As_min)
        xd = x / d
        ductil = xd <= 0.45
        passos.append(Passo(
            titulo="Passo 6" + letras[idx] + " - Armadura " + nome + " (Md = " + _v(abs(Md)) + " kNm/m)",
            formula=r"x = 1{,}25\,d\left[1 - \sqrt{1 - \dfrac{M_d}{0{,}425\,b\,d^2 f_{cd}}}\right] \qquad A_s = \dfrac{0{,}85\,f_{cd}\,0{,}80\,x\,b}{f_{yd}}",
            substituicao=[
                r"x = 1{,}25 \cdot " + _v(d) + r"\left[1 - \sqrt{1 - \dfrac{" + _v(Md_abs, 1) + r"}{0{,}425 \cdot 100 \cdot " + _v(d) + r"^2 \cdot " + _v(fcd, 3) + r"}}\right] = " + _v(x) + r"\ \mathrm{cm}",
                r"\dfrac{x}{d} = " + _v(xd, 3) + (r"\ \le 0{,}45 \Rightarrow \text{ductil OK}" if ductil else r"\ > 0{,}45 \Rightarrow \text{aumentar h}"),
                r"A_s = \dfrac{0{,}85 \cdot " + _v(fcd, 3) + r" \cdot 0{,}80 \cdot " + _v(x) + r" \cdot 100}{" + _v(fyd, 3) + r"} = " + _v(As) + r"\ \mathrm{cm^2/m}",
                r"A_{s,min} = " + _v(rho_min) + r"\% \cdot 100 \cdot " + _v(h_cm) + r" = " + _v(As_min) + r"\ \mathrm{cm^2/m}",
            ],
            resultado="As adotado = " + _v(As_adot) + " cm2/m  (maior entre As=" + _v(As) + " e As,min=" + _v(As_min) + ")",
            norma="NBR 6118:2023 sec.17.2.2 | Tabela 19.1 (As,min) | dominio 2/3 se x/d <= 0,45",
        ))
        idx += 1

    # Passo 7 - reacoes
    rc = res["reacoes"]
    sub_r = []
    if coef.get("rx"):
        sub_r.append(r"R_{dx} = " + cf("rx") + r" \cdot " + _v(fd) + r" \cdot " + _v(lx) + r" = " + _v(rc["Rdx"]) + r"\ \mathrm{kN/m}")
    if coef.get("ry"):
        sub_r.append(r"R_{dy} = " + cf("ry") + r" \cdot " + _v(fd) + r" \cdot " + _v(lx) + r" = " + _v(rc["Rdy"]) + r"\ \mathrm{kN/m}")
    if coef.get("rxe"):
        sub_r.append(r"R_{dxe} = " + cf("rxe") + r" \cdot " + _v(fd) + r" \cdot " + _v(lx) + r" = " + _v(rc["Rdxe"]) + r"\ \mathrm{kN/m}")
    if coef.get("rye"):
        sub_r.append(r"R_{dye} = " + cf("rye") + r" \cdot " + _v(fd) + r" \cdot " + _v(lx) + r" = " + _v(rc["Rdye"]) + r"\ \mathrm{kN/m}")
    passos.append(Passo(
        titulo="Passo 7 - Reacoes nas vigas de apoio",
        formula=r"R_d = r \cdot f_d \cdot l_x",
        substituicao=sub_r,
        resultado="Reacoes que serao carregadas nas vigas de borda",
        norma="Carini, Slide 2 | NBR 6118:2023 sec.14.7.6.1",
        obs="Estas reacoes alimentam o calculo das vigas (fluxo laje -> viga).",
    ))

    # Passo 8 - flecha ELS
    els = res["els_flecha"]
    ai = min(0.8 + 0.2 * fck / 80, 1.0)
    Ecs = ai * 5600 * math.sqrt(fck)
    passos.append(Passo(
        titulo="Passo 8 - Verificacao de flecha (ELS)",
        formula=r"w_\infty = (1 + \varphi)\,w_0 \qquad w_{adm} = \dfrac{l_x}{250}",
        substituicao=[
            r"E_{cs} = " + _v(ai, 3) + r" \cdot 5600 \sqrt{" + _v(fck, 0) + r"} = " + _v(Ecs, 0) + r"\ \mathrm{MPa}",
            r"w_0 = " + _v(els["w0_mm"]) + r"\ \mathrm{mm} \quad w_\infty = (1 + 2{,}5)\,w_0 = " + _v(els["w_total_mm"]) + r"\ \mathrm{mm}",
            r"w_{adm} = " + _v(lx * 100, 0) + r"/250 = " + _v(els["wadm_mm"]) + r"\ \mathrm{mm}",
        ],
        resultado="w_inf = " + _v(els["w_total_mm"]) + " mm " + ("<=" if els["ok"] else ">") + " w_adm = " + _v(els["wadm_mm"]) + " mm -> " + ("OK" if els["ok"] else "AUMENTAR h"),
        norma="NBR 6118:2023 sec.13.3, Tabela 13.3 | fluencia phi = 2,5",
        obs="Flecha por estimativa simplificada de placa. O metodo rigoroso usa os coeficientes wc de Carini por caso de vinculacao.",
    ))

    return passos, res

def memorial_viga(bw, h, L_m, Md_kNm, Vd_kN, fck=25.0, fyk=500.0, caa="II", q_ser=None):
    from dimensionamento.viga import (
        _fck_props, verificar_bielas, dimensionar_estribos,
        momento_limite_simples, armadura_simples, armadura_dupla,
        calcular_flecha_branson, escolher_barras,
    )
    passos = []
    d = h - 5.0
    p = _fck_props(fck)
    fcd = p["fcd"]
    fyd = fyk / 1.15 / 10.0
    lam = p["lam"]
    ac = p["alpha_c"]
    ec = p["eta_c"]
    fctm = p["fctm"]
    fctd = p["fctd"]
    avv = 1 - fck / 250.0
    Md_kNcm = Md_kNm * 100.0

    # Passo 1
    passos.append(Passo(
        titulo="Passo 1 - Geometria e propriedades dos materiais",
        formula=r"d \approx h - 5 \qquad f_{cd}=\dfrac{f_{ck}}{1{,}4}\qquad f_{yd}=\dfrac{f_{yk}}{1{,}15}\qquad \alpha_{v2}=1-\dfrac{f_{ck}}{250}",
        substituicao=[
            r"d = " + _v(h) + r" - 5 = " + _v(d) + r"\ \mathrm{cm}",
            r"f_{cd} = " + _v(fck) + r"/1{,}4 = " + _v(fcd, 3) + r"\ \mathrm{kN/cm^2} \quad f_{yd} = " + _v(fyk) + r"/1{,}15 = " + _v(fyd, 3) + r"\ \mathrm{kN/cm^2}",
            r"\alpha_{v2} = 1 - " + _v(fck, 0) + r"/250 = " + _v(avv, 3) + r" \quad f_{ctd} = 0{,}15\,f_{ck}^{2/3}/1{,}4 = " + _v(fctd, 4) + r"\ \mathrm{kN/cm^2}",
        ],
        resultado="d = " + _v(d) + " cm | fcd = " + _v(fcd, 3) + " | fyd = " + _v(fyd, 3) + " kN/cm2",
        norma="NBR 6118:2023 sec.8.2, 14 | Carini Slide 3",
    ))

    # Passo 2 - bielas
    biel = verificar_bielas(Vd_kN, bw, d, fck)
    VRd2 = biel["VRd2"]
    passos.append(Passo(
        titulo="Passo 2 - Cisalhamento: bielas comprimidas (VRd2)",
        formula=r"V_{Rd2} = 0{,}27\,\alpha_{v2}\,f_{cd}\,b_w\,d",
        substituicao=[
            r"V_{Rd2} = 0{,}27 \cdot " + _v(avv, 3) + r" \cdot " + _v(fcd, 3) + r" \cdot " + _v(bw) + r" \cdot " + _v(d) + r" = " + _v(VRd2) + r"\ \mathrm{kN}",
        ],
        resultado="VRd2 = " + _v(VRd2) + " kN  " + ("vs Vd = " + _v(Vd_kN) + " kN -> bielas OK" if biel["ok"] else "< Vd -> AUMENTAR secao"),
        norma="NBR 6118:2023 sec.17.4.1.2.1 (Modelo I) | Bastos (UNESP)",
        obs="Modelo I de Ritter-Morsch: bielas a 45 graus. Se Vd > VRd2 o concreto esmaga e estribo nao resolve.",
    ))

    # Passo 3 - Vc
    Vc = 0.6 * fctd * bw * d
    passos.append(Passo(
        titulo="Passo 3 - Cisalhamento: parcela do concreto (Vc)",
        formula=r"V_c = 0{,}6\,f_{ctd}\,b_w\,d",
        substituicao=[
            r"V_c = 0{,}6 \cdot " + _v(fctd, 4) + r" \cdot " + _v(bw) + r" \cdot " + _v(d) + r" = " + _v(Vc) + r"\ \mathrm{kN}",
        ],
        resultado="Vc = " + _v(Vc) + " kN (banzo comprimido + engrenamento + efeito pino)",
        norma="NBR 6118:2023 sec.17.4.1.2.1 | Bastos (UNESP)",
    ))

    # Passo 4 - estribos
    est = dimensionar_estribos(Vd_kN, bw, d, fck, fyk)
    fywk = fyk / 10.0
    fctm_c = fctm / 10.0
    Asw_s_min = est["Asw_s_min"]
    Asw_s = est["Asw_s"]
    smax = min(0.6 * d, 30.0)
    sub4 = [
        r"\left(\dfrac{A_{sw}}{s}\right)_{min} = 0{,}2\,\dfrac{f_{ctm}}{f_{ywk}}\,b_w = 0{,}2 \cdot \dfrac{" + _v(fctm_c, 3) + r"}{" + _v(fywk, 1) + r"} \cdot " + _v(bw) + r" = " + _v(Asw_s_min, 4) + r"\ \mathrm{cm^2/cm}",
    ]
    if Vd_kN <= Vc:
        sub4.append(r"V_d = " + _v(Vd_kN) + r" \le V_c \Rightarrow \text{usar armadura minima}")
    else:
        sub4.append(r"\dfrac{A_{sw}}{s} = \dfrac{V_d - V_c}{0{,}9\,d\,f_{yd}} = \dfrac{" + _v(Vd_kN) + r" - " + _v(Vc) + r"}{0{,}9 \cdot " + _v(d) + r" \cdot " + _v(fyd, 3) + r"} = " + _v(Asw_s, 4) + r"\ \mathrm{cm^2/cm}")
    sug_txt = " | ".join(["Phi" + _v(s["phi_mm"], 1) + " c/" + str(s["s_cm"]) + "cm" for s in est["sugestoes"]]) if est["sugestoes"] else "ver tabela"
    passos.append(Passo(
        titulo="Passo 4 - Armadura transversal (estribos, Modelo I)",
        formula=r"\dfrac{A_{sw}}{s} = \dfrac{V_d - V_c}{0{,}9\,d\,f_{yd}} \ge \left(\dfrac{A_{sw}}{s}\right)_{min} \qquad s_{max} = \min(0{,}6d;\ 30)",
        substituicao=sub4,
        resultado="Asw/s = " + _v(Asw_s, 4) + " cm2/cm (trecho " + est["trecho"] + ") | s_max = " + _v(smax) + " cm | sugestoes: " + sug_txt,
        norma="NBR 6118:2023 sec.17.4.2 | Carini Slide 3",
    ))

    # Passo 5 - momento limite
    lim = momento_limite_simples(bw, d, fck)
    x_duc = lim["x_duc"]
    Md_duc = lim["Md_duc"]
    dupla = Md_kNcm > Md_duc
    passos.append(Passo(
        titulo="Passo 5 - Flexao: momento limite (simples ou dupla)",
        formula=r"x_{duc}=0{,}45\,d \qquad M_{d,duc}=\alpha_c\,\eta_c\,f_{cd}\,\lambda\,x_{duc}\,b\left(d-\dfrac{\lambda x_{duc}}{2}\right)",
        substituicao=[
            r"x_{duc} = 0{,}45 \cdot " + _v(d) + r" = " + _v(x_duc) + r"\ \mathrm{cm}",
            r"M_{d,duc} = " + _v(ac, 2) + r" \cdot " + _v(ec, 2) + r" \cdot " + _v(fcd, 3) + r" \cdot " + _v(lam, 2) + r" \cdot " + _v(x_duc) + r" \cdot " + _v(bw) + r"\left(" + _v(d) + r" - \dfrac{" + _v(lam, 2) + r" \cdot " + _v(x_duc) + r"}{2}\right) = " + _v(Md_duc) + r"\ \mathrm{kNcm}",
        ],
        resultado="Md = " + _v(Md_kNcm) + " kNcm " + (">" if dupla else "<=") + " Md,duc = " + _v(Md_duc) + " kNcm -> " + ("ARMADURA DUPLA" if dupla else "ARMADURA SIMPLES"),
        norma="NBR 6118:2023 sec.14.6.4.3, 17.2.2 (x/d <= 0,45 ductilidade)",
    ))

    # Passo 6 - flexao
    if not dupla:
        fx = armadura_simples(Md_kNcm, bw, d, fck, fyk)
        x = fx["x_cm"]
        As = fx["As_cm2"]
        x_lim = fx["x_lim"]
        rho_min = max(0.26 * fctm / fyk, 0.0015)
        As_min = rho_min * bw * d
        As_adot = max(As, As_min)
        barras = escolher_barras(As_adot)
        bar_txt = " ou ".join([str(n) + "Phi" + _v(phi, 1) + "(" + _v(area) + ")" for n, phi, area in barras[:3]]) if barras else "-"
        passos.append(Passo(
            titulo="Passo 6 - Flexao: armadura simples (As)",
            formula=r"x=1{,}25\,d\left[1-\sqrt{1-\dfrac{M_d}{0{,}425\,b\,d^2 f_{cd}}}\right] \qquad A_s=\dfrac{\alpha_c\,\eta_c\,f_{cd}\,\lambda\,x\,b}{f_{yd}}",
            substituicao=[
                r"x = 1{,}25 \cdot " + _v(d) + r"\left[1-\sqrt{1-\dfrac{" + _v(Md_kNcm) + r"}{0{,}425 \cdot " + _v(bw) + r" \cdot " + _v(d) + r"^2 \cdot " + _v(fcd, 3) + r"}}\right] = " + _v(x) + r"\ \mathrm{cm}",
                r"\dfrac{x}{d} = " + _v(x / d, 3) + (r"\ \le 0{,}45 \Rightarrow \text{ductil OK}" if x <= x_lim else r"\ > 0{,}45 \Rightarrow \text{rever secao}"),
                r"A_s = \dfrac{" + _v(ac, 2) + r" \cdot " + _v(ec, 2) + r" \cdot " + _v(fcd, 3) + r" \cdot " + _v(lam, 2) + r" \cdot " + _v(x) + r" \cdot " + _v(bw) + r"}{" + _v(fyd, 3) + r"} = " + _v(As) + r"\ \mathrm{cm^2}",
                r"A_{s,min} = " + _v(rho_min * 100, 3) + r"\% \cdot " + _v(bw) + r" \cdot " + _v(d) + r" = " + _v(As_min) + r"\ \mathrm{cm^2}",
            ],
            resultado="As adotado = " + _v(As_adot) + " cm2 -> " + bar_txt,
            norma="NBR 6118:2023 sec.17.2.2 | Tabela 17.3 (As,min, piso 0,15%)",
            obs="Dominio 2/3 (x/d <= 0,45): ruptura ductil, a viga avisa antes de romper.",
        ))
        As_flecha = As_adot
    else:
        du = armadura_dupla(Md_kNcm, bw, d, fck, fyk, caa)
        passos.append(Passo(
            titulo="Passo 6 - Flexao: armadura dupla (As1 tracionada + As2 comprimida)",
            formula=r"A_{s2}=\dfrac{M_d-M_{d,duc}}{\sigma_{s2}\,(d-d^{\prime})} \qquad A_{s1}=\dfrac{F_c+A_{s2}\sigma_{s2}}{f_{yd}}",
            substituicao=[
                r"d^{\prime} = " + _v(du["dl"]) + r"\ \mathrm{cm} \quad \sigma_{s2} = " + _v(du["sig_s2"], 2) + r"\ \mathrm{kN/cm^2}",
                r"A_{s2} = " + _v(du["As2_cm2"]) + r"\ \mathrm{cm^2} \quad A_{s1} = " + _v(du["As1_cm2"]) + r"\ \mathrm{cm^2}",
            ],
            resultado="As1 (tracionada) = " + _v(du["As1_cm2"]) + " cm2 | As2 (comprimida) = " + _v(du["As2_cm2"]) + " cm2",
            norma="NBR 6118:2023 sec.17.2.2 | Araujo (Dr., FURG) 2014",
        ))
        As_flecha = du["As1_cm2"]

    # Passo 7 - flecha
    if q_ser is not None:
        Md_ser_kNcm = q_ser * L_m ** 2 / 8.0 * 100.0
    else:
        Md_ser_kNcm = Md_kNcm / 1.4
    fl = calcular_flecha_branson(Md_ser_kNcm, As_flecha, bw, h, d, L_m, fck)
    passos.append(Passo(
        titulo="Passo 7 - Flecha por Branson (ELS)",
        formula=r"I_e=\left(\dfrac{M_r}{M_a}\right)^3 I_g+\left[1-\left(\dfrac{M_r}{M_a}\right)^3\right] I_{II} \qquad \delta_\infty=(1+\varphi)\,\dfrac{5\,q\,L^4}{384\,E_{cs}\,I_e}",
        substituicao=[
            r"M_r = " + _v(fl["Mr"], 1) + r"\ \mathrm{kNcm} \quad M_a = " + _v(Md_ser_kNcm, 1) + r"\ \mathrm{kNcm}",
            r"I_g = " + _v(fl["Ig"], 0) + r" \quad I_{II} = " + _v(fl["Iii"], 0) + r" \quad I_e = " + _v(fl["Ie"], 0) + r"\ \mathrm{cm^4}",
            r"\delta_i = " + _v(fl["delta_i"], 3) + r"\ \mathrm{cm} \quad \delta_\infty = (1+2{,}5)\,\delta_i = " + _v(fl["delta_t"] * 10, 2) + r"\ \mathrm{mm}",
            r"w_{adm} = L/250 = " + _v(fl["wadm"] * 10, 2) + r"\ \mathrm{mm}",
        ],
        resultado="delta_inf = " + _v(fl["delta_t"] * 10, 2) + " mm " + ("<=" if fl["ok"] else ">") + " wadm = " + _v(fl["wadm"] * 10, 2) + " mm -> " + ("OK" if fl["ok"] else "AUMENTAR h"),
        norma="NBR 6118:2023 sec.17.3.2 | Branson / Araujo (Dr., FURG) 2014",
        obs="Mr = momento de fissuracao; se Ma > Mr a viga fissura (estadio II) e usa-se a inercia de Branson.",
    ))

    return passos, {"d": d, "VRd2": VRd2, "Vc": Vc, "Md_duc": Md_duc, "dupla": dupla}