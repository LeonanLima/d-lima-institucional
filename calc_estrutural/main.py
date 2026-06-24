#!/usr/bin/env python3
# main.py - Menu interativo do Sistema de Calculo Estrutural
# NBR 6118:2023 | NBR 6120:2019 | Prof. Carini / Bastos / Araujo / Fusco

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm
    RICH_OK = True
except ImportError:
    RICH_OK = False

from datetime import datetime

# ---- Modulos do sistema ----
from dimensionamento.predim import (
    predimensionar_laje, predimensionar_viga, predimensionar_pilar,
    predimensionar_reservatorio
)
from dimensionamento.pilar import (
    calcular_esbeltez, excentricidade_minima, excentricidade_2a_ordem,
    dimensionar_secao, estribo_pilar, escolher_barras as barras_pilar,
    imprimir_pilar
)
from dimensionamento.viga import (
    verificar_bielas, calcular_parcela_concreto,
    dimensionar_estribos, armadura_simples, armadura_dupla,
    calcular_flecha_branson, imprimir_viga
)
from dimensionamento.laje import (
    calcular_laje_macica, calcular_laje_unid, imprimir_laje
)
from dimensionamento.reservatorio import (
    predimensionar_reservatorio as predim_res,
    paredes_dimensionar, fundo_dimensionar, imprimir_reservatorio
)
from dimensionamento.muro_arrimo import (
    predimensionar_muro, calcular_empuxo,
    verificar_estabilidade, dimensionar_fuste, imprimir_muro
)
from dimensionamento.piscina import (
    combinacoes_piscina, dimensionar_parede as dim_par_pisc,
    dimensionar_fundo as dim_fundo_pisc, imprimir_piscina
)
from dimensionamento.viga_parede import (
    classificar_viga_parede, modelo_biela_tirante, imprimir_viga_parede
)
from relatorio.memorial import gerar_memorial


console = Console() if RICH_OK else None


def titulo(texto):
    if RICH_OK:
        console.print(Panel(f"[bold cyan]{texto}[/bold cyan]", expand=False))
    else:
        print("\n" + "="*60)
        print(texto)
        print("="*60)


def pergunta(msg, default=None, tipo=float):
    if RICH_OK:
        val = Prompt.ask(f"  [yellow]{msg}[/yellow]",
                         default=str(default) if default is not None else ...)
        return tipo(val)
    val = input(f"  {msg} [{default}]: ").strip()
    return tipo(val) if val else tipo(default) if default is not None else tipo(input(f"  {msg}: "))


def _get_fck_fyk_caa():
    fck = pergunta("fck (MPa) [25]", 25, float)
    fyk = pergunta("fyk (MPa) [500]", 500, float)
    caa = input("  CAA (I/II/III/IV) [II]: ").strip() or "II"
    return fck, fyk, caa.upper()


# =========================================================
# Opcoes do menu
# =========================================================

def menu_predim():
    titulo("PRE-DIMENSIONAMENTO")
    print("  1 - Laje\n  2 - Viga\n  3 - Pilar\n  4 - Reservatorio\n  0 - Voltar")
    op = input("  > ").strip()
    if op == "1":
        lx = pergunta("lx (m)", 4.0, float)
        ly = pergunta("ly (m)", 5.0, float)
        uso = input("  Uso (residencial/comercial/garagem) [residencial]: ").strip() or "residencial"
        r = predimensionar_laje(lx, ly, uso)
        for k, v in r.items(): print(f"  {k}: {v}")
    elif op == "2":
        L = pergunta("Vao L (m)", 4.0, float)
        tipo = input("  Tipo (simples/continua/balanco) [continua]: ").strip() or "continua"
        r = predimensionar_viga(L, tipo)
        for k, v in r.items(): print(f"  {k}: {v}")
    elif op == "3":
        Nk = pergunta("Normal caracteristica Nk (kN)", 500, float)
        fck = pergunta("fck (MPa)", 25, float)
        tipo = input("  Tipo (intermediario/extremidade/canto) [intermediario]: ").strip() or "intermediario"
        r = predimensionar_pilar(Nk, fck, tipo)
        for k, v in r.items(): print(f"  {k}: {v}")
    elif op == "4":
        V = pergunta("Volume (m3)", 10, float)
        r = predim_res(V)
        for k, v in r.items(): print(f"  {k}: {v}")


def menu_pilar():
    titulo("DIMENSIONAMENTO - PILAR")
    H = pergunta("Altura livre H (cm)", 300, float)
    hx = pergunta("hx - dimensao em x (cm)", 19, float)
    hy = pergunta("hy - dimensao em y (cm)", 19, float)
    beta = pergunta("beta (coef. flambagem) [1.0]", 1.0, float)
    Nd = pergunta("Normal de calculo Nd (kN)", 300, float)
    Md = pergunta("Momento de calculo Md (kNcm)", 150, float)
    fck, fyk, caa = _get_fck_fyk_caa()

    esb = calcular_esbeltez(H, hx, hy, beta)
    exc = excentricidade_minima(hx, hy)

    nu = Nd / (hx * hy * fck / 1.4)
    e2x = excentricidade_2a_ordem(esb["lam_x"], hx, nu)
    e2y = excentricidade_2a_ordem(esb["lam_y"], hy, nu)
    print(f"\n  e2x (2a ordem) = {e2x} cm | e2y = {e2y} cm")

    dim = dimensionar_secao(Nd, Md, hx, hy, fck, fyk, caa)
    est = estribo_pilar(16.0, min(hx, hy))  # phi_long estimado 16mm

    imprimir_pilar(esb, dim, est)

    barras = barras_pilar(dim["As_adot"])
    print("\n  Sugestoes de armadura:")
    for b in barras: print(f"    {b[0]} barras Ø{b[1]}mm (As={b[2]} cm²)")


def menu_viga():
    titulo("DIMENSIONAMENTO - VIGA")
    bw = pergunta("bw (cm)", 14, float)
    h = pergunta("h (cm)", 40, float)
    d = pergunta("d (cm, ou 0 p/ auto)", 0, float)
    L = pergunta("Vao efetivo L (m)", 4.0, float)
    VSd = pergunta("Cortante de calculo VSd (kN)", 30, float)
    Md = pergunta("Momento positivo Md (kNcm)", 1200, float)
    Md_ser = pergunta("Momento servico Md,ser (kNcm)", 800, float)
    fck, fyk, caa = _get_fck_fyk_caa()

    if d <= 0:
        cobr = {"I":2.5,"II":3.0,"III":4.0,"IV":5.0}.get(caa, 3.0)
        d = h - cobr - 0.625

    cor = verificar_bielas(VSd, bw, d, fck)
    cor.update(dimensionar_estribos(VSd, bw, d, fck, fyk))
    flex = armadura_simples(Md, bw, d, fck, fyk)
    el = calcular_flecha_branson(Md_ser, flex.get("As_cm2", 1), bw, h, d, L, fck)

    imprimir_viga(cor, flex, el)


def menu_laje():
    titulo("DIMENSIONAMENTO - LAJE MACICA")
    print("  Casos: 1=4ap | 2=3ap+1eng(ly) | 3=2ap+2eng(opostos) | 4=2ap+2adj | 5=1ap+3eng | 6=4eng")
    caso = int(input("  Caso de vinculacao: ").strip() or "1")
    lx = pergunta("lx - menor vao (m)", 3.5, float)
    ly = pergunta("ly - maior vao (m)", 4.5, float)
    h_cm = pergunta("Espessura h (cm)", 10, float)
    gk = pergunta("Carga permanente gk (kN/m2, excl. PP)", 1.5, float)
    qk = pergunta("Carga variavel qk (kN/m2)", 1.5, float)
    fck, fyk, caa = _get_fck_fyk_caa()

    res = calcular_laje_macica(lx, ly, h_cm, gk, qk, caso, fck, fyk, caa)
    imprimir_laje(res)


def menu_reservatorio():
    titulo("DIMENSIONAMENTO - RESERVATORIO")
    Vol = pergunta("Volume total (m3)", 10, float)
    H = pergunta("Altura da parede H (m)", 2.0, float)
    L = pergunta("Comprimento L (m)", 3.0, float)
    h_par = pergunta("Espessura da parede (m)", 0.20, float)
    h_fund = pergunta("Espessura do fundo (m)", 0.15, float)
    fck = pergunta("fck (MPa, min 40 para CAA IV)", 40, float)
    fyk = pergunta("fyk (MPa)", 500, float)

    predim = predim_res(Vol)
    par = paredes_dimensionar(H, L, h_par, fck, fyk, "IV")
    fund = fundo_dimensionar(H, L, L, h_fund, fck, fyk, "IV")
    imprimir_reservatorio(predim, par, fund)


def menu_muro():
    titulo("DIMENSIONAMENTO - MURO DE ARRIMO")
    H = pergunta("Altura do muro H (m)", 3.0, float)
    phi = pergunta("Angulo de atrito interno do solo phi (graus)", 30, float)
    gamma = pergunta("Peso especifico do solo (kN/m3)", 18, float)
    qs = pergunta("Sobrecarga superficial qs (kN/m2)", 0, float)
    fck, fyk, caa = _get_fck_fyk_caa()

    predim = predimensionar_muro(H, phi, gamma)
    emp = calcular_empuxo(H, gamma, phi, 0.0, qs)
    estab = verificar_estabilidade(predim, emp, gamma)
    fuste = dimensionar_fuste(predim, emp, fck, fyk, caa)
    imprimir_muro(predim, emp, estab, fuste)


