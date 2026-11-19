"""Roteiro verso a verso de 17 "Que Forma É Essa?" (take v1, 2:59, uma voz: Laurinha v2, estilo E6) → musicas/17_que_forma_e_essa/roteiro.json.

A mesa do lanche cheia de comidas-personagem; cada uma pula e a sua forma acende quando a música fala dela (pizza = círculo,
torrada = quadrado, queijo = triângulo, ovo = oval, presente = quadrado). A boca do Luisinho abre num círculo. Planos de 4–7 s.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep17_que_forma_e_essa.py
"""
from __future__ import annotations

import json
from pathlib import Path

from toonstudio.composition.clip_draft import _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "ep17-que-forma-e-essa"
MUS = ROOT / "musicas" / "17_que_forma_e_essa"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
COZ = "plano_cozinha"
CAM = {"x": 1300, "y": 600, "zoom": 1.15, "zoom_fim": 1.2}
LA, LU = "laurinha", "luisinho"
PIZZA, TORRADA, QUEIJO, OVO, PRESENTE = 0, 1, 2, 3, 4
MESA_Y = 930 - 240 * 1.3          # tampo da mesa (depth 1.3)


def bloco_info():
    out, occ = {}, {}
    for b in blocos(song):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        out[f"{b['tipo']}#{occ[b['tipo']]}"] = (b, [l for l in LINES if b["s"] - 0.05 <= l["s"] < b["e"] - 0.05])
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


def tp(t0, versos, *alvos, default=0.4):
    alvos = tuple(a.lower() for a in alvos)
    for l in versos:
        for w in l["words"]:
            if w["w"].lower().strip("!?,.…()\"'") in alvos:
                return round(max(0.0, w["s"] - t0), 2)
    return default


def call(t, text, color):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color}


def comida(tipo, x, y=930, depth=1.0, z=3, acende=None, pula=None):
    ks = [{"t": 0.0, "pose": {"brilho": 0.0, "pulo": 0.0}}]
    if acende is not None:
        ks += [{"t": max(0.05, acende - 0.05), "pose": {"brilho": 0.0}}, {"t": acende + 0.3, "pose": {"brilho": 1.0}, "ease": "out"},
               {"t": acende + 0.1, "pose": {"boca": 0.8}}, {"t": acende + 0.6, "pose": {"boca": 0.0}}]
    if pula is not None:
        ks += [{"t": max(0.05, pula - 0.05), "pose": {"pulo": 0.0}}, {"t": pula + 0.5, "pose": {"pulo": 1.0}, "ease": "linear"}]
    return {"id": "comida_forma", "x": x, "y": y, "z": z, "depth": depth, "pose": {"tipo": tipo}, "keys": ks}


def mesa_cheia(t_pula=None):
    o = {"mesa": {"id": "mesa", "x": 1300, "y": 930, "z": 1, "depth": 1.3}}
    for i, (tipo, x) in enumerate(((PIZZA, 980), (TORRADA, 1150), (QUEIJO, 1310), (OVO, 1470), (PRESENTE, 1630))):
        o[f"c{i}"] = comida(tipo, x, MESA_Y, depth=0.42, z=2, pula=None if t_pula is None else t_pula + 0.25 * i)
    return o


partes: dict = {}

P = starts("intro#1", [2, 1])
partes["intro"] = [
    {"linhas": 2, "cenario": COZ, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1},
     "callout": [call(2.8, "QUE FORMA É ESSA?", "laranja")], "objetos": mesa_cheia(t_pula=3.0),
     "atores": {LA: {"x": -250, "y": 520, "turn": 0.4, "acoes": [{"t": 0.3, "do": "fly", "dur": 2.2, "to_x": 700, "to_y": 930}]},
                LU: {"x": 2900, "y": 480, "turn": -0.4, "acoes": [{"t": 0.6, "do": "fly", "dur": 2.2, "to_x": 1900, "to_y": 930}]}}},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "fx": ["confete"], "callout": [call(0.15, "LAURINHA E LUISINHO!", "rosa")],
     "atores": {LA: {"x": 560, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                LU: {"x": 1360, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}}},
]


