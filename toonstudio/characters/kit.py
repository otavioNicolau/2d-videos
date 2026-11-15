"""Kit de personagens da turma (ADR-0013): partes compartilhadas para novos personagens não duplicarem código.

Estilo "turminha" (gênero de clipe musical infantil): contorno NA COR da peça (versão escura do preenchimento),
espessura quase constante, preenchimento chapado com sombra suave, olhos grandes e brilhantes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from ..drawing.ink import Brush, Ink, ellipse_pts, paint
from .base import lerp, rot


def darken(hex_color: str, k: float = 0.55) -> str:
    c = hex_color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#{:02X}{:02X}{:02X}".format(int(r * k), int(g * k), int(b * k))


def lighten(hex_color: str, k: float = 0.35) -> str:
    c = hex_color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#{:02X}{:02X}{:02X}".format(*(int(v + (255 - v) * k) for v in (r, g, b)))


@dataclass
class Style:
    width: float = 4.2          # contorno (fino: o volume vem do sombreado)
    vary: float = 0.15          # variação suave (quase constante)
    ink_k: float = 0.55         # contorno = cor da peça × ink_k
    shade_k: float = 0.82       # sombra = cor da peça × shade_k
    soft: bool = True           # volume com gradiente + brilho (visual "3D fofinho")
    ink: str = ""               # cor única de contorno (ex.: marrom-escuro do estilo "cel" de TV); "" = cor da peça


TURMINHA = Style()


class Kit:
    """Atalhos de desenho com o estilo da turma."""

    def __init__(self, ink: Ink, style: Style = TURMINHA):
        self.k = ink
        self.s = style

    def brush(self, fill: str, width: float | None = None) -> Brush:
        b = self.k.brush
        ink = self.s.ink or darken(fill, self.s.ink_k)
        return Brush(width or self.s.width, self.s.vary, _rgba(ink), b.jitter, b.seed)

    def blob(self, pts, fill: str, shade: bool = True, width: float | None = None, smooth: bool = True,
             shade_offset=(8, 9), clip_extra=None):
        if self.s.soft and shade:
            return self.k.shape(pts, fill=fill, brush=self.brush(fill, width), smooth=smooth,
                                soft=(lighten(fill, 0.22), fill, darken(fill, self.s.shade_k)), clip_extra=clip_extra)
        return self.k.shape(pts, fill=fill, brush=self.brush(fill, width), smooth=smooth,
                            shade=darken(fill, self.s.shade_k) if shade else None, shade_offset=shade_offset,
                            clip_extra=clip_extra)

    def limb(self, pts, w0: float, w1: float, fill: str):
        return self.k.tube(pts, w0, w1, fill=fill, line=self.s.width, ink=_rgba(self.s.ink or darken(fill, self.s.ink_k)),
                           shade=_rgba(darken(fill, 0.9)) if self.s.soft else None)

    # ------------------------------------------------------------------ rosto
    def eye(self, P: dict, E, c: float, ang: float, f: float, s: float, ht: float, *, rx: float, ry: float,
            iris: str, lid_color: str, lash: str = "#2A1A14", brow_color: str = "#3B2A22", brow_w: float = 11,
            brow_gap: float = 14):
        """Olho grande de desenho infantil: íris colorida, pupila, dois brilhos, pálpebras, cílio e sobrancelha."""
        es = P["eye_scale"]
        rx, ry = rx * c * es, ry * es
        ex, ey = E
        lid, lid_low = P["lid"], P["lid_low"]
        if P.get("eyes_happy", 0.0) > 0.5:
            # "^^": arco grosso para cima, com cílio no canto externo
            out = -1 if ang < 0 else 1
            arc = [(ex - rx * 1.05, ey + ry * 0.15), (ex - rx * 0.5, ey - ry * 0.45), (ex, ey - ry * 0.58),
                   (ex + rx * 0.5, ey - ry * 0.45), (ex + rx * 1.05, ey + ry * 0.15)]
            self.k.stroke(arc, max(6.0, ry * 0.32), taper=(0.25, 0.25), color_=lash)
            b = P["brow_l"] if ang < 0 else P["brow_r"]
            by = ey - ry - brow_gap - P["brow_y"] * 10
            self.k.stroke([(ex - rx * 0.9, by + 4), (ex, by - 4), (ex + rx * 0.9, by + 4)], brow_w * max(c, 0.6),
                          taper=(0.35, 0.25), color_=brow_color)
            return

        def inside(kk: Ink):
            lx = (P["look_x"] * f * 0.5 + 0.25 * f * s) * rx
            ly = P["look_y"] * 0.45 * ry
            ir = ry * 0.62 * max(0.75, P["pupil"] ** 0.3)
            kk.ellipse(ex + lx, ey + ly + 2, ir * max(c, 0.6), ir, iris, line=0)
            kk.ellipse(ex + lx, ey + ly + 2, ir * 0.55 * max(c, 0.6) * P["pupil"], ir * 0.55 * P["pupil"], "#1A1210", line=0)
            kk.dot(ex + lx - ir * 0.35, ey + ly - ir * 0.35, max(2.5, ir * 0.3), "#FFFFFF")
            kk.dot(ex + lx + ir * 0.3, ey + ly + ir * 0.35, max(1.5, ir * 0.14), "#FFFFFF")
            if lid > 0.01:
                top = ey - ry - 4 + (2 * ry + 8) * lid * 0.98
                kk.c.drawRect(_rect(ex - rx - 10, ey - ry - 40, ex + rx + 10, top), paint(lid_color))
                kk.stroke([(ex - rx - 3, top + 1), (ex, top + 4), (ex + rx + 3, top + 1)], 4.5, color_=lash)
            if lid_low > 0.01:
                bot = ey + ry + 4 - (ry * 1.1) * lid_low
                kk.c.drawRect(_rect(ex - rx - 10, bot, ex + rx + 10, ey + ry + 40), paint(lid_color))
                kk.stroke([(ex - rx - 2, bot), (ex, bot - 4), (ex + rx + 2, bot)], 3.5, color_=lash)

        self.k.shape(ellipse_pts(ex, ey, rx, ry, ht, 14), fill="#FFFFFF", brush=self.brush("#5A4A44", 4.0),
                     clip_extra=inside)
        # cílio de cima (traço grosso no canto externo)
        out = -1 if ang < 0 else 1
        if lid < 0.5:   # cílio: linha grossa na borda de cima que termina numa "pontinha" para fora (sem laço)
            self.k.stroke([(ex - rx * 0.2 * out, ey - ry * 1.0), (ex + rx * 0.7 * out, ey - ry * 0.8),
                           (ex + rx * 1.15 * out, ey - ry * 0.95)], 5, taper=(0.6, 0.1), color_=lash)
        # sobrancelha
        inner = 1 if ang < 0 else -1
        b = P["brow_l"] if ang < 0 else P["brow_r"]
        by = ey - ry - brow_gap - P["brow_y"] * 10
        x0, x1 = ex - rx * 1.0 * inner, ex + rx * 0.9 * inner
        y0, y1 = by + b * 4, by + b * 12
        self.k.stroke([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 6 + abs(b) * 3), (x1, y1)], brow_w * max(c, 0.6),
                      taper=(0.35, 0.25), color_=brow_color)

    def mouth(self, P: dict, M, f: float, s: float, ht: float, *, width: float = 34, line: str = "#7A2E2A",
              lips: str = "#E58F86", tongue: str = "#E9707A", inside_col: str = "#7C2430"):
        """Boca humana com os 9 visemas (Rhubarb) + sorriso + abertura extra (jaw)."""
        shapes = {  # (largura, abertura, arredondamento, dentes, língua)
            "X": (1.0, 0, 0, 0, 0), "A": (0.8, 0, 0, 0, 0), "B": (1.05, 9, 0.2, 1, 0), "C": (1.1, 20, 0.3, 1, 0.3),
            "D": (1.2, 34, 0.4, 1, 0.8), "E": (0.8, 24, 0.9, 0, 0.4), "F": (0.5, 12, 1.0, 0, 0), "G": (1.0, 8, 0.2, 1, 0),
            "H": (1.05, 24, 0.4, 1, 1.0)}
        wk, op, rnd, teeth, tng = shapes.get(P["mouth"], shapes["X"])
        smile = P["smile"]
        op = op + P["jaw"] * 30
        w = width * wk * (1 - 0.3 * s) * (1 + 0.2 * max(0, smile))
        cx, cy = M
        if op < 3:
            pts = [(cx - w, cy - smile * 9), (cx - w * 0.5, cy + smile * 4), (cx, cy + smile * 6),
                   (cx + w * 0.5, cy + smile * 4), (cx + w, cy - smile * 9)]
            if s > 0.55:
                pts = pts[1:] if f > 0 else pts[:-1]
            self.k.stroke(pts, 5.5, taper=(0.2, 0.2), color_=line)
            return
        top = cy - 3 - max(0, smile) * 2
        corner = cy - smile * 9
        bot = cy + op
        pts = [(cx - w, corner), (cx - w * 0.55, top + rnd * 4), (cx, top + rnd * 3), (cx + w * 0.55, top + rnd * 4),
               (cx + w, corner), (cx + w * 0.7, lerp(corner, bot, 0.75)), (cx, bot), (cx - w * 0.7, lerp(corner, bot, 0.75))]
        if rnd > 0.6:
            pts = ellipse_pts(cx, cy + op * 0.45, w * 0.6, op * 0.55 + 3, 0, 10)

        def inner(kk: Ink):
            if tng:
                kk.ellipse(cx + f * s * 4, bot - 4 + (1 - tng) * 8, w * 0.6, op * 0.32 + 5, tongue, line=0)
            if teeth:
                kk.c.drawRect(_rect(cx - w, top - 20, cx + w, top + 3 + min(op, 24) * 0.18), paint("#FFFFFF"))
        self.k.shape(pts, fill=inside_col, brush=self.brush(lips, 4.5), clip_extra=inner)

    # ------------------------------------------------------------------ mãos e pés
    def hand(self, H, d, kind: float, skin: str, behind: bool, size: float = 22):
        """Mão cartunesca de 4 dedos. kind: 0 relaxada, 1 punho, 2 apontando, 3 espalmada ("jazz hands")."""
        fill = darken(skin, 0.9) if behind else skin
        a0 = math.atan2(d[1], d[0])
        cx, cy = H[0] + d[0] * size * 0.45, H[1] + d[1] * size * 0.45
        if kind >= 2.5:
            for a in (-0.75, -0.25, 0.25, 0.75):
                ang = a0 + a
                self.blob(ellipse_pts(cx + math.cos(ang) * size * 0.95, cy + math.sin(ang) * size * 0.95, size * 0.42,
                                      size * 0.26, ang, 10), fill, shade=False, width=3.5)
            self.blob(ellipse_pts(cx, cy, size * 0.85, size * 0.8, a0, 12), fill, shade=False, width=4)
            return
        if kind >= 1.5:
            tip = (cx + d[0] * size * 1.6, cy + d[1] * size * 1.6)
            self.limb([(cx, cy), tip], size * 0.42, size * 0.36, fill)
        self.blob(ellipse_pts(cx, cy, size * 0.8, size * 0.72, a0, 12), fill, shade=False, width=4)
        if kind < 0.5:   # dedos relaxados (linhas)
            for a in (-0.3, 0.1, 0.5):
                ang = a0 + a
                self.k.stroke([(cx + math.cos(ang) * size * 0.3, cy + math.sin(ang) * size * 0.3),
                               (cx + math.cos(ang) * size * 0.72, cy + math.sin(ang) * size * 0.72)], 2.6,
                              color_=darken(skin, 0.5))
        # polegar
        tang = a0 - 1.2
        self.blob(ellipse_pts(cx + math.cos(tang) * size * 0.7, cy + math.sin(tang) * size * 0.7, size * 0.3, size * 0.22,
                              tang, 8), fill, shade=False, width=3.5)

    def sneaker(self, F, f: float, s: float, rotf: float, color: str = "#3D7BD9", sole: str = "#FFFFFF",
                behind: bool = False):
        col = darken(color, 0.85) if behind else color
        L = lerp(30, 44, s)
        cx = F[0] + f * s * 14
        self.blob(ellipse_pts(cx, F[1] - 16, L, 18, rotf, 14), col, shade=True, width=4.5)
        self.k.stroke([(cx - L * 0.9, F[1] - 4), (cx + L * 0.95, F[1] - 4)], 7, taper=(0.05, 0.05), color_=sole)
        if s > 0.4:   # cadarço
            self.k.stroke([(cx + f * 4, F[1] - 30), (cx + f * 16, F[1] - 26)], 3, color_="#FFFFFF")


def ik2(S, T, l1: float, l2: float, side: tuple[float, float]):
    """IK de dois ossos (ombro→cotovelo→mão, quadril→joelho→tornozelo) com comprimentos FIXOS.
    O alvo fora de alcance é puxado para a distância máxima (o braço estica reto, nunca "estica como borracha").
    `side` = direção para onde a junta deve dobrar. Retorna (junta, ponta)."""
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = math.hypot(dx, dy) or 1e-6
    reach = (l1 + l2) * 0.999
    near = abs(l1 - l2) + 1e-3
    dd = min(max(d, near), reach)
    ux, uy = dx / d, dy / d
    E_ = (S[0] + ux * dd, S[1] + uy * dd)
    a = (l1 * l1 - l2 * l2 + dd * dd) / (2 * dd)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    px, py = S[0] + ux * a, S[1] + uy * a
    nx, ny = -uy, ux
    if nx * side[0] + ny * side[1] < 0:
        nx, ny = -nx, -ny
    return (px + nx * h, py + ny * h), E_


def _rgba(hex_color: str):
    c = hex_color.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1.0,)


def _rect(l, t, r, b):
    import skia
    return skia.Rect(l, t, r, b)
