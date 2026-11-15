"""Primitivas de desenho "a nanquim" sobre Skia.

Tudo é geometria recalculada a cada quadro (ADR-0002): formas fechadas suaves com contorno de espessura variável
(mais grosso no lado da sombra, como pincel), traços que afinam nas pontas e tubos flexíveis para membros.
Coordenadas em pixels do canvas; y cresce para baixo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np
import skia

Pt = tuple[float, float]
INK = (0.13, 0.09, 0.08, 1.0)          # tinta quase preta, levemente quente
LIGHT = np.array([-0.55, -0.83])        # luz vem de cima-esquerda → linha engrossa embaixo-direita


def color(c: Sequence[float] | str) -> skia.Color4f:
    if isinstance(c, str):
        c = c.lstrip("#")
        if len(c) in (3, 4):
            c = "".join(ch * 2 for ch in c)
        r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
        a = int(c[6:8], 16) / 255 if len(c) == 8 else 1.0
        return skia.Color4f(r, g, b, a)
    return skia.Color4f(*c) if len(c) == 4 else skia.Color4f(*c, 1.0)


def paint(c, style=skia.Paint.kFill_Style, **kw) -> skia.Paint:
    p = skia.Paint(AntiAlias=True, Style=style, **kw)
    p.setColor4f(color(c))
    return p


# ---------------------------------------------------------------- curvas

def catmull_closed(pts: Sequence[Pt], samples: int = 14, tension: float = 0.5) -> np.ndarray:
    """Curva fechada suave passando pelos pontos (Catmull-Rom centrípeta simplificada)."""
    P = np.asarray(pts, dtype=float)
    n = len(P)
    out = []
    ts = np.linspace(0, 1, samples, endpoint=False)
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        m1 = (p2 - p0) * tension
        m2 = (p3 - p1) * tension
        for t in ts:
            t2, t3 = t * t, t * t * t
            out.append((2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2 + (t3 - t2) * m2)
    return np.array(out)


def catmull_open(pts: Sequence[Pt], samples: int = 16, tension: float = 0.5) -> np.ndarray:
    P = np.asarray(pts, dtype=float)
    if len(P) == 2:
        return np.linspace(P[0], P[1], samples)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    ts = np.linspace(0, 1, samples, endpoint=False)
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        m1, m2 = (p2 - p0) * tension, (p3 - p1) * tension
        for t in ts:
            t2, t3 = t * t, t * t * t
            out.append((2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2 + (t3 - t2) * m2)
    out.append(P[-2])
    return np.array(out)


def bezier(p0: Pt, c: Pt, p1: Pt, n: int = 24) -> np.ndarray:
    t = np.linspace(0, 1, n)[:, None]
    a, b, d = np.array(p0), np.array(c), np.array(p1)
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * d


def ellipse_pts(cx: float, cy: float, rx: float, ry: float, rot: float = 0.0, n: int = 12) -> list[Pt]:
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def _normals(P: np.ndarray, closed: bool) -> np.ndarray:
    if closed:
        d = np.roll(P, -1, axis=0) - np.roll(P, 1, axis=0)
    else:
        d = np.gradient(P, axis=0)
    L = np.linalg.norm(d, axis=1, keepdims=True)
    L[L == 0] = 1
    d = d / L
    return np.stack([d[:, 1], -d[:, 0]], axis=1)


def _poly_path(P: np.ndarray, path: skia.Path | None = None) -> skia.Path:
    path = path or skia.Path()
    # suaviza: quadráticas entre pontos médios
    n = len(P)
    m0 = (P[0] + P[1]) / 2
    path.moveTo(*m0)
    for i in range(1, n):
        a, b = P[i], P[(i + 1) % n]
        mid = (a + b) / 2
        path.quadTo(a[0], a[1], mid[0], mid[1])
    path.close()
    return path


def _orient_ccw(P: np.ndarray) -> np.ndarray:
    area = np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
    return P if area < 0 else P[::-1]   # em coordenadas de tela (y para baixo)


# ---------------------------------------------------------------- pincel

@dataclass
class Brush:
    width: float = 6.0          # espessura média do contorno
    vary: float = 0.55          # quanto engrossa no lado da sombra (0 = constante)
    ink: tuple = INK
    jitter: float = 0.0         # "line boil" em px (quadro a quadro)
    seed: int = 0

    def scaled(self, k: float) -> "Brush":
        return Brush(self.width * k, self.vary, self.ink, self.jitter * k, self.seed)


def _jitter(P: np.ndarray, amount: float, seed: int, closed: bool) -> np.ndarray:
    if amount <= 0:
        return P
    rng = np.random.default_rng(seed)
    n = len(P)
    k = max(4, n // 10)
    knots = rng.normal(0, amount, size=(k, 2))
    idx = np.linspace(0, k - (0 if closed else 1), n, endpoint=False if closed else True)
    i0 = np.floor(idx).astype(int) % k
    i1 = (i0 + 1) % k
    f = (idx - np.floor(idx))[:, None]
    f = f * f * (3 - 2 * f)
    return P + knots[i0] * (1 - f) + knots[i1] * f


class Ink:
    """Desenha no canvas Skia com estilo de nanquim."""

    def __init__(self, canvas: skia.Canvas, brush: Brush | None = None):
        self.c = canvas
        self.brush = brush or Brush()
        self._seed = 0

    def _next_seed(self) -> int:
        self._seed += 1
        return self.brush.seed * 1009 + self._seed

    # -- formas fechadas
    def shape(self, pts: Sequence[Pt] | np.ndarray, fill=None, line: float | None = None, smooth: bool = True,
              brush: Brush | None = None, shade: tuple | None = None, shade_offset: Pt = (10, 12),
              clip_extra: Callable[["Ink"], None] | None = None, dense: bool = False) -> np.ndarray:
        """Forma fechada: preenchimento + (sombra interna opcional) + detalhes recortados + contorno variável."""
        b = brush or self.brush
        P = np.asarray(pts, float) if dense else (catmull_closed(pts) if smooth else np.asarray(pts, float))
        P = _jitter(P, b.jitter, self._next_seed(), True)
        P = _orient_ccw(P)
        path = _poly_path(P)
        if fill is not None:
            self.c.drawPath(path, paint(fill))
        if shade is not None or clip_extra is not None:
            self.c.save()
            self.c.clipPath(path, doAntiAlias=True)
            if shade is not None:
                sp = skia.Path(path)
                sp.offset(-shade_offset[0], -shade_offset[1])
                # sombra = forma menos ela mesma deslocada para a luz (meia-lua no lado oposto à luz)
                inv = skia.Path()
                inv.addRect(skia.Rect(-1e5, -1e5, 1e5, 1e5))
                shadow = skia.Op(inv, sp, skia.PathOp.kDifference_PathOp)
                if shadow is not None:
                    self.c.drawPath(shadow, paint(shade))
            if clip_extra is not None:
                clip_extra(self)
            self.c.restore()
        w = b.width if line is None else line
        if w > 0:
            self._outline(P, w, b)
        return P

    def _outline(self, P: np.ndarray, w: float, b: Brush) -> None:
        N = _normals(P, True)
        # normal para fora: em CCW de tela, (dy,-dx) aponta para fora
        shade = np.clip(N @ LIGHT, -1, 1)          # N aponta para dentro; 1 = lado da sombra
        W = w * (1 + b.vary * shade) / 2
        W = np.maximum(W, w * 0.18)
        outer = P + N * W[:, None]
        inner = P - N * W[:, None]
        path = _poly_path(outer)
        _poly_path(inner[::-1], path)
        path.setFillType(skia.PathFillType.kWinding)
        self.c.drawPath(path, paint(b.ink))

    # -- traços abertos
    def stroke(self, pts: Sequence[Pt] | np.ndarray, width: float, taper: tuple[float, float] = (0.15, 0.15),
               color_=None, smooth: bool = True, profile: Callable[[np.ndarray], np.ndarray] | None = None,
               dense: bool = False) -> None:
        """Traço de pincel que afina nas pontas (sobrancelhas, rugas, linhas de ação)."""
        b = self.brush
        P = np.asarray(pts, float) if dense else (catmull_open(pts) if smooth and len(pts) > 2 else
                                                   (np.linspace(pts[0], pts[-1], 12) if len(pts) == 2 else np.asarray(pts, float)))
        P = _jitter(P, b.jitter, self._next_seed(), False)
        n = len(P)
        t = np.linspace(0, 1, n)
        if profile is not None:
            Wt = profile(t)
        else:
            a, z = taper
            Wt = np.ones(n)
            if a > 0:
                Wt = np.minimum(Wt, np.clip(t / a, 0, 1) ** 0.6)
            if z > 0:
                Wt = np.minimum(Wt, np.clip((1 - t) / z, 0, 1) ** 0.6)
            Wt = np.maximum(Wt, 0.12)
        W = width * Wt / 2
        N = _normals(P, False)
        left, right = P + N * W[:, None], P - N * W[:, None]
        poly = np.vstack([left, right[::-1]])
        path = skia.Path()
        path.addPoly([skia.Point(*p) for p in poly], True)
        pt = paint(color_ or b.ink)
        self.c.drawPath(path, pt)
        # pontas arredondadas
        for k in (0, n - 1):
            if W[k] > 0.8:
                self.c.drawCircle(float(P[k][0]), float(P[k][1]), float(W[k]), pt)

    def tube(self, pts: Sequence[Pt] | np.ndarray, w0: float, w1: float, fill, line: float | None = None,
             dense: bool = False, shade=None, ink=None) -> np.ndarray:
        """Membro "de borracha": tubo com contorno, larguras w0→w1 ao longo da curva. `ink` troca a cor do contorno."""
        b = self.brush if ink is None else Brush(self.brush.width, self.brush.vary, ink, self.brush.jitter, self.brush.seed)
        P = np.asarray(pts, float) if dense else catmull_open(pts, samples=12)
        P = _jitter(P, b.jitter * 0.6, self._next_seed(), False)
        n = len(P)
        t = np.linspace(0, 1, n)
        W = (w0 + (w1 - w0) * t) / 2
        lw = b.width if line is None else line
        N = _normals(P, False)

        def poly(extra) -> skia.Path:
            R = W + np.broadcast_to(extra, W.shape)
            left, right = P + N * R[:, None], P - N * R[:, None]
            path = skia.Path()
            path.addPoly([skia.Point(*p) for p in np.vstack([left, right[::-1]])], True)
            for k in (0, n - 1):
                path.addCircle(float(P[k][0]), float(P[k][1]), float(R[k]))
            path.setFillType(skia.PathFillType.kWinding)
            return path

        if lw > 0:
            # contorno: sombra engrossa um lado
            shade_side = np.clip(-(N @ LIGHT), -1, 1)
            extra = lw * (1 + b.vary * 0.5 * np.abs(shade_side)) * 0.5
            self.c.drawPath(poly(extra), paint(b.ink))
        self.c.drawPath(poly(0.0), paint(fill))
        if shade is not None:
            left = P - N * (W * 0.15)[:, None]
            right = P - N * (W * 0.95)[:, None]
            path = skia.Path()
            path.addPoly([skia.Point(*p) for p in np.vstack([left, right[::-1]])], True)
            self.c.drawPath(path, paint(shade))
        return P

    def dot(self, x: float, y: float, r: float, c=None) -> None:
        self.c.drawCircle(x, y, r, paint(c or self.brush.ink))

    def ellipse(self, cx, cy, rx, ry, fill, rot=0.0, line=None, shade=None) -> np.ndarray:
        return self.shape(ellipse_pts(cx, cy, rx, ry, rot, n=16), fill=fill, line=line, shade=shade)


def new_surface(w: int, h: int) -> tuple[skia.Surface, skia.Canvas]:
    s = skia.Surface(w, h)
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    return s, c


def save_png(surface: skia.Surface, path) -> None:
    img = surface.makeImageSnapshot()
    img.save(str(path), skia.kPNG)


def to_array(surface: skia.Surface) -> np.ndarray:
    """RGBA uint8 (não pré-multiplicado)."""
    img = surface.makeImageSnapshot()
    return img.convert(alphaType=skia.kUnpremul_AlphaType, colorType=skia.kRGBA_8888_ColorType).toarray()
