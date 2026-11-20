"""Roteiro verso a verso de 12 "Méé, Carneirinho!" (take v2, 2:20) → musicas/12_mee_carneirinho/roteiro.json.

O carneirinho é o "chefe" da brincadeira: a cada "o carneirinho mandou…" ele dá um comando e TODO MUNDO faz junto
(pular, sentar, girar, abaixar, palma, pé, dançar, abraçar). As boquinhas do carneirinho (méé!) e os passos dele
seguem as palavras e as batidas reais da música (analise/letra.json + song.json).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep12_mee_carneirinho.py
"""
from __future__ import annotations

import json
from pathlib import Path

from toonstudio.composition.clip_draft import _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "laurinha" / "ep12-mee-carneirinho"
MUS = ROOT / "canais" / "laurinha" / "musicas" / "12_mee_carneirinho"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
CAMPO = "plano_campo"
CAM = {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.06}
B = {"blusa": 1.0}                                  # depois do verso 2 a turma fica de blusinha de lã


def bloco_info():
    out, occ = {}, {}
    for b in blocos(song):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        bl = [l for l in LINES if b["s"] - 0.05 <= l["s"] < b["e"] - 0.05]
        out[f"{b['tipo']}#{occ[b['tipo']]}"] = (b, bl)
    return out


INFO = bloco_info()


def starts(key: str, linhas: list[int]) -> list[tuple[float, float, list]]:
    """(início, fim, versos) de cada plano — mesma conta do clip_draft.roteiro_bloco."""
    b, bl = INFO[key]
    res, li = [], 0
    for k, n in enumerate(linhas):
        st = b["s"] if k == 0 else _snap(bl[li]["s"] - 0.12, BEATS)
        res.append([st, None, bl[li:li + n]])
        li += n
    for k in range(len(res)):
        res[k][1] = res[k + 1][0] if k + 1 < len(res) else b["e"]
    return [tuple(r) for r in res]


def palavras(versos, *alvos):
    alvos = tuple(a.lower() for a in alvos)
    return [w for l in versos for w in l["words"] if w["w"].lower().strip("!?,.…()") in alvos]


def mee_keys(t0, versos, extra=None):
    """Boquinha do carneirinho no 'Méé!' (abre na palavra, fecha no fim)."""
    ks = [{"t": 0.0, "pose": {"mee": 0.0}}]
    for w in palavras(versos, "méé", "mee", "méé!"):
        a, e = round(w["s"] - t0, 2), round(max(w["e"], w["s"] + 0.35) - t0, 2)
        ks += [{"t": max(0.0, a - 0.05), "pose": {"mee": 0.0}}, {"t": a + 0.06, "pose": {"mee": 1.0}, "ease": "out"},
               {"t": e, "pose": {"mee": 0.0}, "ease": "in"}]
    return ks + (extra or [])


def balanco(t0, t1, amp=1.0):
    """Carneirinho dançando: inclina de um lado para o outro a cada batida."""
    ks, s = [], 1
    for b in BEATS:
        if t0 <= b < t1:
            ks.append({"t": round(b - t0, 3), "pose": {"balanco": s * amp}, "ease": "inout"})
            s = -s
    return ks


def pulos(t0, t1, cada=2):
    """Pulinhos no tempo: pulo 0→1 (um arco) a cada `cada` batidas, ida e volta."""
    ks, v = [{"t": 0.0, "pose": {"pulo": 0.0}}], 0.0
    bs = [b for b in BEATS if t0 <= b < t1][::cada]
    for a in bs:
        v = 1.0 - v
        ks.append({"t": round(a - t0 + 0.4 * cada * 0.44, 3), "pose": {"pulo": v}, "ease": "linear"})
    return ks


def carneiro(x=1300, y=930, depth=1.0, z=2, lado=1, keys=None, pose=None):
    return {"id": "carneirinho", "x": x, "y": y, "z": z, "depth": depth, "pose": {"lado": lado, **(pose or {})}, "keys": keys or []}


def call(t, text, color):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color}


def t_palavra(t0, versos, *alvos, default=0.4):
    ws = palavras(versos, *alvos)
    return round(ws[0]["s"] - t0, 2) if ws else default


partes: dict = {}

# ───────── intro (0–15 s): o campo, o carneirinho pula na tela no "Méé!", a turma chega voando
(a0, a1, v0), (b0, _fim, v1) = starts("intro#1", [1, 1])
seg_ini = v1[-1]["e"]
b1 = seg_ini
partes["intro"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08},
     "callout": [call(t_palavra(a0, v0, "méé"), "MÉÉ!", "rosa")],
     "objetos": {"carneirinho": carneiro(1300, keys=[{"t": 0.0, "pose": {"x": 2900}}, {"t": 1.8, "pose": {"x": 1300}, "ease": "out"}]
                                         + pulos(a0, a0 + 1.8, 1) + mee_keys(a0, v0)[1:])}},
    {"linhas": 1, "cenario": CAMPO, "camera": "aberto",
     "callout": [call(0.3, "MÉÉ, CARNEIRINHO!", "amarelo")],
     "objetos": {"carneirinho": carneiro(1300, keys=mee_keys(b0, v1) + balanco(b0, b1))},
     "atores": {"laurinha": {"x": -300, "y": 600, "turn": 0.4, "acoes": [{"t": 0.2, "do": "fly", "dur": 2.2, "to_x": 860, "to_y": 930}]},
                "luisinho": {"x": 2900, "y": 560, "turn": -0.4, "acoes": [{"t": 0.5, "do": "fly", "dur": 2.2, "to_x": 1760, "to_y": 930}]}}},
    {"seg": round(_fim - seg_ini, 2), "cenario": CAMPO, "camera": {"x": 1300, "y": 600, "zoom": 1.12, "zoom_fim": 1.18},
     "titulo": "a turma dança com o carneirinho", "fx": ["notas"],
     "objetos": {"carneirinho": carneiro(1300, keys=balanco(seg_ini, 15.1) + pulos(seg_ini, 15.1, 4))},
     "atores": {"laurinha": {"x": 860, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "pulinho", "dur": "resto"}]},
                "luisinho": {"x": 1760, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "gingado", "dur": "resto"}]}}},
]

# ───────── verso 1 (Laurinha): lá no campo tem um carneirinho; ele manda e a gente faz
P = starts("verso#1", [1, 1, 1, 1])
partes["verso#1"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": "medio:laurinha", "callout": [call(t_palavra(P[0][0], P[0][2], "olha"), "OLHA!", "azul")],
     "atores": {"laurinha": {"x": 900, "turn": 0.4, "acoes": [{"t": 0.3, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1500, "y": 560, "zoom": 1.2, "zoom_fim": 1.26},
     "callout": [call(t_palavra(P[1][0], P[1][2], "méé"), "MÉÉ!", "rosa")],
     "objetos": {"cerca": {"id": "cerquinha", "x": 1500, "y": 960, "z": 3, "depth": 1.2},
                 "carneirinho": carneiro(1500, depth=1.0, keys=[{"t": 0.0, "pose": {"y": 1300}}, {"t": 0.5, "pose": {"y": 930}, "ease": "back"}]
                                         + mee_keys(P[1][0], P[1][2]))}},
    {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 520, "zoom": 1.25, "zoom_fim": 1.3},
     "callout": [call(1.0, "FOFINHO!", "amarelo")],
     "objetos": {"carneirinho": carneiro(1300, keys=balanco(P[2][0], P[2][1], 0.5))},
     "atores": {"laurinha": {"x": 700, "y": 700, "fly": 1, "turn": 0.4,
                             "acoes": [{"t": 0.1, "do": "fly", "dur": 1.2, "to_x": 1260, "to_y": 520}, {"t": 1.4, "do": "abraco", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": "aberto", "callout": [call(t_palavra(P[3][0], P[3][2], "bora"), "BORA!", "verde")],
     "objetos": {"carneirinho": carneiro(1300, keys=mee_keys(P[3][0], P[3][2], [{"t": 0.3, "pose": {"mee": 1.0}}, {"t": 0.8, "pose": {"mee": 0.0}}]))},
     "atores": {"laurinha": {"x": 850, "turn": 0.4, "acoes": [{"t": 0.1, "do": "cheguei", "dur": 1.2}, {"t": 1.4, "do": "jump", "dur": 0.8}]},
                "luisinho": {"x": 1760, "turn": -0.4, "acoes": [{"t": 0.3, "do": "cheguei", "dur": 1.2}, {"t": 1.5, "do": "jump", "dur": 0.8}]}}},
]


# ───────── refrões: "Méé, carneirinho!" ×2 dançando · "O carneirinho mandou… (O quê?)" · TODO MUNDO faz o comando
DANCA_BG = {1: ("danca_xadrez_verde", "danca_bolinhas_rosa"), 2: ("danca_ondas_azul", "danca_raios_laranja"),
            3: ("danca_xadrez_azul", "danca_bolinhas_amarelo"), 4: ("danca_raios_rosa", "danca_ondas_verde")}
PASSOS = {1: ("pulinho", "gingado"), 2: ("bracos", "lado"), 3: ("twist", "passinho"), 4: ("festa", "festa")}
CORES = {1: "amarelo", 2: "rosa", 3: "azul", 4: "verde"}


def danca_mee(n, t0, t1, versos, bg, ab=False):
    pl, pu = PASSOS[n]
    blusa = B if n >= 2 else {}
    p = {"linhas": 2, "cenario": bg, "fx": ["notas" if ab else "estrelas"],
         "callout": [call(0.15, "MÉÉ, CARNEIRINHO!", CORES[n])],
         "objetos": {"carneirinho": carneiro(960, 1010, depth=0.95, z=2, keys=mee_keys(t0, versos) + balanco(t0, t1))},
         "atores": {"laurinha": {"x": 470, "y": 1010, "depth": 1.15, "turn": 0.25, "pose": blusa,
                                 "acoes": [{"t": 0.0, "do": "dance", "style": pl, "dur": "resto"}]},
                    "luisinho": {"x": 1450, "y": 1010, "depth": 1.15, "turn": -0.25, "pose": blusa,
                                 "acoes": [{"t": 0.0, "do": "dance", "style": pu, "dur": "resto"}]}}}
    if not ab:
        p["flash"] = True
    return p


def mandou(n, t0, t1, versos):
    blusa = B if n >= 2 else {}
    dur = t1 - t0
    tq = min(t_palavra(t0, versos, "quê", "que", default=1.4), round(dur - 0.5, 2))
    fala = [{"t": 0.05, "pose": {"mee": 0.0}}]
    for w in [w for l in versos for w in l["words"]][:3]:                     # "O carneirinho mandou…": boquinha falando
        a = round(w["s"] - t0, 2)
        fala += [{"t": a, "pose": {"mee": 0.8}}, {"t": a + 0.18, "pose": {"mee": 0.2}}]
    fala = [k for k in fala if k["t"] < tq - 0.1] + [{"t": round(tq - 0.1, 2), "pose": {"mee": 0.0}}]
    return {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1250, "y": 470, "zoom": 1.45, "zoom_fim": 1.5},
            "callout": [call(tq, "O QUÊ?", "laranja")],
            "objetos": {"carneirinho": carneiro(1300, keys=fala)},
            "atores": {"laurinha": {"x": 930, "turn": 0.45, "pose": blusa, "acoes": [{"t": round(max(0.1, min(tq - 0.2, dur - 0.6)), 2), "do": "pensar", "dur": "resto"}]}}}


def comando(n, t0, t1, versos, texto, cor, la, lu, carn_keys, fx=None, cam=None):
    blusa = B if n >= 2 else {}
    p = {"linhas": 1, "cenario": CAMPO, "camera": cam or {"x": 1300, "y": 560, "zoom": 1.08, "zoom_fim": 1.14},
         "callout": [call(0.2, texto, cor)],
         "objetos": {"carneirinho": carneiro(1300, keys=carn_keys)},
         "atores": {"laurinha": {"x": 820, "turn": 0.35, "pose": blusa, "acoes": la},
                    "luisinho": {"x": 1800, "turn": -0.35, "pose": blusa, "acoes": lu}}}
    if fx:
        p["fx"] = fx
    return p


def refrao(n, cmd1, cmd2):
    key = f"refrao#{n}"
    P = starts(key, [2, 1, 1, 2, 1, 1])
    bg1, bg2 = DANCA_BG[n]
    return [danca_mee(n, P[0][0], P[0][1], P[0][2], bg1),
            mandou(n, P[1][0], P[1][1], P[1][2]),
            cmd1(P[2][0], P[2][1], P[2][2]),
            danca_mee(n, P[3][0], P[3][1], P[3][2], bg2, ab=True),
            mandou(n, P[4][0], P[4][1], P[4][2]),
            cmd2(P[5][0], P[5][1], P[5][2])]


def c_pular(t0, t1, v):
    return comando(1, t0, t1, v, "PULA!", "amarelo", [{"t": 0.15, "do": "jump", "dur": 0.9}, {"t": 1.1, "do": "jump", "dur": 0.8}],
                   [{"t": 0.25, "do": "jump", "dur": 0.9}, {"t": 1.2, "do": "jump", "dur": 0.8}],
                   [{"t": 0.0, "pose": {"pulo": 0.0}}, {"t": 0.9, "pose": {"pulo": 1.0}, "ease": "linear"},
                    {"t": 1.8, "pose": {"pulo": 0.0}, "ease": "linear"}])


def c_sentar(t0, t1, v):
    return comando(1, t0, t1, v, "SENTEI!", "verde", [{"t": 0.3, "do": "sit"}], [{"t": 0.4, "do": "sit"}],
                   [{"t": 0.0, "pose": {"senta": 0.0}}, {"t": 0.5, "pose": {"senta": 1.0}, "ease": "out"}])


def c_girar(t0, t1, v):
    gira = []
    for i, tt in enumerate((0.2, 0.5, 0.8, 1.1)):
        gira.append({"t": tt, "pose": {"lado": -1 if i % 2 == 0 else 1}})
    return comando(2, t0, t1, v, "GIREI!", "roxo",
                   [{"t": 0.15, "do": "turn", "to": -0.5}, {"t": 0.55, "do": "turn", "to": 0.5}, {"t": 0.95, "do": "turn", "to": -0.5},
                    {"t": 1.35, "do": "turn", "to": 0.35}],
                   [{"t": 0.2, "do": "turn", "to": 0.5}, {"t": 0.6, "do": "turn", "to": -0.5}, {"t": 1.0, "do": "turn", "to": 0.5},
                    {"t": 1.4, "do": "turn", "to": -0.35}], [{"t": 0.0, "pose": {"lado": 1}}] + gira, fx=["estrelas"])


def c_abaixar(t0, t1, v):
    return comando(2, t0, t1, v, "ABAIXEI!", "azul", [{"t": 0.0, "do": "dance", "style": "agacha", "dur": "resto"}],
                   [{"t": 0.0, "do": "dance", "style": "agacha", "dur": "resto"}],
                   [{"t": 0.0, "pose": {"senta": 0.0}}, {"t": 0.4, "pose": {"senta": 0.7}, "ease": "out"}])


def c_palma(t0, t1, v):
    return comando(3, t0, t1, v, "PLÁ, PLÁ!", "rosa", [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}],
                   [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}], balanco(t0, t1), fx=["estrelas"])


def c_pe(t0, t1, v):
    pe, s = [], 0.0
    for b in BEATS:
        if t0 <= b < t1:
            s = 1.0 - s
            pe.append({"t": round(b - t0, 3), "pose": {"pe": s}, "ease": "out"})
    return comando(3, t0, t1, v, "PÁ, PÁ!", "laranja", [{"t": 0.0, "do": "dance", "style": "pezinho", "dur": "resto"}],
                   [{"t": 0.0, "do": "dance", "style": "pezinho", "dur": "resto"}], pe)


def c_dancar(t0, t1, v):
    return comando(4, t0, t1, v, "DANCEI!", "rosa", [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}],
                   [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}], balanco(t0, t1) + pulos(t0, t1, 2), fx=["notas"])


