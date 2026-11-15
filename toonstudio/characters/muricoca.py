"""Muriçocas da turma — personagens originais de inseto voador (alternativa pedida pelo usuário).

Por que funciona melhor com animação procedural: o voo (flutuar, inclinar nas curvas, asas batendo rápido com borrão,
perninhas penduradas com inércia) é naturalmente "física" — fórmula bem feita parece viva, ao contrário do andar humano.

Construção (estilo desenho de TV: contorno marrom-escuro, cor chapada com sombra recortada):
cabeça redonda grande com olhos enormes, narizinho-canudo (probóscide) que balança, antenas com pompom, tórax pequeno,
abdômen listrado em gota, 2 asas translúcidas (batem conforme `wing_phase`), 6 perninhas finas penduradas.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..drawing.ink import Ink, ellipse_pts, paint
from .base import Character, View, lerp, rot
from .kit import Kit, Style, darken, lighten

INK = "#3B2219"
CEL = Style(width=4.6, vary=0.2, ink_k=0.35, shade_k=0.84, soft=False, ink=INK)


@dataclass
class MuriLook:
    body: str = "#8FB8D8"            # cabeça e tórax
    stripe_a: str = "#FFD23F"        # listras do abdômen
    stripe_b: str = "#3E4A7A"
    eye: str = "#2B1A14"
    hair: str = "#F0C559"
    accent: str = "#FF5FA2"
    extra: dict = field(default_factory=dict)


class Muricoca(Character):
    flies = True

    def __init__(self, cid: str, name: str, look: MuriLook):
        self.look = look
        super().__init__(
            id=cid, name=name, canvas=(760, 700), anchor=(380, 600), height=360, palette=look.__dict__,
            defaults={
                "turn": 0.25, "back": False, "lean": 0.0, "squash": 1.0, "body_y": 0.0, "body_x": 0.0,
                "head_tilt": 0.0, "head_dx": 0.0, "head_dy": 0.0, "head_turn": 0.0,
                "hand_n_x": 30.0, "hand_n_y": 40.0, "hand_n_bend": 0.3, "paw_n": 0.0,
                "hand_f_x": 40.0, "hand_f_y": 36.0, "hand_f_bend": 0.3, "paw_f": 0.0,
                "foot_n_x": 0.0, "foot_n_y": 0.0, "foot_n_bend": 0.0, "foot_n_rot": 0.0,
                "foot_f_x": 0.0, "foot_f_y": 0.0, "foot_f_bend": 0.0, "foot_f_rot": 0.0,
                "mouth": "X", "smile": 0.8, "brow_y": 0.3, "blush": 0.7, "stars": 0.0, "speed": 0.0,
                "holding": "", "wing_phase": 0.0, "bank": 0.0, "dangle": 0.0, "hair_bounce": 0.0,
                "rot_pivot": 0.7,         # gira em torno do próprio corpo (no ar), não do chão
            })

    def draw(self, ink: Ink, P: dict) -> None:
        L = self.look
        kit = Kit(ink, CEL)
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        # o inseto paira acima do "chão" da âncora (sombra no chão mostra a altura)
        H0 = (P["body_x"] * f, -250 + P["body_y"])
        bank = P.get("bank", 0.0)          # inclinação nas curvas (vem da velocidade horizontal)
        ang = (P["lean"] + bank) * f
        sq = P["squash"]

        def T(p):
            x, y = H0[0] + p[0] * sq ** -0.6, H0[1] + p[1] * sq
            return rot((x, y), ang, H0)

        ink.shape(ellipse_pts(H0[0] * 0.4, -6, 60, 10, 0, 14), fill=(0, 0, 0, 0.08 + 0.04 * max(0, P["body_y"] / 100)), line=0)
        # asa de trás
        self._wing(kit, P, T((-f * 4, -46)), f, s, far=True)
        # perninhas (3 pares), penduradas com inércia (dangle)
        dang = P.get("dangle", 0.0)
        for i, dx in enumerate((-18, 0, 18)):
            for side in (-1, 1):
                if s > 0.6 and side == 1:
                    continue
                base = T((dx * f * (1 - 0.4 * s) + side * 8 * (1 - s), 6))
                knee = (base[0] + side * 22 * (1 - s) - f * (10 + dang * 30), base[1] + 34)
                foot = (knee[0] - f * (6 + dang * 40) + side * 8 * (1 - s), knee[1] + 38 + i * 4)
                ink.stroke([base, knee, foot], 5.5, taper=(0.1, 0.4), color_=INK)
                kit.blob(ellipse_pts(foot[0], foot[1] + 2, 7, 5, 0, 8), L.accent, shade=False, width=2.5)
        # abdômen em gota, listrado
        tail = [T(p) for p in ((-f * 6, -10), (-f * 52, -6), (-f * 96, 18), (-f * 112, 44), (-f * 90, 58), (-f * 44, 40), (-f * 6, 16))]

        def stripes(kk: Ink):
            for j in range(4):
                a = T((-f * (34 + j * 22), -40))
                b = T((-f * (34 + j * 22) - f * 4, 80))
                kk.stroke([a, b], 12, taper=(0, 0), color_=L.stripe_b)
        kit.blob(tail, L.stripe_a, clip_extra=stripes)
        # tórax
        kit.blob(ellipse_pts(*T((0, 0)), 36, 30, ang, 14), L.body)
        # cabeça
        C = T((f * (50 + 10 * s) + P["head_dx"] * f, -70 + P["head_dy"]))
        self._head(kit, P, C, View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"]), ang + P["head_tilt"] * f)
        # bracinhos (par da frente) acenam/dançam
        for which, off in (("n", -1), ("f", 1)):
            S = T((f * 18, 10 + off * 2))
            hx, hy = P[f"hand_{which}_x"] * 0.6 * f, P[f"hand_{which}_y"] * 0.6
            Hh = (S[0] + hx, S[1] + hy)
            mid = ((S[0] + Hh[0]) / 2 - f * 6, (S[1] + Hh[1]) / 2 + 6)
            ink.stroke([S, mid, Hh], 5.5, taper=(0.1, 0.3), color_=INK)
            kit.blob(ellipse_pts(Hh[0], Hh[1], 8, 7, 0, 8), L.accent, shade=False, width=2.5)
        # asa da frente (por cima)
        self._wing(kit, P, T((f * 2, -48)), f, s, far=False)

    def _wing(self, kit: Kit, P, A, f, s, far: bool):
        """Asa translúcida batendo rápido; 2 'fantasmas' fazem o borrão de movimento."""
        ph = P.get("wing_phase", 0.0)
        for k, alpha in ((0, 0.55), (1, 0.22), (2, 0.12)):
            a = math.sin((ph - k * 0.11) * 2 * math.pi)
            ang = (-0.9 - 0.75 * a) * f + (0.2 * f if far else 0)
            L_, W_ = (108, 40) if not far else (96, 34)
            cx, cy = A[0] + math.cos(-math.pi / 2 + ang) * L_ * 0.5, A[1] + math.sin(-math.pi / 2 + ang) * L_ * 0.5
            pts = ellipse_pts(cx, cy, W_, L_ * 0.55, ang, 16)
            col = (0.88, 0.96, 1.0, alpha * (0.8 if far else 1.0))
            kit.k.shape(pts, fill=col, line=2.5 if k == 0 else 0, brush=kit.brush("#BFD8EA", 2.5))
            if k == 0:
                kit.k.stroke([A, (cx + math.cos(-math.pi / 2 + ang) * L_ * 0.25, cy + math.sin(-math.pi / 2 + ang) * L_ * 0.25)],
                             2.5, color_=(0.55, 0.7, 0.85, 0.7))

    def _head(self, kit: Kit, P, C, v: View, ht):
        L = self.look
        f, s = v.f, v.side
        k = kit.k
        r = 84
        # antenas com pompom (seguem a cabeça com atraso pelo head_tilt/hair_bounce)
        sway = P.get("hair_bounce", 0.0) * 0.4 + P["head_tilt"] * 0.6
        for side in (-1, 1):
            b = rot((C[0] + side * 18 + f * s * 10, C[1] - r * 0.85), ht, C)
            tip = (b[0] + side * 26 + f * 10 + sway * 30, b[1] - 66)
            k.stroke([b, ((b[0] + tip[0]) / 2 + side * 10, b[1] - 40), tip], 5, taper=(0.1, 0.1), color_=INK)
            kit.blob(ellipse_pts(tip[0], tip[1], 12, 12, 0, 10), L.accent)
        kit.blob(ellipse_pts(C[0], C[1], r, r * 0.94, ht, 22), L.body)
        # cabelinho de identidade (topete/coquinhos da turma)
        sig = L.extra.get("assinatura", "")
        if sig == "molinha":
            base = rot((C[0] + 4, C[1] - r * 0.9), ht, C)
            pts = []
            for i in range(30):
                u = i / 29
                a = u * 3.6 * math.pi
                pts.append((base[0] + (5 + 12 * u) * math.cos(a), base[1] - 48 * u - (5 + 12 * u) * math.sin(a) * 0.4))
            k.stroke(pts, 12, taper=(0, 0.5), color_=darken(L.hair, 0.75))
            k.stroke(pts, 7, taper=(0, 0.6), color_=L.hair)
        elif sig == "coquinhos":
            for side in (-1, 1):
                B = rot((C[0] + side * 40, C[1] - r * 0.86), ht, C)
                kit.blob([(B[0] + 22 * math.cos(a) * (1 + 0.12 * abs(math.sin(a * 3))),
                           B[1] + 20 * math.sin(a) * (1 + 0.12 * abs(math.sin(a * 3)))) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)],
                         L.hair)
        if v.back:
            return
        # bochechas e olhos enormes
        for side in (-1, 1):
            x, c = v.sphere(C[0], r * 0.92, side * 0.62)
            if c > 0.25:
                q = rot((x, C[1] + 26), ht, C)
                k.ellipse(q[0], q[1], 20 * c, 12, (0.98, 0.5, 0.55, 0.45 * P.get("blush", 0.7) + 0.25), line=0)
        for side in (-1, 1):
            x, c = v.sphere(C[0], r * 0.85, side * 0.42)
            if c > 0.3:
                E = rot((x, C[1] - 6), ht, C)
                self._eye(kit, P, E, c, side, f, s, ht)
        # probóscide (narizinho-canudo) — balança com a fala/canto
        nx_, nc = v.sphere(C[0], r * 0.95, 0.0)
        N0 = rot((nx_ + f * s * 6, C[1] + 16), ht, C)
        wob = math.sin(P.get("wing_phase", 0.0) * 0.35) * 4 + (6 if P["mouth"] in "CDEH" else 0)
        # narizinho curto e arredondado (canudinho fofo, não agulha)
        tipn = (N0[0] + f * (26 + 18 * s), N0[1] + 22 + wob * 0.6)
        k.stroke([N0, ((N0[0] + tipn[0]) / 2, N0[1] + 8), tipn], 12, taper=(0.0, 0.0), color_=INK)
        k.stroke([N0, ((N0[0] + tipn[0]) / 2, N0[1] + 8), tipn], 6.5, taper=(0.0, 0.0), color_=lighten(L.body, 0.15))
        kit.blob(ellipse_pts(tipn[0], tipn[1], 8, 8, 0, 10), L.accent, shade=False, width=3)
        # boquinha (abaixo do canudo)
        mq = rot((nx_ - f * 10 * (1 - s) - f * 14 * s, C[1] + 50), ht, C)
        kit.mouth(P, mq, f, s, ht, width=16, line=INK, lips=INK, tongue="#F07C86", inside_col="#7A2430")

    def _eye(self, kit: Kit, P, E, c, side, f, s, ht):
        L = self.look
        k = kit.k
        ex, ey = E
        es = P["eye_scale"]
        rx, ry = 31 * c * es, 39 * es
        if P.get("eyes_happy", 0) > 0.5:
            k.stroke([(ex - rx, ey + 6), (ex, ey - ry * 0.5), (ex + rx, ey + 6)], 7, taper=(0.3, 0.3), color_=INK)
            return
        lid = P["lid"]
        lx = (P["look_x"] * f * 0.45 + 0.22 * f * s) * rx

        def inside(kk: Ink):
            pr = ry * 0.58 * P["pupil"] ** 0.5
            kk.ellipse(ex + lx, ey + 4, pr * 0.85 * max(c, 0.6), pr, L.eye, line=0)
            kk.dot(ex + lx - pr * 0.3, ey - pr * 0.3, max(3, pr * 0.34), "#FFFFFF")
            if lid > 0.02:
                top = ey - ry - 4 + (2 * ry + 8) * lid
                kk.c.drawRect(_rect(ex - rx - 8, ey - ry - 30, ex + rx + 8, top), paint(L.body))
                kk.stroke([(ex - rx - 2, top), (ex + rx + 2, top)], 4.5, color_=INK)
        k.shape(ellipse_pts(ex, ey, rx, ry, ht, 16), fill="#FFFFFF", brush=kit.brush("#FFFFFF", 4.5), clip_extra=inside)
        b = P["brow_l"] if side < 0 else P["brow_r"]
        by = ey - ry - 10 - P["brow_y"] * 8
        k.stroke([(ex - 16 * c, by + (b * 7 if side > 0 else -b * 3)), (ex, by - 4), (ex + 16 * c, by + (b * 7 if side < 0 else -b * 3))],
                 7 * max(c, 0.6), taper=(0.35, 0.35), color_=INK)


def _rect(l, t, r, b):
    import skia
    return skia.Rect(l, t, r, b)


LAURINHA_M = MuriLook(body="#F6B6CF", stripe_a="#FFD23F", stripe_b="#FF6FA8", hair="#F0C559", accent="#FF5FA2",
                      extra={"assinatura": "coquinhos"})
LUIZINHO_M = MuriLook(body="#9CD3F7", stripe_a="#FFD23F", stripe_b="#3E73C8", hair="#E9B949", accent="#E8423F",
                      extra={"assinatura": "molinha"})
