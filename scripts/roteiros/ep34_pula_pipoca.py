"""Roteiro verso a verso de 34 "Pula Pipoca!" (take 'Pula Pipoca!.wav', 2:30, 144 BPM, Ré maior, estilo E18, nota 4,9; letra
5 a 8 anos na RECEITA das letras do Fofolucos) → canais/laurinha/musicas/34_pula_pipoca/roteiro.json.

O ARRAIAL de São João (cenário novo `plano_arraial`: fim de tarde, bandeirinhas, barraquinhas da PIPOCA e do MILHO, mastro)
com a FOGUEIRA (prop novo `fogueira`). O vovô Ciço faz pipoca no PANELÃO (prop novo `panelao`: tampa, fogo, pipocas
pulando); a Laurinha e o Luisinho ficam pertinho escutando. Refrão = todo mundo pula igual pipoca (tela dividida: a
PIPOCA com carinha — prop novo `pipoca` — × quem pula). Ponte = comandos de pipoca. 2º verso = a VIRADA: silêncio, a
panela parou, "cadê?", o vovô levanta a tampa… PLOC! a última pipoca pula no BIGODÃO do vovô Ciço.
Padrão da Laurinha desde a 33: escala 1,7 (padrão do canal), no máximo 2 personagens grandes por plano, trio um passo
atrás, busto um pouco mais aberto (BU).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep34_pula_pipoca.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, LA, LU, Roteiro, cab, call, corpo  # noqa: E402

R = Roteiro("laurinha/ep34-pula-pipoca", "34_pula_pipoca", "laurinha")
ARR, CAMPO, CASA, COZ, RUA, SALA = "plano_arraial", "plano_campo", "plano_casa_frente", "plano_cozinha", "plano_rua", "plano_sala"
VC, VO, MA = "vovo_cico", "vovo", "mamae"
CHAO = 930
E = 1.7


def dur(T):
    return [round(t1 - t0, 2) for t0, t1, _ in T]


def a(x, *acoes, turn=0.0, **kw):
    out = []
    for ac in acoes:
        do, t = ac[0], (ac[1] if len(ac) > 1 else 0.0)
        d = {"t": t, "do": do, "dur": "resto"}
        if do == "dance":
            d["style"] = ac[2] if len(ac) > 2 else "festa"
        elif do == "jump":
            d = {"t": t, "do": "jump", "dur": 0.8, "height": ac[2] if len(ac) > 2 else 150}
        elif len(ac) > 2:
            d["dur"] = ac[2]
        out.append(d)
    return {"x": x, "turn": turn, "acoes": out, **kw}


def g(x, *acoes, turn=0.0):
    return a(x, *acoes, turn=turn, y=1010, depth=0.85)


def fundo(at, depth=0.85):
    return at | {"depth": depth}


def vovo(x, *acoes, alegre=True, **kw):
    kw.setdefault("expr", "joy" if alegre else "angry")
    return a(x, *acoes, **kw)


def BU(x=1300, y=580):
    return {"x": x, "y": y, "zoom": 1.32, "zoom_fim": 1.38}


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


def panelao(d, x=1300, y=CHAO + 20, depth=0.5, ploc=True, tampa=0.0, cheio=0.0, treme=True, pts=None, key="pan", z=3):
    lin = {"chama": (0.0, round(max(0.6, d) * 1.5, 2))}
    if ploc:
        lin["ploc"] = (0.0, round(max(0.6, d) * 0.9, 2))
    if treme:
        lin["treme"] = (0.0, round(max(0.6, d) * 1.2, 2))
    return {key: obj("panelao", x, y, depth, d, z=z, fixo={"tampa": tampa, "cheio": cheio, "fogo": 1.0, "ploc": 0.0, "treme": 0.0},
                     lin=lin, pts=pts)}


def fogueira(d, x=1300, y=CHAO - 10, depth=0.45, z=1):
    return {"fog": obj("fogueira", x, y, depth, d, z=z, lin={"chama": (0.0, round(max(0.6, d) * 1.4, 2))})}


def pipoca(d, x, y, depth=0.6, cara=1.0, pulos=None, key="pip", z=5, gira=1.0):
    pts = {"pulo": [p for t in (pulos or []) for p in ((round(t, 2), 0.0), (round(t + 0.25, 2), 0.5), (round(t + 0.5, 2), 1.0))]}
    return {key: obj("pipoca", x, y, depth, d, z=z, fixo={"cara": cara, "pulo": 0.0},
                     lin={"gira": (0.0, gira)}, pts=pts if pulos else None)}


def banda(d, extra=None):
    """a banda toca NO ARRAIAL (festa de São João): Laurinha no teclado, Luisinho na bateria, a vovó dança à direita."""
    p = R.banda(ARR, d, teclado=True, sax=LA, bateria=LU, cam={"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04},
                extra=extra or {VO: fundo(a(2400, ("dance", 0.0, "balanco"), turn=-0.3, expr="joy"))})
    p["cantam"] = [LA]
    return p


def em(t0, versos, *alvos, default=0.4):
    return R.tp(t0, versos, *alvos, default=default)


CAM_PANELA = {"x": 1300, "y": 640, "zoom": 1.9, "zoom_fim": 2.05}


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
tz = em(T[1][0], T[1][2], "zum", default=round(d[1] * 0.6, 2))
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": ARR, "camera": corpo(1300), "titulo": "a pipoca do arraial", "fx": ["confete"],
     "callout": [call(1.6, "PULA, PULA, PIPOCA!", "laranja")],
     "objetos": panelao(d[0], depth=0.45),
     "atores": {LA: a(650, ("jump", 1.5), ("jump", 2.9), turn=0.3), LU: a(1950, ("jump", 1.7), ("jump", 3.1), turn=-0.3)}},
    {"linhas": 1, "cenario": ARR, "camera": corpo(1300), "callout": [call(0.2, "ESQUENTA A PANELA…", "vermelho"), call(round(tz, 2), "ZUM, ZUM!", "amarelo")],
     "objetos": panelao(d[1], x=1550, depth=0.5, ploc=False, z=4),
     "atores": {VC: vovo(900, ("point", 0.3), turn=0.35)}},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "camera": GCAM, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "LAURINHA E LUISINHO!", "roxo")],
     "atores": {LA: g(640, ("wave", 0.1), turn=0.25) | {"depth": 1.05}, LU: g(1280, ("wave", 0.2), turn=-0.25) | {"depth": 1.05}}},
    {**banda(max(0.6, d[3])), "titulo": "a banda no arraial"},
]


# ───────── 1º verso: o vovô Ciço e o panelão ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": ARR, "camera": corpo(1300), "fx": ["confete"], "callout": [call(0.3, "FESTA DE SÃO JOÃO!", "laranja")],
     "objetos": fogueira(d[0]),
     "atores": {LA: a(600, ("dance", 0.0, "festa"), turn=0.3), LU: a(2000, ("dance", 0.1, "festa"), turn=-0.3)}},
    {"linhas": 1, "cenario": RUA, "camera": corpo(1300, 1500), "callout": [call(0.2, "O VOVÔ CIÇO CHEGOU!", "azul")],
     "atores": {VC: anda(vovo(2300, turn=-0.4), 1500, d[1], como="walk")}},
    {"linhas": 1, "cenario": ARR, "camera": corpo(1450), "callout": [call(0.2, "COM O MILHO NA PANELA…", "amarelo")],
     "objetos": panelao(d[2], x=1700, depth=0.5, ploc=False, treme=False, z=4),
     "atores": {VC: vovo(1150, ("point", 0.2), turn=0.35)}},
    R.dividida({"cenario": ARR, "camera": {"x": 1300, "y": 520, "zoom": 1.6, "zoom_fim": 1.68},
                "atores": {VC: vovo(1300, ("apontar_camera", 0.1))}},
               {"cenario": ARR, "camera": {"x": 1300, "y": 520, "zoom": 1.6, "zoom_fim": 1.68},
                "atores": {LA: a(1300, ("cheguei", round(d[3] * 0.5, 2)), expr="joy")}},
               linhas=1, layout="diagonal", callout=[call(0.1, "QUEM QUER PIPOCA?", "laranja"), call(round(d[3] * 0.55, 2), "EU VOU!", "rosa")]),
    {"linhas": 1, "cenario": ARR, "camera": corpo(1300), "callout": [call(0.2, "O LUISINHO E A LAURINHA…", "roxo")],
     "objetos": panelao(d[4], depth=0.42, ploc=False),
     "atores": {LU: anda(a(300, turn=0.4, expr="sly"), 800, d[4]), LA: anda(a(2300, turn=-0.4, expr="sly"), 1800, d[4])}},
    {"linhas": 1, "cenario": ARR, "camera": BU(1300), "callout": [call(0.2, "BEM PERTINHO!", "verde")],
     "objetos": panelao(d[5], depth=0.42, ploc=False, z=2),
     "atores": {LU: a(880, ("pensar", 0.1), turn=0.4, z=4), LA: a(1720, ("estatua", 0.0), turn=-0.4, expr="sly", z=4)}},
    {"linhas": 1, "cenario": ARR, "camera": CAM_PANELA, "callout": [call(0.2, "ESCUTANDO A PANELA…", "amarelo")],
     "objetos": panelao(d[6], depth=0.5, ploc=False)},
    {"linhas": 1, "cenario": ARR, "camera": cab(1300), "callout": [call(0.2, "PLOC!", "vermelho")], "tremor": [0.3],
     "atores": {LU: a(1300, ("take", 0.2), expr="surprised")}},
]


# ───────── refrão: pula, pula, pipoca! ploc, ploc, no panelão! zum, zum! pula do chão! ─────────
REF = {
    1: dict(trio=("danca_xadrez_laranja", (LA, VC, LU)), pulador=(LU, ARR), close=(LA, CAMPO)),
    2: dict(trio=("danca_bolinhas_rosa", (LU, VO, LA)), pulador=(LA, ARR), close=(LU, CASA)),
    3: dict(trio=("danca_raios_azul", (LA, VC, LU)), pulador=(VC, ARR), close=(LA, SALA)),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        tp_ = em(t0, versos, "pula", default=0.2)
        tz = em(t0, versos, "zum", "ploc", default=round(dd * 0.5, 2))
        if i % 4 == 0:                                     # todo mundo pula em volta do panelão
            out.append({"linhas": 2, "cenario": ARR, "camera": corpo(1300), "fx": ["confete"],
                        "callout": [call(0.1, "PULA, PULA, PIPOCA!", "laranja"), call(round(tz, 2), "PLOC, PLOC!", "vermelho")],
                        "objetos": panelao(dd, depth=0.45),
                        "atores": {LA: a(600, ("jump", round(tp_, 2)), ("jump", round(tp_ + 1.1, 2)), ("jump", round(tp_ + 2.2, 2)), turn=0.3),
                                   LU: a(2000, ("jump", round(tp_ + 0.3, 2)), ("jump", round(tp_ + 1.4, 2)), ("jump", round(tp_ + 2.5, 2)), turn=-0.3)}})
        elif i % 4 == 1:                                   # a dança da pipoca no fundo colorido
            cen, trio = cfg["trio"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "flash": n == 1,
                        "callout": [call(0.1, "PULA, PULA, PIPOCA!", "laranja"), call(round(tz, 2), "ZUM, ZUM! PULA DO CHÃO!", "amarelo")],
                        "atores": {c: g(x, ("dance", 0.05 * j, "pulinho"), turn=tv) | ({"expr": "joy"} if c in (VC, VO) else {})
                                   for j, (c, x, tv) in enumerate(zip(trio, (380, 960, 1540), (0.2, 0.0, -0.2)))}})
        elif i % 4 == 2:                                   # a PIPOCA pulando × quem pula (tela dividida)
            q, cen = cfg["pulador"]
            out.append(R.dividida({"cenario": cen, "camera": {"x": 1300, "y": 560, "zoom": 1.45, "zoom_fim": 1.52},
                                   "atores": {q: (vovo if q == VC else a)(1300, ("jump", round(tp_, 2)), ("jump", round(tp_ + 1.2, 2)))}},
                                  {"cenario": "danca_raios_amarelo", "camera": GCAM,
                                   "objetos": pipoca(dd, 960, 900, depth=1.3, pulos=(round(tp_, 2), round(tp_ + 1.2, 2), round(tp_ + 2.4, 2)))},
                                  linhas=2, layout="vertical",
                                  callout=[call(0.1, "PULA, PULA, PIPOCA!", "laranja"), call(round(tz, 2), "PLOC, PLOC!", "vermelho")]))
        else:                                              # ZUM, ZUM! de pertinho num cenário de verdade
            q, cen = cfg["close"]
            out.append({"linhas": 2, "cenario": cen, "camera": cab(1300), "fx": ["estrelas"],
                        "callout": [call(round(tz, 2), "ZUM, ZUM! PULA DO CHÃO!", "amarelo")],
                        "atores": {q: a(1300, ("dance", 0.0, "pulinho"))}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 2}, {"seg": 6.0}, {"seg": 3.3}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 2, "cenario": ARR, "camera": BU(1300), "callout": [call(0.2, "BORA, TURMINHA!", "laranja")],
     "atores": {LA: a(880, ("cheguei", 0.1), turn=0.35), LU: a(1720, ("wave", 0.4), turn=-0.35)}},
    {**banda(max(0.6, d[1])), "titulo": "a banda no arraial"},
    {"seg": max(0.6, d[2]), "cenario": ARR, "camera": corpo(1300), "fx": ["confete"], "titulo": "a dança da fogueira",
     "objetos": fogueira(d[2]),
     "atores": {LA: fundo(a(560, ("dance", 0.0, "cintura"), turn=0.3)), VC: fundo(vovo(2040, ("dance", 0.1, "balanco"), turn=-0.3))}},
    {"seg": max(0.6, d[3]), "cenario": ARR, "camera": BU(1300), "titulo": "o gato quer a pipoca",
     "objetos": {**pipoca(d[3], 1550, 760, depth=0.4, pulos=(0.3, 1.4), gira=2.0),
                 "gato": obj("gato", 1650, CHAO + 30, 0.75, d[3], z=4, fixo={"lado": -1.0}, pts={"aceno": [(0.5, 1.0)], "miau": [(1.5, 1.0)]},
                             lin={"rabo": (0.0, 3.0)})},
     "atores": {LU: a(950, ("ofegante", 0.1), turn=0.35, expr="laughing")}},
]


# ───────── ponte: os comandos da pipoca ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4 + [{"linhas": 2}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}])
d = dur(T)
tpl = em(T[3][0], T[3][2], "pula", default=0.2)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "callout": [call(0.1, "AGACHA IGUAL MILHO!", "amarelo")],
     "atores": {LA: a(900, ("sit", 0.2), turn=0.3), LU: a(1700, ("sit", 0.35), turn=-0.3)}},
    {"linhas": 1, "cenario": ARR, "camera": CAM_PANELA, "callout": [call(0.1, "ESQUENTOU, ESQUENTOU!", "vermelho")],
     "objetos": panelao(d[1], depth=0.5, ploc=False)},
    R.dividida({"cenario": COZ, "camera": {"x": 1300, "y": 560, "zoom": 1.45, "zoom_fim": 1.52},
                "atores": {LA: a(1300, ("shock_reaction", 0.1), expr="surprised")}},
               {"cenario": ARR, "camera": {"x": 1300, "y": 560, "zoom": 1.45, "zoom_fim": 1.52},
                "atores": {LU: a(1300, ("shock_reaction", 0.15), expr="surprised")}},
               linhas=1, layout="vertical", callout=[call(0.1, "TREME, TREME, TREME…", "roxo")]),
    {"linhas": 1, "cenario": "danca_raios_laranja", "camera": GCAM, "fx": ["estrelas"],
     "callout": [call(round(tpl, 2), "PULA! PLOC! PIPOCOU!", "vermelho")],
     "objetos": pipoca(d[3], 1350, 950, depth=1.0, pulos=(round(tpl, 2),)),
     "atores": {LA: g(620, ("jump", round(tpl, 2), 200), turn=0.2) | {"depth": 1.05}}},
    {"linhas": 2, "cenario": ARR, "camera": corpo(1300), "callout": [call(0.1, "E MAIS!", "verde"), call(round(d[4] * 0.4, 2), "PULA ALTO, PIPOCA!", "laranja")],
     "objetos": fogueira(d[4], x=1900),
     "atores": {LU: a(900, ("jump", round(d[4] * 0.42, 2), 260), turn=0.3)}},
    {"linhas": 1, "cenario": ARR, "camera": BU(1300), "callout": [call(0.1, "AGORA NUM PÉ SÓ!", "rosa")],
     "atores": {LA: a(1300, ("dance", 0.0, "pezinho"))}},
    {"linhas": 1, "cenario": "danca_xadrez_verde", "camera": GCAM, "callout": [call(0.1, "RODA, RODA… E PLOC!", "azul")],
     "atores": {LU: g(960, ("dance", 0.0, "roda")) | {"depth": 1.15}}},
    {"linhas": 1, "cenario": ARR, "camera": BU(1300), "fx": ["estrelas"], "callout": [call(0.1, "NO CHAPÉU DA VOVÓ!", "laranja")],
     "objetos": pipoca(d[7], 1330, 300, depth=0.45, pulos=(0.1,), gira=2.0),
     "atores": {VO: a(1300, ("laugh", 0.6), expr="joy")}},
]


# ───────── 2º verso: a VIRADA — silêncio… PLOC no bigodão! ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
tpc = em(T[6][0], T[6][2], "ploc", default=0.1)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": ARR, "camera": corpo(1300), "callout": [call(0.2, "DE REPENTE… SILÊNCIO!", "roxo")],
     "objetos": panelao(d[0], depth=0.42, ploc=False, treme=False),
     "atores": {LA: a(650, ("estatua", 0.0), turn=0.35, expr="surprised"), LU: a(1950, ("estatua", 0.0), turn=-0.35, expr="surprised")}},
    {"linhas": 1, "cenario": ARR, "camera": CAM_PANELA, "callout": [call(0.2, "A PANELA PAROU…", "azul")],
     "objetos": panelao(d[1], depth=0.5, ploc=False, treme=False)},
    {"linhas": 1, "cenario": ARR, "camera": corpo(1300), "callout": [call(0.2, "O LUISINHO CHEGOU PERTO…", "roxo")],
     "objetos": panelao(d[2], x=1500, depth=0.42, ploc=False, treme=False),
     "atores": {LU: anda(a(500, turn=0.4, expr="sly"), 1050, d[2])}},
    {"linhas": 1, "cenario": ARR, "camera": cab(1300), "callout": [call(0.2, "CADÊ? NÃO ESTOUROU?", "laranja")],
     "atores": {LU: a(1300, ("pensar", 0.1), expr="confused")}},
    {"linhas": 1, "cenario": ARR, "camera": corpo(1300), "callout": [call(0.2, "O VOVÔ LEVANTOU A TAMPA…", "azul")],
     "objetos": panelao(d[4], x=1550, depth=0.5, ploc=False, treme=False, z=4, pts={"tampa": [(round(d[4] * 0.4, 2), 1.0)]}),
     "atores": {VC: vovo(900, ("point", 0.2), turn=0.35, expr="surprised")}},
    {"linhas": 1, "cenario": ARR, "camera": CAM_PANELA, "callout": [call(0.2, "PRA OLHAR O PANELÃO…", "roxo")],
     "objetos": panelao(d[5], depth=0.5, ploc=False, treme=False, tampa=1.0, cheio=1.0)},
    {"linhas": 1, "cenario": ARR, "camera": corpo(1300), "flash": True, "tremor": [round(tpc, 2)],
     "callout": [call(round(tpc, 2), "PLOC!", "vermelho")],
     "objetos": {**panelao(d[6], x=1600, depth=0.5, ploc=False, treme=False, tampa=1.0, cheio=1.0, z=4),
                 **pipoca(d[6], 1350, 640, depth=0.6, pulos=(round(tpc, 2),), gira=2.0)},
     "atores": {VC: vovo(950, ("take", round(tpc, 2)), turn=0.35, expr="surprised")}},
    {"linhas": 1, "cenario": ARR, "camera": cab(1300), "fx": ["coracoes"], "callout": [call(0.2, "PULOU NO BIGODÃO!", "laranja")],
     "objetos": pipoca(d[7], 1300, 505, depth=0.45, cara=1.0, gira=0.0, z=6),
     "atores": {VC: vovo(1300, ("laugh", 0.3))}},
]


# ───────── intervalo 2 (só instrumental): a festa continua ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 * 0.45, 2)
R.partes["intervalo#2"] = [
    {**banda(d1, extra={VC: fundo(vovo(2400, ("dance", 0.0, "balanco"), turn=-0.3))}), "titulo": "a banda no arraial"},
    {"seg": round(D2 - d1, 2), "cenario": ARR, "camera": corpo(1300), "fx": ["confete"], "titulo": "a quadrilha da fogueira",
     "objetos": fogueira(D2 - d1),
     "atores": {LA: fundo(a(560, ("dance", 0.0, "twist"), turn=0.3)), VO: fundo(a(1960, ("dance", 0.1, "balanco"), turn=-0.3, expr="joy")),
                LU: fundo(a(2300, ("dance", 0.05, "pulinho"), turn=-0.3))}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4 + [{"seg": 0.0}])
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": ARR, "camera": cab(1300), "callout": [call(0.2, "E VOCÊ? PULA IGUAL PIPOCA?", "laranja")],
     "atores": {LA: a(1300, ("apontar_camera", 0.1), ("jump", round(d[0] * 0.7, 2)))}},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {VO: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0, "expr": "joy"}}},
    {"linhas": 1, "cenario": CASA, "camera": BU(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {LU: a(880, ("point", 0.1), turn=0.3), MA: a(1720, ("wave", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LA: g(560, ("point", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"seg": max(0.6, d[4]), "cenario": ARR, "camera": BU(1300), "fx": ["coracoes"], "titulo": "o abraço com pipoca",
     "atores": {LA: a(880, ("abraco", 0.1), turn=0.35), LU: a(1720, ("abraco", 0.15), turn=-0.35)}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 2.6, "cenario": ARR, "camera": corpo(1300), "fx": ["confete"],
     "callout": [call(0.2, "PULA PIPOCA!", "laranja"), call(1.3, "TCHAU!", "amarelo")],
     "objetos": fogueira(2.6, x=2350, depth=0.35),
     "atores": {LA: fundo(a(560, ("wave", 0.0), turn=0.3)), VC: fundo(vovo(1300, ("wave", 0.1))), LU: fundo(a(2040, ("wave", 0.1), turn=-0.3))}},
    {"seg": round(dfim - 2.6, 2), "cenario": ARR, "camera": cab(1300), "flash": True, "callout": [call(0.2, "PLOC!", "vermelho")],
     "titulo": "a pipoca no bigodão do vovô",
     "objetos": pipoca(dfim - 2.6, 1300, 505, depth=0.45, cara=1.0, gira=0.0, z=6),
     "atores": {VC: vovo(1300, ("laugh", 0.1))}},
]


# ── vida no cenário: nuvens no céu ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    if cen in (CAMPO, CASA, RUA):
        x0 = (300, 1700, 900, 2100)[j % 4]
        ob.setdefault("nv", obj("nuvem", x0, 260, 0.32, dd, z=0, fixo={"cara": 1.0}, lin={"x": (x0, x0 + 280)}))
    if cen == ARR and "fog" not in ob and "pan" not in ob and "bat" not in ob and not sb.get("tela_dividida") and sb.get("camera") is not CAM_PANELA:
        ob.update(fogueira(dd, x=(2300, 300)[j % 2], depth=0.35, z=1))         # a fogueira sempre acesa ao fundo
    if cen == ARR and "pip" not in ob and sb.get("camera") is not CAM_PANELA:   # pipoquinhas voando pelo arraial
        ob["pv"] = obj("pipoca", (1800, 800, 1500, 1000)[j % 4], 330, 0.22, dd, z=1, fixo={"cara": 0.0},
                       lin={"gira": (0.0, 2.0), "x": ((1800, 800, 1500, 1000)[j % 4], (1500, 1100, 1200, 1300)[j % 4])})
    if not ob:
        sb.pop("objetos", None)


for chave, planos in R.partes.items():
    k_info = chave if chave in R.info else f"{chave}#1"
    for j, (p_, (t0, t1, _)) in enumerate(zip(planos, R.tempos(k_info, planos))):
        for sb in [p_] + list((p_.get("tela_dividida") or {}).get("paineis", [])):
            _ambiente(sb, round(t1 - t0, 2), j)

R.salvar("Roteiro de 34 'Pula Pipoca!' (take inteiro, 2:30, E18, nota 4,9, letra na receita do Fofolucos): o arraial de São João "
         "(plano_arraial) com a fogueira; o vovô Ciço faz pipoca no panelão (panelao); todo mundo pula igual pipoca (pipoca); "
         "ponte de comandos; a virada: silêncio, o vovô levanta a tampa… PLOC! a última pipoca no bigodão. "
         "Gerado por scripts/roteiros/ep34_pula_pipoca.py.")