def menu_piscina():
    titulo("DIMENSIONAMENTO - PISCINA")
    H = pergunta("Profundidade da piscina H (m)", 1.5, float)
    Lx = pergunta("Comprimento Lx (m)", 8.0, float)
    Ly = pergunta("Largura Ly (m)", 4.0, float)
    h_par = pergunta("Espessura das paredes (m)", 0.15, float)
    h_fund = pergunta("Espessura do fundo (m)", 0.15, float)
    phi = pergunta("phi do solo externo (graus)", 30, float)
    gs = pergunta("gamma solo externo (kN/m3)", 18, float)
    fck = pergunta("fck (MPa, min 40)", 40, float)
    fyk = pergunta("fyk (MPa)", 500, float)

    combs = combinacoes_piscina(H, phi, gs)
    par_c1 = dim_par_pisc(H, h_par, combs[0], fck, fyk, "IV")
    par_c2 = dim_par_pisc(H, h_par, combs[1], fck, fyk, "IV")
    fundo  = dim_fundo_pisc(H, Lx, Ly, h_fund, fck, fyk, "IV")
    imprimir_piscina(list(combs), par_c1, par_c2, fundo)


def menu_viga_parede():
    titulo("DIMENSIONAMENTO - VIGA-PAREDE (NBR 6118:2023, sec.22.6)")
    L = pergunta("Vao L (m)", 4.0, float)
    h = pergunta("Altura h (m)", 2.5, float)
    Fd = pergunta("Carga de calculo Fd (kN)", 300, float)
    bw = pergunta("Largura bw (cm)", 20, float)
    fck, fyk, caa = _get_fck_fyk_caa()

    classif = classificar_viga_parede(L, h)
    modelo = modelo_biela_tirante(L, h, Fd, bw, fck, fyk, caa)
    imprimir_viga_parede(classif, modelo)


def menu_memorial():
    titulo("GERAR MEMORIAL DESCRITIVO (PDF)")
    obra = input("  Nome da obra: ").strip() or "Obra"
    resp = input("  Responsavel tecnico: ").strip() or "Engenheiro"
    local = input("  Local: ").strip() or "Local"
    saida = input("  Arquivo de saida [memorial.pdf]: ").strip() or "memorial.pdf"
    dados = {"obra": obra, "responsavel": resp, "local": local,
             "data": datetime.now().strftime("%d/%m/%Y")}
    # Memorial basico (sem resultados calculados nesta sessao)
    gerar_memorial({}, saida, dados)


# =========================================================
# Loop principal
# =========================================================

MENU = """
  [1] Pre-dimensionamento (laje / viga / pilar / reservatorio)
  [2] Pilar (esbeltez + flexo-compressao)
  [3] Viga (cortante + flexao + flecha Branson)
  [4] Laje macica (Carini, casos 1-6)
  [5] Reservatorio (cheio e vazio, NBR 6118:2023 sec.21)
  [6] Muro de arrimo (Rankine)
  [7] Piscina (pressoes internas e externas)
  [8] Viga-parede (biela-tirante, NBR 6118:2023 sec.22.6)
  [9] Gerar Memorial Descritivo PDF
  [0] Sair
"""

def main():
    if RICH_OK:
        console.print(Panel(
            "[bold cyan]SISTEMA DE CALCULO ESTRUTURAL - NBR 6118:2023[/bold cyan]\n"
            "[dim]Prof. Carini | Bastos | Araujo | Fusco | Caputo[/dim]",
            expand=False))
    else:
        print("="*60)
        print("SISTEMA DE CALCULO ESTRUTURAL - NBR 6118:2023")
        print("Prof. Carini | Bastos | Araujo | Fusco | Caputo")
        print("="*60)

    OPCOES = {
        "1": menu_predim,
        "2": menu_pilar,
        "3": menu_viga,
        "4": menu_laje,
        "5": menu_reservatorio,
        "6": menu_muro,
        "7": menu_piscina,
        "8": menu_viga_parede,
        "9": menu_memorial,
    }

    while True:
        print(MENU)
        op = input("  Opcao > ").strip()
        if op == "0":
            print("  Encerrando...")
            break
        elif op in OPCOES:
            try:
                OPCOES[op]()
            except KeyboardInterrupt:
                print("\n  [Cancelado]")
            except Exception as e:
                print(f"\n  [ERRO] {type(e).__name__}: {e}")
        else:
            print("  Opcao invalida.")


if __name__ == "__main__":
    main()
