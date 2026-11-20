"""Roteiro verso a verso de 27 "Careta de Limão!" (take v1 cortado de 3:26 para 2:50, Laurinha, estilo E13, nota 4,8)
→ musicas/27_careta_de_limao/roteiro.json.

O QUINTAL DA VOVÓ com o pé de limão (prop novo `limoeiro`: balança e derruba limão). A Laurinha pega um limãozinho,
morde e faz a CARETA DE AZEDO (expressão nova `azedo`: olhos "> <", boca torta, antenas arrepiadas; ação `careta`).
"Fiz uma careta / o olho fechou / a boca entortou / o cabelo arrepiou" = um detalhe da careta por plano (close no olho,
na boca, nas antenas). O LIMÃO COM CARINHA (prop novo `limao_cara`) também faz careta. Refrão: "mostra a careta,
vizinho!" — os vizinhos (joaninha e formiguinha por cima da cerquinha, a mamãe, o vovô) mostram a careta; no espelho do
banheiro e no sapo da lagoa. Ponte: o vovô e a vovó mordem e fazem careta; "agora é a sua vez" chama a criança.
Banda no quintal, debaixo do limoeiro (nada de salão lilás). Final: limonada de canudinho e o sorriso de volta.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep27_careta_de_limao.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import LA, LU, Roteiro, call  # noqa: E402

R = Roteiro("ep27-careta-de-limao", "27_careta_de_limao", "laurinha")
JARDIM, COZ, SALA, CASA, CAMPO = "plano_jardim", "plano_cozinha", "plano_sala", "plano_casa_frente", "plano_campo"
PARQUE, LAGOA, BANHO, ESCOLA = "plano_parque", "plano_lagoa", "plano_banheiro", "plano_escola"
PALCO = JARDIM                    # 19/11: a banda toca no quintal da vovó, debaixo do limoeiro (nada de salão lilás)
VO, VZ, MA, JO, FO = "vovo", "vovozinho", "mamae", "joaninha", "formiguinha"


def dur(T):
    return [round(t1 - t0, 2) for t0, t1, _ in T]


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


def arvore(d, x=2250, y=960, depth=0.55, cai=None, quantos=1.0, z=0):
    """o pé de limão da vovó: a copa balança sempre; `cai` = instante em que um limão cai do galho."""
    pts = {"cai": [(cai, 0.0), (cai + 0.7, 1.0)]} if cai is not None else None
    depth = round(depth / 0.8, 3)                      # o desenho é × 0,8 (cabe no quadro do nível): mesmo tamanho na tela
    return obj("limoeiro", x, y, depth, d, z=z, fixo={"quantos": quantos, "cai": 0.0}, lin={"balanco": (0.0, d * 0.5)}, pts=pts)


def limao(d, x=1300, y=980, depth=0.6, careta=None, pulo=None, boca=0.4, z=4):
    """o limão com carinha: `careta` = instante em que fica azedo (treme); `pulo` = instantes dos pulinhos."""
    pts = {}
    if careta is not None:
        pts["careta"] = [(careta, 1.0)]
    if pulo:
        pts["pulo"] = [v for t in pulo for v in ((t, 1.0), (t + 0.3, 0.0))]
    return obj("limao_cara", x, y, depth, d, z=z, fixo={"boca": boca, "careta": 0.0, "pulo": 0.0}, lin={"fase": (0.0, d)}, pts=pts)


def nuvem(d, x=500, y=430):
    return obj("nuvem", x, y, 0.35, d, z=0, lin={"x": (x, x + 260)})


def sol(d):
    return obj("sol", 2250, 200, 0.5, d, z=0, pts={"boca": [(0.6, 1.0)]}, lin={"giro": (0.0, 0.5)})


def gato(x, d, y=1010, depth=0.45, lado=1.0, miau=(0.8,), assusta=None):
    ks = [{"t": 0.0, "pose": {"lado": lado, "rabo": 0.0, "miau": 0.0, "assusta": 0.0}, "ease": "step"}]
    ks += [{"t": round(0.4 * j, 2), "pose": {"rabo": float(j % 2)}, "ease": "inout"} for j in range(1, int(d / 0.4))]
    for t in miau:
        ks += [{"t": round(t, 2), "pose": {"miau": 1.0}, "ease": "out"}, {"t": round(t + 0.45, 2), "pose": {"miau": 0.0}, "ease": "in"}]
    if assusta is not None:
        ks.append({"t": round(assusta, 2), "pose": {"assusta": 1.0}, "ease": "back"})
    return {"id": "gato", "x": x, "y": y, "z": 4, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def careta(x, turn=0.0, t=0.1, item="", volta=0, dur_="resto", **kw):
    """ator fazendo a CARETA DE AZEDO (com `item`='limao' morde antes)."""
    ac = {"t": t, "do": "careta", "dur": dur_}
    if item:
        ac["item"] = item
    if volta:
        ac["volta"] = 1
    return {"x": x, "turn": turn, "acoes": [ac], **kw}


def danca(x, estilo, turn=0.0, t=0.1, **kw):
    return {"x": x, "turn": turn, "acoes": [{"t": t, "do": "dance", "style": estilo, "dur": "resto"}], **kw}


def cerca(x=1300):
    return {"id": "cerquinha", "x": x, "y": 960, "z": 2, "depth": 1.0}


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1, "seg": 2.6}, {"seg": 3.2}, {"seg": 0.0}])
d = dur(T)
R.partes["intro"] = [
    {"linhas": 1, "cenario": JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.2}, "titulo": "o quintal da vovó",
     "callout": [call(0.4, "CARETA DE LIMÃO!", "verde")],
     "objetos": {"a": arvore(d[0], x=650, depth=0.6), "l": limao(d[0], x=1600, careta=round(d[0] * 0.5, 2), pulo=(0.4,)), "s": sol(d[0])},
     "atores": {LA: {"x": 2600, "turn": -0.3, "acoes": [{"t": 0.0, "do": "sneak", "to_x": 2150, "dur": 2.0},
                                                       {"t": round(d[0] * 0.55, 2), "do": "shock_reaction", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": JARDIM, "camera": "close:laurinha", "flash": True, "callout": [call(0.3, "UI!", "amarelo")],
     "objetos": {"s": sol(d[1])}, "atores": {LA: careta(1300, 0.0, t=0.1)}},
    {"linhas": 1, "seg": 2.6, "cenario": CASA, "camera": {"x": 1300, "y": 560, "zoom": 1.1, "zoom_fim": 1.2},
     "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")], "fx": ["confete"], "objetos": {"n": nuvem(2.6, 300)},
     "atores": {LA: {"x": 900, "turn": 0.25, "acoes": [{"t": 0.1, "do": "jump", "dur": 0.8}, {"t": 1.0, "do": "dance", "style": "chute", "dur": "resto"}]},
                LU: {"x": 1700, "turn": -0.25, "acoes": [{"t": 0.2, "do": "jump", "dur": 0.8}, {"t": 1.1, "do": "dance", "style": "sapinho", "dur": "resto"}]}}},
    {**R.banda(PALCO, 3.2, fx=["notas"]), "titulo": "a banda debaixo do limoeiro"},
    {**R.banda(PALCO, max(0.6, d[4]), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.2, "zoom_fim": 1.1}),
     "titulo": "teclado e bateria"},
]
R.partes["intro"][3]["objetos"]["a"] = arvore(3.2, x=2350, depth=0.5)
R.partes["intro"][4]["objetos"]["l"] = limao(max(0.6, d[4]), x=2250, y=960, depth=0.4, pulo=(0.5, 1.5))


# ───────── verso: no quintal da vovó… mordi… fiz uma careta, o olho fechou, a boca entortou, o cabelo arrepiou ─────────
def verso(key, n):
    T = R.tempos(key, [{"linhas": 1}] * 8)
    d = dur(T)
    eu, outro = (LA, LU) if n == 1 else (LU, LA)
    out = [
        # No quintal da vovó
        {"linhas": 1, "cenario": JARDIM if n == 1 else CAMPO, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08},
         "callout": [call(0.4, "O QUINTAL DA VOVÓ!", "verde")],
         "objetos": {"a": arvore(d[0], x=2200, depth=0.55), "n": nuvem(d[0], 400), "s": sol(d[0])},
         "atores": {VO: {"x": 1650, "turn": -0.3, "acoes": [{"t": 0.1, "do": "cheguei", "dur": "resto"}]},
                    LA: {"x": 100, "turn": 0.3, "acoes": [{"t": 0.0, "do": "run" if n == 1 else "walk", "to_x": 450, "dur": 1.0},
                                                          {"t": 1.1, "do": "jump", "dur": "resto"}]},
                    LU: {"x": 0, "turn": 0.3, "acoes": [{"t": 0.2, "do": "run", "to_x": 1150, "dur": 1.0}, {"t": 1.3, "do": "laugh", "dur": "resto"}]}}},
        # Tem um pé de limão — a copa balança
        {"linhas": 1, "cenario": JARDIM if n == 1 else CAMPO, "camera": {"x": 1300, "y": 380, "zoom": 1.3, "zoom_fim": 1.42},
         "callout": [call(0.3, "PÉ DE LIMÃO!", "verde")],
         "objetos": {"a": arvore(d[1], x=1300, y=1000, depth=0.65), "s": sol(d[1])}},
        # Eu peguei um limãozinho — o limão cai e o pequeno pega
        {"linhas": 1, "cenario": JARDIM if n == 1 else CAMPO, "camera": {"x": 1300, "y": 540, "zoom": 1.05, "zoom_fim": 1.15},
         "callout": [call(0.6, "PEGUEI!", "amarelo")],
         "objetos": {"a": arvore(d[2], x=1000, depth=0.6, cai=0.0, quantos=0.9), "n": nuvem(d[2], 1900)},
         "atores": {eu: {"x": 1500, "turn": -0.3, "acoes": [{"t": 0.1, "do": "grab", "dur": 0.6},
                                                            {"t": 0.8, "do": "segurar", "item": "limao", "pose": "alto"}]},
                    outro: {"x": 2150, "turn": -0.3, "acoes": [{"t": 0.1, "do": "pensar" if n == 1 else "shock_reaction", "dur": "resto"}]}}},
        # E mordi com emoção… — close: morde e fica azedo
        {"linhas": 1, "cenario": JARDIM if n == 1 else CAMPO, "camera": f"close:{eu}", "callout": [call(0.5, "NHAC!", "laranja")],
         "objetos": {"s": sol(d[3])}, "atores": {eu: careta(1300, 0.1, t=0.0, item="limao")}},
        # Fiz uma careta — tela dividida: a criança × o limão com carinha
        R.dividida({"cenario": JARDIM if n == 1 else CAMPO, "camera": {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.35},
                    "objetos": {"a": arvore(d[4], x=2350, depth=0.45)}, "atores": {eu: careta(1300, 0.15, t=0.0)}},
                   {"cenario": "danca_raios_amarelo" if n == 1 else "danca_bolinhas_verde", "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.08},
                    "objetos": {"l": limao(d[4], x=960, y=1000, depth=0.8, careta=0.2)}},
                   linhas=1, layout="vertical" if n == 1 else "diagonal", callout=[call(0.3, "CARETA!", "verde")]),
        # O olho fechou — close bem perto no rosto
        {"linhas": 1, "cenario": JARDIM if n == 1 else BANHO, "camera": f"close:{eu}", "callout": [call(0.2, "O OLHO FECHOU!", "azul")],
         "objetos": {"s": sol(d[5])} if n == 1 else {"e": obj("espelho", 1650, 640, 0.8, d[5], z=0, pts={"brilho": [(0.3, 1.0)]})},
         "atores": {eu: {"x": 1300, "turn": -0.1, "expr": "azedo", "acoes": [{"t": 0.0, "do": "careta", "dur": "resto"}]}}},
        # A boca entortou — tela dividida: o outro também morde
        R.dividida({"cenario": COZ if n == 1 else SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.35},
                    "objetos": {"l": limao(d[6], x=1750, y=1000, depth=0.4, careta=0.3)},
                    "atores": {outro: careta(1300, -0.15, t=0.0, item="limao")}},
                   {"cenario": JARDIM if n == 1 else CAMPO, "camera": {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.35},
                    "atores": {eu: careta(1300, 0.15, t=0.0)}},
                   linhas=1, layout="diagonal" if n == 1 else "vertical", callout=[call(0.3, "BOCA TORTA!", "rosa")]),
        # E o cabelo arrepiou! — plano aberto, todo mundo treme de azedo
        {"linhas": 1, "cenario": JARDIM if n == 1 else CAMPO, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.12},
         "tremor": [round(d[7] * 0.3, 2)], "callout": [call(0.2, "ARREPIOU!", "vermelho")], "fx": ["estrelas"],
         "objetos": {"a": arvore(d[7], x=2300, depth=0.5), "c": gato(1950, d[7], lado=-1.0, assusta=0.3), "s": sol(d[7])},
         "atores": {eu: careta(500, 0.3, t=0.0), VO: {"x": 1500, "turn": -0.3, "acoes": [{"t": 0.3, "do": "laugh", "dur": "resto"}]},
                    outro: {"x": 1000, "turn": 0.3, "acoes": [{"t": 0.2, "do": "slip", "dur": "resto"}]}}},
    ]
    if n == 2:                                                    # 2º verso: na roça do vovô, com o pato e a cerquinha
        out[0]["atores"][VZ] = out[0]["atores"].pop(VO)
        out[0]["objetos"]["pt"] = obj("pato", 2450, 960, 0.5, d[0], pts={"quem": [(0.5, 1.0), (1.0, 0.0)], "asas": [(0.5, 1.0)]})
        out[2]["objetos"]["ce"] = cerca(400)
        out[7]["atores"] = {eu: careta(500, 0.3, t=0.0), VZ: {"x": 1500, "turn": -0.3, "acoes": [{"t": 0.3, "do": "laugh", "dur": "resto"}]},
                            outro: {"x": 1000, "turn": 0.3, "acoes": [{"t": 0.2, "do": "fall", "to_y": 930, "dur": "resto"}]}}
        out[7]["objetos"] = {"a": arvore(d[7], x=2300, depth=0.5), "s": sol(d[7]),
                             "pt": obj("pato", 1950, 980, 0.5, d[7], pts={"quem": [(0.3, 1.0), (0.8, 0.0)], "pulo": [(0.3, 1.0), (0.6, 0.0)]})}
    return out


R.partes["verso#1"] = verso("verso#1", 1)
R.partes["verso#2"] = verso("verso#2", 2)


# ───────── refrão: careta de limão! ui, que azedinho! / careta de limão! mostra a careta, vizinho! ─────────
CORES = ["verde", "amarelo", "laranja"]


def refrao(n):
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * 4)
    out = []
    for i, (t0, t1, _) in enumerate(T):
        d = round(t1 - t0, 2)
        if n == 3 and i in (1, 3):
            p = R.banda(PALCO, d, teclado=(i == 3), fx=["confete"], cam={"x": 1300, "y": 620, "zoom": 1.05, "zoom_fim": 1.12})
            p.pop("seg")
            p.update({"linhas": 2, "callout": [call(0.3, "CARETA DE LIMÃO!", "verde")]})
            p["objetos"]["l"] = limao(d, x=2300 if i == 1 else 250, y=960, depth=0.4, careta=round(d * 0.5, 2), pulo=(0.4,))
        elif i == 0:                                              # careta de limão! ui, que azedinho! — a turma × o limão
            cen = {1: JARDIM, 2: COZ, 3: PARQUE}[n]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15}, "fx": ["estrelas"],
                 "callout": [call(0.2, "CARETA DE LIMÃO!", CORES[n - 1]), call(round(d * 0.5, 2), "UI, QUE AZEDINHO!", "amarelo")],
                 "objetos": {"l": limao(d, x=1300, y=1010, depth=0.6, careta=round(d * 0.45, 2), pulo=(0.3,))}
                            | ({1: {"a": arvore(d, x=2450, depth=0.45)}, 2: {"m": {"id": "mesa", "x": 2350, "y": 930, "z": 1, "depth": 0.9}},
                                3: {"p": obj("pipa", 2250, 520, 0.4, d, z=0, fixo={"rabiola": 1.0}, lin={"balanco": (0.0, d * 1.2)}),
                                    "n": nuvem(d, 350)}}[n]),
                 "atores": {LA: careta(500, 0.3, t=round(d * 0.4, 2), item="limao"), LU: careta(2050 if n != 2 else 1900, -0.3, t=round(d * 0.45, 2), item="limao")}}
            if n == 1:
                p["flash"] = True
        elif i == 1:                                              # mostra a careta, vizinho! — os vizinhos por cima da cerca
            if n == 1:
                p = {"linhas": 2, "cenario": JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08},
                     "callout": [call(round(d * 0.4, 2), "MOSTRA A CARETA, VIZINHO!", "laranja")],
                     "objetos": {"ce": cerca(1300), "a": arvore(d, x=2450, depth=0.45), "s": sol(d)},
                     "atores": {JO: careta(1000, 0.2, t=round(d * 0.45, 2), z=1), FO: careta(1650, -0.2, t=round(d * 0.5, 2), z=1),
                                LA: {"x": 350, "turn": 0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}}
            else:
                p = {"linhas": 2, "cenario": LAGOA, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08},
                     "callout": [call(round(d * 0.4, 2), "MOSTRA A CARETA, VIZINHO!", "laranja")],
                     "objetos": {"sp": obj("sapo", 1300, 990, 0.6, d, z=4, pts={"croac": [(0.5, 1.0), (1.2, 0.0)], "pulo": [(round(d * 0.5, 2), 1.0), (round(d * 0.5 + 0.4, 2), 0.0)]}),
                                 "n": nuvem(d, 400)},
                     "atores": {LU: careta(500, 0.3, t=round(d * 0.4, 2)), MA: careta(2100, -0.3, t=round(d * 0.5, 2))}}
        elif i == 2:                                              # tela dividida: a careta no espelho × o vizinho
            p = R.dividida({"cenario": BANHO if n != 2 else ESCOLA, "camera": {"x": 1300, "y": 540, "zoom": 1.2, "zoom_fim": 1.3},
                            "objetos": {"e": obj("espelho", 1300, 640, 0.8, d, z=0, pts={"brilho": [(0.5, 1.0)]})} if n != 2 else {},
                            "atores": {(LA if n != 2 else LU): careta(1300, 0.1, t=0.2)}},
                           {"cenario": JARDIM if n != 2 else CAMPO, "camera": {"x": 1300, "y": 560, "zoom": 1.15, "zoom_fim": 1.25},
                            "objetos": {"l": limao(d, x=1850, y=1000, depth=0.45, careta=0.6)},
                            "atores": {(JO if n == 1 else VZ if n == 2 else FO): careta(1200, -0.1, t=0.4)}},
                           linhas=2, layout="diagonal" if n % 2 else "vertical", callout=[call(0.3, "UI, QUE AZEDINHO!", CORES[n - 1])])
        else:                                                     # mostra a careta! todo mundo de careta, tremendo
            cen = {1: SALA, 2: ESCOLA}[n]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.05}, "tremor": [round(d * 0.5, 2)],
                 "fx": ["confete"], "callout": [call(round(d * 0.4, 2), "MOSTRA A CARETA!", "vermelho")],
                 "objetos": {"l": limao(d, x=1300, y=1040, depth=0.55, careta=0.3), "c": gato(1680, d, lado=-1.0, assusta=round(d * 0.5, 2))}
                            | ({"cx": obj("caixa_brinquedos", 2550, 930, 0.7, d, pts={"carrinho": [(0.6, 1.0)]})} if n == 1 else {"n": nuvem(d, 350)}),
                 "atores": {VO: careta(320, 0.3), (MA if n == 1 else VZ): careta(880, 0.3, t=0.2),
                            LA: {"x": 1860, "turn": -0.3, "expr": "azedo", "acoes": [{"t": 0.1, "do": "dance", "style": "treme", "dur": "resto"}]},
                            LU: {"x": 2280, "turn": -0.3, "expr": "azedo", "acoes": [{"t": 0.2, "do": "dance" if n == 1 else "bounce",
                                                                                      **({"style": "treme"} if n == 1 else {}), "dur": "resto"}]}}}
        out.append(p)
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos (bordão + banda no quintal) ─────────
def intervalo(key, n):
    b, bl = R.bloco(key)
    D = b["e"] - b["s"]
    if not bl:
        s1 = round(D / 2, 2)
        banda = {**R.banda(PALCO, s1, fx=["confete"], cam={"x": 1350, "y": 600, "zoom": 1.15, "zoom_fim": 1.05}), "titulo": "a banda (sax)"}
        banda["objetos"]["a"] = arvore(s1, x=2400, depth=0.45)
        return [banda,
                {"seg": round(D - s1, 2), "cenario": COZ, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.1}, "titulo": "o limão dança",
                 "objetos": {"l": limao(D - s1, x=1300, y=1000, depth=0.55, pulo=(0.3, 0.9, 1.5, 2.1)), "c": gato(1700, D - s1, miau=(0.5, 2.0))},
                 "atores": {LA: danca(450, "pulinho", 0.3), LU: danca(2150, "roda", -0.3)}}]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = 3.4
    out = [{"linhas": 1, "seg": p1, "cenario": JARDIM if n == 1 else CAMPO, "camera": "close:laurinha", "callout": [call(0.2, "BORA, TURMINHA!", "rosa")],
            "objetos": {"s": sol(p1)},
            "atores": {LA: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
           {"linhas": 1, "seg": p2, "cenario": "danca_ondas_verde" if n == 1 else PARQUE,
            "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.1} if n == 1 else {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15},
            "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")], "fx": ["confete"],
            "objetos": {"l": limao(p2, x=1600 if n == 1 else 1300, y=1060 if n == 1 else 1020, depth=0.45, pulo=(0.4, 1.4, 2.4))}
                       | ({} if n == 1 else {"n": nuvem(p2, 400)}),
            "atores": {LA: ({"x": 420, "y": 1010, "depth": 1.0} if n == 1 else {"x": 600}) | {"turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura" if n == 1 else "palmas", "dur": "resto"}]},
                       LU: ({"x": 1000, "y": 1010, "depth": 1.0} if n == 1 else {"x": 2000}) | {"turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "joelho" if n == 1 else "festa", "dur": "resto"}]}}}]
    resto = D - p1 - p2
    if n == 1:
        s3 = round(resto / 3, 2)
        out += [{**R.banda(PALCO, s3, fx=["notas"]), "titulo": "a banda"},
                {"seg": s3, "cenario": JARDIM, "camera": {"x": 1300, "y": 540, "zoom": 1.05, "zoom_fim": 1.15}, "titulo": "a vovó e o vovô dançam",
                 "fx": ["notas"], "objetos": {"a": arvore(s3, x=1300, depth=0.55, cai=round(s3 * 0.5, 2), quantos=0.9)},
                 "atores": {VO: danca(450, "twist", 0.3), VZ: danca(2150, "passinho", -0.3, t=0.2)}},
                {**R.banda(PALCO, round(resto - 2 * s3, 2), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.25, "zoom_fim": 1.15}),
                 "titulo": "teclado e bateria"}]
        out[2]["objetos"]["a"] = arvore(s3, x=2400, depth=0.45)
    else:
        s3 = round(resto / 2, 2)
        out += [{**R.banda(PALCO, s3, fx=["notas"], cam={"x": 1350, "y": 600, "zoom": 1.1, "zoom_fim": 1.2}), "titulo": "a banda"},
                {**R.banda(PALCO, round(resto - s3, 2), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.25, "zoom_fim": 1.15}),
                 "titulo": "teclado e bateria"}]
        out[2]["objetos"]["l"] = limao(s3, x=300, y=960, depth=0.4, pulo=(0.5, 1.5))
        out[3]["objetos"]["a"] = arvore(round(resto - s3, 2), x=2400, depth=0.45)
    return out


R.partes["intervalo#1"] = intervalo("intervalo#1", 1)
R.partes["intervalo#2"] = intervalo("intervalo#2", 2)
R.partes["intervalo#3"] = intervalo("intervalo#3", 3)

# ───────── ponte: o vovô mordeu: careta! a vovó mordeu: careta! agora é a sua vez… ui! que careta perfeita! ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4)
dp = dur(T)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": {"x": 1300, "y": 560, "zoom": 1.15, "zoom_fim": 1.3}, "callout": [call(0.2, "O VOVÔ!", "azul")],
     "objetos": {"a": arvore(dp[0], x=2300, depth=0.5), "ce": cerca(500), "n": nuvem(dp[0], 300)},
     "atores": {VZ: careta(1300, 0.0, t=0.0, item="limao")}},
    {"linhas": 1, "cenario": COZ, "camera": {"x": 1300, "y": 560, "zoom": 1.15, "zoom_fim": 1.3}, "callout": [call(0.2, "A VOVÓ!", "rosa")],
     "objetos": {"m": {"id": "mesa", "x": 2250, "y": 930, "z": 1, "depth": 0.9}, "c": gato(500, dp[1], miau=(1.0,))},
     "atores": {VO: careta(1300, 0.0, t=0.0, item="limao")}},
    {"linhas": 1, "cenario": JARDIM, "camera": "close:laurinha", "callout": [call(0.2, "SUA VEZ!", "laranja")], "objetos": {"s": sol(dp[2])},
     "atores": {LA: {"x": 1300, "acoes": [{"t": 0.0, "do": "segurar", "item": "limao", "pose": "alto"}, {"t": 0.4, "do": "apontar_camera", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "UI!", "amarelo"), call(round(dp[3] * 0.45, 2), "CARETA PERFEITA!", "verde")],
     "objetos": {"l": limao(dp[3], x=960, y=1060, depth=0.45, careta=0.2)},
     "atores": {VZ: careta(150, 0.3, y=1010, depth=1.0), VO: careta(560, 0.3, t=0.15, y=1010, depth=1.0),
                LA: careta(1370, -0.3, t=0.1, y=1010, depth=1.0), LU: careta(1770, -0.3, t=0.2, y=1010, depth=1.0)}},
]

# ───────── final: convite + limonada de canudinho (o sorriso de volta) ─────────
R.partes["final#1"] = R.convite(JARDIM, gostou="GOSTOU DA CARETA?", extra_casa={"n": nuvem(3.0, 400)})
for p_ in R.partes["final#1"]:
    if not p_.get("camera"):
        p_["camera"] = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    elif isinstance(p_["camera"], dict) and "zoom_fim" not in p_["camera"]:
        p_["camera"]["zoom_fim"] = p_["camera"]["zoom"] + 0.08
R.partes["final#1"][0]["objetos"] = {"l": limao(3.0, x=1700, y=900, depth=0.4, pulo=(0.6,))}
R.partes["final#1"][2]["atores"]["mamae"]["x"] = 800
R.partes["final#1"][2]["atores"][LA]["x"] = 1800
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 2.6, "cenario": JARDIM, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(0.2, "CARETA DE LIMÃO!", "verde"), call(1.3, "TCHAU!", "amarelo")],
     "objetos": {"a": arvore(2.6, x=1300, depth=0.5), "l": limao(2.6, x=1750, y=1020, depth=0.4, pulo=(0.5, 1.5))},
     "atores": {VO: {"x": 320, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LA: {"x": 880, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LU: {"x": 2250, "turn": -0.3, "acoes": [{"t": 0.0, "do": "jump", "dur": 0.8}, {"t": 0.9, "do": "wave", "dur": "resto"}]}}},
    {"seg": round(dfim - 2.6, 2), "cenario": COZ, "camera": {"x": 1300, "y": 520, "zoom": 1.35, "zoom_fim": 1.5},
     "callout": [call(0.2, "LIMONADA!", "amarelo")], "fx": ["coracoes"], "titulo": "limonada de canudinho: o sorriso de volta",
     "objetos": {"l": limao(dfim - 2.6, x=1850, y=900, depth=0.35, pulo=(1.2,))},
     "atores": {LA: {"x": 1300, "turn": 0.1, "acoes": [{"t": 0.0, "do": "beber", "item": "limonada", "dur": "resto"}]}}},
]

R.salvar("Roteiro de 'Careta de Limão!' (take v1 cortado para 2:50, Laurinha, estilo E13, nota 4,8): o quintal da vovó com o "
         "pé de limão; mordeu → CARETA DE AZEDO (olho fechou, boca entortou, cabelo arrepiou em closes e telas divididas); "
         "os vizinhos mostram a careta (joaninha, formiguinha, sapo, espelho); ponte vovô/vovó; banda debaixo do limoeiro; "
         "final com limonada de canudinho. Gerado por scripts/roteiros/ep27_careta_de_limao.py.")
