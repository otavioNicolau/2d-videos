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

ITEMS = ("copo_leite", "copo_vazio", "banana", "banana_mordida", "pente", "garrafinha", "carrinho", "sombrinha", "escova")


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
    elif name == "escova":
        shape(k, Q([(-6, 14), (-6, -74), (6, -74), (6, 14)]), PAL["escova"], smooth=False)
        shape(k, Q([(-2, -104), (16, -104), (16, -72), (-2, -72)]), "#FFFFFF", line="#B8C4D0", smooth=False)
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
        super().__init__("janela", "Janela", (900, 560), (450, 520), 400, {"abre": 0.0, "luz": 0.0})

    def paint(self, k, P):
        W2, Hh = 170, 340
        shape(k, [(-W2 - 22, 22), (W2 + 22, 22), (W2 + 22, -Hh - 22), (-W2 - 22, -Hh - 22)], PAL["moldura"], line="#C9D6E0", smooth=False)
        shape(k, [(-W2, 0), (W2, 0), (W2, -Hh), (-W2, -Hh)], PAL["ceu"], smooth=False)
        for cx, cy, s in ((-70, -250, 0.9), (80, -150, 0.7)):      # nuvens vistas pela janela
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
