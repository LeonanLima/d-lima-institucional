import math

BITOLAS = [6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0]  # mm
AREAS = {6.3: 0.312, 8.0: 0.503, 10.0: 0.785, 12.5: 1.227,
         16.0: 2.011, 20.0: 3.142, 25.0: 4.909, 32.0: 8.042}  # cm2
BITOLAS_ESTRIBO = [5.0, 6.3, 8.0]
AREA_ESTRIBO = {5.0: 0.196, 6.3: 0.312, 8.0: 0.503}


def _fmt(phi):
    s = ("%.1f" % phi).replace(".", ",").replace(",0", "")
    return s


def escolher_bitola(As_nec, n_min=2, n_max=8):
    """Escolhe (n, phi) que cobre As_nec com menor desperdicio.

    Desempate: menor numero de barras. Retorna dict com n, phi, As_fornecido,
    descricao.
    """
    candidatos = []
    for phi in BITOLAS:
        for n in range(n_min, n_max + 1):
            As_forn = n * AREAS[phi]
            if As_forn >= As_nec:
                candidatos.append((As_forn, n, phi))
                break  # menor n para esta bitola
    if not candidatos:
        phi = BITOLAS[-1]
        n = n_max
        As_forn = n * AREAS[phi]
        candidatos = [(As_forn, n, phi)]
    # menor desperdicio (As_forn), desempate por menor n
    As_forn, n, phi = min(candidatos, key=lambda t: (t[0], t[1]))
    return {"n": n, "phi": phi, "As_fornecido": As_forn,
            "descricao": "%d Ø %s (%.2f cm²)" % (n, _fmt(phi), As_forn)}


def escolher_estribo(Asw_s, comprimento_zona, n_ramos=2, s_max=30.0):
    """Escolhe (phi, espacamento) do estribo para um Asw/s dado.

    Asw_s em cm2/cm (area total dos ramos por cm). comprimento_zona em cm.
    Retorna dict com phi, espacamento, n_ramos, quantidade, descricao.
    """
    for phi in BITOLAS_ESTRIBO:
        area_total = n_ramos * AREA_ESTRIBO[phi]
        s = area_total / Asw_s if Asw_s > 0 else s_max
        s = min(s, s_max)
        s = max(math.floor(s), 5)  # cm, minimo pratico 5 cm
        if s >= 5:
            quantidade = max(int(comprimento_zona / s), 1)
            return {"phi": phi, "espacamento": float(s), "n_ramos": n_ramos,
                    "quantidade": quantidade,
                    "descricao": "Ø %s c/%d cm (%dr) — %d un." % (
                        _fmt(phi), s, n_ramos, quantidade)}
    # fallback
    phi = BITOLAS_ESTRIBO[0]
    s = 5
    quantidade = max(int(comprimento_zona / s), 1)
    return {"phi": phi, "espacamento": 5.0, "n_ramos": n_ramos,
            "quantidade": quantidade,
            "descricao": "Ø 5 c/5 cm (%dr) — %d un." % (n_ramos, quantidade)}
