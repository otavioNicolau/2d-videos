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
         "suco", "fatia_bolo", "fatia_grande", "escova_pasta", "escova_guitarra", "apito", "sapato", "estrela_natal", "sorvete")


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
    elif name == "apito":                                   # apito de escola de samba (amarelo) com cordinha
        shape(k, Q([(-6, -26), (30, -26), (34, -10), (30, 6), (-6, 6)]), "#FFD21F", line="#C99A1A", smooth=False)
        shape(k, Q([(-30, -20), (-6, -20), (-6, 0), (-30, 0)]), "#FFD21F", line="#C99A1A", smooth=False)
        k.dot(*q(14, -10), 7, _rgba("#534946"))
        ln(k, Q([(30, -8), (52, 12), (40, 36)]), "#E9545D", w=LINE * 0.9)
    elif name == "estrela_natal":                           # estrela da ponta da árvore, segura no alto
        cx, cy = q(0, -46)
        pts = [(cx + math.cos(-math.pi / 2 + j * math.pi / 5) * (44 if j % 2 == 0 else 19) * S,
                cy + math.sin(-math.pi / 2 + j * math.pi / 5) * (44 if j % 2 == 0 else 19) * S) for j in range(10)]
        shape(k, pts, "#FFD21F", line="#C99A1A", smooth=False)
    elif name == "sorvete":                                 # casquinha com bola de morango
        shape(k, Q([(-22, -40), (22, -40), (0, 30)]), "#E8B27A", line="#B5741F", smooth=False)
        shape(k, [q(x, y) for x, y in [(-30, -40), (-26, -70), (0, -86), (26, -70), (30, -40)]], "#FF9AC8", line="#E0609A")
    elif name == "sapato":                                  # tênis seguro pela mão (para calçar)
        shape(k, Q([(-40, -10), (-6, -34), (14, -30), (24, -6), (44, 0), (46, 14), (-40, 14)]), "#3C8BF0", line="#1F5FB8", smooth=False)
        box(k, *q(-42, 10), *q(48, 22), "#FFFFFF", line="#9FB3C8", r=6) if f > 0 else box(k, *q(48, 10), *q(-42, 22), "#FFFFFF", line="#9FB3C8", r=6)
        ln(k, Q([(-14, -22), (6, -18)]), "#FFFFFF", w=LINE * 0.9)
        ln(k, Q([(-6, -14), (12, -10)]), "#FFFFFF", w=LINE * 0.9)


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
        nv = min(1.0, n * 1.5)                                    # nuvens nascem junto com a 1ª faixa
        if nv > 0.05:
            for cx in (-R0 + 3 * w, R0 - 3 * w):                   # nuvens nas pontas
                for dx, dy, r in ((-90, -10, 70), (0, -50, 90), (90, -10, 70), (0, 10, 80)):
                    shape(k, ellipse_pts(cx + dx * nv, -40 + dy * nv, r * nv, r * 0.85 * nv, 0, 20), "#FFFFFF", line="#BFD6EA")


PROPS.update({"morango": Morango, "banana_grande": BananaGrande, "folha": Folha, "potes_tinta": PotesTinta,
              "arco_iris": ArcoIris})


# ───────────────────────── 05 Conta Comigo ─────────────────────────

COR_NUMERO = ("#EE3B3B", "#FF8A1F", "#FFC21A", "#2DBE5A", "#2F86F0", "#8E44EF", "#F0509A", "#18B5B0", "#FF6F3C", "#7B5CFF", "#E9545D")


class Numero(_Prop):
    """Número GIGANTE de 0 a 10 que pula na tela (`n` inteiro, `pop` 0→1 = surge crescendo, `pulo` 0→1 = pulinho).
    Cada número tem a sua cor; contorno branco + borda escura (lê sobre qualquer fundo)."""

    def __init__(self):
        super().__init__("numero", "Número", (560, 600), (280, 560), 300, {"n": 1.0, "pop": 1.0, "pulo": 0.0})

    def paint(self, k, P):
        n = int(round(max(0.0, min(10.0, P["n"]))))
        pop = max(0.0, min(1.0, P["pop"]))
        if pop <= 0.02:
            return
        esc = pop * (1 + 0.15 * math.sin(math.pi * pop))           # passa um tiquinho do tamanho e volta (estica)
        y = -60 - 70 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        cor = _rgba(COR_NUMERO[n])
        k.c.save()
        k.c.translate(0, y)
        k.c.scale(esc, esc)
        _texto(k, str(n), 0, 0, 420, (0.12, 0.12, 0.24, 1), contorno=(0.12, 0.12, 0.24, 1), borda=0.3)   # borda escura
        _texto(k, str(n), 0, 0, 420, cor, contorno=(1, 1, 1, 1), borda=0.13)
        k.c.restore()


