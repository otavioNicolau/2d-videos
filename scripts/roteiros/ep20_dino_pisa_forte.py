"""Roteiro verso a verso de 20 "Dino Pisa Forte" (take v1, 2:44, Luisinho, estilo E9) → musicas/20_dino_pisa_forte/roteiro.json.

O Dino grandão e bonzinho chega pela RUA (casa da frente) pisando; a cada passo a TELA TREME e tudo pula: o bolo na COZINHA,
o gato no sofá da SALA, a vovó no JARDIM ("Ai, ai, devagar!"). Refrão: "tum, tum, tremeu!" com a tela tremendo e a turma
pulando ("Quem pulou? Fui eu!"). Ponte de comandos: pé direito, pé esquerdo, pisa forte (tremor grande) e pisa fraquinho
(o Dino na ponta do pé, a turma de fininho). Final: festa no SALÃO com o Dino dançando.
Personagens 1,45× (regra de 19/11), animação A3 (passos com perna; nenhum estilo > 1/3 da dança), sem efeitos sonoros
(desligados pelo usuário em 19/11).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep20_dino_pisa_forte.py
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

from toonstudio.composition.clip_draft import _q, _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "ep20-dino-pisa-forte"
MUS = ROOT / "musicas" / "20_dino_pisa_forte"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
RUA, JARDIM, COZINHA, SALA, SALAO, CAMPO = "plano_casa_frente", "plano_jardim", "plano_cozinha", "plano_sala", "plano_salao", "plano_campo"
LA, LU, VO = "laurinha", "luisinho", "vovo"
CAM = {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.18}
MESA_Y = 930 - 240 * 1.3
# passos da turma em rodízio (A3): nenhum estilo passa de 1/3 da dança do vídeo
ESTILOS = itertools.cycle(["chute", "joelho", "sapinho", "cintura", "pezinho", "marcha", "lado", "balanco", "bracos", "gingado", "palmas", "festa"])


def bloco_info():
    out, occ = {}, {}
    for b in blocos(song):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        out[f"{b['tipo']}#{occ[b['tipo']]}"] = (b, [l for l in LINES if b["s"] - 0.05 <= l["s"] < b["e"] - 0.05])
    return out


INFO = bloco_info()


def planos_tempo(key, planos):
    b, bl = INFO[key]
    res, li, t = [], 0, b["s"]
    for k, p in enumerate(planos):
        n = int(p.get("linhas", 1 if "seg" not in p else 0))
        st = b["s"] if k == 0 else (_snap(bl[li]["s"] - 0.12, BEATS) if n > 0 and li < len(bl) else t)
        mine = bl[li:li + n] if n > 0 else []
        li += n
        res.append([st, None, mine])
        t = st + float(p["seg"]) if "seg" in p else (mine[-1]["e"] if mine else st + 2.0)
    for k in range(len(res)):
        res[k][1] = res[k + 1][0] if k + 1 < len(res) else b["e"]
    return [(_q(a), _q(e), m) for a, e, m in res]


def tps(t0, versos, *alvos):
    """Todos os inícios (relativos ao plano) das palavras pedidas — cada 'tum' vira uma pisada."""
    alvos = tuple(a.lower() for a in alvos)
    return [round(max(0.0, w["s"] - t0), 2) for l in versos for w in l["words"] if w["w"].lower().strip("!?,.…:()\"'") in alvos]


def tp(t0, versos, *alvos, default=0.4):
    r = tps(t0, versos, *alvos)
    return r[0] if r else default


def call(t, text, color):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color}


def dino(x=1500, depth=0.8, pisadas=(), danca=None, extra=None, y=930, pose=None):
    depth = round(depth * 0.85, 3)                          # 1,45× deixava o Dino com a cabeça fora da tela
    """O Dino: pisadas = [(t, pé)] (levanta 0,35 s antes e pisa no t); danca = (t0, t1) balança; extra = chaves livres."""
    ks = [{"t": 0.0, "pose": {"pisa": 0.0, "levinho": 0.0, "ruge": 0.0, "tchau": 0.0}, "ease": "step"}]
    if danca:
        ks += [{"t": round(danca[0], 2), "pose": {"danca": 0.0}, "ease": "step"},
               {"t": round(danca[1], 2), "pose": {"danca": round((danca[1] - danca[0]) * 0.8, 2)}, "ease": "linear"}]
    for t, pe in pisadas:
        ks += [{"t": round(max(0.02, t - 0.38), 2), "pose": {"pisa": 0.0, "pe": float(pe)}, "ease": "step"},
               {"t": round(t, 2), "pose": {"pisa": 1.0}, "ease": "linear", "in": 0.34},
               {"t": round(t + 0.28, 2), "pose": {"pisa": 0.0}, "ease": "step"}]
    ks += extra or []
    return {"id": "dino", "x": x, "y": y, "z": 2, "depth": depth, "pose": pose or {}, "keys": ks}


def danca_kid(x, turn, estilo=None, t0=0.0, y=None, **kw):
    a = {"x": x, "turn": turn, "acoes": [{"t": t0, "do": "dance", "style": estilo or next(ESTILOS), "dur": "resto"}]}
    if y is not None:
        a["y"] = y
    a.update(kw)
    return a


def pula_kid(x, turn, t, estilo=None):
    """Pula no 'tum'/'pulou' e volta a dançar."""
    return {"x": x, "turn": turn, "acoes": [{"t": 0.0, "do": "dance", "style": estilo or next(ESTILOS), "dur": round(max(0.3, t - 0.1), 2)},
                                            {"t": round(t, 2), "do": "jump", "dur": 0.8},
                                            {"t": round(t + 0.9, 2), "do": "dance", "style": "festa", "dur": "resto"}]}


def gato_pula(x, tempos, y=930, depth=0.6):
    """Piada que volta: o gato pula de susto a cada pisada do Dino."""
    ks = [{"t": 0.0, "pose": {"y": y, "assusta": 0.0, "rabo": 0.0}, "ease": "step"}]
    for t in tempos:
        ks += [{"t": round(max(0.03, t - 0.02), 2), "pose": {"y": y, "assusta": 0.0}}, {"t": round(t + 0.25, 2), "pose": {"y": y - 160, "assusta": 1.0}, "ease": "out"},
               {"t": round(t + 0.55, 2), "pose": {"y": y, "assusta": 0.3}, "ease": "in"}]
    return {"id": "gato", "x": x, "y": y, "z": 4, "depth": depth, "keys": ks}


partes: dict = {}

# ───────── intro: o chão treme, o Dino chega pela rua ─────────
P = [{"seg": 1.4}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1, "seg": 4.2}, {"seg": 0.0}]
T = planos_tempo("intro#1", P)
(a0, a1, _), (b0, b1, vb), (c0, c1, vc), (d0, d1, _), (e0, e1, _) = T
P[-1]["seg"] = round(e1 - e0, 2)
partes["intro"] = [
    {"seg": 1.4, "cenario": RUA, "camera": {"x": 1300, "y": 620, "zoom": 1.0, "zoom_fim": 1.05}, "tremor": [0.3, 0.9],
     "callout": [call(0.3, "TUM!", "laranja")], "titulo": "o chão treme"},
    {"linhas": 1, "cenario": RUA, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "callout": [call(0.4, "DINO PISA FORTE!", "verde")],
     "tremor": [0.6, 1.4, 2.2],
     "objetos": {"d": dino(2400, pisadas=[(0.6, 0), (1.4, 1), (2.2, 0)],
                           extra=[{"t": 0.0, "pose": {"x": 2500}, "ease": "step"}, {"t": round(b1 - b0 - 0.1, 2), "pose": {"x": 1700}, "ease": "linear",
                                                                                     "in": round(b1 - b0 - 0.2, 2)}])}},
    {"linhas": 1, "cenario": RUA, "camera": CAM, "tremor": [0.5],
     "objetos": {"d": dino(1750, pisadas=[(0.5, 1)])},
     "atores": {LA: {"x": -250, "y": 520, "turn": 0.4, "acoes": [{"t": 0.0, "do": "fly", "dur": 1.0, "to_x": 650, "to_y": 930},
                                                                {"t": 1.1, "do": "take", "strength": "surprised"}]},
                LU: {"x": -300, "y": 420, "turn": 0.4, "acoes": [{"t": 0.15, "do": "fly", "dur": 1.0, "to_x": 1000, "to_y": 930},
                                                                {"t": 1.2, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "seg": 4.2, "cenario": "danca_raios_verde", "fx": ["confete"], "callout": [call(0.15, "LAURINHA E LUISINHO!", "rosa")],
     "objetos": {"d": dino(1650, depth=0.55, y=1010, danca=(0.0, 4.2))},
     "atores": {LA: danca_kid(480, 0.25, "festa", y=1010, depth=1.0), LU: danca_kid(1100, -0.1, "lado", y=1010, depth=1.0)}},
    {"seg": P[-1]["seg"], "cenario": RUA, "camera": {"x": 1300, "y": 600, "zoom": 1.05, "zoom_fim": 1.15}, "titulo": "o Dino dança na rua",
     "tremor": [0.6, 2.0, 3.4],
     "objetos": {"d": dino(1500, pisadas=[(0.6, 0), (2.0, 1), (3.4, 0)])},
     "atores": {LA: pula_kid(700, 0.35, 0.65, "chute"), LU: pula_kid(2250, -0.35, 0.7, "joelho")}},
]


# ───────── verso: o Dino chega; o chão treme; tudo pula (bolo, gato, vovó) ─────────
def verso(key, n):
    P = [{"linhas": 2}, {"linhas": 2}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}]
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd), (e0, e1, ve), (f0, f1, vf) = planos_tempo(key, P)
    tb, tg, tv = tp(c0, vc, "pulou", default=0.6), tp(d0, vd, "pulou", default=0.6), tp(e0, ve, "pulo", default=0.8)
    passos_a = [(0.4 + 0.75 * i, i % 2) for i in range(int((a1 - a0 - 0.4) / 0.75))]
    return [
        {"linhas": 2, "cenario": RUA if n == 1 else JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.12},
         "callout": [call(1.6, "GRANDÃO E BONZINHO!", "verde")], "tremor": [t for t, _ in passos_a],
         "objetos": {"d": dino(1300, depth=0.85, pisadas=passos_a)},
         "atores": {LU: {"x": 2250, "turn": -0.4, "acoes": [{"t": 0.3, "do": "point", "dur": "resto"}]}} if n == 1 else
                   {LA: {"x": 450, "turn": 0.4, "expr": "surprised", "acoes": [{"t": 0.3, "do": "look_around", "dur": "resto"}]}}},
        # o caminho treme: câmera baixa nos pés do Dino
        {"linhas": 2, "cenario": RUA if n == 1 else JARDIM, "camera": {"x": 1350, "y": 800, "zoom": 1.6, "zoom_fim": 1.7},
         "callout": [call(tp(b0, vb, "treme", default=1.5), "TREME TUDO!", "laranja")],
         "tremor": [0.5, 1.3, 2.1, 2.9][: max(1, int((b1 - b0) / 0.8))],
         "objetos": {"d": dino(1350, depth=0.85, pisadas=[(0.5, 0), (1.3, 1), (2.1, 0), (2.9, 1)][: max(1, int((b1 - b0) / 0.8))])}},
        # o bolo pulou do prato
        {"linhas": 1, "cenario": COZINHA, "camera": {"x": 1300, "y": 640, "zoom": 1.35, "zoom_fim": 1.45}, "tremor": [max(0.05, tb - 0.1)],
         "callout": [call(tb + 0.1, "O BOLO PULOU!", "amarelo")],
         "objetos": {"mesa": {"id": "mesa", "x": 1300, "y": 930, "z": 1, "depth": 1.3},
                     "bolo": {"id": "bolo", "x": 1300, "y": MESA_Y, "z": 2, "depth": 0.6,
                              "keys": [{"t": 0.0, "pose": {"y": MESA_Y}, "ease": "step"}, {"t": max(0.05, tb - 0.02), "pose": {"y": MESA_Y}},
                                       {"t": tb + 0.3, "pose": {"y": MESA_Y - 170}, "ease": "out"}, {"t": tb + 0.65, "pose": {"y": MESA_Y}, "ease": "in"}]}}},
        # o gato pulou do sofá
        {"linhas": 1, "cenario": SALA, "camera": {"x": 2150, "y": 620, "zoom": 1.4, "zoom_fim": 1.5}, "tremor": [max(0.05, tg - 0.1)],
         "callout": [call(tg + 0.1, "O GATO PULOU!", "laranja")],
         "objetos": {"gato": {"id": "gato", "x": 2200, "y": 660, "z": 3, "depth": 0.75,
                              "keys": [{"t": 0.0, "pose": {"y": 660, "assusta": 0.0}, "ease": "step"}, {"t": max(0.05, tg - 0.02), "pose": {"y": 660}},
                                       {"t": tg + 0.3, "pose": {"y": 420, "assusta": 1.0, "miau": 1.0}, "ease": "out"},
                                       {"t": tg + 0.7, "pose": {"y": 660, "miau": 0.0}, "ease": "in"}]}}},
        # a vovó deu um pulo
        {"linhas": 1, "cenario": JARDIM if n == 1 else SALA, "camera": {"x": 1300, "y": 600, "zoom": 1.3, "zoom_fim": 1.4},
         "tremor": [max(0.05, tv - 0.1)], "callout": [call(tv + 0.1, "A VOVÓ PULOU!", "rosa")],
         "objetos": {"d": dino(2300, depth=0.7, pisadas=[(max(0.05, tv - 0.1), 1)])},
         "atores": {VO: {"x": 1300, "turn": 0.1, "expr": "surprised", "acoes": [{"t": round(max(0.05, tv - 0.05), 2), "do": "jump", "dur": 0.9}]}}},
        # "Ai, ai, devagar!": a vovó dá bronca e o Dino pisa de levinho, sem graça
        {"linhas": 1, "cenario": JARDIM if n == 1 else SALA, "camera": {"x": 1300, "y": 600, "zoom": 1.05, "zoom_fim": 1.12},
         "callout": [call(0.4, "DEVAGAR!", "vermelho")],
         "objetos": {"d": dino(1750, depth=0.8, extra=[{"t": 0.3, "pose": {"levinho": 0.0}}, {"t": 0.8, "pose": {"levinho": 1.0}, "ease": "out"}])},
         "atores": {VO: {"x": 750, "turn": 0.4, "acoes": [{"t": 0.1, "do": "shake_fist", "dur": "resto"}]}}},
    ]


partes["verso#1"] = verso("verso#1", 1)
partes["verso#2"] = verso("verso#2", 2)

CORES = ["verde", "laranja", "azul", "rosa"]


# ───────── refrão: "Tum, tum, tremeu!" (o Dino pisa, a tela treme) e "Quem pulou? Fui eu!" (o Luisinho pula) ─────────
def refrao(n):
    P = [{"linhas": 2}, {"linhas": 2}, {"linhas": 2}, {"linhas": 3 if n == 2 else 2}]
    T = planos_tempo(f"refrao#{n}", P)
    cen = [RUA, JARDIM, SALAO, SALAO][n - 1]
    out = []
    for i, (t0, t1, v) in enumerate(T):
        d = t1 - t0
        if i % 2 == 0:                                            # Tum, tum, tremeu!
            tums = tps(t0, v, "tum") or [d * 0.45, d * 0.6]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 600, "zoom": 1.1 if i == 0 else 1.25, "zoom_fim": 1.2 if i == 0 else 1.15},
                 "tremor": tums, "callout": [call(tums[0], "TUM, TUM!", "laranja"), call(tums[-1] + 0.5, "TREMEU!", "vermelho")],
                 "objetos": {"d": dino(1300 if i == 0 else 1600, depth=0.8, pisadas=[(t, k % 2) for k, t in enumerate(tums)])},
                 "atores": {LA: pula_kid(450 if i == 0 else 700, 0.35, tums[-1] + 0.05), LU: pula_kid(2150, -0.35, tums[-1] + 0.1)}}
            if i == 0:
                p["flash"] = True
                p["callout"].insert(0, call(0.1, "DINO PISA FORTE!", CORES[n - 1]))
        else:                                                     # Quem pulou? Fui eu!
            tf = tp(t0, v, "fui", default=d * 0.7)
            p = {"linhas": 3 if (n == 2 and i == 3) else 2, "cenario": cen,
                 "camera": "close:luisinho" if (i == 1 and n in (1, 3)) else {"x": 1100, "y": 620, "zoom": 1.3, "zoom_fim": 1.38},
                 "callout": [call(tf + 0.1, "FUI EU!", "azul")],
                 "atores": {LU: {"x": 1100 if i == 3 or n not in (1, 3) else 1300, "turn": 0.0,
                                 "acoes": [{"t": 0.1, "do": "pensar", "dur": round(max(0.4, tf - 0.4), 2)},
                                           {"t": round(tf, 2), "do": "jump", "dur": 0.8},
                                           {"t": round(tf + 0.9, 2), "do": "cheguei", "dur": "resto"}]}}}
            if not (i == 1 and n in (1, 3)):
                p["atores"][LA] = {"x": 1750, "turn": -0.35, "acoes": [{"t": 0.1, "do": "dance", "style": next(ESTILOS), "dur": round(max(0.4, tf), 2)},
                                                                       {"t": round(tf + 0.1, 2), "do": "laugh", "dur": "resto"}]}
            if n >= 3:
                p["fx"] = ["confete"]
            if not (i == 1 and n in (1, 3)):
                p["objetos"] = {"d": {**dino(1450, depth=0.6, danca=(0.0, d)), "z": 1}}
        out.append(p)
    return out


for n in (1, 2, 3, 4):
    partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos: bordão, o Dino ruge fofo, festa ─────────
def intervalo(key, n):
    b, bl = INFO[key]
    D = b["e"] - b["s"]
    if not bl:                                                    # intervalo 3: festa no salão, 3 planos com passos diferentes
        s1 = round(D / 3, 2)
        return [{"seg": s1, "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["confete"], "titulo": "festa",
                 "objetos": {"d": dino(1300, depth=0.8, danca=(0.0, s1))},
                 "atores": {LA: danca_kid(500, 0.3, "sapinho"), LU: danca_kid(2100, -0.3, "chute")}},
                {"seg": s1, "cenario": SALAO, "camera": {"x": 1300, "y": 640, "zoom": 1.3, "zoom_fim": 1.22}, "titulo": "festa",
                 "atores": {VO: danca_kid(1000, 0.3, "cintura"), LA: danca_kid(1650, -0.3, "joelho")}},
                {"seg": round(D - 2 * s1, 2), "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.0}, "fx": ["confete"],
                 "titulo": "festa", "tremor": [0.5, 1.7, 2.9],
                 "objetos": {"d": dino(1300, depth=0.8, pisadas=[(0.5, 0), (1.7, 1), (2.9, 0)])},
                 "atores": {LA: pula_kid(500, 0.3, 0.55, "marcha"), LU: pula_kid(2100, -0.3, 1.75, "pezinho"),
                            VO: danca_kid(800, 0.2, "palmas")}}]
    if n == 1:
        p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
        return [{"linhas": 1, "seg": p1, "cenario": RUA, "camera": "close:luisinho", "callout": [call(0.2, "QUE MASSA!", "azul")],
                 "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
                {"linhas": 1, "seg": 4.0, "cenario": "danca_bolinhas_verde", "fx": ["confete"], "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")],
                 "objetos": {"d": dino(1650, depth=0.55, y=1010, danca=(0.0, 4.0))},
                 "atores": {LA: danca_kid(480, 0.25, "cintura", y=1010, depth=1.0), LU: danca_kid(1100, -0.1, "sapinho", y=1010, depth=1.0)}},
                {"seg": round(D - p1 - 4.0, 2), "cenario": RUA, "camera": {"x": 1500, "y": 560, "zoom": 1.2, "zoom_fim": 1.3}, "titulo": "rugido fofo",
                 "callout": [call(0.6, "ROAAR!", "verde")],
                 "objetos": {"d": dino(1500, depth=0.85, extra=[{"t": 0.4, "pose": {"ruge": 0.0}}, {"t": 0.8, "pose": {"ruge": 1.0}, "ease": "out"},
                                                               {"t": 2.0, "pose": {"ruge": 1.0}}, {"t": 2.4, "pose": {"ruge": 0.0}}])},
                 "atores": {LA: {"x": 650, "turn": 0.35, "acoes": [{"t": 0.7, "do": "shock_reaction", "dur": 1.2}, {"t": 2.2, "do": "laugh", "dur": "resto"}]}}}]
    p1 = round(bl[0]["s"] - b["s"] - 0.15, 2)
    return [{"seg": p1, "cenario": SALA, "camera": {"x": 1300, "y": 600, "zoom": 1.3, "zoom_fim": 1.4}, "titulo": "o gato e o Dino",
             "objetos": {"d": dino(900, depth=0.75, extra=[{"t": 0.2, "pose": {"tchau": 0.0}}, {"t": 0.6, "pose": {"tchau": 1.0}, "ease": "out"}]),
                         "gato": {"id": "gato", "x": 2200, "y": 660, "z": 3, "depth": 0.75, "keys": [{"t": 0.0, "pose": {"aceno": 0.0}}, {"t": 0.8, "pose": {"aceno": 1.0}}]}}},
            {"linhas": 1, "seg": 4.0, "cenario": "danca_xadrez_verde", "fx": ["confete"], "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")],
             "objetos": {"d": dino(1650, depth=0.55, y=1010, danca=(0.0, 4.0))},
             "atores": {LA: danca_kid(480, 0.25, "chute", y=1010, depth=1.0), LU: danca_kid(1100, -0.1, "joelho", y=1010, depth=1.0)}},
            {"seg": round(D - p1 - 4.0, 2), "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": 1.05, "zoom_fim": 1.15}, "fx": ["confete"],
             "titulo": "festa", "objetos": {"d": dino(1300, depth=0.8, danca=(0.0, D - p1 - 4.0))},
             "atores": {VO: danca_kid(650, 0.3, "balanco"), LA: danca_kid(2050, -0.3, "gingado")}}]


partes["intervalo#1"] = intervalo("intervalo#1", 1)
partes["intervalo#2"] = intervalo("intervalo#2", 2)
partes["intervalo#3"] = intervalo("intervalo#3", 3)


# ───────── ponte: comandos (pé direito, pé esquerdo, pisa forte… tum!, pisa fraquinho em segredo) ─────────
def ponte(key, n):
    P = [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}]
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd) = planos_tempo(key, P)
    cen = CAMPO if n == 1 else SALAO
    td, te = tp(a0, va, "direito", default=1.2), tp(b0, vb, "esquerdo", default=1.2)
    tt = tp(c0, vc, "tum", default=1.6)
    pe_kid = lambda t: [{"t": 0.0, "do": "dance", "style": "pezinho", "dur": "resto"}]
    return [
        {"linhas": 1, "cenario": cen, "camera": {"x": 1300, "y": 640, "zoom": 1.2, "zoom_fim": 1.3}, "tremor": [td + 0.2],
         "callout": [call(td, "PÉ DIREITO!", "azul")], "objetos": {"d": dino(1600, depth=0.8, pisadas=[(td + 0.2, 1)])},
         "atores": {LU: {"x": 800, "turn": 0.35, "acoes": pe_kid(td)}}},
        {"linhas": 1, "cenario": cen, "camera": {"x": 1300, "y": 640, "zoom": 1.2, "zoom_fim": 1.3}, "tremor": [te + 0.2],
         "callout": [call(te, "PÉ ESQUERDO!", "verde")], "objetos": {"d": dino(1000, depth=0.8, pisadas=[(te + 0.2, 0)])},
         "atores": {LA: {"x": 1850, "turn": -0.35, "acoes": pe_kid(te)}}},
        # PISA FORTE… TUM!: pisada gigante, tremor grande, todo mundo pula
        {"linhas": 1, "cenario": cen, "camera": {"x": 1300, "y": 620, "zoom": 1.05, "zoom_fim": 1.2}, "tremor": [tt, tt + 0.15], "flash": True,
         "callout": [call(tt, "TUM!!!", "vermelho")], "objetos": {"d": dino(1300, depth=0.9, pisadas=[(tt, 1)])},
         "atores": {LA: pula_kid(500, 0.35, tt + 0.05, "marcha"), LU: pula_kid(2100, -0.35, tt + 0.08, "marcha")}},
        # pisa fraquinho, em segredo: o Dino na ponta do pé, a turma de fininho
        {"linhas": 1, "cenario": cen, "camera": {"x": 1300, "y": 600, "zoom": 1.25, "zoom_fim": 1.35}, "callout": [call(0.5, "PSSIU…", "roxo")],
         "objetos": {"d": dino(1650, depth=0.8, extra=[{"t": 0.0, "pose": {"levinho": 0.0}}, {"t": 0.5, "pose": {"levinho": 1.0}, "ease": "out"}])},
         "atores": {LU: {"x": 300, "turn": 0.35, "acoes": [{"t": 0.2, "do": "sneak", "to_x": 900}]}}},
    ]


partes["ponte#1"] = ponte("ponte#1", 1)
partes["ponte#2"] = ponte("ponte#2", 2)

# ───────── final: convite e tchau (o Dino de levinho, dando tchau) ─────────
partes["final#1"] = [
    {"linhas": 1, "cenario": RUA, "camera": "close:luisinho", "callout": [call(0.3, "GOSTOU DO DINO?", "verde")],
     "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.3, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LU: {"x": 680, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": RUA, "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "objetos": {"d": dino(2100, depth=0.6, extra=[{"t": 0.2, "pose": {"tchau": 0.0}}, {"t": 0.6, "pose": {"tchau": 1.0}, "ease": "out"}])},
     "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                LU: {"x": 1450, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LU: {"x": 600, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
]
partes["final#2"] = [
    {"linhas": 1, "cenario": RUA, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}, "fx": ["coracoes"], "tremor": [1.4],
     "callout": [call(0.5, "TCHAU!", "amarelo"), call(1.4, "TUM!", "laranja")],
     "objetos": {"d": dino(1700, depth=0.8, pisadas=[(1.4, 0)], extra=[{"t": 0.1, "pose": {"tchau": 0.0}}, {"t": 0.5, "pose": {"tchau": 1.0}, "ease": "out"}])},
     "atores": {LA: {"x": 600, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LU: {"x": 950, "turn": 0.2, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]}}},
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
    for p, (t0, t1, _) in zip(planos, planos_tempo(k_info, planos)):
        p["cantam"] = ["luisinho"]
        d = t1 - t0
        assert d >= 0.6, (chave, t0, t1)
        if p.get("tremor"):
            p["tremor"] = [round(t, 2) for t in p["tremor"] if 0.0 <= t < d - 0.15]
            obs = p.setdefault("objetos", {})
            if p["tremor"] and "gato" not in obs and not str(p.get("cenario", "")).startswith("danca_") and "d" in obs:
                gx = 2350 if obs["d"]["x"] < 1700 else 300
                obs["gato"] = gato_pula(gx, p["tremor"])
        for a in (p.get("atores") or {}).values():           # nenhuma ação começa depois do fim do plano
            a["acoes"] = [ac for ac in a.get("acoes", []) if ac["t"] < d - 0.3] or a.get("acoes", [])[:1]
        for o in (p.get("objetos") or {}).values():
            if o.get("keys"):
                ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                o["keys"] = transicoes(sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"]))

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0",
       "escala_personagens": 1.45,
       "nota": "Roteiro de 'Dino Pisa Forte' (take v1 de 19/11/2026, 2:44, Luisinho, estilo E9, nota de ouvido 4,2): o Dino chega "
               "pisando pela rua, a tela treme e tudo pula (bolo, gato, vovó); refrão com tum-tum e 'Fui eu!'; ponte de comandos "
               "(pé direito, esquerdo, pisa forte, de levinho); festa no salão. Gerado por scripts/roteiros/ep20_dino_pisa_forte.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = sum(len(v) for v in partes.values())
print("roteiro:", n, "planos ·", round(song["duration"] / n, 1), "s por plano")
for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    print(chave, [round(t1 - t0, 1) for t0, t1, _ in planos_tempo(k_info, planos)])
