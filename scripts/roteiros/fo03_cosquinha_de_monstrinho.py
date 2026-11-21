"""Roteiro verso a verso do canal FOFOLUCOS — 03 "Cosquinha de Monstrinho" (take "(1)" inteiro, 2:44, 108 BPM, Dó maior,
estilo F3 + groove dembow do latino, nota 4,9) → canais/fofolucos/musicas/03_cosquinha_de_monstrinho/roteiro.json.

A COSQUINHA: cada monstrinho tem um cantinho secreto (Bilu no chifrinho, Gogo na anteninha, Mimi no pelinho, Nhoque na
barriguinha) — a PENA (objeto novo `pena`, abana com `mexe`) encosta e ele CAI NA RISADA (ação nova `cosquinha`: olhinhos
apertados, mãos na barriga, contorce e quica). Refrão-desafio "quem aguenta? NINGUÉM!": a turma segura o riso e explode.
Ponte: o Teco tenta fazer cosquinha nele mesmo — não dá! — e o Gogo chega com a pena; comandos (pezinho, barriga, bracinho).
2º verso: o Zuzu de cara séria resiste à pena e ao "pincel" (2ª pena)… e a MOSQUINHA (objeto novo `mosquinha`) pousa no
chifrinho dele: ele rola de rir.
Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — CABEÇA / BUSTO / CORPO misturados, espaço ≥ 430 entre monstrinhos,
nunca monstrinho na frente de fundo da mesma cor (Bilu×azul, Teco×roxo, Gogo×verde, Mimi×rosa, Zuzu×laranja,
Nhoque×vermelho), NUNCA a palavra "monstro" nos letreiros.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo03_cosquinha_de_monstrinho.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import Roteiro, call  # noqa: E402

R = Roteiro("fofolucos/ep03-cosquinha-de-monstrinho", "03_cosquinha_de_monstrinho", "bilu")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
VILA, PARQUE, QUARTO, PALCO, NOITE, ESCOLA, COZ = "mon_vila", "mon_parque", "mon_quarto", "mon_palco", "mon_noite", "mon_escola", "mon_cozinha"


def dur(T):
    return [round(t1 - t0, 2) for t0, t1, _ in T]


# ── enquadramentos (bíblia §4; a câmera ainda sobe sozinha se algum chifre for cortar) ──
def cab(x=1300):
    return {"x": x, "y": 500, "zoom": 1.85, "zoom_fim": 1.95}


def busto(x=1300, y=560):
    return {"x": x, "y": y, "zoom": 1.55, "zoom_fim": 1.62}


def corpo(x=1300, x_fim=None):
    c = {"x": x, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    if x_fim:
        c["x_fim"] = x_fim
    return c


GCAM = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}


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


def pena(x, y, d, giro=-0.5, cor=1, depth=0.7, rapido=3.0, z=4):
    """a pena abanando (cosquinha): `mexe` cresce `rapido` voltas por segundo."""
    return obj("pena", x, y, depth, d, z=z, fixo={"giro": giro, "cor": float(cor)}, lin={"mexe": (0.0, round(d * rapido, 1))})


def pena_cab(y, d, cor=1, rapido=3.0):
    """pena num CLOSE: vem de FORA, pela direita, e só a ponta encosta no lado da cabeça (no storyboard 1 ela tapava o rosto).
    `y` = altura da mão que segura (chifrinho/anteninha ~430–520, bochecha ~640)."""
    return pena(1760, y, d, giro=-1.15, cor=cor, depth=0.42, rapido=rapido)


def banda(cen, d, cam=None, extra=None):
    """a banda da turma: Bilu na bateria, Zuzu no teclado; quem dança junto fica à DIREITA (bíblia §4)."""
    p = R.banda(cen, d, teclado=True, sax=ZU, bateria=BI, cam=cam or {"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["cantam"] = [ZU]
    return p


def ninguem_em(t0, versos, default):
    return R.tp(t0, versos, "ninguém!", "ninguém", default=default)


def rawr_em(t0, versos, default):
    return R.tp(t0, versos, "rawr", "rawr!", default=default)


# ───────── intro ─────────
# o 1º verso ("Lá na Vila Monstrinha") começa 0,1 s antes do fim da intro → a intro termina na banda, e o 1º plano do
# verso#1 cobre "Lá na Vila… / Tem segredo pra contar"
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "titulo": "a pena da cosquinha", "cantam": [BI],
     "callout": [call(0.3, "COSQUINHA DE MONSTRINHO!", "rosa")],
     "objetos": {"pena": obj("pena", 600, 720, 0.75, d[0], z=4, fixo={"giro": -1.0, "cor": 1.0},
                             lin={"x": (600, 1120), "y": (720, 640), "mexe": (0.0, round(d[0] * 2.5, 1))})},
     "atores": {BI: a(1300, ("cosquinha", 1.3), expr="determined")}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.2, "QUEM AGUENTA?", "laranja")], "cantam": [TE],
     "objetos": {"pena": pena(1150, 700, d[1], giro=-0.9, cor=2, depth=0.62)},
     "atores": {TE: a(900, ("cosquinha", 0.9), turn=0.25, expr="determined"), MI: a(1700, ("point", 0.2), ("laugh", 1.4), turn=-0.25)}},
    {"linhas": 1, "cenario": "mon_raios_laranja", "camera": GCAM, "flash": True, "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.1, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {TE: g(210, ("rawr", 0.3), turn=0.2), GO: g(710, ("rawr", 0.38)), BI: g(1210, ("rawr", 0.46)),
                NH: g(1710, ("rawr", 0.54), turn=-0.2)}},
    {**banda(PALCO, max(0.6, d[3]), extra={GO: a(2300, ("dance", 0.0, "cintura"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: o cantinho de cada um ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 7)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": corpo(800, 1800), "callout": [call(0.4, "UM SEGREDO!", "roxo")], "cantam": [MI],
     "atores": {MI: a(900, ("pensar", 0.3), turn=0.3), NH: a(1700, ("look_around", 0.6), turn=-0.3)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.3, "UM CANTINHO…", "amarelo")], "cantam": [TE],
     "atores": {TE: a(900, ("apontar_camera", 0.2), turn=0.25), ZU: a(1700, ("dance", 0.1, "pulinho"), turn=-0.25)}},
    {"linhas": 1, "cenario": "mon_brilho_azul", "camera": GCAM, "fx": ["estrelas"], "callout": [call(0.2, "RÁ-RÁ-RÁ!", "amarelo")],
     "cantam": [GO],
     "atores": {GO: g(380, ("cosquinha", 0.1), turn=0.2), MI: g(960, ("cosquinha", 0.2)), NH: g(1540, ("cosquinha", 0.3), turn=-0.2)}},
    {"linhas": 1, "cenario": COZ, "camera": cab(1300), "callout": [call(0.3, "NO CHIFRINHO!", "azul")], "cantam": [BI],
     "objetos": {"pena": pena_cab(500, d[3], cor=1)},
     "atores": {BI: a(1300, ("cosquinha", 0.5))}},
    {"linhas": 1, "cenario": PARQUE, "camera": cab(1300), "callout": [call(0.3, "NA ANTENINHA!", "verde")], "cantam": [GO],
     "objetos": {"pena": pena_cab(430, d[4], cor=3)},
     "atores": {GO: a(1300, ("cosquinha", 0.5))}},
    {"linhas": 1, "cenario": VILA, "camera": cab(1300), "fx": ["coracoes"], "callout": [call(0.3, "NO PELINHO!", "rosa")], "cantam": [MI],
     "objetos": {"pena": pena_cab(640, d[5], cor=2)},
     "atores": {MI: a(1300, ("cosquinha", 0.5))}},
    {"linhas": 1, "cenario": ESCOLA, "camera": busto(1300), "callout": [call(0.5, "NA BARRIGUINHA!", "laranja")], "cantam": [NH],
     "objetos": {"pena": pena(1450, 900, d[6], giro=-1.3, cor=1, depth=0.6)},
     "atores": {NH: a(1300, ("cosquinha", 0.7))}},
]


# ───────── refrão: cosquinha, cosquinha! quem aguenta? NINGUÉM! ─────────
# por ocorrência: (segura o riso e explode, close rindo com a pena, rebolado no xadrez, RAWR-risada nos raios)
REF = {
    1: dict(segura=((TE, MI, GO), VILA), close=(NH, PARQUE, 1), xadrez=("mon_xadrez_azul", (MI, ZU, NH)),
            raios=("mon_raios_roxo", (BI, GO, ZU, NH))),
    2: dict(segura=((ZU, BI, NH), PARQUE), close=(TE, VILA, 3), xadrez=("mon_xadrez_verde", (BI, MI, TE)),
            raios=("mon_raios_azul", (TE, GO, MI, ZU))),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        tn = min(ninguem_em(t0, versos, round(dd * 0.6, 2)), round(dd - 0.6, 2))
        if n == 3:                                         # meio refrão final: close do Bilu + a turma rindo nos raios
            if i == 0:
                out.append({"linhas": 2, "cenario": NOITE, "camera": cab(1300), "flash": True, "cantam": [BI],
                            "callout": [call(0.1, "COSQUINHA!", "rosa"), call(tn, "NINGUÉM!", "laranja")],
                            "objetos": {"pena": pena_cab(500, dd, cor=3)},
                            "atores": {BI: a(1300, ("cosquinha", max(0.2, tn - 0.3)), expr="determined")}})
            else:
                out.append({"linhas": 2, "cenario": "mon_raios_verde", "camera": GCAM, "fx": ["estrelas"], "cantam": [TE],
                            "callout": [call(0.1, "MONSTRINHO RI TAMBÉM!", "roxo")],
                            "atores": {c: g(x, ("cosquinha", 0.1 + 0.08 * k), turn=tv) for k, (c, x, tv) in
                                       enumerate(zip((TE, ZU, BI, NH), (210, 710, 1210, 1710), (0.25, 0.1, -0.1, -0.25)))}})
            continue
        cfg = REF[n]
        if i == 0:                                         # "Cosquinha, cosquinha! / Quem aguenta? Ninguém!" — seguram… e explodem
            (l_, m_, r_), cen = cfg["segura"]
            out.append({"linhas": 2, "cenario": cen, "camera": corpo(1300), "cantam": [m_],
                        "callout": [call(0.1, "COSQUINHA, COSQUINHA!", "rosa"), call(tn, "NINGUÉM!", "laranja")],
                        "atores": {l_: a(640, ("cosquinha", tn), turn=0.3, expr="determined"),
                                   m_: a(1300, ("cosquinha", tn + 0.05), expr="determined"),
                                   r_: a(1960, ("cosquinha", tn + 0.1), turn=-0.3, expr="determined")}})
        elif i == 1:                                       # "Monstrinho ri também!" — CABEÇA rindo com a pena
            q_, cen, cor = cfg["close"]
            out.append({"linhas": 2, "cenario": cen, "camera": cab(1300), "cantam": [q_],
                        "callout": [call(round(dd * 0.45, 2), "MONSTRINHO RI TAMBÉM!", "roxo")],
                        "objetos": {"pena": pena_cab(620, dd, cor=cor)},
                        "atores": {q_: a(1300, ("cosquinha", 0.3))}})
        elif i == 2:                                       # o rebolado latino no xadrez, e explodem no "ninguém"
            cen, quem = cfg["xadrez"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "cantam": [quem[1]],
                        "callout": [call(tn, "QUEM AGUENTA? NINGUÉM!", "laranja")],
                        "atores": {c: g(x, ("dance", 0.0, "cintura"), ("cosquinha", tn + 0.06 * k), turn=tv) for k, (c, x, tv) in
                                   enumerate(zip(quem, (380, 960, 1540), (0.2, 0.0, -0.2)))}})
        else:                                              # "Rá-rá-rá! Rawr! / Cosquinha de monstrinho!"
            cen, quem = cfg["raios"]
            tr = min(rawr_em(t0, versos, round(dd * 0.3, 2)), round(dd - 0.9, 2))
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["estrelas"], "flash": n == 1, "cantam": [quem[1]],
                        "callout": [call(0.1, "RÁ-RÁ-RÁ! RAWR!", "vermelho"), call(round(dd * 0.55, 2), "COSQUINHA DE MONSTRINHO!", "rosa")],
                        "atores": {c: g(x, ("cosquinha", 0.0, max(0.3, tr - 0.05)), ("rawr", tr + 0.05 * k, 0.9),
                                        ("cosquinha", round(tr + 1.0, 2)), turn=tv) for k, (c, x, tv) in
                                   enumerate(zip(quem, (210, 710, 1210, 1710), (0.25, 0.1, -0.1, -0.25)))}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 2}, {"seg": 4.6}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 2, "cenario": VILA, "camera": cab(1300), "cantam": [ZU], "callout": [call(0.2, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {ZU: a(1300, ("rawr", 0.2), ("apontar_camera", 2.6))}},
    {**banda(PALCO, max(0.6, d[1]), extra={NH: a(2300, ("dance", 0.0, "cintura"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": max(0.6, d[2]), "cenario": "mon_xadrez_laranja", "camera": GCAM, "fx": ["confete"], "titulo": "a turma rebola",
     "cantam": [MI],
     "atores": {MI: g(380, ("dance", 0.0, "cintura"), turn=0.2), TE: g(960, ("dance", 0.1, "gingado")),
                GO: g(1540, ("dance", 0.0, "cintura"), turn=-0.2)}},
]


# ───────── ponte: tenta em você… não dá! só com um amiguinho + comandos ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 7)
d = dur(T)
tb = R.tp(T[3][0], T[3][2], "balança", default=round(d[3] * 0.5, 2))
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.3, "TENTA EM VOCÊ!", "amarelo")], "cantam": [TE],
     "objetos": {"pena": pena(1450, 860, d[0], giro=-1.4, cor=2, depth=0.6, rapido=2.0)},
     "atores": {TE: a(1300, ("pensar", 0.4), expr="confused")}},
    {"linhas": 1, "cenario": PARQUE, "camera": cab(1300), "callout": [call(0.2, "NÃO DÁ! NÃO DÁ!", "vermelho")], "cantam": [TE],
     "atores": {TE: a(1300, ("look_around", 0.1), expr="confused")}},
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "callout": [call(0.3, "SÓ COM UM AMIGUINHO!", "verde")], "cantam": [GO],
     "objetos": {"pena": pena(1460, 860, d[2], giro=-1.3, cor=3, depth=0.75)},
     "atores": {TE: a(900, ("cosquinha", 0.6), turn=0.3), GO: a(1650, ("point", 0.1), ("laugh", 1.2), turn=-0.35)}},
    {"linhas": 1, "cenario": "mon_brilho_laranja", "camera": GCAM, "cantam": [MI],
     "callout": [call(0.1, "MEXE O PEZINHO!", "verde"), call(tb, "BALANÇA A BARRIGA!", "rosa")],
     "atores": {BI: g(380, ("dance", 0.0, "pezinho"), ("dance", tb, "cintura"), turn=0.2),
                MI: g(960, ("dance", 0.05, "pezinho"), ("dance", tb + 0.05, "cintura")),
                GO: g(1540, ("dance", 0.1, "pezinho"), ("dance", tb + 0.1, "cintura"), turn=-0.2)}},
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "callout": [call(0.1, "LEVANTA O BRACINHO!", "azul")], "cantam": [ZU],
     "atores": {ZU: a(640, ("dance", 0.0, "bracos"), turn=0.3), NH: a(1300, ("dance", 0.05, "bracos")),
                TE: a(1960, ("dance", 0.1, "bracos"), turn=-0.3)}},
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1300), "callout": [call(0.1, "CUTI-CUTI!", "rosa")], "cantam": [MI],
     "objetos": {"pena": pena_cab(640, d[5], cor=1, rapido=6.0)},
     "atores": {MI: a(1300, ("cosquinha", 0.1))}},
    {"linhas": 1, "cenario": "mon_raios_rosa", "camera": GCAM, "fx": ["estrelas"], "tremor": [0.4], "cantam": [BI],
     "callout": [call(0.1, "RÁ-RÁ-RÁ! RAWR!", "vermelho")],
     "atores": {TE: g(210, ("cosquinha", 0.0, 0.5), ("rawr", 0.5), turn=0.2), BI: g(710, ("cosquinha", 0.0, 0.55), ("rawr", 0.55)),
                ZU: g(1210, ("cosquinha", 0.0, 0.6), ("rawr", 0.6)), GO: g(1710, ("cosquinha", 0.0, 0.65), ("rawr", 0.65), turn=-0.2)}},
]


# ───────── 2º verso: o Zuzu de cara séria… e a MOSQUINHA ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
CHIFRE = (1300, 335)                                      # ponta do chifrinho do Zuzu em pé em x 1300 (medido no storyboard)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.3, "CARA SÉRIA!", "azul")], "cantam": [ZU],
     "atores": {ZU: a(1300, turn=0.1, expr="determined")}},
    {"linhas": 1, "cenario": PARQUE, "camera": cab(1300), "callout": [call(0.3, "COSQUINHA EM MIM? NÃO DÁ!", "vermelho")],
     "cantam": [ZU], "atores": {ZU: a(1300, expr="determined")}},       # sem gesto: o apontar_camera sorria
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "callout": [call(0.2, "PENA… E PINCEL!", "roxo")], "cantam": [TE],
     "objetos": {"pena": pena(900, 860, d[2], giro=0.6, cor=2, depth=0.5),           # cada uma de um lado, só encostando
                 "pincel": pena(1700, 860, d[2], giro=-0.6, cor=3, depth=0.5)},
     "atores": {TE: a(640, ("point", 0.2), turn=0.35), ZU: a(1300, turn=0.0, expr="determined"),
                GO: a(1960, ("point", 0.3), turn=-0.35)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.3, "NEM QUIS OLHAR!", "laranja")], "cantam": [ZU],
     "objetos": {"pena": pena(1060, 720, d[3], giro=-1.0, cor=2, depth=0.62)},
     "atores": {ZU: a(1300, turn=0.65, expr="determined")}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.3, "UMA MOSQUINHA!", "verde")], "cantam": [ZU],
     "objetos": {"mosca": obj("mosquinha", 500, 420, 0.7, d[4], z=5, fixo={"pousada": 0.0},
                              lin={"x": (500, CHIFRE[0]), "y": (420, CHIFRE[1]), "asa": (0.0, round(d[4] * 14, 1))})},
     "atores": {ZU: a(1300, turn=0.1, expr="determined")}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.3, "NA PONTA DO CHIFRINHO!", "roxo")], "cantam": [ZU],
     "objetos": {"mosca": obj("mosquinha", CHIFRE[0], CHIFRE[1], 0.7, d[5], z=5, fixo={"pousada": 1.0, "asa": 0.0})},
     "atores": {ZU: a(1300, ("cosquinha", round(d[5] * 0.7, 2)), turn=0.0, expr="surprised")}},
    {"linhas": 1, "cenario": "mon_brilho_azul", "camera": busto(1300), "fx": ["estrelas"], "callout": [call(0.2, "RÁ-RÁ-RÁ!", "amarelo")],
     "cantam": [ZU], "atores": {ZU: a(1300, ("cosquinha", 0.0))}},
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "callout": [call(0.3, "ROLOU DE RIR!", "laranja")], "cantam": [ZU],
     "atores": {TE: a(640, ("point", 0.1), ("laugh", 0.8), turn=0.3), ZU: a(1300, ("slip", 0.1), ("laugh", 0.9)),
                GO: a(1960, ("point", 0.15), ("laugh", 0.85), turn=-0.3)}},
]


# ───────── intervalo 2 (só instrumental, ~17 s) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 3, 2)
R.partes["intervalo#2"] = [
    {**banda(PALCO, d1, extra={GO: a(2300, ("dance", 0.0, "cintura"), turn=-0.3)}), "titulo": "a banda"},
    {"seg": d1, "cenario": "mon_xadrez_rosa", "camera": GCAM, "fx": ["confete"], "titulo": "a turma rebola", "cantam": [GO],
     "atores": {GO: g(380, ("dance", 0.0, "cintura"), turn=0.2), TE: g(960, ("dance", 0.1, "gingado")),
                ZU: g(1540, ("dance", 0.0, "cintura"), turn=-0.2)}},
    {"seg": round(D2 - 2 * d1, 2), "cenario": "mon_raios_azul", "camera": GCAM, "fx": ["estrelas"], "titulo": "pezinho", "cantam": [MI],
     "atores": {MI: g(210, ("dance", 0.0, "pezinho"), turn=0.2), NH: g(710, ("dance", 0.05, "pezinho")),
                ZU: g(1210, ("dance", 0.1, "pezinho")), GO: g(1710, ("dance", 0.15, "pezinho"), turn=-0.2)}},
]


# ───────── final: cosquinha no papai e na mamãe + convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 2}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}])
d = dur(T)
tm = R.tp(T[0][0], T[0][2], "mamãe!", "mamãe", default=round(d[0] * 0.55, 2))
R.partes["final#1"] = [
    {"linhas": 2, "cenario": VILA, "camera": cab(1300), "cantam": [BI],
     "callout": [call(0.2, "FAZ COSQUINHA NO PAPAI!", "azul"), call(tm, "E NA MAMÃE!", "rosa")],
     "atores": {BI: a(1300, ("apontar_camera", 0.1), ("cosquinha", round(tm + 0.4, 2)))}},
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
    {"linhas": 1, "seg": 3.4, "cenario": VILA, "camera": corpo(1300), "fx": ["coracoes"], "cantam": [BI],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.5, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn, y=y, depth=dp, z=zz) for k, (c, x, y, dp, zz, tn) in
                enumerate(((TE, 400, 880, 0.62, 2, 0.3), (GO, 1000, 880, 0.62, 2, 0.15), (MI, 1600, 880, 0.62, 2, -0.15),
                           (NH, 2200, 880, 0.62, 2, -0.3), (BI, 700, 975, 0.74, 3, 0.2), (ZU, 1900, 975, 0.74, 3, -0.2)))}},
    {"seg": round(dfim - 3.4, 2), "cenario": NOITE, "camera": busto(1300), "flash": True, "callout": [call(0.2, "RAWR!", "vermelho")],
     "titulo": "o último RAWR-risada", "cantam": [ZU],
     "objetos": {"mosca": obj("mosquinha", CHIFRE[0], CHIFRE[1], 0.7, round(dfim - 3.4, 2), z=5, fixo={"pousada": 1.0})},
     "atores": {ZU: a(1300, ("rawr", 0.1, 1.0), ("cosquinha", 1.15))}},
]


# ── vida no cenário (sem contorno): nuvens andando, lua com carinha, bolhas nos fundos ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    if cen in (PARQUE, VILA):
        x0 = (300, 1700, 900, 2100)[j % 4]
        ob.setdefault("nv", obj("nuvem", x0, 300, 0.32, dd, z=0, fixo={"cara": 1.0}, lin={"x": (x0, x0 + 280)}))
    elif cen == NOITE:
        ob.setdefault("lua", obj("lua", 2150, 420, 0.42, dd, z=0, pts={"boca": [(0.5, 0.6)], "brilho": [(0.0, 0.0), (1.0, 1.0)]}))
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

R.salvar("Roteiro do canal Fofolucos — 03 'Cosquinha de Monstrinho' (take '(1)' inteiro, 2:44, F3 + dembow, nota 4,9): "
         "o cantinho de cosquinha de cada um (pena), refrão-desafio 'quem aguenta? NINGUÉM!', o Teco não consegue fazer "
         "cosquinha nele mesmo, e o Zuzu de cara séria que não resiste à MOSQUINHA no chifrinho. "
         "Gerado por scripts/roteiros/fo03_cosquinha_de_monstrinho.py.")