def _capsula(k: Ink, p0, p1, r: float, fill: str, line: str) -> None:
    """Dedo de luva: cápsula (bastão de pontas redondas) de p0 a p1, raio r."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    a = math.atan2(dy, dx)
    pts = [(p1[0] + r * math.cos(a - math.pi / 2 + math.pi * u / 10), p1[1] + r * math.sin(a - math.pi / 2 + math.pi * u / 10))
           for u in range(11)]
    pts += [(p0[0] + r * math.cos(a + math.pi / 2 + math.pi * u / 10), p0[1] + r * math.sin(a + math.pi / 2 + math.pi * u / 10))
            for u in range(11)]
    shape(k, pts, fill, line=line, smooth=False)


class Mao(_Prop):
    """Mão gigante de luva (desenho infantil) mostrando `dedos` 0→5 levantados (indicador primeiro, polegar por último);
    `acende` 0→1 = estrelinha na ponta dos dedos levantados (contando). `espelho` 1 = mão esquerda.
    Dedos-cápsula em leque saindo de TRÁS da palma, polegar redondo, punho de luva (o 1º desenho, com dedos-palito
    retos e polegar de banana, ficou estranho — storyboard ep05)."""

    def __init__(self):
        super().__init__("mao", "Mão", (560, 720), (280, 680), 330, {"dedos": 5.0, "espelho": 0.0, "acende": 0.0})

    def paint(self, k, P):
        d = max(0.0, min(5.0, P["dedos"]))
        sg = -1 if P.get("espelho", 0) > 0.5 else 1
        luva, linha = "#FFFFFF", "#7F93AE"
        X = lambda x: sg * x
        # (base x, base y, comprimento, ângulo em relação à vertical) — indicador, médio, anelar, mínimo
        dedos = ((62, -200, 165, 0.10), (8, -212, 180, 0.0), (-46, -205, 168, -0.10), (-96, -185, 135, -0.22))
        pontas = []
        for j, (bx, by, comp, ang) in enumerate(dedos):
            sobe = max(0.0, min(1.0, d - j))
            L = 38 + (comp - 38) * sobe                                # dobrado: só o nó do dedo aparece
            tip = (X(bx + math.sin(ang) * L), by - math.cos(ang) * L)
            _capsula(k, (X(bx), by + 40), tip, 31 if j < 3 else 27, luva, linha)
            if sobe > 0.9:
                pontas.append((tip[0], tip[1] - 46))
        po = max(0.0, min(1.0, d - 4))                                 # polegar
        if po > 0.05:                                                  # levantado: sai do lado, atrás da palma
            a = 1.15 - 0.45 * po
            tip = (X(100 + math.sin(a) * 150), -105 - math.cos(a) * 150)
            _capsula(k, (X(90), -90), tip, 32, luva, linha)
            if po > 0.9:
                pontas.append((tip[0] + X(30), tip[1] - 34))
        palma = [(X(-128), -205), (X(-40), -230), (X(70), -228), (X(128), -190), (X(138), -110), (X(118), -38), (X(-112), -38),
                 (X(-138), -112)]
        shape(k, palma, luva, line=linha)
        for x in (-50, 0, 50):                                         # costuras da luva
            ln(k, [(X(x), -185), (X(x), -125)], linha, w=LINE * 0.8)
        if po <= 0.05:                                                 # dobrado: deitado por cima da palma
            _capsula(k, (X(118), -96), (X(42), -106), 30, luva, linha)
        shape(k, [(X(-120), -52), (X(120), -52), (X(132), -8), (X(118), 50), (X(-118), 50), (X(-132), -8)], "#FFD23F",
              line="#C99A1A")                                          # punho
        if P["acende"] > 0.05:
            for x, y in pontas:
                _estrela(k, x, y, 22 * P["acende"], "#FFD23F")


class Bicicleta(_Prop):
    """Bicicleta de lado (vista de baixo pelos pequenininhos: é enorme). `giro` gira as rodas; `brilho_rodas` 0→1
    acende as duas rodas (contando: duas!)."""

    def __init__(self):
        super().__init__("bicicleta", "Bicicleta", (1100, 700), (550, 660), 330, {"giro": 0.0, "brilho_rodas": 0.0})

    def _roda(self, k, cx, cy, R, giro, brilho):
        shape(k, ellipse_pts(cx, cy, R, R, 0, 40), "#FFF6C2" if brilho > 0.5 else "#FFFFFF", line="#3A3A48", w=LINE * 2.4)
        shape(k, ellipse_pts(cx, cy, R - 28, R - 28, 0, 40), "#DFF1FF", line="#9FB3C8")
        for j in range(8):
            a = giro * 2 * math.pi + j * math.pi / 4
            ln(k, [(cx, cy), (cx + math.cos(a) * (R - 28), cy + math.sin(a) * (R - 28))], "#9FB3C8", w=LINE * 0.7)
        k.dot(cx, cy, 14, _rgba("#534946"))
        if brilho > 0.05:
            _estrela(k, cx, cy - R - 50, 34 * brilho, "#FFD23F")

    def paint(self, k, P):
        g, b = P["giro"], P["brilho_rodas"]
        R, y = 190, -200
        self._roda(k, -300, y, R, g, b)
        self._roda(k, 300, y, R, g, b)
        quadro = "#E9545D"
        for pts in ([(-300, y), (-40, y - 230), (230, y - 230)], [(-300, y), (20, y)], [(20, y), (-40, y - 230)],
                    [(20, y), (230, y - 230)], [(230, y - 230), (300, y)]):
            ln(k, pts, quadro, w=LINE * 3.2)
        box(k, -110, y - 268, 20, y - 236, "#534946", r=14)          # selim
        ln(k, [(230, y - 230), (250, y - 300), (310, y - 310)], "#534946", w=LINE * 2.2)   # guidão
        shape(k, ellipse_pts(20, y, 34, 34, 0, 20), "#FFD23F", line="#C99A1A")             # pedal/coroa


PROPS.update({"numero": Numero, "mao": Mao, "bicicleta": Bicicleta})


# ───────────────────────── 06 Passeio na Lagoa ─────────────────────────

class Sapo(_Prop):
    """Sapo cantor (objeto-personagem): `croac` 0→1 enche o papo e abre a boca; `pulo` 0→1; `microfone` 1 = taboa na mão."""

    def __init__(self):
        super().__init__("sapo", "Sapo", (520, 520), (260, 480), 230, {"croac": 0.0, "pulo": 0.0, "microfone": 0.0, "lid": 0.0, "coroa": 0.0})

    def paint(self, k, P):
        y0 = -90 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        verde, esc = "#5BC85B", "#2E8B3E"
        for sx in (-1, 1):                                          # patas de trás dobradas
            shape(k, [(sx * 70, y0 - 10), (sx * 150, y0 - 60), (sx * 170, y0 - 10), (sx * 120, y0 + 4)], verde, line=esc)
            shape(k, ellipse_pts(sx * 150, y0 + 2, 46, 14, 0, 12), verde, line=esc)
        shape(k, ellipse_pts(0, y0 - 110, 150, 110, 0, 32), verde, line=esc)           # corpo
        shape(k, ellipse_pts(0, y0 - 80, 92, 62, 0, 24), "#D8F5B0", line=esc)          # barriga
        c = max(0.0, min(1.0, P["croac"]))
        if c > 0.05:                                                # papo cheio
            shape(k, ellipse_pts(0, y0 - 128, 70 * c + 20, 52 * c + 12, 0, 24), "#F6E3A1", line="#C9A64A")
        if P.get("coroa", 0) > 0.5:                                 # fantasia de princesa (Carnaval da Turminha)
            shape(k, [(-44, y0 - 238), (-44, y0 - 290), (-22, y0 - 262), (0, y0 - 302), (22, y0 - 262), (44, y0 - 290), (44, y0 - 238)],
                  "#FFD23F", line="#D9A520", smooth=False)
            k.dot(0, y0 - 270, 8, _rgba("#FF7FBF"))
        for sx in (-1, 1):                                          # olhos no alto
            shape(k, ellipse_pts(sx * 62, y0 - 214, 44, 44, 0, 20), verde, line=esc)
            if P.get("lid", 0) > 0.5:
                ln(k, [(sx * 62 - 22, y0 - 214), (sx * 62, y0 - 204), (sx * 62 + 22, y0 - 214)], "#1F3A1F", w=LINE * 1.1)
            else:
                shape(k, ellipse_pts(sx * 62, y0 - 214, 28, 30, 0, 18), "#FFFFFF", line=esc)
                k.dot(sx * 62 + 4, y0 - 208, 11, _rgba("#1F1F1F"))
        if c > 0.3:
            shape(k, ellipse_pts(0, y0 - 160, 50, 22 * c, 0, 18), "#8A2E2E", line=esc)
        else:
            ln(k, [(-70, y0 - 166), (0, y0 - 150), (70, y0 - 166)], "#1F3A1F", w=LINE * 1.2)
        for sx in (-1, 1):
            k.shape(ellipse_pts(sx * 100, y0 - 150, 18, 11, 0, 12), fill=_rgba("#FF9AAE", 0.75), line=0)
            shape(k, [(sx * 60, y0 - 70), (sx * 80, y0 - 10), (sx * 104, y0 - 6), (sx * 84, y0 - 64)], verde, line=esc)   # bracinhos
        if P.get("microfone", 0) > 0.5:                             # taboa de microfone
            ln(k, [(96, y0 - 30), (120, y0 - 190)], "#3F8F3A", w=LINE * 2)
            shape(k, ellipse_pts(124, y0 - 220, 20, 44, 0.1, 16), "#7A4A2A", line="#4E2E18")


class Pato(_Prop):
    """Patinho amarelo dançante: `quem` 0→1 abre o bico ("quém, quém"); `asas` 0→1 levanta as asinhas; `pulo`."""

    def __init__(self):
        super().__init__("pato", "Pato", (520, 600), (260, 560), 260, {"quem": 0.0, "asas": 0.0, "pulo": 0.0})

    def paint(self, k, P):
        y0 = -60 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        am, esc, lar = "#FFD84A", "#D9A520", "#FF8A1F"
        for sx in (-1, 1):                                          # patinhas laranja
            shape(k, [(sx * 40, y0 - 4), (sx * 40 + 46, y0 + 6), (sx * 40 + 10, y0 + 18), (sx * 40 - 26, y0 + 6)], lar, line="#C9661A")
        shape(k, ellipse_pts(0, y0 - 100, 130, 95, 0, 32), am, line=esc)                # corpo
        a = max(0.0, min(1.0, P["asas"]))
        for sx in (-1, 1):
            shape(k, [(sx * 110, y0 - 120), (sx * (180 + 30 * a), y0 - 150 - 70 * a), (sx * 150, y0 - 70)], am, line=esc)
        shape(k, ellipse_pts(0, y0 - 250, 86, 82, 0, 28), am, line=esc)               # cabeça
        b = max(0.0, min(1.0, P["quem"]))
        shape(k, [(-46, y0 - 232), (46, y0 - 232), (60, y0 - 214), (0, y0 - 206 + 4 * b), (-60, y0 - 214)], lar, line="#C9661A")
        shape(k, [(-44, y0 - 206), (44, y0 - 206), (30, y0 - 186 + 26 * b), (-30, y0 - 186 + 26 * b)], lar, line="#C9661A")
        for sx in (-1, 1):
            shape(k, ellipse_pts(sx * 34, y0 - 272, 15, 19, 0, 14), "#FFFFFF", line=esc)
            k.dot(sx * 34 + 3, y0 - 268, 8, _rgba("#1F1F1F"))
            k.shape(ellipse_pts(sx * 62, y0 - 238, 14, 9, 0, 12), fill=_rgba("#FF9AAE", 0.75), line=0)
        ln(k, [(0, y0 - 330), (14, y0 - 352), (-6, y0 - 360)], esc, w=LINE * 1.2)       # topetinho


class Girino(_Prop):
    """Girino que vira sapo (quadros da história): `fase` 0 = girino nadando com rabo; 1→4 nascem as perninhas
    (uma por vez); 5 = rabo sumiu (vira sapinho). `nada` 0→1 mexe o rabo."""

    def __init__(self):
        super().__init__("girino", "Girino", (620, 360), (310, 320), 170, {"fase": 0.0, "nada": 0.0})

    def paint(self, k, P):
        fase = max(0.0, min(5.0, P["fase"]))
        cor = _mix("#4A5A6A", "#5BC85B", min(1.0, fase / 5))
        esc = dark(cor, 0.7)
        rabo = max(0.0, 1 - max(0.0, fase - 4))
        w = math.sin(P["nada"] * 2 * math.pi * 3) * 26
        if rabo > 0.05:                                             # rabo ondulando
            pts = []
            for j in range(13):
                u = j / 12
                pts.append((90 + 230 * u * rabo, -110 + w * u + 30 * (1 - u) * 0 - (40 * (1 - u)) * (j % 2) * 0))
            top = [(x, y - 26 * (1 - j / 12)) for j, (x, y) in enumerate(pts)]
            bot = [(x, y + 26 * (1 - j / 12)) for j, (x, y) in enumerate(pts)]
            shape(k, top + bot[::-1], cor, line=esc)
        # 4 perninhas, uma por vez: 1ª e 2ª = patas de TRÁS (dobradas, com pezinho de nadadeira); 3ª e 4ª = da frente
        patas = (((60, -60), (110, -10), (70, 10)), ((40, -150), (100, -200), (60, -224)),
                 ((-70, -50), (-60, 4), (-84, 14)), ((-80, -164), (-74, -212), (-96, -226)))
        for i, (a0, a1, a2) in enumerate(patas):
            g = max(0.0, min(1.0, fase - i))
            if g <= 0.05:
                continue
            m = (a0[0] + (a1[0] - a0[0]) * g, a0[1] + (a1[1] - a0[1]) * g)
            e = (m[0] + (a2[0] - a1[0]) * g, m[1] + (a2[1] - a1[1]) * g)
            _capsula(k, a0, m, 15 if i < 2 else 12, cor, esc)
            _capsula(k, m, e, 13 if i < 2 else 10, cor, esc)
            if g > 0.6:                                             # pezinho em leque
                for d in (-0.5, 0.0, 0.5):
                    ang = math.atan2(e[1] - m[1], e[0] - m[0]) + d
                    _capsula(k, e, (e[0] + math.cos(ang) * 24, e[1] + math.sin(ang) * 24), 7, cor, esc)
        shape(k, ellipse_pts(-20, -110, 120, 84, 0, 28), cor, line=esc)
        for sy in (-1, 1):
            shape(k, ellipse_pts(-80, -150 + sy * 0, 22, 24, 0, 16), "#FFFFFF", line=esc) if sy < 0 else None
        k.dot(-76, -146, 10, _rgba("#1F1F1F"))
        ln(k, [(-118, -96), (-96, -86), (-74, -96)], "#1F1F1F", w=LINE)
        k.shape(ellipse_pts(-50, -96, 14, 9, 0, 12), fill=_rgba("#FF9AAE", 0.7), line=0)


class VitoriaRegia(_Prop):
    """Folha de vitória-régia gigante boiando (vira palco/ilha): `balanco` 0→1 afunda e volta; `flor` 1 = florzinha rosa."""

    def __init__(self):
        super().__init__("vitoria_regia", "Vitória-régia", (1000, 360), (500, 320), 160, {"balanco": 0.0, "flor": 1.0})

    def paint(self, k, P):
        b = 18 * math.sin(math.pi * max(0.0, min(1.0, P["balanco"])))
        shape(k, ellipse_pts(0, -40 + b, 440, 92, 0, 40), "#3FAE57", line="#25803A")
        shape(k, ellipse_pts(0, -58 + b, 410, 72, 0, 40), "#5CCB6E", line="#25803A")
        ln(k, [(0, -58 + b), (90, 6 + b)], "#25803A", w=LINE * 1.4)                       # a fendinha
        for a in (-2.6, -2.0, -1.2, -0.5, 0.3):
            ln(k, [(0, -58 + b), (math.cos(a) * 320, -58 + b + math.sin(a) * 52)], "#4BB85E", w=LINE * 0.8)
        if P.get("flor", 0) > 0.5:
            for j in range(6):
                a = j * math.pi / 3
                shape(k, ellipse_pts(-250 + math.cos(a) * 26, -96 + b + math.sin(a) * 14, 30, 16, a, 12), "#FF9AC8", line="#E0609A")
            shape(k, ellipse_pts(-250, -98 + b, 16, 12, 0, 12), "#FFE066")


class Taboa(_Prop):
    """Moita de taboas (plantas da beira da lagoa, gigantes para os pequenininhos); `vento` 0→1 balança."""

    def __init__(self):
        super().__init__("taboa", "Taboa", (420, 820), (210, 790), 400, {"vento": 0.0})

    def paint(self, k, P):
        v = math.sin(P["vento"] * 2 * math.pi) * 18
        for x, h, inc in ((-80, 640, -0.08), (0, 720, 0.0), (80, 600, 0.08), (-30, 520, -0.04), (50, 560, 0.05)):
            tx = x + inc * h + v
            ln(k, [(x, 0), (x + inc * h * 0.5 + v * 0.5, -h * 0.5), (tx, -h)], "#3F8F3A", w=LINE * 2)
            shape(k, ellipse_pts(tx, -h + 70, 20, 64, inc, 16), "#7A4A2A", line="#4E2E18")
        for x, a in ((-110, -0.5), (110, 0.5), (-40, -0.25), (40, 0.25)):                # folhas longas
            shape(k, [(x - 12, 0), (x + 12, 0), (x + math.sin(a) * 420 + 4, -math.cos(a) * 420)], "#5BB84F", line="#2E7A30")


PROPS.update({"sapo": Sapo, "pato": Pato, "girino": Girino, "vitoria_regia": VitoriaRegia, "taboa": Taboa})


# ───────────────────────── 07 Pisca-Pisca de Natal ─────────────────────────

PISCA = ("#FF4D4D", "#FFD21F", "#2F86F0", "#2DBE5A", "#FF7FBF")


class ArvoreNatal(_Prop):
    """Árvore de Natal gigante (para eles). `bolinhas` 0→1 aparecem; `pisca` fase do pisca-pisca (inteiro = qual
    cor acende; luzes apagadas quando `luzes` 0); `estrela` 0→1 a estrela no topo (1 = colocada e brilhando)."""

    def __init__(self):
        super().__init__("arvore_natal", "Árvore de Natal", (900, 1200), (450, 1160), 560,
                         {"bolinhas": 1.0, "luzes": 1.0, "pisca": 0.0, "estrela": 1.0})

    ESCALA = 0.72      # cabe no quadro fixo dos níveis (900 unidades acima do chão; a estrela ia até 1160 e era cortada)

    def paint(self, k, P):
        k.c.save()
        k.c.scale(self.ESCALA, self.ESCALA)
        self._paint(k, P)
        k.c.restore()

    def _paint(self, k, P):
        verde, esc = "#2E9E4F", "#1E6E36"
        box(k, -60, -120, 60, 0, PAL["madeira"], r=8)                                  # tronco
        shape(k, [(-150, -40), (150, -40), (130, -130), (-130, -130)], "#E9545D", smooth=False)   # vaso
        for i, (y, w) in enumerate(((-130, 400), (-430, 320), (-700, 240))):           # três andares
            shape(k, [(-w, y), (w, y), (0, y - 380)], verde, line=esc, smooth=False)
            for j in range(-3, 4):
                shape(k, ellipse_pts(j * w / 3.6, y - 6, w / 7.5, 20, 0, 12), verde, line=esc)
        ph = P["pisca"]; on = P["luzes"] > 0.5
        n = 0
        for row, (y, w) in enumerate(((-210, 300), (-470, 240), (-720, 170), (-920, 90))):    # fio do pisca-pisca
            pts = [(-w + 2 * w * u / 10, y + 26 * math.sin(math.pi * u / 10 * 2 + row)) for u in range(11)]
            ln(k, pts, "#2B2B33", w=LINE * 0.8)
            for x, yy in pts[1:-1:2]:
                c = PISCA[n % len(PISCA)]
                aceso = on and (int(ph) + n) % 2 == 0
                if aceso:
                    k.shape(ellipse_pts(x, yy + 20, 48, 48, 0, 16), fill=_rgba(c, 0.35), line=0)
                shape(k, ellipse_pts(x, yy + 20, 21, 27, 0, 14), c if aceso else _mix(c, "#555566", 0.55), line=dark(c, 0.7))
                n += 1
        b = max(0.0, min(1.0, P["bolinhas"]))
        for j, (x, y, c) in enumerate(((-220, -260, "#E9545D"), (160, -300, "#FFD23F"), (-60, -390, "#2F86F0"),
                                        (-150, -560, "#FFD23F"), (130, -600, "#E9545D"), (0, -800, "#FF7FBF"), (-260, -170, "#FFD23F"), (250, -190, "#2F86F0"))):
            if b > j / 8:
                shape(k, ellipse_pts(x, y, 30, 30, 0, 16), c, line=dark(c, 0.7))
                ln(k, [(x - 12, y - 10), (x - 4, y - 18)], "#FFFFFF", w=LINE * 0.8)
        e = max(0.0, min(1.0, P["estrela"]))
        if e > 0.05:
            _estrela(k, 0, -1090 + 120 * (1 - e), 70 * (0.5 + 0.5 * e), "#FFD21F")
            if e > 0.95:
                for j in range(8):
                    a = j * math.pi / 4
                    ln(k, [(math.cos(a) * 90, -1090 + math.sin(a) * 90), (math.cos(a) * 125, -1090 + math.sin(a) * 125)], "#FFE680", w=LINE)


class PapaiNoel(_Prop):
    """Papai Noel de bermuda e óculos escuros (Natal no calor): `aceno` 0→1 balança a mão; `ho` 0→1 abre a boca."""

    def __init__(self):
        super().__init__("papai_noel", "Papai Noel de bermuda", (620, 900), (310, 860), 420, {"aceno": 0.0, "ho": 0.0})

    def paint(self, k, P):
        k.c.save()
        k.c.scale(0.9, 0.9)                 # o pompom do gorro passava do quadro do nível
        self._paint(k, P)
        k.c.restore()

    def _paint(self, k, P):
        pele, verm = "#FFD7B5", "#E53935"
        for sx in (-1, 1):                                                  # pernas com chinelo
            box(k, sx * 70 - 28, -170, sx * 70 + 28, -20, pele, r=14)
            box(k, sx * 70 - 50, -24, sx * 70 + 50, 0, "#2F86F0", r=10)
        shape(k, [(-150, -340), (150, -340), (140, -160), (-140, -160)], "#3C8BF0", smooth=False)   # bermuda florida
        for x, y in ((-90, -290), (60, -250), (-20, -200), (100, -310)):
            _estrela(k, x, y, 16, "#FFD23F")
        shape(k, ellipse_pts(0, -470, 170, 170, 0, 30), verm, line="#A82020")                # barrigão de camiseta
        box(k, -170, -390, 170, -350, "#2B2B33", r=8)                                         # cinto
        box(k, -30, -398, 30, -342, "#FFD23F", r=6)
        a = math.sin(P["aceno"] * math.pi * 4) * 20
        ln(k, [(-150, -540), (-230, -600), (-250 + a, -700)], pele, w=LINE * 3)               # braço acenando
        shape(k, ellipse_pts(-250 + a, -715, 30, 30, 0, 14), pele)
        ln(k, [(150, -540), (220, -470)], pele, w=LINE * 3)
        shape(k, ellipse_pts(0, -700, 110, 110, 0, 28), pele, line="#D9A27A")                 # cabeça
        shape(k, [(-120, -720), (120, -720), (100, -830), (40, -880), (160, -900), (200, -860), (-100, -800)], verm, line="#A82020")  # gorro
        shape(k, ellipse_pts(196, -870, 26, 26, 0, 14), "#FFFFFF", line="#C9D6E0")
        box(k, -130, -742, 130, -704, "#FFFFFF", line="#C9D6E0", r=16)
        shape(k, [(-110, -660), (110, -660), (90, -560), (0, -520), (-90, -560)], "#FFFFFF", line="#C9D6E0")   # barba
        for sx in (-1, 1):                                                  # óculos escuros
            shape(k, ellipse_pts(sx * 45, -690, 38, 26, 0, 16), "#2B2B33")
        ln(k, [(-8, -690), (8, -690)], "#2B2B33", w=LINE)
        ho = max(0.0, min(1.0, P["ho"]))
        shape(k, ellipse_pts(0, -630, 30, 8 + 22 * ho, 0, 14), "#8A2E2E", line="#5E1E1E")


class Ventilador(_Prop):
    """Ventilador de chão gigante: `giro` gira as pás; `vento` 0→1 linhas de vento saindo."""

    def __init__(self):
        super().__init__("ventilador", "Ventilador", (620, 860), (310, 820), 400, {"giro": 0.0, "vento": 1.0})

    def paint(self, k, P):
        box(k, -140, -30, 140, 0, "#9FB3C8", r=14)
        box(k, -18, -420, 18, -30, "#B8C4D0", r=8)
        cx, cy, R = 0, -560, 200
        for j in range(3):
            a = P["giro"] * 2 * math.pi + j * 2 * math.pi / 3
            p1 = (cx + math.cos(a - 0.35) * R, cy + math.sin(a - 0.35) * R)
            p2 = (cx + math.cos(a + 0.35) * R, cy + math.sin(a + 0.35) * R)
            shape(k, [(cx, cy), p1, p2], "#7FC8FA", line="#3E8FD6")
        shape(k, ellipse_pts(cx, cy, 34, 34, 0, 14), "#3E8FD6")
        shape(k, ellipse_pts(cx, cy, R + 20, R + 20, 0, 40), "#FFFFFF", line="#9FB3C8", alpha=0.25)
        for j in range(-2, 3):
            ln(k, [(cx - R - 40, cy), (cx - R - 30, cy)], "#9FB3C8")
        if P["vento"] > 0.05:
            for j, y in enumerate((-640, -560, -480)):
                ln(k, [(-260, y), (-340, y + 10 * math.sin(j)), (-420, y)], "#BFE6FF", w=LINE * 1.2)


PROPS.update({"arvore_natal": ArvoreNatal, "papai_noel": PapaiNoel, "ventilador": Ventilador})


# ───────────────────────── 09 Pipa no Céu ─────────────────────────

class Pipa(_Prop):
    """Pipa de papel colorido (losango em 4 cores) com rabiola de lacinhos. `balanco` 0→1 balança (fase), `linha` 0→1
    mostra a linha descendo até a mão (comprimento em `linha_dx`/`linha_dy`), `rabiola` 0→1 faz a rabiola ondular."""

    def __init__(self):
        super().__init__("pipa", "Pipa", (1200, 1000), (600, 900), 420,
                         {"balanco": 0.0, "linha": 0.0, "linha_dx": -500.0, "linha_dy": 600.0, "rabiola": 0.0})

    def paint(self, k, P):
        a = math.sin(P["balanco"] * 2 * math.pi) * 0.18
        cx, cy = 0.0, -560.0
        k.c.save()
        k.c.rotate(math.degrees(a), cx, cy)
        top, dir_, base, esq = (cx, cy - 230), (cx + 170, cy - 30), (cx, cy + 230), (cx - 170, cy - 30)
        for pts, cor in (((top, dir_, (cx, cy - 30)), "#E9545D"), ((dir_, base, (cx, cy - 30)), "#FFD21F"),
                         ((base, esq, (cx, cy - 30)), "#2F86F0"), ((esq, top, (cx, cy - 30)), "#2DBE5A")):
            shape(k, list(pts), cor, line="#534946", smooth=False)
        ln(k, [top, base], "#7A5A2E", w=LINE * 1.2)
        ln(k, [esq, dir_], "#7A5A2E", w=LINE * 1.2)
        w = P["rabiola"]
        pts = [(cx + 40 * math.sin(w * 2 * math.pi + j * 0.7), cy + 230 + j * 60) for j in range(7)]
        ln(k, [base] + pts, "#534946", w=LINE * 0.8)
        for j, (x, y) in enumerate(pts[1::2]):
            c = ("#FF7FBF", "#FFD21F", "#2F86F0")[j % 3]
            shape(k, [(x - 26, y - 14), (x, y), (x - 26, y + 14)], c, line=dark(c, 0.7), smooth=False)
            shape(k, [(x + 26, y - 14), (x, y), (x + 26, y + 14)], c, line=dark(c, 0.7), smooth=False)
        k.c.restore()
        if P["linha"] > 0.05:                                     # linha descendo até a mão de quem segura
            ln(k, [(cx, cy - 30), (cx + P["linha_dx"] * 0.5, cy + P["linha_dy"] * 0.6), (cx + P["linha_dx"], cy + P["linha_dy"])],
               "#FFFFFF", w=LINE * 0.6)


class Vento(_Prop):
    """Traços de vento (redemoinhos brancos) que sopram para o lado: `sopro` 0→1 avança os traços."""

    def __init__(self):
        super().__init__("vento", "Vento", (1200, 700), (600, 600), 300, {"sopro": 0.0})

    def paint(self, k, P):
        s = P["sopro"] % 1.0
        for j, (y, L) in enumerate(((-480, 300), (-340, 380), (-200, 260))):
            x0 = -500 + 700 * ((s + j * 0.33) % 1.0)
            pts = [(x0 + u * L, y + 26 * math.sin(u * math.pi * 2)) for u in (i / 10 for i in range(11))]
            ln(k, pts, "#FFFFFF", w=LINE * 1.6)
            ex, ey = pts[-1]
            ln(k, [(ex, ey), (ex + 30, ey - 30), (ex + 10, ey - 50), (ex - 10, ey - 30)], "#FFFFFF", w=LINE * 1.2)


class PosteFios(_Prop):
    """Poste de luz com fios (perigo para a pipa); `alerta` 0→1 acende um X vermelho piscando sobre os fios."""

    def __init__(self):
        super().__init__("poste", "Poste com fios", (1200, 1000), (600, 900), 420, {"alerta": 0.0})

    def paint(self, k, P):
        box(k, -22, -860, 22, 0, "#9FB3C8", r=8)
        box(k, -150, -840, 150, -810, "#7F93AE", r=6)
        for x in (-130, 0, 130):
            k.dot(x, -846, 10, _rgba("#534946"))
        for x in (-130, 0, 130):
            ln(k, [(x, -846), (x - 200, -800), (x - 420, -846)], "#2B2B33", w=LINE * 0.9)
            ln(k, [(x, -846), (x + 200, -800), (x + 420, -846)], "#2B2B33", w=LINE * 0.9)
        if P["alerta"] > 0.05:
            r = 120 * P["alerta"]
            ln(k, [(-r, -700 - r), (r, -700 + r)], "#E53935", w=LINE * 3)
            ln(k, [(r, -700 - r), (-r, -700 + r)], "#E53935", w=LINE * 3)


PROPS.update({"pipa": Pipa, "vento": Vento, "poste": PosteFios})


# ───────────────────────── 10 Pingo de Chuva ─────────────────────────

class Nuvem(_Prop):
    """Nuvem fofinha com carinha. `cinza` 0→1 (branca → nuvem de chuva), `chove` 0→1 pinguinhos saindo de baixo
    (fase em `queda`), `sobe` 0→1 vapor subindo até ela (o caminho da água)."""

    def __init__(self):
        super().__init__("nuvem", "Nuvem", (1100, 900), (550, 850), 380,
                         {"cinza": 0.0, "chove": 0.0, "queda": 0.0, "sobe": 0.0, "boca": 0.0, "lid": 0.0, "cara": 1.0})

    def paint(self, k, P):
        cor = _mix("#FFFFFF", "#9AA6B8", P["cinza"]); lin = _mix("#BFD6EA", "#6E7A8C", P["cinza"])
        cy = -520
        for dx, dy, r in ((-230, 40, 140), (-90, -40, 190), (110, -20, 170), (250, 50, 130), (0, 60, 170)):
            shape(k, ellipse_pts(dx, cy + dy, r, r * 0.86, 0, 24), cor, line=lin)
        if P.get("cara", 1.0) > 0.5:                                    # cara 0 = nuvem sem carinha (esconde-esconde)
            _carinha(k, 0, cy + 20, P, "#3A4A66", "#FF9AB0", esc=1.4)
        c = P["chove"]
        if c > 0.05:
            for j in range(9):
                x = -300 + j * 75
                y = cy + 170 + ((P["queda"] * 380 + j * 97) % 380)
                shape(k, [(x, y - 24), (x + 11, y), (x, y + 13), (x - 11, y)], "#9CD8FF", line="#4A9BE0", alpha=min(1.0, c))
        s = P["sobe"]
        if s > 0.05:
            for j in range(4):
                x = -180 + j * 120
                y = cy + 600 - 380 * ((s + j * 0.25) % 1.0)
                ln(k, [(x, y), (x + 20, y - 30), (x, y - 60), (x + 20, y - 90)], "#FFFFFF", w=LINE * 1.4, alpha=0.8)


class Poca(_Prop):
    """Poça d'água (para eles, um lago). `splash` 0→1 respingos subindo e caindo (pulo na poça)."""

    def __init__(self):
        super().__init__("poca", "Poça", (1100, 600), (550, 500), 200, {"splash": 0.0})

    def paint(self, k, P):
        shape(k, ellipse_pts(0, -20, 430, 70, 0, 36), "#7FC8FA", line="#3E8FD6")
        ln(k, [(-250, -30), (-150, -40)], "#FFFFFF", w=LINE * 1.2)
        ln(k, [(120, -14), (230, -22)], "#FFFFFF", w=LINE * 1.2)
        s = max(0.0, min(1.0, P["splash"]))
        if 0.02 < s < 0.98:
            for j in range(10):
                a = math.pi * (0.1 + 0.8 * j / 9)
                rr = 80 + 300 * s
                x = math.cos(a) * rr
                y = -40 - math.sin(a) * rr * 1.1 + 260 * s * s
                shape(k, ellipse_pts(x, y, 16, 20, 0, 12), "#9CD8FF", line="#4A9BE0")


class Plantinha(_Prop):
    """Plantinha com carinha que cresce com a chuva (`cresce` 0→1) e agradece (`boca`)."""

    def __init__(self):
        super().__init__("plantinha", "Plantinha", (700, 900), (350, 850), 380, {"cresce": 1.0, "boca": 0.0, "lid": 0.0})

    def paint(self, k, P):
        g = 0.35 + 0.65 * max(0.0, min(1.0, P["cresce"]))
        shape(k, [(-130, -150), (130, -150), (100, 0), (-100, 0)], "#C98A4E", line="#8E5E33", smooth=False)
        box(k, -150, -190, 150, -150, "#D9A066", line="#8E5E33", r=10)
        h = 460 * g
        ln(k, [(0, -190), (0, -190 - h)], "#3DAE4E", w=LINE * 3)
        for sgn, y in ((-1, 0.45), (1, 0.7)):
            yy = -190 - h * y
            shape(k, [(0, yy), (sgn * 150 * g, yy - 90 * g), (sgn * 200 * g, yy - 10 * g), (sgn * 80 * g, yy + 20 * g)], "#4CC35E", line="#2E8B3E")
        cy = -190 - h - 70 * g
        for j in range(6):
            a = j * math.pi / 3
            shape(k, ellipse_pts(math.cos(a) * 70 * g, cy + math.sin(a) * 70 * g, 52 * g, 38 * g, a, 14), "#FF8AC6", line="#E0609A")
        shape(k, ellipse_pts(0, cy, 62 * g, 62 * g, 0, 20), "#FFE066", line="#D9A520")
        _carinha(k, 0, cy + 4, P, "#7A4A1E", "#FF9AB0", esc=0.85 * g)


PROPS.update({"nuvem": Nuvem, "poca": Poca, "plantinha": Plantinha})


# ───────────────────────── 11 Foguete pra Lua ─────────────────────────

class Foguete(_Prop):
    """Foguete de brinquedo (cabem os dois na janela): `fogo` 0→1 chama embaixo (fase em `chama`), `treme` 0→1."""

    def __init__(self):
        super().__init__("foguete", "Foguete", (700, 1000), (350, 900), 440, {"fogo": 0.0, "chama": 0.0, "treme": 0.0})

    def paint(self, k, P):
        dx = math.sin(P["chama"] * 40) * 6 * P["treme"]
        k.c.save()
        k.c.translate(dx, 0)
        f = max(0.0, min(1.0, P["fogo"]))
        if f > 0.05:
            h = 160 + 60 * math.sin(P["chama"] * 2 * math.pi * 3)
            shape(k, [(-70, -110), (70, -110), (0, -110 + h * f)], "#FF8A1F", line="#E0601A")
            shape(k, [(-40, -110), (40, -110), (0, -110 + h * 0.6 * f)], "#FFD21F", line="#E0A800")
        for sx in (-1, 1):                                          # aletas
            shape(k, [(sx * 95, -330), (sx * 190, -150), (sx * 175, -100), (sx * 95, -170)], "#E9545D", line="#B03A42")
        shape(k, [(-100, -110), (100, -110), (110, -500), (0, -820), (-110, -500)], "#F4F7FB", line="#9FB3C8")
        shape(k, [(-74, -640), (74, -640), (0, -820)], "#E9545D", line="#B03A42")
        shape(k, ellipse_pts(0, -450, 78, 78, 0, 30), "#FFD21F", line="#C99A1A")
        shape(k, ellipse_pts(0, -450, 58, 58, 0, 30), "#9CD8FF", line="#4A9BE0")
        ln(k, [(-30, -480), (-10, -500)], "#FFFFFF", w=LINE * 1.4)
        box(k, -100, -180, 100, -150, "#2F86F0", r=6)
        _estrela(k, 0, -290, 30, "#FFD21F")
        k.c.restore()


class LuaCara(_Prop):
    """Lua cheia com crateras e carinha; `brilho` 0→1 raios de luz (a luz do sol refletida); `boca`/`lid`."""

    def __init__(self):
        super().__init__("lua", "Lua", (900, 900), (450, 850), 400, {"brilho": 0.0, "boca": 0.0, "lid": 0.0})

    def paint(self, k, P):
        cy = -420
        b = P["brilho"]
        if b > 0.05:
            for j in range(12):
                a = j * math.pi / 6
                ln(k, [(math.cos(a) * 320, cy + math.sin(a) * 320), (math.cos(a) * (320 + 80 * b), cy + math.sin(a) * (320 + 80 * b))],
                   "#FFF3B0", w=LINE * 2)
        shape(k, ellipse_pts(0, cy, 300, 300, 0, 40), "#F2EED8", line="#B8B39A")
        for x, y, r in ((-150, -120, 50), (120, -170, 36), (-60, 150, 40), (170, 90, 30), (-200, 60, 24)):
            shape(k, ellipse_pts(x, cy + y, r, r * 0.85, 0, 18), "#DDD7B8", line="#B8B39A")
        _carinha(k, 0, cy + 10, P, "#6E6A55", "#FFB0B8", esc=1.6)


class Terra(_Prop):
    """Planeta Terra simpático (azul com continentes verdes) e carinha; `gira` 0→1."""

    def __init__(self):
        super().__init__("terra", "Terra", (700, 700), (350, 650), 300, {"gira": 0.0, "boca": 0.0, "lid": 0.0})

    def paint(self, k, P):
        cy = -320
        shape(k, ellipse_pts(0, cy, 240, 240, 0, 40), "#2F86F0", line="#1F5FB8")
        g = P["gira"] * 300
        for x, y, rx, ry in ((-120, -80, 90, 60), (90, 40, 80, 100), (-40, 140, 70, 40)):
            xx = ((x + g + 240) % 480) - 240
            if abs(xx) < 200:
                shape(k, ellipse_pts(xx, cy + y, rx * (1 - abs(xx) / 400), ry, 0, 20), "#2DBE5A", line="#1E8A3E")
        _carinha(k, 0, cy + 10, P, "#123A6E", "#FF9AB0", esc=1.2)


class Cometa(_Prop):
    """Cometa com cauda brilhante (de cima à esquerda para baixo à direita)."""

    def __init__(self):
        super().__init__("cometa", "Cometa", (1200, 600), (600, 500), 260, {"brilho": 1.0})

    def paint(self, k, P):
        for j, (w, c) in enumerate(((60, "#FFE680"), (40, "#FFF3B0"), (20, "#FFFFFF"))):
            shape(k, [(200, -250 - w), (-450, -420), (200, -250 + w)], c, smooth=True)
        _estrela(k, 210, -250, 70, "#FFD21F")


PROPS.update({"foguete": Foguete, "lua": LuaCara, "terra": Terra, "cometa": Cometa})


# ───────────────────────── 12 Méé, Carneirinho! ─────────────────────────


class Carneirinho(_Prop):
    """Carneirinho fofo (lã = nuvenzinha de bolinhas brancas, carinha rosada, perninhas cinza).
    Canais: `mee` 0→1 abre a boca (méé!); `pulo` 0→1 arco do pulo; `senta` 0→1 senta (perninhas dobram);
    `balanco` −1…1 inclina o corpo (dança); `pe` 0→1 levanta a patinha da frente (bate o pé);
    `esconde` 0→1 some cabeça e perninhas: vira uma nuvem (esconde-esconde); `lado` 1 olha p/ direita, −1 p/ esquerda;
    `come` 0→1 abaixa a cabeça (come capim); `lid` fecha os olhos; `altura` multiplica a altura do pulo (cerquinha)."""

    def __init__(self):
        super().__init__("carneirinho", "Carneirinho", (1000, 780), (500, 740), 440,
                         {"mee": 0.0, "pulo": 0.0, "senta": 0.0, "balanco": 0.0, "pe": 0.0, "esconde": 0.0, "lado": 1.0,
                          "come": 0.0, "lid": 0.0, "altura": 1.0})

    def paint(self, k, P):
        sx = 1.0 if P["lado"] >= 0 else -1.0
        senta = max(0.0, min(1.0, P["senta"]))
        y0 = -150 * P.get("altura", 1.0) * math.sin(math.pi * max(0.0, min(1.0, P["pulo"]))) + 70 * senta
        ang = 0.12 * max(-1.0, min(1.0, P["balanco"]))
        esc = max(0.0, min(1.0, P["esconde"]))
        come = max(0.0, min(1.0, P["come"]))
        cx, cy = 0.0, -250.0

        def T(x, y):
            x, y = x * sx, y
            dx, dy = x - cx, y - cy
            c, s = math.cos(ang), math.sin(ang)
            return (cx + dx * c - dy * s, cy + dx * s + dy * c + y0)

        def oval(x, y, rx, ry, fill, line, a=0.0, alpha=1.0):
            q = T(x, y)
            shape(k, ellipse_pts(q[0], q[1], rx, ry, a + ang, 22), fill, line=line, alpha=alpha)

        branco, lin = "#FFFFFF", _mix("#B9C6D8", "#BFD6EA", esc)
        perna, casco = "#5A5A66", "#33333C"
        if esc < 0.5:                                                       # perninhas (atrás e na frente)
            for x, frente in ((-120, False), (60, False), (-60, True), (130, True)):
                lev = 60 * max(0.0, min(1.0, P["pe"])) if (frente and x > 0) else 0.0
                topo, base = (x, -150), (x + (14 if senta > 0.5 else 0), -10 - lev - 120 * senta * (0.7 if frente else 1))
                if senta > 0.9 and not frente:
                    continue
                a, b = T(*topo), T(*base)
                b = (b[0], min(b[1] + 0 * y0, b[1]))
                _capsula(k, a, b, 17, dark(perna, 0.9) if not frente else perna, casco)
                shape(k, ellipse_pts(b[0], b[1] + 6, 22, 13, 0, 14), casco, line=casco)
        # lã: bolinhas que formam a nuvem do corpo (contorno por fora, depois o recheio sem linha)
        bolas = [(-190, -250, 78), (-130, -320, 86), (-30, -350, 92), (80, -330, 86), (170, -270, 76), (150, -190, 72),
                 (40, -160, 82), (-80, -160, 82), (-180, -190, 70), (0, -250, 120)]
        for x, y, r in bolas:
            oval(x, y, r, r * 0.92, branco, lin)
        for x, y, r in bolas:
            q = T(x, y)
            k.shape(ellipse_pts(q[0], q[1], r - 5, r * 0.92 - 5, ang, 22), fill=_rgba(branco), line=0)
        for x, y in ((-120, -280), (30, -300), (110, -230), (-40, -200), (-170, -230)):   # cachinhos (traço)
            q = T(x, y)
            ln(k, [(q[0] - 16, q[1] + 4), (q[0] - 4, q[1] - 10), (q[0] + 10, q[1] - 2), (q[0] + 2, q[1] + 8)], lin, w=LINE * 0.8)
        oval(-240, -280, 40, 36, branco, lin)                              # rabinho
        if esc > 0.5:
            return
        # cabeça (na frente, do lado que ele olha)
        hx, hy = 210, -300 + 90 * come
        rosto, rlin = "#FBE2D4", "#D8A48E"
        for s_ in (-1, 1):                                                 # orelhinhas caídas
            q = T(hx + s_ * 78, hy - 30)
            shape(k, ellipse_pts(q[0], q[1], 48, 22, ang + s_ * 0.5 * sx, 16), "#F6C2B2", line=rlin)
        oval(hx, hy, 82, 92, rosto, rlin)
        for dx, dy, r in ((-40, -80, 34), (0, -98, 38), (40, -80, 34)):    # topete de lã
            oval(hx + dx, hy + dy, r, r * 0.9, branco, lin)
        q = T(hx, hy + 6)
        _carinha(k, q[0], q[1], {"lid": P["lid"], "boca": max(0.0, min(1.0, P["mee"]))}, "#6A3A2E", "#FF8FA8", esc=1.15)


class Cerquinha(_Prop):
    """Cerquinha de madeira do campo (três estacas e duas travessas) — o carneirinho e a turma pulam por cima."""

    def __init__(self):
        super().__init__("cerquinha", "Cerquinha", (760, 340), (380, 310), 230, {})

    def paint(self, k, P):
        mad, lin = "#D9A066", "#9A6634"
        for y in (-170, -80):
            box(k, -330, y - 18, 330, y + 18, mad, line=lin, r=8)
        for x in (-290, 0, 290):
            shape(k, [(x - 28, 0), (x + 28, 0), (x + 28, -210), (x, -244), (x - 28, -210)], mad, line=lin, smooth=False)
            ln(k, [(x - 8, -40), (x - 8, -150)], dark(mad, 0.85), w=LINE * 0.7)


