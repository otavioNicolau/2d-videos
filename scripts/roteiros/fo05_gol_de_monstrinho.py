"""Roteiro verso a verso do canal FOFOLUCOS — 05 "Gol de Monstrinho!" (take inteiro, 2:36, 136 BPM, estilo F4 — groove
próprio, nota 4,9) → canais/fofolucos/musicas/05_gol_de_monstrinho/roteiro.json.

FUTEBOL NA VILA MONSTRINHA: cada um joga do seu jeito — o Gogo vê o campo todo com o olhão, o Zuzu cabeceia com o
chifrinho, o Teco corre ligeiro e o Nhoque goleiro pega até BOLA DE TRAVESSEIRO. Refrão = chuta, PASSA PRO AMIGO (a bola
vai de um para o outro) e GOL (a rede da trave balança, confete) — muda dupla, cor e artilheiro a cada refrão. Ponte =
comandos de jogo (corre, pula pra cabecear, dribla, chuta; goleiro abre os braços, pega no ar, comemora, dança do gol).
2º verso = a VIRADA: o Bilu chuta tão forte que a bola sobe, BATE NA LUA (lua com carinha) e volta… cai no pé da Mimi,
que só olhava; ela chuta fofinho e é GOL — todo mundo pode fazer gol.
Recursos novos: cenário `mon_campinho` (arquibancadinha clara com a torcida, placas amarelas/brancas, gramado listrado),
objetos `bola_futebol` (giro, amassa; tipo 1 = bola de travesseiro) e `trave` (rede balança com `rede`/`onda`).
Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — CABEÇA / BUSTO / CORPO, espaço ≥ 430, nunca monstrinho na frente da própria cor
(Gogo verde: no gramado só em CABEÇA; xadrez/raios/brilho nunca da cor de quem está na frente), closes do Zuzu em BUSTO,
nunca "monstro".
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/fo05_gol_de_monstrinho.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("fofolucos/ep05-gol-de-monstrinho", "05_gol_de_monstrinho", "bilu")
BI, TE, GO, MI, ZU, NH = "bilu", "teco", "gogo", "mimi", "zuzu", "nhoque"
VILA, CAMPO, PALCO, CEU = "mon_vila", "mon_campinho", "mon_palco", "mon_abertura"
CAMPO_GOL, GX = "mon_campinho_gol", 1565            # campinho de frente para o gol (linha do gol e áreas em x = GX)
CHAO = 935                                                  # pé da bola no gramado (mesmo apoio dos monstrinhos)


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


def bola(caminho, d, depth=0.8, z=4, tipo=0.0, giro=None):
    """Bola que percorre `caminho` = [(t, x, y), …] (linear entre os pontos; parada antes do 1º e depois do último);
    `giro` = voltas totais (padrão: proporcional à distância). Quica (amassa) onde o ponto tiver y no chão."""
    t0, x0, y0 = caminho[0]
    ks = [{"t": 0.0, "pose": {"x": float(x0), "y": float(y0), "giro": 0.0, "amassa": 0.0, "tipo": tipo}, "ease": "step"}]
    tot = sum(abs(b[1] - a_[1]) + abs(b[2] - a_[2]) for a_, b in zip(caminho, caminho[1:]))
    voltas = giro if giro is not None else tot / 500.0
    acum = 0.0
    if t0 > 0.05:
        ks.append({"t": round(t0, 2), "pose": {"x": float(x0), "y": float(y0), "giro": 0.0}, "ease": "linear"})
    for (ta, xa, ya), (tb, xb, yb) in zip(caminho, caminho[1:]):
        acum += abs(xb - xa) + abs(yb - ya)
        ks.append({"t": round(min(tb, d - 0.06), 2), "pose": {"x": float(xb), "y": float(yb), "giro": round(voltas * acum / max(1.0, tot), 3)},
                   "ease": "linear"})
        if yb >= CHAO - 5 and ya < CHAO - 60 and tb + 0.16 < d - 0.06:          # quique: achata e volta
            ks.append({"t": round(tb + 0.02, 2), "pose": {"amassa": 0.7}, "ease": "out"})
            ks.append({"t": round(tb + 0.16, 2), "pose": {"amassa": 0.0}, "ease": "out"})
    ks = sorted([k for k in ks if k["t"] <= d - 0.05], key=lambda k: k["t"])
    return {"id": "bola_futebol", "x": float(x0), "y": float(y0), "z": z, "depth": depth, "keys": ks}


def trave(x, d, gol_em=None, forca=1.0, depth=0.72, y=905):
    """Trave atrás da turma; no GOL (gol_em) a rede balança forte e vai acalmando."""
    o = obj("trave", x, y, depth, d, z=0, fixo={"rede": 0.0, "onda": 0.0})
    if gol_em is not None and gol_em < d - 0.3:
        o["keys"] += [{"t": round(gol_em, 2), "pose": {"rede": 0.0, "onda": 0.0}, "ease": "step"},
                      {"t": round(gol_em + 0.12, 2), "pose": {"rede": forca}, "ease": "out"},
                      {"t": round(d - 0.06, 2), "pose": {"rede": 0.15 * forca, "onda": round((d - gol_em) * 3.0, 2)}, "ease": "linear"}]
        o["keys"] = sorted(o["keys"], key=lambda k: k["t"])
    return o


def banda(cen, d, cam=None, extra=None):
    p = R.banda(cen, d, teclado=True, sax=ZU, bateria=BI, cam=cam or {"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["cantam"] = [ZU]
    return p


def em(t0, versos, *alvos, default=0.4):
    return R.tp(t0, versos, *alvos, default=default)


def chute_no_gol(quem, dd, t_chute, t_gol, x_q=500, x_gol=1650, cantam=None, callouts=(), forca=1.0, fofinho=False,
                 extra_atores=None, fx=None):
    """Plano CORPO no campinho: `quem` chuta (passo `chute`) e a bola entra na trave (rede balança, confete no gol)."""
    t_chute = max(0.15, min(t_chute, dd - 0.9))
    t_gol = max(t_chute + 0.35, min(t_gol, dd - 0.35))
    xb = x_q + 110
    alto = 860 if fofinho else 700
    cam = corpo(1350)
    # (trave em 1650 com câmera 1350 → 1565 depois de _aproximar = GX, onde o cenário desenha a área do gol)
    p = {"cenario": CAMPO_GOL, "camera": cam, "cantam": cantam or [quem], "callout": list(callouts), "fx": fx or ["confete"],
         "objetos": {"trave": trave(x_gol, dd, gol_em=t_gol, forca=forca),
                     "bola": bola([(t_chute, xb, CHAO), ((t_chute + t_gol) / 2, (xb + x_gol) / 2, alto), (t_gol, x_gol, CHAO - 120)], dd)},
         "atores": {quem: a(x_q, ("dance", max(0.0, t_chute - 0.35), "chute"), turn=0.35,
                           **({} if quem == ZU else {"expr": "determined"}))}}   # Zuzu: pálpebra achata o anel verde
    if extra_atores:
        p["atores"].update(extra_atores)
    return p


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
tg = em(T[1][0], T[1][2], "gol!", "gol", default=round(d[1] * 0.6, 2))
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "titulo": "o campinho da Vila Monstrinha", "cantam": [BI],
     "callout": [call(0.5, "GOL DE MONSTRINHO!", "roxo")],
     "objetos": {"bola": bola([(0.3, 300, CHAO), (1.6, 1170, CHAO)], d[0])},
     "atores": {BI: a(1300, ("look_around", 0.2), turn=-0.3)}},
    {**chute_no_gol(BI, d[1], round(tg - 0.6, 2), tg, cantam=[BI],
                    callouts=[call(0.1, "CHUTA, CHUTA…", "azul"), call(tg, "GOL!", "amarelo")]), "linhas": 1},
    {"linhas": 1, "cenario": "mon_raios_laranja", "camera": GCAM, "flash": True, "fx": ["estrelas"], "cantam": [GO],
     "callout": [call(0.1, "FOFOLUCOS! RAWR!", "roxo")],
     "atores": {TE: g(210, ("rawr", 0.3), turn=0.2), GO: g(710, ("rawr", 0.38)), BI: g(1210, ("rawr", 0.46)),
                NH: g(1710, ("rawr", 0.54), turn=-0.2)}},
    {**banda(PALCO, max(0.6, d[3]), extra={MI: a(2300, ("dance", 0.0, "chute"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: a escalação ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
tcab = round(min(1.3, d[4] - 0.9), 2)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": VILA, "camera": corpo(900, 1700), "callout": [call(0.3, "HOJE TEM JOGO!", "roxo")], "cantam": [BI],
     "objetos": {"bola": bola([(0.0, 820, CHAO), (min(2.2, d[0] - 0.1), 1700, CHAO)], d[0])},
     "atores": {BI: a(650, turn=0.3) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 1500, "dur": 2.2, "turn": 0.45}, {"t": 2.3, "do": "wave", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "callout": [call(0.2, "TODO MUNDO NO GRAMADO!", "verde")], "cantam": [MI],
     "atores": {TE: a(500, turn=0.3) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 1000, "dur": 1.2, "turn": 0.45}, {"t": 1.3, "do": "wave", "dur": "resto"}]},
                MI: a(2100, turn=-0.3) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 1600, "dur": 1.2, "turn": -0.45}, {"t": 1.3, "do": "wave", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": cab(1300), "callout": [call(0.3, "OLHÃO!", "amarelo")], "cantam": [GO],
     "atores": {GO: a(1300, ("look_around", 0.2), expr="surprised")}},
    {"linhas": 1, "cenario": "mon_brilho_azul", "camera": GCAM, "fx": ["estrelas"], "callout": [call(0.2, "VÊ O CAMPO TODO!", "verde")],
     "cantam": [GO], "objetos": {"bola": bola([(0.0, 1500, 1000), (d[3] - 0.1, 1500, 1000)], d[3], depth=0.85, giro=0.0)},
     "atores": {GO: g(700, ("point", 0.2), turn=0.3)}},
    {"linhas": 1, "cenario": CAMPO, "camera": busto(1300), "callout": [call(tcab, "CABEÇADA!", "laranja")], "cantam": [ZU],
     "objetos": {"bola": bola([(0.0, 350, 520), (tcab, 1300, 300), (tcab + 0.7, 2250, 420)], d[4])},
     "atores": {ZU: a(1300, ("dance", max(0.0, tcab - 0.3), "pulinho"))}},   # (sem "cabeca": inclina só o rosto)
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1100, 1900), "callout": [call(0.2, "CORRE, TECO!", "roxo")], "cantam": [TE],
     "objetos": {"bola": bola([(0.0, 700, CHAO), (d[5] - 0.1, 2250, CHAO)], d[5])},
     "atores": {TE: a(500, turn=0.4) | {"acoes": [{"t": 0.0, "do": "run", "to_x": 2050, "dur": round(max(0.8, d[5] - 0.2), 2), "turn": 0.45}]}}},
    {"linhas": 1, "cenario": CAMPO_GOL, "camera": corpo(GX), "callout": [call(0.3, "NHOQUE GOLEIRO!", "vermelho")], "cantam": [NH],
     "objetos": {"trave": trave(GX, d[6], depth=0.75)},
     "atores": {NH: a(GX, ("rawr", 0.4), z=3, expr="determined")}},
    {"linhas": 1, "cenario": CAMPO, "camera": busto(1300), "fx": ["coracoes"], "callout": [call(0.4, "BOLA DE TRAVESSEIRO?!", "rosa")],
     "cantam": [NH], "objetos": {"bola": bola([(0.1, 200, 400), (0.9, 1300, 905)], d[7], tipo=1.0, z=5)},
     "atores": {NH: a(1300, ("laugh", 1.0))}},
]


# ───────── refrão: chuta, chuta! passa pro amigo! GOL! ─────────
REF = {
    1: dict(passe=(BI, TE), gol=TE, danca=("mon_xadrez_verde", (MI, ZU, NH)), festa=BI, cor="amarelo"),
    2: dict(passe=(MI, ZU), gol=ZU, danca=("mon_xadrez_azul", (GO, TE, NH)), festa=ZU, cor="azul"),
    3: dict(passe=(NH, MI), gol=MI, danca=("mon_xadrez_roxo", (GO, BI, ZU)), festa=MI, cor="rosa"),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        tpassa = min(em(t0, versos, "passa", default=round(dd * 0.5, 2)), round(dd - 0.8, 2))
        tgol = min(em(t0, versos, "gol", default=round(dd * 0.55, 2)), round(dd - 0.7, 2))
        trawr = min(em(t0, versos, "rawr!", "rawr", default=round(dd * 0.8, 2)), round(dd - 0.4, 2))
        if i % 4 == 0:                                     # chuta e PASSA PRO AMIGO (a bola vai de um para o outro)
            p_, q_ = cfg["passe"]
            out.append({"linhas": 2, "cenario": CAMPO, "camera": corpo(1300), "cantam": [p_],
                        "callout": [call(0.1, "CHUTA, CHUTA, CHUTA!", "roxo"), call(tpassa, "PASSA PRO AMIGO!", "verde")],
                        "objetos": {"bola": bola([(tpassa - 0.15, 950, CHAO), (tpassa + 0.75, 1580, CHAO)], dd)},
                        "atores": {p_: a(820, ("dance", 0.0, "chute"), turn=0.35),
                                   q_: a(1780, ("wave", 0.1, 1.0), ("dance", tpassa + 0.8, "festa"), turn=-0.35)}})
        elif i % 4 == 1:                                   # chuta e GOL! (a rede balança)
            q_ = cfg["gol"]
            out.append({**chute_no_gol(q_, dd, round(tgol - 0.55, 2), tgol,
                                       callouts=[call(0.1, "CHUTA, CHUTA!", "azul"), call(tgol, "GOL!", cfg["cor"])]),
                        "linhas": 2, "flash": n == 3})
        elif i % 4 == 2:                                   # a dança do chute no xadrez
            cen, quem = cfg["danca"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["estrelas"], "cantam": [quem[1]],
                        "callout": [call(0.1, "CHUTA, CHUTA, CHUTA!", "laranja"), call(tpassa, "PASSA PRO AMIGO!", "verde")],
                        "atores": {c: g(x, ("dance", 0.05 * k, "chute"), turn=tv) for k, (c, x, tv) in
                                   enumerate(zip(quem, (380, 960, 1540), (0.2, 0.0, -0.2)))}})
        else:                                              # o artilheiro comemora: GOL DE MONSTRINHO! RAWR!
            q_ = cfg["festa"]
            out.append({"linhas": 2, "cenario": CAMPO, "camera": busto(1300) if q_ == ZU else cab(1300), "fx": ["confete"],
                        "cantam": [q_], "callout": [call(max(0.1, tgol - 0.1), "GOL DE MONSTRINHO!", "roxo")],
                        "atores": {q_: a(1300, ("laugh", 0.1, max(0.6, round(trawr - 0.3, 2))), ("rawr", trawr), expr="joy")}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 1}, {"seg": 4.6}, {"seg": 0.0}])
d = dur(T)
_, bl1 = R.bloco("intervalo#1")
tfo = round(bl1[-1]["s"] - T[2][0], 2) if len(bl1) > 1 else round(d[2] - 0.8, 2)
R.partes["intervalo#1"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": cab(1300), "cantam": [TE], "callout": [call(0.2, "FOFOLUCOS!", "roxo")],
     "atores": {TE: a(1300, ("rawr", 0.2), ("apontar_camera", 1.6))}},
    {**banda(PALCO, max(0.6, d[1]), extra={NH: a(2300, ("dance", 0.0, "chute"), turn=-0.3)}), "titulo": "a banda"},
    {"seg": max(0.6, d[2]), "cenario": CAMPO, "camera": corpo(1300), "fx": ["confete"], "titulo": "a turma bate bola",
     "cantam": [MI], "callout": [call(max(0.1, min(tfo, d[2] - 0.7)), "FOFOLUCOS!", "roxo")],
     "objetos": {"bola": bola([(0.2, 900, CHAO), (1.0, 1620, CHAO), (1.9, 900, CHAO), (2.8, 1620, CHAO), (3.7, 900, CHAO),
                               (4.6, 1620, CHAO)], d[2])},
     "atores": {MI: a(700, ("dance", 0.0, "chute"), turn=0.35), ZU: a(1850, ("dance", 0.3, "chute"), turn=-0.35)}},
]


# ───────── ponte: comandos de jogo ─────────
T = R.tempos("ponte#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 2}, {"linhas": 1},
                         {"linhas": 1}, {"linhas": 1}])
d = dur(T)
tja = em(T[3][0], T[3][2], "já!", "já", default=round(d[3] * 0.7, 2))
tab = round(min(0.8, d[4] * 0.4), 2)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": "mon_xadrez_azul", "camera": GCAM, "callout": [call(0.05, "CORRE NO LUGAR!", "azul")],
     "cantam": [TE], "atores": {TE: g(380, ("dance", 0.0, "marcha"), turn=0.2), MI: g(960, ("dance", 0.05, "marcha")),
                                 NH: g(1540, ("dance", 0.1, "marcha"), turn=-0.2)}},
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "callout": [call(0.1, "PULA PRA CABECEAR!", "laranja")], "cantam": [BI],
     "objetos": {"bola": bola([(0.0, 400, 520), (0.65, 1300, 230), (1.4, 2300, -100)], d[1])},
     "atores": {BI: a(1300, expr="determined") | {"acoes": [{"t": 0.3, "do": "jump", "dur": 0.7, "height": 140}]}}},
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "callout": [call(0.05, "DRIBLA PRO LADINHO!", "roxo")], "cantam": [TE],
     "objetos": {"bola": bola([(0.0, 1180, CHAO), (0.35, 1420, CHAO), (0.7, 1180, CHAO), (1.05, 1420, CHAO)], d[2])},
     "atores": {TE: a(1300, ("dance", 0.0, "lado"), turn=0.1)}},
    {**chute_no_gol(MI, d[3], round(tja - 0.5, 2), tja, callouts=[call(0.05, "CHUTA PRO GOL: JÁ!", "rosa")]), "linhas": 1},
    {"linhas": 2, "cenario": CAMPO_GOL, "camera": corpo(GX), "callout": [call(0.05, "E MAIS!", "roxo"), call(tab, "ABRE OS BRAÇOS, GOLEIRO!", "vermelho")],
     "cantam": [NH], "objetos": {"trave": trave(GX, d[4], depth=0.75)},
     "atores": {NH: a(GX, ("rawr", tab), z=3, expr="determined")}},
    {"linhas": 1, "cenario": CAMPO, "camera": busto(1300), "callout": [call(0.1, "PEGA A BOLA NO AR!", "azul")], "cantam": [NH],
     "objetos": {"bola": bola([(0.1, 250, 400), (0.8, 1300, 905)], d[5], z=5)},
     "atores": {NH: a(1300, ("bacana", 0.9), expr="joy")}},
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "fx": ["confete"], "callout": [call(0.1, "COMEMORA COM A TURMA!", "verde")],
     "cantam": [MI], "atores": {BI: a(640, ("abraco", 0.2), turn=0.3), MI: a(1300, ("laugh", 0.1)), ZU: a(1960, ("abraco", 0.3), turn=-0.3)}},
    {"linhas": 1, "cenario": "mon_brilho_laranja", "camera": GCAM, "fx": ["estrelas"], "callout": [call(0.1, "DANÇA DO GOL!", "rosa")],
     "cantam": [GO], "atores": {GO: g(210, ("dance", 0.0, "festa"), turn=0.2), TE: g(710, ("dance", 0.05, "festa")),
                                 MI: g(1210, ("dance", 0.1, "festa")), BI: g(1710, ("dance", 0.15, "festa"), turn=-0.2)}},
]


# ───────── 2º verso: a VIRADA — bateu na lua e caiu no pé da Mimi ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
tbate = round(min(0.7, d[2] - 0.6), 2)
tpe = round(min(0.8, d[4] - 0.5), 2)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "tremor": [0.6], "callout": [call(0.2, "CHUTOU COM FORÇA!", "azul")],
     "cantam": [BI], "objetos": {"bola": bola([(0.55, 1210, CHAO), (1.3, 1700, -200)], d[0])},
     "atores": {BI: a(1100, ("dance", 0.2, "chute"), turn=0.35, expr="determined")}},
    {"linhas": 1, "cenario": CEU, "camera": corpo(1300), "callout": [call(0.2, "SUBIU, SUBIU…", "roxo")], "cantam": [GO],
     "objetos": {"bola": bola([(0.0, 1500, 1150), (d[1] - 0.1, 1700, 150)], d[1])},
     "atores": {GO: a(800, ("look_around", 0.2), turn=0.3, expr="surprised")}},
    {"linhas": 1, "cenario": CEU, "camera": corpo(1300), "tremor": [tbate], "fx": ["estrelas"],
     "callout": [call(max(0.1, tbate - 0.1), "BATEU NA LUA!", "amarelo")], "cantam": [BI],
     "objetos": {"lua": obj("lua", 1600, 900, 0.62, d[2], z=1, fixo={"boca": 0.0, "brilho": 0.4}, pts={"boca": [(tbate, 1.0)]}),
                 "bola": bola([(0.0, 900, 1150), (tbate, 1380, 420), (tbate + 0.9, 700, 1250)], d[2])}},
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "callout": [call(0.2, "QUEM VIU? QUEM VIU?", "laranja")], "cantam": [TE],
     "objetos": {"bola": bola([(0.0, 1300, -200), (d[3] - 0.1, 1300, 250)], d[3])},
     "atores": {TE: a(800, ("look_around", 0.1), turn=0.3, expr="surprised"), BI: a(1800, ("look_around", 0.2), turn=-0.3, expr="surprised")}},
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "callout": [call(0.2, "NO PÉ DA MIMI!", "rosa")], "cantam": [MI],
     "objetos": {"bola": bola([(0.0, 1450, 100), (tpe, 1420, CHAO), (tpe + 0.3, 1430, CHAO - 50), (tpe + 0.55, 1440, CHAO)], d[4])},
     "atores": {MI: a(1300, ("shock_reaction", tpe, 0.7), expr="surprised")}},
    {"linhas": 1, "cenario": CAMPO, "camera": cab(1300), "callout": [call(0.2, "ELA SÓ OLHAVA…", "rosa")], "cantam": [MI],
     "atores": {MI: a(1300, ("look_around", 0.2), expr="surprised")}},
    {**chute_no_gol(MI, d[6], 0.5, round(d[6] - 0.4, 2), forca=0.5, fofinho=True,
                    callouts=[call(0.2, "CHUTOU FOFINHO…", "rosa")], fx=["coracoes"]), "linhas": 1},
    {"linhas": 1, "cenario": CAMPO, "camera": corpo(1300), "flash": True, "fx": ["confete"],
     "callout": [call(0.1, "FOI GOL!", "amarelo"), call(round(d[7] * 0.45, 2), "TODO MUNDO PULANDO!", "verde")], "cantam": [MI],
     "atores": {TE: a(400, ("dance", 0.1, "pulinho"), turn=0.3), MI: a(1000, ("dance", 0.0, "pulinho"), turn=0.15),
                NH: a(1600, ("dance", 0.05, "pulinho"), turn=-0.15), BI: a(2200, ("dance", 0.1, "pulinho"), turn=-0.3)}},
]


# ───────── intervalo 2 (só instrumental) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 3, 2)
R.partes["intervalo#2"] = [
    {**banda(PALCO, d1, extra={GO: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "a banda"},
    {"seg": d1, "cenario": CAMPO, "camera": corpo(1300), "titulo": "embaixadinha", "cantam": [TE],
     "objetos": {"bola": bola([(0.0, 1480, 800), (0.5, 1480, CHAO), (1.0, 1480, 800), (1.5, 1480, CHAO), (2.0, 1480, 800),
                               (2.5, 1480, CHAO), (3.0, 1480, 800), (3.5, 1480, CHAO), (4.0, 1480, 800)], d1, giro=3.0)},
     "atores": {TE: a(1300, ("dance", 0.0, "joelho"), turn=-0.1)}},
    {"seg": round(D2 - 2 * d1, 2), "cenario": "mon_raios_verde", "camera": GCAM, "fx": ["estrelas"], "titulo": "pezinho", "cantam": [TE],
     "atores": {TE: g(210, ("dance", 0.0, "pezinho"), turn=0.2), BI: g(710, ("dance", 0.05, "pezinho")),
                ZU: g(1210, ("dance", 0.1, "pezinho")), NH: g(1710, ("dance", 0.15, "pezinho"), turn=-0.2)}},
]


# ───────── final: e você? gosta de jogar bola? + convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4 + [{"seg": 0.0}])
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": CAMPO, "camera": cab(1300), "callout": [call(0.2, "E VOCÊ? GOSTA DE JOGAR BOLA?", "roxo")], "cantam": [BI],
     "atores": {BI: a(1300, ("apontar_camera", 0.1))}},
    {"linhas": 1, "cenario": "mon_brilho_rosa", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "cantam": [ZU],
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
    {"seg": max(0.6, d[4]), "cenario": CAMPO, "camera": corpo(1300), "fx": ["confete"], "titulo": "a turma dança no campinho",
     "cantam": [NH], "objetos": {"bola": bola([(0.0, 1430, CHAO), (0.1, 1430, CHAO)], d[4], giro=0.0)},
     "atores": {BI: a(640, ("dance", 0.0, "festa"), turn=0.3), NH: a(1300, ("dance", 0.1, "chute")),
                TE: a(1960, ("dance", 0.05, "festa"), turn=-0.3)}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.0, "cenario": CEU, "camera": corpo(1300), "fx": ["estrelas"], "cantam": [BI],
     "callout": [call(0.2, "FOFOLUCOS!", "roxo"), call(1.4, "TCHAU!", "amarelo")],
     "atores": {c: a(x, ("wave", 0.0 + 0.1 * k), turn=tn, y=y, depth=dp, z=zz) for k, (c, x, y, dp, zz, tn) in
                enumerate(((TE, 400, 880, 0.62, 2, 0.3), (GO, 1000, 880, 0.62, 2, 0.15), (MI, 1600, 880, 0.62, 2, -0.15),
                           (ZU, 2200, 880, 0.62, 2, -0.3), (BI, 700, 975, 0.74, 3, 0.2), (NH, 1900, 975, 0.74, 3, -0.2)))}},
    {"seg": round(dfim - 3.0, 2), "cenario": CAMPO, "camera": cab(1300), "flash": True, "fx": ["confete"],
     "callout": [call(0.2, "RAWR!", "vermelho")], "titulo": "o último RAWR da Mimi artilheira", "cantam": [MI],
     "atores": {MI: a(1300, ("rawr", 0.1), expr="joy")}},
]


# ── vida no cenário (sem contorno): nuvens andando no céu, bolhas nos fundos gráficos ──
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

R.salvar("Roteiro do canal Fofolucos — 05 'Gol de Monstrinho!' (take inteiro, 2:36, F4, nota 4,9): futebol na Vila "
         "Monstrinha — cada um joga do seu jeito; refrão do passe e do gol (rede balançando); ponte de comandos de jogo; "
         "a virada: a bola bate na lua e cai no pé da Mimi, que faz o gol. Gerado por scripts/roteiros/fo05_gol_de_monstrinho.py.")
