"""Logo do canal FOFOLUCOS (20/11/2026): letras gordinhas, uma cor da turma em cada, borda de adesivo (branca + roxo
escuro); os dois "O" viram olhos de monstro; chifrinhos e presinha nas letras. Saída: library/brand/fofolucos/logo.png
Rodar: PYTHONPATH=. .venv/bin/python scripts/canais/fofolucos_logo.py
"""
from __future__ import annotations

import math
from pathlib import Path

import skia

ROOT = Path(__file__).resolve().parents[2]
FONTE = ROOT / "library" / "fonts" / "Poppins-ExtraBold.ttf"
OUT = ROOT / "library" / "brand" / "fofolucos"
CORES = ["#2F9BF0", "#A66BFF", "#38C44F", "#FF6FB1", "#FF8A2B", "#F2384E", "#2F9BF0", "#38C44F", "#FF6FB1"]
ESCURO = "#2A1240"


def cor(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color4f(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def logo(texto="FOFOLUCOS", tam=260, W=2000, H=640) -> skia.Surface:
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    tf = skia.Typeface.MakeFromFile(str(FONTE))
    font = skia.Font(tf, tam)
    larg = [font.measureText(ch) * 0.98 for ch in texto]
    total = sum(larg)
    x = (W - total) / 2
    base = H * 0.68
    letras = []
    for i, ch in enumerate(texto):
        ang = math.radians((-6, 5, -4, 6, -5, 4, -6, 5, -3)[i % 9])
        dy = (-14, 10, -6, 14, -10, 8, -12, 10, -4)[i % 9]
        path = skia.Path()
        gl = font.textToGlyphs(ch)
        p = font.getPath(gl[0])
        m = skia.Matrix()
        m.setRotate(math.degrees(ang), larg[i] / 2, -tam * 0.35)
        m.postTranslate(x, base + dy)
        p.transform(m)
        letras.append((ch, p, x, larg[i], dy, ang))
        x += larg[i]
    for i, (ch, p, x0, lw, dy, ang) in enumerate(letras):    # chifres ATRÁS das letras (saem de dentro delas)
        b = p.computeTightBounds()
        cx, cy = (b.left() + b.right()) / 2, (b.top() + b.bottom()) / 2
        if i in (0, 8):                                     # chifrinhos no F e no S
            for sd in (-1, 1):
                hx = cx + sd * (b.right() - b.left()) * 0.25
                hy = b.top() - 2
                horn = skia.Path()                          # chifre curvo para fora, espelhado
                horn.moveTo(hx - 20, hy + 14)
                horn.quadTo(hx - 14 + sd * 12, hy - 44, hx + sd * 40, hy - 96)
                horn.quadTo(hx + 20 + sd * 2, hy - 34, hx + 22, hy + 14)
                horn.close()
                for w, col in ((tam * 0.12, ESCURO), (0, "#FFC93C")):
                    st = skia.Paint.kStroke_Style if w else skia.Paint.kFill_Style
                    c.drawPath(horn, skia.Paint(AntiAlias=True, Color4f=cor(col), Style=st, StrokeWidth=w, StrokeJoin=skia.Paint.kRound_Join))
    # bordas de adesivo: roxo escuro grosso, branco, e a letra colorida
    for w, col in ((tam * 0.24, ESCURO), (tam * 0.13, "#FFFFFF")):
        pt = skia.Paint(AntiAlias=True, Color4f=cor(col), Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeJoin=skia.Paint.kRound_Join)
        for _, p, *_ in letras:
            c.drawPath(p, pt)
    for i, (ch, p, x0, lw, dy, ang) in enumerate(letras):
        c.drawPath(p, skia.Paint(AntiAlias=True, Color4f=cor(CORES[i % len(CORES)])))
        b = p.computeTightBounds()
        cx, cy = (b.left() + b.right()) / 2, (b.top() + b.bottom()) / 2
        if ch == "O" and i in (1, 3):                       # os "O" viram olhos de monstro
            r = (b.right() - b.left()) * 0.27
            c.drawCircle(cx, cy, r, skia.Paint(AntiAlias=True, Color4f=cor("#FFFFFF")))
            c.drawCircle(cx + r * 0.18, cy + r * 0.12, r * 0.55, skia.Paint(AntiAlias=True, Color4f=cor(ESCURO)))
            c.drawCircle(cx - r * 0.05, cy - r * 0.15, r * 0.2, skia.Paint(AntiAlias=True, Color4f=cor("#FFFFFF")))
        if i == 5:                                          # presinha no U
            fx, fy = cx, b.bottom() - 4
            fang = skia.Path()
            fang.moveTo(fx - 16, fy - 6)
            fang.lineTo(fx + 16, fy - 6)
            fang.lineTo(fx, fy + 36)
            fang.close()
            c.drawPath(fang, skia.Paint(AntiAlias=True, Color4f=cor(ESCURO), Style=skia.Paint.kStroke_Style, StrokeWidth=14, StrokeJoin=skia.Paint.kRound_Join))
            c.drawPath(fang, skia.Paint(AntiAlias=True, Color4f=cor("#FFFFFF")))
    return surf


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    s = logo()
    s.makeImageSnapshot().save(str(OUT / "logo.png"), skia.kPNG)
    print(OUT / "logo.png")
