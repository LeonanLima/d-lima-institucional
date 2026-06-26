# relatorio/memorial_trelicada.py - Memorial passo a passo da LAJE TRELICADA
# (nervura = viga T). Re-deriva e confere com a funcao canonica
# dimensionamento.laje_trelicada.calcular_laje_trelicada (fonte unica).
import math

from dimensionamento.laje_trelicada import calcular_laje_trelicada, VINCULACOES
from detalhamento.armaduras import BITOLAS, area_barra, tabela_espacamento
from relatorio.passo_a_passo import Passo, _v, _tabela_barras


def _barras_vigota(As_exig, posicao):
    """Arranjos (n x Phi) para a armadura concentrada da vigota. ★ = recomendado.

    Vigota carrega 1-3 barras na face tracionada; lista da que usa o menor As
    provido que atende ate as mais grossas, para o projetista escolher."""
    opc = []
    for phi in BITOLAS:
        if phi < 5.0:
            continue
        a = area_barra(phi)
        n = max(1, math.ceil(As_exig / a))
        if n > 4:
            continue                      # mais de 4 barras nao cabe numa vigota
        opc.append((n, phi, round(n * a, 2)))
    opc = sorted(opc, key=lambda t: (t[0], t[2]))   # menos barras primeiro (pratico na vigota)
    return _tabela_barras(opc, limite=5, posicao=posicao, As_exig=As_exig)


