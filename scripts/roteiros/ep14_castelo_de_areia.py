"""Roteiro verso a verso de 14 "Castelo de Areia" (take v2, 2:47, uma voz: Laurinha) → musicas/14_castelo_de_areia/roteiro.json.

Jeito novo (referência Animadinhos): planos mais longos (4–7 s, um corte a cada ~5 s), a piada se repete — o castelo cresce,
o siri quer o castelo e sobe na torre, e a onda (chuá!) derruba tudo em todo refrão; a ponte fala com quem assiste.
A Laurinha canta a música inteira (a boca dela segue a letra em todas as partes).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep14_castelo_de_areia.py
"""
from __future__ import annotations

import json
from pathlib import Path

from toonstudio.composition.clip_draft import _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "ep14-castelo-de-areia"
MUS = ROOT / "musicas" / "14_castelo_de_areia"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
PRAIA = "plano_praia"
CAM = {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.06}
LA, LU = "laurinha", "luisinho"
CANTA = ["laurinha"]                       # uma voz só: a Laurinha canta tudo
TORRE_Y = 930 - 356                        # topo da torre do castelo (nível 3, depth 1)


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
            if w["w"].lower().strip("!?,.…()\"'") in alvos:
                return round(max(0.0, w["s"] - t0), 2)
    return default


def call(t, text, color):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color}


def batidas(t0, t1, cada=1):
    return [round(b - t0, 3) for b in BEATS if t0 <= b < t1][::cada]


def siri_anda(t0, t1, x0, x1, cada=1):
    ks = [{"t": 0.0, "pose": {"anda": 0.0, "x": x0}}, {"t": round(t1 - t0, 3), "pose": {"x": x1}, "ease": "linear"}]
    v = 0.0
    for t in batidas(t0, t1, cada):
        v += 0.5
        ks.append({"t": t, "pose": {"anda": v}, "ease": "inout"})
    return ks


def castelo(x=1300, nivel=3.0, depth=1.0, z=2, keys=None):
    return {"id": "castelo_areia", "x": x, "y": 930, "z": z, "depth": depth, "pose": {"nivel": nivel, "derruba": 0.0}, "keys": keys or []}


def onda_chega(t_chua, t1, x_fim=1500, altura=1.0, depth=1.0):
    """A onda entra pela direita, quebra no 'chuá' e volta para o mar."""
    return {"id": "onda", "x": 2900, "y": 960, "z": 4, "depth": depth, "pose": {"altura": altura, "quebra": 0.0, "lado": -1},
            "keys": [{"t": 0.0, "pose": {"x": 2900}}, {"t": max(0.1, t_chua - 1.0), "pose": {"x": 2900}},
                     {"t": t_chua, "pose": {"x": x_fim, "quebra": 0.2}, "ease": "out"},
                     {"t": min(t1 - 0.3, t_chua + 0.7), "pose": {"quebra": 1.0}, "ease": "in"},
                     {"t": min(t1 - 0.05, t_chua + 1.8), "pose": {"x": 3100}, "ease": "in"}]}


def derruba_keys(t_der, nivel=3.0):
    return [{"t": 0.0, "pose": {"nivel": nivel, "derruba": 0.0}}, {"t": max(0.05, t_der - 0.1), "pose": {"derruba": 0.0}},
            {"t": t_der + 0.5, "pose": {"derruba": 1.0}, "ease": "out"}]


partes: dict = {}

# ───────── intro: a praia; o castelo ainda é um montinho; a turma chega; dança enquanto o teclado toca
P = starts("intro#1", [2])
(t0, t1, v), = P
fim_canto = v[-1]["e"]
partes["intro"] = [
    {"linhas": 2, "cenario": PRAIA, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08},
     "callout": [call(t_palavra(t0, v, "castelo", default=1.8), "CASTELO DE AREIA!", "laranja")],
     "objetos": {"castelo": castelo(1300, 0.0), "balde": {"id": "baldinho", "x": 1600, "y": 940, "z": 3, "depth": 0.9, "pose": {"cheio": 1.0}}},
     "atores": {LA: {"x": -250, "y": 520, "turn": 0.4, "acoes": [{"t": 0.3, "do": "fly", "dur": 2.2, "to_x": 950, "to_y": 930}]},
                LU: {"x": 2900, "y": 480, "turn": -0.4, "acoes": [{"t": 0.7, "do": "fly", "dur": 2.2, "to_x": 1850, "to_y": 930}]}}},
    {"seg": round(t1 - fim_canto, 2), "cenario": PRAIA, "camera": {"x": 1300, "y": 600, "zoom": 1.12, "zoom_fim": 1.2},
     "titulo": "dança na praia, o siri espia",
     "objetos": {"castelo": castelo(1300, 0.0), "siri": {"id": "siri", "x": 1650, "y": 1000, "z": 1, "depth": 0.6,
                                                          "keys": [{"t": 0.0, "pose": {"y": 1100}}, {"t": 3.0, "pose": {"y": 1100}}, {"t": 3.6, "pose": {"y": 975}, "ease": "back"},
                                                                   {"t": 5.5, "pose": {"pinca": 1.0}}, {"t": 6.2, "pose": {"pinca": 0.0}}]}},
     "atores": {LA: {"x": 950, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                LU: {"x": 1850, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": "resto"}]}}},
]


def verso_a(key, linhas, longo=False):
    """Linhas 1–4: a praia, o baldinho e o castelo que cresce maior que a casinha."""
    P = starts(key, linhas)
    (a0, a1, va), (b0, b1, vb) = P[0], P[1]
    tg = t_palavra(b0, vb, "grande", default=1.0)
    p2 = {"linhas": linhas[1], "cenario": PRAIA, "camera": {"x": 1300, "y": 560, "zoom": 1.2, "zoom_fim": 1.0},
          "callout": [call(tg + 0.3, "UAU!", "amarelo")],
          "objetos": {"castelo": castelo(1300, 0.0, depth=1.0, keys=[{"t": 0.0, "pose": {"nivel": 0.0}}, {"t": tg + 1.6, "pose": {"nivel": 3.0}, "ease": "out"}])},
          "atores": {LA: {"x": 800, "turn": 0.35, "acoes": [{"t": 0.2, "do": "cheguei", "dur": 1.6}] +
                          ([{"t": 2.4, "do": "dance", "style": "festa", "dur": "resto"}] if longo else [])},
                     LU: {"x": 1850, "turn": -0.35, "expr": "surprised", "acoes": [{"t": max(0.2, tg), "do": "take"}] +
                          ([{"t": 2.6, "do": "dance", "style": "lado", "dur": "resto"}] if longo else [])}}}
    if longo:
        p2["fx"] = ["confete"]
    return [
        {"linhas": linhas[0], "cenario": PRAIA, "camera": {"x": 1350, "y": 640, "zoom": 1.35, "zoom_fim": 1.4},
         "objetos": {"balde": {"id": "baldinho", "x": 1500, "y": 940, "z": 3, "depth": 1.0, "pose": {"cheio": 1.0},
                               "keys": [{"t": 0.0, "pose": {"vira": 0.0}}, {"t": round(a1 - a0 - 0.6, 2), "pose": {"vira": 1.0}, "ease": "inout"}]}},
         "atores": {LA: {"x": 1100, "turn": 0.4, "acoes": [{"t": 0.0, "do": "dance", "style": "agacha", "dur": "resto"}]}}},
        p2]


def siri_torre(t0, t1, v, quem_corre=None):
    """Linhas 5–8: o siri chega correndo, 'esse castelo é meu!', sobe na torre e dá tchauzinho."""
    tm = t_palavra(t0, v, "meu", default=1.8)
    ts = t_palavra(t0, v, "subiu", default=3.4)
    tt = t_palavra(t0, v, "tchauzinho", default=5.0)
    ks = siri_anda(t0, t0 + tm, 2700, 1560) + [
        {"t": max(0.1, tm - 0.1), "pose": {"pinca": 0.0}}, {"t": tm + 0.15, "pose": {"pinca": 1.0}, "ease": "out"}, {"t": tm + 0.9, "pose": {"pinca": 0.0}},
        {"t": ts, "pose": {"x": 1560, "y": 930}}, {"t": ts + 0.9, "pose": {"x": 1300, "y": TORRE_Y}, "ease": "out"},
        {"t": tt, "pose": {"aceno": 0.0}}, {"t": tt + 0.3, "pose": {"aceno": 1.0}}, {"t": tt + 0.6, "pose": {"aceno": 0.3}}, {"t": tt + 0.9, "pose": {"aceno": 1.0}}]
    atores = {LA: {"x": 750, "turn": 0.35, "acoes": [{"t": max(0.1, tm), "do": "take"}, {"t": max(0.6, tt), "do": "laugh", "dur": "resto"}]}}
    if quem_corre:
        atores[LU] = {"x": 2600, "turn": -0.4, "acoes": [{"t": 0.2, "do": "run", "to_x": 1800}, {"t": max(1.5, tt), "do": "laugh", "dur": "resto"}]}
    return {"linhas": 4, "cenario": PRAIA, "camera": {"x": 1350, "y": 520, "zoom": 1.1, "zoom_fim": 1.18},
            "callout": [call(tm, "É MEU!", "vermelho"), call(tt, "TCHAU!", "amarelo")],
            "objetos": {"castelo": castelo(1300, 3.0), "siri": {"id": "siri", "x": 2700, "y": 930, "z": 3, "depth": 0.75, "keys": ks}},
            "atores": atores}


partes["verso#1"] = verso_a("verso#1", [2, 2]) + [siri_torre(*starts("verso#1", [2, 2, 4])[2])]

# verso 2: o Suno cantou a 1ª metade duas vezes (64 e 77 s, com o teclado no meio)
P = starts("verso#2", [2, 2, 4, 4])
vb = verso_a("verso#2", [2, 2], longo=True)
t0, t1, v = P[2]
partes["verso#2"] = vb + [
    {"linhas": 4, "cenario": PRAIA, "camera": {"x": 1300, "y": 600, "zoom": 1.25, "zoom_fim": 1.3}, "callout": [call(0.3, "DE NOVO!", "verde")],
     "objetos": {"castelo": castelo(1150, 0.0, keys=[{"t": 0.0, "pose": {"nivel": 0.0}}, {"t": round(t1 - t0 - 0.4, 2), "pose": {"nivel": 3.0}, "ease": "inout"}]),
                 "balde": {"id": "baldinho", "x": 1550, "y": 940, "z": 3, "depth": 1.0, "pose": {"cheio": 1.0},
                           "keys": [{"t": 0.0, "pose": {"vira": 0.0}}, {"t": 2.5, "pose": {"vira": 1.0}, "ease": "inout"}]}},
     "atores": {LA: {"x": 800, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "agacha", "dur": 2.5}, {"t": 2.8, "do": "cheguei", "dur": "resto"}]},
                LU: {"x": 1900, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}]}}},
    siri_torre(*P[3], quem_corre=True)]

# ───────── refrões: o castelo pronto (torre, ponte, bandeira) · lá vem a onda… chuá! · derrubou! (e no 2º plano, festa)
REF = {1: ("danca_bolinhas_azul", "laranja"), 2: ("danca_raios_amarelo", "rosa"), 3: ("danca_xadrez_verde", "vermelho")}


def refrao(n):
    bg, cor = REF[n]
    P = starts(f"refrao#{n}", [4, 4])
    (a0, a1, va), (b0, b1, vb) = P
    tc = t_palavra(a0, va, "chuá", "chua", default=3.6)
    td = t_palavra(a0, va, "derrubou", default=4.6)
    p1 = {"linhas": 4, "cenario": PRAIA, "camera": {"x": 1350, "y": 540, "zoom": 1.05, "zoom_fim": 1.12}, "flash": True,
          "callout": [call(0.15, "CASTELO DE AREIA!", cor), call(tc, "CHUÁ!", "azul")],
          "objetos": {"castelo": castelo(1250, 3.0, depth=1.0 + 0.1 * (n - 1), keys=derruba_keys(td)), "onda": onda_chega(tc, a1 - a0)},
          "atores": {LA: {"x": 700, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": round(max(0.5, tc - 0.2), 2)},
                                                         {"t": round(td, 2), "do": "laugh", "dur": "resto"}]},
                     LU: {"x": 1950, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": round(max(0.5, tc - 0.2), 2)},
                                                           {"t": round(tc, 2), "do": "take"}, {"t": round(td + 0.3, 2), "do": "laugh", "dur": "resto"}]}}}
    tc2 = t_palavra(b0, vb, "chuá", "chua", default=3.6)
    p2 = {"linhas": 4, "cenario": bg, "fx": ["confete" if n == 3 else "estrelas"],
          "callout": [call(0.15, "TORRE, PONTE E BANDEIRA!", "amarelo"), call(tc2, "CHUÁ!", "azul")],
          "objetos": {"castelo": {"id": "castelo_areia", "x": 960, "y": 1010, "z": 2, "depth": 0.8, "pose": {"nivel": 3.0},
                                  "keys": derruba_keys(t_palavra(b0, vb, "derrubou", default=4.6))},
                      "onda": {**onda_chega(tc2, b1 - b0, x_fim=1100, depth=0.85), "y": 1040}},
          "atores": {LA: {"x": 430, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "pulinho", "dur": "resto"}]},
                     LU: {"x": 1500, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "gingado", "dur": "resto"}]}}}
    if n == 3:                                     # último refrão: todo mundo cai na risada no fim
        p2["atores"][LA]["acoes"] = [{"t": 0.0, "do": "dance", "style": "festa", "dur": round(b1 - b0 - 1.6, 2)}, {"t": round(b1 - b0 - 1.5, 2), "do": "laugh", "dur": "resto"}]
        p2["atores"][LU]["acoes"] = [{"t": 0.0, "do": "dance", "style": "festa", "dur": round(b1 - b0 - 1.6, 2)}, {"t": round(b1 - b0 - 1.4, 2), "do": "laugh", "dur": "resto"}]
    return [p1, p2]


for n in (1, 2, 3):
    partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos: "Bora, turminha!" e a dança do teclado na praia (o siri dança junto)
def intervalo(key, bg_close, n):
    b, bl = INFO[key]
    if bl:
        (t0, t1, v), = starts(key, [1])
        fala_fim = v[-1]["e"]
        return [{"linhas": 1, "cenario": bg_close, "camera": "close:laurinha", "callout": "BORA, TURMINHA!",
                 "atores": {LA: {"x": 960, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
                {"seg": round(t1 - fala_fim, 2), "cenario": PRAIA, "camera": CAM, "titulo": "dança na praia com o siri", "fx": ["notas"],
                 "objetos": {"castelo": castelo(1300, 3.0, depth=0.9, z=1),
                             "siri": {"id": "siri", "x": 1300, "y": TORRE_Y + 40, "z": 2, "depth": 0.7,
                                      "keys": [{"t": t, "pose": {"aceno": float(i % 2)}} for i, t in enumerate(batidas(fala_fim, t1, 2))]}},
                 "atores": {LA: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": ["festa", "bracos"][n % 2], "dur": "resto"}]},
                            LU: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": ["lado", "pulinho"][n % 2], "dur": "resto"}]}}}]
    t0, t1 = b["s"], b["e"]                       # intervalo sem fala (antes do convite): festa
    return [{"seg": round(t1 - t0, 2), "cenario": "danca_raios_laranja", "titulo": "festa do teclado", "fx": ["confete"],
             "objetos": {"siri": {"id": "siri", "x": 960, "y": 1010, "z": 2, "depth": 0.9,
                                  "keys": [{"t": t, "pose": {"pinca": float(i % 2), "pulo": float(i % 2)}} for i, t in enumerate(batidas(t0, t1, 2))]}},
             "atores": {LA: {"x": 450, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                        LU: {"x": 1470, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}}}]


partes["intervalo#1"] = intervalo("intervalo#1", "danca_raios_rosa", 1)
partes["intervalo#2"] = intervalo("intervalo#2", "danca_bolinhas_rosa", 2)
partes["intervalo#3"] = intervalo("intervalo#3", None, 3)


# ───────── ponte: comandos para quem assiste (cava · pula a ondinha · anda de lado igual siri · nada igual peixe)
def ponte(key, perto=False):
    P = starts(key, [2, 2])
    (a0, a1, va), (b0, b1, vb) = P
    tp = t_palavra(a0, va, "pular", "pula", default=2.0)
    tpeixe = t_palavra(b0, vb, "peixe", default=2.0)
    zoom = 1.18 if perto else 1.0
    return [
        {"linhas": 2, "cenario": PRAIA, "camera": {"x": 1300, "y": 600 if perto else 540, "zoom": zoom, "zoom_fim": zoom + 0.06},
         "callout": [call(0.2, "CAVA, CAVA!", "laranja"), call(tp, "PULA A ONDINHA!", "azul")],
         "objetos": {"balde": {"id": "baldinho", "x": 1300, "y": 940, "z": 3, "depth": 1.0, "pose": {"cheio": 1.0}},
                     "onda": onda_chega(tp + 0.4, a1 - a0, x_fim=1400, altura=0.25, depth=0.9)},
         "atores": {LA: {"x": 950, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "agacha", "dur": round(max(0.5, tp - 0.1), 2)},
                                                        {"t": round(tp + 0.2, 2), "do": "jump", "dur": 1.0}]},
                    LU: {"x": 1700, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "agacha", "dur": round(max(0.5, tp), 2)},
                                                          {"t": round(tp + 0.3, 2), "do": "jump", "dur": 1.0}]}}},
        {"linhas": 2, "cenario": PRAIA, "camera": {"x": 1300, "y": 560, "zoom": zoom, "zoom_fim": zoom + 0.05},
         "callout": [call(0.2, "DE LADINHO!", "vermelho"), call(tpeixe, "NADA, PEIXINHO!", "amarelo")],
         "objetos": {"siri": {"id": "siri", "x": 600, "y": 940, "z": 3, "depth": 0.8, "keys": siri_anda(b0, b0 + max(1.0, tpeixe), 500, 1300)},
                     "peixe": {"id": "peixinho", "x": 1900, "y": 700, "z": 1, "depth": 0.7, "pose": {"lado": -1},
                               "keys": [{"t": 0.0, "pose": {"y": 760, "x": 2200}}, {"t": max(0.2, tpeixe), "pose": {"y": 760}},
                                        {"t": tpeixe + 0.6, "pose": {"y": 560, "x": 1800, "boca": 1.0}, "ease": "out"},
                                        {"t": tpeixe + 1.2, "pose": {"y": 760, "x": 1500, "boca": 0.0}, "ease": "in"}]}},
         "atores": {LA: {"x": 900, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": "resto"}]},
                    LU: {"x": 1700, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": round(max(0.5, tpeixe), 2)},
                                                          {"t": round(tpeixe + 0.1, 2), "do": "dance", "style": "bracos", "dur": "resto"}]}}}]


partes["ponte#1"] = ponte("ponte#1")
partes["ponte#2"] = ponte("ponte#2", perto=True)

# ───────── final: convite (uma voz) e o tchau do siri lá da torre — a onda derruba no último 'chuá'
P = starts("final#1", [1, 1, 1, 1])
partes["final#1"] = [
    {"linhas": 1, "cenario": "danca_raios_azul", "camera": "close:laurinha", "callout": [call(0.3, "GOSTOU?", "rosa")],
     "atores": {LA: {"x": 960, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.4, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LA: {"x": 680, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "plano_casa_frente", "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                LA: {"x": 1450, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LA: {"x": 600, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
]
(t0, t1, v), = starts("final#2", [1])
tc = t_palavra(t0, v, "chuá", "chua", default=2.0)
partes["final#2"] = [
    {"linhas": 1, "cenario": PRAIA, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(t_palavra(t0, v, "tchau", default=1.0), "TCHAU!", "amarelo"), call(tc, "CHUÁ!", "azul")],
     "objetos": {"castelo": castelo(1300, 3.0, keys=derruba_keys(tc + 0.3)),
                 "siri": {"id": "siri", "x": 1300, "y": TORRE_Y, "z": 3, "depth": 0.75,
                          "keys": [{"t": t, "pose": {"aceno": float(i % 2)}} for i, t in enumerate(batidas(t0, t0 + tc, 1))] +
                                  [{"t": tc + 0.3, "pose": {"y": TORRE_Y}}, {"t": tc + 0.9, "pose": {"y": 930}, "ease": "in"}]},
                 "onda": onda_chega(tc, t1 - t0, x_fim=1500)},
     "atores": {LA: {"x": 750, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": round(max(1.0, tc), 2)},
                                                     {"t": round(tc + 0.4, 2), "do": "laugh", "dur": "resto"}]},
                LU: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": round(max(1.0, tc), 2)},
                                                       {"t": round(tc + 0.5, 2), "do": "laugh", "dur": "resto"}]}}},
]


def transicoes(keys):
    """O motor só faz a transição nos `in` s antes da chave (padrão 0,25): movimento contínuo precisa vir da chave anterior."""
    ultimo, out = {}, []
    for k in keys:
        k = dict(k)
        if k.get("ease", "inout") != "step" and "in" not in k:
            prev = [ultimo[c] for c in k["pose"] if c in ultimo]
            if prev:
                k["in"] = round(max(0.0, k["t"] - max(prev)), 3)
        for c in k["pose"]:
            ultimo[c] = k["t"]
        out.append(k)
    return out


for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    ls = [p.get("linhas", 0 if "seg" in p else 1) for p in planos]
    durs = [t1 - t0 for t0, t1, _ in starts(k_info, [n for n in ls if n > 0])] if any(ls) else []
    di = iter(durs)
    for p in planos:
        p["cantam"] = CANTA
        d = next(di) if p.get("linhas", 0 if "seg" in p else 1) > 0 else p.get("seg")
        for o in (p.get("objetos") or {}).values():
            if d and o.get("keys"):
                ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                o["keys"] = transicoes(sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"]))

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0",
       "nota": "Roteiro de 'Castelo de Areia' (take v2 de 18/11/2026, 2:47, uma voz — Laurinha; o Suno repetiu a 1ª metade do verso 2): "
               "o castelo cresce maior que a casinha, o siri diz 'é meu!' e sobe na torre, a onda (chuá!) derruba em todo refrão; ponte "
               "de comandos para quem assiste; planos de 4–7 s (referência). Gerado por scripts/roteiros/ep14_castelo_de_areia.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = sum(len(v) for v in partes.values())
print("roteiro:", n, "planos ·", round(song["duration"] / n, 1), "s por plano")
