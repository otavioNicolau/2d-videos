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


def gaits(char: str) -> dict:
    """Parâmetros de andar do personagem (crianças da turma usam o padrão infantil)."""
    return GAITS.get(char, GAITS["luizinho"])


def speed(char: str, style: str) -> float:
    g = gaits(char)[style]
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
    g = gaits(char)[style]
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


def voo(t: float, T: float = 0.12) -> dict[str, float]:
    """Voo das muriçocas: asas zumbindo (3 poses), perninhas penduradas balançando, braços abertos, corpo flutuando."""
    u = math.sin(TAU * t / (T * 6))
    return {"fly": 1.0, "wing_phase": (t / T) % 1.0, "dangle": 0.35 + 0.25 * u,
            "hand_n_x": -95, "hand_n_y": -10 + 12 * u, "hand_n_bend": 0.4, "paw_n": 3,
            "hand_f_x": 95, "hand_f_y": -10 - 12 * u, "hand_f_bend": -0.4, "paw_f": 3, "body_y": 5 * u}


# ------------------------------------------------------------------ dança no tempo da música (clipes)
GAITS["luizinho"] = {
    "walk": {"T": 0.7, "S": 64, "lift": 26, "bob": 8, "lean": 0.05, "arm": 1.0, "ex": 1},
    "sneak": {"T": 1.2, "S": 80, "lift": 46, "bob": 12, "lean": 0.15, "arm": 0.0, "ex": 1},
    "run": {"T": 0.34, "S": 150, "lift": 60, "bob": 18, "lean": 0.3, "arm": 1.0, "ex": 1},
}
GAITS["laurinha"] = GAITS["luizinho"]
GAITS["calanguinho"] = {
    "walk": {"T": 0.7, "S": 60, "lift": 22, "bob": 7, "lean": 0.08, "arm": 0.8, "ex": 1},
    "sneak": {"T": 1.2, "S": 80, "lift": 40, "bob": 10, "lean": 0.2, "arm": 0.0, "ex": 1},
    "run": {"T": 0.3, "S": 150, "lift": 50, "bob": 16, "lean": 0.4, "arm": 1.0, "ex": 1},
}

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


# ------------------------------------------------------------------ coreografia (passos em batidas)
# Cada passo: (duração em batidas, [(posição em batidas, pose)]). As poses são interpoladas por curva suave cíclica
# (Catmull-Rom): movimento contínuo com arcos, sem "pausa" entre batidas. Chaves com "+" SOMAM ao canal base
# (ex.: "turn+" gira o corpo em torno da direção definida na cena). Mãos em coordenadas "para a frente".
# braços em V: cotovelo para FORA (o braço sobe por fora da cabeça grande, nunca cruza o rosto)
_ARM_V_N = {"hand_n_x": -128, "hand_n_y": -82, "hand_n_bend": 0.5, "paw_n": 3}
_ARM_V_F = {"hand_f_x": 128, "hand_f_y": -82, "hand_f_bend": -0.5, "paw_f": 3}
CHOREO: dict[str, tuple[float, list[tuple[float, dict]]]] = {
    # balanço lateral (A1, 19/11 — "os braços estão estranhos"): peso de um pé para o outro, tronco quase de frente;
    # braços SEMPRE por fora do corpo, abertos, balançando juntos para o lado do peso (nunca cruzam a barriga)
    "balanco": (2, [
        (0.0, {"body_x": -30, "body_y": 8, "lean": -0.12, "turn+": -0.12, "head_tilt": 0.18, "squash": 0.975,
               "hand_n_x": -132, "hand_n_y": -28, "hand_n_bend": 0.45, "paw_n": 3, "hand_f_x": 96, "hand_f_y": 48,
               "hand_f_bend": -0.35, "paw_f": 3, "foot_n_bend": 0.4, "foot_f_bend": 0.08, "foot_f_y": -10, "tail_wag": -0.5}),
        (0.5, {"body_x": 0, "body_y": -6, "lean": 0.0, "turn+": 0.0, "head_tilt": 0.0, "squash": 1.02,
               "hand_n_x": -104, "hand_n_y": 22, "hand_n_bend": 0.35, "hand_f_x": 104, "hand_f_y": 22, "hand_f_bend": -0.35,
               "foot_n_bend": 0.1, "foot_f_bend": 0.1, "foot_f_y": 0, "foot_n_y": 0, "tail_wag": 0}),
        (1.0, {"body_x": 30, "body_y": 8, "lean": 0.12, "turn+": 0.12, "head_tilt": -0.18, "squash": 0.975,
               "hand_n_x": -96, "hand_n_y": 48, "hand_n_bend": 0.35, "paw_n": 3, "hand_f_x": 132, "hand_f_y": -28,
               "hand_f_bend": -0.45, "paw_f": 3, "foot_n_bend": 0.08, "foot_f_bend": 0.4, "foot_n_y": -10, "tail_wag": 0.5}),
        (1.5, {"body_x": 0, "body_y": -6, "lean": 0.0, "turn+": 0.0, "head_tilt": 0.0, "squash": 1.02,
               "hand_n_x": -104, "hand_n_y": 22, "hand_n_bend": 0.35, "hand_f_x": 104, "hand_f_y": 22, "hand_f_bend": -0.35,
               "foot_n_bend": 0.1, "foot_f_bend": 0.1, "foot_f_y": 0, "foot_n_y": 0, "tail_wag": 0}),
    ]),
    # palmas no tempo: mãos se encontram NA batida (com o corpo descendo), abrem entre as batidas
    "palmas": (1, [
        (0.0, {"hand_n_x": 38, "hand_n_y": 8, "hand_f_x": 38, "hand_f_y": 8, "hand_n_bend": 0.7, "hand_f_bend": 0.7,
               "paw_n": 3, "paw_f": 3, "body_y": 5, "squash": 0.976, "head_tilt": 0.06, "head_dy": 4}),
        (0.5, {"hand_n_x": -75, "hand_n_y": -10, "hand_f_x": 120, "hand_f_y": -10, "hand_n_bend": 0.2, "hand_f_bend": 0.2,
               "body_y": -5, "squash": 1.018, "head_tilt": -0.06, "head_dy": -2}),
    ]),
    # pulinho: agacha (antecipação), sobe esticado com braços em V, aterrissa amassado, quica
    "pulinho": (2, [
        (0.0, {"body_y": 34, "squash": 0.8, "foot_n_y": 0, "foot_f_y": 0, "foot_n_bend": 0.6, "foot_f_bend": 0.6,
               "hand_n_x": -30, "hand_n_y": 95, "hand_f_x": 30, "hand_f_y": 95, "paw_n": 0, "paw_f": 0, "head_dy": 10}),
        (0.35, {"body_y": -95, "squash": 1.18, "foot_n_y": -70, "foot_f_y": -62, "foot_n_bend": 0.7, "foot_f_bend": 0.7,
                **_ARM_V_N, **_ARM_V_F, "head_dy": -6}),
        (0.75, {"body_y": 26, "squash": 0.84, "foot_n_y": 0, "foot_f_y": 0, "foot_n_bend": 0.5, "foot_f_bend": 0.5,
                "hand_n_x": -80, "hand_n_y": 30, "hand_f_x": 80, "hand_f_y": 30, "paw_n": 3, "paw_f": 3, "head_dy": 12}),
        (1.2, {"body_y": -18, "squash": 1.05, "foot_n_bend": 0.1, "foot_f_bend": 0.1, "hand_n_x": -60, "hand_n_y": 10,
               "hand_f_x": 60, "hand_f_y": 10, "head_dy": -3}),
        (1.6, {"body_y": 6, "squash": 0.98, "hand_n_x": -40, "hand_n_y": 60, "hand_f_x": 40, "hand_f_y": 60, "head_dy": 3}),
    ]),
    # passinho (step-touch): pisa para um lado, o outro pé encosta; braços balançam junto
    "passinho": (2, [
        (0.0, {"body_x": 30, "body_y": 5, "lean": 0.1, "turn+": 0.2, "foot_f_x": 62, "foot_n_x": 20, "foot_n_y": -8,
               "foot_f_y": 0, "hand_n_x": 30, "hand_n_y": 20, "hand_f_x": 110, "hand_f_y": 0, "paw_n": 1, "paw_f": 3,
               "head_tilt": -0.12}),
        (0.5, {"body_x": 10, "body_y": -3, "lean": 0.0, "turn+": 0.0, "foot_f_x": 30, "foot_n_x": -10, "foot_n_y": -22,
               "hand_n_x": 0, "hand_n_y": 40, "hand_f_x": 40, "hand_f_y": 40, "head_tilt": 0.0}),
        (1.0, {"body_x": -30, "body_y": 5, "lean": -0.1, "turn+": -0.2, "foot_n_x": -62, "foot_f_x": -20, "foot_f_y": -8,
               "foot_n_y": 0, "hand_n_x": -110, "hand_n_y": 0, "hand_f_x": -30, "hand_f_y": 20, "paw_n": 3, "paw_f": 1,
               "head_tilt": 0.12}),
        (1.5, {"body_x": -10, "body_y": -3, "lean": 0.0, "turn+": 0.0, "foot_n_x": -30, "foot_f_x": 10, "foot_f_y": -22,
               "hand_n_x": -40, "hand_n_y": 40, "hand_f_x": 0, "hand_f_y": 40, "head_tilt": 0.0}),
    ]),
    # cabeça balançando (com o corpo em contraponto e joelhos marcando)
    "cabeca": (2, [
        (0.0, {"head_tilt": 0.34, "head_dx": -12, "body_x": 14, "body_y": 5, "lean": -0.05, "turn+": 0.12, "squash": 0.982,
               "hand_n_x": 45, "hand_n_y": 30, "hand_f_x": 70, "hand_f_y": 20, "hand_n_bend": 0.8, "hand_f_bend": 0.8,
               "paw_n": 1, "paw_f": 1, "hat_tilt": -0.18, "tail_wag": 0.5}),
        (0.5, {"head_tilt": 0.0, "head_dx": 0, "body_x": 0, "body_y": -2, "lean": 0.0, "turn+": 0.0, "squash": 1.01,
               "hand_n_x": 30, "hand_n_y": 40, "hand_f_x": 55, "hand_f_y": 36, "hat_tilt": 0.05, "tail_wag": 0}),
        (1.0, {"head_tilt": -0.34, "head_dx": 12, "body_x": -14, "body_y": 5, "lean": 0.05, "turn+": -0.12, "squash": 0.982,
               "hand_n_x": 20, "hand_n_y": 20, "hand_f_x": 45, "hand_f_y": 30, "hat_tilt": 0.18, "tail_wag": -0.5}),
        (1.5, {"head_tilt": 0.0, "head_dx": 0, "body_x": 0, "body_y": -2, "lean": 0.0, "turn+": 0.0, "squash": 1.01,
               "hand_n_x": 30, "hand_n_y": 40, "hand_f_x": 55, "hand_f_y": 36, "hat_tilt": -0.05, "tail_wag": 0}),
    ]),
    # "lango, lango": cabeça e corpo dão um tranco para a frente em cada batida, braços pistão
    "lango": (1, [
        (0.0, {"head_dy": 10, "head_dx": 14, "head_tilt": 0.08, "body_y": 6, "lean": 0.1, "squash": 0.965,
               "hand_n_x": 70, "hand_n_y": 5, "hand_f_x": 85, "hand_f_y": 0, "hand_n_bend": 0.4, "hand_f_bend": 0.4,
               "paw_n": 3, "paw_f": 3, "hat_tilt": 0.15, "tail_wag": 0.4}),
        (0.5, {"head_dy": -4, "head_dx": -4, "head_tilt": -0.04, "body_y": -3, "lean": -0.04, "squash": 1.018,
               "hand_n_x": 20, "hand_n_y": 45, "hand_f_x": 30, "hand_f_y": 45, "hand_n_bend": 0.7, "hand_f_bend": 0.7,
               "hat_tilt": -0.08, "tail_wag": -0.4}),
    ]),
    # braços em V alternados, com o corpo girando para o lado do braço alto
    "bracos": (2, [
        (0.0, {**_ARM_V_N, "hand_f_x": 90, "hand_f_y": -20, "hand_f_bend": 0.3, "paw_f": 3, "body_y": 5, "turn+": -0.22,
               "head_tilt": 0.15, "squash": 0.982, "lean": -0.06}),
        (0.5, {"hand_n_x": -100, "hand_n_y": -50, "hand_f_x": 100, "hand_f_y": -50, "body_y": -3, "turn+": 0.0,
               "head_tilt": 0.0, "squash": 1.014, "lean": 0.0}),
        (1.0, {"hand_n_x": -90, "hand_n_y": -20, "hand_n_bend": 0.3, "paw_n": 3, **_ARM_V_F, "body_y": 5, "turn+": 0.22,
               "head_tilt": -0.15, "squash": 0.982, "lean": 0.06}),
        (1.5, {"hand_n_x": -100, "hand_n_y": -50, "hand_f_x": 100, "hand_f_y": -50, "body_y": -3, "turn+": 0.0,
               "head_tilt": 0.0, "squash": 1.014, "lean": 0.0}),
    ]),
    # "vai pro lado" (A1, 19/11): passo lateral; o braço DO LADO aponta longe (esticado, um pouco para cima) e o outro
    # abre dobrado na altura do ombro (cotovelo para fora) — nada de mão no quadril atravessando o corpo
    "lado": (2, [
        (0.0, {"body_x": -40, "body_y": 8, "lean": -0.12, "squash": 0.97, "foot_n_x": -40, "foot_n_y": 0, "foot_f_x": 10,
               "foot_f_y": 0, "hand_n_x": -150, "hand_n_y": -52, "hand_n_bend": 0.12, "paw_n": 2, "hand_f_x": 92,
               "hand_f_y": -10, "hand_f_bend": -0.6, "paw_f": 3, "turn+": -0.12, "head_tilt": 0.12}),
        (0.45, {"body_x": 0, "body_y": -12, "lean": 0.0, "squash": 1.03, "foot_n_x": -14, "foot_f_x": 16, "foot_n_y": -12,
                "foot_f_y": -16, "turn+": 0.0, "hand_n_x": -112, "hand_n_y": 18, "hand_n_bend": 0.35, "paw_n": 3,
                "hand_f_x": 112, "hand_f_y": 18, "hand_f_bend": -0.35, "paw_f": 3, "head_tilt": 0.0}),
        (1.0, {"body_x": 40, "body_y": 8, "lean": 0.12, "squash": 0.97, "foot_n_x": -10, "foot_n_y": 0, "foot_f_x": 40,
               "foot_f_y": 0, "hand_n_x": -92, "hand_n_y": -10, "hand_n_bend": 0.6, "paw_n": 3, "hand_f_x": 150,
               "hand_f_y": -52, "hand_f_bend": -0.12, "paw_f": 2, "turn+": 0.12, "head_tilt": -0.12}),
        (1.45, {"body_x": 0, "body_y": -12, "lean": 0.0, "squash": 1.03, "foot_n_x": -14, "foot_f_x": 16, "foot_n_y": -16,
                "foot_f_y": -12, "turn+": 0.0, "hand_n_x": -112, "hand_n_y": 18, "hand_n_bend": 0.35, "paw_n": 3,
                "hand_f_x": 112, "hand_f_y": 18, "hand_f_bend": -0.35, "paw_f": 3, "head_tilt": 0.0}),
    ]),
    # marcha: joelho alto alternado, braços em oposição
    "marcha": (2, [
        (0.0, {"foot_n_y": -55, "foot_n_x": 25, "foot_n_bend": 0.9, "foot_f_y": 0, "foot_f_bend": 0.05, "body_y": -3,
               "hand_n_x": -70, "hand_n_y": 50, "hand_f_x": 80, "hand_f_y": 10, "paw_n": 1, "paw_f": 1, "head_tilt": 0.08}),
        (0.5, {"foot_n_y": 0, "foot_n_bend": 0.1, "foot_f_y": 0, "body_y": 4, "hand_n_x": 0, "hand_n_y": 60,
               "hand_f_x": 20, "hand_f_y": 60, "head_tilt": 0.0}),
        (1.0, {"foot_f_y": -55, "foot_f_x": 35, "foot_f_bend": 0.9, "foot_n_y": 0, "foot_n_x": -10, "body_y": -3,
               "hand_n_x": 60, "hand_n_y": 10, "hand_f_x": -40, "hand_f_y": 50, "head_tilt": -0.08}),
        (1.5, {"foot_f_y": 0, "foot_f_bend": 0.1, "foot_n_y": 0, "body_y": 4, "hand_n_x": 0, "hand_n_y": 60,
               "hand_f_x": 20, "hand_f_y": 60, "head_tilt": 0.0}),
    ]),
    # rebolado/giro do tronco (twist): o corpo gira de um 3/4 ao outro, braços abertos acompanham
    "twist": (2, [
        (0.0, {"turn+": -0.55, "body_y": 5, "lean": -0.08, "hand_n_x": -100, "hand_n_y": 20, "hand_f_x": 100, "hand_f_y": 20,
               "paw_n": 3, "paw_f": 3, "head_turn": 0.2, "squash": 0.982}),
        (0.5, {"turn+": 0.0, "body_y": -2, "lean": 0.0, "head_turn": 0.0, "squash": 1.01}),
        (1.0, {"turn+": 0.55, "body_y": 5, "lean": 0.08, "head_turn": -0.2, "squash": 0.982}),
        (1.5, {"turn+": 0.0, "body_y": -2, "lean": 0.0, "head_turn": 0.0, "squash": 1.01}),
    ]),
    # ---- movimentos simples "de marionete" (como nos clipes de referência): o corpo todo gira a partir dos pés
    # gingado: balança de um lado para o outro (1 lado por batida), braços alternando, cabeça em contraponto
    "gingado": (2, [
        (0.0, {"rot": -0.11, "head_tilt": 0.12, "hand_n_x": -70, "hand_n_y": -40, "hand_f_x": 60, "hand_f_y": 50,
               "hand_n_bend": 0.4, "hand_f_bend": -0.3, "paw_n": 3, "paw_f": 0, "tail_wag": -0.4}),
        (1.0, {"rot": 0.11, "head_tilt": -0.12, "hand_n_x": -60, "hand_n_y": 50, "hand_f_x": 70, "hand_f_y": -40,
               "hand_n_bend": 0.3, "hand_f_bend": -0.4, "paw_n": 0, "paw_f": 3, "tail_wag": 0.4}),
    ]),
    # pêndulo lento: 2 batidas para cada lado, braços abertos
    # 26 (Gelatina): TREME-TREME — joelho dobrado, corpo chacoalhando de um lado para o outro a cada meia batida,
    # braços moles abertos balançando ao contrário, cabeça atrasada (como a gelatina no prato)
    "treme": (1, [
        (0.0, {"body_x": -16, "body_y": 14, "rot": -0.06, "squash": 0.96, "head_tilt": 0.10, "hand_n_x": -125, "hand_n_y": 25,
               "hand_f_x": 105, "hand_f_y": 45, "hand_n_bend": 0.6, "hand_f_bend": -0.6, "foot_n_bend": 0.35, "foot_f_bend": 0.35,
               "paw_n": 3, "paw_f": 3}),
        (0.25, {"body_x": 14, "body_y": 8, "rot": 0.06, "squash": 1.03, "head_tilt": -0.10, "hand_n_x": -105, "hand_n_y": 45,
                "hand_f_x": 125, "hand_f_y": 25}),
        (0.5, {"body_x": -14, "body_y": 14, "rot": -0.06, "squash": 0.96, "head_tilt": 0.10, "hand_n_x": -125, "hand_n_y": 25,
               "hand_f_x": 105, "hand_f_y": 45}),
        (0.75, {"body_x": 16, "body_y": 8, "rot": 0.06, "squash": 1.03, "head_tilt": -0.10, "hand_n_x": -105, "hand_n_y": 45,
                "hand_f_x": 125, "hand_f_y": 25}),
    ]),
    "pendulo": (4, [
        (0.0, {"rot": -0.14, "head_tilt": 0.1, "hand_n_x": -100, "hand_n_y": 10, "hand_f_x": 100, "hand_f_y": 10,
               "hand_n_bend": 0.3, "hand_f_bend": -0.3, "paw_n": 3, "paw_f": 3}),
        (2.0, {"rot": 0.14, "head_tilt": -0.1, "hand_n_x": -100, "hand_n_y": 10, "hand_f_x": 100, "hand_f_y": 10}),
    ]),
    # tchauzinho: o corpo balança de leve e as duas mãos acenam lado a lado na altura do rosto
    # tchau: as duas mãos abertas ao lado do rosto, fora da cabeça, balançando (storyboards ep04/ep05)
    "tchau": (1, [
        (0.0, {"rot": -0.05, "hand_n_x": -158, "hand_n_y": -92, "hand_f_x": 138, "hand_f_y": -104, "hand_n_bend": 0.5,
               "hand_f_bend": -0.5, "paw_n": 3, "paw_f": 3, "head_tilt": 0.05}),
        (0.5, {"rot": 0.05, "hand_n_x": -138, "hand_n_y": -104, "hand_f_x": 158, "hand_f_y": -92, "head_tilt": -0.05}),
    ]),
    # ---- passos das MURIÇOCAS (BIBLIA_VISUAL; ADR-0016): de frente, sem giro do corpo e sem pula-pula; ligados à letra
    # "bati as asinhas": cotovelos batendo como asinhas + asas zumbindo (3 poses de asa por batida)
    "asinhas": (1, [
        (0.0, {"hand_n_x": -60, "hand_n_y": -50, "hand_n_bend": 0.95, "paw_n": 1, "hand_f_x": 60, "hand_f_y": -50,
               "hand_f_bend": -0.95, "paw_f": 1, "buzz": 1.0, "wing_phase": 0.15, "body_y": 2, "head_tilt": 0.04}),
        (0.33, {"hand_n_x": -105, "hand_n_y": 10, "hand_f_x": 105, "hand_f_y": 10, "wing_phase": 0.5, "body_y": -2}),
        (0.66, {"hand_n_x": -70, "hand_n_y": -40, "hand_f_x": 70, "hand_f_y": -40, "wing_phase": 0.85, "body_y": 1,
                "head_tilt": -0.04}),
    ]),
    # passo de frevo com a sombrinha no alto: joelho alternado, corpo inclina para o lado do joelho
    "frevo": (2, [
        (0.0, {"foot_n_y": -34, "foot_n_bend": 0.8, "foot_f_y": 0, "lean": -0.1, "body_y": 4, "hand_n_x": -135,
               "hand_n_y": -20, "hand_n_bend": 0.5, "paw_n": 1, "hand_f_x": 115, "hand_f_y": 10, "hand_f_bend": -0.3,
               "paw_f": 3, "head_tilt": 0.08}),
        (0.5, {"foot_n_y": 0, "foot_n_bend": 0.1, "foot_f_y": 0, "lean": 0.0, "body_y": -2, "head_tilt": 0.0}),
        (1.0, {"foot_f_y": -34, "foot_f_bend": 0.8, "foot_n_y": 0, "lean": 0.1, "body_y": 4, "hand_f_x": 95,
               "hand_f_y": -30, "head_tilt": -0.08}),
        (1.5, {"foot_f_y": 0, "foot_f_bend": 0.1, "lean": 0.0, "body_y": -2, "hand_f_x": 115, "hand_f_y": 10, "head_tilt": 0.0}),
    ]),
    # agacha (2 tempos) e levanta com braços para cima (2 tempos)
    "agacha": (4, [
        (0.0, {"body_y": 0, "squash": 1.0, "hand_n_x": -55, "hand_n_y": 75, "hand_f_x": 55, "hand_f_y": 75}),
        (0.8, {"body_y": 46, "squash": 0.9, "hand_n_x": 30, "hand_n_y": 95, "hand_f_x": 30, "hand_f_y": 95, "foot_n_bend": 0.7,
               "foot_f_bend": 0.7, "paw_n": 1, "paw_f": 1}),
        (2.0, {"body_y": 46, "squash": 0.9}),
        (2.6, {"body_y": -6, "squash": 1.04, "hand_n_x": -130, "hand_n_y": -140, "hand_f_x": 130, "hand_f_y": -140,
               "foot_n_bend": 0.1, "foot_f_bend": 0.1, "paw_n": 3, "paw_f": 3}),
        (3.6, {"body_y": -6, "squash": 1.04}),
    ]),
    # passo para o lado de frente (sem girar), braços balançando junto
    "lado_frente": (2, [
        (0.0, {"body_x": -30, "body_y": 3, "lean": -0.06, "foot_n_x": -50, "foot_f_x": 0, "hand_n_x": -110, "hand_n_y": 0,
               "hand_f_x": 30, "hand_f_y": 40, "paw_n": 3, "paw_f": 1, "head_tilt": 0.08}),
        (0.5, {"body_x": 0, "body_y": -2, "lean": 0.0, "foot_n_x": -20, "foot_f_x": 20, "hand_n_x": -50, "hand_n_y": 40,
               "hand_f_x": 50, "hand_f_y": 40, "head_tilt": 0.0}),
        (1.0, {"body_x": 30, "body_y": 3, "lean": 0.06, "foot_n_x": 0, "foot_f_x": 50, "hand_n_x": -30, "hand_n_y": 40,
               "hand_f_x": 110, "hand_f_y": 0, "paw_n": 1, "paw_f": 3, "head_tilt": -0.08}),
        (1.5, {"body_x": 0, "body_y": -2, "lean": 0.0, "foot_n_x": -20, "foot_f_x": 20, "hand_n_x": -50, "hand_n_y": 40,
               "hand_f_x": 50, "hand_f_y": 40, "head_tilt": 0.0}),
    ]),
    # festa: braços em V alternando (sem girar), cabeça acompanhando
    "festa": (2, [
        (0.0, {"hand_n_x": -130, "hand_n_y": -140, "hand_n_bend": 0.5, "paw_n": 3, "hand_f_x": 70, "hand_f_y": 20,
               "hand_f_bend": -0.3, "paw_f": 3, "head_tilt": 0.1, "body_y": 3}),
        (1.0, {"hand_n_x": -70, "hand_n_y": 20, "hand_n_bend": 0.3, "hand_f_x": 130, "hand_f_y": -140, "hand_f_bend": -0.5,
               "head_tilt": -0.1, "body_y": 3}),
    ]),
    # "bate o pezinho": pisa forte alternando os pés, mãos na cintura
    "pezinho": (1, [
        (0.0, {"foot_n_y": 0, "foot_f_y": -70, "foot_f_bend": 0.8, "body_y": 4, "hand_n_x": 10, "hand_n_y": 40, "hand_n_bend": 0.9,
               "hand_f_x": 10, "hand_f_y": 40, "hand_f_bend": -0.9, "paw_n": 1, "paw_f": 1, "head_tilt": 0.06}),
        (0.5, {"foot_f_y": 0, "foot_n_y": -70, "foot_n_bend": 0.8, "foot_f_bend": 0.1, "body_y": 4, "head_tilt": -0.06}),
    ]),
    # "roda": de mãos dadas (braços abertos na horizontal), passo para o lado em sincronia
    "roda": (2, [
        (0.0, {"body_x": -26, "body_y": 3, "lean": -0.05, "hand_n_x": -150, "hand_n_y": 20, "hand_f_x": 150, "hand_f_y": 20,
               "hand_n_bend": 0.1, "hand_f_bend": -0.1, "paw_n": 1, "paw_f": 1, "foot_n_x": -40, "foot_f_x": 0}),
        (1.0, {"body_x": 26, "body_y": 3, "lean": 0.05, "foot_n_x": 0, "foot_f_x": 40}),
    ]),
    # "pra cima, pra baixo! roda, rodinha!": escova na boca sobe e desce (2 tempos) e faz rodinha (2 tempos);
    # a outra mão na cintura, o corpo marca o tempo
    "escovar": (4, [
        (0.0, {"hand_n_x": 115, "hand_n_y": -112, "hand_n_bend": 0.7, "paw_n": 1, "hand_f_x": 10, "hand_f_y": 40,
               "hand_f_bend": -0.9, "paw_f": 1, "body_y": -3, "head_tilt": 0.05, "squash": 1.01}),
        (0.5, {"hand_n_x": 115, "hand_n_y": -56, "body_y": 5, "head_tilt": -0.03, "squash": 0.985}),
        (1.0, {"hand_n_x": 115, "hand_n_y": -112, "body_y": -3, "head_tilt": 0.05, "squash": 1.01}),
        (1.5, {"hand_n_x": 115, "hand_n_y": -56, "body_y": 5, "head_tilt": -0.03, "squash": 0.985}),
        (2.0, {"hand_n_x": 140, "hand_n_y": -84, "body_y": -3, "head_tilt": 0.08, "squash": 1.01}),
        (2.5, {"hand_n_x": 115, "hand_n_y": -108, "body_y": 5, "head_tilt": 0.0, "squash": 0.985}),
        (3.0, {"hand_n_x": 90, "hand_n_y": -84, "body_y": -3, "head_tilt": -0.08, "squash": 1.01}),
        (3.5, {"hand_n_x": 115, "hand_n_y": -60, "body_y": 5, "head_tilt": 0.0, "squash": 0.985}),
    ]),
    # guitarra-escova: mão de baixo "toca" na barriga a cada meio tempo, a de cima no braço da guitarra,
    # cabeça balança no ritmo do rock, pezinho marcando
    "guitarra": (2, [
        (0.0, {"hand_n_x": 20, "hand_n_y": 40, "hand_n_bend": 0.8, "paw_n": 1, "hand_f_x": 130, "hand_f_y": -40,
               "hand_f_bend": -0.4, "paw_f": 1, "lean": -0.07, "head_tilt": 0.14, "body_y": 4, "foot_f_y": -18}),
        (0.5, {"hand_n_x": 30, "hand_n_y": 66, "lean": 0.03, "head_tilt": -0.08, "body_y": -2, "foot_f_y": 0}),
        (1.0, {"hand_n_x": 20, "hand_n_y": 40, "hand_f_y": -30, "lean": -0.07, "head_tilt": 0.14, "body_y": 4, "foot_f_y": -18}),
        (1.5, {"hand_n_x": 30, "hand_n_y": 66, "hand_f_y": -40, "lean": 0.03, "head_tilt": -0.08, "body_y": -2, "foot_f_y": 0}),
    ]),
    # ---- A3 (19/11): passos com PERNA de verdade (as pernas eram o ponto fraco: 11–12 no placar, meta 40)
    # chutinho: chuta de leve para a frente/lado alternando os pés, braços balançam em oposição
    "chute": (2, [
        (0.0, {"foot_n_x": -40, "foot_n_y": -46, "foot_n_bend": 0.15, "foot_f_x": 16, "foot_f_y": 0, "foot_f_bend": 0.35,
               "body_y": 4, "lean": 0.05, "hand_n_x": -96, "hand_n_y": 38, "hand_f_x": 126, "hand_f_y": -44, "paw_n": 3, "paw_f": 3,
               "head_tilt": 0.08}),
        (0.5, {"foot_n_x": -14, "foot_n_y": 0, "foot_n_bend": 0.3, "foot_f_x": 16, "foot_f_y": 0, "foot_f_bend": 0.3, "body_y": 10,
               "lean": 0.0, "hand_n_x": -70, "hand_n_y": 40, "hand_f_x": 70, "hand_f_y": 40, "head_tilt": 0.0}),
        (1.0, {"foot_f_x": 42, "foot_f_y": -46, "foot_f_bend": 0.15, "foot_n_x": -14, "foot_n_y": 0, "foot_n_bend": 0.35,
               "body_y": 4, "lean": -0.05, "hand_n_x": -126, "hand_n_y": -44, "hand_f_x": 96, "hand_f_y": 38, "head_tilt": -0.08}),
        (1.5, {"foot_n_x": -14, "foot_n_y": 0, "foot_n_bend": 0.3, "foot_f_x": 16, "foot_f_y": 0, "foot_f_bend": 0.3, "body_y": 10,
               "lean": 0.0, "hand_n_x": -70, "hand_n_y": 40, "hand_f_x": 70, "hand_f_y": 40, "head_tilt": 0.0}),
    ]),
    # joelhinho: sobe o joelho bem alto e a mão do mesmo lado bate no joelho (palminha no joelho)
    "joelho": (2, [
        (0.0, {"foot_n_y": -78, "foot_n_x": -4, "foot_n_bend": 1.0, "foot_f_y": 0, "foot_f_bend": 0.2, "body_y": -4,
               "hand_n_x": -78, "hand_n_y": 62, "hand_n_bend": 0.5, "hand_f_x": 120, "hand_f_y": -60, "paw_n": 0, "paw_f": 3,
               "head_tilt": 0.1, "squash": 1.02}),
        (0.5, {"foot_n_y": 0, "foot_n_x": -14, "foot_n_bend": 0.3, "foot_f_y": 0, "foot_f_bend": 0.3, "body_y": 10,
               "hand_n_x": -90, "hand_n_y": 30, "hand_f_x": 90, "hand_f_y": 30, "head_tilt": 0.0, "squash": 0.97}),
        (1.0, {"foot_f_y": -78, "foot_f_x": 6, "foot_f_bend": 1.0, "foot_n_y": 0, "foot_n_bend": 0.2, "body_y": -4,
               "hand_f_x": 78, "hand_f_y": 62, "hand_f_bend": -0.5, "hand_n_x": -120, "hand_n_y": -60, "paw_n": 3, "paw_f": 0,
               "head_tilt": -0.1, "squash": 1.02}),
        (1.5, {"foot_f_y": 0, "foot_f_x": 16, "foot_f_bend": 0.3, "foot_n_y": 0, "foot_n_bend": 0.3, "body_y": 10,
               "hand_n_x": -90, "hand_n_y": 30, "hand_f_x": 90, "hand_f_y": 30, "head_tilt": 0.0, "squash": 0.97}),
    ]),
    # sapinho: pernas abertas, agacha na batida e dá um pulinho de sapo, braços abertos de lado
    "sapinho": (2, [
        (0.0, {"foot_n_x": -58, "foot_f_x": 60, "foot_n_y": 0, "foot_f_y": 0, "foot_n_bend": 0.8, "foot_f_bend": 0.8, "body_y": 40,
               "squash": 0.86, "hand_n_x": -120, "hand_n_y": 40, "hand_f_x": 120, "hand_f_y": 40, "paw_n": 3, "paw_f": 3, "head_dy": 8}),
        (0.6, {"foot_n_x": -40, "foot_f_x": 42, "foot_n_y": -40, "foot_f_y": -40, "foot_n_bend": 0.5, "foot_f_bend": 0.5,
               "body_y": -70, "squash": 1.14, "hand_n_x": -130, "hand_n_y": -90, "hand_f_x": 130, "hand_f_y": -90, "head_dy": -6}),
        (1.0, {"foot_n_x": -58, "foot_f_x": 60, "foot_n_y": 0, "foot_f_y": 0, "foot_n_bend": 0.8, "foot_f_bend": 0.8, "body_y": 36,
               "squash": 0.88, "hand_n_x": -120, "hand_n_y": 40, "hand_f_x": 120, "hand_f_y": 40, "head_dy": 8}),
        (1.5, {"foot_n_x": -50, "foot_f_x": 52, "foot_n_bend": 0.4, "foot_f_bend": 0.4, "body_y": 8, "squash": 1.0,
               "hand_n_x": -110, "hand_n_y": 10, "hand_f_x": 110, "hand_f_y": 10, "head_dy": 0}),
    ]),
    # cintura: mãos na cintura, quadril balança de um lado para o outro e o pé do lado sobe na ponta
    "cintura": (2, [
        (0.0, {"hand_n_x": -70, "hand_n_y": 40, "hand_n_bend": 0.95, "hand_f_x": 70, "hand_f_y": 40, "hand_f_bend": -0.95,
               "paw_n": 1, "paw_f": 1, "body_x": -26, "rot": -0.06, "foot_f_y": -28, "foot_f_bend": 0.6, "foot_n_y": 0,
               "foot_n_bend": 0.2, "head_tilt": 0.14, "body_y": 4}),
        (0.5, {"body_x": 0, "rot": 0.0, "foot_f_y": 0, "foot_f_bend": 0.25, "foot_n_y": 0, "foot_n_bend": 0.25, "head_tilt": 0.0,
               "body_y": -3}),
        (1.0, {"body_x": 26, "rot": 0.06, "foot_n_y": -28, "foot_n_bend": 0.6, "foot_f_y": 0, "foot_f_bend": 0.2,
               "head_tilt": -0.14, "body_y": 4}),
        (1.5, {"body_x": 0, "rot": 0.0, "foot_f_y": 0, "foot_f_bend": 0.25, "foot_n_y": 0, "foot_n_bend": 0.25, "head_tilt": 0.0,
               "body_y": -3}),
    ]),
    # ---- 19/11: a turma TOCA (E12: teclado, bateria e sax). Usar com o objeto na mão: "segura" (e "segura_f")
    # toca_bateria: baquetas nas duas mãos, batem alternadas na caixa/tom (pancada NA batida), corpo quica
    "toca_bateria": (1, [
        (0.0, {"hand_n_x": 70, "hand_n_y": 40, "hand_n_bend": 0.5, "paw_n": 1, "hand_f_x": 95, "hand_f_y": -25,
               "hand_f_bend": -0.4, "paw_f": 1, "body_y": 6, "head_tilt": 0.08, "head_dy": 4}),
        (0.5, {"hand_n_x": 60, "hand_n_y": -25, "hand_f_x": 105, "hand_f_y": 40, "body_y": -2, "head_tilt": -0.06, "head_dy": -2}),
    ]),
    # A4 (19/11): toca_bateria_a4 — com a bateria_show e "baqueta_a4" nas duas mãos (a baqueta segue o antebraço).
    # Compasso de 4: 1 = PRATO (mão de trás no prato) + caixa; 2 = caixa; 3 = tom (mão de trás); 4 = as duas + virada no
    # contratempo. Antes de cada pancada a baqueta SOBE (preparação) e depois da pancada dá um quique (rebote).
    "toca_bateria_a4": (4, [
        (0.0, {"hand_n_x": 90, "hand_n_y": 35, "hand_n_bend": 0.4, "hand_f_x": -125, "hand_f_y": -60, "hand_f_bend": -0.4,
               "paw_n": 1, "paw_f": 1, "body_y": 7, "head_dy": 5, "head_tilt": 0.08, "lean": 0.04}),
        (0.15, {"hand_n_x": 88, "hand_n_y": 18, "hand_f_x": -120, "hand_f_y": -75, "body_y": 3, "head_dy": 2}),
        (0.5, {"hand_n_x": 128, "hand_n_y": -50, "hand_f_x": -128, "hand_f_y": -50, "body_y": -3, "head_dy": -2, "head_tilt": 0.0}),
        (1.0, {"hand_n_x": 90, "hand_n_y": 35, "hand_f_x": -128, "hand_f_y": -50, "body_y": 6, "head_dy": 4, "head_tilt": -0.06, "lean": 0.0}),
        (1.15, {"hand_n_x": 88, "hand_n_y": 18, "body_y": 3, "head_dy": 2}),
        (1.5, {"hand_n_x": 128, "hand_n_y": -50, "hand_f_x": -128, "hand_f_y": -50, "body_y": -3, "head_dy": -2, "head_tilt": 0.0}),
        (2.0, {"hand_n_x": 128, "hand_n_y": -50, "hand_f_x": -90, "hand_f_y": 35, "body_y": 7, "head_dy": 5, "head_tilt": 0.07, "lean": 0.04}),
        (2.15, {"hand_f_x": -88, "hand_f_y": 18, "body_y": 3, "head_dy": 2}),
        (2.5, {"hand_n_x": 128, "hand_n_y": -50, "hand_f_x": -128, "hand_f_y": -50, "body_y": -3, "head_dy": -2, "head_tilt": 0.0}),
        (3.0, {"hand_n_x": 90, "hand_n_y": 35, "hand_f_x": -90, "hand_f_y": 35, "body_y": 7, "head_dy": 5, "head_tilt": -0.07, "lean": 0.0}),
        (3.25, {"hand_n_x": 115, "hand_n_y": -20, "hand_f_x": -88, "hand_f_y": 12, "body_y": 2, "head_dy": 1}),
        (3.5, {"hand_n_x": 82, "hand_n_y": 0, "hand_f_x": -90, "hand_f_y": 35, "body_y": 5, "head_dy": 3}),
        (3.75, {"hand_n_x": 128, "hand_n_y": -50, "hand_f_x": -128, "hand_f_y": -50, "body_y": 0, "head_dy": 0, "lean": 0.02}),
    ]),
    # kit_a4: a própria bateria_show reage NAS MESMAS batidas do toca_bateria_a4 (usar como "dance" no objeto)
    "kit_a4": (4, [
        (0.0, {"prato": 1.0, "caixa": 1.0, "bumbo": 1.0, "tom": 0.0, "chimbal": 0.0}),
        (0.25, {"prato": 0.7, "caixa": 0.0, "bumbo": 0.0}),
        (0.5, {"chimbal": 1.0}),
        (0.75, {"chimbal": 0.0}),
        (1.0, {"prato": 0.3, "caixa": 1.0}),
        (1.25, {"prato": 0.0, "caixa": 0.0}),
        (1.5, {"chimbal": 1.0}),
        (1.75, {"chimbal": 0.0}),
        (2.0, {"tom": 1.0, "bumbo": 1.0}),
        (2.25, {"tom": 0.0, "bumbo": 0.0}),
        (2.5, {"chimbal": 1.0}),
        (2.75, {"chimbal": 0.0}),
        (3.0, {"caixa": 1.0, "tom": 1.0, "bumbo": 1.0}),
        (3.25, {"caixa": 0.0, "tom": 0.0, "bumbo": 0.0}),
        (3.5, {"tom": 1.0}),
        (3.75, {"tom": 0.0}),
    ]),
    # toca_sax: sax na boca (mão da frente no corpo do sax), balança o corpo e a cabeça vai para trás no fim da frase
    "toca_sax": (2, [
        (0.0, {"hand_n_x": 34, "hand_n_y": -20, "hand_n_bend": 0.8, "paw_n": 1, "hand_f_x": 62, "hand_f_y": 20,
               "hand_f_bend": -0.6, "paw_f": 1, "lean": -0.05, "head_tilt": 0.05, "body_y": 4, "body_x": -8}),
        (1.0, {"hand_n_x": 38, "hand_n_y": -24, "hand_f_x": 66, "hand_f_y": 14, "lean": 0.04, "head_tilt": -0.1, "body_y": -3,
               "body_x": 8}),
    ]),
    # toca_teclado: as duas mãos na frente, na altura do teclado, dedilhando (sobe/desce alternado), ombro balança
    "toca_teclado": (1, [
        (0.0, {"hand_n_x": 40, "hand_n_y": 30, "hand_n_bend": 0.6, "paw_n": 1, "hand_f_x": 95, "hand_f_y": 22,
               "hand_f_bend": -0.5, "paw_f": 1, "body_y": 4, "head_tilt": 0.07, "body_x": -5}),
        (0.5, {"hand_n_x": 48, "hand_n_y": 22, "hand_f_x": 88, "hand_f_y": 32, "body_y": -2, "head_tilt": -0.05, "body_x": 5}),
    ]),
}
ALIASES = {"bob": "balanco"}


def soma_giro(turn: float, delta: float) -> float:
    """Giro do passo de dança (canal "turn+") somado à direção da cena SEM passar do outro lado: o desenho espelha
    quando o turn troca de sinal (laço, rosto e braços pulam de lado a cada batida — usuário, 19/11)."""
    lado = 1.0 if turn >= 0 else -1.0
    return lado * max(0.0, lado * (turn + delta))
DANCE_WITH_ITEM = {"frevo", "escovar", "guitarra", "toca_bateria", "toca_sax", "toca_teclado", "toca_bateria_a4"}        # passos em que a mão que segura o objeto (sombrinha) também dança
DANCES = tuple(CHOREO) + tuple(ALIASES)
_CAT = ("paw_n", "paw_f")
_SCALE = {"body_x", "body_y", "lean", "turn+", "head_tilt", "head_dx", "head_dy", "foot_n_y", "foot_f_y", "hat_tilt", "tail_wag"}


def _filled(keys):
    """Cada chave com todos os canais do passo (valor anterior quando omitido; primeiro: o da última chave)."""
    names = []
    for _, k in keys:
        for n in k:
            if n not in names:
                names.append(n)
    full = []
    last = {}
    for _, k in reversed(keys):          # valor "antes do início" = última chave que define o canal (ciclo)
        for n in names:
            if n not in last and n in k:
                last[n] = k[n]
    prev = {n: last[n] for n in names}
    for b, k in keys:
        cur = {n: k.get(n, prev[n]) for n in names}
        full.append((b, cur))
        prev = cur
    return names, full


_FILLED = {k: (L, *_filled(keys)) for k, (L, keys) in CHOREO.items()}

# ---- ginga de base (A2, 19/11): pernas e corpo nos passos que só mexiam os braços (14 dos 22 tinham perna parada).
# Joelhos dobram e o corpo desce NA batida, o peso passa de um pé para o outro (2 batidas) e o calcanhar do pé livre
# levanta no contratempo. Só entra no canal que o passo NÃO define (o passo manda no que ele já mexe).
def _amp_perna(keys):
    vals = [kk[n] for _, kk in keys for n in kk if n in ("foot_n_x", "foot_n_y", "foot_f_x", "foot_f_y")]
    return max(vals) - min(vals) if vals else 0.0


_SEM_PERNA = {k for k, (_, names, keys) in _FILLED.items()
              if (not any(n.startswith("foot_") for n in names) or _amp_perna(keys) < 15) and k != "agacha"}   # A3: perna fraca também ganha passo
_SEM_CORPO = {k for k, (_, names, keys) in _FILLED.items()
              if "body_y" not in names or max(kk["body_y"] for _, kk in keys) - min(kk["body_y"] for _, kk in keys) < 6}
_SEM_PESO = {k for k, (_, names, _) in _FILLED.items() if not ({"body_x", "rot"} & set(names))}
# A4: o baterista toca SENTADO (sem passo nem troca de peso) e a bateria (kit_a4) não ganha ginga nenhuma
_SEM_PERNA -= {"toca_bateria_a4", "kit_a4", "treme"}   # treme: pés plantados, só o corpo chacoalha
_SEM_CORPO -= {"kit_a4"}
_SEM_PESO -= {"toca_bateria_a4", "kit_a4"}


