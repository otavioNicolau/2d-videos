"""Folha de modelo (model sheet): vistas, expressões, bocas e proporções, gerada da mesma definição usada na animação.

Saídas: PNG da folha inteira e ORA com uma camada por bloco (vira KRA editável no Krita, ADR-0004).
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont

from .base import EXPRESSIONS, VISEMES, Character, expression

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG = (250, 246, 236, 255)


def _font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except OSError:
        return ImageFont.load_default()


def _render(ch: Character, pose: dict, scale: float) -> Image.Image:
    arr = ch.render_array(pose, scale=scale, jitter=0.0)
    return Image.fromarray(arr, "RGBA")


def _crop_head(ch: Character, img: Image.Image, scale: float) -> Image.Image:
    """Recorta a região da cabeça (parte de cima do personagem) para pranchas de rosto."""
    bbox = img.getbbox()
    if not bbox:
        return img
    l, t, r, b = bbox
    h = int(ch.height * 0.58 * scale)
    cx = (l + r) // 2
    return img.crop((cx - h // 2 - 20, t - 10, cx + h // 2 + 20, t + h))


def _row(cells: list[tuple[str, Image.Image]], cell_w: int, cell_h: int, font) -> Image.Image:
    row = Image.new("RGBA", (cell_w * len(cells), cell_h + 46), BG)
    d = ImageDraw.Draw(row)
    for i, (label, im) in enumerate(cells):
        im = im.copy()
        im.thumbnail((cell_w - 16, cell_h - 8))
        x = i * cell_w + (cell_w - im.width) // 2
        y = cell_h - im.height
        row.alpha_composite(im, (x, y))
        tw = d.textlength(label, font=font)
        d.text((i * cell_w + (cell_w - tw) / 2, cell_h + 10), label, fill=(60, 45, 40), font=font)
    return row


def build(ch: Character, out_dir: Path, scale: float = 1.0) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    f_title, f_lab = _font(46), _font(26)
    blocks: dict[str, Image.Image] = {}

    # 1. vistas (turnaround) com linhas de proporção
    views = [("frente", {"turn": 0.0}), ("3/4", {"turn": 0.5}), ("perfil", {"turn": 1.0}),
             ("3/4 costas", {"turn": -0.55, "back": True}), ("costas", {"turn": 0.0, "back": True})]
    imgs = [(lab, _render(ch, p, scale)) for lab, p in views]
    cw, chh = int(ch.canvas[0] * scale * 0.62), int(ch.canvas[1] * scale * 0.9)
    vrow = _row([(lab, im.crop(im.getbbox() or (0, 0, 1, 1))) for lab, im in imgs], cw, chh, f_lab)
    # linhas de proporção (altura em "cabeças")
    d = ImageDraw.Draw(vrow)
    head_px = ch.height * 0.36 * scale
    for i in range(0, 4):
        y = chh - i * head_px
        d.line([(0, y), (vrow.width, y)], fill=(120, 150, 200, 110), width=2)
    blocks["vistas"] = vrow

    # 2. expressões (rosto em 3/4)
    exps = list(EXPRESSIONS)
    cells = []
    for name in exps:
        p = {"turn": 0.35, **expression(name)}
        if name in ("laughing", "shock", "surprised", "crying"):
            p["mouth"] = "D" if name != "surprised" else "E"
        im = _render(ch, p, scale * 1.2)
        cells.append((name, _crop_head(ch, im, scale * 1.2)))
    hw = int(ch.height * 0.62 * scale * 1.2)
    blocks["expressoes_1"] = _row(cells[:7], hw, hw, f_lab)
    blocks["expressoes_2"] = _row(cells[7:], hw, hw, f_lab)

    # 3. bocas (visemas) de frente e de perfil
    mouth_cells = []
    for v in VISEMES:
        im = _render(ch, {"turn": 0.2, "mouth": v}, scale * 1.2)
        mouth_cells.append((v, _crop_head(ch, im, scale * 1.2)))
    blocks["bocas"] = _row(mouth_cells, int(hw * 0.8), hw, f_lab)

    # 4. poses de ação
    poses = ch_poses(ch)
    pc = []
    for lab, p in poses:
        im = _render(ch, p, scale)
        pc.append((lab, im.crop(im.getbbox() or (0, 0, 1, 1))))
    if pc:
        blocks["poses"] = _row(pc, cw, chh, f_lab)

    # monta a folha
    W = max(b.width for b in blocks.values()) + 80
    titles = {"vistas": "VISTAS E PROPORÇÕES (linhas = cabeças)", "expressoes_1": "EXPRESSÕES", "expressoes_2": "",
              "bocas": "BOCAS (VISEMAS RHUBARB A–H, X)", "poses": "POSES"}
    H = 140 + sum(b.height + (70 if titles[k] else 10) for k, b in blocks.items())
    sheet = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((40, 36), f"{ch.name.upper()} — FOLHA DE MODELO", fill=(40, 30, 28), font=f_title)
    y = 130
    offsets = {}
    for k, b in blocks.items():
        if titles[k]:
            d.text((40, y + 14), titles[k], fill=(150, 70, 40), font=f_lab)
            y += 60
        sheet.alpha_composite(b, (40, y))
        offsets[k] = (40, y)
        y += b.height + 10
    png = out_dir / f"{ch.id}_model_sheet.png"
    sheet.convert("RGB").save(png)

    # ORA com uma camada por bloco + fundo
    ora = out_dir / f"{ch.id}_model_sheet.ora"
    _write_ora(ora, sheet.size, [("fundo", Image.new("RGBA", sheet.size, BG), (0, 0))] +
               [(k, b, offsets[k]) for k, b in blocks.items()])
    return {"png": png, "ora": ora}


def ch_poses(ch: Character) -> list[tuple[str, dict]]:
    """Poses de referência — cada personagem pode definir `reference_poses`."""
    fn = getattr(ch, "reference_poses", None)
    return fn() if fn else []


def _write_ora(path: Path, size, layers) -> None:
    W, H = size
    stack = "".join(f'<layer name="{n}" src="data/{n}.png" x="{x}" y="{y}" opacity="1.0" visibility="visible"/>'
                    for n, _, (x, y) in reversed(layers))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr("stack.xml", f'<?xml version="1.0" encoding="UTF-8"?><image w="{W}" h="{H}"><stack>{stack}</stack></image>')
        flat = Image.new("RGBA", (W, H))
        for n, im, (x, y) in layers:
            b = io.BytesIO(); im.save(b, "PNG"); z.writestr(f"data/{n}.png", b.getvalue())
            flat.alpha_composite(im, (x, y))
        b = io.BytesIO(); flat.save(b, "PNG"); z.writestr("mergedimage.png", b.getvalue())
