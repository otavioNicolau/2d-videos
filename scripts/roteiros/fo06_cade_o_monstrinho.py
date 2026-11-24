"""Roteiro verso a verso do canal FOFOLUCOS — 06 "Cadê o Monstrinho?" (take inteiro, 2:50, 136 BPM, estilo F5 — groove
próprio com o baixo reforçado, nota 4,9; letra 5 a 8 anos) → canais/fofolucos/musicas/06_cade_o_monstrinho/roteiro.json.

ESCONDE-ESCONDE NA VILA MONSTRINHA: o Gogo conta (e espia com o olhão!) e cada monstrinho se esconde MAL — o chifre do Bilu
fica de fora da MOITA (prop novo `moita`), a antena do Teco aparece em cima do MURO (prop novo `muro`), a Mimi finge que é
flor no CANTEIRO (prop novo `canteiro`) e a barriga do Nhoque ronca. Refrão = o Gogo procura (tá aqui? tá ali?) e ACHA um
monstrinho diferente a cada refrão (Bilu, Teco, Mimi) — "achei! sai daí! RAWR!". Ponte = comandos de esconder.
2º verso = a VIRADA: ninguém acha o Zuzu… ele é LARANJA e estava no meio das ABÓBORAS (prop novo `abobora`), dormindo.
Esconderijos no `mon_parque` (céu e grama: ninguém na frente da própria cor); o Gogo procura na `mon_vila` (longe da casa
verde; o Teco longe da casa roxa, a Mimi longe da rosa, o Zuzu longe da laranja).
Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — CABEÇA / BUSTO / CORPO, espaço ≥ 430, chifres/antenas sempre no quadro, closes do
Zuzu em BUSTO, nunca "monstro".
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo06_cade_o_monstrinho.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("fofolucos/ep06-cade-o-monstrinho", "06_cade_o_monstrinho", "gogo")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
VILA, PARQUE, PALCO, CEU = "mon_vila", "mon_parque", "mon_palco", "mon_abertura"
CHAO = 935
ESCONDE = 0   
PULO = {"bilu": 170, "teco": 190, "mimi": 220, "nhoque": 200}   # o ACHEI: sobe até o rosto aparecer (chifre/antena no quadro)
                   # quanto o monstrinho "afunda" atrás do esconderijo (só o topo aparece)


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


def anda(at, x0, x1, d):
    """o ator atravessa de x0 a x1 durante o plano (run/sneak/walk com to_x)."""
    at["x"] = x0
    for ac in at["acoes"]:
        if ac["do"] in ("run", "sneak", "walk"):
            ac["to_x"] = float(x1)
            ac["dur"] = round(max(0.6, d) - 0.1, 2)
    return at


def olho_fechado(at, t_abre=None, meio=False):
    """Gogo contando: olhão fechado; `meio` = espiando (pálpebra pela metade); `t_abre` abre de vez."""
    ks = [{"t": 0.0, "pose": {"lid": 0.55 if meio else 1.0}, "ease": "step"}]
    if t_abre is not None:
        ks.append({"t": round(t_abre, 2), "pose": {"lid": 0.0}, "ease": "out"})
    at["keys"] = at.get("keys", []) + ks
    return at


def escondido(quem, x, d, sai_em=None, depth=1.0, **kw):
    """monstrinho atrás do esconderijo (afundado `ESCONDE`); `sai_em` = instante do ACHEI (pula pra cima com RAWR)."""
    at = a(x, *([("rawr", round(sai_em + 0.1, 2))] if sai_em is not None else []), y=CHAO + ESCONDE, depth=depth, z=2, **kw)
    if sai_em is not None:
        at["keys"] = [{"t": 0.0, "pose": {"y": float(CHAO + ESCONDE)}, "ease": "step"},
                      {"t": round(sai_em, 2), "pose": {"y": float(CHAO + ESCONDE)}, "ease": "step"},
                      {"t": round(sai_em + 0.25, 2), "pose": {"y": float(CHAO - PULO.get(quem, 200))}, "ease": "out"}]
    return at


ESCONDERIJO = {BI: ("moita", {"balanca": 0.0}), TE: ("muro", {}), MI: ("canteiro", {}), NH: ("moita", {})}
PROF = {BI: 0.85, TE: 1.0, MI: 1.25, NH: 0.85}      # tamanho do esconderijo: só o topo de quem se esconde aparece


def esconderijo(quem, x, d, depth=1.0, mexe=False):
    pid, fixo = ESCONDERIJO[quem]
    lin = {"onda": (0.0, round(d, 1))} if pid == "moita" else ({"vento": (0.0, round(d * 0.8, 1))} if pid == "canteiro" else None)
    o = obj(pid, x, CHAO, depth, d, z=4, fixo=dict(fixo), lin=lin)
    if mexe and pid == "moita":
        o["keys"][0]["pose"]["balanca"] = 1.0
    return o


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
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "titulo": "esconde-esconde na Vila Monstrinha", "cantam": [GO],
     "callout": [call(round(d[0] - 1.8, 2), "CADÊ O MONSTRINHO?", "roxo")],
     "atores": {GO: olho_fechado(a(700, ("estatua", 0.0), turn=0.2)),
                BI: anda(a(1500, ("run", 0.0), turn=-0.45), 1500, 2500, d[0]),
                MI: anda(a(1900, ("run", 0.0), turn=-0.45), 1900, 2900, d[0])}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "cantam": [GO],
     "callout": [call(0.1, "UM, DOIS, TRÊS…", "azul"), call(round(d[1] * 0.6, 2), "LÁ VOU EU!", "amarelo")],
     "atores": {GO: olho_fechado(g(960, ("point", round(d[1] * 0.6, 2))) | {"depth": 1.3}, t_abre=round(d[1] * 0.55, 2))}},
    {"linhas": 1, "cenario": "mon_raios_laranja", "camera": GCAM, "flash": True, "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.1, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {TE: g(210, ("rawr", 0.3), turn=0.2), GO: g(710, ("rawr", 0.38)), BI: g(1210, ("rawr", 0.46)),
                NH: g(1710, ("rawr", 0.54), turn=-0.2)}},
    {**banda(PALCO, max(0.6, d[3]), extra={MI: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: o Gogo conta e cada um se esconde (mal!) ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.3, "ESCONDE-ESCONDE!", "laranja")],
     "atores": {TE: anda(a(300, ("run", 0.0), turn=0.45), 300, 1300, d[0]), NH: anda(a(2300, ("run", 0.0), turn=-0.45), 2300, 1700, d[0]),
                ZU: anda(a(800, ("run", 0.0), turn=0.45), 800, -400, d[0])}},
    {"linhas": 1, "cenario": "mon_brilho_laranja", "camera": GCAM, "cantam": [GO], "callout": [call(0.3, "O GOGO VAI CONTAR!", "verde")],
     "atores": {GO: olho_fechado(g(960, ("estatua", 0.0)) | {"depth": 1.3})}},
    {"linhas": 1, "cenario": VILA, "camera": busto(870, 520), "cantam": [GO], "callout": [call(0.4, "ESPIOU!", "amarelo")],
     "atores": {GO: olho_fechado(a(700, ("estatua", 0.0), turn=0.1, expr="sly"), meio=True)}},
    {"linhas": 1, "cenario": "mon_raios_azul", "camera": GCAM, "cantam": [MI], "callout": [call(0.2, "NÃO VALE ESPIAR!", "vermelho")],
     "atores": {MI: g(960, ("shake_fist", 0.1)) | {"depth": 1.3, "expr": "angry"}}},
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.3, "O BILU ATRÁS DA MOITA…", "azul")],
     "objetos": {"moita": esconderijo(BI, 1300, d[4], depth=PROF[BI], mexe=True)},
     "atores": {BI: escondido(BI, 1300, d[4], depth=0.95)}},
    {"linhas": 1, "cenario": PARQUE, "camera": cab(1300), "cantam": [GO], "callout": [call(0.2, "O CHIFRE FICOU DE FORA!", "laranja")],
     "objetos": {"moita": esconderijo(BI, 1300, d[5], depth=PROF[BI], mexe=True)},
     "atores": {BI: escondido(BI, 1300, d[5], depth=0.95)}},
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.3, "O TECO ATRÁS DO MURO…", "roxo")],
     "objetos": {"muro": esconderijo(TE, 1300, d[6], depth=PROF[TE])},
     "atores": {TE: escondido(TE, 1300, d[6], depth=0.95)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300, 460), "cantam": [GO], "callout": [call(0.2, "E A ANTENA?", "verde")],
     "objetos": {"muro": esconderijo(TE, 1300, d[7], depth=PROF[TE])},
     "atores": {TE: escondido(TE, 1300, d[7], depth=0.95)}},
]


# ───────── refrão: cadê o monstrinho? tá aqui? tá ali? achei! sai daí! RAWR! ─────────
REF = {
    1: dict(acha=BI, danca=("mon_xadrez_verde", (BI, MI, NH)), close=(BI, "mon_raios_laranja")),
    2: dict(acha=TE, danca=("mon_xadrez_azul", (TE, ZU, NH)), close=(TE, "mon_brilho_laranja")),
    3: dict(acha=MI, danca=("mon_xadrez_roxo", (MI, BI, ZU)), close=(MI, "mon_raios_azul")),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    quem = cfg["acha"]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        if i % 4 == 0:                                     # "Cadê o monstrinho? Tá aqui? Tá ali?" — o Gogo procura na Vila
            out.append({"linhas": 2, "cenario": VILA, "camera": corpo(1300), "cantam": [GO],
                        "callout": [call(0.1, "CADÊ O MONSTRINHO?", "roxo"), call(round(dd * 0.5, 2), "TÁ AQUI? TÁ ALI?", "amarelo")],
                        "atores": {GO: anda(a(400, ("look_around", 0.0), turn=0.3), 400, 950, dd)}})
        elif i % 4 == 1:                                   # "Cadê o monstrinho? Achei! Sai daí! RAWR!" — achou!
            ta = em(t0, versos, "achei", default=round(dd * 0.45, 2))
            # (o Gogo é verde: no parque — grama e árvores — ele não aparece; quem procura fica na Vila)
            out.append({"linhas": 2, "cenario": PARQUE, "camera": corpo(1300), "cantam": [GO],
                        "callout": [call(round(ta, 2), "ACHEI!", "laranja"), call(round(ta + 0.6, 2), "SAI DAÍ! RAWR!", "vermelho")],
                        "objetos": {ESCONDERIJO[quem][0]: esconderijo(quem, 1300, dd, depth=PROF[quem], mexe=True)},
                        "atores": {quem: escondido(quem, 1300, dd, sai_em=ta, depth=0.9)}})
        elif i % 4 == 2:                                   # a dança no fundo colorido (ninguém na frente da própria cor)
            cen, trio = cfg["danca"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "flash": n == 1, "cantam": [trio[0]],
                        "callout": [call(0.1, "CADÊ O MONSTRINHO?", "roxo")],
                        "atores": {c: g(x, ("dance", 0.05 * j, st), turn=tv) for j, (c, x, tv, st) in
                                   enumerate(zip(trio, (380, 960, 1540), (0.2, 0.0, -0.2), ("festa", "chute", "festa")))}})
        else:                                              # o achado faz RAWR de pertinho
            q, cen = cfg["close"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "cantam": [q], "fx": ["estrelas"],
                        "callout": [call(round(dd * 0.5, 2), "SAI DAÍ! RAWR!", "vermelho")],
                        "atores": {q: g(960, ("rawr", round(dd * 0.45, 2))) | {"depth": 1.35}}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 1, "cenario": "mon_raios_roxo", "camera": GCAM, "cantam": [NH], "callout": [call(0.2, "FOFOLUCOS! RAWR!", "laranja")],
     "atores": {NH: g(700, ("rawr", 0.2), turn=0.2) | {"depth": 1.1}, ZU: g(1300, ("rawr", 0.35), turn=-0.2) | {"depth": 1.1}}},
    {**banda(PALCO, max(0.6, d[1]), extra={TE: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria", "linhas": 1},
    {"seg": max(0.6, d[2]), "cenario": PARQUE, "camera": corpo(1300), "fx": ["confete"], "titulo": "a turma dança no parque", "cantam": [MI],
     "atores": {MI: a(640, ("dance", 0.0, "festa"), turn=0.3), BI: a(1300, ("dance", 0.1, "chute")), NH: a(1960, ("dance", 0.05, "festa"), turn=-0.3)}},
]


# ───────── ponte: comandos de esconder ("Tapa os olhos!" entra colado no fim do intervalo) ─────────
T = R.tempos("ponte#1", [{"seg": 1.5}] + [{"linhas": 1}] * 3 + [{"linhas": 2}] + [{"linhas": 1}] * 3)
d = dur(T)
R.partes["ponte#1"] = [
    {"seg": 1.5, "cenario": "mon_brilho_rosa", "camera": GCAM, "cantam": [GO], "callout": [call(0.0, "TAPA OS OLHOS!", "laranja")],
     "atores": {GO: olho_fechado(g(960, ("estatua", 0.0)) | {"depth": 1.3})}},
    {"linhas": 1, "cenario": "mon_raios_roxo", "camera": GCAM, "cantam": [BI], "callout": [call(0.1, "CONTA ATÉ TRÊS!", "azul")],
     "atores": {BI: g(960, ("point", 0.1)) | {"depth": 1.3}}},
    {"linhas": 1, "cenario": "mon_xadrez_azul", "camera": GCAM, "cantam": [MI], "callout": [call(0.1, "NA PONTA DO PÉ…", "rosa")],
     "atores": {MI: anda(g(500, ("sneak", 0.0), turn=0.45) | {"depth": 1.1}, 500, 1400, d[2])}},
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "cantam": [TE], "callout": [call(0.1, "SE ESCONDE DE VEZ!", "roxo")],
     "objetos": {"muro": esconderijo(TE, 1500, d[3], depth=PROF[TE])},
     "atores": {TE: anda(a(500, ("run", 0.0), turn=0.45), 500, 1500, d[3]) | {"z": 2}}},
    {"linhas": 2, "cenario": "mon_brilho_azul", "camera": GCAM, "cantam": [NH], "callout": [call(0.1, "E MAIS! AGACHA BEM QUIETO!", "verde")],
     "atores": {NH: g(960, ("sit", 0.3)) | {"depth": 1.3}}},
    {"linhas": 1, "cenario": "mon_raios_verde", "camera": GCAM, "cantam": [ZU], "callout": [call(0.1, "SEGURA A RISADA!", "laranja")],
     "atores": {ZU: g(960, ("estatua", 0.0)) | {"depth": 1.3, "expr": "laughing"}}},
    {"linhas": 1, "cenario": "mon_xadrez_rosa", "camera": GCAM, "cantam": [GO], "callout": [call(0.1, "NINGUÉM FAZ BARULHO…", "azul")],
     "atores": {GO: anda(g(1400, ("sneak", 0.0), turn=-0.45) | {"depth": 0.95}, 1400, 600, d[6])}},
    {"linhas": 1, "cenario": "mon_brilho_laranja", "camera": GCAM, "cantam": [TE], "callout": [call(0.1, "PSIU! NEM UMA PISCADA!", "roxo")],
     "atores": {TE: g(960, ("estatua", 0.0)) | {"depth": 1.4, "expr": "surprised"}}},
]


# ───────── 2º verso: a Mimi flor, a barriga do Nhoque… e a VIRADA do Zuzu nas abóboras ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)


def aboboras(d, x=1300, depth=1.0):
    """o canteiro de abóboras (a do meio é a cabeça do Zuzu, que fica atrás)."""
    return {f"ab{j}": obj("abobora", x + dx, CHAO + dy, depth * s, d, z=4 if dy > 0 else 1, fixo={"tom": float(tm)})
            for j, (dx, dy, s, tm) in enumerate(((-560, 10, 1.0, 0), (-330, 40, 1.05, 2), (340, 40, 1.05, 1), (580, 10, 1.0, 0),
                                                  (-140, 90, 1.0, 1), (160, 90, 1.0, 2), (-450, -30, 0.85, 2), (470, -30, 0.85, 1)))}


R.partes["verso#2"] = [
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.2, "A MIMI NO CANTEIRO…", "rosa")],
     "objetos": {"canteiro": esconderijo(MI, 1300, d[0], depth=PROF[MI])},
     "atores": {MI: escondido(MI, 1300, d[0], depth=0.95)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300, 470), "cantam": [GO], "callout": [call(0.2, "FINGIU QUE ERA FLOR!", "amarelo")],
     "objetos": {"canteiro": esconderijo(MI, 1300, d[1], depth=PROF[MI])},
     "atores": {MI: escondido(MI, 1300, d[1], depth=0.95) | {"expr": "fofinho"}}},
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.2, "MAS A BARRIGA DO NHOQUE…", "vermelho")],
     "objetos": {"moita": esconderijo(NH, 1300, d[2], depth=PROF[NH], mexe=True)},
     "atores": {NH: escondido(NH, 1300, d[2], depth=0.95)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300, 460), "cantam": [GO], "tremor": [0.2, 0.7],
     "callout": [call(0.1, "RONC! RONC!", "laranja")],
     "objetos": {"moita": esconderijo(NH, 1300, d[3], depth=PROF[NH], mexe=True)},
     "atores": {NH: escondido(NH, 1300, d[3], depth=0.95) | {"expr": "surprised"}}},
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.2, "E O ZUZU? NINGUÉM ACHOU…", "laranja")],
     "atores": {GO: a(600, ("look_around", 0.0), turn=0.3), BI: a(1300, ("look_around", 0.1), expr="confused"),
                MI: a(2000, ("look_around", 0.05), turn=-0.3)}},
    {"linhas": 1, "cenario": "mon_raios_roxo", "camera": GCAM, "cantam": [GO], "callout": [call(0.2, "SUMIU? QUE MISTÉRIO!", "verde")],
     "atores": {GO: g(960, ("look_around", 0.0)) | {"depth": 1.3, "expr": "confused"}}},
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.2, "LARANJA ENTRE AS ABÓBORAS…", "laranja")],
     "objetos": aboboras(d[6]),
     "atores": {ZU: a(1300, ("estatua", 0.0), y=CHAO + 40, depth=0.95, z=2, keys=[{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"}])}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300, 560), "cantam": [GO], "fx": ["estrelas"],
     "callout": [call(0.2, "DORMINDO E RONCANDO!", "roxo"), call(round(d[7] * 0.55, 2), "ZZZ…", "azul")],
     "objetos": aboboras(d[7]),
     "atores": {ZU: a(1300, ("estatua", 0.0), y=CHAO + 40, depth=0.95, z=2, keys=[{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"}])}},
]


# ───────── intervalo 2 (só instrumental) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 2, 2)
R.partes["intervalo#2"] = [
    {**banda(PALCO, d1, extra={GO: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": round(D2 - d1, 2), "cenario": PARQUE, "camera": corpo(1300), "fx": ["confete"], "titulo": "o Zuzu acordou e dança", "cantam": [ZU],
     "objetos": {"ab0": obj("abobora", 2100, CHAO, 1.1, D2 - d1, z=1), "ab1": obj("abobora", 500, CHAO, 1.0, D2 - d1, z=1, fixo={"tom": 2.0})},
     "atores": {TE: a(700, ("dance", 0.0, "festa"), turn=0.3), ZU: a(1300, ("dance", 0.1, "chute")), BI: a(1900, ("dance", 0.05, "festa"), turn=-0.3)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": busto(870, 520), "cantam": [GO], "callout": [call(0.2, "E VOCÊ? ACHOU TODO MUNDO?", "roxo")],
     "atores": {GO: a(700, ("apontar_camera", 0.1), turn=0.1)}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"], "cantam": [ZU],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {ZU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": VILA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")], "cantam": [MI],
     "atores": {MI: a(900, ("point", 0.1), turn=0.3), NH: a(1700, ("wave", 0.2), turn=-0.25)}},
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
    {"linhas": 1, "seg": 3.0, "cenario": CEU, "camera": corpo(1300), "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.4, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn, y=y, depth=dp, z=zz) for k, (c, x, y, dp, zz, tn) in
                enumerate(((TE, 400, 880, 0.62, 2, 0.3), (GO, 1000, 880, 0.62, 2, 0.15), (MI, 1600, 880, 0.62, 2, -0.15),
                           (ZU, 2200, 880, 0.62, 2, -0.3), (BI, 700, 975, 0.74, 3, 0.2), (NH, 1900, 975, 0.74, 3, -0.2)))}},
    {"seg": round(dfim - 3.0, 2), "cenario": PARQUE, "camera": busto(1300, 560), "flash": True, "fx": ["confete"],
     "callout": [call(0.2, "RAWR!", "vermelho")], "titulo": "o Zuzu acorda: RAWR!", "cantam": [ZU],
     "objetos": aboboras(round(dfim - 3.0, 2)),
     "atores": {ZU: a(1300, ("rawr", 0.4), y=CHAO + 60, depth=0.95, z=2, expr="joy",
                      keys=[{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"}, {"t": 0.35, "pose": {"lid": 0.0}, "ease": "out"}])}},
]


# ── vida no cenário (sem contorno): nuvens andando no céu, bolhas nos fundos gráficos ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    if cen in (VILA, CEU, PARQUE):
        x0 = (300, 1700, 900, 2100)[j % 4]
        ob.setdefault("nv", obj("nuvem", x0, 300, 0.32, dd, z=0, fixo={"cara": 1.0}, lin={"x": (x0, x0 + 280)}))
    elif cen.startswith(("mon_raios_", "mon_xadrez_", "mon_brilho_")):
        x0 = (300, 1650, 800, 1300)[j % 4]
        ob.setdefault("bo", obj("bolha", x0, 1000, 0.3, dd, z=0, fixo={"tam": 1.0}, lin={"y": (1000, 250), "balanco": (0.0, round(dd, 1))}))
    if not ob:
        sb.pop("objetos", None)


for chave, planos in R.partes.items():
    k_info = chave if chave in R.info else f"{chave}#1"
    for j, (p_, (t0, t1, _)) in enumerate(zip(planos, R.tempos(k_info, planos))):
        for sb in [p_] + list((p_.get("tela_dividida") or {}).get("paineis", [])):
            _ambiente(sb, round(t1 - t0, 2), j)

R.salvar("Roteiro do canal Fofolucos — 06 'Cadê o Monstrinho?' (take inteiro, 2:50, F5, nota 4,9): esconde-esconde na Vila "
         "Monstrinha — o Gogo conta e espia; o chifre do Bilu na moita, a antena do Teco no muro, a Mimi flor no canteiro, a "
         "barriga do Nhoque roncando; refrão que acha um monstrinho por vez; ponte de comandos de esconder; a virada: o Zuzu "
         "laranja dormindo no meio das abóboras. Gerado por scripts/roteiros/fo06_cade_o_monstrinho.py.")
