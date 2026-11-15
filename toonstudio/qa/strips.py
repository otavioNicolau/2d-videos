"""Pranchas de revisão visual: tira de quadros e "onion skin" sobre o caminho no palco.

Código funcionando não prova animação boa — estas pranchas são o que a revisão humana (e a do Claude) olha.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from ..characters.base import Character

BG = (250, 246, 236, 255)


def film_strip(ch: Character, drawings: list[dict], cells: list[int], out: Path, every: int = 1, cols: int = 12,
               scale: float = 0.45, label: bool = True) -> Path:
    frames = list(range(0, len(cells), every))
    imgs = {}
    for fi in frames:
        d = cells[fi]
        if d not in imgs:
            imgs[d] = Image.fromarray(ch.render_array(drawings[d - 1], scale=scale, jitter=0.0), "RGBA")
    w, h = next(iter(imgs.values())).size
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * w, rows * (h + 22)), BG)
    dr = ImageDraw.Draw(sheet)
    for i, fi in enumerate(frames):
        x, y = (i % cols) * w, (i // cols) * (h + 22)
        sheet.alpha_composite(imgs[cells[fi]], (x, y))
        dr.line([(x, y + int(h * ch.anchor[1] / ch.canvas[1])), (x + w, y + int(h * ch.anchor[1] / ch.canvas[1]))],
                fill=(180, 170, 160, 255))
        if label:
            dr.text((x + 6, y + h + 4), f"q{fi + 1} d{cells[fi]}", fill=(90, 70, 60, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)
    return out


def onion(ch: Character, drawings: list[dict], cells: list[int], stage: list[dict], out: Path, every: int = 2,
          scale: float = 0.4, world_w: int = 1920, world_h: int = 1080) -> Path:
    """Sobrepõe desenhos no lugar onde ficam no palco (espaçamento e arcos aparecem)."""
    W, H = int(world_w * scale), int(world_h * scale)
    sheet = Image.new("RGBA", (W, H), BG)
    frames = list(range(0, len(cells), every))
    for n, fi in enumerate(frames):
        im = Image.fromarray(ch.render_array(drawings[cells[fi] - 1], scale=scale, jitter=0.0), "RGBA")
        a = 0.25 + 0.75 * (n + 1) / len(frames)
        im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        sx, sy = stage[fi]["x"] * scale, stage[fi]["y"] * scale
        sheet.alpha_composite(im, (int(sx - ch.anchor[0] * scale), int(sy - ch.anchor[1] * scale)))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)
    return out