class Capim(_Prop):
    """Tufo de capim verdinho. `come` 0→1 vai sumindo de cima para baixo (nhac!)."""

    def __init__(self):
        super().__init__("capim", "Capim", (420, 320), (210, 300), 200, {"come": 0.0})

    def paint(self, k, P):
        g = 1.0 - 0.75 * max(0.0, min(1.0, P["come"]))
        for x, h, inc, col in ((-110, 170, -0.5, "#49B84F"), (-60, 230, -0.25, "#5CCB5F"), (0, 260, 0.0, "#49B84F"),
                               (60, 220, 0.3, "#5CCB5F"), (110, 160, 0.55, "#49B84F"), (-20, 190, 0.12, "#6BD86A")):
            hh = h * g
            shape(k, [(x - 22, 0), (x + inc * hh, -hh), (x + 22, 0)], col, line="#2E8B3E")


PROPS.update({"carneirinho": Carneirinho, "cerquinha": Cerquinha, "capim": Capim})


# ───────────────────────── 13 Andar de Pinguim ─────────────────────────


class Pinguim(_Prop):
    """Pinguim simpático "de casaca preta" com gravatinha vermelha. Canais:
    `anda` (fase contínua: cada +1 = um passinho de cada lado — ginga e pezinho grudado);
    `asas` 0→1 abre as asinhas (bate a asinha / tchau); `bico` 0→1 abre o bico; `barriga` 0→1 deita de barriga
    (escorregar no gelo / nadar); `pulo` 0→1 arco do pulo; `lado` 1 olha p/ direita, −1 p/ esquerda; `lid` fecha os olhos;
    `gravata` 1 mostra a gravatinha."""

    def __init__(self):
        super().__init__("pinguim", "Pinguim", (900, 760), (450, 720), 380,
                         {"anda": 0.0, "asas": 0.0, "bico": 0.0, "barriga": 0.0, "pulo": 0.0, "lado": 1.0, "lid": 0.0,
                          "gravata": 1.0})

    def paint(self, k, P):
        sx = 1.0 if P["lado"] >= 0 else -1.0
        fase = math.sin(2 * math.pi * P["anda"])
        bar = max(0.0, min(1.0, P["barriga"]))
        ginga = 0.15 * fase * (1 - bar)
        ang = ginga + 1.42 * bar * sx                                  # de barriga: cabeça para a frente (para onde olha)
        y0 = -170 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"]))) + 70 * bar
        piv = (0.0, -12.0 - 180 * bar)

        def T(x, y):
            x = x * sx
            dx, dy = x - piv[0], y - piv[1]
            c, s = math.cos(ang), math.sin(ang)
            return (piv[0] + dx * c - dy * s, piv[1] + dx * s + dy * c + y0)

        def oval(x, y, rx, ry, fill, line, a=0.0):
            q = T(x, y)
            shape(k, ellipse_pts(q[0], q[1], rx, ry, a * sx + ang, 24), fill, line=line)

        preto, plin, branco, blin, lar, llar = "#2E3A4F", "#1C2433", "#FFFFFF", "#C9D6E6", "#FF9A1F", "#C9661A"
        for side in (-1, 1):                                            # pezinhos de pato (pé grudadinho)
            lev = 22 * max(0.0, side * fase) * (1 - bar)
            q = T(side * 42 + 18, -8 - lev) if bar < 0.5 else T(side * 40, -8)
            shape(k, ellipse_pts(q[0], q[1], 46, 16, ang, 16), lar, line=llar)
        a = max(0.0, min(1.0, P["asas"]))
        for side in (-1, 1):                                            # asinhas (atrás do corpo quando fechadas)
            ombro = (side * 96, -275)
            th = side * (0.25 + 1.15 * a)                               # 0 = caída junto ao corpo, 1 = aberta
            ponta = (ombro[0] + math.sin(th) * 150, ombro[1] + math.cos(th) * 150)
            m = ((ombro[0] + ponta[0]) / 2, (ombro[1] + ponta[1]) / 2)
            oval(m[0], m[1], 30, 82, preto, plin, a=-th)
        oval(0, -195, 124, 178, preto, plin)                             # corpo (casaca)
        oval(0, -180, 90, 150, branco, blin)                             # barriga + rostinho branco
        oval(0, -300, 70, 46, branco, blin)
        q = T(0, -230)
        k.shape(ellipse_pts(q[0], q[1], 84, 120, ang, 24), fill=_rgba(branco), line=0)
        for side in (-1, 1):                                            # olhos e bochechas
            e = T(side * 32 + 6, -305)
            if P["lid"] > 0.5:
                ln(k, [(e[0] - 14, e[1]), (e[0], e[1] - 9), (e[0] + 14, e[1])], plin, w=LINE)
            else:
                shape(k, ellipse_pts(e[0], e[1], 15, 19, 0, 14), branco, line=plin)
                k.dot(e[0] + 3 * sx, e[1] + 4, 8, _rgba("#111111"))
            b = T(side * 58 + 6, -272)
            k.shape(ellipse_pts(b[0], b[1], 15, 9, 0, 12), fill=_rgba("#FF9AB0", 0.8), line=0)
        o = max(0.0, min(1.0, P["bico"]))                                 # bico de frente (abre no "pinguim!")
        if o > 0.1:
            q = T(0, -262)
            shape(k, ellipse_pts(q[0], q[1], 18, 8 + 10 * o, ang, 14), "#C63A3A", line=llar)
            shape(k, [T(-22, -258 + 4 * o), T(22, -258 + 4 * o), T(0, -236 + 8 * o)], lar, line=llar)
        shape(k, [T(-30, -284 - 6 * o), T(30, -284 - 6 * o), T(0, -252 - 8 * o)], lar, line=llar)
        if P.get("gravata", 1.0) > 0.5:                                  # gravatinha vermelha
            for side in (-1, 1):
                shape(k, [T(0, -226), T(side * 34, -244), T(side * 34, -206)], "#E9545D", line="#B83A42", smooth=False)
            q = T(0, -226)
            shape(k, ellipse_pts(q[0], q[1], 10, 10, 0, 12), "#E9545D", line="#B83A42")


PROPS.update({"pinguim": Pinguim})


# ───────────────────────── 14 Castelo de Areia ─────────────────────────

AREIA, AREIA_L, AREIA_E = "#F3D58A", "#C9A24E", "#E6C26E"


class CasteloAreia(_Prop):
    """Castelo de areia que cresce: `nivel` 0 = montinho, 1 = torre, 2 = + ponte e torre pequena, 3 = + bandeira;
    `derruba` 0→1 a onda desmancha (vira montinho achatado com pedacinhos)."""

    def __init__(self):
        super().__init__("castelo_areia", "Castelo de areia", (1000, 760), (500, 720), 460, {"nivel": 3.0, "derruba": 0.0})

    def paint(self, k, P):
        nv = max(0.0, min(3.0, P["nivel"]))
        d = max(0.0, min(1.0, P["derruba"]))
        esm = 1 - 0.85 * d                                              # altura que sobra quando a onda passa
        shape(k, ellipse_pts(0, -10, 300 + 60 * d, 46 + 10 * d, 0, 30), AREIA_E, line=AREIA_L)    # base espalhada
        if d > 0.6:
            for x, y, r in ((-260, -20, 26), (230, -14, 22), (-120, -40, 18), (300, -30, 16), (60, -46, 20)):
                shape(k, ellipse_pts(x, y, r, r * 0.7, 0, 12), AREIA, line=AREIA_L)
        h0 = 120 * esm
        shape(k, [(-220, -10), (220, -10), (200, -10 - h0), (-200, -10 - h0)], AREIA, line=AREIA_L, smooth=False)   # muralha
        if d < 0.7:
            for x in range(-200, 201, 50):                              # ameias
                box(k, x - 16, -10 - h0 - 26 * esm, x + 16, -10 - h0, AREIA, line=AREIA_L, r=3)
        if nv >= 1 and d < 0.9:                                          # torre do meio (feita com o baldinho)
            t = min(1.0, nv) * esm
            shape(k, [(-80, -10 - h0), (80, -10 - h0), (66, -10 - h0 - 200 * t), (-66, -10 - h0 - 200 * t)], AREIA, line=AREIA_L, smooth=False)
            for x in (-60, -20, 20, 60):
                box(k, x - 14, -10 - h0 - 200 * t - 26 * t, x + 14, -10 - h0 - 200 * t, AREIA, line=AREIA_L, r=3)
            shape(k, ellipse_pts(0, -10 - h0 - 110 * t, 22, 30 * t, 0, 14), "#8C6A2E", line=AREIA_L)          # janela
            for y in (-40, -90, -150):                                    # marquinhas do baldinho
                ln(k, [(-62, -10 - h0 + y * t * 0.9), (62, -10 - h0 + y * t * 0.9)], AREIA_L, w=LINE * 0.6)
        if nv >= 2 and d < 0.8:                                          # ponte + torrinhas laterais
            for sx in (-1, 1):
                shape(k, [(sx * 170 - 46, -10 - h0), (sx * 170 + 46, -10 - h0), (sx * 170 + 38, -10 - h0 - 90 * esm),
                          (sx * 170 - 38, -10 - h0 - 90 * esm)], AREIA, line=AREIA_L, smooth=False)
            shape(k, [(-60, -10), (60, -10), (60, -60 * esm), (40, -84 * esm), (-40, -84 * esm), (-60, -60 * esm)], "#8C6A2E", line=AREIA_L)
        if nv >= 3 and d < 0.5:                                          # bandeirinha no alto
            topo = -10 - h0 - 226 * esm
            ln(k, [(0, topo), (0, topo - 110)], "#7A5A2E", w=LINE * 1.2)
            shape(k, [(2, topo - 110), (78, topo - 92), (2, topo - 70)], "#E9545D", line="#B83A42", smooth=False)
        for x, y in ((-150, -50), (130, -60), (-40, -30)):                # conchinhas
            shape(k, ellipse_pts(x, y * esm, 12, 9, 0.3, 10), "#FFB3C7", line="#E07A9A")