def verso(key):
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd) = starts(key, [2, 2, 2, 2])
    tpz, ttr = tp(b0, vb, "pizza", default=0.3), tp(b0, vb, "torrada", default=1.8)
    tqj, tov = tp(c0, vc, "queijo", default=0.3), tp(c0, vc, "ovo", default=2.0)
    tc = tp(d0, vd, "círculo", "circulo", default=1.8)
    return [
        {"linhas": 2, "cenario": COZ, "camera": CAM, "callout": [call(1.6, "QUE ENGRAÇADO!", "amarelo")], "objetos": mesa_cheia(t_pula=0.6),
         "atores": {LA: {"x": 750, "turn": 0.4, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
        {"linhas": 2, "cenario": COZ, "camera": CAM, "callout": [call(tpz + 0.3, "CÍRCULO!", "vermelho"), call(ttr + 0.3, "QUADRADO!", "azul")],
         "objetos": {"pz": comida(PIZZA, 1050, acende=tpz), "tr": comida(TORRADA, 1550, acende=ttr)}},
        {"linhas": 2, "cenario": COZ, "camera": CAM, "callout": [call(tqj + 0.3, "TRIÂNGULO!", "amarelo"), call(tov + 0.3, "OVAL!", "rosa")],
         "objetos": {"qj": comida(QUEIJO, 1050, acende=tqj), "ov": comida(OVO, 1550, acende=tov)}},
        {"linhas": 2, "cenario": COZ, "camera": "close:luisinho", "callout": [call(tc, "UM CÍRCULO!", "laranja")],
         "atores": {LU: {"x": 1300, "turn": 0.0, "expr": "shock",
                         "acoes": [{"t": max(0.1, tc - 0.3), "do": "take"}]}}},
    ]


partes["verso#1"] = verso("verso#1")
partes["verso#2"] = verso("verso#2")

BG = {1: "danca_bolinhas_azul", 2: "danca_xadrez_verde", 3: "danca_ondas_rosa", 4: "danca_raios_laranja"}


def refrao(n):
    (a0, a1, va), (b0, b1, vb) = starts(f"refrao#{n}", [4, 4])
    tipos = [(PIZZA, TORRADA), (QUEIJO, OVO), (PRESENTE, PIZZA), (TORRADA, QUEIJO)][n - 1]
    tq = tp(a0, va, "acertou", default=5.5)
    p1 = {"linhas": 4, "cenario": COZ, "camera": CAM, "flash": True,
          "callout": [call(0.15, "QUE FORMA É ESSA?", ["laranja", "azul", "rosa", "verde"][n - 1]), call(tq, "ACERTOU!", "verde")],
          "objetos": {"c1": comida(tipos[0], 1300, acende=round(tq - 0.4, 2))},
          "atores": {LA: {"x": 800, "turn": 0.35, "acoes": [{"t": 0.0, "do": "pensar", "dur": round(max(0.5, tq - 0.5), 2)},
                                                          {"t": round(tq, 2), "do": "cheguei", "dur": "resto"}]},
                     LU: {"x": 1800, "turn": -0.35, "acoes": [{"t": 0.0, "do": "pensar", "dur": round(max(0.5, tq - 0.3), 2)},
                                                           {"t": round(tq + 0.2, 2), "do": "jump", "dur": 1.0}]}}}
    d2 = b1 - b0
    p2 = {"linhas": 4, "cenario": BG[n], "fx": ["confete" if n >= 3 else "estrelas"],
          "objetos": {"c2": {**comida(tipos[1], 960, 1010, depth=0.8, acende=1.0), "keys":
                             [{"t": round(i * 0.9, 2), "pose": {"pulo": float(i % 2)}, "ease": "linear"} for i in range(int(d2 / 0.9))] +
                             [{"t": 1.0, "pose": {"brilho": 1.0}}]}},
          "atores": {LA: {"x": 470, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "pulinho" if n < 3 else "festa", "dur": "resto"}]},
                     LU: {"x": 1450, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "gingado" if n < 3 else "festa", "dur": "resto"}]}}}
    if n == 4:
        for w in (LA, LU):
            p2["atores"][w]["acoes"] = [{"t": 0.0, "do": "dance", "style": "festa", "dur": round(d2 - 1.6, 2)}, {"t": round(d2 - 1.5, 2), "do": "laugh", "dur": "resto"}]
    return [p1, p2]


for n in (1, 2, 3, 4):
    partes[f"refrao#{n}"] = refrao(n)


def intervalo(key, n):
    b, bl = INFO[key]
    if not bl:
        return [{"seg": round(b["e"] - b["s"], 2), "cenario": "danca_raios_roxo", "titulo": "as comidas dançam", "fx": ["confete"],
                 "objetos": {f"c{i}": {**comida(t, 450 + i * 255, 1010, depth=0.55), "keys":
                                       [{"t": round(j * 0.45, 2), "pose": {"pulo": float((j + i) % 2)}, "ease": "linear"} for j in range(int((b["e"] - b["s"]) / 0.45))]}
                             for i, t in enumerate((PIZZA, TORRADA, QUEIJO, OVO, PRESENTE))}}]
    (t0, t1, v), (u0, u1, w) = starts(key, [1, 1])
    return [{"linhas": 1, "cenario": "danca_raios_rosa" if n == 1 else "danca_bolinhas_rosa", "camera": "close:laurinha", "callout": "BORA, TURMINHA!",
             "atores": {LA: {"x": 960, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
            {"linhas": 1, "cenario": COZ, "camera": CAM, "fx": ["confete"], "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")],
             "objetos": mesa_cheia(t_pula=0.4),
             "atores": {LA: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                        LU: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": "resto"}]}}}]


partes["intervalo#1"] = intervalo("intervalo#1", 1)
partes["intervalo#2"] = intervalo("intervalo#2", 2)
partes["intervalo#3"] = intervalo("intervalo#3", 3)


def ponte(key):
    (a0, a1, va), (b0, b1, vb) = starts(key, [2, 2])
    t1, t2 = tp(a0, va, "círculo", "circulo", default=1.2), tp(a0, va, "quadrado", default=3.0)
    t3, t4 = tp(b0, vb, "triângulo", "triangulo", default=1.2), tp(b0, vb, "oval", default=3.0)
    return [
        {"linhas": 2, "cenario": COZ, "camera": CAM, "callout": [call(t1, "CÍRCULO!", "vermelho"), call(t2, "QUADRADO!", "azul")],
         "objetos": {"pz": comida(PIZZA, 1050, acende=t1, pula=t1), "pr": comida(PRESENTE, 1550, acende=t2, pula=t2)},
         "atores": {LA: {"x": 650, "turn": 0.4, "acoes": [{"t": max(0.1, t1 - 0.6), "do": "point", "dur": "resto"}]}}},
        {"linhas": 2, "cenario": COZ, "camera": CAM, "callout": [call(t3, "TRIÂNGULO!", "amarelo"), call(t4, "OVAL!", "rosa")],
         "objetos": {"qj": comida(QUEIJO, 1050, acende=t3, pula=t3), "ov": comida(OVO, 1550, acende=t4, pula=t4)},
         "atores": {LU: {"x": 1950, "turn": -0.4, "acoes": [{"t": max(0.1, t4 + 0.4), "do": "bacana", "dur": "resto"}]}}}]


partes["ponte#1"] = ponte("ponte#1")
partes["ponte#2"] = ponte("ponte#2")

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
partes["final#2"] = [
    {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(1.0, "TCHAU!", "amarelo")], "objetos": mesa_cheia(t_pula=1.2),
     "atores": {LA: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 4.0}, {"t": 4.3, "do": "fly", "dur": 1.4, "to_x": -300, "to_y": 300}]},
                LU: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 4.0}, {"t": 4.4, "do": "fly", "dur": 1.4, "to_x": 2900, "to_y": 350}]}}},
]


def transicoes(keys):
    ultimo, out = {}, []
    for k in keys:
        k = dict(k)
        if k.get("ease", "inout") != "step" and "in" not in k:
            prev = [ultimo[c] for c in k["pose"] if c in ultimo]
            if prev:
                k["in"] = round(max(0.0, k["t"] - max(prev) - 0.03), 3)
        for c in k["pose"]:
            ultimo[c] = k["t"]
        out.append(k)
    return out


for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    ls = [p.get("linhas", 0 if "seg" in p else 1) for p in planos]
    durs = iter([t1 - t0 for t0, t1, _ in starts(k_info, [n for n in ls if n > 0])] if any(ls) else [])
    for p, n in zip(planos, ls):
        p["cantam"] = ["laurinha"]
        d = next(durs) if n > 0 else p.get("seg")
        for o in (p.get("objetos") or {}).values():
            if d and o.get("keys"):
                ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                o["keys"] = transicoes(sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"]))

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0",
       "nota": "Roteiro de 'Que Forma É Essa?' (take v1 de 18/11/2026, 2:59, Laurinha v2, estilo E6): a mesa do lanche com comidas-"
               "personagem; cada forma acende quando é cantada; o Luisinho de boca em círculo; ponte de pergunta e resposta. "
               "Gerado por scripts/roteiros/ep17_que_forma_e_essa.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = sum(len(v) for v in partes.values())
print("roteiro:", n, "planos ·", round(song["duration"] / n, 1), "s por plano")
