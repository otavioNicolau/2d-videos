"""Laboratório de dança: um vídeo curto com TODOS os passos lado a lado (Laurinha), no tempo de uma batida de 0,6 s.

Serve para o usuário avaliar de olho cada passo (braços, pernas, corpo) sem esperar um clipe inteiro, e para comparar
ANTES × DEPOIS de cada ajuste da animação (versão A1, A2…).
Uso: PYTHONPATH=. .venv/bin/python scripts/referencias/laboratorio_danca.py [--versao A1] [--quem laurinha] [--estilos festa,lado]
Saída: Windows → Canal\\Laboratório de dança\\<versão> - <quem>.mp4
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from toonstudio.animation import cycles  # noqa: E402
from toonstudio.characters.base import expression  # noqa: E402
from toonstudio.core.registry import character  # noqa: E402
from toonstudio.drawing.ink import to_array  # noqa: E402

WIN = Path("/mnt/c/Users/DELL/Videos/Laurinha e Luisinho/Canal/Laboratório de dança")
BATIDA, FPS, SEG = 0.6, 24, 7.2           # 12 batidas por passo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versao", default="A1")
    ap.add_argument("--quem", default="laurinha")
    ap.add_argument("--estilos", default="")
    a = ap.parse_args()
    estilos = [e for e in (a.estilos.split(",") if a.estilos else cycles.CHOREO) if e]
    ch = character(a.quem)
    base = {**ch.pose(), **expression("happy"), "turn": 0.0}
    beats = [i * BATIDA for i in range(int(SEG / BATIDA) + 4)]
    cols = 6
    rows = (len(estilos) + cols - 1) // cols
    cw, chh = 300, 300
    font = ImageFont.truetype(str(ROOT / "library" / "fonts" / next(p.name for p in (ROOT / "library" / "fonts").glob("*.ttf"))), 22) \
        if list((ROOT / "library" / "fonts").glob("*.ttf")) else ImageFont.load_default()
    tmp = Path(tempfile.mkdtemp())
    n = int(SEG * FPS)
    for f in range(n):
        t = f / FPS
        sheet = Image.new("RGB", (cols * cw, rows * chh + 50), (255, 246, 228))
        d = ImageDraw.Draw(sheet)
        d.text((12, rows * chh + 12), f"Laboratório de dança — versão {a.versao} — {a.quem} — batida {int(t / BATIDA) + 1}",
               fill=(60, 60, 60), font=font)
        for i, e in enumerate(estilos):
            ov = cycles.dance(e, t, beats, 1.0, 0.0)
            P = dict(base)
            for k, v in ov.items():
                if k.endswith("+"):
                    P[k[:-1]] = P.get(k[:-1], 0.0) + v
                else:
                    P[k] = v
            im = Image.fromarray(to_array(ch.render(P, 0.42, 0, 0)))
            im.thumbnail((cw, chh - 30))
            x, y = (i % cols) * cw, (i // cols) * chh
            if (int(t / BATIDA) % 2 == 0) and (t % BATIDA) < 0.08:          # marca a batida (pisca a borda)
                d.rectangle([x + 2, y + 2, x + cw - 3, y + chh - 3], outline=(255, 120, 0), width=4)
            sheet.paste(im, (x + (cw - im.width) // 2, y + 26), im)
            d.text((x + 10, y + 4), e, fill=(30, 30, 30), font=font)
        sheet.save(tmp / f"f{f:04d}.png")
    WIN.mkdir(parents=True, exist_ok=True)
    out = WIN / f"{a.versao} - {a.quem}.mp4"
    # metrônomo: clique em cada batida, para conferir se o passo bate no tempo
    sr = 48000
    au = np.zeros(int(SEG * sr), np.float32)
    for b in beats:
        i = int(b * sr)
        if i < len(au):
            k = np.arange(int(0.03 * sr))
            au[i:i + len(k)] += (0.5 * np.sin(2 * np.pi * 1800 * k / sr) * np.exp(-k / (0.006 * sr)))[: len(au) - i]
    import soundfile as sf
    sf.write(tmp / "click.wav", au, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f%04d.png"), "-i", str(tmp / "click.wav"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-shortest", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main()