def c_abracar(t0, t1, v):
    p = comando(4, t0, t1, v, "ABRAÇO!", "vermelho", [{"t": 0.2, "do": "abraco", "dur": "resto"}], [{"t": 0.3, "do": "abraco", "dur": "resto"}],
                [{"t": 0.0, "pose": {"lid": 0.0}}, {"t": 0.6, "pose": {"lid": 1.0}}], fx=["coracoes"],
                cam={"x": 1300, "y": 560, "zoom": 1.15, "zoom_fim": 1.25})
    p["atores"]["laurinha"]["x"], p["atores"]["luisinho"]["x"] = 980, 1700
    return p


partes["refrao#1"] = refrao(1, c_pular, c_sentar)
partes["refrao#2"] = refrao(2, c_girar, c_abaixar)
partes["refrao#3"] = refrao(3, c_palma, c_pe)
partes["refrao#4"] = refrao(4, c_dancar, c_abracar)

# ───────── intervalos (bordões)
P = starts("intervalo#1", [1, 1])
partes["intervalo#1"] = [
    {"linhas": 1, "cenario": "danca_raios_roxo", "camera": "close:laurinha", "callout": "BORA, TURMINHA!",
     "atores": {"laurinha": {"x": 960, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": CAM, "fx": ["confete"], "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")],
     "objetos": {"carneirinho": carneiro(1300, keys=balanco(P[1][0], P[1][1]) + pulos(P[1][0], P[1][1], 2))},
     "atores": {"laurinha": {"x": 820, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                "luisinho": {"x": 1800, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}}},
]
partes["intervalo#2"] = [
    {"linhas": 1, "cenario": "danca_bolinhas_azul", "camera": "medio:luisinho", "fx": ["confete"], "callout": [call(0.2, "ZUM-ZUM, QUE MASSA!", "amarelo")],
     "atores": {"luisinho": {"x": 960, "pose": B, "acoes": [{"t": 0.1, "do": "bacana", "dur": 1.4}, {"t": 1.6, "do": "dance", "style": "festa", "dur": "resto"}]}}},
]

# ───────── verso 2 (Luisinho): brrr, friozinho; o vento sopra; a lã do carneirinho vira blusinha quentinha
P = starts("verso#2", [1, 1, 1, 1, 1])
partes["verso#2"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": "medio:luisinho", "callout": [call(t_palavra(P[0][0], P[0][2], "brrr"), "BRRR!", "azul")],
     "atores": {"luisinho": {"x": 1500, "turn": -0.2, "expr": "scared", "acoes": [{"t": 0.1, "do": "shock_reaction", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": CAM, "callout": [call(t_palavra(P[1][0], P[1][2], "uuuu"), "UUUU!", "roxo")],
     "objetos": {"vento": {"id": "vento", "x": 1300, "y": 700, "z": 4, "depth": 1.7, "keys": [{"t": 0.0, "pose": {"x": 300}}, {"t": 1.8, "pose": {"x": 2300}, "ease": "linear"}]},
                 "carneirinho": carneiro(1300, keys=balanco(P[1][0], P[1][1], 0.6))},
     "atores": {"luisinho": {"x": 1850, "turn": -0.4, "expr": "scared", "acoes": [{"t": 0.0, "do": "shock_reaction", "dur": "resto"}]},
                "laurinha": {"x": 760, "turn": 0.4, "expr": "scared", "acoes": [{"t": 0.2, "do": "shock_reaction", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 500, "zoom": 1.4, "zoom_fim": 1.48}, "callout": [call(0.4, "LÃ QUENTINHA!", "amarelo")],
     "objetos": {"carneirinho": carneiro(1300, keys=[{"t": 0.0, "pose": {"mee": 0.0}}, {"t": 0.6, "pose": {"mee": 0.6}}, {"t": 1.1, "pose": {"mee": 0.0}}]
                                         + balanco(P[2][0], P[2][1], 0.4))}},
    {"linhas": 1, "cenario": CAMPO, "camera": "medio:luisinho", "flash": True, "fx": ["estrelas"],
     "callout": [call(t_palavra(P[3][0], P[3][2], "blusinha", default=0.5) + 0.6, "BLUSINHA!", "rosa")],
     "atores": {"luisinho": {"x": 1300, "turn": 0.1, "pose": B, "expr": "joy", "acoes": [{"t": 0.2, "do": "cheguei", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": CAM, "fx": ["coracoes"], "callout": [call(t_palavra(P[4][0], P[4][2], "hum", default=1.6), "HUM!", "laranja")],
     "objetos": {"carneirinho": carneiro(1300, keys=balanco(P[4][0], P[4][1], 0.5))},
     "atores": {"laurinha": {"x": 820, "turn": 0.35, "pose": B, "acoes": [{"t": 0.1, "do": "abraco", "dur": "resto"}]},
                "luisinho": {"x": 1800, "turn": -0.35, "pose": B, "acoes": [{"t": 0.2, "do": "abraco", "dur": "resto"}]}}},
]

# ───────── ponte (2×): pula a cerquinha, come capim, faz méé… congelou! de novo!
CERCA = {"id": "cerquinha", "x": 1300, "y": 950, "z": 3, "depth": 1.0}


def pula_cerca(t0, t1, v, turma=False):
    th = t_palavra(t0, v, "hop", default=0.9)
    k = [{"t": 0.0, "pose": {"x": 700, "pulo": 0.0}}, {"t": max(0.3, th - 0.5), "pose": {"x": 850, "pulo": 0.0}},
         {"t": th + 0.25, "pose": {"x": 1650, "pulo": 1.0}, "ease": "linear"}]
    p = {"linhas": 1, "cenario": CAMPO, "camera": CAM, "callout": [call(th, "HOP!", "laranja")],
         "objetos": {"cerca": dict(CERCA), "carneirinho": carneiro(700, z=4, keys=k, pose={"altura": 2.3})}}
    if turma:
        p["atores"] = {"laurinha": {"x": 1120, "y": 900, "z": 1, "depth": 0.85, "turn": 0.2, "pose": B, "acoes": [{"t": 0.1, "do": "jump", "dur": 0.9}, {"t": 1.0, "do": "cheguei", "dur": "resto"}]},
                       "luisinho": {"x": 1480, "y": 900, "z": 1, "depth": 0.85, "turn": -0.2, "pose": B, "acoes": [{"t": 0.2, "do": "jump", "dur": 0.9}, {"t": 1.1, "do": "cheguei", "dur": "resto"}]}}
    return p


def come_capim(t0, t1, v, turma=False):
    tn = t_palavra(t0, v, "nhac", default=1.0)
    p = {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1350, "y": 600, "zoom": 1.35, "zoom_fim": 1.4},
         "callout": [call(tn, "NHAC!", "verde")],
         "objetos": {"capim": {"id": "capim", "x": 1600, "y": 960, "z": 3, "depth": 1.0,
                               "keys": [{"t": 0.0, "pose": {"come": 0.0}}, {"t": tn, "pose": {"come": 0.0}}, {"t": tn + 0.2, "pose": {"come": 0.8}, "ease": "out"}]},
                     "carneirinho": carneiro(1250, keys=[{"t": 0.0, "pose": {"come": 0.0, "mee": 0.0}}, {"t": max(0.2, tn - 0.3), "pose": {"come": 1.0}, "ease": "inout"},
                                                         {"t": tn, "pose": {"mee": 0.7}}, {"t": tn + 0.25, "pose": {"mee": 0.0}},
                                                         {"t": tn + 0.6, "pose": {"come": 0.0}, "ease": "inout"}])}}
    if turma:                                  # o Luisinho tenta comer capim também… e ri
        p["atores"] = {"luisinho": {"x": 1900, "turn": -0.4, "pose": B, "acoes": [{"t": 0.1, "do": "eat", "dur": 1.0}, {"t": 1.2, "do": "laugh", "dur": "resto"}]}}
    return p


def faz_mee(t0, t1, v):
    return {"linhas": 1, "cenario": CAMPO, "camera": CAM, "callout": [call(t_palavra(t0, v, "méé", default=0.8), "MÉÉ!", "rosa")],
            "objetos": {"carneirinho": carneiro(1300, keys=mee_keys(t0, v) + balanco(t0, t1))},
            "atores": {"laurinha": {"x": 820, "turn": 0.35, "pose": B, "acoes": [{"t": 0.0, "do": "dance", "style": "pulinho", "dur": "resto"}]},
                       "luisinho": {"x": 1800, "turn": -0.35, "pose": B, "acoes": [{"t": 0.0, "do": "dance", "style": "pulinho", "dur": "resto"}]}}}


def estatua(t0, t1, v, pose_la="perna", pose_lu="bracos"):
    return {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 560, "zoom": 1.1, "zoom_fim": 1.1}, "flash": True,
            "callout": [call(0.1, "ESTÁTUA!", "vermelho")],
            "objetos": {"carneirinho": carneiro(1300, pose={"pe": 1.0, "mee": 0.5})},
            "atores": {"laurinha": {"x": 820, "turn": 0.35, "pose": B, "acoes": [{"t": 0.0, "do": "estatua", "pose": pose_la, "dur": "resto"}]},
                       "luisinho": {"x": 1800, "turn": -0.35, "pose": B, "acoes": [{"t": 0.0, "do": "estatua", "pose": pose_lu, "dur": "resto"}]}}}


P = starts("ponte#1", [1, 1, 1])
partes["ponte#1"] = [pula_cerca(*P[0]), come_capim(*P[1]), faz_mee(*P[2])]
P = starts("ponte#2", [1, 1, 1, 1, 1])
partes["ponte#2"] = [
    estatua(*P[0]),
    {"linhas": 1, "cenario": "danca_raios_vermelho", "camera": "close:laurinha", "callout": [call(0.2, "DE NOVO!", "amarelo")],
     "atores": {"laurinha": {"x": 960, "pose": B, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    pula_cerca(*P[2], turma=True), come_capim(*P[3], turma=True), faz_mee(*P[4])]
P = starts("ponte#3", [1])
partes["ponte#3"] = [estatua(*P[0], pose_la="bracos", pose_lu="perna")]

# ───────── verso 3 (Laurinha): esconde-esconde — o carneirinho sumiu no meio das nuvens
P = starts("verso#3", [1, 1, 1, 1])
NUVENS = {"n1": {"id": "nuvem", "x": 600, "y": 1080, "z": 1, "depth": 0.6, "pose": {"cara": 0.0}},
          "n2": {"id": "nuvem", "x": 2050, "y": 1060, "z": 1, "depth": 0.55, "pose": {"cara": 0.0}}}
partes["verso#3"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": CAM, "callout": [call(t_palavra(P[0][0], P[0][2], "cadê", default=1.2), "CADÊ?", "azul")],
     "objetos": {"cerca": dict(CERCA)},
     "atores": {"laurinha": {"x": 820, "turn": 0.35, "pose": B, "acoes": [{"t": 0.1, "do": "look_around", "dur": "resto"}]},
                "luisinho": {"x": 1800, "turn": -0.35, "pose": B, "acoes": [{"t": 0.3, "do": "pensar", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "plano_ceu", "camera": CAM, "callout": [call(t_palavra(P[1][0], P[1][2], "uau", default=1.0), "UAU!", "rosa")],
     "objetos": {**NUVENS, "carneirinho": carneiro(1300, 880, depth=0.8, pose={"esconde": 1.0})},
     "atores": {"laurinha": {"x": 600, "y": 860, "fly": 1, "turn": 0.4, "pose": B, "acoes": [{"t": 0.1, "do": "fly", "dur": 1.2, "to_x": 820, "to_y": 800}]},
                "luisinho": {"x": 2050, "y": 840, "fly": 1, "turn": -0.4, "pose": B, "acoes": [{"t": 0.2, "do": "fly", "dur": 1.2, "to_x": 1800, "to_y": 780}]}}},
    {"linhas": 1, "cenario": "plano_ceu", "camera": {"x": 1150, "y": 680, "zoom": 1.3, "zoom_fim": 1.34},
     "callout": [call(t_palavra(P[2][0], P[2][2], "méé", default=1.6), "MÉÉ!", "amarelo")],
     "objetos": {**NUVENS, "carneirinho": carneiro(1300, 880, depth=0.8, pose={"esconde": 1.0},
                                                   keys=[{"t": 0.0, "pose": {"balanco": 0.0}}, {"t": t_palavra(P[2][0], P[2][2], "méé", default=1.6), "pose": {"balanco": 1.0}, "ease": "out"},
                                                         {"t": t_palavra(P[2][0], P[2][2], "méé", default=1.6) + 0.3, "pose": {"balanco": -1.0}, "ease": "inout"},
                                                         {"t": t_palavra(P[2][0], P[2][2], "méé", default=1.6) + 0.6, "pose": {"balanco": 0.0}, "ease": "inout"}])},
     "atores": {"laurinha": {"x": 820, "y": 880, "fly": 1, "turn": 0.4, "pose": B, "acoes": [{"t": max(0.2, t_palavra(P[2][0], P[2][2], "méé", default=1.6)), "do": "take"}]}}},
    {"linhas": 1, "cenario": "plano_ceu", "camera": CAM, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.2, "ACHEI!", "verde")],
     "objetos": {**NUVENS, "carneirinho": carneiro(1300, 880, depth=0.8, keys=[{"t": 0.0, "pose": {"mee": 1.0}}, {"t": 0.5, "pose": {"mee": 0.0}}])},
     "atores": {"laurinha": {"x": 820, "y": 800, "fly": 1, "turn": 0.4, "pose": B, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]},
                "luisinho": {"x": 1800, "y": 780, "fly": 1, "turn": -0.4, "pose": B, "acoes": [{"t": 0.2, "do": "laugh", "dur": "resto"}]}}},
]

# ───────── final: convite (gostou? joinha! papai e mamãe, inscreva-se) e tchau no campo
P = starts("final#1", [1, 1, 1, 1])
partes["final#1"] = [
    {"linhas": 1, "cenario": "danca_raios_azul", "camera": "close:laurinha", "callout": [call(0.3, "GOSTOU?", "rosa")],
     "atores": {"laurinha": {"x": 960, "pose": B, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.4, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {"luisinho": {"x": 680, "pose": B, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "plano_casa_frente", "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                "laurinha": {"x": 1450, "turn": -0.3, "pose": B, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {"laurinha": {"x": 600, "pose": B, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
]
P = starts("final#2", [1])
t0, t1, v = P[0]
partes["final#2"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(t_palavra(t0, v, "tchau", default=1.0), "TCHAU!", "amarelo")],
     "objetos": {"carneirinho": carneiro(1300, keys=mee_keys(t0, v) + balanco(t0, t1, 0.6))},
     "atores": {"laurinha": {"x": 820, "turn": 0.3, "pose": B, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 3.4},
                                                                         {"t": 3.7, "do": "fly", "dur": 1.4, "to_x": -300, "to_y": 300}]},
                "luisinho": {"x": 1800, "turn": -0.3, "pose": B, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 3.4},
                                                                          {"t": 3.8, "do": "fly", "dur": 1.4, "to_x": 2900, "to_y": 350}]}}},
]

# chaves de objetos nunca passam do fim do próprio plano (o validador avisa e o render ignora)
for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    b, _ = INFO[k_info]
    ls = [p.get("linhas", 0 if "seg" in p else 1) for p in planos]
    if all(n > 0 for n in ls):
        durs = [t1 - t0 for t0, t1, _ in starts(k_info, ls)]
    else:                                   # planos com verso primeiro, depois os "seg" (instrumentais)
        durs = [t1 - t0 for t0, t1, _ in starts(k_info, [n for n in ls if n > 0])] + [None] * ls.count(0)
    for p, d in zip(planos, durs):
        d = d if d is not None else p.get("seg")
        for o in (p.get("objetos") or {}).values():
            if d and o.get("keys"):
                ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                o["keys"] = sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"])   # chave no fim exato: puxa p/ dentro

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0",
       "nota": "Roteiro verso a verso de 'Méé, Carneirinho!' (take v2 de 18/11/2026, 2:20; letra aumentada): no campo, o carneirinho "
               "é o chefe da brincadeira — a cada \"o carneirinho mandou…\" todo mundo faz o comando junto (pular, sentar, girar, abaixar, "
               "palma, pé, dançar, abraçar); a lã vira blusinha quentinha no frio; ponte da cerquinha/capim/estátua 2×; esconde-esconde "
               "nas nuvens; convite e tchau. Gerado por scripts/roteiros/ep12_mee_carneirinho.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("roteiro:", sum(len(v) for v in partes.values()), "planos")
