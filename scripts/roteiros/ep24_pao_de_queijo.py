"""Roteiro verso a verso de 24 "Pão de Queijo" (take v1 cortado para 2:53, Luisinho, estilo E12, nota 4,8)
→ musicas/24_pao_de_queijo/roteiro.json.

A COZINHA da vovó mineira: a fornada sai fumegando; o Luisinho dá uma mordida grande e o queijo ESTICA, estica… vai parar
no TELHADO (rua), passa pela LUA (céu) e volta! Refrão: "Estica, estica e não sai!" (o fio vai para lá e para cá) e "Mais um,
vovó!" (a vovó traz o tabuleiro). Ponte de comandos: estica pro lado, pro outro, pra cima… NHAC! Telas divididas e a BANDA.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep24_pao_de_queijo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import LA, LU, SALAO, Roteiro, call  # noqa: E402

R = Roteiro("ep24-pao-de-queijo", "24_pao_de_queijo", "luisinho")
COZ, RUA, CEU, SALA, JARDIM = "plano_cozinha", "plano_casa_frente", "plano_ceu", "plano_sala", "plano_jardim"
VO = "vovo"
CAM = {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.18}
MESA_Y = 930 - 240 * 1.3


def pao(x=1300, y=930, depth=0.8, z=3, estica=None, dir_=None, mordido=0.0, vapor=1.0, extra=None):
    """estica = [(t, valor)], dir_ = [(t, direção em voltas)]: o fio de queijo vai e volta."""
    ks = [{"t": 0.0, "pose": {"estica": 0.0, "dir": 0.0, "mordido": mordido, "vapor": vapor, "onda": 0.0}, "ease": "step"}]
    for t, v in (estica or []):
        ks.append({"t": round(t, 2), "pose": {"estica": v}, "ease": "out"})
    for t, v in (dir_ or []):
        ks.append({"t": round(t, 2), "pose": {"dir": v}, "ease": "inout"})
    ks += extra or []
    return {"id": "pao_queijo", "x": x, "y": y, "z": z, "depth": depth, "keys": ks}


def tabuleiro(x=1300, y=930, depth=0.8, z=2, some=None):
    ks = [{"t": 0.0, "pose": {"quantos": 1.0, "vapor": 1.0}, "ease": "step"}]
    if some is not None:
        ks.append({"t": round(some, 2), "pose": {"quantos": 0.4}, "ease": "linear"})
    return {"id": "tabuleiro", "x": x, "y": y, "z": z, "depth": depth, "keys": ks}


def gato(x, y=930, depth=0.5, lado=1.0, miau=(1.2,), assusta=None, d=8.0):
    """o gato da vovó: abana o rabo, mia e se assusta quando o queijo estica."""
    ks = [{"t": 0.0, "pose": {"lado": lado, "rabo": 0.0, "miau": 0.0, "assusta": 0.0}, "ease": "step"}]
    ks += [{"t": round(0.5 * j, 2), "pose": {"rabo": float(j % 2)}, "ease": "inout"} for j in range(1, int(d / 0.5))]
    for t in miau:
        ks += [{"t": round(t, 2), "pose": {"miau": 1.0}, "ease": "out"}, {"t": round(t + 0.5, 2), "pose": {"miau": 0.0}, "ease": "in"}]
    if assusta is not None:
        ks += [{"t": round(assusta, 2), "pose": {"assusta": 1.0}, "ease": "back"}]
    return {"id": "gato", "x": x, "y": y, "z": 2, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def pulando(obj, y0, alto=70, per=0.45, d=8.0):
    """o objeto pula no ritmo (pão de queijo dançando)."""
    obj = dict(obj)
    obj["keys"] = list(obj.get("keys", [])) + [{"t": round(per * j, 2), "pose": {"y": y0 - alto * (j % 2)}, "ease": "out" if j % 2 else "in"}
                                               for j in range(int(d / per))]
    obj["keys"].sort(key=lambda k: k["t"])
    obj["y"] = y0
    return obj


def sol(x=2150, y=230):
    return {"id": "sol", "x": x, "y": y, "z": 0, "depth": 0.5,
            "keys": [{"t": 0.0, "pose": {"giro": 0.0, "boca": 0.0}, "ease": "step"}, {"t": 0.8, "pose": {"boca": 1.0}, "ease": "out"},
                     {"t": 6.0, "pose": {"giro": 1.0}, "ease": "linear"}]}


def mesa():
    return {"id": "mesa", "x": 1300, "y": 930, "z": 1, "depth": 1.3}


# ───────── intro: a fornada sai do forno ─────────
R.partes["intro"] = [
    {"seg": 3.0, "cenario": COZ, "camera": {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.08}, "titulo": "a fornada",
     "objetos": {"m": mesa(), "t": tabuleiro(1300, MESA_Y, depth=0.5), "g": gato(650, miau=(1.4,))},
     "atores": {VO: {"x": 2000, "turn": -0.3, "acoes": [{"t": 0.3, "do": "point", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 640, "zoom": 1.45, "zoom_fim": 1.55}, "flash": True,
     "callout": [call(0.3, "PÃO DE QUEIJO, UAI!", "laranja")], "objetos": {"p": pao(1300, depth=0.95)}},
    {"linhas": 1, "cenario": COZ, "camera": CAM, "objetos": {"m": mesa(), "t": tabuleiro(1300, MESA_Y, depth=0.5)},
     "atores": {LA: {"x": 150, "turn": 0.35, "acoes": [{"t": 0.0, "do": "run", "to_x": 600, "dur": 0.9}, {"t": 1.0, "do": "jump", "dur": 0.8}, {"t": 1.9, "do": "dance", "style": "cintura", "dur": "resto"}]},
                LU: {"x": 2450, "turn": -0.35, "acoes": [{"t": 0.0, "do": "run", "to_x": 2000, "dur": 0.9}, {"t": 1.0, "do": "take", "dur": 1.0}, {"t": 2.1, "do": "dance", "style": "joelho", "dur": "resto"}]}}},
    {**R.banda(SALAO, 4.0, fx=["confete"]), "linhas": 1, "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")]},
    {**R.banda(SALAO, 5.0, teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.2, "zoom_fim": 1.1},
               extra={VO: {"x": 2350, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco", "dur": "resto"}]}}), "titulo": "a banda"},
    {"seg": 0.0, "cenario": COZ, "camera": {"x": 1300, "y": 580, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["confete"], "titulo": "a cozinha dança",
     "objetos": {"m": mesa(), "t": tabuleiro(1300, MESA_Y, depth=0.5), "g": gato(1800, depth=0.45, lado=-1.0, miau=(2.0,)),
                 "p": pulando(pao(1300, depth=0.35), MESA_Y - 150, alto=90)},
     "atores": {LA: {"x": 380, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "chute", "dur": "resto"}]},
                LU: {"x": 980, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "sapinho", "dur": "resto"}]},
                VO: {"x": 2100, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}]}}},
]
R.partes["intro"][3].pop("seg")


# ───────── verso: a vovó de Minas; a mordida; o queijo estica até o telhado e a lua ─────────
def verso(key, n):
    T = R.tempos(key, [{"linhas": 1}] * 8)
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd), (e0, e1, ve), (f0, f1, vf), (g0, g1, vg), (h0, h1, vh) = T
    tm = R.tp(e0, ve, "mordida", default=1.0)
    return [
        {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 600, "zoom": 1.25, "zoom_fim": 1.35}, "callout": [call(0.4, "A VOVÓ DE MINAS!", "verde")],
         "objetos": {"g": gato(1720, depth=0.45, lado=-1.0, miau=(0.9,))},
         "atores": {VO: {"x": 1300, "turn": 0.0, "acoes": [{"t": 0.1, "do": "wave", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": COZ, "camera": CAM, "objetos": {"m": mesa(), "t": tabuleiro(1300, MESA_Y, depth=0.55), "g": gato(2350, depth=0.45, lado=-1.0, miau=(1.0,))},
         "atores": {VO: {"x": 2000, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]},
                    LA: {"x": 600, "turn": 0.3, "acoes": [{"t": 0.1, "do": "pensar", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 620, "zoom": 1.6, "zoom_fim": 1.75}, "callout": [call(0.4, "REDONDINHO!", "laranja"), call(1.3, "QUENTINHO!", "vermelho")],
         "objetos": {"p": pao(1300, depth=0.95)}},
        # tela dividida: a vovó orgulhosa × o Luisinho com água na boca
        R.dividida({"cenario": COZ, "camera": {"x": 1300, "y": 600, "zoom": 1.2, "zoom_fim": 1.3},
                    "objetos": {"t": tabuleiro(1600, 760, depth=0.45)},
                    "atores": {VO: {"x": 1150, "turn": 0.2, "acoes": [{"t": 0.1, "do": "bacana", "dur": "resto"}]}}},
                   {"cenario": SALA if n == 1 else JARDIM, "camera": {"x": 1300, "y": 600, "zoom": 1.2, "zoom_fim": 1.3},
                    "objetos": {"p": pulando(pao(1550, depth=0.4), 560, alto=60)},
                    "atores": {LU: {"x": 1150, "turn": 0.15, "acoes": [{"t": 0.1, "do": "cheguei", "dur": "resto"}]}}},
                   linhas=1, layout="vertical" if n == 1 else "diagonal", callout=[call(0.3, "PRA MIM!", "azul")]),
        {"linhas": 1, "cenario": COZ, "camera": {"x": 1350, "y": 620, "zoom": 1.35, "zoom_fim": 1.45}, "callout": [call(tm + 0.2, "NHAC!", "vermelho")],
         "objetos": {"g": gato(1850, depth=0.45, lado=-1.0, miau=(), assusta=tm + 0.2)},
         "atores": {LU: {"x": 1250, "turn": 0.3, "segura": "pao_queijo", "acoes": [{"t": round(max(0.05, tm - 0.25), 2), "do": "comer", "item": "pao_queijo", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 520, "zoom": 1.1, "zoom_fim": 1.0}, "callout": [call(0.4, "ESTICOU!", "amarelo")],
         "objetos": {"p": pao(1300, depth=0.8, mordido=1.0, estica=[(0.2, 0.0), (f1 - f0 - 0.2, 1.0)], extra=[{"t": round(f1 - f0 - 0.1, 2), "pose": {"onda": 1.0}, "ease": "linear"}]),
                     "g": gato(1900, depth=0.45, lado=-1.0, miau=(), assusta=0.3)},
         "atores": {LU: {"x": 700, "turn": 0.3, "expr": "surprised", "acoes": [{"t": 0.3, "do": "shock_reaction", "dur": "resto"}]}}},
        # foi parar lá no telhado
        {"linhas": 1, "cenario": RUA, "camera": {"x": 1300, "y": 420, "zoom": 1.1, "zoom_fim": 1.2}, "callout": [call(0.5, "NO TELHADO!", "laranja")],
         "objetos": {"p": pao(1300, depth=1.0, mordido=1.0, estica=[(0.0, 0.7), (g1 - g0 - 0.2, 1.0)], dir_=[(0.0, -0.03), (g1 - g0 - 0.2, 0.03)],
                             extra=[{"t": round(g1 - g0 - 0.1, 2), "pose": {"onda": 2.0}, "ease": "linear"}]),
                     "n": {"id": "nuvem", "x": 600, "y": 200, "z": 0, "depth": 0.5, "keys": [{"t": 0.0, "pose": {"boca": 0.0, "x": 500}, "ease": "step"},
                                                                                           {"t": 0.6, "pose": {"boca": 1.0}, "ease": "out"},
                                                                                           {"t": 4.0, "pose": {"x": 800}, "ease": "linear"}]},
                     "po": {"id": "poste", "x": 2250, "y": 930, "z": 1, "depth": 0.7, "keys": [{"t": 0.0, "pose": {"alerta": 0.0}, "ease": "step"}, {"t": 0.5, "pose": {"alerta": 1.0}, "ease": "out"}]}},
         "atores": {"vovozinho": {"x": 1900, "turn": -0.2, "expr": "surprised", "acoes": [{"t": 0.1, "do": "look_around" if n == 1 else "shock_reaction", "dur": "resto"}]}}},
        # passou a lua e voltou
        {"linhas": 1, "cenario": CEU, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["estrelas"], "callout": [call(0.4, "PASSOU A LUA!", "roxo"),
                                                                                                                    call(h1 - h0 - 1.4, "E VOLTOU!", "verde")],
         "objetos": {"c": {"id": "cometa", "x": 300, "y": 250, "z": 0, "depth": 0.5, "keys": [{"t": 0.0, "pose": {"x": 300, "y": 220}, "ease": "step"},
                                                                                         {"t": 3.0, "pose": {"x": 2300, "y": 380}, "ease": "linear"}]},
                     "lua": {"id": "lua", "x": 1700, "y": 620, "z": 1, "depth": 0.6, "keys": [{"t": 0.0, "pose": {"boca": 0.0, "brilho": 1.0}}, {"t": 0.8, "pose": {"boca": 1.0}}]},
                     "p": pao(1100, y=1350, depth=1.2, mordido=1.0, estica=[(0.0, 1.0), (h1 - h0 - 1.2, 1.0), (h1 - h0 - 0.2, 0.2)],
                              dir_=[(0.0, 0.05), (h1 - h0 - 1.3, 0.12)], extra=[{"t": round(h1 - h0 - 0.1, 2), "pose": {"onda": 2.5}, "ease": "linear"}])}},
    ]


R.partes["verso#1"] = verso("verso#1", 1)
R.partes["verso#2"] = verso("verso#2", 2)
CORES = ["laranja", "verde", "rosa"]


# ───────── refrão: estica e não sai / mais um, vovó! ─────────
def refrao(n):
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * 4)
    out = []
    for i, (t0, t1, v) in enumerate(T):
        d = t1 - t0
        if n == 3 and i in (1, 3):
            p = R.banda(SALAO, d, teclado=(i == 3), fx=["confete"], cam={"x": 1300, "y": 620, "zoom": 1.0, "zoom_fim": 1.08},
                        extra={VO: {"x": 2350, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}]}})
            p.pop("seg")
            p.update({"linhas": 2, "callout": [call(0.3, "UAI, UAI!", "amarelo")]})
        elif i == 2:                                                # tela dividida: a Laurinha e o Luisinho, cada um com o seu fio de queijo
            def painel(who, cen, dx):
                return {"cenario": cen, "camera": {"x": 1300, "y": 600, "zoom": 1.15, "zoom_fim": 1.25},
                        "objetos": {"p": pao(1300 + dx, depth=0.7, mordido=1.0, estica=[(0.2, 0.7)], dir_=[(0.2, 0.15 * (1 if dx < 0 else -1)), (d - 0.3, -0.15 * (1 if dx < 0 else -1))],
                                            extra=[{"t": round(d - 0.1, 2), "pose": {"onda": 2.0}, "ease": "linear"}])},
                        "atores": {who: {"x": 1300 - dx, "turn": 0.25 if dx > 0 else -0.25, "acoes": [{"t": 0.1, "do": "dance", "style": R.estilo(), "dur": "resto"}]}}}
            p = R.dividida(painel(LA, COZ, 250), painel(LU, SALA, -250), linhas=2, layout="vertical" if n % 2 else "diagonal",
                           callout=[call(0.3, "ESTICA, ESTICA!", "amarelo")])
        elif i % 2 == 0:                                            # pão de queijo, uai! estica, estica e não sai!
            p = {"linhas": 2, "cenario": COZ if n != 2 else JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15},
                 "callout": [call(0.2, "PÃO DE QUEIJO, UAI!", CORES[n - 1]), call(d * 0.55, "NÃO SAI!", "vermelho")],
                 "objetos": {"p": pao(1550, depth=0.8, mordido=1.0, estica=[(0.1, 0.5), (d * 0.5, 0.9)], dir_=[(0.1, -0.2), (d * 0.5, 0.2), (d - 0.2, -0.1)],
                                     extra=[{"t": round(d - 0.1, 2), "pose": {"onda": 3.0}, "ease": "linear"}]),
                             "g": gato(2250, depth=0.45, lado=-1.0, miau=(0.6,), assusta=d * 0.5) if n != 2 else sol()},
                 "atores": {LU: {"x": 900, "turn": 0.3, "acoes": [{"t": 0.1, "do": "puxar", "dur": "resto"}]}}}
            if n == 2:
                p["atores"]["vovozinho"] = {"x": 2250, "turn": -0.3, "acoes": [{"t": 0.1, "do": "laugh", "dur": "resto"}]}
            if i == 0:
                p["flash"] = True
        else:                                                       # mais um, vovó! vai, vai!
            tv = R.tp(t0, v, "vovó", "vovo", default=d * 0.5)
            p = {"linhas": 2, "cenario": COZ, "camera": CAM, "callout": [call(tv + 0.1, "MAIS UM, VOVÓ!", "verde")],
                 "objetos": {"m": mesa(), "t": tabuleiro(1300, MESA_Y, depth=0.5, some=d - 0.2), "g": gato(1700, y=930, depth=0.4, lado=-1.0, miau=(tv + 0.3,))},
                 "atores": {VO: {"x": 2050, "turn": -0.3, "acoes": [{"t": 0.1, "do": "entregar", "item": "pao_queijo", "dur": 1.2}, {"t": 1.4, "do": "laugh", "dur": "resto"}]},
                            LU: {"x": 550, "turn": 0.35, "acoes": [{"t": round(max(0.1, tv - 0.1), 2), "do": "receber", "item": "pao_queijo", "dur": 0.8},
                                                                  {"t": round(min(d - 0.5, tv + 0.9), 2), "do": "dance", "style": R.estilo(), "dur": "resto"}]}}}
        out.append(p)
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos ─────────
def intervalo(key, n):
    b, bl = R.bloco(key)
    D = b["e"] - b["s"]
    if not bl:
        return [R.banda(SALAO, D, teclado=True, fx=["confete"], extra={VO: {"x": 2350, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura", "dur": "resto"}]}})]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = 3.6 if D - p1 - 3.6 >= 2.0 else round(D - p1, 2)
    out = [{"linhas": 1, "seg": p1, "cenario": COZ if n == 1 else JARDIM, "camera": "close:luisinho", "callout": [call(0.2, "ZUM-ZUM, QUE MASSA!", "azul")],
            "objetos": {"p": pulando(pao(1650, depth=0.4), 620, alto=50)},
            "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
           {"linhas": 1, "seg": p2, "cenario": "danca_raios_laranja" if n == 1 else "danca_bolinhas_verde", "fx": ["confete"],
            "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")], "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.1},
            "objetos": {"p1": pulando(pao(300, depth=0.35), 760, alto=80), "p2": pulando(pao(1650, depth=0.35), 760, alto=80, per=0.5)},
            "atores": {LA: {"x": 560, "y": 1010, "depth": 1.0, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "sapinho", "dur": "resto"}]},
                       LU: {"x": 1360, "y": 1010, "depth": 1.0, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "chute", "dur": "resto"}]}}}]
    resto = D - p1 - p2
    if resto >= 1.0:
        s3 = round(resto / 2, 2)
        out += [{**R.banda(SALAO, s3, fx=["notas"]), "titulo": "a banda"},
                {**R.banda(SALAO, round(resto - s3, 2), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.25, "zoom_fim": 1.15},
                           extra={VO: {"x": 2350, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco", "dur": "resto"}]}}), "titulo": "a vovó dança"}]
    return out


R.partes["intervalo#1"] = intervalo("intervalo#1", 1)
R.partes["intervalo#2"] = intervalo("intervalo#2", 2)
R.partes["intervalo#3"] = intervalo("intervalo#3", 3)

# ───────── ponte: estica pro lado, pro outro, pra cima… NHAC! ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4)
dirs = [-0.22, 0.22, 0.0]
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": [COZ, JARDIM, SALA][i], "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.12},
     "callout": [call(0.2, ["PRO LADO!", "PRO OUTRO!", "PRA CIMA!"][i], ["azul", "verde", "laranja"][i])],
     "objetos": {"p": pao(1300, depth=0.85, mordido=1.0, estica=[(0.0, 0.3), (T[i][1] - T[i][0] - 0.3, 1.0)], dir_=[(0.0, dirs[i])],
                         extra=[{"t": round(T[i][1] - T[i][0] - 0.1, 2), "pose": {"onda": 1.5}, "ease": "linear"}])},
     "objetos_extra": [{"g": gato(1900 if dirs[i] > 0 else 700, depth=0.45, miau=(1.0,), assusta=1.4)}, {"s": sol()}, {}][i],
     "atores": {LU: {"x": 2050 if dirs[i] <= 0 else 550, "turn": -0.3 if dirs[i] <= 0 else 0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]},
                **({LA: {"x": 550, "turn": 0.3, "acoes": [{"t": 0.2, "do": "fly", "dur": 1.2}, {"t": 1.5, "do": "jump", "dur": "resto"}]}} if i == 2 else {})}}
    for i in range(3)] + [
    {"linhas": 1, "cenario": COZ, "camera": "close:luisinho", "callout": [call(0.1, "NHAC!", "vermelho"), call(1.0, "HUM, QUE BOM!", "verde")],
     "objetos": {"g": gato(1750, depth=0.45, lado=-1.0, miau=(1.1,))},
     "atores": {LU: {"x": 1300, "segura": "pao_queijo", "acoes": [{"t": 0.0, "do": "comer", "item": "pao_queijo", "dur": 1.1}, {"t": 1.15, "do": "sorriso", "dur": "resto"}]}}},
]

for p_ in R.partes["ponte#1"]:
    p_.setdefault("objetos", {}).update(p_.pop("objetos_extra", {}))

R.partes["final#1"] = R.convite(COZ, gostou="GOSTOU DO PÃO DE QUEIJO?", extra_casa={"t": tabuleiro(2150, depth=0.5)})
(f0, f1, vf), = R.tempos("final#2", [{"linhas": 1}])
R.partes["final#2"] = [
    {"linhas": 1, "seg": 5.0, "cenario": COZ, "camera": {"x": 1300, "y": 580, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"], "callout": [call(0.6, "TCHAU!", "amarelo"), call(2.2, "UAI!", "laranja")],
     "objetos": {"m": mesa(), "t": tabuleiro(1300, MESA_Y, depth=0.5)},
     "atores": {VO: {"x": 2050, "turn": -0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LA: {"x": 550, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LU: {"x": 850, "turn": 0.25, "acoes": [{"t": 0.0, "do": "abraco", "dur": 1.4}, {"t": 1.5, "do": "wave", "dur": "resto"}]}}},
    {"seg": round(f1 - f0 - 5.0, 2), "cenario": COZ, "camera": {"x": 1300, "y": 640, "zoom": 1.6, "zoom_fim": 1.75}, "titulo": "o último pão de queijo",
     "objetos": {"p": pao(1300, depth=0.95, extra=[{"t": 1.0, "pose": {"mordido": 1.0}, "ease": "step"}])}},
]

for p_ in R.partes["final#1"]:
    if not p_.get("camera"):
        p_["camera"] = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    elif isinstance(p_["camera"], dict) and "zoom_fim" not in p_["camera"]:
        p_["camera"]["zoom_fim"] = p_["camera"]["zoom"] + 0.08
R.partes["final#1"][0]["objetos"] = {"p": pulando(pao(1650, depth=0.4), 620, alto=50)}
for planos in R.partes.values():
    for p_ in planos:
        if p_.get("cenario") == SALAO and "bat" in p_.get("objetos", {}):
            p_["objetos"]["p"] = pulando(pao(1250, depth=0.35), 600, alto=80)

R.salvar("Roteiro de 'Pão de Queijo' (take v1 cortado para 2:53, Luisinho, estilo E12, nota 4,8): a cozinha da vovó mineira, a mordida e o "
         "queijo que estica até o telhado e passa pela lua; refrão 'estica e não sai' e 'mais um, vovó!'; ponte de comandos; telas "
         "divididas e a banda. Gerado por scripts/roteiros/ep24_pao_de_queijo.py.")
