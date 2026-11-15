"""Pintura de cenários (estilo fundo pintado de desenho clássico: sem contorno de nanquim, volumes por manchas
de cor, gradientes e textura de papel). Os personagens têm contorno; o fundo não — isso separa "cel" de "fundo".
"""
from __future__ import annotations

import math

import numpy as np
import skia

from ..drawing.ink import catmull_closed, catmull_open, color


def P(c, alpha: float | None = None, blur: float = 0.0, shader=None) -> skia.Paint:
    p = skia.Paint(AntiAlias=True)
    col = color(c)
    if alpha is not None:
        col = skia.Color4f(col.fR, col.fG, col.fB, alpha)
    p.setColor4f(col)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None:
        p.setShader(shader)
    return p


def poly(points) -> skia.Path:
    path = skia.Path()
    pts = np.asarray(points)
    path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    path.close()
    return path


def blob(c: skia.Canvas, pts, fill, alpha=None, blur=0.0, shader=None):
    c.drawPath(poly(catmull_closed(pts, 10)), P(fill, alpha, blur, shader))


def lin(p0, p1, cols) -> skia.Shader:
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [color(x).toColor() for x in cols])


def radial(center, r, cols) -> skia.Shader:
    return skia.GradientShader.MakeRadial(skia.Point(*center), r, [color(x).toColor() for x in cols])


def paper(c: skia.Canvas, w: float, h: float, strength: float = 0.07, seed: int = 0):
    """Textura de tinta/papel (ruído fractal multiplicado)."""
    sh = skia.PerlinNoiseShader.MakeFractalNoise(0.012, 0.012, 4, seed)
    p = skia.Paint(Shader=sh, BlendMode=skia.BlendMode.kOverlay)
    p.setAlphaf(strength)
    c.drawRect(skia.Rect(0, 0, w, h), p)
    sh2 = skia.PerlinNoiseShader.MakeTurbulence(0.15, 0.15, 2, seed + 1)
    p2 = skia.Paint(Shader=sh2, BlendMode=skia.BlendMode.kSoftLight)
    p2.setAlphaf(strength * 0.6)
    c.drawRect(skia.Rect(0, 0, w, h), p2)


def canopy(c: skia.Canvas, cx, cy, rx, ry, base, mid, light, rng, n=14, dapple=True):
    """Copa de árvore pintada: massa escura, tufos médios, luz no alto-esquerda."""
    blob(c, [(cx + rx * math.cos(a) * (0.85 + 0.25 * rng.random()), cy + ry * math.sin(a) * (0.85 + 0.25 * rng.random()))
             for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)], base)
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.15, 0.75)
        x, y = cx + math.cos(a) * rx * d, cy + math.sin(a) * ry * d - ry * 0.08
        r = rng.uniform(0.22, 0.38) * min(rx, ry)
        up = (cy - y) / ry
        col = mid if up < 0.15 else light
        blob(c, [(x + r * math.cos(b) * (0.8 + 0.3 * rng.random()), y + r * 0.8 * math.sin(b) * (0.8 + 0.3 * rng.random()))
                 for b in np.linspace(0, 2 * math.pi, 9, endpoint=False)], col, alpha=0.9)
    if dapple:
        for _ in range(n // 2):
            x = cx + rng.uniform(-0.6, 0.2) * rx
            y = cy + rng.uniform(-0.8, -0.2) * ry
            c.drawCircle(x, y, rng.uniform(4, 10) * rx / 160, P(light, alpha=0.8))


def trunk(c: skia.Canvas, x, y_top, y_bot, w_top, w_bot, col, dark, light, rng, roots=True):
    pts = [(x - w_top / 2, y_top), (x + w_top / 2, y_top), (x + w_bot / 2 * 1.1, y_bot), (x - w_bot / 2 * 1.1, y_bot)]
    c.drawPath(poly(pts), P(col, shader=lin((x - w_bot / 2, 0), (x + w_bot / 2, 0), [light, col, col, dark])))
    if roots:
        for s in (-1, 1):
            blob(c, [(x + s * w_bot * 0.3, y_bot - 40), (x + s * w_bot * 0.95, y_bot - 4), (x + s * w_bot * 0.85, y_bot + 6),
                     (x + s * w_bot * 0.2, y_bot + 4)], dark if s > 0 else col)
    # casca: traços verticais suaves
    for _ in range(int(w_bot / 6)):
        xx = x + rng.uniform(-0.45, 0.45) * w_bot
        yy = rng.uniform(y_top, y_bot - 30)
        L = rng.uniform(25, 90)
        pa = P(dark, alpha=0.35)
        pa.setStrokeWidth(rng.uniform(2, 4))
        pa.setStyle(skia.Paint.kStroke_Style)
        pa.setStrokeCap(skia.Paint.kRound_Cap)
        c.drawLine(xx, yy, xx + rng.uniform(-4, 4), yy + L, pa)


def grass_tufts(c: skia.Canvas, x0, x1, y0, y1, cols, rng, n=300, h=(10, 28)):
    for _ in range(n):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        hh = rng.uniform(*h) * (0.6 + 0.4 * (y - y0) / max(1, y1 - y0))
        col = cols[rng.integers(len(cols))]
        pa = P(col, alpha=0.9)
        pa.setStyle(skia.Paint.kStroke_Style)
        pa.setStrokeWidth(max(1.5, hh / 9))
        pa.setStrokeCap(skia.Paint.kRound_Cap)
        for k in range(3):
            dx = (k - 1) * hh * 0.25 + rng.uniform(-2, 2)
            path = skia.Path()
            path.moveTo(x + (k - 1) * 2, y)
            path.quadTo(x + dx * 0.4, y - hh * 0.6, x + dx, y - hh)
            c.drawPath(path, pa)
