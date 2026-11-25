"""Roteiro verso a verso do canal FOFOLUCOS — 08 "Sombra de Monstrinho!" (take inteiro, 2:47, 136 BPM, estilo F5, nota 5;
letra 5 a 8 anos) → canais/fofolucos/musicas/08_sombra_de_monstrinho/roteiro.json.

TEATRO DE SOMBRAS à noite na sala da Vila Monstrinha (cenário novo `mon_sombras`: parede bege iluminada no meio, janela com
lua — bege não é cor de nenhum monstrinho). A LANTERNA (prop `lanterna`) acende e as SOMBRAS (prop novo `sombra`) aparecem
na parede: o dragão do Bilu (com o chifrinho), o coelho do Teco (com a antena), o jacaré que abre e fecha a boca e a
borboleta de mãos cruzadas (ponte = os comandos). 2º verso = a VIRADA: uma sombra gigante e assustadora (formiga), todo
mundo pula… a Mimi chega perto e acha o culpado: a FORMIGUINHA (prop novo `formiga`) em cima da lanterna, acenando.
Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — CABEÇA / BUSTO / CORPO, chifres/antenas no quadro, closes do Zuzu sem cortar o
chifre, nunca monstrinho na frente da própria cor, nunca "monstro".
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo08_sombra_de_monstrinho.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("fofolucos/ep08-sombra-de-monstrinho", "08_sombra_de_monstrinho", "bilu")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
SALA, NOITE, VILA, PALCO, CEU = "mon_sombras", "mon_noite", "mon_vila", "mon_palco", "mon_abertura"
QUARTO, FESTA, COZ = "mon_quarto", "mon_festa", "mon_cozinha"        # outras paredes da Vila onde as sombras aparecem
CHAO = 935
DRAGAO, COELHO, JACARE, BORBOLETA, FORMIGA = 0, 1, 2, 3, 4
K_SOMBRA = 0.62         # o roteiro multiplica objetos por escala_personagens (1,45): sombra 0,6 → 0,54 na tela (cabe no CORPO)


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


def pula(x, t=0.1, turn=0.0, **kw):
    return {"x": x, "turn": turn, "acoes": [{"t": t, "do": "jump", "dur": 0.8, "height": 170}], **kw}


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


def sombra(forma, x, d, depth=0.55, y=740, liga_em=None, key="sb", lin=None, pts=None, **fixo):
    """sombra na parede (atrás de todo mundo); `liga_em` = aparece quando a luz bate."""
    f = {"forma": float(forma), "liga": 0.0 if liga_em is not None else 1.0, **{k: float(v) for k, v in fixo.items()}}
    p = dict(pts or {})
    if liga_em is not None:
        p["liga"] = [(round(liga_em, 2), 1.0)]
    li = {"treme": (0.0, round(max(0.6, d) * 0.5, 2)), **(lin or {})}
    if forma == FORMIGA:
        li.setdefault("anda", (0.0, round(max(0.6, d) * 1.6, 2)))
    return {key: obj("sombra", x, y, round(depth * K_SOMBRA, 3), d, z=0, fixo=f, lin=li, pts=p)}


def lanterna(x, d, direc=-0.16, liga_em=None, depth=0.45, y=960):
    p = {"liga": [(round(liga_em, 2), 1.0)]} if liga_em is not None else None
    return {"lant": obj("lanterna", x, y, depth, d, z=1, fixo={"liga": 0.0 if liga_em is not None else 1.0, "dir": direc}, pts=p)}


def abre_fecha(d, passo=0.45, t0=0.1):
    """boca do jacaré/dragão abrindo e fechando no ritmo."""
    out, t, k = [], t0, 0
    while t < d - 0.1:
        out.append((round(t, 2), 1.0 if k % 2 == 0 else 0.0))
        t += passo
        k += 1
    return out


def banda(cen, d, extra=None):
    p = R.banda(cen, d, teclado=True, sax=ZU, bateria=BI, cam={"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["cantam"] = [ZU]
    return p


def em(t0, versos, *alvos, default=0.4):
    return R.tp(t0, versos, *alvos, default=default)


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
tr = em(T[1][0], T[1][2], "rawr", default=round(d[1] * 0.5, 2))
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "titulo": "teatro de sombras na Vila Monstrinha", "cantam": [BI],
     "callout": [call(0.4, "SOMBRA DE MONSTRINHO!", "roxo")],
     "objetos": {**sombra(DRAGAO, 1550, d[0], depth=0.6, liga_em=0.3, pts={"boca": abre_fecha(d[0], 0.6, 0.6)}),
                 **lanterna(750, d[0], direc=-0.12)},
     "atores": {BI: a(1000, ("rawr", 0.3), turn=0.3)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [NH],
     "callout": [call(0.2, "ACENDE A LANTERNA…", "amarelo"), call(round(tr, 2), "RAWR!", "vermelho")],
     "objetos": {**lanterna(1050, d[1], direc=-0.14, liga_em=0.7), **sombra(COELHO, 1650, d[1], liga_em=round(tr, 2), orelha=0.0,
                                                                            lin={"orelha": (0.0, 4.0)})},
     "atores": {NH: a(800, ("point", 0.2), ("rawr", round(tr, 2)), turn=0.35)}},
    {"linhas": 1, "cenario": "mon_raios_laranja", "camera": GCAM, "flash": True, "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.1, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {TE: g(210, ("rawr", 0.3), turn=0.2), GO: g(710, ("rawr", 0.38)), BI: g(1210, ("rawr", 0.46)),
                MI: g(1710, ("rawr", 0.54), turn=-0.2)}},
    {**banda(PALCO, max(0.6, d[3]), extra={TE: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: a lanterna, o dragão do Bilu e o coelho do Teco ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": NOITE, "camera": corpo(1300, 1420), "cantam": [BI], "fx": ["estrelas"],
     "callout": [call(0.3, "NA NOITE DA VILA…", "roxo")],
     "objetos": {"gato": obj("gato", 420, CHAO + 10, 0.55, d[0], z=2, fixo={"lado": 1.0}, lin={"rabo": (0.0, 3.0)},
                             pts={"miau": [(round(d[0] * 0.5, 2), 1.0), (round(d[0] * 0.8, 2), 0.0)]}),
                 "cometa": obj("cometa", 600, 200, 0.4, d[0], z=0, lin={"x": (600, 2300), "y": (200, 120)})},
     "atores": {GO: anda(a(750, turn=0.4, expr="sly"), 1150, d[0], como="walk"), ZU: anda(a(1300, turn=0.4, expr="sly"), 1750, d[0])}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1150, 600), "cantam": [BI], "callout": [call(0.1, "A LANTERNA ACENDEU!", "amarelo")],
     "objetos": lanterna(1250, d[1], direc=-0.1, liga_em=0.15, depth=0.6),
     "atores": {NH: a(950, ("grab", 0.0), turn=0.35, expr="surprised")}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [BI], "tremor": [0.4],
     "callout": [call(0.2, "NA PAREDE, UM BICHÃO!", "vermelho")],
     "objetos": {**sombra(DRAGAO, 1500, d[2], depth=0.68, liga_em=0.1, boca=1.0), **lanterna(700, d[2], direc=-0.1)},
     "atores": {MI: a(1000, ("take", 0.3), turn=0.3, expr="surprised"),
                GO: a(2050, ("shock_reaction", 0.4), turn=-0.3, expr="surprised")}},
    R.dividida({"cenario": SALA, "camera": {"x": 1350, "y": 560, "zoom": 1.5, "zoom_fim": 1.58}, "cantam": [BI],
                "objetos": sombra(DRAGAO, 1650, d[3], depth=0.6, boca=0.0, pts={"boca": abre_fecha(d[3], 0.5)}),
                "atores": {MI: a(1150, ("look_around", 0.0), turn=0.3, expr="surprised")}},
               {"cenario": QUARTO, "camera": {"x": 1250, "y": 560, "zoom": 1.5, "zoom_fim": 1.58},
                "objetos": sombra(DRAGAO, 1650, d[3], depth=0.6, key="sb3", boca=1.0),
                "atores": {GO: a(1250, ("take", 0.2), turn=0.3, expr="surprised")}},
               linhas=1, layout="diagonal", callout=[call(0.2, "RAWR! QUEM É?", "roxo")]),
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [BI], "callout": [call(0.2, "ERA O BILU COM O CHIFRINHO!", "azul")],
     "objetos": {**sombra(DRAGAO, 1600, d[4], depth=0.62), **lanterna(650, d[4], direc=-0.08)},
     "atores": {BI: a(1050, ("rawr", 0.2), turn=0.4, expr="joy")}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1450), "cantam": [BI], "fx": ["estrelas"],
     "callout": [call(0.2, "SOMBRA DE DRAGÃO!", "vermelho")],
     "objetos": sombra(DRAGAO, 1650, d[5], depth=0.7, pts={"boca": abre_fecha(d[5], 0.4)}),
     "atores": {BI: a(900, ("rawr", 0.1), turn=0.4)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [BI], "callout": [call(0.2, "E O TECO FEZ UM COELHO!", "roxo")],
     "objetos": {**sombra(COELHO, 1600, d[6], depth=0.62, liga_em=0.3), **lanterna(650, d[6], direc=-0.08)},
     "atores": {TE: a(1050, ("pensar", 0.0), ("point", round(d[6] * 0.55, 2)), turn=0.4)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1450), "cantam": [BI], "fx": ["coracoes"],
     "callout": [call(0.2, "COM A ANTENA, QUE BONITÃO!", "rosa")],
     "objetos": sombra(COELHO, 1700, d[7], depth=0.66, lin={"orelha": (0.0, 3.0)}),
     "atores": {TE: a(1000, ("laugh", 0.1), turn=0.4, expr="joy")}},
]


# ───────── refrão: sombra de monstrinho! grandona no paredão! rawr! faz com a mão! ─────────
REF = {
    1: dict(par=((BI, DRAGAO), (TE, COELHO)), cens=(SALA, SALA), trio=("mon_raios_laranja", (GO, MI, TE)), close=(MI, "mon_brilho_azul")),
    2: dict(par=((NH, JACARE), (MI, BORBOLETA)), cens=(FESTA, QUARTO), trio=("mon_xadrez_verde", (BI, MI, ZU)), close=(ZU, QUARTO)),
    3: dict(par=((GO, DRAGAO), (BI, COELHO)), cens=(SALA, SALA), trio=("mon_xadrez_azul", (GO, MI, NH)), close=(BI, COZ)),
}


def plano_sombra(quem, forma, dd, versos, t0, x_q=950, x_s=1600, depth=0.66, cor="roxo", cen=SALA):
    if cen == QUARTO:                                      # quarto: a cama pintada fica à direita (x ≥ 1700)
        x_q, x_s = 700, 1300
    trw = em(t0, versos, "grandona", "rawr", default=round(dd * 0.5, 2))
    ex = {"boca": abre_fecha(dd, 0.45)} if forma in (DRAGAO, JACARE) else None
    li = {"asas": (0.0, round(dd * 2.2, 1))} if forma == BORBOLETA else ({"orelha": (0.0, 3.0)} if forma == COELHO else None)
    return {"linhas": 2, "cenario": cen, "camera": corpo(1300), "cantam": [quem], "fx": ["estrelas"],
            "callout": [call(0.1, "SOMBRA DE MONSTRINHO!", cor), call(round(trw, 2), "GRANDONA NO PAREDÃO!", "amarelo")],
            "objetos": {**sombra(forma, x_s, dd, depth=0.45, lin={**(li or {}), "x": (x_s, x_s)}, pts={**(ex or {})}),
                        **lanterna(x_q - 330, dd, direc=-0.1)},
            "atores": {quem: a(x_q, ("rawr", round(min(trw, dd - 0.6), 2)), turn=0.4)}} | _cresce(dd, depth, trw)


def _cresce(dd, depth, t):
    """a sombra CRESCE no "grandona": a profundidade vai de 0,45 para `depth` (keys do próprio objeto ficam iguais)."""
    return {"_cresce": (round(t, 2), depth)}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        tm = em(t0, versos, "rawr", default=round(dd * 0.5, 2))
        if i % 4 in (0, 2):                                # a sombra na parede, grandona
            quem, forma = cfg["par"][i // 2]
            p = plano_sombra(quem, forma, dd, versos, t0, cor=("roxo", "azul")[i // 2], cen=cfg["cens"][i // 2])
            if n == 3 and i == 2:                          # no último refrão a formiguinha volta: em cima da lanterna, acenando
                p["objetos"]["form"] = obj("formiga", 600, 862, 0.35, dd, z=6, fixo={"lado": 1.0}, lin={"aceno": (0.0, 1.0)})
                p["objetos"]["sb2"] = sombra(FORMIGA, 2050, dd, depth=0.42, key="sb2")["sb2"]
            out.append(p)
        elif i % 4 == 1:                                   # "Rawr! Faz com a mão!" — o trio faz o RAWR no fundo colorido
            cen, trio = cfg["trio"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "flash": n == 1, "fx": ["estrelas"], "cantam": [trio[1]],
                        "callout": [call(0.1, "SOMBRA DE MONSTRINHO!", "roxo"), call(round(tm, 2), "RAWR! FAZ COM A MÃO!", "vermelho")],
                        "atores": {c: g(x, ("dance", 0.05 * j, "festa"), ("rawr", round(tm + 0.05 * j, 2)), turn=tv_) for j, (c, x, tv_) in
                                   enumerate(zip(trio, (380, 960, 1540), (0.2, 0.0, -0.2)))}})
        else:                                              # RAWR de pertinho
            q, cen = cfg["close"]
            if cen.startswith("mon_") and cen not in (QUARTO, COZ):
                out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "cantam": [q], "fx": ["estrelas"],
                            "callout": [call(round(tm, 2), "RAWR!", "vermelho")],
                            "atores": {q: g(960, ("dance", 0.0, "festa"), ("rawr", round(tm, 2))) | {"depth": 1.1 if q == ZU else 1.3}}})
            elif n == 2:                                   # RAWR dividido: Zuzu no quarto (BUSTO: chifre no quadro) × Nhoque no salão
                out.append(R.dividida({"cenario": QUARTO, "camera": {"x": 1560, "y": 520, "zoom": 1.3, "zoom_fim": 1.36}, "cantam": [ZU],
                                       "atores": {ZU: a(1560, ("dance", 0.0, "cabeca"), ("rawr", round(tm, 2)))}},     # longe do pôster amarelo (chifre)
                                      {"cenario": FESTA, "camera": cab(1300),
                                       "atores": {NH: a(1300, ("dance", 0.0, "cabeca"), ("rawr", round(tm + 0.15, 2)))}},
                                      linhas=2, layout="vertical", callout=[call(round(tm, 2), "RAWR!", "vermelho")]))
            else:                                          # RAWR de pertinho num cenário de verdade (Zuzu em BUSTO: chifre no quadro)
                out.append({"linhas": 2, "cenario": cen, "camera": busto(1300), "cantam": [q],
                            "fx": ["estrelas"], "callout": [call(round(tm, 2), "RAWR!", "vermelho")],
                            "atores": {q: a(1300, ("dance", 0.0, "cabeca"), ("rawr", round(tm, 2)))}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 1}, {"linhas": 1}, {"seg": 6.0}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [ZU], "callout": [call(0.2, "FOFOLUCOS! RAWR!", "laranja")],
     "objetos": sombra(DRAGAO, 1300, d[0], depth=0.6, pts={"boca": abre_fecha(d[0], 0.4)}),
     "atores": {ZU: a(650, ("cheguei", 0.0), ("rawr", 0.9), turn=0.3), MI: a(1950, ("rawr", 0.35), turn=-0.3)}},
    R.dividida({"cenario": "mon_brilho_laranja", "camera": GCAM, "cantam": [TE], "atores": {TE: g(960, ("rawr", 0.1)) | {"depth": 1.3}}},
               {"cenario": "mon_raios_azul", "camera": GCAM, "atores": {GO: g(960, ("rawr", 0.25)) | {"depth": 1.3}}},
               linhas=1, layout="diagonal", callout=[call(0.1, "FOFOLUCOS!", "roxo")]),
    {**banda(PALCO, max(0.6, d[2]), extra={GO: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": max(0.6, d[3]), "cenario": SALA, "camera": corpo(1300), "titulo": "a turma dança com as sombras", "cantam": [MI],
     "objetos": {**sombra(BORBOLETA, 1300, d[3], depth=0.5, lin={"asas": (0.0, round(d[3] * 2, 1))}), **lanterna(420, d[3], direc=-0.06)},
     "atores": {TE: a(700, ("dance", 0.0, "festa"), turn=0.3), MI: a(1950, ("dance", 0.05, "festa"), turn=-0.3)}},
]


# ───────── ponte: os comandos do teatro de sombras ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4 + [{"linhas": 2}, {"linhas": 1}, {"linhas": 2}])
d = dur(T)
tb = em(T[6][0], T[6][2], "voando", default=round(d[6] * 0.5, 2))
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": busto(1150, 600), "cantam": [NH], "callout": [call(0.1, "ACENDE A LANTERNA!", "amarelo")],
     "objetos": lanterna(1300, d[0], direc=-0.1, liga_em=0.35, depth=0.6),
     "atores": {NH: a(950, ("point", 0.1), turn=0.35, expr="joy")}},
    R.dividida({"cenario": SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58}, "cantam": [NH],
                "objetos": {**lanterna(1000, d[1], direc=-0.1, depth=0.5), **sombra(COELHO, 1650, d[1], depth=0.5)},
                "atores": {NH: a(1300, ("rawr", 0.2), turn=0.3)}},
               {"cenario": QUARTO, "camera": {"x": 1300, "y": 560, "zoom": 1.5, "zoom_fim": 1.58},
                "objetos": {**lanterna(1000, d[1], direc=-0.1, depth=0.5), **sombra(DRAGAO, 1650, d[1], depth=0.5, key="sb3")},
                "atores": {TE: a(1300, ("rawr", 0.35), turn=0.3)}},
               linhas=1, layout="vertical", callout=[call(0.1, "PÕE A MÃO NA FRENTE!", "verde")]),
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.1, "ABRE E FECHA A BOCA…", "laranja")],
     "objetos": {**sombra(JACARE, 1550, d[2], depth=0.6, pts={"boca": abre_fecha(d[2], 0.35)}), **lanterna(620, d[2], direc=-0.08)},
     "atores": {GO: a(950, ("rawr", 0.1), turn=0.4)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1450), "cantam": [GO], "tremor": [0.3], "fx": ["estrelas"],
     "callout": [call(0.1, "É UM JACARÉ VALENTE!", "verde")],
     "objetos": sombra(JACARE, 1500, d[3], depth=0.72, pts={"boca": abre_fecha(d[3], 0.3)}),
     "atores": {GO: a(900, ("laugh", 0.1), turn=0.4, expr="joy")}},
    {"linhas": 2, "cenario": "mon_xadrez_verde", "camera": GCAM, "cantam": [TE],
     "callout": [call(0.1, "E MAIS!", "verde"), call(round(d[4] * 0.4, 2), "CRUZA OS DEDÕES!", "amarelo")],
     "atores": {TE: g(960, ("point", 0.3)) | {"depth": 1.3}}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1350), "cantam": [MI], "callout": [call(0.1, "BATE AS MÃOS DEVAGAR!", "rosa")],
     "objetos": sombra(BORBOLETA, 1750, d[5], depth=0.5, lin={"asas": (0.0, round(d[5] * 1.2, 1))}),
     "atores": {MI: a(1150, ("fofinho", 0.1), turn=0.35)}},
    {"linhas": 2, "cenario": SALA, "camera": corpo(1300), "cantam": [MI], "fx": ["coracoes"],
     "callout": [call(0.1, "É UMA BORBOLETA…", "rosa"), call(round(tb, 2), "VOANDO PELO AR!", "azul")],
     "objetos": {**sombra(BORBOLETA, 1150, d[6], depth=0.55, y=700, lin={"asas": (0.0, round(d[6] * 2.4, 1)), "x": (1150, 1750)}),
                 **lanterna(560, d[6], direc=-0.08)},
     "atores": {MI: a(950, ("estatua", 0.0), turn=0.4, expr="joy")}},
]


# ───────── 2º verso: a VIRADA — a sombra gigante era uma formiguinha! ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
tp_ = max(0.05, min(em(T[2][0], T[2][2], "pulo", default=0.4), d[2] - 0.6) - 0.2)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [BI], "callout": [call(0.2, "DE REPENTE, NA PAREDE…", "roxo")],
     "objetos": {**sombra(FORMIGA, 1550, d[0], depth=0.75, liga_em=round(d[0] * 0.5, 2), key="sb2"), **lanterna(1950, d[0], direc=-0.42)},
     "atores": {BI: a(450, ("dance", 0.0, "festa"), turn=0.3), TE: a(1100, ("dance", 0.1, "festa"), turn=0.2)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [BI], "tremor": [0.2, 0.9],
     "callout": [call(0.1, "UMA SOMBRA ASSUSTADORA!", "vermelho")],
     "objetos": sombra(FORMIGA, 1300, d[1], depth=1.3, y=800, key="sb2"),
     "atores": {BI: a(520, ("take", 0.2), turn=0.3, expr="surprised"),
                TE: a(2080, ("slip", 0.3), turn=-0.3, expr="surprised")}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [BI], "callout": [call(round(tp_, 2), "TODO MUNDO DEU UM PULO!", "laranja")],
     "objetos": sombra(FORMIGA, 1300, d[2], depth=1.2, y=800, key="sb2"),
     "atores": {BI: pula(600, round(tp_, 2), turn=0.3, expr="surprised"), TE: pula(1300, round(tp_ + 0.08, 2), expr="surprised"),
                GO: pula(2000, round(tp_ + 0.16, 2), turn=-0.3, expr="surprised")}},
    R.dividida({"cenario": SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.45, "zoom_fim": 1.55}, "cantam": [GO],
                "objetos": sombra(FORMIGA, 1450, d[3], depth=0.9, key="sb2"),
                "atores": {GO: a(1050, ("shake_fist", 0.1), turn=0.35, expr="surprised")}},
               {"cenario": SALA, "camera": {"x": 1700, "y": 560, "zoom": 1.45, "zoom_fim": 1.55},
                "objetos": sombra(FORMIGA, 1300, d[3], depth=0.9, key="sb2"),
                "atores": {TE: a(1800, ("shock_reaction", 0.1), turn=-0.35, expr="surprised")}},
               linhas=1, layout="diagonal", callout=[call(0.1, "QUE BICHÃO! VAI EMBORA!", "roxo")]),
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [MI], "callout": [call(0.2, "MAS A MIMI CHEGOU PERTO…", "rosa")],
     "objetos": {**sombra(FORMIGA, 1150, d[4], depth=1.0, key="sb2"), **lanterna(1950, d[4], direc=-0.42)},
     "atores": {MI: anda(a(850, turn=0.45, expr="sly"), 1550, d[4])}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1750, 700), "cantam": [MI], "callout": [call(0.2, "E ACHOU O CULPADO!", "verde")],
     "objetos": {**lanterna(1950, d[5], direc=-0.42), "form": obj("formiga", 1930, 862, 0.35, d[5], z=6, fixo={"lado": -1.0})},
     "atores": {MI: a(1550, ("pensar", 0.0), ("point", round(d[5] * 0.55, 2)), turn=0.45, expr="surprised")}},
    {"linhas": 1, "cenario": SALA, "camera": {"x": 1880, "y": 810, "zoom": 2.1, "zoom_fim": 2.25}, "cantam": [MI], "fx": ["coracoes"],
     "callout": [call(0.2, "ERA UMA FORMIGUINHA!", "laranja")],
     "objetos": {**lanterna(1950, d[6], direc=-0.42), "form": obj("formiga", 1930, 862, 0.35, d[6], z=6, fixo={"lado": -1.0},
                                                                   lin={"aceno": (0.0, 1.0)})}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "cantam": [MI], "fx": ["coracoes"],
     "callout": [call(0.2, "NA FRENTE DO LANTERNÃO!", "amarelo")],
     "objetos": {**sombra(FORMIGA, 1050, d[7], depth=0.9, key="sb2"), **lanterna(1950, d[7], direc=-0.42),
                 "form": obj("formiga", 1930, 862, 0.35, d[7], z=6, fixo={"lado": -1.0}, lin={"aceno": (0.0, 1.0)})},
     "atores": {MI: a(1580, ("laugh", 0.1), turn=0.4, expr="joy"), BI: a(520, ("laugh", 0.2), ("abraco", round(d[7] * 0.5, 2)), turn=0.4, expr="joy")}},
]


# ───────── intervalo 2 (só instrumental) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 2, 2)
R.partes["intervalo#2"] = [
    {**banda(PALCO, d1, extra={NH: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": round(D2 - d1, 2), "cenario": SALA, "camera": corpo(1300), "fx": ["estrelas"], "titulo": "o teatro de sombras da turma",
     "cantam": [GO],
     "objetos": {**sombra(DRAGAO, 1000, D2 - d1, depth=0.6, pts={"boca": abre_fecha(D2 - d1, 0.6)}),
                 **sombra(COELHO, 1650, D2 - d1, depth=0.6, key="sb3", lin={"orelha": (0.0, 6.0)}), **lanterna(1380, D2 - d1, direc=-0.25)},
     "atores": {BI: a(480, ("dance", 0.0, "bob"), turn=0.3), GO: a(2120, ("dance", 0.05, "chute"), turn=-0.3)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"seg": 2.0}] + [{"linhas": 1}] * 4 + [{"seg": 0.0}])
d0, *d, dz = dur(T)
R.partes["final#1"] = [
    {"seg": 2.0, "cenario": SALA, "camera": corpo(1300), "fx": ["estrelas"], "titulo": "a turma apaga a lanterna", "cantam": [BI],
     "objetos": {**lanterna(1300, d0, direc=-0.25), **sombra(COELHO, 1000, d0, depth=0.55, lin={"orelha": (0.0, 2.0)}),
                 **sombra(BORBOLETA, 1620, d0, depth=0.5, key="sb3", lin={"asas": (0.0, round(d0 * 2, 1))})},
     "atores": {TE: a(450, ("wave", 0.1), turn=0.3), NH: a(2150, ("wave", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300), "cantam": [MI], "callout": [call(0.3, "E VOCÊ? FAZ SOMBRA COM A MÃO?", "roxo")],
     "objetos": sombra(BORBOLETA, 1450, d[0], depth=0.45, lin={"asas": (0.0, round(d[0] * 2, 1))}),
     "atores": {MI: a(950, ("apontar_camera", 0.3), expr="joy")}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"], "cantam": [ZU],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {ZU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": VILA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")], "cantam": [BI],
     "atores": {BI: a(850, ("cheguei", 0.1), turn=0.3), MI: a(1750, ("wave", 0.2), turn=-0.25)}},
    {"linhas": 1, "cenario": "mon_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "cantam": [GO],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {GO: g(560, ("point", 0.2), ("rawr", max(0.6, round(d[3] - 1.4, 2))), turn=0.2) | {"depth": 1.0}}},
    {"seg": max(0.6, dz), "cenario": SALA, "camera": corpo(1300), "fx": ["estrelas"], "titulo": "o RAWR da sombra de jacaré", "cantam": [GO],
     "objetos": {**sombra(JACARE, 1550, max(0.6, dz), depth=0.65, pts={"boca": abre_fecha(max(0.6, dz), 0.35)}),
                 **lanterna(620, max(0.6, dz), direc=-0.08)},
     "atores": {GO: a(950, ("rawr", 0.1), turn=0.4, expr="joy")}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.0, "cenario": CEU, "camera": corpo(1300), "fx": ["estrelas"], "cantam": [BI],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.4, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn, y=y, depth=dp, z=zz) for k, (c, x, y, dp, zz, tn) in
                enumerate(((TE, 400, 880, 0.62, 2, 0.3), (GO, 1000, 880, 0.62, 2, 0.15), (MI, 1600, 880, 0.62, 2, -0.15),
                           (ZU, 2200, 880, 0.62, 2, -0.3), (BI, 700, 975, 0.74, 3, 0.2), (NH, 1900, 975, 0.74, 3, -0.2)))}},
    {"seg": round(dfim - 3.0, 2), "cenario": SALA, "camera": corpo(1300), "flash": True, "fx": ["estrelas"],
     "callout": [call(0.2, "RAWR!", "vermelho")], "titulo": "o RAWR do dragão de sombra", "cantam": [BI],
     "objetos": {**sombra(DRAGAO, 1600, dfim - 3.0, depth=0.7, boca=1.0), **lanterna(650, dfim - 3.0, direc=-0.08)},
     "atores": {BI: a(1050, ("rawr", 0.1), turn=0.4, expr="joy")}},
]


# ── a sombra CRESCE no "grandona" (refrão): troca a profundidade fixa por keys de escala ──
def _aplica_cresce(sb):
    c = sb.pop("_cresce", None)
    if not c:
        return
    t, depth = c
    o = sb["objetos"]["sb"]
    o["depth"] = round(depth * K_SOMBRA, 3)
    o["keys"][0]["pose"]["tam"] = round(0.45 / depth, 3)
    o["keys"].append({"t": t, "pose": {"tam": 1.0}, "ease": "back"})
    o["keys"].sort(key=lambda k: k["t"])


# ── vida no cenário: nuvens no céu, bolhas nos fundos gráficos ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    if cen in (VILA, CEU):
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
            _aplica_cresce(sb)
            _ambiente(sb, round(t1 - t0, 2), j)

R.salvar("Roteiro do canal Fofolucos — 08 'Sombra de Monstrinho!' (take inteiro, 2:47, F5, nota 5): teatro de sombras à noite "
         "na sala (mon_sombras): a lanterna acende e aparecem o dragão do Bilu, o coelho do Teco, o jacaré e a borboleta "
         "(ponte); a virada: uma sombra gigante assusta a turma… era a formiguinha em cima da lanterna. "
         "Gerado por scripts/roteiros/fo08_sombra_de_monstrinho.py.")
