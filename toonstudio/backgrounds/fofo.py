"""Cenários "fofos" do canal (pedido do usuário: bem infantis e coloridos — natureza, cidade…).

Mesmo acabamento da turma: formas arredondadas, cores saturadas, volume com gradiente suave, nada de textura
realista. Escala pensada para as crianças (≈430 unidades de altura): árvores 380–520, casas 500–800.
Camadas: céu (fixo-lento), fundo, meio, chão, frente (parallax).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import skia

from .painter import P, lin, poly

W_SCENE, H = 4400, 1080
GROUND = 935


def _surf(w, h, scale):
    s = skia.Surface(int(w * scale), int(h * scale))
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.scale(scale, scale)
    return s, c


def soft(c, path: skia.Path, col: str, light: str, dark: str, box):
    """Preenchimento com volume suave (luz no alto-esquerda), como os personagens."""
    x0, y0, x1, y1 = box
    sh = skia.GradientShader.MakeRadial(skia.Point(x0 + (x1 - x0) * 0.35, y0 + (y1 - y0) * 0.3), max(x1 - x0, y1 - y0),
                                        [_c(light), _c(col), _c(dark)], [0.0, 0.55, 1.0])
    c.drawPath(path, skia.Paint(AntiAlias=True, Shader=sh))


def _c(h):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _mix(h, k, to=(255, 255, 255)):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#{:02X}{:02X}{:02X}".format(*(int(v + (t - v) * k) for v, t in zip((r, g, b), to)))


def light(h):
    return _mix(h, 0.3)


def dark(h):
    return _mix(h, 0.22, (0, 0, 0))


def circle_path(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def cloud(c, x, y, s=1.0):
    p = skia.Path()
    for dx, dy, r in ((-60, 8, 42), (-20, -16, 54), (30, -8, 48), (66, 10, 36), (0, 18, 44)):
        p.addCircle(x + dx * s, y + dy * s, r * s)
    p.setFillType(skia.PathFillType.kWinding)
    c.drawPath(p, P("#FFFFFF"))
    c.drawCircle(x - 34 * s, y - 20 * s, 14 * s, P("#FFFFFF", alpha=0.6))


def sun(c, x, y, r, t=0.0):
    for k in range(12):
        a = k * math.pi / 6 + t
        c.drawPath(poly([(x + math.cos(a - 0.12) * r * 1.15, y + math.sin(a - 0.12) * r * 1.15),
                         (x + math.cos(a) * r * 1.65, y + math.sin(a) * r * 1.65),
                         (x + math.cos(a + 0.12) * r * 1.15, y + math.sin(a + 0.12) * r * 1.15)]), P("#FFC93C"))
    soft(c, circle_path(x, y, r), "#FFD84D", "#FFF3A6", "#F7B92B", (x - r, y - r, x + r, y + r))
    # carinha do sol (olhos fechados felizes + bochechas)
    pe = skia.Paint(AntiAlias=True, Color=_c("#7A4A1A"), Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.09,
                    StrokeCap=skia.Paint.kRound_Cap)
    for sx in (-1, 1):
        path = skia.Path()
        path.moveTo(x + sx * r * 0.45 - r * 0.16, y - r * 0.05)
        path.quadTo(x + sx * r * 0.45, y - r * 0.28, x + sx * r * 0.45 + r * 0.16, y - r * 0.05)
        c.drawPath(path, pe)
        c.drawCircle(x + sx * r * 0.58, y + r * 0.22, r * 0.14, P("#FF9A7A", alpha=0.7))
    sm = skia.Path()
    sm.moveTo(x - r * 0.25, y + r * 0.2)
    sm.quadTo(x, y + r * 0.48, x + r * 0.25, y + r * 0.2)
    c.drawPath(sm, pe)


def lollipop_tree(c, x, base, h, col, rng):
    trunk = skia.Path()
    trunk.addRRect(skia.RRect.MakeRectXY(skia.Rect(x - 16, base - h * 0.55, x + 16, base), 14, 14))
    soft(c, trunk, "#B97A4A", "#D9A070", "#8E5A34", (x - 16, base - h * 0.55, x + 16, base))
    r = h * 0.3
    cy = base - h * 0.62
    blob = skia.Path()
    for a in np.linspace(0, 2 * math.pi, 7, endpoint=False):
        blob.addCircle(x + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.45, r * 0.62)
    blob.addCircle(x, cy, r * 0.8)
    blob.setFillType(skia.PathFillType.kWinding)
    soft(c, blob, col, light(col), dark(col), (x - r * 1.2, cy - r * 1.1, x + r * 1.2, cy + r * 1.1))
    for _ in range(4):        # frutinhas
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.2, 0.75)
        c.drawCircle(x + math.cos(a) * r * d, cy + math.sin(a) * r * d * 0.8, 9, P("#FF5A6E"))


def flower(c, x, y, s, col, center="#FFD23F"):
    for k in range(5):
        a = k * 2 * math.pi / 5
        c.drawCircle(x + math.cos(a) * 9 * s, y + math.sin(a) * 9 * s, 7.5 * s, P(col))
    c.drawCircle(x, y, 6 * s, P(center))


def hills(c, w, base, amp, col, phase, step=520):
    pts = [(0, H + 10)]
    for x in np.linspace(-50, w + 50, 120):
        pts.append((x, base - amp * (0.55 + 0.45 * math.sin(x / step * math.pi + phase))))
    pts.append((w, H + 10))
    path = poly(pts)
    soft(c, path, col, light(col), dark(col), (0, base - amp, w, H))


def ground(c, w, top, col, path_col=None):
    gp = poly([(0, top), (w, top), (w, H + 10), (0, H + 10)])
    c.drawPath(gp, P(col, shader=lin((0, top), (0, H), [light(col), col])))
    if path_col:
        p = skia.Path()
        p.moveTo(0, top + 40)
        for x in np.linspace(0, w, 40):
            p.lineTo(x, top + 38 + 10 * math.sin(x / 300))
        for x in np.linspace(w, 0, 40):
            p.lineTo(x, top + 96 + 10 * math.sin(x / 260 + 1))
        p.close()
        c.drawPath(p, P(path_col, shader=lin((0, top + 38), (0, top + 100), [light(path_col), path_col])))


def sky(scale, top: str, bottom: str, w: int, seed: int, sun_x: float | None = 0.8):
    s, c = _surf(w, H, scale)
    c.drawRect(skia.Rect(0, 0, w, H), P("#000", shader=lin((0, 0), (0, 800), [_hex(top), _hex(bottom)])))
    rng = np.random.default_rng(seed)
    if sun_x is not None:
        sun(c, w * sun_x, 170, 78)
    for i in range(int(w / 420)):
        cloud(c, rng.uniform(0, w), rng.uniform(90, 330), rng.uniform(0.8, 1.3))
    return s


def _hex(h):
    return h


# ---------------------------------------------------------------- cenários
def parque(scale, rng):
    """Natureza: morros arredondados, árvores pirulito, flores, trilha amarela."""
    out = {}
    out["BG_ceu"] = (sky(scale, "#6CC7F5", "#C9F1FF", int(W_SCENE * 0.15 + 2000), 3), 0.15, -50)
    s, c = _surf(int(W_SCENE * 0.35 + 2100), H, scale)
    hills(c, s.width() / scale, 760, 190, "#8AD86B", 0.4, 640)
    hills(c, s.width() / scale, 820, 130, "#5EC25A", 2.1, 480)
    out["BG_morros"] = (s, 0.35, -40)
    w = int(W_SCENE * 0.65 + 2100)
    s, c = _surf(w, H, scale)
    x = 80.0
    cols = ["#43B95A", "#7DD35F", "#2FA36B", "#9BDB4D"]
    while x < w:
        lollipop_tree(c, x, 850, rng.uniform(300, 420), cols[int(rng.integers(len(cols)))], rng)
        x += rng.uniform(260, 420)
    out["MG_arvores"] = (s, 0.62, -30)
    s, c = _surf(W_SCENE, H, scale)
    ground(c, W_SCENE, 860, "#7ED957", "#FFD66B")
    for _ in range(260):
        y = rng.uniform(880, 1075)
        if 895 < y < 965:
            continue
        flower(c, rng.uniform(0, W_SCENE), y, rng.uniform(0.8, 1.3), ["#FF6FA8", "#FFFFFF", "#B06CF0", "#FF9A3C"][int(rng.integers(4))])
    for x in (700, 1900, 3300):       # arbustos redondos
        b = skia.Path()
        for dx, r in ((-50, 55), (0, 72), (55, 58)):
            b.addCircle(x + dx, 870, r)
        b.setFillType(skia.PathFillType.kWinding)
        soft(c, b, "#3FAE55", "#6CD27A", "#2B8A40", (x - 110, 800, x + 110, 940))
    out["MG_chao"] = (s, 1.0, -20)
    return out


def cidade(scale, rng):
    """Cidade de brinquedo: prédios arredondados em cores doces, janelas redondas, rua e calçada."""
    out = {}
    out["BG_ceu"] = (sky(scale, "#7FD0FF", "#FFE9F3", int(W_SCENE * 0.15 + 2000), 5, sun_x=0.25), 0.15, -50)
    w = int(W_SCENE * 0.4 + 2100)
    s, c = _surf(w, H, scale)
    x = -40.0
    pastel = ["#FFB3C7", "#B8E3FF", "#FFE08A", "#C9B8FF", "#A8EBC4", "#FFC79E"]
    while x < w:
        bw, bh = rng.uniform(170, 260), rng.uniform(420, 640)
        col = pastel[int(rng.integers(len(pastel)))]
        r = skia.Path()
        r.addRRect(skia.RRect.MakeRectXY(skia.Rect(x, 820 - bh, x + bw, 840), 28, 28))
        soft(c, r, col, light(col), dark(col), (x, 820 - bh, x + bw, 840))
        for yy in np.arange(820 - bh + 50, 760, 78):
            for xx in np.linspace(x + bw * 0.25, x + bw * 0.75, 2):
                c.drawCircle(xx, yy, 18, P("#FFFFFF"))
                c.drawCircle(xx, yy, 13, P("#6EC6FF"))
        x += bw + rng.uniform(10, 40)
    out["BG_predios"] = (s, 0.4, -40)
    s, c = _surf(W_SCENE, H, scale)
    # calçada + rua
    c.drawRect(skia.Rect(0, 840, W_SCENE, 960), P("#E9E4F2"))
    for xx in np.arange(0, W_SCENE, 120):
        c.drawLine(xx, 840, xx, 960, P("#D4CDE3"))
    c.drawRect(skia.Rect(0, 960, W_SCENE, H), P("#5D6380"))
    for xx in np.arange(40, W_SCENE, 220):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(xx, 1015, xx + 110, 1027), 6, 6), P("#FFFFFF"))
    for x in np.arange(300, W_SCENE, 900):      # árvores de calçada e postes
        lollipop_tree(c, x, 850, 330, "#4FC36A", rng)
        px = x + 420
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(px - 8, 560, px + 8, 850), 8, 8), P("#7C83A6"))
        c.drawCircle(px, 556, 24, P("#FFE36E"))
    out["MG_rua"] = (s, 1.0, -20)
    return out


def praia(scale, rng):
    """Praia: mar turquesa com ondinhas, areia clara, guarda-sóis listrados, conchas."""
    out = {}
    out["BG_ceu"] = (sky(scale, "#5CC8FF", "#D8F6FF", int(W_SCENE * 0.15 + 2000), 9), 0.15, -50)
    w = int(W_SCENE * 0.45 + 2100)
    s, c = _surf(w, H, scale)
    c.drawRect(skia.Rect(0, 640, w, H), P("#000", shader=lin((0, 640), (0, 840), [_hex("#2BB8D8"), _hex("#5FE0E6")])))
    for yy in (690, 740, 790):
        p = skia.Path()
        p.moveTo(0, yy)
        for xx in np.linspace(0, w, 160):
            p.lineTo(xx, yy + 6 * math.sin(xx / 40))
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=_c("#E8FFFF"), Style=skia.Paint.kStroke_Style, StrokeWidth=4))
    out["BG_mar"] = (s, 0.45, -40)
    s, c = _surf(W_SCENE, H, scale)
    sand = poly([(0, 830)] + [(x, 820 + 14 * math.sin(x / 300)) for x in np.linspace(0, W_SCENE, 80)] + [(W_SCENE, H + 10), (0, H + 10)])
    c.drawPath(sand, P("#000", shader=lin((0, 820), (0, H), [_hex("#FFF0C2"), _hex("#FFDE94")])))
    for x in np.arange(500, W_SCENE, 1100):        # guarda-sol listrado
        c.drawRect(skia.Rect(x - 6, 560, x + 6, 900), P("#FFFFFF"))
        for k in range(6):
            a0, a1 = math.pi + k * math.pi / 6, math.pi + (k + 1) * math.pi / 6
            c.drawPath(poly([(x, 560)] + [(x + 190 * math.cos(a), 600 + 90 * math.sin(a)) for a in np.linspace(a0, a1, 8)]),
                       P("#FF5A6E" if k % 2 == 0 else "#FFFFFF"))
    for _ in range(40):
        flower(c, rng.uniform(0, W_SCENE), rng.uniform(900, 1070), 0.7, "#FFB3C7", "#FFFFFF")
    out["MG_areia"] = (s, 1.0, -20)
    return out


KINDS = {"parque": parque, "cidade": cidade, "praia": praia}


def build(bg_id: str, out_dir: Path, scale: float = 1.5, seed: int = 4) -> dict:
    kind = bg_id.split("_", 1)[1]
    rng = np.random.default_rng(seed)
    layers = KINDS[kind](scale, rng)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"id": bg_id, "name": f"Fofo — {kind}", "width": W_SCENE, "height": H, "scale": scale,
            "landmarks": {"ground_y": GROUND}, "layers": []}
    for name, (surf, par, z) in layers.items():
        surf.makeImageSnapshot().save(str(out_dir / f"{name}.png"), skia.kPNG)
        meta["layers"].append({"name": name, "file": f"{name}.png", "parallax": par, "z": z,
                               "width": surf.width() / scale, "height": H})
    (out_dir / "background.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta
