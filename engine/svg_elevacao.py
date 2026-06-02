def desenhar_elevacao(L, h, zonas, barras_pos, barras_neg):
    """Gera SVG da elevacao (vista longitudinal) com zonas de estribo.

    L, h em cm. zonas = lista de {x0, x1, tipo('critica'|'corrente'), estribo}.
    barras_pos/neg = textos descritivos. Escala horizontal e vertical proprias.
    """
    ESC_X = 1.2          # px por cm (comprimento)
    ESC_Y = 4.0          # px por cm (altura)
    MARG = 50.0
    W = L * ESC_X
    H = h * ESC_Y
    svg_w = W + 2 * MARG
    svg_h = H + 2 * MARG + 40

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" '
             'width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
             % (svg_w, svg_h, svg_w, svg_h)]

    # contorno da viga
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="#fafafa" stroke="#333" stroke-width="2"/>'
                 % (MARG, MARG, W, H))

    # zonas coloridas
    cores = {"critica": "#fecaca", "corrente": "#fef9c3"}
    for z in zonas:
        zx = MARG + z["x0"] * ESC_X
        zw = (z["x1"] - z["x0"]) * ESC_X
        parts.append('<rect class="zona" x="%.1f" y="%.1f" width="%.1f" '
                     'height="%.1f" fill="%s" opacity="0.6"/>'
                     % (zx, MARG, zw, H, cores.get(z["tipo"], "#eee")))
        parts.append('<text x="%.1f" y="%.1f" font-size="11" '
                     'text-anchor="middle">%s</text>'
                     % (zx + zw / 2, MARG + H + 16, z["estribo"]))

    # barras negativas (topo, vermelho) e positivas (fundo, azul)
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                 'stroke="#dc2626" stroke-width="3"/>'
                 % (MARG, MARG + 6, MARG + W, MARG + 6))
    parts.append('<text x="%.1f" y="%.1f" font-size="12" fill="#dc2626">'
                 '%s</text>' % (MARG + 4, MARG - 6, barras_neg))
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                 'stroke="#2563eb" stroke-width="3"/>'
                 % (MARG, MARG + H - 6, MARG + W, MARG + H - 6))
    parts.append('<text x="%.1f" y="%.1f" font-size="12" fill="#2563eb">'
                 '%s</text>' % (MARG + 4, MARG + H + 30, barras_pos))

    # cota de comprimento
    parts.append('<text x="%.1f" y="%.1f" font-size="13" '
                 'text-anchor="middle">L = %.0f cm</text>'
                 % (MARG + W / 2, svg_h - 8, L))

    parts.append('</svg>')
    return "\n".join(parts)
