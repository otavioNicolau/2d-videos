"""Roteiro verso a verso de 15 "Bolha de Sabão" (take v1, 2:49, uma voz: Laurinha, estilo E5) → musicas/15_bolha_de_sabao/roteiro.json.

A piada: a bolha cresce maior que o Luisinho ("maior que o meu vizinho"), engole o gato e leva ele para passear no ar;
no "ploc!" ela estoura e o gato cai em pé, assustado. Planos de 4–7 s (referência).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep15_bolha_de_sabao.py
"""
from __future__ import annotations

import json
from pathlib import Path

from toonstudio.composition.clip_draft import _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "ep15-bolha-de-sabao"
MUS = ROOT / "musicas" / "15_bolha_de_sabao"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
JARDIM = "plano_campo"   # campo aberto: a bolha aparece contra o céu (no jardim de flores ela sumia)
CAM = {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.06}
LA, LU = "laurinha", "luisinho"


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


def bolha(x, y=930, depth=0.8, z=3, tam=1.0, keys=None):
    return {"id": "bolha", "x": x, "y": y, "z": z, "depth": depth, "pose": {"tam": tam, "estoura": 0.0}, "keys": keys or []}


def gato(x, y=930, depth=0.55, z=2, keys=None, pose=None):
    return {"id": "gato", "x": x, "y": y, "z": z, "depth": depth, "pose": pose or {}, "keys": keys or []}


def bolhinhas(t0, t1, n=5, x0=500, dx=230, depth=0.35, sobe=520, estoura_em=None):
    """Várias bolhinhas subindo devagar (e estourando no 'ploc')."""
    out = {}
    for i in range(n):
        y0 = 1000 + (i % 2) * 60
        ks = [{"t": 0.0, "pose": {"y": y0, "x": x0 + i * dx}}, {"t": round(t1 - t0 - 0.05, 2), "pose": {"y": y0 - sobe - (i % 3) * 80, "x": x0 + i * dx + (40 if i % 2 else -40)}, "ease": "linear"}]
        if estoura_em is not None:
            te = round(estoura_em + 0.08 * i, 2)
            ks += [{"t": max(0.05, te - 0.05), "pose": {"estoura": 0.0}}, {"t": te + 0.3, "pose": {"estoura": 1.0}, "ease": "out"}]
        out[f"b{i + 1}"] = bolha(x0 + i * dx, y0, depth=depth * (1 - 0.12 * (i % 3)), z=4, keys=ks)
    return out


partes: dict = {}

# ───────── intro: o jardim; a Laurinha chega com o potinho; bolhinhas sobem
(t0, t1, v), = starts("intro#1", [2])
partes["intro"] = [
    {"linhas": 2, "cenario": JARDIM, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08},
     "callout": [call(tp(t0, v, "bolha", default=1.5), "BOLHA DE SABÃO!", "azul")],
     "objetos": {"pote": {"id": "potinho", "x": 1500, "y": 940, "z": 3, "depth": 0.9}, **bolhinhas(t0, t1, n=5, x0=700, dx=260)},
     "atores": {LA: {"x": -250, "y": 520, "turn": 0.4, "acoes": [{"t": 0.3, "do": "fly", "dur": 2.2, "to_x": 1150, "to_y": 930}]}}},
]


def verso(key, variante=1):
    P = starts(key, [2, 2, 2, 2])
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd) = P
    # 1–2: pega o potinho e assopra devagarinho (a bolha nasce)
    p1 = {"linhas": 2, "cenario": JARDIM, "camera": {"x": 1300, "y": 640, "zoom": 1.35, "zoom_fim": 1.42},
          "objetos": {"pote": {"id": "potinho", "x": 1450, "y": 940, "z": 3, "depth": 1.0},
                      "bolha": bolha(1250, 760, depth=0.5, keys=[{"t": 0.0, "pose": {"tam": 0.0}}, {"t": round(a1 - a0 - 0.1, 2), "pose": {"tam": 0.5}, "ease": "out"}])},
          "atores": {LA: {"x": 1050, "turn": 0.4, "pose": {"mouth": "O"}, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}}
    # 3–4: a bolha gigante, maior que o vizinho (o Luisinho, de olho arregalado)
    tg = tp(b0, vb, "gigante", default=1.0)
    p2 = {"linhas": 2, "cenario": JARDIM, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.04},
          "callout": [call(tg, "GIGANTE!", "rosa")],
          "objetos": {"bolha": bolha(1300, 930, depth=0.9, keys=[{"t": 0.0, "pose": {"tam": 0.4}}, {"t": tg + 1.2, "pose": {"tam": 1.0}, "ease": "out"}])},
          "atores": {LA: {"x": 700, "turn": 0.4, "acoes": [{"t": 0.2, "do": "cheguei", "dur": "resto"}]},
                     LU: {"x": 1900, "turn": -0.4, "expr": "surprised", "acoes": [{"t": max(0.2, tg + 0.4), "do": "take"}]}}}
    # 5–6: a bolha pega o gato e leva pro ar
    tgato = tp(c0, vc, "gato", default=0.6)
    sobe = [{"t": 0.0, "pose": {"y": 930}}, {"t": max(0.3, tgato + 0.6), "pose": {"y": 930}}, {"t": round(c1 - c0 - 0.1, 2), "pose": {"y": 560}, "ease": "inout"}]
    p3 = {"linhas": 2, "cenario": JARDIM, "camera": {"x": 1300, "y": 520, "zoom": 1.05, "zoom_fim": 1.0},
          "callout": [call(tgato + 0.3, "O GATO!", "laranja")],
          "objetos": {"gato": gato(1300, 930, keys=[{"t": 0.0, "pose": {"assusta": 0.0}}, {"t": tgato + 0.5, "pose": {"assusta": 1.0}, "ease": "out"}] + [dict(k) for k in sobe]),
                      "bolha": bolha(1300, 960, depth=0.75, keys=[{"t": 0.0, "pose": {"x": 900}}, {"t": max(0.2, tgato + 0.4), "pose": {"x": 1300}, "ease": "inout"}]
                                     + [{"t": k["t"], "pose": {"y": k["pose"]["y"] + 30}, **({"ease": k["ease"]} if "ease" in k else {})} for k in sobe])},
          "atores": {LA: {"x": 650, "turn": 0.4, "acoes": [{"t": max(0.2, tgato + 0.5), "do": "take"}]}}}
    # 7–8: "miau" e vai passear no ar (atravessa o céu)
    tm = tp(d0, vd, "miau", default=0.8)
    p4 = {"linhas": 2, "cenario": JARDIM if variante == 1 else "plano_ceu", "camera": CAM, "callout": [call(tm, "MIAU!", "amarelo")],
          "objetos": {"gato": gato(500, 560, depth=0.5, keys=[{"t": 0.0, "pose": {"x": 450}}, {"t": round(d1 - d0 - 0.1, 2), "pose": {"x": 2200}, "ease": "inout"},
                                                                {"t": max(0.05, tm - 0.05), "pose": {"miau": 0.0}}, {"t": tm + 0.1, "pose": {"miau": 1.0}}, {"t": tm + 0.6, "pose": {"miau": 0.0, "aceno": 1.0}}]),
                      "bolha": bolha(450, 590, depth=0.7, keys=[{"t": 0.0, "pose": {"x": 450}}, {"t": round(d1 - d0 - 0.1, 2), "pose": {"x": 2200}, "ease": "inout"}])},
          "atores": {LA: {"x": 900, "y": 930 if variante == 1 else 820, "turn": 0.3, "fly": 0 if variante == 1 else 1,
                          "acoes": [{"t": 0.2, "do": "laugh", "dur": "resto"}]}}}
    if variante == 2:                                          # 2ª vez: o Luisinho voa atrás da bolha
        p4["atores"][LU] = {"x": 200, "y": 700, "fly": 1, "turn": 0.4, "acoes": [{"t": 0.4, "do": "fly", "dur": round(d1 - d0 - 0.8, 2), "to_x": 1900, "to_y": 640}]}
    return [p1, p2, p3, p4]


partes["verso#1"] = verso("verso#1", 1)
partes["verso#2"] = verso("verso#2", 2)

REF = {1: ("danca_bolinhas_azul", "azul"), 2: ("danca_ondas_rosa", "rosa"), 3: ("danca_xadrez_azul", "roxo"), 4: ("danca_raios_amarelo", "laranja")}


def refrao(n):
    bg, cor = REF[n]
    (a0, a1, va), (b0, b1, vb) = starts(f"refrao#{n}", [4, 4])
    tpl = tp(a0, va, "ploc", "poque", "plóqui", default=5.6)
    # 1º plano: a bolha com o gato sobe devagar… ploc! o gato cai de pé no jardim
    sobe = [{"t": 0.0, "pose": {"y": 900}}, {"t": max(0.3, tpl - 0.1), "pose": {"y": 420}, "ease": "inout"}]
    p1 = {"linhas": 4, "cenario": JARDIM, "camera": {"x": 1300, "y": 520, "zoom": 1.0, "zoom_fim": 1.05}, "flash": True,
          "callout": [call(0.15, "BOLHA DE SABÃO!", cor), call(tpl, "PLOC!", "vermelho")],
          "objetos": {"bolha": bolha(1300, 900, depth=0.75, keys=[dict(k) for k in sobe] + [{"t": max(0.05, tpl - 0.05), "pose": {"estoura": 0.0}},
                                                                                         {"t": tpl + 0.4, "pose": {"estoura": 1.0}, "ease": "out"}]),
                      "gato": gato(1300, 870, keys=[dict(k, pose={"y": k["pose"]["y"] - 30}) for k in sobe] +
                                   [{"t": tpl + 0.05, "pose": {"assusta": 1.0}}, {"t": tpl + 0.8, "pose": {"y": 930}, "ease": "in"},
                                    {"t": tpl + 1.4, "pose": {"assusta": 0.0}, "ease": "out"}])},
          "atores": {LA: {"x": 650, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "bracos", "dur": round(max(0.5, tpl - 0.1), 2)},
                                                         {"t": round(tpl + 0.2, 2), "do": "laugh", "dur": "resto"}]},
                     LU: {"x": 1950, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "pulinho", "dur": round(max(0.5, tpl - 0.1), 2)},
                                                           {"t": round(tpl + 0.3, 2), "do": "laugh", "dur": "resto"}]}}}
    tpl2 = tp(b0, vb, "ploc", "poque", "plóqui", default=5.6)
    p2 = {"linhas": 4, "cenario": bg, "fx": ["confete" if n >= 3 else "estrelas"], "callout": [call(0.2, "SOBE, SOBE!", "amarelo"), call(tpl2, "PLOC!", "vermelho")],
          "objetos": bolhinhas(b0, b1, n=6, x0=300, dx=270, depth=0.45, sobe=480, estoura_em=tpl2),
          "atores": {LA: {"x": 560, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa" if n >= 3 else "pulinho", "dur": "resto"}]},
                     LU: {"x": 1360, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa" if n >= 3 else "gingado", "dur": "resto"}]}}}
    if n == 4:
        dd = round(b1 - b0, 2)
        p2["atores"][LA]["acoes"] = [{"t": 0.0, "do": "dance", "style": "festa", "dur": round(dd - 1.6, 2)}, {"t": round(dd - 1.5, 2), "do": "laugh", "dur": "resto"}]
        p2["atores"][LU]["acoes"] = [{"t": 0.0, "do": "dance", "style": "festa", "dur": round(dd - 1.6, 2)}, {"t": round(dd - 1.4, 2), "do": "laugh", "dur": "resto"}]
    return [p1, p2]


for n in (1, 2, 3, 4):
    partes[f"refrao#{n}"] = refrao(n)


def intervalo(key, bg_close, n):
    b, bl = INFO[key]
    if not bl:
        return [{"seg": round(b["e"] - b["s"], 2), "cenario": "danca_raios_laranja", "titulo": "festa das bolhas", "fx": ["confete"],
                 "objetos": bolhinhas(b["s"], b["e"], n=5, x0=400, dx=280, depth=0.4, sobe=400),
                 "atores": {LA: {"x": 560, "y": 1010, "depth": 1.15, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                            LU: {"x": 1360, "y": 1010, "depth": 1.15, "turn": -0.2, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}}}]
    (t0, t1, v), = starts(key, [1])
    fim = v[-1]["e"]
    return [{"linhas": 1, "cenario": bg_close, "camera": "close:laurinha", "callout": "BORA, TURMINHA!",
             "atores": {LA: {"x": 960, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
            {"seg": round(t1 - fim, 2), "cenario": JARDIM, "camera": CAM, "titulo": "dança com o gato e as bolhinhas", "fx": ["notas"],
             "objetos": {"gato": gato(1300, 930, depth=0.6, keys=[{"t": 0.0, "pose": {"rabo": 0.0}}, {"t": round(t1 - fim - 0.1, 2), "pose": {"rabo": 4.0}, "ease": "linear"}]),
                         **bolhinhas(fim, t1, n=4, x0=500, dx=450, depth=0.35, sobe=450)},
             "atores": {LA: {"x": 750, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": ["festa", "bracos"][n % 2], "dur": "resto"}]},
                        LU: {"x": 1850, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": ["lado", "pulinho"][n % 2], "dur": "resto"}]}}}]


partes["intervalo#1"] = intervalo("intervalo#1", "danca_raios_rosa", 1)
partes["intervalo#2"] = intervalo("intervalo#2", "danca_bolinhas_rosa", 2)
partes["intervalo#3"] = intervalo("intervalo#3", None, 3)


def ponte(key):
    (a0, a1, va), (b0, b1, vb) = starts(key, [2, 2])
    tl = tp(a0, va, "lado", default=1.8)
    tdedo = tp(b0, vb, "dedo", default=1.6)
    p1 = {"linhas": 2, "cenario": JARDIM, "camera": CAM, "callout": [call(0.2, "PRA CIMA!", "azul"), call(tl, "PRO LADO!", "verde")],
          "objetos": {"b1": bolha(1300, 760, depth=0.5, keys=[{"t": 0.0, "pose": {"y": 760, "x": 1300}}, {"t": max(0.3, tl - 0.1), "pose": {"y": 380}, "ease": "inout"},
                                                              {"t": round(a1 - a0 - 0.1, 2), "pose": {"x": 2000}, "ease": "inout"}])},
          "atores": {LA: {"x": 800, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "bracos", "dur": round(max(0.5, tl - 0.1), 2)},
                                                         {"t": round(tl, 2), "do": "dance", "style": "lado", "dur": "resto"}]},
                     LU: {"x": 1850, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "bracos", "dur": round(max(0.5, tl - 0.1), 2)},
                                                           {"t": round(tl, 2), "do": "dance", "style": "lado", "dur": "resto"}]}}}
    p2 = {"linhas": 2, "cenario": JARDIM, "camera": {"x": 1250, "y": 520, "zoom": 1.35, "zoom_fim": 1.4}, "callout": [call(tdedo + 0.2, "PLOC!", "vermelho")],
          "objetos": {"b1": bolha(1400, 600, depth=0.35, keys=[{"t": 0.0, "pose": {"y": 640}}, {"t": max(0.3, tdedo), "pose": {"y": 560}, "ease": "inout"},
                                                              {"t": tdedo + 0.15, "pose": {"estoura": 0.0}}, {"t": tdedo + 0.5, "pose": {"estoura": 1.0}, "ease": "out"}])},
          "atores": {LA: {"x": 1050, "turn": 0.4, "acoes": [{"t": max(0.1, tdedo - 0.4), "do": "point", "dur": "resto"}]}}}
    return [p1, p2]


partes["ponte#1"] = ponte("ponte#1")
partes["ponte#2"] = ponte("ponte#2")

(P1, P2, P3, P4) = starts("final#1", [1, 1, 1, 1])
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
tpl = tp(t0, v, "ploc", "plóqui", "poque", default=2.0)
partes["final#2"] = [
    {"linhas": 1, "cenario": JARDIM, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(tp(t0, v, "tchau", default=1.0), "TCHAU!", "amarelo"), call(tpl, "PLOC!", "vermelho")],
     "objetos": {"gato": gato(1300, 600, depth=0.5, keys=[{"t": 0.0, "pose": {"aceno": 1.0}}, {"t": max(0.1, tpl), "pose": {"y": 600}}, {"t": tpl + 0.8, "pose": {"y": 930, "aceno": 0.0}, "ease": "in"}]),
                 "bolha": bolha(1300, 630, depth=0.7, keys=[{"t": max(0.05, tpl - 0.05), "pose": {"estoura": 0.0}}, {"t": tpl + 0.4, "pose": {"estoura": 1.0}, "ease": "out"}])},
     "atores": {LA: {"x": 750, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": round(max(1.0, tpl), 2)}, {"t": round(tpl + 0.3, 2), "do": "laugh", "dur": "resto"}]},
                LU: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": round(max(1.0, tpl), 2)}, {"t": round(tpl + 0.4, 2), "do": "laugh", "dur": "resto"}]}}},
]


def transicoes(keys):
    ultimo, out = {}, []
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
       "nota": "Roteiro de 'Bolha de Sabão' (take v1 de 18/11/2026, 2:49, uma voz — Laurinha, estilo E5): a bolha gigante maior que o "
               "vizinho leva o gato pra passear; no 'ploc!' estoura e o gato cai de pé; ponte de comandos (assopra pra cima, pro lado, "
               "pega a bolhinha com o dedo). Gerado por scripts/roteiros/ep15_bolha_de_sabao.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = sum(len(v) for v in partes.values())
print("roteiro:", n, "planos ·", round(song["duration"] / n, 1), "s por plano")
