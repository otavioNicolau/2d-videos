"""Roteiro verso a verso do canal FOFOLUCOS — 07 "Festa Surpresa do Nhoque!" (take inteiro, 2:34, 136 BPM, Sol maior, estilo
F5, nota 4,8; letra 5 a 8 anos) → canais/fofolucos/musicas/07_festa_surpresa/roteiro.json.

A FESTA SURPRESA do aniversário do Nhoque (o comilão) no SALÃO DE FESTA (cenário novo `mon_festa`: parede creme — ninguém
some na frente —, bandeirinhas, porta à direita): a turma monta tudo em segredo e dá tudo meio errado — a antena do Teco
fura o BALÃO (prop novo `balao`, ploc!), o Bilu sopra a vela do BOLO (prop novo `bolo_aniversario`) antes da hora.
Refrão = "psiu!" na ponta do pé e todo mundo escondidinho atrás do SOFÁ (prop novo `sofa`). Ponte = comandos da surpresa.
2º verso = a VIRADA: a porta abre, todos gritam SURPRESA… era o Zuzu com o bolo, que cai sentado (bolo amassado); o Nhoque
entra atrás, chora de alegria e abraça a turma.
Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — CABEÇA / BUSTO / CORPO, espaço ≥ 430, chifres/antenas no quadro, closes do Zuzu
em BUSTO, nunca monstrinho na frente da própria cor, nunca "monstro".
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo07_festa_surpresa.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("fofolucos/ep07-festa-surpresa", "07_festa_surpresa", "nhoque")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
FESTA, VILA, PALCO, CEU = "mon_festa", "mon_vila", "mon_palco", "mon_abertura"
CHAO = 935


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


def baloes(d, xs=((500, 0), (2100, 3)), y=560, depth=0.7, z=1):
    """balões soltos flutuando no salão (atrás da turma)."""
    return {f"bal{j}": obj("balao", x, y, depth, d, z=z, fixo={"cor": float(c)}, lin={"balanco": (0.0, round(d * 0.6, 1))})
            for j, (x, c) in enumerate(xs)}


def sofa(d, x=1300, depth=0.6):
    return obj("sofa", x, CHAO, depth, d, z=4)


def atras_do_sofa(quem_xs, d, sai_em=None, depth=0.9):
    """monstrinhos escondidos atrás do sofá (só o topo aparece); `sai_em` = pulam pra cima (SURPRESA!)."""
    out = {}
    for j, (q, x) in enumerate(quem_xs):
        at = a(x, *([("rawr", round(sai_em + 0.1, 2))] if sai_em is not None else [("estatua", 0.0)]), y=CHAO, depth=depth, z=2,
               turn=(0.25 if x < 1300 else -0.25))
        if sai_em is not None:
            at["keys"] = [{"t": 0.0, "pose": {"y": float(CHAO)}, "ease": "step"},
                          {"t": round(sai_em, 2), "pose": {"y": float(CHAO)}, "ease": "step"},
                          {"t": round(sai_em + 0.25, 2), "pose": {"y": float(CHAO - 170)}, "ease": "out"}]
        out[q] = at
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
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "titulo": "a festa surpresa do Nhoque", "cantam": [MI], "fx": ["confete"],
     "callout": [call(0.5, "FESTA SURPRESA!", "rosa")], "objetos": baloes(d[0], xs=((450, 0), (1300, 2), (2150, 1))),
     "atores": {BI: a(700, ("dance", 0.0, "festa"), turn=0.3), MI: a(1900, ("dance", 0.1, "festa"), turn=-0.3)}},
    {"linhas": 1, "cenario": FESTA, "camera": busto(1300), "cantam": [MI], "callout": [call(0.2, "PSIU! NINGUÉM PODE CONTAR!", "roxo")],
     "atores": {MI: a(1000, ("estatua", 0.0), turn=0.3, expr="sly"), BI: a(1600, ("estatua", 0.0), turn=-0.3, expr="sly")}},
    {"linhas": 1, "cenario": "mon_raios_laranja", "camera": GCAM, "flash": True, "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.1, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {TE: g(210, ("rawr", 0.3), turn=0.2), GO: g(710, ("rawr", 0.38)), BI: g(1210, ("rawr", 0.46)),
                MI: g(1710, ("rawr", 0.54), turn=-0.2)}},
    {**banda(PALCO, max(0.6, d[3]), extra={TE: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: o aniversário do Nhoque, o balão e a vela ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
tv = em(T[7][0], T[7][2], "apagou", default=round(d[7] * 0.6, 2))
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "cantam": [NH], "fx": ["confete"], "callout": [call(0.3, "HOJE É ANIVERSÁRIO!", "laranja")],
     "objetos": baloes(d[0]), "atores": {TE: a(800, ("dance", 0.0, "festa"), turn=0.3), GO: a(1800, ("dance", 0.1, "festa"), turn=-0.3)}},
    {"linhas": 1, "cenario": "mon_brilho_azul", "camera": GCAM, "cantam": [NH], "callout": [call(0.2, "DO NHOQUE, O COMILÃO!", "vermelho")],
     "atores": {NH: g(960, ("eat", 0.2)) | {"depth": 1.3, "segura": "biscoito_mordido", "expr": "joy"}}},
    {"linhas": 1, "cenario": FESTA, "camera": busto(1300), "cantam": [NH], "callout": [call(0.2, "A TURMA FAZ SEGREDO…", "roxo")],
     "atores": {MI: a(1000, ("estatua", 0.0), turn=0.45, expr="sly"), BI: a(1600, ("estatua", 0.0), turn=-0.45, expr="sly")}},
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "cantam": [NH], "fx": ["confete"], "callout": [call(0.2, "PRA MONTAR O FESTÃO!", "amarelo")],
     "objetos": {**baloes(d[3], xs=((420, 1), (2180, 4))), "bolo": obj("bolo_aniversario", 1300, CHAO + 10, 0.75, d[3], z=3)},
     "atores": {GO: a(700, ("dance", 0.0, "festa"), turn=0.3), MI: a(1900, ("dance", 0.1, "festa"), turn=-0.3)}},
    {"linhas": 1, "cenario": FESTA, "camera": busto(1300), "cantam": [NH], "callout": [call(0.2, "O TECO ENCHE O BALÃO…", "roxo")],
     "objetos": {"bal0": obj("balao", 1650, 720, 0.9, d[4], z=4, fixo={"cor": 0.0}, lin={"enche": (0.15, 1.0)})},
     "atores": {TE: a(1150, ("estatua", 0.0), turn=0.3)}},
    {"linhas": 1, "cenario": FESTA, "camera": busto(1300, 480), "cantam": [NH], "tremor": [0.3],
     "callout": [call(0.2, "PLOC! A ANTENA FUROU!", "vermelho")],
     "objetos": {"bal0": obj("balao", 1300, 560, 0.75, d[5], z=4, fixo={"cor": 0.0}, pts={"estoura": [(0.25, 0.01), (0.9, 1.0)]})},
     "atores": {TE: a(1300, ("shock_reaction", 0.25), expr="surprised")}},
    {"linhas": 1, "cenario": "mon_raios_roxo", "camera": GCAM, "cantam": [NH], "callout": [call(0.2, "O BILU, TODO ANIMADO…", "azul")],
     "atores": {BI: g(960, ("dance", 0.0, "festa")) | {"depth": 1.25}}},
    {"linhas": 1, "cenario": FESTA, "camera": busto(1300), "cantam": [NH], "callout": [call(round(tv, 2), "A VELA APAGOU!", "laranja")],
     "objetos": {"bolo": obj("bolo_aniversario", 1600, CHAO + 30, 1.0, d[7], z=4, fixo={"vela": 1.0},
                             pts={"vela": [(round(tv, 2), 0.0)], "fumaca": [(round(d[7] - 0.1, 2), 2.0)]})},
     "atores": {BI: a(1050, ("estatua", 0.0), turn=0.35, expr="surprised")}},
]


# ───────── refrão: festa surpresa! psiu! fala baixinho! todo mundo escondidinho! ─────────
REF = {
    1: dict(pe=(BI, MI), esconde=((TE, 1050), (GO, 1550)), danca=("mon_xadrez_azul", (MI, GO, ZU)), close=(MI, "mon_raios_azul")),
    2: dict(pe=(TE, GO), esconde=((BI, 1050), (MI, 1550)), danca=("mon_xadrez_verde", (BI, MI, TE)), close=(TE, "mon_brilho_laranja")),
    3: dict(pe=(MI, BI), esconde=((GO, 1050), (TE, 1550)), danca=("mon_xadrez_roxo", (GO, MI, BI)), close=(BI, "mon_raios_rosa")),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        if i % 4 == 0:                                     # "Festa surpresa! Psiu! Fala baixinho!" — na ponta do pé
            q1, q2 = cfg["pe"]
            out.append({"linhas": 2, "cenario": FESTA, "camera": corpo(1300), "cantam": [q1],
                        "callout": [call(0.1, "FESTA SURPRESA!", "rosa"), call(round(dd * 0.5, 2), "PSIU! FALA BAIXINHO!", "roxo")],
                        "objetos": baloes(dd),
                        "atores": {q1: anda(a(500, turn=0.45, expr="sly"), 1000, dd), q2: anda(a(2100, turn=-0.45, expr="sly"), 1650, dd)}})
        elif i % 4 == 1:                                   # "Todo mundo escondidinho!" — atrás do sofá
            out.append({"linhas": 2, "cenario": FESTA, "camera": corpo(1300), "cantam": [cfg["esconde"][0][0]],
                        "callout": [call(0.1, "FESTA SURPRESA!", "rosa"), call(round(dd * 0.5, 2), "TODO MUNDO ESCONDIDINHO!", "verde")],
                        "objetos": {"sofa": sofa(dd)}, "atores": atras_do_sofa(cfg["esconde"], dd)})
        elif i % 4 == 2:                                   # a dança da festa no fundo colorido
            cen, trio = cfg["danca"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "flash": n == 1, "cantam": [trio[0]],
                        "callout": [call(0.1, "FESTA SURPRESA!", "rosa")],
                        "atores": {c: g(x, ("dance", 0.05 * j, st), turn=tv_) for j, (c, x, tv_, st) in
                                   enumerate(zip(trio, (380, 960, 1540), (0.2, 0.0, -0.2), ("festa", "chute", "festa")))}})
        else:                                              # PSIU de pertinho
            q, cen = cfg["close"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "cantam": [q], "fx": ["estrelas"],
                        "callout": [call(round(dd * 0.5, 2), "PSIU!", "roxo")],
                        "atores": {q: g(960, ("estatua", 0.0)) | {"depth": 1.35, "expr": "sly"}}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 1}, {"linhas": 1}, {"seg": 6.0}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 1, "cenario": "mon_raios_roxo", "camera": GCAM, "cantam": [ZU], "callout": [call(0.2, "FOFOLUCOS! RAWR!", "laranja")],
     "atores": {ZU: g(700, ("rawr", 0.2), turn=0.2) | {"depth": 1.1}, BI: g(1300, ("rawr", 0.35), turn=-0.2) | {"depth": 1.1}}},
    {"linhas": 1, "cenario": "mon_brilho_laranja", "camera": GCAM, "cantam": [MI], "callout": [call(0.1, "FOFOLUCOS!", "roxo")],
     "atores": {MI: g(960, ("rawr", 0.1)) | {"depth": 1.3}}},
    {**banda(PALCO, max(0.6, d[2]), extra={GO: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": max(0.6, d[3]), "cenario": FESTA, "camera": corpo(1300), "fx": ["confete"], "titulo": "a turma dança no salão", "cantam": [TE],
     "objetos": baloes(d[3], xs=((420, 2), (2180, 0))),
     "atores": {TE: a(640, ("dance", 0.0, "festa"), turn=0.3), GO: a(1300, ("dance", 0.1, "chute")), MI: a(1960, ("dance", 0.05, "festa"), turn=-0.3)}},
]


# ───────── ponte: comandos da surpresa ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4 + [{"linhas": 2}] + [{"linhas": 1}] * 3)
d = dur(T)
ts = em(T[7][0], T[7][2], "surpresa", default=round(d[7] * 0.4, 2))
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": "mon_xadrez_azul", "camera": GCAM, "cantam": [MI], "callout": [call(0.1, "APAGA A LUZ!", "amarelo")],
     "atores": {MI: g(960, ("point", 0.1)) | {"depth": 1.3}}},
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "cantam": [BI], "callout": [call(0.1, "SE ESCONDE NO SOFÁ!", "verde")],
     "objetos": {"sofa": sofa(d[1])},
     "atores": {BI: a(1300, ("estatua", 0.0), y=CHAO, depth=0.9, z=2, keys=[{"t": 0.0, "pose": {"y": float(CHAO - 230)}, "ease": "step"},
                                                                          {"t": 0.5, "pose": {"y": float(CHAO)}, "ease": "out"}])}},
    {"linhas": 1, "cenario": "mon_brilho_laranja", "camera": GCAM, "cantam": [TE], "callout": [call(0.1, "SEGURA O RISO…", "roxo")],
     "atores": {TE: g(960, ("estatua", 0.0)) | {"depth": 1.3, "expr": "laughing"}}},
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1700), "cantam": [GO], "callout": [call(0.1, "ELE VEM CHEGANDO, JÁ!", "laranja")],
     "atores": {GO: a(1150, ("look_around", 0.0), turn=0.35, expr="surprised")}},
    {"linhas": 2, "cenario": "mon_raios_rosa", "camera": GCAM, "cantam": [GO],
     "callout": [call(0.1, "E MAIS!", "verde"), call(round(d[4] * 0.45, 2), "3… 2… 1…", "amarelo")],
     "atores": {GO: g(960, ("point", 0.3)) | {"depth": 1.3}}},
    {"linhas": 1, "cenario": "mon_raios_azul", "camera": GCAM, "cantam": [MI], "callout": [call(0.1, "PULA BEM ALTO!", "rosa")],
     "atores": {MI: g(960) | {"depth": 1.1, "acoes": [{"t": 0.1, "do": "jump", "dur": 0.8, "height": 160}]}}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "cantam": [BI], "callout": [call(0.1, "ABRE OS BRAÇOS…", "azul")],
     "atores": {BI: g(960, ("abraco", 0.1)) | {"depth": 1.3}}},
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "cantam": [GO], "flash": True, "fx": ["confete"],
     "callout": [call(round(ts, 2), "SURPRESA!", "vermelho")], "objetos": {"sofa": sofa(d[7])},
     "atores": atras_do_sofa(((BI, 1000), (MI, 1600)), d[7], sai_em=max(0.1, ts - 0.1))},
]


# ───────── 2º verso: a VIRADA — era o Zuzu com o bolo! ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
tq = em(T[3][0], T[3][2], "caiu", default=0.3)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1650), "cantam": [GO], "callout": [call(0.2, "A PORTA ABRIU DEVAGAR…", "roxo")],
     "objetos": {"sofa": sofa(d[0], x=1100)}, "atores": atras_do_sofa(((TE, 850), (MI, 1350)), d[0])},
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "cantam": [GO], "flash": True, "fx": ["confete"], "tremor": [0.2],
     "callout": [call(0.1, "SURPRESA!", "vermelho"), call(round(d[1] * 0.55, 2), "QUE CONFUSÃO!", "laranja")],
     "objetos": {"sofa": sofa(d[1])}, "atores": atras_do_sofa(((TE, 1000), (MI, 1600)), d[1], sai_em=0.05)},
    {"linhas": 1, "cenario": FESTA, "camera": busto(1300), "cantam": [GO], "callout": [call(0.2, "ERA O ZUZU COM O BOLO!", "laranja")],
     "objetos": {"bolo": obj("bolo_aniversario", 1300, 1140, 0.95, d[2], z=4, fixo={"vela": 1.0})},
     "atores": {ZU: a(1300, ("estatua", 0.0), expr="surprised")}},
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "cantam": [GO], "tremor": [round(tq + 0.3, 2)],
     "callout": [call(round(tq, 2), "CAIU SENTADO NO CHÃO!", "vermelho")],
     "objetos": {"bolo": obj("bolo_aniversario", 1650, CHAO + 10, 0.85, d[3], z=4, fixo={"vela": 1.0},
                             pts={"amassa": [(round(tq + 0.3, 2), 1.0)], "vela": [(round(tq + 0.3, 2), 0.0)]})},
     "atores": {ZU: a(1250, ("sit", round(tq, 2)), turn=0.2, expr="dizzy")}},
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "cantam": [GO], "callout": [call(0.2, "O NHOQUE ENTROU ATRÁS…", "vermelho")],
     "objetos": {"bolo": obj("bolo_aniversario", 1000, CHAO + 10, 0.85, d[4], z=4, fixo={"amassa": 1.0, "vela": 0.0})},
     "atores": {NH: anda(a(2300, turn=-0.4, expr="surprised"), 1700, d[4], como="walk"), ZU: a(700, ("sit", 0.0), turn=0.3, expr="dizzy")}},
    {"linhas": 1, "cenario": FESTA, "camera": cab(1300), "cantam": [GO], "fx": ["coracoes"], "callout": [call(0.2, "VIU A FESTA E CHOROU…", "azul")],
     "atores": {NH: a(1300, ("estatua", 0.0), expr="crying")}},
    {"linhas": 1, "cenario": FESTA, "camera": busto(1300), "cantam": [GO], "fx": ["coracoes"], "callout": [call(0.2, "DE ALEGRIA, É CLARO!", "rosa")],
     "atores": {NH: a(1300, ("laugh", 0.1), expr="joy")}},
    {"linhas": 1, "cenario": FESTA, "camera": corpo(1300), "cantam": [GO], "fx": ["coracoes", "confete"],
     "callout": [call(0.2, "E ABRAÇOU A TURMA!", "verde")],
     "atores": {TE: a(700, ("abraco", 0.1), turn=0.3), NH: a(1300, ("abraco", 0.0), expr="joy"), ZU: a(1900, ("abraco", 0.15), turn=-0.3)}},
]


# ───────── intervalo 2 (só instrumental) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 2, 2)
R.partes["intervalo#2"] = [
    {**banda(PALCO, d1, extra={NH: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": round(D2 - d1, 2), "cenario": FESTA, "camera": corpo(1300), "fx": ["confete"], "titulo": "a festa do Nhoque", "cantam": [NH],
     "objetos": baloes(D2 - d1, xs=((420, 3), (2180, 2))),
     "atores": {BI: a(640, ("dance", 0.0, "festa"), turn=0.3), NH: a(1300, ("dance", 0.1, "chute"), expr="joy"),
                GO: a(1960, ("dance", 0.05, "festa"), turn=-0.3)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": FESTA, "camera": cab(1300), "cantam": [NH], "callout": [call(0.2, "E VOCÊ? JÁ FEZ SURPRESA?", "roxo")],
     "atores": {NH: a(1300, ("apontar_camera", 0.1), expr="joy")}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"], "cantam": [ZU],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {ZU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": VILA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")], "cantam": [MI],
     "atores": {MI: a(900, ("point", 0.1), turn=0.3), NH: a(1700, ("wave", 0.2), turn=-0.25)}},
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
    {"linhas": 1, "seg": 3.0, "cenario": CEU, "camera": corpo(1300), "fx": ["estrelas"], "cantam": [NH],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.4, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn, y=y, depth=dp, z=zz) for k, (c, x, y, dp, zz, tn) in
                enumerate(((TE, 400, 880, 0.62, 2, 0.3), (GO, 1000, 880, 0.62, 2, 0.15), (MI, 1600, 880, 0.62, 2, -0.15),
                           (ZU, 2200, 880, 0.62, 2, -0.3), (BI, 700, 975, 0.74, 3, 0.2), (NH, 1900, 975, 0.74, 3, -0.2)))}},
    {"seg": round(dfim - 3.0, 2), "cenario": FESTA, "camera": cab(1300), "flash": True, "fx": ["confete"],
     "callout": [call(0.2, "RAWR!", "vermelho")], "titulo": "o RAWR do aniversariante", "cantam": [NH],
     "atores": {NH: a(1300, ("rawr", 0.1), expr="joy")}},
]


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
            _ambiente(sb, round(t1 - t0, 2), j)

R.salvar("Roteiro do canal Fofolucos — 07 'Festa Surpresa do Nhoque!' (take inteiro, 2:34, F5, nota 4,8): a festa surpresa no "
         "salão (mon_festa): o balão que a antena do Teco fura, a vela que o Bilu sopra antes da hora, todo mundo escondido "
         "atrás do sofá; a virada: era o Zuzu com o bolo, que cai sentado; o Nhoque chora de alegria e abraça a turma. "
         "Gerado por scripts/roteiros/fo07_festa_surpresa.py.")
