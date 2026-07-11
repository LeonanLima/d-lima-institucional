"""Subseta a Montserrat (300/500/600) só com os glifos usados nas peças e
gera um CSS reutilizável com @font-face em base64 (TTF subsetado).
Rode uma vez; os builders de arte importam agencia/config/fonts-mont.css."""
import base64
import io
from pathlib import Path

from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = Path("C:/Windows/Fonts")
WEIGHTS = {300: "Montserrat-Light.ttf", 500: "Montserrat-Medium.ttf", 600: "Montserrat-SemiBold.ttf"}

# Superset seguro: ASCII imprimível + acentos PT-BR + símbolos usados nas peças.
CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " .,;:!?()[]{}\"'-–—/\\&%+=@#°ºª"
    "ÁÀÂÃÄÉÊÈËÍÎÏÓÔÕÖÚÛÜÇáàâãäéêèëíîïóôõöúûüçÑñ"
    "→▶·…"
)


def subset_face(src: Path, chars: str) -> bytes:
    opts = subset.Options(
        layout_features=[], hinting=False, desubroutinize=True,
        notdef_outline=True, recalc_bounds=True, glyph_names=False,
        drop_tables=["GPOS", "GSUB", "GDEF", "kern", "FFTM", "DSIG"],
    )
    font = subset.load_font(str(src), opts)
    ss = subset.Subsetter(opts)
    ss.populate(text=chars)
    ss.subset(font)
    buf = io.BytesIO()
    subset.save_font(font, buf, opts)
    return buf.getvalue()


blocks = []
for weight, fname in WEIGHTS.items():
    src = FONTS_DIR / fname
    data = subset_face(src, CHARS)
    b64 = base64.b64encode(data).decode("ascii")
    print(f"weight {weight}: {len(data)//1024} KB subsetado")
    blocks.append(
        "@font-face{font-family:'Mont';font-style:normal;font-weight:%d;"
        "font-display:swap;src:url(data:font/ttf;base64,%s) format('truetype');}"
        % (weight, b64)
    )

out = ROOT / "agencia/config/fonts-mont.css"
out.write_text("\n".join(blocks), encoding="utf-8")
print("written", out, len(out.read_text(encoding='utf-8'))//1024, "KB total")