def _ginga(style: str, pos: float, out: dict, amp: float) -> None:
    u = pos % 1.0
    dip = (0.5 + 0.5 * math.cos(TAU * u)) ** 1.6                 # 1 na batida, 0 no contratempo
    if style in _SEM_CORPO:
        out["body_y"] = out.get("body_y", 0.0) * 0.3 + (14 * dip - 4) * amp
        out["squash"] = 1 + (out.get("squash", 1.0) - 1) + (-0.03 * dip + 0.01) * amp
    if style in _SEM_PERNA:
        livre = int(math.floor(pos)) % 2                          # pé livre alterna a cada batida
        arco = math.sin(math.pi * u)
        lift = arco ** 2 * 32 * amp                               # A3: calcanhar/joelho sobe mais (22 → 32)
        passo = 20 * arco * amp                                   # A3: o pé livre sai para o lado e volta (passo de verdade)
        out["foot_n_bend"] = 0.06 + 0.3 * dip * amp + (0.35 * arco if livre == 0 else 0.0)
        out["foot_f_bend"] = 0.06 + 0.3 * dip * amp + (0.35 * arco if livre == 1 else 0.0)
        out["foot_n_y"] = -lift if livre == 0 else 0.0
        out["foot_f_y"] = -lift if livre == 1 else 0.0
        out["foot_n_x"] = -14 - (passo if livre == 0 else 0.0)
        out["foot_f_x"] = 16 + (passo if livre == 1 else 0.0)
    if style in _SEM_PESO:
        out["body_x"] = 12 * math.cos(math.pi * pos) * amp        # peso de um pé para o outro


def dance(style: str, t: float, beats: list[float], amp: float = 1.0, t0: float | None = None) -> dict[str, float]:
    """Pose de dança no instante t, presa à grade real de batidas (posição = batidas desde o início do passo)."""
    style = ALIASES.get(style, style)
    if style not in _FILLED:
        raise KeyError(f"dança desconhecida: {style} (disponíveis: {DANCES})")
    L, names, keys = _FILLED[style]
    i, u = beat_phase(t, beats)
    i0 = beat_phase(t0, beats)[0] if t0 is not None else 0
    pos = ((i - i0) + u) % L
    n = len(keys)
    bs = [b for b, _ in keys]
    k = max(j for j in range(n) if bs[j] <= pos)
    b0 = bs[k]
    b1 = bs[k + 1] if k + 1 < n else L
    s = (pos - b0) / max(1e-6, b1 - b0)
    s2, s3 = s * s, s * s * s
    out: dict[str, float] = {}
    for name in names:
        if name in _CAT:
            out[name] = keys[k][1][name]
            continue
        p0 = keys[(k - 1) % n][1][name]
        p1 = keys[k][1][name]
        p2 = keys[(k + 1) % n][1][name]
        p3 = keys[(k + 2) % n][1][name]
        # Catmull-Rom: passa pelas poses-chave com tangentes suaves (arcos, sem paradas)
        v = 0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3)
        if name in _SCALE:
            v *= amp
        elif name == "squash":
            v = 1 + (v - 1) * amp
        out[name] = v
    _ginga(style, pos, out, amp)
    return out
