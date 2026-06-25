# relatorio/passo_a_passo.py - Memorial de calculo passo a passo
# Metodologia: Prof. M.R. Carini (MSc, UFSC) - notas de aula
# Cada funcao retorna (lista de Passo, dict resultado canonico para conferencia).
import math
from dataclasses import dataclass, field
from dimensionamento.laje import calcular_laje_macica, COEF_CARINI
from dimensionamento.bares import (
    dimensionar_parede_placa, coeficientes_parede, momentos_parede,
)
from dimensionamento.flexo_tracao import as_min_flexo_tracao

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
    res = calcular_laje_macica(lx, ly, h_cm, gk, qk, caso, fck, fyk, caa, psi2)
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

    # Passo 2 - cargas (lidas do resultado canonico - fonte unica)
    PP = res["PP_kNm2"]
    g_total = gk + PP
    fd = res["fd_kNm2"]
    fd_ser = res["fd_ser_kNm2"]
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
            r"\lambda = l_y/l_x = " + _v(els["lambda_flecha"], 3) + r" \Rightarrow \alpha = " + _v(els["alpha_flecha"], 5) + r"\quad(w_0 = \alpha\,f_{d,ser}\,l_x^4/D)",
            r"w_0 = " + _v(els["w0_mm"]) + r"\ \mathrm{mm} \quad w_\infty = (1 + 2{,}5)\,w_0 = " + _v(els["w_total_mm"]) + r"\ \mathrm{mm}",
            r"w_{adm} = \dfrac{l_x}{250} = \dfrac{" + _v(lx * 1000, 0) + r"\,\mathrm{mm}}{250} = " + _v(els["wadm_mm"]) + r"\ \mathrm{mm}",
        ],
        resultado="w_inf = " + _v(els["w_total_mm"]) + " mm " + ("<=" if els["ok"] else ">") + " w_adm = " + _v(els["wadm_mm"]) + " mm -> " + ("OK" if els["ok"] else "AUMENTAR h"),
        norma="NBR 6118:2023 sec.17.3.2, Tabela 13.3 | fluencia phi = 2,5",
        obs="Flecha de placa: alpha(lambda) de Timoshenko/Carini (placa apoiada 4 bordos) interpolado por lambda=ly/lx. Casos com engaste usam o mesmo alpha (conservador).",
    ))

    return passos, res

