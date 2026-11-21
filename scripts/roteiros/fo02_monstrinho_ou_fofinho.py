"""Roteiro verso a verso do canal FOFOLUCOS — 02 "Monstrinho ou Fofinho?" (take v2 inteiro, 2:33, 129 BPM, Sol maior,
estilo F3, nota 4,8) → canais/fofolucos/musicas/02_monstrinho_ou_fofinho/roteiro.json.

O JOGO: no "monstrinho!" a turma faz o RAWR (fundo de raios, garras, sobrancelha brava); no "fofinho!" faz a CARINHA
FOFINHO (ação nova `fofinho`: olhão brilhando, mãozinhas juntas, corações); quem errar dança sozinho no meio.
Ponte = comandos (garra, palminha, pula, giradinha) cada vez mais rápidos. 2º verso = a virada do Bilu no ESPELHO
(objeto novo `espelho_reflexo`: o reflexo faz o RAWR junto e o Bilu escorrega e cai sentado de susto).
Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — CABEÇA / BUSTO / CORPO misturados, espaço ≥ 430 entre monstrinhos,
nunca monstrinho na frente de fundo da mesma cor, NUNCA a palavra "monstro" nos letreiros.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo02_monstrinho_ou_fofinho.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import Roteiro, call  # noqa: E402

R = Roteiro("fofolucos/ep02-monstrinho-ou-fofinho", "02_monstrinho_ou_fofinho", "bilu")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
VILA, PARQUE, QUARTO, PALCO, NOITE, ESCOLA, COZ = "mon_vila", "mon_parque", "mon_quarto", "mon_palco", "mon_noite", "mon_escola", "mon_cozinha"


def dur(T):
    return [round(t1 - t0, 2) for t0, t1, _ in T]


# ── enquadramentos (bíblia §4; a câmera ainda sobe sozinha se algum chifre for cortar) ──
def cab(x=1300):
    return {"x": x, "y": 500, "zoom": 1.85, "zoom_fim": 1.95}


def busto(x=1300, y=560):
    return {"x": x, "y": y, "zoom": 1.55, "zoom_fim": 1.62}


def corpo(x=1300, x_fim=None):
    c = {"x": x, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    if x_fim:
        c["x_fim"] = x_fim
    return c


GCAM = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}


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


def banda(cen, d, cam=None, extra=None):
    """a banda da turma: Bilu na bateria, Zuzu no teclado; quem dança junto fica à DIREITA (bíblia §4)."""
    p = R.banda(cen, d, teclado=True, sax=ZU, bateria=BI, cam=cam or {"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["cantam"] = [ZU]
    return p


def espelho(x, d, **pts):
    """espelho de pé com o reflexo do Bilu (quem 0), virado para a esquerda (para o Bilu de verdade)."""
    return obj("espelho_reflexo", x, 935, 0.75, d, z=2, fixo={"quem": 0.0, "vira": -0.45, "rawr": 0.0, "susto": 0.0, "brilho": 0.0},
               pts=pts)


def rawr_em(t0, versos, default):
    return R.tp(t0, versos, "rawr", "rawr!", default=default)


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "titulo": "monstrinho ou fofinho?", "cantam": [BI],
     "callout": [call(0.3, "MONSTRINHO OU FOFINHO?", "roxo")],
     "atores": {BI: a(700, ("rawr", 0.4), turn=0.3), MI: a(1900, ("fofinho", 0.9), turn=-0.3)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.2, "QUEM ADIVINHA?", "laranja")], "cantam": [TE],
     "atores": {TE: a(900, ("look_around", 0.1), turn=0.25, expr="confused"), ZU: a(1700, ("pensar", 0.2), turn=-0.25)}},
    {"linhas": 1, "cenario": "mon_raios_laranja", "camera": GCAM, "flash": True, "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.1, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {TE: g(210, ("rawr", 0.3), turn=0.2), GO: g(710, ("rawr", 0.38)), BI: g(1210, ("rawr", 0.46)),
                NH: g(1710, ("rawr", 0.54), turn=-0.2)}},
    {**banda(PALCO, max(0.6, d[3]), extra={TE: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: o jogo ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": corpo(800, 1800), "callout": [call(0.3, "VILA MONSTRINHA!", "roxo")], "cantam": [GO],
     "atores": {GO: a(500, ("walk", 0.0), turn=0.3) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 1000, "dur": 1.4},
                                                                 {"t": 1.5, "do": "wave", "dur": "resto"}]},
                TE: a(2250, ("wave", 0.3), turn=-0.3)}},
    {"linhas": 1, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.3, "UM JOGO!", "amarelo")], "cantam": [MI],
     "atores": {MI: a(1000, ("apontar_camera", 0.2), turn=0.25), NH: a(1650, ("dance", 0.1, "pulinho"), turn=-0.25)}},
    {"linhas": 1, "cenario": COZ, "camera": cab(1300), "callout": [call(0.3, "MONSTRINHO!", "vermelho")], "cantam": [BI],
     "atores": {BI: a(1300, ("rawr", 0.25))}},
    {"linhas": 1, "cenario": "mon_raios_vermelho", "camera": GCAM, "tremor": [0.5], "callout": [call(0.2, "RAWR!", "vermelho")],
     "cantam": [GO],
     "atores": {GO: g(380, ("rawr", 0.15), turn=0.2), ZU: g(960, ("rawr", 0.22)), TE: g(1540, ("rawr", 0.3), turn=-0.2)}},
    {"linhas": 1, "cenario": PARQUE, "camera": cab(1300), "fx": ["coracoes"], "callout": [call(0.3, "FOFINHO!", "rosa")], "cantam": [MI],
     "atores": {MI: a(1300, ("fofinho", 0.2))}},
    {"linhas": 1, "cenario": "mon_brilho_azul", "camera": GCAM, "fx": ["coracoes"], "callout": [call(0.2, "QUE FOFO!", "rosa")],
     "cantam": [ZU],
     "atores": {ZU: g(380, ("fofinho", 0.1), turn=0.2), MI: g(960, ("fofinho", 0.18)), NH: g(1540, ("fofinho", 0.26), turn=-0.2)}},
    {"linhas": 1, "cenario": ESCOLA, "camera": busto(1300), "callout": [call(0.3, "ERROU!", "laranja")], "cantam": [ZU],
     "atores": {NH: a(900, ("fofinho", 0.0), turn=0.25), ZU: a(1700, ("point", 0.2), ("laugh", 0.9), turn=-0.25)}},
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "fx": ["confete"], "callout": [call(0.2, "VAI PRO MEIO DANÇAR!", "verde")],
     "cantam": [NH],
     "atores": {ZU: a(640, ("dance", 0.0, "palmas"), turn=0.3), NH: a(1300, ("dance", 0.0, "festa")),
                TE: a(1960, ("dance", 0.1, "palmas"), turn=-0.3)}},
]


# ───────── refrão: monstrinho ou fofinho? ─────────
# por ocorrência: (busto RAWR, cab FOFINHO, dança sozinho no meio, raios RAWR da turma) — elenco e cenário mudam
REF = {
    1: dict(par=(BI, ZU, PARQUE), fofo=(MI, VILA), meio=(TE, (GO, NH), VILA), raios=("mon_raios_laranja", (TE, GO, BI, NH))),
    2: dict(par=(GO, NH, ESCOLA), fofo=(TE, QUARTO), meio=(NH, (MI, BI), PARQUE), raios=("mon_raios_verde", (MI, ZU, BI, TE))),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    spec = [{"linhas": 2}] * (linhas // 2)
    T = R.tempos(f"refrao#{n}", spec)
    out = []
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        tr = min(rawr_em(t0, versos, round(dd * 0.55, 2)), round(dd - 0.6, 2))   # o RAWR sempre começa dentro do plano
        if n == 3:                                         # meio refrão final: close RAWR + a turma toda no raios
            if i == 0:
                out.append({"linhas": 2, "cenario": NOITE, "camera": cab(1300), "flash": True, "cantam": [BI],
                            "callout": [call(0.1, "MONSTRINHO OU FOFINHO?", "roxo"), call(tr, "RAWR!", "vermelho")],
                            "atores": {BI: a(1300, ("fofinho", 0.0), ("rawr", tr))}})
            else:
                out.append({"linhas": 2, "cenario": "mon_raios_rosa", "camera": GCAM, "fx": ["estrelas"], "cantam": [GO],
                            "callout": [call(0.1, "FOFOLUCOS!", "roxo")],
                            "atores": {c: g(x, ("fofinho", 0.0), ("rawr", tr + 0.06 * k), turn=tn) for k, (c, x, tn) in
                                       enumerate(zip((TE, GO, BI, ZU), (210, 710, 1210, 1710), (0.25, 0.1, -0.1, -0.25)))}})
            continue
        cfg = REF[n]
        if i == 0:                                         # "Monstrinho! Rawr!" — dois em BUSTO fazendo o RAWR
            p_, q_, cen = cfg["par"]
            out.append({"linhas": 2, "cenario": cen, "camera": busto(1300), "tremor": [tr], "cantam": [p_],
                        "callout": [call(0.1, "MONSTRINHO OU FOFINHO?", "roxo"), call(tr, "MONSTRINHO! RAWR!", "vermelho")],
                        "atores": {p_: a(900, ("rawr", tr), turn=0.25), q_: a(1700, ("rawr", tr + 0.08), turn=-0.25)}})
        elif i == 1:                                       # "Fofinho! Ai, que lindinho!" — CABEÇA com o olhão brilhando
            q_, cen = cfg["fofo"]
            tf = R.tp(t0, versos, "fofinho!", "fofinho", default=round(dd * 0.45, 2))
            out.append({"linhas": 2, "cenario": cen, "camera": cab(1300), "fx": ["coracoes"], "cantam": [q_],
                        "callout": [call(tf, "FOFINHO!", "rosa"), call(min(dd - 0.6, tf + 0.9), "AI, QUE LINDINHO!", "rosa")],
                        "atores": {q_: a(1300, ("fofinho", max(0.0, tf - 0.15)))}})
        elif i == 2:                                       # "Quem errar dança sozinho!" — um dança no meio, os outros riem
            m_, (l_, r_), cen = cfg["meio"]
            out.append({"linhas": 2, "cenario": cen, "camera": corpo(1300), "fx": ["confete"], "cantam": [m_],
                        "callout": [call(round(dd * 0.4, 2), "DANÇA SOZINHO!", "verde")],
                        "atores": {l_: a(640, ("point", 0.1), ("laugh", round(dd * 0.5, 2)), turn=0.3),
                                   m_: a(1300, ("dance", 0.0, "twist")),
                                   r_: a(1960, ("point", 0.15), ("laugh", round(dd * 0.55, 2)), turn=-0.3)}})
        else:                                              # "Fofolucos! Rawr!" — a turma no fundo de raios
            cen, quem = cfg["raios"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["estrelas"], "flash": n == 1, "cantam": [quem[1]],
                        "callout": [call(tr, "FOFOLUCOS! RAWR!", "roxo")],
                        "atores": {c: g(x, ("dance", 0.0, "festa"), ("rawr", tr + 0.06 * k), turn=tn) for k, (c, x, tn) in
                                   enumerate(zip(quem, (210, 710, 1210, 1710), (0.25, 0.1, -0.1, -0.25)))}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 2}, {"seg": 4.3}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 2, "cenario": VILA, "camera": cab(1300), "cantam": [ZU], "callout": [call(0.2, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {ZU: a(1300, ("rawr", 0.1), ("apontar_camera", 1.7))}},
    {**banda(PALCO, max(0.6, d[1]), extra={GO: a(2300, ("dance", 0.0, "bracos"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
    {"seg": max(0.6, d[2]), "cenario": "mon_xadrez_verde", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança",
     "cantam": [MI],
     "atores": {MI: g(380, ("dance", 0.0, "cintura"), turn=0.2), TE: g(960, ("dance", 0.1, "joelho")),
                NH: g(1540, ("dance", 0.0, "palmas"), turn=-0.2)}},
]


# ───────── ponte: os comandos (garra, palminha, pula, giradinha… rapidinho!) ─────────
# o 1º verso da ponte ("Monstrinho! Mostra a garra!") começa no fim do intervalo → 1º plano da ponte por tempo (seg)
T = R.tempos("ponte#1", [{"seg": 2.0}] + [{"linhas": 1}] * 6)
d = dur(T)
R.partes["ponte#1"] = [
    {"seg": 2.0, "cenario": PARQUE, "camera": busto(1300), "callout": [call(0.1, "MOSTRA A GARRA!", "rosa")], "cantam": [MI],
     "atores": {MI: a(1300, ("rawr", 0.05))}},
    {"linhas": 1, "cenario": "mon_brilho_azul", "camera": GCAM, "callout": [call(0.1, "BATE PALMINHA!", "amarelo")], "cantam": [MI],
     "atores": {MI: g(380, ("dance", 0.0, "palmas"), turn=0.2), ZU: g(960, ("dance", 0.05, "palmas")),
                NH: g(1540, ("dance", 0.1, "palmas"), turn=-0.2)}},
    {"linhas": 1, "cenario": VILA, "camera": corpo(1300), "callout": [call(0.1, "PULA BEM ALTO!", "verde")], "cantam": [GO],
     "atores": {GO: a(640, ("jump", 0.1), turn=0.3, depth=0.8), BI: a(1300, ("jump", 0.18), depth=0.8),
                MI: a(1960, ("jump", 0.26), turn=-0.3, depth=0.8)}},
    {"linhas": 1, "cenario": "mon_xadrez_laranja", "camera": GCAM, "callout": [call(0.1, "DÁ UMA GIRADINHA!", "azul")], "cantam": [TE],
     "atores": {TE: g(380, ("dance", 0.0, "roda"), turn=0.2), GO: g(960, ("dance", 0.05, "roda")),
                BI: g(1540, ("dance", 0.1, "roda"), turn=-0.2)}},
    {"linhas": 1, "cenario": ESCOLA, "camera": busto(1300), "callout": [call(0.2, "BEM RAPIDINHO!", "laranja")], "cantam": [BI],
     "atores": {BI: a(900, ("dance", 0.0, "pulinho"), turn=0.25), MI: a(1700, ("dance", 0.1, "pulinho"), turn=-0.25)}},
]
t0, t1, vv = T[5]
ts = R.tps(t0, vv, "monstrinho!", "monstrinho", "fofinho!", "fofinho")
ts = (ts + [0.1, 0.9, 1.7])[:3] if len(ts) < 3 else ts[:3]
R.partes["ponte#1"].append(                                # troca rápida no MESMO close: monstrinho → fofinho → monstrinho
    {"linhas": 1, "cenario": NOITE, "camera": cab(1300), "cantam": [ZU],
     "callout": [call(ts[0], "MONSTRINHO!", "vermelho"), call(ts[1], "FOFINHO!", "rosa"), call(ts[2], "MONSTRINHO!", "vermelho")],
     "atores": {ZU: a(1300, ("rawr", ts[0], 0.75), ("fofinho", ts[1], 0.75), ("rawr", ts[2]))}})
R.partes["ponte#1"].append(
    {"linhas": 1, "cenario": PARQUE, "camera": corpo(1300), "fx": ["coracoes"], "callout": [call(0.2, "UFA… FOFINHO!", "rosa")],
     "cantam": [NH],
     "atores": {TE: a(640, ("fofinho", 0.3), turn=0.3), NH: a(1300, ("fofinho", 0.2)), GO: a(1960, ("fofinho", 0.4), turn=-0.3)}})


# ───────── 2º verso: o Bilu e o ESPELHO ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
tr3 = rawr_em(T[3][0], T[3][2], 0.5)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "callout": [call(0.3, "ESPELHO!", "azul")], "cantam": [BI],
     "objetos": {"esp": espelho(1650, d[0], brilho=[(0.5, 1.0)])},
     "atores": {BI: a(950, ("look_around", 0.1), turn=0.45)}},
    {"linhas": 1, "cenario": QUARTO, "camera": busto(1300), "callout": [call(0.3, "A CARETA MAIS FEROZ!", "laranja")], "cantam": [BI],
     "objetos": {"esp": espelho(1650, d[1], rawr=[(0.4, 0.6), (0.8, 0.0)])},
     "atores": {BI: a(950, ("rawr", 0.3, 0.9), turn=0.45)}},
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1050), "callout": [call(0.3, "OLHÃO!", "azul")], "cantam": [BI],
     "atores": {BI: a(950, turn=0.25, expr="surprised")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "tremor": [tr3], "callout": [call(tr3, "RAWR!", "vermelho")], "cantam": [BI],
     "objetos": {"esp": espelho(1650, d[3], rawr=[(tr3, 1.0)])},
     "atores": {BI: a(950, ("rawr", tr3), turn=0.45)}},
    {"linhas": 1, "cenario": QUARTO, "camera": {"x": 1650, "y": 520, "zoom": 1.6, "zoom_fim": 1.75}, "tremor": [0.4],
     "callout": [call(0.3, "FEZ IGUAL!", "roxo")], "cantam": [BI],
     "objetos": {"esp": espelho(1650, d[4], rawr=[(0.2, 1.0)], brilho=[(0.4, 1.0)])},
     "atores": {BI: a(950, turn=0.45, expr="surprised")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "callout": [call(0.4, "AI!", "vermelho")], "cantam": [BI],
     "objetos": {"esp": espelho(1650, d[5], rawr=[(0.0, 1.0)])},
     "atores": {BI: a(950, ("shock_reaction", 0.0, 0.5), ("slip", 0.5), turn=0.45, expr="scared")}},
    {"linhas": 1, "cenario": QUARTO, "camera": corpo(1300), "callout": [call(0.3, "HA HA HA!", "amarelo")], "cantam": [TE],
     "atores": {TE: a(500, ("laugh", 0.0), turn=0.3), GO: a(1300, ("laugh", 0.1)), MI: a(2100, ("laugh", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": QUARTO, "camera": cab(1300), "callout": [call(0.4, "QUE MONSTRINHO ASSUSTADO!", "roxo")], "cantam": [BI],
     "atores": {BI: a(1300, ("laugh", round(d[7] * 0.55, 2)), expr="scared")}},
]


# ───────── intervalo 2 (só instrumental) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
R.partes["intervalo#2"] = [
    {**banda(PALCO, round(D2 / 2, 2), extra={NH: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "a banda"},
    {"seg": round(D2 - round(D2 / 2, 2), 2), "cenario": "mon_xadrez_rosa", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança",
     "cantam": [GO],
     "atores": {GO: g(380, ("dance", 0.0, "roda"), turn=0.2), TE: g(960, ("dance", 0.1, "twist")),
                ZU: g(1540, ("dance", 0.0, "sapinho"), turn=-0.2)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": cab(1300), "callout": [call(0.2, "E VOCÊ?", "roxo"), call(1.4, "MONSTRINHO OU FOFINHO?", "rosa")],
     "cantam": [BI], "atores": {BI: a(1300, ("apontar_camera", 0.1), ("fofinho", round(d[0] * 0.6, 2)))}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "cantam": [ZU],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {ZU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": VILA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")], "cantam": [MI],
     "atores": {MI: a(900, ("point", 0.1), turn=0.3), TE: a(1700, ("wave", 0.2), turn=-0.25)}},
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
    {"linhas": 1, "seg": 3.6, "cenario": VILA, "camera": corpo(1300), "fx": ["coracoes"], "cantam": [BI],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.5, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn, y=y, depth=dp, z=zz) for k, (c, x, y, dp, zz, tn) in
                enumerate(((TE, 400, 880, 0.62, 2, 0.3), (GO, 1000, 880, 0.62, 2, 0.15), (BI, 1600, 880, 0.62, 2, -0.15),
                           (ZU, 2200, 880, 0.62, 2, -0.3), (MI, 700, 975, 0.74, 3, 0.2), (NH, 1900, 975, 0.74, 3, -0.2)))}},
    {"seg": round(dfim - 3.6, 2), "cenario": NOITE, "camera": cab(1300), "flash": True, "callout": [call(0.2, "RAWR!", "vermelho")],
     "titulo": "o último RAWR", "cantam": [MI], "atores": {MI: a(1300, ("fofinho", 0.0, 0.9), ("rawr", 1.0))}},
]


# ── vida no cenário (sem contorno): nuvens andando, lua com carinha, bolhas nos fundos ──
def _ambiente(sb, dd, j):
    cen = sb.get("cenario") or ""
    ob = sb.setdefault("objetos", {})
    if cen in (PARQUE, VILA):
        x0 = (300, 1700, 900, 2100)[j % 4]
        ob.setdefault("nv", obj("nuvem", x0, 300, 0.32, dd, z=0, fixo={"cara": 1.0}, lin={"x": (x0, x0 + 280)}))
    elif cen == NOITE:
        ob.setdefault("lua", obj("lua", 2150, 420, 0.42, dd, z=0, pts={"boca": [(0.5, 0.6)], "brilho": [(0.0, 0.0), (1.0, 1.0)]}))
    elif cen.startswith(("mon_raios_", "mon_xadrez_", "mon_brilho_")) or cen in (ESCOLA, COZ):
        x0 = (300, 1650, 800, 1300)[j % 4]
        ob.setdefault("bo", obj("bolha", x0, 1000, 0.3, dd, z=0, fixo={"tam": 1.0}, lin={"y": (1000, 250), "balanco": (0.0, round(dd, 1))}))
    if not ob:
        sb.pop("objetos", None)


for chave, planos in R.partes.items():
    k_info = chave if chave in R.info else f"{chave}#1"
    for j, (p_, (t0, t1, _)) in enumerate(zip(planos, R.tempos(k_info, planos))):
        for sb in [p_] + list((p_.get("tela_dividida") or {}).get("paineis", [])):
            _ambiente(sb, round(t1 - t0, 2), j)

R.salvar("Roteiro do canal Fofolucos — 02 'Monstrinho ou Fofinho?' (take v2 inteiro, 2:33, F3, nota 4,8): o jogo do "
         "monstrinho (RAWR) × fofinho (carinha fofinho); ponte de comandos; a virada do Bilu no espelho (espelho_reflexo); "
         "banda da turma. Gerado por scripts/roteiros/fo02_monstrinho_ou_fofinho.py.")
