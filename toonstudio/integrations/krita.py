"""Integração com o Krita 5.3 por arquivos + linha de comando (ADR-0004): ORA ↔ KRA, com camadas nomeadas."""
from __future__ import annotations

import io
import re
import subprocess
import zipfile
from pathlib import Path

from PIL import Image

from ..core.config import StudioError, to_win, tool

Image.MAX_IMAGE_PIXELS = None


def _export(src: Path, dst: Path, timeout: int = 600) -> Path:
    dst.unlink(missing_ok=True)
    subprocess.run([tool("krita"), "--nosplash", to_win(src), "--export", "--export-filename", to_win(dst)],
                   capture_output=True, timeout=timeout)
    if not dst.exists():
        raise StudioError(f"Krita não exportou {src.name} → {dst.name}")
    return dst


def ora_to_kra(ora: Path) -> Path:
    return _export(ora, ora.with_suffix(".kra"))


def kra_layers(kra: Path, out_dir: Path) -> list[dict]:
    """Volta do Krita: KRA → ORA → PNG por camada (nome, posição)."""
    ora = _export(kra, out_dir / (kra.stem + ".roundtrip.ora"))
    out = []
    with zipfile.ZipFile(ora) as z:
        st = z.read("stack.xml").decode()
        for m in re.finditer(r"<layer ([^>]*)/>", st):
            a = dict(re.findall(r'(\S+?)="([^"]*)"', m.group(1)))
            p = out_dir / f"{a['name']}.png"
            p.write_bytes(z.read(a["src"]))
            out.append({"name": a["name"], "x": int(a["x"]), "y": int(a["y"]), "file": p.name})
    return out


def layers_to_kra(layer_dir: Path, kra: Path, meta: dict) -> Path:
    """Cenário em camadas → um KRA editável (cada camada com seu nome; larguras diferentes alinhadas à esquerda)."""
    layers = sorted(meta["layers"], key=lambda l: l["z"])
    imgs = [(l["name"], Image.open(layer_dir / l["file"])) for l in layers]
    W = max(im.width for _, im in imgs)
    H = max(im.height for _, im in imgs)
    ora = kra.with_suffix(".ora")
    stack = "".join(f'<layer name="{n}" src="data/{n}.png" x="0" y="0" opacity="1.0" visibility="visible"/>'
                    for n, _ in reversed(imgs))
    with zipfile.ZipFile(ora, "w") as z:
        z.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr("stack.xml", f'<?xml version="1.0" encoding="UTF-8"?><image w="{W}" h="{H}"><stack>{stack}</stack></image>')
        for n, im in imgs:
            b = io.BytesIO(); im.save(b, "PNG"); z.writestr(f"data/{n}.png", b.getvalue())
        th = imgs[0][1].copy(); th.thumbnail((256, 256))
        b = io.BytesIO(); th.save(b, "PNG"); z.writestr("Thumbnails/thumbnail.png", b.getvalue())
        b = io.BytesIO(); imgs[0][1].convert("RGBA").save(b, "PNG"); z.writestr("mergedimage.png", b.getvalue())
    out = _export(ora, kra, timeout=900)
    ora.unlink(missing_ok=True)
    return out
