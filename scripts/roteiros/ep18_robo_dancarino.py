"""Roteiro verso a verso de 18 "Robô Dançarino" (take v1 cortado para 3:11, uma voz: Luisinho v2, estilo E6) → musicas/18_robo_dancarino/roteiro.json.

A oficina do Luisinho: ele monta um robozinho de caixa, aperta o botão vermelho e o robô dança sem parar até a pilha
acabar (pfff!). No refrão o robô TRAVA (olhos de X) e a turma congela junto (estátua); VOLTA e todo mundo dança de novo.
Na ponte o Luisinho dá os comandos (braço, perna, gira a cabeça) e a Laurinha troca a pilha. Planos de 3–7 s.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep18_robo_dancarino.py
"""
from __future__ import annotations

import json
from pathlib import Path

from toonstudio.composition.clip_draft import _q, _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "laurinha" / "ep18-robo-dancarino"
MUS = ROOT / "canais" / "laurinha" / "musicas" / "18_robo_dancarino"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
OF = "plano_oficina"
CAM = {"x": 1300, "y": 600, "zoom": 1.15, "zoom_fim": 1.2}
LA, LU = "laurinha", "luisinho"
RITMO = 0.75                       # passinhos do robô por segundo (1 a cada 2 batidas de ~0,65 s)


def bloco_info():
    out, occ = {}, {}
    for b in blocos(song):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        out[f"{b['tipo']}#{occ[b['tipo']]}"] = (b, [l for l in LINES if b["s"] - 0.05 <= l["s"] < b["e"] - 0.05])
    return out


INFO = bloco_info()


def planos_tempo(key, planos):
    """Início/fim/versos de cada plano — a mesma conta de clip_draft.roteiro_bloco (inclui planos com `seg`)."""
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


def starts(key, linhas):
    return planos_tempo(key, [{"linhas": n} for n in linhas])


def tp(t0, versos, *alvos, default=0.4):
    alvos = tuple(a.lower() for a in alvos)
    for l in versos:
        for w in l["words"]:
            if w["w"].lower().strip("!?,.…()\"'") in alvos:
                return round(max(0.0, w["s"] - t0), 2)
    return default


def call(t, text, color):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color}


def danca(t0, t1, fase0=0.0, rate=RITMO):
    """Robô dançando de t0 a t1 (fase contínua, linear)."""
    return [{"t": round(t0, 2), "pose": {"danca": round(fase0, 3)}, "ease": "step"},
            {"t": round(t1, 2), "pose": {"danca": round(fase0 + (t1 - t0) * rate, 3)}, "ease": "linear"}]


def robo(x=1300, y=930, depth=0.9, z=3, pose=None, keys=None):
    return {"id": "robo", "x": x, "y": y, "z": z, "depth": depth, "pose": pose or {}, "keys": keys or []}


def trava_volta(d, t_trava=None, t_volta=None):
    """Robô dança; trava (olhos de X, faísca) em t_trava; volta (pulinho) em t_volta."""
    ks = [{"t": 0.0, "pose": {"trava": 0.0, "pulo": 0.0}, "ease": "step"}] + danca(0.0, d)
    if t_trava is not None:
        ks += [{"t": max(0.05, t_trava - 0.05), "pose": {"trava": 0.0}}, {"t": t_trava + 0.08, "pose": {"trava": 1.0}, "ease": "step"}]
    if t_volta is not None:
        ks += [{"t": max(0.06, t_volta - 0.02), "pose": {"trava": 1.0}}, {"t": t_volta + 0.08, "pose": {"trava": 0.0}, "ease": "step"},
               {"t": t_volta + 0.1, "pose": {"pulo": 0.0}}, {"t": t_volta + 0.55, "pose": {"pulo": 1.0}, "ease": "linear"}]
    return ks


partes: dict = {}

# ───────── intro: a oficina; o Luisinho aperta o botão e o robô começa a dançar ─────────
(i0, i1, _), (j0, j1, vj), (k0, k1, _), (l0, l1, _) = planos_tempo("intro#1", [{"seg": 4.0}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}])
partes["intro"] = [
    {"seg": 4.0, "cenario": OF, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}, "callout": [call(1.2, "A OFICINA DO LUISINHO!", "azul")],
     "objetos": {"robo": robo(1450, pose={"murcha": 0.6, "pilha": 1.0, "luz": 0.0})},
     "atores": {LU: {"x": 2900, "y": 480, "turn": -0.4, "acoes": [{"t": 0.3, "do": "fly", "dur": 2.0, "to_x": 1900, "to_y": 930},
                                                                   {"t": 2.6, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": OF, "camera": CAM, "callout": [call(0.3, "ROBÔ DANÇARINO!", "laranja")],
     "objetos": {"robo": robo(1300, keys=[{"t": 0.0, "pose": {"murcha": 0.6, "botao": 1.0, "luz": 1.0}, "ease": "step"},
                                          {"t": 0.5, "pose": {"murcha": 0.0}, "ease": "out"}, {"t": 0.7, "pose": {"botao": 0.0}}] + danca(0.6, j1 - j0))},
     "atores": {LU: {"x": 1900, "turn": -0.35, "acoes": [{"t": 0.6, "do": "laugh", "dur": 1.6}, {"t": 2.4, "do": "dance", "style": "bracos", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_xadrez_azul", "fx": ["estrelas"],
     "objetos": {"robo": robo(960, 1010, depth=0.95, keys=danca(0.0, k1 - k0, 0.3))}},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "fx": ["confete"], "callout": [call(0.15, "LAURINHA E LUISINHO!", "rosa")],
     "atores": {LA: {"x": 560, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                LU: {"x": 1360, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}}},
]


# ───────── verso: montei, botão vermelho, confuso, dança sem parar, a pilha acaba ─────────
def verso(key, n):
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd) = starts(key, [2, 2, 2, 2])
    tbt, tcf = tp(b0, vb, "botão", "botao", default=0.6), tp(b0, vb, "confuso", default=3.0)
    tdc = tp(c0, vc, "dançar", "dancar", default=0.6)
    tac = tp(d0, vd, "acabou", default=1.6)
    amiga = {LA: {"x": 700, "turn": 0.35, "acoes": [{"t": 0.3, "do": "cheguei", "dur": 1.2}, {"t": 1.8, "do": "point", "dur": "resto"}]}} if n == 2 else {}
    return [
        {"linhas": 2, "cenario": OF, "camera": CAM, "callout": [call(1.4, "MEU ROBÔ!", "azul")],
         "objetos": {"robo": robo(1250, pose={"luz": 0.0}, keys=[{"t": 0.0, "pose": {"cabeca": 0.0}}, {"t": 2.2, "pose": {"cabeca": 0.04}},
                                                              {"t": 2.6, "pose": {"cabeca": -0.04}}, {"t": 3.0, "pose": {"cabeca": 0.0}}])},
         "atores": {LU: {"x": 1900, "turn": -0.35, "acoes": [{"t": 0.2, "do": "bacana", "dur": 1.6}, {"t": 2.0, "do": "point", "dur": "resto"}]}, **amiga}},
        {"linhas": 2, "cenario": OF, "camera": {"x": 1300, "y": 640, "zoom": 1.35, "zoom_fim": 1.45},
         "callout": [call(tbt + 0.1, "BOTÃO VERMELHO!", "vermelho"), call(tcf + 0.2, "CONFUSO!", "amarelo")],
         "objetos": {"robo": robo(1300, keys=[{"t": 0.0, "pose": {"botao": 0.0, "luz": 0.0, "cabeca": 0.0}},
                                              {"t": tbt + 0.2, "pose": {"botao": 1.0, "luz": 1.0}, "ease": "step"},
                                              {"t": tbt + 0.9, "pose": {"botao": 0.0}},
                                              {"t": max(tbt + 1.0, tcf - 0.1), "pose": {"cabeca": 0.0}},
                                              {"t": tcf + 1.3, "pose": {"cabeca": 2.0}, "ease": "inout"}])},
         "atores": {LU: {"x": 1850, "turn": -0.35, "expr": "surprised", "acoes": [{"t": max(0.1, tcf), "do": "shock_reaction", "dur": "resto"}]}}},
        {"linhas": 2, "cenario": OF, "camera": CAM, "callout": [call(tdc + 0.2, "DANÇA, ROBÔ!", "laranja")], "fx": ["notas"],
         "objetos": {"robo": robo(1300, keys=danca(max(0.05, tdc), c1 - c0))},
         "atores": {LU: {"x": 1950, "turn": -0.35, "acoes": [{"t": tdc + 0.4, "do": "dance", "style": "marcha", "dur": "resto"}]},
                    **({LA: {"x": 650, "turn": 0.35, "acoes": [{"t": tdc + 0.6, "do": "dance", "style": "bracos", "dur": "resto"}]}} if n == 2 else {})}},
        {"linhas": 2, "cenario": OF, "camera": {"x": 1300, "y": 620, "zoom": 1.25, "zoom_fim": 1.35}, "callout": [call(tac + 0.2, "PFFF!", "roxo")],
         "objetos": {"robo": robo(1300, keys=danca(0.0, tac) + [{"t": tac - 0.05, "pose": {"pilha": 1.0, "murcha": 0.0, "luz": 1.0}},
                                                               {"t": tac + 0.35, "pose": {"pilha": 0.2}, "ease": "linear"},
                                                               {"t": tac + 0.9, "pose": {"murcha": 1.0, "pilha": 0.0, "luz": 0.0}, "ease": "out"}])},
         "atores": {LU: {"x": 1900, "turn": -0.35, "acoes": [{"t": max(0.1, tac + 0.3), "do": "take", "dur": 1.2},
                                                           {"t": tac + 1.6, "do": "laugh", "dur": "resto"}]}}},
    ]


partes["verso#1"] = verso("verso#1", 1)
partes["verso#2"] = verso("verso#2", 2)

BG = {1: ("danca_bolinhas_azul", "danca_raios_laranja"), 2: ("danca_xadrez_verde", "danca_ondas_azul"), 3: ("danca_raios_roxo", "danca_bolinhas_amarelo")}
CORES = {1: "azul", 2: "verde", 3: "laranja"}


# ───────── refrão: trava (todo mundo vira estátua) e volta (todo mundo dança) ─────────
def refrao(n):
    planos = []
    for i, (t0, t1, v) in enumerate(starts(f"refrao#{n}", [2, 2, 2, 3])):
        d = t1 - t0
        trava = i % 2 == 0
        palavra = "travou" if trava else "voltou"
        tw = tp(t0, v, palavra, default=d * 0.6)
        if trava:
            ks = trava_volta(d, t_trava=tw)
        else:
            ks = [{"t": 0.0, "pose": {"trava": 1.0}, "ease": "step"}] + danca(0.0, d) + \
                 [{"t": max(0.06, tw - 0.02), "pose": {"trava": 1.0}}, {"t": tw + 0.08, "pose": {"trava": 0.0}, "ease": "step"},
                  {"t": tw + 0.1, "pose": {"pulo": 0.0}}, {"t": tw + 0.55, "pose": {"pulo": 1.0}, "ease": "linear"}]
        no_cenario = i in (0, 2) if n != 2 else i in (1, 3)
        cen = OF if no_cenario else BG[n][i // 2]
        y, dep = (930, 1.0) if no_cenario else (1010, 0.95)
        def kid(w, x, turn, estilo):
            if trava:
                return {"x": x, "y": y, "depth": 1.0 if no_cenario else 1.1, "turn": turn,
                        "acoes": [{"t": 0.0, "do": "dance", "style": estilo, "dur": round(max(0.4, tw), 2)},
                                  {"t": round(tw + 0.1, 2), "do": "estatua", "pose": "bracos" if w == LU else "perna", "dur": "resto"}]}
            return {"x": x, "y": y, "depth": 1.0 if no_cenario else 1.1, "turn": turn,
                    "acoes": [{"t": 0.0, "do": "estatua", "pose": "bracos" if w == LU else "perna", "dur": round(max(0.4, tw), 2)},
                              {"t": round(tw + 0.1, 2), "do": "jump", "dur": round(min(0.9, d - tw - 0.6), 2)},
                              {"t": round(min(tw + 1.1, d - 0.45), 2), "do": "dance", "style": "festa" if i == 3 else "bracos", "dur": "resto"}]}
        cam = {"x": 1300, "y": 640, "zoom": 1.3, "zoom_fim": 1.22} if i == 2 else CAM
        p = {"linhas": 3 if i == 3 else 2, "cenario": cen, "camera": cam if no_cenario else None,
             "callout": [call(tw + 0.1, "TRAVOU!" if trava else "VOLTOU!", "vermelho" if trava else "verde")],
             "objetos": {"robo": robo(1300 if no_cenario else 960, y, depth=dep * 0.9, keys=ks)},
             "atores": {LA: kid(LA, 700 if no_cenario else 430, 0.35, "marcha"), LU: kid(LU, 1900 if no_cenario else 1490, -0.35, "bracos")}}
        if i == 0:
            p["flash"] = True
            p["callout"].insert(0, call(0.15, "ROBÔ DANÇARINO!", CORES[n]))
        if i == 3:
            tz = tp(t0, v, "massa", "zum-zum,", default=d - 1.6)
            p["callout"].append(call(tz, "QUE MASSA!", "rosa"))
            p["fx"] = ["confete"]
        if p["camera"] is None:
            del p["camera"]
        planos.append(p)
    return planos


for n in (1, 2, 3):
    partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalo: "Laurinha e Luisinho!" e a dança do robô com a turma ─────────
def intervalo(key, n, seg1):
    b, _ = INFO[key]
    d2 = b["e"] - b["s"] - seg1
    return [{"linhas": 1, "seg": seg1, "cenario": "danca_raios_rosa" if n == 1 else "danca_bolinhas_rosa", "fx": ["confete"],
             "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")],
             "atores": {LA: {"x": 560, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                        LU: {"x": 1360, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}}},
            {"seg": round(d2, 2), "cenario": OF, "camera": {"x": 1300, "y": 600, "zoom": 1.05, "zoom_fim": 1.18}, "titulo": "a dança do robô",
             "callout": [call(0.4, "DANÇA DO ROBÔ!", "azul")], "fx": ["notas"],
             "objetos": {"robo": robo(1300, keys=danca(0.0, d2) + [{"t": 0.0, "pose": {"braco": 0.0}}] +
                                 [{"t": round(1.3 * j + 1.0, 2), "pose": {"braco": float(j % 2)}} for j in range(int((d2 - 1.2) / 1.3))])},
             "atores": {LA: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "marcha", "dur": "resto"}]},
                        LU: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "bracos", "dur": "resto"}]}}}]


partes["intervalo#1"] = intervalo("intervalo#1", 1, 6.4)
partes["intervalo#2"] = intervalo("intervalo#2", 2, 4.9)


# ───────── ponte: comandos do Luisinho; a pilha acaba; (1ª vez) a Laurinha troca a pilha ─────────
def ponte(key, n):
    planos = [{"linhas": 2}, {"linhas": 2, "seg": 5.6}, {"seg": 0.0}] if n == 1 else [{"linhas": 2}, {"linhas": 2}]
    T = planos_tempo(key, planos)
    (a0, a1, va), (b0, b1, vb) = T[0], T[1]
    tb, tpn = tp(a0, va, "braço", "braco", default=0.3), tp(a0, va, "perna", default=3.2)
    tg, tpf = tp(b0, vb, "gira", default=0.3), tp(b0, vb, "pfff", default=2.0)
    out = [
        {"linhas": 2, "cenario": OF, "camera": CAM, "callout": [call(tb + 0.2, "BRAÇO!", "azul"), call(tpn + 0.2, "PERNA!", "verde")],
         "objetos": {"robo": robo(1250, keys=[{"t": 0.0, "pose": {"braco": 0.0, "perna": 0.0}}, {"t": tb + 0.5, "pose": {"braco": 1.0}, "ease": "out"},
                                              {"t": max(tb + 0.6, tpn - 0.2), "pose": {"braco": 1.0, "perna": 0.0}},
                                              {"t": tpn + 0.3, "pose": {"braco": 0.0, "perna": 1.0}, "ease": "out"}])},
         "atores": {LU: {"x": 1900, "turn": -0.35, "acoes": [{"t": max(0.05, tb - 0.2), "do": "point", "dur": "resto"}]},
                    LA: {"x": 650, "turn": 0.35, "acoes": [{"t": tb + 0.6, "do": "dance", "style": "bracos", "dur": round(max(0.5, tpn - tb - 0.8), 2)},
                                                           {"t": tpn + 0.2, "do": "dance", "style": "pezinho", "dur": "resto"}]}}},
        {"linhas": 2, **({"seg": 5.6} if n == 1 else {}), "cenario": OF, "camera": {"x": 1300, "y": 640, "zoom": 1.3, "zoom_fim": 1.4},
         "callout": [call(tg + 0.2, "GIRA A CABEÇA!", "laranja"), call(tpf + 0.1, "PFFF!", "roxo")],
         "objetos": {"robo": robo(1300, keys=[{"t": 0.0, "pose": {"cabeca": 0.0, "murcha": 0.0, "pilha": 1.0, "luz": 1.0}},
                                              {"t": max(0.1, tg + 0.1), "pose": {"cabeca": 0.0}}, {"t": tg + 1.5, "pose": {"cabeca": 1.0}, "ease": "inout"},
                                              {"t": max(tg + 1.6, tpf - 0.05), "pose": {"pilha": 1.0, "murcha": 0.0, "luz": 1.0}},
                                              {"t": tpf + 0.3, "pose": {"pilha": 0.2}, "ease": "linear"},
                                              {"t": tpf + 0.9, "pose": {"murcha": 1.0, "pilha": 0.0, "luz": 0.0}, "ease": "out"}])},
         "atores": {LU: {"x": 1880, "turn": -0.35, "acoes": [{"t": 0.1, "do": "point", "dur": round(max(0.5, tpf - 0.2), 2)},
                                                           {"t": tpf + 0.4, "do": "take", "dur": "resto"}]}}},
    ]
    if n == 1:
        d3 = T[2][1] - T[2][0]
        out.append({"seg": 0.0, "cenario": OF, "camera": CAM, "callout": [call(0.4, "PILHA NOVA!", "verde")], "fx": ["estrelas"],
                    "objetos": {"robo": robo(1300, keys=[{"t": 0.0, "pose": {"murcha": 1.0, "pilha": 0.0, "luz": 0.0}, "ease": "step"},
                                                         {"t": 1.4, "pose": {"pilha": 0.0}}, {"t": 2.0, "pose": {"pilha": 1.0}, "ease": "linear"},
                                                         {"t": 2.1, "pose": {"murcha": 1.0, "luz": 0.0}},
                                                         {"t": 2.5, "pose": {"murcha": 0.0, "luz": 1.0}, "ease": "out"}] + danca(2.6, d3))},
                    "atores": {LA: {"x": 900, "turn": 0.4, "acoes": [{"t": 0.1, "do": "cheguei", "dur": 1.2}, {"t": 2.6, "do": "jump", "dur": 0.9}]},
                               LU: {"x": 1900, "turn": -0.35, "acoes": [{"t": 2.5, "do": "laugh", "dur": "resto"}]}}})
        del out[2]["seg"]
        out[2]["seg"] = round(d3, 2)
    return out


partes["ponte#1"] = ponte("ponte#1", 1)
partes["ponte#2"] = ponte("ponte#2", 2)

# ───────── final: convite (joinha, papai e mamãe, inscrever) e tchau ─────────
partes["final#1"] = [
    {"linhas": 1, "cenario": OF, "camera": "close:luisinho", "callout": [call(0.3, "GOSTOU DO ROBÔ?", "azul")],
     "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.3, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LU: {"x": 680, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "plano_casa_frente", "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                LU: {"x": 1450, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]},
                 "robo": robo(1640, 1000, depth=0.62, keys=danca(0.0, 4.6))},
     "atores": {LU: {"x": 600, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
]
partes["final#2"] = [
    {"linhas": 1, "cenario": OF, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(1.0, "TCHAU!", "amarelo")],
     "objetos": {"robo": robo(1300, keys=danca(0.0, 3.0) + [{"t": 3.0, "pose": {"braco": 0.0}}, {"t": 3.4, "pose": {"braco": 1.0}, "ease": "out"},
                                                         {"t": 5.2, "pose": {"murcha": 0.0, "luz": 1.0}}, {"t": 5.9, "pose": {"murcha": 1.0, "luz": 0.0}, "ease": "out"}])},
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
    for p, (t0, t1, _) in zip(planos, planos_tempo(k_info, planos)):
        p["cantam"] = ["luisinho"]
        d = t1 - t0
        assert d >= 0.6, (chave, t0, t1)
        for o in (p.get("objetos") or {}).values():
            if o.get("keys"):
                ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                o["keys"] = transicoes(sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"]))

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0",
       "nota": "Roteiro de 'Robô Dançarino' (take v1 de 18/11/2026 cortado para 3:11, Luisinho v2, estilo E6): a oficina do "
               "Luisinho; o robô de caixa dança, trava (a turma vira estátua) e volta; a pilha acaba (pfff!) e a Laurinha "
               "troca a pilha. Gerado por scripts/roteiros/ep18_robo_dancarino.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = sum(len(v) for v in partes.values())
print("roteiro:", n, "planos ·", round(song["duration"] / n, 1), "s por plano")
for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    print(chave, [round(t1 - t0, 1) for t0, t1, _ in planos_tempo(k_info, planos)])
