"""Cenários no estilo oficial (BIBLIA_VISUAL.md): vetor CHAPADO, contorno = cor da peça escurecida, linha uniforme,
detalhes em traços soltos, céu e nuvens sem contorno, sem gradiente/textura/desfoque.

Ids: plano_parque (jardim com lago, árvores, casinha).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import skia

from ..characters.flat_muri import LINE, _rgba, dark
from ..drawing.ink import Brush, Ink, ellipse_pts

W_SCENE, H = 4400, 1080
GROUND_Y = 930
PAL = {"ceu": "#87B8F6", "nuvem": "#FFFFFF", "morro": "#8ED07A", "morro2": "#6DBF63", "grama": "#75C66B",
       "arbusto": "#2FA34A", "folha": "#6DAD47", "tronco": "#534946", "agua": "#225CA8", "pedra": "#7F7D7B",
       "madeira": "#9A5A2E", "parede": "#FFE07A", "telhado": "#E9545D", "porta": "#7D4724", "janela": "#87B8F6",
       "flor": ["#FFFFFF", "#FEAEDE", "#FFE066", "#B865E6"], "miolo": "#FFC93C"}


def _surf(w, h, scale):
    s = skia.Surface(int(w * scale), int(h * scale))
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.scale(scale, scale)
    return s, c


class Flat:
    """Atalhos de desenho chapado com contorno da bíblia."""

    def __init__(self, c: skia.Canvas):
        self.k = Ink(c, Brush(LINE, 0.0, (0, 0, 0, 1), 0.0))

    def shape(self, pts, fill, line=True, smooth=True, w=LINE):
        br = Brush(w, 0.0, _rgba(dark(fill)), 0.0)
        if not smooth:
            # polígono de poucos cantos: amostra as arestas (cantos levemente arredondados, contorno sem defeito)
            dense = []
            n = len(pts)
            for i in range(n):
                a, b = np.array(pts[i], float), np.array(pts[(i + 1) % n], float)
                steps = max(2, int(np.linalg.norm(b - a) / 12))
                dense += [tuple(a + (b - a) * u) for u in np.linspace(0, 1, steps, endpoint=False)]
            return self.k.shape(dense, fill=_rgba(fill), brush=br, dense=True, line=w if line else 0)
        return self.k.shape(pts, fill=_rgba(fill), brush=br, smooth=smooth, line=w if line else 0)

    def line(self, pts, col, w=LINE):
        self.k.stroke(pts, w, taper=(0.0, 0.0), color_=_rgba(col))

    def oval(self, x, y, rx, ry, fill, line=True, a=0.0):
        return self.shape(ellipse_pts(x, y, rx, ry, a, 18), fill, line)

    # ---------------------------------------------------------- elementos
    def cloud(self, x, y, s=1.0):
        p = skia.Path()
        for dx, dy, r in ((-58, 10, 40), (-18, -14, 52), (30, -6, 46), (64, 12, 34), (2, 18, 42)):
            p.addCircle(x + dx * s, y + dy * s, r * s)
        p.setFillType(skia.PathFillType.kWinding)
        self.k.c.drawPath(p, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(PAL["nuvem"]))))

    def leaf(self, x, y, size, ang, col):
        """Folha em gota com rabisco interno (traço solto)."""
        tip = (x + math.cos(ang) * size, y + math.sin(ang) * size)
        side = (math.cos(ang + math.pi / 2) * size * 0.42, math.sin(ang + math.pi / 2) * size * 0.42)
        pts = [(x, y), ((x + tip[0]) / 2 + side[0], (y + tip[1]) / 2 + side[1]), tip, ((x + tip[0]) / 2 - side[0], (y + tip[1]) / 2 - side[1])]
        self.shape(pts, col)
        mid = ((x + tip[0]) / 2, (y + tip[1]) / 2)
        loop = [(x + (mid[0] - x) * 0.4, y + (mid[1] - y) * 0.4),
                (mid[0] + side[0] * 0.45, mid[1] + side[1] * 0.45), (tip[0] - (tip[0] - mid[0]) * 0.3, tip[1] - (tip[1] - mid[1]) * 0.3),
                (mid[0] - side[0] * 0.3, mid[1] - side[1] * 0.3)]
        self.line(loop, dark(col), w=LINE * 0.7)

    def tree(self, x, base, h, rng, col=None):
        col = col or PAL["folha"]
        top = base - h
        self.line([(x, base), (x - 4, base - h * 0.5), (x + 2, top + h * 0.2)], PAL["tronco"], w=LINE * 3.2)
        for side in (-1, 1):                        # galhos em traço
            by = base - h * rng.uniform(0.45, 0.65)
            bx = x + side * h * 0.28
            self.line([(x, by + 30), (bx, by - h * 0.12)], PAL["tronco"], w=LINE * 2)
            self.leaf(bx, by - h * 0.12, h * 0.26, -math.pi / 2 + side * 0.6, col)
        for j, ang in enumerate((-2.0, -1.57, -1.1)):
            self.leaf(x + (j - 1) * 30, top + h * 0.28, h * 0.32, ang, col)

    def bush(self, x, y, s=1.0):
        for ang in (-2.4, -1.9, -1.4, -0.9, -0.5, -2.8):
            self.leaf(x + math.cos(ang) * 10 * s, y, 62 * s, ang, PAL["arbusto"])

    def stone(self, x, y, w, h):
        pts = [(x - w, y), (x - w * 0.9, y - h * 0.7), (x - w * 0.3, y - h), (x + w * 0.5, y - h * 0.9), (x + w, y - h * 0.3), (x + w, y)]
        self.shape(pts, PAL["pedra"])
        for dx, dy in ((-0.4, 0.5), (0.1, 0.65), (0.45, 0.4), (-0.1, 0.3)):
            self.k.dot(x + dx * w, y - dy * h, 4.5, _rgba(dark(PAL["pedra"])))

    def flower(self, x, y, col):
        self.line([(x, y), (x, y + 26)], "#4E9E46", w=LINE * 0.8)
        for j in range(5):
            a = j * 2 * math.pi / 5
            self.oval(x + math.cos(a) * 9, y + math.sin(a) * 9, 7, 7, col)
        self.oval(x, y, 6, 6, PAL["miolo"], line=False)

    def grass_ticks(self, x, y):
        for dx in (-5, 3):
            self.line([(x + dx, y), (x + dx + 1, y - 13)], dark(PAL["grama"]), w=LINE * 0.7)

    def house(self, x, base, w=360, h=300):
        """Casinha: bloco arredondado + telhado + janelas de moldura colorida + porta."""
        self.shape([(x - w / 2, base), (x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2, base)], PAL["parede"], smooth=False)
        self.shape([(x - w / 2 - 30, base - h + 6), (x, base - h - 150), (x + w / 2 + 30, base - h + 6)], PAL["telhado"], smooth=False)
        for wx in (x - w * 0.27, x + w * 0.27):
            self.shape([(wx - 44, base - h + 70), (wx + 44, base - h + 70), (wx + 44, base - h + 150), (wx - 44, base - h + 150)], PAL["janela"], smooth=False)
            self.line([(wx, base - h + 70), (wx, base - h + 150)], dark(PAL["janela"]))
            self.line([(wx - 44, base - h + 110), (wx + 44, base - h + 110)], dark(PAL["janela"]))
        # porta: base reta no chão, laterais retas e ARCO em cima (desenho explícito; a suavização arredondava a base)
        arco = [(x + 40 * np.cos(a), base - 110 - 40 * np.sin(a)) for a in np.linspace(np.pi, 0, 24)]
        self.shape([(x - 40, base)] + arco + [(x + 40, base)], PAL["porta"], smooth=False)
        self.k.dot(x + 22, base - 64, 6, _rgba("#FFE066"))


def layer_ceu(scale, rng):
    w = int(W_SCENE * 0.15 + 2000)
    s, c = _surf(w, H, scale)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba(PAL["ceu"]))))
    F = Flat(c)
    for i in range(int(w / 380)):
        F.cloud(rng.uniform(0, w), rng.uniform(90, 300), rng.uniform(0.9, 1.3))
    return s, w, 0.15


def layer_morros(scale, rng):
    w = int(W_SCENE * 0.4 + 2100)
    s, c = _surf(w, H, scale)
    F = Flat(c)
    for col, base, amp, per in ((PAL["morro"], 760, 170, 700), (PAL["morro2"], 820, 110, 520)):
        pts = [(-60, H + 20)] + [(x, base - amp * (0.5 + 0.5 * math.sin(x / per * math.pi + rng.uniform(0, 0.1))))
                                 for x in np.linspace(-60, w + 60, 90)] + [(w + 60, H + 20)]
        F.shape(pts, col, smooth=False)
    x = 150.0
    while x < w:
        F.tree(x, 790, rng.uniform(220, 300), rng, col="#5E9E3E")
        x += rng.uniform(380, 640)
    return s, w, 0.4


def layer_chao(scale, rng):
    s, c = _surf(W_SCENE, H, scale)
    F = Flat(c)
    F.shape([(-20, 840), (W_SCENE + 20, 840), (W_SCENE + 20, H + 20), (-20, H + 20)], PAL["grama"], smooth=False)
    # lago
    F.shape([(2700, 880), (2860, 850), (3180, 846), (3420, 866), (3480, 900), (3300, 930), (2900, 932), (2720, 912)], PAL["agua"])
    for xx in (2880, 3060, 3240):
        F.line([(xx, 888), (xx + 40, 888)], "#5A8FD6", w=LINE * 0.8)
    F.house(1700, 860)
    for x in (500, 1050, 2250, 3800, 4250):
        F.tree(x, 870, rng.uniform(330, 420), rng)
    for x in (820, 1350, 2050, 2600, 3600, 4050):
        F.bush(x, 880, rng.uniform(0.8, 1.1))
    for x, w_, h_ in ((300, 70, 60), (1250, 56, 46), (2620, 80, 64), (3550, 60, 50)):
        F.stone(x, 900, w_, h_)
    for _ in range(180):
        F.grass_ticks(rng.uniform(0, W_SCENE), rng.uniform(950, 1070))
    for _ in range(90):
        y = rng.uniform(960, 1060)
        F.flower(rng.uniform(0, W_SCENE), y, PAL["flor"][int(rng.integers(len(PAL["flor"])))])
    return s, W_SCENE, 1.0


LAYERS = [("BG_ceu", layer_ceu, -50), ("BG_morros", layer_morros, -40), ("MG_chao", layer_chao, -20)]


def build(bg_id: str, out_dir: Path, scale: float = 1.5, seed: int = 9) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"id": bg_id, "name": "Plano — parque", "width": W_SCENE, "height": H, "scale": scale,
            "landmarks": {"ground_y": GROUND_Y}, "layers": [], "estilo": "BIBLIA_VISUAL.md"}
    for name, fn, z in LAYERS:
        rng = np.random.default_rng(seed + abs(z))
        surf, w, par = fn(scale, rng)
        surf.makeImageSnapshot().save(str(out_dir / f"{name}.png"), skia.kPNG)
        meta["layers"].append({"name": name, "file": f"{name}.png", "parallax": par, "z": z, "width": w, "height": H})
    (out_dir / "background.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta
