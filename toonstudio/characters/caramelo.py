"""Caramelo — vira-lata caramelo grandalhão, guarda-costas autodeclarado de tortas. Personagem original.

Construção: corpo em pera (pesado embaixo), cabeça larga com focinho creme que avança no perfil, orelhas
caídas marrom-escuras (ação secundária), topete de três mechas, bandana vermelha, braços e pernas "de borracha".
"""
from __future__ import annotations

import math

import numpy as np

from ..drawing.ink import Ink, ellipse_pts
from .base import Character, View, lerp, rot

PAL = {
    "fur": "#D99442", "fur_shade": "#B4722E", "cream": "#F6E2B3", "cream_shade": "#DFC08A",
    "ear": "#8A5527", "ear_shade": "#6A3E1A", "nose": "#2A1B16", "bandana": "#D23A2E", "bandana_shade": "#A62A21",
    "mouth": "#5E1C1C", "tongue": "#E77A7E", "teeth": "#FFFDF4", "eye": "#FFFFFF", "pupil": "#1E1412",
    "brow": "#5A3519", "paw": "#F1D49E", "tear": "#8FD3F5", "sweat": "#BFE8FA", "blush": "#F08A7A",
}

TORSO_FRONT = [(0, -215), (70, -198), (103, -115), (118, -30), (80, 25), (0, 40), (-80, 25), (-118, -30), (-103, -115), (-70, -198)]
TORSO_SIDE = [(12, -215), (72, -185), (98, -108), (92, -25), (55, 30), (0, 40), (-65, 30), (-102, -20), (-88, -120), (-50, -200)]
HEAD_FRONT = [(0, -100), (62, -92), (102, -55), (114, 0), (104, 48), (62, 80), (0, 88), (-62, 80), (-104, 48), (-114, 0), (-102, -55), (-62, -92)]
HEAD_SIDE = [(8, -100), (62, -88), (96, -50), (104, 0), (92, 48), (45, 82), (-15, 88), (-70, 70), (-104, 25), (-108, -25), (-90, -66), (-50, -95)]

# bocas (largura, abertura, arredondamento, dentes de cima, língua)
MOUTHS = {
    "X": (52, 0, 0.0, 0, 0), "A": (40, 0, 0.0, 0, 0), "B": (54, 12, 0.2, 1, 0), "C": (58, 28, 0.3, 1, 0.3),
    "D": (66, 52, 0.4, 1, 0.8), "E": (42, 36, 0.9, 0, 0.4), "F": (26, 16, 1.0, 0, 0), "G": (50, 10, 0.2, 1, 0),
    "H": (54, 34, 0.4, 1, 1.0),
}


