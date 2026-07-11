import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = (ROOT / "agencia/config/fonts-mont.css").read_text(encoding="utf-8")

BASE = """
:root { --carvao:#161616; --dourado:#C9A84C; --claro:#F7F5EF; --verde:#2D5016; }
* { box-sizing:border-box; margin:0; padding:0; }
.wrap { font-family:'Mont','Helvetica Neue',Arial,sans-serif; background:#0c0c0c;
  padding:32px; display:flex; flex-direction:column; align-items:center; gap:28px; }
.hint { color:#8a8a8a; font-size:13px; letter-spacing:.14em; text-transform:uppercase;
  font-weight:500; text-align:center; }
.frame { background:var(--carvao); color:var(--claro); position:relative; overflow:hidden;
  box-shadow:0 24px 60px rgba(0,0,0,.5); }
.square { width:min(540px,92vw); aspect-ratio:1/1; }
.vertical { width:min(430px,80vw); aspect-ratio:9/16; }
.pad { position:absolute; inset:0; padding:56px 52px; display:flex; flex-direction:column; }
.rule { position:absolute; left:0; top:0; width:100%; height:6px;
  background:linear-gradient(90deg,var(--dourado) 0%,var(--dourado) 62%,transparent 62%); }
.stair::after { content:""; position:absolute; right:-40px; bottom:-40px; width:220px; height:220px;
  background:repeating-linear-gradient(0deg,transparent 0 26px,rgba(201,168,76,.10) 26px 30px);
  transform:skewX(-18deg); pointer-events:none; }
.top { display:flex; align-items:baseline; gap:18px; }
.num { font-size:60px; font-weight:600; line-height:.8; color:var(--dourado); font-variant-numeric:tabular-nums; }
.kicker { font-size:14px; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:var(--dourado); }
.title { font-weight:600; font-size:44px; line-height:1.05; letter-spacing:-.01em; text-wrap:balance; margin-top:24px; }
.body { font-weight:300; font-size:20px; line-height:1.5; color:#d9d5cb; max-width:30ch; margin-top:22px; }
.foot { margin-top:auto; display:flex; justify-content:space-between; align-items:flex-end;
  padding-top:24px; position:relative; z-index:1; }
.mark { font-weight:600; letter-spacing:.16em; font-size:16px; color:var(--claro); }
.tag { font-weight:500; font-size:13px; letter-spacing:.1em; color:var(--dourado); text-align:right; }
.errs { margin-top:30px; display:flex; flex-direction:column; gap:20px; }
.err { display:flex; gap:18px; align-items:flex-start; }
.err .en { font-weight:600; font-size:34px; color:var(--dourado); line-height:1; font-variant-numeric:tabular-nums; }
.err .et { font-weight:300; font-size:19px; line-height:1.4; color:#d9d5cb; }
.err .et b { font-weight:600; color:var(--claro); }
.cover .title { font-size:52px; margin-top:30px; }
.cta .title { color:var(--dourado); }
.cover::before { content:""; position:absolute; inset:0;
  background:radial-gradient(120% 80% at 100% 0%, rgba(201,168,76,.14), transparent 55%); }
"""


def foot(mark_tag=""):
    tag = f'<div class="tag">{mark_tag}</div>' if mark_tag else ""
    return f'<div class="foot"><div class="mark">D\'LIMA</div>{tag}</div>'


def slide(shape, kicker, title, body, n="", tag="", extra=""):
    cls = "frame " + shape + " stair"
    if extra:
        cls += " " + extra
    num = f'<div class="num">{n}</div>' if n else ""
    title = title.replace("\n", "<br>")
    bodyhtml = f'<p class="body">{body}</p>' if body else ""
    return f"""<div class="{cls}"><div class="pad">
      <div class="rule"></div>
      <div class="top">{num}<div class="kicker">{kicker}</div></div>
      <h2 class="title">{title}</h2>
      {bodyhtml}
      {foot(tag)}
    </div></div>"""


def page(title, hint_top, hint_bot, inner):
    return f"""<style>
{FONTS}
{BASE}
</style>
<div class="wrap">
  <div class="hint">{hint_top}</div>
  {inner}
  <div class="hint">{hint_bot}</div>
</div>"""


def write(name, html):
    out = ROOT / "docs/design/pecas" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("written", name, len(html))


EXP_DIR = ROOT / "docs/design/pecas/export"


def export(slug, shape, frames):
    """Emite uma pagina por frame (540px) p/ screenshot em 1080 (scale 2)."""
    EXP_DIR.mkdir(parents=True, exist_ok=True)
    over = ("html,body{margin:0;padding:0;background:#161616;"
            "font-family:'Mont','Helvetica Neue',Arial,sans-serif;}"
            ".frame{box-shadow:none!important;"
            "font-family:'Mont','Helvetica Neue',Arial,sans-serif;}"
            ".square{width:540px;height:540px;aspect-ratio:auto;}"
            ".vertical{width:540px;height:960px;aspect-ratio:auto;}")
    for i, frame in enumerate(frames, 1):
        html = f"<style>\n{FONTS}\n{BASE}\n{over}\n</style>\n{frame}"
        (EXP_DIR / f"{slug}-{i:02d}.html").write_text(html, encoding="utf-8")
    print("export", slug, len(frames), "frames", shape)


