"""F0 / spike Krita: Python gera ORA com camadas -> `krita --export` salva KRA -> `krita --export` devolve ORA.

Valida a troca de arquivos com camadas sem plugin (o kritarunner 5.3.4.1 no Windows não importa módulos; ver ADR-0004).
Uso: python3 spikes/f0_krita.py <dir>   (ex.: .spike/krita — caminho no WSL funciona via UNC)
"""
from __future__ import annotations

import io
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

KRITA = "/mnt/c/Program Files/Krita (x64)/bin/krita.com"
W, H = 1920, 1080


def to_win(p: Path) -> str:
    return subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True, check=True).stdout.strip()


def layers() -> dict[str, Image.Image]:
    sky = Image.new("RGBA", (W, H), (150, 200, 235, 255))
    hills = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hills).ellipse([-400, 600, 1200, 1500], fill=(90, 150, 80, 255))
    tree = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(tree)
    d.rectangle([1500, 500, 1560, 1000], fill=(110, 70, 40, 255))
    d.ellipse([1380, 300, 1680, 620], fill=(40, 110, 50, 255), outline=(15, 30, 15, 255), width=6)
    return {"BG_ceu": sky, "MG_colinas": hills, "FG_arvore": tree}  # fundo -> frente


def write_ora(path: Path, ls: dict[str, Image.Image]) -> Image.Image:
    names = list(ls)[::-1]  # stack.xml lista do topo para o fundo
    stack = "".join(f'<layer name="{n}" src="data/{n}.png" x="0" y="0" opacity="1.0" visibility="visible"/>' for n in names)
    flat = Image.new("RGBA", (W, H))
    for im in ls.values():
        flat.alpha_composite(im)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr("stack.xml", f'<?xml version="1.0" encoding="UTF-8"?><image w="{W}" h="{H}"><stack>{stack}</stack></image>')
        for n, im in ls.items():
            b = io.BytesIO(); im.save(b, "PNG"); z.writestr(f"data/{n}.png", b.getvalue())
        b = io.BytesIO(); flat.save(b, "PNG"); z.writestr("mergedimage.png", b.getvalue())
    return flat


def krita_export(src: Path, dst: Path) -> None:
    dst.unlink(missing_ok=True)
    t = time.time()
    subprocess.run([KRITA, "--nosplash", to_win(src), "--export", "--export-filename", to_win(dst)],
                   capture_output=True, timeout=300)
    print(f"[krita] {src.name} -> {dst.name}: {'ok' if dst.exists() else 'FALHOU'} ({time.time() - t:.1f}s)")


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    root.mkdir(parents=True, exist_ok=True)
    ls = layers()
    ora, kra, back, flat_png = root / "cenario.ora", root / "cenario.kra", root / "volta.ora", root / "volta.png"
    flat = write_ora(ora, ls)
    krita_export(ora, kra)
    krita_export(kra, back)
    krita_export(kra, flat_png)
    with zipfile.ZipFile(back) as z:
        st = z.read("stack.xml").decode()
        found = re.findall(r'name="(\w+)" x="(\d+)"[^>]*src="([^"]+)" y="(\d+)"', st)
        print("camadas devolvidas (nome, x, src, y):", found)
        ok_names = sorted(n for n, *_ in found) == sorted(ls)
    diff = max(e[1] for e in ImageChops.difference(Image.open(flat_png).convert("RGBA"), flat).getextrema())
    print(f"nomes preservados: {ok_names} · diferença máx. da imagem achatada: {diff}")
    return 0 if ok_names and diff == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
