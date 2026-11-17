"""Objetos de cena no estilo oficial (BIBLIA_VISUAL.md): chapados, contorno = cor da peça escurecida, linha uniforme.

Dois tipos:
- **objetos de mão** (`draw_item`): desenhados na mão do personagem pelo canal `holding` (copo de leite, banana, pente…);
- **objetos de cena** (classes `Character`): entram no episódio como `props` com canais próprios animáveis
  (a janela abre, o lençol se arruma, o sol pisca e acena…).
Unidades iguais às dos personagens (Laurinha ≈ 470 de altura). Origem = base do objeto, no chão/apoio.
"""
from __future__ import annotations

import math

import numpy as np
import skia

from ..drawing.ink import Brush, Ink, ellipse_pts
from .base import Character, lerp, rot
from .flat_muri import LINE, _rgba, dark

PAL = {"leite": "#FFFFFF", "vidro": "#CFE8FA", "banana": "#FFD84A", "banana_ponta": "#7A5A2E", "pente": "#F0509A",
       "garrafa": "#36C2A8", "tampa": "#FF8A1F", "carro": "#E9545D", "roda": "#4A4A55", "escova": "#3E7BD6",
       "madeira": "#C98A4E", "folha_janela": "#F7A8D8", "moldura": "#FFFFFF", "ceu": "#87B8F6", "luz": "#FFF3B0",
       "colchao": "#FFFFFF", "travesseiro": "#FFF6D6", "lencol": "#FFB3D9", "lencol2": "#FF8CC6", "mesa": "#E9545D",
       "toalha": "#FFFFFF", "espelho": "#CFE8FA", "caixa": "#FFC21A", "bola": "#3E7BD6", "sol": "#FFD23F",
       "sol_raio": "#FFB23F", "bochecha": "#FF9A7A"}
SOMBRINHA = ["#E9545D", "#FFD23F", "#2DB34A", "#3C8BF0", "#B865E6", "#FF8A1F"]


def shape(k: Ink, pts, fill: str, line: str | None = None, alpha: float = 1.0, w: float = LINE, smooth: bool = True):
    br = Brush(width=w, vary=0.0, ink=_rgba(line or dark(fill)), jitter=0.0)
    if not smooth:                       # polígono reto: amostra as arestas (cantos vivos, contorno uniforme)
        dense = []
        n = len(pts)
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            steps = max(2, int(math.hypot(bx - ax, by - ay) / 10))
            dense += [(ax + (bx - ax) * j / steps, ay + (by - ay) * j / steps) for j in range(steps)]
        return k.shape(dense, fill=_rgba(fill, alpha), brush=br, dense=True, line=w)
    return k.shape(pts, fill=_rgba(fill, alpha), brush=br, smooth=smooth, line=w)


def box(k: Ink, x0, y0, x1, y1, fill, line=None, r=10.0):
    """Retângulo de cantos levemente arredondados (amostrado: contorno uniforme sem defeito)."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(5):
            a = math.radians(a0 + i * 22.5)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return shape(k, pts, fill, line, smooth=False)


def ln(k: Ink, pts, col: str, w: float = LINE, alpha: float = 1.0):
    k.stroke(pts, w, taper=(0.0, 0.0), color_=_rgba(col, alpha))


# ───────────────────────── objetos de mão ─────────────────────────

ITEMS = ("copo_leite", "copo_vazio", "banana", "banana_mordida", "pente", "garrafinha", "carrinho", "sombrinha", "escova",
         "suco", "fatia_bolo", "fatia_grande", "escova_pasta", "escova_guitarra")


ITEM_SCALE = 1.6


def draw_item(k: Ink, name: str, H: tuple[float, float], f: float = 1.0) -> None:
    """Desenha o objeto SEGURO na mão H. Coordenadas do desenho relativas à mão, ampliadas por ITEM_SCALE
    (a espessura do contorno NÃO muda: linha uniforme da bíblia)."""
    S = ITEM_SCALE
    hx, hy = H

    def q(px, py):
        return (hx + px * f * S, hy + py * S)

    def Q(pts):
        return [q(*p) for p in pts]

    if name in ("copo_leite", "copo_vazio"):
        shape(k, Q([(-24, -64), (24, -64), (18, 18), (-18, 18)]), PAL["vidro"], line="#7FB6DB", alpha=0.9, smooth=False)
        if name == "copo_leite":
            shape(k, Q([(-21, -48), (21, -48), (17, 14), (-17, 14)]), PAL["leite"], line="#C9D6E0", smooth=False)
        ln(k, Q([(-12, -54), (-9, 6)]), "#FFFFFF", w=LINE * 0.8)
    elif name in ("banana", "banana_mordida"):
        _banana(k, Q, q, name == "banana_mordida")
    elif name == "pente":
        box(k, *q(-10, -70), *q(10, 10), PAL["pente"], r=6) if f > 0 else box(k, *q(10, -70), *q(-10, 10), PAL["pente"], r=6)
        for j in range(6):
            yy = -62 + j * 12
            ln(k, Q([(10, yy), (26, yy)]), PAL["pente"], w=LINE * 0.9)
    elif name == "garrafinha":
        x0, y0 = q(-20 * f, -76)
        x1, y1 = q(20 * f, 22)
        box(k, min(x0, x1), y0, max(x0, x1), y1, PAL["garrafa"], r=12)
        a0, b0 = q(-13 * f, -96)
        a1, b1 = q(13 * f, -74)
        box(k, min(a0, a1), b0, max(a0, a1), b1, PAL["tampa"], r=6)
        ln(k, Q([(-20, -30), (20, -30)]), "#FFFFFF", w=LINE * 1.4)
    elif name == "carrinho":
        shape(k, Q([(-46, 4), (-46, -18), (-22, -22), (-12, -42), (20, -42), (32, -22), (46, -18), (46, 4)]), PAL["carro"], smooth=False)
        shape(k, Q([(-6, -38), (16, -38), (24, -24), (-10, -24)]), PAL["ceu"], smooth=False)
        for wx in (-26, 26):
            c = q(wx, 6)
            shape(k, ellipse_pts(c[0], c[1], 12 * S, 12 * S, 0, 14), PAL["roda"])
            k.dot(c[0], c[1], 4 * S, _rgba("#FFFFFF"))
    elif name in ("escova", "escova_pasta"):
        # deitada, apontando para TRÁS do punho (para a boca quando a mão está ao lado do rosto); cerdas para cima
        shape(k, Q([(22, -6), (-38, -6), (-38, 6), (22, 6)]), PAL["escova"], smooth=False)
        shape(k, Q([(-40, -6), (-64, -6), (-64, -24), (-40, -24)]), "#FFFFFF", line="#B8C4D0", smooth=False)
        if name == "escova_pasta":                          # pasta do tamanho de um grão de feijão em cima das cerdas
            shape(k, Q([(-62, -24), (-57, -34), (-47, -34), (-42, -24)]), "#7FD3F7", line="#3E9FD6")
    elif name == "escova_guitarra":                         # escova gigante segurada como guitarra (cabo na diagonal)
        def g(px, py):
            a = -0.62                                       # cabo sobe para a frente
            return q(px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a))
        shape(k, [g(-40, -12), g(150, -12), g(150, 12), g(-40, 12)], PAL["escova"], smooth=False)
        shape(k, [g(150, -16), g(196, -16), g(196, 10), g(150, 10)], "#FFFFFF", line="#B8C4D0", smooth=False)
        for j in range(4):                                  # "cordas" (listrinhas brancas no cabo)
            ln(k, [g(-30 + j * 8, -3), g(140, -3 + j * 2)], "#FFFFFF", w=LINE * 0.45)
        shape(k, ellipse_pts(*g(-30, 0), 26 * S, 22 * S, -0.62, 18), "#FF8A1F")     # corpo da "guitarra" (adesivo de estrela)
        _estrela(k, *g(-30, 0), 16 * S, "#FFD23F")
    elif name == "suco":                                   # copinho de suco de uva com canudinho
        shape(k, Q([(-22, -60), (22, -60), (17, 16), (-17, 16)]), PAL["vidro"], line="#7FB6DB", alpha=0.9, smooth=False)
        shape(k, Q([(-19, -40), (19, -40), (16, 12), (-16, 12)]), "#9B4FD1", line="#7A3AAE", smooth=False)
        ln(k, Q([(8, -40), (14, -84), (26, -92)]), "#FF5A8A", w=LINE * 1.2)
    elif name in ("fatia_bolo", "fatia_grande"):           # fatia de bolo vista de lado: base reta, topo inclinado com casquinha
        g = 1.45 if name == "fatia_grande" else 1.0
        shape(k, Q([(-40 * g, 6), (40 * g, 6), (40 * g, -54 * g), (-40 * g, -26 * g)]), "#F7C948", line="#C99A2A", smooth=False)
        shape(k, Q([(-40 * g, -26 * g), (40 * g, -54 * g), (40 * g, -64 * g), (-40 * g, -36 * g)]), "#D9902E", line="#B5741F", smooth=False)
        for dx, dy in ((-20, -10), (6, -24), (22, -12), (-4, -4)):
            k.dot(*q(dx * g, dy * g), 3, _rgba("#E0A93A"))
    elif name == "sombrinha":
        ln(k, Q([(0, 20), (0, -110)]), "#534946", w=LINE * 1.1)
        cx, cy = q(0, -110)
        R = 70 * S
        n = len(SOMBRINHA)
        for j in range(n):
            a0, a1 = math.pi + j * math.pi / n, math.pi + (j + 1) * math.pi / n
            pts = [(cx, cy)] + [(cx + R * math.cos(a0 + (a1 - a0) * u / 6), cy + R * 0.62 * math.sin(a0 + (a1 - a0) * u / 6))
                                for u in range(7)]
            shape(k, pts, SOMBRINHA[j], smooth=False)
        k.dot(cx, cy - R * 0.62, 7, _rgba("#534946"))


def _banana_lado(u0, u1, n, w0=22.0, comp=118.0, curva=30.0, k_w=1.0):
    """Contorno de uma banana entre as frações u0..u1 do comprimento: linha central curva + largura que afina nas pontas."""
    import math as _m
    esq, dir_ = [], []
    for i in range(n + 1):
        u = u0 + (u1 - u0) * i / n
        cx, cy = curva * _m.sin(_m.pi * u), -comp * u
        dx, dy = curva * _m.pi * _m.cos(_m.pi * u), -comp
        L = _m.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        w = (w0 * max(0.0, _m.sin(_m.pi * u)) ** 0.6 + 3) * k_w
        esq.append((cx + nx * w, cy + ny * w))
        dir_.append((cx - nx * w, cy - ny * w))
    return esq, dir_


def _banana(k: Ink, Q, q, descascada: bool) -> None:
    """Banana clássica de desenho: comprida, curvada, cabinho embaixo (na mão) e pontinha marrom em cima.
    Mordida = descascada: fruta creme com mordida + 3 cascas caindo para os lados."""
    if not descascada:
        esq, dir_ = _banana_lado(0.0, 1.0, 20, w0=17)
        shape(k, Q(esq + dir_[::-1]), PAL["banana"], line="#D8A21E")
        c_esq, c_dir = _banana_lado(0.12, 0.9, 14, k_w=0.0)
        ln(k, Q([((a[0] + b[0]) / 2 + 6, (a[1] + b[1]) / 2) for a, b in zip(c_esq, c_dir)]), "#E8B92E", w=LINE * 0.8)
        shape(k, Q([(-5, 2), (5, 2), (4, 18), (-4, 18)]), PAL["banana_ponta"], smooth=False)       # cabinho
        tip = q(*_banana_lado(1.0, 1.0, 1)[0][0])
        k.dot(tip[0], tip[1], 5, _rgba(PAL["banana_ponta"]))
        return
    # fruta (creme) com mordida no alto
    esq, dir_ = _banana_lado(0.3, 0.86, 12, k_w=0.72)
    fruta = esq + dir_[::-1]
    shape(k, Q(fruta), "#FFF3C4", line="#E2C77A")
    topo = ((esq[-1][0] + dir_[-1][0]) / 2, (esq[-1][1] + dir_[-1][1]) / 2)
    for dx in (-7, 7):                                                     # topo arredondado da mordida
        k.dot(*q(topo[0] + dx, topo[1] + 2), 9 * ITEM_SCALE, _rgba("#FFF3C4"))
    ln(k, Q([(topo[0] - 14, topo[1] + 6), (topo[0] - 7, topo[1] - 2), (topo[0], topo[1] + 6), (topo[0] + 7, topo[1] - 2),
             (topo[0] + 14, topo[1] + 6)]), "#E2C77A", w=LINE * 0.8)
    # casca de baixo + 3 abas caindo
    esq, dir_ = _banana_lado(0.0, 0.42, 8)
    shape(k, Q(esq + dir_[::-1]), PAL["banana"], line="#D8A21E")
    base_y = esq[-1][1]
    cx = (esq[-1][0] + dir_[-1][0]) / 2
    for lado, ang in ((-1, 0.9), (0, 0.0), (1, 0.9)):
        if lado == 0:
            pts = [(cx - 8, base_y + 2), (cx + 8, base_y + 2), (cx + 6, base_y - 30), (cx, base_y - 40), (cx - 6, base_y - 30)]
        else:
            pts = [(cx + lado * 6, base_y + 2), (cx + lado * 20, base_y - 4), (cx + lado * 40, base_y + 22),
                   (cx + lado * 44, base_y + 40), (cx + lado * 30, base_y + 30), (cx + lado * 14, base_y + 12)]
        shape(k, Q(pts), PAL["banana"], line="#D8A21E")
    shape(k, Q([(-5, 2), (5, 2), (4, 18), (-4, 18)]), PAL["banana_ponta"], smooth=False)


# ───────────────────────── objetos de cena ─────────────────────────

class _Prop(Character):
    def __init__(self, cid, name, canvas, anchor, height, defaults):
        super().__init__(id=cid, name=name, canvas=canvas, anchor=anchor, height=height,
                         defaults={"turn": 0.0, "hidden": 0.0, **defaults})

    def draw(self, ink: Ink, P: dict) -> None:
        if P.get("hidden", 0) > 0.5:
            return
        self.paint(ink, P)


class Janela(_Prop):
    """Janela de parede com duas folhas que ABREM (canal `abre` 0→1) e faixa de luz entrando."""

    def __init__(self):
        super().__init__("janela", "Janela", (900, 560), (450, 520), 400, {"abre": 0.0, "luz": 0.0, "noite": 0.0})

    def paint(self, k, P):
        W2, Hh = 170, 340
        shape(k, [(-W2 - 22, 22), (W2 + 22, 22), (W2 + 22, -Hh - 22), (-W2 - 22, -Hh - 22)], PAL["moldura"], line="#C9D6E0", smooth=False)
        noite = P.get("noite", 0.0) > 0.5
        shape(k, [(-W2, 0), (W2, 0), (W2, -Hh), (-W2, -Hh)], "#2B3A78" if noite else PAL["ceu"], smooth=False)
        if noite:                                                  # céu de noite: lua e estrelinhas
            shape(k, ellipse_pts(60, -240, 56, 56, 0, 28), "#FFF3B0", line="#E0C860")
            shape(k, ellipse_pts(84, -258, 48, 48, 0, 28), "#2B3A78", line="#2B3A78")
            for sx, sy, r in ((-100, -280, 12), (-40, -120, 9), (110, -90, 10), (-120, -60, 8)):
                _estrela(k, sx, sy, r, "#FFF3B0")
        for cx, cy, s in (() if noite else ((-70, -250, 0.9), (80, -150, 0.7))):      # nuvens vistas pela janela
            p = skia.Path()
            for dx, dy, r in ((-40, 6, 28), (-10, -10, 36), (24, -4, 32), (46, 8, 24)):
                p.addCircle(cx + dx * s, cy + dy * s, r * s)
            k.c.drawPath(p, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(1, 1, 1, 1)))
        a = max(0.0, min(1.0, P["abre"]))
        th = a * math.pi * 0.92
        for side in (-1, 1):                                       # folhas: giram nas dobradiças das laterais
            hx = side * W2
            far = hx - side * W2 * math.cos(th)
            dh = 18 * math.sin(th)
            pts = [(hx, 0), (hx, -Hh), (far, -Hh - dh * (1 if side > 0 else 1)), (far, dh)]
            shape(k, pts, P.get("cor", PAL["folha_janela"]), smooth=False)
            mx = (hx + far) / 2
            if abs(far - hx) > 30:
                ln(k, [(mx, -Hh * 0.2), (mx, -Hh * 0.8)], dark(PAL["folha_janela"]), w=LINE * 0.8)
        box(k, -W2 - 40, 8, W2 + 40, 32, PAL["moldura"], line="#C9D6E0", r=8)       # peitoril
        luz = max(0.0, min(1.0, P["luz"]))
        if luz > 0.02:
            k.shape([(-W2, 0), (W2, 0), (W2 + 220, 420), (-W2 + 60, 420)], fill=_rgba(PAL["luz"], 0.35 * luz), line=0)


class Cama(_Prop):
    """Cama vista de frente: cabeceira, colchão e travesseiro (fica ATRÁS do personagem; o lençol vem na frente)."""

    def __init__(self):
        super().__init__("cama", "Cama", (900, 560), (450, 520), 420, {})

    def paint(self, k, P):
        cor = P.get("cor", PAL["madeira"])
        shape(k, [(-300, 0), (-300, -330), (-220, -400), (220, -400), (300, -330), (300, 0)], cor)
        box(k, -320, -150, 320, -40, PAL["colchao"], line="#C9D6E0", r=24)
        box(k, -200, -230, 40, -140, PAL["travesseiro"], line="#E2D3A6", r=40)
        for x in (-280, 280):
            box(k, x - 18, -40, x + 18, 0, cor, r=6)


class Lencol(_Prop):
    """Lençol na frente do personagem deitado/sentado. `arrumado` 0 = amarrotado → 1 = esticado."""

    def __init__(self):
        super().__init__("lencol", "Lençol", (900, 400), (450, 360), 200, {"arrumado": 1.0})

    def paint(self, k, P):
        a = max(0.0, min(1.0, P["arrumado"]))
        top = []
        for i in range(17):
            u = i / 16
            x = -330 + 660 * u
            onda = (1 - a) * 26 * math.sin(u * math.pi * 5.0) + (1 - a) * 18 * math.sin(u * math.pi * 2.3 + 1)
            top.append((x, -190 + onda))
        pts = top + [(340, -40), (300, 0), (-300, 0), (-340, -40)]
        shape(k, pts, P.get("cor", PAL["lencol"]))
        for j in range(3):                                         # listras do lençol
            y = -140 + j * 46
            ln(k, [(-300, y + (1 - a) * 10 * math.sin(j)), (300, y - (1 - a) * 10 * math.sin(j + 1))], PAL["lencol2"], w=LINE * 1.6)
        ln(k, [(-320, -170 + (1 - a) * 10), (320, -170 - (1 - a) * 6)], "#FFFFFF", w=LINE * 2.4)    # dobra branca


class Mesa(_Prop):
    """Mesa com toalha (fica NA FRENTE do personagem; esconde as pernas)."""

    def __init__(self):
        super().__init__("mesa", "Mesa", (900, 360), (450, 330), 260, {})

    def paint(self, k, P):
        cor = P.get("cor", PAL["mesa"])
        for x in (-250, 250):
            box(k, x - 16, -200, x + 16, 0, PAL["madeira"], r=6)
        box(k, -320, -240, 320, -190, PAL["toalha"], line="#C9D6E0", r=10)
        shape(k, [(-320, -200), (320, -200), (300, -110), (-300, -110)], cor, smooth=False)
        for x in range(-280, 300, 70):                             # barrado da toalha
            k.dot(x, -150, 9, _rgba("#FFFFFF"))


class Espelho(_Prop):
    def __init__(self):
        super().__init__("espelho", "Espelho", (500, 640), (250, 600), 520, {"brilho": 0.0})

    def paint(self, k, P):
        shape(k, ellipse_pts(0, -300, 170, 230, 0, 32), P.get("cor", "#FFD23F"))
        shape(k, ellipse_pts(0, -300, 140, 200, 0, 32), PAL["espelho"], line="#7FB6DB")
        ln(k, [(-70, -400), (-30, -440)], "#FFFFFF", w=LINE * 1.6)
        ln(k, [(-90, -350), (-30, -410)], "#FFFFFF", w=LINE * 1.6)
        if P["brilho"] > 0.05:
            _estrela(k, 90, -420, 30 * P["brilho"], "#FFFFFF")


class CaixaBrinquedos(_Prop):
    """Caixa de brinquedos; `carrinho` 1 = o carrinho aparece guardado lá dentro."""

    def __init__(self):
        super().__init__("caixa_brinquedos", "Caixa de brinquedos", (600, 400), (300, 360), 220, {"carrinho": 0.0})

    def paint(self, k, P):
        shape(k, ellipse_pts(-80, -210, 54, 54, 0, 24), PAL["bola"])
        ln(k, [(-130, -210), (-30, -210)], "#FFFFFF", w=LINE * 1.4)
        if P["carrinho"] > 0.5:
            draw_item(k, "carrinho", (70, -200))
        box(k, -200, -190, 200, 0, PAL["caixa"], r=14)
        box(k, -214, -206, 214, -170, dark(PAL["caixa"], 0.92), r=10)
        _estrela(k, 0, -90, 44, "#FFFFFF")


class Sol(_Prop):
    """Sol com carinha (personagem-objeto): raios giram (`giro`), pisca (`lid`), acena com a mãozinha (`aceno`)."""

    def __init__(self):
        super().__init__("sol", "Sol", (760, 760), (380, 720), 600,
                         {"giro": 0.0, "aceno": 0.0, "boca": 0.0, "lid": 0.0})

    def paint(self, k, P):
        cx, cy, R = 0, -340, 190
        g = P["giro"]
        for j in range(12):
            a = g + j * math.pi / 6
            b1, b2 = a - 0.16, a + 0.16
            pts = [(cx + R * 1.08 * math.cos(b1), cy + R * 1.08 * math.sin(b1)), (cx + R * 1.55 * math.cos(a), cy + R * 1.55 * math.sin(a)),
                   (cx + R * 1.08 * math.cos(b2), cy + R * 1.08 * math.sin(b2))]
            shape(k, pts, PAL["sol_raio"], smooth=False)
        shape(k, ellipse_pts(cx, cy, R, R, 0, 40), PAL["sol"])
        for s in (-1, 1):                                          # bochechas
            k.shape(ellipse_pts(cx + s * 110, cy + 40, 32, 26, 0, 16), fill=_rgba(PAL["bochecha"], 0.8), line=0)
        lid = P["lid"]
        for s in (-1, 1):                                          # olhos
            ex, ey = cx + s * 62, cy - 30
            if lid > 0.5:
                ln(k, [(ex - 22, ey), (ex, ey - 14), (ex + 22, ey)], "#5C3A10", w=LINE * 1.2)
            else:
                shape(k, ellipse_pts(ex, ey, 24, 30, 0, 18), "#FFFFFF", line="#5C3A10")
                k.dot(ex + 4, ey + 6, 10, _rgba("#000000"))
        b = P["boca"]
        if b < 0.15:
            ln(k, [(cx - 50, cy + 50), (cx, cy + 82), (cx + 50, cy + 50)], "#5C3A10", w=LINE * 1.3)
        else:
            shape(k, [(cx - 54, cy + 48), (cx + 54, cy + 48), (cx + 30, cy + 48 + 60 * b), (cx - 30, cy + 48 + 60 * b)],
                  "#8A2E2E", line="#5C3A10")
        ac = P["aceno"]
        if ac > 0.01:                                              # mãozinha acenando ao lado
            sh = (cx + R * 0.95, cy + 30)
            ang = -0.6 - 0.5 * math.sin(ac * math.pi * 4)
            hand = (sh[0] + 120 * math.cos(ang), sh[1] + 120 * math.sin(ang))
            ln(k, [sh, hand], "#D9A11E", w=LINE * 2.2)
            for d in (-0.6, 0.0, 0.6):
                ln(k, [hand, (hand[0] + 22 * math.cos(ang + d), hand[1] + 22 * math.sin(ang + d))], "#D9A11E", w=LINE * 1.6)


def _estrela(k: Ink, x, y, r, col):
    pts = [(x + math.cos(-math.pi / 2 + j * math.pi / 5) * (r if j % 2 == 0 else r * 0.45),
            y + math.sin(-math.pi / 2 + j * math.pi / 5) * (r if j % 2 == 0 else r * 0.45)) for j in range(10)]
    shape(k, pts, col, line=dark("#FFD23F"), smooth=False)


PROPS = {"janela": Janela, "cama": Cama, "lencol": Lencol, "mesa": Mesa, "espelho": Espelho,
         "caixa_brinquedos": CaixaBrinquedos, "sol": Sol}


# ───────────────────────── marca: logo, botão de inscrição, joinha ─────────────────────────

def _texto(k: Ink, txt: str, x: float, y: float, size: float, cor, contorno=(1, 1, 1, 1), borda: float = 0.16):
    from ..core.config import LIBRARY
    tf = skia.Typeface.MakeFromFile(str(LIBRARY / "fonts" / "Poppins-ExtraBold.ttf"))
    font = skia.Font(tf, size)
    w = font.measureText(txt)
    blob = skia.TextBlob.MakeFromString(txt, font)
    k.c.drawTextBlob(blob, x - w / 2, y, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*contorno), Style=skia.Paint.kStroke_Style,
                                                    StrokeWidth=size * borda, StrokeJoin=skia.Paint.kRound_Join))
    k.c.drawTextBlob(blob, x - w / 2, y, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*cor)))


class Logo(_Prop):
    """Selo do canal em tamanho de vinheta (mesmo desenho do logo do canto): nuvem amarela, borda vermelha,
    LAURINHA (rosa) e 'e Luisinho' (azul). Canais: `escala` (entra pulando), `giro` (balanço leve)."""

    def __init__(self):
        super().__init__("logo", "Logo do canal", (1300, 700), (650, 640), 520, {"escala": 1.0, "giro": 0.0})

    def paint(self, k, P):
        s = max(0.0, P["escala"])
        if s < 0.02:
            return
        k.c.save()
        k.c.translate(0, -300)
        k.c.rotate(math.degrees(P["giro"]))
        k.c.scale(s, s)
        W, H = 1000.0, 380.0
        path = skia.Path()
        r = H * 0.42
        path.addRRect(skia.RRect.MakeRectXY(skia.Rect(-W / 2, -H / 2 + 10, W / 2, H / 2 - 8), r, r))
        for fx, fy, rr in ((-0.32, -0.30, 0.22), (-0.05, -0.38, 0.26), (0.25, -0.30, 0.22)):
            path.addCircle(W * fx, H * fy + 10, H * rr)
        path.setFillType(skia.PathFillType.kWinding)
        k.c.drawPath(path, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#E0342E")), Style=skia.Paint.kStroke_Style,
                                      StrokeWidth=30, StrokeJoin=skia.Paint.kRound_Join))
        k.c.drawPath(path, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba("#FFD640"))))
        _texto(k, "LAURINHA", 0, H * 0.10, H * 0.40, _rgba("#E83E78"))
        _texto(k, "e Luisinho", 0, H * 0.36, H * 0.25, _rgba("#2E70D2"))
        k.c.restore()


class BotaoInscrever(_Prop):
    """Botão vermelho 'INSCREVA-SE' (canal infantil: sem sininho). `aperta` 0→1 afunda o botão (clique)."""

    def __init__(self):
        super().__init__("botao_inscrever", "Botão inscreva-se", (900, 340), (450, 300), 220, {"aperta": 0.0, "escala": 1.0})

    def paint(self, k, P):
        s = max(0.0, P["escala"]) * (1 - 0.08 * P["aperta"])
        if s < 0.02:
            return
        k.c.save()
        k.c.translate(0, -120)
        k.c.scale(s, s)
        pressed = P["aperta"] > 0.5
        cor = "#9E9E9E" if pressed else "#E0342E"
        box(k, -330, -90, 330, 90, cor, line=dark(cor, 0.75), r=60)
        if pressed:                          # a fonte não tem "✓": o visto é desenhado
            _texto(k, "INSCRITO", -40, 32, 92, _rgba("#FFFFFF"), contorno=_rgba(dark(cor, 0.7)), borda=0.12)
            ln(k, [(215, -4), (240, 26), (285, -34)], "#FFFFFF", w=LINE * 3)
        else:
            _texto(k, "INSCREVA-SE", 0, 32, 92, _rgba("#FFFFFF"), contorno=_rgba(dark(cor, 0.7)), borda=0.12)
        k.c.restore()


class Joinha(_Prop):
    """Joinha (polegar para cima) dentro de um círculo azul. `escala` faz ele 'pular' na tela."""

    def __init__(self):
        super().__init__("joinha", "Joinha", (420, 420), (210, 400), 360, {"escala": 1.0})

    def paint(self, k, P):
        s = max(0.0, P["escala"])
        if s < 0.02:
            return
        k.c.save()
        k.c.translate(0, -180)
        k.c.scale(s, s)
        shape(k, ellipse_pts(0, 0, 160, 160, 0, 40), "#3C8BF0")
        box(k, -70, -10, 40, 90, "#FFFFFF", line="#C9D6E0", r=24)                     # mão
        box(k, -100, -6, -66, 92, "#FFFFFF", line="#C9D6E0", r=12)                    # punho
        shape(k, [(-30, -10), (-36, -88), (-14, -100), (6, -84), (10, -10)], "#FFFFFF", line="#C9D6E0")   # polegar
        for y in (16, 42, 68):
            ln(k, [(-10, y), (36, y)], "#C9D6E0", w=LINE * 0.8)
        k.c.restore()


class Sabonete(_Prop):
    """Sabonete com carinha (objeto-personagem): `pulo` 0→1 faz ele saltar; `bolhas` solta bolhinhas."""

    def __init__(self):
        super().__init__("sabonete", "Sabonete", (420, 420), (210, 380), 200, {"pulo": 0.0, "bolhas": 0.0, "lid": 0.0})

    def paint(self, k, P):
        y0 = -60 - 120 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        box(k, -90, y0 - 70, 90, y0 + 50, "#FF9EC7", line="#E0679F", r=46)
        ln(k, [(-56, y0 - 46), (-20, y0 - 56)], "#FFFFFF", w=LINE * 1.6)
        for s in (-1, 1):
            ex, ey = s * 32, y0 - 12
            if P["lid"] > 0.5:
                ln(k, [(ex - 14, ey), (ex, ey - 9), (ex + 14, ey)], "#5C1E2E", w=LINE)
            else:
                shape(k, ellipse_pts(ex, ey, 14, 18, 0, 14), "#FFFFFF", line="#C2557F")
                k.dot(ex + 2, ey + 4, 6, _rgba("#000000"))
        ln(k, [(-20, y0 + 18), (0, y0 + 30), (20, y0 + 18)], "#5C1E2E", w=LINE * 1.1)
        k.shape(ellipse_pts(-58, y0 + 10, 14, 10, 0, 12), fill=_rgba("#FF6FA8", 0.7), line=0)
        k.shape(ellipse_pts(58, y0 + 10, 14, 10, 0, 12), fill=_rgba("#FF6FA8", 0.7), line=0)
        b = P["bolhas"]
        for j, (bx, by, r) in enumerate(((-110, -120, 26), (100, -150, 20), (-40, -190, 16), (60, -230, 24), (-120, -260, 14))):
            if b > j * 0.15:
                yy = by - 60 * b
                shape(k, ellipse_pts(bx, y0 + yy, r, r, 0, 18), "#E8F6FF", line="#9CCBFA", alpha=0.8)
                ln(k, [(bx - r * 0.4, y0 + yy - r * 0.4), (bx - r * 0.1, y0 + yy - r * 0.6)], "#FFFFFF", w=LINE * 0.8)


class Bolo(_Prop):
    """Bolo de fubá (tipo pudim, com furo) num prato. `fatias` 0→1 tira um pedaço; `vapor` mostra o calorzinho."""

    def __init__(self):
        super().__init__("bolo", "Bolo de fubá", (620, 520), (310, 480), 300, {"fatias": 0.0, "vapor": 1.0})

    def paint(self, k, P):
        shape(k, ellipse_pts(0, -10, 250, 40, 0, 32), "#FFFFFF", line="#C9D6E0")
        shape(k, [(-190, -30), (190, -30), (160, -200), (-160, -200)], "#F7C948", line="#C99A2A", smooth=False)
        shape(k, ellipse_pts(0, -200, 160, 36, 0, 32), "#E9A93A", line="#C99A2A")
        shape(k, ellipse_pts(0, -200, 40, 10, 0, 20), "#B5741F", line="#8E5A18")
        for x in (-120, -40, 40, 120):
            ln(k, [(x, -60), (x * 0.86, -180)], "#E0A93A", w=LINE * 0.8)
        if P["fatias"] > 0.5:                                   # pedaço tirado (frente direita)
            shape(k, [(60, -32), (150, -32), (140, -196), (50, -200)], "#FFF4C9", line="#C99A2A", smooth=False)
        if P["vapor"] > 0.05:
            for x in (-60, 0, 60):
                pts = [(x + 14 * math.sin(i / 2.0), -250 - i * 14) for i in range(8)]
                ln(k, pts, "#FFFFFF", w=LINE * 1.2, alpha=0.8 * P["vapor"])


class MochilaChao(_Prop):
    """Mochila largada no chão (rosa da Laurinha; `azul` 1 = a azul do Luisinho). `cai` 0→1 = caindo até o chão (ploft).
    `cor` 0 = cinza → 1 a cor acende (Cadê a Cor?)."""

    def __init__(self):
        super().__init__("mochila", "Mochila", (360, 360), (180, 330), 180, {"cai": 1.0, "azul": 0.0, "cor": 1.0})

    def paint(self, k, P):
        dy = -220 * (1 - max(0.0, min(1.0, P["cai"])))
        az = P.get("azul", 0) > 0.5
        c1, c2, c3 = ("#2F86F0", "#6FB2FF", "#1F5FB8") if az else ("#F0509A", "#FF7FBF", "#C2357A")
        c1, c2, c3 = (_mix(CINZA, c, P.get("cor", 1.0)) for c in (c1, c2, c3))
        box(k, -80, dy - 150, 80, dy, c1, r=30)
        box(k, -54, dy - 70, 54, dy - 16, c2, r=14)
        ln(k, [(-50, dy - 150), (-30, dy - 196), (30, dy - 196), (50, dy - 150)], c3, w=LINE * 1.4)
        _estrela(k, 0, dy - 110, 18, "#FFD23F")


PROPS.update({"logo": Logo, "botao_inscrever": BotaoInscrever, "joinha": Joinha, "sabonete": Sabonete, "bolo": Bolo,
              "mochila": MochilaChao})


# ───────────────────────── 03 Sorriso Brilhante ─────────────────────────

def _carinha(k: Ink, cx: float, cy: float, P: dict, linha: str, bochecha: str, esc: float = 1.0) -> None:
    """Carinha de objeto-personagem (mesmo desenho do sabonete): olhos, boca e bochechas."""
    for s_ in (-1, 1):
        ex, ey = cx + s_ * 30 * esc, cy - 10 * esc
        if P.get("lid", 0) > 0.5:
            ln(k, [(ex - 13 * esc, ey), (ex, ey - 9 * esc), (ex + 13 * esc, ey)], linha, w=LINE)
        else:
            shape(k, ellipse_pts(ex, ey, 13 * esc, 17 * esc, 0, 14), "#FFFFFF", line=linha)
            k.dot(ex + 2 * esc, ey + 4 * esc, 6 * esc, _rgba("#000000"))
    b = P.get("boca", 0.0)
    if b < 0.15:
        ln(k, [(cx - 18 * esc, cy + 18 * esc), (cx, cy + 30 * esc), (cx + 18 * esc, cy + 18 * esc)], linha, w=LINE * 1.1)
    else:
        shape(k, [(cx - 20 * esc, cy + 16 * esc), (cx + 20 * esc, cy + 16 * esc), (cx + 10 * esc, cy + (16 + 30 * b) * esc),
                  (cx - 10 * esc, cy + (16 + 30 * b) * esc)], "#8A2E2E", line=linha)
    for s_ in (-1, 1):
        k.shape(ellipse_pts(cx + s_ * 54 * esc, cy + 12 * esc, 13 * esc, 9 * esc, 0, 12), fill=_rgba(bochecha, 0.7), line=0)


class PastaDente(_Prop):
    """Tubo de pasta de dente deitado. `aperta` 0→1 amassa o tubo e sai uma bolinha de pasta (do tamanho de um feijão)."""

    def __init__(self):
        super().__init__("pasta", "Pasta de dente", (640, 320), (320, 290), 150, {"aperta": 0.0})

    def paint(self, k, P):
        a = max(0.0, min(1.0, P["aperta"]))
        p_ = 18 * a                                                          # amassado no meio
        corpo = [(-230, -150), (60, -140 + p_ * 0.4), (130, -128), (170, -105), (170, -45), (130, -22), (60, -10 - p_ * 0.4),
                 (-230, 0)]
        shape(k, corpo, "#FFFFFF", line="#9FB3C8", smooth=False)
        shape(k, [(-250, -156), (-226, -156), (-226, 6), (-250, 6)], "#E9545D", smooth=False)     # fundo dobrado (crimpado)
        for y in (-128, -96, -64, -32):
            ln(k, [(-246, y), (-230, y)], "#FFFFFF", w=LINE * 0.6)
        shape(k, [(-170, -128 + 3), (40, -120 + p_ * 0.3), (40, -30 - p_ * 0.3), (-170, -22)], "#3C8BF0", smooth=False)  # rótulo
        _estrela(k, -65, -75, 30, "#FFFFFF")
        ln(k, [(-150, -112), (20, -106)], "#FFFFFF", w=LINE * 1.2)
        box(k, 170, -100, 222, -50, "#E9545D", r=10)                                            # tampinha
        if a > 0.4:
            u = min(1.0, (a - 0.4) / 0.6)
            for dx, dy, r in ((0, 6, 26), (0, -12, 20), (4, -26, 11)):
                shape(k, ellipse_pts(254 + 22 * u + dx, -75 + dy, r * (0.6 + 0.4 * u), r * 0.7 * (0.6 + 0.4 * u), 0, 16),
                      "#7FD3F7", line="#3E9FD6")


class Feijao(_Prop):
    """Grão de feijão gigante (destaque 'do tamanho de um grão de feijão'). `pasta` 1 = a bolinha de pasta igual ao lado."""

    def __init__(self):
        super().__init__("feijao", "Grão de feijão", (760, 460), (380, 420), 260, {"pasta": 0.0, "pulo": 0.0})

    def paint(self, k, P):
        y0 = -130 - 60 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        x0 = -130 if P["pasta"] > 0.05 else 0
        pts = []
        for j in range(40):                                        # contorno de feijão (rim)
            t = j / 40 * 2 * math.pi
            r = 1.0 - 0.3 * max(0.0, math.cos(t - math.pi / 2)) ** 2      # entalhe do "rim" embaixo
            pts.append((x0 + 150 * math.cos(t) * r, y0 + 100 * math.sin(t) * r))
        shape(k, pts, "#8E3B2E", line="#5E2219")
        ln(k, [(x0 - 80, y0 - 50), (x0 - 30, y0 - 70)], "#C46A57", w=LINE * 2.0)                    # brilho
        k.shape(ellipse_pts(x0 + 60, y0 + 70, 26, 8, 0, 12), fill=_rgba("#F2E6D8"), line=0)          # olhinho do feijão
        if P["pasta"] > 0.05:
            sc = P["pasta"]
            cx, cy = 190, y0
            for dx, dy, r in ((0, 30, 132), (0, -12, 98), (6, -48, 54)):                            # bolinha de pasta (casquinha),
                shape(k, ellipse_pts(cx + dx * sc, cy + dy * sc, r * sc, r * 0.5 * sc, 0, 24), "#7FD3F7", line="#3E9FD6")  # mesmo tamanho
            ln(k, [(cx - 70 * sc, cy - 10 * sc), (cx - 30 * sc, cy - 26 * sc)], "#FFFFFF", w=LINE * 1.6)
            for yy in (-18, 18):                                                                     # sinal de igual
                box(k, 4, y0 + yy - 9, 56, y0 + yy + 9, "#FFFFFF", line="#5E2219", r=6)


class Ampulheta(_Prop):
    """Ampulheta dos 'dois minutinhos'. `areia` 0→1 escorre de cima para baixo; `vira` 0→1 gira meia volta."""

    def __init__(self):
        super().__init__("ampulheta", "Ampulheta", (520, 640), (260, 600), 330, {"areia": 0.0, "vira": 0.0, "brilho": 0.0})

    def paint(self, k, P):
        cy = -260
        k.c.save()
        k.c.rotate(math.degrees(math.pi * max(0.0, min(1.0, P["vira"]))), 0, cy)
        for y in (-240, 240):                                      # tampas de madeira
            box(k, -150, cy + y - 22 if y < 0 else cy + y - 6, 150, cy + y + 6 if y < 0 else cy + y + 22, PAL["madeira"], r=8)
        glass = [(-110, cy - 230), (110, cy - 230), (20, cy - 10), (110, cy + 230), (-110, cy + 230), (-20, cy - 10)]
        a = max(0.0, min(1.0, P["areia"]))
        top_h = 170 * (1 - a)                                      # areia de cima diminui, a de baixo cresce
        if top_h > 4:
            yt = cy - 30 - top_h
            w = 20 + (110 - 20) * (top_h / 220)
            shape(k, [(-w, yt), (w, yt), (16, cy - 24), (-16, cy - 24)], "#FFC93A", line="#D99A1E", smooth=False)
        bot_h = 30 + 150 * a
        shape(k, [(-104, cy + 226), (104, cy + 226), (104 - bot_h * 0.25, cy + 226 - bot_h * 0.6),
                  (0, cy + 226 - bot_h), (-104 + bot_h * 0.25, cy + 226 - bot_h * 0.6)], "#FFC93A", line="#D99A1E", smooth=False)
        if 0.0 < a < 1.0:
            ln(k, [(0, cy - 24), (0, cy + 226 - bot_h)], "#FFC93A", w=LINE * 1.2)
        shape(k, glass, PAL["vidro"], line="#7FB6DB", alpha=0.45, smooth=False)
        ln(k, [(-80, cy - 200), (-40, cy - 120)], "#FFFFFF", w=LINE * 1.4)
        for x in (-150, 150):
            box(k, x - 10, cy - 230, x + 10, cy + 230, PAL["madeira"], r=6)
        k.c.restore()
        if P["brilho"] > 0.05:
            _estrela(k, 160, cy - 260, 30 * P["brilho"], "#FFFFFF")


class Gotinha(_Prop):
    """Gotinha d'água com carinha (objeto-personagem): agradece fazendo reverência (`reverencia` 0→1), pula, fala (`boca`)."""

    def __init__(self):
        super().__init__("gotinha", "Gotinha d'água", (460, 560), (230, 520), 260,
                         {"reverencia": 0.0, "pulo": 0.0, "boca": 0.0, "lid": 0.0})

    def paint(self, k, P):
        y0 = -40 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        rv = max(0.0, min(1.0, P["reverencia"]))
        k.c.save()
        k.c.rotate(-28 * rv, 0, y0)                                # inclina para a frente (reverência) a partir da base
        pts = []
        for j in range(40):
            t = j / 40 * 2 * math.pi
            x = 120 * math.sin(t) * (1 - 0.0)
            yy = -120 - 120 * math.cos(t)
            if math.cos(t) > 0:                                     # parte de cima afina até a ponta
                x *= (1 - math.cos(t)) ** 0.8
                yy = -120 - 210 * math.cos(t)
            pts.append((x, y0 + yy))
        shape(k, pts, "#7FC8FA", line="#3E8FD6")
        ln(k, [(-60, y0 - 200), (-30, y0 - 260)], "#FFFFFF", w=LINE * 1.8)
        _carinha(k, 0, y0 - 120, P, "#1E4E8C", "#FF8AB0", esc=1.2)
        if rv > 0.3:                                                # bracinhos de reverência (um na barriga, outro aberto)
            ln(k, [(-100, y0 - 80), (-40, y0 - 60)], "#3E8FD6", w=LINE * 1.6)
            ln(k, [(100, y0 - 90), (160, y0 - 150)], "#3E8FD6", w=LINE * 1.6)
        k.c.restore()


class AguaTorneira(_Prop):
    """Fio d'água saindo da torneira da pia do banheiro. `aberta` 0→1 (0 = torneira fechada, só pinga)."""

    def __init__(self):
        super().__init__("agua", "Água da torneira", (200, 300), (100, 20), 80, {"aberta": 1.0})

    def paint(self, k, P):
        a = max(0.0, min(1.0, P["aberta"]))
        if a > 0.05:                                                # origem = bico da torneira; cai até a cuba
            w = 6 + 10 * a
            shape(k, [(-w, 0), (w, 0), (w * 0.8, 70 * a + 10), (-w * 0.8, 70 * a + 10)], "#9CD8FF", line="#5AA8E6", alpha=0.85,
                  smooth=False)
        else:
            shape(k, [(0, 6), (8, 22), (0, 30), (-8, 22)], "#9CD8FF", line="#5AA8E6")


PROPS.update({"pasta": PastaDente, "feijao": Feijao, "ampulheta": Ampulheta, "gotinha": Gotinha, "agua": AguaTorneira})


# ───────────────────────── 04 Cadê a Cor? ─────────────────────────
# Objetos de cor com o canal `cor`: 0 = cinza (a cor "sumiu"), 1 = a cor acende (resposta do coro ao "cadê?").

CINZA = "#C9CBD3"
CORES_TINTA = {0: None, 1: "#2F86F0", 2: "#FFD21F", 3: "#EE3B3B", 4: "#2DBE5A", 5: "#FF8A1F", 6: "#8E44EF", 7: "#8A5A36"}
#               vazio     azul          amarelo       vermelho      verde         laranja       roxo          marrom


