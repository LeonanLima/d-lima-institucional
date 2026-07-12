"""Renderiza os frames reel-*.html (Edge headless) e monta o Reel MP4 9:16
com movimento suave (zoompan) e cortes, via ffmpeg."""
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
FFMPEG = (r"C:\Users\leona\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_"
          r"Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe")
EXP = ROOT / "docs/design/pecas/export"
PNG = ROOT / "docs/design/pecas/png"
OUTDIR = ROOT / "docs/design/pecas/video"
TMP = Path(r"C:\Users\leona\AppData\Local\Temp\dlima_reel")
PNG.mkdir(parents=True, exist_ok=True)
OUTDIR.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

frames = sorted(EXP.glob("reel-*.html"))
DUR = 3  # segundos por cena

# 1) screenshot 1080x1920
pngs = []
for i, f in enumerate(frames):
    out = PNG / f"{f.stem}.png"
    if out.exists():
        out.unlink()
    subprocess.run([
        EDGE, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
        f"--user-data-dir=C:\\Users\\leona\\AppData\\Local\\Temp\\edgeR{i}",
        "--force-device-scale-factor=2", "--window-size=540,960",
        "--virtual-time-budget=4000", f"--screenshot={out}", f"file:///{f.as_posix()}",
    ], capture_output=True, timeout=90)
    for _ in range(20):
        if out.exists() and out.stat().st_size > 2000:
            break
        time.sleep(0.25)
    print("shot", out.name, out.stat().st_size // 1024, "KB" if out.exists() else "FAIL")
    pngs.append(out)

# 2) um clip por cena com zoom suave
clips = []
for i, p in enumerate(pngs):
    clip = TMP / f"c{i:02d}.mp4"
    vf = (f"scale=1080:1920,zoompan=z='min(zoom+0.0009,1.10)':d={DUR*30}:"
          f"s=1080x1920:fps=30,format=yuv420p")
    subprocess.run([FFMPEG, "-y", "-loop", "1", "-i", str(p), "-t", str(DUR),
                    "-r", "30", "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    str(clip)], capture_output=True, timeout=120)
    clips.append(clip)
    print("clip", clip.name, clip.stat().st_size // 1024 if clip.exists() else "FAIL", "KB")

# 3) concat
lst = TMP / "list.txt"
lst.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
out_mp4 = OUTDIR / "obra-estoura-orcamento-reel.mp4"
subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(out_mp4)], capture_output=True, timeout=180)
print("MP4:", out_mp4, out_mp4.stat().st_size // 1024, "KB" if out_mp4.exists() else "FAIL")
