"""Muriçocas da turma (v2) — Laurinha e Luizinho como mosquitinhos fofos, a partir da referência do usuário.

Corpo em pé (2 braços + 2 pernas) para ANDAR, ACENAR e VOAR:
cabeça grande e redonda com volume suave, olhões contornados com muito brilho, sobrancelhas grossas, bocão sorridente,
antenas com pompom felpudo, tórax com camisetinha, abdômen listrado atrás, braços e pernas finos e escuros com mãozinhas,
tênis grandes com estrela e sola colorida, 2 pares de asas iridescentes com nervuras.

Canal `fly` (0 = no chão, 1 = voando): no ar as asas batem rápido, o corpo paira e as pernas ficam penduradas;
no chão as asas descansam com uma vibração leve e as pernas andam (mesmos ciclos de caminhada da turma).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import skia

from ..drawing.ink import Brush, Ink, ellipse_pts, paint
from .base import Character, View, lerp, rot
from .kit import Kit, Style, darken, ik2, lighten

SOFT = Style(width=2.4, vary=0.0, ink_k=0.6, shade_k=0.78, soft=True)
LIMB = "#3A2A40"          # braços e pernas finos e escuros
OUTLINE = "#2A1C24"
EYE_BRUSH = Brush(6.5, 0.1, (0.16, 0.11, 0.14, 1.0))


def _star(k: Ink, x, y, r, col, line=0.0, kit: Kit | None = None):
    pts = [(x + math.cos(-math.pi / 2 + j * math.pi / 5) * (r if j % 2 == 0 else r * 0.42),
            y + math.sin(-math.pi / 2 + j * math.pi / 5) * (r if j % 2 == 0 else r * 0.42)) for j in range(10)]
    k.shape(pts, fill=col, smooth=False, line=line, brush=kit.brush(col, line) if (kit and line) else None)


@dataclass
class MuriLook:
    head: str = "#9CD3F7"
    top: str = "#5BA8F0"               # camiseta/tórax
    stripe_a: str = "#FFD23F"
    stripe_b: str = "#22305E"
    shoe: str = "#3E73E0"
    sole: str = "#FFB23A"
    pom: str = "#3E73E0"
    eye: str = "#2B1720"
    lashes: bool = False
    bow: str = ""                      # cor do laço ("" = sem laço)
    wing_tint: tuple = (0.75, 0.9, 1.0)
    extra: dict = field(default_factory=dict)


class Muricoca(Character):
    flies = True

    def __init__(self, cid: str, name: str, look: MuriLook):
        self.look = look
        super().__init__(
            id=cid, name=name, canvas=(820, 760), anchor=(410, 690), height=470, palette=look.__dict__,
            defaults={
                "turn": 0.2, "back": False, "lean": 0.0, "squash": 1.0, "body_y": 0.0, "body_x": 0.0,
                "head_tilt": 0.0, "head_dx": 0.0, "head_dy": 0.0, "head_turn": 0.0,
                "hand_n_x": -60.0, "hand_n_y": 70.0, "hand_n_bend": 0.3, "paw_n": 0.0,
                "hand_f_x": 60.0, "hand_f_y": 70.0, "hand_f_bend": -0.3, "paw_f": 0.0,
                "foot_n_x": -14.0, "foot_n_y": 0.0, "foot_n_bend": 0.0, "foot_n_rot": 0.0,
                "foot_f_x": 16.0, "foot_f_y": 0.0, "foot_f_bend": 0.0, "foot_f_rot": 0.0,
                "mouth": "X", "smile": 0.85, "brow_y": 0.3, "blush": 0.8, "stars": 0.0, "speed": 0.0,
                "holding": "", "wing_phase": 0.0, "bank": 0.0, "dangle": 0.0, "hair_bounce": 0.0,
                "fly": 0.0, "rot_pivot": 0.55,
            })

    # ------------------------------------------------------------------ corpo
    def draw(self, ink: Ink, P: dict) -> None:
        L = self.look
        kit = Kit(ink, SOFT)
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        fly = max(0.0, min(1.0, P.get("fly", 0.0)))
        sq = P["squash"]
        lift = 170 * fly                                   # altura do voo acima do chão
        hip = (P["body_x"] * f, -132 + P["body_y"] - lift)
        ang = (P["lean"] + P.get("bank", 0.0) * fly) * f

        def T(p):
            x, y = hip[0] + p[0] * sq ** -0.6, hip[1] + p[1] * sq
            return rot((x, y), ang, hip)

        # sombra no chão (menor e mais clara quando voa)
        ink.shape(ellipse_pts(hip[0] * 0.3, -6, 90 - 35 * fly, 14 - 5 * fly, 0, 16), fill=(0, 0, 0, 0.14 - 0.07 * fly), line=0)
        shoulder_n = T((lerp(-34 * f, -6 * f, s), -70))
        shoulder_f = T((lerp(34 * f, 8 * f, s), -70))
        hip_n, hip_f = T((lerp(-18 * f, -4 * f, s), 0)), T((lerp(18 * f, 6 * f, s), -2))
        C = T((f * s * 10 + P["head_dx"] * f, -178 + P["head_dy"]))
        hv = View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"])
        ht = ang * 0.5 + P["head_tilt"] * f

        self._wings(kit, P, T((-f * 14, -80)), f, s, fly, far=True)
        self._arm(kit, P, "f", shoulder_f, f, behind=True)
        self._abdomen(kit, T, f, s)
        self._leg(kit, P, "f", hip_f, f, s, fly, behind=True)
        self._leg(kit, P, "n", hip_n, f, s, fly, behind=False)
        # tórax com camisetinha (gota arredondada)
        torso = [T(p) for p in ((-30 * f, -84), (30 * f, -84), (40 * f, -40), (36 * f, -4), (0, 6), (-36 * f, -4), (-40 * f, -40))]
        kit.blob(torso, L.top, clip_extra=lambda kk: self._shirt(kk, T, v, f, s))
        self._wings(kit, P, T((-f * 8, -82)), f, s, fly, far=False)
        self._head(kit, P, C, hv, ht)
        self._arm(kit, P, "n", shoulder_n, f, behind=False)

    def _shirt(self, kk: Ink, T, v: View, f, s):
        L = self.look
        if v.back:
            return
        if L.extra.get("listras_peito"):
            for y in (-70, -22):
                a, b = T((-44 * f, y)), T((44 * f, y))
                kk.stroke([a, b], 9, taper=(0, 0), color_=L.stripe_b)
        c = T((f * s * 14, -44))
        _star(kk, c[0], c[1], 14, "#FFD23F")

    def _abdomen(self, kit: Kit, T, f, s):
        """Barriguinha listrada atrás do corpo (a 'cauda' de mosquito)."""
        L = self.look
        pts = [T(p) for p in ((-f * 10, -54), (-f * 60, -66), (-f * 112, -48), (-f * 138, -14), (-f * 120, 18), (-f * 70, 22), (-f * 18, 4))]

        def stripes(kk: Ink):
            for j in range(4):
                a, b = T((-f * (44 + j * 24), -90)), T((-f * (40 + j * 24), 40))
                kk.stroke([a, b], 13, taper=(0, 0), color_=L.stripe_b)
        kit.blob(pts, L.stripe_a, clip_extra=stripes)

    def _arm(self, kit: Kit, P, which, S, f, behind):
        T_ = (S[0] + P[f"hand_{which}_x"] * f * 0.62, S[1] + P[f"hand_{which}_y"] * 0.62)
        bend = P[f"hand_{which}_bend"]
        E, H = ik2(S, T_, 44, 42, (-f if bend >= 0 else f, 0.4))
        col = darken(LIMB, 0.8) if behind else LIMB
        kit.k.tube([S, E], 15, 14, fill=col, line=0)
        kit.k.tube([E, H], 14, 13, fill=col, line=0)
        dx, dy = H[0] - E[0], H[1] - E[1]
        Ln = math.hypot(dx, dy) or 1
        self._hand(kit, H, (dx / Ln, dy / Ln), P[f"paw_{which}"], col)

    def _hand(self, kit: Kit, H, d, kind, col):
        """Mãozinha escura de 4 dedos: aberta (acenando) ou fechadinha."""
        k = kit.k
        a0 = math.atan2(d[1], d[0])
        k.ellipse(H[0] + d[0] * 6, H[1] + d[1] * 6, 11, 10, col, line=0)
        spread = (-0.9, -0.3, 0.3, 0.9) if kind >= 2.5 else (-0.35, -0.1, 0.15, 0.4)
        ln = 20 if kind >= 2.5 else 12
        for a in spread:
            ang = a0 + a
            p0 = (H[0] + d[0] * 6 + math.cos(ang) * 6, H[1] + d[1] * 6 + math.sin(ang) * 6)
            p1 = (p0[0] + math.cos(ang) * ln, p0[1] + math.sin(ang) * ln)
            k.stroke([p0, p1], 6.5, taper=(0.0, 0.2), color_=col)
        ta = a0 - 1.5
        k.stroke([(H[0] + math.cos(ta) * 6, H[1] + math.sin(ta) * 6), (H[0] + math.cos(ta) * 18, H[1] + math.sin(ta) * 18)], 6.5,
                 taper=(0, 0.2), color_=col)

    def _leg(self, kit: Kit, P, which, Hp, f, s, fly, behind):
        if fly > 0.5:          # no ar: pernas penduradas para trás, joelho dobrado (com inércia)
            dg = P.get("dangle", 0.0)
            F = (Hp[0] - f * (20 + 40 * dg) + (10 if which == "n" else -10), Hp[1] + 96 - 12 * dg)
        else:
            F = (Hp[0] + P[f"foot_{which}_x"] * f * 0.7, P[f"foot_{which}_y"] * 0.7)
        ankle = (F[0], F[1] - 22)
        K, A = ik2(Hp, ankle, 58, 58, (f, 0.0))
        col = darken(LIMB, 0.8) if behind else LIMB
        kit.k.tube([Hp, K], 16, 15, fill=col, line=0)
        kit.k.tube([K, A], 15, 14, fill=col, line=0)
        self._shoe(kit, (A[0], A[1] + 22), f, s, P[f"foot_{which}_rot"] * f + (0.35 * f if fly > 0.5 else 0), behind)

    def _shoe(self, kit: Kit, F, f, s, rotf, behind):
        """Tênis grandão: cabedal colorido, cadarço branco, estrela e sola colorida."""
        L = self.look
        col = darken(L.shoe, 0.85) if behind else L.shoe
        c = kit.k.c
        c.save()
        c.translate(F[0], F[1])
        c.rotate(math.degrees(rotf))
        w = lerp(40, 52, s)
        kit.blob([(-w * 0.75 * f, -8), (-w * 0.7 * f, -40), (-w * 0.1 * f, -48), (w * 0.55 * f, -34), (w * 1.0 * f, -16),
                  (w * 1.05 * f, -6), (0, -2)], col)
        kit.blob([(-w * 0.85 * f, -12), (w * 1.12 * f, -12), (w * 1.1 * f, 2), (-w * 0.8 * f, 2)], L.sole, smooth=True, shade=False)
        for j in range(3):          # cadarço
            x = (-w * 0.25 + j * 13) * f
            kit.k.stroke([(x - 6, -38 + j * 4), (x + 6, -30 + j * 4)], 3.5, color_="#FFFFFF")
        _star(kit.k, -w * 0.35 * f, -22, 10, "#FFD23F")
        c.restore()

    def _wings(self, kit: Kit, P, A, f, s, fly, far: bool):
        """Dois pares de asas iridescentes com nervuras. Voando: batem rápido com borrão; no chão: tremidinha."""
        L = self.look
        ph = P.get("wing_phase", 0.0)
        amp = lerp(0.12, 0.75, fly)
        ghosts = ((0, 0.6), (1, 0.25), (2, 0.12)) if fly > 0.5 else ((0, 0.6),)
        for Lw, Ww, base_ang in ((175, 66, -0.35), (125, 48, -0.95)):
            for k, alpha in ghosts:
                a = math.sin((ph - k * 0.1) * 2 * math.pi)
                angw = (base_ang - amp * a) * f + (0.25 * f if far else 0) - f * 0.35
                cx = A[0] + math.cos(-math.pi / 2 + angw) * Lw * 0.5
                cy = A[1] + math.sin(-math.pi / 2 + angw) * Lw * 0.5
                pts = ellipse_pts(cx, cy, Ww, Lw * 0.55, angw, 18)
                path = skia.Path()
                path.addPoly([skia.Point(*p) for p in pts], True)
                sh = skia.GradientShader.MakeLinear(
                    [skia.Point(A[0], A[1]), skia.Point(cx * 2 - A[0], cy * 2 - A[1])],
                    [skia.Color4f(*L.wing_tint, alpha * 0.8).toColor(), skia.Color4f(1.0, 0.85, 0.95, alpha * 0.6).toColor(),
                     skia.Color4f(0.85, 1.0, 0.95, alpha * 0.45).toColor()])
                kit.k.c.drawPath(path, skia.Paint(AntiAlias=True, Shader=sh))
                if k == 0:
                    edge = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.2)
                    edge.setColor4f(skia.Color4f(0.55, 0.65, 0.85, 0.75))
                    kit.k.c.drawPath(path, edge)
                    tip = (A[0] + (cx - A[0]) * 1.8, A[1] + (cy - A[1]) * 1.8)
                    for t_ in (0.3, 0.7):      # nervuras
                        side = (cx + math.cos(angw) * Ww * (t_ - 0.5) * 1.4, cy + math.sin(angw) * Ww * (t_ - 0.5) * 1.4)
                        kit.k.stroke([A, side, tip], 1.6, color_=(0.55, 0.65, 0.85, 0.6))

    # ------------------------------------------------------------------ cabeça
    def _head(self, kit: Kit, P, C, v: View, ht):
        L = self.look
        f, s = v.f, v.side
        k = kit.k
        r = 104
        for side in (-1, 1):       # antenas com pompom felpudo
            b = rot((C[0] + side * 30 + f * s * 12, C[1] - r * 0.86), ht, C)
            sway = P.get("hair_bounce", 0.0) * 0.6 + P["head_tilt"] * 0.8
            tip = (b[0] + side * 34 + f * 6 + sway * 30, b[1] - 92)
            k.stroke([b, (b[0] + side * 4, b[1] - 52), tip], 8, taper=(0.1, 0.0), color_=LIMB)
            kit.blob(ellipse_pts(tip[0], tip[1], 22, 21, 0, 16), L.pom)
            for j in range(7):      # textura felpuda
                a = j * 0.9
                k.dot(tip[0] + math.cos(a) * 13, tip[1] + math.sin(a) * 12, 3.2, lighten(L.pom, 0.35))
        kit.blob(ellipse_pts(C[0], C[1], r, r * 0.95, ht, 28), L.head)
        if L.bow and not v.back:
            self._bow(kit, rot((C[0] - 46 + f * s * 10, C[1] - r * 0.78), ht, C))
        if v.back:
            return
        for side in (-1, 1):       # bochechas
            x, c = v.sphere(C[0], r * 0.9, side * 0.68)
            if c > 0.25:
                q = rot((x, C[1] + 30), ht, C)
                k.ellipse(q[0], q[1], 22 * c, 13, (1.0, 0.45, 0.55, 0.3 + 0.25 * P.get("blush", 0.8)), line=0)
        for side in (-1, 1):
            x, c = v.sphere(C[0], r * 0.8, side * 0.42)
            if c > 0.3:
                self._eye(kit, P, rot((x, C[1] - 4), ht, C), c, side, f, s, ht)
        nx_, _ = v.sphere(C[0], r * 0.95, 0.0)
        N = rot((nx_ + f * s * 8, C[1] + 34), ht, C)
        k.ellipse(N[0], N[1], 7, 5, darken(L.head, 0.8), line=0)
        M = rot((nx_ - f * s * 6, C[1] + 60), ht, C)
        kit.mouth(P, M, f, s, ht, width=30, line=OUTLINE, lips=OUTLINE, tongue="#F2788A", inside_col="#8A2236")

    def _bow(self, kit: Kit, B):
        L = self.look
        for wing in (-1, 1):
            kit.blob([(B[0], B[1]), (B[0] + wing * 52, B[1] - 34), (B[0] + wing * 60, B[1] + 6), (B[0] + wing * 44, B[1] + 30)], L.bow)
            for j in range(3):
                kit.k.dot(B[0] + wing * (24 + j * 10), B[1] - 6 + j * 6, 2.6, lighten(L.bow, 0.5))
        kit.blob(ellipse_pts(B[0], B[1], 16, 15, 0, 12), darken(L.bow, 0.88))
        _star(kit.k, B[0], B[1], 17, "#FFD23F", line=2.2, kit=kit)

    def _eye(self, kit: Kit, P, E, c, side, f, s, ht):
        """Olhão: branco com contorno grosso, íris escura grande com 3 brilhos, cílios (Laurinha), sobrancelha grossa."""
        L = self.look
        k = kit.k
        ex, ey = E
        es = P["eye_scale"]
        rx, ry = 34 * c * es, 42 * es
        if P.get("eyes_happy", 0) > 0.5:
            k.stroke([(ex - rx, ey + 8), (ex, ey - ry * 0.45), (ex + rx, ey + 8)], 9, taper=(0.3, 0.3), color_=OUTLINE)
        else:
            lid = P["lid"]
            lx = (P["look_x"] * f * 0.45 + 0.2 * f * s) * rx
            ly = P["look_y"] * 0.4 * ry

            def inside(kk: Ink):
                pr = ry * 0.66 * P["pupil"] ** 0.4
                kk.ellipse(ex + lx, ey + ly + 4, pr * 0.86 * max(c, 0.6), pr, L.eye, line=0)
                kk.ellipse(ex + lx, ey + ly + 4 + pr * 0.35, pr * 0.6 * max(c, 0.6), pr * 0.45, lighten(L.eye, 0.3), line=0)
                kk.dot(ex + lx - pr * 0.32, ey + ly - pr * 0.34, max(4, pr * 0.3), "#FFFFFF")
                kk.dot(ex + lx + pr * 0.28, ey + ly + pr * 0.3, max(2, pr * 0.14), "#FFFFFF")
                kk.dot(ex + lx + pr * 0.36, ey + ly - pr * 0.12, max(1.5, pr * 0.08), "#FFFFFF")
                if lid > 0.02:
                    top = ey - ry - 4 + (2 * ry + 8) * lid
                    kk.c.drawRect(skia.Rect(ex - rx - 8, ey - ry - 30, ex + rx + 8, top), paint(L.head))
                    kk.stroke([(ex - rx - 2, top), (ex + rx + 2, top)], 6, color_=OUTLINE)
            k.shape(ellipse_pts(ex, ey, rx, ry, ht, 18), fill="#FFFFFF", brush=EYE_BRUSH, clip_extra=inside)
            if L.lashes:            # cílios no canto externo
                for j in range(3):
                    a = -0.9 + j * 0.32
                    p0 = (ex + side * rx * math.cos(a) * 0.95, ey + ry * math.sin(a) * 0.95)
                    p1 = (p0[0] + side * 14, p0[1] - 10 + j * 3)
                    k.stroke([p0, p1], 5, taper=(0.1, 0.6), color_=OUTLINE)
        b = P["brow_l"] if side < 0 else P["brow_r"]
        by = ey - ry - 14 - P["brow_y"] * 10
        k.stroke([(ex - 26 * c, by + (b * 9 if side > 0 else -b * 3) + 4), (ex, by - 6),
                  (ex + 26 * c, by + (b * 9 if side < 0 else -b * 3) + 4)], 11 * max(c, 0.6), taper=(0.35, 0.35), color_=OUTLINE)


LAURINHA_M = MuriLook(head="#F7A1C4", top="#FF5FA2", stripe_a="#FF8FC0", stripe_b="#7A2050", shoe="#E83E9A", sole="#FFC93C",
                      pom="#FF4F8F", lashes=True, bow="#FF4F9A", wing_tint=(1.0, 0.82, 0.95))
LUIZINHO_M = MuriLook(head="#5EA9F2", top="#3E7BE0", stripe_a="#FFD23F", stripe_b="#1E2A5A", shoe="#2F6FE0", sole="#FFB23A",
                      pom="#3A6FD8", wing_tint=(0.75, 0.9, 1.0), extra={"listras_peito": True})
