"""Ações de ATUAÇÃO (ilustram a letra): segurar, beber, comer, espreguiçar, abrir a janela, pentear, guardar…

Princípio (análise da referência, ADR-0016): o personagem quase parado, com UM gesto claro por verso, de frente para a
câmera; o movimento do clipe vem do corte a cada verso e do objeto em cena. Sem pulos e sem giro do corpo.
Coordenadas das mãos como no resto da biblioteca: x positivo = para a frente do personagem; y negativo = para cima.
"""
from __future__ import annotations

from ..characters.base import expression
from .library import ActionResult, action

REST = {"hand_n_x": -55, "hand_n_y": 75, "hand_n_bend": 0.3, "paw_n": 0, "hand_f_x": 55, "hand_f_y": 75, "hand_f_bend": -0.3,
        "paw_f": 0}
HOLD_SIDE = {"hand_n_x": -110, "hand_n_y": 20, "hand_n_bend": 0.5, "paw_n": 1}       # objeto ao lado do corpo, bem visível
AT_MOUTH = {"hand_n_x": 50, "hand_n_y": -95, "hand_n_bend": 0.7, "paw_n": 1}


def _d(a, default):
    return float(a.get("dur", default))


@action("segurar", "acting", "Pega/mostra um objeto na mão (copo_leite, banana, pente, garrafinha, carrinho, sombrinha…).",
        {"item": "objeto", "pose": "lado|alto"})
def segurar(char, st, a):
    pose = dict(HOLD_SIDE)
    if a.get("pose") == "alto":
        pose.update({"hand_n_x": -70, "hand_n_y": -40})
    return ActionResult(keys=[(0.0, {"holding": a.get("item", "")}, "step"), (0.0, {}, "step"),
                              (0.25, pose, "back")], dur=0.3, ex=1)


@action("beber", "acting", "Leva o copo à boca, bebe e fica com bigodinho de leite.", {"dur": "s"})
def beber(char, st, a):
    d = _d(a, 1.6)
    return ActionResult(keys=[
        (0.0, {"holding": "copo_leite", **HOLD_SIDE}, "step"),
        (0.3, {**AT_MOUTH, "head_tilt": -0.12, "lid": 0.55, "mouth": "B"}, "inout"),
        (d * 0.75, {"head_tilt": -0.18, "lid": 0.7}, "inout"),
        (d * 0.8, {"holding": "copo_vazio", "bigode": 1.0}, "step"),
        (d, {**HOLD_SIDE, "head_tilt": 0.0, "lid": 0.0, "mouth": "X", **expression("joy")}, "back")], dur=d, ex=1)


@action("comer", "acting", "Morde a banana duas vezes e mastiga feliz.", {"dur": "s", "item": "banana"})
def comer(char, st, a):
    d = _d(a, 1.8)
    item = a.get("item", "banana")
    keys = [(0.0, {"holding": item, **HOLD_SIDE}, "step"),
            (0.25, {**AT_MOUTH, "mouth": "D"}, "inout"),
            (0.4, {"mouth": "X", "holding": f"{item}_mordida" if item == "banana" else item}, "step"),
            (0.6, {**HOLD_SIDE}, "inout")]
    t = 0.6
    while t < d - 0.15:                                    # mastiga
        t += 0.15
        keys.append((t, {"mouth": "B" if int(t / 0.15) % 2 else "X", "head_dy": 3 if int(t / 0.15) % 2 else 0}, "step"))
    keys.append((d, {"mouth": "X", "head_dy": 0, **expression("joy")}, "inout"))
    return ActionResult(keys=keys, dur=d, ex=1)


@action("espreguicar", "acting", "Acordando: braços para cima, bocejo de olhos fechados, depois sorriso.", {"dur": "s"})
def espreguicar(char, st, a):
    d = _d(a, 1.6)
    return ActionResult(keys=[
        (0.0, {}, "step"),
        (0.35, {"hand_n_x": -125, "hand_n_y": -125, "hand_n_bend": 0.4, "paw_n": 3, "hand_f_x": 125, "hand_f_y": -125,
                "hand_f_bend": -0.4, "paw_f": 3, "lid": 1.0, "mouth": "D", "squash": 1.05, "head_tilt": 0.1}, "inout"),
        (d * 0.65, {"head_tilt": -0.1, "squash": 1.06}, "inout"),
        (d, {**REST, "lid": 0.0, "mouth": "X", "squash": 1.0, "head_tilt": 0.0, **expression("joy")}, "back")], dur=d, ex=1)


@action("acordar", "acting", "Abre os olhos devagar (pisca) e sorri.", {"dur": "s"})
def acordar(char, st, a):
    d = _d(a, 1.0)
    return ActionResult(keys=[(0.0, {"lid": 1.0, "mouth": "X"}, "step"), (d * 0.4, {"lid": 0.45}, "inout"),
                              (d * 0.55, {"lid": 1.0}, "step"), (d * 0.7, {"lid": 0.0, "brow_y": 0.8}, "out"),
                              (d, {**expression("happy")}, "inout")], dur=d, ex=1)


@action("empurrar", "acting", "Empurra para a frente com as duas mãos (abrir a janela, a porta).", {"dur": "s"})
def empurrar(char, st, a):
    d = _d(a, 0.9)
    return ActionResult(keys=[
        (0.0, {}, "step"),
        (0.2, {"hand_n_x": 30, "hand_n_y": 20, "hand_f_x": 30, "hand_f_y": 20, "lean": -0.05}, "inout"),     # antecipa
        (0.4, {"hand_n_x": 125, "hand_n_y": -50, "hand_n_bend": 0.1, "paw_n": 3, "hand_f_x": 125, "hand_f_y": -50,
               "hand_f_bend": -0.1, "paw_f": 3, "lean": 0.12}, "back"),
        (d, {"lean": 0.04, **expression("joy")}, "inout")], dur=d, ex=1)


@action("ajeitar_laco", "acting", "Mão na cabeça ajeitando o laço, com carinha satisfeita.", {"dur": "s"})
def ajeitar_laco(char, st, a):
    d = _d(a, 1.4)
    keys = [(0.0, {}, "step"), (0.3, {"hand_n_x": -80, "hand_n_y": -160, "hand_n_bend": 0.6, "paw_n": 1, "head_tilt": 0.12,
                                       "eyes_happy": 1.0}, "inout")]
    t = 0.3
    while t < d - 0.3:
        t += 0.2
        keys.append((t, {"hand_n_x": -80 + (12 if int(t / 0.2) % 2 else -8)}, "inout"))
    keys.append((d, {**REST, "head_tilt": 0.0, "eyes_happy": 0.0, **expression("joy")}, "inout"))
    return ActionResult(keys=keys, dur=d, ex=1)


@action("bacana", "acting", "Pose 'bacana!': mão na cintura, outra com polegar para cima, olhinhos felizes.", {"dur": "s"})
def bacana(char, st, a):
    d = _d(a, 1.2)
    return ActionResult(keys=[(0.0, {}, "step"),
                              (0.25, {"hand_f_x": 110, "hand_f_y": -70, "hand_f_bend": -0.4, "paw_f": 1, "hand_n_x": 10,
                                      "hand_n_y": 40, "hand_n_bend": 0.9, "paw_n": 1, "eyes_happy": 1.0, "mouth": "D",
                                      "head_tilt": -0.1}, "back"),
                              (d, {"head_tilt": -0.06}, "inout")], dur=d, ex=1)


@action("pentear", "acting", "Penteia o topete/cabeça com o pente (o topete balança).", {"dur": "s"})
def pentear(char, st, a):
    d = _d(a, 1.6)
    keys = [(0.0, {"holding": "pente"}, "step"), (0.25, {"hand_n_x": -95, "hand_n_y": -150, "hand_n_bend": 0.5, "paw_n": 1}, "inout")]
    t = 0.25
    while t < d - 0.25:
        t += 0.22
        on = int(t / 0.22) % 2
        keys.append((t, {"hand_n_x": -70 if on else -110, "hand_n_y": -165 if on else -140, "hair_bounce": 1.0 if on else -1.0},
                     "inout"))
    keys.append((d, {"hand_n_x": -105, "hand_n_y": 35, "hair_bounce": 0.0, **expression("joy")}, "inout"))
    return ActionResult(keys=keys, dur=d, ex=1)


@action("puxar", "acting", "Puxa algo com as duas mãos (arrumar o lençol).", {"dur": "s"})
def puxar(char, st, a):
    d = _d(a, 1.2)
    return ActionResult(keys=[(0.0, {}, "step"),
                              (0.3, {"hand_n_x": 60, "hand_n_y": 110, "hand_f_x": 60, "hand_f_y": 110, "paw_n": 1, "paw_f": 1,
                                     "lean": 0.12}, "inout"),
                              (d * 0.8, {"hand_n_x": 20, "hand_n_y": 10, "hand_f_x": 20, "hand_f_y": 10, "lean": -0.05}, "inout"),
                              (d, {**REST, "lean": 0.0, **expression("happy")}, "back")], dur=d, ex=1)


@action("guardar", "acting", "Abaixa e solta o objeto da mão (guardar o carrinho na caixa).", {"dur": "s"})
def guardar(char, st, a):
    d = _d(a, 1.0)
    return ActionResult(keys=[(0.0, {}, "step"),
                              (0.35, {"hand_n_x": 90, "hand_n_y": 95, "hand_n_bend": 0.2, "lean": 0.15}, "inout"),
                              (0.5, {"holding": "", "paw_n": 3}, "step"),
                              (d, {**REST, "lean": 0.0, **expression("happy")}, "back")], dur=d, ex=1)


@action("por_mochila", "acting", "Põe a mochila nas costas (alças) e fica pronto.", {"dur": "s"})
def por_mochila(char, st, a):
    d = _d(a, 1.0)
    return ActionResult(keys=[(0.0, {}, "step"),
                              (0.3, {"hand_n_x": -20, "hand_n_y": -60, "hand_f_x": 20, "hand_f_y": -60, "paw_n": 1, "paw_f": 1}, "inout"),
                              (0.5, {"mochila": 1.0}, "step"),
                              (d, {"hand_n_x": -20, "hand_n_y": 0, "hand_f_x": 20, "hand_f_y": 0, **expression("joy")}, "back")],
                        dur=d, ex=1)


@action("pensar", "acting", "Mão no queixo, olhando para cima, curioso.", {"dur": "s"})
def pensar(char, st, a):
    d = _d(a, 1.4)
    return ActionResult(keys=[(0.0, {}, "step"),
                              (0.3, {"hand_n_x": 45, "hand_n_y": -70, "hand_n_bend": 0.8, "paw_n": 1, "head_tilt": 0.15,
                                     "look_y": -0.8, "look_x": 0.4, "brow_y": 0.9, "mouth": "F"}, "inout"),
                              (d, {"head_tilt": 0.2}, "inout")], dur=d, ex=1)


@action("cheguei", "acting", "Pose de chegada 'Cheguei!': braços abertos para cima, sorrisão.", {"dur": "s"})
def cheguei(char, st, a):
    d = _d(a, 1.0)
    return ActionResult(keys=[(0.0, {}, "step"),
                              (0.12, {"hand_n_x": 0, "hand_n_y": 40, "hand_f_x": 0, "hand_f_y": 40, "squash": 0.96}, "out"),
                              (0.32, {"hand_n_x": -135, "hand_n_y": -135, "hand_n_bend": 0.5, "paw_n": 3, "hand_f_x": 135,
                                      "hand_f_y": -135, "hand_f_bend": -0.5, "paw_f": 3, "squash": 1.03, **expression("joy"),
                                      "mouth": "D"}, "back"),
                              (d, {"squash": 1.0}, "inout")], dur=d, ex=1)


@action("apontar_camera", "acting", "Aponta para quem está assistindo (\"Bora, turminha!\").", {"dur": "s"})
def apontar_camera(char, st, a):
    d = _d(a, 1.0)
    return ActionResult(keys=[(0.0, {}, "step"),
                              (0.2, {"hand_f_x": 70, "hand_f_y": -30, "hand_f_bend": -0.1, "paw_f": 2, "lean": 0.06,
                                     **expression("joy"), "mouth": "D"}, "back"),
                              (d, {"lean": 0.02}, "inout")], dur=d, ex=1)
