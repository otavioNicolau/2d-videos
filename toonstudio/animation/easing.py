"""Curvas de aceleração (timing & spacing). Todas mapeiam u∈[0,1] → [0,1] (back/elastic passam do alvo)."""
from __future__ import annotations

import math


def linear(u: float) -> float:
    return u


def ease_in(u: float) -> float:            # sai devagar, chega rápido (queda)
    return u * u * u


def ease_out(u: float) -> float:           # sai rápido, chega devagar (desaceleração)
    return 1 - (1 - u) ** 3


def inout(u: float) -> float:
    return u * u * (3 - 2 * u)


def inout_strong(u: float) -> float:
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def back(u: float, s: float = 1.9) -> float:   # passa do alvo e volta (overshoot)
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def elastic(u: float) -> float:            # tremida ao assentar
    if u in (0, 1):
        return u
    return 2 ** (-9 * u) * math.sin((u * 10 - 0.75) * (2 * math.pi) / 3) + 1


def step(u: float) -> float:               # corte seco (sem intermediários)
    return 1.0 if u >= 1 else 0.0


EASES = {"linear": linear, "in": ease_in, "out": ease_out, "inout": inout, "inout2": inout_strong,
         "back": back, "elastic": elastic, "step": step}


def get(name: str):
    if name not in EASES:
        raise KeyError(f"easing desconhecido: {name} (disponíveis: {sorted(EASES)})")
    return EASES[name]
