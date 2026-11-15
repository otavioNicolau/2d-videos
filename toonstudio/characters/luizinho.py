"""Luizinho — menino animado, protagonista do canal "Luizinho e Turminha". Personagem original, estilizado a partir de
uma foto de referência (que fica só em library/characters/luizinho/referencia/, fora do git).

Traços de identidade: cabelão castanho-escuro volumoso e bagunçado com franja, olhos castanhos grandes e brilhantes,
pele morena clara, regata vermelha, bermuda azul e tênis azuis. Cabeça grande (≈2,3 cabeças de altura).
Desenhado com o kit da turma (contorno na cor da peça, preenchimento chapado).
"""
from __future__ import annotations

import math

import numpy as np

from ..drawing.ink import Ink, ellipse_pts
from .base import Character, View, lerp, rot
from .kit import Kit, darken, lighten

PAL = {
    "skin": "#E8AE86", "skin_shade": "#D2946D", "hair": "#3A2A22", "hair_light": "#5E4536",
    "shirt": "#E0342E", "shirt_trim": "#B8231F", "shorts": "#3E73C8", "shoe": "#2F8EE0", "sole": "#FFFFFF",
    "iris": "#6B3D1F", "blush": "#F2837A", "lips": "#D9776D", "brow": "#3A2A22",
}

TORSO_FRONT = [(0, -95), (46, -93), (57, -60), (60, -12), (54, 16), (0, 24), (-54, 16), (-60, -12), (-57, -60), (-46, -93)]
TORSO_SIDE = [(8, -95), (44, -88), (56, -50), (62, -6), (46, 20), (0, 26), (-44, 18), (-52, -20), (-48, -68), (-26, -93)]
HEAD_FRONT = [(0, -88), (58, -80), (88, -42), (94, 6), (82, 48), (48, 78), (0, 86), (-48, 78), (-82, 48), (-94, 6), (-88, -42), (-58, -80)]
HEAD_SIDE = [(6, -88), (60, -78), (90, -38), (94, 8), (84, 46), (50, 76), (2, 84), (-50, 74), (-88, 36), (-98, -8), (-88, -52), (-50, -84)]