# ---- 2) Reel cover (9:16) — Por que a obra estoura o orcamento
reel = slide("vertical", "Bastidor de obra", "Por que a obra\nestoura o\norçamento",
             "Quase sempre começou sem projeto fechado. Os 3 pontos onde o custo escapa neste Reel.",
             tag="assista  ▶", extra="cover")
write("obra-estoura-orcamento.html",
      page("Reel", "Capa de Reel · 1080×1920 · @leonan.dlima", reel and "Peça aprovada · Agência Automática D'LIMA", reel))

# ---- 3) Carrossel — Quanto custa o m2
m2 = [
    slide("square", "D'LIMA · Engenharia de custos", "Quanto custa\no m² de verdade\nem 2026",
          "A resposta que roda na internet esconde metade do custo. Vou abrir a conta real.",
          tag="arraste  →", extra="cover"),
    slide("square", "O truque do número bonito", "Só a estrutura\nnão é a obra",
          "O valor barato que você vê por aí costuma ser só a estrutura. Sem fundação de verdade, sem acabamento, sem projeto, sem imprevisto.", n="01"),
    slide("square", "Onde o dinheiro entra", "A conta real,\npor etapa",
          "Movimento de terra, fundação, estrutura, alvenaria, instalações, acabamento. Cada etapa tem seu peso, e o acabamento surpreende quase todo mundo.", n="02"),
    slide("square", "O item esquecido", "Projeto e\nimprevisto",
          "Projeto bem feito não é gasto, é o que segura o custo lá na frente. E toda obra honesta reserva uma margem pro que a terra ainda vai revelar.", n="03"),
    slide("square", "Seu próximo passo", "Vem com o\nnúmero certo",
          "Guarda esse post pra quando for orçar. Quer a conta fechada pro seu caso? Me chama no direct.",
          n="04", tag="@leonan.dlima", extra="cta"),
]
write("quanto-custa-m2.html",
      page("Carrossel", "Carrossel · 5 slides · 1080×1080 · @leonan.dlima", "Peça aprovada · Agência Automática D'LIMA", "\n".join(m2)))
export("quanto-custa-m2", "square", m2)

# ---- 4) Feed unico — 3 erros que encarecem a fundacao
errs = """<div class="errs">
  <div class="err"><div class="en">01</div><div class="et"><b>Chutar sem sondagem.</b> Escolher o tipo de fundação sem conhecer o solo é apostar com o seu dinheiro.</div></div>
  <div class="err"><div class="en">02</div><div class="et"><b>Superdimensionar por medo.</b> Concreto e aço a mais que o cálculo pede é custo enterrado, literalmente.</div></div>
  <div class="err"><div class="en">03</div><div class="et"><b>Copiar a do vizinho.</b> O terreno ao lado pode ter outro solo. Fundação não se copia, se calcula.</div></div>
</div>"""
feed = f"""<div class="frame square stair"><div class="pad">
  <div class="rule"></div>
  <div class="top"><div class="kicker">A parte que ninguém vê</div></div>
  <h2 class="title">3 erros que<br>encarecem a<br>fundação</h2>
  {errs}
  {foot('@leonan.dlima')}
</div></div>"""
write("erros-fundacao.html",
      page("Feed", "Feed · 1080×1080 · @leonan.dlima", "Peça aprovada · Agência Automática D'LIMA", feed))
export("erros-fundacao", "square", [feed])

# ---- 5) Carrossel — Casa pronta ou construir
casa = [
    slide("square", "Decisão com número", "Casa pronta\nou construir?",
          "Essa dúvida trava muita gente boa. Dá pra decidir com número, não com achismo.",
          tag="arraste  →", extra="cover"),
    slide("square", "Caminho A", "Construir\ndo zero",
          "Rende mais casa pelo mesmo dinheiro quando você tem terreno e paciência. O preço é prazo maior e sua gestão no meio.", n="01"),
    slide("square", "Caminho B", "Comprar\npronto",
          "Ganha em prazo e previsibilidade: você já sabe o que vai receber e quando. Costuma custar mais pelo metro entregue.", n="02"),
    slide("square", "O que pesa na balança", "Prazo, custo\ne risco",
          "Não existe resposta única. Existe a resposta pro seu terreno, sua pressa e o quanto de obra você aguenta tocar.", n="03"),
    slide("square", "Seu próximo passo", "Me diz a sua\nsituação",
          "Comenta aqui se você já tem terreno ou não que eu te mostro o caminho que compensa no seu caso.",
          n="04", tag="@leonan.dlima", extra="cta"),
]
write("casa-pronta-ou-construir.html",
      page("Carrossel", "Carrossel · 5 slides · 1080×1080 · @leonan.dlima", "Peça aprovada · Agência Automática D'LIMA", "\n".join(casa)))
export("casa-pronta-ou-construir", "square", casa)

# Reel: capa 9:16 (mídia final precisa ser MP4; exportamos a capa como referência)
export("obra-estoura-orcamento", "vertical", [reel])

print("OK")
