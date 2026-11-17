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
ARM_A, ARM_B, ARM_K = 56, 52, 0.82   # braço e antebraço; escala dos alvos das mãos
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



# ── olhos e boca no giro da cabeça (BIBLIA_VISUAL §4: desenho chapado, olhos sempre redondinhos) ──
OLHO_MAX = 0.9       # ângulo máximo (rad) do centro do olho: nunca encosta na borda da cabeça
PERFIL = 0.7         # giro a partir do qual o rosto está de perfil (só então o olho de trás some)
DESLOCA_MAX = 0.52   # quanto o rosto (olhos e boca) anda para o lado do giro antes do perfil
BOCA_MAX = 1.0


def _rosto(v) -> tuple[float, float, float]:
    """(sentido, deslocamento do rosto, abertura entre os olhos) para o giro da cabeça."""
    t = max(-1.0, min(1.0, v.turn))
    f = 1.0 if t >= 0 else -1.0
    s = abs(t)
    if s <= PERFIL:
        return f, f * min(s * (math.pi / 2) * 0.92, DESLOCA_MAX), 0.42 - 0.04 * s / PERFIL
    u = (s - PERFIL) / (1 - PERFIL)
    return f, f * (DESLOCA_MAX + (BOCA_MAX - DESLOCA_MAX) * u), 0.38


