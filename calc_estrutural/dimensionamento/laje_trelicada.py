# dimensionamento/laje_trelicada.py - Dimensionamento de LAJE TRELICADA
# (vigotas + tavelas / lajes nervuradas pre-moldadas), modelo de NERVURA = VIGA T.
#
# CONSIDERACOES DO PROF. MUSSO (UFES), CAP3-LAJE, slide 3 (§13.4.2 nervuradas):
#   - mesa (capa) >= l0/15 e >= 4 cm (sem tubulacao); bw >= 5 cm;
#   - criterio de CISALHAMENTO conforme o espacamento entre eixos de nervuras (e):
#       a) e <= 65 cm ............... verifica como LAJE (sem estribo);
#       b) 65 < e <= 110 cm ......... verifica como VIGA (laje se e<=90 e bw_med>12);
#       c) e > 110 cm ............... mesa deve ser projetada como laje macica.
#   Transcricao completa em docs/musso-lajes-nervuradas.md.
#
# Modelo de calculo (vao unidirecional da vigota):
#   - cada nervura = viga T (alma bw da vigota; mesa = capa de largura e);
#   - coeficientes de vinculacao (planilha Eng. Waltner Wagner / Carini):
#       M+ = fd*lx^2/alpha ; M- = fd*lx^2/beta ; V = delta*fd*lx  [por metro];
#   - por nervura: multiplica a carga distribuida por e (faixa de influencia).
#
# REFERENCIAS:
#   [1'] MUSSO Jr., F. (UFES) CAP3-LAJE, slide 3 (§13.4.2)
#   [W]  WAGNER, W. Planilha Laje Trelicada (coef. de vinculacao alpha/beta/delta)
#   [4]  NBR 6118:2023, sec.13.2.4.2, 14.6.2.2 (mesa colaborante), 17, 19.4
import math

# Coeficientes de vinculacao do vao unidirecional da vigota [W].
#   alpha -> M+ = fd*lx^2/alpha   (None = sem momento positivo, ex. balanco)
#   beta  -> M- = fd*lx^2/beta    (None = sem engaste, ex. bi-apoiada)
#   delta -> reacao/cortante max = delta*fd*lx
#   wcoef -> flecha imediata = wcoef*p*lx^4/(Ecs*I)
VINCULACOES = {
    "apoio_apoio": {
        "alpha": 8.00, "beta": None, "delta": 0.500, "wcoef": 5.0 / 384.0,
        "descr": "Bi-apoiada (apoio/apoio)",
    },
    "apoio_engaste": {
        "alpha": 14.22, "beta": 8.00, "delta": 0.625, "wcoef": 1.0 / 185.0,
        "descr": "Apoiada-engastada (apoio/engaste)",
    },
    "engaste_engaste": {
        "alpha": 24.00, "beta": 12.00, "delta": 0.500, "wcoef": 1.0 / 384.0,
        "descr": "Bi-engastada (engaste/engaste)",
    },
    "balanco": {
        "alpha": None, "beta": 2.00, "delta": 1.000, "wcoef": 1.0 / 8.0,
        "descr": "Balanco (engaste/livre)",
    },
}

COBRIMENTO_CAA = {"I": 2.0, "II": 2.5, "III": 3.5, "IV": 4.5}  # cm (laje, NBR T.7.2)


def _criterio_cisalhamento(e_cm, bw_cm):
    """Criterio de verificacao ao cisalhamento por espacamento e (Musso §13.4.2)."""
    if e_cm <= 65.0:
        return "laje", "e <= 65 cm: verifica como laje (sem estribo)"
    if e_cm <= 110.0:
        if e_cm <= 90.0 and bw_cm > 12.0:
            return "laje", "65<e<=90 cm e bw>12 cm: permitido verificar como laje"
        return "viga", "65 < e <= 110 cm: verifica como viga (pode exigir estribo)"
    return "mesa_macica", "e > 110 cm: mesa deve ser projetada como laje macica"


def _inercia_T(bf, bw, hf, h):
    """Inercia bruta da secao T (cm) em torno do centroide. Retorna (I_cm4, yt_cm)."""
    hw = h - hf
    A_mesa, A_alma = bf * hf, bw * hw
    A = A_mesa + A_alma
    # centroide medido do topo (face comprimida)
    y_top = (A_mesa * (hf / 2.0) + A_alma * (hf + hw / 2.0)) / A
    I_mesa = bf * hf**3 / 12.0 + A_mesa * (y_top - hf / 2.0) ** 2
    I_alma = bw * hw**3 / 12.0 + A_alma * (hf + hw / 2.0 - y_top) ** 2
    return I_mesa + I_alma, y_top


def _armar_secao_T(Md_kNcm, bf, bw, hf, d, fcd, fyd):
    """Armadura de flexao de secao T (LN na mesa => retangular bf; senao T real)."""
    if Md_kNcm <= 0.0:
        return {"As_cm2": 0.0, "x_cm": 0.0, "secao": "-", "ok_ductil": True}
    # momento resistido com bloco de compressao ate o fim da mesa (a = hf)
    M_mesa = 0.85 * fcd * bf * hf * (d - hf / 2.0)
    if Md_kNcm <= M_mesa:
        disc = 1.0 - Md_kNcm / (0.425 * bf * d**2 * fcd)
        if disc < 0.0:
            return {"As_cm2": -1.0, "erro": "Md grande: aumentar h ou bw"}
        x = 1.25 * d * (1.0 - math.sqrt(disc))
        As = 0.85 * fcd * 0.80 * x * bf / fyd
        secao = "retangular (LN na mesa)"
    else:
        # T verdadeira: parcela da mesa (abas) + parcela da alma
        Mf = 0.85 * fcd * (bf - bw) * hf * (d - hf / 2.0)
        Asf = 0.85 * fcd * (bf - bw) * hf / fyd
        Mw = Md_kNcm - Mf
        disc = 1.0 - Mw / (0.425 * bw * d**2 * fcd)
        if disc < 0.0:
            return {"As_cm2": -1.0, "erro": "Md grande: aumentar h ou bw"}
        x = 1.25 * d * (1.0 - math.sqrt(disc))
        As = Asf + 0.85 * fcd * 0.80 * x * bw / fyd
        secao = "T (LN na nervura)"
    return {"As_cm2": round(As, 2), "x_cm": round(x, 2),
            "secao": secao, "ok_ductil": x <= 0.45 * d}


