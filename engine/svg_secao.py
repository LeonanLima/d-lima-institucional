def desenhar_secao(bw, h, cobrimento, barras_inf, barras_sup,
                   barras_pele, phi_est):
    """Gera SVG da secao transversal com armaduras posicionadas.

    bw, h, cobrimento em cm. barras_inf/sup = (n, phi_mm). barras_pele = n por
    face (>0 desenha 'n' barras em cada lateral). Escala: 1 cm = ESCALA px.
    """
    ESCALA = 6.0          # px por cm
    MARG = 40.0           # margem px
    W = bw * ESCALA
    H = h * ESCALA
    svg_w = W + 2 * MARG
    svg_h = H + 2 * MARG

    def px(x_cm, y_cm):
        # y invertido (SVG cresce para baixo); origem no canto inf-esq da secao
        return (MARG + x_cm * ESCALA, MARG + (h - y_cm) * ESCALA)

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" '
             'width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
             % (svg_w, svg_h, svg_w, svg_h)]

    # contorno da secao
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="#f5f5f5" stroke="#333" stroke-width="2"/>'
                 % (MARG, MARG, W, H))

    # linha de cobrimento (estribo) tracejada
    c = cobrimento
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="none" stroke="#888" stroke-width="1" '
                 'stroke-dasharray="4 3"/>'
                 % (MARG + c * ESCALA, MARG + c * ESCALA,
                    W - 2 * c * ESCALA, H - 2 * c * ESCALA))

    def circulos(n, phi_mm, y_cm, cor):
        if n <= 0:
            return
        r = max(phi_mm / 10.0 / 2.0 * ESCALA, 3.0)  # raio px
        x0 = c + phi_mm / 10.0 / 2.0
        x1 = bw - c - phi_mm / 10.0 / 2.0
        for k in range(n):
            xc = x0 if n == 1 else x0 + (x1 - x0) * k / (n - 1)
            cx, cy = px(xc, y_cm)
            parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                         % (cx, cy, r, cor))

    # armadura inferior (positiva, azul) e superior (negativa, vermelha)
    n_inf, phi_inf = barras_inf
    n_sup, phi_sup = barras_sup
    circulos(n_inf, phi_inf, c + phi_inf / 20.0, "#2563eb")
    circulos(n_sup, phi_sup, h - c - phi_sup / 20.0, "#dc2626")

    # armadura de pele (cinza) nas duas laterais
    if barras_pele > 0:
        r = max(8.0 / 10.0 / 2.0 * ESCALA, 3.0)
        for face_x in (c + 0.4, bw - c - 0.4):
            for k in range(barras_pele):
                y_cm = h * (k + 1) / (barras_pele + 1)
                cx, cy = px(face_x, y_cm)
                parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" '
                             'fill="#6b7280"/>' % (cx, cy, r))

    # cotas
    parts.append('<text x="%.1f" y="%.1f" font-size="14" text-anchor="middle">'
                 'b=%.0f cm</text>' % (MARG + W / 2, svg_h - 12, bw))
    parts.append('<text x="12" y="%.1f" font-size="14" '
                 'transform="rotate(-90 12 %.1f)" text-anchor="middle">'
                 'h=%.0f cm</text>' % (MARG + H / 2, MARG + H / 2, h))

    parts.append('</svg>')
    return "\n".join(parts)
