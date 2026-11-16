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
MOTIVOS = ("bananas", "leite", "lacos", "estrelas", "coracoes")


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


COR_MOTIVO = {"bananas": "#FFE066", "leite": "#FFFFFF", "lacos": "#FFD23F", "estrelas": "#FFFFFF", "coracoes": "#FFFFFF"}


def _motivo(c, kind, x, y, s, col):
    """Desenho do padrão com a cor REAL do objeto e contorno escurecido (legível sobre qualquer fundo)."""
    p = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(col, 0.95)))
    pl = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(*_rgba(dark(col, 0.75))), Style=skia.Paint.kStroke_Style,
                    StrokeWidth=LINE * 0.8 / max(s, 1e-3), StrokeJoin=skia.Paint.kRound_Join)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if kind == "bananas":
        path = skia.Path()
        path.moveTo(-44, -26); path.quadTo(-6, 52, 48, -22); path.quadTo(0, 18, -44, -26); path.close()
        c.drawPath(path, p); c.drawPath(path, pl)
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
            _motivo(c, kind, 0, 0, 1.2, COR_MOTIVO.get(kind, light))
            c.restore()
    return s, w, h, P_


SCENES = {"plano_quarto_rosa": lambda rng: quarto("rosa", rng), "plano_quarto_azul": lambda rng: quarto("azul", rng),
          "plano_cozinha": cozinha, "plano_casa_frente": casa_frente, "plano_escola": escola, "plano_ceu": ceu}


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
                "landmarks": {"ground_y": 930, "floor_y": FLOOR_Y}, "estilo": "BIBLIA_VISUAL.md",
                "layers": [{"name": "MG_cena", "file": "MG_cena.png", "parallax": 1.0, "z": -20, "width": w, "height": H}]}
    (out_dir / "background.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta
