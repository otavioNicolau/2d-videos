"""Roteiro verso a verso de 16 "Carnaval da Turminha" (take v1, 2:29, uma voz: Luisinho, estilo E5) → musicas/16_carnaval_da_turminha/roteiro.json.

O bloquinho no salão: cada um chega com a fantasia mais engraçada (sapo de princesa, formiga de leão, vovó bailarina,
vovô tubarão) e o Luisinho de sombrinha de frevo; a ponte manda a sombrinha pra cima, pra baixo, agacha e pula.
Planos de 3–7 s (as fantasias aparecem uma a uma). Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep16_carnaval_da_turminha.py
"""
from __future__ import annotations

import json
from pathlib import Path

from toonstudio.composition.clip_draft import _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "ep16-carnaval-da-turminha"
MUS = ROOT / "musicas" / "16_carnaval_da_turminha"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
SALAO = "plano_salao"
CAM = {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.06}
LA, LU = "laurinha", "luisinho"
SOMB = "sombrinha"


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


def call(t, text, color):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color}


def ator(x, turn=0.3, pose=None, acoes=None, **kw):
    d = {"x": x, "turn": turn, "acoes": acoes or [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}
    if pose:
        d["pose"] = pose
    d.update(kw)
    return d


def frevo(x, turn=0.3, **kw):
    return ator(x, turn, segura=SOMB, acoes=[{"t": 0.0, "do": "dance", "style": "frevo", "dur": "resto"}], **kw)


SAPO = lambda x, keys=None: {"id": "sapo", "x": x, "y": 935, "z": 2, "depth": 0.85, "pose": {"coroa": 1.0}, "keys": keys or []}
FANT = {"formiguinha": {"juba": 1.0}, "vovo": {"tutu": 1.0}, "vovozinho": {"tubarao": 1.0}}


def turma_toda(festa="festa"):
    """O bloco inteiro fantasiado (os dois na frente)."""
    return {"atores": {"formiguinha": ator(450, 0.3, FANT["formiguinha"], z=1, depth=0.85),
                       "vovo": ator(2150, -0.3, FANT["vovo"], z=1, depth=0.9),
                       "vovozinho": ator(1750, -0.2, FANT["vovozinho"], z=1, depth=0.9,
                                         acoes=[{"t": 0.0, "do": "dance", "style": "marcha", "dur": "resto"}]),
                       LA: frevo(950, 0.3), LU: frevo(1450, -0.2)},
            "objetos": {"sapo": SAPO(700, keys=[{"t": 0.0, "pose": {"pulo": 0.0}}])}}


partes: dict = {}

# ───────── intro: o salão enfeitado; o Luisinho chega de sombrinha; o grito do canal
P = starts("intro#1", [2, 1])
partes["intro"] = [
    {"linhas": 2, "cenario": SALAO, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["confete"],
     "callout": [call(2.4, "CARNAVAL DA TURMINHA!", "amarelo")],
     "atores": {LU: {"x": -250, "y": 520, "turn": 0.4, "segura": SOMB, "acoes": [{"t": 0.3, "do": "fly", "dur": 2.2, "to_x": 1300, "to_y": 930},
                                                                                  {"t": 2.8, "do": "dance", "style": "frevo", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "fx": ["confete"], "callout": [call(0.15, "LAURINHA E LUISINHO!", "rosa")],
     "atores": {LA: frevo(560, 0.25, y=1010, depth=1.15), LU: frevo(1360, -0.25, y=1010, depth=1.15)}},
]


def verso(key, n):
    P = starts(key, [2, 2, 2, 2])
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd) = P
    close = 1.15 if n == 1 else 1.3
    return [
        {"linhas": 2, "cenario": SALAO, "camera": CAM, "fx": ["confete"], "callout": [call(1.2, "CONFETE!", "verde")],
         "atores": {LU: frevo(1300, 0.0)}},
        {"linhas": 2, "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": close, "zoom_fim": close + 0.05},
         "callout": [call(0.4, "PRINCESA?!", "rosa"), call(1.7, "LEÃO!", "laranja")],
         "objetos": {"sapo": SAPO(1050, keys=[{"t": 0.0, "pose": {"pulo": 0.0, "croac": 0.0}}, {"t": 0.6, "pose": {"pulo": 1.0, "croac": 1.0}, "ease": "linear"},
                                             {"t": 1.0, "pose": {"croac": 0.0}}])},
         "atores": {"formiguinha": ator(1600, -0.3, FANT["formiguinha"], acoes=[{"t": 1.4, "do": "cheguei", "dur": "resto"}])}},
        {"linhas": 2, "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": close, "zoom_fim": close + 0.05},
         "callout": [call(0.4, "BAILARINA!", "rosa"), call(1.7, "TUBARÃO!", "azul")],
         "atores": {"vovo": ator(1000, 0.3, FANT["vovo"], acoes=[{"t": 0.0, "do": "turn", "to": -0.4}, {"t": 0.4, "do": "turn", "to": 0.4},
                                                                  {"t": 0.8, "do": "dance", "style": "bracos", "dur": "resto"}]),
                    "vovozinho": ator(1650, -0.3, FANT["vovozinho"], acoes=[{"t": 1.5, "do": "take"}, {"t": 2.2, "do": "laugh", "dur": "resto"}])}},
        {"linhas": 2, "cenario": SALAO, "camera": "medio:luisinho", "fx": ["estrelas"], "callout": [call(0.4, "SOMBRINHA!", "amarelo")],
         "atores": {LU: {"x": 1300, "turn": 0.1, "segura": SOMB, "acoes": [{"t": 0.1, "do": "cheguei", "dur": 1.0}, {"t": 1.3, "do": "jump", "dur": 0.9}]}}},
    ]


partes["verso#1"] = verso("verso#1", 1)
partes["verso#2"] = verso("verso#2", 2)

BG = {1: "danca_xadrez_verde", 2: "danca_bolinhas_rosa", 3: "danca_ondas_azul", 4: "danca_raios_laranja"}


def refrao(n):
    P = starts(f"refrao#{n}", [4, 4])
    t = turma_toda()
    p1 = {"linhas": 4, "cenario": SALAO, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}, "flash": True, "fx": ["confete"],
          "callout": [call(0.15, "CARNAVAL DA TURMINHA!", ["amarelo", "rosa", "verde", "laranja"][n - 1]), call(1.8, "ABRE A RODA!", "azul")],
          **t}
    t1 = P[1][1] - P[1][0]
    p2 = {"linhas": 4, "cenario": BG[n], "fx": ["confete" if n >= 3 else "estrelas"], "callout": [call(1.6, "NINGUÉM FICA SEM DANÇAR!", "rosa")],
          "atores": {LA: frevo(500, 0.25, y=1010, depth=1.15), LU: frevo(1420, -0.25, y=1010, depth=1.15)},
          "objetos": {"sapo": {"id": "sapo", "x": 960, "y": 1010, "z": 2, "depth": 0.8, "pose": {"coroa": 1.0},
                               "keys": [{"t": round(i * 0.9, 2), "pose": {"pulo": float(i % 2)}, "ease": "linear"} for i in range(int(t1 / 0.9))]}}}
    if n == 4:
        dd = round(t1, 2)
        for w in (LA, LU):
            p2["atores"][w]["acoes"] = [{"t": 0.0, "do": "dance", "style": "frevo", "dur": round(dd - 1.6, 2)}, {"t": round(dd - 1.5, 2), "do": "laugh", "dur": "resto"}]
    return [p1, p2]


for n in (1, 2, 3, 4):
    partes[f"refrao#{n}"] = refrao(n)


def intervalo(key, n):
    b, bl = INFO[key]
    if not bl:                                   # pausa só de teclado: o bloco desfila pelo salão
        d = round(b["e"] - b["s"], 2)
        desf = lambda w, x0, extra: {"x": x0, "turn": 0.4, "pose": extra, "acoes": [{"t": 0.0, "do": "walk", "to_x": x0 + 1600}]}
        return [{"seg": d, "cenario": SALAO, "camera": CAM, "titulo": "o bloco desfila", "fx": ["confete"],
                 "atores": {"vovozinho": desf("vovozinho", -400, FANT["vovozinho"]), "vovo": desf("vovo", -700, FANT["vovo"]),
                            "formiguinha": desf("formiguinha", -1000, FANT["formiguinha"]),
                            LA: {**frevo(800, 0.3), "z": 4}, LU: {**frevo(1800, -0.3), "z": 4}}}]
    P = starts(key, [1, 1])
    return [{"linhas": 1, "cenario": "danca_raios_roxo" if n == 1 else "danca_bolinhas_azul", "camera": "medio:luisinho", "fx": ["confete"],
             "callout": [call(0.2, "ZUM-ZUM, QUE MASSA!", "amarelo")],
             "atores": {LU: {"x": 960, "segura": SOMB, "acoes": [{"t": 0.1, "do": "bacana", "dur": 1.4}, {"t": 1.6, "do": "dance", "style": "frevo", "dur": "resto"}]}}},
            {"linhas": 1, "cenario": SALAO, "camera": CAM, "fx": ["confete"], "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")],
             **turma_toda()}]


partes["intervalo#1"] = intervalo("intervalo#1", 1)
partes["intervalo#2"] = intervalo("intervalo#2", 2)
partes["intervalo#3"] = intervalo("intervalo#3", 3)


def ponte(key):
    (a0, a1, va), (b0, b1, vb) = starts(key, [2, 2])
    up = [{"t": 0.0, "pose": {"hand_n_y": -170, "hand_n_x": 70}}]
    return [
        {"linhas": 2, "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": 1.2, "zoom_fim": 1.25},
         "callout": [call(0.2, "PRA CIMA!", "amarelo"), call(round(va[-1]["s"] - a0, 2) if len(va) > 1 else 1.4, "PRA BAIXO!", "azul")],
         "atores": {LA: {"x": 1000, "turn": 0.3, "segura": SOMB, "acoes": [{"t": 0.0, "do": "dance", "style": "bracos", "dur": "resto"}]},
                    LU: {"x": 1600, "turn": -0.3, "segura": SOMB, "acoes": [{"t": 0.0, "do": "dance", "style": "bracos", "dur": "resto"}]}}},
        {"linhas": 2, "cenario": SALAO, "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.1}, "fx": ["confete"],
         "callout": [call(0.2, "AGACHA!", "laranja"), call(round(vb[-1]["s"] - b0, 2) if len(vb) > 1 else 1.5, "PULA!", "verde")],
         "atores": {LA: {"x": 950, "turn": 0.3, "segura": SOMB, "acoes": [{"t": 0.0, "do": "dance", "style": "agacha", "dur": round(max(0.6, (vb[-1]["s"] - b0) - 0.2), 2) if len(vb) > 1 else 1.3},
                                                                      {"t": round((vb[-1]["s"] - b0) if len(vb) > 1 else 1.5, 2), "do": "jump", "dur": 1.0}]},
                    LU: {"x": 1650, "turn": -0.3, "segura": SOMB, "acoes": [{"t": 0.0, "do": "dance", "style": "agacha", "dur": round(max(0.6, (vb[-1]["s"] - b0) - 0.2), 2) if len(vb) > 1 else 1.3},
                                                                         {"t": round((vb[-1]["s"] - b0 + 0.1) if len(vb) > 1 else 1.6, 2), "do": "jump", "dur": 1.0}]}},
         "objetos": {"sapo": SAPO(1300, keys=[{"t": 0.0, "pose": {"pulo": 0.0}}, {"t": round((vb[-1]["s"] - b0) if len(vb) > 1 else 1.5, 2), "pose": {"pulo": 0.0}},
                                              {"t": round((vb[-1]["s"] - b0 + 0.7) if len(vb) > 1 else 2.2, 2), "pose": {"pulo": 1.0}, "ease": "linear"}])}}]


partes["ponte#1"] = ponte("ponte#1")
partes["ponte#2"] = ponte("ponte#2")

partes["final#1"] = [
    {"linhas": 1, "cenario": "danca_raios_azul", "camera": "close:luisinho", "callout": [call(0.3, "GOSTOU?", "rosa")],
     "atores": {LU: {"x": 960, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.4, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LU: {"x": 680, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "plano_casa_frente", "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                LU: {"x": 1450, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LU: {"x": 600, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
]
t = turma_toda()
for w in t["atores"]:
    t["atores"][w]["acoes"] = [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 4.0}, {"t": 4.2, "do": "dance", "style": "festa", "dur": "resto"}]
partes["final#2"] = [{"linhas": 1, "cenario": SALAO, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["confete"],
                      "callout": [call(1.6, "TCHAU!", "amarelo")], **t}]

for chave, planos in partes.items():
    for p in planos:
        p["cantam"] = ["luisinho"]

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0",
       "nota": "Roteiro de 'Carnaval da Turminha' (take v1 de 18/11/2026, 2:29, uma voz — Luisinho, estilo E5): o bloquinho no salão com as "
               "fantasias trocadas (sapo de princesa, formiga de leão, vovó bailarina, vovô tubarão) e o Luisinho de sombrinha de frevo; "
               "ponte de comandos de frevo. Gerado por scripts/roteiros/ep16_carnaval_da_turminha.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = sum(len(v) for v in partes.values())
print("roteiro:", n, "planos ·", round(song["duration"] / n, 1), "s por plano")
