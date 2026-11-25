"""Cenários do canal "Fofolucos" (2º canal, 20/11/2026) — DIFERENTES dos da Laurinha e no jeito do gênero de clipe
infantil da referência (canais/fofolucos/BIBLIA_VISUAL.md): chapado SEM CONTORNO, cores saturadas, céu com degradê
suave, nuvens fofas, árvores de copa redonda em dois verdes, fundos gráficos de raios em espiral / xadrez / brilho com
confete. Toque próprio do canal: a Vila Monstrinha (casas com chifrinhos e janelas-olho).

Ids (cenários de verdade, 2600×1080, chão em y≈930):
  mon_parque · mon_vila · mon_quarto · mon_palco · mon_noite · mon_escola · mon_cozinha · mon_campinho · mon_campinho_gol
  mon_festa · mon_sombras
Fundos gráficos (ênfase/refrão; câmera no centro 960): mon_raios_<cor> · mon_xadrez_<cor> · mon_brilho_<cor>
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import skia

from ..characters.flat_muri import _rgba
from ..drawing.ink import ellipse_pts
from .plano import Flat, _surf

W_INT, H = 2600, 1080
CHAO_Y = 760
CENAS = ("mon_festa", "mon_parque", "mon_vila", "mon_quarto", "mon_palco", "mon_noite", "mon_escola", "mon_cozinha", "mon_abertura", "mon_campinho", "mon_campinho_gol", "mon_sombras")
GRAF_KINDS = ("raios", "xadrez", "brilho")
CORES = {"roxo": ("#4A158F", "#9B4FF0"), "azul": ("#0A4FC0", "#3AA6FF"), "verde": ("#0B8740", "#46D677"),
         "laranja": ("#E85A08", "#FFA63A"), "rosa": ("#C2166C", "#FF6AB2"), "vermelho": ("#B00D28", "#FF4A5E")}
GW, GH = 2200, 1240


def known(bg_id: str) -> bool:
    if bg_id in CENAS:
        return True
    p = bg_id.split("_")
    return len(p) == 3 and p[0] == "mon" and p[1] in GRAF_KINDS and p[2] in CORES


def catalog() -> list[str]:
    return list(CENAS) + [f"mon_{k}_{c}" for k in GRAF_KINDS for c in CORES]


# ───────────────────────── primitivas (sem contorno) ─────────────────────────
class P:
    def __init__(self, c: skia.Canvas):
        self.c = c
        self.F = Flat(c)

    def poly(self, pts, cor, smooth=True, alpha=1.0):
        if alpha < 1.0:
            p = skia.Path()
            p.addPoly([skia.Point(*q) for q in pts], True)
            self.c.drawPath(p, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(cor, alpha))))
            return
        self.F.shape(pts, cor, line=False, smooth=smooth)

    def rect(self, x0, y0, x1, y1, cor, r=0.0):
        p = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(cor)))
        self.c.drawRoundRect(skia.Rect(x0, y0, x1, y1), r, r, p)

    def circ(self, x, y, r, cor, alpha=1.0):
        self.c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(cor, alpha))))

    def oval(self, x, y, rx, ry, cor, alpha=1.0):
        self.c.drawOval(skia.Rect(x - rx, y - ry, x + rx, y + ry), skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(cor, alpha))))

    def grad_v(self, x0, y0, x1, y1, c0, c1):
        sh = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [skia.Color4f(*_rgba(c0)).toColor(), skia.Color4f(*_rgba(c1)).toColor()])
        self.c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=sh))

    def grad_r(self, cx, cy, r, c0, c1, w=W_INT, h=H):
        sh = skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, [skia.Color4f(*_rgba(c0)).toColor(), skia.Color4f(*_rgba(c1)).toColor()])
        self.c.drawRect(skia.Rect(0, 0, w, h), skia.Paint(Shader=sh))

    # elementos do gênero
    def nuvem(self, x, y, s=1.0):
        for dx, dy, r in ((-62, 14, 42), (-20, -16, 56), (34, -8, 50), (72, 14, 36), (4, 22, 46)):
            self.circ(x + dx * s, y + dy * s + 6 * s, r * s, "#D7E8FF")            # sombrinha azulada embaixo
        for dx, dy, r in ((-62, 10, 42), (-20, -20, 56), (34, -12, 50), (72, 10, 36), (4, 16, 46)):
            self.circ(x + dx * s, y + dy * s, r * s, "#FFFFFF")

    def arvore(self, x, base, h, verde="#3FAE3A", verde2="#2F8F2E", tronco="#7A4A26"):
        self.rect(x - h * 0.06, base - h * 0.55, x + h * 0.06, base, tronco, r=h * 0.03)
        for dx, dy, r, cor in ((-0.2, -0.62, 0.22, verde2), (0.2, -0.62, 0.22, verde2), (0, -0.8, 0.27, verde2),
                               (-0.16, -0.66, 0.2, verde), (0.18, -0.68, 0.2, verde), (0, -0.84, 0.24, verde)):
            self.circ(x + dx * h, base + dy * h, r * h, cor)
        self.circ(x - 0.08 * h, base - 0.9 * h, 0.07 * h, "#7BD66B")                 # brilho da copa

    def arbusto(self, x, base, s=1.0, cor="#2F9E3A", cor2="#46BE4E"):
        for dx, r in ((-50, 42), (0, 56), (52, 40)):
            self.circ(x + dx * s, base - r * s * 0.6, r * s, cor)
        for dx, r in ((-36, 26), (12, 34)):
            self.circ(x + dx * s, base - r * s * 1.1, r * s, cor2)

    def flor(self, x, y, cor, s=1.0):
        for j in range(5):
            a = j * 2 * math.pi / 5
            self.circ(x + math.cos(a) * 9 * s, y + math.sin(a) * 9 * s, 7 * s, cor)
        self.circ(x, y, 6 * s, "#FFD23F")

    def estrela(self, x, y, r, cor, ang=0.0):
        pts = [(x + math.cos(ang + i * math.pi / 5 - math.pi / 2) * (r if i % 2 == 0 else r * 0.45),
                y + math.sin(ang + i * math.pi / 5 - math.pi / 2) * (r if i % 2 == 0 else r * 0.45)) for i in range(10)]
        self.poly(pts, cor, smooth=False)


def _ceu_campo(p: P, rng, ceu=("#38A8F5", "#BDE6FF"), morro=("#7FD35E", "#5DBB45"), grama="#4FB83F"):
    p.grad_v(0, 0, W_INT, CHAO_Y + 40, *ceu)
    for x, y, s in ((260, 150, 1.2), (980, 110, 0.9), (1650, 170, 1.1), (2350, 120, 1.0)):
        p.nuvem(x, y, s)
    p.poly([(-50, CHAO_Y + 10)] + [(x, CHAO_Y - 120 - 70 * math.sin(x / 420)) for x in range(0, W_INT + 60, 60)] + [(W_INT + 50, CHAO_Y + 10)], morro[0])
    p.poly([(-50, CHAO_Y + 20)] + [(x, CHAO_Y - 50 - 40 * math.sin(x / 300 + 1.3)) for x in range(0, W_INT + 60, 60)] + [(W_INT + 50, CHAO_Y + 20)], morro[1])
    p.rect(0, CHAO_Y, W_INT, H, grama)
    p.rect(0, CHAO_Y, W_INT, CHAO_Y + 18, "#3FA233")


def parque(rng):
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    _ceu_campo(p, rng)
    for x, h in ((180, 520), (640, 430), (1880, 470), (2420, 540)):
        p.arvore(x, CHAO_Y + 30, h)
    for x in (420, 1180, 1500, 2150):
        p.arbusto(x, CHAO_Y + 40, 0.9)
    for _ in range(46):
        p.flor(rng.uniform(0, W_INT), rng.uniform(CHAO_Y + 60, H - 20), rng.choice(["#FFFFFF", "#FF7FBF", "#FFE14D", "#B78CFF"]), 1.1)
    return s, W_INT


def vila(rng):
    """Vila Monstrinha: casinhas coloridas com CHIFRINHOS no telhado e janelas redondas (olhos)."""
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.grad_v(0, 0, W_INT, CHAO_Y, "#3DB2FF", "#C9EEFF")
    for x, y, s_ in ((350, 140, 1.0), (1300, 100, 1.2), (2200, 160, 0.9)):
        p.nuvem(x, y, s_)
    casas = [(120, 520, "#FF6B8B", "#C8335A"), (620, 460, "#FFC23D", "#E07B1A"), (1120, 540, "#7C5CFF", "#4B2FC9"),
             (1640, 480, "#2ECC9A", "#13906A"), (2140, 520, "#FF8A3D", "#C9561A")]
    for x, h_, cor, teto in casas:
        w_ = 400
        topo = CHAO_Y - h_
        p.rect(x, topo + 90, x + w_, CHAO_Y, cor, r=26)
        p.poly([(x - 30, topo + 110), (x + w_ / 2, topo - 10), (x + w_ + 30, topo + 110)], teto, smooth=False)
        for sd in (-1, 1):                                                      # chifrinhos do telhado
            bx = x + w_ / 2 + sd * 90
            p.poly([(bx - 22, topo + 50), (bx + sd * 10, topo - 60), (bx + 26, topo + 46)], "#FFF1B8", smooth=True)
        for jx in (0.3, 0.7):                                                   # janelas-olho
            ox, oy = x + w_ * jx, topo + 220
            p.circ(ox, oy, 48, "#FFFFFF")
            p.circ(ox + 6, oy + 8, 22, "#2A1630")
            p.circ(ox - 2, oy, 7, "#FFFFFF")
        p.rect(x + w_ / 2 - 50, CHAO_Y - 170, x + w_ / 2 + 50, CHAO_Y, "#2A1630", r=50)   # porta em arco
    p.rect(0, CHAO_Y, W_INT, CHAO_Y + 70, "#E6E1F2")                             # calçada
    p.rect(0, CHAO_Y + 70, W_INT, H, "#5A5F73")                                  # rua
    for x in range(40, W_INT, 260):
        p.rect(x, CHAO_Y + 200, x + 140, CHAO_Y + 216, "#FFE14D", r=8)
    return s, W_INT


def quarto(rng):
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.rect(0, 0, W_INT, CHAO_Y, "#7FD8C8")
    for x in range(0, W_INT, 120):                                                # listras da parede
        p.rect(x, 0, x + 60, CHAO_Y, "#6CCBBA")
    p.rect(0, CHAO_Y, W_INT, H, "#F2A65A")
    p.rect(0, CHAO_Y, W_INT, CHAO_Y + 22, "#D9853C")
    p.rect(300, 180, 700, 520, "#FFFFFF", r=30)                                   # janela com lua
    p.rect(320, 200, 680, 500, "#2B2A7A", r=20)
    p.circ(560, 300, 60, "#FFE88A")
    p.circ(585, 285, 52, "#2B2A7A")
    for x, y in ((380, 260), (450, 420), (620, 440), (400, 360)):
        p.estrela(x, y, 12, "#FFF6C9")
    p.rect(1700, 470, 2500, CHAO_Y + 60, "#FF5C8A", r=40)                         # cama
    p.rect(1700, 420, 1960, 560, "#FFFFFF", r=50)
    p.rect(1680, 380, 1730, CHAO_Y + 60, "#B03A6A", r=20)
    p.rect(1080, 280, 1320, 520, "#FFD23F", r=16)                                 # pôster
    p.circ(1200, 380, 70, "#7C5CFF")
    p.circ(1200, 370, 26, "#FFFFFF")
    p.circ(1206, 376, 12, "#2A1630")
    p.oval(1300, 960, 520, 80, "#B18CFF")                                         # tapete
    p.oval(1300, 960, 400, 56, "#CDB3FF")
    return s, W_INT


def palco(rng):
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.grad_r(1300, 420, 1400, "#8E44E0", "#2A0E5C")
    cores = ["#FF5CA8", "#FFD23F", "#2ECC9A", "#2E9BFF", "#FF8A3D"]
    for j in range(60):                                                           # bolinhas de luz na parede
        x, y = 300 + (j % 12) * 180, 215 + (j // 12) * 112
        p.circ(x, y, 22, cores[j % 5])
    for sd, x0 in ((-1, 0), (1, W_INT)):                                          # cortinas vermelhas
        xs = [x0 + sd * w for w in (0, 380)]
        pts = [(xs[0], 0), (xs[1], 0)] + [(xs[1] - sd * 30 * math.sin(y / 60), y) for y in range(0, CHAO_Y + 40, 40)] + [(xs[0], CHAO_Y + 40)]
        p.poly(pts, "#D61F3C")
        for k in range(4):
            xx = x0 + sd * (60 + k * 85)
            p.rect(min(xx, xx + sd * 18), 0, max(xx, xx + sd * 18), CHAO_Y + 40, "#B0102C")
    # bambinela (21/11): a faixa lisa de 70 no alto parecia um risco vermelho no quadro da banda (as cortinas laterais
    # ficam fora da câmera) → barra de cortina franzida, em ondas, com friso dourado — lê como palco de teatro
    p.rect(0, 0, W_INT, 95, "#B0102C")
    for x in range(0, W_INT + 120, 120):
        p.circ(x + 60, 95, 62, "#B0102C")                                         # ondas da barra
        p.rect(x + 8, 0, x + 22, 120, "#94091F")                                  # dobras
    p.rect(0, 0, W_INT, 22, "#FFC83D")                                            # friso dourado
    for x in range(0, W_INT + 120, 120):
        p.circ(x + 60, 150, 9, "#FFC83D")                                         # pinguinhos dourados nas pontas
    p.rect(0, CHAO_Y - 10, W_INT, H, "#8A4B23")                                   # tablado
    p.rect(0, CHAO_Y - 10, W_INT, CHAO_Y + 20, "#A85E2E")
    for x in range(0, W_INT, 200):
        p.rect(x, CHAO_Y + 20, x + 8, H, "#6F3B1A")
    for x in (650, 1300, 1950):                                                   # focos de luz no chão
        p.oval(x, 960, 260, 50, "#FFF4B0", alpha=0.35)
    return s, W_INT


def noite(rng):
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.grad_v(0, 0, W_INT, CHAO_Y, "#160B4A", "#5B2A9E")
    p.circ(2050, 230, 120, "#FFF2A8")
    p.circ(2010, 210, 26, "#F2DE84")
    p.circ(2090, 270, 18, "#F2DE84")
    for _ in range(70):
        p.estrela(rng.uniform(0, W_INT), rng.uniform(20, CHAO_Y - 260), rng.uniform(5, 13), "#FFF6C9", rng.uniform(0, 1))
    p.poly([(-50, CHAO_Y + 10)] + [(x, CHAO_Y - 160 - 60 * math.sin(x / 380)) for x in range(0, W_INT + 60, 60)] + [(W_INT + 50, CHAO_Y + 10)], "#3B1C78")
    p.rect(0, CHAO_Y, W_INT, H, "#2B6B5A")
    p.rect(0, CHAO_Y, W_INT, CHAO_Y + 18, "#215546")
    for x, sc in ((260, 1.0), (760, 0.7), (1850, 0.9), (2400, 1.2)):             # cogumelos que brilham
        b = CHAO_Y + 40
        p.oval(x, b - 10, 70 * sc, 18 * sc, "#7CFFE1", alpha=0.25)
        p.rect(x - 14 * sc, b - 80 * sc, x + 14 * sc, b, "#F3E9FF", r=10)
        p.poly([(x - 70 * sc, b - 70 * sc), (x, b - 140 * sc), (x + 70 * sc, b - 70 * sc)], "#FF5CA8")
        for dx in (-30, 10, 36):
            p.circ(x + dx * sc, b - 92 * sc, 9 * sc, "#FFFFFF")
    return s, W_INT


def escola(rng):
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.rect(0, 0, W_INT, CHAO_Y, "#FFE38A")
    p.rect(0, CHAO_Y - 220, W_INT, CHAO_Y, "#FFC94D")                             # rodapé alto
    p.rect(700, 140, 1900, 560, "#1F6B4F", r=20)                                  # lousa
    p.rect(680, 120, 1920, 140, "#8A5A2B")
    p.rect(680, 560, 1920, 590, "#8A5A2B")
    for (x, y, t) in ((820, 260, 0), (1150, 300, 1), (1520, 250, 2)):            # rabiscos de giz: monstrinho, 1+1, estrela
        if t == 0:
            p.circ(x, y, 50, "#FFFFFF", 0.85)
            p.circ(x, y - 4, 16, "#1F6B4F")
        elif t == 1:                                      # casinha a giz
            p.rect(x, y - 10, x + 110, y + 70, "#FFFFFF", r=6)
            p.rect(x + 12, y + 2, x + 98, y + 58, "#1F6B4F", r=4)
            p.poly([(x - 14, y - 6), (x + 55, y - 70), (x + 124, y - 6)], "#FFFFFF", smooth=False)
            p.rect(x + 42, y + 22, x + 68, y + 70, "#FFFFFF", r=4)
        else:
            p.estrela(x, y, 50, "#FFFFFF")
    for x in (150, 2200):                                                         # janelas
        p.rect(x, 180, x + 300, 480, "#FFFFFF", r=20)
        p.rect(x + 18, 198, x + 282, 462, "#7FD0FF", r=12)
        p.nuvem(x + 150, 330, 0.6)
    p.rect(0, CHAO_Y, W_INT, H, "#B88A5C")
    for y in (CHAO_Y + 80, CHAO_Y + 180, CHAO_Y + 290):
        p.rect(0, y, W_INT, y + 8, "#A27648")
    return s, W_INT


def cozinha(rng):
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.rect(0, 0, W_INT, CHAO_Y, "#FF9E80")
    for x in range(0, W_INT, 100):                                               # azulejos em losango (sem contorno: tons)
        for y in range(380, CHAO_Y - 160, 100):
            if (x // 100 + y // 100) % 2 == 0:
                p.rect(x, y, x + 100, y + 100, "#FFB59C")
    p.rect(0, CHAO_Y - 160, W_INT, CHAO_Y, "#2E9BFF")                              # balcão
    p.rect(0, CHAO_Y - 180, W_INT, CHAO_Y - 150, "#FFFFFF")
    for x in range(80, W_INT, 320):
        p.rect(x, CHAO_Y - 130, x + 260, CHAO_Y - 20, "#1F7FE0", r=14)
        p.circ(x + 230, CHAO_Y - 75, 9, "#FFFFFF")
    p.rect(1900, 100, 2300, CHAO_Y - 180, "#FFFFFF", r=30)                        # geladeira
    p.rect(1900, 330, 2300, 346, "#E2E2EE")
    p.rect(1930, 160, 1946, 300, "#C9C9D9", r=8)
    p.circ(1200, 200, 90, "#FFFFFF")                                              # relógio
    p.circ(1200, 200, 8, "#2A1630")
    p.rect(1196, 140, 1204, 200, "#2A1630", r=4)
    p.rect(1200, 196, 1250, 204, "#2A1630", r=4)
    p.rect(0, CHAO_Y, W_INT, H, "#F7E6C4")
    for x in range(0, W_INT, 160):
        for y in range(CHAO_Y, H, 160):
            if (x // 160 + y // 160) % 2 == 0:
                p.rect(x, y, x + 160, y + 160, "#EBD3A6")
    return s, W_INT


def abertura(rng):
    """Abertura do canal (21/11, referência: abertura do Animadinhos): céu claro e limpo, nuvens espalhadas, estrelinhas
    nas cores da turma e um CHÃO DE NUVENS (a turma pisa nas nuvens). Fundo claro = qualquer monstrinho se destaca."""
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.grad_v(0, 0, W_INT, H, "#BFE4FF", "#EEF8FF")
    for x, y, s_ in ((180, 120, 0.8), (700, 70, 0.6), (1160, 150, 0.7), (1620, 80, 0.65), (2050, 140, 0.8), (2480, 70, 0.6),
                     (430, 330, 0.5), (2230, 340, 0.55), (90, 560, 0.5), (2530, 560, 0.5)):
        p.nuvem(x, y, s_)
    cores = ["#FF6AB2", "#FFD23F", "#9B4FF0", "#46D677", "#3AA6FF", "#FF8A3D"]
    for _ in range(70):                                         # estrelinhas e bolinhas (confete) pelo céu
        x, y = rng.uniform(0, W_INT), rng.uniform(20, 860)
        cor = cores[int(rng.integers(0, len(cores)))]
        if rng.random() < 0.45:
            p.estrela(x, y, rng.uniform(9, 18), cor, ang=float(rng.uniform(0, 1.2)))
        else:
            p.circ(x, y, rng.uniform(5, 10), cor, alpha=0.8)
    for x in range(-80, W_INT + 160, 150):                     # chão de nuvens: sombra azulada + fofura branca
        r = 120 + 30 * math.sin(x / 170)
        p.circ(x, 1000 - 0.25 * r, r, "#D2E7FF")
    for x in range(-40, W_INT + 160, 150):
        r = 105 + 25 * math.sin(x / 130 + 1.0)
        p.circ(x, 1030 - 0.25 * r, r, "#FFFFFF")
    p.rect(0, 1010, W_INT, H, "#FFFFFF")
    return s, W_INT


def campinho(rng, gol_x=None):
    """Campinho de futebol da Vila Monstrinha (Fofolucos 05): céu, arquibancadinha CLARA com a torcida de monstrinhos
    (bolinhas de cor clarinha com olhinhos e chifrinhos), bandeirinhas, placas amarelas e brancas na beira do campo
    (nada da cor de um monstrinho atrás do corpo) e gramado listrado com as linhas brancas (lateral, meio de campo e o círculo central em
    x ≈ 1300). As TRAVES são o objeto `trave` (a rede balança no gol)."""
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.grad_v(0, 0, W_INT, 520, "#3DB2FF", "#C9EEFF")
    for x, y, s_ in ((300, 110, 1.0), (1250, 80, 1.15), (2250, 130, 0.95)):
        p.nuvem(x, y, s_)
    # arquibancadinha: 4 degraus claros (creme / lilás clarinho)
    degraus = [(400, "#F3E9FF"), (480, "#FFF4DC"), (560, "#F3E9FF"), (640, "#FFF4DC")]
    p.rect(0, 380, W_INT, 700, "#E3D6FA")
    for y, cor in degraus:
        p.rect(0, y, W_INT, y + 72, cor)
        p.rect(0, y + 64, W_INT, y + 72, "#D9CBF2")
    tons = ["#FFC2DF", "#FFE89A", "#D7C2FF", "#B9DFFF", "#FFD0AE", "#FFB8C4"]
    for y, _ in degraus:                                           # a torcida (cabecinhas clarinhas, olhinhos, chifrinhos)
        x = float(rng.uniform(-20, 60))
        while x < W_INT + 40:
            cor = tons[int(rng.integers(0, len(tons)))]
            r = float(rng.uniform(24, 30))
            cy = y + 52 - r
            for sd in (-1, 1):
                p.poly([(x + sd * r * 0.35, cy - r * 0.75), (x + sd * r * 0.75, cy - r * 1.35), (x + sd * r * 0.8, cy - r * 0.55)], cor)
            p.circ(x, cy, r, cor)
            for sd in (-1, 1):
                p.circ(x + sd * r * 0.36, cy - r * 0.12, r * 0.22, "#FFFFFF")
                p.circ(x + sd * r * 0.36, cy - r * 0.08, r * 0.11, "#4A3A6A")
            x += float(rng.uniform(78, 104))
    # bandeirinhas no alto da arquibancada
    band = ["#FF4FA0", "#FFC21A", "#3A9BFF", "#FF7A1F", "#9B4FF0"]
    for j, x in enumerate(range(0, W_INT + 80, 80)):
        yy = 360.0
        p.poly([(x, yy), (x + 70, yy + 6), (x + 35, yy + 62)], band[j % len(band)], smooth=False)
    p.rect(0, 352, W_INT, 362, "#FFFFFF")
    # placas na beira do campo (cores fortes, nada verde)
    # (amarelo e branco: nenhum monstrinho na frente da própria cor — Mimi rosa, Bilu azul, Teco roxo, Zuzu laranja)
    listras = ["#FF4FA0", "#3A9BFF", "#9B4FF0", "#FF7A1F"]
    for j, x in enumerate(range(0, W_INT, 260)):
        amarela = j % 2 == 0
        p.rect(x, 690, x + 260, CHAO_Y, "#FFD23F" if amarela else "#FFFFFF")
        cor = "#FFFFFF" if amarela else listras[(j // 2) % len(listras)]
        p.rect(x + 30, 712, x + 230, 724, cor, r=6)
        p.rect(x + 60, 736, x + 200, 746, cor, r=5)
    # gramado listrado em perspectiva + linhas brancas
    p.rect(0, CHAO_Y, W_INT, H, "#4FB83F")
    for j in range(-6, 14, 2):
        x0, x1 = 1300 + (j - 0.5) * 230, 1300 + (j + 0.5) * 230
        p.poly([(x0, CHAO_Y), (x1, CHAO_Y), (1300 + (x1 - 1300) * 1.9, H), (1300 + (x0 - 1300) * 1.9, H)], "#5DC84B", smooth=False)
    if gol_x is not None:                                                     # perto do GOL: linha do gol + áreas
        _area_do_gol(p, gol_x)
        return s, W_INT
    p.rect(0, CHAO_Y + 22, W_INT, CHAO_Y + 34, "#FFFFFF")                       # linha lateral
    p.poly([(1292, CHAO_Y + 34), (1308, CHAO_Y + 34), (1318, H), (1282, H)], "#FFFFFF", smooth=False)   # meio de campo
    for rx, ry, cor in ((330, 86, "#FFFFFF"), (316, 74, None)):                # círculo central (anel)
        if cor:
            p.oval(1300, 975, rx, ry, cor)
        else:
            p.c.save()
            p.c.clipRect(skia.Rect(0, 0, W_INT, H))
            p.oval(1300, 975, rx, ry, "#56C044")
            p.c.restore()
    p.poly([(1292, 900), (1308, 900), (1318, H), (1282, H)], "#FFFFFF", smooth=False)
    p.circ(1300, 975, 12, "#FFFFFF")
    return s, W_INT


def _area_do_gol(p: P, gx: float):
    """Gramado olhando para o gol: a LINHA DO GOL passa no pé da trave (y ≈ 905, onde fica o objeto `trave`), a pequena
    e a grande área em perspectiva na frente dela e a marca do pênalti — nada de círculo central."""
    yl, B = 900, 14                                                              # linha do gol (pé da trave)

    def faixa(pts):
        p.poly(pts, "#FFFFFF", smooth=False)
    faixa([(0, yl), (W_INT, yl), (W_INT, yl + B), (0, yl + B)])
    for (w0, w1, y1) in ((430, 470, 975), (820, 920, H + 40)):                   # pequena área · grande área
        for sd in (-1, 1):                                                       # laterais (abrem para a câmera)
            xa, xb = gx + sd * w0, gx + sd * w1
            faixa([(xa - 7, yl), (xa + 7, yl), (xb + 9, y1), (xb - 9, y1)])
        if y1 < H:
            faixa([(gx - w1 - 9, y1 - 7), (gx + w1 + 9, y1 - 7), (gx + w1 + 9, y1 + 9), (gx - w1 - 9, y1 + 9)])
    p.oval(gx, 1035, 13, 7, "#FFFFFF")                                           # marca do pênalti


def campinho_gol(rng):
    """mon_campinho visto de frente para o GOL (trave em x ≈ 1565, o lugar do gol nos roteiros com chute)."""
    return campinho(rng, gol_x=1565)



def festa(rng):
    """Salão de festa (Fofolucos 07, festa surpresa do Nhoque): parede CREME clara (nenhum monstrinho some na frente),
    bandeirinhas e balõezinhos pintados no alto, faixa de "PARABÉNS" em bolinhas, porta à direita (por onde o Zuzu
    entra com o bolo) e piso de madeira clara."""
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    p.rect(0, 0, W_INT, CHAO_Y, "#FFF4D6")
    for x in range(0, W_INT, 140):                                                # listrinhas suaves da parede
        p.rect(x, 0, x + 70, CHAO_Y, "#FFEDC2")
    cores = ["#FF5CA8", "#FFD23F", "#2ECC9A", "#2E9BFF", "#B78CFF", "#FF8A3D"]
    for fila, y0 in ((0, 150), (1, 300)):                                         # bandeirinhas em dois varais
        pts = [(x, y0 + 40 * math.sin(math.pi * (x % 1300) / 1300)) for x in range(0, W_INT + 20, 20)]
        p.poly(pts + [(W_INT, y0 + 6), (0, y0 + 6)][::-1] if False else pts + [(pts[-1][0], pts[-1][1] + 5)] + [(x, y + 5) for x, y in pts[::-1]], "#C9A06B")
        for j, x in enumerate(range(40 + fila * 60, W_INT, 120)):
            y = y0 + 40 * math.sin(math.pi * (x % 1300) / 1300)
            p.poly([(x - 34, y), (x + 34, y), (x, y + 70)], cores[(j + fila * 2) % 6], smooth=False)
    for j in range(9):                                                            # faixa de bolinhas (PARABÉNS)
        p.circ(820 + j * 120, 470, 44, cores[j % 6])
        p.circ(820 + j * 120, 470, 20, "#FFFFFF", alpha=0.85)
    for (x, cor) in ((180, "#FF5CA8"), (300, "#2E9BFF"), (2380, "#FFD23F"), (2470, "#B78CFF")):   # cachos de balão na parede
        p.oval(x, 380, 52, 64, cor)
        p.poly([(x - 2, 444), (x + 6, 444), (x + 2, 520)], "#C9A06B")
    p.rect(2040, 230, 2320, CHAO_Y, "#FFFFFF", r=18)                              # porta (à direita)
    p.rect(2060, 250, 2300, CHAO_Y, "#E9C48C", r=14)
    p.rect(2080, 270, 2280, 480, "#F2D3A2", r=10)
    p.rect(2080, 510, 2280, CHAO_Y - 20, "#F2D3A2", r=10)
    p.circ(2100, 520, 14, "#C98A3A")
    p.rect(0, CHAO_Y, W_INT, H, "#E8C08F")                                        # piso de madeira clara
    p.rect(0, CHAO_Y, W_INT, CHAO_Y + 20, "#D6A66C")
    for y in range(CHAO_Y + 80, H, 80):
        p.rect(0, y, W_INT, y + 4, "#D9B17E")
    p.oval(1300, 965, 560, 80, "#FFE7A8")                                         # tapete redondo
    p.oval(1300, 965, 430, 56, "#FFF3CC")
    return s, W_INT


def sombras(rng):
    """Sala da Vila Monstrinha À NOITE (Fofolucos 08, "Sombra de Monstrinho!"): parede BEGE-CLARA (iluminada no meio, como
    se a lanterna batesse ali — é onde as sombras aparecem, x 900–1700), cantos mais escuros de noite, janela com lua à
    esquerda, baú de brinquedos amarelo e estante à direita, piso de madeira e tapete. Bege não é cor de nenhum monstrinho
    (azul, roxo, verde, rosa, laranja, coral), então ninguém some na frente da parede."""
    s, c = _surf(W_INT, H, ESC_CENA)
    p = P(c)
    sh = skia.GradientShader.MakeRadial(skia.Point(1300, 420), 1500,
                                        [skia.Color4f(*_rgba("#FFF3D6")).toColor(), skia.Color4f(*_rgba("#EAD6AE")).toColor(),
                                         skia.Color4f(*_rgba("#B9A27E")).toColor()], [0.0, 0.45, 1.0])
    c.drawRect(skia.Rect(0, 0, W_INT, CHAO_Y), skia.Paint(Shader=sh))
    for x in range(0, W_INT, 160):                                                # bolinhas suaves do papel de parede
        for y in range(70, CHAO_Y - 120, 160):
            p.circ(x + (80 if (y // 160) % 2 else 0), y, 9, "#D9C29A", alpha=0.45)
    p.rect(0, CHAO_Y - 70, W_INT, CHAO_Y, "#C9A77A")                              # rodapé
    p.rect(150, 170, 560, 560, "#FFFFFF", r=26)                                   # janela com lua e estrelas
    p.rect(172, 192, 538, 538, "#1E1A5E", r=18)
    p.circ(430, 290, 62, "#FFE88A")
    p.circ(458, 272, 54, "#1E1A5E")
    for x, y in ((230, 250), (300, 430), (470, 470), (260, 350), (380, 220)):
        p.estrela(x, y, 11, "#FFF6C9")
    p.rect(343, 192, 367, 538, "#FFFFFF")
    p.rect(172, 353, 538, 377, "#FFFFFF")
    for sd in (-1, 1):                                                            # cortininhas azul-petróleo
        x0 = 150 if sd < 0 else 560
        p.poly([(x0, 140), (x0 + sd * 110, 140), (x0 + sd * 70, 600), (x0, 600)], "#2E6E8E")
    p.rect(120, 130, 590, 152, "#8A5A2B", r=8)
    p.rect(2080, 260, 2480, 560, "#9A6A3A", r=10)                                 # estante com livros
    for y0 in (280, 420):
        x = 2100
        for j, cor in enumerate(("#E9433F", "#FFD23F", "#2E9BFF", "#FF8A3D", "#46D677", "#B98CFF", "#FF6AB2")):
            w = 34 + (j % 3) * 8
            p.rect(x, y0 + (j % 2) * 18, x + w, y0 + 120, cor, r=4)
            x += w + 8
        p.rect(2080, y0 + 120, 2480, y0 + 136, "#7A4A22")
    p.rect(2060, 600, 2460, CHAO_Y + 40, "#F2B632", r=22)                         # baú de brinquedos amarelo
    p.rect(2040, 580, 2480, 640, "#D9962A", r=18)
    p.estrela(2260, 720, 46, "#FFFFFF")
    p.rect(0, CHAO_Y, W_INT, H, "#B07A4A")                                        # piso de madeira (à noite)
    p.rect(0, CHAO_Y, W_INT, CHAO_Y + 20, "#8E5E34")
    for y in range(CHAO_Y + 80, H, 80):
        p.rect(0, y, W_INT, y + 4, "#9A6A3E")
    p.oval(1300, 965, 560, 80, "#E8CFA4")                                         # tapete redondo
    p.oval(1300, 965, 430, 56, "#F5E3C0")
    p.grad_v(0, 0, W_INT, 120, "#B9A27E", "#E6D2AA")                              # teto mais escurinho
    p.rect(0, 112, W_INT, 128, "#C9A77A")                                         # friso
    return s, W_INT


SCENES = {"mon_parque": parque, "mon_vila": vila, "mon_quarto": quarto, "mon_palco": palco, "mon_noite": noite,
          "mon_escola": escola, "mon_cozinha": cozinha, "mon_abertura": abertura, "mon_campinho": campinho, "mon_campinho_gol": campinho_gol, "mon_festa": festa, "mon_sombras": sombras}


# ───────────────────────── fundos gráficos ─────────────────────────
def _raios(cor, scale):
    c0, c1 = CORES[cor]
    s0, c = _surf(GW, GH, scale)
    P(c).grad_r(GW / 2, GH / 2, GW * 0.7, c1, c0, GW, GH)
    s1, c = _surf(3000, 3000, scale * ESC_RAIOS)
    p = P(c)
    n = 16
    for j in range(n):                                                            # raios em ESPIRAL (curvos)
        if j % 2:
            continue
        pts = [(1500, 1500)]
        for u in np.linspace(0, 1, 24):
            a = 2 * math.pi * j / n + u * 0.9
            pts.append((1500 + math.cos(a) * 2100 * u, 1500 + math.sin(a) * 2100 * u))
        for u in np.linspace(1, 0, 24):
            a = 2 * math.pi * (j + 1) / n + u * 0.9
            pts.append((1500 + math.cos(a) * 2100 * u, 1500 + math.sin(a) * 2100 * u))
        p.poly(pts, c1, smooth=False, alpha=0.95)
    return s0, s1


def _xadrez(cor, scale):
    c0, c1 = CORES[cor]
    tam = 160
    w_, h_ = GW + tam * 2, GH + tam * 2
    s, c = _surf(w_, h_, scale)
    p = P(c)
    p.rect(0, 0, w_, h_, c0)
    c.save()
    c.rotate(20, w_ / 2, h_ / 2)
    for i in range(-6, w_ // tam + 8):
        for j in range(-6, h_ // tam + 8):
            if (i + j) % 2 == 0:
                p.rect(i * tam, j * tam, i * tam + tam, j * tam + tam, c1)
    c.restore()
    return s, w_, h_, tam * 2


def _brilho(cor, scale, rng):
    c0, c1 = CORES[cor]
    s, c = _surf(GW, GH, scale)
    p = P(c)
    p.grad_r(GW / 2, GH / 2, GW * 0.65, c1, c0, GW, GH)
    pal = ["#FFFFFF", "#FFD23F", "#FF8FC8", "#7FE3FF", "#9BFF8A"]
    for _ in range(90):                                                           # confete/bokeh
        x, y, r = rng.uniform(0, GW), rng.uniform(0, GH), rng.uniform(8, 34)
        p.circ(x, y, r, pal[int(rng.integers(0, 5))], alpha=float(rng.uniform(0.25, 0.75)))
    return s


# 21/11: cenários de história desenhados a 2,2x (antes 1,5x): os closes do canal (zoom ~2x) ficavam serrilhados
ESC_CENA = 2.2
ESC_RAIOS = 1.7         # espiral: aparece a 1/0,6 do desenho → desenhada já nesse tamanho (antes ampliava 1,67x)


def build(bg_id: str, out_dir: Path, scale: float = 1.5, seed: int = 7) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    if bg_id in SCENES:
        s, w = SCENES[bg_id](rng)
        s.makeImageSnapshot().save(str(out_dir / "MG_cena.png"), skia.kPNG)
        meta = {"id": bg_id, "name": bg_id.replace("mon_", "Fofolucos — "), "width": w, "height": H, "scale": ESC_CENA,
                "landmarks": {"ground_y": 930, "floor_y": CHAO_Y}, "estilo": "canais/fofolucos/BIBLIA_VISUAL.md",
                "layers": [{"name": "MG_cena", "file": "MG_cena.png", "parallax": 1.0, "z": -20, "width": w, "height": H}]}
    else:
        _, kind, cor = bg_id.split("_", 2)
        meta = {"id": bg_id, "name": f"Fofolucos — {kind} {cor}", "width": GW, "height": GH, "scale": 1.0, "landmarks": {},
                "graphic": True, "layers": []}
        if kind == "raios":
            s0, s1 = _raios(cor, 1.0)
            s0.makeImageSnapshot().save(str(out_dir / "BG_cor.png"), skia.kPNG)
            s1.makeImageSnapshot().save(str(out_dir / "BG_raios.png"), skia.kPNG)
            meta["layers"] += [{"name": "BG_cor", "file": "BG_cor.png", "parallax": 0.0, "z": -50, "width": GW, "height": GH, "fixed": True},
                               {"name": "BG_raios", "file": "BG_raios.png", "parallax": 0.0, "z": -49, "width": 3000, "height": 3000,
                                "fixed": True, "scale_override": 0.6 * ESC_RAIOS, "spin_per_beat": 5.0, "center": True}]
        elif kind == "xadrez":
            s0, w_, h_, per = _xadrez(cor, 1.0)
            s0.makeImageSnapshot().save(str(out_dir / "BG_padrao.png"), skia.kPNG)
            meta["layers"].append({"name": "BG_padrao", "file": "BG_padrao.png", "parallax": 0.0, "z": -50, "width": w_,
                                   "height": h_, "fixed": True, "scroll": [60.0, 30.0, per, per]})
        else:
            _brilho(cor, 1.0, rng).makeImageSnapshot().save(str(out_dir / "BG_cor.png"), skia.kPNG)
            meta["layers"].append({"name": "BG_cor", "file": "BG_cor.png", "parallax": 0.0, "z": -50, "width": GW, "height": GH, "fixed": True})
    (out_dir / "background.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta
