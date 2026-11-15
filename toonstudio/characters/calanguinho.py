"""Calanguinho — calango do sertão, dançarino da turma. Personagem original (estilo "turminha", kit compartilhado).

Identidade: cor de areia alaranjada com pintas marrom-terra, barriga creme, olhos verdes grandes no alto da cabeça,
focinho comprido no perfil, rabo comprido com ponta enrolada, dedos com pontas redondas e chapéu de palha com fita
vermelha. (Propositalmente diferente de lagartos de outros canais: nada de verde-limão nem óculos escuros.)
"""
from __future__ import annotations

import math

import numpy as np

from ..drawing.ink import Ink, ellipse_pts
from .base import Character, View, lerp, rot
from .kit import Kit, darken, lighten

PAL = {"body": "#E9A23B", "spot": "#A3552B", "belly": "#F8E3B0", "iris": "#3E8E3A", "straw": "#EBC97F",
       "band": "#D9473F", "mouth_line": "#7A3A1E"}

TORSO_FRONT = [(0, -110), (40, -104), (56, -66), (62, -14), (50, 22), (0, 30), (-50, 22), (-62, -14), (-56, -66), (-40, -104)]
TORSO_SIDE = [(10, -110), (44, -96), (56, -56), (58, -8), (40, 24), (-4, 30), (-46, 20), (-58, -16), (-50, -64), (-24, -104)]
HEAD_FRONT = [(0, -60), (54, -56), (84, -28), (92, 6), (78, 36), (40, 54), (0, 58), (-40, 54), (-78, 36), (-92, 6), (-84, -28), (-54, -56)]
HEAD_SIDE = [(10, -60), (70, -48), (120, -22), (138, 4), (126, 30), (80, 48), (20, 56), (-34, 50), (-70, 28), (-82, -4), (-70, -38), (-36, -58)]


class Calanguinho(Character):
    def __init__(self) -> None:
        super().__init__(
            id="calanguinho", name="Calanguinho", canvas=(760, 640), anchor=(380, 600), height=360, palette=PAL,
            defaults={
                "turn": 0.4, "back": False, "lean": 0.0, "squash": 1.0, "body_y": 0.0, "body_x": 0.0,
                "head_tilt": 0.0, "head_dx": 0.0, "head_dy": 0.0, "head_turn": 0.0,
                "hand_n_x": -16.0, "hand_n_y": 78.0, "hand_n_bend": 0.25, "paw_n": 0.0,
                "hand_f_x": 16.0, "hand_f_y": 78.0, "hand_f_bend": 0.25, "paw_f": 0.0,
                "foot_n_x": -10.0, "foot_n_y": 0.0, "foot_n_bend": 0.25, "foot_n_rot": 0.0,
                "foot_f_x": 12.0, "foot_f_y": 0.0, "foot_f_bend": 0.25, "foot_f_rot": 0.0,
                "mouth": "X", "smile": 0.7, "brow_y": 0.15, "tail": 0.0, "tail_wag": 0.0, "hat_tilt": 0.0,
                "stars": 0.0, "speed": 0.0, "holding": "",
            })

    def draw(self, ink: Ink, P: dict) -> None:
        kit = Kit(ink)
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        sq = P["squash"]
        sx, sy = sq ** -0.8, sq
        HP = (P["body_x"] * f, -96 + P["body_y"])
        lean = P["lean"] * f

        def T(p):
            x, y = (HP[0] + p[0]) * sx, (HP[1] + p[1]) * sy
            return rot((x, y), lean, (HP[0] * sx, HP[1] * sy))

        torso = [T((lerp(a[0] * f, b[0] * f, s), lerp(a[1], b[1], s))) for a, b in zip(TORSO_FRONT, TORSO_SIDE)]
        neck = T((f * s * 12, -104))
        sh_n = T((lerp(-48 * f, -4 * f, s), lerp(-92, -88, s)))
        sh_f = T((lerp(48 * f, 14 * f, s), lerp(-92, -94, s)))
        hip_n = (lerp(-30 * f, -6 * f, s) * sx + HP[0] * sx, (HP[1] + 8) * sy)
        hip_f = (lerp(30 * f, 10 * f, s) * sx + HP[0] * sx, (HP[1] + 4) * sy)
        ht = lean * 0.5 + P["head_tilt"] * f
        hsq = sq ** 0.3
        C = (neck[0] + f * P["head_dx"] + math.sin(ht) * 60 + f * s * 18, neck[1] - 52 * hsq + P["head_dy"])
        hv = View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"])

        if not v.back:
            self._tail(kit, P, T, f, s)
        self._arm(kit, P, "f", sh_f, f, s, behind=True)
        self._leg(kit, P, "f", hip_f, f, s, behind=True)
        self._leg(kit, P, "n", hip_n, f, s)

        def spots_belly(kk: Ink):
            if not v.back:
                c = T((f * s * 22, -40))
                kk.shape(ellipse_pts(c[0], c[1], 40 - 14 * s, 64, lean, 12), fill=PAL["belly"], line=0)
            rng = np.random.default_rng(3)
            for i in range(9):
                px = rng.uniform(-60, 60)
                py = rng.uniform(-104, 10)
                if not v.back and abs(px - f * s * 22) < 34 - 10 * s:
                    continue
                q = T((px * (1 - 0.4 * s) - f * s * 20, py))
                kk.ellipse(q[0], q[1], rng.uniform(6, 10), rng.uniform(5, 8), PAL["spot"], line=0)
        kit.blob(torso, PAL["body"], clip_extra=spots_belly)
        if v.back:
            self._tail(kit, P, T, f, s)
        self._head(kit, P, C, hv, ht, hsq)
        self._arm(kit, P, "n", sh_n, f, s, behind=False)

    # ------------------------------------------------------------------ cabeça
    def _head(self, kit: Kit, P, C, v: View, ht, hsq):
        f, s = v.f, v.side
        k = kit.k
        head = [rot((C[0] + lerp(a[0] * f, b[0] * f, s), C[1] + lerp(a[1], b[1], s) * hsq), ht, C)
                for a, b in zip(HEAD_FRONT, HEAD_SIDE)]
        # olhos ficam no alto da cabeça, em "calombos" (órbitas) que saltam da silhueta
        sockets = []
        for ang in (-0.62, 0.62):
            x, c = v.sphere(C[0], 70, ang)
            sockets.append((c, x, ang))
        sockets.sort()
        for c, x, ang in sockets:
            if c < 0.3:
                pos = rot((x - C[0], -46), ht)
                kit.blob(ellipse_pts(C[0] + pos[0], C[1] + pos[1], 34 * max(c, 0.5), 32, 0, 12), PAL["body"], shade=False)
        kit.blob(head, PAL["body"], shade_offset=(10, 10))
        if v.back:
            self._hat(kit, P, C, v, ht, back=True)
            return
        for c, x, ang in sockets:
            if c >= 0.3:
                pos = rot((x - C[0], -46), ht)
                kit.blob(ellipse_pts(C[0] + pos[0], C[1] + pos[1], 34 * c, 32, 0, 12), PAL["body"], shade=False)
        # pintas na cabeça
        for (a, y, r) in ((-0.2, -30, 7), (0.35, -40, 6), (-0.75, -8, 6)):
            x, c = v.sphere(C[0], 80, a)
            if c > 0.3:
                q = rot((x - C[0], y), ht)
                k.ellipse(C[0] + q[0], C[1] + q[1], r * c, r * 0.8, PAL["spot"], line=0)
        for c, x, ang in sockets:
            if c > 0.3:
                pos = rot((x - C[0], -46), ht)
                kit.eye(P, (C[0] + pos[0], C[1] + pos[1]), max(c, 0.45), ang, f, s, ht, rx=24, ry=27, iris=PAL["iris"],
                        lid_color=PAL["body"], brow_color=darken(PAL["body"], 0.45), brow_w=8, brow_gap=8)
        # narinas na ponta do focinho
        tip_x, tc = v.sphere(C[0], 88, 0.0)
        tip_x = tip_x + f * s * 40
        for d in (-1, 1):
            if s < 0.55 or d == f:
                q = rot((tip_x - C[0] + d * 12 * (1 - s), 2), ht)
                k.ellipse(C[0] + q[0], C[1] + q[1], 4, 3, darken(PAL["body"], 0.45), line=0)
        # boca larga (sorriso de lagarto)
        q = rot((tip_x - C[0] - f * s * 40, 26), ht)
        kit.mouth(P, (C[0] + q[0], C[1] + q[1]), f, s, ht, width=46, line=PAL["mouth_line"], lips=darken(PAL["body"], 0.8))
        self._hat(kit, P, C, v, ht, back=False)

    def _hat(self, kit: Kit, P, C, v: View, ht, back: bool):
        """Chapéu de palha com fita vermelha, um pouco inclinado (marca do personagem)."""
        f, s = v.f, v.side
        tilt = ht - 0.12 * f + P.get("hat_tilt", 0.0)
        top = rot((-f * s * 22, -100), tilt)
        H = (C[0] + top[0], C[1] + top[1])
        brim = ellipse_pts(H[0], H[1] + 6, 96 - 14 * s, 18 + 5 * (1 - s), tilt, 16)
        kit.blob(brim, PAL["straw"], shade_offset=(0, 6))
        crown = [rot((H[0] + x, H[1] + y), tilt, H) for x, y in ((-50, 6), (-46, -40), (-20, -54), (20, -54), (46, -40), (50, 6))]
        kit.blob(crown, PAL["straw"])
        band = [rot((H[0] + x, H[1] + y), tilt, H) for x, y in ((-50, 4), (-49, -12), (49, -12), (50, 4))]
        kit.blob(band, PAL["band"], shade=False, smooth=False, width=3.5)
        for i in range(-2, 3):   # trama da palha
            a = rot((H[0] + i * 18, H[1] - 44), tilt, H)
            b = rot((H[0] + i * 20, H[1] - 16), tilt, H)
            kit.k.stroke([a, b], 2.5, color_=darken(PAL["straw"], 0.75))

    # ------------------------------------------------------------------ corpo
    def _tail(self, kit: Kit, P, T, f, s):
        wag = P["tail"] + P["tail_wag"]
        base = T((-f * (30 + 20 * s), 6))
        pts = [base]
        L = 180
        for i in range(1, 7):
            u = i / 6
            a = (math.pi if f > 0 else 0) + f * (0.2 + 0.9 * u * u) * (1 if s > 0.3 else 0.3) + wag * u * -f
            px = base[0] + math.cos(a) * L * u * (1.0 if s > 0.3 else 0.6)
            py = base[1] + 24 * u - 60 * u * u * u + (0 if s > 0.3 else -30 * u)
            pts.append((px, py))
        kit.limb(pts, 44, 10, PAL["body"])
        tip = pts[-1]
        kit.k.stroke([tip, (tip[0] - f * 10, tip[1] - 16), (tip[0] + f * 6, tip[1] - 26)], 9, taper=(0.2, 0.6),
                     color_=PAL["body"])

    def _arm(self, kit: Kit, P, which, S, f, s, behind):
        H = (S[0] + P[f"hand_{which}_x"] * f, S[1] + P[f"hand_{which}_y"])
        dx, dy = H[0] - S[0], H[1] - S[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if nx * -f < 0:
            nx, ny = -nx, -ny
        bend = P[f"hand_{which}_bend"]
        mid = ((S[0] + H[0]) / 2 + nx * bend * L, (S[1] + H[1]) / 2 + ny * bend * L)
        col = darken(PAL["body"], 0.9) if behind else PAL["body"]
        kit.limb([S, mid, H], 22, 17, col)
        kit.hand(H, (dx / L, dy / L), P[f"paw_{which}"], PAL["body"], behind, size=19)

    def _leg(self, kit: Kit, P, which, Hp, f, s, behind=False):
        F = (Hp[0] + P[f"foot_{which}_x"] * f, P[f"foot_{which}_y"])
        ankle = (F[0], F[1] - 14)
        bend = P[f"foot_{which}_bend"]
        dx, dy = ankle[0] - Hp[0], ankle[1] - Hp[1]
        L = math.hypot(dx, dy) or 1
        mid = ((Hp[0] + ankle[0]) / 2 + f * bend * L * 0.6 - (1 if Hp[0] < 0 else -1) * 8 * (1 - s), (Hp[1] + ankle[1]) / 2)
        col = darken(PAL["body"], 0.9) if behind else PAL["body"]
        kit.limb([Hp, mid, ankle], 30, 22, col)
        rotf = P[f"foot_{which}_rot"] * f
        # pé de calango: três dedos com pontas redondas
        for a, ln in ((-0.5, 30), (0.0, 36), (0.5, 30)):
            ang = (0 if f > 0 else math.pi) + a * (0.6 if s > 0.4 else 1.6) + rotf if s > 0.4 else math.pi / 2 + a * 1.4
            tip = (F[0] + math.cos(ang) * ln, F[1] - 6 + math.sin(ang) * ln * (0.2 if s > 0.4 else 0.25))
            kit.limb([(F[0], F[1] - 8), tip], 12, 9, col)
            kit.blob(ellipse_pts(tip[0], tip[1], 8, 6, 0, 10), lighten(col, 0.15), shade=False, width=3)

    def reference_poses(self):
        from .base import expression
        return [("dança: cabeça", {"turn": 0.2, **expression("happy"), "mouth": "C", "head_tilt": 0.25, "hand_n_x": 40,
                                   "hand_n_y": 30, "hand_f_x": 40, "hand_f_y": 30, "hand_n_bend": 0.6, "hand_f_bend": 0.6}),
                ("pro lado", {"turn": 0.5, **expression("happy"), "lean": 0.25, "body_x": 30, "hand_n_x": 90, "hand_n_y": -20,
                              "paw_n": 2, "tail": 0.5}),
                ("braços para cima", {"turn": 0.0, **expression("laughing"), "mouth": "D", "hand_n_x": -40, "hand_n_y": -90,
                                      "hand_f_x": 40, "hand_f_y": -90, "paw_n": 3, "paw_f": 3, "squash": 1.08})]
