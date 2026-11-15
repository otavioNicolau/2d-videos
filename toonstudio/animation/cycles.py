"""Ciclos procedurais (caminhada, pé-ante-pé, corrida, voo, respiração).

Cada ciclo é função da fase p∈[0,1) e devolve canais de pose. O pé de apoio recua em relação ao quadril na mesma
velocidade em que o personagem avança (pé "plantado" no chão, sem patinar): velocidade = passo / (meio período).
"""
from __future__ import annotations

import math

from .easing import inout

TAU = 2 * math.pi

# parâmetros de andar por personagem e estilo: período (s), passada (u), elevação do pé (u)
GAITS = {
    "caramelo": {
        "walk": {"T": 1.0, "S": 130, "lift": 44, "bob": 13, "lean": 0.06, "arm": 1.0, "ex": 2},
        "sneak": {"T": 1.5, "S": 140, "lift": 80, "bob": 16, "lean": 0.14, "arm": 0.0, "ex": 2},
        "run": {"T": 0.40, "S": 300, "lift": 105, "bob": 32, "lean": 0.46, "arm": 1.0, "ex": 1},
    },
    "tevico": {
        "walk": {"T": 0.6, "S": 70, "lift": 28, "bob": 7, "lean": 0.12, "arm": 1.0, "ex": 2},
        "sneak": {"T": 1.3, "S": 100, "lift": 62, "bob": 14, "lean": 0.3, "arm": 0.0, "ex": 2},
        "run": {"T": 0.26, "S": 120, "lift": 48, "bob": 14, "lean": 0.42, "arm": 1.0, "ex": 1},
    },
}


def speed(char: str, style: str) -> float:
    g = GAITS[char][style]
    return g["S"] / (0.5 * g["T"])


def _leg(p: float, S: float, lift: float, contact: float = 0.5) -> tuple[float, float]:
    """x relativo ao quadril (+ = frente) e y (negativo = levantado) de uma perna na fase p."""
    p %= 1.0
    if p < contact:
        u = p / contact
        return S / 2 - S * u, 0.0
    u = (p - contact) / (1 - contact)
    return -S / 2 + S * inout(u), -lift * math.sin(math.pi * u) ** 0.8


def gait(char: str, style: str, p: float) -> dict[str, float]:
    g = GAITS[char][style]
    S, lift, bob = g["S"], g["lift"], g["bob"]
    contact = 0.5 if style != "run" else 0.38
    nx, ny = _leg(p, S, lift, contact)
    fx, fy = _leg(p + 0.5, S, lift, contact)
    out: dict[str, float] = {"foot_n_x": nx, "foot_n_y": ny, "foot_f_x": fx, "foot_f_y": fy}
    # joelho dobra mais no ar
    out["foot_n_bend"] = 0.05 + 0.35 * (-ny / max(lift, 1))
    out["foot_f_bend"] = 0.05 + 0.35 * (-fy / max(lift, 1))
    # pé inclina: calcanhar levanta ao sair, ponta sobe ao chegar
    out["foot_n_rot"] = -0.25 * math.sin(TAU * p) * (1 if ny < 0 else 0.3)
    out["foot_f_rot"] = -0.25 * math.sin(TAU * (p + 0.5)) * (1 if fy < 0 else 0.3)
    # corpo: baixo no contato, alto na passagem (no run: no ar entre passos)
    if style == "run":
        out["body_y"] = -bob * abs(math.sin(TAU * p)) + 6
        out["squash"] = 1.0 + 0.07 * math.cos(2 * TAU * p)
    else:
        out["body_y"] = bob * math.cos(2 * TAU * p)
        out["squash"] = 1.0 - 0.025 * math.cos(2 * TAU * p)
    out["lean"] = g["lean"] + 0.03 * math.cos(2 * TAU * p)
    out["head_dy"] = 0.4 * bob * math.cos(2 * TAU * p - 0.9)     # cabeça atrasa (sobreposição)
    out["head_tilt"] = 0.03 * math.sin(TAU * p)
    # braços opostos às pernas
    a = g["arm"]
    if style == "run":
        out.update({"hand_n_x": 95 * math.sin(TAU * p + math.pi), "hand_n_y": 95 - 25 * abs(math.cos(TAU * p)),
                    "hand_n_bend": 0.55, "hand_f_x": 95 * math.sin(TAU * p), "hand_f_y": 95 - 25 * abs(math.cos(TAU * p)),
                    "hand_f_bend": 0.55, "paw_n": 1, "paw_f": 1, "speed": 0.8})
        if char == "caramelo":
            out["ear"] = 0.75 + 0.25 * math.sin(2 * TAU * p)
            out["tail"] = -0.5
            out["hand_n_y"] *= 1.35
            out["hand_f_y"] *= 1.35
        else:
            out["hand_n_y"] *= 0.7
            out["hand_f_y"] *= 0.7
            out["tail"] = 0.35
    elif style == "sneak":
        # pé-ante-pé: mãos à frente, "patinhas" erguidas, corpo encolhido e tronco que sobe e desce
        up = math.sin(TAU * p)
        out.update({"hand_n_x": 55 + 10 * up, "hand_n_y": 35 - 12 * abs(up), "hand_n_bend": 0.7, "paw_n": 0,
                    "hand_f_x": 70 - 10 * up, "hand_f_y": 30 - 12 * abs(up), "hand_f_bend": 0.7, "paw_f": 0,
                    "head_dx": 14, "head_dy": 6 + 4 * math.cos(2 * TAU * p)})
        if char == "tevico":
            out.update({"hand_n_x": 30, "hand_n_y": 18, "hand_f_x": 40, "hand_f_y": 10})
    else:
        base_n, base_f = (-34, 30) if char == "caramelo" else (-22, 22)
        out.update({"hand_n_x": base_n * 0.3 + a * fx * 1.5, "hand_f_x": base_f * 0.3 + a * nx * 1.5, "hand_n_bend": 0.3, "hand_f_bend": 0.3,
                    "hand_n_y": (138 if char == "caramelo" else 70) - abs(fx) * 0.15,
                    "hand_f_y": (138 if char == "caramelo" else 70) - abs(nx) * 0.15})
    return out


def breathe(t: float, amount: float = 1.0) -> dict[str, float]:
    """Respiração de repouso (aditiva): quem está parado nunca fica congelado."""
    ph = TAU * t / 2.6
    return {"squash": 0.012 * math.sin(ph) * amount, "body_y": -2.5 * math.sin(ph) * amount,
            "head_dy": -1.5 * math.sin(ph - 0.6) * amount}


def flap(t: float, T: float = 0.24) -> dict[str, float]:
    """Bater de asas (Tevico em voo): asas sobem e descem, pernas recolhidas."""
    ph = TAU * t / T
    up = math.sin(ph)
    return {"hand_n_x": -10, "hand_n_y": -55 * up, "hand_n_bend": -0.2 * up, "paw_n": 2,
            "hand_f_x": 10, "hand_f_y": -55 * up, "hand_f_bend": -0.2 * up, "paw_f": 2,
            "foot_n_y": -26, "foot_f_y": -22, "foot_n_x": -16, "foot_f_x": -6, "foot_n_bend": 0.6, "foot_f_bend": 0.6,
            "body_y": -6 * up, "tail": 0.25 * up, "squash": 1 + 0.04 * up}