def _olho(v, cx: float, r: float, side: int):
    """(x, largura) do olho `side` com a cabeça girada, ou None se ele fica escondido.
    1ª versão: o olho seguia a esfera à risca (olho de trás espremido no contorno). 2ª (17/11 cedo): o de trás sumia a
    partir do giro 0,37 — rosto quase de frente com um olho só. Agora o rosto inteiro anda para o lado do giro, os
    dois olhos ficam visíveis e redondinhos até o perfil (giro 0,7) e só então o de trás some."""
    f, shift, spread = _rosto(v)
    s = abs(max(-1.0, min(1.0, v.turn)))
    if s <= PERFIL:
        a = side * spread + shift
    else:
        if side * f > 0:                                   # de perfil: só o olho da frente
            return None
        u = (s - PERFIL) / (1 - PERFIL)
        a = f * ((DESLOCA_MAX - spread) + (0.75 - (DESLOCA_MAX - spread)) * u)
    a = max(-OLHO_MAX, min(OLHO_MAX, a))
    return cx + r * 0.78 * math.sin(a), 0.75 + 0.25 * math.cos(a)


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
                "fly": 0.0, "rot_pivot": 0.55, "bigode": 0.0, "mochila": 0.0, "buzz": 0.0, "suor": 0.0,
                "despenteado": 0.0, "bafinho": 0.0, "espuma": 0.0, "brilho": 0.0, "cuspe": 0.0,
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
        if L.extra.get("asas", True):
            for side in (-1, 1):
                self._wing(ink, P, T((side * 10 * (1 - s) - f * 10 * s, -66)), f, fly, far=(side == f), side=side, s=s)
        if P.get("mochila", 0) > 0.5:          # mochila nas costas (atrás do tórax; aparece pelas bordas)
            self._mochila(ink, T, f, s)
        self._abdomen(ink, T, f)
        if L.extra.get("patas_meio"):        # formiga: o par do meio (6 patinhas)
            for side in (-1, 1):
                a0 = T((side * 34, -22))
                k1 = T((side * 92, -8))
                k2 = T((side * 112, 34))
                col = dark(L.body, 0.75)
                self._line(ink, [a0, k1, k2], col, w=LIMB * 0.9)
                self._line(ink, [k2, (k2[0] + side * 12, k2[1] + 4)], col, w=LIMB * 0.9)   # pezinho
        self._arm(ink, P, "f", T((lerp(38 * f, 8 * f, s), -62)), f, behind=True)
        self._leg(ink, P, "f", T((lerp(16 * f, 6 * f, s), -2)), f, s, fly, behind=True)
        self._leg(ink, P, "n", T((lerp(-16 * f, -4 * f, s), 0)), f, s, fly, behind=False)
        # tórax (gota) — mesma cor do corpo
        self._shape(ink, [T(p) for p in ((0, -80), (30, -74), (44, -44), (44, -10), (26, 10), (0, 14), (-26, 10), (-44, -10), (-44, -44), (-30, -74))], L.body)
        if L.extra.get("pintas"):             # casco de joaninha: risca do meio + pintinhas
            self._line(ink, [T((0, -78)), T((0, 12))], dark(L.body, 0.6), w=LINE)
            for dx, dy, r in ((-24, -52, 9), (22, -46, 10), (-28, -12, 8), (26, -10, 9)):
                q = T((dx, dy))
                ink.shape(ellipse_pts(q[0], q[1], r, r, 0, 12), fill=_rgba(L.extra["pintas"]), line=0)
        if P.get("mochila", 0) > 0.5:          # alças por cima dos ombros
            for side in (-1, 1):
                self._line(ink, [T((side * 26 - f * s * 10, -76)), T((side * 30, -20))], "#3E7BD6" if not L.bow else "#F0509A", w=LINE * 1.6)
        if L.extra.get("colar"):               # colar de bolinhas (mamãe)
            for j in range(7):
                a = math.pi * (0.15 + 0.7 * j / 6)
                q = T((math.cos(a) * 30, -76 + math.sin(a) * 16))
                ink.dot(q[0], q[1], 6.5, _rgba(L.extra["colar"]))
        self._head(ink, P, C, hv, ht)
        self._arm(ink, P, "n", T((lerp(-38 * f, -6 * f, s), -62)), f, behind=False)

    def _mochila(self, k: Ink, T, f, s):
        cor = "#3E7BD6" if not self.look.bow else "#F0509A"
        pts = [T(p) for p in ((-f * 30 - 58, -96), (-f * 30 + 58, -96), (-f * 30 + 62, -6), (-f * 30 - 62, -6))]
        self._shape(k, pts, cor, smooth=False)
        a, b = T((-f * 30 - 40, -46)), T((-f * 30 + 40, -46))
        self._line(k, [a, b], "#FFFFFF", w=LINE * 1.2)

    def _abdomen(self, k: Ink, T, f):
        """Barriguinha listrada atrás (gota inclinada para trás/baixo), listras chapadas recortadas."""
        L = self.look
        pts = [T(p) for p in ((-f * 8, -50), (-f * 56, -64), (-f * 106, -48), (-f * 130, -16), (-f * 114, 14), (-f * 66, 18), (-f * 16, 2))]
        P_ = k.shape(pts, fill=_rgba(L.belly_a), line=0)
        if L.extra.get("abdomen_liso"):
            if L.extra.get("pintas"):
                for j, (dx, dy) in enumerate(((-60, -30), (-96, -10), (-70, 4))):
                    q = T((f * dx, dy))
                    k.shape(ellipse_pts(q[0], q[1], 9, 9, 0, 12), fill=_rgba(L.extra["pintas"]), line=0)
            k.shape(P_, fill=None, brush=Brush(LINE, 0.0, _rgba(dark(L.belly_a)), 0.0), dense=True, line=LINE)
            return
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
        if fly > 0.5 or P.get("buzz", 0.0) > 0.5:       # voando ou "batendo as asinhas" no chão
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
        # braços ~30% mais longos que no 1º modelo: os gestos precisam passar da cabeça grande (análise da referência)
        T_ = (S[0] + P[f"hand_{which}_x"] * f * ARM_K, S[1] + P[f"hand_{which}_y"] * ARM_K)
        bend = P[f"hand_{which}_bend"]
        E, H = ik2(S, T_, ARM_A, ARM_B, (-f if bend >= 0 else f, 0.4))
        col = dark(self.look.body, 0.72 if behind else 0.8)
        self._line(k, [S, E, H], col, w=LIMB)
        d = (H[0] - E[0], H[1] - E[1])
        a0 = math.atan2(d[1], d[0])
        spread = (-0.7, 0.0, 0.7) if P[f"paw_{which}"] >= 2.5 else (-0.35, 0.0, 0.35)
        ln = 15 if P[f"paw_{which}"] >= 2.5 else 10
        item = P.get("holding", "") if which == "n" else ""
        if item:                              # objeto na mão (desenhado sob os dedos)
            from .flat_props import draw_item
            draw_item(k, item, (H[0] + math.cos(a0) * 8, H[1] + math.sin(a0) * 8), f)
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
            if L.extra.get("antena_cotovelo"):  # formiga: antena dobrada em "cotovelo"
                mid = (b[0] + side * 8, b[1] - 54)
                tip = (b[0] + side * 44 + sway * 20, b[1] - 66)
                self._line(k, [b, mid, tip], line, w=LINE * 1.2)
            elif P.get("despenteado", 0) > 0.5:   # acordou despenteado: antena em zigue-zague, ponta caída
                tip = (b[0] + side * (44 if side > 0 else 12) + sway * 26, b[1] - (58 if side > 0 else 86))
                self._line(k, [b, (b[0] + side * 22, b[1] - 26), (b[0] - side * 6, b[1] - 50), tip], line, w=LINE * 1.2)
            else:
                self._line(k, [b, (b[0] + side * 6, b[1] - 46), tip], line, w=LINE * 1.2)
            self._shape(k, ellipse_pts(tip[0], tip[1], 17, 17, 0, 16), L.pom)
        if P.get("despenteado", 0) > 0.5 and not v.back:   # tufinhos arrepiados no topo
            for j, (dx, ang) in enumerate(((-22, -2.0), (0, -1.55), (22, -1.1))):
                q = rot((C[0] + dx + f * s * 8, C[1] - r * 0.9), ht, C)
                ln_ = 34 if j == 1 else 28
                self._line(k, [q, (q[0] + math.cos(ang) * ln_ * 0.55 + 6, q[1] + math.sin(ang) * ln_ * 0.55),
                               (q[0] + math.cos(ang) * ln_, q[1] + math.sin(ang) * ln_)], line, w=LINE * 1.2)
        elif L.curl and not v.back:            # topetinho em espiral (traço)
            base = rot((C[0] - 6 + f * s * 8, C[1] - r * 0.98), ht, C)
            pts = []
            for i in range(26):
                u = i / 25
                a = u * 3.4 * math.pi
                pts.append((base[0] + (4 + 13 * u) * math.cos(a), base[1] - 40 * u - (4 + 13 * u) * math.sin(a) * 0.45))
            self._line(k, pts, line, w=LINE * 1.3)
        if L.extra.get("coque"):             # coque da vovó (atrás do topo da cabeça)
            q = rot((C[0] + f * s * 10, C[1] - r * 0.98), ht, C)
            self._shape(k, ellipse_pts(q[0], q[1], 46, 40, 0, 24), L.extra["coque"])
            self._line(k, [(q[0] - 30, q[1] + 18), (q[0] + 30, q[1] + 18)], dark(L.extra["coque"]), w=LINE)
        self._shape(k, ellipse_pts(C[0], C[1], r, r * 0.94, ht, 32), L.body)
        if L.extra.get("cabelo"):            # franjinha grisalha (vovó)
            for j in range(5):
                q = rot((C[0] - 60 + j * 30 + f * s * 10, C[1] - r * 0.82), ht, C)
                self._shape(k, ellipse_pts(q[0], q[1], 22, 16, 0, 14), L.extra["cabelo"])
        if L.bow:
            self._bow(k, rot((C[0] - 52 * f + f * s * 30, C[1] - r * 0.8), ht, C))
        if P.get("folha_cabeca", 0) > 0.5:   # folha carregada na cabeça (Dança da Formiguinha)
            base = rot((C[0], C[1] - r * 0.95), ht, C)
            pts = [(base[0] - 150, base[1] - 10), (base[0] - 60, base[1] - 120), (base[0] + 90, base[1] - 150),
                   (base[0] + 170, base[1] - 60), (base[0] + 120, base[1] + 10), (base[0], base[1] + 18)]
            self._shape(k, pts, "#4CC35E")
            self._line(k, [(base[0] - 130, base[1] - 4), (base[0] + 150, base[1] - 70)], "#2E8B3E", w=LINE * 1.1)
            for u in (0.3, 0.55, 0.8):
                mx, my = base[0] - 130 + 280 * u, base[1] - 4 - 66 * u
                self._line(k, [(mx, my), (mx - 20, my - 50)], "#2E8B3E", w=LINE * 0.8)
                self._line(k, [(mx, my), (mx + 30, my + 22)], "#2E8B3E", w=LINE * 0.8)
        if P.get("chapeu", 0) > 0.5:         # chapéu de sol (Passeio na Lagoa): aba larga + copa + fita
            cor_c = "#F5D67A"
            aba = [rot((C[0] + dx * r, C[1] - r * 0.62 + dy * r), ht, C) for dx, dy in
                   ((-1.45, 0.06), (-1.1, -0.12), (0.0, -0.2), (1.1, -0.12), (1.45, 0.06), (1.0, 0.12), (0.0, 0.08), (-1.0, 0.12))]
            self._shape(k, aba, cor_c)
            copa = [rot((C[0] + dx * r, C[1] - r * 0.62 + dy * r), ht, C) for dx, dy in
                    ((-0.72, -0.08), (-0.6, -0.62), (0.0, -0.78), (0.6, -0.62), (0.72, -0.08))]
            self._shape(k, copa, cor_c)
            fita = [rot((C[0] + dx * r, C[1] - r * 0.62 + dy * r), ht, C) for dx, dy in
                    ((-0.71, -0.12), (0.71, -0.12), (0.68, -0.3), (-0.68, -0.3))]
            self._shape(k, fita, "#E9545D" if L.bow else "#3C8BF0", smooth=False)
        if P.get("touca", 0) > 0.5:          # touca de pijama (Conta Comigo: "Pijama!") com pompom caído
            base_l, base_r = rot((C[0] - r * 0.86, C[1] - r * 0.42), ht, C), rot((C[0] + r * 0.86, C[1] - r * 0.42), ht, C)
            ponta = rot((C[0] + f * r * 1.15, C[1] - r * 1.05), ht, C)
            topo = rot((C[0] + f * r * 0.1, C[1] - r * 1.25), ht, C)
            cor_t = "#7FA8FF" if not L.bow else "#B98CFF"
            self._shape(k, [base_l, topo, ponta, base_r], cor_t)
            self._shape(k, [(base_l[0], base_l[1] - 4), (base_r[0], base_r[1] - 4), (base_r[0], base_r[1] + 22),
                            (base_l[0], base_l[1] + 22)], "#FFFFFF", smooth=False)
            self._shape(k, ellipse_pts(ponta[0], ponta[1], 22, 22, 0, 14), "#FFFFFF")
        if L.extra.get("flor"):              # florzinha no lugar do laço (mamãe)
            q = rot((C[0] - 56 * f + f * s * 30, C[1] - r * 0.78), ht, C)
            for j in range(5):
                a = j * 2 * math.pi / 5
                self._shape(k, ellipse_pts(q[0] + math.cos(a) * 17, q[1] + math.sin(a) * 17, 14, 14, 0, 12), L.extra["flor"])
            self._shape(k, ellipse_pts(q[0], q[1], 10, 10, 0, 12), "#FFE066")
        if v.back:
            return
        for side in (-1, 1):                 # bochechas chapadas, sem contorno
            x, c = v.sphere(C[0], r * 0.9, side * 0.72)
            if c > 0.25:
                q = rot((x, C[1] + 34), ht, C)
                k.shape(ellipse_pts(q[0], q[1], 22 * c, 20, 0, 16), fill=_rgba(L.cheek, 0.85 * P.get("blush", 1.0)), line=0)
        for side in (-1, 1):
            e = _olho(v, C[0], r, side)
            if e:
                self._eye(k, P, rot((e[0], C[1] - 8), ht, C), e[1], side, f, s, line)
        if L.extra.get("oculos"):            # óculos redondos (vovó)
            eyes = []
            for side in (-1, 1):
                e = _olho(v, C[0], r, side)
                if e:
                    x, c = e
                    q = rot((x, C[1] - 8), ht, C)
                    eyes.append(q)
                    k.shape(ellipse_pts(q[0], q[1], 34 * c, 34, 0, 20), fill=None,
                            brush=Brush(LINE * 0.9, 0.0, _rgba("#534946"), 0.0), dense=True, line=LINE * 0.9)
            if len(eyes) == 2:
                self._line(k, [(eyes[0][0] + 30, eyes[0][1] - 4), (eyes[1][0] - 30, eyes[1][1] - 4)], "#534946", w=LINE * 0.9)
        a_m = max(-BOCA_MAX, min(BOCA_MAX, _rosto(v)[1]))          # boca anda junto com os olhos
        nx_ = C[0] + r * 0.72 * math.sin(a_m)              # boca sempre dentro da cabeça, inclusive de perfil
        self._mouth(k, P, rot((nx_, C[1] + 52), ht, C), f, s, line)
        self._boca_fx(k, P, rot((nx_, C[1] + 52), ht, C), f)
        if P.get("protetor", 0) > 0.05:       # protetor solar: risquinhos brancos nas bochechas e no nariz
            a_ = min(1.0, P["protetor"])
            for side in (-1, 1):
                x, c = v.sphere(C[0], r * 0.9, side * 0.72)
                if c > 0.25:
                    q_ = rot((x, C[1] + 30), ht, C)
                    for j in (-1, 1):
                        k.shape(ellipse_pts(q_[0] + j * 10 * c, q_[1] + j * 4, 13 * c, 5, 0.3, 12), fill=_rgba("#FFFFFF", 0.95 * a_), line=0)
        if P.get("tinta", 0) > 0.05:          # sujo de tinta (Cadê a Cor?: "misturei tudo… marrom!")
            self._tinta(k, P["tinta"], C, r, ht)
        if P.get("suor", 0) > 0.5:            # gotinhas de suor (chegou correndo)
            for dx, dy, sc in ((r * 0.95, -r * 0.55, 1.0), (r * 1.12, -r * 0.2, 0.75)):
                q = rot((C[0] + dx * f, C[1] + dy), ht, C)
                pts = [(q[0], q[1] - 18 * sc), (q[0] + 10 * sc, q[1]), (q[0], q[1] + 10 * sc), (q[0] - 10 * sc, q[1])]
                self._shape(k, pts, "#9CCBFA", line="#5A8FD6")
        if P.get("bigode", 0) > 0.5:          # bigodinho de leite
            m = rot((nx_, C[1] + 40), ht, C)
            pts = [(m[0] - 34, m[1] + 4), (m[0] - 20, m[1] - 8), (m[0], m[1] - 4), (m[0] + 20, m[1] - 8), (m[0] + 34, m[1] + 4),
                   (m[0] + 18, m[1] + 10), (m[0], m[1] + 6), (m[0] - 18, m[1] + 10)]
            self._shape(k, pts, "#FFFFFF", line="#C9D6E0")

    def _tinta(self, k: Ink, t: float, C, r: float, ht: float):
        """Manchas de tinta na cabeça (topo, lateral e queixo; nunca em cima dos olhos). t 0→1 = quanto sujou."""
        for j, (dx, dy, R, cor) in enumerate(((-0.45, -0.72, 34, "#8A5A36"), (0.5, -0.62, 26, "#8A5A36"),
                                              (0.86, 0.1, 22, "#2DBE5A"), (-0.82, 0.25, 24, "#8E44EF"),
                                              (-0.05, -0.9, 18, "#FF8A1F"))):
            if t <= j * 0.14:
                continue
            q = rot((C[0] + dx * r, C[1] + dy * r), ht, C)
            sc = min(1.0, (t - j * 0.14) / 0.3)
            pts = [(q[0] + math.cos(a) * R * sc * (1 + 0.28 * math.sin(5 * a + j)),
                    q[1] + math.sin(a) * R * sc * (1 + 0.28 * math.sin(5 * a + j))) for a in (i * 2 * math.pi / 21 for i in range(21))]
            k.shape(pts, fill=_rgba(cor), line=0)

    def _boca_fx(self, k: Ink, P, M, f):
        """Efeitos da escovação em volta da boca: espuma, bafinho (nuvenzinha verde), brilho 'tim-tim' e cuspe."""
        mx, my = M
        e = P.get("espuma", 0.0)
        if e > 0.05:                          # espuminha branca nos cantos da boca
            for j, (dx, dy, r) in enumerate(((-30, 4, 11), (-18, 14, 9), (24, 6, 12), (34, -6, 8), (6, 18, 10), (-40, -6, 7))):
                if e > j * 0.12:
                    self._shape(k, ellipse_pts(mx + dx, my + dy, r, r, 0, 12), "#FFFFFF", line="#B9D7EE", w=LINE * 0.7)
        b = P.get("bafinho", 0.0)
        if 0.02 < b < 0.98:                   # nuvenzinha verde que sai da boca, cresce e some
            a = 0.85 * min(1.0, (1 - b) * 3.0)
            cx, cy = mx + f * (50 + 120 * b), my - 10 - 70 * b
            sc = 0.6 + 0.8 * b
            for dx, dy, r in ((-26, 6, 24), (0, -10, 30), (26, 4, 24), (8, 14, 20)):
                k.shape(ellipse_pts(cx + dx * sc, cy + dy * sc, r * sc, r * sc, 0, 16), fill=_rgba("#A8E07A", a),
                        brush=Brush(LINE * 0.7, 0.0, _rgba("#6FB33F", a), 0.0), line=LINE * 0.7)
            for j in (-1, 0, 1):              # risquinhos de "cheirinho"
                x0 = cx + j * 24 * sc
                self._line(k, [(x0, cy - 40 * sc), (x0 + 6, cy - 52 * sc), (x0 - 4, cy - 64 * sc)], "#6FB33F", w=LINE * 0.8,
                           alpha=a)
        g = P.get("brilho", 0.0)
        if g > 0.05:                          # brilho "tim-tim" no sorriso: estrela de 4 pontas
            cx, cy, R = mx + f * 30, my - 6, 34 * g
            pts = []
            for j in range(8):
                ang = -math.pi / 2 + j * math.pi / 4
                rr = R if j % 2 == 0 else R * 0.28
                pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
            self._shape(k, pts, "#FFFFFF", line="#FFC21A", smooth=False)
        c = P.get("cuspe", 0.0)
        if 0.02 < c < 0.98:                   # cuspe de espuma indo para a pia
            for j, (dx, dy, r) in enumerate(((40, 30, 10), (60, 50, 8), (30, 60, 7))):
                q = (mx + f * (dx + 90 * c), my + dy + 140 * c * c)
                self._shape(k, ellipse_pts(q[0], q[1], r, r, 0, 12), "#FFFFFF", line="#B9D7EE", w=LINE * 0.7)

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
        elif P["lid"] >= 0.85:                 # olho FECHADO (piscada, dormindo): curvinha para baixo, sem fresta branca
            self._line(k, [(ex - rx, ey + 4), (ex, ey + ry * 0.42), (ex + rx, ey + 4)], PUPIL, w=LINE * 1.15)
            if L.lashes:                        # cílios caídos no canto de fora
                fora = -1 if side < 0 else 1
                for d in (0.0, 0.45):
                    p0 = (ex + fora * rx * (1 - d * 0.6), ey + 4 + d * ry * 0.22)
                    self._line(k, [p0, (p0[0] + fora * 11, p0[1] + 9)], PUPIL, w=LINE * 0.75)
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
# família: mamãe e vovó muriçoca (mesmo modelo; acessórios próprios)
MAMAE = FlatLook(body="#C9A6F2", belly_a="#FFE066", belly_b="#9B6BD9", shoe="#9B6BD9", sole="#FFD23F",
                 pom="#9B6BD9", cheek="#FF8FC4", lashes=True, extra={"colar": "#FFFFFF", "flor": "#FF7FBF"})
