"""Roteiro verso a verso de 22 "Roda, Rodinha!" (take v1, 2:52, Laurinha, estilo E12, nota 4,8) → musicas/22_roda_rodinha/roteiro.json.

A roda que cresce: a Laurinha chama a turma de mãos dadas no JARDIM; entram o sapo e o pato (LAGOA), o grilo e o tatu
(CAMPO)… e quando entra o ELEFANTE a tela treme e cai todo mundo, buuu! Refrão: a roda gira e "quem tá tonto cai"
(todos sentam, os bichos com olho de espiral). Ponte de comandos (direita, esquerda, agacha, levanta). Telas divididas
(turma × bichos) e a BANDA da turma no SALÃO (Luisinho na bateria, Laurinha no sax/teclado) com os bichos na plateia.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep22_roda_rodinha.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import LA, LU, SALAO, Roteiro, call  # noqa: E402

R = Roteiro("ep22-roda-rodinha", "22_roda_rodinha", "laurinha")
JARDIM, LAGOA, CAMPO, CASA = "plano_jardim", "plano_lagoa", "plano_campo", "plano_casa_frente"
CAM = {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.18}


def bicho(bid, x, depth=0.7, pulos=0.0, d=4.0, cai=None, entra=None, y=930, extra=None):
    """Bicho da roda: pula no ritmo; `entra` = (t0, t1, x0) chega andando aos pulinhos; `cai` = t (cai tonto)."""
    ks = [{"t": 0.0, "pose": {"pulo": 0.0, "cai": 0.0}, "ease": "step"}]
    if pulos:
        ks += [{"t": round(j * pulos, 2), "pose": {"pulo": float(j % 2)}, "ease": "linear"} for j in range(1, int(d / pulos))]
    if entra:
        t0, t1, x0 = entra
        ks += [{"t": 0.0, "pose": {"x": x0}, "ease": "step"}, {"t": round(t1, 2), "pose": {"x": x}, "ease": "out", "in": round(t1 - t0, 2)}]
    if cai is not None:
        ks = [k for k in ks if k["t"] < cai - 0.05] + [{"t": round(cai, 2), "pose": {"cai": 1.0, "pulo": 0.0}, "ease": "step"}]
    ks += extra or []
    return {"id": bid, "x": x, "y": y, "z": 2, "depth": depth, "keys": ks}


def roda(t_cai=None, estilo="roda", perto=False):
    """Laurinha e Luisinho de mãos dadas na roda; caem sentados no 'cai'."""
    def ator(x, turn):
        ac = [{"t": 0.0, "do": "dance", "style": estilo, "dur": round(max(0.4, (t_cai or 99) - 0.1), 2)}]
        if t_cai is not None:
            ac += [{"t": round(t_cai, 2), "do": "sit"}, {"t": round(t_cai + 0.6, 2), "do": "ofegante" if turn < 0 else "laugh", "dur": "resto"}]
        return {"x": x, "turn": turn, "acoes": ac}
    return {LA: ator(1120, 0.25), LU: ator(1480, -0.25)} if perto else {LA: ator(850, 0.25), LU: ator(1750, -0.25)}   # perto: metade da tela


def bichos_roda(d, t_cai=None, xs=(450, 2150), ids=("sapo", "pato")):
    return {f"b{i}": bicho(b, x, pulos=0.45, d=d, cai=t_cai) for i, (b, x) in enumerate(zip(ids, xs))}


# ───────── intro ─────────
P = [{"seg": 2.3}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}]
T = R.tempos("intro#1", P)
(a0, a1, _), (b0, b1, vb), (c0, c1, vc), (d0, d1, _) = T
R.partes["intro"] = [
    {"seg": 2.3, "cenario": JARDIM, "camera": {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.08}, "titulo": "o jardim",
     "objetos": {"s": bicho("sapo", 600, pulos=0.45, d=2.3), "p": bicho("pato", 2000, pulos=0.5, d=2.3)},
     "atores": {LA: {"x": 1300, "turn": 0.0, "acoes": [{"t": 0.3, "do": "wave", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": JARDIM, "camera": CAM, "flash": True, "callout": [call(0.3, "RODA, RODINHA!", "rosa")],
     "objetos": bichos_roda(b1 - b0), "atores": roda()},
    R.dividida({"cenario": JARDIM, "camera": {"x": 1300, "y": 600, "zoom": 1.15, "zoom_fim": 1.22}, "atores": roda(perto=True)},
               {"cenario": CAMPO, "camera": {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.08},
                "objetos": {"g": bicho("grilo", 1050, pulos=0.45, d=c1 - c0), "t": bicho("tatu", 1550, pulos=0.5, d=c1 - c0)}},
               linhas=1, layout="diagonal"),
    {**R.banda(SALAO, d1 - d0, fx=["confete"]), "linhas": 1, "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")]},
]
R.partes["intro"][-1].pop("seg")


# ───────── verso: a roda cresce; o elefante entra e cai todo mundo ─────────
def verso(key, n):
    P = [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}]
    (a0, a1, va), (a2, a3, va2), (b0, b1, vb), (b2, b3, vb2), (c0, c1, vc), (d0, d1, vd), (e0, e1, ve), (f0, f1, vf) = R.tempos(key, P)
    tc = R.tp(f0, vf, "caiu", default=0.5)
    cen = JARDIM if n == 1 else CASA
    return [
        {"linhas": 1, "cenario": cen, "camera": CAM, "callout": [call(0.5, "VAMOS FAZER UMA RODA!", "rosa")],
         "atores": {LA: {"x": 1000, "turn": 0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]},
                    LU: {"x": 1650, "turn": -0.3, "acoes": [{"t": 0.3, "do": "pensar", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": cen, "camera": {"x": 1300, "y": 620, "zoom": 1.3, "zoom_fim": 1.38}, "callout": [call(0.4, "DÁ A MÃO!", "verde")],
         "atores": {LA: {"x": 1100, "turn": 0.3, "acoes": [{"t": 0.1, "do": "dance", "style": "roda", "dur": "resto"}]},
                    LU: {"x": 2300, "turn": -0.3, "acoes": [{"t": 0.0, "do": "walk", "to_x": 1550}, {"t": 1.3, "do": "dance", "style": "roda", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": cen, "camera": "close:laurinha", "callout": [call(0.4, "QUEM QUISER…", "amarelo")],
         "atores": {LA: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": cen, "camera": {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.2}, "callout": [call(0.4, "VEM RODAR!", "verde")],
         "atores": {LU: {"x": 1300, "turn": 0.0, "acoes": [{"t": 0.1, "do": "bacana", "dur": 1.0}, {"t": 1.2, "do": "dance", "style": "sapinho", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": LAGOA, "camera": {"x": 1300, "y": 640, "zoom": 1.2, "zoom_fim": 1.3}, "callout": [call(0.4, "O SAPO E O PATO!", "verde")],
         "objetos": {"s": bicho("sapo", 1000, entra=(0.1, 1.0, -300), pulos=0.4, d=c1 - c0),
                     "p": bicho("pato", 1600, entra=(0.3, 1.3, 2900), pulos=0.45, d=c1 - c0)},
         "atores": {LA: {"x": 2000, "turn": -0.35, "acoes": [{"t": 0.6, "do": "look_around", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 660, "zoom": 1.3, "zoom_fim": 1.4}, "callout": [call(0.4, "O GRILO E O TATU!", "amarelo")],
         "objetos": {"g": bicho("grilo", 1050, entra=(0.1, 1.0, -300), pulos=0.35, d=d1 - d0, depth=0.8),
                     "t": bicho("tatu", 1600, entra=(0.2, 1.2, 2900), pulos=0.5, d=d1 - d0, depth=0.8)}},
        # o elefante: chega pisando, a tela treme, todo mundo de olho arregalado
        {"linhas": 1, "cenario": JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}, "tremor": [0.5, 1.2],
         "callout": [call(0.5, "O ELEFANTE!", "roxo")],
         "objetos": {"e": bicho("elefante", 1650, entra=(0.0, 1.3, 2900), depth=0.75, extra=[{"t": 1.2, "pose": {"tromba": 1.0}, "ease": "out"}])},
         "atores": {LA: {"x": 650, "turn": 0.35, "expr": "surprised", "acoes": [{"t": 0.4, "do": "take", "strength": "shock"}]},
                    LU: {"x": 300, "turn": 0.4, "acoes": [{"t": 0.5, "do": "shock_reaction", "dur": "resto"}]}}},
        # caiu todo mundo, buuu!
        {"linhas": 1, "cenario": JARDIM, "camera": {"x": 1300, "y": 640, "zoom": 1.05, "zoom_fim": 1.15}, "tremor": [tc], "flash": True,
         "callout": [call(tc + 0.2, "BUUU!", "vermelho")],
         "objetos": {"e": bicho("elefante", 1900, depth=0.7, cai=tc), "s": bicho("sapo", 450, cai=tc + 0.05, depth=0.6),
                     "g": bicho("grilo", 2400, cai=tc + 0.1, depth=0.6)},
         "atores": {LA: {"x": 900, "turn": 0.3, "acoes": [{"t": round(max(0.05, tc - 0.05), 2), "do": "slip"}]},
                    LU: {"x": 1350, "turn": -0.2, "acoes": [{"t": round(tc, 2), "do": "slip"}]}}},
    ]


R.partes["verso#1"] = verso("verso#1", 1)
R.partes["verso#2"] = verso("verso#2", 2)
CORES = ["rosa", "verde", "azul", "laranja"]


# ───────── refrão: a roda gira; "quem tá tonto cai" ─────────
def refrao(n):
    P = [{"linhas": 2}, {"linhas": 2}, {"linhas": 2}, {"linhas": 2}]
    T = R.tempos(f"refrao#{n}", P)
    out = []
    for i, (t0, t1, v) in enumerate(T):
        d = t1 - t0
        tcai = R.tp(t0, v, "cai", default=None) if i % 2 == 1 else None
        if n >= 3 and i in (1, 3):                                    # a banda com os bichos na plateia
            p = R.banda(SALAO, d, teclado=(i == 3), fx=["confete"], cam={"x": 1300, "y": 620, "zoom": 1.0, "zoom_fim": 1.08})
            p.pop("seg")
            p["objetos"].update({"pl1": bicho("pato", 300, pulos=0.45, d=d, depth=0.55), "pl2": bicho("grilo", 2350, pulos=0.4, d=d, depth=0.55)})
            p.update({"linhas": 2, "callout": [call(0.3, "GIRA, GIRA!", "amarelo")]})
        elif i == 2:                                                   # tela dividida: a turma × os bichos girando
            p = R.dividida({"cenario": JARDIM, "camera": {"x": 1300, "y": 600, "zoom": 1.15, "zoom_fim": 1.25}, "atores": roda(estilo="twist", perto=True)},
                           {"cenario": [LAGOA, CAMPO, LAGOA, CAMPO][n - 1], "camera": {"x": 1300, "y": 640, "zoom": 1.1, "zoom_fim": 1.2},
                            "objetos": {"b1": bicho("sapo" if n % 2 else "grilo", 1050, pulos=0.35, d=d), "b2": bicho("pato" if n % 2 else "tatu", 1550, pulos=0.4, d=d)}},
                           linhas=2, layout="vertical" if n % 2 else "diagonal", callout=[call(0.3, "RODA, RODINHA!", CORES[n - 1])])
        else:
            cen = [JARDIM, CASA, SALAO, JARDIM][n - 1]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 600, "zoom": 1.05 if i == 0 else 1.2, "zoom_fim": 1.15 if i == 0 else 1.1},
                 "callout": [call(0.2, "RODA, RODINHA!", CORES[n - 1])], "atores": roda(t_cai=tcai, estilo="roda" if i == 0 else "lado"),
                 "objetos": bichos_roda(d, t_cai=tcai, ids=("sapo", "pato") if (n + i) % 2 else ("grilo", "tatu"))}
            if tcai is not None:
                p["callout"].append(call(tcai + 0.1, "CAIU!", "vermelho"))
            if i == 0:
                p["flash"] = True
        out.append(p)
    return out


for n in (1, 2, 3, 4):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos: "Bora, turminha!", "Laurinha e Luisinho!" e a banda ─────────
def intervalo(key, n):
    b, bl = R.bloco(key)
    D = b["e"] - b["s"]
    if not bl:
        return [R.banda(SALAO, D, teclado=True, fx=["confete"], extra={"vovozinho": {"x": 300, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}]}})]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = 3.6
    return [{"linhas": 1, "seg": p1, "cenario": JARDIM if n == 1 else LAGOA, "camera": "close:laurinha", "callout": [call(0.2, "BORA, TURMINHA!", "rosa")],
             "atores": {LA: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
            {"linhas": 1, "seg": p2, "cenario": "danca_raios_rosa" if n == 1 else "danca_xadrez_verde", "fx": ["confete"],
             "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")],
             "atores": {LA: {"x": 560, "y": 1010, "depth": 1.0, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura", "dur": "resto"}]},
                        LU: {"x": 1360, "y": 1010, "depth": 1.0, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "chute", "dur": "resto"}]}}},
            {**R.banda(SALAO, D - p1 - p2, teclado=(n == 2), fx=["notas"],
                       extra={"vovo": {"x": 280, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco", "dur": "resto"}]}}), "titulo": "a banda"}]


R.partes["intervalo#1"] = intervalo("intervalo#1", 1)
R.partes["intervalo#2"] = intervalo("intervalo#2", 2)
R.partes["intervalo#3"] = intervalo("intervalo#3", 3)


# ───────── ponte: direita, esquerda, agacha, levanta ─────────
def ponte(key, n):
    (a0, a1, va), (b0, b1, vb) = R.tempos(key, [{"linhas": 2}, {"linhas": 2}])
    tl = R.tp(b0, vb, "levanta", default=1.0)
    cen = CAMPO if n == 1 else LAGOA
    return [
        {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 620, "zoom": 1.15, "zoom_fim": 1.25}, "callout": [call(0.1, "PRA DIREITA!", "azul"), call(1.4, "PRA ESQUERDA!", "verde")],
         "objetos": bichos_roda(a1 - a0, ids=("grilo", "tatu") if n == 1 else ("sapo", "pato")),
         "atores": {LA: {"x": 850, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": "resto"}]},
                    LU: {"x": 1750, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": "resto"}]}}},
        {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 640, "zoom": 1.2, "zoom_fim": 1.1}, "flash": False,
         "callout": [call(0.1, "AGACHA…", "roxo"), call(tl + 0.05, "QUE FESTA!", "amarelo")], "fx": ["confete"],
         "objetos": bichos_roda(b1 - b0, ids=("grilo", "tatu") if n == 1 else ("sapo", "pato")),
         "atores": {LA: {"x": 850, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "agacha", "dur": round(max(0.4, tl - 0.1), 2)},
                                                          {"t": round(tl, 2), "do": "jump", "dur": 0.8}]},
                    LU: {"x": 1750, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "agacha", "dur": round(max(0.4, tl - 0.1), 2)},
                                                           {"t": round(tl + 0.05, 2), "do": "jump", "dur": 0.8}]}}},
    ]


R.partes["ponte#1"] = ponte("ponte#1", 1)
R.partes["ponte#2"] = ponte("ponte#2", 2)

R.partes["final#1"] = R.convite(JARDIM, gostou="GOSTOU DA RODA?", extra_casa={"e": bicho("elefante", 2150, depth=0.55, extra=[{"t": 0.3, "pose": {"tromba": 1.0}, "ease": "out"}])})
(f0, f1, vf), = R.tempos("final#2", [{"linhas": 1}])
R.partes["final#2"] = [
    {"linhas": 1, "seg": 5.0, "cenario": JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}, "fx": ["coracoes"],
     "callout": [call(0.6, "TCHAU!", "amarelo")],
     "objetos": {"e": bicho("elefante", 1300, depth=0.7, extra=[{"t": 0.3, "pose": {"tromba": 0.0}}, {"t": 0.9, "pose": {"tromba": 1.0}, "ease": "out"},
                                                                 {"t": 2.0, "pose": {"tromba": 0.3}}, {"t": 2.8, "pose": {"tromba": 1.0}}]),
                 "s": bicho("sapo", 350, pulos=0.45, d=5.0, depth=0.55), "p": bicho("pato", 2300, pulos=0.5, d=5.0, depth=0.55)},
     "atores": {LA: {"x": 750, "turn": 0.3, "acoes": [{"t": 0.0, "do": "abraco", "dur": 1.4}, {"t": 1.5, "do": "wave", "dur": "resto"}]},
                LU: {"x": 1850, "turn": -0.3, "acoes": [{"t": 0.0, "do": "sorriso", "dur": 1.4}, {"t": 1.5, "do": "wave", "dur": "resto"}]}}},
    {"seg": round(f1 - f0 - 5.0, 2), "cenario": CAMPO, "camera": {"x": 1300, "y": 600, "zoom": 1.15, "zoom_fim": 1.0}, "fx": ["confete"],
     "titulo": "a roda dá tchau",
     "objetos": {"e": bicho("elefante", 1300, depth=0.6, pulos=0.6, d=f1 - f0 - 5.0), "g": bicho("grilo", 400, pulos=0.4, d=f1 - f0 - 5.0, depth=0.55),
                 "t": bicho("tatu", 2200, pulos=0.5, d=f1 - f0 - 5.0, depth=0.55)},
     "atores": {LA: {"x": 800, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 3.0}, {"t": 3.2, "do": "fly", "dur": 1.4, "to_x": -300, "to_y": 300}]},
                LU: {"x": 1800, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 3.0}, {"t": 3.3, "do": "fly", "dur": 1.4, "to_x": 2900, "to_y": 300}]}}},
]

R.salvar("Roteiro de 'Roda, Rodinha!' (take v1 de 19/11/2026, 2:52, Laurinha, estilo E12, nota 4,8): a roda que cresce com sapo, pato, "
         "grilo, tatu e o elefante que derruba todo mundo; refrão girando com 'quem tá tonto cai'; telas divididas (turma × bichos) e a "
         "banda da turma no salão. Gerado por scripts/roteiros/ep22_roda_rodinha.py.")
