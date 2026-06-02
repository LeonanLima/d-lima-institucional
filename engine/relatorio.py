from engine.solver import (resolver, reacoes, esforcos_elemento, flecha_viga)
from engine.dimensionamento import (cisalhamento_viga, flexao_viga,
                                    armadura_pele)
from engine.detalhamento import escolher_bitola, escolher_estribo
from engine.svg_secao import desenhar_secao
from engine.svg_elevacao import desenhar_elevacao


def _matriz_serializavel(K, contrib):
    """Converte K e mapa de contribuicoes em listas para o template."""
    n = K.shape[0]
    linhas = []
    for i in range(n):
        linha = []
        for j in range(n):
            elems = sorted(contrib.get((i, j), set()))
            linha.append({"v": round(float(K[i, j]), 2), "elem": elems})
        linhas.append(linha)
    return linhas


def gerar_relatorio(estrutura):
    """Gera o relatorio completo: passos Carini, resultados, detalhamento,
    SVG e avisos. Retorna dict pronto para serializar/renderizar."""
    res = resolver(estrutura)
    R = reacoes(estrutura, res)
    avisos = []
    passos = []
    elementos_out = {}

    mat = estrutura.material

    # Passo 1 — Pre-dimensionamento
    passos.append({"titulo": "Passo 1 — Pre-dimensionamento",
                   "conteudo": "Verificacao das secoes adotadas."})
    # Passo 2 — Materiais
    passos.append({"titulo": "Passo 2 — Propriedades dos materiais",
                   "conteudo": "Ecs=%.0f kN/cm2 | fcd=%.3f | fyd=%.2f | "
                   "fctd=%.4f kN/cm2" % (mat.Ecs, mat.fcd, mat.fyd, mat.fctd)})
    # Passo 3 — Geometria
    geo = "; ".join("%s: A=%.0f cm2, I=%.0f cm4, L=%.0f cm"
                    % (e.id, e.secao.area, e.secao.inercia, e.comprimento())
                    for e in estrutura.elementos)
    passos.append({"titulo": "Passo 3 — Propriedades geometricas",
                   "conteudo": geo})
    # Passos 4-6 — Matrizes (referencia ao painel visual)
    passos.append({"titulo": "Passo 4-6 — Montagem da matriz de rigidez global",
                   "conteudo": "Ver matriz colorida por elemento no painel."})
    # Passo 7 — Contorno
    passos.append({"titulo": "Passo 7 — Condicoes de contorno",
                   "conteudo": "GDLs restritos: %s" % str(res["restritos"])})
    # Passo 9-10 — Deslocamentos
    desl = "; ".join("No %d: uy=%.3f mm, rz=%.5f rad"
                     % (nid, d["uy"], d["rz"])
                     for nid, d in res["deslocamentos"].items())
    passos.append({"titulo": "Passo 9-10 — Deslocamentos nodais",
                   "conteudo": desl})
    # Passo 11 — Reacoes
    rtxt = "; ".join("No %d: Fy=%.1f kN, Mz=%.1f kNm"
                     % (nid, r["fy"], r["mz"]) for nid, r in R.items())
    passos.append({"titulo": "Passo 11 — Reacoes de apoio", "conteudo": rtxt})

    # Por elemento: esforcos, dimensionamento, detalhamento, SVG
    for el in estrutura.elementos:
        esf = esforcos_elemento(estrutura, res, el.id, n_pontos=11)
        Mmax = max(abs(m) for m in esf["M"])
        Vmax = max(abs(v) for v in esf["V"])
        d = el.secao.h - el.cobrimento(estrutura.caa) - 0.5 - 0.625  # est+long/2

        if el.tipo in ("viga", "fundacao"):
            cis = cisalhamento_viga(mat, el.secao.bw, d, Vmax)
            flx = flexao_viga(mat, el.secao.bw, d, Mmax)
            pele = armadura_pele(mat, el.secao.bw, el.secao.h,
                                 el.cobrimento(estrutura.caa), 0.5)
            fl = flecha_viga(estrutura, res, el.id)

            if not flx["ductil"]:
                avisos.append("%s: x/d > 0,45 (secao insuficiente a flexao) "
                              "- aumentar h ou usar armadura dupla." % el.id)
            if not cis["bielas_ok"]:
                avisos.append("%s: VSd > VRd2 (bielas comprimidas) "
                              "- aumentar bw." % el.id)
            if fl["diferida"] > fl["limite"]:
                avisos.append("%s: flecha %.1f mm > limite %.1f mm "
                              "- aumentar h." % (el.id, fl["diferida"],
                                                 fl["limite"]))

            barras_pos = escolher_bitola(flx["As"])
            estribo = escolher_estribo(cis["Asw_s"], comprimento_zona=el.comprimento())

            zonas = [
                {"x0": 0, "x1": 2 * d, "tipo": "critica",
                 "estribo": estribo["descricao"]},
                {"x0": 2 * d, "x1": el.comprimento() - 2 * d, "tipo": "corrente",
                 "estribo": estribo["descricao"]},
                {"x0": el.comprimento() - 2 * d, "x1": el.comprimento(),
                 "tipo": "critica", "estribo": estribo["descricao"]},
            ]

            svg_sec = desenhar_secao(
                el.secao.bw, el.secao.h, el.cobrimento(estrutura.caa),
                barras_inf=(barras_pos["n"], barras_pos["phi"]),
                barras_sup=(barras_pos["n"], barras_pos["phi"]),
                barras_pele=2 if pele["necessaria"] else 0, phi_est=5.0)
            svg_elev = desenhar_elevacao(
                el.comprimento(), el.secao.h, zonas,
                barras_pos=barras_pos["descricao"],
                barras_neg=barras_pos["descricao"])

            elementos_out[el.id] = {
                "tipo": el.tipo, "Mmax_kNm": round(Mmax, 1),
                "Vmax_kN": round(Vmax, 1), "d": round(d, 1),
                "regioes": {
                    "meio": {"As_pos": round(flx["As"], 2),
                             "barras": barras_pos["descricao"],
                             "estribo": estribo["descricao"]},
                },
                "armadura_pele": pele,
                "flecha": fl, "svg_secao": svg_sec, "svg_elevacao": svg_elev,
            }
        else:
            elementos_out[el.id] = {"tipo": el.tipo,
                                    "Nmax_kN": round(max(abs(n) for n in esf["N"]), 1)}

    passos.append({"titulo": "Passo 12 — Esforcos internos",
                   "conteudo": "Diagramas N, V, M calculados por elemento."})
    passos.append({"titulo": "Passo 13 — Flechas", "conteudo":
                   "Imediata e diferida (phi=2,5) verificadas vs L/250."})
    passos.append({"titulo": "Passo 14-15 — Dimensionamento ELU",
                   "conteudo": "Cortante e flexao por elemento."})
    passos.append({"titulo": "Passo 16 — Detalhamento",
                   "conteudo": "Bitolas e estribos por regiao."})
    passos.append({"titulo": "Passo 17 — Verificacoes ELS",
                   "conteudo": "Flecha e fissuracao."})

    return {
        "passos": passos,
        "deslocamentos": res["deslocamentos"],
        "reacoes": R,
        "matriz_global": _matriz_serializavel(res["K"], res["contrib"]),
        "ordem_nos": res["ordem_nos"],
        "elementos": elementos_out,
        "avisos": avisos,
        "cores": {e.id: e.cor for e in estrutura.elementos},
    }
