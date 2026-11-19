"""Roteiro verso a verso de 23 "Pula, Coelhinho!" (take v1 cortado para 2:56, Luisinho, estilo E12, nota 4,8)
→ musicas/23_pula_coelhinho/roteiro.json.

A caça aos ovinhos: o COELHINHO da Páscoa esconde ovinhos coloridos nos lugares mais engraçados — chapéu do VOVÔ, meia
do Luisinho (tela dividida), geladeira da COZINHA e tapete da SALA (tela dividida) e… no capacete! Refrão: o coelhinho
pula pela casa e a turma corre atrás ("Cadê o ovinho? Ai, ai!"). Ponte: narizinho, orelha, pula com os dois pés, ACHOU
(o ovinho brilha e vai para a cesta). Intervalos com a BANDA da turma. Personagens 1,45×, animação A3.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep23_pula_coelhinho.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import LA, LU, SALAO, Roteiro, call  # noqa: E402

R = Roteiro("ep23-pula-coelhinho", "23_pula_coelhinho", "luisinho")
JARDIM, COZINHA, SALA, CASA, CAMPO = "plano_jardim", "plano_cozinha", "plano_sala", "plano_casa_frente", "plano_campo"
CAM = {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.18}
VO = "vovozinho"


def coelho(x=1500, depth=0.65, pulos=None, d=4.0, extra=None, pose=None, entra=None):
    ks = [{"t": 0.0, "pose": {"pulo": 0.0, "nariz": 0.0}, "ease": "step"}]
    if pulos:
        ks += [{"t": round(j * pulos, 2), "pose": {"pulo": float(j % 2), "nariz": float(j % 3) * 0.3}, "ease": "linear"} for j in range(1, int(d / pulos))]
    if entra:
        t0, t1, x0 = entra
        ks += [{"t": 0.0, "pose": {"x": x0}, "ease": "step"}, {"t": round(t1, 2), "pose": {"x": x}, "ease": "linear", "in": round(t1 - t0, 2)}]
    ks += extra or []
    return {"id": "coelhinho", "x": x, "y": 930, "z": 2, "depth": depth, "pose": pose or {}, "keys": ks}


def ovo(x, y, cor, achou=None, pulos=None, d=3.0, depth=0.7, z=5):
    ks = [{"t": 0.0, "pose": {"cor": float(cor), "achou": 0.0, "pulo": 0.0}, "ease": "step"}]
    if pulos:
        ks += [{"t": round(j * pulos, 2), "pose": {"pulo": float(j % 2)}, "ease": "linear"} for j in range(1, int(d / pulos))]
    if achou is not None:
        ks += [{"t": round(max(0.05, achou - 0.05), 2), "pose": {"achou": 0.0}}, {"t": round(achou + 0.3, 2), "pose": {"achou": 1.0}, "ease": "out"}]
    return {"id": "ovinho", "x": x, "y": y, "z": z, "depth": depth, "keys": ks}


def corre_atras(d, t0=0.3):
    return {LA: {"x": 300, "turn": 0.4, "acoes": [{"t": t0, "do": "run", "to_x": 900}, {"t": round(min(d - 0.5, t0 + 1.4), 2), "do": "look_around", "dur": "resto"}]},
            LU: {"x": 100, "turn": 0.4, "acoes": [{"t": t0 + 0.2, "do": "run", "to_x": 650}, {"t": round(min(d - 0.5, t0 + 1.6), 2), "do": "dance", "style": R.estilo(), "dur": "resto"}]}}


# ───────── intro ─────────
P = [{"seg": 2.2}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}]
(a0, a1, _), (b0, b1, vb), (c0, c1, vc), (d0, d1, _) = R.tempos("intro#1", P)
R.partes["intro"] = [
    {"seg": 2.2, "cenario": JARDIM, "camera": {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.08}, "titulo": "o coelhinho chega",
     "objetos": {"c": coelho(1400, entra=(0.0, 2.0, 2900), pulos=0.4, d=2.2), "cesta": {"id": "cesta", "x": 700, "y": 930, "z": 2, "depth": 0.7}}},
    {"linhas": 1, "cenario": JARDIM, "camera": CAM, "flash": True, "callout": [call(0.3, "PULA, COELHINHO!", "rosa")],
     "objetos": {"c": coelho(1300, pulos=0.4, d=b1 - b0, depth=0.75)},
     "atores": {LA: {"x": 600, "turn": 0.35, "acoes": [{"t": 0.2, "do": "dance", "style": "sapinho", "dur": "resto"}]},
                LU: {"x": 2000, "turn": -0.35, "acoes": [{"t": 0.2, "do": "dance", "style": "joelho", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 640, "zoom": 1.3, "zoom_fim": 1.4},
     "objetos": {"c": coelho(1300, pulos=0.35, d=c1 - c0, depth=0.8, extra=[{"t": 0.4, "pose": {"piscar": 1.0}, "ease": "step"}, {"t": 0.8, "pose": {"piscar": 0.0}, "ease": "step"}])}},
    {**R.banda(SALAO, 4.0, fx=["confete"]), "linhas": 1, "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")]},
    {"seg": round(d1 - d0 - 4.0, 2), "cenario": JARDIM, "camera": {"x": 1300, "y": 620, "zoom": 1.1, "zoom_fim": 1.2}, "titulo": "escondendo os ovinhos",
     "objetos": {"c": coelho(1300, entra=(0.0, 2.5, 300), pulos=0.4, d=d1 - d0 - 4.0, depth=0.7),
                 "o1": ovo(700, 940, 0, pulos=0.5, d=d1 - d0 - 4.0, depth=0.55), "o2": ovo(1900, 940, 1, pulos=0.45, d=d1 - d0 - 4.0, depth=0.55)}},
]


# ───────── verso: os esconderijos engraçados ─────────
def verso(key, n):
    T = R.tempos(key, [{"linhas": 1}] * 8)
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd), (e0, e1, ve), (g0, g1, vg), (h0, h1, vh), (f0, f1, vf) = T
    w = lambda t0, v, *al, default=0.8: R.tp(t0, v, *al, default=default)
    t_chap, t_meia, t_gel, t_tap, t_cap = w(c0, vc, "chapéu", "chapeu"), w(d0, vd, "meia"), w(e0, ve, "geladeira"), w(g0, vg, "tapete"), w(f0, vf, "capacete")
    base = JARDIM if n == 1 else SALA
    return [
        {"linhas": 1, "cenario": base, "camera": CAM, "callout": [call(0.4, "O COELHINHO DA PÁSCOA!", "rosa")],
         "objetos": {"c": coelho(1300, pulos=0.45, d=a1 - a0, depth=0.75), "cesta": {"id": "cesta", "x": 2000, "y": 930, "z": 2, "depth": 0.6,
                     "keys": [{"t": 0.0, "pose": {"cheia": 1.0}, "ease": "step"}, {"t": round(a1 - a0 - 0.3, 2), "pose": {"cheia": 0.2}, "ease": "linear"}]}},
         "atores": {LU: {"x": 550, "turn": 0.4, "acoes": [{"t": 0.3, "do": "point", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": base, "camera": {"x": 1300, "y": 640, "zoom": 1.35, "zoom_fim": 1.45}, "callout": [call(0.5, "ESCONDEU!", "roxo")],
         "objetos": {"c": coelho(1300, depth=0.85, extra=[{"t": 0.3, "pose": {"ovo": 1.0}, "ease": "step"}, {"t": 1.6, "pose": {"ovo": 0.0, "piscar": 1.0}, "ease": "step"}])}},
        {"linhas": 1, "cenario": SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.3}, "callout": [call(t_chap + 0.2, "NO CHAPÉU DO VOVÔ!", "amarelo")],
         "objetos": {"o": ovo(1300, 330, 0, achou=t_chap, depth=0.8)},
         "atores": {VO: {"x": 1300, "turn": 0.1, "expr": "surprised", "acoes": [{"t": round(t_chap, 2), "do": "take", "strength": "surprised"}]}}},
        {"linhas": 1, "cenario": CASA, "camera": {"x": 1300, "y": 650, "zoom": 1.25, "zoom_fim": 1.35}, "callout": [call(t_meia + 0.2, "NA MEIA!", "azul")],
         "objetos": {"o": ovo(1360, 920, 1, achou=t_meia, depth=0.7)},
         "atores": {LU: {"x": 1250, "turn": 0.1, "acoes": [{"t": round(max(0.1, t_meia - 0.1), 2), "do": "jump", "dur": 0.8},
                                                         {"t": round(t_meia + 0.9, 2), "do": "laugh", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": COZINHA, "camera": {"x": 900, "y": 600, "zoom": 1.2, "zoom_fim": 1.3}, "callout": [call(t_gel + 0.2, "NA GELADEIRA!", "verde")],
         "objetos": {"o": ovo(900, 560, 2, achou=t_gel, depth=0.8, pulos=0.5, d=e1 - e0)},
         "atores": {LA: {"x": 1350, "turn": -0.3, "acoes": [{"t": round(t_gel, 2), "do": "shock_reaction", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": SALA, "camera": {"x": 1300, "y": 760, "zoom": 1.3, "zoom_fim": 1.4}, "callout": [call(t_tap + 0.2, "NO TAPETE!", "laranja")],
         "objetos": {"o": ovo(1300, 960, 3, achou=t_tap, depth=0.7, pulos=0.4, d=g1 - g0)},
         "atores": {LU: {"x": 1800, "turn": -0.3, "acoes": [{"t": 0.2, "do": "sneak", "to_x": 1600}, {"t": round(t_tap + 0.1, 2), "do": "cheguei", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": base, "camera": "close:luisinho", "callout": [call(0.6, "ADIVINHA…", "roxo")],
         "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "pensar", "dur": "resto"}]}}},
        {"linhas": 1, "cenario": base, "camera": {"x": 1300, "y": 560, "zoom": 1.3, "zoom_fim": 1.4}, "flash": True,
         "callout": [call(t_cap + 0.2, "NO CAPACETE!", "vermelho")],
         "objetos": {"o": ovo(1300, 330, 4, achou=t_cap, depth=0.75), "c": coelho(2250, pulos=0.4, d=f1 - f0, depth=0.6)},
         "atores": {LU: {"x": 1300, "turn": 0.0, "expr": "surprised", "acoes": [{"t": round(t_cap, 2), "do": "take", "strength": "shock"},
                                                                               {"t": round(t_cap + 0.8, 2), "do": "laugh", "dur": "resto"}]}}},
    ]


R.partes["verso#1"] = verso("verso#1", 1)
R.partes["verso#2"] = verso("verso#2", 2)
CORES = ["rosa", "verde", "azul"]


# ───────── refrão: o coelhinho pula pela casa; "Cadê o ovinho? Ai, ai!" ─────────
def refrao(n):
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * 4)
    out = []
    cens = [(JARDIM, SALA), (COZINHA, CASA), (SALAO, CAMPO)][n - 1]
    for i, (t0, t1, v) in enumerate(T):
        d = t1 - t0
        if n == 3 and i in (1, 3):
            p = R.banda(SALAO, d, teclado=(i == 3), fx=["confete"], cam={"x": 1300, "y": 620, "zoom": 1.0, "zoom_fim": 1.08})
            p.pop("seg")
            p["objetos"]["c"] = coelho(2350, pulos=0.45, d=d, depth=0.5)
            p.update({"linhas": 2, "callout": [call(0.3, "PULA, PULA!", "amarelo")]})
        elif i % 2 == 0:                                                # pula, coelhinho: o coelho passa pulando, a turma corre atrás
            p = {"linhas": 2, "cenario": cens[i // 2], "camera": {"x": 1300, "y": 600, "zoom": 1.05, "zoom_fim": 1.15},
                 "callout": [call(0.2, "PULA, COELHINHO!", CORES[n - 1])],
                 "objetos": {"c": coelho(2200, entra=(0.0, d - 0.2, 1100), pulos=0.35, d=d, depth=0.7),
                             "o1": ovo(1500, 950, n, pulos=0.4, d=d, depth=0.55), "o2": ovo(2500, 950, n + 1, pulos=0.5, d=d, depth=0.55)},
                 "atores": corre_atras(d)}
            if i == 0:
                p["flash"] = True
        elif i == 1:                                                    # TELA DIVIDIDA: cada um procura num lugar
            ta = R.tp(t0, v, "cadê", "cade", default=d * 0.5)
            p = R.dividida({"cenario": COZINHA, "camera": {"x": 1300, "y": 620, "zoom": 1.2, "zoom_fim": 1.3},
                            "objetos": {"o": ovo(1650, 900, n, pulos=0.45, d=d, depth=0.6)},
                            "atores": {LA: {"x": 1200, "turn": 0.2, "acoes": [{"t": 0.1, "do": "look_around", "dur": "resto"}]}}},
                           {"cenario": SALA, "camera": {"x": 1300, "y": 620, "zoom": 1.2, "zoom_fim": 1.3},
                            "objetos": {"o": ovo(950, 950, n + 2, pulos=0.5, d=d, depth=0.6)},
                            "atores": {LU: {"x": 1400, "turn": -0.2, "acoes": [{"t": 0.2, "do": "pensar", "dur": round(max(0.4, ta + 0.5), 2)},
                                                                             {"t": round(ta + 0.7, 2), "do": "shake_fist", "dur": "resto"}]}}},
                           linhas=2, layout="vertical" if n % 2 else "diagonal", callout=[call(ta + 0.1, "CADÊ O OVINHO?", "roxo")])
        else:                                                           # cadê o ovinho? ai, ai!
            ta = R.tp(t0, v, "cadê", "cade", default=d * 0.5)
            p = {"linhas": 2, "cenario": cens[i // 2], "camera": "close:laurinha" if (n + i) % 2 else {"x": 1300, "y": 620, "zoom": 1.25, "zoom_fim": 1.15},
                 "callout": [call(ta + 0.1, "CADÊ O OVINHO?", "roxo")],
                 "atores": {LA: {"x": 1000 if (n + i) % 2 == 0 else 1300, "turn": 0.2, "acoes": [{"t": 0.1, "do": "look_around", "dur": round(max(0.4, ta + 0.6), 2)},
                                                                                             {"t": round(ta + 0.8, 2), "do": "shake_fist", "dur": "resto"}]}}}
            if (n + i) % 2 == 0:
                p["atores"][LU] = {"x": 1700, "turn": -0.3, "acoes": [{"t": 0.2, "do": "pensar", "dur": "resto"}]}
                p["objetos"] = {"o": ovo(2300, 900, n + i, pulos=0.5, d=d, depth=0.6)}
        out.append(p)
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos ─────────
def intervalo(key, n):
    b, bl = R.bloco(key)
    D = b["e"] - b["s"]
    if not bl:
        s1 = round(D / 2, 2)
        return [R.banda(SALAO, s1, teclado=True, fx=["confete"]),
                {**R.dividida({"cenario": SALAO, "camera": {"x": 1300, "y": 620, "zoom": 1.15, "zoom_fim": 1.25}, "fx": ["confete"],
                               "atores": {LA: {"x": 1150, "turn": 0.2, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura", "dur": "resto"}]},
                                          VO: {"x": 1550, "turn": -0.2, "acoes": [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}]}}},
                              {"cenario": CAMPO, "camera": {"x": 1300, "y": 640, "zoom": 1.2, "zoom_fim": 1.3},
                               "objetos": {"c": coelho(1300, pulos=0.4, d=D - s1, depth=0.75), "o": ovo(1750, 940, 2, pulos=0.45, d=D - s1, depth=0.55)}},
                              layout="diagonal"), "seg": round(D - s1, 2), "titulo": "festa"}]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = 3.6 if D - p1 - 3.6 >= 2.0 else round(D - p1, 2)          # intervalo curto: sem a banda
    out = [{"linhas": 1, "seg": p1, "cenario": JARDIM if n == 1 else COZINHA, "camera": "close:luisinho", "callout": [call(0.2, "QUE MASSA!", "azul")],
            "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
           {"linhas": 1, "seg": p2, "cenario": "danca_raios_rosa" if n == 1 else "danca_bolinhas_verde", "fx": ["confete"],
            "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")],
            "atores": {LA: {"x": 560, "y": 1010, "depth": 1.0, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "pezinho", "dur": "resto"}]},
                       LU: {"x": 1360, "y": 1010, "depth": 1.0, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "chute", "dur": "resto"}]}}}]
    resto = D - p1 - p2
    if resto < 1.0:
        return out
    if n == 1:                                                          # intervalo longo: banda + o coelhinho mexendo o narizinho
        s3 = round(resto * 0.55, 2)
        out += [{**R.banda(SALAO, round(s3 / 2, 2), teclado=True, fx=["notas"], extra={VO: {"x": 2350, "turn": -0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco", "dur": "resto"}]}}), "titulo": "a banda"},
                {**R.banda(SALAO, round(s3 - round(s3 / 2, 2), 2), fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.25, "zoom_fim": 1.15},
                           extra={"vovo": {"x": 300, "turn": 0.35, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura", "dur": "resto"}]}}), "titulo": "solo de sax"},
                {"seg": round(resto - s3, 2), "cenario": CAMPO, "camera": {"x": 1300, "y": 600, "zoom": 1.4, "zoom_fim": 1.6}, "titulo": "o narizinho",
                 "callout": [call(round(resto - s3 - 1.0, 2), "MEXE O NARIZINHO!", "rosa")],
                 "objetos": {"c": coelho(1300, depth=0.9, extra=[{"t": round(j * 0.25, 2), "pose": {"nariz": j * 0.25}, "ease": "linear"} for j in range(int((resto - s3) / 0.25))])}}]
    else:
        out += [{**R.banda(SALAO, resto, fx=["notas"]), "titulo": "a banda"}]
    return out


R.partes["intervalo#1"] = intervalo("intervalo#1", 1)
R.partes["intervalo#2"] = intervalo("intervalo#2", 2)
R.partes["intervalo#3"] = intervalo("intervalo#3", 3)


# ───────── ponte: orelha, pula com os dois pés, achou! ─────────
(a0, a1, va), (b0, b1, vb), (c0, c1, vc) = R.tempos("ponte#1", [{"linhas": 1}] * 3)
tach = R.tp(c0, vc, "achou", default=0.3)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 560, "zoom": 1.3, "zoom_fim": 1.4}, "callout": [call(0.3, "BALANÇA A ORELHA!", "rosa")],
     "objetos": {"c": coelho(1300, depth=0.85, extra=[{"t": 0.0, "pose": {"orelha": 0.0}, "ease": "step"}, {"t": round(a1 - a0, 2), "pose": {"orelha": 3.0}, "ease": "linear"}])}},
    {"linhas": 1, "cenario": CAMPO, "camera": CAM, "callout": [call(0.3, "PULA COM OS DOIS PÉS!", "verde")],
     "objetos": {"c": coelho(1300, pulos=0.35, d=b1 - b0, depth=0.7)},
     "atores": {LA: {"x": 600, "turn": 0.35, "acoes": [{"t": 0.2, "do": "dance", "style": "sapinho", "dur": "resto"}]},
                LU: {"x": 2000, "turn": -0.35, "acoes": [{"t": 0.2, "do": "dance", "style": "pulinho", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": JARDIM, "camera": {"x": 1300, "y": 640, "zoom": 1.2, "zoom_fim": 1.3}, "fx": ["estrelas"], "callout": [call(tach + 0.1, "ACHOU!", "amarelo")],
     "objetos": {"o": ovo(1300, 820, 2, achou=tach, depth=0.8), "cesta": {"id": "cesta", "x": 1900, "y": 930, "z": 2, "depth": 0.6, "keys": [{"t": 0.0, "pose": {"cheia": 0.6}, "ease": "step"}, {"t": round(tach + 0.6, 2), "pose": {"cheia": 1.0}, "ease": "out"}]}},
     "atores": {LU: {"x": 700, "turn": 0.35, "acoes": [{"t": round(tach, 2), "do": "cheguei", "dur": "resto"}]}}},
]

R.partes["final#1"] = R.convite(JARDIM, gostou="GOSTOU DO COELHINHO?", extra_casa={"c": coelho(2150, depth=0.55, pulos=0.45, d=3.0)})
(f0, f1, vf), = R.tempos("final#2", [{"linhas": 1}])
R.partes["final#2"] = [
    {"linhas": 1, "seg": 4.0, "cenario": JARDIM, "camera": {"x": 1300, "y": 580, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(0.6, "TCHAU!", "amarelo"), call(2.0, "HOP!", "rosa")],
     "objetos": {"c": coelho(1300, pulos=0.45, d=f1 - f0, depth=0.7, pose={"ovo": 1.0}),
                 "cesta": {"id": "cesta", "x": 2050, "y": 930, "z": 3, "depth": 0.65}},
     "atores": {LA: {"x": 550, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LU: {"x": 850, "turn": 0.25, "acoes": [{"t": 0.0, "do": "abraco", "dur": 1.4}, {"t": 1.5, "do": "wave", "dur": "resto"}]}}},
    {"seg": round(f1 - f0 - 4.0, 2), "cenario": JARDIM, "camera": {"x": 1300, "y": 760, "zoom": 1.6, "zoom_fim": 1.75}, "fx": ["estrelas"], "titulo": "a cesta cheia",
     "callout": [call(0.4, "HOP!", "rosa")],
     "objetos": {"cesta": {"id": "cesta", "x": 1300, "y": 930, "z": 2, "depth": 0.8, "keys": [{"t": 0.0, "pose": {"cheia": 0.4}, "ease": "step"}, {"t": 1.5, "pose": {"cheia": 1.0}, "ease": "out"}]},
                 "c": coelho(1800, pulos=0.4, d=f1 - f0 - 4.0, depth=0.7)}},
]

R.salvar("Roteiro de 'Pula, Coelhinho!' (take v1 cortado para 2:56, Luisinho, estilo E12, nota 4,8): o coelhinho esconde os ovinhos (chapéu "
         "do vovô, meia, geladeira, tapete, capacete) em telas divididas; refrão de pula-pula e 'cadê o ovinho?'; ponte do narizinho e da "
         "orelha; a banda da turma nos intervalos. Gerado por scripts/roteiros/ep23_pula_coelhinho.py.")
