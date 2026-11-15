"""Cenário "clareira da floresta": camadas independentes para parallax.

Coordenadas em unidades de palco (1080 de altura). O chão onde os personagens pisam fica em y≈GROUND.
Marcos de cena (usados pelo roteiro): toco com a torta, arbusto do esconderijo, árvore grande com galho.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import skia

from .painter import P, blob, canopy, grass_tufts, lin, paper, poly, radial, trunk

WIDTH, HEIGHT = 5200, 1080
GROUND = 930
LANDMARKS = {
    "ground_y": GROUND,
    "stump": {"x": 1500, "top_y": 820},
    "bush": {"x": 2350, "top_y": 700},
    "big_tree": {"x": 4380, "trunk_left": 4290, "trunk_right": 4470, "branch_y": 470, "branch_x0": 4000, "branch_x1": 4440},
}

PAL = {
    "sky_top": "#8EC7EA", "sky_bot": "#F4EBC4", "cloud": "#FFFDF4", "cloud_shade": "#E3E6EC",
    "far": "#9DBFAE", "far2": "#86AE9C", "far_light": "#B8D3C0",
    "mid_base": "#3F7A4A", "mid_mid": "#559457", "mid_light": "#7DB46A", "trunk_mid": "#6E5340", "trunk_mid_d": "#4E3A2E",
    "trunk_mid_l": "#8C6D52",
    "ground": "#7BAE52", "ground_d": "#5E9442", "ground_l": "#9CC468", "path": "#D9B98A", "path_d": "#BF9A68",
    "grass": ["#4E8A3C", "#62A048", "#3E7633", "#7DB458"], "rock": "#A49B90", "rock_d": "#7E766C",
    "bark": "#7A5838", "bark_d": "#523A26", "bark_l": "#9C7A55", "stump_top": "#D8B983", "ring": "#B48E5C",
    "fg": "#2F5E36", "fg_mid": "#3F7643", "fg_light": "#5A9452", "flower": ["#F6F1E7", "#F7D14B", "#E87A8A"],
}


def _surface(w, h, scale):
    s = skia.Surface(int(w * scale), int(h * scale))
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.scale(scale, scale)
    return s, c


def layer_sky(scale, rng):
    w = int(WIDTH * 0.45 + 1920)        # parallax 0,15: cobre o percurso da câmera
    s, c = _surface(w, HEIGHT, scale)
    c.drawRect(skia.Rect(0, 0, w, HEIGHT), P("#000", shader=lin((0, 0), (0, HEIGHT * 0.8), [PAL["sky_top"], PAL["sky_bot"]])))
    c.drawCircle(w * 0.18, 150, 260, P("#FFF7D6", alpha=0.35, blur=80))
    for i in range(9):
        cx, cy = rng.uniform(0, w), rng.uniform(80, 360)
        for j in range(6):
            r = rng.uniform(40, 90)
            blob(c, [(cx + j * 55 + r * math.cos(a), cy - (j % 3) * 18 + r * 0.6 * math.sin(a)) for a in np.linspace(0, 6.28, 10, endpoint=False)],
                 PAL["cloud_shade"] if j % 2 else PAL["cloud"], alpha=0.85, blur=3)
    paper(c, w, HEIGHT, 0.05, 1)
    return s, w, 0.15


def layer_far(scale, rng):
    w = int(WIDTH * 0.35 + 1920 + 200)
    s, c = _surface(w, HEIGHT, scale)
    for k, (col, base, amp) in enumerate(((PAL["far_light"], 640, 70), (PAL["far"], 700, 90), (PAL["far2"], 760, 60))):
        pts = [(0, HEIGHT)]
        for x in np.linspace(0, w, 60):
            y = base - amp * (0.5 + 0.5 * math.sin(x / (260 + 90 * k) + k)) - 25 * math.sin(x / 70 + k * 2)
            pts.append((x, y))
        pts.append((w, HEIGHT))
        c.drawPath(poly(pts), P(col))
        # linha de copas distantes
        for x in np.arange(0, w, 38):
            y = base - amp * (0.5 + 0.5 * math.sin(x / (260 + 90 * k) + k)) - 25 * math.sin(x / 70 + k * 2)
            c.drawCircle(x, y + 6, rng.uniform(16, 30), P(col))
    paper(c, w, HEIGHT, 0.05, 2)
    return s, w, 0.35


def layer_mid(scale, rng):
    w = int(WIDTH * 0.65 + 1920 + 200)
    s, c = _surface(w, HEIGHT, scale)
    c.drawRect(skia.Rect(0, 760, w, HEIGHT), P(PAL["mid_base"], shader=lin((0, 760), (0, 900), ["#4E8A55", "#3F7A4A"])))
    x = 60.0
    while x < w:
        h = rng.uniform(330, 520)
        tw = rng.uniform(30, 52)
        top = 820 - h
        trunk(c, x, top + 120, 860, tw * 0.7, tw, PAL["trunk_mid"], PAL["trunk_mid_d"], PAL["trunk_mid_l"], rng, roots=False)
        canopy(c, x + rng.uniform(-20, 20), top + 80, rng.uniform(120, 190), rng.uniform(110, 160),
               PAL["mid_base"], PAL["mid_mid"], PAL["mid_light"], rng)
        x += rng.uniform(170, 290)
    # névoa clara na base (profundidade)
    c.drawRect(skia.Rect(0, 640, w, 900), P("#000", shader=lin((0, 640), (0, 900), ["#DDEBD800", "#DDEBD866"])))
    paper(c, w, HEIGHT, 0.06, 3)
    return s, w, 0.6


def layer_ground(scale, rng):
    w = WIDTH
    s, c = _surface(w, HEIGHT, scale)
    c.drawRect(skia.Rect(0, 820, w, HEIGHT), P("#000", shader=lin((0, 820), (0, HEIGHT), [PAL["ground_l"], PAL["ground"], PAL["ground_d"]])))
    # borda irregular do gramado contra a floresta
    pts = [(0, 860)] + [(x, 832 + 12 * math.sin(x / 90) + rng.uniform(-6, 6)) for x in np.linspace(0, w, 140)] + [(w, 860)]
    c.drawPath(poly(pts + [(w, 900), (0, 900)]), P(PAL["ground_l"]))
    # trilha de terra
    path = skia.Path()
    path.moveTo(0, 905)
    for x in np.linspace(0, w, 40):
        path.lineTo(x, 900 + 18 * math.sin(x / 400))
    for x in np.linspace(w, 0, 40):
        path.lineTo(x, 985 + 22 * math.sin(x / 330 + 1))
    path.close()
    c.drawPath(path, P(PAL["path"], shader=lin((0, 900), (0, 990), [PAL["path"], PAL["path_d"]])))
    for _ in range(140):     # pedrinhas na trilha
        x, y = rng.uniform(0, w), rng.uniform(910, 980)
        c.drawOval(skia.Rect(x, y, x + rng.uniform(5, 14), y + rng.uniform(3, 7)), P(PAL["path_d"], alpha=0.8))
    grass_tufts(c, 0, w, 840, 900, PAL["grass"], rng, n=900, h=(10, 24))
    grass_tufts(c, 0, w, 990, 1075, PAL["grass"], rng, n=900, h=(16, 34))
    for _ in range(120):     # flores
        x, y = rng.uniform(0, w), rng.uniform(845, 1070)
        if 895 < y < 995:
            continue
        col = PAL["flower"][rng.integers(3)]
        for a in range(5):
            c.drawCircle(x + 4 * math.cos(a * 1.256), y + 4 * math.sin(a * 1.256), 3.2, P(col))
        c.drawCircle(x, y, 2.4, P("#F2B33D"))
    # pedras
    for x in (900, 2950, 3450):
        blob(c, [(x - 60, 905), (x - 40, 870), (x + 10, 858), (x + 55, 878), (x + 65, 905)], PAL["rock"],
             shader=lin((x - 60, 860), (x + 60, 905), [PAL["rock"], PAL["rock_d"]]))
    # toco (onde fica a torta)
    st = LANDMARKS["stump"]
    sx, top = st["x"], st["top_y"]
    trunk(c, sx, top + 10, 915, 150, 170, PAL["bark"], PAL["bark_d"], PAL["bark_l"], rng)
    c.drawOval(skia.Rect(sx - 76, top - 12, sx + 76, top + 26), P(PAL["stump_top"]))
    for r in (54, 36, 18):
        pa = P(PAL["ring"], alpha=0.8)
        pa.setStyle(skia.Paint.kStroke_Style)
        pa.setStrokeWidth(2.5)
        c.drawOval(skia.Rect(sx - r * 1.3, top + 7 - r * 0.32, sx + r * 1.3, top + 7 + r * 0.32), pa)
    # árvore grande (onde o Caramelo bate) com galho
    bt = LANDMARKS["big_tree"]
    tx = bt["x"]
    trunk(c, tx, -40, 925, 150, 190, PAL["bark"], PAL["bark_d"], PAL["bark_l"], rng)
    by = bt["branch_y"]
    x0 = bt["branch_x0"]
    blob(c, [(tx - 30, by - 44), (tx - 160, by - 8), (x0 + 120, by + 2), (x0, by + 4), (x0 - 8, by + 18), (x0 + 120, by + 26),
             (tx - 160, by + 34), (tx - 30, by + 60)], PAL["bark"],
         shader=lin((0, by - 30), (0, by + 50), [PAL["bark_l"], PAL["bark"], PAL["bark_d"]]))
    blob(c, [(x0 + 150, by + 2), (x0 + 110, by - 50), (x0 + 128, by - 46), (x0 + 175, by + 2)], PAL["bark"])   # galhinho
    canopy(c, x0 + 108, by - 70, 70, 46, PAL["mid_base"], PAL["mid_mid"], PAL["mid_light"], rng, n=7)
    canopy(c, x0 - 20, by - 6, 46, 32, PAL["mid_base"], PAL["mid_mid"], PAL["mid_light"], rng, n=5)
    canopy(c, tx, 60, 420, 260, PAL["mid_base"], PAL["mid_mid"], PAL["mid_light"], rng, n=30)
    # sombras de contato no chão
    for x, wd in ((sx, 120), (tx, 150)):
        c.drawOval(skia.Rect(x - wd, 905, x + wd, 935), P("#2E4A22", alpha=0.25, blur=8))
    paper(c, w, HEIGHT, 0.07, 4)
    return s, w, 1.0


def layer_bush(scale, rng):
    """Arbusto do esconderijo — no mesmo plano dos personagens, mas na frente deles."""
    w = WIDTH
    s, c = _surface(w, HEIGHT, scale)
    b = LANDMARKS["bush"]
    for (dx, dy, rx, ry, col) in ((-140, 820, 150, 110, PAL["fg"]), (120, 830, 160, 120, PAL["fg"]), (0, 780, 200, 140, PAL["fg_mid"])):
        canopy(c, b["x"] + dx, dy, rx, ry, col, PAL["fg_mid"], PAL["fg_light"], rng, n=12)
    c.drawOval(skia.Rect(b["x"] - 280, 905, b["x"] + 280, 945), P("#24401F", alpha=0.35, blur=10))
    paper(c, w, HEIGHT, 0.06, 5)
    return s, w, 1.0


def layer_front(scale, rng):
    """Moldura de primeiro plano (passa mais rápido que o chão)."""
    w = int(WIDTH * 1.25 + 400)
    s, c = _surface(w, HEIGHT, scale)
    x = 0.0
    while x < w:
        if rng.random() < 0.55:
            canopy(c, x, 1080 + rng.uniform(-10, 40), rng.uniform(140, 230), rng.uniform(90, 140), PAL["fg"], PAL["fg_mid"],
                   PAL["fg_light"], rng, n=8, dapple=False)
        x += rng.uniform(500, 900)
    grass_tufts(c, 0, w, 1060, 1082, ["#2C5530", "#356B38"], rng, n=500, h=(30, 60))
    return s, w, 1.25


LAYERS = [("BG_ceu", layer_sky, -50), ("BG_morros", layer_far, -40), ("MG_floresta", layer_mid, -30),
          ("MG_chao", layer_ground, -20), ("FG_arbusto", layer_bush, 50), ("FG_moldura", layer_front, 60)]


def build(out_dir: Path, scale: float = 1.5, seed: int = 7) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"id": "floresta_clareira", "name": "Clareira da floresta", "width": WIDTH, "height": HEIGHT, "scale": scale,
            "landmarks": LANDMARKS, "layers": []}
    for name, fn, z in LAYERS:
        rng = np.random.default_rng(seed + abs(z))
        surf, w, parallax = fn(scale, rng)
        path = out_dir / f"{name}.png"
        surf.makeImageSnapshot().save(str(path), skia.kPNG)
        meta["layers"].append({"name": name, "file": path.name, "parallax": parallax, "z": z, "width": w, "height": HEIGHT})
    (out_dir / "background.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta
