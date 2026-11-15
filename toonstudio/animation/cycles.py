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


# ------------------------------------------------------------------ dança no tempo da música (clipes)
GAITS["luizinho"] = {
    "walk": {"T": 0.7, "S": 64, "lift": 26, "bob": 8, "lean": 0.05, "arm": 1.0, "ex": 1},
    "sneak": {"T": 1.2, "S": 80, "lift": 46, "bob": 12, "lean": 0.15, "arm": 0.0, "ex": 1},
    "run": {"T": 0.34, "S": 150, "lift": 60, "bob": 18, "lean": 0.3, "arm": 1.0, "ex": 1},
}
GAITS["calanguinho"] = {
    "walk": {"T": 0.7, "S": 60, "lift": 22, "bob": 7, "lean": 0.08, "arm": 0.8, "ex": 1},
    "sneak": {"T": 1.2, "S": 80, "lift": 40, "bob": 10, "lean": 0.2, "arm": 0.0, "ex": 1},
    "run": {"T": 0.3, "S": 150, "lift": 50, "bob": 16, "lean": 0.4, "arm": 1.0, "ex": 1},
}

DANCES = ("bob", "cabeca", "lango", "lado", "bracos")


def beat_phase(t: float, beats: list[float]) -> tuple[int, float]:
    """(índice da batida, fração 0..1 até a próxima) na grade REAL de batidas da música."""
    import bisect
    if not beats:
        return 0, 0.0
    i = bisect.bisect_right(beats, t) - 1
    if i < 0:
        period = beats[1] - beats[0] if len(beats) > 1 else 0.5
        return -1, 1 + (t - beats[0]) / period
    nxt = beats[i + 1] if i + 1 < len(beats) else beats[i] + (beats[i] - beats[i - 1] if i else 0.5)
    return i, (t - beats[i]) / max(1e-6, nxt - beats[i])


def dance(style: str, t: float, beats: list[float], amp: float = 1.0) -> dict[str, float]:
    """Pose de dança em função da batida. `beats` = grade principal (tempo da dança, ex.: 86 BPM).
    Acentos caem NA batida (ease-out logo depois), como coreografia de verdade."""
    i, u = beat_phase(t, beats)
    hit = math.exp(-5.0 * u)                  # impulso no instante da batida, decaindo
    side = 1 if i % 2 == 0 else -1            # alterna lado a cada batida
    sway = side * (1 - 2 * u)                 # vai de um lado ao outro entre batidas (para pendular)
    smooth_side = math.cos(math.pi * (i + u))       # extremos caem NA batida
    if style == "bob":
        return {"body_y": 14 * amp * (1 - math.cos(2 * math.pi * u)) / 2 * 0 + 12 * amp * hit, "squash": 1 - 0.06 * amp * hit,
                "head_dy": 6 * amp * math.exp(-5.0 * max(0.0, u - 0.08)), "hand_n_x": 30 + 18 * side, "hand_n_y": 50 - 20 * hit,
                "hand_f_x": 30 - 18 * side, "hand_f_y": 50 - 20 * hit, "hand_n_bend": 0.7, "hand_f_bend": 0.7,
                "paw_n": 1, "paw_f": 1, "tail_wag": 0.3 * smooth_side, "foot_n_bend": 0.3 * hit, "foot_f_bend": 0.3 * hit}
    if style == "cabeca":
        return {"head_tilt": 0.26 * amp * smooth_side, "body_x": -6 * smooth_side, "lean": 0.04 * smooth_side,
                "hat_tilt": -0.12 * math.cos(math.pi * (i + u) - 0.6),     # chapéu atrasa (follow-through)
                "body_y": 8 * amp * hit, "squash": 1 - 0.04 * hit,
                "hand_n_x": 50, "hand_n_y": 34, "hand_f_x": 46, "hand_f_y": 30, "hand_n_bend": 0.75, "hand_f_bend": 0.75,
                "paw_n": 0, "paw_f": 0, "tail_wag": 0.5 * smooth_side, "look_x": 0.3 * smooth_side}
    if style == "lango":
        return {"head_dy": 16 * amp * hit, "head_tilt": 0.1 * side * hit, "body_y": 10 * amp * hit, "squash": 1 - 0.07 * hit,
                "hand_n_x": 60, "hand_n_y": 20 - 30 * hit, "hand_f_x": 55, "hand_f_y": 20 - 30 * hit, "paw_n": 3, "paw_f": 3,
                "hand_n_bend": 0.4, "hand_f_bend": 0.4, "tail_wag": 0.6 * side * hit, "hat_tilt": 0.15 * side * hit}
    if style == "lado":
        # cada batida: pulinho para o lado, braço aponta para onde vai
        # aponta com o braço DO LADO para onde vai (o outro na cintura): o braço nunca cruza o rosto.
        # braço "n" fica do lado de trás (-x em coordenadas de frente), o "f" do lado da frente (+x)
        point_n = side < 0
        base = {"body_x": 34 * amp * side * (1 - math.exp(-6 * u)) - 34 * amp * side * 0.5, "lean": 0.18 * side,
                "body_y": -18 * amp * math.sin(math.pi * min(1.0, u * 2)) if u < 0.5 else 0.0, "squash": 1 + 0.05 * hit,
                "tail_wag": -0.5 * side, "head_tilt": 0.1 * side}
        point = {"x": 120, "y": -15, "bend": 0.05, "paw": 2}
        rest = {"x": 18, "y": 52, "bend": -0.9, "paw": 1}       # mão na cintura
        pn, pf = (point, rest) if point_n else (rest, point)
        base.update({"hand_n_x": -pn["x"] if point_n else -rest["x"], "hand_n_y": pn["y"], "hand_n_bend": pn["bend"], "paw_n": pn["paw"],
                     "hand_f_x": pf["x"] if not point_n else rest["x"], "hand_f_y": pf["y"], "hand_f_bend": pf["bend"], "paw_f": pf["paw"]})
        return base
    if style == "bracos":
        up_n = 1.0 if side > 0 else 0.4
        up_f = 0.4 if side > 0 else 1.0
        # braços em "V": as mãos sobem POR FORA da cabeça (antes subiam por cima e pareciam "mão na cabeça")
        return {"hand_n_x": -105, "hand_n_y": -30 - 70 * up_n, "hand_f_x": 105, "hand_f_y": -30 - 70 * up_f,
                "paw_n": 3, "paw_f": 3, "hand_n_bend": 0.2, "hand_f_bend": 0.2, "body_y": 10 * amp * hit, "squash": 1 + 0.05 * hit,
                "head_tilt": 0.08 * smooth_side, "tail_wag": 0.4 * smooth_side}
    raise KeyError(f"dança desconhecida: {style} (disponíveis: {DANCES})")