def memorial_viga(bw, h, L_m, Md_kNm, Vd_kN, fck=25.0, fyk=500.0, caa="II", q_ser=None):
    from dimensionamento.viga import (
        _fck_props, verificar_bielas, dimensionar_estribos,
        momento_limite_simples, armadura_simples, armadura_dupla,
        calcular_flecha_branson, escolher_barras, as_minima_viga,
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
        asm = as_minima_viga(bw, d, fck, fyk)
        rho_min = asm["rho_min"]
        As_min = asm["As_min"]
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

def memorial_pilar(H, hx, hy, beta, Nd, Md_kNcm, fck=25.0, fyk=500.0, caa="II"):
    from dimensionamento.pilar import (
        _fck_props, calcular_esbeltez, excentricidade_minima, lambda1_limite,
        excentricidade_2a_ordem, dimensionar_secao, escolher_barras, estribo_pilar,
        momento_total_pilar,
    )
    passos = []
    p = _fck_props(fck)
    fcd = p["fcd"] / 10.0
    fyd = fyk / 1.15 / 10.0
    Ac = hx * hy
    # Fonte unica das excentricidades (mesma fn que a pagina usa)
    mt = momento_total_pilar(Nd, Md_kNcm, H, hx, hy, beta, fck)
    nu = mt["nu"]
    esb = calcular_esbeltez(H, hx, hy, beta)
    exc = excentricidade_minima(hx, hy)
    e0 = mt["e0"]
    sx = r"\text{" + esb["status_x"] + r"}"
    sy = r"\text{" + esb["status_y"] + r"}"

    # Passo 1 - esbeltez
    passos.append(Passo(
        titulo="Passo 1 - Indice de esbeltez",
        formula=r"\ell_e=\beta\,H \qquad \lambda=\dfrac{\ell_e}{i}=\dfrac{\ell_e}{h/\sqrt{12}}",
        substituicao=[
            r"\ell_e = " + _v(beta, 2) + r" \cdot " + _v(H) + r" = " + _v(esb["le_cm"]) + r"\ \mathrm{cm}",
            r"\lambda_x = \dfrac{" + _v(esb["le_cm"]) + r"}{" + _v(hx) + r"/\sqrt{12}} = " + _v(esb["lam_x"], 1) + r"\ (" + sx + r")",
            r"\lambda_y = \dfrac{" + _v(esb["le_cm"]) + r"}{" + _v(hy) + r"/\sqrt{12}} = " + _v(esb["lam_y"], 1) + r"\ (" + sy + r")",
        ],
        resultado="lambda_x = " + _v(esb["lam_x"], 1) + " (" + esb["status_x"] + ") | lambda_y = " + _v(esb["lam_y"], 1) + " (" + esb["status_y"] + ")",
        norma="NBR 6118:2023 sec.15.8.2 | Carini Slide 4",
        obs="lambda <= 35 curto (sem 2a ordem); 35 < lambda <= 90 pilar-padrao; > 90 metodos mais rigorosos.",
    ))

    # Passo 2 - exc 1a ordem
    lam1 = lambda1_limite(max(e0, exc["e1y_min"]), hy, 1.0)
    precisa2a = esb["lam_y"] > lam1
    passos.append(Passo(
        titulo="Passo 2 - Excentricidades de 1a ordem",
        formula=r"e_0=\dfrac{M_d}{N_d}\qquad e_{1,min}=1{,}5+0{,}03\,h\qquad \lambda_1=25+12{,}5\,\dfrac{\alpha_b\,e_1}{h}",
        substituicao=[
            r"e_0 = \dfrac{" + _v(Md_kNcm) + r"}{" + _v(Nd) + r"} = " + _v(e0) + r"\ \mathrm{cm}",
            r"e_{1x,min} = 1{,}5+0{,}03\cdot" + _v(hx) + r" = " + _v(exc["e1x_min"]) + r"\quad e_{1y,min} = 1{,}5+0{,}03\cdot" + _v(hy) + r" = " + _v(exc["e1y_min"]) + r"\ \mathrm{cm}",
            r"\lambda_1 = " + _v(lam1, 1) + r"\quad \lambda_y = " + _v(esb["lam_y"], 1) + (r" > \lambda_1 \Rightarrow \text{calcular 2a ordem}" if precisa2a else r" \le \lambda_1 \Rightarrow \text{dispensa 2a ordem}"),
        ],
        resultado="e0 = " + _v(e0) + " cm | e1y,min = " + _v(exc["e1y_min"]) + " cm | lambda1 = " + _v(lam1, 1) + " -> " + ("precisa 2a ordem" if precisa2a else "dispensa 2a ordem"),
        norma="NBR 6118:2023 sec.11.4.1, 15.8.2 | Carini Slide 4",
    ))

    # Passo 3 - 2a ordem (e2 vem da fonte unica)
    e2y = mt["e2y"]
    e2x = mt["e2x"]
    passos.append(Passo(
        titulo="Passo 3 - Excentricidade de 2a ordem (pilar-padrao)",
        formula=r"\nu=\dfrac{N_d}{A_c\,f_{cd}}\qquad e_2=0{,}0005\,\lambda^2\,\dfrac{h}{0{,}5+\nu}",
        substituicao=[
            r"\nu = \dfrac{" + _v(Nd) + r"}{" + _v(Ac, 0) + r" \cdot " + _v(fcd, 3) + r"} = " + _v(nu, 3),
            r"e_{2y} = 0{,}0005 \cdot " + _v(esb["lam_y"], 1) + r"^2 \cdot \dfrac{" + _v(hy) + r"}{0{,}5+" + _v(nu, 3) + r"} = " + _v(e2y, 2) + r"\ \mathrm{cm}",
            r"e_{2x} = 0{,}0005 \cdot " + _v(esb["lam_x"], 1) + r"^2 \cdot \dfrac{" + _v(hx) + r"}{0{,}5+" + _v(nu, 3) + r"} = " + _v(e2x, 2) + r"\ \mathrm{cm}",
        ],
        resultado="nu = " + _v(nu, 3) + " | e2x = " + _v(e2x, 2) + " cm | e2y = " + _v(e2y, 2) + " cm",
        norma="NBR 6118:2023 sec.15.8.3.3.2 (curvatura aproximada) | Carini Slide 4",
    ))

    # Passo 4 - momento total (fonte unica)
    e_design = mt["e_design"]
    Md_design = mt["Md_design"]
    passos.append(Passo(
        titulo="Passo 4 - Momento total de calculo (direcao y)",
        formula=r"M_{d,tot}=N_d\,(e_1+e_2)\quad\text{com } e_1=\max(e_0,\ e_{1,min})",
        substituicao=[
            r"e_{tot} = \max(" + _v(e0) + r",\ " + _v(exc["e1y_min"]) + r") + " + _v(e2y, 2) + r" = " + _v(e_design, 2) + r"\ \mathrm{cm}",
            r"M_{d,tot} = " + _v(Nd) + r" \cdot " + _v(e_design, 2) + r" = " + _v(Md_design, 1) + r"\ \mathrm{kNcm}",
        ],
        resultado="Md,tot = " + _v(Md_design, 1) + " kNcm (dimensiona com este momento)",
        norma="NBR 6118:2023 sec.15.8 | Carini Slide 4",
        obs="A pagina Pilar dimensiona com o Md informado; aqui o memorial soma e1+e2 (pilar-padrao correto).",
    ))

    # Passo 5 - flexo-compressao
    dim = dimensionar_secao(Nd, Md_design, hx, hy, fck, fyk, caa)
    cobr = {"I": 2.5, "II": 3.0, "III": 4.0, "IV": 5.0}.get(caa, 3.0)
    d = hy - cobr - 0.625
    passos.append(Passo(
        titulo="Passo 5 - Flexo-compressao normal (armadura simetrica)",
        formula=r"N_d=F_c-A_s\sigma_{s1}+A_s\sigma_{s2}\qquad A_{s,min}=\max\!\left(0{,}15\dfrac{N_d}{f_{yd}};\ 0{,}4\%\,A_c\right)",
        substituicao=[
            r"d = " + _v(hy) + r" - " + _v(cobr) + r" - 0{,}625 = " + _v(d) + r"\ \mathrm{cm}\quad x = " + _v(dim["x_cm"]) + r"\ \mathrm{cm}\ (\text{dominio } " + str(dim["dominio"]) + r")",
            r"A_{s,total} = " + _v(dim["As_calc"]) + r"\quad A_{s,min} = " + _v(dim["As_min"]) + r"\quad A_{s,max} = " + _v(dim["As_max"]) + r"\ \mathrm{cm^2}",
        ],
        resultado="As adotado = " + _v(dim["As_adot"]) + " cm2 (dominio " + str(dim["dominio"]) + (", ductil OK" if dim["ok_ductil"] else ", verificar") + ")",
        norma="NBR 6118:2023 sec.17.2.2, 17.2.5, 18.4.2.1 | Araujo (Dr., FURG) cap.10",
    ))

    # Passo 6 - detalhamento
    escolha = escolher_barras(dim["As_adot"])
    phi_long = escolha[0][1] if escolha else 16.0
    est = estribo_pilar(phi_long, min(hx, hy))
    bar_txt = " ou ".join([str(n) + "Phi" + _v(phi, 1) + "(" + _v(area) + ")" for n, phi, area in escolha[:3]]) if escolha else "-"
    passos.append(Passo(
        titulo="Passo 6 - Detalhamento: barras e estribos",
        formula=r"\phi_t\ge\max(5\,\mathrm{mm};\ \phi_\ell/4)\qquad s_{max}=\min(b;\ 20\,\phi_\ell;\ 30\,\mathrm{cm})",
        substituicao=[
            r"\text{Longitudinal: " + bar_txt + r"}",
            r"\phi_t = " + _v(est["phi_est_mm"], 0) + r"\,\mathrm{mm}\quad s_{max} = " + _v(est["s_max_cm"]) + r"\,\mathrm{cm}\quad s_{red} = " + _v(est["s_red_cm"]) + r"\,\mathrm{cm}",
        ],
        resultado="Barras: " + bar_txt + " | Estribo Phi" + _v(est["phi_est_mm"], 0) + " c/" + _v(est["s_max_cm"]) + "cm (s_red " + _v(est["s_red_cm"]) + " cm em emendas/base)",
        norma="NBR 6118:2023 sec.18.4.2.1, 18.4.3 | Carini Slide 4",
    ))

    return passos, dim

def memorial_muro(H_m, phi, gs, qs=0.0, fck=25.0, fyk=500.0, caa="III"):
    from dimensionamento.muro_arrimo import (
        predimensionar_muro, calcular_empuxo, verificar_estabilidade, dimensionar_fuste,
    )
    passos = []
    pm = predimensionar_muro(H_m, phi, gs)
    emp = calcular_empuxo(H_m, gs, phi, 0.0, qs)
    est = verificar_estabilidade(pm, emp, gs)
    fus = dimensionar_fuste(pm, emp, fck, fyk, caa)
    Ka = emp["Ka"]

    # Passo 1 - geometria
    passos.append(Passo(
        titulo="Passo 1 - Pre-dimensionamento geometrico",
        formula=r"e_{base}=0{,}08H+0{,}15\qquad B=0{,}5H\qquad e_{sap}=\max(0{,}10H;\ 0{,}20)",
        substituicao=[
            r"e_{base} = 0{,}08\cdot" + _v(H_m) + r"+0{,}15 = " + _v(pm["espessura_fuste_base"]) + r"\ \mathrm{m}\quad e_{topo} = " + _v(pm["espessura_fuste_topo"]) + r"\ \mathrm{m}",
            r"B = " + _v(pm["B_sapata"]) + r"\ \mathrm{m}\quad e_{sap} = " + _v(pm["esp_sapata"]) + r"\ \mathrm{m}",
            r"\text{ponta} = " + _v(pm["comprimento_ponta"]) + r"\ \mathrm{m}\quad \text{calcanheira} = " + _v(pm["comprimento_calcanheira"]) + r"\ \mathrm{m}",
        ],
        resultado="B = " + _v(pm["B_sapata"]) + " m | fuste base = " + _v(pm["espessura_fuste_base"]) + " m | sapata = " + _v(pm["esp_sapata"]) + " m",
        norma="Bastos (Dr., UNESP) 2017 + pratica Carini",
        obs="Carini ensina o muro logo apos o reservatorio elevado (ordem das aulas).",
    ))

    # Passo 2 - empuxo
    passos.append(Passo(
        titulo="Passo 2 - Empuxo ativo de Rankine",
        formula=r"K_a=\tan^2\!\left(45^\circ-\dfrac{\varphi}{2}\right)\qquad P_a=\tfrac{1}{2}K_a\,\gamma\,H^2\qquad z_a=\dfrac{H}{3}",
        substituicao=[
            r"K_a = \tan^2\!\left(45-\dfrac{" + _v(phi, 0) + r"}{2}\right) = " + _v(Ka, 4),
            r"P_a = \tfrac{1}{2}\cdot" + _v(Ka, 4) + r"\cdot" + _v(gs) + r"\cdot" + _v(H_m) + r"^2 = " + _v(emp["Pa_total"]) + r"\ \mathrm{kN/m}",
            r"z_a = " + _v(emp["za"]) + r"\ \mathrm{m}\quad(\text{ponto de aplicacao})",
        ],
        resultado="Ka = " + _v(Ka, 4) + " | Pa = " + _v(emp["Pa_total"]) + " kN/m | za = " + _v(emp["za"]) + " m",
        norma="Caputo (Dr., PUC-Rio) 2008 | Mecanica dos Solos",
    ))

    # Passo 3 - tombamento
    passos.append(Passo(
        titulo="Passo 3 - Estabilidade ao tombamento (FST)",
        formula=r"FST=\dfrac{M_{resist}}{M_{tomb}}=\dfrac{\sum W_i\,x_i}{P_a\,z_a}\ge 1{,}5",
        substituicao=[
            r"M_{resist} = " + _v(est["Mt_resist"]) + r"\ \mathrm{kNm/m}\quad M_{tomb} = P_a z_a = " + _v(est["Mt_acao"]) + r"\ \mathrm{kNm/m}",
            r"FST = \dfrac{" + _v(est["Mt_resist"]) + r"}{" + _v(est["Mt_acao"]) + r"} = " + _v(est["FST"], 3),
        ],
        resultado="FST = " + _v(est["FST"], 3) + (" >= 1,5 -> OK" if est["FST_ok"] else " < 1,5 -> aumentar base"),
        norma="Bastos (Dr., UNESP) 2017 + Araujo (Dr., FURG) 2014",
    ))

    # Passo 4 - deslizamento
    passos.append(Passo(
        titulo="Passo 4 - Estabilidade ao deslizamento (FSD)",
        formula=r"\mu=\tan\!\left(\tfrac{2}{3}\varphi\right)\qquad FSD=\dfrac{\mu\,\sum W_i}{P_a}\ge 1{,}5",
        substituicao=[
            r"W_{total} = " + _v(est["W_total"]) + r"\ \mathrm{kN/m}",
            r"FSD = \dfrac{\tan(\tfrac{2}{3}\cdot" + _v(phi, 0) + r")\cdot" + _v(est["W_total"]) + r"}{" + _v(emp["Pa_total"]) + r"} = " + _v(est["FSD"], 3),
        ],
        resultado="FSD = " + _v(est["FSD"], 3) + (" >= 1,5 -> OK" if est["FSD_ok"] else " < 1,5 -> aumentar base (0,6 a 0,7 H) ou chave de cisalhamento"),
        norma="Bastos (Dr., UNESP) 2017 | atrito solo-sapata",
    ))

    # Passo 5 - fuste
    if "erro" in fus:
        passos.append(Passo(
            titulo="Passo 5 - Dimensionamento do fuste",
            resultado="ERRO: " + fus["erro"],
            norma="NBR 6118:2023 sec.17",
        ))
    else:
        passos.append(Passo(
            titulo="Passo 5 - Fuste: armadura vertical (balanco com carga triangular)",
            formula=r"M_d=\gamma_f\,\dfrac{K_a\,\gamma\,h^3}{6}\qquad V_d=\gamma_f\,\dfrac{K_a\,\gamma\,h^2}{2}\qquad A_s=\dfrac{0{,}85 f_{cd}\,0{,}80\,x\,b}{f_{yd}}",
            substituicao=[
                r"M_d = 1{,}4\cdot\dfrac{" + _v(Ka, 4) + r"\cdot" + _v(gs) + r"\cdot" + _v(fus["h_fuste"]) + r"^3}{6} = " + _v(fus["Md_kNm"]) + r"\ \mathrm{kNm/m}",
                r"V_d = 1{,}4\cdot\dfrac{" + _v(Ka, 4) + r"\cdot" + _v(gs) + r"\cdot" + _v(fus["h_fuste"]) + r"^2}{2} = " + _v(fus["Vd_kN"]) + r"\ \mathrm{kN/m}",
                r"d = " + _v(fus["d_cm"]) + r"\ \mathrm{cm}\quad A_s = " + _v(fus["As_cm2m"]) + r"\ \mathrm{cm^2/m}",
            ],
            resultado="Md = " + _v(fus["Md_kNm"]) + " kNm/m | Vd = " + _v(fus["Vd_kN"]) + " kN/m | As vertical = " + _v(fus["As_cm2m"]) + " cm2/m",
            norma="Bastos (Dr., UNESP) eq.4.12 | NBR 6118:2023 sec.17",
            obs="O fuste e uma laje em balanco engastada na sapata; momento na base pela carga triangular do empuxo.",
        ))

    return passos, {"Ka": Ka, "FST": est["FST"], "FSD": est["FSD"], "fuste": fus}


def _passos_parede_bares(r, p_base, H_m, L_m, h_par_cm, fck, caa):
    """Passos 2..6 do memorial de parede hidraulica (placa de Bares + flexo-tracao).

    Narra A PARTIR do dict canonico r = dimensionar_parede_placa(...), garantindo
    que o memorial use exatamente os mesmos numeros do dimensionamento (fonte
    unica: dados/coef_bares_parede.json). Trata os casos sem pressao e secao
    insuficiente. p_base = pressao CARACTERISTICA na base [kN/m2].
    """
    b = 100.0

    if "erro" in r:
        return [Passo(
            titulo="Passo 2 - Secao insuficiente",
            resultado="ERRO: " + r["erro"],
            norma="NBR 6118:2023 sec.21",
            obs="Aumentar a espessura da parede ou o fck e refazer.",
        )]

    if r.get("As_cm2m") == 0:
        As_min = as_min_flexo_tracao(fck, b, h_par_cm)
        return [Passo(
            titulo="Passo 2 - Sem empuxo nesta combinacao",
            formula=r"p = 0 \Rightarrow \text{sem flexao de placa; adotar armadura minima}",
            substituicao=[
                r"A_{s,min} = \rho_{min}\,b\,h = " + _v(As_min, 2) + r"\ \mathrm{cm^2/m}",
            ],
            resultado="Sem pressao liquida: detalhar As,min = " + _v(As_min, 2) + " cm2/m nas duas direcoes/faces",
            norma="NBR 6118:2023 sec.21 | Carini, flexo-tracao slide 31",
            obs=r.get("nota", ""),
        )]

    passos = []
    coef = coeficientes_parede(L_m, H_m)   # mesma selecao da fonte (lx=L, ly=H)
    lam = H_m / L_m

    # Passo 2 - pressao, razao e os 4 coeficientes de Bares
    passos.append(Passo(
        titulo="Passo 2 - Pressao na base, razao e coeficientes de Bares",
        formula=r"p = \gamma\,H \qquad \lambda=\dfrac{l_y}{l_x} \qquad M=\dfrac{m}{1000}\,p\,l_{ref}^2",
        substituicao=[
            r"p = " + _v(p_base) + r"\ \mathrm{kN/m^2}\quad(\text{pico na base, carga triangular})",
            r"\lambda = \dfrac{" + _v(H_m) + r"}{" + _v(L_m) + r"} = " + _v(lam, 3) + r"\quad \text{razao tabela} = " + _v(r["razao"], 3) + r"\quad l_{ref} = " + _v(r["l_ref"]) + r"\ \mathrm{m}",
            r"m_x=" + _v(coef["mx"], 2) + r",\ m_{xe}=" + _v(coef["mxe"], 2) + r",\ m_y=" + _v(coef["my"], 2) + r",\ m_{ye}=" + _v(coef["mye"], 2),
        ],
        resultado="p = " + _v(p_base) + " kN/m2 | razao = " + _v(r["razao"], 3) + " | 4 coeficientes de Bares interpolados",
        norma="Tabela de Bares (carga triangular) | Carini, Reservatorios Elevados, slide 15",
    ))

    # Passo 3 - os 4 momentos de placa (caracteristicos e de calculo)
    Mk = momentos_parede(L_m, H_m, p_base)   # caracteristicos
    passos.append(Passo(
        titulo="Passo 3 - Momentos de placa nas 4 posicoes (Mx, Mxe, My, Mye)",
        formula=r"M_k=\dfrac{m}{1000}\,p\,l_{ref}^2 \qquad M_d = 1{,}4\,M_k",
        substituicao=[
            r"\text{Caracteristicos: } M_x=" + _v(Mk["Mx"], 2) + r",\ M_{xe}=" + _v(Mk["Mxe"], 2) + r",\ M_y=" + _v(Mk["My"], 2) + r",\ M_{ye}=" + _v(Mk["Mye"], 2) + r"\ \mathrm{kNm/m}",
            r"\text{De calculo }(\times 1{,}4): M_x=" + _v(r["Mx"], 2) + r",\ M_{xe}=" + _v(r["Mxe"], 2) + r",\ M_y=" + _v(r["My"], 2) + r",\ M_{ye}=" + _v(r["Mye"], 2) + r"\ \mathrm{kNm/m}",
        ],
        resultado="Momentos de calculo: Mx=" + _v(r["Mx"], 2) + " Mxe=" + _v(r["Mxe"], 2) + " My=" + _v(r["My"], 2) + " Mye=" + _v(r["Mye"], 2) + " kNm/m",
        norma="Carini, Reservatorios Elevados, slide 15 | gamma_f = 1,4",
        obs="x = horizontal (direcao do anel); y = vertical. (e) = engaste na base/lados; vao = centro do painel.",
    ))

    # Passo 4 - HORIZONTAL: flexo-tracao (placa + anel)
    Nd = r["Nd_anel_kNm"]
    fvx, fex = r["ft_vao_x"], r["ft_eng_x"]
    passos.append(Passo(
        titulo="Passo 4 - Direcao HORIZONTAL: flexo-tracao (placa + anel)",
        formula=r"N_d = 1{,}2\,p\,\dfrac{L}{2}\qquad(\text{momento da placa + tracao do anel = flexo-tracao})",
        substituicao=[
            r"N_d = 1{,}2 \cdot " + _v(p_base) + r" \cdot \dfrac{" + _v(L_m) + r"}{2} = " + _v(Nd, 2) + r"\ \mathrm{kN/m}",
            r"\text{Vao } (M_x): \text{caso " + str(fvx.get("caso", "-")) + r"},\ e_0=" + _v(fvx.get("e0") or 0, 2) + r",\ x=" + _v(fvx.get("x_cm") or 0, 2) + r"\ \Rightarrow A_{s1}=" + _v(fvx.get("As1_cm2") or 0, 2) + r"\ \mathrm{cm^2/m}",
            r"\text{Engaste } (M_{xe}): \text{caso " + str(fex.get("caso", "-")) + r"},\ x=" + _v(fex.get("x_cm") or 0, 2) + r"\ \Rightarrow A_{s1}=" + _v(fex.get("As1_cm2") or 0, 2) + r"\ \mathrm{cm^2/m}",
        ],
        resultado="As horizontal: vao = " + _v(r["As_vao_x"], 2) + " | engaste = " + _v(r["As_eng_x"], 2) + " cm2/m (flexo-tracao)",
        norma="NBR 6118:2023 sec.17.2.2, 21 | Carini, flexo-tracao slides 25-31",
        obs="O anel traciona a parede no plano horizontal; soma-se a flexao da placa -> flexo-tracao (gamma_f = 1,2 no normal).",
    ))

    # Passo 5 - VERTICAL: flexao simples
    passos.append(Passo(
        titulo="Passo 5 - Direcao VERTICAL: flexao simples (My vao, Mye engaste)",
        formula=r"A_s=\dfrac{0{,}85 f_{cd}\,0{,}80\,x\,b}{f_{yd}}\quad(\text{carga vertical nao traciona o anel: flexao pura})",
        substituicao=[
            r"M_{dy} = " + _v(r["My"], 2) + r"\ \Rightarrow A_s = " + _v(r["As_vao_y"], 2) + r"\ \mathrm{cm^2/m}\ (\text{vao})",
            r"M_{dye} = " + _v(r["Mye"], 2) + r"\ \Rightarrow A_s = " + _v(r["As_eng_y"], 2) + r"\ \mathrm{cm^2/m}\ (\text{engaste na base})",
        ],
        resultado="As vertical: vao = " + _v(r["As_vao_y"], 2) + " | engaste = " + _v(r["As_eng_y"], 2) + " cm2/m (flexao)",
        norma="NBR 6118:2023 sec.17.2.2 | Carini, Reservatorios Elevados",
    ))

    # Passo 6 - As,min, governante, cisalhamento e ELS
    wlim = "0,10" if caa == "IV" else "0,20"
    passos.append(Passo(
        titulo="Passo 6 - Armadura minima, governante, cisalhamento e ELS",
        formula=r"A_{s,min}=\rho_{min}\,b\,h \qquad w_k \le w_{lim}\ (\text{estanqueidade})",
        substituicao=[
            r"A_{s,min} = " + _v(r["As_min"], 2) + r"\ \mathrm{cm^2/m}\quad A_{s,gov} = " + _v(r["As_cm2m"], 2) + r"\ \mathrm{cm^2/m}",
            r"V_d = 1{,}4\,p\,\dfrac{H}{2} = " + _v(r["Vd_kN"], 2) + r"\ \mathrm{kN/m}",
            r"w_k \le " + wlim + r"\ \mathrm{mm}\quad(\text{contato com agua, CAA " + caa + r"})",
        ],
        resultado="As governante = " + _v(r["As_cm2m"], 2) + " cm2/m | Vd = " + _v(r["Vd_kN"], 2) + " kN/m | wlim = " + wlim + " mm",
        norma="NBR 6118:2023 sec.17.4, 21.3.3, Tabela 13.4 | Carini, flexo-tracao slide 31",
    ))

    return passos


def memorial_reservatorio(tipo, estado, H_m, L_m, h_par_cm, phi=30.0, gs=18.0,
                          fck=40.0, fyk=500.0, caa="IV"):
    """Memorial da parede de reservatorio: placa de Bares + flexo-tracao (Carini).

    Delega ao motor canonico dimensionar_parede_placa (fonte unica) e narra os 4
    momentos de Bares, a flexo-tracao horizontal (placa + anel) e a flexao vertical.
    """
    GAMMA_AGUA = 10.0
    Ka = math.tan(math.radians(45 - phi / 2.0)) ** 2
    cobr = {"I": 2.0, "II": 2.5, "III": 4.0, "IV": 4.5}.get(caa, 4.5)
    d = h_par_cm - cobr - 0.625
    enterrado = tipo.lower().startswith("enter")
    cheio = estado.lower().startswith("ch")

    p_agua = GAMMA_AGUA * H_m
    p_solo = Ka * gs * H_m
    if not enterrado:
        p = p_agua if cheio else 0.0
        carga = "agua interna" if cheio else "vazio (so peso proprio, sem empuxo lateral)"
    else:
        if cheio:
            p = p_agua
            carga = "agua interna (solo externo desprezado a favor da seguranca)"
        else:
            p = p_solo
            carga = "solo externo (reservatorio enterrado vazio)"

    contorno = "laterais apoiadas + base engastada + topo apoiado (tampa)"
    passos = [Passo(
        titulo="Passo 1 - Modelo: parede como placa de Bares (carga triangular)",
        formula=r"\text{Contorno: " + contorno + r"; carga hidrostatica triangular (pico na base)}",
        substituicao=[
            r"\text{Tipo: " + tipo + r" | Estado: " + estado + r" | carga = " + carga + r"}",
            r"\text{H = " + _v(H_m) + r"\ m (l_y, altura) | L = " + _v(L_m) + r"\ m (l_x, vao horizontal) | h = " + _v(h_par_cm) + r"\ cm | d = " + _v(d) + r"\ cm}",
        ],
        resultado="CAA " + caa + " (cob. " + _v(cobr) + " cm) | fck >= 40 MPa | placa bidirecional de Bares",
        norma="Carini, Reservatorios Elevados, slides 14-15 | NBR 6118:2023 sec.21",
        obs="Horizontal = flexo-tracao (placa + anel); vertical = flexao simples. Com tampa o topo apoia; sem tampa fica livre.",
    )]

    r = dimensionar_parede_placa(H_m, L_m, h_par_cm / 100.0, p, fck, fyk, caa)
    passos += _passos_parede_bares(r, p, H_m, L_m, h_par_cm, fck, caa)
    r["p_base"] = p
    r["carga"] = carga
    return passos, r

def memorial_piscina(estado, H_m, L_m, h_par_cm, phi=30.0, gs=18.0, qs=0.0,
                     fck=40.0, fyk=500.0, caa="IV"):
    """Memorial da parede de piscina: placa de Bares + flexo-tracao (Carini).

    Mesmo motor canonico do reservatorio (dimensionar_parede_placa). Piscina
    aberta -> topo livre; combinacoes cheia (agua) e vazia (solo externo).
    """
    GAMMA_AGUA = 10.0
    Ka = math.tan(math.radians(45 - phi / 2.0)) ** 2
    cobr = {"I": 2.0, "II": 2.5, "III": 4.0, "IV": 4.5}.get(caa, 4.0)
    d = h_par_cm - cobr - 0.625
    cheia = estado.lower().startswith("ch")
    razao = H_m / L_m

    p_agua = GAMMA_AGUA * H_m
    p_solo = Ka * gs * H_m + Ka * qs
    if cheia:
        p = p_agua
        carga = "agua interna (piscina cheia, sem solo de alivio)"
    else:
        p = p_solo
        carga = "solo externo (piscina vazia)"

    contorno = "laterais apoiadas + base engastada (topo livre: piscina aberta)"
    passos = [Passo(
        titulo="Passo 1 - Modelo: parede como placa de Bares (carga triangular)",
        formula=r"\text{Contorno: " + contorno + r"; carga triangular (pico na base)}",
        substituicao=[
            r"\text{Estado: " + estado + r" | carga = " + carga + r"}",
            r"\text{H = " + _v(H_m) + r"\ m (l_y) | L = " + _v(L_m) + r"\ m (l_x) | h = " + _v(h_par_cm) + r"\ cm | d = " + _v(d) + r"\ cm}",
            r"\lambda = \dfrac{l_y}{l_x} = \dfrac{" + _v(H_m) + r"}{" + _v(L_m) + r"} = " + _v(razao, 3) + (r"\ < 2\ \Rightarrow\ \text{placa bidirecional}" if razao < 2 else r"\ \ge 2\ \Rightarrow\ \text{unidirecional}"),
        ],
        resultado="Placa " + ("bidirecional" if razao < 2 else "unidirecional") + " de Bares | CAA " + caa + " (cob. " + _v(cobr) + " cm)",
        norma="BARES, R. - Tabelas para placas | Carini, Piscinas e Reservatorios",
        obs="Horizontal = flexo-tracao (placa + anel); vertical = flexao. Com sobrecarga no solo a carga vira trapezoidal - adota-se o pico (a favor da seguranca).",
    )]

    r = dimensionar_parede_placa(H_m, L_m, h_par_cm / 100.0, p, fck, fyk, caa)
    passos += _passos_parede_bares(r, p, H_m, L_m, h_par_cm, fck, caa)
    r["p_base"] = p
    r["carga"] = carga
    return passos, r