VOVO = FlatLook(body="#8FD9C4", belly_a="#FFE066", belly_b="#3FA98C", shoe="#E9545D", sole="#FFFFFF",
                pom="#3FA98C", cheek="#FF9AAE", lashes=True, extra={"oculos": True, "coque": "#E4E4EE", "cabelo": "#E4E4EE"})
# amigas da turma (música 02): mesmo modelo, detalhes próprios
JOANINHA = FlatLook(body="#F2545B", belly_a="#F2545B", belly_b="#2B2B33", shoe="#2B2B33", sole="#FFD23F",
                    pom="#2B2B33", cheek="#FF9AAE", lashes=True, extra={"pintas": "#2B2B33", "abdomen_liso": True})
FORMIGA_MAE = FlatLook(body="#B86A3A", belly_a="#8E4C26", belly_b="#8E4C26", shoe="#E9545D", sole="#FFE066",
                       pom="#8E4C26", cheek="#FF8FA0", lashes=True,
                       extra={"asas": False, "abdomen_liso": True, "patas_meio": True, "antena_cotovelo": True, "flor": "#FFD23F"})
FORMIGUINHA = FlatLook(body="#E08A4F", belly_a="#B9652E", belly_b="#B9652E", shoe="#9B6BD9", sole="#FFE066",
                       pom="#B9652E", cheek="#FF8FA0", lashes=True,
                       extra={"asas": False, "abdomen_liso": True, "patas_meio": True, "antena_cotovelo": True})
