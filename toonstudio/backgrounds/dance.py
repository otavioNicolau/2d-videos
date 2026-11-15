"""Fundos gráficos de dança (refrões): cor saturada + faixas onduladas + padrão de silhuetas do tema, ou raios que giram.

Cada variante é um "cenário" próprio (id `danca_<forma>_<cor>`), com 1–2 camadas. A camada de raios tem `spin`
(graus por batida), aplicada pelo compositor no tempo da música.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import skia

from .painter import P, lin, poly

W, H = 2200, 1240     # um pouco maior que a tela: cobre zoom/tremor de câmera
COLORS = {"laranja": ("#FF8A1F", "#FFB04D"), "azul": ("#1E6FD9", "#3C8BF0"), "rosa": ("#F0459A", "#F76FB3"),
          "roxo": ("#7B3FD1", "#9560E3"), "verde": ("#2DB34A", "#4FCB67"), "amarelo": ("#FFC21A", "#FFD658"),
          "vermelho": ("#E0322E", "#F05A4E")}


def _surf(w, h, scale):
    s = skia.Surface(int(w * scale), int(h * scale))
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.scale(scale, scale)
    return s, c


def lizard_silhouette(c, x, y, size, color, angle):
    """Silhueta simples de calanguinho (padrão de fundo, sem rosto)."""
    c.save()
    c.translate(x, y)
    c.rotate(angle)
    c.scale(size / 100, size / 100)
    p = P(color)
    c.drawOval(skia.Rect(-14, -46, 14, 26), p)                 # corpo
    c.drawCircle(0, -52, 15, p)                                # cabeça
    path = skia.Path()
    path.moveTo(-6, 20); path.quadTo(-4, 60, 22, 74); path.quadTo(2, 60, 6, 20); path.close()
    c.drawPath(path, p)                                        # rabo
    for sx, sy, a in ((-1, -30, -0.6), (1, -30, 0.6), (-1, 10, 0.6), (1, 10, -0.6)):
        c.save(); c.translate(sx * 12, sy); c.rotate(math.degrees(a) + (180 if sx < 0 else 0))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(0, -4, 26, 4), 4, 4), p)
        c.drawCircle(27, 0, 5, p)
        c.restore()
    c.restore()


WAVE_PER = 2 * math.pi * 170


def waves(color: str, scale: float, seed: int = 0) -> skia.Surface:
    base, light = COLORS[color]
    Hh = int(H + WAVE_PER + 2)
    s, c = _surf(W, Hh, scale)
    c.drawRect(skia.Rect(0, 0, W, Hh), P(base))
    for k in range(7):      # faixas verticais onduladas, mais claras
        x0 = k * W / 6 - 80
        pts = [(x0 + 70 * math.sin(y / 170 + k), y) for y in np.linspace(-20, Hh + 20, 90)]
        pts += [(x0 + 150 + 70 * math.sin(y / 170 + k + 0.6), y) for y in np.linspace(Hh + 20, -20, 90)]
        c.drawPath(poly(pts), P(light, alpha=0.55))
    rng = np.random.default_rng(seed)
    for i in range(18):     # padrão de silhuetas, tom sobre tom (repetido a cada período para não emendar)
        x, y = (i % 6) * W / 6 + rng.uniform(40, 220), (i // 6) * WAVE_PER / 3 + rng.uniform(60, 300)
        for dy in (0, WAVE_PER):
            lizard_silhouette(c, x, y + dy, rng.uniform(70, 110) if dy == 0 else 90, light, (i * 37) % 100 - 50)
    return s


def rays(color: str, scale: float) -> tuple[skia.Surface, skia.Surface]:
    """Fundo liso + camada de raios (gira no compositor)."""
    base, light = COLORS[color]
    s0, c0 = _surf(W, H, scale)
    c0.drawRect(skia.Rect(0, 0, W, H), P(base))
    R = 1500
    s1, c1 = _surf(2 * R, 2 * R, scale * 0.6)
    for k in range(16):
        a0, a1 = k * 2 * math.pi / 16, (k + 0.5) * 2 * math.pi / 16
        c1.drawPath(poly([(R, R), (R + 2 * R * math.cos(a0), R + 2 * R * math.sin(a0)), (R + 2 * R * math.cos(a1), R + 2 * R * math.sin(a1))]),
                    P(light, alpha=0.6))
    c1.drawCircle(R, R, R, P("#000", shader=skia.GradientShader.MakeRadial(
        skia.Point(R, R), R, [skia.Color4f(1, 1, 1, 0.25).toColor(), skia.Color4f(0, 0, 0, 0.0).toColor()])))
    return s0, s1


def checker(color: str, scale: float, cell: int = 120) -> tuple[skia.Surface, int, int, float]:
    """Xadrez inclinado 45° em dois tons. Período de rolagem sem emenda = cell·√2 (na horizontal e na vertical)."""
    base, light = COLORS[color]
    P = cell * math.sqrt(2)
    w, h = int(W + P + 2), int(H + P + 2)
    s, c = _surf(w, h, scale)
    c.drawRect(skia.Rect(0, 0, w, h), P_(base))
    c.save()
    c.translate(w / 2, h / 2)
    c.rotate(45)
    n = int(max(w, h) / cell) + 4
    for i in range(-n, n):
        for j in range(-n, n):
            if (i + j) % 2 == 0:
                c.drawRect(skia.Rect(i * cell, j * cell, (i + 1) * cell, (j + 1) * cell), P_(light))
    c.restore()
    return s, w, h, P


def dots(color: str, scale: float, gap: int = 110) -> tuple[skia.Surface, int, int, float]:
    """Bolinhas em grade desencontrada. Período = gap na horizontal, 2·gap na vertical (usamos 2·gap nos dois)."""
    base, light = COLORS[color]
    P = 2 * gap
    w, h = int(W + P + 2), int(H + P + 2)
    s, c = _surf(w, h, scale)
    c.drawRect(skia.Rect(0, 0, w, h), P_(base))
    for r in range(-1, int(h / gap) + 2):
        for k in range(-1, int(w / gap) + 2):
            x = k * gap + (gap / 2 if r % 2 else 0)
            c.drawCircle(x, r * gap, gap * 0.22, P_(light, alpha=0.85))
    return s, w, h, P


def P_(c, alpha=None):
    return P(c, alpha)


def build(bg_id: str, out_dir: Path, scale: float = 1.0) -> dict:
    """bg_id: danca_<ondas|raios|xadrez|bolinhas>_<cor>. Camadas com `scroll` rolam sem emenda no compositor."""
    _, kind, color = bg_id.split("_", 2)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"id": bg_id, "name": f"Dança — {kind} {color}", "width": W, "height": H, "scale": scale, "landmarks": {},
            "graphic": True, "layers": []}
    if kind == "ondas":
        waves(color, scale, seed=len(color)).makeImageSnapshot().save(str(out_dir / "BG_ondas.png"), skia.kPNG)
        meta["layers"].append({"name": "BG_ondas", "file": "BG_ondas.png", "parallax": 0.0, "z": -50, "width": W,
                               "height": int(H + WAVE_PER + 2), "fixed": True, "scroll": [0.0, -60.0, 0.0, WAVE_PER]})
    elif kind == "raios":
        s0, s1 = rays(color, scale)
        s0.makeImageSnapshot().save(str(out_dir / "BG_cor.png"), skia.kPNG)
        s1.makeImageSnapshot().save(str(out_dir / "BG_raios.png"), skia.kPNG)
        meta["layers"] += [{"name": "BG_cor", "file": "BG_cor.png", "parallax": 0.0, "z": -50, "width": W, "height": H, "fixed": True},
                           {"name": "BG_raios", "file": "BG_raios.png", "parallax": 0.0, "z": -49, "width": 3000, "height": 3000,
                            "fixed": True, "scale_override": scale * 0.6, "spin_per_beat": 6.0, "center": True}]
    elif kind in ("xadrez", "bolinhas"):
        s0, w, h, per = checker(color, scale) if kind == "xadrez" else dots(color, scale)
        s0.makeImageSnapshot().save(str(out_dir / "BG_padrao.png"), skia.kPNG)
        v = (70.0, 45.0) if kind == "xadrez" else (-50.0, 35.0)
        meta["layers"].append({"name": "BG_padrao", "file": "BG_padrao.png", "parallax": 0.0, "z": -50, "width": w,
                               "height": h, "fixed": True, "scroll": [v[0], v[1], per, per]})
    else:
        raise KeyError(f"fundo de dança desconhecido: {bg_id}")
    (out_dir / "background.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta
