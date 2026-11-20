"""Cenários de rotina no estilo oficial (BIBLIA_VISUAL.md): vetor chapado, contorno = cor escurecida, sem gradiente.

Ids:
  plano_quarto_rosa · plano_quarto_azul   quarto (Laurinha / Luisinho): parede, papel de parede, chão de madeira, tapete
  plano_cozinha                           azulejos, armários, geladeira, relógio
  plano_casa_frente                       fachada da casa com porta em arco, janelas com floreira (despedida na porta)
  plano_escola                            prédio da escola com placa ESCOLA, bandeirinha, caminho
  plano_ceu                               céu da manhã com nuvens (sol-personagem e voos)
  padrao_<motivo>_<cor>                   fundo de desenhos repetidos que ilustra a palavra cantada (rola sem emenda)
                                          motivos: bananas, leite, lacos, estrelas, coracoes · cores: as de dance.COLORS
Objetos que se mexem (janela, cama, mesa…) NÃO estão aqui: são props (characters/flat_props.py).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import skia

from ..characters.flat_muri import LINE, _rgba, dark
from ..core.config import LIBRARY
from .plano import Flat, PAL as PPAL, _surf

W_INT, H = 2600, 1080
FLOOR_Y = 760          # encontro parede/chão (o personagem pisa por volta de y 930, à frente)
QUARTO = {"rosa": ("#FFD6EC", "#FFC2E2", "#E8B27A"), "azul": ("#D6ECFF", "#C2E0FF", "#E8B27A")}
MOTIVOS = ("bananas", "leite", "lacos", "estrelas", "coracoes", "bolhas", "bolo", "feijao", "gotas", "respingos", "arcoiris", "folhas")


def _text(c, txt, x, y, size, col, outline=None):
    tf = skia.Typeface.MakeFromFile(str(LIBRARY / "fonts" / "Poppins-ExtraBold.ttf"))
    font = skia.Font(tf, size)
    w = font.measureText(txt)
    if outline:
        p = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(outline)), Style=skia.Paint.kStroke_Style, StrokeWidth=size * 0.14,
                       StrokeJoin=skia.Paint.kRound_Join)
        c.drawString(txt, x - w / 2, y, font, p)
    c.drawString(txt, x - w / 2, y, font, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(col))))


def _floor(F: Flat, w, col):
    F.shape([(-20, FLOOR_Y), (w + 20, FLOOR_Y), (w + 20, H + 20), (-20, H + 20)], col, smooth=False)
    for y in (830, 920, 1010):
        F.line([(-10, y), (w + 10, y)], dark(col, 0.9), w=LINE * 0.8)
    for i, y0 in enumerate((FLOOR_Y, 830, 920, 1010)):
        for x in range(120 + i * 90, w, 420):
            F.line([(x, y0 + 4), (x, y0 + 66)], dark(col, 0.9), w=LINE * 0.8)


def quarto(cor: str, rng) -> tuple[skia.Surface, int]:
    parede, papel, chao = QUARTO[cor]
    s, c = _surf(W_INT, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, W_INT, H), skia.Paint(Color4f=skia.Color4f(*_rgba(parede))))
    for y in range(60, FLOOR_Y - 40, 120):                       # papel de parede: bolinhas desencontradas
        for x in range(40 + (60 if (y // 120) % 2 else 0), W_INT, 120):
            c.drawCircle(x, y, 14, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(papel))))
    F.shape([(-20, FLOOR_Y - 30), (W_INT + 20, FLOOR_Y - 30), (W_INT + 20, FLOOR_Y), (-20, FLOOR_Y)], "#FFFFFF", smooth=False)
    _floor(F, W_INT, chao)
    F.oval(W_INT * 0.5, 960, 420, 70, "#FFE066" if cor == "rosa" else "#9FDCCB")          # tapete
    F.oval(W_INT * 0.5, 960, 330, 50, "#FFFFFF")
    # prateleira com livros e brinquedo
    x0 = 2050
    F.shape([(x0, 420), (x0 + 360, 420), (x0 + 360, 444), (x0, 444)], "#C98A4E", smooth=False)
    for j, (h_, col) in enumerate(((120, "#E9545D"), (100, "#3C8BF0"), (130, "#2DB34A"), (90, "#FFC21A"))):
        F.shape([(x0 + 20 + j * 44, 420 - h_), (x0 + 58 + j * 44, 420 - h_), (x0 + 58 + j * 44, 420), (x0 + 20 + j * 44, 420)], col, smooth=False)
    F.oval(x0 + 290, 380, 38, 38, "#B865E6")
    # quadrinho de estrela
    F.shape([(330, 230), (530, 230), (530, 400), (330, 400)], "#FFFFFF", smooth=False)
    pts = [(430 + math.cos(-math.pi / 2 + j * math.pi / 5) * (60 if j % 2 == 0 else 26),
            318 + math.sin(-math.pi / 2 + j * math.pi / 5) * (60 if j % 2 == 0 else 26)) for j in range(10)]
    F.shape(pts, "#FFD23F", smooth=False)
    # abajur
    F.shape([(1950, 700), (1990, 700), (1990, 600), (1950, 600)], "#FFFFFF", smooth=False)
    F.shape([(1890, 600), (2050, 600), (2010, 520), (1930, 520)], "#FF8CC6" if cor == "rosa" else "#3C8BF0", smooth=False)
    F.shape([(1900, 700), (2040, 700), (2040, 760), (1900, 760)], "#C98A4E", smooth=False)
    return s, W_INT


def cozinha(rng) -> tuple[skia.Surface, int]:
    s, c = _surf(W_INT, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, W_INT, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#FFF4C9"))))
    for x in range(0, W_INT, 90):                                 # azulejos
        F.line([(x, 0), (x, FLOOR_Y)], "#F1E2A8", w=LINE * 0.6)
    for y in range(0, FLOOR_Y, 90):
        F.line([(0, y), (W_INT, y)], "#F1E2A8", w=LINE * 0.6)
    _floor(F, W_INT, "#9FDCCB")
    # armários e bancada à esquerda
    F.shape([(60, 500), (760, 500), (760, FLOOR_Y + 40), (60, FLOOR_Y + 40)], "#FF8A5B", smooth=False)
    F.shape([(40, 470), (780, 470), (780, 505), (40, 505)], "#FFFFFF", smooth=False)
    for x in (110, 350, 590):
        F.shape([(x, 540), (x + 200, 540), (x + 200, FLOOR_Y + 10), (x, FLOOR_Y + 10)], "#FFA27F", smooth=False)
        F.oval(x + 170, 640, 10, 10, "#FFFFFF")
    F.shape([(120, 150), (700, 150), (700, 330), (120, 330)], "#FF8A5B", smooth=False)                  # armário alto
    F.line([(410, 160), (410, 320)], dark("#FF8A5B"), w=LINE)
    # geladeira à direita
    F.shape([(2100, 230), (2420, 230), (2420, FLOOR_Y + 40), (2100, FLOOR_Y + 40)], "#FFFFFF", smooth=False)
    F.line([(2100, 440), (2420, 440)], "#C9D6E0", w=LINE)
    for y in (330, 560):
        F.shape([(2140, y), (2160, y), (2160, y + 70), (2140, y + 70)], "#C9D6E0", smooth=False)
    F.oval(2300, 330, 24, 24, "#FFD23F")                                                                 # ímã
    # relógio de parede
    F.oval(1300, 220, 90, 90, "#FFFFFF")
    F.line([(1300, 220), (1300, 160)], "#534946", w=LINE * 1.2)
    F.line([(1300, 220), (1345, 240)], "#534946", w=LINE * 1.2)
    # vaso de planta
    F.shape([(1760, 640), (1860, 640), (1840, FLOOR_Y), (1780, FLOOR_Y)], "#E9545D", smooth=False)
    for a in (-0.6, -0.2, 0.2, 0.6):
        F.leaf(1810, 640, 90, -math.pi / 2 + a, PPAL["folha"])
    return s, W_INT


def casa_frente(rng) -> tuple[skia.Surface, int]:
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba(PPAL["ceu"]))))
    for x, y in ((200, 140), (900, 90), (2300, 160)):
        F.cloud(x, y, 1.1)
    F.shape([(-20, 820), (w + 20, 820), (w + 20, H + 20), (-20, H + 20)], PPAL["grama"], smooth=False)
    cx = w / 2
    F.shape([(cx - 760, 840), (cx - 760, 260), (cx + 760, 260), (cx + 760, 840)], PPAL["parede"], smooth=False)
    F.shape([(cx - 840, 270), (cx, 20), (cx + 840, 270)], PPAL["telhado"], smooth=False)
    # porta grande em arco (base reta)
    arco = [(cx + 150 * np.cos(a), 560 - 150 * np.sin(a)) for a in np.linspace(np.pi, 0, 28)]
    F.shape([(cx - 150, 840)] + arco + [(cx + 150, 840)], PPAL["porta"], smooth=False)
    F.oval(cx + 100, 700, 14, 14, "#FFE066")
    for wx in (cx - 480, cx + 480):                               # janelas com floreira
        F.shape([(wx - 140, 380), (wx + 140, 380), (wx + 140, 620), (wx - 140, 620)], PPAL["janela"], smooth=False)
        F.line([(wx, 380), (wx, 620)], dark(PPAL["janela"]), w=LINE)
        F.line([(wx - 140, 500), (wx + 140, 500)], dark(PPAL["janela"]), w=LINE)
        F.shape([(wx - 170, 620), (wx + 170, 620), (wx + 150, 690), (wx - 150, 690)], "#C98A4E", smooth=False)
        for j in range(6):
            F.flower(wx - 140 + j * 56, 612, PPAL["flor"][j % len(PPAL["flor"])])
    F.shape([(cx - 230, 840), (cx + 230, 840), (cx + 260, 880), (cx - 260, 880)], "#7F7D7B", smooth=False)   # degrau
    for x in (160, 2440):
        F.bush(x, 860, 1.2)
    return s, w


def escola(rng) -> tuple[skia.Surface, int]:
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba(PPAL["ceu"]))))
    for x, y in ((260, 120), (1400, 80), (2350, 150)):
        F.cloud(x, y, 1.0)
    F.shape([(-20, 820), (w + 20, 820), (w + 20, H + 20), (-20, H + 20)], PPAL["grama"], smooth=False)
    cx = w / 2
    F.shape([(cx - 900, 840), (cx - 900, 330), (cx + 900, 330), (cx + 900, 840)], "#FF9A6B", smooth=False)
    F.shape([(cx - 300, 330), (cx - 300, 180), (cx + 300, 180), (cx + 300, 330)], "#FF9A6B", smooth=False)
    F.shape([(cx - 340, 190), (cx, 40), (cx + 340, 190)], PPAL["telhado"], smooth=False)
    F.shape([(cx - 260, 210), (cx + 260, 210), (cx + 260, 310), (cx - 260, 310)], "#FFFFFF", smooth=False)
    _text(c, "ESCOLA", cx, 290, 92, "#3E7BD6")
    arco = [(cx + 160 * np.cos(a), 600 - 160 * np.sin(a)) for a in np.linspace(np.pi, 0, 28)]
    F.shape([(cx - 160, 840)] + arco + [(cx + 160, 840)], "#3E7BD6", smooth=False)
    F.line([(cx, 470), (cx, 840)], dark("#3E7BD6"), w=LINE)
    for wx in (cx - 640, cx - 380, cx + 380, cx + 640):
        F.shape([(wx - 100, 420), (wx + 100, 420), (wx + 100, 620), (wx - 100, 620)], PPAL["janela"], smooth=False)
        F.line([(wx, 420), (wx, 620)], dark(PPAL["janela"]), w=LINE)
    F.line([(cx + 980, 840), (cx + 980, 300)], "#7F7D7B", w=LINE * 1.6)                                     # mastro
    F.shape([(cx + 980, 300), (cx + 1160, 330), (cx + 980, 370)], "#FFD23F", smooth=False)                    # bandeirinha
    F.shape([(cx - 160, 840), (cx + 160, 840), (cx + 360, H + 20), (cx - 360, H + 20)], "#F2D9A6", smooth=False)  # caminho
    for x in (240, 520, 2100, 2380):
        F.bush(x, 860, 1.1)
    return s, w


def ceu(rng) -> tuple[skia.Surface, int]:
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#9CCBFA"))))
    for _ in range(14):
        F.cloud(rng.uniform(0, w), rng.uniform(80, 1000), rng.uniform(0.9, 1.8))
    return s, w


COR_MOTIVO = {"bananas": "#FFE066", "leite": "#FFFFFF", "lacos": "#FFD23F", "estrelas": "#FFFFFF", "coracoes": "#FFFFFF",
              "bolhas": "#E8F6FF", "bolo": "#F7C948", "feijao": "#8E3B2E", "gotas": "#9CD8FF", "arcoiris": "#FFFFFF", "folhas": "#5CCB6E"}
TINTAS = ("#2F86F0", "#FFD21F", "#EE3B3B", "#2DBE5A", "#FF8A1F", "#8E44EF")   # respingos: uma cor por desenho


def _motivo(c, kind, x, y, s, col):
    """Desenho do padrão com a cor REAL do objeto e contorno escurecido (legível sobre qualquer fundo)."""
    p = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(col, 0.95)))
    pl = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(dark(col, 0.75))), Style=skia.Paint.kStroke_Style,
                    StrokeWidth=LINE * 0.8 / max(s, 1e-3), StrokeJoin=skia.Paint.kRound_Join)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if kind == "bananas":
        from ..characters.flat_props import _banana_lado
        esq, dir_ = _banana_lado(0.0, 1.0, 16, w0=16, comp=86, curva=22)
        path = skia.Path()
        pts = [(px, py + 43) for px, py in esq + dir_[::-1]]
        path.moveTo(*pts[0])
        for pt in pts[1:]:
            path.lineTo(*pt)
        path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
        c.drawRect(skia.Rect(-3, 40, 3, 52), skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#7A5A2E"))))
    elif kind == "leite":
        path = skia.Path()
        path.moveTo(0, -42); path.quadTo(30, 0, 22, 18); path.quadTo(0, 44, -22, 18); path.quadTo(-30, 0, 0, -42); path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
    elif kind == "lacos":
        for sgn in (-1, 1):
            path = skia.Path()
            path.moveTo(0, 0); path.lineTo(sgn * 40, -24); path.lineTo(sgn * 44, 18); path.close()
            c.drawPath(path, p); c.drawPath(path, pl)
        c.drawCircle(0, 0, 11, p); c.drawCircle(0, 0, 11, pl)
    elif kind == "estrelas":
        path = skia.Path()
        for j in range(10):
            a = -math.pi / 2 + j * math.pi / 5
            r = 40 if j % 2 == 0 else 17
            (path.moveTo if j == 0 else path.lineTo)(math.cos(a) * r, math.sin(a) * r)
        path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
    elif kind == "bolhas":
        c.drawCircle(0, 0, 34, p); c.drawCircle(0, 0, 34, pl)
        c.drawCircle(42, 26, 16, p); c.drawCircle(42, 26, 16, pl)
        c.drawCircle(-12, -14, 8, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(1, 1, 1, 1)))
    elif kind == "bolo":
        path = skia.Path()
        path.moveTo(-34, 22); path.lineTo(34, 22); path.lineTo(22, -26); path.lineTo(-22, -26); path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
        c.drawRect(skia.Rect(-22, -34, 22, -26), skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#D9902E"))))
    elif kind == "feijao":                                      # grãozinho de feijão (rim) com olhinho claro
        path = skia.Path()
        for j in range(30):
            t = j / 30 * 2 * math.pi
            r = 1.0 - 0.18 * max(0.0, math.cos(t - math.pi / 2)) ** 3
            (path.moveTo if j == 0 else path.lineTo)(48 * math.cos(t) * r, 31 * math.sin(t) * r)
        path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
        c.drawOval(skia.Rect(8, 16, 30, 23), skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#F2E6D8"))))
    elif kind == "gotas":                                       # gotinha d'água com brilho
        c.scale(1.4, 1.4)
        path = skia.Path()
        path.moveTo(0, -34); path.cubicTo(14, -12, 24, 0, 24, 10); path.cubicTo(24, 26, 12, 34, 0, 34)
        path.cubicTo(-12, 34, -24, 26, -24, 10); path.cubicTo(-24, 0, -14, -12, 0, -34); path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
        c.drawCircle(-9, 8, 5, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(1, 1, 1, 1)))
    elif kind == "respingos":                                   # mancha de tinta com gotinhas em volta
        path = skia.Path()
        for j in range(24):
            t = j / 24 * 2 * math.pi
            r = 34 * (1 + 0.3 * math.sin(5 * t) + 0.12 * math.sin(3 * t + 1))
            (path.moveTo if j == 0 else path.lineTo)(r * math.cos(t), r * math.sin(t))
        path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
        for dx, dy, r in ((52, -20, 8), (-48, 30, 6), (30, 50, 7)):
            c.drawCircle(dx, dy, r, p); c.drawCircle(dx, dy, r, pl)
    elif kind == "arcoiris":                                    # arco-íris pequeno com nuvenzinhas
        for i, cc in enumerate(("#EE3B3B", "#FF8A1F", "#FFD21F", "#2DBE5A", "#2F86F0", "#8E44EF")):
            r = 54 - i * 7
            arc = skia.Path()
            arc.addArc(skia.Rect(-r, -r + 10, r, r + 10), 180, 180)
            c.drawPath(arc, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(cc)), Style=skia.Paint.kStroke_Style,
                                       StrokeWidth=7.5 / max(s, 1e-3) * s))
        for cx in (-42, 42):
            c.drawCircle(cx, 12, 13, p); c.drawCircle(cx, 12, 13, pl)
    elif kind == "folhas":                                      # vitória-régia pequenininha com fendinha
        c.drawOval(skia.Rect(-46, -20, 46, 20), p); c.drawOval(skia.Rect(-46, -20, 46, 20), pl)
        c.drawLine(0, 0, 18, 14, pl)
    elif kind == "coracoes":
        path = skia.Path()
        path.moveTo(0, 30); path.cubicTo(-50, -4, -26, -44, 0, -18); path.cubicTo(26, -44, 50, -4, 0, 30); path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
    c.restore()


def padrao(kind: str, color: str, scale: float, gap: int = 180):
    from .dance import COLORS, W as DW, H as DH
    base, light = COLORS[color]
    P_ = 2 * gap
    w, h = int(DW + P_ + 2), int(DH + P_ + 2)
    s, c = _surf(w, h, scale)
    c.drawRect(skia.Rect(0, 0, w, h), skia.Paint(Color4f=skia.Color4f(*_rgba(base))))
    for r in range(-1, int(h / gap) + 2):
        for k in range(-1, int(w / gap) + 2):
            x = k * gap + (gap / 2 if r % 2 else 0)
            ang = 0.35 if (r + k) % 2 else -0.35
            c.save(); c.translate(x, r * gap); c.rotate(math.degrees(ang))
            cor_m = TINTAS[(r * 3 + k) % len(TINTAS)] if kind == "respingos" else COR_MOTIVO.get(kind, light)
            _motivo(c, kind, 0, 0, 1.2, cor_m)
            c.restore()
    return s, w, h, P_


def banheiro(rng) -> tuple[skia.Surface, int]:
    s, c = _surf(W_INT, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, W_INT, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#D6F1FF"))))
    for xx in range(0, W_INT, 110):                               # azulejos azuis
        F.line([(xx, 0), (xx, FLOOR_Y)], "#B9E2F7", w=LINE * 0.6)
    for yy in range(0, FLOOR_Y, 110):
        F.line([(0, yy), (W_INT, yy)], "#B9E2F7", w=LINE * 0.6)
    _floor(F, W_INT, "#F2F2F7")
    cx = 1300                                                     # pia com torneira e espelho
    F.shape([(cx - 300, 560), (cx + 300, 560), (cx + 260, 640), (cx - 260, 640)], "#FFFFFF", smooth=False)
    F.shape([(cx - 70, 640), (cx + 70, 640), (cx + 50, FLOOR_Y + 60), (cx - 50, FLOOR_Y + 60)], "#FFFFFF", smooth=False)
    F.shape([(cx - 20, 560), (cx - 20, 480), (cx + 60, 480), (cx + 60, 500), (cx, 500), (cx, 560)], "#B8C4D0", smooth=False)
    F.oval(cx - 90, 548, 22, 12, "#E9545D")
    F.oval(cx + 110, 548, 22, 12, "#3C8BF0")
    F.oval(cx, 300, 190, 150, "#FFD23F")
    F.oval(cx, 300, 160, 122, "#CFE8FA")
    F.shape([(1900, 360), (2060, 360), (2060, 700), (1900, 700)], "#FF8CC6", smooth=False)      # toalha
    F.line([(1880, 360), (2080, 360)], "#B8C4D0", w=LINE * 1.6)
    F.oval(620, 640, 60, 80, "#9FDCCB")                                                     # vaso de planta
    for a in (-0.6, -0.2, 0.2, 0.6):
        F.leaf(620, 570, 80, -math.pi / 2 + a, PPAL["folha"])
    return s, W_INT


def jardim(rng) -> tuple[skia.Surface, int]:
    """Jardim visto por quem é pequenininho (mundo pequenino): hastes de flores e folhas de grama GIGANTES, céu, chão de grama."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#A8D8FF"))))
    for x, y, sc in ((300, 140, 1.4), (1150, 90, 1.7), (2050, 160, 1.3)):
        F.cloud(x, y, sc)
    flores = (("#FF6FA8", "#FFD23F"), ("#FFFFFF", "#FFC21A"), ("#9B6CFF", "#FFE066"), ("#FF8A1F", "#FFF3B0"), ("#3C8BF0", "#FFFFFF"))
    for i, x in enumerate(range(160, w, 420)):                  # flores gigantes ao fundo (haste + folha + flor)
        topo = 170 + (i * 97) % 180
        F.shape([(x - 16, FLOOR_Y + 20), (x - 12, topo), (x + 12, topo), (x + 16, FLOOR_Y + 20)], "#3DAE4E", smooth=False)
        F.leaf(x + 14, topo + 300, 170, -0.5, "#4CC35E")
        F.leaf(x - 14, topo + 420, 150, math.pi + 0.5, "#4CC35E")
        petala, miolo = flores[i % len(flores)]
        for j in range(8):
            a = j * math.pi / 4
            F.oval(x + math.cos(a) * 92, topo + math.sin(a) * 92, 62, 42, petala, a=a)
        F.oval(x, topo, 64, 64, miolo)
    for i, x in enumerate(range(0, w + 120, 130)):               # folhas de grama altas na frente do fundo
        h = 260 + (i * 53) % 160
        lean = 40 if i % 2 else -30
        F.shape([(x - 34, FLOOR_Y + 40), (x + lean, FLOOR_Y - h), (x + 34, FLOOR_Y + 40)], "#5CCB5F" if i % 2 else "#49B84F")
    F.shape([(-20, FLOOR_Y), (w + 20, FLOOR_Y), (w + 20, H + 20), (-20, H + 20)], "#7BD36A", smooth=False)
    for x in range(40, w, 90):                                  # tufinhos no chão
        F.grass_ticks(x + (x * 7) % 40, FLOOR_Y + 60 + (x * 13) % 220)
    return s, w


def lagoa(rng) -> tuple[skia.Surface, int]:
    """Beira da lagoa vista de pertinho: céu de tarde, árvores ao fundo, a água com brilhos e vitórias-régias,
    margem de grama na frente (onde a turma pisa)."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#AEDCFF"))))
    for x, y, sc in ((420, 130, 1.4), (1450, 90, 1.6), (2250, 150, 1.2)):
        F.cloud(x, y, sc)
    for x in range(-60, w + 200, 260):                           # mata ao fundo
        F.oval(x, 430, 180, 140, "#5BB84F")
        F.oval(x + 120, 400, 150, 120, "#4CAA46")
    F.shape([(-20, 470), (w + 20, 470), (w + 20, 800), (-20, 800)], "#4FA8E8", smooth=False)      # água
    for j in range(16):                                          # brilhos
        x, y = (j * 397) % w, 520 + (j * 53) % 220
        F.line([(x, y), (x + 70, y)], "#BFE6FF", w=LINE * 1.2)
    for x, y, sx in ((350, 640, 1.0), (1700, 560, 0.7), (2300, 700, 0.9)):    # vitórias-régias ao fundo
        F.oval(x, y, 150 * sx, 32 * sx, "#5CCB6E")
        F.line([(x, y), (x + 40 * sx, y + 22 * sx)], "#25803A", w=LINE)
    F.shape([(-20, 790), (w + 20, 760), (w + 20, H + 20), (-20, H + 20)], "#7BD36A", smooth=False)  # margem
    for x in range(40, w, 110):
        F.grass_ticks(x + (x * 7) % 40, 820 + (x * 13) % 220)
    for x in (120, 980, 2480):                                   # taboas na margem
        for d, h in ((-24, 330), (0, 380), (26, 300)):
            F.line([(x + d, 800), (x + d + 6, 800 - h)], "#3F8F3A", w=LINE * 1.6)
            F.oval(x + d + 6, 800 - h + 40, 14, 40, "#7A4A2A")
    return s, w


def sala(rng) -> tuple[skia.Surface, int]:
    """Sala da casa em dezembro: parede creme com listrinhas, janela com dia de sol (Natal no calor), sofá e tapete.
    A árvore de Natal é prop (acende/apaga); aqui fica só o cenário."""
    s, c = _surf(W_INT, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, W_INT, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#FFF1D6"))))
    for x in range(0, W_INT, 90):                                 # listrinhas verticais
        c.drawRect(skia.Rect(x, 0, x + 30, FLOOR_Y - 30), skia.Paint(Color4f=skia.Color4f(*_rgba("#FFE7BF"))))
    F.shape([(-20, FLOOR_Y - 30), (W_INT + 20, FLOOR_Y - 30), (W_INT + 20, FLOOR_Y), (-20, FLOOR_Y)], "#FFFFFF", smooth=False)
    _floor(F, W_INT, "#E8B27A")
    F.oval(W_INT * 0.5, 960, 460, 74, "#E9545D")                 # tapete vermelho com borda verde
    F.oval(W_INT * 0.5, 960, 380, 56, "#3DAE57")
    x0, y0 = 300, 180                                            # janela: dia de sol lá fora
    F.shape([(x0, y0), (x0 + 380, y0), (x0 + 380, y0 + 330), (x0, y0 + 330)], "#FFFFFF", smooth=False)
    F.shape([(x0 + 20, y0 + 20), (x0 + 360, y0 + 20), (x0 + 360, y0 + 310), (x0 + 20, y0 + 310)], "#9CCBFA", smooth=False)
    F.oval(x0 + 280, y0 + 90, 46, 46, "#FFD23F")
    F.line([(x0 + 190, y0 + 20), (x0 + 190, y0 + 310)], "#FFFFFF", w=LINE * 2)
    F.line([(x0 + 20, y0 + 165), (x0 + 360, y0 + 165)], "#FFFFFF", w=LINE * 2)
    for j in range(9):                                           # festão de bolinhas em cima da janela
        F.oval(x0 + 10 + j * 45, y0 - 8 + 14 * math.sin(j * 0.9), 13, 13, ("#E9545D", "#FFD23F", "#3DAE57")[j % 3])
    sx = 1950                                                    # sofá
    F.shape([(sx, 560), (sx + 520, 560), (sx + 520, 720), (sx, 720)], "#3C8BF0", smooth=True)
    F.shape([(sx - 40, 650), (sx + 560, 650), (sx + 560, 780), (sx - 40, 780)], "#2F6FD0", smooth=True)
    for k in (sx + 90, sx + 390):
        F.oval(k, 610, 70, 48, "#FFD23F")
    return s, W_INT


def espaco(rng) -> tuple[skia.Surface, int]:
    """Espaço: azul-escuro com estrelinhas e planetinhas coloridos (sem chão)."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#1B2A6B"))))
    for _ in range(140):
        x, y, r = rng.uniform(0, w), rng.uniform(0, H), rng.uniform(2, 6)
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#FFFFFF", 0.9))))
    for x, y, rr, col in ((300, 220, 70, "#FF8AC6"), (2250, 300, 90, "#FFB04D"), (1500, 900, 50, "#7FD3A0")):
        F.oval(x, y, rr, rr, col)
        F.oval(x, y, rr * 1.6, rr * 0.35, "#FFE680", a=-0.3) if col == "#FFB04D" else None
    return s, w


def lua_chao(rng) -> tuple[skia.Surface, int]:
    """Chão da lua (cinza claro com crateras) e céu escuro estrelado; a Terra fica como prop."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#1B2A6B"))))
    for _ in range(90):
        c.drawCircle(rng.uniform(0, w), rng.uniform(0, FLOOR_Y), rng.uniform(2, 5), skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#FFFFFF", 0.9))))
    F.shape([(-20, FLOOR_Y - 40), (w * 0.3, FLOOR_Y - 90), (w * 0.6, FLOOR_Y - 50), (w + 20, FLOOR_Y - 100), (w + 20, H + 20), (-20, H + 20)], "#D9D6C4")
    for x, y, rr in ((300, 900, 90), (900, 1000, 60), (1500, 880, 110), (2200, 980, 70), (2500, 860, 50)):
        F.oval(x, y, rr, rr * 0.3, "#BDB9A4")
    return s, w


def campo(rng) -> tuple[skia.Surface, int]:
    """Campo do carneirinho (Méé, Carneirinho!): céu azul com nuvens fofas, morrinhos verdes que se sobrepõem,
    cerquinha de madeira ao fundo, florzinhas e tufinhos no gramado da frente (onde a turma pisa)."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#9ED6FF"))))
    F.oval(2280, 150, 90, 90, "#FFE066")                                    # solzinho
    for x, y, sc in ((260, 130, 1.5), (900, 210, 1.2), (1500, 110, 1.7), (2000, 250, 1.1)):
        F.cloud(x, y, sc)
    for col, base, amp, per, ph in (("#8EDB7A", 560, 120, 520, 0.0), ("#74CC66", 640, 100, 430, 1.3)):
        pts = [(-60, H + 20)] + [(x, base - amp * (0.5 + 0.5 * math.sin(x / per * math.pi + ph))) for x in np.linspace(-60, w + 60, 120)] \
            + [(w + 60, H + 20)]
        F.shape(pts, col, smooth=False)
    for x in range(-40, w + 80, 170):                                        # cerquinha comprida ao fundo
        F.shape([(x - 12, 720), (x + 12, 720), (x + 12, 600), (x, 588), (x - 12, 600)], "#D9A066", smooth=False)
    for y in (630, 680):
        F.shape([(-40, y - 9), (w + 40, y - 9), (w + 40, y + 9), (-40, y + 9)], "#D9A066", smooth=False)
    F.shape([(-20, FLOOR_Y - 20), (w * 0.35, FLOOR_Y - 40), (w * 0.7, FLOOR_Y - 10), (w + 20, FLOOR_Y - 30), (w + 20, H + 20), (-20, H + 20)],
            "#7BD36A")
    flores = ("#FFFFFF", "#FFD23F", "#FF8AC6", "#B98CFF")
    for j, x in enumerate(range(60, w, 150)):                                # florzinhas e tufos no gramado
        y = FLOOR_Y + 30 + (j * 67) % 250
        F.grass_ticks(x + (j * 31) % 60, y)
        if j % 2 == 0:
            F.flower(x + 50, y + 20, flores[j // 2 % len(flores)])
    return s, w


def gelo(rng) -> tuple[skia.Surface, int]:
    """Polo gelado (Andar de Pinguim): céu clarinho, mar azul ao fundo com icebergs, chão de gelo branco-azulado com
    montinhos de neve (atrás deles um pinguim pode se esconder) e risquinhos de gelo liso (para escorregar)."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#CDEBFF"))))
    F.oval(2250, 160, 80, 80, "#FFF3B0")
    for x, y, sc in ((380, 150, 1.2), (1250, 110, 1.5), (1900, 200, 1.0)):
        F.cloud(x, y, sc)
    F.shape([(-20, 520), (w + 20, 520), (w + 20, 700), (-20, 700)], "#4FA8E8", smooth=False)       # mar
    for x, base, ww, hh in ((260, 560, 300, 230), (980, 540, 220, 160), (1700, 560, 360, 280), (2400, 545, 240, 190)):
        F.shape([(x - ww / 2, base), (x - ww * 0.3, base - hh * 0.7), (x - ww * 0.05, base - hh), (x + ww * 0.2, base - hh * 0.8),
                 (x + ww / 2, base)], "#F4FBFF", smooth=False)
        F.shape([(x - ww * 0.05, base - hh), (x + ww * 0.2, base - hh * 0.8), (x + ww / 2, base), (x + ww * 0.05, base)], "#D5ECFA", smooth=False)
    for j in range(14):
        x, y = (j * 211) % w, 600 + (j * 37) % 80
        F.line([(x, y), (x + 60, y)], "#BFE6FF", w=LINE)
    F.shape([(-20, 690), (w * 0.3, 670), (w * 0.62, 700), (w + 20, 680), (w + 20, H + 20), (-20, H + 20)], "#F2F9FF")
    for x, y, ww in ((180, 760, 260), (1150, 745, 200), (2050, 755, 300)):                        # montinhos de neve
        F.oval(x, y, ww, 70, "#FFFFFF")
        F.oval(x + ww * 0.3, y - 30, ww * 0.5, 50, "#FFFFFF")
    for j in range(18):                                                                           # risquinhos de gelo liso
        x, y = (j * 157 + 40) % w, 830 + (j * 61) % 220
        F.line([(x, y), (x + 90, y - 6)], "#BFDDF2", w=LINE)
    return s, w


def mar_gelado(rng) -> tuple[skia.Surface, int]:
    """Debaixo d'água no mar gelado (o pinguim "voa" nadando): faixas de azul, raios de luz, bolhinhas,
    a beira do gelo lá em cima e algas e pedrinhas no fundo."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#3E9BE0"))))
    for y0, col in ((360, "#3590D6"), (620, "#2C82C9"), (860, "#2474B8")):
        F.shape([(-20, y0), (w + 20, y0 - 30), (w + 20, H + 20), (-20, H + 20)], col, smooth=False)
    for x in (300, 900, 1500, 2100):                                                              # raios de luz
        c.drawPath(skia.Path.Polygon([skia.Point(x, 0), skia.Point(x + 160, 0), skia.Point(x + 420, H), skia.Point(x + 220, H)], True),
                   skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#FFFFFF", 0.10))))
    F.shape([(-20, -20), (w + 20, -20), (w + 20, 60), (w * 0.7, 90), (w * 0.4, 50), (-20, 80)], "#F2F9FF")   # gelo em cima
    for _ in range(40):
        x, y, r = rng.uniform(0, w), rng.uniform(120, 900), rng.uniform(6, 18)
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#CFEFFF", 0.7)), Style=skia.Paint.kStroke_Style,
                                         StrokeWidth=3))
    F.shape([(-20, 990), (w + 20, 970), (w + 20, H + 20), (-20, H + 20)], "#E8D29A")
    for x in range(80, w, 260):                                                                   # algas
        h = 180 + (x * 7) % 120
        F.shape([(x - 14, 1000), (x - 30, 1000 - h * 0.5), (x, 1000 - h), (x + 26, 1000 - h * 0.5), (x + 14, 1000)], "#3DAE6E")
    for x, rr in ((400, 40), (1300, 55), (2000, 35)):
        F.oval(x, 1010, rr, rr * 0.6, "#9AA6B8")
    return s, w


def fundo_mar(rng) -> tuple[skia.Surface, int]:
    """Fundo do mar tropical (25, Polvo de Oito Braços): água turquesa em faixas, raios de sol vindos de cima, bolhinhas,
    corais coloridos (rosa, laranja, roxo), algas balançando, areia clarinha com conchas e estrelas-do-mar, e a TOCA do
    polvo (pedra redonda com entrada escura) à esquerda."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#5FD3E0"))))
    for y0, col in ((300, "#4CC6D8"), (560, "#3BB5CF"), (790, "#30A6C4")):
        F.shape([(-20, y0), (w * 0.5, y0 + 30), (w + 20, y0 - 20), (w + 20, H + 20), (-20, H + 20)], col)
    for x in (250, 850, 1450, 2050):                                                              # raios de sol
        c.drawPath(skia.Path.Polygon([skia.Point(x, 0), skia.Point(x + 140, 0), skia.Point(x + 380, H), skia.Point(x + 200, H)], True),
                   skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#FFFFFF", 0.12))))
    for _ in range(45):                                                                           # bolhinhas
        x, y, r = rng.uniform(0, w), rng.uniform(60, 820), rng.uniform(6, 16)
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#E6FBFF", 0.8)), Style=skia.Paint.kStroke_Style,
                                         StrokeWidth=3))
    F.shape([(-20, 820), (w * 0.3, 800), (w * 0.7, 830), (w + 20, 805), (w + 20, H + 20), (-20, H + 20)], "#F6E2A8")   # areia
    F.shape([(-20, 760), (120, 520), (330, 470), (520, 560), (600, 830), (-20, 840)], "#8E9BB5")                     # toca (pedra)
    F.oval(330, 720, 120, 110, "#3E4A66")
    F.oval(250, 560, 60, 30, "#A7B3CB")
    for x, h, col in ((820, 260, "#FF7FA8"), (1980, 300, "#FF9F45"), (2400, 220, "#B98CFF"), (1180, 180, "#FF7FA8")):    # corais
        F.line([(x, 830), (x, 830 - h)], col, w=LINE * 5)
        for d, hh in ((-1, 0.55), (1, 0.4), (-1, 0.25)):
            yb = 830 - h * hh
            F.line([(x, yb), (x + d * 70, yb - 60), (x + d * 80, yb - 120)], col, w=LINE * 4)
        for d in (-1, 1):
            F.oval(x + d * 80, 830 - h * 0.55 - 125, 20, 20, col)
        F.oval(x, 830 - h - 10, 22, 22, col)
    for x in range(120, w, 300):                                                                  # algas
        h = 200 + (x * 7) % 160
        F.shape([(x - 16, 840), (x - 40, 840 - h * 0.4), (x - 5, 840 - h * 0.7), (x - 30, 840 - h), (x + 20, 840 - h * 0.65),
                 (x + 30, 840 - h * 0.3), (x + 16, 840)], "#3DBE7A")
    for j in range(16):                                                                           # conchas e estrelas na areia
        x, y = (j * 211 + 90) % w, 880 + (j * 53) % 170
        if j % 2 == 0:
            pts = []
            for i in range(10):
                r = 24 if i % 2 == 0 else 10
                a = -math.pi / 2 + i * math.pi / 5
                pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
            F.shape(pts, "#FF8A5C" if j % 4 == 0 else "#FFC94A", smooth=False)
        else:
            F.oval(x, y, 16, 12, "#FFC1D6")
    return s, w


def praia(rng) -> tuple[skia.Surface, int]:
    """Praia de férias vista de pertinho: céu de verão, mar com ondinhas, areia dourada com conchinhas e estrelas-do-mar,
    guarda-sol listrado ao fundo (castelo, siri e onda são props)."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#9ED8FF"))))
    for x, y, sc in ((420, 150, 1.3), (1500, 110, 1.6), (2150, 210, 1.0)):
        F.cloud(x, y, sc)
    F.shape([(-20, 470), (w + 20, 470), (w + 20, 690), (-20, 690)], "#3FA2E6", smooth=False)
    for j in range(18):
        x, y = (j * 173) % w, 500 + (j * 41) % 160
        F.line([(x, y), (x + 40, y - 10), (x + 80, y)], "#BFE6FF", w=LINE)
    F.shape([(-20, 670), (w * 0.3, 650), (w * 0.6, 680), (w + 20, 660), (w + 20, 700), (-20, 700)], "#FFFFFF")      # espuma da beira
    F.shape([(-20, 690), (w + 20, 680), (w + 20, H + 20), (-20, H + 20)], "#F3D58A")
    for x0 in (2150,):                                                   # guarda-sol
        F.line([(x0, 760), (x0 + 30, 470)], "#8C6A2E", w=LINE * 1.6)
        cores = ("#E9545D", "#FFFFFF", "#3C8BF0", "#FFFFFF", "#E9545D")
        for i, col in enumerate(cores):
            a0, a1 = math.pi + i * math.pi / 5, math.pi + (i + 1) * math.pi / 5
            pts = [(x0 + 30, 470)] + [(x0 + 30 + math.cos(a0 + (a1 - a0) * t / 6) * 230, 520 + math.sin(a0 + (a1 - a0) * t / 6) * 90)
                                     for t in range(7)]
            F.shape(pts, col, smooth=False)
    for j in range(16):                                                   # conchinhas e estrelinhas
        x, y = (j * 211 + 70) % w, 780 + (j * 59) % 240
        if j % 3 == 0:
            F.oval(x, y, 14, 10, "#FFB3C7")
        elif j % 3 == 1:
            pts = []
            for i in range(10):
                r = 22 if i % 2 == 0 else 9
                a = -math.pi / 2 + i * math.pi / 5
                pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
            F.shape(pts, "#FF9A2E", smooth=False)
        else:
            F.line([(x - 10, y), (x + 10, y - 4)], "#E6C26E", w=LINE)
    return s, w


def salao(rng) -> tuple[skia.Surface, int]:
    """Salão de carnaval (Carnaval da Turminha): parede colorida com serpentinas e bandeirinhas, máscaras penduradas,
    chão de tábua com confete espalhado."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#7B5CFF"))))
    for x in range(0, w, 260):                                              # faixas na parede
        F.shape([(x, 0), (x + 130, 0), (x + 130, FLOOR_Y), (x, FLOOR_Y)], "#6A4BEA", smooth=False)
    cores = ("#FFD23F", "#FF7FBF", "#2DBE5A", "#3C8BF0", "#FF8A1F")
    for fila, y0 in enumerate((70, 190)):                                   # bandeirinhas
        pts = [(x, y0 + 40 * math.sin(x / 300 + fila)) for x in range(-20, w + 40, 40)]
        F.line(pts, "#FFFFFF", w=LINE)
        for i, (x, y) in enumerate(pts[::3]):
            F.shape([(x - 22, y), (x + 22, y), (x, y + 48)], cores[(i + fila) % len(cores)], smooth=False)
    for i in range(40):                                                     # serpentinas
        x, y = rng.uniform(0, w), rng.uniform(260, 620)
        pts = [(x + 14 * math.sin(j * 0.9), y + j * 14) for j in range(7)]
        F.line(pts, cores[i % len(cores)], w=LINE * 1.2)
    for x in (420, 1300, 2180):                                             # máscaras de carnaval
        F.oval(x, 360, 90, 50, "#FFD23F")
        F.oval(x - 36, 355, 20, 14, "#7B5CFF")
        F.oval(x + 36, 355, 20, 14, "#7B5CFF")
    _floor(F, w, "#E8B27A")
    for i in range(260):                                                    # confete no chão
        x, y = rng.uniform(0, w), rng.uniform(FLOOR_Y + 10, H)
        F.oval(x, y, 6, 4, cores[i % len(cores)], line=False, a=rng.uniform(0, 3))
    return s, w


def oficina(rng) -> tuple[skia.Surface, int]:
    """Oficina do Luisinho (Robô Dançarino): parede verde-água com quadro de ferramentas (chave, martelo, chave de fenda),
    engrenagens coloridas, bancada de madeira com caixa de peças, chão de tábua com parafusos."""
    w = W_INT
    s, c = _surf(w, H, 1.5)
    F = Flat(c)
    c.drawRect(skia.Rect(0, 0, w, H), skia.Paint(Color4f=skia.Color4f(*_rgba("#BFEBD9"))))
    for y in range(40, FLOOR_Y - 40, 120):                                  # azulejinhos da parede
        F.line([(0, y), (w, y)], "#AEE0CC", w=LINE * 0.8)
    for x0 in (260, 1560):                                                  # quadros de ferramentas (pegboard)
        F.shape([(x0, 150), (x0 + 520, 150), (x0 + 520, 470), (x0, 470)], "#E8B27A", smooth=False)
        for i in range(12):
            for j in range(6):
                F.oval(x0 + 30 + i * 42, 175 + j * 52, 5, 5, "#C98A4E", line=False)
        F.line([(x0 + 70, 200), (x0 + 70, 420)], "#3C8BF0", w=LINE * 2.4)    # chave de fenda
        F.oval(x0 + 70, 230, 22, 40, "#E9545D")
        F.line([(x0 + 200, 200), (x0 + 200, 430)], "#8C6A4A", w=LINE * 2.6)  # martelo
        F.shape([(x0 + 150, 190), (x0 + 250, 190), (x0 + 250, 235), (x0 + 150, 235)], "#7F8EA3", smooth=False)
        F.line([(x0 + 330, 210), (x0 + 330, 420)], "#7F8EA3", w=LINE * 2.4)  # chave inglesa
        F.oval(x0 + 330, 205, 32, 32, "#7F8EA3")
        F.oval(x0 + 330, 192, 14, 14, "#E8B27A", line=False)
        F.oval(x0 + 440, 300, 50, 50, "#FFD23F")                            # rolo de fita
        F.oval(x0 + 440, 300, 22, 22, "#E8B27A")
    cores = ("#FF8A1F", "#3C8BF0", "#FF7FBF", "#FFD23F")
    for i, (x, y, r) in enumerate(((1050, 230, 90), (1190, 340, 60), (2350, 260, 80), (110, 300, 70))):   # engrenagens
        pts = []
        for a in range(48):
            th = a * math.pi / 24
            rr = r * (1.0 if (a // 3) % 2 == 0 else 0.8)
            pts.append((x + rr * math.cos(th), y + rr * math.sin(th)))
        F.shape(pts, cores[i % len(cores)], smooth=False)
        F.oval(x, y, r * 0.3, r * 0.3, "#BFEBD9")
    _floor(F, w, "#D9A066")
    bx = 1880                                                               # bancada com caixa de peças
    F.shape([(bx, 600), (bx + 640, 600), (bx + 640, 650), (bx, 650)], "#B97A2E", smooth=False)
    for xx in (bx + 30, bx + 580):
        F.shape([(xx, 650), (xx + 30, 650), (xx + 30, FLOOR_Y + 10), (xx, FLOOR_Y + 10)], "#B97A2E", smooth=False)
    F.shape([(bx + 380, 520), (bx + 560, 520), (bx + 560, 600), (bx + 380, 600)], "#E9545D", smooth=False)
    F.shape([(bx + 80, 560), (bx + 160, 560), (bx + 160, 600), (bx + 80, 600)], "#3C8BF0", smooth=False)
    for i in range(70):                                                     # parafusos e porquinhas no chão
        x, y = rng.uniform(0, w), rng.uniform(FLOOR_Y + 20, H)
        F.oval(x, y, 7, 7, ("#7F8EA3", "#FFD23F")[i % 2], line=False)
    return s, w


SCENES = {"plano_banheiro": banheiro, "plano_quarto_rosa": lambda rng: quarto("rosa", rng), "plano_quarto_azul": lambda rng: quarto("azul", rng),
          "plano_cozinha": cozinha, "plano_casa_frente": casa_frente, "plano_escola": escola, "plano_ceu": ceu,
          "plano_jardim": jardim, "plano_lagoa": lagoa, "plano_sala": sala, "plano_espaco": espaco, "plano_lua": lua_chao, "plano_campo": campo, "plano_gelo": gelo, "plano_mar_gelado": mar_gelado, "plano_praia": praia, "plano_fundo_mar": fundo_mar, "plano_salao": salao, "plano_oficina": oficina}


def build(bg_id: str, out_dir: Path, scale: float = 1.5, seed: int = 11) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    if bg_id.startswith("padrao_"):
        _, kind, color = bg_id.split("_", 2)
        s, w, h, per = padrao(kind, color, 1.0)
        s.makeImageSnapshot().save(str(out_dir / "BG_padrao.png"), skia.kPNG)
        from .dance import W as DW, H as DH
        meta = {"id": bg_id, "name": f"Padrão — {kind} {color}", "width": DW, "height": DH, "scale": 1.0, "landmarks": {},
                "graphic": True, "layers": [{"name": "BG_padrao", "file": "BG_padrao.png", "parallax": 0.0, "z": -50, "width": w,
                                             "height": h, "fixed": True, "scroll": [40.0, 25.0, per, per]}]}
    else:
        rng = np.random.default_rng(seed)
        s, w = SCENES[bg_id](rng)
        s.makeImageSnapshot().save(str(out_dir / "MG_cena.png"), skia.kPNG)
        meta = {"id": bg_id, "name": bg_id.replace("plano_", "Plano — ").replace("_", " "), "width": w, "height": H, "scale": scale,
                "landmarks": {"ground_y": 930, "floor_y": FLOOR_Y}, "estilo": "canais/laurinha/BIBLIA_VISUAL.md",
                "layers": [{"name": "MG_cena", "file": "MG_cena.png", "parallax": 1.0, "z": -20, "width": w, "height": H}]}
    (out_dir / "background.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta
