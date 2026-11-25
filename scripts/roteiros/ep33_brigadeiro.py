"""Roteiro verso a verso de 33 "Brigadeiro" (take 'Brigadeiro.wav', 2:22, 136 BPM, Sol maior, estilo E18 = receita do
Fofolucos, nota 5; letra 5 a 8 anos) → canais/laurinha/musicas/33_brigadeiro/roteiro.json.

A FESTA DE ANIVERSÁRIO DA VOVÓ na sala (balões, mesa com a BANDEJA de brigadeiro — prop novo `bandeja_brigadeiro`, que
brilha "como se viesse do céu" e depois aparece VAZIA). Refrão = a Laurinha DETETIVE com a LUPA (item novo `lupa`)
interroga os suspeitos em tela dividida: o vovô Ciço (bravo), a mamãe, o gato — e quem assiste ("Foi você?").
Ponte = comandos de detetive: lupa, chão, embaixo da mesa, PEGADAS DE CHOCOLATE (prop novo `pegadas`), segue a pegada
na ponta do pé até o quarto… "Achei!". 2º verso = a VIRADA: o Luisinho, de boca suja de chocolate (canal novo
`chocolate`), confessa… e abre a mão: guardou o ÚLTIMO BRIGADEIRO (item novo `brigadeiro`) pra Laurinha.
Placar de cena (24/11): as Laurinha 29–32 ficaram em 6/10 → a 33 volta a 10/10 (cenários, ações, telas divididas).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep33_brigadeiro.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, LA, LU, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("laurinha/ep33-brigadeiro", "33_brigadeiro", "laurinha")
SALA, COZ, JARDIM, QUARTO, CASA = "plano_sala", "plano_cozinha", "plano_jardim", "plano_quarto_azul", "plano_casa_frente"
VO, VC, MA = "vovo", "vovo_cico", "mamae"
CHAO = 930
E = 1.7                                       # escala_personagens: 24/11 o usuário achou a turma pequena na tela → 1,45 → 1,7
MESA_TOPO = CHAO - 240 * 0.9 * E              # tampo da mesa (mesa depth 0.9)


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


def detetive(x, *acoes, turn=0.0, **kw):
    """a Laurinha detetive: sempre com a LUPA na mão."""
    return a(x, *acoes, turn=turn, segura="lupa", **kw)


def sujo(at, t=None):
    """boca suja de chocolate (o Luisinho comeu!); `t` = a partir de quando (senão desde o começo)."""
    ks = [{"t": 0.0, "pose": {"chocolate": 0.0 if t else 1.0}, "ease": "step"}]
    if t:
        ks.append({"t": round(t, 2), "pose": {"chocolate": 1.0}, "ease": "step"})
    at["keys"] = at.get("keys", []) + ks
    return at


def anda(at, x1, d, como="sneak", t0=0.0):
    at["acoes"] = [{"t": t0, "do": como, "to_x": float(x1), "dur": round(max(0.6, d) - t0 - 0.1, 2)}]
    return at


def mesa(x=1300):
    return {"mesa": {"id": "mesa", "x": x, "y": CHAO, "z": 3, "depth": 0.9}}


def bandeja(d, x=1100, quantos=12, lin=None, pts=None, brilho=0.0, key="bdj"):
    return {key: obj("bandeja_brigadeiro", x, MESA_TOPO - 28, 0.55, d, z=4, fixo={"quantos": float(quantos), "brilho": brilho},
                     lin=lin, pts=pts)}


def bolo(d, x=1520, vela=1.0):
    return {"bolo": obj("bolo_aniversario", x, MESA_TOPO - 6, 0.42, d, z=4, fixo={"vela": vela})}


def baloes(d, xs=((420, 0), (2200, 2))):
    return {f"bal{j}": obj("balao", x, 640, 0.55, d, z=1, fixo={"cor": float(c)}, lin={"balanco": (0.0, round(d * 0.6, 1))})
            for j, (x, c) in enumerate(xs)}


def pegadas(d, x=1300, y=1000, n=(7, 7), depth=0.7, brilho=0.0, lado=1.0):
    return {"peg": obj("pegadas", x, y, depth, d, z=2, fixo={"brilho": brilho, "lado": lado}, lin={"n": n})}


def banda(d, extra=None):
    """a banda toca NA FESTA da vovó (sala): Laurinha no teclado, Luisinho na bateria, a vovó dança à direita."""
    p = R.banda(SALA, d, teclado=True, sax=LA, bateria=LU, cam={"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04},
                extra=extra or {VO: fundo(a(2400, ("dance", 0.0, "balanco"), turn=-0.3, expr="joy"))})
    p["cantam"] = [LA]
    return p


def em(t0, versos, *alvos, default=0.4):
    return R.tp(t0, versos, *alvos, default=default)


def BU(x=1300, y=580):
    """BUSTO da Laurinha com a escala 1,7: um pouco mais aberto que o padrão (1,55) para a dupla não se sobrepor."""
    return {"x": x, "y": y, "zoom": 1.32, "zoom_fim": 1.38}


def fundo(at, depth=0.85):
    """grupo de 3 no CORPO: um passo para trás (com a escala 1,7 três personagens não cabem lado a lado)."""
    return at | {"depth": depth}


CAM_BANDEJA = {"x": 1100, "y": 560, "zoom": 2.0, "zoom_fim": 2.15}


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": COZ, "camera": corpo(1300), "titulo": "a vovó faz brigadeiro", "callout": [call(2.8, "BRIGADEIRO!", "laranja")],
     "objetos": {**mesa(), **bandeja(d[0], x=1300, brilho=0.0, pts={"brilho": [(2.8, 1.0)]})},
     "atores": {VO: a(800, ("point", 2.8), turn=0.3, expr="joy"), LU: a(1950, ("look_around", 0.5), turn=-0.3, expr="sly")}},
    {"linhas": 1, "cenario": COZ, "camera": BU(1550), "callout": [call(0.2, "ZUM, ZUM!", "amarelo")],
     "objetos": {**mesa(), **bandeja(d[1], x=1300, brilho=1.0)},
     "atores": {LU: a(1850, ("estatua", 0.0), turn=-0.35, expr="sly")}},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "camera": GCAM, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "LAURINHA E LUISINHO!", "roxo")],
     "atores": {LA: g(640, ("wave", 0.1), turn=0.25) | {"depth": 1.05}, LU: g(1280, ("wave", 0.2), turn=-0.25) | {"depth": 1.05}}},
    {**banda(max(0.6, d[3])), "titulo": "a banda na festa da vovó"},
]


# ───────── 1º verso: a festa… e a bandeja vazia ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "fx": ["confete"], "callout": [call(0.2, "ANIVERSÁRIO DA VOVÓ!", "rosa")],
     "objetos": baloes(d[0]),
     "atores": {LA: fundo(a(620, ("wave", 0.2), turn=0.3)), VO: fundo(a(1300, ("cheguei", 0.1), expr="joy")),
                LU: fundo(a(1980, ("wave", 0.3), turn=-0.3))}},
    {"linhas": 1, "cenario": SALA, "camera": BU(1300), "callout": [call(0.2, "TEM BALÃO E TEM CHAPÉU!", "azul")],
     "objetos": {"bal0": obj("balao", 700, 640, 0.6, d[1], z=1, fixo={"cor": 1.0}, lin={"balanco": (0.0, 1.5)}),
                 "bal1": obj("balao", 1900, 640, 0.6, d[1], z=1, fixo={"cor": 3.0}, lin={"balanco": (0.3, 1.8)})},
     "atores": {LA: a(880, ("dance", 0.0, "pulinho"), turn=0.3), LU: a(1720, ("dance", 0.1, "pulinho"), turn=-0.3)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.2, "TEM BANDEJA DE DOCINHO…", "laranja")],
     "objetos": {**mesa(), **bandeja(d[2]), **bolo(d[2])},
     "atores": {VC: a(2200, ("point", 0.2), turn=-0.35, expr="joy"), LA: a(380, ("pensar", 0.3), turn=0.35)}},
    {"linhas": 1, "cenario": SALA, "camera": CAM_BANDEJA, "fx": ["estrelas"], "callout": [call(0.2, "QUE PARECE VIR DO CÉU!", "amarelo")],
     "objetos": {**mesa(), **bandeja(d[3], brilho=0.0, pts={"brilho": [(0.2, 1.0)]})}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "fx": ["confete"], "callout": [call(0.2, "HORA DO PARABÉNS!", "rosa")],
     "objetos": {**mesa(), **bolo(d[4], x=1300), **baloes(d[4])},
     "atores": {LA: fundo(a(560, ("dance", 0.0, "palmas"), turn=0.3)), VO: fundo(a(1300, ("dance", 0.1, "palmas"), expr="joy"), 0.8),
                MA: fundo(a(2040, ("dance", 0.05, "palmas"), turn=-0.3))}},
    {"linhas": 1, "cenario": SALA, "camera": BU(1300), "tremor": [0.4], "callout": [call(0.2, "OLHA SÓ QUE DESESPERO!", "vermelho")],
     "atores": {LA: a(880, ("take", 0.2), turn=0.3, expr="surprised"), VO: a(1720, ("shock_reaction", 0.3), turn=-0.3, expr="shock")}},
    {"linhas": 1, "cenario": SALA, "camera": CAM_BANDEJA, "callout": [call(0.2, "A BANDEJA TÁ VAZIA…", "roxo")],
     "objetos": {**mesa(), **bandeja(d[6], quantos=0, pts={"treme": [(0.3, 2.0)]})}},
    R.dividida({"cenario": SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58},
                "atores": {VO: a(1300, ("shock_reaction", 0.1), expr="shock")}},
               {"cenario": SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58},
                "atores": {VC: a(1300, ("take", 0.15), expr="surprised")}},
               linhas=1, layout="diagonal", callout=[call(0.1, "SUMIU O BRIGADEIRO!", "vermelho")]),
]


# ───────── refrão: brigadeiro, brigadeiro! quem comeu? foi você? fala primeiro! ─────────
REF = {
    1: dict(cen=SALA, suspeito=(VC, SALA, dict(expr="angry")), danca=("danca_xadrez_vermelho", (LA, VO, LU), ("roda", "balanco", "roda"))),
    2: dict(cen=COZ, suspeito=(MA, COZ, dict(expr="confused")), danca=("danca_bolinhas_laranja", (LU, MA, LA), ("cintura", "palmas", "cintura"))),
    3: dict(cen=JARDIM, suspeito=("gato", JARDIM, None), danca=("danca_raios_azul", (LA, VC, LU), ("pulinho", "balanco", "pulinho"))),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        tq = em(t0, versos, "quem", "foi", default=round(dd * 0.5, 2))
        if i % 4 == 0:                                     # a detetive procura com a lupa
            ob = {**mesa(), **bandeja(dd, quantos=0)} if cfg["cen"] != JARDIM else pegadas(dd, n=(3, 7), depth=0.6)
            out.append({"linhas": 2, "cenario": cfg["cen"], "camera": corpo(1300), "cantam": [LA],
                        "callout": [call(0.1, "BRIGADEIRO, BRIGADEIRO!", "laranja"), call(round(tq, 2), "QUEM COMEU?", "roxo")],
                        "objetos": ob,
                        "atores": {LA: anda(detetive(450, turn=0.4, expr="determined", z=6, y=CHAO + 60), 1000 if cfg["cen"] != JARDIM else 1700, dd)}})
        elif i % 4 == 1:                                   # "Foi você?" — interrogatório em tela dividida
            quem, cen, extra = cfg["suspeito"]
            if quem == "gato":
                painel_b = {"cenario": cen, "camera": {"x": 1300, "y": 640, "zoom": 1.6, "zoom_fim": 1.7},
                            "objetos": {"gato": obj("gato", 1300, CHAO, 1.2, dd, z=3, fixo={"lado": -1.0},
                                                    pts={"assusta": [(round(tq, 2), 1.0)], "miau": [(round(tq + 0.6, 2), 1.0)]})}}
            else:
                painel_b = {"cenario": cen, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58},
                            "atores": {quem: a(1300, ("look_around", 0.1), ("shake_fist" if quem == VC else "pensar", round(tq + 0.3, 2)),
                                               turn=-0.2, **(extra or {}))}}
            out.append(R.dividida({"cenario": cfg["cen"], "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58}, "cantam": [LA],
                                   "atores": {LA: detetive(1300, ("point", round(tq, 2)), turn=0.3, expr="determined")}},
                                  painel_b, linhas=2, layout="vertical",
                                  callout=[call(0.1, "BRIGADEIRO, BRIGADEIRO!", "laranja"), call(round(tq, 2), "FOI VOCÊ?", "vermelho")]))
        elif i % 4 == 2:                                   # a dança do brigadeiro
            cen, trio, st = cfg["danca"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "flash": n == 1, "cantam": [LA],
                        "callout": [call(0.1, "BRIGADEIRO, BRIGADEIRO!", "laranja")],
                        "atores": {c: g(x, ("dance", 0.05 * j, s), turn=tv) | ({"expr": "joy"} if c in (VO, VC, MA) else {})
                                   for j, (c, x, tv, s) in enumerate(zip(trio, (380, 960, 1540), (0.2, 0.0, -0.2), st))}})
        else:                                              # "Foi você? Fala primeiro!" — para quem assiste
            out.append({"linhas": 2, "cenario": cfg["cen"], "camera": cab(1300), "cantam": [LA],
                        "callout": [call(round(tq, 2), "FOI VOCÊ? FALA PRIMEIRO!", "roxo")],
                        "atores": {LA: detetive(1300, ("apontar_camera", round(tq, 2)), expr="sly")}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 2}, {"seg": 3.6}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 2, "cenario": SALA, "camera": BU(1300), "cantam": [LA], "callout": [call(0.2, "BORA, TURMINHA!", "laranja")],
     "atores": {LA: detetive(1000, ("cheguei", 0.1), turn=0.3), LU: sujo(a(1720, ("wave", 0.4), turn=-0.3))}},
    {**banda(max(0.6, d[1])), "titulo": "a banda na festa da vovó"},
    {"seg": max(0.6, d[2]), "cenario": "danca_ondas_amarelo", "camera": GCAM, "fx": ["confete"], "titulo": "a vovó dança com os netos",
     "atores": {LA: g(380, ("dance", 0.0, "cintura"), turn=0.2), VO: g(960, ("dance", 0.1, "balanco")) | {"expr": "joy"},
                LU: g(1540, ("dance", 0.0, "twist"), turn=-0.2)}},
]


# ───────── ponte: comandos de detetive ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4 + [{"linhas": 2}] + [{"linhas": 1}] * 3)     # "E mais!" junto com "segue a pegada"
d = dur(T)
ta = em(T[7][0], T[7][2], "achei", default=0.3)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": BU(1300), "callout": [call(0.1, "PEGA A LUPA, DETETIVE!", "amarelo")],
     "atores": {LA: detetive(1300, ("grab", 0.1), expr="determined")}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.1, "PROCURA PELO CHÃO!", "verde")],
     "atores": {LA: detetive(900, ("look_around", 0.0), turn=0.35, expr="determined")}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.1, "OLHA EMBAIXO DA MESA…", "roxo")],
     "objetos": {**mesa(1550), **bandeja(d[2], x=1550, quantos=0)},
     "atores": {LA: detetive(620, ("sit", 0.2), turn=0.4, expr="sly", z=6, y=CHAO + 50)}},
    {"linhas": 1, "cenario": SALA, "camera": {"x": 1300, "y": 900, "zoom": 1.8, "zoom_fim": 1.95}, "fx": ["estrelas"],
     "callout": [call(0.2, "PEGADA DE CHOCOLATE!", "laranja")],
     "objetos": pegadas(d[3], x=1300, y=990, n=(0, 7), depth=0.75, brilho=1.0)},
    {"linhas": 2, "cenario": COZ, "camera": corpo(1300, 1450), "callout": [call(0.1, "E MAIS!", "verde"), call(round(d[4] * 0.4, 2), "SEGUE A PEGADA!", "laranja")],
     "objetos": pegadas(d[4], x=1500, n=(7, 7), depth=0.65),
     "atores": {LA: anda(detetive(500, turn=0.4, expr="determined"), 1500, d[4], como="walk")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "callout": [call(0.1, "NA PONTA DO PÉ…", "rosa")],
     "objetos": pegadas(d[5], x=1400, n=(7, 7), depth=0.6),
     "atores": {LA: anda(detetive(500, turn=0.4, expr="sly"), 1200, d[5])}},
    {"linhas": 1, "cenario": QUARTO, "camera": BU(1300), "callout": [call(0.1, "PSIU, DEVAGARINHO…", "roxo")],
     "atores": {LA: detetive(1100, ("estatua", 0.0), turn=0.35, expr="sly")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "flash": True, "tremor": [round(ta, 2)],
     "callout": [call(round(ta, 2), "ACHEI! SABE QUEM É?", "vermelho")],
     "atores": {LA: detetive(800, ("point", round(ta, 2)), turn=0.35, expr="surprised"),
                LU: sujo(a(1750, ("take", round(ta, 2)), turn=-0.35, expr="shock"))}},
]


# ───────── 2º verso: a VIRADA — foi o Luisinho… e guardou o último pra ela ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1300), "callout": [call(0.2, "O LUISINHO FICOU VERMELHO!", "vermelho")],
     "atores": {LU: sujo(a(1300, ("estatua", 0.0), expr="sad"))}},
    {"linhas": 1, "cenario": QUARTO, "camera": BU(1300), "callout": [call(0.2, "ESCONDEU A MÃO PRA TRÁS…", "roxo")],
     "atores": {LA: detetive(880, ("pensar", 0.1), turn=0.35), LU: sujo(a(1720, ("look_around", 0.1), turn=-0.35, expr="sly"))}},
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1300), "callout": [call(0.2, "FUI EU, SIM, EU CONFESSO!", "laranja")],
     "atores": {LU: sujo(a(1300, ("estatua", 0.0), expr="crying"))}},
    R.dividida({"cenario": COZ, "camera": {"x": 1300, "y": 600, "zoom": 1.5, "zoom_fim": 1.58},
                "atores": {LU: sujo(a(1300, ("eat", 0.1), segura="brigadeiro", expr="joy"), t=0.6)}},
               {"cenario": COZ, "camera": {"x": 1300, "y": 560, "zoom": 1.9, "zoom_fim": 2.0},
                "objetos": {**mesa(), **bandeja(d[3], x=1300, lin={"quantos": (12, 0)})}},
               linhas=1, layout="diagonal", callout=[call(0.1, "NÃO AGUENTEI!", "laranja")]),
    {"linhas": 1, "cenario": QUARTO, "camera": BU(1300), "callout": [call(0.2, "MAS ABRIU A MÃO FECHADA…", "verde")],
     "atores": {LA: detetive(880, ("estatua", 0.0), turn=0.35, expr="surprised"),
                LU: sujo(a(1720, ("entregar", 0.2), segura="brigadeiro", turn=-0.35, expr="joy"))}},
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1300), "fx": ["coracoes"], "callout": [call(0.2, "COM UM SORRISO MANEIRO!", "rosa")],
     "atores": {LU: sujo(a(1300, ("sorriso", 0.1), segura="brigadeiro"))}},
    {"linhas": 1, "cenario": QUARTO, "camera": BU(1300), "fx": ["coracoes"], "callout": [call(0.2, "GUARDEI UM PRA VOCÊ!", "rosa")],
     "atores": {LU: sujo(a(1720, ("entregar", 0.1), segura="brigadeiro", turn=-0.35, expr="joy")),
                LA: a(880, ("receber", round(d[6] * 0.5, 2)), turn=0.35, segura="brigadeiro")}},
    {"linhas": 1, "cenario": QUARTO, "camera": BU(1300), "fx": ["coracoes"], "callout": [call(0.2, "O ÚLTIMO BRIGADEIRO!", "laranja")],
     "atores": {LA: a(880, ("abraco", 0.1), turn=0.35), LU: sujo(a(1720, ("abraco", 0.15), turn=-0.35, expr="joy"))}},
]


# ───────── intervalo 2 (só instrumental): a festa continua ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1, d2 = round(D2 * 0.4, 2), round(D2 * 0.3, 2)
R.partes["intervalo#2"] = [
    {**banda(d1), "titulo": "a banda na festa da vovó"},
    {"seg": d2, "cenario": SALA, "camera": BU(1300), "fx": ["coracoes"], "titulo": "a vovó assopra a vela",
     "objetos": {**mesa(1150), **bolo(d2, x=1150, vela=1.0)} | {"bolo": obj("bolo_aniversario", 1150, MESA_TOPO - 6, 0.42, d2, z=4,
                                                                           fixo={"vela": 1.0}, pts={"vela": [(1.2, 0.0)], "fumaca": [(d2 - 0.1, 2.0)]})},
     "atores": {VO: a(1720, ("laugh", 1.3), turn=-0.35, z=5, expr="joy")}},     # ao lado do bolo (o bolo não cobre o rosto)
    {"seg": round(D2 - d1 - d2, 2), "cenario": SALA, "camera": corpo(1300), "fx": ["confete"], "titulo": "a turma dança na festa",
     "objetos": baloes(D2 - d1 - d2, xs=((420, 4), (2200, 1))),
     "atores": {LA: fundo(a(560, ("dance", 0.0, "cintura"), turn=0.3)), VC: fundo(a(1300, ("dance", 0.1, "balanco"), expr="joy")),
                LU: fundo(sujo(a(2040, ("dance", 0.05, "chute"), turn=-0.3)))}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "callout": [call(0.2, "E VOCÊ? DIVIDE O SEU?", "rosa")],
     "atores": {LA: a(1300, ("apontar_camera", 0.1), segura="brigadeiro")}},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {VC: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0, "expr": "joy"}}},
    {"linhas": 1, "cenario": CASA, "camera": BU(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {LU: sujo(a(880, ("point", 0.1), turn=0.3)), MA: a(1720, ("wave", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LA: g(560, ("point", 0.2), turn=0.2) | {"depth": 1.0}}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 2.6, "cenario": SALA, "camera": corpo(1300), "fx": ["coracoes"],
     "callout": [call(0.2, "BRIGADEIRO!", "laranja"), call(1.3, "TCHAU!", "amarelo")],
     "atores": {LA: fundo(a(560, ("wave", 0.0), turn=0.3)), VO: fundo(a(1300, ("wave", 0.1), expr="joy")),
                LU: fundo(sujo(a(2040, ("wave", 0.1), turn=-0.3)))}},
    {"seg": round(dfim - 2.6, 2), "cenario": SALA, "camera": cab(1300), "flash": True, "callout": [call(0.2, "NHAC!", "vermelho")],
     "titulo": "o último NHAC do Luisinho", "atores": {LU: sujo(a(1300, ("eat", 0.1), segura="brigadeiro", expr="joy"))}},
]


# ── vida no cenário: nuvens no céu ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    cam = sb.get("camera") or {}
    if cen == SALA and "bal0" not in ob and cam is not CAM_BANDEJA:           # a festa: balões balançando no alto
        ob.update(baloes(dd, xs=((420, j % 5), (2200, (j + 2) % 5))))
    if cen == QUARTO and "peg" not in ob:                                      # a trilha de chocolate que levou até o quarto
        ob["peg"] = obj("pegadas", 700, 1010, 0.55, dd, z=2, fixo={"n": 7.0, "lado": 1.0},
                        pts={"brilho": [(round(t, 2), 0.7 if k % 2 == 0 else 0.0) for k, t in enumerate(x * 0.45 for x in range(int(dd / 0.45) + 1))]})
    if cen in (CASA, JARDIM):
        x0 = (300, 1700, 900, 2100)[j % 4]
        ob.setdefault("nv", obj("nuvem", x0, 260, 0.32, dd, z=0, fixo={"cara": 1.0}, lin={"x": (x0, x0 + 280)}))
    if not ob:
        sb.pop("objetos", None)


for chave, planos in R.partes.items():
    k_info = chave if chave in R.info else f"{chave}#1"
    for j, (p_, (t0, t1, _)) in enumerate(zip(planos, R.tempos(k_info, planos))):
        for sb in [p_] + list((p_.get("tela_dividida") or {}).get("paineis", [])):
            _ambiente(sb, round(t1 - t0, 2), j)

R.salvar("Roteiro de 33 'Brigadeiro' (take inteiro, 2:22, E18, nota 5, letra 5–8): a festa da vovó, a bandeja de brigadeiro "
         "(bandeja_brigadeiro) que brilha e depois aparece vazia; a Laurinha detetive (lupa) interroga os suspeitos em tela "
         "dividida; a ponte segue as pegadas de chocolate (pegadas) até o quarto; a virada: o Luisinho, de boca suja de "
         "chocolate, confessa e guardou o último brigadeiro pra ela. Gerado por scripts/roteiros/ep33_brigadeiro.py.", escala=E)