def calcular_laje_trelicada(lx, e_cm, h_capa_cm, h_total_cm, bw_cm, gk, qk,
                            vinculacao="apoio_apoio", fck=25.0, fyk=500.0,
                            caa="II", psi2=0.3, pp_enchimento=0.0):
    """Dimensionamento de laje trelicada unidirecional (nervura = viga T).

    lx [m] vao da vigota | e_cm espacamento entre eixos das nervuras
    h_capa_cm capa/mesa | h_total_cm altura total | bw_cm largura da nervura
    gk, qk [kN/m2] (gk SEM peso proprio - o PP do concreto e calculado da geometria;
    pp_enchimento = peso das tavelas/EPS em kN/m2, default 0).
    Ref: Musso §13.4.2 [1'] + Wagner [W] + NBR 6118:2023 [4].
    """
    v = VINCULACOES.get(vinculacao, VINCULACOES["apoio_apoio"])
    bf = float(e_cm)          # mesa colaborante = espacamento entre eixos (mesa continua)
    bw = float(bw_cm)
    hf = float(h_capa_cm)
    h = float(h_total_cm)
    e_m = e_cm / 100.0

    # --- Peso proprio do concreto pela geometria real da secao (por m2) ---
    A_c_cm2 = bf * hf + bw * (h - hf)                  # area de concreto na faixa e
    PP = 25.0 * (A_c_cm2 / 1.0e4) / e_m                # kN/m2
    g_total = gk + PP + pp_enchimento
    fd = 1.4 * g_total + 1.4 * qk                      # ELU [kN/m2]
    fd_ser = g_total + psi2 * qk                       # ELS [kN/m2]

    # --- Esforcos por metro e por nervura ---
    Md_pos = fd * lx**2 / v["alpha"] if v["alpha"] else 0.0   # kNm/m
    Md_neg = fd * lx**2 / v["beta"] if v["beta"] else 0.0     # kNm/m (>0, sinal neg.)
    Vd = v["delta"] * fd * lx                                  # kN/m
    Md_pos_nerv = Md_pos * e_m                                 # kNm por nervura
    Md_neg_nerv = Md_neg * e_m
    Vd_nerv = Vd * e_m                                         # kN por nervura

    # --- ELU flexao (secao T por nervura) ---
    cobr = COBRIMENTO_CAA.get(caa, 2.5)
    d = h - cobr - 0.5                                  # cm (vigota: cobr + ~Phi/2)
    fcd = fck / 1.4 / 10.0                              # kN/cm2
    fyd = fyk / 1.15 / 10.0
    arm_pos = _armar_secao_T(Md_pos_nerv * 100.0, bf, bw, hf, d, fcd, fyd)
    # momento negativo: traciona o TOPO -> secao retangular da nervura (bw), mesa em baixo
    arm_neg = (_armar_secao_T(Md_neg_nerv * 100.0, bw, bw, hf, d, fcd, fyd)
               if Md_neg_nerv > 0 else {"As_cm2": 0.0, "x_cm": 0.0,
                                        "secao": "-", "ok_ductil": True})
    # armadura minima da nervura (NBR T.17.3 viga T; rho_min sobre bw*h)
    rho_min = 0.0015 if fyk <= 500 else 0.0012
    As_min_nerv = rho_min * bw * h
    for a in (arm_pos, arm_neg):
        if a.get("As_cm2", 0) >= 0:
            a["As_min_cm2"] = round(As_min_nerv, 2)
            a["As_adot_cm2"] = round(max(a["As_cm2"], As_min_nerv), 2)

    # --- Cisalhamento (criterio do Musso por e) ---
    crit, crit_txt = _criterio_cisalhamento(e_cm, bw)
    # VRd1 (laje sem armadura, NBR 19.4.1) na nervura
    fctd = 0.15 * fck ** (2.0 / 3.0)                    # MPa (fctk,inf/gamma_c)
    tau_rd = 0.25 * fctd / 10.0                         # kN/cm2
    As_trac = max(arm_pos.get("As_adot_cm2", 0.0), 0.0)
    rho1 = min(As_trac / (bw * d), 0.02)
    VRd1 = tau_rd * (1.2 + 40.0 * rho1) * bw * d        # kN por nervura
    cis_ok = Vd_nerv <= VRd1
    precisa_estribo = (not cis_ok) and crit == "viga"

    # --- ELS flecha (secao T bruta) ---
    I_cm4, yt = _inercia_T(bf, bw, hf, h)
    I_m4 = I_cm4 * 1.0e-8
    ai = min(0.8 + 0.2 * fck / 80.0, 1.0)
    Ecs = ai * 5600.0 * math.sqrt(fck) * 1000.0        # kN/m2
    p_ser_nerv = fd_ser * e_m                           # kN/m por nervura
    w0 = v["wcoef"] * p_ser_nerv * lx**4 / (Ecs * I_m4)  # m
    w_total = w0 * (1.0 + 2.5)                          # fluencia phi=2,5
    wadm = lx / (125.0 if vinculacao == "balanco" else 250.0)

    return dict(
        lx=lx, vinculacao=vinculacao, vinc_descr=v["descr"],
        e_cm=e_cm, h_capa_cm=hf, h_total_cm=h, bw_cm=bw, d_cm=round(d, 2),
        bf_cm=bf, PP_kNm2=round(PP, 2), fd_kNm2=round(fd, 2),
        fd_ser_kNm2=round(fd_ser, 2), psi2=psi2,
        momentos={
            "Md_pos_kNm_m": round(Md_pos, 3), "Md_neg_kNm_m": round(Md_neg, 3),
            "Md_pos_nerv": round(Md_pos_nerv, 3), "Md_neg_nerv": round(Md_neg_nerv, 3),
            "Vd_kN_m": round(Vd, 3), "Vd_nerv": round(Vd_nerv, 3),
        },
        armaduras={"As_pos": arm_pos, "As_neg": arm_neg},
        cisalhamento={
            "criterio": crit, "criterio_txt": crit_txt,
            "VSd_nerv_kN": round(Vd_nerv, 3), "VRd1_nerv_kN": round(VRd1, 3),
            "ok": cis_ok, "precisa_estribo": precisa_estribo,
        },
        els_flecha={
            "I_T_cm4": round(I_cm4, 1), "yt_cm": round(yt, 2),
            "w0_mm": round(w0 * 1000.0, 2), "w_total_mm": round(w_total * 1000.0, 2),
            "wadm_mm": round(wadm * 1000.0, 2), "ok": w_total <= wadm,
        },
        ref="[1'] Musso §13.4.2 + [W] Wagner + [4] NBR 6118:2023",
    )