class Caramelo(Character):
    def __init__(self) -> None:
        super().__init__(
            id="caramelo", name="Caramelo", canvas=(1000, 900), anchor=(500, 830), height=542, palette=PAL,
            defaults={
                "turn": 0.45, "back": False, "lean": 0.0, "squash": 1.0, "body_y": 0.0, "body_x": 0.0,
                "head_tilt": 0.0, "head_dx": 0.0, "head_dy": 0.0, "head_turn": 0.0,
                "ear": 0.0, "ear_swing": 0.0, "tail": 0.0, "tail_wag": 0.0,
                # alvos (frente, baixo) relativos ao ombro/quadril; bend + = cotovelo/joelho para trás
                "hand_n_x": -34.0, "hand_n_y": 138.0, "hand_n_bend": 0.22, "paw_n": 0.0,
                "hand_f_x": 30.0, "hand_f_y": 138.0, "hand_f_bend": 0.22, "paw_f": 0.0,
                "foot_n_x": -10.0, "foot_n_y": 0.0, "foot_n_bend": -0.05, "foot_n_rot": 0.0,
                "foot_f_x": 12.0, "foot_f_y": 0.0, "foot_f_bend": -0.05, "foot_f_rot": 0.0,
                "mouth": "X", "stars": 0.0, "speed": 0.0,
            })

    # ------------------------------------------------------------------ geometria
    def draw(self, ink: Ink, P: dict) -> None:
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        sq = P["squash"]
        sx, sy = sq ** -0.8, sq
        HP = (P["body_x"] * f, -132 + P["body_y"])
        lean = P["lean"] * f

        def T(p, k=1.0):
            """local (relativo ao quadril) -> quadro."""
            x, y = HP[0] + p[0], HP[1] + p[1]
            x, y = x * sx, y * sy
            hp = (HP[0] * sx, HP[1] * sy)
            return rot((x, y), lean * k, hp)

        def side_mix(front, side):
            return [(lerp(a[0] * f, b[0] * f, s), lerp(a[1], b[1], s)) for a, b in zip(front, side)]

        torso = [T(p) for p in side_mix(TORSO_FRONT, TORSO_SIDE)]
        neck = T((f * s * 12, -210))
        hp_world = T((0, 0))

        # ombros e quadris (n = lado da câmera, f = lado de lá)
        sh_n = T((lerp(-88 * f, -4 * f, s), lerp(-185, -178, s)))
        sh_f = T((lerp(88 * f, 18 * f, s), lerp(-185, -188, s)))
        hip_n = (lerp(-56 * f, -6 * f, s) * sx + HP[0] * sx, (HP[1] + 0) * sy)
        hip_f = (lerp(56 * f, 14 * f, s) * sx + HP[0] * sx, (HP[1] - 4) * sy)

        # cabeça
        ht = lean * 0.55 + P["head_tilt"] * f
        hsq = sq ** 0.35
        C = (neck[0] + f * P["head_dx"] + math.sin(ht) * 95, neck[1] - 95 * hsq + P["head_dy"] + (1 - math.cos(ht)) * 30)
        hv = View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"])

        # ---------- ordem de desenho
        if P["speed"] > 0:
            self._speed_lines(ink, P, hp_world, f)
        if not v.back:
            self._tail(ink, P, T, f, s, front=False)
        self._leg(ink, P, "f", hip_f, f, s, behind=True)
        self._arm(ink, P, "f", sh_f, f, s, behind=True)
        self._leg(ink, P, "n", hip_n, f, s)          # pernas saem de baixo do corpo (sempre atrás do tronco)
        ink.shape(torso, fill=PAL["fur"], shade=PAL["fur_shade"],
                  clip_extra=None if v.back else (lambda k: self._belly(k, T, f, s)))
        self._bandana(ink, neck, f, s, v.back)
        self._head(ink, P, C, hv, ht, hsq)
        if v.back:
            self._tail(ink, P, T, f, s, front=True)
        self._arm(ink, P, "n", sh_n, f, s, behind=False)
        if P["stars"] > 0:
            self._stars(ink, P, C)

    # ------------------------------------------------------------------ partes
    def _belly(self, k: Ink, T, f, s):
        c = T((f * s * 40, -78))
        k.shape(ellipse_pts(c[0], c[1], 72 - 26 * s, 92), fill=PAL["cream"], line=0)

    def _bandana(self, k: Ink, N, f, s, back):
        w = 64 * (1 - 0.35 * s)
        a = (N[0] - w + f * s * 10, N[1] - 6)
        b = (N[0] + w + f * s * 22, N[1] - 6)
        tip = (N[0] + f * s * 34, N[1] + 66)
        if back:
            k.shape([a, b, (N[0], N[1] + 22)], fill=PAL["bandana"], smooth=False)
            knot = (N[0], N[1] + 6)
            k.ellipse(knot[0], knot[1], 14, 11, PAL["bandana_shade"])
            k.shape([(knot[0] - 4, knot[1] + 6), (knot[0] - 24, knot[1] + 44), (knot[0] + 4, knot[1] + 40)], fill=PAL["bandana"], smooth=False)
            return
        k.shape([a, (N[0] + f * s * 16, N[1] + 8), b, (lerp(b[0], tip[0], .5) + 4, lerp(b[1], tip[1], .5)), tip,
                 (lerp(a[0], tip[0], .5) - 4, lerp(a[1], tip[1], .5))], fill=PAL["bandana"], shade=PAL["bandana_shade"],
                shade_offset=(6, 8))
        # bolinhas da estampa
        for (u, w2) in ((0.35, 0.3), (0.62, 0.55), (0.5, 0.25)):
            x = lerp(lerp(a[0], b[0], w2), tip[0], u)
            y = lerp(lerp(a[1], b[1], w2), tip[1], u)
            k.dot(x, y, 4.5, "#F6E2B3")

    def _head(self, k: Ink, P, C, v: View, ht, hsq):
        f, s = v.f, v.side
        shape = [(C[0] + x * (1 / hsq) ** 0.5, C[1] + y * hsq) for x, y in
                 [rot((lerp(a[0] * f, b[0] * f, s), lerp(a[1], b[1], s)), ht) for a, b in zip(HEAD_FRONT, HEAD_SIDE)]]
        R = 82
        ears = []
        for side_ang in (-1.42, 1.42):
            x, c = v.sphere(C[0], 96, side_ang)
            x += (1 if x >= C[0] else -1) * 34 * max(0.0, 1 - 1.4 * s)   # de frente, as orelhas caem por fora do rosto
            ears.append((c, x, side_ang))
        ears.sort()
        # orelhas atrás da cabeça
        for c, x, a in ears:
            if v.back or c < 0.35:
                self._ear(k, P, (x, C[1] - 62), a, c, v, ht)
        # topete (atrás da cabeça, sobressai no alto)
        tx, tc = v.sphere(C[0], 40, -0.15)
        top = rot((tx - C[0], -96), ht)
        base = (C[0] + top[0], C[1] + top[1] * hsq)
        lock = [(base[0] - 22, base[1] + 16), (base[0] - 26, base[1] - 30), (base[0] - 6, base[1] - 6),
                (base[0] + 6, base[1] - 44), (base[0] + 14, base[1] - 4), (base[0] + 36, base[1] - 26), (base[0] + 24, base[1] + 16)]
        k.shape(lock, fill=PAL["fur"], smooth=True)
        k.shape(shape, fill=PAL["fur"], shade=PAL["fur_shade"], shade_offset=(12, 12))
        if v.back:
            for c, x, a in ears:
                self._ear(k, P, (x, C[1] - 62), a, 1.0, v, ht)
            return
        # rosto: olhos, sobrancelhas
        eye_y = C[1] - 30 * hsq
        eyes = []
        for ang in (-0.40, 0.40):
            x, c = v.sphere(C[0], R, ang)
            eyes.append((c, x, ang))
        eyes.sort()
        for c, x, ang in eyes:
            if c > 0.08:
                ex, ey = rot((x - C[0], eye_y - C[1]), ht)
                self._eye(k, P, (C[0] + ex, C[1] + ey), max(c, 0.55), ang, f, s, ht)
        # focinho
        mx, mc = v.sphere(C[0], 40, 0.0)
        mcx = lerp(C[0], C[0] + f * 104, s) + (mx - C[0]) * (1 - s)
        mpos = rot((mcx - C[0], 40), ht)
        M = (C[0] + mpos[0], C[1] + mpos[1] * hsq)
        jaw = P["jaw"]
        mw, mo, rnd, teeth, tongue = MOUTHS.get(P["mouth"], MOUTHS["X"])
        open_ = mo + jaw * 40
        k.shape(ellipse_pts(M[0], M[1] + open_ * 0.25, 74 + 14 * s, 50 + open_ * 0.3, ht, 14), fill=PAL["cream"],
                shade=PAL["cream_shade"], shade_offset=(8, 10))
        # boca
        mo_pos = rot((lerp(0, f * 30, s), 18 + open_ * 0.15), ht)
        self._mouth(k, P, (M[0] + mo_pos[0], M[1] + mo_pos[1]), f, s, ht, (mw, open_, rnd, teeth, tongue))
        # nariz
        npos = rot((lerp(0, f * 74, s), -14), ht)
        Nn = (M[0] + npos[0], M[1] + npos[1])
        k.shape([(Nn[0] - 26 + 6 * s, Nn[1] - 8), (Nn[0], Nn[1] - 16), (Nn[0] + 26 - 6 * s, Nn[1] - 8), (Nn[0] + 12, Nn[1] + 12),
                 (Nn[0], Nn[1] + 15), (Nn[0] - 12, Nn[1] + 12)], fill=PAL["nose"], line=3)
        k.ellipse(Nn[0] - 8 + 4 * s * f, Nn[1] - 6, 6, 3.5, "#FFFFFF", line=0)
        # lágrimas (por cima do focinho): dois riachos
        if P["tears"] > 0:
            tt = P["tears"]
            for c, x, ang in eyes:
                if c > 0.2:
                    ex2 = rot((x - C[0], eye_y - C[1]), ht)[0] + C[0]
                    y0 = eye_y + 30
                    pts = [(ex2 - 9, y0), (ex2 + 9, y0), (ex2 + 14, y0 + 60 * tt), (ex2 + 4, y0 + 95 * tt),
                           (ex2 - 8, y0 + 92 * tt), (ex2 - 14, y0 + 55 * tt)]
                    k.shape(pts, fill=PAL["tear"], line=3.5)
        # bochecha corada
        if P["blush"] > 0:
            for c, x, ang in eyes:
                if c > 0.3:
                    k.ellipse(x + (ang > 0 and 6 or -6), eye_y + 52, 18 * c, 9, (0.94, 0.54, 0.48, 0.55 * P["blush"]), line=0)
        # orelhas na frente
        for c, x, a in ears:
            if c >= 0.35:
                self._ear(k, P, (x, C[1] - 62), a, c, v, ht)
        # gotas
        if P["sweat"] > 0:
            sx_ = C[0] - f * 90
            k.shape([(sx_, C[1] - 90), (sx_ + 12, C[1] - 60), (sx_, C[1] - 52), (sx_ - 12, C[1] - 60)], fill=PAL["sweat"], line=3)

    def _eye(self, k: Ink, P, E, c, ang, f, s, ht):
        es = P["eye_scale"]
        rx, ry = 27 * c * es, 37 * es
        ex, ey = E
        lid, lid_low = P["lid"], P["lid_low"]
        pts = ellipse_pts(ex, ey, rx, ry, ht, 14)

        def inside(kk: Ink):
            # pupila
            lx = (P["look_x"] * f * 0.55 + 0.28 * f * s) * rx
            ly = P["look_y"] * 0.5 * ry
            pr = 12.5 * P["pupil"] * es ** 0.5
            kk.ellipse(ex + lx, ey + ly + 4, pr * max(c, 0.6), pr * 1.25, PAL["pupil"], line=0)
            kk.dot(ex + lx - pr * 0.35, ey + ly - pr * 0.4, max(2.5, pr * 0.32), "#FFFFFF")
            # pálpebras (pelo)
            if lid > 0.01:
                top = ey - ry - 4 + (2 * ry + 8) * lid * 0.98
                kk.c.drawRect(_rect(ex - rx - 10, ey - ry - 40, ex + rx + 10, top), _p(PAL["fur"]))
                kk.stroke([(ex - rx - 4, top + 2), (ex, top + 5), (ex + rx + 4, top + 2)], 5, smooth=True)
            if lid_low > 0.01:
                bot = ey + ry + 4 - (ry * 1.2) * lid_low
                kk.c.drawRect(_rect(ex - rx - 10, bot, ex + rx + 10, ey + ry + 40), _p(PAL["fur"]))
                kk.stroke([(ex - rx - 2, bot), (ex, bot - 6), (ex + rx + 2, bot)], 4)

        k.shape(pts, fill=PAL["eye"], line=4.5, clip_extra=inside)
        # sobrancelha
        inner = 1 if ang < 0 else -1          # lado de dentro (em direção ao centro do rosto) em x de tela
        b = P["brow_l"] if ang < 0 else P["brow_r"]
        by = ey - ry - 14 - P["brow_y"] * 11
        x0, x1 = ex - rx * 1.05 * inner, ex + rx * 0.95 * inner
        y0 = by - b * -6
        y1 = by + b * 16
        mid = ((x0 + x1) / 2, (y0 + y1) / 2 - 7 + abs(b) * 4)
        k.stroke([(x0, y0), mid, (x1, y1)], 13 * max(c, 0.6), taper=(0.35, 0.2), color_=PAL["brow"])

    def _mouth(self, k: Ink, P, M, f, s, ht, spec):
        mw, mo, rnd, teeth, tongue = spec
        smile = P["smile"]
        w = mw * (1 - 0.35 * s) * (1 + 0.15 * smile)
        cx, cy = M
        if mo < 3:
            # boca fechada: linha com cantos
            pts = [(cx - w, cy - smile * 10), (cx - w * 0.5, cy + smile * 4), (cx, cy + smile * 7),
                   (cx + w * 0.5, cy + smile * 4), (cx + w, cy - smile * 10)]
            if s > 0.5:
                pts = pts[1:] if f > 0 else pts[:-1]
            k.stroke(pts, 6 if P["mouth"] == "A" else 5, taper=(0.25, 0.25))
            for sgn in (-1, 1):
                if s < 0.5 or sgn == -f:
                    k.stroke([(cx + sgn * w * 1.05, cy - smile * 10 - 6), (cx + sgn * w * 1.1, cy - smile * 10 + 6)], 4)
            return
        h = mo
        top = cy - 4 - smile * 3
        bot = cy + h
        corner_y = cy - smile * 10
        pts = [(cx - w, corner_y), (cx - w * 0.6, top - 2 + rnd * 6), (cx, top + rnd * 4), (cx + w * 0.6, top - 2 + rnd * 6),
               (cx + w, corner_y), (cx + w * 0.75, lerp(corner_y, bot, 0.7)), (cx, bot), (cx - w * 0.75, lerp(corner_y, bot, 0.7))]
        if rnd > 0.6:
            pts = ellipse_pts(cx, cy + h * 0.45, w * 0.55, h * 0.55 + 4, 0, 10)

        def inner(kk: Ink):
            if tongue > 0:
                kk.ellipse(cx + f * s * 6, bot - 6 + (1 - tongue) * 10, w * 0.55, h * 0.35 + 6, PAL["tongue"], line=0)
            if teeth:
                kk.c.drawRect(_rect(cx - w * 0.75, top - 30, cx + w * 0.75, top + 8 + min(h, 30) * 0.12), _p(PAL["teeth"]))
        k.shape(pts, fill=PAL["mouth"], line=5, clip_extra=inner)

    def _ear(self, k: Ink, P, A, side_ang, c, v: View, ht):
        f = v.f
        out = 1 if (side_ang + v.turn * 1.4) > 0 else -1
        swing = P["ear"] + P["ear_swing"]
        ang = out * (0.22 + swing) + ht * 0.5
        L, W = 150, 64 * max(abs(c), 0.55)
        base = A
        pts = [(0, -6), (W * 0.55, 10), (W * 0.62, L * 0.55), (W * 0.35, L * 0.92), (0, L), (-W * 0.38, L * 0.85),
               (-W * 0.45, L * 0.45), (-W * 0.3, 8)]
        pts = [rot((x * out, y), -ang * out * 0 + ang, (0, 0)) for x, y in pts]
        pts = [(base[0] + x, base[1] + y) for x, y in pts]
        k.shape(pts, fill=PAL["ear"], shade=PAL["ear_shade"], shade_offset=(8, 10))

    def _arm(self, k: Ink, P, which, S, f, s, behind):
        hx = P[f"hand_{which}_x"] * f
        hy = P[f"hand_{which}_y"]
        H = (S[0] + hx, S[1] + hy)
        bend = P[f"hand_{which}_bend"]
        mid = ((S[0] + H[0]) / 2, (S[1] + H[1]) / 2)
        dx, dy = H[0] - S[0], H[1] - S[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if nx * -f < 0:                     # normal escolhida aponta para trás (bend + = cotovelo para trás)
            nx, ny = -nx, -ny
        ctrl = (mid[0] + nx * bend * L, mid[1] + ny * bend * L)
        fill = PAL["fur_shade"] if behind else PAL["fur"]
        k.tube([S, ctrl, H], 44, 34, fill=fill)
        self._paw(k, H, (dx / L, dy / L), P[f"paw_{which}"], behind, f)

    def _paw(self, k: Ink, H, d, kind, behind, f):
        """kind: 0 = mão aberta relaxada, 1 = punho, 2 = apontando, 3 = espalmada (mostra a palma)."""
        r = 30
        fill = PAL["paw"] if not behind else PAL["cream_shade"]
        cx, cy = H[0] + d[0] * 14, H[1] + d[1] * 14
        if kind >= 2.5:
            k.shape(ellipse_pts(cx, cy, r * 1.15, r * 1.05, math.atan2(d[1], d[0]), 12), fill=fill)
            for a in (-0.7, -0.2, 0.3, 0.8):
                ang = math.atan2(d[1], d[0]) + a
                k.ellipse(cx + math.cos(ang) * r * 1.2, cy + math.sin(ang) * r * 1.2, 11, 13, fill, rot=ang)
            k.ellipse(cx, cy + 4, 12, 10, "#C98A7A", line=0)
            return
        k.shape(ellipse_pts(cx, cy, r, r * 0.92, math.atan2(d[1], d[0]), 12), fill=fill)
        if kind >= 1.5:   # apontando: um dedo esticado
            tip = (cx + d[0] * 46, cy + d[1] * 46)
            k.tube([(cx + d[0] * 14, cy + d[1] * 14), tip], 16, 13, fill=fill)
        # dedos (linhas)
        for a in (-0.35, 0.05, 0.45):
            ang = math.atan2(d[1], d[0]) + a
            p0 = (cx + math.cos(ang) * r * 0.45, cy + math.sin(ang) * r * 0.45)
            p1 = (cx + math.cos(ang) * r * 0.95, cy + math.sin(ang) * r * 0.95)
            k.stroke([p0, p1], 3.5, taper=(0.3, 0.1))

    def _leg(self, k: Ink, P, which, Hp, f, s, behind=False):
        fx = P[f"foot_{which}_x"] * f
        fy = P[f"foot_{which}_y"]
        F = (Hp[0] + fx, fy)
        ankle = (F[0], F[1] - 24)
        bend = P[f"foot_{which}_bend"]
        dx, dy = ankle[0] - Hp[0], ankle[1] - Hp[1]
        L = math.hypot(dx, dy) or 1
        mid = ((Hp[0] + ankle[0]) / 2, (Hp[1] + ankle[1]) / 2)
        ctrl = (mid[0] + f * bend * L, mid[1])
        fill = PAL["fur_shade"] if behind else PAL["fur"]
        k.tube([Hp, ctrl, ankle], 58, 46, fill=fill)
        # pé
        rotf = P[f"foot_{which}_rot"] * f
        fw = lerp(40, 54, s)
        cx = F[0] + f * s * 20
        pts = ellipse_pts(cx, F[1] - 20, fw, 22, rotf, 14)
        k.shape(pts, fill=PAL["paw"] if not behind else PAL["cream_shade"])
        for i in (-1, 1) if s < 0.6 else (1,):
            tx = cx + (f * fw * 0.8 if s >= 0.6 else i * 12)
            k.stroke([(tx, F[1] - 34), (tx + (f * 4 if s >= 0.6 else 0), F[1] - 12)], 3.5, taper=(0.3, 0.2))

    def _tail(self, k: Ink, P, T, f, s, front):
        base = T((-f * (70 + 30 * s) * (s if front else 1.0), -40 if not front else -60))
        wag = P["tail"] + P["tail_wag"]
        p1 = rot((base[0] - f * 55, base[1] - 30), wag * -f, base)
        p2 = rot((base[0] - f * 60, base[1] - 105), wag * -f, base)
        k.tube([base, p1, p2], 30, 14, fill=PAL["fur"])
        k.ellipse(p2[0], p2[1], 10, 12, PAL["cream"], line=4)

    def _speed_lines(self, k: Ink, P, hp, f):
        n = int(5 + P["speed"] * 4)
        for i in range(n):
            y = hp[1] - 260 + i * (300 / n)
            x0 = hp[0] - f * (140 + (i * 37) % 60)
            k.stroke([(x0, y), (x0 - f * (120 + 160 * P["speed"]), y)], 5, taper=(0.05, 0.9), color_=(0.13, 0.09, 0.08, 0.55))

    def _stars(self, k: Ink, P, C):
        ph = P["stars"] * 6.28
        for i in range(4):
            a = ph + i * math.pi / 2
            x, y = C[0] + math.cos(a) * 120, C[1] - 120 + math.sin(a) * 30
            pts = []
            for j in range(10):
                r = 22 if j % 2 == 0 else 9
                aa = j * math.pi / 5 - math.pi / 2
                pts.append((x + math.cos(aa) * r, y + math.sin(aa) * r))
            k.shape(pts, fill="#FFE14D", smooth=False, line=4)


def _rect(l, t, r, b):
    import skia
    return skia.Rect(l, t, r, b)


def _p(c):
    from ..drawing.ink import paint
    return paint(c)
