"""Roteiro verso a verso do canal FOFOLUCOS — 01 "Somos os Fofolucos!" (take v1 inteiro, 2:47, voz Persona Luisinho v2,
estilo F1, nota 4,9) → canais/fofolucos/musicas/01_somos_os_fofolucos/roteiro.json.

Hino de apresentação da turma da VILA MONSTRINHA. Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — chapado sem contorno,
cenários mon_*, e os TRÊS enquadramentos misturados (CABEÇA enchendo a tela · BUSTO cortado na cintura · CORPO TODO).
Cada monstrinho aparece em close no seu verso (Bilu do olhão, Teco dos três olhinhos, Zuzu do chifrinho, Nhoque do
bocão); refrão = a turma faz a cara de monstro (ação nova `rawr`); ponte = mostra o dente / a garra / balança o rabo /
BU!; 2º verso = medinho do escuro e a LANTERNA (prop novo); banda da turma no palco (Bilu na bateria, Zuzu no teclado).
Sem dupla fixa: `cantam` = o monstrinho em foco em cada plano.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo01_somos_os_fofolucos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import Roteiro, call  # noqa: E402

R = Roteiro("fofolucos/ep01-somos-os-fofolucos", "01_somos_os_fofolucos", "bilu")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
TURMA = (BI, TE, GO, MI, ZU, NH)
VILA, PARQUE, QUARTO, PALCO, NOITE, ESCOLA, COZ = "mon_vila", "mon_parque", "mon_quarto", "mon_palco", "mon_noite", "mon_escola", "mon_cozinha"
# fundos de destaque: nunca a mesma cor de quem está na frente (Bilu × azul, Teco × roxo…)
RAIOS = {"laranja": "mon_raios_laranja", "verde": "mon_raios_verde", "rosa": "mon_raios_rosa", "vermelho": "mon_raios_vermelho"}


def dur(T):
    return [round(t1 - t0, 2) for t0, t1, _ in T]


# ── enquadramentos (bíblia §4) ──
def cab(x=1300):                       # CABEÇA: cabeça e peito enchendo a tela
    return {"x": x, "y": 515, "zoom": 2.2, "zoom_fim": 2.32}


def busto(x=1300, y=650):              # BUSTO: corte na cintura
    return {"x": x, "y": y, "zoom": 1.75, "zoom_fim": 1.85}


def corpo(x=1300, x_fim=None):         # CORPO TODO
    c = {"x": x, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    if x_fim:
        c["x_fim"] = x_fim
    return c


GCAM = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}      # fundos gráficos (raios/xadrez/brilho)


def a(x, *acoes, turn=0.0, **kw):
    """ator: a('x', ('dance','festa'), ('rawr', 0.4)…) — cada ação = (do, t[, estilo/dur])."""
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
    """ator em fundo gráfico (coordenadas de 1920, pé em 1010)."""
    return a(x, *acoes, turn=turn, y=1010, depth=0.85)     # ≈ 55–60 % da altura da tela (bíblia §4)


def obj(id_, x, y, depth, d, z=1, fixo=None, lin=None, pts=None):
    d = max(0.6, d)
    ks = [{"t": 0.0, "pose": dict(fixo or {}), "ease": "step"}]
    for c, (v0, v1) in (lin or {}).items():
        ks[0]["pose"][c] = float(v0)
        ks.append({"t": round(d - 0.06, 2), "pose": {c: float(v1)}, "ease": "linear"})
    for c, vs in (pts or {}).items():
        ks += [{"t": round(t, 2), "pose": {c: float(v)}, "ease": "out"} for t, v in vs]
    return {"id": id_, "x": x, "y": y, "z": z, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def anel(d, x, y, cor=0, depth=0.7):
    """anel de estrelinhas (destaque) apontando o detalhe do monstrinho (olho, antena, chifre…)."""
    return obj("destaque", x, y, depth, d, z=6, fixo={"cor": cor, "pulso": 0.0}, lin={"giro": (0.0, d * 0.8)},
               pts={"pulso": [(round(0.4 * j, 2), float(j % 2)) for j in range(1, int(d / 0.4))]})


def num(d, n, x=2050, y=330):
    return obj("numero", x, y, 0.9, d, z=6, fixo={"n": n, "pop": 0.0}, pts={"pop": [(0.25, 1.0)]})


def banda(cen, d, cam=None, extra=None):
    """a banda da turma: Bilu na bateria, Zuzu no teclado (+ quem mais dançar em `extra`)."""
    p = R.banda(cen, d, teclado=True, sax=ZU, bateria=BI, cam=cam or {"x": 1250, "y": 620, "zoom": 1.15, "zoom_fim": 1.05}, extra=extra)
    p["cantam"] = [ZU]
    return p


# ───────── intro ─────────
T = R.tempos("intro#1", [{"seg": 3.4}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1, "seg": 2.6}, {"seg": 3.0}, {"seg": 0.0}])
d = dur(T)
R.partes["intro"] = [
    {"seg": 3.4, "cenario": VILA, "camera": corpo(700, 1900), "titulo": "a Vila Monstrinha", "cantam": [GO],
     "atores": {GO: a(2200, ("look_around", 0.2), turn=-0.3), MI: a(600, ("wave", 0.4), turn=0.3)}},
    {"linhas": 1, "cenario": VILA, "camera": cab(1300), "flash": True, "callout": [call(0.1, "FOFOLUCOS!", "roxo")], "cantam": [BI],
     "atores": {BI: a(1300, ("rawr", 0.1))}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.2, "RAWR!", "laranja")], "cantam": [MI],
     "atores": {MI: a(1050, ("rawr", 0.0), turn=0.25), ZU: a(1550, ("rawr", 0.2), turn=-0.25)}},
    {"linhas": 1, "seg": 2.6, "cenario": RAIOS["laranja"], "camera": GCAM, "fx": ["confete"], "cantam": [TE],
     "callout": [call(0.2, "FOFINHO E MALUQUINHO!", "rosa")],
     "atores": {TE: g(210, ("dance", 0.0, "festa"), turn=0.2), GO: g(710, ("dance", 0.1, "pulinho")), MI: g(1210, ("dance", 0.0, "bracos")),
                NH: g(1710, ("dance", 0.15, "festa"), turn=-0.2)}},
    {**banda(PALCO, 3.0), "titulo": "a banda da turma"},
    {**banda(PALCO, max(0.6, d[5]), cam={"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1},
             extra={TE: a(2250, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado e bateria"},
]


# ───────── 1º verso: a turma, um a um (closes de cabeça) ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": corpo(800, 1800), "callout": [call(0.4, "VILA MONSTRINHA!", "roxo")], "cantam": [BI],
     "atores": {BI: a(300, ("walk", 0.0), turn=0.3) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 1100, "dur": 2.4},
                                                                  {"t": 2.5, "do": "wave", "dur": "resto"}]},
                TE: a(2300, ("wave", 0.3), turn=-0.3)}},
    {"linhas": 1, "cenario": VILA, "camera": {"x": 1300, "y": 600, "zoom": 1.4, "zoom_fim": 1.48}, "tremor": [1.4], "callout": [call(0.6, "DE ARREPIAR!", "laranja")], "cantam": [GO],
     "atores": {GO: a(850, ("dance", 0.0, "treme"), turn=0.25), MI: a(1300, ("dance", 0.1, "treme")), NH: a(1750, ("dance", 0.2, "treme"), turn=-0.25)}},
    R.dividida({"cenario": PARQUE, "camera": {"x": 1300, "y": 500, "zoom": 2.0, "zoom_fim": 2.1}, "cantam": [ZU],
                "objetos": {"m": anel(d[2], 1300, 300, cor=0)}, "atores": {ZU: a(1300, ("dance", 0.0, "cabeca"))}},
               {"cenario": ESCOLA, "camera": {"x": 1300, "y": 500, "zoom": 2.0, "zoom_fim": 2.1},
                "objetos": {"m": anel(d[2], 1300, 300, cor=2)}, "atores": {TE: a(1300, ("dance", 0.0, "cabeca"))}},
               linhas=1, layout="vertical", callout=[call(0.2, "CHIFRE!", "amarelo"), call(1.4, "ANTENA!", "azul")]),
    {"linhas": 1, "cenario": COZ, "camera": cab(1300), "callout": [call(0.3, "DENTINHO!", "vermelho")], "cantam": [NH],
     "atores": {NH: a(1300, ("rawr", 0.2))}},
    {"linhas": 1, "cenario": PARQUE, "camera": cab(1300), "callout": [call(0.3, "BILU!", "azul")], "cantam": [BI],
     "objetos": {"m": anel(d[4], 1300, 520, cor=0, depth=0.9)},
     "atores": {BI: a(1300, ("look_around", 0.1), expr="surprised")}},
    {"linhas": 1, "cenario": ESCOLA, "camera": cab(1300), "callout": [call(0.3, "TECO!", "roxo")], "cantam": [TE],
     "objetos": {"n": num(d[5], 3, x=1700, y=420)},
     "atores": {TE: {"x": 1300, "turn": 0.0, "acoes": [{"t": 0.0, "do": "dance", "style": "cabeca", "dur": "resto"}],
                     "keys": [{"t": round(0.6 + 0.5 * j, 2), "pose": {"lid": 1.0 if j % 2 == 0 else 0.0}, "ease": "step"} for j in range(5)]}}},
    {"linhas": 1, "cenario": VILA, "camera": busto(1300), "callout": [call(0.3, "ZUZU!", "laranja")], "cantam": [ZU],
     "objetos": {"m": anel(d[6], 1300, 250, cor=1, depth=0.6)},
     "atores": {ZU: a(1300, ("dance", 0.0, "gingado"))}},
    {"linhas": 1, "cenario": NOITE, "camera": cab(1300), "tremor": [round(d[7] * 0.5, 2)], "flash": True,
     "callout": [call(0.3, "NHOQUE!", "vermelho")], "cantam": [NH],
     "atores": {NH: a(1300, ("rawr", round(d[7] * 0.35, 2)))}},
]


# ───────── refrão: faz a cara de monstro! mostra a garrinha! ─────────
CEN_REF = {1: (RAIOS["laranja"], PARQUE), 2: (RAIOS["verde"], ESCOLA), 3: (RAIOS["rosa"], VILA)}


def refrao(n):
    spec = [{"linhas": 2}] * 4 + ([{"seg": 0.0}] if n == 2 else [])      # 2º refrão: trecho só instrumental antes do bordão
    T = R.tempos(f"refrao#{n}", spec)
    out = []
    for i, (t0, t1, _) in enumerate(T):
        dd = round(t1 - t0, 2)
        meio = round(dd * 0.45, 2)
        if i == 4:
            p = {**banda(PALCO, dd, cam={"x": 1350, "y": 600, "zoom": 1.2, "zoom_fim": 1.1},
                         extra={NH: a(350, ("dance", 0.0, "festa"), turn=0.3)}), "titulo": "a banda"}
            out.append(p)
            continue
        if n == 3 and i in (1, 3):
            p = banda(PALCO, dd, extra={(MI if i == 1 else NH): a(2250, ("rawr", meio), turn=-0.3)})
            p.pop("seg")
            p.update({"linhas": 2, "callout": [call(0.2, "FOFOLUCOS!", "roxo")]})
        elif i == 0:                                       # a turma inteira faz a cara de monstro (corpo todo, fundo de raios)
            p = {"linhas": 2, "cenario": CEN_REF[n][0], "camera": GCAM, "fx": ["estrelas"], "cantam": [BI],
                 "callout": [call(0.1, "FOFOLUCOS!", "roxo"), call(meio, "FAZ A CARA DE MONSTRO!", "amarelo")],
                 "atores": {c: g(x, ("dance", 0.0, "festa"), ("rawr", meio + 0.08 * k), turn=tn)
                            for k, (c, x, tn) in enumerate(zip({1: (TE, GO, BI, NH), 2: (MI, ZU, BI, TE), 3: (GO, NH, ZU, MI)}[n],
                                                               (210, 710, 1210, 1710), (0.25, 0.1, -0.1, -0.25)))}}
            if n == 1:
                p["flash"] = True
        elif i == 1:                                       # mostra a garrinha! (busto, dois monstrinhos)
            p = {"linhas": 2, "cenario": CEN_REF[n][1], "camera": busto(1300, 630), "cantam": [MI],
                 "callout": [call(meio, "MOSTRA A GARRINHA!", "rosa")],
                 "atores": {MI: a(1000, ("dance", 0.0, "bracos"), ("rawr", meio), turn=0.25),
                            GO: a(1600, ("dance", 0.1, "bracos"), ("rawr", meio + 0.1), turn=-0.25)}}
        elif i == 2:                                       # faz a cara de monstro! (tela dividida em CABEÇA)
            pa, pb = ((BI, NOITE), (NH, COZ)) if n != 2 else ((ZU, VILA), (TE, QUARTO))
            p = R.dividida({"cenario": pa[1], "camera": {"x": 1300, "y": 560, "zoom": 2.0, "zoom_fim": 2.15}, "cantam": [pa[0]],
                            "atores": {pa[0]: a(1300, ("rawr", 0.2))}},
                           {"cenario": pb[1], "camera": {"x": 1300, "y": 560, "zoom": 2.0, "zoom_fim": 2.15},
                            "atores": {pb[0]: a(1300, ("rawr", meio))}},
                           linhas=2, layout="diagonal" if n % 2 else "vertical", callout=[call(meio, "RAWR!", "vermelho")])
        else:                                              # fofinho e maluquinho! (corpo todo, a turma ri e dança)
            p = {"linhas": 2, "cenario": (PARQUE, VILA, PARQUE)[n - 1], "camera": corpo(1300), "fx": ["confete"], "cantam": [TE],
                 "callout": [call(meio, "FOFINHO E MALUQUINHO!", "rosa")],
                 "atores": {TE: a(350, ("dance", 0.0, "festa"), ("laugh", meio), turn=0.3),
                            ZU: a(850, ("dance", 0.1, "pulinho"), turn=0.2),
                            MI: a(1750, ("dance", 0.0, "cintura"), ("laugh", meio + 0.2), turn=-0.2),
                            GO: a(2250, ("dance", 0.15, "roda"), turn=-0.3)}}
        out.append(p)
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos: o bordão "Fofolucos! Rawr!" + a banda ─────────
def intervalo(key, n):
    b, bl = R.bloco(key)
    D = b["e"] - b["s"]
    if not bl:
        s1 = round(D / 2, 2)
        return [{**banda(PALCO, s1, extra={MI: a(2250, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "a banda"},
                {"seg": round(D - s1, 2), "cenario": "mon_brilho_laranja", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança",
                 "cantam": [GO],
                 "atores": {GO: g(210, ("dance", 0.0, "roda")), TE: g(710, ("dance", 0.1, "pulinho")), NH: g(1210, ("dance", 0.0, "festa")),
                            BI: g(1710, ("dance", 0.1, "sapinho"), turn=-0.2)}}]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = round(min(3.4, D - p1 - 0.6), 2)
    quem = (ZU, GO)[n - 1]
    out = [{"linhas": 1, "seg": p1, "cenario": (VILA, NOITE)[n - 1], "camera": cab(1300), "cantam": [quem],
            "callout": [call(0.2, "FOFOLUCOS! RAWR!", "roxo")],
            "atores": {quem: a(1300, ("rawr", 0.1), ("apontar_camera", 1.6))}},
           {"linhas": 1, "seg": p2, "cenario": ("mon_xadrez_verde", "mon_xadrez_laranja")[n - 1], "camera": GCAM, "fx": ["confete"],
            "callout": [call(0.2, "FOFOLUCOS!", "rosa")], "cantam": [MI],
            "atores": {MI: g(380, ("dance", 0.0, "cintura"), turn=0.2), TE: g(960, ("dance", 0.1, "joelho")),
                       NH: g(1540, ("dance", 0.0, "palmas"), turn=-0.2)}}]
    resto = round(D - p1 - p2, 2)
    if resto >= 0.6:
        out.append({**banda(PALCO, resto, cam={"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15},
                            extra={GO: a(350, ("dance", 0.0, "bracos"), turn=0.3)}), "titulo": "teclado e bateria"})
    return out


for n in (1, 2, 3):
    R.partes[f"intervalo#{n}"] = intervalo(f"intervalo#{n}", n)


# ───────── ponte: mostra o dente! mostra a garra! balança o rabo… e dá um susto: BU! ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4)
dp = dur(T)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": COZ, "camera": cab(1300), "callout": [call(0.1, "MOSTRA O DENTE!", "branco" if False else "vermelho")], "cantam": [NH],
     "atores": {NH: a(1300, ("rawr", 0.0))}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300, 600), "callout": [call(0.1, "MOSTRA A GARRA!", "rosa")], "cantam": [MI],
     "atores": {MI: a(1300, ("rawr", 0.0))}},
    {"linhas": 1, "cenario": RAIOS["vermelho"], "camera": GCAM, "callout": [call(0.1, "BALANÇA O RABO!", "verde")], "cantam": [GO],
     "atores": {GO: g(700, ("dance", 0.0, "cintura"), turn=-0.75), ZU: g(1250, ("dance", 0.1, "cintura"), turn=0.75)}},
    {"linhas": 1, "cenario": NOITE, "camera": corpo(1300), "flash": True, "tremor": [round(dp[3] * 0.5, 2)], "cantam": [BI],
     "callout": [call(round(dp[3] * 0.45, 2), "BU!", "vermelho")],
     "atores": {BI: a(1300, ("rawr", round(dp[3] * 0.4, 2))),
                TE: a(500, ("shock_reaction", round(dp[3] * 0.5, 2)), turn=0.3, expr="surprised"),
                MI: a(2100, ("jump", round(dp[3] * 0.5, 2)), turn=-0.3)}},
]


# ───────── 2º verso: o medinho do escuro e a lanterna ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": VILA, "camera": {"x": 1700, "y": 430, "zoom": 1.6, "zoom_fim": 1.7}, "callout": [call(0.3, "GOGO!", "verde")],
     "cantam": [GO], "atores": {GO: a(1700, ("look_around", 0.1), y=860, depth=0.9)}},
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "callout": [call(0.3, "MIMI!", "rosa")], "cantam": [MI],
     "objetos": {"ce": {"id": "cerquinha", "x": 1300, "y": 960, "z": 4, "depth": 1.0}},
     "atores": {MI: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "run", "to_x": 1100, "dur": 0.6},
                                                     {"t": 0.6, "do": "jump", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": VILA, "camera": {"x": 1300, "y": 600, "zoom": 1.4, "zoom_fim": 1.48}, "callout": [call(0.4, "MEDO? NADA!", "laranja")], "cantam": [ZU],
     "atores": {ZU: a(850, ("bacana", 0.1), turn=0.25), BI: a(1300, ("bacana", 0.2)), NH: a(1750, ("bacana", 0.3), turn=-0.25)}},
    {"linhas": 1, "cenario": NOITE, "camera": busto(1300, 640), "escurece": [0.0, 0.35], "callout": [call(0.4, "DO ESCURO!", "azul")],
     "cantam": [TE],
     "atores": {TE: a(1000, ("shock_reaction", 0.3), turn=0.25, expr="scared"), MI: a(1600, ("shock_reaction", 0.5), turn=-0.25, expr="scared")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "escurece": [0.45, 0.0], "callout": [call(0.4, "LANTERNA!", "amarelo")],
     "cantam": [BI],
     "objetos": {"l": obj("lanterna", 900, 960, 0.9, d[4], z=5, fixo={"liga": 0.0, "dir": -0.04}, pts={"liga": [(0.5, 1.0)]})},
     "atores": {BI: a(1800, ("look_around", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "tremor": [0.3], "flash": True, "callout": [call(0.2, "AI!", "vermelho")],
     "cantam": [TE],
     "objetos": {"l": obj("lanterna", 2350, 960, 0.8, d[5], z=5, fixo={"liga": 1.0, "dir": 0.5})},
     "atores": {TE: a(500, ("jump", 0.0), turn=0.3, expr="surprised"), GO: a(1000, ("jump", 0.1), turn=0.2, expr="surprised"),
                ZU: a(1500, ("jump", 0.05), turn=-0.2, expr="surprised")}},
    R.dividida({"cenario": NOITE, "camera": {"x": 1300, "y": 600, "zoom": 1.6, "zoom_fim": 1.7}, "cantam": [TE],
                "atores": {TE: a(1300, ("shock_reaction", 0.1), expr="scared")}},
               {"cenario": PARQUE, "camera": {"x": 1300, "y": 600, "zoom": 1.6, "zoom_fim": 1.7},
                "atores": {MI: a(1300, ("laugh", 0.1))}},
               linhas=1, layout="diagonal", callout=[call(0.3, "FOFINHO E MEDROSO!", "rosa")]),
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "fx": ["estrelas"], "callout": [call(0.4, "NUNCA VI!", "laranja")], "cantam": [NH],
     "atores": {NH: a(400, ("laugh", 0.0), turn=0.3), BI: a(900, ("dance", 0.1, "pulinho"), turn=0.2),
                TE: a(1700, ("laugh", 0.2), turn=-0.2), GO: a(2200, ("dance", 0.0, "festa"), turn=-0.3)}},
]

# ───────── final: convite + tchau (Rawr!) ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": cab(1300), "callout": [call(0.3, "GOSTOU DOS FOFOLUCOS?", "roxo")], "cantam": [BI],
     "atores": {BI: a(1300, ("apontar_camera", 0.1))}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "callout": [call(0.3, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"], "cantam": [ZU],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {ZU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": VILA, "camera": busto(1300, 640), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")], "cantam": [MI],
     "atores": {MI: a(1000, ("point", 0.1), turn=0.3), TE: a(1600, ("wave", 0.2), turn=-0.25)}},
    {"linhas": 1, "cenario": RAIOS["vermelho"], "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"], "cantam": [GO],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {GO: g(560, ("point", 0.2), ("rawr", round(d[3] - 1.5, 2)), turn=0.2) | {"depth": 1.0}}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.6, "cenario": VILA, "camera": corpo(1300), "fx": ["coracoes"], "cantam": [BI],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.5, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn, depth=0.78) for k, (c, x, tn) in
                enumerate(((TE, 260, 0.3), (GO, 676, 0.25), (BI, 1092, 0.1), (MI, 1508, -0.1), (ZU, 1924, -0.25), (NH, 2340, -0.3)))}},
    {"seg": round(dfim - 3.6, 2), "cenario": NOITE, "camera": cab(1300), "flash": True, "callout": [call(0.2, "RAWR!", "vermelho")],
     "titulo": "o último RAWR", "cantam": [NH], "atores": {NH: a(1300, ("rawr", 0.1))}},
]

# ── vida no cenário (sem contorno, como todos os objetos do canal): nuvens andando, lua com carinha, bolhas nos fundos ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    if cen in (PARQUE, VILA):
        x0 = (300, 1700, 900, 2100)[j % 4]
        ob.setdefault("nv", obj("nuvem", x0, 300, 0.32, dd, z=0, fixo={"cara": 1.0}, lin={"x": (x0, x0 + 280)}))
    elif cen == NOITE:
        ob.setdefault("lua", obj("lua", 2150, 420, 0.42, dd, z=0, pts={"boca": [(0.5, 0.6)], "brilho": [(0.0, 0.0), (1.0, 1.0)]}))
    elif cen.startswith(("mon_raios_", "mon_xadrez_", "mon_brilho_")) or cen in (QUARTO, ESCOLA, COZ):
        x0 = (300, 1650, 800, 1300)[j % 4]
        ob.setdefault("bo", obj("bolha", x0, 1000, 0.3, dd, z=0, fixo={"tam": 1.0}, lin={"y": (1000, 250), "balanco": (0.0, round(dd, 1))}))
    if not ob:
        sb.pop("objetos", None)


for chave, planos in R.partes.items():
    k_info = chave if chave in R.info else f"{chave}#1"
    for j, (p_, (t0, t1, _)) in enumerate(zip(planos, R.tempos(k_info, planos))):
        for sb in [p_] + list((p_.get("tela_dividida") or {}).get("paineis", [])):
            _ambiente(sb, round(t1 - t0, 2), j)

R.salvar("Roteiro do canal Fofolucos — 01 'Somos os Fofolucos!' (take v1 inteiro, 2:47, nota 4,9): hino da turma da Vila "
         "Monstrinha; closes de CABEÇA para cada monstrinho, BUSTO para cantar, CORPO TODO para dançar; refrão com a cara de "
         "monstro (rawr); ponte mostra o dente/garra/rabo/BU!; medinho do escuro e a lanterna; banda da turma no palco. "
         "Gerado por scripts/roteiros/fo01_somos_os_fofolucos.py.")
