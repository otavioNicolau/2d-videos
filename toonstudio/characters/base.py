"""Base dos personagens desenhados por código (ADR-0002).

Uma pose é um dicionário de canais numéricos (interpoláveis) + alguns categóricos (boca, vista de costas).
O personagem redesenha tudo a partir da pose — não existem imagens prontas de partes do corpo.

Convenções (unidades = pixels no palco 1080p, escala 1):
- origem no ponto de apoio no chão, y para baixo;
- `turn` em [-1, 1]: 0 = frente, ±0,5 = 3/4, ±1 = perfil; o sinal é para onde o personagem olha (+ = direita);
- alvos de mão/pé em coordenadas "para a frente" (+x = direção do olhar), relativos ao ombro/quadril.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..drawing.ink import Brush, Ink, new_surface, to_array, save_png

# canais faciais comuns
FACE_NEUTRAL = {
    "brow_l": 0.0, "brow_r": 0.0,       # inclinação: + = bravo (ponta interna para baixo), - = triste/preocupado
    "brow_y": 0.0,                      # + = sobrancelhas levantadas
    "lid": 0.0,                         # 0 aberto, 1 fechado
    "lid_low": 0.0,                     # pálpebra de baixo subindo (sorriso de olhos, desconfiança)
    "eye_scale": 1.0,                   # olhos esbugalhados > 1
    "pupil": 1.0,                       # tamanho da pupila
    "look_x": 0.0, "look_y": 0.0,       # direção do olhar (-1..1), relativo à frente do personagem
    "smile": 0.2,                       # -1 tristeza .. 1 sorriso
    "jaw": 0.0,                         # abertura extra além do visema (grito)
    "tears": 0.0, "sweat": 0.0, "blush": 0.0,
    "eyes_happy": 0.0,                  # >0,5: olhos fechados em arco "^^" (alegria pura, canto, riso)
}

EXPRESSIONS: dict[str, dict[str, float]] = {
    "neutral": {},
    "happy": {"brow_y": 0.35, "smile": 0.9, "lid_low": 0.35, "brow_l": -0.1, "brow_r": -0.1},
    "angry": {"brow_l": 0.9, "brow_r": 0.9, "brow_y": -0.4, "smile": -0.6, "lid": 0.25, "pupil": 0.8},
    "sad": {"brow_l": -0.8, "brow_r": -0.8, "brow_y": 0.15, "smile": -0.8, "lid": 0.35, "look_y": 0.5},
    "surprised": {"brow_y": 0.7, "eye_scale": 1.35, "pupil": 0.6, "smile": 0.0, "jaw": 0.5},
    "shock": {"brow_y": 1.4, "eye_scale": 1.7, "pupil": 0.45, "smile": -0.2, "jaw": 1.0},
    "scared": {"brow_l": -0.9, "brow_r": -0.9, "brow_y": 0.55, "eye_scale": 1.3, "pupil": 0.5, "smile": -0.7, "sweat": 1.0},
    "laughing": {"brow_y": 0.4, "lid": 0.85, "smile": 1.0, "jaw": 0.7, "lid_low": 0.4},
    "crying": {"brow_l": -1.0, "brow_r": -1.0, "brow_y": 0.3, "lid": 0.75, "smile": -1.0, "jaw": 0.5, "tears": 1.0},
    "confused": {"brow_l": 0.6, "brow_r": -0.7, "brow_y": 0.2, "smile": -0.2, "look_y": -0.6, "look_x": 0.4},
    "sly": {"brow_l": 0.55, "brow_r": -0.3, "lid": 0.45, "lid_low": 0.2, "smile": 0.75, "look_x": 0.6},
    "dizzy": {"brow_l": -0.5, "brow_r": 0.4, "lid": 0.3, "smile": -0.3, "jaw": 0.25},
    "sleepy": {"lid": 0.7, "brow_y": -0.2, "smile": 0.0},
    "determined": {"brow_l": 0.6, "brow_r": 0.6, "brow_y": -0.2, "smile": -0.2, "lid": 0.15},
    "joy": {"eyes_happy": 1.0, "smile": 1.0, "brow_y": 0.5, "blush": 1.0, "jaw": 0.25},
}

VISEMES = "ABCDEFGHX"   # Rhubarb (Preston Blair estendido)


def expression(name: str, amount: float = 1.0) -> dict[str, float]:
    if name not in EXPRESSIONS:
        raise KeyError(f"expressão desconhecida: {name} (disponíveis: {sorted(EXPRESSIONS)})")
    out = dict(FACE_NEUTRAL)
    for k, v in EXPRESSIONS[name].items():
        out[k] = FACE_NEUTRAL[k] + (v - FACE_NEUTRAL[k]) * amount
    return out


@dataclass
class View:
    """Geometria da vista: direção (f) e quanto o personagem está de perfil (|turn|)."""
    turn: float
    back: bool = False

    @property
    def f(self) -> float:
        return 1.0 if self.turn >= 0 else -1.0

    @property
    def side(self) -> float:      # 0 frente .. 1 perfil
        return min(1.0, abs(self.turn))

    def sphere(self, cx: float, r: float, ang: float) -> tuple[float, float]:
        """Elemento num ângulo `ang` (rad, 0 = centro da cara) sobre uma cabeça redonda que gira.
        Retorna (x, escala de escorço); escala <= 0 significa escondido atrás."""
        a = ang + self.turn * (math.pi / 2) * 0.92
        return cx + r * math.sin(a), math.cos(a)


def rot(p, ang: float, center=(0.0, 0.0)):
    x, y = p[0] - center[0], p[1] - center[1]
    c, s = math.cos(ang), math.sin(ang)
    return (center[0] + x * c - y * s, center[1] + x * s + y * c)


def lerp(a, b, t):
    return a + (b - a) * t


@dataclass
class Character:
    id: str
    name: str
    canvas: tuple[int, int]          # tamanho do quadro em unidades
    anchor: tuple[int, int]          # onde fica a origem (pé no chão) dentro do quadro
    height: float                    # altura de referência em pé (unidades)
    palette: dict[str, str] = field(default_factory=dict)
    defaults: dict[str, Any] = field(default_factory=dict)

    def pose(self, **kw) -> dict[str, Any]:
        p = dict(FACE_NEUTRAL)
        p.update({"rot": 0.0, "rot_pivot": 0.0, "flat": 0.0, "stretch_x": 1.0})
        p.update(self.defaults)
        p.update(kw)
        return p

    # implementado por cada personagem
    def draw(self, ink: Ink, p: dict[str, Any]) -> None:
        raise NotImplementedError

    def render(self, p: dict[str, Any], scale: float = 1.5, seed: int = 0, jitter: float = 0.5,
               canvas: tuple[int, int] | None = None, anchor: tuple[int, int] | None = None):
        """Desenha uma pose num quadro transparente. Retorna o Surface do Skia.
        `canvas`/`anchor` permitem um quadro padronizado (níveis do OpenToonz)."""
        cw, ch = canvas or self.canvas
        ax, ay = anchor or self.anchor
        W, H = int(cw * scale), int(ch * scale)
        surf, c = new_surface(W, H)
        c.translate(ax * scale, ay * scale)
        c.scale(scale, scale)
        P = self.pose(**p)
        # canais de corpo inteiro: rotação em torno do apoio (queda), achatamento contra parede, esticão lateral
        f = 1.0 if P.get("turn", 0) >= 0 else -1.0
        pivot_y = -self.height * P.get("rot_pivot", 0.0)
        c.translate(0, pivot_y)
        c.rotate(math.degrees(P.get("rot", 0.0)) * f)
        c.translate(0, -pivot_y)
        flat = P.get("flat", 0.0)
        stx = P.get("stretch_x", 1.0)
        if flat or stx != 1.0:
            front = f * self.height * 0.25
            c.translate(front, 0)
            c.scale(stx * (1 - 0.62 * flat), 1 + 0.22 * flat)
            c.translate(-front, 0)
        ink = Ink(c, Brush(width=6.0, jitter=jitter, seed=seed))
        self.draw(ink, P)
        return surf

    def render_png(self, p: dict[str, Any], path, scale: float = 1.5, seed: int = 0, jitter: float = 0.5, **kw) -> None:
        save_png(self.render(p, scale, seed, jitter, **kw), path)

    def render_array(self, p: dict[str, Any], scale: float = 1.5, seed: int = 0, jitter: float = 0.5) -> np.ndarray:
        return to_array(self.render(p, scale, seed, jitter))
