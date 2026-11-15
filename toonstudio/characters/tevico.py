"""Tevico — bem-te-vi trapaceiro e guloso. Personagem original.

Construção: corpo em ovo inclinado (barriga amarela, costas e asas marrons), cabeça grande branca com boné preto,
faixa preta passando pelos olhos e listra branca de "sobrancelha" (padrão do bem-te-vi), bico preto comprido,
asas que funcionam como braços (três penas-dedo), pernas finas com pés de três dedos, cauda em leque e um
topetinho preto na nuca.
"""
from __future__ import annotations

import math

from ..drawing.ink import Ink, ellipse_pts, paint
from .base import Character, View, lerp, rot

PAL = {
    "yellow": "#F8D33A", "yellow_shade": "#DDA91C", "brown": "#8A5A33", "brown_shade": "#674024",
    "black": "#211C1E", "white": "#FBFAF5", "white_shade": "#D8D3C6", "beak": "#2B2526", "legs": "#5E5452",
    "mouth": "#6A1F24", "tongue": "#E77A7E", "eye": "#FFFFFF", "pupil": "#1A1416", "tear": "#8FD3F5",
    "sweat": "#BFE8FA", "blush": "#F08A7A",
}

BODY_FRONT = [(0, -85), (45, -76), (64, -30), (60, 22), (32, 56), (0, 64), (-32, 56), (-60, 22), (-64, -30), (-45, -76)]
BODY_SIDE = [(14, -85), (50, -68), (68, -22), (58, 28), (22, 60), (-10, 62), (-46, 46), (-64, 8), (-60, -42), (-30, -80)]

# abertura do bico por visema (0..1) e arredondamento
BEAK = {"X": 0.0, "A": 0.0, "B": 0.22, "C": 0.45, "D": 0.85, "E": 0.55, "F": 0.25, "G": 0.15, "H": 0.5}


class Tevico(Character):
    def __init__(self) -> None:
        super().__init__(
            id="tevico", name="Tevico", canvas=(640, 620), anchor=(320, 580), height=348, palette=PAL,
            defaults={
                "turn": 0.45, "back": False, "lean": 0.12, "squash": 1.0, "body_y": 0.0, "body_x": 0.0,
                "head_tilt": 0.0, "head_dx": 0.0, "head_dy": 0.0, "head_turn": 0.0,
                "crest": 0.0, "tail": 0.0, "tail_wag": 0.0,
                "hand_n_x": -22.0, "hand_n_y": 70.0, "hand_n_bend": 0.25, "paw_n": 0.0,
                "hand_f_x": 22.0, "hand_f_y": 70.0, "hand_f_bend": 0.25, "paw_f": 0.0,
                "foot_n_x": -8.0, "foot_n_y": 0.0, "foot_n_bend": 0.15, "foot_n_rot": 0.0,
                "foot_f_x": 10.0, "foot_f_y": 0.0, "foot_f_bend": 0.15, "foot_f_rot": 0.0,
                "mouth": "X", "stars": 0.0, "speed": 0.0, "holding": "", "eaten": 0.0,
            })

    def draw(self, ink: Ink, P: dict) -> None:
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        sq = P["squash"]
        sx, sy = sq ** -0.8, sq
        HP = (P["body_x"] * f, -142 + P["body_y"])
        lean = P["lean"] * f

        def T(p):
            x, y = (HP[0] + p[0]) * sx, (HP[1] + p[1]) * sy
            return rot((x, y), lean, (HP[0] * sx, HP[1] * sy))

        body = [T((lerp(a[0] * f, b[0] * f, s), lerp(a[1], b[1], s))) for a, b in zip(BODY_FRONT, BODY_SIDE)]
        neck = T((f * s * 14, -78))
        sh_n = T((lerp(-50 * f, -6 * f, s), lerp(-40, -38, s)))
        sh_f = T((lerp(50 * f, 16 * f, s), lerp(-40, -44, s)))
        hip_n = T((lerp(-22 * f, -4 * f, s), 50))
        hip_f = T((lerp(22 * f, 10 * f, s), 46))

        ht = lean * 0.4 + P["head_tilt"] * f
        hsq = sq ** 0.3
        C = (neck[0] + f * P["head_dx"] + math.sin(ht) * 62, neck[1] - 60 * hsq + P["head_dy"])
        hv = View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"])

        if P["speed"] > 0:
            self._speed_lines(ink, P, T((0, 0)), f)
        if not v.back:
            self._tail(ink, P, T, f, s)
        self._leg(ink, P, "f", hip_f, f, s, behind=True)
        self._wing(ink, P, "f", sh_f, f, s, behind=True)
        self._leg(ink, P, "n", hip_n, f, s)
        ink.shape(body, fill=PAL["brown"], shade=PAL["brown_shade"], shade_offset=(8, 9),
                  clip_extra=None if v.back else (lambda k: self._belly(k, T, f, s)))
        if v.back:
            self._tail(ink, P, T, f, s)
        self._head(ink, P, C, hv, ht, hsq)
        self._wing(ink, P, "n", sh_n, f, s, behind=False)
        if P["stars"] > 0:
            self._stars(ink, P, C)

    # ------------------------------------------------------------------ partes
    def _belly(self, k: Ink, T, f, s):
        c = T((f * s * 26, 4))
        k.shape(ellipse_pts(c[0], c[1], 54 - 14 * s, 68), fill=PAL["yellow"], line=0)
        c2 = T((f * s * 26 + 10, 18))
        k.shape(ellipse_pts(c2[0] + 14, c2[1] + 10, 46 - 12 * s, 60), fill=PAL["yellow_shade"], line=0)
        k.shape(ellipse_pts(c[0] - 4, c[1] - 6, 46 - 14 * s, 60), fill=PAL["yellow"], line=0)

    def _head(self, k: Ink, P, C, v: View, ht, hsq):
        f, s = v.f, v.side
        rx, ry = 66, 62 * hsq
        head = ellipse_pts(C[0], C[1], rx, ry, ht, 16)
        # topete na nuca (atrás)
        nx, nc = v.sphere(C[0], 58, math.pi * 0.85 * (-1 if f > 0 else 1) * 0 + (-2.3 if f > 0 else 2.3))
        if s > 0.25 or v.back:
            bx = C[0] - f * 40 * max(s, 0.3)
            by = C[1] - 50
            cr = P["crest"]
            tuft = [(bx, by + 18), (bx - f * (34 + 14 * cr), by - 22 - 20 * cr), (bx - f * 10, by - 2),
                    (bx - f * (22 + 10 * cr), by - 34 - 22 * cr), (bx + f * 12, by - 4)]
            k.shape(tuft, fill=PAL["black"], smooth=True, line=4)
        # bico atrás da cabeça quando de costas
        if v.back:
            k.shape(head, fill=PAL["black"], shade="#000000", shade_offset=(8, 8),
                    clip_extra=lambda kk: self._back_stripes(kk, C, ht))
            return

        def markings(kk: Ink):
            # boné preto (topo)
            cap = [(C[0] - 120, C[1] - 120), (C[0] + 120, C[1] - 120), (C[0] + 120, C[1] - 32), (C[0] - 120, C[1] - 32)]
            kk.shape([rot(p, ht, C) for p in cap], fill=PAL["black"], smooth=False, line=0)
            # máscara preta pelos lados (com abertura branca na frente, entre os olhos / atrás do bico)
            gx, gc = v.sphere(C[0], 66, 0.0)
            gap = 18 * (1 - s) + 6
            for side in (-1, 1):
                x_in = gx + side * gap
                x_out = C[0] + side * 130
                if s > 0.6 and side == f:          # no perfil a máscara começa logo atrás do bico
                    x_in = gx - f * 16
                    x_out = C[0] - f * 130
                band = [(x_in, C[1] - 6), (x_out, C[1] - 10), (x_out, C[1] + 22), (x_in, C[1] + 16)]
                kk.shape([rot(p, ht, C) for p in band], fill=PAL["black"], smooth=False, line=0)
            # garganta com sombra
            kk.shape(ellipse_pts(C[0] + 10, C[1] + 72, 70, 32, ht), fill=PAL["white_shade"], line=0)

        k.shape(head, fill=PAL["white"], clip_extra=markings)
        # olhos
        eyes = []
        for ang in (-0.42, 0.42):
            x, c = v.sphere(C[0], 46, ang)
            eyes.append((c, x, ang))
        eyes.sort()
        for c, x, ang in eyes:
            if c > 0.1:
                ex, ey = rot((x - C[0], -4), ht)
                self._eye(k, P, (C[0] + ex, C[1] + ey), max(c, 0.55), ang, f, s, ht)
        # bico
        self._beak(k, P, C, v, ht)
        # lágrimas / suor / rubor
        if P["tears"] > 0:
            for c, x, ang in eyes:
                if c > 0.2:
                    y0 = C[1] + 30
                    t = P["tears"]
                    k.shape([(x - 7, y0), (x + 7, y0), (x + 11, y0 + 46 * t), (x, y0 + 70 * t), (x - 11, y0 + 46 * t)],
                            fill=PAL["tear"], line=3)
        if P["sweat"] > 0:
            sx_ = C[0] - f * 70
            k.shape([(sx_, C[1] - 70), (sx_ + 10, C[1] - 44), (sx_, C[1] - 36), (sx_ - 10, C[1] - 44)], fill=PAL["sweat"], line=3)

    def _back_stripes(self, kk: Ink, C, ht):
        for y0, y1 in ((-24, -6), (18, 30)):
            band = [(C[0] - 120, C[1] + y0), (C[0] + 120, C[1] + y0), (C[0] + 120, C[1] + y1), (C[0] - 120, C[1] + y1)]
            kk.shape([rot(p, ht, C) for p in band], fill=PAL["white"], smooth=False, line=0)

    def _eye(self, k: Ink, P, E, c, ang, f, s, ht):
        es = P["eye_scale"]
        rx, ry = 22 * c * es, 28 * es
        ex, ey = E
        lid, lid_low = P["lid"], P["lid_low"]

        def inside(kk: Ink):
            lx = (P["look_x"] * f * 0.55 + 0.3 * f * s) * rx
            ly = P["look_y"] * 0.5 * ry
            pr = 10 * P["pupil"] * es ** 0.5
            kk.ellipse(ex + lx, ey + ly + 3, pr * max(c, 0.6), pr * 1.25, PAL["pupil"], line=0)
            kk.dot(ex + lx - pr * 0.35, ey + ly - pr * 0.4, max(2.2, pr * 0.32), "#FFFFFF")
            if lid > 0.01:
                top = ey - ry - 4 + (2 * ry + 8) * lid * 0.98
                kk.c.drawRect(_rect(ex - rx - 10, ey - ry - 40, ex + rx + 10, top), paint("#E9E5DA"))
                kk.stroke([(ex - rx - 4, top + 2), (ex, top + 4), (ex + rx + 4, top + 2)], 4)
            if lid_low > 0.01:
                bot = ey + ry + 4 - (ry * 1.2) * lid_low
                kk.c.drawRect(_rect(ex - rx - 10, bot, ex + rx + 10, ey + ry + 40), paint("#E9E5DA"))
                kk.stroke([(ex - rx - 2, bot), (ex, bot - 5), (ex + rx + 2, bot)], 3.5)

        k.shape(ellipse_pts(ex, ey, rx, ry, ht, 14), fill=PAL["eye"], line=4, clip_extra=inside)
        # sobrancelha (sobre a listra branca)
        inner = 1 if ang < 0 else -1
        b = P["brow_l"] if ang < 0 else P["brow_r"]
        by = ey - ry - 10 - P["brow_y"] * 9
        x0, x1 = ex - rx * 1.1 * inner, ex + rx * inner
        y0, y1 = by + b * 5, by + b * 13
        pts = [(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 5 + abs(b) * 3), (x1, y1)]
        k.stroke(pts, 16 * max(c, 0.6), taper=(0.3, 0.15), color_=PAL["black"])
        k.stroke(pts, 9 * max(c, 0.6), taper=(0.3, 0.15), color_=PAL["white"])

    def _beak(self, k: Ink, P, C, v: View, ht):
        f, s = v.f, v.side
        op = min(1.25, BEAK.get(P["mouth"], 0.0) + P["jaw"] * 0.7)
        smile = P["smile"]
        bx, _ = v.sphere(C[0], 58, 0.0)
        bpos = rot((bx - C[0], 16), ht)
        B = (C[0] + bpos[0], C[1] + bpos[1])
        ink_w = 4.5
        if s < 0.3:
            # de frente: triângulo de cima; a mandíbula de baixo desce ao abrir
            w, L = 19, 34
            drop = op * 26
            up = [rot((B[0] + x, B[1] + y), ht, B) for x, y in [(-w, -4), (w, -4), (0, L)]]
            if op > 0.04:
                cav = ellipse_pts(B[0], B[1] + 10 + drop * 0.5, w * 0.95, 8 + drop * 0.55, ht, 12)
                k.shape(cav, fill=PAL["mouth"], line=ink_w,
                        clip_extra=lambda kk: kk.ellipse(B[0], B[1] + 16 + drop * 0.8, w * 0.7, 6 + drop * 0.3, PAL["tongue"], line=0))
                lo = [rot((B[0] + x, B[1] + y), ht, B) for x, y in [(-w * 0.85, 6 + drop), (w * 0.85, 6 + drop), (0, L * 0.75 + drop)]]
                k.shape(lo, fill=PAL["beak"], smooth=False, line=ink_w)
            k.shape(up, fill=PAL["beak"], smooth=False, line=ink_w)
            k.stroke([rot((B[0] - w * 0.45, B[1] + 2), ht, B), rot((B[0] - 2, B[1] + L * 0.6), ht, B)], 3, color_="#6B6265")
            return
        # perfil / 3/4: duas mandíbulas articuladas na base
        u = min(1.0, (s - 0.3) / 0.5)
        dang = lerp(0.55, 0.06, u)                     # inclinação para baixo no 3/4
        L = lerp(56, 76, u)
        hh = 17
        a0 = ht + (dang if f > 0 else -dang)
        dirx, diry = math.cos(a0) * f, math.sin(a0) * (1 if f > 0 else -1) * f
        d = (dirx, diry)
        nrm = (-d[1] * f, d[0] * f)                     # "para baixo" em relação ao bico
        if nrm[1] < 0:
            nrm = (-nrm[0], -nrm[1])
        open_a = op * 0.8 * f
        B0 = (B[0] - d[0] * 10, B[1] - d[1] * 10)       # base recuada (entra no rosto)

        def P_(along, down, dd=d, nn=nrm, base=B0):
            return (base[0] + dd[0] * along + nn[0] * down, base[1] + dd[1] * along + nn[1] * down)
        dl = rot(d, open_a)
        nl = rot(nrm, open_a)
        tip_u = P_(L, 2)
        tip_l = P_(L * 0.88, 0, dl, nl)
        if op > 0.04:
            cav = [P_(4, 0), tip_u, P_(L * 0.5, 4), tip_l, P_(L * 0.4, 2, dl, nl), P_(2, hh * 0.6, dl, nl)]
            k.shape([P_(0, -2), P_(L * 0.75, 3), P_(L * 0.7, 2, dl, nl), P_(0, hh * 0.7, dl, nl)], fill=PAL["mouth"],
                    smooth=False, line=0)
            if op > 0.25:
                tq = P_(L * 0.35, 4, dl, nl)
                k.ellipse(tq[0], tq[1], 13 + 4 * op, 6 + 2 * op, PAL["tongue"], rot=math.atan2(dl[1], dl[0]), line=0)
        lo = [P_(0, 0, dl, nl), tip_l, P_(L * 0.25, hh * 0.75, dl, nl), P_(0, hh * 0.8, dl, nl)]
        k.shape(lo, fill=PAL["beak"], smooth=False, line=ink_w)
        up = [P_(0, -hh), P_(L * 0.45, -hh * 0.55), tip_u, P_(L * 0.5, 2), P_(0, 3)]
        k.shape(up, fill=PAL["beak"], smooth=False, line=ink_w)
        k.stroke([P_(8, -hh * 0.55), P_(L * 0.6, -hh * 0.2)], 3, color_="#6B6265")
        # canto da boca com sorriso
        cpt = P_(-2, 3)
        k.stroke([cpt, (cpt[0] - f * 12, cpt[1] - 8 * smile)], 4, taper=(0.1, 0.5))

    def _wing(self, k: Ink, P, which, S, f, s, behind):
        hx = P[f"hand_{which}_x"] * f
        hy = P[f"hand_{which}_y"]
        H = (S[0] + hx, S[1] + hy)
        bend = P[f"hand_{which}_bend"]
        dx, dy = H[0] - S[0], H[1] - S[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if nx * -f < 0:
            nx, ny = -nx, -ny
        mid = ((S[0] + H[0]) / 2 + nx * bend * L, (S[1] + H[1]) / 2 + ny * bend * L)
        fill = PAL["brown_shade"] if behind else PAL["brown"]
        k.tube([S, mid, H], 30, 20, fill=fill)
        if which == "n" and P.get("holding") == "torta":
            from .props import PIE_SCALE, draw_pie
            draw_pie(k, H[0] + f * 10, H[1] - 2, PIE_SCALE, P.get("eaten", 0.0), -1.0, tilt=0.08 * f)
        # penas-dedo
        d = (dx / L, dy / L)
        base_a = math.atan2(d[1], d[0])
        kind = P[f"paw_{which}"]
        spreads = {0: (-0.45, 0.0, 0.45), 1: (-0.15, 0.0, 0.15), 2: (-0.9, 0.0, 0.9), 3: (-0.6, 0.0, 0.6)}
        sp = spreads.get(int(round(kind)), spreads[0])
        lens = (30, 40, 30) if kind != 2 else (22, 46, 22)
        for a, ln in zip(sp, lens):
            ang = base_a + a
            p0 = (H[0] + math.cos(ang) * 4, H[1] + math.sin(ang) * 4)
            p1 = (H[0] + math.cos(ang) * ln, H[1] + math.sin(ang) * ln)
            k.shape(ellipse_pts((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, ln * 0.55, 8.5, ang, 10), fill=fill, line=4)

    def _leg(self, k: Ink, P, which, Hp, f, s, behind=False):
        fx = P[f"foot_{which}_x"] * f
        F = (Hp[0] + fx, P[f"foot_{which}_y"])
        knee = ((Hp[0] + F[0]) / 2 - f * P[f"foot_{which}_bend"] * 30, (Hp[1] + F[1]) / 2)
        col = PAL["legs"] if not behind else "#4A4240"
        k.tube([Hp, knee, (F[0], F[1] - 6)], 11, 8, fill=col, line=4)
        rotf = P[f"foot_{which}_rot"] * f
        toes = [(-0.15, 26), (0.25, 24), (-0.55, 20)] if s > 0.4 else [(-0.9, 20), (0.0, 22), (0.9, 20)]
        for a, ln in toes:
            if s > 0.4:
                ang = (0 if f > 0 else math.pi) + a * f + rotf
            else:
                ang = math.pi / 2 + a
            k.stroke([(F[0], F[1] - 4), (F[0] + math.cos(ang) * ln, F[1] - 4 + math.sin(ang) * ln * (0.25 if s > 0.4 else 0.35))],
                     8, taper=(0.0, 0.5), color_=col)
        if s > 0.4:
            k.stroke([(F[0], F[1] - 4), (F[0] - f * 14, F[1] - 2)], 7, taper=(0.0, 0.6), color_=col)

    def _tail(self, k: Ink, P, T, f, s):
        base = T((-f * (40 + 22 * s), 34))
        wag = P["tail"] + P["tail_wag"]
        for i, a in enumerate((-0.35, 0.0, 0.35)):
            ang = (math.pi - 0.55 if f > 0 else 0.55) + a * (0.4 + 0.6 * (1 - s)) + wag * -f
            ang = ang if s > 0.2 else math.pi / 2 + a * 1.4
            L = 70 - abs(a) * 16
            tip = (base[0] + math.cos(ang) * L, base[1] + math.sin(ang) * L * (1 if s > 0.2 else 0.6))
            k.shape(ellipse_pts((base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2, L * 0.55, 13, ang, 12),
                    fill=PAL["brown_shade"] if i != 1 else PAL["brown"], line=4.5)

    def _speed_lines(self, k: Ink, P, hp, f):
        n = int(4 + P["speed"] * 4)
        for i in range(n):
            y = hp[1] - 170 + i * (190 / n)
            x0 = hp[0] - f * (80 + (i * 29) % 40)
            k.stroke([(x0, y), (x0 - f * (90 + 120 * P["speed"]), y)], 4, taper=(0.05, 0.9), color_=(0.13, 0.09, 0.08, 0.55))

    def _stars(self, k: Ink, P, C):
        ph = P["stars"] * 6.28
        for i in range(3):
            a = ph + i * 2.09
            x, y = C[0] + math.cos(a) * 80, C[1] - 80 + math.sin(a) * 22
            pts = [(x + math.cos(j * math.pi / 5 - math.pi / 2) * (16 if j % 2 == 0 else 7),
                    y + math.sin(j * math.pi / 5 - math.pi / 2) * (16 if j % 2 == 0 else 7)) for j in range(10)]
            k.shape(pts, fill="#FFE14D", smooth=False, line=3.5)


def _rect(l, t, r, b):
    import skia
    return skia.Rect(l, t, r, b)
