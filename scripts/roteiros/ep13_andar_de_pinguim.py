"""Roteiro verso a verso de 13 "Andar de Pinguim" (take v1 cortado em 2:19) → musicas/13_andar_de_pinguim/roteiro.json.

O Luisinho voa até o gelo e encontra um pinguim de casaca e gravatinha; a turma imita o andar do pinguim (pé grudadinho,
balança, balança). A cada refrão a fila de pinguins cresce; os dois últimos refrões vão "mais rápido" e "mais rápido ainda"
(os pinguins gingam no dobro e no quádruplo do tempo) até todo mundo cair na risada.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep13_andar_de_pinguim.py
"""
from __future__ import annotations

import json
from pathlib import Path

from toonstudio.composition.clip_draft import _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "laurinha" / "ep13-andar-de-pinguim"
MUS = ROOT / "canais" / "laurinha" / "musicas" / "13_andar_de_pinguim"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
GELO, MAR = "plano_gelo", "plano_mar_gelado"
CAM = {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.06}


def bloco_info():
    out, occ = {}, {}
    for b in blocos(song):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        bl = [l for l in LINES if b["s"] - 0.05 <= l["s"] < b["e"] - 0.05]
        out[f"{b['tipo']}#{occ[b['tipo']]}"] = (b, bl)
    return out


INFO = bloco_info()


def starts(key, linhas):
    b, bl = INFO[key]
    res, li = [], 0
    for k, n in enumerate(linhas):
        st = b["s"] if k == 0 else _snap(bl[li]["s"] - 0.12, BEATS)
        res.append([st, None, bl[li:li + n]])
        li += n
    for k in range(len(res)):
        res[k][1] = res[k + 1][0] if k + 1 < len(res) else b["e"]
    return [tuple(r) for r in res]


def t_palavra(t0, versos, *alvos, default=0.4):
    alvos = tuple(a.lower() for a in alvos)
    for l in versos:
        for w in l["words"]:
            if w["w"].lower().strip("!?,.…()") in alvos:
                return round(max(0.0, w["s"] - t0), 2)
    return default


def call(t, text, color):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color}


def anda(t0, t1, passo=0.5, cada=1, desde=0.0):
    """Ginga do pinguim presa às batidas: a cada `cada` batida(s) a fase avança `passo` (0,5 = um pezinho)."""
    ks, v = [{"t": 0.0, "pose": {"anda": desde}}], desde
    for b in [b for b in BEATS if t0 <= b < t1][::cada]:
        v += passo
        ks.append({"t": round(b - t0, 3), "pose": {"anda": v}, "ease": "inout"})
    return ks


def bico_em(t, dur=0.35):
    return [{"t": round(max(0.0, t - 0.05), 2), "pose": {"bico": 0.0}}, {"t": round(t + 0.05, 2), "pose": {"bico": 1.0}, "ease": "out"},
            {"t": round(t + dur, 2), "pose": {"bico": 0.0}, "ease": "in"}]


def asas_bate(t0, t1, cada=1):
    ks, v = [{"t": 0.0, "pose": {"asas": 0.0}}], 0.0
    for b in [b for b in BEATS if t0 <= b < t1][::cada]:
        v = 1.0 - v
        ks.append({"t": round(b - t0, 3), "pose": {"asas": v}, "ease": "out"})
    return ks


def pinguim(x, y=930, depth=1.0, z=2, lado=1, keys=None, pose=None):
    return {"id": "pinguim", "x": x, "y": y, "z": z, "depth": depth, "pose": {"lado": lado, **(pose or {})}, "keys": keys or []}


def fila(t0, t1, n, x0, x1, y=930, depth=0.8, gap=230, cada=1, z=1):
    """Fila de pinguins atravessando o gelo, um atrás do outro, gingando no tempo."""
    out = {}
    lado = 1 if x1 > x0 else -1
    for i in range(n):
        dx = -lado * i * gap
        ks = [{"t": 0.0, "pose": {"x": x0 + dx}}, {"t": round(t1 - t0, 3), "pose": {"x": x1 + dx}, "ease": "linear"}]
        out[f"p{i + 1}"] = pinguim(x0 + dx, y, depth * (1 - 0.06 * (i % 3)), z, lado, ks + anda(t0, t1, 0.5, cada, desde=0.25 * i))
    return out


def transicoes(keys):
    """O motor segura o canal e só faz a transição nos `in` segundos antes da chave (padrão 0,25 s). Movimento contínuo
    (atravessar a tela, gingar) precisa da transição desde a chave anterior DO MESMO CANAL."""
    ultimo: dict = {}
    out = []
    for k in keys:
        k = dict(k)
        if k.get("ease", "inout") != "step" and "in" not in k:
            prev = [ultimo[c] for c in k["pose"] if c in ultimo]
            if prev:
                k["in"] = round(max(0.0, k["t"] - max(prev) - 0.03), 3)   # a "segura" do motor não pode cair no mesmo instante da chave anterior (viraria degrau)
        for c in k["pose"]:
            ultimo[c] = k["t"]
        out.append(k)
    return out


partes: dict = {}
LA, LU = "laurinha", "luisinho"

# ───────── intro: o gelo; o pinguim chega gingando; a fila; título
(a0, a1, v0), (b0, fim0, v1) = starts("intro#1", [1, 1])
seg_ini = v1[-1]["e"]
partes["intro"] = [
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08},
     "callout": [call(t_palavra(a0, v0, "andar", default=1.6), "ANDAR DE PINGUIM!", "azul")],
     "objetos": {"ping": pinguim(1300, keys=[{"t": 0.0, "pose": {"x": 2250}}, {"t": 2.0, "pose": {"x": 1300}, "ease": "out"}]
                                + anda(a0, a0 + 4.4))}},
    {"linhas": 1, "cenario": GELO, "camera": CAM, "callout": [call(t_palavra(b0, v1, "ê", default=1.2), "Ê!", "rosa")],
     "objetos": fila(b0, seg_ini - 0.06, 4, 1100, 2000, gap=210)},
    {"seg": round(fim0 - seg_ini, 2), "cenario": "danca_ondas_azul", "titulo": "pinguins dançando", "fx": ["estrelas"],
     "objetos": {"ping": pinguim(960, 1010, depth=1.1, keys=anda(seg_ini, fim0) + asas_bate(seg_ini, fim0, 2))},
     "atores": {}},
]

