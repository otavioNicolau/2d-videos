"""Biblioteca de animações reutilizáveis.

Cada ação recebe o estado atual (x, y, turn…) e parâmetros, e devolve:
  keys: [(dt, {canais}, easing)]  — chaves relativas ao início da ação (antecipação, exagero, assentamento)
  cycle: (estilo, período) opcional — ciclo procedural sobreposto durante a ação
  dur, ex — duração e exposição (1 = um desenho por quadro em ação rápida; 2 = desenhos em "2s")
Variações saem dos parâmetros (intensidade, distância, alvo, estilo).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable

from ..characters.base import expression
from . import cycles


@dataclass
class ActionResult:
    keys: list[tuple[float, dict[str, Any], str]] = field(default_factory=list)
    cycle: tuple[str, float] | None = None       # ("walk"|"sneak"|"run"|"flap", período)
    dur: float = 0.0
    ex: int | None = None
    end_state: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionDef:
    name: str
    category: str
    description: str
    params: dict[str, str]
    fn: Callable[[str, dict, dict], ActionResult]


REGISTRY: dict[str, ActionDef] = {}


def action(name: str, category: str, description: str, params: dict[str, str] | None = None):
    def deco(fn):
        REGISTRY[name] = ActionDef(name, category, description, params or {}, fn)
        return fn
    return deco


def _face(name: str, amount: float = 1.0) -> dict[str, float]:
    return expression(name, amount)


# ------------------------------------------------------------------ locomoção
def _travel(char: str, st: dict, a: dict, style: str) -> ActionResult:
    x0 = st["x"]
    to_x = float(a["to_x"])
    d = to_x - x0
    sgn = 1 if d >= 0 else -1
    v = cycles.speed(char, style) * float(a.get("speed", 1.0))
    dur = float(a.get("dur", abs(d) / v if v else 1.0))
    turn = float(a.get("turn", sgn * (0.8 if style != "run" else 0.95)))
    g = cycles.GAITS[char][style]
    T = g["T"] * (abs(d) / dur / cycles.speed(char, style)) ** -1 if dur > 0 and d else g["T"]
    keys = [(0.0, {"x": x0, "turn": turn}, "step"), (dur, {"x": to_x}, "linear")]
    # assentamento ao parar (desaceleração + inclinação de volta)
    if a.get("settle", True):
        keys += [(dur + 0.12, {"lean": -0.06 if style != "run" else -0.2, "squash": 0.96}, "out"),
                 (dur + 0.4, {"lean": 0.0, "squash": 1.0}, "inout")]
    return ActionResult(keys=keys, cycle=(style, T), dur=dur, ex=int(a.get("ex", g["ex"])),
                        end_state={"x": to_x, "turn": turn})


@action("walk", "basic", "Caminhada (ciclo procedural com pé plantado).", {"to_x": "destino x", "speed": "fator"})
def walk(char, st, a):
    return _travel(char, st, a, "walk")


@action("sneak", "basic", "Pé-ante-pé exagerado, joelhos altos, mãos à frente.", {"to_x": "destino x"})
def sneak(char, st, a):
    return _travel(char, st, a, "sneak")


@action("run", "basic", "Corrida com fases no ar, braços bombeando, linhas de velocidade.", {"to_x": "destino x"})
def run(char, st, a):
    return _travel(char, st, a, "run")


@action("fly", "basic", "Voo batendo asas até (to_x, to_y) — só personagens alados.", {"to_x": "x", "to_y": "y", "dur": "s"})
def fly(char, st, a):
    dur = float(a.get("dur", 1.0))
    to_x, to_y = float(a.get("to_x", st["x"])), float(a.get("to_y", st["y"]))
    sgn = 1 if to_x >= st["x"] else -1
    keys = [(0.0, {"x": st["x"], "y": st["y"], "turn": sgn * 0.9, "lean": 0.25}, "step"),
            (dur, {"x": to_x, "y": to_y}, a.get("ease", "inout"))]
    if a.get("land", True):
        keys += [(dur + 0.08, {"squash": 0.8, "lean": 0.0}, "out"), (dur + 0.3, {"squash": 1.0}, "back")]
    return ActionResult(keys=keys, cycle=("flap", 0.22), dur=dur, ex=1, end_state={"x": to_x, "y": to_y, "turn": sgn * 0.9})


@action("jump", "basic", "Pulo com agachamento, esticão, arco e aterrissagem.", {"to_x": "x", "to_y": "y", "height": "u", "dur": "s"})
def jump(char, st, a):
    x0, y0 = st["x"], st["y"]
    to_x, to_y = float(a.get("to_x", x0)), float(a.get("to_y", y0))
    h = float(a.get("height", 200))
    dur = float(a.get("dur", 0.7))
    c = 0.2
    keys = [(0.0, {"x": x0, "y": y0}, "step"),
            (c, {"squash": 0.72, "body_y": 22, "lean": 0.2, "hand_n_y": 40, "hand_f_y": 40}, "out"),
            (c + 0.08, {"squash": 1.3, "body_y": 0, "lean": 0.1, "hand_n_y": -60, "hand_f_y": -60, "y": y0 - h * 0.35}, "out"),
            (c + dur * 0.5, {"y": min(y0, to_y) - h, "x": (x0 + to_x) / 2, "squash": 1.05}, "out"),
            (c + dur, {"y": to_y, "x": to_x, "squash": 1.22}, "in"),
            (c + dur + 0.06, {"squash": 0.7, "body_y": 18, "hand_n_y": 120, "hand_f_y": 120}, "out"),
            (c + dur + 0.3, {"squash": 1.0, "body_y": 0, "lean": 0.0}, "back")]
    return ActionResult(keys=keys, dur=c + dur + 0.3, ex=1, end_state={"x": to_x, "y": to_y})


@action("turn", "basic", "Virar para o outro lado com antecipação.", {"to": "turn final (-1..1)"})
def turn(char, st, a):
    to = float(a["to"])
    keys = [(0.0, {"squash": 1.0}, "step"), (0.08, {"squash": 0.9, "body_y": 6}, "out"),
            (0.16, {"turn": to, "squash": 1.08, "body_y": -6}, "step"), (0.36, {"squash": 1.0, "body_y": 0}, "back")]
    return ActionResult(keys=keys, dur=0.36, ex=1, end_state={"turn": to})


@action("look_around", "basic", "Olhar desconfiado para um lado e para o outro.", {"dur": "s"})
def look_around(char, st, a):
    d = float(a.get("dur", 1.6))
    keys = [(0.0, {"look_x": 0.0, "head_turn": 0.0}, "step"), (d * 0.15, {"look_x": -1.0, "head_turn": -0.3}, "out"),
            (d * 0.45, {"look_x": -1.0, "head_turn": -0.3}, "linear"), (d * 0.6, {"look_x": 1.0, "head_turn": 0.25}, "inout"),
            (d * 0.85, {"look_x": 1.0, "head_turn": 0.25}, "linear"), (d, {"look_x": 0.0, "head_turn": 0.0}, "inout")]
    return ActionResult(keys=keys, dur=d)


@action("sit", "basic", "Sentar (agacha com peso, acomoda).", {})
def sit(char, st, a):
    keys = [(0.0, {}, "step"), (0.25, {"body_y": 55, "squash": 0.82, "foot_n_x": 45, "foot_f_x": 55, "foot_n_bend": 0.6,
                                       "foot_f_bend": 0.6, "lean": -0.06}, "out"),
            (0.45, {"body_y": 50, "squash": 0.9}, "back")]
    return ActionResult(keys=keys, dur=0.45)


@action("stand", "basic", "Levantar.", {})
def stand(char, st, a):
    keys = [(0.0, {}, "step"), (0.15, {"body_y": 60, "squash": 0.78}, "out"),
            (0.4, {"body_y": 0, "squash": 1.0, "foot_n_x": -10, "foot_f_x": 12, "foot_n_bend": -0.05, "foot_f_bend": -0.05,
                   "lean": 0.0}, "back")]
    return ActionResult(keys=keys, dur=0.4)


# ------------------------------------------------------------------ comédia física
@action("take", "comedy", "Reação de susto/choque: antecipação, esticão com olhos esbugalhados, assentamento.",
        {"strength": "surprised|shock"})
def take(char, st, a):
    strong = a.get("strength", "shock") == "shock"
    peak = _face("shock" if strong else "surprised")
    keys = [(0.0, {**_face("neutral"), "lid": 0.55, "squash": 0.86, "body_y": 14, "ear": 0.0}, "out"),
            (0.12, {**peak, "squash": 1.42 if strong else 1.2, "body_y": -42 if strong else -20, "ear": -1.1,
                    "hand_n_y": -40, "hand_f_y": -40, "hand_n_x": -40, "hand_f_x": 40, "paw_n": 3, "paw_f": 3,
                    "crest": 1.0}, "out"),
            (0.26, {"squash": 0.9, "body_y": 6}, "inout"),
            (0.42, {**_face("surprised"), "squash": 1.06, "body_y": -6, "ear": -0.4}, "inout"),
            (0.62, {"squash": 1.0, "body_y": 0, "ear": 0.0, "hand_n_y": 100, "hand_f_y": 100, "paw_n": 0, "paw_f": 0,
                    "crest": 0.3}, "inout")]
    return ActionResult(keys=keys, dur=0.62, ex=1)


@action("crash", "comedy", "Bate de cara num obstáculo à frente: achata, tremida, estrelinhas, cai de costas.",
        {"wall_x": "x do contato", "fall": "true/false"})
def crash(char, st, a):
    impact = {"flat": 1.0, **_face("shock"), "lid": 0.0, "jaw": 0.6, "ear": -0.8, "speed": 0.0, "lean": 0.0,
              "head_tilt": 0.0, "body_y": 0.0, "squash": 1.0, "rot": 0.0,
              "hand_n_x": 60, "hand_n_y": -30, "hand_f_x": 70, "hand_f_y": -40, "paw_n": 3, "paw_f": 3,
              "foot_n_x": 10, "foot_n_y": 0, "foot_f_x": 20, "foot_f_y": 0}
    if "surface_x" in a:
        # contato de verdade: mede no próprio desenho até onde vai o focinho na pose de impacto
        turn = st.get("pose", {}).get("turn", st.get("turn", 0.95))
        f = 1 if turn >= 0 else -1
        reach = _reach(char, {**st.get("pose", {}), **impact, "turn": turn}, f)
        wx = float(a["surface_x"]) - f * (reach - 4)
    else:
        wx = float(a.get("wall_x", st["x"]))
    keys = [(0.0, {"x": st["x"], "flat": 0.0}, "step"),
            (0.06, {"x": wx, **impact}, "step"),
            (0.5, {"flat": 0.92, "stars": 0.4}, "linear"),
            (0.62, {"flat": 0.2, **_face("dizzy"), "stars": 0.7}, "out")]
    dur = 0.62
    if a.get("fall", True):
        keys += [(dur + 0.42, {"rot": -1.5, "rot_pivot": 0.0, "stars": 1.4, "flat": 0.0, "hand_n_y": -80, "hand_f_y": -90,
                               "foot_n_x": 60, "foot_f_x": 40}, "in"),
                 (dur + 0.5, {"rot": -1.38, "squash": 0.85}, "out"),
                 (dur + 0.62, {"rot": -1.52, "squash": 1.0, "stars": 2.0}, "inout"),
                 (dur + 1.6, {"stars": 4.0}, "linear")]
        dur += 1.6
    return ActionResult(keys=keys, dur=dur, ex=1)


@action("fall", "comedy", "Queda exagerada: estica caindo, panqueca no chão, quica e assenta.",
        {"to_y": "y do chão", "dur": "s (tempo de queda)"})
def fall(char, st, a):
    y0 = st["y"]
    to_y = float(a["to_y"])
    d = float(a.get("dur", 0.6))
    keys = [(0.0, {"y": y0, "squash": 1.0}, "step"),
            (0.25, {"y": y0, **_face("scared"), "squash": 1.15, "hand_n_y": -90, "hand_f_y": -95, "ear": -1.2,
                    "paw_n": 3, "paw_f": 3, "foot_n_y": -20}, "out"),          # "pendurado" no ar um instante
            (0.25 + d, {"y": to_y, "squash": 1.5, "ear": -1.5}, "in"),
            (0.25 + d + 0.05, {"squash": 0.42, "body_y": 10, **_face("shock"), "jaw": 0.4, "hand_n_y": 40, "hand_f_y": 40,
                               "foot_n_y": 0}, "step"),
            (0.25 + d + 0.55, {"squash": 0.45, "stars": 1.0}, "linear"),
            (0.25 + d + 0.75, {"squash": 1.15, **_face("dizzy"), "body_y": 0}, "out"),
            (0.25 + d + 1.05, {"squash": 1.0, "stars": 2.5, "ear": 0.0}, "elastic")]
    return ActionResult(keys=keys, dur=0.25 + d + 1.05, ex=1, end_state={"y": to_y})


@action("slip", "comedy", "Escorrega: pés para a frente, corpo no ar, cai sentado.", {})
def slip(char, st, a):
    keys = [(0.0, {}, "step"),
            (0.1, {"foot_n_x": 120, "foot_n_y": -80, "foot_f_x": 90, "foot_f_y": -60, "rot": -0.6, "body_y": -40,
                   **_face("shock"), "hand_n_y": -60, "hand_f_y": -70, "paw_n": 3, "paw_f": 3}, "out"),
            (0.35, {"rot": -0.9, "body_y": -60}, "out"),
            (0.55, {"rot": -0.25, "body_y": 50, "squash": 0.7, "foot_n_y": 0, "foot_f_y": 0}, "in"),
            (0.8, {"rot": -0.15, "squash": 0.9, **_face("dizzy")}, "back")]
    return ActionResult(keys=keys, dur=0.8, ex=1)


@action("bounce", "comedy", "Quicar no chão (após queda).", {"times": "n"})
def bounce(char, st, a):
    n = int(a.get("times", 2))
    keys, t, h = [(0.0, {"y": st["y"]}, "step")], 0.0, float(a.get("height", 120))
    for i in range(n):
        keys += [(t + 0.18, {"y": st["y"] - h, "squash": 1.2}, "out"), (t + 0.36, {"y": st["y"], "squash": 0.75}, "in")]
        t += 0.36
        h *= 0.45
    keys.append((t + 0.2, {"squash": 1.0}, "back"))
    return ActionResult(keys=keys, dur=t + 0.2, ex=1)


@action("shock_reaction", "comedy", "Tremedeira de choque/raiva no lugar.", {"dur": "s"})
def shock_reaction(char, st, a):
    d = float(a.get("dur", 0.8))
    keys = [(0.0, {"body_x": 0.0}, "step")]
    n = int(d / 0.05)
    for i in range(1, n + 1):
        keys.append((i * 0.05, {"body_x": 7 * (1 if i % 2 else -1), "head_dx": 5 * (-1 if i % 2 else 1)}, "step"))
    keys.append((d + 0.05, {"body_x": 0.0, "head_dx": 0.0}, "step"))
    return ActionResult(keys=keys, dur=d + 0.05, ex=1)


# ------------------------------------------------------------------ interações
@action("grab", "interaction", "Agarrar algo à frente com antecipação e puxar para o peito.",
        {"reach_x": "u à frente do ombro", "reach_y": "u abaixo do ombro", "item": "nome do objeto"})
def grab(char, st, a):
    rx, ry = float(a.get("reach_x", 120)), float(a.get("reach_y", 60))
    item = a.get("item", "")
    keys = [(0.0, {}, "step"),
            (0.15, {"lean": -0.12, "hand_n_x": -40, "hand_n_y": 60, "paw_n": 3, "body_y": 4}, "out"),      # antecipação
            (0.27, {"lean": 0.25, "hand_n_x": rx, "hand_n_y": ry, "hand_n_bend": 0.0, "paw_n": 3}, "out"),
            (0.32, {"paw_n": 1, "holding": item}, "step"),
            (0.6, {"lean": 0.0, "hand_n_x": 62, "hand_n_y": 38, "hand_n_bend": 0.4, "paw_n": 0}, "back")]
    return ActionResult(keys=keys, dur=0.6, ex=1)


@action("point", "interaction", "Apontar para a frente.", {"dur": "s"})
def point(char, st, a):
    d = float(a.get("dur", 1.0))
    keys = [(0.0, {}, "step"), (0.1, {"hand_n_x": -20, "hand_n_y": 80, "lean": -0.05}, "out"),
            (0.22, {"hand_n_x": 150, "hand_n_y": -20, "hand_n_bend": -0.05, "paw_n": 2, "lean": 0.08}, "back"),
            (d, {"hand_n_x": 150, "hand_n_y": -18}, "linear"),
            (d + 0.25, {"hand_n_x": -34, "hand_n_y": 138, "hand_n_bend": 0.22, "paw_n": 0, "lean": 0.0}, "inout")]
    return ActionResult(keys=keys, dur=d + 0.25)


@action("shake_fist", "interaction", "Sacudir o punho fechado (ameaça).", {"dur": "s"})
def shake_fist(char, st, a):
    d = float(a.get("dur", 1.0))
    # punho erguido AO LADO da cabeça (não na frente da boca), antebraço sacudindo
    keys = [(0.0, {}, "step"), (0.06, {"hand_n_x": -10, "hand_n_y": 40, "lean": -0.04}, "out"),          # antecipação
            (0.16, {"hand_n_x": -70, "hand_n_y": -115, "hand_n_bend": -0.35, "paw_n": 1, "lean": 0.06}, "back")]
    # x negativo = para fora/para trás: o braço do lado da câmera sobe por FORA da cabeça (não cobre o rosto)
    t = 0.16
    while t < d:
        t += 0.09
        keys.append((t, {"hand_n_y": -115 + (16 if int(t / 0.09) % 2 else -8), "hand_n_x": -70 + (8 if int(t / 0.09) % 2 else -4)}, "inout"))
    keys.append((d + 0.25, {"hand_n_x": -34, "hand_n_y": 138, "hand_n_bend": 0.22, "paw_n": 0}, "inout"))
    return ActionResult(keys=keys, dur=d + 0.25, ex=1)


@action("eat", "interaction", "Comer com gosto (cabeça mergulha, mastiga).", {"dur": "s"})
def eat(char, st, a):
    d = float(a.get("dur", 1.2))
    keys = [(0.0, {}, "step")]
    t = 0.0
    i = 0
    while t < d:
        t += 0.16
        i += 1
        keys.append((t, {"mouth": "D" if i % 2 else "A", "head_dy": 10 if i % 2 else -2, "lid": 0.6 if i % 2 else 0.7,
                         "smile": 0.9}, "step"))
    return ActionResult(keys=keys, dur=d, ex=2)


@action("laugh", "expression", "Gargalhada: corpo quica, cabeça para trás.", {"dur": "s"})
def laugh(char, st, a):
    d = float(a.get("dur", 1.2))
    keys = [(0.0, {**_face("laughing"), "mouth": "D"}, "out")]
    t, i = 0.0, 0
    while t < d:
        t += 0.12
        i += 1
        keys.append((t, {"body_y": -10 if i % 2 else 4, "squash": 1.05 if i % 2 else 0.95, "head_tilt": -0.12 if i % 2 else -0.05,
                         "mouth": "D" if i % 2 else "C"}, "inout"))
    keys.append((d + 0.2, {"body_y": 0, "squash": 1.0, "head_tilt": 0.0}, "inout"))
    return ActionResult(keys=keys, dur=d + 0.2, ex=2)


def _reach(char_id: str, pose: dict, f: int) -> float:
    """Distância (unidades) do ponto de apoio até a borda do desenho na direção do olhar."""
    import numpy as np
    from ..core.registry import character
    ch = character(char_id)
    sc = 0.5
    a = ch.render_array(pose, scale=sc, jitter=0.0)[..., 3]
    cols = np.where(a.max(axis=0) > 40)[0]
    if not len(cols):
        return 0.0
    edge = cols[-1] if f > 0 else cols[0]
    return abs(edge / sc - ch.anchor[0])


def catalog() -> list[dict]:
    """Catálogo da biblioteca (para validação, IA e interface)."""
    from ..characters.base import EXPRESSIONS
    out = [{"name": d.name, "category": d.category, "description": d.description, "params": d.params}
           for d in REGISTRY.values()]
    out += [{"name": f"expr:{e}", "category": "expression", "description": f"expressão facial {e}", "params": {}}
            for e in EXPRESSIONS]
    return out
