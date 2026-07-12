"""Gera os frames verticais (9:16) do Reel 'Por que a obra estoura o orcamento'
a partir do roteiro cena a cena. Saida: docs/design/pecas/export/reel-NN.html."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = (ROOT / "agencia/config/fonts-mont.css").read_text(encoding="utf-8")

# Roteiro cena a cena (gancho -> erros -> CTA)
CENAS = [
    {"kicker": "Bastidor de obra", "big": "Por que a obra\nestoura o\norçamento",
     "sub": "", "cta": False, "cover": True},
    {"kicker": "O motivo é quase sempre o mesmo", "big": "Começou\nsem projeto\nfechado",
     "sub": "E aí cada decisão vira improviso no meio da obra.", "cta": False},
    {"kicker": "Erro 1", "big": "Muda o piso\nno meio do\ncaminho",
     "sub": "Compra, quebra, recompra. Dinheiro saindo duas vezes.", "cta": False},
    {"kicker": "Erro 2", "big": "Fundação\nsubdimensionada",
     "sub": "Sem sondagem, você descobre o problema no pior momento.", "cta": False},
    {"kicker": "Erro 3", "big": "Refaz parede\nque já estava\npronta",
     "sub": "Retrabalho é o custo mais silencioso da obra.", "cta": False},
    {"kicker": "A saída", "big": "Trave o custo\nantes da\nprimeira viga",
     "sub": "Projeto fechado e orçamento por etapa. Chama no direct.", "cta": True},
]

CSS = """
:root{--carvao:#161616;--dourado:#C9A84C;--claro:#F7F5EF;}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{margin:0;background:#161616;font-family:'Mont','Helvetica Neue',Arial,sans-serif;}
.f{width:540px;height:960px;background:var(--carvao);color:var(--claro);position:relative;
   overflow:hidden;padding:80px 56px;display:flex;flex-direction:column;}
.f .rule{position:absolute;left:0;top:0;width:100%;height:8px;
   background:linear-gradient(90deg,var(--dourado) 0 62%,transparent 62%);}
.f::after{content:"";position:absolute;right:-50px;bottom:-50px;width:280px;height:280px;
   background:repeating-linear-gradient(0deg,transparent 0 30px,rgba(201,168,76,.10) 30px 34px);
   transform:skewX(-18deg);}
.kicker{font-size:22px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;
   color:var(--dourado);}
.big{font-weight:600;font-size:62px;line-height:1.03;letter-spacing:-.01em;margin-top:40px;}
.sub{font-weight:300;font-size:27px;line-height:1.45;color:#d9d5cb;margin-top:34px;max-width:22ch;}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;
   position:relative;z-index:1;}
.mark{font-weight:600;letter-spacing:.16em;font-size:22px;}
.tag{font-weight:500;font-size:18px;letter-spacing:.1em;color:var(--dourado);}
.cover .big{font-size:70px;margin-top:60px;}
.cta .big{color:var(--dourado);}
.cover::before{content:"";position:absolute;inset:0;
   background:radial-gradient(120% 70% at 100% 0%,rgba(201,168,76,.16),transparent 55%);}
"""

EXP = ROOT / "docs/design/pecas/export"
EXP.mkdir(parents=True, exist_ok=True)

for i, c in enumerate(CENAS, 1):
    cls = "f" + (" cover" if c.get("cover") else "") + (" cta" if c.get("cta") else "")
    big = c["big"].replace("\n", "<br>")
    sub = f'<p class="sub">{c["sub"]}</p>' if c["sub"] else ""
    tag = '<div class="tag">@leonan.dlima</div>' if c.get("cta") else ""
    html = f"""<style>{FONTS}{CSS}</style>
<div class="{cls}"><div class="rule"></div>
  <div class="kicker">{c['kicker']}</div>
  <h2 class="big">{big}</h2>
  {sub}
  <div class="foot"><div class="mark">D'LIMA</div>{tag}</div>
</div>"""
    (EXP / f"reel-{i:02d}.html").write_text(html, encoding="utf-8")
    print("reel frame", i, c["kicker"])
print("OK", len(CENAS), "frames")
