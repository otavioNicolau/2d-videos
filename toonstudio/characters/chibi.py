"""Modelo de criança "chibi fofinho" (v2 da turma) — pedido do usuário: personagens mais bonitos, no estilo das referências
de clipe infantil (cabeça ≈ metade da altura, olhos ovais escuros e brilhantes, bochechas rosadas, sem contorno preto,
volume por sombreado suave, membros curtinhos e mãos redondas, cabelo como massa lisa com brilho).

Usa os mesmos canais de pose dos outros personagens (coreografia, expressões, visemas funcionam igual). Os alvos de
mãos/pés da biblioteca foram pensados para braços longos: aqui são escalados (`ARM_K`, `LEG_K`).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..drawing.ink import Ink, ellipse_pts
from .base import Character, View, lerp, rot
from .kit import Kit, Style, darken, ik2, lighten

SOFT = Style(width=2.6, vary=0.0, ink_k=0.78, shade_k=0.8, soft=True)   # contorno quase invisível (tom da peça)
# estilo "desenho de TV": contorno marrom-escuro uniforme, cor chapada com sombra recortada (cel), olhos brancos grandes
CEL = Style(width=5.2, vary=0.2, ink_k=0.35, shade_k=0.84, soft=False, ink="#3B2219")
STYLES = {"fofo": SOFT, "cel": CEL}
ARM_K, LEG_K = 0.7, 0.6
HEAD_RX, HEAD_RY = 118.0, 108.0


@dataclass
class ChibiLook:
    skin: str = "#F4C7A1"
    hair: str = "#4A2E22"
    hair_style: str = "bagunçado"          # bagunçado | maria_chiquinha
    top: str = "#E8423F"
    top_detail: str = ""                    # "" | "flor" | "estrela"
    bottom: str = "#3E73C8"
    bottom_style: str = "bermuda"           # bermuda | saia
    shoe: str = "#2F8EE0"
    accent: str = "#FFD23F"                 # laços / detalhes
    eye: str = "#2B1A14"
    extra: dict = field(default_factory=dict)


class Chibi(Character):
    def __init__(self, cid: str, name: str, look: ChibiLook, style: str = "cel"):
        self.look = look
        self.style = STYLES[style]
        super().__init__(
            id=cid, name=name, canvas=(700, 640), anchor=(350, 600), height=430, palette=look.__dict__,
            defaults={
                "turn": 0.2, "back": False, "lean": 0.0, "squash": 1.0, "body_y": 0.0, "body_x": 0.0,
                "head_tilt": 0.0, "head_dx": 0.0, "head_dy": 0.0, "head_turn": 0.0,
                "hand_n_x": -42.0, "hand_n_y": 92.0, "hand_n_bend": 0.15, "paw_n": 0.0,
                "hand_f_x": 42.0, "hand_f_y": 92.0, "hand_f_bend": -0.15, "paw_f": 0.0,
                "foot_n_x": -10.0, "foot_n_y": 0.0, "foot_n_bend": 0.0, "foot_n_rot": 0.0,
                "foot_f_x": 12.0, "foot_f_y": 0.0, "foot_f_bend": 0.0, "foot_f_rot": 0.0,
                "mouth": "X", "smile": 0.75, "brow_y": 0.25, "blush": 0.6, "stars": 0.0, "speed": 0.0,
                "holding": "", "hair_bounce": 0.0,
            })

    # ------------------------------------------------------------------ corpo
    def draw(self, ink: Ink, P: dict) -> None:
        L = self.look
        kit = Kit(ink, self.style)
        v = View(P["turn"], P["back"])
        f, s = v.f, v.side
        sq = P["squash"]
        sx, sy = sq ** -0.7, sq
        leg = 66 * L.extra.get("perna", 1.0)             # crianças maiores: pernas e tronco mais longos
        tb = L.extra.get("tronco", 1.0)
        hip = (P["body_x"] * f, -leg + P["body_y"])
        lean = P["lean"] * f

        def T(p):
            x, y = (hip[0] + p[0]) * sx, (hip[1] + p[1]) * sy
            return rot((x, y), lean, (hip[0] * sx, hip[1] * sy))

        # sombra no chão
        ink.c.save()
        sh = ellipse_pts(hip[0] * 0.3, -4, 95, 15, 0, 16)
        ink.shape(sh, fill=(0, 0, 0, 0.12), line=0)
        ink.c.restore()

        neck = T((f * s * 4, -96 * tb))
        sh_n = T((lerp(-44 * f, -6 * f, s), -84 * tb))      # ombro na borda do tronco: o braço sai pelo lado
        sh_f = T((lerp(44 * f, 10 * f, s), -84 * tb))
        hip_n = T((lerp(-22 * f, -4 * f, s), 0))
        hip_f = T((lerp(22 * f, 8 * f, s), -2))
        ht = lean * 0.5 + P["head_tilt"] * f
        hsq = sq ** 0.25
        C = (neck[0] + f * P["head_dx"] + math.sin(ht) * 80, neck[1] - 92 * hsq + P["head_dy"])
        hv = View(max(-1, min(1, P["turn"] + P["head_turn"])), P["back"])

        hk = L.extra.get("cabeca", 1.0)

        def head_scope(fn):
            ink.c.save()
            ink.c.translate(*neck)
            ink.c.scale(hk, hk)
            ink.c.translate(-neck[0], -neck[1])
            fn()
            ink.c.restore()
        head_scope(lambda: self._back_hair(kit, P, C, hv, ht))
        self._arm(kit, P, "f", sh_f, f, s, True)
        self._leg(kit, P, "f", hip_f, f, s, True)
        self._leg(kit, P, "n", hip_n, f, s, False)
        # braço da frente: quando a mão fica fora do peito, nasce por trás do tronco (ombro sem emenda)
        hn_x = P["hand_n_x"] * ARM_K
        crosses = hn_x * 1 > -10 and P["hand_n_y"] * ARM_K > -30      # mão vai para o centro do corpo
        if not crosses:
            self._arm(kit, P, "n", sh_n, f, s, False, sleeve=False)
        # tronco (camiseta) — forma de "gota" arredondada
        w0, w1 = lerp(52, 40, s), lerp(62, 50, s)
        torso = [T(p) for p in ((-w0 * f, -100 * tb), (w0 * f, -100 * tb), (w1 * f, -38 * tb), (w1 * 1.02 * f, 8), (0, 14),
                                 (-w1 * 1.02 * f, 8), (-w1 * f, -38 * tb))]
        if L.bottom_style == "bermuda":
            kit.blob([T(p) for p in ((-w1 * f, -12), (w1 * f, -12), (w1 * 1.05 * f, 26), (0, 30), (-w1 * 1.05 * f, 26))],
                     L.bottom)
        kit.blob(torso, L.top, clip_extra=lambda kk: self._top_detail(kk, T, v, f, s))
        if L.bottom_style == "saia":
            kit.blob([T(p) for p in ((-w1 * f, -16), (w1 * f, -16), (w1 * 1.45 * f, 34), (w1 * 0.6 * f, 40), (0, 42),
                                     (-w1 * 0.6 * f, 40), (-w1 * 1.45 * f, 34))], L.bottom)
        if not crosses:      # manguinha por cima do ombro, já dentro do contorno do tronco
            self._sleeve_cap(kit, sh_n, f, s)
        head_scope(lambda: self._head(kit, P, C, hv, ht, hsq))
        if crosses:
            self._arm(kit, P, "n", sh_n, f, s, False)

    def _top_detail(self, kk: Ink, T, v: View, f, s):
        L = self.look
        if v.back or not L.top_detail:
            return
        c = T((f * s * 20, -56))
        if L.top_detail == "flor":
            for k in range(5):
                a = k * 2 * math.pi / 5
                kk.ellipse(c[0] + math.cos(a) * 10, c[1] + math.sin(a) * 10, 8, 8, "#FFFFFF", line=0)
            kk.dot(c[0], c[1], 6, L.accent)
        elif L.top_detail == "estrela":
            pts = [(c[0] + math.cos(-math.pi / 2 + j * math.pi / 5) * (17 if j % 2 == 0 else 7),
                    c[1] + math.sin(-math.pi / 2 + j * math.pi / 5) * (17 if j % 2 == 0 else 7)) for j in range(10)]
            kk.shape(pts, fill=L.accent, smooth=False, line=0)

    def _sleeve_cap(self, kit: Kit, S, f, s):
        L = self.look
        kit.k.shape(ellipse_pts(S[0] + f * 4, S[1] + 8, 20, 17, 0, 12), fill=darken(L.top, 0.94), line=0)

    def _arm(self, kit: Kit, P, which, S, f, s, behind, sleeve: bool = True):
        """Braço de verdade: braço + antebraço de comprimento fixo, dobrando no cotovelo (IK de 2 ossos)."""
        L = self.look
        ak = ARM_K * L.extra.get("braco", 1.0)
        T = (S[0] + P[f"hand_{which}_x"] * f * ak, S[1] + P[f"hand_{which}_y"] * ak)
        l1 = l2 = 38 * L.extra.get("braco", 1.0)
        bend = P[f"hand_{which}_bend"]
        # cotovelo: + = para trás do personagem; também sempre um pouco para baixo/fora (braço de criança relaxado)
        side = (-f if bend >= 0 else f, 0.35)
        E, H = ik2(S, T, l1, l2, side)
        dx, dy = H[0] - E[0], H[1] - E[1]
        Ln = math.hypot(dx, dy) or 1
        skin = darken(L.skin, 0.9) if behind else L.skin
        kit.limb([S, E], 28, 27, skin)               # braço (segmento reto)
        kit.limb([E, H], 27, 25, skin)               # antebraço (segmento reto)
        if sleeve:
            a = math.atan2(E[1] - S[1], E[0] - S[0])
            c0 = (S[0] + math.cos(a) * 8, S[1] + math.sin(a) * 8)
            kit.blob(ellipse_pts(c0[0], c0[1], 23, 21, a, 14), darken(L.top, 0.9) if behind else L.top)
        self._hand(kit, P, which, H, dx, dy, Ln, skin)

    def _hand(self, kit: Kit, P, which, H, dx, dy, Ln, skin):
        # mão redonda (luva), polegar só quando aberta
        r = 17
        kit.blob(ellipse_pts(H[0] + dx / Ln * 6, H[1] + dy / Ln * 6, r, r * 0.95, 0, 12), skin)
        if P[f"paw_{which}"] >= 2.5:
            a = math.atan2(dy, dx) - 1.2
            kit.blob(ellipse_pts(H[0] + math.cos(a) * r, H[1] + math.sin(a) * r, 8, 6, a, 8), skin, shade=False)

    def _leg(self, kit: Kit, P, which, Hp, f, s, behind):
        """Perna com coxa e canela de comprimento fixo; o joelho dobra para a frente (IK)."""
        L = self.look
        F = (Hp[0] + P[f"foot_{which}_x"] * f * LEG_K, P[f"foot_{which}_y"] * LEG_K)
        ankle = (F[0], F[1] - 14)
        seg = (66 * L.extra.get("perna", 1.0) - 14) / 2 + 1.5      # em pé fica quase reta, sem esticar
        K, A = ik2(Hp, ankle, seg, seg, (f, 0.0))
        skin = darken(L.skin, 0.9) if behind else L.skin
        kit.limb([Hp, K], 34, 32, skin)
        kit.limb([K, A], 32, 30, skin)
        F = (A[0], A[1] + 14)
        cx = F[0] + f * s * 10
        shoe = darken(L.shoe, 0.88) if behind else L.shoe
        kit.blob(ellipse_pts(cx, F[1] - 14, lerp(30, 38, s), 17, P[f"foot_{which}_rot"] * f, 14), shoe)
        kit.k.stroke([(cx - lerp(28, 34, s), F[1] - 3), (cx + lerp(28, 36, s), F[1] - 3)], 6, taper=(0.1, 0.1),
                     color_=lighten(L.shoe, 0.75))

    # ------------------------------------------------------------------ cabeça
    def _head(self, kit: Kit, P, C, v: View, ht, hsq):
        L = self.look
        f, s = v.f, v.side
        k = kit.k
        rx, ry = HEAD_RX * (1 - 0.05 * s), HEAD_RY * hsq
        # orelhas
        for side in (-1, 1):
            x, c = v.sphere(C[0], rx * 0.98, side * 1.55)
            if c > -0.2:
                kit.blob(ellipse_pts(x, C[1] + 16, 16 * max(c, 0.5), 22, 0, 12), L.skin)
                if not self.style.soft and c > 0.2:     # dobrinha da orelha (C)
                    kit.k.stroke([(x + side * 3, C[1] + 6), (x - side * 5, C[1] + 14), (x + side * 2, C[1] + 26)], 3.5,
                                 taper=(0.3, 0.3), color_=self.style.ink)
        head = [rot((C[0] + rx * math.cos(a) * (1 - 0.04 * (math.sin(a) > 0)), C[1] + ry * math.sin(a) * (1.04 if math.sin(a) > 0 else 1)), ht, C)
                for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)]
        kit.blob(head, L.skin)
        if v.back:
            self._hair(kit, P, C, v, ht, back=True)
            return
        # rosto: posição dos traços acompanha o giro (esfera)
        def face(ang, dy):
            x, c = v.sphere(C[0], rx * 0.92, ang)
            return rot((x, C[1] + dy), ht, C), c
        for side in (-1, 1):                         # bochechas
            (bx, by), c = face(side * 0.62, 36)
            if c > 0.25:
                k.ellipse(bx, by, 20 * c, 11, (0.98, 0.52, 0.52, 0.35 + 0.35 * P.get("blush", 0.6)), line=0)
        for side in (-1, 1):                         # olhos
            (ex, ey), c = face(side * 0.38, 8)
            if c > 0.3:
                self._eye(kit, P, ex, ey, c, side, f, s, ht)
        if L.extra.get("sardas"):
            for side in (-1, 1):
                for dx_, dy_ in ((-10, 0), (0, -6), (10, 2), (4, 10), (-6, 9)):
                    (fx_, fy_), c = face(side * 0.5, 22)
                    if c > 0.3:
                        k.dot(fx_ + dx_ * c, fy_ + dy_, 2.6, darken(L.skin, 0.72))
        (nx_, ny_), c = face(0.0, 30)                 # narizinho
        if self.style.soft:
            k.ellipse(nx_ + f * s * 6, ny_, 6.5, 5, darken(L.skin, 0.82), line=0)
        else:      # narizinho de TV: curva com sombra embaixo
            nx2 = nx_ + f * s * 14
            k.stroke([(nx2 - 10, ny_ + 2), (nx2 - 4, ny_ + 9), (nx2 + 6, ny_ + 8), (nx2 + 11, ny_ + 1)], 4.5,
                     taper=(0.4, 0.4), color_=self.style.ink)
        (mx, my), c = face(-f * 0.04 * s, 56)        # boca
        if self.style.soft:
            kit.mouth(P, (mx, my), f, s, ht, width=19, line="#8C3A34", lips="#C9615A", tongue="#F07C86", inside_col="#8A2A36")
        else:
            kit.mouth(P, (mx, my), f, s, ht, width=24, line=self.style.ink, lips=self.style.ink, tongue="#F07C86",
                      inside_col="#7A2430")
        self._hair(kit, P, C, v, ht, back=False)

    def _eye(self, kit: Kit, P, ex, ey, c, side, f, s, ht):
        if not self.style.soft:
            return self._eye_cel(kit, P, ex, ey, c, side, f, s, ht)
        return self._eye_fofo(kit, P, ex, ey, c, side, f, s, ht)

    def _eye_cel(self, kit: Kit, P, ex, ey, c, side, f, s, ht):
        """Olho de desenho de TV: branco grande contornado, pupila escura grande com brilho, pálpebra e sobrancelha grossa."""
        L = self.look
        k = kit.k
        es = P["eye_scale"]
        rx, ry = 25 * c * es, 32 * es          # olhos grandes (expressão lê de longe)
        inner = -side
        b = P["brow_l"] if side < 0 else P["brow_r"]
        by = ey - ry - 12 - P["brow_y"] * 9
        if P.get("eyes_happy", 0) > 0.5:
            k.stroke([(ex - rx * 1.1, ey + 6), (ex, ey - ry * 0.55), (ex + rx * 1.1, ey + 6)], 7, taper=(0.3, 0.3),
                     color_=self.style.ink)
        else:
            lid, lid_low = P["lid"], P["lid_low"]
            lx = (P["look_x"] * f * 0.45 + 0.22 * f * s) * rx
            ly = P["look_y"] * 0.4 * ry

            def inside(kk: Ink):
                pr = ry * 0.56 * P["pupil"] ** 0.5
                kk.ellipse(ex + lx + inner * rx * 0.08, ey + ly + 3, pr * 0.82 * max(c, 0.6), pr, L.eye, line=0)
                kk.dot(ex + lx + inner * rx * 0.08 - pr * 0.3, ey + ly - pr * 0.35, max(3.0, pr * 0.32), "#FFFFFF")
                if lid > 0.02:
                    top = ey - ry - 4 + (2 * ry + 8) * lid
                    kk.c.drawRect(_rect(ex - rx - 8, ey - ry - 30, ex + rx + 8, top), _p(L.skin))
                    kk.stroke([(ex - rx - 2, top), (ex + rx + 2, top)], 4.5, color_=self.style.ink)
                if lid_low > 0.02:
                    bot = ey + ry + 4 - ry * 1.1 * lid_low
                    kk.c.drawRect(_rect(ex - rx - 8, bot, ex + rx + 8, ey + ry + 30), _p(L.skin))
            k.shape(ellipse_pts(ex, ey, rx, ry, ht, 16), fill="#FFFFFF", brush=kit.brush("#FFFFFF", 4.5), clip_extra=inside)
        # sobrancelha grossa e expressiva
        x0, x1 = ex - 18 * c * inner * -1, ex + 18 * c * inner * -1
        y0, y1 = by - b * 3, by + b * 9
        k.stroke([(ex - 19 * c, by + (b * 8 if inner < 0 else -b * 3) + 2), (ex, by - 5),
                  (ex + 19 * c, by + (b * 8 if inner > 0 else -b * 3) + 2)], 9 * max(c, 0.6), taper=(0.35, 0.35),
                 color_=darken(L.hair, 0.55) if L.hair_style != "black_power" else "#1A110E")

    def _eye_fofo(self, kit: Kit, P, ex, ey, c, side, f, s, ht):
        """Olho oval escuro com dois brilhos (estilo das referências), pálpebra e sobrancelha fininha."""
        L = self.look
        k = kit.k
        es = P["eye_scale"]
        rx, ry = 14 * c * es, 19 * es
        by = ey - ry - 16 - P["brow_y"] * 8
        b = P["brow_l"] if side < 0 else P["brow_r"]
        inner = -side
        if P.get("eyes_happy", 0) > 0.5:
            k.stroke([(ex - rx * 1.3, ey + 5), (ex, ey - ry * 0.55), (ex + rx * 1.3, ey + 5)], 6.5, taper=(0.3, 0.3),
                     color_=L.eye)
        else:
            lid = P["lid"]
            look = (P["look_x"] * f * 0.35 + 0.15 * f * s) * rx

            def inside(kk: Ink):
                _star(kk, ex + look - rx * 0.28, ey - ry * 0.33, max(4.0, rx * 0.62), "#FFFFFF")   # assinatura do canal
                kk.dot(ex + look + rx * 0.3, ey + ry * 0.38, max(1.5, rx * 0.17), "#FFFFFF")
                if lid > 0.02:
                    top = ey - ry - 2 + (2 * ry + 4) * lid
                    kk.c.drawRect(_rect(ex - rx - 6, ey - ry - 20, ex + rx + 6, top), _p(L.skin))
                    kk.stroke([(ex - rx - 2, top), (ex + rx + 2, top)], 3.5, color_=L.eye)
            k.shape(ellipse_pts(ex + look * 0.3, ey, rx, ry, ht, 14), fill=L.eye, line=0, clip_extra=inside)
        k.stroke([(ex - 13 * c, by + b * 4 * inner * -1 + 2), (ex, by - 3), (ex + 13 * c, by + b * 4 * inner + 2)],
                 4.5, taper=(0.3, 0.3), color_=darken(L.hair, 0.9))

    # ------------------------------------------------------------------ cabelo
    def _signature(self, kit: Kit, P, C, v: View, ht, back, rx, ry):
        """Traços únicos de cada criança (silhueta reconhecível)."""
        L = self.look
        f, s = v.f, v.side
        bounce = P.get("hair_bounce", 0.0)
        sig = L.extra.get("assinatura", "")
        k = kit.k
        if sig == "molinha":       # cachinho em espiral de mola no topo (balança com o corpo)
            base = rot((C[0] + 8 - f * s * 10, C[1] - ry * 1.08), ht, C)
            sw = P.get("head_tilt", 0.0) * 1.5 + bounce * 0.4
            pts = []
            for i in range(40):
                u = i / 39
                a = u * 4.2 * math.pi
                r = 6 + 16 * u
                pts.append(rot((base[0] + r * math.cos(a) * 0.9, base[1] - 70 * u - r * math.sin(a) * 0.45), sw * u, base))
            k.stroke(pts, 15, taper=(0.0, 0.5), color_=darken(L.hair, 0.82))
            k.stroke(pts, 9, taper=(0.0, 0.6), color_=L.hair)
        elif sig == "coquinhos":   # dois coques fofos de "nuvem" no alto, com presilha de estrela
            for side in (-1, 1):
                x, c = v.sphere(C[0], rx * 0.62, side * 0.75)
                B = rot((x, C[1] - ry * 1.02 - bounce * 6), ht, C)
                lobes = [(B[0] + 30 * math.cos(a) * (1 + 0.12 * abs(math.sin(a * 3))),
                          B[1] + 28 * math.sin(a) * (1 + 0.12 * abs(math.sin(a * 3)))) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
                kit.blob(lobes, L.hair)
                _star(k, B[0] + side * 4, B[1] + 26, 13, L.accent)
        elif sig == "faixa":   # faixa esportiva atravessando o black power
            band = [rot((C[0] + u * rx * 1.16 - f * s * 18, C[1] - 52 + 30 * abs(u) ** 2 - 20), ht, C) for u in np.linspace(-1, 1, 15)]
            k.stroke(band, 22, taper=(0.05, 0.05), color_=L.accent)
            k.stroke([(p[0], p[1] - 4) for p in band[2:-2]], 4, taper=(0.1, 0.1), color_=lighten(L.accent, 0.5))
        elif sig == "bone" and not back:   # boné virado para trás: copa sobre o cabelo, aba saindo atrás
            cap = [rot((C[0] + rx * 1.02 * math.cos(a) - f * s * 10, C[1] - 18 + ry * 0.95 * math.sin(a)), ht, C)
                   for a in np.linspace(math.pi * 1.02, math.pi * 1.98, 20)]
            cap += [rot((C[0] + u * rx * 1.02 - f * s * 10, C[1] - 30), ht, C) for u in np.linspace(1, -1, 7)]
            kit.blob(cap, L.accent)
            brim = [rot((C[0] - f * (rx * 0.9) + dx, C[1] - 34 + dy), ht, C)
                    for dx, dy in ((-f * 10, -14), (-f * 70, -10), (-f * 78, 6), (-f * 10, 8))]
            kit.blob(brim, darken(L.accent, 0.85))
            kit.k.dot(*rot((C[0] - f * s * 10, C[1] - ry * 0.98), ht, C), 7, darken(L.accent, 0.7))
        elif sig == "flor" and not back:   # flor grande presa ao cabelo
            x, c = v.sphere(C[0], rx * 0.9, 0.9)
            B = rot((x, C[1] - 56), ht, C)
            for j in range(6):
                a = j * math.pi / 3
                kit.blob(ellipse_pts(B[0] + math.cos(a) * 17, B[1] + math.sin(a) * 17, 14, 11, a, 10), L.accent, shade=False)
            kit.blob(ellipse_pts(B[0], B[1], 10, 10, 0, 10), "#FFFFFF", shade=False)
        if L.extra.get("oculos") and not back:      # óculos redondos
            for side in (-1, 1):
                x, c = v.sphere(C[0], rx * 0.92 / 1.06, side * 0.38)
                if c > 0.3:
                    E = rot((x, C[1] + 8), ht, C)
                    k.c.save()
                    pt = _p((0.15, 0.1, 0.2, 1))
                    import skia
                    pt.setStyle(skia.Paint.kStroke_Style)
                    pt.setStrokeWidth(4.5)
                    pt.setAntiAlias(True)
                    k.c.drawOval(skia.Rect(E[0] - 30 * c, E[1] - 28, E[0] + 30 * c, E[1] + 28), pt)
                    k.c.restore()

    def _back_hair(self, kit: Kit, P, C, v: View, ht):
        L = self.look
        f, s = v.f, v.side
        sway = P.get("head_tilt", 0.0) * 40 + P.get("hair_bounce", 0.0) * 6
        if L.hair_style == "liso" and L.extra.get("comprido"):   # cabelo comprido e liso até os ombros
            w = HEAD_RX * 1.06
            long_ = [(C[0] - w, C[1] - 20), (C[0] - w - 6, C[1] + 90), (C[0] - w + 20 + sway, C[1] + 160),
                     (C[0] - 30 + sway, C[1] + 170), (C[0] + 30 + sway, C[1] + 170), (C[0] + w - 20 + sway, C[1] + 160),
                     (C[0] + w + 6, C[1] + 90), (C[0] + w, C[1] - 20), (C[0], C[1] - 100)]
            kit.blob([rot(p, ht, C) for p in long_], darken(L.hair, 0.9))
            return
        if L.hair_style == "chanel":       # corte chanel: desce até o queixo pelos lados
            w = HEAD_RX * 1.08
            bob = [(C[0] - w, C[1] - 20), (C[0] - w - 4, C[1] + 66), (C[0] - w + 34 + sway * 0.3, C[1] + 78),
                   (C[0] + w - 34 + sway * 0.3, C[1] + 78), (C[0] + w + 4, C[1] + 66), (C[0] + w, C[1] - 20), (C[0], C[1] - 100)]
            kit.blob([rot(p, ht, C) for p in bob], darken(L.hair, 0.9))
            return
        if L.hair_style == "rabo":         # rabo de cavalo alto que balança atrás da cabeça
            A = rot((C[0] - f * (40 + 60 * s), C[1] - 70), ht, C)
            sw = P.get("head_tilt", 0.0) * 1.2 * f + P.get("hair_bounce", 0.0) * 0.3 + P.get("body_x", 0.0) * 0.004
            tail = [(0, -16), (-f * 40, -26), (-f * 82, 4), (-f * 96, 60), (-f * 74, 108), (-f * 56, 70), (-f * 20, 14)]
            kit.blob([rot((A[0] + px, A[1] + py), sw, A) for px, py in tail], L.hair)
            if L.extra.get("cachos"):      # cachos de mola descendo pelo rabo
                for j, (px, py) in enumerate(((-f * 70, 30), (-f * 82, 62), (-f * 70, 94))):
                    q = rot((A[0] + px, A[1] + py), sw, A)
                    kit.k.stroke([(q[0] - 16, q[1] - 6), (q[0], q[1] + 6), (q[0] + 16, q[1] - 6)], 5,
                                 taper=(0.3, 0.3), color_=darken(L.hair, 0.75))
            kit.blob(ellipse_pts(A[0], A[1] - 4, 14, 12, 0, 10), L.accent)
            return
        if L.hair_style != "maria_chiquinha":
            return
        sway = P.get("head_tilt", 0.0) * 40 + P.get("hair_bounce", 0.0) * 6
        w = HEAD_RX * 1.02
        back = [(C[0] - w, C[1] - 10), (C[0] - w - 6, C[1] + 70), (C[0] - w + 30 + sway, C[1] + 118),
                (C[0] + w - 30 + sway, C[1] + 118), (C[0] + w + 6, C[1] + 70), (C[0] + w, C[1] - 10), (C[0], C[1] - 100)]
        kit.blob([rot(p, ht, C) for p in back], darken(L.hair, 0.9))
        for side in (-1, 1):                 # maria-chiquinhas fofas
            x, c = v.sphere(C[0], HEAD_RX * 1.02, side * 1.3)
            A = rot((x + side * 18, C[1] - 52), ht, C)
            sw = P.get("head_tilt", 0.0) * 0.9 * side + P.get("hair_bounce", 0.0) * 0.25
            tail = [(0, -22), (side * 46, -30), (side * 84, 0), (side * 92, 42), (side * 70, 76), (side * 40, 60), (side * 14, 18)]
            kit.blob([rot((A[0] + px, A[1] + py), sw, A) for px, py in tail], L.hair)

    def _hair(self, kit: Kit, P, C, v: View, ht, back: bool):
        L = self.look
        f, s = v.f, v.side
        bounce = P.get("hair_bounce", 0.0)
        rx, ry = HEAD_RX * 1.06, HEAD_RY * 1.04
        pts = []
        if L.hair_style == "bagunçado":
            # massa fofa: contorno de "nuvem" (lobos arredondados) que cobre o alto e desce pelas laterais
            lobes = 9
            for a in np.linspace(math.pi * 0.97, math.pi * 2.03, 60):
                ph = (a - math.pi * 0.97) / (math.pi * 1.06) * lobes
                bump = 1 + 0.085 * abs(math.sin(ph * math.pi))
                pts.append((C[0] + rx * 1.06 * bump * math.cos(a), C[1] - 2 + ry * 1.08 * bump * math.sin(a)
                            - bounce * 6 * max(0.0, -math.sin(a))))
            # franja: 3 conchas arredondadas sobre a testa (deslocam com o giro)
            for u in np.linspace(0.98, -0.98, 25):
                x = C[0] + u * rx * 0.98 - f * s * 24
                sc = abs(math.sin((u + 1) * math.pi * 1.5))            # 3 arcos
                y = C[1] - 46 + 22 * sc - (26 * max(0.0, abs(u) - 0.8) / 0.2)
                pts.append((x, y))
        elif L.hair_style == "black_power":
            # nuvem grande e redonda com textura de cachinhos na borda
            # nuvem grande e alta (cobre o alto e as laterais até a altura da orelha), textura de cachinhos na borda
            for a in np.linspace(math.pi * 0.93, math.pi * 2.07, 70):
                bump = 1 + 0.055 * abs(math.sin(a * 13))
                pts.append((C[0] + rx * 1.3 * bump * math.cos(a), C[1] - 34 + ry * 1.3 * bump * math.sin(a)
                            - bounce * 6 * max(0.0, -math.sin(a))))
            for u in np.linspace(0.95, -0.95, 13):                # linha da testa arredondada, acima das sobrancelhas
                pts.append((C[0] + u * rx * 0.96 - f * s * 22, C[1] - 52 + 30 * abs(u) ** 2))
        elif L.hair_style in ("liso_curto", "rabo"):
            for a in np.linspace(math.pi * 0.98, math.pi * 2.02, 30):
                pts.append((C[0] + rx * 1.03 * math.cos(a), C[1] - 2 + ry * 1.05 * math.sin(a)))
            part = 0.35 if L.hair_style == "liso_curto" else 0.0   # repartido de lado: franja varre para um lado
            for u in np.linspace(1, -1, 13):
                sweep = (u - part) * 0.9
                y = C[1] - 40 + 12 * max(0.0, -sweep) - 30 * max(0.0, abs(u) - 0.75) / 0.25   # sobe suave nas têmporas
                pts.append((C[0] + u * rx * 0.97 - f * s * 22, y))
        elif L.hair_style == "chanel":
            for a in np.linspace(math.pi * 0.98, math.pi * 2.02, 30):
                pts.append((C[0] + rx * 1.07 * math.cos(a), C[1] - 2 + ry * 1.06 * math.sin(a)))
            for u in np.linspace(1, -1, 9):
                pts.append((C[0] + u * rx * 0.95 - f * s * 22, C[1] - 30 + (0 if abs(u) < 0.9 else -10)))
        else:   # franja reta e lisa
            for a in np.linspace(math.pi * 1.0, math.pi * 2.0, 26):
                pts.append((C[0] + rx * math.cos(a), C[1] - 4 + ry * math.sin(a)))
            for u in np.linspace(1, -1, 9):
                pts.append((C[0] + u * rx * 0.96 - f * s * 22, C[1] - 34 + (6 if abs(u) < 0.9 else -26)))
        if back:
            pts = [(C[0] + rx * 1.05 * math.cos(a), C[1] - 4 + ry * 1.05 * math.sin(a) * (1.0 if math.sin(a) < 0 else 0.62))
                   for a in np.linspace(0, 2 * math.pi, 30, endpoint=False)]
        pts = [rot(p, ht, C) for p in pts]
        kit.blob(pts, L.hair)
        self._signature(kit, P, C, v, ht, back, rx, ry)
        # brilho do cabelo (faixa clara em arco)
        hl = [rot((C[0] + rx * 0.62 * math.cos(a) - f * s * 20, C[1] - 18 + ry * 0.72 * math.sin(a)), ht, C)
              for a in np.linspace(math.pi * 1.22, math.pi * 1.62, 8)]
        kit.k.stroke(hl, 13, taper=(0.4, 0.4), color_=(1, 1, 1, 0.22))
        if L.hair_style == "maria_chiquinha":
            for side in (-1, 1):
                x, c = v.sphere(C[0], HEAD_RX * 1.02, side * 1.15)
                if c < -0.2 and not back:
                    continue
                B = rot((x, C[1] - 70), ht, C)
                for wing in (-1, 1):
                    kit.blob([(B[0], B[1]), (B[0] + wing * 28, B[1] - 18), (B[0] + wing * 30, B[1] + 14)], L.accent)
                kit.blob(ellipse_pts(B[0], B[1], 9, 8, 0, 10), L.accent)


def _star(k: Ink, x, y, r, col):
    """Estrelinha de 4 pontas (brilho dos olhos = marca visual da turma)."""
    pts = []
    for j in range(8):
        rr = r if j % 2 == 0 else r * 0.32
        a = -math.pi / 2 + j * math.pi / 4
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    k.shape(pts, fill=col, smooth=False, line=0)


def _rect(l, t, r, b):
    import skia
    return skia.Rect(l, t, r, b)


def _p(c):
    from ..drawing.ink import paint
    return paint(c)


# ---------------------------------------------------------------- elenco do canal (Laurinha e Luizinho são loirinhos)
LUIZINHO = ChibiLook(skin="#F6CDAA", hair="#E9B949", hair_style="bagunçado", top="#E8423F", top_detail="estrela",
                     bottom="#3E73C8", bottom_style="bermuda", shoe="#2F8EE0", accent="#FFD23F", eye="#2A1712",
                     extra={"assinatura": "molinha"})
LAURINHA = ChibiLook(skin="#F8D2B3", hair="#F0C559", hair_style="liso", top="#FF7A9C", top_detail="flor",
                     bottom="#26B8AE", bottom_style="saia", shoe="#FF6FA8", accent="#FFD23F", eye="#2B1A14",
                     extra={"assinatura": "coquinhos", "comprido": True,
                            # a mais velha da turma (11 anos): mais alta, cabeça proporcionalmente menor
                            "perna": 1.55, "tronco": 1.28, "cabeca": 0.9, "braco": 1.2})
DAVI = ChibiLook(skin="#8A5638", hair="#1E1512", hair_style="black_power", top="#2DB34A", top_detail="estrela",
                 bottom="#FF8A1F", bottom_style="bermuda", shoe="#F7F3E8", accent="#FFD23F", eye="#1A0F0C",
                 extra={"assinatura": "faixa"})
BIA = ChibiLook(skin="#FBDCC4", hair="#D9562B", hair_style="rabo", top="#3C8BF0", top_detail="flor",
                bottom="#FFC21A", bottom_style="saia", shoe="#7B3FD1", accent="#2DB34A", eye="#3A2418", extra={"sardas": True, "oculos": True, "cachos": True})
MATEO = ChibiLook(skin="#D7A07A", hair="#1F1B1B", hair_style="liso_curto", top="#FFC21A", top_detail="estrela",
                  bottom="#2DB34A", bottom_style="bermuda", shoe="#E0322E", accent="#2E9E56", eye="#24160F",
                  extra={"assinatura": "bone"})
NINA = ChibiLook(skin="#F3D1B0", hair="#141214", hair_style="chanel", top="#7B3FD1", top_detail="flor",
                 bottom="#F05A9A", bottom_style="saia", shoe="#2EC4B6", accent="#FF9EC7", eye="#1A1210",
                 extra={"assinatura": "flor"})
TURMA = {"luizinho": ("Luizinho", LUIZINHO), "laurinha": ("Laurinha", LAURINHA), "davi": ("Davi", DAVI),
         "bia": ("Bia", BIA), "mateo": ("Mateo", MATEO), "nina": ("Nina", NINA)}