class Luizinho(Character):
    def __init__(self) -> None:
        super().__init__(
            id="luizinho", name="Luizinho", canvas=(700, 640), anchor=(350, 600), height=400, palette=PAL,
            defaults={
                "turn": 0.35, "back": False, "lean": 0.0, "squash": 1.0, "body_y": 0.0, "body_x": 0.0,
                "head_tilt": 0.0, "head_dx": 0.0, "head_dy": 0.0, "head_turn": 0.0,
                "hand_n_x": -14.0, "hand_n_y": 82.0, "hand_n_bend": 0.2, "paw_n": 0.0,
                "hand_f_x": 14.0, "hand_f_y": 82.0, "hand_f_bend": 0.2, "paw_f": 0.0,
                "foot_n_x": -8.0, "foot_n_y": 0.0, "foot_n_bend": 0.0, "foot_n_rot": 0.0,
                "foot_f_x": 10.0, "foot_f_y": 0.0, "foot_f_bend": 0.0, "foot_f_rot": 0.0,
                "mouth": "X", "smile": 0.6, "brow_y": 0.2, "stars": 0.0, "speed": 0.0, "holding": "",
                "hair_bounce": 0.0,
            })

    def draw(self, ink: Ink, P: dict) -> None:
        kit = Kit(ink)
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        sq = P["squash"]
        sx, sy = sq ** -0.8, sq
        HP = (P["body_x"] * f, -112 + P["body_y"])
        lean = P["lean"] * f

        def T(p):
            x, y = (HP[0] + p[0]) * sx, (HP[1] + p[1]) * sy
            return rot((x, y), lean, (HP[0] * sx, HP[1] * sy))

        torso = [T((lerp(a[0] * f, b[0] * f, s), lerp(a[1], b[1], s))) for a, b in zip(TORSO_FRONT, TORSO_SIDE)]
        neck = T((f * s * 8, -92))
        sh_n = T((lerp(-50 * f, -4 * f, s), lerp(-82, -80, s)))
        sh_f = T((lerp(50 * f, 14 * f, s), lerp(-82, -84, s)))
        hip_n = (lerp(-22 * f, -5 * f, s) * sx + HP[0] * sx, (HP[1] + 6) * sy)
        hip_f = (lerp(22 * f, 9 * f, s) * sx + HP[0] * sx, (HP[1] + 2) * sy)
        ht = lean * 0.5 + P["head_tilt"] * f
        hsq = sq ** 0.3
        C = (neck[0] + f * P["head_dx"] + math.sin(ht) * 70, neck[1] - 72 * hsq + P["head_dy"])
        hv = View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"])

        if P["speed"] > 0:
            for i in range(int(4 + P["speed"] * 4)):
                y = T((0, 0))[1] - 220 + i * 50
                x0 = T((0, 0))[0] - f * (90 + (i * 31) % 40)
                ink.stroke([(x0, y), (x0 - f * (90 + 120 * P["speed"]), y)], 4.5, taper=(0.05, 0.9), color_=(0.2, 0.15, 0.15, 0.5))
        self._arm(kit, P, "f", sh_f, f, s, behind=True)
        self._leg(kit, P, "f", hip_f, f, s, behind=True)
        self._leg(kit, P, "n", hip_n, f, s)
        # pescoço
        kit.limb([neck, (neck[0] + (C[0] - neck[0]) * 0.5, neck[1] - 30)], 34, 32, PAL["skin_shade"])
        # tronco: regata + bermuda
        def clothes(kk: Ink):
            b0 = T((0, -6))
            kk.c.drawRect(_rect(b0[0] - 200, b0[1], b0[0] + 200, b0[1] + 200), _p(PAL["shorts"]))
            kk.stroke([(b0[0] - 120, b0[1]), (b0[0] + 120, b0[1])], 5, taper=(0, 0), color_=darken(PAL["shorts"], 0.6))
            if not v.back:   # decote em U mostrando a pele
                nk = T((f * s * 14, -96))
                kk.shape(ellipse_pts(nk[0], nk[1] + 2, 26 - 8 * s, 18, ht * 0.5, 12), fill=PAL["skin"], line=0)
                kk.stroke([(nk[0] - 27 + 8 * s, nk[1] + 2), (nk[0], nk[1] + 21), (nk[0] + 27 - 8 * s, nk[1] + 2)], 6,
                          taper=(0.1, 0.1), color_=PAL["shirt_trim"])
        kit.blob(torso, PAL["shirt"], clip_extra=clothes)
        self._head(kit, P, C, hv, ht, hsq)
        self._arm(kit, P, "n", sh_n, f, s, behind=False)
        if P["stars"] > 0:
            for i in range(3):
                a = P["stars"] * 6.28 + i * 2.09
                x, y = C[0] + math.cos(a) * 100, C[1] - 110 + math.sin(a) * 24
                pts = [(x + math.cos(j * math.pi / 5 - math.pi / 2) * (18 if j % 2 == 0 else 8),
                        y + math.sin(j * math.pi / 5 - math.pi / 2) * (18 if j % 2 == 0 else 8)) for j in range(10)]
                kit.blob(pts, "#FFD93D", shade=False, smooth=False)

    # ------------------------------------------------------------------ cabeça
    def _head(self, kit: Kit, P, C, v: View, ht, hsq):
        f, s = v.f, v.side
        k = kit.k
        head = [rot((C[0] + lerp(a[0] * f, b[0] * f, s), C[1] + lerp(a[1], b[1], s) * hsq), ht, C)
                for a, b in zip(HEAD_FRONT, HEAD_SIDE)]
        ears = []
        for a in (-1.5, 1.5):
            x, c = v.sphere(C[0], 92, a)
            ears.append((c, x, a))
        ears.sort()
        for c, x, a in ears:
            if v.back or c < 0.3:
                self._ear(kit, (x, C[1] + 10), c, a)
        kit.blob(head, PAL["skin"], shade_offset=(10, 10))
        if v.back:
            for c, x, a in ears:
                self._ear(kit, (x, C[1] + 10), 1.0, a)
            self._hair(kit, P, C, v, ht, back=True)
            return
        for c, x, a in ears:
            if c >= 0.3:
                self._ear(kit, (x, C[1] + 10), c, a)
        # bochechas
        eyes = []
        for ang in (-0.4, 0.4):
            x, c = v.sphere(C[0], 72, ang)
            eyes.append((c, x, ang))
        eyes.sort()
        for c, x, ang in eyes:
            if c > 0.25:
                bx, by = rot((x - C[0] + (12 if ang > 0 else -12) * c, 40), ht)
                k.ellipse(C[0] + bx, C[1] + by, 16 * c, 9, (0.95, 0.51, 0.48, 0.35 + 0.3 * P["blush"]), line=0)
        self._hair(kit, P, C, v, ht, back=False)
        for c, x, ang in eyes:
            if c > 0.3:          # olho de trás quase escondido no perfil: não desenha (evita olho "achatado" atrás do nariz)
                ex, ey = rot((x - C[0], 4), ht)
                kit.eye(P, (C[0] + ex, C[1] + ey), max(c, 0.45), ang, f, s, ht, rx=23, ry=29, iris=PAL["iris"],
                        lid_color=PAL["skin"], brow_color=PAL["brow"], brow_w=10, brow_gap=12)
        # nariz
        nx, nc = v.sphere(C[0], 90, 0.0)
        npos = rot((nx - C[0] - f * s * 4, 34), ht)
        N = (C[0] + npos[0], C[1] + npos[1])
        if s > 0.55:
            k.shape([(N[0] - f * 8, N[1] - 10), (N[0] + f * 6, N[1] - 2), (N[0] + f * 7, N[1] + 4), (N[0] - f * 4, N[1] + 8)],
                    fill=PAL["skin"], brush=kit.brush(PAL["skin"], 4), smooth=True)
        else:
            k.ellipse(N[0], N[1], 9, 6.5, PAL["skin_shade"], line=0)
            k.dot(N[0] - 3, N[1] - 2, 2.2, lighten(PAL["skin"], 0.5))
        # boca
        mpos = rot((nx - C[0] - f * s * 22, 58), ht)
        kit.mouth(P, (C[0] + mpos[0], C[1] + mpos[1]), f, s, ht, width=26, line=darken(PAL["lips"], 0.55),
                  lips=PAL["lips"])
        if P["tears"] > 0:
            for c, x, ang in eyes:
                if c > 0.2:
                    y0 = C[1] + 30
                    t = P["tears"]
                    kit.blob([(x - 7, y0), (x + 7, y0), (x + 11, y0 + 46 * t), (x, y0 + 66 * t), (x - 11, y0 + 46 * t)],
                             "#8FD3F5", shade=False)
        if P["sweat"] > 0:
            sx_ = C[0] - f * 80
            kit.blob([(sx_, C[1] - 60), (sx_ + 10, C[1] - 34), (sx_, C[1] - 26), (sx_ - 10, C[1] - 34)], "#BFE8FA", shade=False)

    def _ear(self, kit: Kit, E, c, a):
        kit.blob(ellipse_pts(E[0], E[1], 15 * max(abs(c), 0.6), 21, 0, 12), PAL["skin"], shade=False)
        kit.k.ellipse(E[0] + (2 if a > 0 else -2), E[1] + 1, 7 * max(abs(c), 0.6), 11, PAL["skin_shade"], line=0)

    def _hair(self, kit: Kit, P, C, v: View, ht, back: bool):
        """Cabelão volumoso e bagunçado: massa com tufos + franja; borda de baixo segue a testa ao girar."""
        f, s = v.f, v.side
        bounce = P.get("hair_bounce", 0.0)
        top_c = (C[0] - f * s * 8, C[1] - 8)
        if back:
            arc = []
            for i, a in enumerate(np.linspace(-2.1, 2.1, 40)):
                r = 104 + 11 * abs(math.sin(a * 4.2 + 0.4)) + 3 * math.sin(a * 9)        # tufos ondulados, não espinhos
                arc.append((top_c[0] + r * math.sin(a), top_c[1] - r * math.cos(a) * 0.98 - bounce * 8 * math.cos(a)))
            nape = [(C[0] + 70, C[1] + 44), (C[0] + 30, C[1] + 58), (C[0] - 6, C[1] + 48), (C[0] - 40, C[1] + 60), (C[0] - 72, C[1] + 42)]
            pts = [rot(p, ht, C) for p in arc + nape]
            kit.blob(pts, PAL["hair"], shade_offset=(8, 10))
            return

        def yl(phi):
            a = abs(phi)
            if a < 1.0:
                return -54 + 8 * math.cos(a * 4.5) ** 2                 # franja: 2–3 ondas suaves (sobrancelhas à mostra)
            if a < 1.55:
                return lerp(-50, 2, (a - 1.0) / 0.55)                   # têmporas
            return lerp(2, 44, min(1.0, (a - 1.55) / 1.4))              # nuca (lado de trás no perfil)

        p0 = -1.55 - (1.445 * s if f > 0 else 0.0)
        p1 = 1.55 + (1.445 * s if f < 0 else 0.0)
        # só o hemisfério visível: pontos "atrás" da cabeça dariam a volta e cruzariam o rosto
        shift = v.turn * (math.pi / 2) * 0.92
        p0 = max(p0, -math.pi / 2 - shift)
        p1 = min(p1, math.pi / 2 - shift)
        lower = []
        for phi in np.linspace(p1, p0, 22):
            x, c = v.sphere(C[0], 95, phi)
            lower.append((x, C[1] + yl(phi)))
        L, R = lower[-1], lower[0]          # ponta esquerda e direita da borda de baixo
        aL = math.atan2(L[0] - top_c[0], -(L[1] - top_c[1]))
        aR = math.atan2(R[0] - top_c[0], -(R[1] - top_c[1]))
        if aL > aR:
            aL, aR = aR, aL
        upper = []
        n = 40
        for i, a in enumerate(np.linspace(aL, aR, n)):
            u = i / (n - 1)
            edge = min(u, 1 - u) * 2              # 0 nas pontas, 1 no topo
            r = lerp(math.hypot(L[0] - top_c[0], L[1] - top_c[1]) if u < 0.5 else math.hypot(R[0] - top_c[0], R[1] - top_c[1]),
                     102, min(1, edge * 3))
            # tufos arredondados (ondas) — cabelo fofo e bagunçado
            r += (12 * abs(math.sin(a * 4.2 + 0.4)) + 3 * math.sin(a * 9)) * min(1, edge * 2.5)
            yb = -bounce * 10 * edge
            upper.append((top_c[0] + r * math.sin(a), top_c[1] - r * math.cos(a) + yb))
        pts = [rot(p, ht, C) for p in upper + lower]
        kit.blob(pts, PAL["hair"], shade_offset=(8, 10))
        # brilho do cabelo
        hl = [rot((top_c[0] - 40 + 50 * f * s * 0.3 + dx, top_c[1] - 78 + dy), ht, C) for dx, dy in ((0, 10), (30, -4), (62, 6))]
        kit.k.stroke(hl, 8, taper=(0.3, 0.3), color_=PAL["hair_light"])
        # mechas soltas na franja

    # ------------------------------------------------------------------ membros
    def _arm(self, kit: Kit, P, which, S, f, s, behind):
        H = (S[0] + P[f"hand_{which}_x"] * f, S[1] + P[f"hand_{which}_y"])
        dx, dy = H[0] - S[0], H[1] - S[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if nx * -f < 0:
            nx, ny = -nx, -ny
        bend = P[f"hand_{which}_bend"]
        mid = ((S[0] + H[0]) / 2 + nx * bend * L, (S[1] + H[1]) / 2 + ny * bend * L)
        skin = darken(PAL["skin"], 0.92) if behind else PAL["skin"]
        kit.limb([S, mid, H], 27, 22, skin)
        kit.hand(H, (dx / L, dy / L), P[f"paw_{which}"], PAL["skin"], behind, size=21)

    def _leg(self, kit: Kit, P, which, Hp, f, s, behind=False):
        F = (Hp[0] + P[f"foot_{which}_x"] * f, P[f"foot_{which}_y"])
        ankle = (F[0], F[1] - 18)
        bend = P[f"foot_{which}_bend"]
        dx, dy = ankle[0] - Hp[0], ankle[1] - Hp[1]
        L = math.hypot(dx, dy) or 1
        mid = ((Hp[0] + ankle[0]) / 2 + f * bend * L, (Hp[1] + ankle[1]) / 2)
        skin = darken(PAL["skin"], 0.92) if behind else PAL["skin"]
        kit.limb([Hp, mid, ankle], 30, 25, skin)
        # perna da bermuda
        cuff = (Hp[0] + (mid[0] - Hp[0]) * 0.75, Hp[1] + (mid[1] - Hp[1]) * 0.75)
        kit.limb([Hp, cuff], 40, 38, darken(PAL["shorts"], 0.9) if behind else PAL["shorts"])
        kit.sneaker(F, f, s, P[f"foot_{which}_rot"] * f, PAL["shoe"], PAL["sole"], behind)

    def reference_poses(self):
        from .base import expression
        return [("aceno", {"turn": 0.2, **expression("happy"), "mouth": "C", "hand_n_x": -55, "hand_n_y": -80, "hand_n_bend": 0.35, "paw_n": 3}),
                ("braços para cima", {"turn": 0.0, **expression("happy"), "mouth": "D", "hand_n_x": -40, "hand_n_y": -95,
                                      "hand_f_x": 40, "hand_f_y": -95, "paw_n": 3, "paw_f": 3, "squash": 1.08}),
                ("palmas", {"turn": 0.3, **expression("happy"), "hand_n_x": 30, "hand_n_y": 18, "hand_f_x": 40, "hand_f_y": 14,
                            "hand_n_bend": 0.6, "hand_f_bend": 0.6, "paw_n": 3, "paw_f": 3}),
                ("pulo", {"turn": 0.4, **expression("happy"), "mouth": "C", "squash": 1.2, "foot_n_y": -40, "foot_f_y": -30,
                          "foot_n_bend": 0.5, "foot_f_bend": 0.5, "hand_n_y": -60, "hand_f_y": -70, "paw_n": 3, "paw_f": 3})]


def _rect(l, t, r, b):
    import skia
    return skia.Rect(l, t, r, b)


def _p(c):
    from ..drawing.ink import paint
    return paint(c)
