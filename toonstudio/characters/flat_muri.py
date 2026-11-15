"""Laurinha (muriçoca) e Luisinho (mosquito) no estilo oficial da BIBLIA_VISUAL.md.

Regras aplicadas (ver BIBLIA_VISUAL.md §3):
- preenchimento CHAPADO (sem gradiente, brilho, sombra interna ou desfoque);
- contorno = cor da peça escurecida, espessura UNIFORME ≈ 1,1 % da altura, pontas arredondadas;
- braços e pernas em TRAÇO, mãos de 3 dedos-traço; olho = elipse branca contornada + pupila-ponto;
  bochecha = círculo chapado; detalhes internos = traços soltos;
- asas chapadas brancas semitransparentes; batida de asa em 3 poses (sem borrão).
Canais de pose iguais aos da turma (coreografia, expressões e visemas funcionam igual) + `fly`, `wing_phase`, `dangle`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import skia

from ..drawing.ink import Brush, Ink, ellipse_pts
from .base import Character, View, lerp, rot
from .kit import ik2

H_REF = 470.0
LINE = H_REF * 0.0115            # ≈ 5,4 unidades — contorno padrão (BÍBLIA §3.1)
LIMB = LINE * 1.9                # braços/pernas em traço
PUPIL = "#000000"


def dark(hex_color: str, k: float = 0.82) -> str:
    """Cor de contorno: a própria cor escurecida (e levemente mais saturada)."""
    c = hex_color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    m = max(r, g, b)
    r, g, b = (int(v * k - (m - v) * 0.12) for v in (r, g, b))
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, v)) for v in (r, g, b)))


def _rgba(h: str, a: float = 1.0):
    c = h.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


@dataclass
class FlatLook:
    body: str                  # cabeça + tórax
    belly_a: str               # listras do abdômen
    belly_b: str
    shoe: str
    sole: str
    pom: str                   # bolinha das antenas
    cheek: str
    lashes: bool = False
    bow: str = ""              # laço (Laurinha)
    curl: bool = False         # topetinho em espiral (Luisinho)
    extra: dict = field(default_factory=dict)


class FlatMuri(Character):
    flies = True

    def __init__(self, cid: str, name: str, look: FlatLook):
        self.look = look
        super().__init__(
            id=cid, name=name, canvas=(820, 760), anchor=(410, 690), height=H_REF, palette=look.__dict__,
            defaults={
                "turn": 0.15, "back": False, "lean": 0.0, "squash": 1.0, "body_y": 0.0, "body_x": 0.0,
                "head_tilt": 0.0, "head_dx": 0.0, "head_dy": 0.0, "head_turn": 0.0,
                "hand_n_x": -55.0, "hand_n_y": 75.0, "hand_n_bend": 0.3, "paw_n": 0.0,
                "hand_f_x": 55.0, "hand_f_y": 75.0, "hand_f_bend": -0.3, "paw_f": 0.0,
                "foot_n_x": -14.0, "foot_n_y": 0.0, "foot_n_bend": 0.0, "foot_n_rot": 0.0,
                "foot_f_x": 16.0, "foot_f_y": 0.0, "foot_f_bend": 0.0, "foot_f_rot": 0.0,
                "mouth": "X", "smile": 0.8, "brow_y": 0.2, "blush": 1.0, "stars": 0.0, "speed": 0.0,
                "holding": "", "wing_phase": 0.0, "bank": 0.0, "dangle": 0.0, "hair_bounce": 0.0,
                "fly": 0.0, "rot_pivot": 0.55,
            })

    # ------------------------------------------------------------------ primitivas chapadas
    def _shape(self, k: Ink, pts, fill: str, line: str | None = None, alpha: float = 1.0, w: float = LINE, smooth=True):
        """Forma chapada com contorno uniforme na cor da peça escurecida."""
        br = Brush(width=w, vary=0.0, ink=_rgba(line or dark(fill)), jitter=0.0)
        return k.shape(pts, fill=_rgba(fill, alpha), brush=br, smooth=smooth, line=w)

    def _line(self, k: Ink, pts, col: str, w: float = LINE, alpha: float = 1.0):
        k.stroke(pts, w, taper=(0.0, 0.0), color_=_rgba(col, alpha))

    # ------------------------------------------------------------------ corpo
    def draw(self, ink: Ink, P: dict) -> None:
        L = self.look
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        fly = max(0.0, min(1.0, P.get("fly", 0.0)))
        sq = P["squash"]
        hip = (P["body_x"] * f, -104 + P["body_y"] - 165 * fly)
        ang = (P["lean"] + P.get("bank", 0.0) * fly) * f

        def T(p):
            return rot((hip[0] + p[0] * sq ** -0.5, hip[1] + p[1] * sq), ang, hip)

        # sombra chapada no chão (BÍBLIA §3.6)
        ink.shape(ellipse_pts(hip[0] * 0.3, -4, 82 - 32 * fly, 12 - 4 * fly, 0, 16),
                  fill=(0, 0, 0, 0.13 - 0.06 * fly), line=0)
        C = T((f * s * 8 + P["head_dx"] * f, -196 + P["head_dy"]))
        hv = View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"])
        ht = ang * 0.5 + P["head_tilt"] * f

        # asas: as duas ATRÁS do corpo, saindo das costas (de frente abrem para os lados; de perfil vão para trás)
        for side in (-1, 1):
            self._wing(ink, P, T((side * 10 * (1 - s) - f * 10 * s, -66)), f, fly, far=(side == f), side=side, s=s)
        self._abdomen(ink, T, f)
        self._arm(ink, P, "f", T((lerp(38 * f, 8 * f, s), -62)), f, behind=True)
        self._leg(ink, P, "f", T((lerp(16 * f, 6 * f, s), -2)), f, s, fly, behind=True)
        self._leg(ink, P, "n", T((lerp(-16 * f, -4 * f, s), 0)), f, s, fly, behind=False)
        # tórax (gota) — mesma cor do corpo
        self._shape(ink, [T(p) for p in ((0, -80), (30, -74), (44, -44), (44, -10), (26, 10), (0, 14), (-26, 10), (-44, -10), (-44, -44), (-30, -74))], L.body)
        self._head(ink, P, C, hv, ht)
        self._arm(ink, P, "n", T((lerp(-38 * f, -6 * f, s), -62)), f, behind=False)

    def _abdomen(self, k: Ink, T, f):
        """Barriguinha listrada atrás (gota inclinada para trás/baixo), listras chapadas recortadas."""
        L = self.look
        pts = [T(p) for p in ((-f * 8, -50), (-f * 56, -64), (-f * 106, -48), (-f * 130, -16), (-f * 114, 14), (-f * 66, 18), (-f * 16, 2))]
        P_ = k.shape(pts, fill=_rgba(L.belly_a), line=0)
        path = skia.Path()
        path.addPoly([skia.Point(*p) for p in P_], True)
        k.c.save()
        k.c.clipPath(path, doAntiAlias=True)
        for j in range(3):
            a, b = T((-f * (48 + j * 26), -90)), T((-f * (44 + j * 26), 40))
            self._line(k, [a, b], L.belly_b, w=14)
        k.c.restore()
        k.shape(P_, fill=None, brush=Brush(LINE, 0.0, _rgba(dark(L.belly_a)), 0.0), dense=True, line=LINE)

    def _wing(self, k: Ink, P, A, f, fly, far: bool, side: int = 1, s: float = 0.0):
        """Asa chapada branca semitransparente. Batida em 3 poses (sem borrão); parada no chão."""
        ph = P.get("wing_phase", 0.0)
        if fly > 0.5:
            beat = (0.0, 0.45, 0.9)[int(ph * 3) % 3]          # 3 poses discretas
        else:
            beat = 0.25 + 0.04 * math.sin(ph * 2 * math.pi)
        # direção: de frente cada asa vai para o seu lado; de perfil, ambas para trás
        dirx = lerp(float(side), -f * (1.0 if far else 0.8), s)
        base = math.atan2(-1.0, dirx * 1.15)                   # ângulo para cima/fora
        for (Lw, Ww, extra) in ((150, 52, 0.0), (104, 36, 0.55)):
            a = base + (beat + extra) * (1 if math.cos(base) >= 0 else -1)
            cx, cy = A[0] + math.cos(a) * Lw * 0.5, A[1] + math.sin(a) * Lw * 0.5
            self._shape(k, ellipse_pts(cx, cy, Lw * 0.55, Ww, a, 18), "#FFFFFF", line="#9CC9EA", alpha=0.6 if far else 0.8)
            self._line(k, [A, (cx, cy), (A[0] + (cx - A[0]) * 1.7, A[1] + (cy - A[1]) * 1.7)], "#9CC9EA", w=LINE * 0.6)

    def _arm(self, k: Ink, P, which, S, f, behind):
        T_ = (S[0] + P[f"hand_{which}_x"] * f * 0.62, S[1] + P[f"hand_{which}_y"] * 0.62)
        bend = P[f"hand_{which}_bend"]
        E, H = ik2(S, T_, 42, 40, (-f if bend >= 0 else f, 0.4))
        col = dark(self.look.body, 0.72 if behind else 0.8)
        self._line(k, [S, E, H], col, w=LIMB)
        d = (H[0] - E[0], H[1] - E[1])
        a0 = math.atan2(d[1], d[0])
        spread = (-0.7, 0.0, 0.7) if P[f"paw_{which}"] >= 2.5 else (-0.35, 0.0, 0.35)
        ln = 15 if P[f"paw_{which}"] >= 2.5 else 10
        for a in spread:                      # mão = 3 dedos-traço
            self._line(k, [H, (H[0] + math.cos(a0 + a) * ln, H[1] + math.sin(a0 + a) * ln)], col, w=LIMB * 0.75)

    def _leg(self, k: Ink, P, which, Hp, f, s, fly, behind):
        L = self.look
        if fly > 0.5:
            dg = P.get("dangle", 0.0)
            F = (Hp[0] - f * (16 + 36 * dg) + (8 if which == "n" else -8), Hp[1] + 92 - 10 * dg)
        else:
            F = (Hp[0] + P[f"foot_{which}_x"] * f * 0.7, P[f"foot_{which}_y"] * 0.7)
        ankle = (F[0], F[1] - 20)
        K, A = ik2(Hp, ankle, 44, 44, (f, 0.0))
        self._line(k, [Hp, K, A], dark(L.body, 0.72 if behind else 0.8), w=LIMB)
        # tênis chapado: cabedal + sola em faixa + 2 traços de cadarço
        cx, cy = A[0] + f * 10, A[1] + 6
        rotf = P[f"foot_{which}_rot"] * f + (0.35 * f if fly > 0.5 else 0.0)
        shoe = L.shoe if not behind else dark(L.shoe, 0.9)
        pts = [rot(p, rotf, (cx, cy)) for p in ((cx - 26, cy + 12), (cx - 24, cy - 8), (cx + 2, cy - 16), (cx + 30, cy - 4), (cx + 34, cy + 12))]
        pts = [(cx + (x - cx) * f, y) for x, y in pts]
        self._shape(k, pts, shoe)
        sole = [rot(p, rotf, (cx, cy)) for p in ((cx - 28, cy + 10), (cx + 36, cy + 10), (cx + 36, cy + 18), (cx - 28, cy + 18))]
        sole = [(cx + (x - cx) * f, y) for x, y in sole]
        self._shape(k, sole, L.sole, smooth=False)
        for j in (0, 1):
            x = cx + f * (2 + j * 10)
            self._line(k, [(x - 4, cy - 10 + j * 2), (x + 5, cy - 4 + j * 2)], "#FFFFFF", w=LINE * 0.7)

    # ------------------------------------------------------------------ cabeça
    def _head(self, k: Ink, P, C, v: View, ht):
        L = self.look
        f, s = v.f, v.side
        r = 112
        line = dark(L.body)
        for side in (-1, 1):                 # antenas = traço + bolinha
            b = rot((C[0] + side * 34 + f * s * 10, C[1] - r * 0.88), ht, C)
            sway = P.get("hair_bounce", 0.0) * 0.5 + P["head_tilt"] * 0.7
            tip = (b[0] + side * 30 + sway * 26, b[1] - 82)
            self._line(k, [b, (b[0] + side * 6, b[1] - 46), tip], line, w=LINE * 1.2)
            self._shape(k, ellipse_pts(tip[0], tip[1], 17, 17, 0, 16), L.pom)
        if L.curl and not v.back:            # topetinho em espiral (traço)
            base = rot((C[0] - 6 + f * s * 8, C[1] - r * 0.98), ht, C)
            pts = []
            for i in range(26):
                u = i / 25
                a = u * 3.4 * math.pi
                pts.append((base[0] + (4 + 13 * u) * math.cos(a), base[1] - 40 * u - (4 + 13 * u) * math.sin(a) * 0.45))
            self._line(k, pts, line, w=LINE * 1.3)
        self._shape(k, ellipse_pts(C[0], C[1], r, r * 0.94, ht, 32), L.body)
        if L.bow:
            self._bow(k, rot((C[0] - 52 * f + f * s * 30, C[1] - r * 0.8), ht, C))
        if v.back:
            return
        for side in (-1, 1):                 # bochechas chapadas, sem contorno
            x, c = v.sphere(C[0], r * 0.9, side * 0.72)
            if c > 0.25:
                q = rot((x, C[1] + 34), ht, C)
                k.shape(ellipse_pts(q[0], q[1], 22 * c, 20, 0, 16), fill=_rgba(L.cheek, 0.85 * P.get("blush", 1.0)), line=0)
        for side in (-1, 1):
            x, c = v.sphere(C[0], r * 0.78, side * 0.42)
            if c > 0.3:
                self._eye(k, P, rot((x, C[1] - 8), ht, C), c, side, f, s, line)
        nx_, _ = v.sphere(C[0], r * 0.72, 0.0)            # boca sempre dentro da cabeça, inclusive de perfil
        self._mouth(k, P, rot((nx_, C[1] + 52), ht, C), f, s, line)

    def _bow(self, k: Ink, B):
        L = self.look
        for wing in (-1, 1):
            self._shape(k, [(B[0], B[1]), (B[0] + wing * 44, B[1] - 26), (B[0] + wing * 50, B[1] + 12), (B[0] + wing * 30, B[1] + 22)], L.bow)
        self._shape(k, ellipse_pts(B[0], B[1], 13, 12, 0, 12), L.bow)
        pts = [(B[0] + math.cos(-math.pi / 2 + j * math.pi / 5) * (11 if j % 2 == 0 else 5),
                B[1] + math.sin(-math.pi / 2 + j * math.pi / 5) * (11 if j % 2 == 0 else 5)) for j in range(10)]
        k.shape(pts, fill=_rgba("#FFFFFF"), smooth=False, line=0)

    def _eye(self, k: Ink, P, E, c, side, f, s, line):
        """Olho da bíblia: elipse branca com contorno + pupila-ponto preta; cílios em 3 tracinhos; sobrancelha-traço."""
        L = self.look
        ex, ey = E
        es = P["eye_scale"]
        rx, ry = 22 * c * es, 27 * es
        if P.get("eyes_happy", 0) > 0.5:
            self._line(k, [(ex - rx, ey + 6), (ex, ey - ry * 0.5), (ex + rx, ey + 6)], PUPIL, w=LINE * 1.15)
        else:
            lid = P["lid"]
            self._shape(k, ellipse_pts(ex, ey, rx, ry, 0, 18), "#FFFFFF", line=line)
            if lid > 0.05:
                top = ey - ry + 2 * ry * lid
                pts = [(ex - rx - 2, ey - ry - 4), (ex + rx + 2, ey - ry - 4), (ex + rx + 2, top), (ex - rx - 2, top)]
                k.c.save()
                pth = skia.Path()
                pth.addOval(skia.Rect(ex - rx, ey - ry, ex + rx, ey + ry))
                k.c.clipPath(pth, doAntiAlias=True)
                k.shape(pts, fill=_rgba(L.body), smooth=False, line=0)
                k.c.restore()
                self._line(k, [(ex - rx, top), (ex + rx, top)], line, w=LINE)
            if lid < 0.8:
                lx = (P["look_x"] * f * 0.4 + 0.2 * f * s) * rx
                ly = P["look_y"] * 0.35 * ry
                pr = 7.5 * P["pupil"] ** 0.5 * es ** 0.3
                k.dot(ex + lx, ey + ly + 3, pr, PUPIL)
            if L.lashes:
                for j, a in enumerate((-2.2, -1.75, -1.3) if side < 0 else (-0.95, -1.4, -1.85)):
                    p0 = (ex + math.cos(a) * rx, ey + math.sin(a) * ry)
                    p1 = (ex + math.cos(a) * (rx + 13), ey + math.sin(a) * (ry + 13))
                    self._line(k, [p0, p1], PUPIL, w=LINE * 0.75)
        b = P["brow_l"] if side < 0 else P["brow_r"]
        if abs(b) > 0.15 or P["brow_y"] > 0.5 or L.extra.get("sobrancelha"):
            by = ey - ry - 14 - P["brow_y"] * 8
            inner = 1 if side < 0 else -1
            y_in, y_out = by + b * 10, by - b * 4
            xa, xb = ex - 16 * c, ex + 16 * c
            pts = [(xa, y_in if inner < 0 else y_out), (xb, y_in if inner > 0 else y_out)]
            self._line(k, pts, line if not L.extra.get("sobrancelha") else "#3A2A40", w=LINE * 1.1)

    def _mouth(self, k: Ink, P, M, f, s, line):
        """Boca de traço (fechada) ou forma escura com língua (aberta). 9 visemas + sorriso."""
        shapes = {"X": (1.0, 0), "A": (0.8, 0), "B": (1.0, 8), "C": (1.05, 18), "D": (1.15, 30), "E": (0.75, 22),
                  "F": (0.5, 10), "G": (0.95, 6), "H": (1.0, 20)}
        wk, op = shapes.get(P["mouth"], shapes["X"])
        op += P["jaw"] * 26
        sm = P["smile"]
        w = 26 * wk * (1 - 0.3 * s)
        cx, cy = M
        if op < 3:
            pts = [(cx - w, cy - sm * 8), (cx, cy + sm * 8), (cx + w, cy - sm * 8)]
            if s > 0.6:
                pts = pts[1:] if f > 0 else pts[:-1]
            self._line(k, pts, line, w=LINE * 1.15)
            return
        pts = [(cx - w, cy - sm * 6), (cx - w * 0.5, cy - 2), (cx + w * 0.5, cy - 2), (cx + w, cy - sm * 6),
               (cx + w * 0.6, cy + op * 0.8), (cx, cy + op), (cx - w * 0.6, cy + op * 0.8)]
        P_ = k.shape(pts, fill=_rgba("#5C1E2E"), line=0)
        pth = skia.Path()
        pth.addPoly([skia.Point(*p) for p in P_], True)
        k.c.save()
        k.c.clipPath(pth, doAntiAlias=True)
        k.shape(ellipse_pts(cx, cy + op * 0.95, w * 0.6, op * 0.42 + 4, 0, 12), fill=_rgba("#F27A8E"), line=0)
        k.c.restore()
        k.shape(P_, fill=None, brush=Brush(LINE, 0.0, _rgba(line), 0.0), dense=True, line=LINE)


def _poses():
    from .base import expression
    return [("andando", {"turn": 0.8, **expression("happy"), "foot_n_x": 50, "foot_f_x": -40, "foot_f_y": -20,
                         "hand_n_x": -70, "hand_f_x": 70}),
            ("acenando", {"turn": 0.15, **expression("happy"), "mouth": "C", "hand_f_x": 110, "hand_f_y": -90,
                          "paw_f": 3, "hand_f_bend": -0.5}),
            ("voando", {"turn": 0.35, **expression("joy"), "mouth": "D", "fly": 1, "wing_phase": 0.4,
                        "hand_n_x": -110, "hand_n_y": -40, "paw_n": 3, "hand_f_x": 110, "hand_f_y": -40, "paw_f": 3})]


FlatMuri.reference_poses = lambda self: _poses()

LAURINHA = FlatLook(body="#F7A8D8", belly_a="#FFE066", belly_b="#F27AB8", shoe="#F0509A", sole="#FFD23F",
                    pom="#F0509A", cheek="#FF7FBF", lashes=True, bow="#FFD23F")
LUISINHO = FlatLook(body="#7CC2F2", belly_a="#FFE066", belly_b="#3E7BD6", shoe="#3E7BD6", sole="#FFA53E",
                    pom="#3E7BD6", cheek="#FF9AAE", curl=True, extra={"sobrancelha": True})
