"""F0 / spike OpenToonz: Python gera nível PNG + ToonzScript; OpenToonz cria o .tnz; tcomposer renderiza.

Uso: python3 spikes/f0_opentoonz.py <dir_windows_montado>   (ex.: /mnt/c/Users/DELL/toonstudio-spike)
Só valida viabilidade — não é código de produção.
"""
from __future__ import annotations

import math
import subprocess
import sys
import time
from pathlib import Path, PureWindowsPath

from PIL import Image, ImageDraw

OT = "/mnt/c/Program Files/OpenToonz"
W, H = 1920, 1080


def to_win(p: Path) -> str:
    s = str(p)
    if s.startswith("/mnt/") and len(s) > 6:
        return f"{s[5].upper()}:\\" + s[7:].replace("/", "\\")
    out = subprocess.run(["wslpath", "-w", s], capture_output=True, text=True, check=True)
    return out.stdout.strip()


def ball_frame(i: int, n: int) -> Image.Image:
    """Quique com squash/stretch: desenho redesenhado a cada quadro (não é sprite movido)."""
    t = i / n
    y_air = abs(math.sin(math.pi * t))          # 0 no chão, 1 no topo
    cy = 900 - 600 * y_air
    speed = abs(math.cos(math.pi * t))         # rápido perto do chão
    stretch = 1 + 0.45 * speed * (y_air > 0.05)
    squash = 1.6 if y_air < 0.05 else 1.0
    rx, ry = 70 / math.sqrt(stretch) * squash, 70 * stretch / squash
    cx = 300 + 1300 * t
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx, cy + 70 - 2 * ry, cx + rx, cy + 70], fill=(230, 60, 50, 255), outline=(20, 15, 15, 255), width=8)
    return img


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    lvl = root / "levels" / "ball"
    lvl.mkdir(parents=True, exist_ok=True)
    n = 12
    for i in range(n):
        ball_frame(i, n).save(lvl / f"ball.{i + 1:04d}.png")

    tnz = root / "ball_test.tnz"
    tnz.unlink(missing_ok=True)
    # Exposição em 2s (cada desenho fica 2 quadros), 24 fps → 1 s de animação
    cells = "\n".join(f"scene.setCell({row}, 0, lv, {row // 2 + 1});" for row in range(2 * n))
    script = f"""
scene = new Scene();
lv = scene.loadLevel("ball", "{to_win(lvl / 'ball..png').replace(chr(92), chr(92) * 2)}");
print("level frames: " + lv.frameCount);
{cells}
scene.save("{to_win(tnz).replace(chr(92), chr(92) * 2)}");
print("SPIKE_OK frames=" + scene.frameCount + " cols=" + scene.columnCount);
"""
    js = root / "make_scene.toonzscript"
    js.write_text(script, encoding="utf-8")

    t = time.time()
    p = subprocess.run([f"{OT}/OpenToonz.exe", to_win(js)], capture_output=True, timeout=180)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    print(f"[OpenToonz] exit={p.returncode} {time.time() - t:.1f}s\n{out[-2000:]}")
    print("tnz existe:", tnz.exists())
    if not tnz.exists():
        return 1

    render = root / "render"
    render.mkdir(exist_ok=True)
    for f in render.glob("*"):
        f.unlink()
    t = time.time()
    cmd = [f"{OT}/tcomposer.exe", to_win(tnz), "-o", to_win(render / "out.png"), "-range", "1", str(2 * n)]
    p = subprocess.run(cmd, capture_output=True, timeout=600)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    print(f"[tcomposer] exit={p.returncode} {time.time() - t:.1f}s\n{out[-2000:]}")
    frames = sorted(render.glob("*.png"))
    print("quadros renderizados:", len(frames), [f.name for f in frames[:3]])
    if frames:
        im = Image.open(frames[0])
        print("modo/tamanho:", im.mode, im.size, "alpha min/max:", im.getchannel("A").getextrema() if "A" in im.mode else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
