"""Cenário "sertão" (clipes da turma): céu quente, mesas roxas ao longe, mandacarus, caatinga, chão de areia,
pedra grande (esconderijo). Pintado sem contorno (fundo), mas mais saturado e limpo que a floresta (estilo turminha).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import skia

from .painter import P, blob, canopy, grass_tufts, lin, paper, poly

WIDTH, HEIGHT = 4400, 1080
GROUND = 930
LANDMARKS = {"ground_y": GROUND, "rock": {"x": 2600, "top_y": 806}, "big_cactus": {"x": 1250}}
PAL = {"sky_top": "#5BB8F0", "sky_bot": "#FFE6A8", "sun": "#FFD23F", "mesa": "#B67BB8", "mesa2": "#9A69A8",
       "mesa_l": "#D3A0CF", "sand": "#F2C77A", "sand_d": "#E0A85B", "sand_l": "#F8DCA0", "cactus": "#5BA65A",
       "cactus_d": "#3F8443", "cactus_l": "#7CC46F", "shrub": "#8AA35A", "shrub_d": "#6B8545", "shrub_l": "#AFC377",
       "rock": "#C9967A", "rock_d": "#A87458", "rock_l": "#E2B79C", "trunk": "#8C6A4E"}


def _surface(w, h, scale):
    s = skia.Surface(int(w * scale), int(h * scale))
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.scale(scale, scale)
    return s, c


def mandacaru(c, x, base_y, h, rng, scale=1.0):
    """Cacto mandacaru: tronco com braços que sobem, gomos verticais e espinhos claros."""
    w = 46 * scale
    def stem(x0, y0, x1, y1, ww):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(min(x0, x1) - ww / 2, min(y0, y1), max(x0, x1) + ww / 2, max(y0, y1)), ww / 2, ww / 2),
                    P(PAL["cactus"], shader=lin((x0 - ww / 2, 0), (x0 + ww / 2, 0), [PAL["cactus_l"], PAL["cactus"], PAL["cactus_d"]])))
        for k in (-0.25, 0.0, 0.25):
            pa = P(PAL["cactus_d"], alpha=0.5)
            pa.setStyle(skia.Paint.kStroke_Style)
            pa.setStrokeWidth(2.5)
            c.drawLine(x0 + k * ww, min(y0, y1) + ww * 0.4, x0 + k * ww, max(y0, y1) - 4, pa)
    stem(x, base_y - h, x, base_y, w)
    for side, hy, ah in ((-1, 0.55, 0.32), (1, 0.42, 0.38)):
        ay = base_y - h * hy
        ax = x + side * w * 1.4
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(min(x, ax), ay - w * 0.3, max(x, ax), ay + w * 0.35), w * 0.3, w * 0.3),
                    P(PAL["cactus"]))
        stem(ax, ay - h * ah, ax, ay + w * 0.2, w * 0.8)
    for _ in range(int(h / 14)):
        sx = x + rng.uniform(-w / 2, w / 2)
        sy = rng.uniform(base_y - h, base_y - 10)
        c.drawCircle(sx, sy, 1.8, P("#F7F3DA", alpha=0.9))


def layer_sky(scale, rng):
    w = int(WIDTH * 0.12 + 2000)
    s, c = _surface(w, HEIGHT, scale)
    c.drawRect(skia.Rect(0, 0, w, HEIGHT), P("#000", shader=lin((0, 0), (0, 820), [PAL["sky_top"], PAL["sky_bot"]])))
    sx, sy = w * 0.78, 170
    for r, a in ((190, 0.18), (130, 0.3)):
        c.drawCircle(sx, sy, r, P(PAL["sun"], alpha=a, blur=30))
    c.drawCircle(sx, sy, 78, P(PAL["sun"]))
    for i in range(6):
        cx, cy = rng.uniform(0, w), rng.uniform(70, 330)
        for j in range(5):
            r = rng.uniform(36, 70)
            blob(c, [(cx + j * 46 + r * math.cos(a), cy - (j % 2) * 16 + r * 0.55 * math.sin(a)) for a in np.linspace(0, 6.28, 10, endpoint=False)],
                 "#FFFFFF", alpha=0.95)
    paper(c, w, HEIGHT, 0.03, 11)
    return s, w, 0.12


def layer_mesas(scale, rng):
    w = int(WIDTH * 0.3 + 2000)
    s, c = _surface(w, HEIGHT, scale)
    x = -100.0
    while x < w:
        mw, mh = rng.uniform(380, 700), rng.uniform(120, 220)
        top = 700 - mh
        pts = [(x, 760), (x + mw * 0.12, top + 20), (x + mw * 0.2, top), (x + mw * 0.75, top), (x + mw * 0.85, top + 24), (x + mw, 760)]
        c.drawPath(poly(pts), P(PAL["mesa"], shader=lin((0, top), (0, 760), [PAL["mesa_l"], PAL["mesa"], PAL["mesa2"]])))
        x += mw * rng.uniform(0.7, 1.1)
    c.drawRect(skia.Rect(0, 740, w, HEIGHT), P(PAL["sand_l"]))
    c.drawRect(skia.Rect(0, 600, w, 780), P("#000", shader=lin((0, 600), (0, 780), ["#FFE6A800", "#FFE6A866"])))
    return s, w, 0.3


def layer_caatinga(scale, rng):
    w = int(WIDTH * 0.6 + 2000)
    s, c = _surface(w, HEIGHT, scale)
    c.drawRect(skia.Rect(0, 770, w, HEIGHT), P(PAL["sand_l"]))
    x = 0.0
    while x < w:
        if rng.random() < 0.35:
            mandacaru(c, x, 820, rng.uniform(95, 140), rng, 0.5)
        else:
            canopy(c, x, 790, rng.uniform(70, 120), rng.uniform(45, 70), PAL["shrub_d"], PAL["shrub"], PAL["shrub_l"], rng, n=8)
        x += rng.uniform(160, 320)
    return s, w, 0.6


def layer_ground(scale, rng):
    w = WIDTH
    s, c = _surface(w, HEIGHT, scale)
    c.drawRect(skia.Rect(0, 820, w, HEIGHT), P("#000", shader=lin((0, 820), (0, HEIGHT), [PAL["sand_l"], PAL["sand"], PAL["sand_d"]])))
    pts = [(0, 850)] + [(x, 826 + 10 * math.sin(x / 140)) for x in np.linspace(0, w, 90)] + [(w, 850), (w, 880), (0, 880)]
    c.drawPath(poly(pts), P(PAL["sand_l"]))
    for _ in range(260):   # pedrinhas e marcas de areia
        x, y = rng.uniform(0, w), rng.uniform(850, 1075)
        c.drawOval(skia.Rect(x, y, x + rng.uniform(6, 16), y + rng.uniform(3, 7)), P(PAL["sand_d"], alpha=0.7))
    grass_tufts(c, 0, w, 840, 880, [PAL["shrub_d"], PAL["shrub"]], rng, n=140, h=(10, 22))
    mandacaru(c, LANDMARKS["big_cactus"]["x"], 905, 250, rng, 0.85)     # cenário na escala das crianças
    for x in (400, 3600):
        mandacaru(c, x, 900, 185, rng, 0.7)
    rx = LANDMARKS["rock"]["x"]
    for x0, wd in ((rx, 210), (LANDMARKS["big_cactus"]["x"], 90)):
        c.drawOval(skia.Rect(x0 - wd, 912, x0 + wd, 944), P("#8A5A2B", alpha=0.25, blur=8))
    paper(c, w, HEIGHT, 0.04, 12)
    return s, w, 1.0


def layer_rock(scale, rng):
    """Pedra grande numa camada própria, NA FRENTE dos personagens: o calango pode se esconder atrás dela."""
    s, c = _surface(WIDTH, HEIGHT, scale)
    rx = LANDMARKS["rock"]["x"]
    blob(c, [(rx - 150, 935), (rx - 132, 862), (rx - 70, 818), (rx + 8, 806), (rx + 92, 826), (rx + 145, 878), (rx + 158, 935)],
         PAL["rock"], shader=lin((rx - 150, 760), (rx + 150, 930), [PAL["rock_l"], PAL["rock"], PAL["rock_d"]]))
    blob(c, [(rx - 46, 836), (rx + 14, 824), (rx + 56, 838), (rx + 8, 850)], PAL["rock_l"], alpha=0.8)
    return s, WIDTH, 1.0


def layer_front(scale, rng):
    w = int(WIDTH * 1.2 + 400)
    s, c = _surface(w, HEIGHT, scale)
    x = 0.0
    while x < w:
        if rng.random() < 0.6:
            canopy(c, x, 1080 + rng.uniform(0, 30), rng.uniform(120, 200), rng.uniform(70, 110), PAL["shrub_d"], PAL["shrub"],
                   PAL["shrub_l"], rng, n=7, dapple=False)
        x += rng.uniform(600, 1000)
    return s, w, 1.2


LAYERS = [("BG_ceu", layer_sky, -50), ("BG_mesas", layer_mesas, -40), ("MG_caatinga", layer_caatinga, -30),
          ("MG_chao", layer_ground, -20), ("FG_pedra", layer_rock, 40), ("FG_moita", layer_front, 60)]


def build(out_dir: Path, scale: float = 1.5, seed: int = 21) -> dict:
    import json
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"id": "sertao", "name": "Sertão", "width": WIDTH, "height": HEIGHT, "scale": scale, "landmarks": LANDMARKS,
            "layers": []}
    for name, fn, z in LAYERS:
        rng = np.random.default_rng(seed + abs(z))
        surf, w, parallax = fn(scale, rng)
        surf.makeImageSnapshot().save(str(out_dir / f"{name}.png"), skia.kPNG)
        meta["layers"].append({"name": name, "file": f"{name}.png", "parallax": parallax, "z": z, "width": w, "height": HEIGHT})
    (out_dir / "background.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta
