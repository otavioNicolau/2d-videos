"""Roteiro verso a verso do canal FOFOLUCOS — 04 "Tem Criança Debaixo da Cama!" (take inteiro, 3:23, 136 BPM, Sol menor,
estilo F4 — groove próprio, nota 5) → canais/fofolucos/musicas/04_tem_crianca_debaixo_da_cama/roteiro.json.

MEDO BOBO AO CONTRÁRIO: de noite o Bilu deita, apaga a luz e ouve "crec, crec!" debaixo da cama — e se for uma CRIANÇA?!
Refrão = a turma em pânico fofo (tremendo, abraçadinha, pedindo ajuda). Ponte = coragem: respira fundo, cara de valente
(RAWR), acende a LANTERNA (prop `lanterna`, facho de luz), abaixa devagarinho, levanta o lençol… um, dois, três!
2º verso = a VIRADA: a turma levanta o lençol e era o NHOQUE comendo BISCOITO escondido (item novo `biscoito`).
Noite: cenários de quarto com `escurece` (véu escuro); a luz volta na revelação.
Os tempos da letra desta música foram corrigidos à mão (o alinhador se perdeu depois do 1º refrão; backup em
analise/letra.auto.json e song.auto.json).
Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — CABEÇA / BUSTO / CORPO, espaço ≥ 430, nunca monstrinho na frente da própria cor
(Bilu×azul, Teco×roxo, Gogo×verde, Mimi×rosa, Zuzu×laranja, Nhoque×vermelho), closes do Zuzu em BUSTO, nunca "monstro".
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo04_tem_crianca_debaixo_da_cama.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("fofolucos/ep04-tem-crianca-debaixo-da-cama", "04_tem_crianca_debaixo_da_cama", "bilu")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
VILA, PARQUE, QUARTO, PALCO, NOITE, ESCOLA, COZ = "mon_vila", "mon_parque", "mon_quarto", "mon_palco", "mon_noite", "mon_escola", "mon_cozinha"
ESCURO = [0.42, 0.42]                                      # quarto de noite, luz apagada


def dur(T):
    return [round(t1 - t0, 2) for t0, t1, _ in T]


def a(x, *acoes, turn=0.0, **kw):
    out = []
    for ac in acoes:
        do, t = ac[0], (ac[1] if len(ac) > 1 else 0.0)
        d = {"t": t, "do": do, "dur": "resto"}
        if do == "dance":
            d["style"] = ac[2] if len(ac) > 2 else "festa"
        elif len(ac) > 2:
            d["dur"] = ac[2]
        out.append(d)
    return {"x": x, "turn": turn, "acoes": out, **kw}


def g(x, *acoes, turn=0.0):
    return a(x, *acoes, turn=turn, y=1010, depth=0.85)


def obj(id_, x, y, depth, d, z=1, fixo=None, lin=None, pts=None):
    d = max(0.6, d)
    ks = [{"t": 0.0, "pose": dict(fixo or {}), "ease": "step"}]
    for c, (v0, v1) in (lin or {}).items():
        ks[0]["pose"][c] = float(v0)
        ks.append({"t": round(d - 0.06, 2), "pose": {c: float(v1)}, "ease": "linear"})
    for c, vs in (pts or {}).items():
        ks += [{"t": round(t, 2), "pose": {c: float(v)}, "ease": "out"} for t, v in vs]
    return {"id": id_, "x": x, "y": y, "z": z, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def cama(x=1300):
    """cama atrás do monstrinho e lençol na frente (o monstrinho "deitado"), como no 'Dorme, Acorda' da Laurinha."""
    return {"cama": {"id": "cama", "x": x, "y": 930, "z": 1, "depth": 0.8},
            "lencol": {"id": "lencol", "x": x, "y": 930, "z": 5, "depth": 0.75}}


def lanterna(x, d, liga_em=None, dirc=0.0, depth=0.8, y=960):
    pts = {"liga": [(liga_em, 1.0)]} if liga_em is not None else None
    return obj("lanterna", x, y, depth, d, z=5, fixo={"liga": 0.0 if liga_em is not None else 1.0, "dir": dirc}, pts=pts)


def banda(cen, d, cam=None, extra=None):
    p = R.banda(cen, d, teclado=True, sax=ZU, bateria=BI, cam=cam or {"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["cantam"] = [ZU]
    return p


def em(t0, versos, *alvos, default=0.4):
    return R.tp(t0, versos, *alvos, default=default)


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "escurece": ESCURO, "titulo": "de noite, no quarto",
     "callout": [call(0.4, "TEM CRIANÇA DEBAIXO DA CAMA?", "roxo")], "cantam": [BI],
     "objetos": cama(1300), "atores": {BI: a(1300, ("look_around", 0.3), expr="scared")}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300), "escurece": ESCURO, "tremor": [0.3], "callout": [call(0.2, "AI, AI, AI…", "laranja")],
     "cantam": [BI], "atores": {BI: a(1300, ("shock_reaction", 0.2, 0.8), expr="scared")}},
    {"linhas": 1, "cenario": "mon_raios_laranja", "camera": GCAM, "flash": True, "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.1, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {TE: g(210, ("rawr", 0.3), turn=0.2), GO: g(710, ("rawr", 0.38)), BI: g(1210, ("rawr", 0.46)),
                NH: g(1710, ("rawr", 0.54), turn=-0.2)}},
    {**banda(PALCO, max(0.6, d[3]), extra={MI: a(2300, ("dance", 0.0, "treme"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: o Bilu vai dormir… crec, crec! ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": NOITE, "camera": corpo(800, 1800), "callout": [call(0.4, "DE NOITE…", "roxo")], "cantam": [BI],
     "atores": {BI: a(700, turn=0.3) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 1300, "dur": 1.6}, {"t": 1.7, "do": "wave", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "callout": [call(0.3, "BOA NOITE!", "azul")], "cantam": [BI],
     "objetos": cama(1300), "atores": {BI: a(1300, expr="sleepy")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "escurece": [0.0, 0.42], "callout": [call(0.3, "APAGOU A LUZ…", "roxo")],
     "cantam": [BI], "objetos": cama(1300), "atores": {BI: a(1300, expr="sleepy")}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300), "escurece": ESCURO, "callout": [call(0.5, "UM BARULHO?!", "laranja")],
     "cantam": [BI], "objetos": cama(1300), "atores": {BI: a(1300, ("look_around", 0.3), expr="surprised")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "escurece": ESCURO, "tremor": [0.2, 1.0],
     "callout": [call(0.2, "CREC, CREC!", "vermelho")], "cantam": [BI],
     "objetos": cama(1300), "atores": {BI: a(1300, ("shock_reaction", 0.2, 0.9), expr="scared")}},
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1300), "escurece": ESCURO, "callout": [call(0.3, "QUE PAVOR!", "roxo")], "cantam": [BI],
     "atores": {BI: a(1300, ("dance", 0.0, "treme"), expr="scared")}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300), "escurece": ESCURO, "callout": [call(0.3, "SERÁ QUE É UMA CRIANÇA?!", "laranja")],
     "cantam": [BI], "atores": {BI: a(1300, ("pensar", 0.2), expr="scared")}},
    {"linhas": 1, "cenario": NOITE, "camera": cab(1300), "callout": [call(0.3, "ME AJUDA!", "vermelho")], "cantam": [BI],
     "atores": {BI: a(1300, ("apontar_camera", 0.2), expr="scared")}},
]


# ───────── refrão: TEM CRIANÇA DEBAIXO DA CAMA! ─────────
REF = {
    1: dict(susto=((TE, MI), QUARTO), chama=(GO, NOITE), treme=("mon_xadrez_azul", (MI, ZU, NH)), abraco=((ZU, BI, NH), QUARTO)),
    2: dict(susto=((GO, NH), QUARTO), chama=(MI, NOITE), treme=("mon_xadrez_verde", (BI, MI, TE)), abraco=((TE, GO, MI), QUARTO)),
    3: dict(susto=((BI, ZU), QUARTO), chama=(TE, NOITE), treme=("mon_xadrez_rosa", (GO, ZU, BI)), abraco=((MI, NH, GO), QUARTO)),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        tai = min(em(t0, versos, "ai,", "ai", default=round(dd * 0.5, 2)), round(dd - 0.6, 2))
        if i % 4 == 0:                                     # "Tem criança… / Ai, ai, ai, quem vai olhar?" — susto em BUSTO
            (p_, q_), cen = cfg["susto"]
            out.append({"linhas": 2, "cenario": cen, "camera": busto(1300), "escurece": ESCURO, "tremor": [tai], "cantam": [p_],
                        "callout": [call(0.1, "TEM CRIANÇA DEBAIXO DA CAMA!", "roxo"), call(tai, "QUEM VAI OLHAR?", "laranja")],
                        "atores": {p_: a(900, ("shock_reaction", tai, 0.9), turn=0.25, expr="scared"),
                                   q_: a(1700, ("shock_reaction", tai + 0.08, 0.9), turn=-0.25, expr="scared")}})
        elif i % 4 == 1:                                   # "Monstrinho, vem me ajudar!" — CABEÇA chamando
            q_, cen = cfg["chama"]
            cam = busto(1300) if q_ == ZU else cab(1300)
            out.append({"linhas": 2, "cenario": cen, "camera": cam, "cantam": [q_],
                        "callout": [call(round(dd * 0.45, 2), "VEM ME AJUDAR!", "vermelho")],
                        "atores": {q_: a(1300, ("apontar_camera", round(dd * 0.4, 2)), expr="scared")}})
        elif i % 4 == 2:                                   # a dança do medo (treme) no xadrez
            cen, quem = cfg["treme"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["estrelas"], "flash": n == 1, "cantam": [quem[1]],
                        "callout": [call(0.1, "AI, AI, AI!", "laranja")],
                        "atores": {c: g(x, ("dance", 0.05 * k, "treme"), turn=tv) for k, (c, x, tv) in
                                   enumerate(zip(quem, (380, 960, 1540), (0.2, 0.0, -0.2)))}})
        else:                                              # abraçadinhos de medo no quarto escuro
            (l_, m_, r_), cen = cfg["abraco"]
            out.append({"linhas": 2, "cenario": cen, "camera": corpo(1300), "escurece": ESCURO, "cantam": [m_],
                        "callout": [call(round(dd * 0.45, 2), "MONSTRINHO, VEM ME AJUDAR!", "roxo")],
                        "atores": {l_: a(640, ("abraco", 0.2), turn=0.3, expr="scared"), m_: a(1300, ("dance", 0.0, "treme"), expr="scared"),
                                   r_: a(1960, ("abraco", 0.3), turn=-0.3, expr="scared")}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 1}, {"seg": 4.6}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": cab(1300), "cantam": [GO], "callout": [call(0.2, "FOFOLUCOS!", "roxo")],
     "atores": {GO: a(1300, ("rawr", 0.2), ("apontar_camera", 2.2))}},
    {**banda(PALCO, max(0.6, d[1]), extra={TE: a(2300, ("dance", 0.0, "treme"), turn=-0.3)}), "titulo": "a banda"},
    {"seg": max(0.6, d[2]), "cenario": "mon_xadrez_laranja", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança",
     "cantam": [MI], "atores": {MI: g(380, ("dance", 0.0, "cintura"), turn=0.2), TE: g(960, ("dance", 0.1, "treme")),
                                 GO: g(1540, ("dance", 0.0, "cintura"), turn=-0.2)}},
]


# ───────── ponte: coragem! ─────────
T = R.tempos("ponte#1", [{"linhas": 2}, {"linhas": 2}, {"linhas": 2}, {"linhas": 2}, {"linhas": 1}])
d = dur(T)
tv = em(T[0][0], T[0][2], "valente!", "valente", default=round(d[0] * 0.5, 2))
tl = em(T[1][0], T[1][2], "lanterna…", "lanterna", default=0.4)
t3 = em(T[3][0], T[3][2], "três…", "três", default=round(d[3] * 0.7, 2))
R.partes["ponte#1"] = [
    {"linhas": 2, "cenario": PARQUE, "camera": cab(1300), "callout": [call(0.1, "RESPIRA FUNDO!", "azul"), call(tv, "CARA DE VALENTE!", "vermelho")],
     "cantam": [BI], "atores": {BI: a(1300, ("rawr", tv), expr="determined")}},
    {"linhas": 2, "cenario": QUARTO, "camera": corpo(1300), "escurece": ESCURO, "callout": [call(tl, "ACENDE A LANTERNA!", "amarelo")],
     "cantam": [TE], "objetos": {"lt": lanterna(1150, d[1], liga_em=tl, dirc=0.0)},
     "atores": {TE: a(900, ("rawr", tl + 0.4, 0.8), turn=0.35, expr="determined"), BI: a(1700, turn=-0.3, expr="scared")}},
    {"linhas": 2, "cenario": "mon_brilho_laranja", "camera": GCAM, "callout": [call(0.1, "E MAIS!", "roxo"), call(0.9, "ABAIXA DEVAGARINHO!", "verde")],
     "cantam": [MI], "atores": {BI: g(380, ("dance", 0.3, "agacha"), turn=0.2), MI: g(960, ("dance", 0.35, "agacha")),
                                 GO: g(1540, ("dance", 0.4, "agacha"), turn=-0.2)}},
    {"linhas": 2, "cenario": QUARTO, "camera": corpo(1300), "escurece": ESCURO, "tremor": [t3],
     "callout": [call(0.1, "LEVANTA O LENÇOL!", "azul"), call(t3, "UM, DOIS, TRÊS…", "laranja")], "cantam": [ZU],
     "objetos": {**cama(1300), "lt": lanterna(900, d[3], dirc=0.0)},
     "atores": {ZU: a(700, ("look_around", 0.1), turn=0.4, expr="determined"), GO: a(1900, ("look_around", 0.2), turn=-0.4, expr="determined")}},
    {"linhas": 1, "cenario": "mon_raios_azul", "camera": GCAM, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "LANTERNA ACESA!", "amarelo")], "cantam": [MI],
     "objetos": {"l1": lanterna(560, d[4], dirc=-0.15, depth=0.85, y=1000), "l2": lanterna(1500, d[4], dirc=-0.35, depth=0.85, y=1000)},
     "atores": {MI: g(380, ("rawr", 0.2), turn=0.2), ZU: g(960, ("rawr", 0.28)), NH: g(1540, ("rawr", 0.36), turn=-0.2)}},
]


# ───────── 2º verso: a VIRADA — era o Nhoque comendo biscoito! ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": NOITE, "camera": corpo(1300), "callout": [call(0.2, "JUNTOU A TURMA TODA!", "roxo")], "cantam": [GO],
     "objetos": {"lt": lanterna(1300, d[0], dirc=0.0)},
     "atores": {GO: a(640, ("walk", 0.0), turn=0.3) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 900, "dur": 1.2}]},
                MI: a(1960, ("walk", 0.0), turn=-0.3) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 1700, "dur": 1.2}]}}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300), "escurece": ESCURO, "callout": [call(0.2, "QUE EMOÇÃO!", "laranja")],
     "cantam": [MI], "objetos": {"lt": lanterna(1300, d[1], dirc=-0.05, depth=0.7)},
     "atores": {GO: a(900, turn=0.3, expr="determined"), MI: a(1700, turn=-0.3, expr="determined")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "escurece": ESCURO, "tremor": [0.5],
     "callout": [call(0.2, "LEVANTARAM O LENÇOL…", "azul")], "cantam": [BI],
     "objetos": {**cama(1300), "lt": lanterna(800, d[2], dirc=0.02)},
     "atores": {BI: a(640, ("look_around", 0.1), turn=0.4, expr="scared"), TE: a(1960, ("look_around", 0.2), turn=-0.4, expr="scared")}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300), "escurece": ESCURO, "tremor": [0.3], "callout": [call(0.2, "QUEM TAVA LÁ?!", "vermelho")],
     "cantam": [BI], "atores": {BI: a(1300, ("shock_reaction", 0.2, 0.9), expr="scared")}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300), "flash": True, "fx": ["estrelas"], "callout": [call(0.1, "O NHOQUE!", "roxo")],
     "cantam": [NH], "atores": {NH: a(1300, ("bacana", 0.3), segura="biscoito")}},
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1300), "callout": [call(0.2, "CREC, CREC!", "laranja")], "cantam": [NH],
     "atores": {NH: a(1300, segura="biscoito") | {"acoes": [{"t": 0.1, "do": "comer", "item": "biscoito", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "fx": ["confete"], "callout": [call(0.2, "CRIANÇA? QUE CRIANÇA?", "verde")],
     "cantam": [NH], "atores": {BI: a(640, ("laugh", 0.3), turn=0.3), NH: a(1300, ("laugh", 0.1), segura="biscoito_mordido"),
                                 MI: a(1960, ("laugh", 0.4), turn=-0.3)}},
    {"linhas": 1, "cenario": PARQUE, "camera": cab(1300), "fx": ["coracoes"], "callout": [call(0.2, "TÁ DIVERTIDO!", "rosa")],
     "cantam": [NH], "atores": {NH: a(1300, ("laugh", 0.2), segura="biscoito_mordido")}},
]


# ───────── intervalo 2 (só instrumental, ~15 s) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 3, 2)
R.partes["intervalo#2"] = [
    {**banda(PALCO, d1, extra={NH: a(2300, ("dance", 0.0, "festa"), turn=-0.3, segura="biscoito")}), "titulo": "a banda"},
    {"seg": d1, "cenario": "mon_xadrez_roxo", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança", "cantam": [GO],
     "atores": {GO: g(380, ("dance", 0.0, "cintura"), turn=0.2), ZU: g(960, ("dance", 0.1, "treme")),
                MI: g(1540, ("dance", 0.0, "cintura"), turn=-0.2)}},
    {"seg": round(D2 - 2 * d1, 2), "cenario": "mon_raios_verde", "camera": GCAM, "fx": ["estrelas"], "titulo": "pezinho", "cantam": [TE],
     "atores": {TE: g(210, ("dance", 0.0, "pezinho"), turn=0.2), BI: g(710, ("dance", 0.05, "pezinho")),
                ZU: g(1210, ("dance", 0.1, "pezinho")), NH: g(1710, ("dance", 0.15, "pezinho"), turn=-0.2)}},
]


# ───────── final: e você? tem medo de quê? + convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": cab(1300), "callout": [call(0.2, "E VOCÊ? TEM MEDO DE QUÊ?", "roxo")], "cantam": [BI],
     "atores": {BI: a(1300, ("apontar_camera", 0.1))}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "cantam": [ZU],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {ZU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": VILA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")], "cantam": [MI],
     "atores": {MI: a(900, ("point", 0.1), turn=0.3), TE: a(1700, ("wave", 0.2), turn=-0.25)}},
    {"linhas": 1, "cenario": "mon_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "cantam": [GO],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {GO: g(560, ("point", 0.2), ("rawr", max(0.6, round(d[3] - 1.4, 2))), turn=0.2) | {"depth": 1.0}}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.0, "cenario": NOITE, "camera": corpo(1300), "fx": ["estrelas"], "cantam": [BI],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.4, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn, y=y, depth=dp, z=zz) for k, (c, x, y, dp, zz, tn) in
                enumerate(((TE, 400, 880, 0.62, 2, 0.3), (GO, 1000, 880, 0.62, 2, 0.15), (MI, 1600, 880, 0.62, 2, -0.15),
                           (ZU, 2200, 880, 0.62, 2, -0.3), (BI, 700, 975, 0.74, 3, 0.2), (NH, 1900, 975, 0.74, 3, -0.2)))}},
    {"seg": round(dfim - 3.0, 2), "cenario": QUARTO, "camera": cab(1300), "flash": True, "callout": [call(0.2, "RAWR!", "vermelho")],
     "titulo": "o último RAWR (com biscoito)", "cantam": [NH],
     "atores": {NH: a(1300, ("rawr", 0.1), segura="biscoito_mordido")}},
]


# ── vida no cenário (sem contorno): nuvens andando, lua com carinha, bolhas nos fundos ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    if cen in (PARQUE, VILA):
        x0 = (300, 1700, 900, 2100)[j % 4]
        ob.setdefault("nv", obj("nuvem", x0, 300, 0.32, dd, z=0, fixo={"cara": 1.0}, lin={"x": (x0, x0 + 280)}))
    # (sem a lua extra na NOITE: o cenário já tem lua e as duas apareciam juntas no storyboard)
    elif cen.startswith(("mon_raios_", "mon_xadrez_", "mon_brilho_")) or cen in (ESCOLA, COZ):
        x0 = (300, 1650, 800, 1300)[j % 4]
        ob.setdefault("bo", obj("bolha", x0, 1000, 0.3, dd, z=0, fixo={"tam": 1.0}, lin={"y": (1000, 250), "balanco": (0.0, round(dd, 1))}))
    if not ob:
        sb.pop("objetos", None)


for chave, planos in R.partes.items():
    k_info = chave if chave in R.info else f"{chave}#1"
    for j, (p_, (t0, t1, _)) in enumerate(zip(planos, R.tempos(k_info, planos))):
        for sb in [p_] + list((p_.get("tela_dividida") or {}).get("paineis", [])):
            _ambiente(sb, round(t1 - t0, 2), j)

R.salvar("Roteiro do canal Fofolucos — 04 'Tem Criança Debaixo da Cama!' (take inteiro, 3:23, F4, nota 5): o Bilu "
         "ouve 'crec, crec' no quarto escuro e acha que é uma criança; refrão do pânico fofo; ponte da coragem com a "
         "lanterna; a virada: era o Nhoque comendo biscoito. Gerado por scripts/roteiros/fo04_tem_crianca_debaixo_da_cama.py.")
