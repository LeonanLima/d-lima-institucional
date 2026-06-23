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