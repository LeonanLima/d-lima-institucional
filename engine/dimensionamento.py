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


def flexao_viga(material, bw, d, Md):
    """Dimensionamento a flexao simples/dupla (NBR 6118:2023).

    Md em kNm; bw, d em cm. Retorna dict com x, As, As2, As_min, tipo,
    ductil. As em cm2.
    """
    fcd = material.fcd
    fyd = material.fyd
    Md_cm = Md * 100.0   # kNm -> kN.cm

    x_duc = 0.45 * d
    Md_duc = 0.85 * fcd * 0.80 * x_duc * bw * (d - 0.80 * x_duc / 2)

    As_min = 0.0015 * bw * d   # 0,15%

    if Md_cm <= Md_duc:
        # armadura simples
        rad = 1 - Md_cm / (0.425 * bw * d * d * fcd)
        rad = max(rad, 0.0)
        x = 1.25 * d * (1 - rad ** 0.5)
        As = 0.85 * fcd * 0.80 * x * bw / fyd
        As = max(As, As_min)
        return {"x": x, "As": As, "As2": 0.0, "As_min": As_min,
                "tipo": "simples", "ductil": x <= x_duc}
    else:
        # armadura dupla
        Es = 21000.0  # kN/cm2
        ecu = 0.0035
        d_linha = 0.10 * d   # estimativa d'
        sigma_s2 = min(ecu * (x_duc - d_linha) / x_duc * Es, fyd)
        As2 = (Md_cm - Md_duc) / (sigma_s2 * (d - d_linha))
        As1 = (0.85 * fcd * 0.80 * x_duc * bw + As2 * sigma_s2) / fyd
        return {"x": x_duc, "As": As1, "As2": As2, "As_min": As_min,
                "tipo": "dupla", "ductil": True}


def armadura_pele(material, bw, h, cobrimento, phi_est):
    """Armadura de pele para vigas com h > 60 cm (NBR 6118, 17.3.5.2.3).

    As_pele = 0,10% da area da alma, por face. Retorna dict.
    """
    if h <= 60.0:
        return {"necessaria": False, "As_face": 0.0}
    h_util = h - 2 * cobrimento - 2 * phi_est
    As_face = 0.0010 * bw * h_util / 2.0  # por face
    return {"necessaria": True, "As_face": As_face, "espacamento_max": 20.0}
