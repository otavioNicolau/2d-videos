"""Monstrinhos do canal "Bulu e Tetê" (2º canal, 20/11/2026) — estilo próprio do canal (canais/bulu_tete/BIBLIA_VISUAL.md):
- chapado SEM CONTORNO (formas de cor pura; separação por tons do mesmo corpo);
- CABEÇÃO (≈ 55 % da altura) e corpinho curto; braços e pernas grossinhos com mão de luva redonda e pé redondo;
- olho de bolinha preta com brilho branco (o Bulu tem UM olhão; a Tetê, dois olhinhos); boca simples escura com língua;
- cores saturadas; bochecha rosada suave.
Mesmo ESQUELETO DE POSES da turma (FlatMuri): todas as danças, ações, expressões e visemas funcionam igual.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..drawing.ink import Ink, ellipse_pts
from .base import View, lerp, rot
from .flat_muri import ARM_A, ARM_B, ARM_K, FlatMuri, _olho, _rgba, _rosto, dark
from .kit import ik2

ESCURO = "#2A1630"          # olho, boca fechada, sobrancelha (nunca preto puro de contorno: não há contorno)
BRILHO = "#FFFFFF"
LIMB_M = 26.0               # braço/perna grossinhos
R_CAB = 132.0               # raio da cabeça


@dataclass
class MonstroLook:
    body: str                  # corpo e cabeça
    belly: str                 # barriguinha (mancha clara)
    feet: str                  # pés
    cheek: str = "#FF8FB8"
    olhos: int = 2             # 1 = olhão (Bulu); 2 = olhinhos (Tetê)
    chifres: str = ""          # cor dos chifrinhos (Bulu)
    antenas: str = ""          # cor das bolinhas das antenas (Tetê)
    pelo: bool = False         # tufinhos de pelo no alto da cabeça (Bulu)
    presas: bool = False       # dois dentinhos de baixo (Bulu)
    dente: bool = False        # um dentinho de cima (Tetê)
    extra: dict = field(default_factory=dict)


class FlatMonstro(FlatMuri):
    flies = False

    def __init__(self, cid: str, name: str, look: MonstroLook):
        super().__init__(cid, name, look)          # mesmos canais de pose (ver FlatMuri.defaults)

    # sem contorno: só preenchimento
    def _shape(self, k: Ink, pts, fill: str, line: str | None = None, alpha: float = 1.0, w: float = 0.0, smooth=True):
        return k.shape(pts, fill=_rgba(fill, alpha), line=0, smooth=smooth)

    def _blob(self, k: Ink, x, y, rx, ry, cor, ang=0.0, alpha=1.0):
        return k.shape(ellipse_pts(x, y, rx, ry, ang, 28), fill=_rgba(cor, alpha), line=0)

    # ------------------------------------------------------------------ corpo
    def draw(self, ink: Ink, P: dict) -> None:
        L = self.look
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        sq = P["squash"]
        # perna curta: o agachar desce menos e o corpo inclina menos (senão o monstrinho senta no chão)
        hip = (P["body_x"] * f, -78 + P["body_y"] * 0.5)
        ang = max(-0.28, min(0.28, P["lean"])) * f

        def T(p):
            return rot((hip[0] + p[0] * sq ** -0.5, hip[1] + p[1] * sq), ang, hip)

        ink.shape(ellipse_pts(hip[0] * 0.3, -4, 92, 13, 0, 16), fill=(0, 0, 0, 0.13), line=0)     # sombra chapada
        C = T((f * s * 10 + P["head_dx"] * f, -192 + P["head_dy"]))
        hv = View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"])
        ht = ang * 0.5 + P["head_tilt"] * f

        self._arm(ink, P, "f", T((lerp(42 * f, 10 * f, s), -64)), f, behind=True)
        self._leg(ink, P, "f", T((lerp(22 * f, 8 * f, s), -4)), f, s, 0.0, behind=True)
        self._leg(ink, P, "n", T((lerp(-22 * f, -6 * f, s), -2)), f, s, 0.0, behind=False)
        # corpinho (gota arredondada) + barriguinha clara
        corpo = [T(p) for p in ((0, -86), (34, -82), (52, -54), (56, -18), (44, 8), (0, 16), (-44, 8), (-56, -18), (-52, -54), (-34, -82))]
        self._shape(ink, corpo, L.body)
        if not v.back:
            bx = T((f * s * 14, -30))
            self._blob(ink, bx[0], bx[1], 34 * (1 - 0.35 * s), 36, L.belly, ang)
        self._head(ink, P, C, hv, ht)
        self._arm(ink, P, "n", T((lerp(-42 * f, -8 * f, s), -64)), f, behind=False)

    def _arm(self, k: Ink, P, which, S, f, behind):
        T_ = (S[0] + P[f"hand_{which}_x"] * f * ARM_K, S[1] + P[f"hand_{which}_y"] * ARM_K)
        bend = P[f"hand_{which}_bend"]
        E, H = ik2(S, T_, ARM_A, ARM_B, (-f if bend >= 0 else f, 0.4))
        col = dark(self.look.body, 0.8 if behind else 0.9)
        self._line(k, [S, E, H], col, w=LIMB_M)
        item = P.get("holding", "") if which == "n" else P.get("holding_f", "")
        if item:
            from .flat_props import draw_item
            a0 = math.atan2(H[1] - E[1], H[0] - E[0])
            draw_item(k, item, (H[0] + math.cos(a0) * 8, H[1] + math.sin(a0) * 8), f, a0)
        aberta = P[f"paw_{which}"] >= 2.5
        self._blob(k, H[0], H[1], 19 if aberta else 16, 19 if aberta else 16, col)          # mão de luva redonda
        if aberta:                                                                            # polegarzinho
            a0 = math.atan2(H[1] - E[1], H[0] - E[0])
            q = (H[0] + math.cos(a0 - 1.2) * 16, H[1] + math.sin(a0 - 1.2) * 16)
            self._blob(k, q[0], q[1], 8, 8, col)

    def _leg(self, k: Ink, P, which, Hp, f, s, fly, behind):
        L = self.look
        F = (Hp[0] + P[f"foot_{which}_x"] * f * 0.7, P[f"foot_{which}_y"] * 0.7)
        ankle = (F[0], F[1] - 16)
        K, A = ik2(Hp, ankle, 36, 34, (f, 0.0))
        self._line(k, [Hp, K, A], dark(L.body, 0.8 if behind else 0.9), w=LIMB_M)
        cx, cy = A[0] + f * 8, A[1] + 6
        rotf = P[f"foot_{which}_rot"] * f
        pe = L.feet if not behind else dark(L.feet, 0.88)
        pts = [rot((cx + x * f, cy + y), rotf, (cx, cy)) for x, y in
               ((-24, 8), (-26, -4), (-12, -14), (14, -14), (32, -4), (34, 8), (20, 12), (-16, 12))]
        self._shape(k, pts, pe)
        if L.extra.get("tenis"):                               # 5–8 anos: tênis com sola branca e faixa
            sola = [rot((cx + x * f, cy + y), rotf, (cx, cy)) for x, y in ((-26, 5), (34, 5), (34, 12), (-26, 12))]
            self._shape(k, sola, "#FFFFFF", smooth=False)
            fx_ = [rot((cx + x * f, cy + y), rotf, (cx, cy)) for x, y in ((-4, -12), (6, -12), (14, 3), (4, 3))]
            self._shape(k, fx_, L.extra["tenis"], smooth=False)

    # ------------------------------------------------------------------ cabeça
    def _head(self, k: Ink, P, C, v: View, ht):
        L = self.look
        f, s = v.f, v.side
        r = R_CAB
        if L.chifres:                                        # chifrinhos atrás do alto da cabeça
            for side in (-1, 1):
                b = rot((C[0] + side * r * 0.5 + f * s * 12, C[1] - r * 0.78), ht, C)
                pts = [(b[0] + side * x, b[1] + y) for x, y in ((-22, 10), (8, -62), (28, -74), (24, 8))]      # espelhado
                self._shape(k, pts, L.chifres)
        if L.antenas:                                        # anteninhas com bolinha
            for side in (-1, 1):
                b = rot((C[0] + side * 30 + f * s * 10, C[1] - r * 0.9), ht, C)
                sway = P.get("hair_bounce", 0.0) * 0.5 + P["head_tilt"] * 0.7
                tip = (b[0] + side * 26 + sway * 24, b[1] - 86)
                self._line(k, [b, (b[0] + side * 4, b[1] - 46), tip], dark(L.body, 0.8), w=11)
                self._blob(k, tip[0], tip[1], 20, 20, L.antenas)
        self._shape(k, ellipse_pts(C[0], C[1], r, r * 0.95, ht, 40), L.body)
        if L.pelo:                                           # tufinhos de pelo no alto (mesma cor: silhueta)
            esp = 1.35 if L.extra.get("espetado") else 1.0      # 5–8 anos: pelo mais espetado
            for j, dx in enumerate((-0.42, -0.14, 0.14, 0.42)):
                b = rot((C[0] + dx * r + f * s * 10, C[1] - r * 0.86 + abs(dx) * 22), ht, C)
                h = (46 if j in (1, 2) else 36) * esp
                self._shape(k, [(b[0] - 24, b[1] + 14), (b[0] - 4 + (8 if dx > 0 else -8), b[1] - h), (b[0] + 24, b[1] + 14)], L.body, smooth=False)
        if v.back:
            return
        for side in (-1, 1):                                 # bochechas suaves
            x, c = v.sphere(C[0], r * 0.86, side * 0.78)
            if c > 0.25:
                q = rot((x, C[1] + 50), ht, C)
                k.shape(ellipse_pts(q[0], q[1], 22 * c, 15, 0, 16), fill=_rgba(L.cheek, 0.8 + 0.2 * P.get("blush", 1.0)), line=0)
        if L.olhos == 1:                                     # Bulu: UM olhão no meio
            sh = _rosto(v)[1]
            x = C[0] + r * 0.74 * math.sin(max(-0.9, min(0.9, sh)))
            self._eye(k, P, rot((x, C[1] - 4), ht, C), 0.8 + 0.2 * math.cos(sh), 0, f, s, ESCURO)
        else:
            for side in (-1, 1):
                e = _olho(v, C[0], r, side)
                if e:
                    self._eye(k, P, rot((e[0], C[1] + 8), ht, C), e[1], side, f, s, ESCURO)       # olhos abaixo do meio (referência)
        a_m = max(-1.0, min(1.0, _rosto(v)[1]))
        nx_ = C[0] + r * 0.7 * math.sin(a_m)
        self._mouth(k, P, rot((nx_, C[1] + 66), ht, C), f, s, ESCURO)

    def _eye(self, k: Ink, P, E, c, side, f, s, line):
        ex, ey = E
        big = self.look.olhos == 1
        R = (40 if big else 19) * P["eye_scale"]
        rx = R * c
        if P.get("careta", 0) > 0.5:                     # "> <" (no olhão: "x" espremido)
            pt = -side if side else 1
            if big:
                for sgn in (-1, 1):
                    self._line(k, [(ex - sgn * R, ey - R * 0.5), (ex, ey), (ex - sgn * R, ey + R * 0.5)], ESCURO, w=9)
            else:
                self._line(k, [(ex - pt * rx, ey - R * 0.6), (ex + pt * rx * 0.7, ey + 1), (ex - pt * rx, ey + R * 0.6)], ESCURO, w=8)
        elif P.get("eyes_happy", 0) > 0.5:
            self._line(k, [(ex - rx, ey + 6), (ex, ey - R * 0.55), (ex + rx, ey + 6)], ESCURO, w=9 if big else 8)
        elif P["lid"] >= 0.85:
            self._line(k, [(ex - rx, ey + 2), (ex, ey + R * 0.4), (ex + rx, ey + 2)], ESCURO, w=9 if big else 8)
        else:
            lx = (P["look_x"] * f * 0.35 + 0.15 * f * s) * rx
            ly = P["look_y"] * 0.3 * R
            ry = R * (1.0 - 0.75 * max(0.0, P["lid"]))
            self._blob(k, ex + lx, ey + ly + (R - ry) * 0.5, rx, ry, ESCURO)
            if ry > R * 0.4:                                   # brilho branco (duas bolinhas)
                self._blob(k, ex + lx - rx * 0.32, ey + ly - R * 0.32, R * 0.32, R * 0.32, BRILHO)
                self._blob(k, ex + lx + rx * 0.3, ey + ly + R * 0.28, R * 0.13, R * 0.13, BRILHO)
        b = P["brow_l"] if side <= 0 else P["brow_r"]
        if self.look.extra.get("sobrancelha") and not P.get("careta", 0) > 0.5:   # 5–8 anos: sobrancelha SEMPRE (atitude)
            by = ey - R - (26 if big else 22) - P["brow_y"] * 8
            wb = 28 if big else 15
            arco = 6 + max(0.0, P["brow_y"]) * 5                # arquinho (alegre); o "b" inclina (bravo/triste)
            def arco_pts(xa, ya, xb, yb, h):                   # arco suave (curva de 2º grau amostrada)
                return [(xa + (xb - xa) * u, ya + (yb - ya) * u - h * 4 * u * (1 - u)) for u in (i / 8 for i in range(9))]
            if big:                                            # Bulu: uma sobrancelha só, grossa
                self._line(k, arco_pts(ex - wb, by + 3 - b * 4, ex + wb, by + 3 - b * 4, arco - b * 18), ESCURO, w=10)   # bravo: "V"
            else:
                inner = 1 if side < 0 else -1                  # ponta de dentro (perto do nariz)
                xi, xo = ex + inner * wb, ex - inner * wb
                self._line(k, arco_pts(xo, by + 2 - b * 3, xi, by + 2 + b * 9, (arco - abs(b) * 5) * 0.6), ESCURO, w=7)
        elif abs(b) > 0.3:                                       # sobrancelha só quando expressiva (bravo / triste)
            by = ey - R - 16 - P["brow_y"] * 6
            inner = 1 if side <= 0 else -1
            self._line(k, [(ex - 16, by + (b * 9 if inner < 0 else -b * 4)), (ex + 16, by + (b * 9 if inner > 0 else -b * 4))], ESCURO, w=7)

    def _mouth(self, k: Ink, P, M, f, s, line):
        L = self.look
        cx, cy = M
        if P.get("careta", 0) > 0.5:
            w = 30
            self._line(k, [(cx - w + 2 * w * i / 6, cy + (7 if i % 2 else -7) + (i - 3) * 2.5) for i in range(7)], ESCURO, w=8)
            return
        o = max(0.0, min(1.0, P.get("boca_o", 0.0)))
        shapes = {"X": (1.0, 0), "A": (0.8, 0), "B": (1.0, 8), "C": (1.05, 18), "D": (1.15, 30), "E": (0.75, 22),
                  "F": (0.5, 10), "G": (0.95, 6), "H": (1.0, 20)}
        wk, op = shapes.get(P["mouth"], shapes["X"])
        op += P["jaw"] * 26
        if o > 0.04:
            wk, op = 0.6, 20 + 30 * o
        sm = P["smile"]
        w = 30 * wk * (1 - 0.3 * s)
        if op < 3:                                             # fechada: sorriso grossinho
            pts = [(cx - w, cy - sm * 9), (cx, cy + sm * 9), (cx + w, cy - sm * 9)]
            self._line(k, pts, ESCURO, w=9)
            if L.presas and sm > 0.2:
                for side in (-1, 1):
                    x = cx + side * w * 0.45
                    self._shape(k, [(x - 6, cy - sm * 2), (x + 6, cy - sm * 2), (x, cy - sm * 2 - 13)], BRILHO, smooth=False)
            return
        pts = [(cx - w, cy - sm * 6), (cx - w * 0.5, cy - 2), (cx + w * 0.5, cy - 2), (cx + w, cy - sm * 6),
               (cx + w * 0.6, cy + op * 0.8), (cx, cy + op), (cx - w * 0.6, cy + op * 0.8)]
        self._shape(k, pts, "#7A1E3A")
        self._blob(k, cx, cy + op * 0.78, w * 0.55, op * 0.3 + 3, "#FF7A9A")              # língua
        if L.dente:                                            # Tetê: um dentinho em cima
            self._shape(k, [(cx - 8, cy - 2), (cx + 8, cy - 2), (cx + 7, cy + 11), (cx - 7, cy + 11)], BRILHO, smooth=False)
        if L.presas:                                           # Bulu: presinhas em baixo
            for side in (-1, 1):
                x = cx + side * w * 0.42
                yb = cy + op * 0.86
                self._shape(k, [(x - 6, yb), (x + 6, yb), (x, yb - 12)], BRILHO, smooth=False)


BULU = MonstroLook(body="#3DA5F4", belly="#9AD8FF", feet="#1C6CB8", olhos=1, chifres="#FFC93C", pelo=True, presas=True,
                   cheek="#FF9CC2")
TETE = MonstroLook(body="#B27BFF", belly="#E6CCFF", feet="#7A43D6", olhos=2, antenas="#FF6FB5", dente=True, cheek="#FF8FC8")
# versão "5 a 8 anos" (20/11): sobrancelha sempre, tênis com sola e faixa, pelo espetado, bochecha mais discreta
BULU_58 = MonstroLook(body="#2F9BF0", belly="#9AD8FF", feet="#E9433F", olhos=1, chifres="#FFC93C", pelo=True, presas=True,
                      cheek="#FF8FB3", extra={"sobrancelha": True, "tenis": "#FFD23F", "espetado": True})
TETE_58 = MonstroLook(body="#A66BFF", belly="#E6CCFF", feet="#19B7A6", olhos=2, antenas="#FF4FA3", dente=True, cheek="#FF9AD0",
                      extra={"sobrancelha": True, "tenis": "#FFFFFF"})
