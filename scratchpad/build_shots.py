import subprocess
import struct
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
EXP = ROOT / "docs/design/pecas/export"
OUT = ROOT / "docs/design/pecas/png"
OUT.mkdir(parents=True, exist_ok=True)


def dims(p: Path):
    d = p.read_bytes()
    return struct.unpack(">II", d[16:24])


files = sorted(EXP.glob("*.html"))
for i, f in enumerate(files):
    slug = f.stem
    ws = "540,960" if slug.startswith("obra-estoura") else "540,540"
    out = OUT / f"{slug}.png"
    if out.exists():
        out.unlink()
    cmd = [
        EDGE, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
        f"--user-data-dir=C:\\Users\\leona\\AppData\\Local\\Temp\\edgeS{i}",
        "--force-device-scale-factor=2", f"--window-size={ws}",
        f"--screenshot={out}", f"file:///{f.as_posix()}",
    ]
    subprocess.run(cmd, capture_output=True, timeout=90)
    # Edge as vezes retorna antes de fechar o arquivo; espera curta e confere.
    for _ in range(20):
        if out.exists() and out.stat().st_size > 2000:
            break
        time.sleep(0.25)
    if out.exists():
        w, h = dims(out)
        print(f"ok {slug}.png {w}x{h} {out.stat().st_size//1024}KB")
    else:
        print(f"FAIL {slug}")

print("total:", len(list(OUT.glob("*.png"))))
