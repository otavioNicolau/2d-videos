"""Objetos de cena desenhados como personagens (cel com contorno): a torta.

A torta tem canais próprios: `steam` (fase do vapor — anima mesmo parada), `eaten` (0 inteira … 1 só farelos).
Também pode ser desenhada na mão de um personagem (`draw_pie`).
"""
from __future__ import annotations

import math

from ..drawing.ink import Ink, ellipse_pts
from .base import Character

PIE_SCALE = 0.78     # mesma escala no toco e na mão (continuidade de tamanho)
PAL = {"crust": "#E3A95A", "crust_d": "#C0813A", "crust_l": "#F3CB86", "filling": "#B8324A", "filling_d": "#8C2238",
       "plate": "#F4F1EA", "plate_d": "#CFC9BD", "steam": (1, 1, 1, 0.75)}


def draw_pie(k: Ink, x: float, y: float, s: float = 1.0, eaten: float = 0.0, steam: float = -1.0, tilt: float = 0.0) -> None:
    """Torta com prato; (x, y) = base do prato."""
    c = k.c
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(tilt))
    c.scale(s, s)
    k.shape(ellipse_pts(0, -6, 92, 20, 0, 16), fill=PAL["plate"], shade=PAL["plate_d"], shade_offset=(0, -6), line=5)
    if eaten < 0.98:
        cut = 1.0 - eaten
        # corpo da torta (lateral) + topo treliçado
        w = 74 * (0.35 + 0.65 * cut)
        x0 = -74
        k.shape([(x0, -12), (x0 + 2 * w * 1.0, -12), (x0 + 2 * w * 1.0 + 4, -44), (x0 - 4, -44)], fill=PAL["crust"],
                shade=PAL["crust_d"], shade_offset=(8, 0), smooth=False, line=5)
        k.shape(ellipse_pts(x0 + w, -46, w + 4, 18, 0, 14), fill=PAL["crust_l"], line=5,
                clip_extra=lambda kk: _lattice(kk, x0 + w, -46, w))
        if eaten > 0.02:      # face mordida mostrando o recheio
            bx = x0 + 2 * w
            k.shape([(bx - 6, -12), (bx + 6, -20), (bx - 2, -30), (bx + 8, -40), (bx - 6, -48), (bx - 18, -40), (bx - 10, -26)],
                    fill=PAL["filling"], line=4)
    for i in range(int(6 * eaten)):          # farelos
        k.ellipse(-60 + i * 22, -14 + (i % 2) * 3, 5, 3, PAL["crust_d"], line=2)
    if steam >= 0 and eaten < 0.5:
        for j in range(3):
            ph = steam * 2 * math.pi + j * 2.1
            xs = -36 + j * 36
            pts = [(xs + 8 * math.sin(ph + u * 3.5), -70 - u * 70) for u in (0, 0.33, 0.66, 1.0)]
            k.stroke(pts, 9 * (1 - 0.1 * j), taper=(0.3, 0.6), color_=PAL["steam"])
    c.restore()


def _lattice(kk: Ink, cx, cy, w):
    kk.ellipse(cx, cy + 2, w * 0.92, 13, PAL["filling"], line=0)
    for i in range(-3, 4):
        x = cx + i * w * 0.27
        kk.stroke([(x - 8, cy - 18), (x + 8, cy + 18)], 7, taper=(0, 0), color_=PAL["crust_l"])
        kk.stroke([(x + 8, cy - 18), (x - 8, cy + 18)], 7, taper=(0, 0), color_=PAL["crust"])


class Torta(Character):
    def __init__(self) -> None:
        super().__init__(id="torta", name="Torta", canvas=(420, 330), anchor=(210, 300), height=120,
                         defaults={"turn": 0.0, "steam": 0.0, "eaten": 0.0, "hidden": 0.0})

    def draw(self, ink: Ink, P: dict) -> None:
        if P.get("hidden", 0) > 0.5:
            return
        draw_pie(ink, 0, 0, PIE_SCALE, P["eaten"], P["steam"])