# ───────── verso 1 (Luisinho): voei pro gelo; quem tá aí? de casaca preta… é o pinguim!
P = starts("verso#1", [1, 1, 1, 1])
partes["verso#1"] = [
    {"linhas": 1, "cenario": GELO, "camera": CAM, "callout": [call(t_palavra(P[0][0], P[0][2], "uhuu", default=0.9), "UHUU!", "amarelo")],
     "atores": {LU: {"x": -200, "y": 420, "turn": 0.4, "acoes": [{"t": 0.0, "do": "fly", "dur": 1.3, "to_x": 1100, "to_y": 930}]}}},
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 600, "zoom": 1.2, "zoom_fim": 1.25},
     "callout": [call(t_palavra(P[1][0], P[1][2], "hein", default=0.6), "HEIN?", "roxo")],
     "objetos": {"ping": pinguim(1500, 860, depth=0.9, z=1, lado=-1, keys=[{"t": 0.0, "pose": {"y": 1050}}, {"t": 0.7, "pose": {"y": 860}, "ease": "back"}])},
     "atores": {LU: {"x": 1000, "turn": 0.3, "acoes": [{"t": 0.0, "do": "look_around", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1350, "y": 560, "zoom": 1.35, "zoom_fim": 1.4},
     "callout": [call(t_palavra(P[2][0], P[2][2], "oi", default=1.4), "OI!", "rosa")],
     "objetos": {"ping": pinguim(1350, lado=-1, keys=asas_bate(P[2][0], P[2][1]) + bico_em(t_palavra(P[2][0], P[2][2], "oi", default=1.4)))}},
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 560, "zoom": 1.15, "zoom_fim": 1.2},
     "callout": [call(t_palavra(P[3][0], P[3][2], "pinguim", default=0.5), "PINGUIM!", "laranja")],
     "objetos": {"ping": pinguim(1500, lado=-1, keys=bico_em(t_palavra(P[3][0], P[3][2], "pinguim", default=0.5)))},
     "atores": {LU: {"x": 1000, "turn": 0.3, "expr": "joy", "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
]


# ───────── refrões: 4 planos de 2 versos — fila no gelo · balança no fundo de dança · pé grudadinho · balança geral
REF = {1: dict(n=3, cada=2, bg=("danca_bolinhas_azul", "danca_xadrez_azul"), cor="azul"),
       2: dict(n=4, cada=2, bg=("danca_raios_roxo", "danca_ondas_azul"), cor="roxo"),
       3: dict(n=5, cada=2, bg=("danca_xadrez_verde", "danca_bolinhas_rosa"), cor="verde"),
       4: dict(n=5, cada=1, bg=("danca_raios_laranja", "danca_ondas_rosa"), cor="laranja"),
       5: dict(n=6, cada=1, bg=("danca_raios_vermelho", "danca_bolinhas_amarelo"), cor="vermelho")}


def refrao(n):
    R = REF[n]
    P = starts(f"refrao#{n}", [2, 2, 2, 2])
    rap = n >= 4
    passo_la, passo_lu = ("lado", "lado") if not rap else ("pulinho", "pulinho")
    planos = []
    t0, t1, v = P[0]
    planos.append({"linhas": 2, "cenario": GELO, "camera": CAM, "flash": True,
                   "callout": [call(0.15, "ANDAR DE PINGUIM!" if n < 4 else ("MAIS RÁPIDO!" if n == 4 else "MAIS RÁPIDO AINDA!"), R["cor"])],
                   "objetos": fila(t0, t1, R["n"], 2150, 1150, depth=0.8, gap=200, cada=R["cada"] if not rap else 1),
                   "atores": {LA: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": passo_la, "dur": "resto"}]},
                              LU: {"x": 1000, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": passo_lu, "dur": "resto"}]}}
                   if n > 1 else {LU: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": "resto"}]}}})
    t0, t1, v = P[1]
    planos.append({"linhas": 2, "cenario": R["bg"][0], "fx": ["notas"], "callout": [call(t_palavra(t0, v, "balança", default=1.4), "BALANÇA, BALANÇA!", "rosa")],
                   "objetos": {"ping": pinguim(960, 1010, depth=1.05, keys=anda(t0, t1, 0.5, 1 if rap else 2) + asas_bate(t0, t1, 2))},
                   "atores": {**({LA: {"x": 470, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco", "dur": "resto"}]}} if n > 1 else {}),
                              LU: {"x": 1450, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco", "dur": "resto"}]}}})
    t0, t1, v = P[2]
    planos.append({"linhas": 2, "cenario": GELO, "camera": {"x": 1300, "y": 700, "zoom": 1.45, "zoom_fim": 1.5},
                   "callout": [call(t_palavra(t0, v, "tic", default=1.0), "TIC, TIC!", "laranja")],
                   "objetos": {"ping": pinguim(1150, keys=anda(t0, t1, 0.5, 1))},
                   "atores": {LU if n == 1 else LA: {"x": 1500, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "pezinho", "dur": "resto"}]}}})
    t0, t1, v = P[3]
    fim = {"linhas": 2, "cenario": R["bg"][1], "fx": ["confete" if rap else "estrelas"],
           "callout": [call(t_palavra(t0, v, "balança", default=1.4), "Ê!" if n < 5 else "HA HA HA!", R["cor"])],
           "objetos": {"p1": pinguim(700, 1010, depth=0.9, keys=anda(t0, t1, 0.5, 1 if rap else 2)),
                       "p2": pinguim(1220, 1010, depth=0.9, lado=-1, keys=anda(t0, t1, 0.5, 1 if rap else 2, desde=0.5))},
           "atores": {LU: {"x": 960, "y": 1010, "depth": 1.2, "turn": 0.0, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco" if not rap else "festa", "dur": "resto"}]}}}
    if n > 1:
        fim["atores"][LA] = {"x": 1500, "y": 1010, "depth": 1.2, "turn": -0.2, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco" if not rap else "festa", "dur": "resto"}]}
        fim["atores"][LU]["x"] = 420
    if n == 5:                                                     # no fim do "mais rápido ainda", todo mundo cai na risada
        fim["atores"][LU]["acoes"] = [{"t": 0.0, "do": "dance", "style": "festa", "dur": round(t1 - t0 - 1.6, 2)}, {"t": round(t1 - t0 - 1.5, 2), "do": "laugh", "dur": "resto"}]
        fim["atores"][LA]["acoes"] = [{"t": 0.0, "do": "dance", "style": "festa", "dur": round(t1 - t0 - 1.6, 2)}, {"t": round(t1 - t0 - 1.4, 2), "do": "laugh", "dur": "resto"}]
    planos.append(fim)
    return planos


for n in range(1, 6):
    partes[f"refrao#{n}"] = refrao(n)

# ───────── intervalos (bordões e gritos)
P = starts("intervalo#1", [1, 1])
partes["intervalo#1"] = [
    {"linhas": 1, "cenario": "danca_raios_rosa", "camera": "close:laurinha", "callout": "BORA, TURMINHA!",
     "atores": {LA: {"x": 960, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": GELO, "camera": CAM, "fx": ["confete"], "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")],
     "objetos": {"ping": pinguim(1300, keys=anda(P[1][0], P[1][1]) + asas_bate(P[1][0], P[1][1], 2))},
     "atores": {LA: {"x": 800, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                LU: {"x": 1800, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}}},
]
partes["intervalo#2"] = [
    {"linhas": 1, "cenario": "danca_bolinhas_verde" if False else "danca_xadrez_vermelho", "camera": "medio:luisinho", "fx": ["confete"],
     "callout": [call(0.2, "ZUM-ZUM, QUE MASSA!", "amarelo")],
     "atores": {LU: {"x": 960, "acoes": [{"t": 0.1, "do": "bacana", "dur": 1.4}, {"t": 1.6, "do": "dance", "style": "festa", "dur": "resto"}]}}}]
partes["intervalo#3"] = [
    {"linhas": 1, "cenario": "danca_raios_laranja", "flash": True, "callout": [call(0.05, "MAIS RÁPIDO!", "amarelo")],
     "atores": {LU: {"x": 960, "y": 1010, "depth": 1.3, "acoes": [{"t": 0.0, "do": "cheguei", "dur": "resto"}]}}}]
partes["intervalo#4"] = [
    {"linhas": 1, "cenario": "danca_raios_vermelho", "flash": True, "fx": ["estrelas"], "callout": [call(0.1, "MAIS RÁPIDO AINDA!", "amarelo")],
     "objetos": {"ping": pinguim(1300, 1010, depth=1.0, keys=anda(*starts("intervalo#4", [1])[0][:2], 0.5, 1) + asas_bate(*starts("intervalo#4", [1])[0][:2], 1))},
     "atores": {LA: {"x": 600, "y": 1010, "depth": 1.2, "acoes": [{"t": 0.0, "do": "cheguei", "dur": "resto"}]}}}]

# ───────── verso 2 (Laurinha): escorrega de barriga, mergulha, "voa" na água, no céu não dá
P = starts("verso#2", [1, 1, 1, 1])
t0, t1, v = P[0]
partes["verso#2"] = [
    {"linhas": 1, "cenario": GELO, "camera": CAM, "callout": [call(t_palavra(t0, v, "uiii", default=1.4), "UIII!", "rosa")],
     "objetos": {"ping": pinguim(400, keys=[{"t": 0.0, "pose": {"x": 400, "barriga": 0.0}}, {"t": 0.5, "pose": {"barriga": 1.0}, "ease": "out"},
                                           {"t": 0.5, "pose": {"x": 400}}, {"t": round(t1 - t0, 2), "pose": {"x": 2300}, "ease": "out"}])},
     "atores": {LA: {"x": 1300, "y": 600, "fly": 1, "turn": 0.3, "acoes": [{"t": 0.6, "do": "laugh", "dur": "resto"}]}}},
]
t0, t1, v = P[1]
partes["verso#2"].append(
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1500, "y": 500, "zoom": 1.2, "zoom_fim": 1.25}, "flash": False,
     "callout": [call(t_palavra(t0, v, "splash", default=1.6), "SPLASH!", "azul")],
     "objetos": {"ping": pinguim(1300, 760, depth=0.85, z=1, keys=[{"t": 0.0, "pose": {"pulo": 0.0, "x": 1300, "y": 760}},
                                                                 {"t": 0.9, "pose": {"pulo": 1.0, "x": 1600}, "ease": "linear"},
                                                                 {"t": 0.9, "pose": {"y": 760}}, {"t": 1.3, "pose": {"y": 1300}, "ease": "in"}])}})
t0, t1, v = P[2]
partes["verso#2"].append(
    {"linhas": 1, "cenario": MAR, "camera": CAM, "callout": [call(t_palavra(t0, v, "uau", default=1.8), "UAU!", "amarelo")],
     "objetos": {"ping": pinguim(300, 620, depth=1.0, pose={"barriga": 1.0},
                                 keys=[{"t": 0.0, "pose": {"x": 200, "y": 700}}, {"t": round((t1 - t0) / 2, 2), "pose": {"x": 1300, "y": 520}, "ease": "inout"},
                                       {"t": round(t1 - t0, 2), "pose": {"x": 2400, "y": 680}, "ease": "inout"}] + asas_bate(t0, t1, 1))}})
t0, t1, v = P[3]
partes["verso#2"].append(
    {"linhas": 1, "cenario": GELO, "camera": CAM, "callout": [call(t_palavra(t0, v, "ha", default=1.8), "HA HA!", "laranja")],
     "objetos": {"ping": pinguim(1300, keys=asas_bate(t0, t0 + 1.6, 1) + [{"t": 0.0, "pose": {"pulo": 0.0}}, {"t": 0.8, "pose": {"pulo": 1.0}, "ease": "linear"},
                                                                         {"t": 1.7, "pose": {"lid": 0.0}}, {"t": 1.8, "pose": {"lid": 1.0}}])},
     "atores": {LA: {"x": 800, "turn": 0.3, "acoes": [{"t": 1.0, "do": "laugh", "dur": "resto"}]},
                LU: {"x": 1800, "turn": -0.3, "acoes": [{"t": 1.1, "do": "laugh", "dur": "resto"}]}}})

# ───────── ponte: braço colado · pé de pato · escorrega · bate a asinha
P = starts("ponte#1", [1, 1, 1, 1])
t0, t1, v = P[0]
partes["ponte#1"] = [
    {"linhas": 1, "cenario": GELO, "camera": CAM, "callout": [call(0.1, "BRAÇO COLADO!", "azul")],
     "objetos": {"ping": pinguim(1300, keys=anda(t0, t1, 0.5, 1))},
     "atores": {LA: {"x": 800, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "marcha", "dur": "resto"}]},
                LU: {"x": 1800, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "marcha", "dur": "resto"}]}}}]
t0, t1, v = P[1]
partes["ponte#1"].append(
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 720, "zoom": 1.4, "zoom_fim": 1.45}, "callout": [call(0.1, "PÉ DE PATO!", "laranja")],
     "objetos": {"ping": pinguim(1300, keys=anda(t0, t1, 0.5, 1))},
     "atores": {LA: {"x": 950, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "pezinho", "dur": "resto"}]},
                LU: {"x": 1650, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "pezinho", "dur": "resto"}]}}})
t0, t1, v = P[2]
partes["ponte#1"].append(
    {"linhas": 1, "cenario": GELO, "camera": CAM, "callout": [call(0.2, "UIII!", "rosa")],
     "objetos": {"ping": pinguim(500, keys=[{"t": 0.0, "pose": {"barriga": 1.0, "x": 500}}, {"t": round(t1 - t0, 2), "pose": {"x": 2000}, "ease": "out"}])},
     "atores": {LA: {"x": 900, "turn": 0.3, "acoes": [{"t": 0.1, "do": "slip"}]},
                LU: {"x": 1750, "turn": -0.3, "acoes": [{"t": 0.25, "do": "slip"}]}}})
t0, t1, v = P[3]
partes["ponte#1"].append(
    {"linhas": 1, "cenario": GELO, "camera": CAM, "callout": [call(t_palavra(t0, v, "flap", default=0.6), "FLAP, FLAP!", "amarelo")],
     "objetos": {"ping": pinguim(1300, keys=asas_bate(t0, t1, 1))},
     "atores": {LA: {"x": 800, "turn": 0.3, "pose": {"buzz": 1.0}, "acoes": [{"t": 0.0, "do": "dance", "style": "asinhas", "dur": "resto"}]},
                LU: {"x": 1800, "turn": -0.3, "pose": {"buzz": 1.0}, "acoes": [{"t": 0.0, "do": "dance", "style": "asinhas", "dur": "resto"}]}}})

# ───────── verso 3 (Luisinho): jogo de imitar — pequenininho, grandão, com pressa, cansado
P = starts("verso#3", [1, 1, 1, 1])
t0, t1, v = P[0]
partes["verso#3"] = [
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 680, "zoom": 1.35, "zoom_fim": 1.4},
     "callout": [call(t_palavra(t0, v, "tic", default=1.4), "TIC, TIC, TIC!", "rosa")],
     "objetos": {"ping": pinguim(1500, depth=0.5, keys=[{"t": 0.0, "pose": {"x": 1150}}, {"t": round(t1 - t0, 2), "pose": {"x": 1750}, "ease": "linear"}]
                                + anda(t0, t1, 0.5, 1))},
     "atores": {LU: {"x": 820, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "pezinho", "dur": "resto"}]}}}]
t0, t1, v = P[1]
tum = [{"t": 0.0, "pose": {"pulo": 0.0}}]
for i, b in enumerate([b for b in BEATS if t0 <= b < t1][::2]):
    tum.append({"t": round(b - t0, 3), "pose": {"pulo": float((i + 1) % 2)}, "ease": "linear"})
partes["verso#3"].append(
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 480, "zoom": 1.0, "zoom_fim": 1.04},
     "callout": [call(t_palavra(t0, v, "tum", default=1.4), "TUM, TUM!", "roxo")],
     "objetos": {"ping": pinguim(1450, 960, depth=1.75, z=2, keys=tum + anda(t0, t1, 0.5, 2))},
     "atores": {LU: {"x": 700, "turn": 0.3, "expr": "surprised", "acoes": [{"t": 0.2, "do": "take"}]}}})
t0, t1, v = P[2]
partes["verso#3"].append(
    {"linhas": 1, "cenario": GELO, "camera": CAM, "callout": [call(t_palavra(t0, v, "corre", default=1.4), "CORRE!", "laranja")],
     "objetos": {"ping": pinguim(-200, keys=[{"t": 0.0, "pose": {"x": -200}}, {"t": round(t1 - t0 - 0.3, 2), "pose": {"x": 2800}, "ease": "linear"}]
                                 + anda(t0, t1, 1.0, 1))},
     "atores": {LU: {"x": 300, "turn": 0.4, "acoes": [{"t": 0.4, "do": "run", "to_x": 2700}]}}})
t0, t1, v = P[3]
partes["verso#3"].append(
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 600, "zoom": 1.2, "zoom_fim": 1.25},
     "callout": [call(t_palavra(t0, v, "ufa", default=1.6), "UFA!", "verde")],
     "objetos": {"ping": pinguim(1550, lado=-1, keys=[{"t": 0.0, "pose": {"lid": 0.0, "barriga": 0.0}}, {"t": 1.0, "pose": {"lid": 1.0}},
                                                     {"t": 1.2, "pose": {"barriga": 1.0}, "ease": "inout"}])},
     "atores": {LU: {"x": 1000, "turn": 0.3, "acoes": [{"t": 0.0, "do": "ofegante", "dur": "resto"}]}}})

# ───────── final: convite e tchau no gelo
P = starts("final#1", [1, 1, 1, 1])
partes["final#1"] = [
    {"linhas": 1, "cenario": "danca_raios_azul", "camera": "close:laurinha", "callout": [call(0.3, "GOSTOU?", "rosa")],
     "atores": {LA: {"x": 960, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.4, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LU: {"x": 680, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "plano_casa_frente", "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                LA: {"x": 1450, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LA: {"x": 600, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
]
P = starts("final#2", [1])
t0, t1, v = P[0]
partes["final#2"] = [
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(t_palavra(t0, v, "tchau", default=1.0), "TCHAU!", "amarelo")],
     "objetos": {"p1": pinguim(1150, depth=0.9, keys=asas_bate(t0, t1, 2) + anda(t0, t1, 0.5, 2)),
                 "p2": pinguim(1500, depth=0.75, lado=-1, keys=asas_bate(t0, t1, 2) + anda(t0, t1, 0.5, 2, desde=0.5))},
     "atores": {LA: {"x": 750, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 3.0},
                                                      {"t": 3.3, "do": "fly", "dur": 1.4, "to_x": -300, "to_y": 300}]},
                LU: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 3.0},
                                                        {"t": 3.4, "do": "fly", "dur": 1.4, "to_x": 2900, "to_y": 350}]}}},
]

# chaves de objetos dentro do próprio plano
for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    ls = [p.get("linhas", 0 if "seg" in p else 1) for p in planos]
    durs = [t1 - t0 for t0, t1, _ in starts(k_info, [n for n in ls if n > 0])] + [None] * ls.count(0)
    for p, d in zip(planos, durs):
        d = d if d is not None else p.get("seg")
        for o in (p.get("objetos") or {}).values():
            if d and o.get("keys"):
                ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                o["keys"] = transicoes(sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"]))   # chave no fim exato: puxa p/ dentro

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0",
       "nota": "Roteiro verso a verso de 'Andar de Pinguim' (take v1 de 18/11/2026, cortado em 2:19 — o Suno repetiu o fim): o Luisinho "
               "voa até o gelo e encontra o pinguim de casaca e gravatinha; a fila de pinguins cresce a cada refrão; escorrega de barriga, "
               "mergulha e 'voa' na água; ponte de comandos; jogo de imitar (pequenininho, grandão, com pressa, cansado); "
               "'mais rápido' e 'mais rápido ainda' até todo mundo rir; convite e tchau. Gerado por scripts/roteiros/ep13_andar_de_pinguim.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("roteiro:", sum(len(v) for v in partes.values()), "planos")