class Siri(_Prop):
    """Siri (caranguejinho) vermelho-alaranjado: `anda` fase das perninhas (anda de ladinho), `pinca` 0→1 abre as pinças,
    `aceno` 0→1 levanta a pinça direita (tchauzinho), `pulo`, `lid`."""

    def __init__(self):
        super().__init__("siri", "Siri", (760, 560), (380, 520), 200, {"anda": 0.0, "pinca": 0.0, "aceno": 0.0, "pulo": 0.0, "lid": 0.0})

    def paint(self, k, P):
        cor, lin = "#F2603A", "#B83A1E"
        y0 = -90 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        f = math.sin(2 * math.pi * P["anda"])
        for side in (-1, 1):                                             # perninhas (3 de cada lado)
            for j in range(3):
                bx = side * (60 + 26 * j)
                lev = 14 * f * (1 if (j % 2 == 0) == (side > 0) else -1)
                ln(k, [(bx, y0 - 60), (bx + side * 40, y0 - 40 - lev), (bx + side * 52, y0 - 4 - max(0, lev))], lin, w=LINE * 1.5)
        a = max(0.0, min(1.0, P["aceno"]))
        for side in (-1, 1):                                             # braços + pinças
            up = a if side > 0 else 0.0
            om = (side * 100, y0 - 100)
            pin = (side * (170 - 40 * up), y0 - 170 - 120 * up)
            ln(k, [om, ((om[0] + pin[0]) / 2 + side * 20, (om[1] + pin[1]) / 2), pin], cor, w=LINE * 2.6)
            ab = 0.25 + 0.5 * max(0.0, min(1.0, P["pinca"]))
            shape(k, ellipse_pts(pin[0], pin[1], 34, 26, 0, 16), cor, line=lin)
            shape(k, [(pin[0] + side * 10, pin[1] - 8), (pin[0] + side * 60, pin[1] - 40 * ab - 10), (pin[0] + side * 30, pin[1] - 4)],
                  cor, line=lin, smooth=False)
        shape(k, ellipse_pts(0, y0 - 90, 120, 66, 0, 28), cor, line=lin)          # casco
        for side in (-1, 1):                                             # olhos no talinho
            ln(k, [(side * 30, y0 - 140), (side * 40, y0 - 186)], lin, w=LINE * 1.4)
            if P["lid"] > 0.5:
                ln(k, [(side * 40 - 12, y0 - 196), (side * 40, y0 - 188), (side * 40 + 12, y0 - 196)], "#222222", w=LINE)
            else:
                shape(k, ellipse_pts(side * 40, y0 - 196, 18, 20, 0, 14), "#FFFFFF", line=lin)
                k.dot(side * 40 + 3, y0 - 192, 8, _rgba("#1F1F1F"))
        ln(k, [(-30, y0 - 80), (0, y0 - 66), (30, y0 - 80)], "#7A2412", w=LINE * 1.2)
        for side in (-1, 1):
            k.shape(ellipse_pts(side * 66, y0 - 86, 14, 9, 0, 12), fill=_rgba("#FFB0A0", 0.85), line=0)


class Baldinho(_Prop):
    """Baldinho de praia vermelho com pazinha amarela. `vira` 0→1 vira de boca pra baixo (faz a torre); `cheio` 1 mostra areia."""

    def __init__(self):
        super().__init__("baldinho", "Baldinho e pazinha", (560, 520), (280, 480), 220, {"vira": 0.0, "cheio": 1.0})

    def paint(self, k, P):
        v = max(0.0, min(1.0, P["vira"]))
        ang = math.pi * v
        def T(x, y):
            c, s = math.cos(ang), math.sin(ang)
            cx, cy = 0.0, -90.0
            dx, dy = x - cx, y - cy
            return (cx + dx * c - dy * s, cy + dx * s + dy * c)
        shape(k, [T(-80, -170), T(80, -170), T(60, -10), T(-60, -10)], "#E9545D", line="#B83A42", smooth=False)
        shape(k, [T(-88, -180), T(88, -180), T(88, -160), T(-88, -160)], "#FF7A85", line="#B83A42", smooth=False)
        if P.get("cheio", 1.0) > 0.5 and v < 0.3:
            shape(k, ellipse_pts(0, -176, 76, 18, 0, 18), AREIA, line=AREIA_L)
        if v < 0.5:                                                        # alça e pazinha (somem com o balde virado)
            ln(k, [T(-80, -170), T(0, -250), T(80, -170)], "#B83A42", w=LINE * 1.1)
            ln(k, [(110, -10), (150, -200)], "#F2B21A", w=LINE * 2.2)
            shape(k, [(100, -10), (124, -10), (130, 30), (94, 30)], "#FFD23F", line="#C99A12", smooth=False)


class Onda(_Prop):
    """Onda do mar que chega na areia: crista azul com espuma branca enrolando. `altura` 0→1 tamanho; `quebra` 0→1 a espuma
    desaba para a frente (direção do `lado`)."""

    def __init__(self):
        super().__init__("onda", "Onda", (1300, 900), (650, 860), 520, {"altura": 1.0, "quebra": 0.0, "lado": 1.0})

    def paint(self, k, P):
        sx = 1.0 if P["lado"] >= 0 else -1.0
        h = 140 + 420 * max(0.0, min(1.0, P["altura"]))
        q = max(0.0, min(1.0, P["quebra"]))
        corpo = [(-500 * sx, 0), (-500 * sx, -h * 0.35), (-260 * sx, -h * 0.75), (0, -h), (170 * sx, -h * (0.95 - 0.4 * q)),
                 (280 * sx, -h * (0.7 - 0.5 * q)), (310 * sx, -h * 0.3 * (1 - q)), (500 * sx, 0)]   # cabe no quadro do nível (±650)
        shape(k, corpo, "#4FA8E8", line="#2E7FC0")
        shape(k, [(x * 0.92, y * 0.6) for x, y in corpo], "#7CC4F5", line="#4FA8E8")
        for j in range(7):                                                # espuma
            a = j / 6
            x = (-60 + 380 * a) * sx
            y = -h * (1 - 0.6 * a * (0.4 + q))
            shape(k, ellipse_pts(x, y, 46 - 3 * j, 36 - 2 * j, 0, 14), "#FFFFFF", line="#BFE0F5")
        for x in (-400, -160, 120):
            ln(k, [(x * sx, -h * 0.4), ((x + 80) * sx, -h * 0.45)], "#BFE6FF", w=LINE)


class Peixinho(_Prop):
    """Peixinho dourado com carinha: `nada` fase do rabinho; `boca` 0→1 (blub); `lado`."""

    def __init__(self):
        super().__init__("peixinho", "Peixinho", (560, 420), (280, 380), 170, {"nada": 0.0, "boca": 0.0, "lado": 1.0, "lid": 0.0})

    def paint(self, k, P):
        sx = 1.0 if P["lado"] >= 0 else -1.0
        w = math.sin(2 * math.pi * P["nada"]) * 22
        cor, lin = "#FF9A2E", "#C9661A"
        shape(k, [(-90 * sx, -110), (-190 * sx, -170 + w), (-170 * sx, -110), (-190 * sx, -50 + w)], cor, line=lin)   # rabo
        shape(k, ellipse_pts(0, -110, 120, 76, 0, 28), cor, line=lin)
        shape(k, [(-10 * sx, -180), (50 * sx, -210), (60 * sx, -176)], cor, line=lin)                                   # barbatana
        for x in (-40, 0):
            ln(k, [(x * sx, -170), ((x + 10) * sx, -60)], "#FFC56E", w=LINE)
        e = (56 * sx, -128)
        if P["lid"] > 0.5:
            ln(k, [(e[0] - 12, e[1]), (e[0], e[1] - 8), (e[0] + 12, e[1])], "#222222", w=LINE)
        else:
            shape(k, ellipse_pts(e[0], e[1], 18, 20, 0, 14), "#FFFFFF", line=lin)
            k.dot(e[0] + 4 * sx, e[1] + 3, 8, _rgba("#1F1F1F"))
        b = max(0.0, min(1.0, P["boca"]))
        shape(k, ellipse_pts(104 * sx, -96, 10, 6 + 10 * b, 0, 12), "#C63A3A", line=lin)
        k.shape(ellipse_pts(70 * sx, -96, 13, 8, 0, 12), fill=_rgba("#FF9AB0", 0.8), line=0)


PROPS.update({"castelo_areia": CasteloAreia, "siri": Siri, "baldinho": Baldinho, "onda": Onda, "peixinho": Peixinho})


# ───────────────────────── 15 Bolha de Sabão ─────────────────────────


class Bolha(_Prop):
    """Bolha de sabão transparente com reflexo de arco-íris. `tam` 0→1 cresce (assoprando); `estoura` 0→1 vira respingos
    (ploc!); `balanco` −1…1 ondula (achata de um lado). A origem é o FUNDO da bolha (para ela 'carregar' quem está dentro)."""

    def __init__(self):
        super().__init__("bolha", "Bolha de sabão", (1000, 980), (500, 900), 420, {"tam": 1.0, "estoura": 0.0, "balanco": 0.0})

    def paint(self, k, P):
        t = max(0.0, min(1.0, P["tam"]))
        e = max(0.0, min(1.0, P["estoura"]))
        r = 40 + 340 * t
        cy = -r - 10
        sq = 0.06 * math.sin(math.pi * P["balanco"])
        if e < 0.15:
            shape(k, ellipse_pts(0, cy, r * (1 + sq), r * (1 - sq), 0, 48), "#D8F2FF", line="#4FA8E8", alpha=0.34, w=LINE * 1.5)
            ln(k, [(math.cos(a) * r * 0.93 * (1 + sq), cy + math.sin(a) * r * 0.93 * (1 - sq)) for a in [i * 0.2 for i in range(33)]],
               "#FFFFFF", w=LINE * 1.2, alpha=0.7)                                  # borda brilhante por dentro
            for j, (cor, d) in enumerate((("#FF9AC8", 0.86), ("#FFE066", 0.80), ("#9BE7FF", 0.74))):   # reflexos de arco-íris
                a0 = 3.6 + 0.12 * j
                pts = [(math.cos(a0 + i * 0.09) * r * d, cy + math.sin(a0 + i * 0.09) * r * d) for i in range(14)]
                ln(k, pts, cor, w=LINE * 1.6, alpha=0.7)
            shape(k, ellipse_pts(-r * 0.42, cy - r * 0.45, r * 0.16, r * 0.09, -0.6, 16), "#FFFFFF", alpha=0.9)        # brilho
            k.dot(-r * 0.2, cy - r * 0.62, max(4, r * 0.035), _rgba("#FFFFFF", 0.9))
        else:                                                              # ploc! respingos e tracinhos
            for j in range(12):
                a = j * math.pi / 6
                d = r * (0.6 + 0.5 * e)
                x, y = math.cos(a) * d, cy + math.sin(a) * d
                shape(k, ellipse_pts(x, y, 10 * (1 - e) + 4, 10 * (1 - e) + 4, 0, 10), "#BFE6FF", line="#7FC4EE", alpha=1 - 0.7 * e)
                ln(k, [(math.cos(a) * r * 0.35, cy + math.sin(a) * r * 0.35), (math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55)],
                   "#9BD3F5", w=LINE, alpha=max(0.0, 1 - e))


class Gato(_Prop):
    """Gatinho laranja listrado, sentado. `miau` 0→1 abre a boca; `assusta` 0→1 olhos arregalados e pelo arrepiado;
    `aceno` 0→1 levanta a patinha; `rabo` fase do rabo; `lado`; `lid`."""

    def __init__(self):
        super().__init__("gato", "Gato", (760, 760), (380, 720), 330,
                         {"miau": 0.0, "assusta": 0.0, "aceno": 0.0, "rabo": 0.0, "lado": 1.0, "lid": 0.0})

    def paint(self, k, P):
        sx = 1.0 if P["lado"] >= 0 else -1.0
        cor, lin, cl = "#FF9F43", "#C96F1E", "#FFE3C2"
        a = max(0.0, min(1.0, P["assusta"]))
        w = math.sin(2 * math.pi * P["rabo"]) * 30
        ln(k, [(-90 * sx, -40), (-170 * sx, -90 + w * 0.3), (-190 * sx, -190 + w), (-150 * sx, -230 + w)], lin, w=LINE * 5)   # rabo
        ln(k, [(-90 * sx, -40), (-170 * sx, -90 + w * 0.3), (-190 * sx, -190 + w), (-150 * sx, -230 + w)], cor, w=LINE * 3.6)
        shape(k, ellipse_pts(0, -95, 105, 95, 0, 28), cor, line=lin)                        # corpo
        shape(k, ellipse_pts(0, -80, 55, 60, 0, 20), cl, line=lin)                          # barriguinha
        for s_ in (-1, 1):                                                                  # patinhas da frente
            up = 90 * max(0.0, min(1.0, P["aceno"])) if s_ * sx > 0 else 0
            shape(k, ellipse_pts(s_ * 45, -14 - up, 26, 18, 0, 14), cl, line=lin)
        hy = -230
        if a > 0.3:                                                                         # pelo arrepiado
            for j in range(9):
                ang = math.pi * (1.05 + 0.9 * j / 8)
                ln(k, [(math.cos(ang) * 95, hy + math.sin(ang) * 85), (math.cos(ang) * (95 + 26 * a), hy + math.sin(ang) * (85 + 26 * a))], lin, w=LINE)
        for s_ in (-1, 1):                                                                  # orelhas
            shape(k, [(s_ * 30, hy - 70), (s_ * 85, hy - 125 - 20 * a), (s_ * 92, hy - 40)], cor, line=lin, smooth=False)
            shape(k, [(s_ * 45, hy - 72), (s_ * 80, hy - 108 - 20 * a), (s_ * 82, hy - 55)], "#FFB3C1", smooth=False)
        shape(k, ellipse_pts(0, hy, 100, 88, 0, 28), cor, line=lin)                          # cabeça
        for x in (-40, 0, 40):                                                              # listrinhas
            ln(k, [(x, hy - 86), (x * 0.8, hy - 60)], lin, w=LINE * 1.2)
        shape(k, ellipse_pts(0, hy + 30, 46, 32, 0, 18), cl, line=lin)                      # focinho
        for s_ in (-1, 1):
            ex = s_ * 36
            if P["lid"] > 0.5:
                ln(k, [(ex - 14, hy - 10), (ex, hy - 18), (ex + 14, hy - 10)], "#3A2A1A", w=LINE)
            else:
                rr = 14 + 8 * a
                shape(k, ellipse_pts(ex, hy - 12, rr, rr * 1.15, 0, 14), "#FFFFFF", line=lin)
                k.dot(ex + 3 * sx, hy - 8, 7 - 3 * a, _rgba("#2A1A0A"))
            for dy in (-6, 6):                                                              # bigodes
                ln(k, [(s_ * 40, hy + 30 + dy), (s_ * 110, hy + 22 + dy * 1.6)], "#7A5030", w=LINE * 0.7)
        shape(k, [(-10, hy + 16), (10, hy + 16), (0, hy + 27)], "#FF7FA0", line="#C9506E", smooth=False)   # narizinho
        m = max(0.0, min(1.0, P["miau"]))
        if m > 0.1:
            shape(k, ellipse_pts(0, hy + 44, 14, 6 + 16 * m, 0, 14), "#8A2E3E", line=lin)
        else:
            ln(k, [(-16, hy + 38), (0, hy + 44), (16, hy + 38)], lin, w=LINE)


class Potinho(_Prop):
    """Potinho de fazer bolha (rosa, tampinha amarela) com a varinha de argola ao lado."""

    def __init__(self):
        super().__init__("potinho", "Potinho de bolha", (420, 460), (210, 420), 200, {"varinha": 1.0})

    def paint(self, k, P):
        shape(k, [(-60, 0), (60, 0), (55, -150), (-55, -150)], "#FF7FB8", line="#D14F8C", smooth=False)
        shape(k, [(-50, -10), (50, -10), (46, -100), (-46, -100)], "#CFEFFF", alpha=0.6)
        box(k, -45, -190, 45, -150, "#FFD23F", line="#D9A520", r=8)
        if P.get("varinha", 1.0) > 0.5:
            ln(k, [(110, 0), (130, -230)], "#FFD23F", w=LINE * 1.6)
            shape(k, ellipse_pts(134, -268, 34, 34, 0, 20), "#CFEFFF", line="#FFD23F", alpha=0.4)


PROPS.update({"bolha": Bolha, "gato": Gato, "potinho": Potinho})


# ───────────────────────── 17 Que Forma É Essa? ─────────────────────────


class ComidaForma(_Prop):
    """Comida-personagem com uma forma geométrica: `tipo` 0 pizza (círculo), 1 torrada (quadrado), 2 queijo (triângulo),
    3 ovo (oval), 4 presente (quadrado com laço). `brilho` 0→1 acende o contorno da forma (a resposta: "círculo!");
    `pulo` 0→1 pulinho; `boca` abre a boquinha; `lid` fecha os olhos."""

    FORMAS = ("circulo", "quadrado", "triangulo", "oval", "quadrado")

    def __init__(self):
        super().__init__("comida_forma", "Comida com forma", (700, 700), (350, 660), 300,
                         {"tipo": 0.0, "brilho": 0.0, "pulo": 0.0, "boca": 0.0, "lid": 0.0})

    def _contorno(self, k, forma, cy, esc, cor, w):
        if forma == "circulo":
            pts = [(math.cos(a) * 150 * esc, cy + math.sin(a) * 150 * esc) for a in [i * 0.2 for i in range(33)]]
        elif forma == "quadrado":
            s = 150 * esc
            pts = [(-s, cy - s), (s, cy - s), (s, cy + s), (-s, cy + s), (-s, cy - s)]
        elif forma == "triangulo":
            pts = [(-170 * esc, cy + 120 * esc), (0, cy - 160 * esc), (170 * esc, cy + 120 * esc), (-170 * esc, cy + 120 * esc)]
        else:
            pts = [(math.cos(a) * 118 * esc, cy + math.sin(a) * 158 * esc) for a in [i * 0.2 for i in range(33)]]
        ln(k, pts, cor, w=w)

    def paint(self, k, P):
        t = int(round(max(0.0, min(4.0, P["tipo"]))))
        y0 = -120 * math.sin(math.pi * max(0.0, min(1.0, P["pulo"])))
        cy = -170 + y0
        b = max(0.0, min(1.0, P["brilho"]))
        forma = self.FORMAS[t]
        if b > 0.02:                                                     # brilho da forma (fica atrás)
            self._contorno(k, forma, cy, 1.0 + 0.12 * b, "#FFF27A", LINE * (6 + 6 * b))
        if t == 0:                                                       # pizza
            shape(k, ellipse_pts(0, cy, 140, 140, 0, 36), "#E9A15A", line="#B9712E")
            shape(k, ellipse_pts(0, cy, 118, 118, 0, 36), "#FFCE4A", line="#E0A020")
            for x, y in ((-60, -50), (55, -40), (-20, 55), (70, 50), (-75, 25)):
                shape(k, ellipse_pts(x, cy + y, 20, 20, 0, 14), "#E9545D", line="#B83A42")
        elif t == 1:                                                     # torrada
            box(k, -135, cy - 135, 135, cy + 135, "#B97A2E", line="#8A5520", r=26)
            box(k, -112, cy - 112, 112, cy + 112, "#F2C27A", line="#D19A50", r=18)
        elif t == 2:                                                     # queijo
            shape(k, [(-150, cy + 105), (0, cy - 140), (150, cy + 105)], "#FFD23F", line="#D9A520", smooth=False)
            for x, y, r in ((-40, 40, 18), (45, 60, 14), (0, -20, 12), (70, 20, 10)):
                shape(k, ellipse_pts(x, cy + y, r, r, 0, 12), "#F2B21F", line="#D9A520")
        elif t == 3:                                                     # ovo
            shape(k, ellipse_pts(0, cy, 105, 140, 0, 36), "#FFF8EC", line="#D9CBB4")
        else:                                                            # presente
            box(k, -130, cy - 130, 130, cy + 130, "#3C8BF0", line="#2A64B8", r=10)
            box(k, -22, cy - 130, 22, cy + 130, "#FFD23F", line="#D9A520", r=4)
            box(k, -130, cy - 22, 130, cy + 22, "#FFD23F", line="#D9A520", r=4)
            for s_ in (-1, 1):
                shape(k, [(0, cy - 130), (s_ * 70, cy - 190), (s_ * 80, cy - 140)], "#FFD23F", line="#D9A520", smooth=False)
        if b > 0.02:                                                     # contorno aceso por cima (bem visível)
            self._contorno(k, forma, cy, 1.0 + 0.12 * b, "#FF7A00", LINE * 1.6)
        _carinha(k, 0, cy + (25 if t != 2 else 45), {"lid": P["lid"], "boca": P["boca"]}, "#5A3A1A", "#FF8FA8", esc=1.2)


PROPS.update({"comida_forma": ComidaForma})
