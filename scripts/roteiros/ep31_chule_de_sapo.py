"""Roteiro verso a verso de 31 "Chulé de Sapo!" (take inteiro, 2:31, 144 BPM, Ré# maior, estilo E17 — groove próprio,
nota 4,9; letra para 5 a 8 anos) → canais/laurinha/musicas/31_chule_de_sapo/roteiro.json.

O BAILE DO SAPO no salão de festa (`plano_salao`, é festa: bandeirinhas valem): o sapo (prop `sapo`) dança a noite
inteira, TIRA A BOTA (prop novo `bota`, sai o chulé em ondinhas verdes) e a NUVEM DE CHULÉ (prop novo `nuvem_chule`,
carinha de "eca") passa: a ROSEIRA murcha (prop novo `roseira`), a mosca cai tonta, o mosquito foge e até o GAMBÁ
(prop novo `gamba`) tapa o nariz — "Que fedor! Quem já viu?!".
Ponte = comandos (tapa o nariz, abana o ar, pula num pé só… tira a botina, joga a meia, esfrega com sabão, aprovado!).
2º verso = o banho caprichado (`plano_banheiro`, sabonete e bolhas), volta ao baile cheiroso… mas calça a MEIA SUJA que
dormiu no porão (prop novo `meia`, suja=1) e o chulé volta correndo: "Meia limpa, sapão!".
Narrador = Luisinho (a turma reage tapando o nariz: ação `tampar_nariz`). Padrão: CABEÇA / BUSTO / CORPO.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep31_chule_de_sapo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, LA, LU, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("laurinha/ep31-chule-de-sapo", "31_chule_de_sapo", "luisinho")
SALAO, LAGOA, JARDIM, BANHO, CASA = "plano_salao", "plano_lagoa", "plano_jardim", "plano_banheiro", "plano_casa_frente"
MA = "mamae"
CHAO = 930
CSAPO = {"x": 1300, "y": 560, "zoom": 1.25, "zoom_fim": 1.32}      # close do sapo (os olhos ficam no quadro)


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


def sapo(x, d, depth=1.4, y=CHAO, pula=True, croac=(), z=4, lid=0.0, **extra):
    """o sapo dançando: pulinhos no ritmo (~0,42 s = 1 batida a 144 BPM); `croac` = instantes em que abre o papo."""
    pts = {}
    if pula:
        pts["pulo"] = [(round(0.21 * j, 2), 0.45 if j % 2 else 0.0) for j in range(int(max(0.6, d) / 0.21))]
    if croac:
        pts["croac"] = [(t + dd, v) for t in croac for dd, v in ((0.0, 1.0), (0.35, 0.0))]
    return obj("sapo", x, y, depth, d, z=z, fixo={"lid": lid, **extra}, pts=pts)


def nuvem(x0, x1, d, y=760, depth=1.0, tam=(1.0, 1.0), z=5):
    return obj("nuvem_chule", x0, y, depth, d, z=z, lin={"x": (x0, x1), "onda": (0.0, round(d * 1.5, 1)), "tam": tam})


def banda(d, extra=None):
    """a banda toca NO BAILE: Laurinha no teclado, Luisinho na bateria, o sapo dança na frente à direita."""
    p = R.banda(SALAO, d, teclado=True, sax=LA, bateria=LU, cam={"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["objetos"]["sapo"] = sapo(2300, d, depth=1.1)
    p["cantam"] = [LU]
    return p


def nariz(quem, x, t=0.2, turn=0.0, **kw):
    return a(x, ("tampar_nariz", t), turn=turn, **kw) | {"expr": "azedo"}


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}])
d = dur(T)
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": SALAO, "camera": corpo(1300), "titulo": "o baile do sapo",
     "callout": [call(0.3, "QUE CHULÉ!", "verde")], "objetos": {"sapo": sapo(1300, d[0], depth=1.5), "nv": nuvem(2500, 1700, d[0], tam=(0.4, 0.8))},
     "atores": {LA: a(500, ("dance", 0.0, "festa"), turn=0.3), LU: a(2100, ("tampar_nariz", round(d[0] * 0.6, 2)), turn=-0.3)}},
    {"linhas": 1, "cenario": SALAO, "camera": busto(1300), "callout": [call(0.2, "QUE CHULÉ!", "verde")],
     "atores": {LU: nariz(LU, 1300, 0.1)}},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": GCAM, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "LAURINHA E LUISINHO!", "roxo")],
     "atores": {LA: g(640, ("wave", 0.1), turn=0.25) | {"depth": 1.05}, LU: g(1280, ("wave", 0.2), turn=-0.25) | {"depth": 1.05}}},
]


# ───────── 1º verso: o baile, a bota e a nuvem de chulé ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": SALAO, "camera": corpo(1300), "callout": [call(0.3, "O SAPO FOI PRO BAILE!", "verde")],
     "objetos": {"sapo": sapo(1300, d[0], depth=1.5, croac=(0.3,))},
     "atores": {LA: a(500, ("dance", 0.0, "roda"), turn=0.3), MA: a(2100, ("dance", 0.1, "palmas"), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_bolinhas_verde", "camera": GCAM, "fx": ["confete"], "callout": [call(0.2, "A NOITE INTEIRA!", "roxo")],
     "objetos": {"sapo": sapo(960, d[1], depth=2.0, y=1000)}},
    {"linhas": 1, "cenario": SALAO, "camera": CSAPO, "callout": [call(0.4, "TIROU A BOTA…", "laranja")],
     "objetos": {"sapo": sapo(1050, d[2], depth=1.6, pula=False, lid=0.0),
                 "bota": obj("bota", 1720, CHAO, 1.3, d[2], z=5, lin={"cheiro": (0.0, 1.0), "onda": (0.0, 2.0)},
                             pts={"y": [(0.25, 800), (0.5, CHAO)]})}},
    {"linhas": 1, "cenario": SALAO, "camera": CSAPO, "callout": [call(0.3, "MURCHOU A ROSEIRA!", "vermelho")],
     "objetos": {"rosa": obj("roseira", 1150, CHAO, 0.95, d[3], z=3, pts={"murcha": [(0.4, 1.0)]}),
                 "nv": nuvem(2300, 1500, d[3], y=820, depth=0.9, tam=(0.8, 1.0))}},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": GCAM, "callout": [call(0.2, "A MOSCA CAIU TONTA!", "amarelo")],
     "objetos": {"mosca": obj("mosquinha", 960, 380, 2.0, d[4], z=4, fixo={"asa": 0.0},
                              pts={"y": [(0.5, 860)], "giro": [(0.5, 2.6)], "asa": [(0.4, 3.0)], "pousada": [(0.7, 1.0)]})}},
    {"linhas": 1, "cenario": SALAO, "camera": corpo(1300), "callout": [call(0.2, "O MOSQUITO FUGIU!", "azul")],
     "objetos": {"mosq": obj("mosquinha", 700, 520, 1.6, d[5], z=5, lin={"x": (700, 2700), "asa": (0.0, round(d[5] * 12, 1))},
                             pts={"y": [(0.4, 380), (0.9, 470)]}),
                 "nv": nuvem(200, 900, d[5], y=860, depth=1.0)}},
    {"linhas": 1, "cenario": JARDIM, "camera": corpo(1300), "callout": [call(0.3, "ATÉ O GAMBÁ!", "roxo")],
     "objetos": {"gamba": obj("gamba", 1300, CHAO, 1.5, d[6], z=4, lin={"rabo": (0.0, 2.0)}, pts={"tapa": [(0.5, 1.0)]}),
                 "nv": nuvem(2500, 2000, d[6], y=780, depth=0.9, tam=(0.6, 0.9))}},
    {"linhas": 1, "cenario": JARDIM, "camera": CSAPO, "callout": [call(0.1, "QUE FEDOR! QUEM JÁ VIU?!", "vermelho")],
     "objetos": {"gamba": obj("gamba", 1300, CHAO, 1.25, d[7], z=4, fixo={"tapa": 1.0}, lin={"rabo": (0.0, 3.0)})}},
]


# ───────── refrão: que chulé! chulé de sapo, ê! vai lavar o pé! ─────────
REF = {
    1: dict(nuvem=(SALAO, (LA, MA)), danca=("danca_xadrez_verde", (LA, LU, MA)), close=(LA, CASA)),
    2: dict(nuvem=(LAGOA, (LU, LA)), danca=("danca_bolinhas_laranja", (LU, MA, LA)), close=(MA, CASA)),
    3: dict(nuvem=(SALAO, (MA, LU)), danca=("danca_raios_azul", (MA, LA, LU)), close=(LU, JARDIM)),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        if i % 4 == 0:                                     # "Que chulé! Chulé de sapo, ê!" — a nuvem passa, todos tapam o nariz
            cen, (q1, q2) = cfg["nuvem"]
            out.append({"linhas": 2, "cenario": cen, "camera": corpo(1300), "cantam": [LU],
                        "callout": [call(0.1, "QUE CHULÉ!", "verde"), call(round(dd * 0.5, 2), "CHULÉ DE SAPO, Ê!", "roxo")],
                        "objetos": {"nv": nuvem(2600, 0, dd, y=700, depth=1.0), "sapo": sapo(1300, dd, depth=1.3)},
                        "atores": {q1: nariz(q1, 450, 0.3, turn=0.3), q2: nariz(q2, 2150, 0.5, turn=-0.3)}})
        elif i % 4 == 1:                                   # "Vai lavar o pé!" — CABEÇA do sapo, close de "ops"
            out.append({"linhas": 2, "cenario": LAGOA, "camera": CSAPO, "cantam": [LU],
                        "callout": [call(round(dd * 0.45, 2), "VAI LAVAR O PÉ!", "azul")],
                        "objetos": {"sapo": sapo(1150, dd, depth=1.9, pula=False, croac=(0.2, round(dd * 0.55, 2))),
                                    "bota": obj("bota", 1780, CHAO, 1.3, dd, z=5, fixo={"cheiro": 1.0}, lin={"onda": (0.0, 2.0)})}})
        elif i % 4 == 2:                                   # a dança do chulé no fundo colorido
            cen, quem = cfg["danca"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "flash": n == 1, "cantam": [quem[0]],
                        "callout": [call(0.1, "QUE CHULÉ!", "verde")],
                        "atores": {c: g(x, ("dance", 0.05 * j, st), turn=tv) for j, (c, x, tv, st) in
                                   enumerate(zip(quem, (380, 960, 1540), (0.2, 0.0, -0.2), ("pezinho", "festa", "pezinho")))}})
        else:                                              # CABEÇA: tapa o nariz e manda lavar
            quem, cen = cfg["close"]
            out.append({"linhas": 2, "cenario": cen, "camera": cab(1300), "cantam": [quem],
                        "callout": [call(round(dd * 0.4, 2), "VAI LAVAR O PÉ!", "azul")],
                        "atores": {quem: a(1300, ("tampar_nariz", 0.1, round(dd * 0.45, 2)), ("point", round(dd * 0.5, 2)))}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 2}, {"seg": 7.0}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 2, "cenario": CASA, "camera": cab(1300), "cantam": [LU], "callout": [call(0.2, "ZUM-ZUM, QUE MASSA!", "laranja")],
     "atores": {LU: a(1300, ("apontar_camera", 0.1), ("wave", 2.0))}},
    {**banda(max(0.6, d[1])), "titulo": "a banda no baile"},
    {"seg": max(0.6, d[2]), "cenario": "danca_ondas_verde", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança com o sapo",
     "objetos": {"sapo": sapo(960, d[2], depth=1.6, y=1000)},
     "atores": {LA: g(330, ("dance", 0.0, "cintura"), turn=0.2), LU: g(1600, ("dance", 0.0, "bracos"), turn=-0.2)}},
]


# ───────── ponte: comandos ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4 + [{"linhas": 2}] + [{"linhas": 1}] * 3)     # "E mais!" junto com "Tira a botina!"
d = dur(T)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": "danca_raios_laranja", "camera": GCAM, "callout": [call(0.1, "TAPA O NARIZ!", "laranja")],
     "atores": {LU: g(960, ("tampar_nariz", 0.0)) | {"depth": 1.15, "expr": "azedo"}}},
    {"linhas": 1, "cenario": "danca_xadrez_amarelo", "camera": GCAM, "callout": [call(0.1, "ABANA O AR!", "azul")],
     "atores": {LA: g(960, ("wave", 0.0)) | {"depth": 1.15}}},
    {"linhas": 1, "cenario": "danca_bolinhas_rosa", "camera": GCAM, "callout": [call(0.1, "PULA NUM PÉ SÓ…", "rosa")],
     "atores": {MA: g(960, ("dance", 0.0, "pezinho")) | {"depth": 1.15}}},
    {"linhas": 1, "cenario": "danca_raios_azul", "camera": GCAM, "callout": [call(0.1, "E NO OUTRO, SEM PARAR!", "verde")],
     "atores": {LU: g(640, ("dance", 0.0, "pezinho"), turn=0.2), LA: g(1280, ("dance", 0.05, "pezinho"), turn=-0.2)}},
    {"linhas": 2, "cenario": SALAO, "camera": CSAPO, "callout": [call(0.1, "E MAIS! TIRA A BOTINA!", "laranja")],
     "objetos": {"sapo": sapo(1050, d[4], depth=1.6, pula=False),
                 "bota": obj("bota", 1720, CHAO, 1.3, d[4], z=5, fixo={"cheiro": 0.6}, lin={"onda": (0.0, 2.0)},
                             pts={"y": [(0.6, 800), (0.85, CHAO)]})}},
    {"linhas": 1, "cenario": SALAO, "camera": corpo(1300), "callout": [call(0.1, "JOGA A MEIA PRO LADO!", "vermelho")],
     "objetos": {"sapo": sapo(1000, d[5], depth=1.5),
                 "meia": obj("meia", 1100, CHAO, 1.2, d[5], z=5, fixo={"suja": 0.7}, lin={"onda": (0.0, 2.0)},
                             pts={"x": [(0.5, 2200)], "y": [(0.3, 600), (0.7, CHAO)]})}},
    {"linhas": 1, "cenario": BANHO, "camera": CSAPO, "fx": ["bolhas"], "callout": [call(0.1, "ESFREGA COM SABÃO…", "azul")],
     "objetos": {"sapo": sapo(1150, d[6], depth=1.7, pula=False, lid=1.0),
                 "sab": obj("sabonete", 1500, CHAO, 1.4, d[6], z=5, pts={"pulo": [(0.2, 1.0), (0.5, 0.0), (0.8, 1.0), (1.1, 0.0)],
                                                                        "bolhas": [(0.3, 1.0)]})}},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "camera": GCAM, "fx": ["estrelas"], "flash": True,
     "callout": [call(0.1, "TÁ CHEIROSO? APROVADO!", "verde")],
     "objetos": {"sapo": sapo(1300, d[7], depth=1.7, y=1000)},
     "atores": {LU: g(560, ("bacana", 0.2), turn=0.25) | {"depth": 1.0}}},
]


# ───────── 2º verso: o banho, o baile de novo… e a MEIA SUJA ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": BANHO, "camera": corpo(1300), "fx": ["bolhas"], "callout": [call(0.2, "ENTROU NO BANHO!", "azul")],
     "objetos": {"sapo": sapo(1300, d[0], depth=1.6, croac=(0.4,)),
                 "bolha": obj("bolha", 1700, 820, 0.7, d[0], z=5, pts={"y": [(0.8, 500)]})}},
    {"linhas": 1, "cenario": BANHO, "camera": CSAPO, "fx": ["bolhas"], "callout": [call(0.2, "DEDO POR DEDO!", "verde")],
     "objetos": {"sapo": sapo(1150, d[1], depth=1.8, pula=False, lid=1.0),
                 "sab": obj("sabonete", 1560, CHAO, 1.4, d[1], z=5, pts={"pulo": [(0.2, 1.0), (0.5, 0.0), (0.8, 1.0)], "bolhas": [(0.2, 1.0)]})}},
    {"linhas": 1, "cenario": "danca_raios_rosa", "camera": GCAM, "fx": ["coracoes"], "callout": [call(0.2, "CHEIRANDO A SABONETE!", "rosa")],
     "objetos": {"sapo": sapo(960, d[2], depth=2.0, y=1000)}},
    {"linhas": 1, "cenario": SALAO, "camera": corpo(1300), "callout": [call(0.2, "PRO BAILE MAIS CEDO!", "roxo")],
     "objetos": {"sapo": sapo(1300, d[3], depth=1.5)},
     "atores": {LA: a(500, ("wave", 0.2), turn=0.3), MA: a(2100, ("dance", 0.1, "palmas"), turn=-0.3)}},
    {"linhas": 1, "cenario": SALAO, "camera": CSAPO, "callout": [call(0.2, "A MEIA SUJA…", "laranja")],
     "objetos": {"meia": obj("meia", 1300, CHAO, 1.2, d[4], z=4, fixo={"suja": 1.0}, lin={"onda": (0.0, 2.5)})}},
    {"linhas": 1, "cenario": "danca_xadrez_laranja", "camera": GCAM, "callout": [call(0.2, "QUE DORMIU NO PORÃO…", "roxo")],
     "objetos": {"sapo": sapo(780, d[5], depth=1.6, y=1000, pula=False),
                 "meia": obj("meia", 1260, 1000, 1.5, d[5], z=4, fixo={"suja": 1.0}, lin={"onda": (0.0, 2.5)})}},
    {"linhas": 1, "cenario": SALAO, "camera": corpo(1300), "callout": [call(0.1, "O CHULÉ VOLTOU CORRENDO!", "verde")],
     "objetos": {"nv": nuvem(-200, 1300, d[6], y=760, depth=1.1, tam=(0.6, 1.1)), "sapo": sapo(1300, d[6], depth=1.3)},
     "atores": {LA: nariz(LA, 450, 0.4, turn=0.3), MA: nariz(MA, 2150, 0.5, turn=-0.3)}},
    {"linhas": 1, "cenario": CASA, "camera": cab(1300), "callout": [call(0.1, "MEIA LIMPA, SAPÃO!", "azul")],
     "atores": {LU: a(1300, ("tampar_nariz", 0.0, 0.6), ("point", 0.6))}},
]


# ───────── intervalo 2 (só instrumental) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 2, 2)
R.partes["intervalo#2"] = [
    {**banda(d1), "titulo": "a banda no baile"},
    {"seg": round(D2 - d1, 2), "cenario": "danca_xadrez_verde", "camera": GCAM, "fx": ["confete"], "titulo": "o sapo de meia limpa dança",
     "objetos": {"sapo": sapo(960, D2 - d1, depth=1.6, y=1000),
                 "meia": obj("meia", 1500, 1000, 1.0, D2 - d1, z=4, fixo={"suja": 0.0, "cor": 2.0})},
     "atores": {MA: g(330, ("dance", 0.0, "palmas"), turn=0.2), LA: g(1700, ("dance", 0.1, "roda"), turn=-0.2)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": CASA, "camera": cab(1300), "callout": [call(0.2, "E O SEU PÉ? TÁ CHEIROSO?", "rosa")],
     "atores": {LU: a(1300, ("apontar_camera", 0.1))}},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LA: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": CASA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {LU: a(950, ("point", 0.1), turn=0.3), MA: a(1650, ("wave", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LU: g(560, ("point", 0.2), turn=0.2) | {"depth": 1.0}}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.4, "cenario": SALAO, "camera": corpo(1300), "fx": ["coracoes"],
     "callout": [call(0.2, "QUE CHULÉ!", "verde"), call(1.5, "TCHAU!", "amarelo")],
     "objetos": {"sapo": sapo(1300, 3.4, depth=1.4, croac=(1.4,))},
     "atores": {LA: a(500, ("wave", 0.0), turn=0.3), LU: a(2100, ("wave", 0.1), turn=-0.3)}},
    {"seg": round(dfim - 3.4, 2), "cenario": LAGOA, "camera": CSAPO, "flash": True, "callout": [call(0.2, "PLOFT!", "rosa")],
     "titulo": "o último croac", "objetos": {"sapo": sapo(1300, dfim - 3.4, depth=1.9, pula=False, croac=(0.2, 1.2, 2.4))}},
]

R.salvar("Roteiro de 31 'Chulé de Sapo!' (take inteiro, 2:31, E17, nota 4,9, letra 5–8): o baile do sapo (plano_salao), a bota, "
         "a nuvem de chulé, a roseira murcha, a mosca tonta, o mosquito fugindo e o GAMBÁ tapando o nariz; ponte de comandos; "
         "o banho e a virada da MEIA SUJA. Gerado por scripts/roteiros/ep31_chule_de_sapo.py.")
