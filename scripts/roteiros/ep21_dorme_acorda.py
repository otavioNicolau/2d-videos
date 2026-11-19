"""Roteiro verso a verso de 21 "Dorme, Acorda!" (take v1, 2:56, Luisinho, estilo E12, nota 4,8) → musicas/21_dorme_acorda/roteiro.json.

A brincadeira de dormir e acordar: no QUARTO do Luisinho e no QUARTO da Laurinha (camas, olhinhos fechados, "zzz"),
"Acorda!" e todo mundo pula de pé; quem dorme na hora errada ganha COSQUINHA NO PÉ. Novidade (usuário, 19/11): a turma
TOCA os instrumentos da música (E12: teclado, bateria e sax) — nos intervalos e nos últimos refrões a BANDA no SALÃO:
Luisinho na bateria, Laurinha no saxofone e no teclado. Personagens 1,45×, animação A3, sem efeitos sonoros.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep21_dorme_acorda.py
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

from toonstudio.composition.clip_draft import _q, _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "ep21-dorme-acorda"
MUS = ROOT / "musicas" / "21_dorme_acorda"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
QAZ, QRO, SALA, SALAO, CASA = "plano_quarto_azul", "plano_quarto_rosa", "plano_sala", "plano_salao", "plano_casa_frente"
LA, LU = "laurinha", "luisinho"
CAM = {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.18}
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
    alvos = tuple(a.lower() for a in alvos)
    return [round(max(0.0, w["s"] - t0), 2) for l in versos for w in l["words"] if w["w"].lower().strip("!?,.…:()\"'") in alvos]


def tp(t0, versos, *alvos, default=0.4):
    r = tps(t0, versos, *alvos)
    return r[0] if r else default


def call(t, text, color, **kw):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color, **kw}


def cama(x, depth=0.8):
    return {"id": "cama", "x": x, "y": 930, "z": 1, "depth": depth}


def lua(t_dorme=None, t_acorda=None, x=1300):
    """Piada que volta: a lua na janela também dorme ('zzz', olhinho fechado) e acorda junto com a turma."""
    ks = [{"t": 0.0, "pose": {"lid": 0.0, "boca": 0.0, "brilho": 1.0}, "ease": "step"}]
    if t_dorme is not None:
        ks += [{"t": round(t_dorme, 2), "pose": {"lid": 1.0}, "ease": "step"}]
    if t_acorda is not None:
        ks += [{"t": round(t_acorda, 2), "pose": {"lid": 0.0, "boca": 1.0}, "ease": "step"}, {"t": round(t_acorda + 0.6, 2), "pose": {"boca": 0.0}}]
    return {"id": "lua", "x": x, "y": 470, "z": 0, "depth": 0.32, "keys": ks}


def lencol(x, t=None):
    ks = [{"t": 0.0, "pose": {"arrumado": 1.0}, "ease": "step"}]
    if t is not None:
        ks += [{"t": round(t, 2), "pose": {"arrumado": 0.0}, "ease": "out"}]
    return {"id": "lencol", "x": x, "y": 930, "z": 5, "depth": 0.75, "keys": ks}


def quarto(t_dorme=None, t_acorda=None, camas=(900, 1700)):
    o = {"lua": lua(t_dorme, t_acorda)}
    for i, x in enumerate(camas):
        o[f"c{i}"] = cama(x)
        o[f"l{i}"] = lencol(x, t_acorda)
    return o


def dorme_acorda(x, turn, t_dorme, t_acorda, d, estilo=None):
    """Fecha os olhos ('zzz', balança de sono) e PULA de pé no 'acorda'; depois dança."""
    acoes = []
    if t_dorme is not None:
        acoes.append({"t": round(t_dorme, 2), "do": "dance", "style": "pendulo", "dur": round(max(0.3, (t_acorda or d) - t_dorme - 0.05), 2)})
    if t_acorda is not None and t_acorda < d - 0.4:
        acoes += [{"t": round(t_acorda, 2), "do": "jump", "dur": 0.8},
                  {"t": round(min(d - 0.35, t_acorda + 0.9), 2), "do": "dance", "style": estilo or next(ESTILOS), "dur": "resto"}]
    keys = []
    if t_dorme is not None:
        keys += [{"t": round(t_dorme, 2), "pose": {"lid": 1.0}, "ease": "step"}]
    if t_acorda is not None:
        keys += [{"t": round(t_acorda, 2), "pose": {"lid": 0.0}, "ease": "step"}]
    return {"x": x, "turn": turn, "acoes": acoes, "keys": keys}


def banda(cen, d, quem_sax=LA, teclado=False, cam=None, extra=None, fx=None):
    """A BANDA: Luisinho na bateria (baquetas nas duas mãos); Laurinha no sax (ou no teclado)."""
    p = {"seg": round(d, 2), "cenario": cen, "camera": cam or {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.18}, "fx": fx or ["notas"],
         "objetos": {"bat": {"id": "bateria", "x": 1700, "y": 930, "z": 4, "depth": 0.9,
                             "keys": [{"t": round(j * 0.45, 2), "pose": {"bumbo": float(j % 2 == 0), "caixa": float(j % 2), "prato": float(j % 4 == 0)}, "ease": "out"}
                                      for j in range(int(d / 0.45))]}},
         "atores": {LU: {"x": 1700, "y": 900, "turn": -0.2, "z": 3, "segura": "baqueta", "segura_f": "baqueta",
                         "acoes": [{"t": 0.0, "do": "dance", "style": "toca_bateria", "dur": "resto"}]}}}
    if teclado:
        p["objetos"]["tec"] = {"id": "teclado_inst", "x": 800, "y": 930, "z": 4, "depth": 0.85, "keys": [{"t": 0.0, "pose": {"tecla": 0.0}, "ease": "step"},
                                                                                                    {"t": round(d, 2), "pose": {"tecla": round(d * 2, 1)}, "ease": "linear"}]}
        p["atores"][LA] = {"x": 800, "y": 900, "turn": 0.2, "z": 3, "acoes": [{"t": 0.0, "do": "dance", "style": "toca_teclado", "dur": "resto"}]}
    else:
        p["atores"][quem_sax] = {"x": 800, "turn": 0.3, "segura": "saxofone", "acoes": [{"t": 0.0, "do": "dance", "style": "toca_sax", "dur": "resto"}]}
    if extra:
        p["atores"].update(extra)
    return p


partes: dict = {}

# ───────── intro: o quarto de noite; a turma de pijama; "Laurinha e Luisinho!" com a banda ─────────
P = [{"seg": 3.0}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}]
(a0, a1, _), (b0, b1, vb), (c0, c1, vc), (d0, d1, _) = planos_tempo("intro#1", P)
partes["intro"] = [
    {"seg": 3.0, "cenario": QAZ, "camera": {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.08}, "escurece": [0.45, 0.45], "titulo": "boa noite",
     "callout": [call(0.8, "ZZZ…", "roxo")], "objetos": quarto(0.0, None),
     "atores": {LA: {"x": 900, "turn": 0.2, "expr": "sleepy", "keys": [{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"}]},
                LU: {"x": 1700, "turn": -0.2, "expr": "sleepy", "keys": [{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"}]}}},
    {"linhas": 1, "cenario": QAZ, "camera": CAM, "flash": True, "callout": [call(0.3, "DORME… ACORDA!", "amarelo")],
     "objetos": quarto(0.0, tp(b0, vb, "acorda", default=1.0)),
     "atores": {LA: dorme_acorda(900, 0.2, 0.0, tp(b0, vb, "acorda", default=1.0), b1 - b0, "festa"),
                LU: dorme_acorda(1700, -0.2, 0.0, tp(b0, vb, "acorda", default=1.0) + 0.05, b1 - b0, "lado")}},
    {"linhas": 1, "cenario": QRO, "camera": {"x": 1300, "y": 620, "zoom": 1.3, "zoom_fim": 1.2},
     "atores": {LA: dorme_acorda(1300, 0.0, 0.0, tp(c0, vc, "acorda", default=0.9), c1 - c0, "cintura")}},
    {**banda(SALAO, d1 - d0, fx=["confete"]), "linhas": 1, "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")]},
]
partes["intro"][-1].pop("seg")


# ───────── verso: a regra da brincadeira; a cosquinha no pé ─────────
def verso(key, n):
    P = [{"linhas": 2}, {"linhas": 2}, {"linhas": 2}, {"linhas": 1}, {"linhas": 1}]
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd), (e0, e1, ve) = planos_tempo(key, P)
    ta = tp(b0, vb, "acorda", default=1.5)
    tc = tp(c0, vc, "cosquinha", default=2.0)
    q1, q2 = (QAZ, QRO) if n == 1 else (QRO, SALA)
    return [
        {"linhas": 2, "cenario": q1, "camera": "close:luisinho" if n == 1 else {"x": 1300, "y": 620, "zoom": 1.25, "zoom_fim": 1.35},
         "callout": [call(1.6, "FECHA O OLHO!", "roxo")],
         "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": 1.4}],
                         "keys": [{"t": round(tp(a0, va, "fecha", default=1.6), 2), "pose": {"lid": 1.0}, "ease": "step"}]}}},
        {"linhas": 2, "cenario": q1, "camera": CAM, "callout": [call(ta + 0.1, "ACORDA!", "amarelo")], "objetos": quarto(0.1, ta, camas=(1300,)),
         "atores": {LA: dorme_acorda(800, 0.3, 0.1, ta, b1 - b0), LU: dorme_acorda(1850, -0.3, 0.1, ta + 0.05, b1 - b0)}},
        # a cosquinha no pé: a Laurinha de fininho e o Luisinho morre de rir
        {"linhas": 2, "cenario": q2, "camera": {"x": 1300, "y": 640, "zoom": 1.3, "zoom_fim": 1.4}, "callout": [call(tc + 0.2, "COSQUINHA!", "rosa")],
         "atores": {LU: {"x": 1550, "turn": -0.3, "expr": "sleepy", "keys": [{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"},
                                                                             {"t": round(tc + 0.2, 2), "pose": {"lid": 0.0}, "ease": "step"}],
                         "acoes": [{"t": round(tc + 0.2, 2), "do": "laugh", "dur": "resto"}]},
                    LA: {"x": 600, "turn": 0.4, "acoes": [{"t": 0.1, "do": "sneak", "to_x": 1050}, {"t": round(tc + 0.1, 2), "do": "laugh", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": QRO if n == 1 else QAZ, "camera": {"x": 1300, "y": 600, "zoom": 1.05, "zoom_fim": 1.15},
         "callout": [call(0.4, "PRESTA ATENÇÃO!", "azul")], "objetos": quarto(None, None, camas=(1300,)),
         "atores": {LU: {"x": 1700, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]},
                    LA: {"x": 900, "turn": 0.3, "acoes": [{"t": 0.3, "do": "look_around", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": SALAO, "camera": "close:laurinha", "callout": [call(0.5, "OLHA SÓ!", "rosa")],
         "atores": {LA: {"x": 1300, "acoes": [{"t": 0.1, "do": "pensar", "dur": 1.2}, {"t": 1.4, "do": "cheguei", "dur": "resto"}]}}},
    ]


partes["verso#1"] = verso("verso#1", 1)
partes["verso#2"] = verso("verso#2", 2)


# ───────── refrão: dorme (olho fechado, balança) / acorda (pula de pé); 3º e 4º com a banda tocando ─────────
def refrao(n):
    P = [{"linhas": 2}, {"linhas": 2}, {"linhas": 2}, {"linhas": 2}]
    T = planos_tempo(f"refrao#{n}", P)
    out = []
    for i, (t0, t1, v) in enumerate(T):
        d = t1 - t0
        ta = tp(t0, v, "acorda", default=0.9)
        if n >= 3 and i in (1, 3):                                   # a BANDA no refrão final
            plateia = {"vovozinho": {"x": 2350, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}]}} if (n == 3 and i == 1) else \
                      ({"vovo": {"x": 250, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco", "dur": "resto"}]}} if i == 3 else None)
            p = banda(SALAO, d, teclado=(i == 3), fx=["confete"], cam={"x": 1300, "y": 600, "zoom": 1.0 if i == 1 else 1.15, "zoom_fim": 1.1}, extra=plateia)
            p.pop("seg")
            p.update({"linhas": 2, "callout": [call(ta + 0.1, "ACORDA!", "amarelo")]})
        else:
            cen = [QAZ, QRO, SALA, SALAO][n - 1] if i % 2 == 0 else [QRO, QAZ, SALAO, SALA][n - 1]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 600, "zoom": 1.1 if i % 2 == 0 else 1.25, "zoom_fim": 1.2 if i % 2 == 0 else 1.15},
                 "callout": [call(0.2, "DORME…", "roxo"), call(ta + 0.1, "ACORDA!", "amarelo")],
                 "objetos": quarto(0.05, ta, camas=(1300,)) if cen in (QAZ, QRO) else {"lua": lua(0.05, ta, x=1300)},
                 "atores": {LA: dorme_acorda([700, 1000, 600, 950][i], 0.3, 0.05, ta, d), LU: dorme_acorda([1900, 1650, 2000, 1700][i], -0.3, 0.05, ta + 0.05, d)}}
            if i == 3:
                tp_ = tp(t0, v, "pula", default=d * 0.6)
                p["callout"].append(call(tp_ + 0.1, "DE PÉ!", "verde"))
        if i == 0:
            p["flash"] = True
        out.append(p)
    return out


for n in (1, 2, 3, 4):
    partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos: bordão e a BANDA tocando ─────────
def intervalo(key, n):
    b, bl = INFO[key]
    D = b["e"] - b["s"]
    if not bl:                                                       # instrumental: banda completa, com os três instrumentos
        s1 = round(D / 2, 2)
        return [banda(SALAO, s1, teclado=True, fx=["confete"], cam={"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.08}),
                {**banda(SALAO, D - s1, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.15, "zoom_fim": 1.05},
                         extra={"vovo": {"x": 300, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura", "dur": "resto"}]}}),
                 "titulo": "solo de sax"}]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = 3.6
    return [{"linhas": 1, "seg": p1, "cenario": QAZ if n == 1 else QRO, "camera": "close:luisinho", "callout": [call(0.2, "QUE MASSA!", "azul")],
             "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
            {"linhas": 1, "seg": p2, "cenario": "danca_raios_roxo" if n == 1 else "danca_bolinhas_azul", "fx": ["confete"],
             "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")],
             "atores": {LA: {"x": 560, "y": 1010, "depth": 1.0, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "sapinho", "dur": "resto"}]},
                        LU: {"x": 1360, "y": 1010, "depth": 1.0, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "chute", "dur": "resto"}]}}},
            {**banda(SALAO, D - p1 - p2, teclado=(n == 2), fx=["notas"]), "titulo": "a banda"}]


partes["intervalo#1"] = intervalo("intervalo#1", 1)
partes["intervalo#2"] = intervalo("intervalo#2", 2)
partes["intervalo#3"] = intervalo("intervalo#3", 3)


# ───────── ponte: a pegadinha "Acor… dorme! Peguei você!" ─────────
def ponte(key, n):
    P = [{"linhas": 2}, {"linhas": 2}]
    (a0, a1, va), (b0, b1, vb) = planos_tempo(key, P)
    ta = tp(a0, va, "acorda", default=0.8)
    tg = tp(b0, vb, "peguei", default=1.3)
    cen = QRO if n == 1 else SALA
    return [
        {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 620, "zoom": 1.2, "zoom_fim": 1.3}, "callout": [call(0.1, "ZZZ!", "roxo"), call(ta, "Ê!", "amarelo")],
         "objetos": quarto(0.0, ta, camas=(1300,)) if cen in (QAZ, QRO) else {"lua": lua(0.0, ta)},
         "atores": {LA: dorme_acorda(800, 0.3, 0.0, ta, a1 - a0, "pezinho"), LU: dorme_acorda(1800, -0.3, 0.0, ta + 0.05, a1 - a0, "joelho")}},
        # "Acor… dorme!": o Luisinho pula na hora errada e a Laurinha pega ele (cosquinha)
        {"linhas": 2, "cenario": cen, "camera": {"x": 1350, "y": 630, "zoom": 1.35, "zoom_fim": 1.45}, "callout": [call(tg + 0.05, "PEGUEI VOCÊ!", "rosa")],
         "atores": {LU: {"x": 1650, "turn": -0.3, "acoes": [{"t": 0.2, "do": "jump", "dur": 0.8}, {"t": round(tg, 2), "do": "shock_reaction", "dur": 0.8},
                                                          {"t": round(min(b1 - b0 - 0.4, tg + 0.9), 2), "do": "laugh", "dur": "resto"}]},
                    LA: {"x": 900, "turn": 0.35, "expr": "sleepy", "keys": [{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"},
                                                                            {"t": round(max(0.1, tg - 0.2), 2), "pose": {"lid": 0.0}, "ease": "step"}],
                         "acoes": [{"t": round(max(0.1, tg - 0.1), 2), "do": "point", "dur": "resto"}]}}},
    ]


partes["ponte#1"] = ponte("ponte#1", 1)
partes["ponte#2"] = ponte("ponte#2", 2)

partes["final#1"] = [
    {"linhas": 1, "cenario": QAZ, "camera": "close:luisinho", "callout": [call(0.3, "GOSTOU?", "azul")],
     "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.3, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LU: {"x": 680, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CASA, "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                LU: {"x": 1450, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LU: {"x": 600, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
]
(f0, f1, vf), = planos_tempo("final#2", [{"linhas": 1}])
partes["final#2_"] = [
    {"linhas": 1, "cenario": QAZ, "camera": {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.06}, "escurece": [0.0, 0.5], "fx": ["coracoes"],
     "callout": [call(0.6, "TCHAU!", "amarelo"), call(round(f1 - f0 - 3.0, 2), "ZZZ…", "roxo")], "objetos": {"c1": cama(900), "c2": cama(1700)},
     "atores": {LA: {"x": 900, "turn": 0.2, "acoes": [{"t": 0.0, "do": "wave", "dur": 2.6}, {"t": 2.8, "do": "espreguicar", "dur": 2.0}],
                     "keys": [{"t": round(f1 - f0 - 3.2, 2), "pose": {"lid": 1.0}, "ease": "step"}]},
                LU: {"x": 1700, "turn": -0.2, "acoes": [{"t": 0.0, "do": "wave", "dur": 2.6}, {"t": 2.9, "do": "espreguicar", "dur": 2.0}],
                     "keys": [{"t": round(f1 - f0 - 3.1, 2), "pose": {"lid": 1.0}, "ease": "step"}]}}},
]

_tchau = partes.pop("final#2_")[0]
_d = f1 - f0
partes["final#2"] = [
    {**_tchau, "linhas": 1, "seg": 5.0, "callout": [call(0.6, "TCHAU!", "amarelo")], "escurece": [0.0, 0.2], "objetos": quarto(None, None)},
    {"seg": 4.0, "cenario": QAZ, "camera": {"x": 1300, "y": 640, "zoom": 1.2, "zoom_fim": 1.3}, "escurece": [0.2, 0.45], "titulo": "boa noite",
     "callout": [call(0.8, "BOA NOITE!", "roxo")], "objetos": quarto(1.8, None),
     "atores": {LA: {"x": 900, "turn": 0.2, "acoes": [{"t": 0.2, "do": "espreguicar", "dur": 1.6}], "keys": [{"t": 2.0, "pose": {"lid": 1.0}, "ease": "step"}]},
                LU: {"x": 1700, "turn": -0.2, "acoes": [{"t": 0.3, "do": "espreguicar", "dur": 1.6}], "keys": [{"t": 2.1, "pose": {"lid": 1.0}, "ease": "step"}]}}},
    {"seg": round(_d - 9.0, 2), "cenario": QAZ, "camera": {"x": 1300, "y": 470, "zoom": 1.6, "zoom_fim": 1.75}, "escurece": [0.45, 0.6], "titulo": "a lua dorme",
     "callout": [call(0.5, "ZZZ…", "roxo")], "objetos": {"lua": lua(1.0, None)}},
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
        for a in (p.get("atores") or {}).values():
            a["acoes"] = [ac for ac in a.get("acoes", []) if ac["t"] < d - 0.3] or a.get("acoes", [])[:1]
            if a.get("keys"):
                a["keys"] = [k for k in a["keys"] if k["t"] < d - 0.05]
        for o in (p.get("objetos") or {}).values():
            if o.get("keys"):
                ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                o["keys"] = transicoes(sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"]))

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0", "escala_personagens": 1.45,
       "nota": "Roteiro de 'Dorme, Acorda!' (take v1 de 19/11/2026, 2:56, Luisinho, estilo E12, nota 4,8): quartos de noite, dorme/acorda "
               "com olhinhos fechados e pulo de pé, cosquinha no pé, a pegadinha da ponte; a BANDA da turma no salão (Luisinho na bateria, "
               "Laurinha no sax e no teclado) nos intervalos e nos últimos refrões. Gerado por scripts/roteiros/ep21_dorme_acorda.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = sum(len(v) for v in partes.values())
print("roteiro:", n, "planos ·", round(song["duration"] / n, 1), "s por plano")
for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    print(chave, [round(t1 - t0, 1) for t0, t1, _ in planos_tempo(k_info, planos)])
