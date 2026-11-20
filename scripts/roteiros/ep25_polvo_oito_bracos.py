"""Roteiro verso a verso de 25 "Polvo de Oito Braços" (take v1 cortado para 2:48, Luisinho, estilo E12 com resposta do
teclado, nota 4,8) → musicas/25_polvo_oito_bracos/roteiro.json.

A turma mergulha da PRAIA (vovô, vovó e mamãe na areia) até o FUNDO DO MAR e conhece o polvo engraçado que mora na toca:
com um braço toca tambor, com outro come pão, com outro penteia o topete… CONFUSÃO! Cada "com um braço" vira tela dividida
(o polvo × a turma fazendo igual). Refrão: o ABRAÇO DE POLVO (ninguém escapa). Ponte: contagem de 1 a 8 com os braços
levantando um a um. A banda toca na praia (A4: bateria aberta). Final: o polvo dá tchau com os oito braços.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep25_polvo_oito_bracos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import LA, LU, Roteiro, call  # noqa: E402

R = Roteiro("ep25-polvo-oito-bracos", "25_polvo_oito_bracos", "luisinho")
MAR, PRAIA, COZ, BANHO, CASA, SALA = "plano_fundo_mar", "plano_praia", "plano_cozinha", "plano_banheiro", "plano_casa_frente", "plano_sala"
PALCO = PRAIA                     # 19/11: a banda toca na praia (nada de salão lilás fora de festa)
VO, VZ, MA = "vovo", "vovozinho", "mamae"


def pv(d, x=1650, y=990, depth=0.85, z=2, **canais):
    """O polvo: braços sempre ondulando (fase `onda`); canais = valor fixo ou [(t, valor), …]."""
    d = max(0.6, d)
    ks = [{"t": 0.0, "pose": {"onda": 0.0}, "ease": "step"}, {"t": round(d - 0.05, 2), "pose": {"onda": round(d * 0.75, 2)}, "ease": "linear"}]
    pose = {}
    for c, v in canais.items():
        if isinstance(v, (int, float)):
            pose[c] = float(v)
        else:
            ks += [{"t": round(t, 2), "pose": {c: float(val)}, "ease": "out"} for t, val in v]
    ks[0]["pose"].update(pose)
    # 0,83 (× desenho 0,84 = 0,7): com a escala 1,45 o polvo cortava a cabeça no alto do quadro (conferido no storyboard)
    return {"id": "polvo", "x": x, "y": y, "z": z, "depth": round(depth * 0.83, 3), "keys": sorted(ks, key=lambda k: k["t"])}


def bolinha_peixe(x, y, d, para=1):
    """peixinho atravessando a cena (vida no fundo do mar)."""
    return {"id": "peixinho", "x": x, "y": y, "z": 1, "depth": 0.45,
            "keys": [{"t": 0.0, "pose": {"x": x, "lado": float(para), "nada": 0.0}, "ease": "step"},
                     {"t": round(max(0.6, d) - 0.05, 2), "pose": {"x": x + para * 900, "nada": round(max(0.6, d) * 2, 2)}, "ease": "linear"}]}


def nadando(quem, x0, x1, t=0.0, dur=1.2, turn=None, depois="dance", estilo=None):
    a = [{"t": t, "do": "fly", "to_x": x1, "to_y": 900, "dur": dur, "land": True}]
    if depois:
        a.append({"t": round(t + dur + 0.35, 2), "do": "dance", "style": estilo or R.estilo(), "dur": "resto"})
    return {"x": x0, "y": 760, "turn": turn if turn is not None else (0.3 if x1 > x0 else -0.3), "acoes": a}


CAM_MAR = {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.08}

# ───────── intro ─────────
T = R.tempos("intro#1", [{"seg": 3.6}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1, "seg": 3.6}, {"seg": 3.0}, {"seg": 0.0}])
d = [round(t1 - t0, 2) for t0, t1, _ in T]
R.partes["intro"] = [
    {"seg": 3.6, "cenario": MAR, "camera": {"x": 900, "y": 560, "zoom": 1.15, "zoom_fim": 1.3}, "fx": ["bolhas"], "titulo": "a toca do polvo",
     "objetos": {"p": pv(d[0], x=620, y=1060, depth=0.6, lid=[(0.0, 1.0), (1.6, 0.0)], boca=[(2.2, 0.6)]), "f": bolinha_peixe(1300, 330, d[0], -1)}},
    {"linhas": 1, "cenario": MAR, "camera": {"x": 1300, "y": 520, "zoom": 1.25, "zoom_fim": 1.35}, "flash": True, "fx": ["bolhas"],
     "callout": [call(0.3, "OITO BRAÇOS!", "rosa")],
     "objetos": {"p": pv(d[1], x=1300, depth=0.95, tchau=[(0.0, 0.0), (0.5, 1.0)], boca=[(0.4, 0.8)])}},
    {"linhas": 1, "cenario": MAR, "camera": CAM_MAR, "fx": ["bolhas"],
     "objetos": {"p": pv(d[2], x=1950, depth=0.8, agita=[(0.0, 0.0), (0.6, 0.7)])},
     "atores": {LA: nadando(LA, 100, 500, dur=1.1), LU: nadando(LU, 50, 1050, t=0.2, dur=1.2)}},
    {"linhas": 1, "seg": 3.6, "cenario": PRAIA, "camera": {"x": 1300, "y": 560, "zoom": 1.1, "zoom_fim": 1.2},
     "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")], "fx": ["confete"],
     "atores": {LA: {"x": 900, "turn": 0.25, "acoes": [{"t": 0.1, "do": "jump", "dur": 0.8}, {"t": 1.0, "do": "dance", "style": "chute", "dur": "resto"}]},
                LU: {"x": 1500, "turn": -0.25, "acoes": [{"t": 0.2, "do": "jump", "dur": 0.8}, {"t": 1.1, "do": "dance", "style": "sapinho", "dur": "resto"}]}}},
    {**R.banda(PALCO, 3.0, fx=["notas"]), "titulo": "a banda na praia"},
    {**R.banda(PALCO, max(0.6, d[5]), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.2, "zoom_fim": 1.1}), "titulo": "teclado e bateria"},
]


# ───────── verso: o polvo engraçado; com um braço… (telas divididas) ─────────
def verso(key, n):
    T = R.tempos(key, [{"linhas": 1}] * 8)
    d = [round(t1 - t0, 2) for t0, t1, _ in T]
    out = [
        # Lá no fundo do mar — a turma mergulha
        {"linhas": 1, "cenario": PRAIA if n == 1 else MAR, "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15},
         "callout": [call(0.4, "TCHIBUM!" if n == 1 else "FUNDO DO MAR!", "azul")], "fx": ["bolhas"] if n == 2 else [],
         "objetos": {"o": {"id": "onda", "x": 1300, "y": 760, "z": 1, "depth": 0.8, "keys": [{"t": 0.0, "pose": {"quebra": 0.0}, "ease": "step"},
                                                                                         {"t": 1.0, "pose": {"quebra": 1.0}, "ease": "out"}]},
                     "s": {"id": "siri", "x": 250, "y": 960, "z": 3, "depth": 0.5, "keys": [{"t": 0.0, "pose": {"anda": 0.0, "aceno": 0.0}, "ease": "step"},
                                                                                         {"t": round(d[0] - 0.06, 2), "pose": {"anda": round(d[0] * 2, 1), "aceno": 1.0}, "ease": "linear"}]}} if n == 1 else
         {"f": bolinha_peixe(300, 420, d[0]), "f2": bolinha_peixe(2200, 300, d[0], -1)},
         "atores": ({VO: {"x": 2150, "turn": -0.3, "acoes": [{"t": 0.1, "do": "wave", "dur": "resto"}]},
                     VZ: {"x": 2420, "turn": -0.3, "acoes": [{"t": 0.3, "do": "laugh", "dur": "resto"}]},
                     LA: {"x": 300, "turn": 0.3, "acoes": [{"t": 0.0, "do": "run", "to_x": 700, "dur": 0.8}, {"t": 0.9, "do": "jump", "dur": "resto"}]},
                     LU: {"x": 100, "turn": 0.3, "acoes": [{"t": 0.1, "do": "run", "to_x": 1350, "dur": 0.9}, {"t": 1.1, "do": "jump", "dur": "resto"}]}}
                    if n == 1 else {LA: nadando(LA, 300, 900, dur=1.2, estilo="bracos"), LU: nadando(LU, 200, 1400, t=0.2, dur=1.3, estilo="balanco")})},
        # Mora um polvo engraçado — sai da toca
        {"linhas": 1, "cenario": MAR, "camera": {"x": 900, "y": 560, "zoom": 1.15, "zoom_fim": 1.28}, "callout": [call(0.8, "ENGRAÇADO!", "rosa")],
         "objetos": {"p": pv(d[1], x=780, y=1060, depth=0.7, boca=[(0.6, 1.0)], agita=[(0.0, 0.0), (1.0, 0.5)])},
         "atores": {LU: {"x": 1500, "turn": -0.3, "expr": "surprised", "acoes": [{"t": 0.3, "do": "shock_reaction", "dur": 1.0}, {"t": 1.4, "do": "laugh", "dur": "resto"}]}}},
        # Ele tem oito braços — conta os braços
        {"linhas": 1, "cenario": MAR, "camera": {"x": 1300, "y": 500, "zoom": 1.2, "zoom_fim": 1.3}, "callout": [call(0.4, "8 BRAÇOS!", "laranja")],
         "objetos": {"p": pv(d[2], x=1300, depth=0.95, conta=[(0.0, 0.0), (max(0.7, d[2] - 0.4), 8.0)]),
                     "n": {"id": "numero", "x": 2150, "y": 360, "z": 4, "depth": 1.0, "keys": [{"t": 0.0, "pose": {"n": 8, "pop": 0.0}, "ease": "step"},
                                                                                               {"t": 0.5, "pose": {"pop": 1.0}, "ease": "back"}]}}},
        # E nunca fica parado — agita e passeia
        {"linhas": 1, "cenario": MAR, "camera": CAM_MAR, "callout": [call(0.4, "NUNCA PARA!", "verde")], "fx": ["bolhas"],
         "objetos": {"p": {**pv(d[3], x=1600, depth=0.8, agita=0.9), "keys": pv(d[3], x=1600, depth=0.8, agita=0.9)["keys"] +
                           [{"t": 0.0, "pose": {"x": 1300}, "ease": "step"}, {"t": round(d[3] * 0.5, 2), "pose": {"x": 1900}, "ease": "inout"},
                            {"t": round(d[3] - 0.06, 2), "pose": {"x": 1500}, "ease": "inout"}]}},
         "atores": {LA: {"x": 600, "turn": 0.3, "acoes": [{"t": 0.1, "do": "look_around", "dur": "resto"}]}}},
        # Com um braço toca tambor — polvo × Luisinho na bateria
        R.dividida({"cenario": MAR, "camera": {"x": 1300, "y": 520, "zoom": 1.2, "zoom_fim": 1.3},
                    "objetos": {"p": pv(d[4], x=1350, depth=0.85, tambor=1, agita=0.3)}},
                   {k: v for k, v in R.banda(PALCO, d[4], cam={"x": 1700, "y": 560, "zoom": 1.25, "zoom_fim": 1.35}).items() if k != "seg"},
                   linhas=1, layout="vertical" if n == 1 else "diagonal", callout=[call(0.3, "TUM, TUM!", "vermelho")]),
        # Com outro come pão — polvo × Laurinha comendo pão de queijo (da 24!)
        R.dividida({"cenario": MAR, "camera": {"x": 1300, "y": 520, "zoom": 1.2, "zoom_fim": 1.3},
                    "objetos": {"p": pv(d[5], x=1250, depth=0.85, pao=1, boca=[(0.3, 1.0), (0.7, 0.0), (1.1, 1.0)])}},
                   {"cenario": COZ, "camera": {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.35},
                    "atores": {LA: {"x": 1300, "turn": 0.1, "segura": "pao_queijo", "acoes": [{"t": 0.1, "do": "comer", "item": "pao_queijo", "dur": "resto"}]}}},
                   linhas=1, layout="diagonal" if n == 1 else "vertical", callout=[call(0.3, "NHAC!", "laranja")]),
        # Com outro penteia o cabelo — polvo × Luisinho/Laurinha no banheiro
        R.dividida({"cenario": MAR, "camera": {"x": 1300, "y": 480, "zoom": 1.2, "zoom_fim": 1.3},
                    "objetos": {"p": pv(d[6], x=1300, depth=0.85, pente=1, lid=[(0.4, 1.0), (1.4, 0.0)])}},
                   {"cenario": BANHO, "camera": {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.35},
                    "atores": {(LU if n == 1 else LA): {"x": 1300, "turn": 0.1, "acoes": [{"t": 0.1, "do": "pentear", "dur": "resto"}]}}},
                   linhas=1, layout="vertical", callout=[call(0.3, "PENTEIA!", "azul")]),
        # E com os outros? Confusão! — tudo ao mesmo tempo
        {"linhas": 1, "cenario": MAR, "camera": {"x": 1300, "y": 540, "zoom": 1.05, "zoom_fim": 1.2}, "tremor": [round(d[7] * 0.55, 2)],
         "callout": [call(round(d[7] * 0.5, 2), "CONFUSÃO!", "vermelho")], "fx": ["bolhas"],
         "objetos": {"p": pv(d[7], x=1300, depth=0.9, tambor=1, pao=1, pente=1, agita=[(0.0, 0.3), (d[7] * 0.5, 1.0)], boca=[(d[7] * 0.5, 1.0)]),
                     "f": bolinha_peixe(2300, 300, d[7], -1)},
         "atores": {LA: {"x": 450, "turn": 0.3, "expr": "surprised", "acoes": [{"t": round(d[7] * 0.5, 2), "do": "shock_reaction", "dur": "resto"}]},
                    LU: {"x": 2150, "turn": -0.3, "expr": "surprised", "acoes": [{"t": round(d[7] * 0.5, 2), "do": "slip", "dur": "resto"}]}}},
    ]
    if n == 2:                                                     # 2º verso: o polvo vem VISITAR a casa da turma
        out[2] = {"linhas": 1, "cenario": SALA, "camera": {"x": 1300, "y": 520, "zoom": 1.1, "zoom_fim": 1.2}, "callout": [call(0.4, "8 BRAÇOS!", "laranja")],
                  "objetos": {"p": pv(d[2], x=1350, depth=0.85, conta=[(0.0, 0.0), (max(0.7, d[2] - 0.4), 8.0)], boca=0.5)},
                  "atores": {LA: {"x": 500, "turn": 0.3, "acoes": [{"t": 0.1, "do": "pensar", "dur": "resto"}]},
                             LU: {"x": 2150, "turn": -0.3, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}}
        out[3] = {"linhas": 1, "cenario": "plano_jardim", "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "callout": [call(0.4, "NUNCA PARA!", "verde")],
                  "objetos": {"p": {**pv(d[3], depth=0.75, agita=0.9), "keys": pv(d[3], depth=0.75, agita=0.9)["keys"] +
                                    [{"t": 0.0, "pose": {"x": 600}, "ease": "step"}, {"t": round(d[3] * 0.5, 2), "pose": {"x": 2000}, "ease": "inout"},
                                     {"t": round(d[3] - 0.06, 2), "pose": {"x": 1200}, "ease": "inout"}]},
                              "s": {"id": "sol", "x": 2250, "y": 200, "z": 0, "depth": 0.5,
                                    "keys": [{"t": 0.0, "pose": {"giro": 0.0, "boca": 0.0}, "ease": "step"}, {"t": 0.6, "pose": {"boca": 1.0}, "ease": "out"},
                                             {"t": round(d[3] - 0.06, 2), "pose": {"giro": 0.5}, "ease": "linear"}]}},
                  "atores": {LU: {"x": 300, "turn": 0.3, "acoes": [{"t": 0.0, "do": "run", "to_x": 900, "dur": 1.2}, {"t": 1.3, "do": "ofegante", "dur": "resto"}]}}}
        out[4] = {**R.banda(SALA, d[4], cam={"x": 1500, "y": 560, "zoom": 1.15, "zoom_fim": 1.25}), "linhas": 1,
                  "callout": [call(0.3, "TUM, TUM!", "vermelho")]}
        out[4].pop("seg")
        out[4]["objetos"]["p"] = pv(d[4], x=800, depth=0.75, tambor=1, boca=0.6)
        del out[4]["atores"][LA]
        out[5] = {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 560, "zoom": 1.1, "zoom_fim": 1.2}, "callout": [call(0.3, "NHAC!", "laranja")],
                  "objetos": {"m": {"id": "mesa", "x": 1300, "y": 930, "z": 1, "depth": 1.3},
                              "t": {"id": "tabuleiro", "x": 1300, "y": 618, "z": 2, "depth": 0.5,
                                    "keys": [{"t": 0.0, "pose": {"quantos": 1.0, "vapor": 1.0}, "ease": "step"}, {"t": round(d[5] - 0.1, 2), "pose": {"quantos": 0.5}, "ease": "linear"}]},
                              "p": pv(d[5], x=1750, depth=0.8, pao=1, boca=[(0.3, 1.0), (0.7, 0.0), (1.1, 1.0)])},
                  "atores": {VO: {"x": 650, "turn": 0.3, "acoes": [{"t": 0.1, "do": "entregar", "item": "pao_queijo", "dur": 1.2}, {"t": 1.4, "do": "laugh", "dur": "resto"}]}}}
        out[6] = {"linhas": 1, "cenario": BANHO, "camera": {"x": 1300, "y": 520, "zoom": 1.15, "zoom_fim": 1.25}, "callout": [call(0.3, "PENTEIA!", "azul")],
                  "objetos": {"e": {"id": "espelho", "x": 1300, "y": 640, "z": 0, "depth": 0.8,
                                    "keys": [{"t": 0.0, "pose": {"brilho": 0.0}, "ease": "step"}, {"t": 0.6, "pose": {"brilho": 1.0}, "ease": "out"}]},
                              "p": pv(d[6], x=1650, depth=0.8, pente=1, lid=[(0.4, 1.0), (1.4, 0.0)])},
                  "atores": {LA: {"x": 800, "turn": 0.3, "acoes": [{"t": 0.1, "do": "ajeitar_laco", "dur": "resto"}]}}}
        out[7] = {"linhas": 1, "cenario": SALA, "camera": {"x": 1300, "y": 540, "zoom": 1.05, "zoom_fim": 1.2}, "tremor": [round(d[7] * 0.55, 2)],
                  "callout": [call(round(d[7] * 0.5, 2), "CONFUSÃO!", "vermelho")],
                  "objetos": {"p": pv(d[7], x=1300, depth=0.9, tambor=1, pao=1, pente=1, agita=[(0.0, 0.3), (d[7] * 0.5, 1.0)], boca=[(d[7] * 0.5, 1.0)]),
                              "c": {"id": "caixa_brinquedos", "x": 2250, "y": 930, "z": 1, "depth": 0.7,
                                    "keys": [{"t": 0.0, "pose": {"carrinho": 0.0}, "ease": "step"}, {"t": round(d[7] * 0.55, 2), "pose": {"carrinho": 1.0}, "ease": "back"}]}},
                  "atores": {MA: {"x": 450, "turn": 0.3, "expr": "surprised", "acoes": [{"t": round(d[7] * 0.5, 2), "do": "shock_reaction", "dur": "resto"}]},
                             LU: {"x": 1950, "turn": -0.3, "expr": "surprised", "acoes": [{"t": round(d[7] * 0.5, 2), "do": "slip", "dur": "resto"}]}}}
    return out


R.partes["verso#1"] = verso("verso#1", 1)
R.partes["verso#2"] = verso("verso#2", 2)
CORES = ["rosa", "laranja", "roxo"]


# ───────── refrão: oito braços / abraço de polvo, aperta! / ninguém escapa, que festa! ─────────
def refrao(n):
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * 4)
    out = []
    for i, (t0, t1, v) in enumerate(T):
        d = round(t1 - t0, 2)
        if n == 3 and i in (1, 3):
            p = R.banda(PALCO, d, teclado=(i == 3), fx=["confete"], cam={"x": 1300, "y": 620, "zoom": 1.05, "zoom_fim": 1.12})
            p.pop("seg")
            p.update({"linhas": 2, "callout": [call(0.3, "OITO BRAÇOS!", "rosa")]})
        elif i == 2:                                               # tela dividida: o polvo dança × a turma dança igual
            p = R.dividida({"cenario": MAR, "camera": {"x": 1300, "y": 520, "zoom": 1.15, "zoom_fim": 1.25}, "fx": ["bolhas"],
                            "objetos": {"p": pv(d, x=1300, depth=0.85, tchau=[(0.0, 0.0), (0.4, 1.0), (d * 0.5, 0.0), (d * 0.5 + 0.4, 1.0)], boca=0.7)}},
                           {"cenario": PRAIA if n != 2 else SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.15, "zoom_fim": 1.25},
                            "atores": {LA: {"x": 1100, "turn": 0.25, "acoes": [{"t": 0.1, "do": "dance", "style": "bracos", "dur": "resto"}]},
                                       LU: {"x": 1500, "turn": -0.25, "acoes": [{"t": 0.1, "do": "dance", "style": "festa", "dur": "resto"}]}}},
                           linhas=2, layout="diagonal" if n % 2 else "vertical", callout=[call(0.3, "OITO BRAÇOS!", CORES[n - 1])])
        elif i == 0:                                               # oito braços! abraço de polvo, aperta!
            p = {"linhas": 2, "cenario": MAR, "camera": {"x": 1300, "y": 540, "zoom": 1.05, "zoom_fim": 1.15}, "fx": ["coracoes"],
                 "callout": [call(0.2, "OITO BRAÇOS!", CORES[n - 1]), call(d * 0.5, "APERTA!", "vermelho")],
                 "objetos": {"p": pv(d, x=1300, depth=0.9, tchau=[(0.0, 1.0), (d * 0.45, 0.0)], abraco=[(0.0, 0.0), (d * 0.45, 0.0), (d * 0.55, 1.0)],
                                     boca=[(d * 0.5, 0.8)])},
                 "atores": {LA: {"x": 800, "turn": 0.3, "acoes": [{"t": 0.1, "do": "dance", "style": R.estilo(), "dur": round(d * 0.45, 2)},
                                                                  {"t": round(d * 0.5, 2), "do": "abraco", "dur": "resto"}]},
                            LU: {"x": 1800, "turn": -0.3, "acoes": [{"t": 0.1, "do": "dance", "style": R.estilo(), "dur": round(d * 0.45, 2)},
                                                                    {"t": round(d * 0.5, 2), "do": "abraco", "dur": "resto"}]}}}
            if n == 1:
                p["flash"] = True
        else:                                                      # oito braços! ninguém escapa, que festa!
            p = {"linhas": 2, "cenario": MAR if n != 2 else PRAIA, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["confete"],
                 "callout": [call(d * 0.5, "NINGUÉM ESCAPA!", "laranja")],
                 "objetos": {"p": pv(d, x=1950, depth=0.8, agita=0.5, abraco=[(0.0, 0.0), (d * 0.5, 1.0)], boca=[(d * 0.5, 1.0)])},
                 "atores": {LA: {"x": 300, "turn": 0.3, "acoes": [{"t": 0.0, "do": "run", "to_x": 900, "dur": round(d * 0.45, 2)},
                                                                  {"t": round(d * 0.5, 2), "do": "laugh", "dur": "resto"}]},
                            LU: {"x": 100, "turn": 0.3, "acoes": [{"t": 0.2, "do": "run", "to_x": 1450, "dur": round(d * 0.45, 2)},
                                                                  {"t": round(d * 0.55, 2), "do": "jump", "dur": "resto"}]}}}
            if n == 2:
                p["objetos"]["s"] = {"id": "siri", "x": 2250, "y": 960, "z": 3, "depth": 0.5,
                                     "keys": [{"t": 0.0, "pose": {"anda": 0.0, "pinca": 0.0}, "ease": "step"},
                                              {"t": round(d - 0.06, 2), "pose": {"anda": round(d * 2, 1), "pinca": 1.0}, "ease": "linear"}]}
                p["callout"] = [call(d * 0.5, "QUE FESTA!", "laranja")]
        out.append(p)
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos (bordão + banda na praia) ─────────
def intervalo(key, n):
    b, bl = R.bloco(key)
    D = b["e"] - b["s"]
    if not bl:
        s1 = round(D / 2, 2)
        return [{**R.banda(PALCO, s1, teclado=True, fx=["confete"]), "titulo": "a banda"},
                {"seg": round(D - s1, 2), "cenario": MAR, "camera": CAM_MAR, "fx": ["bolhas"], "titulo": "o polvo dança",
                 "objetos": {"p": pv(D - s1, x=1650, depth=0.8, agita=0.4, tchau=[(0.0, 0.0), (0.5, 1.0), (1.5, 0.0), (2.0, 1.0), (3.0, 0.0)])},
                 "atores": {LA: {"x": 600, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "sapinho", "dur": "resto"}]},
                            LU: {"x": 1000, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "chute", "dur": "resto"}]}}}]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = 3.4 if D - p1 - 3.4 >= 2.0 else round(D - p1, 2)
    out = [{"linhas": 1, "seg": p1, "cenario": MAR if n == 1 else PRAIA, "camera": "close:luisinho", "callout": [call(0.2, "ZUM-ZUM, QUE MASSA!", "azul")],
            "objetos": {"f": bolinha_peixe(1700, 380, p1, -1)} if n == 1 else {},
            "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
           {"linhas": 1, "seg": p2, "cenario": "danca_ondas_azul" if n == 1 else "danca_bolinhas_rosa", "fx": ["bolhas"],
            "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")],
            "objetos": {"p": pv(p2, x=1600, y=1080, depth=0.45, tchau=1, boca=0.6)},
            "atores": {LA: {"x": 420, "y": 1010, "depth": 1.0, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura", "dur": "resto"}]},
                       LU: {"x": 1000, "y": 1010, "depth": 1.0, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "joelho", "dur": "resto"}]}}}]
    resto = D - p1 - p2
    if resto >= 1.0:
        s3 = round(resto / 2, 2)
        out += [{**R.banda(PALCO, s3, fx=["notas"]), "titulo": "a banda"},
                {**R.banda(PALCO, round(resto - s3, 2), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.25, "zoom_fim": 1.15}),
                 "titulo": "teclado e bateria"}]
    return out


R.partes["intervalo#1"] = intervalo("intervalo#1", 1)
R.partes["intervalo#2"] = intervalo("intervalo#2", 2)
R.partes["intervalo#3"] = intervalo("intervalo#3", 3)

# ───────── ponte: um, dois… sete, oito, abraço com calma ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4)
dp = [round(t1 - t0, 2) for t0, t1, _ in T]
acao_turma = [("dance", "toca_bateria_a4"), ("dance", "palmas"), ("dance", "bracos"), ("abraco", None)]
R.partes["ponte#1"] = []
for i in range(4):
    d = dp[i]
    conta = [(0.0, 2 * i), (d * 0.3, 2 * i + 1), (d * 0.65, 2 * i + 2)]
    canais = {"conta": conta, "boca": 0.6}
    if i == 0:
        canais["tambor"] = 1
    if i == 3:
        canais["abraco"] = [(d * 0.7, 1.0)]
        canais["conta"] = [(0.0, 6.0), (d * 0.3, 7.0), (d * 0.6, 8.0), (d * 0.7, 0.0)]
    do, st = acao_turma[i]
    quem = {(LA if i % 2 else LU): {"x": [450, 450, 2050, 450][i], "turn": 0.3 if i != 2 else -0.3, "acoes": [{"t": 0.1, "do": do, **({"style": st} if st else {}), "dur": "resto"}]}} if i != 0 else {}
    R.partes["ponte#1"].append(
        {"linhas": 1, "cenario": [MAR, PRAIA, MAR, PRAIA][i], "camera": {"x": 1350, "y": 520, "zoom": 1.1, "zoom_fim": 1.2},
         "callout": [call(0.1, ["UM, DOIS!", "TRÊS, QUATRO!", "CINCO, SEIS!", "SETE, OITO!"][i], ["azul", "verde", "laranja", "rosa"][i])],
         "objetos": {"p": pv(d, x=[1500, 1650, 1200, 1500][i], depth=0.85, **canais),
                     "n": {"id": "numero", "x": 2250, "y": 330, "z": 4, "depth": 0.9,
                           "keys": [{"t": 0.0, "pose": {"n": 2 * i + 1, "pop": 0.0}, "ease": "step"}, {"t": 0.3, "pose": {"pop": 1.0}, "ease": "back"},
                                    {"t": round(d * 0.5, 2), "pose": {"n": 2 * i + 2}, "ease": "step"}]}},
         "atores": quem})
R.partes["ponte#1"][0]["objetos"]["n"]["x"] = 2250

# ───────── final: convite + tchau com os oito braços ─────────
R.partes["final#1"] = R.convite(MAR, gostou="GOSTOU DO POLVO?", extra_casa={})
for p_ in R.partes["final#1"]:
    if not p_.get("camera"):
        p_["camera"] = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    elif isinstance(p_["camera"], dict) and "zoom_fim" not in p_["camera"]:
        p_["camera"]["zoom_fim"] = p_["camera"]["zoom"] + 0.08
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#1"][0]["objetos"] = {"p": pv(3.0, x=1750, y=1080, depth=0.5, tchau=1)}
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.4, "cenario": MAR, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["coracoes"],
     "callout": [call(0.3, "OITO BRAÇOS!", "rosa"), call(1.9, "TCHAU!", "amarelo")],
     "objetos": {"p": pv(3.4, x=1300, depth=0.85, tchau=[(0.0, 0.0), (0.4, 1.0)], boca=0.8)},
     "atores": {LA: {"x": 500, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LU: {"x": 2100, "turn": -0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]}}},
    {"seg": round(dfim - 3.4, 2), "cenario": MAR, "camera": {"x": 1300, "y": 600, "zoom": 1.2, "zoom_fim": 1.35}, "fx": ["coracoes"],
     "callout": [call(0.2, "ABRAÇO!", "vermelho")], "titulo": "o abraço de polvo",
     "objetos": {"p": pv(dfim - 3.4, x=1300, depth=0.85, abraco=[(0.0, 0.0), (0.4, 1.0)], lid=1, boca=0.3)},
     "atores": {LA: {"x": 900, "turn": 0.3, "acoes": [{"t": 0.1, "do": "abraco", "dur": "resto"}]},
                LU: {"x": 1700, "turn": -0.3, "acoes": [{"t": 0.1, "do": "abraco", "dur": "resto"}]}}},
]

def bolhas_subindo(d, x0):
    return {"id": "bolha", "x": x0, "y": 900, "z": 0, "depth": 0.35,
            "keys": [{"t": 0.0, "pose": {"y": 900, "balanco": 0.0}, "ease": "step"},
                     {"t": round(max(0.6, d) - 0.06, 2), "pose": {"y": 150, "balanco": round(d, 1)}, "ease": "linear"}]}


for chave, planos in R.partes.items():
    k_info = chave if chave in R.info else f"{chave}#1"
    for j, (p_, (t0, t1, _)) in enumerate(zip(planos, R.tempos(k_info, planos))):
        for sb in [p_] + list((p_.get("tela_dividida") or {}).get("paineis", [])):
            if sb.get("cenario") == MAR:
                sb.setdefault("objetos", {})["b"] = bolhas_subindo(t1 - t0, [380, 2250, 1000, 1800][j % 4])

R.salvar("Roteiro de 'Polvo de Oito Braços' (take v1 cortado para 2:48, Luisinho, estilo E12 com resposta do teclado, nota 4,8): "
         "a turma mergulha da praia até o fundo do mar e conhece o polvo; 'com um braço…' em telas divididas; abraço de polvo; "
         "contagem de 1 a 8; banda na praia (A4). Gerado por scripts/roteiros/ep25_polvo_oito_bracos.py.")
