import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
logo = (ROOT / "docs/design/logo-dlima.html").read_text(encoding="utf-8")
fonts = "\n".join(re.findall(r"@font-face\s*\{.*?\}", logo, re.S))

SLIDES = [
    {
        "n": "",
        "kicker": "D'LIMA · Engenharia & Incorporação",
        "title": "Você ainda paga\na casa do outro?",
        "body": "Todo mês o aluguel sai da sua conta e some. "
                "No fim do ano, você somou o preço de um carro e continua sem nada seu.",
        "tag": "arraste  →",
        "cover": True,
    },
    {
        "n": "01",
        "kicker": "A conta que ninguém faz",
        "title": "A parcela do MCMV\nvs. o seu aluguel",
        "body": "Em muitas cidades a parcela de um financiamento Minha Casa Minha Vida "
                "fica perto do que você já paga de aluguel. A diferença é o destino: "
                "uma parcela vira patrimônio, o aluguel vira recibo.",
        "tag": "",
    },
    {
        "n": "02",
        "kicker": "O primeiro passo",
        "title": "Enquadramento\npor faixa de renda",
        "body": "O programa separa as famílias por faixa de renda. É isso que define "
                "quanto de subsídio você recebe e qual juro paga. Saber a sua faixa "
                "antes de tudo evita frustração lá na frente.",
        "tag": "",
    },
    {
        "n": "03",
        "kicker": "O empurrão do governo",
        "title": "Quanto entra\nde subsídio",
        "body": "Nas faixas mais baixas, uma parte do valor do imóvel é um desconto "
                "que não volta pro seu bolso mensal: é abatimento direto. "
                "Isso reduz o quanto você financia e a parcela cai junto.",
        "tag": "",
    },
    {
        "n": "04",
        "kicker": "Antes de aprovar",
        "title": "O que o banco\nolha em você",
        "body": "Renda comprovada, nome limpo, tempo de trabalho e a relação entre "
                "parcela e renda. Organizar esses quatro pontos antes de dar entrada "
                "é o que separa quem aprova de quem espera.",
        "tag": "",
    },
    {
        "n": "05",
        "kicker": "Seu próximo passo",
        "title": "Vamos ver se\na sua renda encaixa",
        "body": "Sem promessa milagrosa. É engenharia de custo aplicada à sua vida. "
                "Me chama no direct com a sua renda que eu te mostro, na real, "
                "se dá pra sair do aluguel ainda esse ano.",
        "tag": "@leonan.dlima · dlimaengenharia.org",
        "cta": True,
    },
]


def slide_html(s):
    cls = "slide"
    if s.get("cover"):
        cls += " cover"
    if s.get("cta"):
        cls += " cta"
    num = f'<div class="num">{s["n"]}</div>' if s["n"] else ""
    title = s["title"].replace("\n", "<br>")
    tag = f'<div class="tag">{s["tag"]}</div>' if s.get("tag") else ""
    return f"""<div class="{cls}">
      <div class="rule"></div>
      <div class="top">
        {num}
        <div class="kicker">{s['kicker']}</div>
      </div>
      <h2 class="title">{title}</h2>
      <p class="body">{s['body']}</p>
      <div class="foot">
        <div class="mark">D'LIMA</div>
        {tag}
      </div>
    </div>"""


slides = "\n".join(slide_html(s) for s in SLIDES)

html = f"""<style>
{fonts}
:root {{
  --carvao:#161616; --dourado:#C9A84C; --claro:#F7F5EF; --verde:#2D5016;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
.wrap {{
  font-family:'Mont','Helvetica Neue',Arial,sans-serif;
  background:#0c0c0c; padding:32px; display:flex; flex-direction:column;
  align-items:center; gap:28px;
}}
.hint {{
  color:#8a8a8a; font-size:14px; letter-spacing:.14em; text-transform:uppercase;
  font-weight:500; text-align:center;
}}
.slide {{
  width:min(540px,92vw); aspect-ratio:1/1; background:var(--carvao);
  color:var(--claro); position:relative; overflow:hidden;
  padding:56px 52px; display:flex; flex-direction:column;
  box-shadow:0 24px 60px rgba(0,0,0,.5);
}}
.slide .rule {{
  position:absolute; left:0; top:0; width:100%; height:6px;
  background:linear-gradient(90deg,var(--dourado) 0%,var(--dourado) 62%,transparent 62%);
}}
/* escada de lajes: motivo do rodape, evoca o "D" da logo */
.slide::after {{
  content:""; position:absolute; right:-40px; bottom:-40px; width:220px; height:220px;
  background:
    repeating-linear-gradient(0deg, transparent 0 26px, rgba(201,168,76,.10) 26px 30px);
  transform:skewX(-18deg); pointer-events:none;
}}
.top {{ display:flex; align-items:baseline; gap:18px; }}
.num {{
  font-size:64px; font-weight:600; line-height:.8; color:var(--dourado);
  font-variant-numeric:tabular-nums;
}}
.kicker {{
  font-size:15px; font-weight:600; letter-spacing:.22em; text-transform:uppercase;
  color:var(--dourado);
}}
.title {{
  font-weight:600; font-size:46px; line-height:1.04; letter-spacing:-.01em;
  text-wrap:balance; margin-top:26px;
}}
.body {{
  font-weight:300; font-size:21px; line-height:1.5; color:#d9d5cb;
  max-width:30ch; margin-top:24px;
}}
.foot {{
  margin-top:auto; display:flex; justify-content:space-between; align-items:flex-end;
  padding-top:28px; position:relative; z-index:1;
}}
.mark {{ font-weight:600; letter-spacing:.16em; font-size:17px; color:var(--claro); }}
.tag {{
  font-weight:500; font-size:14px; letter-spacing:.1em; color:var(--dourado);
  text-align:right;
}}
/* capa */
.slide.cover {{ background:var(--carvao); }}
.slide.cover .title {{ font-size:56px; margin-top:34px; }}
.slide.cover .kicker {{ color:#9a9488; }}
.slide.cover::before {{
  content:""; position:absolute; inset:0;
  background:radial-gradient(120% 80% at 100% 0%, rgba(201,168,76,.14), transparent 55%);
}}
.slide.cover .tag {{ font-size:16px; letter-spacing:.28em; text-transform:uppercase; }}
/* cta */
.slide.cta {{
  background:linear-gradient(160deg,#1c1c1c,#161616 60%);
}}
.slide.cta .title {{ color:var(--dourado); }}
</style>
<div class="wrap">
  <div class="hint">Carrossel · 6 slides · 1080×1080 · @leonan.dlima</div>
  {slides}
  <div class="hint">Peça gerada pela Agência Automática D'LIMA · aguardando aprovação</div>
</div>"""

out = ROOT / "docs/design/pecas/sair-do-aluguel.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("written", out, len(html), "bytes")