def _mix(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#{:02X}{:02X}{:02X}".format(*(round(x + (y - x) * t) for x, y in zip(a, b)))


def _acende(cor: str, P: dict) -> str:
    return _mix(CINZA, cor, P.get("cor", 1.0))


def _brilho_cor(k: Ink, P: dict, x: float, y: float, raio: float) -> None:
    """Estrelinhas em volta no instante em que a cor acende (cor entre 0,2 e 0,95)."""
    c = P.get("cor", 1.0)
    if 0.2 < c < 0.95:
        for j in range(5):
            a = j * 2 * math.pi / 5 + 0.3
            _estrela(k, x + math.cos(a) * raio, y + math.sin(a) * raio, 22 * math.sin(math.pi * c), "#FFFFFF")


class Morango(_Prop):
    """Morango GIGANTE (mundo pequenino: maior que a Laurinha). Sementinhas, folhas e carinha opcional (`cara`)."""

    def __init__(self):
        super().__init__("morango", "Morango", (620, 700), (310, 660), 340, {"cor": 1.0, "cara": 0.0, "lid": 0.0, "boca": 0.0,
                                                                            "pulo": 0.0})

    def paint(self, k, P):
        y0 = -40 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        verm, folha = _acende("#EE3B3B", P), _acende("#3DBE5A", P)
        pts = []
        for j in range(48):                                         # coração arredondado, ponta para baixo
            t = j / 48 * 2 * math.pi
            x = 230 * math.sin(t) * (0.78 + 0.22 * math.cos(t))
            yy = -300 - 270 * math.cos(t) * (0.9 if math.cos(t) < 0 else 1.0)
            pts.append((x, y0 + yy * 1.0 + (0 if math.cos(t) < 0 else 0)))
        shape(k, pts, verm, line=dark(verm, 0.7))
        ln(k, [(-140, y0 - 430), (-90, y0 - 480)], "#FFFFFF", w=LINE * 2.2, alpha=0.7)          # brilho
        sem = _acende("#FFE15A", P)
        for sx, sy in ((-120, -380), (-40, -420), (60, -400), (140, -350), (-150, -260), (-60, -300), (40, -280),
                       (130, -230), (-100, -160), (0, -180), (80, -130), (-30, -90)):
            if P["cara"] > 0.5 and -110 < sx < 110 and -360 < sy < -180:
                continue                                            # a carinha fica limpa
            shape(k, [(sx, y0 + sy - 12), (sx + 7, y0 + sy), (sx, y0 + sy + 12), (sx - 7, y0 + sy)], sem, line=dark(sem, 0.75),
                  w=LINE * 0.6)
        for a in (-1.0, -0.45, 0.1, 0.65, 1.2):                     # coroa de folhas no topo
            cx, cy = 60 * math.sin(a), y0 - 560
            tip = (cx + 150 * math.sin(a), cy - 40 - 60 * math.cos(a))
            shape(k, [(cx - 30, cy + 10), tip, (cx + 30, cy + 10)], folha, line=dark(folha, 0.7))
        shape(k, [(-12, y0 - 580), (-6, y0 - 660), (12, y0 - 660), (14, y0 - 580)], folha, line=dark(folha, 0.7), smooth=False)
        if P["cara"] > 0.5:
            _carinha(k, 0, y0 - 290, P, "#7A1E1E", "#FF9AB0", esc=1.5)
        _brilho_cor(k, P, 0, y0 - 320, 300)


class BananaGrande(_Prop):
    """Banana GIGANTE deitada em arco (vira escorregador). Mesma banana dos itens, ampliada."""

    def __init__(self):
        super().__init__("banana_grande", "Banana gigante", (900, 420), (450, 380), 220, {"cor": 1.0})

    def paint(self, k, P):
        am, pt = _acende("#FFD84A", P), _acende("#7A5A2E", P)
        cima, baixo = [], []
        for j in range(25):                                         # arco: a curva de cima e a de baixo
            u = j / 24
            x = -380 + 760 * u
            arco = 200 * (1 - math.sin(math.pi * u))              # "sorriso": deitada, pontas para cima (escorregador)
            w = 30 + 70 * math.sin(math.pi * u)
            cima.append((x, -110 - arco - w))
            baixo.append((x, -110 - arco + w))
        shape(k, cima + baixo[::-1], am, line=dark(am, 0.78))
        ln(k, [(p[0], p[1] + 30 + 20 * math.sin(math.pi * j / 24)) for j, p in enumerate(cima[4:21], 4)], dark(am, 0.85),
           w=LINE * 0.8)                                            # gomo
        shape(k, [(-404, -340), (-370, -356), (-360, -316), (-398, -306)], pt, smooth=False)            # pontinhas
        shape(k, [(366, -326), (414, -342), (420, -302), (372, -296)], pt, smooth=False)
        ln(k, [(-160, -150), (-40, -120)], "#FFFFFF", w=LINE * 2.0, alpha=0.7)
        _brilho_cor(k, P, 0, -180, 330)


class Folha(_Prop):
    """Folhinha gigante (vira cama elástica): `balanco` 0→1 afunda e volta; nervuras; caule."""

    def __init__(self):
        super().__init__("folha", "Folhinha", (820, 420), (410, 380), 200, {"cor": 1.0, "balanco": 0.0})

    def paint(self, k, P):
        verde = _acende("#3DBE5A", P)
        b = 50 * math.sin(math.pi * max(0.0, min(1.0, P["balanco"])))   # afunda no meio
        pts = []
        for j in range(41):                                         # contorno: ponta à direita, base à esquerda
            u = j / 40 * 2 * math.pi
            x = 340 * math.cos(u)
            yy = -170 + 120 * math.sin(u) * (1 - 0.35 * max(0.0, math.cos(u))) + b * (1 - abs(math.cos(u)))
            pts.append((x, yy))
        shape(k, pts, verde, line=dark(verde, 0.7))
        meio = [(-330, -170), (-100, -170 + b * 0.9), (120, -170 + b * 0.8), (330, -170)]
        ln(k, meio, dark(verde, 0.78), w=LINE * 1.2)
        for x in (-200, -60, 80, 200):                              # nervuras
            y = -170 + b * (1 - abs(x) / 340)
            for s_ in (-1, 1):
                ln(k, [(x, y), (x + 70, y + s_ * 70)], dark(verde, 0.78), w=LINE * 0.9)
        ln(k, [(-340, -170), (-400, -120), (-420, -40)], dark(verde, 0.6), w=LINE * 2.2)             # caule
        ln(k, [(-150, -240), (0, -265)], "#FFFFFF", w=LINE * 1.8, alpha=0.6)
        _brilho_cor(k, P, 0, -170, 330)


class PotesTinta(_Prop):
    """Três potes de tinta gigantes: esquerda e direita despejam (`derrama` 0→1) no pote do meio, que enche (`nivel`)
    com a cor nova; `explode` 0→1 = a cor nova estoura em bolinhas. Cores pelo código de CORES_TINTA
    (`esq`, `dir`, `meio`: 1 azul, 2 amarelo, 3 vermelho, 4 verde, 5 laranja, 6 roxo, 7 marrom)."""

    def __init__(self):
        super().__init__("potes_tinta", "Potes de tinta", (1000, 620), (500, 580), 300,
                         {"esq": 1.0, "dir": 2.0, "meio": 4.0, "derrama": 0.0, "nivel": 0.0, "explode": 0.0})

    def _pote(self, k, cx, cor, nivel, incl=0.0, base=0.0):
        k.c.save()
        k.c.rotate(incl, cx, base - 60)
        corpo = [(cx - 120, base - 230), (cx + 120, base - 230), (cx + 100, base), (cx - 100, base)]
        shape(k, corpo, "#F4F7FB", line="#9FB3C8", smooth=False)
        if cor and nivel > 0.02:
            h = 200 * nivel
            shape(k, [(cx - 100 - 20 * (h / 230), base - h), (cx + 100 + 20 * (h / 230), base - h), (cx + 100, base), (cx - 100, base)],
                  cor, line=dark(cor, 0.75), smooth=False)
            shape(k, ellipse_pts(cx, base - h, 100 + 20 * (h / 230), 18, 0, 20), _mix(cor, "#FFFFFF", 0.25), line=dark(cor, 0.75))
        shape(k, ellipse_pts(cx, base - 230, 120, 22, 0, 24), "#FFFFFF", line="#9FB3C8")       # boca do pote
        if cor:
            box(k, cx - 60, base - 150, cx + 60, base - 90, cor, line=dark(cor, 0.7), r=12)       # etiqueta da cor
        k.c.restore()

    def paint(self, k, P):
        d = max(0.0, min(1.0, P["derrama"]))
        ce, cd, cm = (CORES_TINTA.get(int(round(P[n]))) for n in ("esq", "dir", "meio"))
        self._pote(k, -330, ce, 0.8 - 0.4 * d, incl=35 * math.sin(math.pi * d) if d < 1 else 0)
        self._pote(k, 330, cd, 0.8 - 0.4 * d, incl=-35 * math.sin(math.pi * d) if d < 1 else 0)
        if 0.15 < d < 0.85:                                         # fios de tinta caindo no pote do meio
            for cx, cor, s_ in ((-330, ce, 1), (330, cd, -1)):
                if cor:
                    ln(k, [(cx + s_ * 110, -250), (cx + s_ * 200, -300), (s_ * -60, -240)], cor, w=LINE * 3.5)
        self._pote(k, 0, cm, max(0.0, min(1.0, P["nivel"])))
        e = max(0.0, min(1.0, P["explode"]))
        if cm and 0.0 < e < 1.0:                                    # a cor nova estoura em bolinhas
            for j in range(12):
                a = -math.pi / 2 + (j - 5.5) * 0.28
                rr = 80 + 380 * e
                r = 34 * (1 - e * 0.6) * (1 if j % 2 else 0.7)
                shape(k, ellipse_pts(math.cos(a) * rr, -260 + math.sin(a) * rr, r, r, 0, 14), cm, line=dark(cm, 0.75))


class ArcoIris(_Prop):
    """Arco-íris que se monta faixa por faixa: `faixas` 0→6 (vermelho → roxo, de fora para dentro), nuvens nas pontas."""

    def __init__(self):
        super().__init__("arco_iris", "Arco-íris", (1300, 720), (650, 680), 360, {"faixas": 6.0})

    def paint(self, k, P):
        n = max(0.0, min(6.0, P["faixas"]))
        cores = ("#EE3B3B", "#FF8A1F", "#FFD21F", "#2DBE5A", "#2F86F0", "#8E44EF")
        R0, w = 560, 62
        for i, c in enumerate(cores):
            vis = max(0.0, min(1.0, n - i))
            if vis <= 0:
                break
            r1, r2 = R0 - i * w, R0 - (i + 1) * w
            a_fim = math.pi * vis                                  # cada faixa cresce da esquerda para a direita
            ext = [(-r1 * math.cos(a), -60 - r1 * math.sin(a)) for a in np.linspace(0, a_fim, 40)]
            inn = [(-r2 * math.cos(a), -60 - r2 * math.sin(a)) for a in np.linspace(a_fim, 0, 40)]
            shape(k, ext + inn, c, line=dark(c, 0.8), smooth=False)
        for cx in (-R0 + 3 * w, R0 - 3 * w):                       # nuvens nas pontas
            for dx, dy, r in ((-90, -10, 70), (0, -50, 90), (90, -10, 70), (0, 10, 80)):
                shape(k, ellipse_pts(cx + dx, -40 + dy, r, r * 0.85, 0, 20), "#FFFFFF", line="#BFD6EA")


PROPS.update({"morango": Morango, "banana_grande": BananaGrande, "folha": Folha, "potes_tinta": PotesTinta,
              "arco_iris": ArcoIris})
