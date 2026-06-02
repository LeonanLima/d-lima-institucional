def cisalhamento_viga(material, bw, d, VSd):
    """Verificacao ao cortante (Modelo I, NBR 6118:2023).

    bw, d em cm; VSd em kN. Retorna dict com VRd2, Vc, Asw_s, Asw_s_min,
    bielas_ok. Asw_s em cm2/cm (area total dos ramos por cm).
    """
    fck = material.fck
    fcd = material.fcd
    fctd = material.fctd
    fywd = min(material.fyk / 1.15 / 10.0, 43.5)  # kN/cm2, limite 435 MPa

    av2 = 1 - fck / 250.0
    VRd2 = 0.27 * av2 * fcd * bw * d
    Vc = 0.6 * fctd * bw * d

    fctm = material.fctm  # MPa
    fywk = min(material.fyk, 500.0)
    # Asw/s minimo: 0,2 * fctm/fywk * bw  (com fctm,fywk em MPa, bw em cm)
    Asw_s_min = 0.2 * (fctm / fywk) * bw

    if VSd <= Vc:
        Asw_s = Asw_s_min
    else:
        Asw_s = max((VSd - Vc) / (0.9 * d * fywd), Asw_s_min)

    return {
        "VRd2": VRd2, "Vc": Vc,
        "Asw_s": Asw_s, "Asw_s_min": Asw_s_min,
        "bielas_ok": VSd <= VRd2,
    }
