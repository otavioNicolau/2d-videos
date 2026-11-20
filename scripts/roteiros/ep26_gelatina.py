"""Roteiro verso a verso de 26 "Gelatina!" (take v1 cortado em 2:32 sem o aviso cantado, Laurinha, estilo E12, nota 4,7)
→ musicas/26_gelatina/roteiro.json.

A vovó faz uma gelatina vermelhinha na COZINHA; ela acorda, cria perninhas e SAI CORRENDO pela casa (sala) e pelo
JARDIM (o gato corre atrás). Quem olha para ela começa a TREMER junto (passo novo `treme`). "Tremia pra cá / pra lá" =
telas divididas (a gelatina × a turma tremendo igual). Refrão: todo mundo treme (ninguém fica firme). Ponte de comandos:
fica molinho (a gelatina esparrama, a turma agacha), fica durinho (estátua), treme a barriga, CONGELOU (vira gelo azul,
no cenário de gelo). A banda toca na cozinha da vovó (nada de salão lilás). Final: a gelatina dá tchau tremendo.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep26_gelatina.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import LA, LU, Roteiro, call  # noqa: E402

R = Roteiro("laurinha/ep26-gelatina", "26_gelatina", "laurinha")
COZ, SALA, JARDIM, GELO, CASA = "plano_cozinha", "plano_sala", "plano_jardim", "plano_gelo", "plano_casa_frente"
PALCO = COZ                       # 19/11: a banda toca na cozinha da vovó (o tema), não no salão lilás de festa
VO, VZ, MA = "vovo", "vovozinho", "mamae"
MESA_Y = 930 - 240 * 1.3


def gel(d, x=1300, y=960, depth=0.8, z=4, treme=0.5, corre=None, **canais):
    """A gelatina: balança sempre (fase contínua); `corre` = [(t, x), …] cria perninhas e anda até x."""
    d = max(0.6, d)
    ks = [{"t": 0.0, "pose": {"fase": 0.0, "treme": float(treme) if not isinstance(treme, list) else 0.0}, "ease": "step"},
          {"t": round(d - 0.05, 2), "pose": {"fase": round(d * 2.6, 2)}, "ease": "linear"}]
    if isinstance(treme, list):
        ks += [{"t": round(t, 2), "pose": {"treme": float(v)}, "ease": "out"} for t, v in treme]
    if corre:
        ks[0]["pose"].update({"pernas": 1.0, "prato": 0.0, "anda": 0.0, "x": float(x)})
        ks.append({"t": round(d - 0.05, 2), "pose": {"anda": round(d * 2.8, 2)}, "ease": "linear"})
        ks += [{"t": round(t, 2), "pose": {"x": float(v)}, "ease": "inout"} for t, v in corre]
    for c, v in canais.items():
        if isinstance(v, (int, float)):
            ks[0]["pose"][c] = float(v)
        else:
            ks += [{"t": round(t, 2), "pose": {c: float(val)}, "ease": "out"} for t, val in v]
    return {"id": "gelatina", "x": x, "y": y, "z": z, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def mesa(x=1300, treme_d=None):
    """a mesa; com `treme_d` (duração) ela chacoalha junto quando todo mundo treme."""
    m = {"id": "mesa", "x": x, "y": 930, "z": 1, "depth": 1.3}
    if treme_d:
        m["keys"] = [{"t": round(0.19 * j, 2), "pose": {"x": float(x + (7 if j % 2 else -7))}, "ease": "inout"}
                     for j in range(int(max(0.6, treme_d) / 0.19))]
    return m


def obj(id_, x, y, depth, d, z=1, fixo=None, lin=None, pts=None):
    """objeto de cena animado: `fixo` {canal: v}, `lin` {canal: (v0, v1)} do começo ao fim, `pts` {canal: [(t, v), …]}."""
    d = max(0.6, d)
    ks = [{"t": 0.0, "pose": dict(fixo or {}), "ease": "step"}]
    for c, (a, b) in (lin or {}).items():
        ks[0]["pose"][c] = float(a)
        ks.append({"t": round(d - 0.06, 2), "pose": {c: float(b)}, "ease": "linear"})
    for c, vs in (pts or {}).items():
        ks += [{"t": round(t, 2), "pose": {c: float(v)}, "ease": "out"} for t, v in vs]
    return {"id": id_, "x": x, "y": y, "z": z, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def nuvem(d, x=500, y=260):
    return obj("nuvem", x, y, 0.35, d, z=0, lin={"x": (x, x + 260)})


def pipa(d, x=1900, y=420):
    return obj("pipa", x, y, 0.4, d, z=0, fixo={"rabiola": 1.0}, lin={"balanco": (0.0, d * 1.2)})


def gato(x, d, y=930, depth=0.5, lado=1.0, miau=(0.8,), assusta=None, corre=None):
    ks = [{"t": 0.0, "pose": {"lado": lado, "rabo": 0.0, "miau": 0.0, "assusta": 0.0}, "ease": "step"}]
    ks += [{"t": round(0.4 * j, 2), "pose": {"rabo": float(j % 2)}, "ease": "inout"} for j in range(1, int(d / 0.4))]
    for t in miau:
        ks += [{"t": round(t, 2), "pose": {"miau": 1.0}, "ease": "out"}, {"t": round(t + 0.45, 2), "pose": {"miau": 0.0}, "ease": "in"}]
    if assusta is not None:
        ks.append({"t": round(assusta, 2), "pose": {"assusta": 1.0}, "ease": "back"})
    if corre:
        ks[0]["pose"]["x"] = float(x)
        ks += [{"t": round(t, 2), "pose": {"x": float(v)}, "ease": "inout"} for t, v in corre]
    return {"id": "gato", "x": x, "y": y, "z": 2, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def treme(quem_x, turn=0.0, t=0.1, expr=None, **kw):
    a = {"x": quem_x, "turn": turn, "acoes": [{"t": t, "do": "dance", "style": "treme", "dur": "resto"}], **kw}
    if expr:
        a["expr"] = expr
    return a


def sol(d):
    return {"id": "sol", "x": 2250, "y": 200, "z": 0, "depth": 0.5,
            "keys": [{"t": 0.0, "pose": {"giro": 0.0, "boca": 0.0}, "ease": "step"}, {"t": 0.6, "pose": {"boca": 1.0}, "ease": "out"},
                     {"t": round(max(0.7, d) - 0.06, 2), "pose": {"giro": 0.5}, "ease": "linear"}]}


def dur(T):
    return [round(t1 - t0, 2) for t0, t1, _ in T]


# ───────── intro ─────────
T = R.tempos("intro#1", [{"seg": 2.0}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1, "seg": 2.8}, {"seg": 3.4}, {"seg": 0.0}])
d = dur(T)
R.partes["intro"] = [
    {"seg": 2.0, "cenario": COZ, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.12}, "titulo": "a gelatina da vovó",
     "objetos": {"m": mesa(), "g": gel(d[0], y=MESA_Y, depth=0.5, treme=0.0, lid=[(0.0, 1.0), (1.4, 0.0)])},
     "atores": {VO: {"x": 0, "turn": 0.3, "acoes": [{"t": 0.0, "do": "walk", "to_x": 480, "dur": 1.6}]}}},
    {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 470, "zoom": 1.5, "zoom_fim": 1.6}, "flash": True,
     "callout": [call(0.2, "GELATINA!", "vermelho")],
     "objetos": {"m": mesa(), "g": gel(d[1], y=MESA_Y, depth=0.5, treme=[(0.0, 0.3), (0.6, 1.0)], boca=[(0.3, 0.9)])}},
    {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15},
     "objetos": {"m": mesa(), "g": gel(d[2], y=MESA_Y, depth=0.5, treme=0.8, boca=0.6)},
     "atores": {LA: {"x": 450, "turn": 0.3, "expr": "surprised", "acoes": [{"t": 0.1, "do": "shock_reaction", "dur": "resto"}]},
                LU: {"x": 2150, "turn": -0.3, "acoes": [{"t": 0.2, "do": "laugh", "dur": "resto"}]}}},
    {"linhas": 1, "seg": 2.8, "cenario": CASA, "camera": {"x": 1300, "y": 560, "zoom": 1.1, "zoom_fim": 1.2},
     "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")], "fx": ["confete"], "objetos": {"n": nuvem(2.8, 300, 430)},
     "atores": {LA: {"x": 900, "turn": 0.25, "acoes": [{"t": 0.1, "do": "jump", "dur": 0.8}, {"t": 1.0, "do": "dance", "style": "treme", "dur": "resto"}]},
                LU: {"x": 1700, "turn": -0.25, "acoes": [{"t": 0.2, "do": "jump", "dur": 0.8}, {"t": 1.1, "do": "dance", "style": "treme", "dur": "resto"}]}}},
    {**R.banda(PALCO, 3.4, fx=["notas"]), "titulo": "a banda na cozinha da vovó"},
    {**R.banda(PALCO, max(0.6, d[5]), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.2, "zoom_fim": 1.1}),
     "titulo": "teclado e bateria"},
]
R.partes["intro"][4]["objetos"]["g"] = gel(3.4, x=2250, y=960, depth=0.45, treme=0.8, boca=0.6)


# ───────── verso: a vovó fez gelatina… saiu correndo… quem olhava começava a tremelicar ─────────
def verso(key, n):
    T = R.tempos(key, [{"linhas": 1}] * 8)
    d = dur(T)
    cen_fuga = SALA if n == 1 else JARDIM
    out = [
        # A vovó fez gelatina
        {"linhas": 1, "cenario": COZ if n == 1 else JARDIM, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08},
         "callout": [call(0.4, "A VOVÓ FEZ!", "laranja")],
         "objetos": {"m": mesa(), "g": gel(d[0], y=MESA_Y, depth=0.5, treme=0.2, lid=[(0.0, 1.0), (0.9, 0.0)])} | ({"s": sol(d[0])} if n == 2 else {}),
         "atores": {VO: {"x": 470, "turn": 0.3, "acoes": [{"t": 0.1, "do": "point", "dur": 1.0}, {"t": 1.2, "do": "laugh", "dur": "resto"}]}}},
        # Vermelhinha e tremendo — close
        {"linhas": 1, "cenario": COZ if n == 1 else JARDIM, "camera": {"x": 1300, "y": 470, "zoom": 1.55, "zoom_fim": 1.65},
         "callout": [call(0.3, "VERMELHINHA!", "vermelho")],
         "objetos": {"m": mesa(), "g": gel(d[1], y=MESA_Y, depth=0.5, treme=[(0.0, 0.2), (0.5, 1.0)], boca=0.5)}},
        # Botou em cima da mesa — a turma chega
        {"linhas": 1, "cenario": COZ if n == 1 else JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08},
         "callout": [call(0.4, "NA MESA!", "verde")],
         "objetos": {"m": mesa(), "g": gel(d[2], y=MESA_Y, depth=0.5, treme=0.4, olha=[(0.3, -1.0), (1.0, 1.0)])}
                    | ({"c": {**gato(1000, d[2], y=1000, depth=0.45), "z": 4}} if n == 2 else {}),
         "atores": {LA: {"x": 250, "turn": 0.3, "acoes": [{"t": 0.0, "do": "sneak" if n == 1 else "run", "to_x": 650, "dur": 1.0},
                                                          {"t": 1.1, "do": "dance", "style": R.estilo(), "dur": "resto"}]},
                    LU: {"x": 2500 if n == 1 else 2600, "turn": -0.3, "acoes": [{"t": 0.1, "do": "sneak" if n == 1 else "run", "to_x": 2000, "dur": 1.0},
                                                                               {"t": 1.2, "do": "dance", "style": R.estilo(), "dur": "resto"}]}}},
        # E ela saiu correndo! — perninhas
        {"linhas": 1, "cenario": cen_fuga, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "tremor": [0.3],
         "callout": [call(0.2, "SAIU CORRENDO!", "vermelho")],
         "objetos": {"g": gel(d[3], x=1100, depth=0.6, treme=0.9, boca=0.9, corre=[(round(d[3] - 0.1, 2), 2000)])}
                    | ({"c": gato(200, d[3], lado=1.0, miau=(0.3,), corre=[(round(d[3] - 0.1, 2), 1500)])} if n == 2 else {}),
         "atores": {(LA if n == 1 else LU): {"x": 2150, "turn": -0.3, "expr": "surprised",
                                            "acoes": [{"t": 0.2, "do": "shock_reaction", "dur": "resto"}]},
                    (LU if n == 1 else LA): {"x": 900, "turn": 0.3, "acoes": [{"t": 0.1, "do": "grab", "dur": 0.7},
                                                                             {"t": 0.85, "do": "fall" if n == 1 else "crash", "to_y": 930, "dur": "resto"}]}}},
        # Tremia pra cá — gelatina × turma tremendo
        R.dividida({"cenario": cen_fuga, "camera": {"x": 1300, "y": 560, "zoom": 1.2, "zoom_fim": 1.3},
                    "objetos": {"g": gel(d[4], x=1300, depth=0.75, treme=1.0, boca=0.7)}},
                   {"cenario": "danca_ondas_rosa" if n == 1 else "danca_xadrez_verde", "camera": {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.35},
                    "atores": {LA: treme(1300, 0.15)}},
                   linhas=1, layout="vertical" if n == 1 else "diagonal", callout=[call(0.3, "PRA CÁ!", "rosa")]),
        # Tremia pra lá
        R.dividida({"cenario": "danca_ondas_azul" if n == 1 else "danca_xadrez_amarelo", "camera": {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.35},
                    "atores": {LU: treme(1300, -0.15)}},
                   {"cenario": cen_fuga, "camera": {"x": 1300, "y": 560, "zoom": 1.2, "zoom_fim": 1.3},
                    "objetos": {"g": gel(d[5], x=1300, depth=0.75, treme=1.0, boca=0.7, olha=-1.0)}},
                   linhas=1, layout="diagonal" if n == 1 else "vertical", callout=[call(0.3, "PRA LÁ!", "azul")]),
        # E quem olhava pra ela — o vovô e a mamãe olham
        {"linhas": 1, "cenario": cen_fuga, "camera": {"x": 1300, "y": 540, "zoom": 1.1, "zoom_fim": 1.2},
         "callout": [call(0.4, "OLHOU?", "laranja")],
         "objetos": {"g": gel(d[6], x=1300, depth=0.6, treme=0.7, boca=0.5)} | ({"s": sol(d[6]), "p": pipa(d[6], 1900, 380)} if n == 2 else
                                                                               {"cx": obj("caixa_brinquedos", 2550, 930, 0.7, d[6], pts={"carrinho": [(0.5, 1.0)]})}),
         "atores": {VZ: {"x": 550, "turn": 0.3, "acoes": [{"t": 0.1, "do": "look_around", "dur": "resto"}]},
                    MA: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.2, "do": "pensar", "dur": "resto"}]}}},
        # Começava a tremelicar! — todo mundo treme
        {"linhas": 1, "cenario": cen_fuga, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.05}, "tremor": [round(d[7] * 0.4, 2)],
         "callout": [call(0.3, "TREMELICAR!", "vermelho")], "fx": ["estrelas"],
         "objetos": {"g": gel(d[7], x=1300, y=1040, depth=0.7, treme=1.0, boca=0.9)}
                    | ({"c": {**gato(1680, d[7], y=1010, depth=0.45, lado=-1.0, assusta=0.3), "z": 4}} if n == 2 else {}),
         "atores": {VZ: treme(320, 0.3), MA: treme(880, 0.3, t=0.2), LA: treme(1860, -0.3, t=0.15), LU: treme(2280, -0.3, t=0.25)}},
    ]
    if n == 2:                                                    # 2º verso no jardim: a vovó traz outra gelatina
        out[0]["atores"][VZ] = {"x": 2150, "turn": -0.3, "acoes": [{"t": 0.2, "do": "cheguei", "dur": "resto"}]}
        out[0]["objetos"]["pl"] = obj("plantinha", 250, 960, 0.45, d[0], pts={"boca": [(0.6, 1.0)], "cresce": [(0.0, 0.6), (1.2, 1.0)]})
        out[6]["atores"][VZ] = {"x": 550, "turn": 0.3, "acoes": [{"t": 0.1, "do": "sit", "dur": "resto"}]}
        out[3]["objetos"]["n"] = nuvem(d[3], 1900, 430)
        out[7]["objetos"]["s"] = sol(d[7])
        out[7]["atores"] = {VO: treme(320, 0.3), VZ: treme(880, 0.3, t=0.2), LA: treme(1860, -0.3, t=0.15), LU: treme(2280, -0.3, t=0.25)}
    return out


R.partes["verso#1"] = verso("verso#1", 1)
R.partes["verso#2"] = verso("verso#2", 2)


# ───────── refrão: gelatina, gelatina! treme, treme, treme! / ninguém fica firme! ─────────
FUNDO_REF = {1: SALA, 2: "plano_parque", 3: "plano_quarto_azul"}           # a gelatina foge pela casa toda (cenários de verdade)
FIM_REF = {1: "plano_quarto_rosa", 2: "plano_campo"}


def extras_ref(n, d):
    return {1: {"cx": obj("caixa_brinquedos", 2550, 930, 0.7, d, pts={"carrinho": [(0.4, 1.0)]})},
            2: {"p": pipa(d, 2300, 520), "s": sol(d), "n": nuvem(d, 350, 430)},
            3: {"cx": obj("caixa_brinquedos", 150, 930, 0.7, d, pts={"carrinho": [(0.6, 1.0)]}),
                "v": obj("ventilador", 2500, 940, 0.55, d, fixo={"vento": 1.0}, lin={"giro": (0.0, d * 3)})}}[n]
CORES = ["vermelho", "laranja", "roxo"]


def refrao(n):
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * 4)
    out = []
    for i, (t0, t1, _) in enumerate(T):
        d = round(t1 - t0, 2)
        if n == 3 and i in (1, 3):
            p = R.banda(PALCO, d, teclado=(i == 3), fx=["confete"], cam={"x": 1300, "y": 620, "zoom": 1.05, "zoom_fim": 1.12})
            p.pop("seg")
            p.update({"linhas": 2, "callout": [call(0.3, "TREME, TREME!", "vermelho")]})
            p["objetos"]["g"] = gel(d, x=2300 if i == 1 else 300, y=960, depth=0.45, treme=1.0, boca=0.8)
        elif i == 0:                                              # a gelatina no meio e a turma tremendo dos lados
            p = {"linhas": 2, "cenario": FUNDO_REF[n], "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15}, "fx": ["estrelas"],
                 "callout": [call(0.2, "GELATINA!", CORES[n - 1]), call(round(d * 0.5, 2), "TREME, TREME!", "vermelho")],
                 "objetos": {"g": gel(d, x=1300, y=1000, depth=0.7, treme=[(0.0, 0.4), (round(d * 0.45, 2), 1.0)], boca=0.8)} | extras_ref(n, d),
                 "atores": {LA: treme(500 if n != 3 else 750, 0.3), LU: treme({1: 2050, 2: 1800, 3: 1950}[n], -0.3, t=0.2)}}
            if n == 1:
                p["flash"] = True
        elif i == 1:                                              # ninguém fica firme: a família inteira treme
            cen = {1: COZ, 2: JARDIM}[n]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.05}, "tremor": [round(d * 0.55, 2)],
                 "callout": [call(round(d * 0.45, 2), "NINGUÉM FICA FIRME!", "laranja")],
                 "objetos": {"g": gel(d, x=1300, y=1040, depth=0.7, treme=1.0, boca=0.9),
                             "c": {**gato(1680, d, y=1010, depth=0.45, lado=-1.0, assusta=0.5), "z": 4}} | ({"s": sol(d)} if n == 2 else {}),
                 "atores": {VO: treme(320, 0.3), MA: treme(880, 0.3, t=0.2), LA: treme(1860, -0.3, t=0.1), LU: treme(2280, -0.3, t=0.3)}}
            if n == 2:
                p["atores"][VZ] = p["atores"].pop(MA)
        elif i == 2:                                              # tela dividida: a gelatina × a turma
            p = R.dividida({"cenario": SALA if n != 2 else JARDIM, "camera": {"x": 1300, "y": 540, "zoom": 1.2, "zoom_fim": 1.3},
                            "objetos": {"g": gel(d, x=1300, depth=0.75, treme=1.0, boca=0.7, olha=[(0.0, -1.0), (d * 0.5, 1.0)])}},
                           {"cenario": COZ if n != 2 else SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.15, "zoom_fim": 1.25},
                            "atores": {LA: treme(1050, 0.25), LU: treme(1550, -0.25, t=0.2)}},
                           linhas=2, layout="diagonal" if n % 2 else "vertical", callout=[call(0.3, "TREME, TREME!", CORES[n - 1])])
        else:                                                     # ninguém fica firme: o gato e a turma escorregam de tanto tremer
            p = {"linhas": 2, "cenario": FIM_REF[n], "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1},
                 "fx": ["confete"], "callout": [call(round(d * 0.45, 2), "NINGUÉM FICA FIRME!", "laranja")],
                 "objetos": {"g": gel(d, x=1950, y=1000, depth=0.6, treme=1.0, boca=0.9, mole=[(round(d * 0.5, 2), 0.6)])}
                            | ({"n": nuvem(d, 400, 430), "pt": obj("pato", 2400, 960, 0.5, d, pts={"quem": [(0.5, 1.0), (1.0, 0.0), (1.6, 1.0)], "asas": [(0.5, 1.0)]})}
                               if n == 2 else {"j": obj("janela", 2250, 520, 0.8, d, pts={"abre": [(0.3, 1.0)], "luz": [(0.3, 1.0)]})}),
                 "atores": {LA: {"x": 450, "turn": 0.3, "acoes": [{"t": 0.1, "do": "dance", "style": "treme", "dur": round(d * 0.5, 2)},
                                                                  {"t": round(d * 0.55, 2), "do": "slip", "dur": "resto"}]},
                            LU: {"x": 950, "turn": 0.3, "acoes": [{"t": 0.2, "do": "dance", "style": "treme", "dur": round(d * 0.5, 2)},
                                                                  {"t": round(d * 0.6, 2), "do": "bounce", "dur": "resto"}]}}}
        out.append(p)
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos (bordão + banda na cozinha) ─────────
def intervalo(key, n):
    b, bl = R.bloco(key)
    D = b["e"] - b["s"]
    if not bl:
        s1 = round(D / 2, 2)
        banda = {**R.banda(PALCO, s1, fx=["confete"], cam={"x": 1350, "y": 600, "zoom": 1.15, "zoom_fim": 1.05}), "titulo": "a banda (sax)"}
        banda["objetos"]["g"] = gel(s1, x=2300, y=960, depth=0.45, treme=1.0, boca=0.8)
        return [banda,
                {"seg": round(D - s1, 2), "cenario": COZ, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.1}, "titulo": "a gelatina dança",
                 "objetos": {"m": mesa(treme_d=D - s1), "g": gel(D - s1, y=MESA_Y, depth=0.5, treme=1.0, boca=0.7),
                             "c": {**gato(1000, D - s1, y=1010, depth=0.45, miau=(0.5, 2.0)), "z": 4}},
                 "atores": {LA: {"x": 450, "turn": 0.3, "acoes": [{"t": 0.1, "do": "dance", "style": "pulinho", "dur": "resto"}]},
                            LU: {"x": 2150, "turn": -0.3, "acoes": [{"t": 0.1, "do": "dance", "style": "roda", "dur": "resto"}]}}}]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = 3.4
    out = [{"linhas": 1, "seg": p1, "cenario": COZ if n == 1 else JARDIM, "camera": "close:laurinha", "callout": [call(0.2, "BORA, TURMINHA!", "rosa")],
            "objetos": {} if n == 1 else {"s": sol(p1)},
            "atores": {LA: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
           {"linhas": 1, "seg": p2, "cenario": "danca_bolinhas_rosa" if n == 1 else "plano_banheiro",
            "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")], "fx": ["confete"],
            "objetos": {"g": gel(p2, x=1600, y=1060, depth=0.45, treme=1.0, boca=0.7)}
                       | ({} if n == 1 else {"sb": obj("sabonete", 1950, 1000, 0.5, p2, fixo={"bolhas": 1.0}, pts={"pulo": [(0.3, 1.0), (0.7, 0.0), (1.5, 1.0), (1.9, 0.0)]}),
                                            "b": obj("bolha", 300, 700, 0.3, p2, lin={"balanco": (0.0, 3.0)})}),
            "atores": {LA: {"x": 420, "y": 1010, "depth": 1.0, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura", "dur": "resto"}]},
                       LU: {"x": 1000, "y": 1010, "depth": 1.0, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "joelho", "dur": "resto"}]}}}]
    resto = D - p1 - p2
    s3 = round(resto / 3, 2)
    out += [{**R.banda(PALCO, s3, fx=["notas"]), "titulo": "a banda"},
            {"seg": s3, "cenario": COZ if n == 1 else SALA, "camera": {"x": 1300, "y": 540, "zoom": 1.05, "zoom_fim": 1.15}, "titulo": "a gelatina dança",
             "fx": ["notas"],
             "objetos": {"g": gel(s3, x=1300, y=1000, depth=0.55, treme=1.0, boca=0.7, olha=[(0.0, -1.0), (s3 * 0.5, 1.0)])}
                        | ({"c": {**gato(1700, s3, y=1010, depth=0.45, lado=-1.0, miau=(1.0, 3.0)), "z": 4}} if n == 2 else {}),
             "atores": {VO: treme(450, 0.3) if n == 1 else {"x": 450, "turn": 0.3, "acoes": [{"t": 0.1, "do": "dance", "style": "twist", "dur": "resto"}]},
                        (VZ if n == 1 else MA): treme(2150, -0.3, t=0.2) if n == 1 else
                        {"x": 2150, "turn": -0.3, "acoes": [{"t": 0.1, "do": "dance", "style": "passinho", "dur": "resto"}]}}},
            {**R.banda(PALCO, round(resto - 2 * s3, 2), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.25, "zoom_fim": 1.15}),
             "titulo": "teclado e bateria"}]
    out[2]["objetos"]["g"] = gel(s3, x=300, y=960, depth=0.45, treme=1.0, boca=0.6)
    return out


R.partes["intervalo#1"] = intervalo("intervalo#1", 1)
R.partes["intervalo#2"] = intervalo("intervalo#2", 2)
R.partes["intervalo#3"] = intervalo("intervalo#3", 3)

# ───────── ponte: fica molinho… fica durinho! treme a barriga… congelou! ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4)
dp = dur(T)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": "plano_quarto_rosa", "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.12},
     "callout": [call(0.2, "MOLINHO…", "rosa")],
     "objetos": {"cm": {"id": "cama", "x": 2250, "y": 900, "z": 0, "depth": 0.7},
                 "g": gel(dp[0], x=1300, y=1000, depth=0.65, treme=0.6, mole=[(0.0, 0.0), (1.0, 1.0)], lid=1, boca=0.3)},
     "atores": {LA: {"x": 500, "turn": 0.3, "acoes": [{"t": 0.1, "do": "dance", "style": "agacha", "dur": "resto"}]},
                LU: {"x": 2100, "turn": -0.3, "acoes": [{"t": 0.2, "do": "dance", "style": "agacha", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_azul", "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}, "flash": True,
     "callout": [call(0.2, "DURINHO!", "azul")],
     "objetos": {"g": gel(dp[1], x=960, y=1060, depth=0.5, treme=0.0, mole=[(0.0, 1.0), (0.3, 0.0)], boca=0.0)},
     "atores": {LA: {"x": 380, "y": 1010, "depth": 1.0, "turn": 0.3, "acoes": [{"t": 0.1, "do": "estatua", "dur": "resto"}]},
                LU: {"x": 1540, "y": 1010, "depth": 1.0, "turn": -0.3, "acoes": [{"t": 0.1, "do": "estatua", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": SALA, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.1}, "tremor": [0.5],
     "callout": [call(0.2, "TREME A BARRIGA!", "laranja")],
     "objetos": {"g": gel(dp[2], x=1300, y=1000, depth=0.6, treme=1.0, boca=0.9),
                 "cx": obj("caixa_brinquedos", 1750, 930, 0.6, dp[2], pts={"carrinho": [(0.5, 1.0)]})},
     "atores": {LA: treme(330, 0.3), LU: treme(2200, -0.3, t=0.1), MA: treme(880, 0.3, t=0.2)}},
    {"linhas": 1, "cenario": GELO, "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15}, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "CONGELOU!", "azul"), call(round(dp[3] * 0.55, 2), "GELADINHO!", "azul")],
     "objetos": {"g": gel(dp[3], x=1300, y=1000, depth=0.65, treme=[(0.0, 1.0), (0.2, 0.0)], congela=[(0.0, 0.0), (0.35, 1.0)])},
     "atores": {LA: {"x": 500, "turn": 0.3, "acoes": [{"t": 0.15, "do": "estatua", "dur": "resto"}]},
                LU: {"x": 2100, "turn": -0.3, "acoes": [{"t": 0.15, "do": "estatua", "dur": "resto"}]}}},
]

# ───────── final: convite + tchau tremendo ─────────
R.partes["final#1"] = R.convite(COZ, gostou="GOSTOU DA GELATINA?", extra_casa={})
for p_ in R.partes["final#1"]:
    if not p_.get("camera"):
        p_["camera"] = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    elif isinstance(p_["camera"], dict) and "zoom_fim" not in p_["camera"]:
        p_["camera"]["zoom_fim"] = p_["camera"]["zoom"] + 0.08
R.partes["final#1"][0]["objetos"] = {"g": gel(3.0, x=1700, y=900, depth=0.5, treme=0.8, boca=0.6)}
R.partes["final#1"][2]["atores"]["mamae"]["x"] = 800                 # mamãe e Laurinha sem se cobrir na frente de casa
R.partes["final#1"][2]["atores"][LA]["x"] = 1800
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 2.4, "cenario": COZ, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["coracoes"],
     "callout": [call(0.2, "GELATINA!", "vermelho"), call(1.2, "TCHAU!", "amarelo")],
     "objetos": {"g": gel(2.4, x=1300, y=1040, depth=0.7, treme=0.8, boca=0.8),
                 "c": {**gato(2250, 2.4, y=1010, depth=0.45, lado=-1.0, miau=(1.0,)), "z": 4}},
     "atores": {VO: {"x": 320, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LA: {"x": 880, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LU: {"x": 1860, "turn": -0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]}}},
    {"seg": round(dfim - 2.4, 2), "cenario": COZ, "camera": {"x": 1300, "y": 760, "zoom": 1.5, "zoom_fim": 1.7}, "tremor": [0.2],
     "callout": [call(0.1, "TREMEU!", "vermelho")], "titulo": "a gelatina treme e pisca",
     "objetos": {"g": gel(dfim - 2.4, x=1300, y=1040, depth=0.7, treme=1.0, boca=[(0.0, 0.9), (1.2, 0.3)], lid=[(1.3, 1.0)]),
                 "c": {**gato(1750, dfim - 2.4, y=1010, depth=0.45, lado=-1.0, miau=(0.4,)), "z": 4}}},
]

R.salvar("Roteiro de 'Gelatina!' (take v1 cortado em 2:32, Laurinha, estilo E12, nota 4,7): a gelatina da vovó sai correndo "
         "pela casa e pelo jardim e quem olha treme junto (passo `treme`); 'pra cá / pra lá' em telas divididas; ponte "
         "molinho/durinho/congelou (cenário de gelo); banda na cozinha da vovó (A4). Gerado por scripts/roteiros/ep26_gelatina.py.")
