"""Laurinha — menina alegre, co-protagonista do canal. Personagem original, construída sobre o mesmo modelo de criança
do Luizinho (characters/luizinho.py) para manter as proporções e o estilo da turma idênticos.

Identidade: cabelo castanho comprido e liso com franja reta, duas maria-chiquinhas altas com laços amarelos,
blusa coral com uma florzinha branca, saia turquesa rodada, tênis rosa.
"""
from __future__ import annotations

import math

import numpy as np

from ..drawing.ink import Ink, ellipse_pts
from .base import View, lerp, rot
from .kit import Kit, darken, lighten
from .luizinho import Luizinho

PAL = {
    "skin": "#F1BE98", "skin_shade": "#DCA27C", "hair": "#5B3A26", "hair_light": "#8A5D40",
    "shirt": "#FF7A8A", "shirt_trim": "#E25467", "skirt": "#26B8AE", "shorts": "",
    "shoe": "#FF6FA8", "sole": "#FFFFFF", "iris": "#5A3420", "blush": "#FF8C8C", "lips": "#E07A74", "brow": "#5B3A26",
    "bow": "#FFD23F", "flower": "#FFFFFF", "flower_c": "#FFD23F",
}


class Laurinha(Luizinho):
    hair_tuft = 3.0           # cabelo liso
    fringe_y = -40.0          # franja reta mais baixa
    lash_w = 6.0

    def __init__(self) -> None:
        super().__init__(cid="laurinha", name="Laurinha", pal=PAL)
        self.defaults["smile"] = 0.7

    # cabelo comprido atrás da cabeça (cai até os ombros, balança com a dança)
    def _back_hair(self, kit: Kit, P, C, v: View, ht):
        f, s = v.f, v.side
        bounce = P.get("hair_bounce", 0.0)
        sway = P.get("head_tilt", 0.0) * 30
        w = 112 - 10 * s
        pts = [(C[0] - w, C[1] - 20), (C[0] - w - 6, C[1] + 50), (C[0] - w + 14 + sway, C[1] + 100 + bounce * 6),
               (C[0] - 20 + sway, C[1] + 108 + bounce * 8), (C[0] + 20 + sway, C[1] + 108 + bounce * 8),
               (C[0] + w - 14 + sway, C[1] + 100 + bounce * 6), (C[0] + w + 6, C[1] + 50), (C[0] + w, C[1] - 20),
               (C[0], C[1] - 90)]
        pts = [rot((x - f * s * 26, y), ht, C) for x, y in pts]
        kit.blob(pts, darken(self.pal["hair"], 0.92))
        # maria-chiquinhas (atrás da cabeça, saem pelos lados no alto)
        for side in (-1, 1):            # saem pelos lados no alto da cabeça (visíveis de frente e de costas)
            x, c = v.sphere(C[0], 96, side * 1.25)
            self._pigtail(kit, P, rot((x + side * 6, C[1] - 52), ht, C), side if (x - C[0]) * side >= 0 else -side, ht)

    def _pigtail(self, kit: Kit, P, A, side, ht):
        bounce = P.get("hair_bounce", 0.0)
        swing = P.get("head_tilt", 0.0) * 0.8 + bounce * 0.15 * side
        L = 92
        tip_ang = side * (1.15 + swing)
        pts = [(0, -18), (side * 40, -26), (side * 80, -4), (side * 96, 30), (side * 84, 66), (side * 56, 78),
               (side * 40, 40), (side * 8, 14)]
        pts = [rot((A[0] + x, A[1] + y), swing * 0.6, A) for x, y in pts]
        kit.blob(pts, self.pal["hair"])

    def _hair_extras(self, kit: Kit, P, C, v: View, ht):
        """Laços amarelos na base das maria-chiquinhas."""
        f, s = v.f, v.side
        for side in (-1, 1):
            x, c = v.sphere(C[0], 96, side * 1.15)
            if c < -0.25 and not v.back:      # laço do lado de lá da cabeça, no perfil, fica escondido
                continue
            B = rot((x, C[1] - 66), ht, C)
            for wing in (-1, 1):
                pts = [(B[0], B[1]), (B[0] + wing * 30, B[1] - 20), (B[0] + wing * 34, B[1] + 16)]
                kit.blob(pts, self.pal["bow"], smooth=True, width=3.5)
            kit.blob(ellipse_pts(B[0], B[1], 10, 9, 0, 10), self.pal["bow"], width=3.5)

    def _clothes(self, kk: Ink, T, v: View, f, s, ht):
        """Blusa coral com gola arredondada e uma florzinha no peito."""
        if v.back:
            return
        nk = T((f * s * 14, -96))
        kk.shape(ellipse_pts(nk[0], nk[1] + 2, 24 - 8 * s, 15, ht * 0.5, 12), fill=self.pal["skin"], line=0)
        kk.stroke([(nk[0] - 26 + 8 * s, nk[1] + 2), (nk[0], nk[1] + 18), (nk[0] + 26 - 8 * s, nk[1] + 2)], 6,
                  taper=(0.1, 0.1), color_=self.pal["shirt_trim"])
        fl = T((f * s * 22 + 4, -50))
        for k in range(5):
            a = k * 2 * math.pi / 5
            kk.ellipse(fl[0] + math.cos(a) * 9, fl[1] + math.sin(a) * 9, 7, 7, self.pal["flower"], line=0)
        kk.dot(fl[0], fl[1], 5.5, self.pal["flower_c"])

    def _over_torso(self, kit: Kit, P, T, v: View, f, s, ht):
        """Saia rodada turquesa: sai da cintura e abre sobre as coxas (balança com o corpo)."""
        w0 = lerp(58, 46, s)
        flare = 1.0 + 0.08 * math.sin(P.get("body_x", 0.0) * 0.05)
        top_l, top_r = T((-w0, -10)), T((w0, -10))
        bot_y = 44
        pts = [top_l, T((-w0 * 1.45 * flare, bot_y)), T((-w0 * 0.7, bot_y + 8)), T((0, bot_y + 10)),
               T((w0 * 0.7, bot_y + 8)), T((w0 * 1.45 * flare, bot_y)), top_r]
        kit.blob(pts, self.pal["skirt"], smooth=True)
        for xx in (-0.7, 0.0, 0.7):      # pregas
            a, b = T((w0 * xx * 0.6, -4)), T((w0 * xx * 1.1, bot_y + 4))
            kit.k.stroke([a, b], 3, taper=(0.5, 0.2), color_=darken(self.pal["skirt"], 0.8))

    def reference_poses(self):
        from .base import expression
        return [("alegria", {"turn": 0.15, **expression("joy"), "mouth": "D", "hand_n_x": -125, "hand_n_y": -80,
                             "hand_n_bend": 0.5, "hand_f_x": 125, "hand_f_y": -80, "hand_f_bend": -0.5, "paw_n": 3, "paw_f": 3}),
                ("aceno", {"turn": 0.25, **expression("happy"), "mouth": "C", "hand_n_x": -55, "hand_n_y": -80,
                           "hand_n_bend": 0.35, "paw_n": 3}),
                ("palmas", {"turn": 0.3, **expression("happy"), "hand_n_x": 30, "hand_n_y": 18, "hand_f_x": 40,
                            "hand_f_y": 14, "hand_n_bend": 0.6, "hand_f_bend": 0.6, "paw_n": 3, "paw_f": 3})]
