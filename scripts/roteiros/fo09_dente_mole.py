"""Roteiro verso a verso do canal FOFOLUCOS — 09 "Dente Mole de Monstrinho!" (take inteiro, 2:24, 136 BPM, Dó maior, estilo
F5, nota 4,9; letra 5 a 8 anos) → canais/fofolucos/musicas/09_dente_mole/roteiro.json.

O NHOQUE (o comilão) está com um DENTE MOLE e não consegue morder o pãozinho. Cenário novo `mon_jantar` (sala de jantar
da Vila de dia; parede creme — o Nhoque coral sumia na cozinha salmão), a MESA com toalha amarela (`mesa` tom 1) e
props novos: `dente` (o dentão de leite com carinha, que balança pra lá e pra cá e cai) e `maca` (a maçã do lanche:
mordida, e o dentinho grudado). Refrão = todo mundo balança junto, "será que vai cair já?" (tela dividida: o Nhoque × o
dente). Ponte = comandos de cuidado (abre a boca no espelho, mostra o dente, balança com a língua, devagar; escova bem,
sorriso brilhante, nada de puxar com força). 2º verso = a VIRADA: no lanche do parque, a maçã — NHAC! — o dente some,
procuram pela casa… e ele estava grudadinho na maçã.
Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — CABEÇA / BUSTO / CORPO, chifres/antenas no quadro, closes do Zuzu em BUSTO,
nunca monstrinho na frente da própria cor (Nhoque fora da cozinha salmão), nunca "monstro".
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo09_dente_mole.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("fofolucos/ep09-dente-mole", "09_dente_mole", "nhoque")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
SALA, VILA, PARQUE, ESCOLA, QUARTO = "mon_jantar", "mon_vila", "mon_parque", "mon_escola", "mon_quarto"
PALCO, CEU, CAMPO, COZ = "mon_palco", "mon_abertura", "mon_campinho", "mon_cozinha"
CHAO = 935
E = 1.45                                    # escala_personagens do canal (objetos também crescem)
MESA_TOPO = CHAO - 240 * 0.8 * E            # tampo da mesa (mesa depth 0.8)


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


def anda(at, x1, d, como="sneak", t0=0.0):
    at["acoes"] = [{"t": t0, "do": como, "to_x": float(x1), "dur": round(max(0.6, d) - t0 - 0.1, 2)}]
    return at


def mesa(x=1300):
    return {"mesa": {"id": "mesa", "x": x, "y": CHAO, "z": 3, "depth": 0.8, "keys": [{"t": 0.0, "pose": {"tom": 1.0}, "ease": "step"}]}}


def dente(d, x=960, y=900, depth=1.0, forca=1.0, sorri=0.0, cai=None, brilho=0.0, key="dt", z=3, ritmo=0.9):
    """o dentão balançando pra lá e pra cá (`ritmo` = balanços por segundo); `cai` = instante em que cai."""
    p = {"cai": [(round(cai, 2), 1.0)]} if cai is not None else None
    return {key: obj("dente", x, y, depth, d, z=z, fixo={"forca": forca, "sorri": sorri, "brilho": brilho, "cai": 0.0},
                     lin={"balanca": (0.0, round(max(0.6, d) * ritmo, 2))}, pts=p)}


def maca(d, x, y, depth=0.6, mordida=0.0, dente_=0.0, pts=None, key="mc", z=4, brilho=0.0):
    return {key: obj("maca", x, y, depth, d, z=z, fixo={"mordida": mordida, "dente": dente_, "brilho": brilho},
                     lin={"rola": (0.0, round(max(0.6, d) * 0.5, 2))}, pts=pts)}


def banda(cen, d, extra=None):
    p = R.banda(cen, d, teclado=True, sax=ZU, bateria=BI, cam={"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["cantam"] = [ZU]
    return p


def em(t0, versos, *alvos, default=0.4):
    return R.tp(t0, versos, *alvos, default=default)


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
tr = em(T[1][0], T[1][2], "rawr", default=round(d[1] * 0.6, 2))
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": busto(1150), "titulo": "o dente mole do Nhoque", "cantam": [NH],
     "callout": [call(0.3, "DENTE MOLE DE MONSTRINHO!", "vermelho")],
     "objetos": {**mesa(1300), **dente(d[0], x=1650, y=760, depth=0.5, z=5, ritmo=1.1)},
     "atores": {NH: a(1000, ("estatua", 0.0), turn=0.35, expr="surprised")}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1550), "cantam": [NH],
     "callout": [call(0.2, "BALANÇA, BALANÇA…", "amarelo"), call(round(tr, 2), "RAWR!", "vermelho")],
     "objetos": dente(d[1], x=1850, y=880, depth=0.6, sorri=1.0, ritmo=1.2, z=5),
     "atores": {NH: a(1350, ("dance", 0.0, "cabeca"), ("rawr", round(tr, 2)), turn=0.35)}},
    {"linhas": 1, "cenario": "mon_raios_laranja", "camera": GCAM, "flash": True, "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.1, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {TE: g(210, ("rawr", 0.3), turn=0.2), GO: g(710, ("rawr", 0.38)), BI: g(1210, ("rawr", 0.46)),
                MI: g(1710, ("rawr", 0.54), turn=-0.2)}},
    {**banda(PALCO, max(0.6, d[3]), extra={NH: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: o pãozinho, o "ai!" e a turma que vem ajudar ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
tai = em(T[3][0], T[3][2], "ai", default=0.3)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [NH], "callout": [call(0.3, "NA MESA DA VILA…", "roxo")],
     "objetos": mesa(1300),
     "atores": {NH: anda(a(450, turn=0.4, expr="joy"), 900, d[0], como="walk"), MI: a(1950, ("wave", 0.3), turn=-0.35)}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1150), "cantam": [NH], "callout": [call(0.2, "O NHOQUE FOI COMER!", "laranja")],
     "objetos": mesa(1450), "atores": {NH: a(1000, ("estatua", 0.0), turn=0.35, expr="joy", segura="pao_queijo")}},
    {"linhas": 1, "cenario": SALA, "camera": cab(1150), "cantam": [NH], "callout": [call(0.2, "MORDEU O PÃOZINHO…", "amarelo")],
     "atores": {NH: a(1150, ("eat", 0.2), turn=0.2, segura="pao_queijo_mordido")}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1150), "cantam": [NH], "tremor": [round(tai, 2)],
     "callout": [call(round(tai, 2), "AI!", "vermelho")], "objetos": mesa(1450),
     "atores": {NH: a(1000, ("take", round(max(0.05, tai - 0.1), 2)), turn=0.35, expr="shock")}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300, 600), "cantam": [NH], "fx": ["estrelas"],
     "callout": [call(0.2, "MEU DENTE TÁ MOLINHO!", "rosa")],
     "objetos": dente(d[4], x=1300, y=900, depth=0.75, sorri=0.0, ritmo=1.3, z=5)},
    {"linhas": 1, "cenario": SALA, "camera": cab(1150), "cantam": [NH], "callout": [call(0.2, "PRA LÁ E PRA CÁ!", "azul")],
     "atores": {NH: a(1150, ("dance", 0.0, "cabeca"), turn=0.1, expr="surprised")}},
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300, 1500), "cantam": [NH], "fx": ["estrelas"],
     "callout": [call(0.2, "A TURMA TODA VEIO!", "verde")],
     "atores": {BI: anda(a(500, turn=0.4, expr="surprised"), 1300, d[6], como="run"),
                MI: anda(a(150, turn=0.4, expr="surprised"), 900, d[6], como="run", t0=0.15)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [NH], "fx": ["confete"],
     "callout": [call(0.2, "PRA AJUDAR A BALANÇAR!", "laranja")],
     "atores": {BI: a(650, ("dance", 0.0, "cabeca"), turn=0.3), NH: a(1300, ("dance", 0.1, "cabeca"), expr="joy"),
                MI: a(1950, ("dance", 0.05, "cabeca"), turn=-0.3)}},
]


# ───────── refrão: dente mole de monstrinho! balança pra lá e pra cá! rawr! será que vai cair já? ─────────
REF = {
    1: dict(dentista=(BI, SALA), trio=("mon_raios_rosa", (TE, BI, GO)), close=(MI, PARQUE)),
    2: dict(dentista=(TE, SALA), trio=("mon_xadrez_azul", (NH, MI, ZU)), close=(ZU, CAMPO)),
    3: dict(dentista=(GO, SALA), trio=("mon_raios_verde", (BI, NH, MI)), close=(TE, ESCOLA)),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        tr = em(t0, versos, "rawr", default=round(dd * 0.5, 2))
        tb = em(t0, versos, "balança", default=round(dd * 0.5, 2))
        if i % 4 == 0:                                     # o dentão balançando grandão + o Nhoque balançando junto
            out.append({"linhas": 2, "cenario": (SALA, QUARTO, SALA)[n - 1], "camera": corpo(1300),
                        "cantam": [NH], "fx": ["estrelas"],
                        "callout": [call(0.1, "DENTE MOLE DE MONSTRINHO!", "vermelho"), call(round(tb, 2), "PRA LÁ E PRA CÁ!", "azul")],
                        "objetos": dente(dd, x=1650, y=900, depth=0.75, sorri=1.0, ritmo=1.15, z=5),
                        "atores": {NH: a(900, ("dance", 0.0, "cabeca"), turn=0.35), (MI, BI, ZU)[n - 1]: a(2200, ("dance", 0.1, "cabeca"), turn=-0.35)}})
        elif i % 4 == 1:                                   # "Rawr! Será que vai cair já?" — o amigo × o dente (tela dividida)
            q, cen = cfg["dentista"]
            out.append(R.dividida(
                {"cenario": cen, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58}, "cantam": [q],
                 "atores": {q: a(1300, ("pensar", 0.0), ("rawr", round(tr, 2)), turn=0.3, expr="surprised")}},
                {"cenario": "mon_brilho_azul", "camera": GCAM,
                 "objetos": dente(dd, x=960, y=1000, depth=1.2, sorri=0.0, forca=1.0, ritmo=1.6, key="dt2")},
                linhas=2, layout="diagonal",
                callout=[call(0.1, "DENTE MOLE DE MONSTRINHO!", "vermelho"), call(round(tr, 2), "SERÁ QUE VAI CAIR JÁ?", "roxo")]))
        elif i % 4 == 2:                                   # a dança do dente mole no fundo colorido
            cen, trio = cfg["trio"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "flash": n == 1, "fx": ["estrelas"], "cantam": [trio[1]],
                        "callout": [call(0.1, "DENTE MOLE DE MONSTRINHO!", "vermelho")],
                        "atores": {c: g(x, ("dance", 0.05 * j, st), turn=tv_) for j, (c, x, tv_, st) in
                                   enumerate(zip(trio, (380, 960, 1540), (0.2, 0.0, -0.2), ("festa", "cabeca", "chute")))}})
        else:                                              # RAWR de pertinho num cenário de verdade (Zuzu em BUSTO)
            q, cen = cfg["close"]
            out.append({"linhas": 2, "cenario": cen, "camera": busto(1300), "cantam": [q], "fx": ["estrelas"],
                        "callout": [call(round(tr, 2), "SERÁ QUE VAI CAIR JÁ?", "roxo")],
                        "atores": {q: a(1300, ("dance", 0.0, "cabeca"), ("rawr", round(tr, 2)))}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 1}, {"linhas": 1}, {"seg": 4.0}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [ZU], "callout": [call(0.2, "FOFOLUCOS! RAWR!", "laranja")],
     "objetos": mesa(1300),
     "atores": {ZU: a(600, ("cheguei", 0.0), ("rawr", 1.0), turn=0.3), NH: a(2000, ("rawr", 0.4), turn=-0.3)}},
    R.dividida({"cenario": "mon_brilho_laranja", "camera": GCAM, "cantam": [TE], "atores": {TE: g(960, ("rawr", 0.1)) | {"depth": 1.3}}},
               {"cenario": "mon_raios_azul", "camera": GCAM, "atores": {GO: g(960, ("rawr", 0.25)) | {"depth": 1.3}}},
               linhas=1, layout="diagonal", callout=[call(0.1, "FOFOLUCOS!", "roxo")]),
    {**banda(PALCO, max(0.6, d[2]), extra={NH: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": max(0.6, d[3]), "cenario": SALA, "camera": corpo(1300), "fx": ["confete"], "titulo": "a turma dança na sala", "cantam": [MI],
     "objetos": mesa(1300),
     "atores": {TE: a(650, ("dance", 0.0, "festa"), turn=0.3), MI: a(1950, ("dance", 0.05, "chute"), turn=-0.3)}},
]


# ───────── ponte: os comandos de cuidado com o dente ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4 + [{"linhas": 2}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}])
d = dur(T)
tp_ = em(T[6][0], T[6][2], "puxar", default=round(d[6] * 0.4, 2))
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "cantam": [NH], "callout": [call(0.1, "ABRE A BOCA BEM GRANDONA!", "laranja")],
     "objetos": {"esp": obj("espelho_reflexo", 1650, 935, 0.75, d[0], z=2,
                            fixo={"quem": 5.0, "vira": -0.45, "rawr": 0.0, "susto": 0.0, "brilho": 0.0}, pts={"rawr": [(0.4, 1.0)]})},
     "atores": {NH: a(1000, ("rawr", 0.3), turn=0.4)}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300, 600), "cantam": [NH], "fx": ["estrelas"],
     "callout": [call(0.1, "MOSTRA O DENTE DA FRENTE!", "azul")],
     "objetos": dente(d[1], x=1300, y=900, depth=0.75, sorri=1.0, brilho=1.0, ritmo=0.8, z=5)},
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1300), "cantam": [NH], "callout": [call(0.1, "BALANÇA COM A LÍNGUA…", "roxo")],
     "atores": {NH: a(1300, ("dance", 0.0, "cabeca"), expr="sly")}},
    R.dividida({"cenario": SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58}, "cantam": [MI],
                "atores": {MI: a(1300, ("fofinho", 0.1), turn=0.3)}},
               {"cenario": VILA, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58},
                "atores": {TE: a(1300, ("estatua", 0.0), turn=-0.3, expr="sly")}},
               linhas=1, layout="vertical", callout=[call(0.1, "DEVAGAR, BEM PACIENTE!", "verde")]),
    {"linhas": 2, "cenario": QUARTO, "camera": busto(1300), "cantam": [GO],
     "callout": [call(0.1, "E MAIS!", "verde"), call(round(d[4] * 0.35, 2), "ESCOVA BEM OS DENTES!", "azul")],
     "objetos": {"esp": obj("espelho_reflexo", 1700, 935, 0.7, d[4], z=2, fixo={"quem": 2.0, "vira": -0.45, "brilho": 0.0},
                            pts={"brilho": [(round(d[4] * 0.8, 2), 1.0)]})},
     "atores": {GO: a(1050, ("escovar_dentes", 0.3), turn=0.4, segura="escova")}},
    {"linhas": 1, "cenario": "mon_raios_roxo", "camera": GCAM, "cantam": [ZU], "fx": ["estrelas"],
     "callout": [call(0.1, "FAZ UM SORRISO BRILHANTE!", "amarelo")],
     "atores": {ZU: g(960, ("sorriso", 0.1)) | {"depth": 1.1}}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "cantam": [BI], "callout": [call(round(tp_, 2), "NADA DE PUXAR COM FORÇA!", "vermelho")],
     "atores": {BI: a(950, ("puxar", 0.1), ("shake_fist", round(tp_ + 0.3, 2)), turn=0.35), NH: a(1650, ("take", 0.4), turn=-0.35, expr="shock")}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [NH], "fx": ["estrelas"],
     "callout": [call(0.1, "QUE ELE CAI NUM INSTANTE!", "rosa")],
     "objetos": {**mesa(1300), **dente(d[7], x=1300, y=640, depth=0.55, sorri=1.0, ritmo=2.2, z=5)},
     "atores": {NH: a(600, ("dance", 0.0, "cabeca"), turn=0.35), MI: a(2000, ("fofinho", 0.2), turn=-0.35)}},
]


# ───────── 2º verso: a VIRADA — o lanche, a maçã… NHAC! ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
tn = em(T[3][0], T[3][2], "nhac", default=0.2)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "cantam": [NH], "fx": ["estrelas"],
     "callout": [call(0.2, "NO LANCHE DA TARDE…", "laranja")],
     "objetos": {"cesta": obj("cesta", 1300, CHAO + 40, 0.7, d[0], z=4)},
     "atores": {NH: a(800, ("dance", 0.0, "festa"), turn=0.35), TE: a(1850, ("wave", 0.2), turn=-0.35)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300, 640), "cantam": [NH], "fx": ["estrelas"],
     "callout": [call(0.2, "UMA MAÇÃ APARECEU!", "vermelho")],
     "objetos": {**maca(d[1], 1300, 960, depth=0.9, brilho=1.0), "cesta": obj("cesta", 1300, CHAO + 60, 0.7, d[1], z=3)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "cantam": [NH], "callout": [call(0.2, "O NHOQUE DEU MORDIDA…", "laranja")],
     "objetos": maca(d[2], 1500, 830, depth=0.55, z=5),
     "atores": {NH: a(1100, ("eat", 0.3), turn=0.4, expr="joy")}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "cantam": [NH], "flash": True, "tremor": [round(tn, 2)],
     "callout": [call(round(tn, 2), "NHAC!", "vermelho"), call(round(tn + 0.6, 2), "E O DENTE SE PERDEU!", "roxo")],
     "objetos": maca(d[3], 1820, 830, depth=0.55, z=5, pts={"mordida": [(round(tn, 2), 1.0)]}),
     "atores": {NH: a(1420, ("take", round(tn + 0.2, 2)), turn=0.4, expr="shock")}},
    {"linhas": 1, "cenario": COZ, "camera": corpo(1300), "cantam": [NH], "callout": [call(0.2, "PROCURARAM PELA CASA…", "azul")],
     "atores": {BI: a(700, ("look_around", 0.0), turn=0.3), GO: a(1900, ("look_around", 0.1), turn=-0.3)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [NH], "callout": [call(0.2, "DEBAIXO DA MESA E DO CHÃO!", "verde")],
     "objetos": mesa(1500),
     "atores": {MI: a(700, ("sit", 0.1), turn=0.4, expr="surprised", z=6, y=CHAO + 40), TE: a(2150, ("look_around", 0.0), turn=-0.35)}},
    {"linhas": 1, "cenario": PARQUE, "camera": {"x": 1300, "y": 700, "zoom": 1.9, "zoom_fim": 2.05}, "cantam": [NH], "fx": ["estrelas"],
     "callout": [call(0.2, "E O DENTE TAVA LÁ…", "amarelo")],
     "objetos": maca(d[6], 1300, 930, depth=0.8, mordida=1.0, dente_=0.0, pts={"dente": [(0.5, 1.0)], "brilho": [(0.6, 1.0)]})},
    R.dividida({"cenario": PARQUE, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58}, "cantam": [NH],
                "atores": {NH: a(1300, ("laugh", 0.1), expr="joy")}},
               {"cenario": PARQUE, "camera": {"x": 1300, "y": 640, "zoom": 1.7, "zoom_fim": 1.8},
                "objetos": maca(d[7], 1300, 860, depth=0.9, mordida=1.0, dente_=1.0, brilho=1.0, key="mc2"),
                "atores": {MI: a(1650, ("point", 0.2), turn=-0.4, expr="joy")}},
               linhas=1, layout="diagonal", callout=[call(0.2, "GRUDADINHO NA MAÇÃ!", "vermelho")]),
]


# ───────── intervalo 2 (só instrumental): a festa do dente ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 2, 2)
R.partes["intervalo#2"] = [
    {**banda(PALCO, d1, extra={NH: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": round(D2 - d1, 2), "cenario": PARQUE, "camera": corpo(1300), "fx": ["confete"], "titulo": "a festa da janelinha",
     "cantam": [NH],
     "objetos": maca(D2 - d1, 1300, CHAO + 30, depth=0.55, mordida=1.0, dente_=1.0, z=2),
     "atores": {BI: a(600, ("dance", 0.0, "festa"), turn=0.3), NH: a(1300, ("dance", 0.1, "chute"), expr="joy", z=4, y=CHAO + 60),
                GO: a(2000, ("dance", 0.05, "festa"), turn=-0.3)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4 + [{"seg": 0.0}])
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "cantam": [NH], "callout": [call(0.2, "E VOCÊ? TEM DENTE MOLE?", "roxo")],
     "atores": {NH: a(1300, ("apontar_camera", 0.1), expr="joy")}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"], "cantam": [ZU],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {ZU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": VILA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")], "cantam": [BI],
     "atores": {BI: a(850, ("point", 0.1), turn=0.3), MI: a(1750, ("wave", 0.2), turn=-0.25)}},
    {"linhas": 1, "cenario": "mon_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "cantam": [GO],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {GO: g(560, ("point", 0.2), ("rawr", max(0.6, round(d[3] - 1.4, 2))), turn=0.2) | {"depth": 1.0}}},
    {"seg": max(0.6, d[4]), "cenario": CAMPO, "camera": corpo(1300), "fx": ["estrelas"], "titulo": "a turma sorri com a janelinha",
     "cantam": [NH], "atores": {TE: a(650, ("sorriso", 0.1), turn=0.3), NH: a(1950, ("sorriso", 0.2), turn=-0.3)}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.0, "cenario": CEU, "camera": corpo(1300), "fx": ["estrelas"], "cantam": [NH],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.4, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn_, y=y, depth=dp, z=zz) for k, (c, x, y, dp, zz, tn_) in
                enumerate(((TE, 400, 880, 0.62, 2, 0.3), (GO, 1000, 880, 0.62, 2, 0.15), (MI, 1600, 880, 0.62, 2, -0.15),
                           (ZU, 2200, 880, 0.62, 2, -0.3), (BI, 700, 975, 0.74, 3, 0.2), (NH, 1900, 975, 0.74, 3, -0.2)))}},
    {"seg": round(dfim - 3.0, 2), "cenario": SALA, "camera": cab(1300), "flash": True, "fx": ["estrelas"],
     "callout": [call(0.2, "RAWR!", "vermelho")], "titulo": "o RAWR banguela do Nhoque", "cantam": [NH],
     "atores": {NH: a(1300, ("rawr", 0.1), expr="joy")}},
]


# ── vida no cenário: nuvens no céu, bolhas nos fundos gráficos ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    if cen == SALA and "mesa" not in ob and not sb.get("tela_dividida"):        # a mesa da sala sempre ao fundo
        ob.update({"mesa": {**mesa(2150)["mesa"], "depth": 0.6, "z": 1}})
    if cen == QUARTO:                                                             # bolhas de sabão (a escovação)
        ob.setdefault("bo", obj("bolha", (400, 2100, 700)[j % 3], 900, 0.3, dd, z=1, fixo={"tam": 1.0},
                                lin={"y": (900, 300), "balanco": (0.0, round(dd, 1))}))
    if cen == COZ:                                                                # maçã no balcão da cozinha
        ob.setdefault("mf", obj("maca", 1500, 590, 0.32, dd, z=1, lin={"rola": (0.0, round(dd * 0.8, 2))}))
    if cen == SALA and "mesa" in ob and "mf" not in ob and "mc" not in ob:      # a fruteira: uma maçã balançando na mesa
        k_ = ob["mesa"]["depth"] / 0.8
        atores_x = [float(at.get("x", 0)) for at in (sb.get("atores") or {}).values()]
        lado = 1 if not atores_x or sum(atores_x) / len(atores_x) < ob["mesa"]["x"] else -1   # ponta da mesa LONGE dos atores
        mx = ob["mesa"]["x"] + lado * 230 * k_
        ob["mf"] = obj("maca", mx, CHAO - 240 * ob["mesa"]["depth"] * E + 4, 0.32 * k_, dd, z=ob["mesa"].get("z", 3) + 1,
                       lin={"rola": (0.0, round(dd * 0.8, 2))})
    if cen in (VILA, CEU, PARQUE, CAMPO):
        x0 = (300, 1700, 900, 2100)[j % 4]
        ob.setdefault("nv", obj("nuvem", x0, 260, 0.32, dd, z=0, fixo={"cara": 1.0}, lin={"x": (x0, x0 + 280)}))
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

R.salvar("Roteiro do canal Fofolucos — 09 'Dente Mole de Monstrinho!' (take inteiro, 2:24, F5, nota 4,9): o Nhoque com o dente "
         "mole (prop `dente`) na sala de jantar (mon_jantar, mesa amarela); a turma balança junto no refrão; ponte de cuidados "
         "(espelho, escova, sorriso, nada de puxar); a virada: no lanche do parque a maçã (prop `maca`) — NHAC — e o dente "
         "grudadinho nela. Gerado por scripts/roteiros/fo09_dente_mole.py.")