def memorial_laje_trelicada(lx, e_cm, h_capa_cm, h_total_cm, bw_cm, gk, qk,
                            vinculacao="apoio_apoio", fck=25.0, fyk=500.0,
                            caa="II", psi2=0.3, pp_enchimento=0.0):
    """Memorial da laje trelicada. Retorna (lista de Passo, dict canonico)."""
    res = calcular_laje_trelicada(lx, e_cm, h_capa_cm, h_total_cm, bw_cm, gk, qk,
                                  vinculacao, fck, fyk, caa, psi2, pp_enchimento)
    v = VINCULACOES.get(vinculacao, VINCULACOES["apoio_apoio"])
    passos = []

    # Passo 1 - vinculacao e limites dimensionais do Musso (§13.4.2)
    capa_min = max(h_capa_cm * 0.0 + 4.0, (e_cm - bw_cm) / 15.0)  # mesa >= l0/15 e >=4
    l0 = e_cm - bw_cm
    ok_capa = h_capa_cm >= max(4.0, l0 / 15.0)
    ok_bw = bw_cm >= 5.0
    passos.append(Passo(
        titulo="Passo 1 - Vinculacao e limites do Musso (§13.4.2)",
        formula=r"\text{mesa} \ge \dfrac{l_0}{15}\ \text{e}\ \ge 4\,\mathrm{cm}; \quad b_w \ge 5\,\mathrm{cm}",
        substituicao=[
            r"l_0 = e - b_w = " + _v(e_cm, 1) + r" - " + _v(bw_cm, 1) + r" = " + _v(l0, 1) + r"\ \mathrm{cm}",
            r"\text{mesa}_{min} = \max(4;\ " + _v(l0, 1) + r"/15) = " + _v(max(4.0, l0 / 15.0), 2) + r"\ \mathrm{cm}",
        ],
        resultado=("Vinculacao: " + v["descr"] +
                   "  |  capa " + ("OK" if ok_capa else "INSUFICIENTE") +
                   "  |  bw " + ("OK" if ok_bw else "< 5 cm (NAO)")),
        norma="Musso (UFES) §13.4.2 = NBR 6118:2023 §13.2.4.2",
        obs="Nervura com bw < 8 cm nao pode conter armadura de compressao.",
    ))

    # Passo 2 - cargas (PP pela geometria real da secao T)
    PP, fd, fd_ser = res["PP_kNm2"], res["fd_kNm2"], res["fd_ser_kNm2"]
    A_c = e_cm * h_capa_cm + bw_cm * (h_total_cm - h_capa_cm)
    passos.append(Passo(
        titulo="Passo 2 - Cargas de calculo (PP pela geometria)",
        formula=r"PP = 25\,\dfrac{A_c}{e};\quad f_d = 1{,}4(g_k{+}PP{+}g_{ench}) + 1{,}4\,q_k",
        substituicao=[
            r"A_c = e\,h_f + b_w(h{-}h_f) = " + _v(A_c, 0) + r"\ \mathrm{cm^2}",
            r"PP = 25 \cdot \dfrac{" + _v(A_c, 0) + r"/10^4}{" + _v(e_cm / 100.0, 2) + r"} = " + _v(PP) + r"\ \mathrm{kN/m^2}",
            r"f_d = " + _v(fd) + r"\ \mathrm{kN/m^2};\quad f_{d,ser} = " + _v(fd_ser) + r"\ \mathrm{kN/m^2}",
        ],
        resultado="fd = " + _v(fd) + " kN/m2 (ELU)  |  fd,ser = " + _v(fd_ser) + " kN/m2 (ELS)",
        norma="NBR 6118:2023 sec.11.2 | PP da treliçada < 25h (ha vazios das tavelas)",
    ))

    # Passo 3 - momentos por metro e por nervura
    m = res["momentos"]
    sub = [r"M_d^+ = \dfrac{f_d\,l_x^2}{\alpha} = \dfrac{" + _v(fd) + r"\cdot" + _v(lx) +
           r"^2}{" + _v(v["alpha"], 2) + r"} = " + _v(m["Md_pos_kNm_m"], 3) + r"\ \mathrm{kNm/m}"] if v["alpha"] else []
    if v["beta"]:
        sub.append(r"M_d^- = \dfrac{f_d\,l_x^2}{\beta} = \dfrac{" + _v(fd) + r"\cdot" + _v(lx) +
                   r"^2}{" + _v(v["beta"], 2) + r"} = " + _v(m["Md_neg_kNm_m"], 3) + r"\ \mathrm{kNm/m}")
    sub.append(r"\text{por nervura: } M\cdot e \Rightarrow M_d^+ = " + _v(m["Md_pos_nerv"], 3) +
               r"\ \mathrm{kNm};\ V_d = " + _v(m["Vd_nerv"], 3) + r"\ \mathrm{kN}")
    passos.append(Passo(
        titulo="Passo 3 - Esforcos (por metro e por nervura)",
        formula=r"M_d^+ = f_d l_x^2/\alpha;\quad M_d^- = f_d l_x^2/\beta;\quad V_d = \delta f_d l_x",
        substituicao=sub,
        resultado="Md+ = " + _v(m["Md_pos_nerv"], 2) + " kNm/nerv  |  Vd = " + _v(m["Vd_nerv"], 2) + " kN/nerv",
        norma="Coeficientes alpha/beta/delta - planilha Wagner / Carini",
    ))

    # Passo 4 - secao T + armadura da vigota (tabela de aco editavel)
    ap = res["armaduras"]["As_pos"]
    passos.append(Passo(
        titulo="Passo 4 - Flexao: secao T da nervura e armadura da vigota",
        formula=r"x = 1{,}25\,d\left[1-\sqrt{1-\dfrac{M_d}{0{,}425\,b_f\,d^2 f_{cd}}}\right];\ A_s = \dfrac{0{,}85 f_{cd}\,0{,}8x\,b}{f_{yd}}",
        substituicao=[
            r"b_f = e = " + _v(res["bf_cm"], 0) + r"\ \mathrm{cm};\ h_f = " + _v(res["h_capa_cm"], 1) +
            r";\ b_w = " + _v(res["bw_cm"], 1) + r";\ d = " + _v(res["d_cm"], 1) + r"\ \mathrm{cm}",
            r"\text{Secao: " + ap.get("secao", "-") + r"};\ x = " + _v(ap.get("x_cm", 0), 2) +
            r"\ \mathrm{cm}\ (x/d " + ("\\le" if ap.get("ok_ductil") else ">") + r" 0{,}45)",
            r"A_s = " + _v(ap.get("As_cm2", 0), 2) + r";\ A_{s,min} = " + _v(ap.get("As_min_cm2", 0), 2) +
            r"\Rightarrow A_{s,adot} = " + _v(ap.get("As_adot_cm2", 0), 2) + r"\ \mathrm{cm^2/nervura}",
        ],
        resultado="As+ = " + _v(ap.get("As_adot_cm2", 0), 2) + " cm2/nervura  (escolher o arranjo abaixo)",
        norma="NBR 6118:2023 sec.14.6.2.2 (mesa colaborante), 17.2.2; T.17.3 (As,min)",
        tabela=_barras_vigota(ap.get("As_adot_cm2", 0.0), "Vigota (+)"),
    ))

    # Passo 5 - cisalhamento (criterio do Musso por e)
    c = res["cisalhamento"]
    passos.append(Passo(
        titulo="Passo 5 - Cisalhamento (criterio do Musso por e)",
        formula=r"V_{Rd1} = \tau_{Rd}(1{,}2 + 40\rho_1)\,b_w\,d,\quad \tau_{Rd} = 0{,}25\,f_{ctd}",
        substituicao=[
            r"\text{criterio: } " + c["criterio_txt"],
            r"V_{Sd} = " + _v(c["VSd_nerv_kN"], 2) + r"\ \mathrm{kN};\ V_{Rd1} = " + _v(c["VRd1_nerv_kN"], 2) + r"\ \mathrm{kN/nervura}",
        ],
        resultado=("V_Sd " + ("<=" if c["ok"] else ">") + " V_Rd1 -> " +
                   ("OK (sem estribo)" if c["ok"] else
                    ("PRECISA ESTRIBO (verificar como viga)" if c["precisa_estribo"]
                     else "NAO PASSA: aumentar h ou bw"))),
        norma="Musso §13.4.2 + NBR 6118:2023 sec.19.4.1",
    ))

    # Passo 6 - flecha (secao T bruta, fluencia phi=2,5)
    fl = res["els_flecha"]
    passos.append(Passo(
        titulo="Passo 6 - Flecha (ELS, secao T)",
        formula=r"w_0 = \dfrac{w_{coef}\,p_{ser}\,l_x^4}{E_{cs}\,I_T};\quad w_\infty = (1+\varphi)\,w_0;\quad w_{adm} = l_x/250",
        substituicao=[
            r"I_T = " + _v(fl["I_T_cm4"], 0) + r"\ \mathrm{cm^4}\ (y_t = " + _v(fl["yt_cm"], 2) + r"\ \mathrm{cm})",
            r"w_0 = " + _v(fl["w0_mm"], 2) + r"\ \mathrm{mm};\ w_\infty = " + _v(fl["w_total_mm"], 2) +
            r"\ \mathrm{mm};\ w_{adm} = " + _v(fl["wadm_mm"], 2) + r"\ \mathrm{mm}",
        ],
        resultado=("w_inf = " + _v(fl["w_total_mm"], 2) + " mm " +
                   ("<=" if fl["ok"] else ">") + " w_adm = " + _v(fl["wadm_mm"], 2) +
                   " mm -> " + ("OK" if fl["ok"] else "NAO PASSA: aumentar h")),
        norma="NBR 6118:2023 sec.17.3.2.1 (fluencia), Tabela 13.3 (w_adm)",
    ))

    return passos, res
