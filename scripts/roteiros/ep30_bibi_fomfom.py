"""Roteiro verso a verso de 30 "Bi-Bi, Fom-Fom!" (take inteiro, 2:33, 136 BPM, Lá# maior, estilo E17 — groove próprio,
nota 4,9) → canais/laurinha/musicas/30_bibi_fomfom/roteiro.json.

O PASSEIO DE CARRINHO na cidade (cenário novo `plano_rua`: lojinhas, calçada, faixa de pedestre): a Laurinha dirige o
CARRINHO ABERTO (prop novo `carrinho_aberto`, rodas girando), na frente um ÔNIBUS (`onibus`), atrás o Luisinho na
MOTINHA (`moto`); o SEMÁFORO (`semaforo`) fica vermelho — todo mundo para — verde, vai! — e a buzina: BI-BI!
Ponte = os barulhos (fom, vrum, piuí, bi-bi… zuum, tuuu, uiô) em fundos coloridos.
2º verso = a VIRADA: o trânsito para e quem atravessa na faixa é a mamãe pata com seis patinhos (`pato`), bem devagar;
ninguém buzina, todo mundo espera… "Quá-quá, obrigada!" e o trânsito anda.
Padrão novo da Laurinha (21/11): CABEÇA / BUSTO / CORPO, nitidez; só teclado/baixo/bateria na banda (que toca NA RUA,
festa da cidade — nada de salão lilás).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep30_bibi_fomfom.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, LA, LU, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("laurinha/ep30-bibi-fomfom", "30_bibi_fomfom", "laurinha")
RUA, CASA, PARQUE, SALA = "plano_rua", "plano_casa_frente", "plano_parque", "plano_sala"
MA = "mamae"
CHAO = 930


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


def veiculo(tipo, quem, x0, x1, d, *, cor=1, acoes=(), turn=0.3, depth=0.8, rodas=2.5, nome=None):
    """um veículo andando de x0 a x1 (rodas girando) com o motorista ATRÁS dele no mesmo x (aparece do peito para cima).
    Devolve (objetos, atores)."""
    fixo = {"cor": float(cor)} if tipo == "carrinho_aberto" else {}
    o = obj(tipo, x0, CHAO, depth, d, z=4, fixo=fixo, lin={"x": (x0, x1), "roda": (0.0, round(d * rodas, 1)) if x0 != x1 else (0.0, 0.0)})
    if x0 == x1:
        o["keys"] = [k for k in o["keys"] if "roda" not in k["pose"] or k["t"] == 0.0]
    dx = -60 if tipo == "carrinho_aberto" else 40
    atores = {}
    if quem:
        # sentado no banco: mais alto que o chão, pés escondidos atrás da lataria (usuário, 21/11: "dá pra ver o pé dela embaixo")
        at = a(x0 + dx, *acoes, turn=turn, y=CHAO - (115 if tipo == "carrinho_aberto" else 95), depth=depth, z=3)
        if x0 != x1:
            at["keys"] = [{"t": 0.0, "pose": {"x": x0 + dx}, "ease": "step"},
                          {"t": round(max(0.6, d) - 0.06, 2), "pose": {"x": x1 + dx}, "ease": "linear"}]
        atores[quem] = at
    return {nome or tipo: o}, atores


def semaforo(x, luz, d, troca=None, depth=0.7):
    """semáforo na calçada; `troca` = [(t, luz)] para mudar de cor durante o plano."""
    return obj("semaforo", x, 920, depth, d, z=1, fixo={"luz": float(luz)},
               pts={"luz": [(t, v) for t, v in (troca or [])]} if troca else None)


def patos(x0, x1, d, n=6, y=CHAO):
    """mamãe pata na frente e os patinhos em fila atrás, andando de x0 até x1."""
    ob = {"pata": obj("pato", x0, y, 0.9, d, z=4, lin={"x": (x0, x1), "pulo": (0.0, 0.0)}, pts={"asas": [(0.3, 0.4)]})}
    for j in range(n):
        xo = x0 - 190 - j * 150
        ob[f"p{j}"] = obj("pato", xo, y + 10, 0.45, d, z=4, lin={"x": (xo, xo + (x1 - x0))})
    return ob


def banda(d, extra=None):
    """a banda toca NA RUA (festa da cidade): Laurinha no teclado, Luisinho na bateria; quem dança fica à DIREITA."""
    p = R.banda(RUA, d, teclado=True, sax=LA, bateria=LU, cam={"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["cantam"] = [LA]
    return p


def junta(*partes):
    ob, at = {}, {}
    for o, t in partes:
        ob.update(o)
        at.update(t)
    return ob, at


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
ob0, at0 = veiculo("carrinho_aberto", LA, 300, 1300, d[0], acoes=(("wave", 1.5),))
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": RUA, "camera": corpo(1100), "titulo": "o passeio de carrinho",
     "callout": [call(0.4, "BI-BI, FOM-FOM!", "vermelho")], "objetos": ob0, "atores": at0},
    {"linhas": 1, "cenario": RUA, "camera": busto(1240), "callout": [call(0.2, "BI-BI!", "amarelo")],
     "objetos": veiculo("carrinho_aberto", LA, 1300, 1300, d[1])[0],
     "atores": veiculo("carrinho_aberto", LA, 1300, 1300, d[1], acoes=(("apontar_camera", 0.2),), turn=0.15)[1]},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "camera": GCAM, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "LAURINHA E LUISINHO!", "roxo")],
     "atores": {LA: g(640, ("wave", 0.1), turn=0.25) | {"depth": 1.05}, LU: g(1280, ("wave", 0.2), turn=-0.25) | {"depth": 1.05}}},
    {**banda(max(0.6, d[3]), extra={MA: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "a banda na rua"},
]


# ───────── 1º verso: o passeio, o ônibus, a motinha e o semáforo ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = []
ob, at = veiculo("carrinho_aberto", LA, 200, 1100, d[0], acoes=(("wave", 0.8),))
R.partes["verso#1"].append({"linhas": 1, "cenario": RUA, "camera": corpo(800, 1100), "callout": [call(0.3, "SAÍ NO MEU CARRINHO!", "rosa")],
                            "objetos": ob, "atores": at})
ob, at = veiculo("carrinho_aberto", LA, 1300, 1300, d[1], acoes=(("wave", 0.2),), turn=0.2)
R.partes["verso#1"].append({"linhas": 1, "cenario": PARQUE, "camera": busto(1240), "callout": [call(0.3, "UMA VOLTINHA!", "verde")],
                            "objetos": ob, "atores": at})
ob, at = junta(veiculo("carrinho_aberto", LA, 450, 450, d[2], acoes=(("look_around", 0.3),), turn=0.3),
               ({"bus": obj("onibus", 2050, CHAO, 0.85, d[2], z=4)}, {}))
R.partes["verso#1"].append({"linhas": 1, "cenario": RUA, "camera": corpo(1250), "callout": [call(0.3, "UM ÔNIBUS NA FRENTE!", "amarelo")],
                            "objetos": ob, "atores": at})
ob, at = junta(veiculo("carrinho_aberto", LA, 1950, 1950, d[3], acoes=(("look_around", 0.2),), turn=-0.3),
               veiculo("moto", LU, 400, 650, d[3], acoes=(("wave", 0.4),), turn=0.3))
R.partes["verso#1"].append({"linhas": 1, "cenario": RUA, "camera": corpo(1200), "callout": [call(0.3, "E ATRÁS UMA MOTINHA!", "verde")],
                            "objetos": ob, "atores": at})
R.partes["verso#1"].append({"linhas": 1, "cenario": RUA, "camera": {"x": 1300, "y": 420, "zoom": 1.3, "zoom_fim": 1.38},
                            "callout": [call(0.3, "VERMELHO!", "vermelho")], "objetos": {"sem": semaforo(1300, 0, d[4])}})
ob, at = junta(veiculo("carrinho_aberto", LA, 1950, 1950, d[5], turn=0.3), veiculo("moto", LU, 650, 650, d[5], turn=0.3),
               ({"sem": semaforo(2350, 0, d[5])}, {}))
R.partes["verso#1"].append({"linhas": 1, "cenario": RUA, "camera": corpo(1300), "callout": [call(0.2, "TODO MUNDO PAROU!", "laranja")],
                            "objetos": ob, "atores": {k: v | {"expr": "surprised"} for k, v in at.items()}})
R.partes["verso#1"].append({"linhas": 1, "cenario": RUA, "camera": {"x": 1300, "y": 420, "zoom": 1.3, "zoom_fim": 1.38},
                            "callout": [call(0.5, "VERDE… VAI!", "verde")],
                            "objetos": {"sem": semaforo(1300, 0, d[6], troca=[(0.4, 2.0)])}})
ob, at = veiculo("carrinho_aberto", LA, 1300, 1300, d[7], acoes=(("apontar_camera", 0.1),), turn=0.15)
R.partes["verso#1"].append({"linhas": 1, "cenario": RUA, "camera": cab(1240), "callout": [call(0.2, "BI-BI!", "vermelho")],
                            "objetos": ob, "atores": at})


# ───────── refrão: bi-bi, fom-fom! lá vem o carro! sai da frente, cachorro! ─────────
REF = {
    1: dict(passa=(LA, 1), buzina=(LU, CASA), danca=("danca_xadrez_verde", (LA, LU, MA)), close=(LA, PARQUE)),
    2: dict(passa=(LU, 2), buzina=(LA, PARQUE), danca=("danca_bolinhas_laranja", (LU, MA, LA)), close=(LU, CASA)),
    3: dict(passa=(LA, 3), buzina=(MA, CASA), danca=("danca_raios_verde", (MA, LA, LU)), close=(LA, RUA)),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        if i % 4 == 0:                                     # "Bi-bi, fom-fom! Lá vem o carro!" — passa o carrinho na rua
            quem, cor = cfg["passa"]
            ob, at = veiculo("carrinho_aberto", quem, 200, 2300, dd, cor=cor, acoes=(("wave", 0.6),), rodas=4.0)
            out.append({"linhas": 2, "cenario": RUA, "camera": corpo(800, 1800), "cantam": [quem],
                        "callout": [call(0.1, "BI-BI, FOM-FOM!", "vermelho"), call(round(dd * 0.5, 2), "LÁ VEM O CARRO!", "azul")],
                        "objetos": ob, "atores": at})
        elif i % 4 == 1:                                   # "Sai da frente, cachorro!" — busto buzinando
            quem, cen = cfg["buzina"]
            out.append({"linhas": 2, "cenario": cen, "camera": busto(1300), "cantam": [quem],
                        "callout": [call(round(dd * 0.45, 2), "SAI DA FRENTE!", "laranja")],
                        "atores": {quem: a(1300, ("point", round(dd * 0.4, 2)))}})
        elif i % 4 == 2:                                   # a dança do volante no fundo colorido
            cen, quem = cfg["danca"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "flash": n == 1, "cantam": [quem[0]],
                        "callout": [call(0.1, "BI-BI, FOM-FOM!", "vermelho")],
                        "atores": {c: g(x, ("dance", 0.05 * j, st), turn=tv) for j, (c, x, tv, st) in
                                   enumerate(zip(quem, (380, 960, 1540), (0.2, 0.0, -0.2), ("roda", "festa", "roda")))}})
        else:                                              # CABEÇA no carrinho: BI-BI!
            quem, cen = cfg["close"]
            ob, at = veiculo("carrinho_aberto", quem, 1300, 1300, dd, cor=2 if quem == LU else 1,
                             acoes=(("apontar_camera", round(dd * 0.3, 2)),), turn=0.15)
            out.append({"linhas": 2, "cenario": cen, "camera": cab(1240), "cantam": [quem],
                        "callout": [call(round(dd * 0.3, 2), "BI-BI!", "amarelo")], "objetos": ob, "atores": at})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 2}, {"seg": 6.0}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 2, "cenario": CASA, "camera": cab(1300), "cantam": [LU], "callout": [call(0.2, "BORA, TURMINHA!", "laranja")],
     "atores": {LU: a(1300, ("apontar_camera", 0.1), ("wave", 2.0))}},
    {**banda(max(0.6, d[1]), extra={MA: a(2300, ("dance", 0.0, "palmas"), turn=-0.3)}), "titulo": "a banda na rua"},
    {"seg": max(0.6, d[2]), "cenario": "danca_ondas_amarelo", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança",
     "atores": {LA: g(380, ("dance", 0.0, "cintura"), turn=0.2), MA: g(960, ("dance", 0.1, "festa")),
                LU: g(1540, ("dance", 0.0, "bracos"), turn=-0.2)}},
]


# ───────── ponte: os barulhos ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4 + [{"linhas": 2}] + [{"linhas": 1}] * 3)     # "E mais!" (0,5 s) junto com o avião
d = dur(T)
SONS = [("O CAMINHÃO: FOM!", "danca_raios_laranja", LU, "bracos", "laranja"),
        ("A MOTO: VRUM!", None, None, None, "verde"),
        ("O TREM: PIUÍ!", "danca_xadrez_amarelo", LA, "marcha", "azul"),
        ("E O CARRINHO? BI-BI! TCHUM!", None, None, None, "rosa"),
        ("E MAIS! O AVIÃO: ZUUM!", "danca_raios_azul", LA, "asinhas", "azul"),
        ("O BARCO: TUUU!", "danca_ondas_verde", LU, "balanco", "azul"),
        ("A AMBULÂNCIA: UIÔ, UIÔ!", "danca_raios_vermelho", MA, "roda", "vermelho"),
        ("BI-BI! TCHUM!", None, None, None, "rosa")]
R.partes["ponte#1"] = []
for j, (txt, cen, quem, st, cor) in enumerate(SONS):
    if j == 1:                                             # a moto passa de verdade
        ob, at = veiculo("moto", LU, 300, 2000, d[j], acoes=(("wave", 0.3),), rodas=4.0)
        R.partes["ponte#1"].append({"linhas": 1, "cenario": RUA, "camera": corpo(800, 1500), "callout": [call(0.1, txt, cor)],
                                    "objetos": ob, "atores": at})
    elif j in (3, 7):                                      # o carrinho buzina
        ob, at = veiculo("carrinho_aberto", LA, 1300, 1300, d[j], acoes=(("apontar_camera", 0.1),), turn=0.15)
        R.partes["ponte#1"].append({"linhas": 1, "cenario": RUA, "camera": busto(1240), "callout": [call(0.1, txt, cor)],
                                    "objetos": ob, "atores": at})
    else:
        R.partes["ponte#1"].append({"linhas": 2 if j == 4 else 1, "cenario": cen, "camera": GCAM, "callout": [call(0.1, txt, cor)],
                                    "atores": {quem: g(960, ("dance", 0.0, st)) | {"depth": 1.15}}})


# ───────── 2º verso: a VIRADA — a mamãe pata e os seis patinhos na faixa ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#2"] = []
ob, at = junta(veiculo("carrinho_aberto", LA, 500, 500, d[0], turn=0.3), ({"sem": semaforo(1000, 0, d[0])}, {}))
R.partes["verso#2"].append({"linhas": 1, "cenario": RUA, "camera": corpo(900), "callout": [call(0.2, "PAROU TUDO!", "vermelho")],
                            "objetos": ob, "atores": {k: v | {"expr": "surprised"} for k, v in at.items()}})
ob, at = veiculo("carrinho_aberto", LA, 1300, 1300, d[1], acoes=(("look_around", 0.1),), turn=0.2)
R.partes["verso#2"].append({"linhas": 1, "cenario": RUA, "camera": busto(1240), "callout": [call(0.2, "QUEM TÁ PASSANDO?", "roxo")],
                            "objetos": ob, "atores": at})
R.partes["verso#2"].append({"linhas": 1, "cenario": RUA, "camera": corpo(1300), "fx": ["coracoes"],
                            "callout": [call(0.2, "UMA PATA E SEIS PATINHOS!", "amarelo")], "objetos": patos(1150, 1450, d[2])})
R.partes["verso#2"].append({"linhas": 1, "cenario": RUA, "camera": {"x": 1550, "y": 620, "zoom": 1.6, "zoom_fim": 1.7},
                            "callout": [call(0.2, "BEM DEVAGAR…", "rosa")], "objetos": patos(1450, 1700, d[3])})
ob, at = junta(veiculo("carrinho_aberto", LA, 1950, 1950, d[4], turn=0.3), veiculo("moto", LU, 650, 650, d[4], turn=0.3))
R.partes["verso#2"].append({"linhas": 1, "cenario": RUA, "camera": corpo(1300), "callout": [call(0.2, "NINGUÉM BUZINOU!", "verde")],
                            "objetos": ob, "atores": at})
ob, at = veiculo("carrinho_aberto", LA, 1300, 1300, d[5], turn=0.2)
R.partes["verso#2"].append({"linhas": 1, "cenario": RUA, "camera": busto(1240), "fx": ["coracoes"],
                            "callout": [call(0.2, "TODO MUNDO ESPEROU…", "azul")], "objetos": ob,
                            "atores": {k: v | {"expr": "happy"} for k, v in at.items()}})
pata = obj("pato", 1300, CHAO, 1.3, d[6], z=4, pts={"quem": [(0.2, 1.0), (0.45, 0.0), (0.7, 1.0), (0.95, 0.0)], "asas": [(0.3, 1.0)]})
R.partes["verso#2"].append({"linhas": 1, "cenario": RUA, "camera": {"x": 1300, "y": 620, "zoom": 1.5, "zoom_fim": 1.6}, "fx": ["coracoes"],
                            "callout": [call(0.2, "QUÁ-QUÁ, OBRIGADA!", "rosa")], "objetos": {"pata": pata}})
ob, at = junta(veiculo("carrinho_aberto", LA, 1100, 2300, d[7], acoes=(("wave", 0.3),)), veiculo("moto", LU, -100, 800, d[7], turn=0.3),
               ({"sem": semaforo(2200, 2, d[7])}, {}))
R.partes["verso#2"].append({"linhas": 1, "cenario": RUA, "camera": corpo(1000, 1500), "callout": [call(0.2, "O TRÂNSITO ANDOU!", "verde")],
                            "objetos": ob, "atores": at})


# ───────── intervalo 2 (só instrumental, ~14 s) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 2, 2)
R.partes["intervalo#2"] = [
    {**banda(d1, extra={MA: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "a banda na rua"},
    {"seg": round(D2 - d1, 2), "cenario": "danca_xadrez_laranja", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança",
     "atores": {MA: g(380, ("dance", 0.0, "palmas"), turn=0.2), LA: g(960, ("dance", 0.1, "roda")),
                LU: g(1540, ("dance", 0.0, "palmas"), turn=-0.2)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": RUA, "camera": cab(1240), "callout": [call(0.2, "GOSTOU DO PASSEIO?", "rosa")],
     "objetos": veiculo("carrinho_aberto", LA, 1300, 1300, d[0])[0],
     "atores": veiculo("carrinho_aberto", LA, 1300, 1300, d[0], acoes=(("apontar_camera", 0.1),), turn=0.15)[1]},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": CASA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {LA: a(950, ("point", 0.1), turn=0.3), MA: a(1650, ("wave", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LA: g(560, ("point", 0.2), turn=0.2) | {"depth": 1.0}}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
ob, at = junta(veiculo("carrinho_aberto", LA, 1950, 1950, 3.2, acoes=(("wave", 0.0),), turn=0.3),
               veiculo("moto", LU, 650, 650, 3.2, acoes=(("wave", 0.1),), turn=0.3))
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.2, "cenario": RUA, "camera": corpo(1300), "fx": ["coracoes"],
     "callout": [call(0.2, "BI-BI, FOM-FOM!", "vermelho"), call(1.5, "TCHAU!", "amarelo")], "objetos": ob, "atores": at},
    {"seg": round(dfim - 3.2, 2), "cenario": RUA, "camera": cab(1240), "flash": True, "callout": [call(0.2, "BI-BI!", "rosa")],
     "titulo": "a última buzinada", "objetos": veiculo("carrinho_aberto", LA, 1300, 1300, round(dfim - 3.2, 2))[0],
     "atores": veiculo("carrinho_aberto", LA, 1300, 1300, round(dfim - 3.2, 2), acoes=(("apontar_camera", 0.1),), turn=0.15)[1]},
]

R.salvar("Roteiro de 30 'Bi-Bi, Fom-Fom!' (take inteiro, 2:33, E17, nota 4,9): passeio de carrinho na rua (plano_rua), "
         "ônibus na frente, Luisinho na motinha, semáforo vermelho/verde, a ponte dos barulhos e a VIRADA da mamãe pata com "
         "seis patinhos na faixa. Gerado por scripts/roteiros/ep30_bibi_fomfom.py.")
