"""Roteiro verso a verso de 29 "Mamãe Querida" (take "(3)" inteiro, 2:31, 136 BPM, Ré maior, estilo E16 — groove próprio,
nota 4,8) → canais/laurinha/musicas/29_mamae_querida/roteiro.json.

DIA DAS MÃES. O superpoder da mamãe (acha tudo, sara o dodói com beijinho) e a VIRADA do 2º verso: a mamãe procura os
óculos pela casa toda (chão, bolsa, sofá, geladeira)… e eles estavam NA CABEÇA dela (canal novo `oculos_cabeca` no
FlatMuri) — quem achou foi a Laurinha. 1º clipe da Laurinha no padrão do Fofolucos (21/11): CABEÇA / BUSTO / CORPO
misturados (`cab`, `busto`, `corpo`, `GCAM` do _comum), nitidez nova, só teclado/baixo/bateria na banda (sem sax).
A banda toca na SALA de casa (festa da família; nada de salão lilás).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep29_mamae_querida.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, LA, LU, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("laurinha/ep29-mamae-querida", "29_mamae_querida", "laurinha")
SALA, CASA, QROSA, COZ, JARDIM, PARQUE = "plano_sala", "plano_casa_frente", "plano_quarto_azul", "plano_cozinha", "plano_jardim", "plano_parque"
MA, VO = "mamae", "vovo"
OC = {"oculos_cabeca": 1.0}                                   # óculos em cima da cabeça da mamãe (2º verso)


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


def banda(d, extra=None):
    """a banda da família na sala: Laurinha no teclado, Luisinho na bateria; quem dança junto fica à DIREITA."""
    p = R.banda(SALA, d, teclado=True, sax=LA, bateria=LU, cam={"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04}, extra=extra)
    p["cantam"] = [LA]
    return p


# ───────── intro ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": CASA, "camera": corpo(1300), "fx": ["coracoes"], "titulo": "Mamãe querida!",
     "callout": [call(0.3, "MAMÃE QUERIDA!", "rosa")],
     "atores": {LA: a(950, ("abraco", 0.5), turn=0.35), MA: a(1650, ("abraco", 0.6), turn=-0.35)}},
    {"linhas": 1, "cenario": JARDIM, "camera": cab(1300), "fx": ["coracoes"], "cantam": [LA],
     "atores": {MA: a(1300, ("beijo", 0.3))}},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "camera": GCAM, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "LAURINHA E LUISINHO!", "roxo")],
     "atores": {LA: g(640, ("wave", 0.1), turn=0.25) | {"depth": 1.05}, LU: g(1280, ("wave", 0.2), turn=-0.25) | {"depth": 1.05}}},
    {**banda(max(0.6, d[3]), extra={MA: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "teclado, baixo e bateria"},
]


# ───────── 1º verso: o superpoder da mamãe ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "callout": [call(0.3, "A MINHA MAMÃE…", "rosa")],
     "atores": {LA: a(1300, ("apontar_camera", 0.2))}},
    {"linhas": 1, "cenario": "danca_raios_azul", "camera": GCAM, "fx": ["estrelas"], "cantam": [LA],
     "callout": [call(0.2, "TEM UM SUPERPODER!", "amarelo")], "atores": {MA: g(960, ("bacana", 0.2)) | {"depth": 1.25}}},
    {"linhas": 1, "cenario": QROSA, "camera": busto(1300), "cantam": [LA], "callout": [call(0.2, "ACHA QUALQUER COISA!", "verde")],
     "atores": {MA: a(1300, ("look_around", 0.1))}},
    {"linhas": 1, "cenario": QROSA, "camera": cab(1300), "callout": [call(0.2, "CADÊ?", "laranja")],
     "atores": {LA: a(1300, ("look_around", 0.1), expr="confused")}},
    {"linhas": 1, "cenario": QROSA, "camera": corpo(1300), "callout": [call(0.3, "O SAPATO!", "azul")], "cantam": [LA],
     "atores": {MA: a(900, ("entregar", 0.3), turn=0.35, segura="sapato"), LA: a(1700, ("dance", 0.5, "pulinho"), turn=-0.35)}},
    {"linhas": 1, "cenario": QROSA, "camera": corpo(1300), "callout": [call(0.3, "O BONÉ!", "laranja")], "cantam": [LA],
     "atores": {MA: a(900, ("point", 0.2), turn=0.35), LU: a(1700, ("dance", 0.4, "pulinho"), turn=-0.35)}},
    {"linhas": 1, "cenario": JARDIM, "camera": cab(1300), "fx": ["coracoes"], "callout": [call(0.3, "UM BEIJINHO…", "rosa")],
     "cantam": [LA], "atores": {MA: a(1300, ("beijo", 0.3))}},
    {"linhas": 1, "cenario": JARDIM, "camera": corpo(1300), "fx": ["coracoes"], "callout": [call(0.3, "SAROU!", "verde")],
     "atores": {LA: a(950, ("dance", 0.3, "pulinho"), turn=0.35), MA: a(1650, ("bacana", 0.5), turn=-0.35)}},
]


# ───────── refrão: mamãe querida! te amo, mamãe! vem cá, um abraço, vem! ─────────
REF = {
    1: dict(te_amo=(SALA, LA), abraco=(CASA, LA, MA), danca=("danca_xadrez_amarelo", (LA, MA, LU)), vem=(JARDIM, MA)),
    2: dict(te_amo=(JARDIM, LU), abraco=(SALA, LU, MA), danca=("danca_bolinhas_verde", (LU, MA, LA)), vem=(COZ, MA)),
    3: dict(te_amo=(CASA, LA), abraco=(JARDIM, LA, MA), danca=("danca_raios_laranja", (MA, LA, LU)), vem=(SALA, MA)),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * max(1, linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        k = i % 4
        if k == 0:                                         # "Mamãe querida! / Te amo, mamãe!" — busto com coração
            cen, quem = cfg["te_amo"]
            out.append({"linhas": 2, "cenario": cen, "camera": busto(1300), "fx": ["coracoes"], "cantam": [quem],
                        "callout": [call(0.1, "MAMÃE QUERIDA!", "rosa"), call(round(dd * 0.5, 2), "TE AMO, MAMÃE!", "vermelho")],
                        "atores": {quem: a(1300, ("beijo", round(dd * 0.45, 2)))}})
        elif k == 1:                                       # "Vem cá, um abraço, vem!" — o abraço no corpo todo
            cen, p_, m_ = cfg["abraco"]
            out.append({"linhas": 2, "cenario": cen, "camera": corpo(1300), "fx": ["coracoes"], "cantam": [p_],
                        "callout": [call(round(dd * 0.45, 2), "VEM CÁ, UM ABRAÇO!", "laranja")],
                        "atores": {p_: a(1000, ("wave", 0.1), ("abraco", round(dd * 0.45, 2)), turn=0.35),
                                   m_: a(1600, ("abraco", round(dd * 0.5, 2)), turn=-0.35)}})
        elif k == 2:                                       # a família dança no fundo colorido
            cen, quem = cfg["danca"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "flash": n == 1, "cantam": [quem[1]],
                        "callout": [call(0.1, "MAMÃE QUERIDA!", "rosa")],
                        "atores": {c: g(x, ("dance", 0.05 * j, st), turn=tv) for j, (c, x, tv, st) in
                                   enumerate(zip(quem, (380, 960, 1540), (0.2, 0.0, -0.2), ("festa", "palmas", "festa")))}})
        else:                                              # a mamãe em CABEÇA chamando para o abraço
            cen, quem = cfg["vem"]
            out.append({"linhas": 2, "cenario": cen, "camera": cab(1300), "fx": ["coracoes"], "cantam": [LA],
                        "callout": [call(round(dd * 0.4, 2), "UM ABRAÇO!", "rosa")],
                        "atores": {quem: a(1300, ("abraco", round(dd * 0.35, 2)))}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 2}, {"seg": 6.0}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 2, "cenario": CASA, "camera": cab(1300), "cantam": [LU], "callout": [call(0.2, "BORA, TURMINHA!", "laranja")],
     "atores": {LU: a(1300, ("apontar_camera", 0.1), ("wave", 2.0))}},
    {**banda(max(0.6, d[1]), extra={MA: a(2300, ("dance", 0.0, "palmas"), turn=-0.3)}), "titulo": "a banda da família"},
    {"seg": max(0.6, d[2]), "cenario": "danca_ondas_amarelo", "camera": GCAM, "fx": ["confete"], "titulo": "a família dança",
     "cantam": [LA],
     "atores": {LA: g(380, ("dance", 0.0, "cintura"), turn=0.2), MA: g(960, ("dance", 0.1, "festa")),
                LU: g(1540, ("dance", 0.0, "bracos"), turn=-0.2)}},
]


# ───────── ponte: beijo, abraço, coração… e agora vem dançar! ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "fx": ["coracoes"], "callout": [call(0.1, "UM BEIJO NA BOCHECHA!", "rosa")],
     "atores": {LA: a(1300, ("beijo", 0.1))}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.1, "UM ABRAÇO APERTADO!", "laranja")],
     "atores": {LA: a(1050, ("abraco", 0.1), turn=0.35), MA: a(1550, ("abraco", 0.15), turn=-0.35)}},
    {"linhas": 1, "cenario": "danca_raios_rosa", "camera": GCAM, "fx": ["coracoes"], "callout": [call(0.1, "UM CORAÇÃO COM A MÃO!", "vermelho")],
     "atores": {LU: g(640, ("bacana", 0.1), turn=0.2), MA: g(1280, ("abraco", 0.2), turn=-0.2)}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "fx": ["coracoes"], "callout": [call(0.1, "PRA MAMÃE DO MEU LADO!", "rosa")],
     "atores": {LA: a(950, ("point", 0.1), turn=0.3), MA: a(1650, ("beijo", 0.3), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_xadrez_verde", "camera": GCAM, "fx": ["confete"], "callout": [call(0.1, "AGORA VEM DANÇAR!", "verde")],
     "atores": {LA: g(380, ("dance", 0.0, "festa"), turn=0.2), MA: g(960, ("dance", 0.05, "festa")),
                LU: g(1540, ("dance", 0.1, "festa"), turn=-0.2)}},
    {"linhas": 1, "cenario": JARDIM, "camera": corpo(1300), "callout": [call(0.1, "PULA PRA CÁ, PULA PRA LÁ!", "azul")],
     "atores": {LA: a(950, ("dance", 0.0, "pulinho"), turn=0.3), MA: a(1650, ("dance", 0.1, "pulinho"), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "camera": GCAM, "callout": [call(0.1, "GIRA, GIRA!", "laranja")],
     "atores": {LA: g(640, ("dance", 0.0, "roda"), turn=0.2), MA: g(1280, ("dance", 0.05, "roda"), turn=-0.2)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "fx": ["coracoes"], "callout": [call(0.1, "UM ABRAÇO PRA ACABAR!", "rosa")],
     "atores": {LA: a(1050, ("abraco", 0.1), turn=0.35), MA: a(1550, ("abraco", 0.1), turn=-0.35)}},
]


# ───────── 2º verso: a VIRADA — cadê os óculos da mamãe? ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 7 + [{"linhas": 2}])
d = dur(T)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.3, "MAS HOJE A MAMÃE…", "roxo")],
     "atores": {MA: a(1300, ("look_around", 0.2)) | {"keys": [{"t": 0.0, "pose": OC, "ease": "step"}]}}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "callout": [call(0.2, "QUE CONFUSÃO!", "laranja")],
     "atores": {MA: a(1300, ("pensar", 0.1), expr="confused") | {"keys": [{"t": 0.0, "pose": OC, "ease": "step"}]}}},
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "callout": [call(0.2, "CADÊ OS MEUS ÓCULOS?", "roxo")], "cantam": [MA],
     "atores": {MA: a(1300, ("look_around", 0.1), expr="confused") | {"keys": [{"t": 0.0, "pose": OC, "ease": "step"}]}}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.2, "NO CHÃO?", "verde")],
     "atores": {MA: a(1300, ("dance", 0.0, "agacha")) | {"keys": [{"t": 0.0, "pose": OC, "ease": "step"}]}}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.2, "NA BOLSA? NO SOFÁ?", "azul")],
     "atores": {MA: a(1000, ("look_around", 0.1), turn=0.3) | {"keys": [{"t": 0.0, "pose": OC, "ease": "step"}]},
                LU: a(1700, ("laugh", 0.6), turn=-0.3)}},
    {"linhas": 1, "cenario": COZ, "camera": busto(1300), "callout": [call(0.2, "NA GELADEIRA?!", "azul")],
     "atores": {MA: a(1300, ("look_around", 0.1), expr="surprised") | {"keys": [{"t": 0.0, "pose": OC, "ease": "step"}]}}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "tremor": [0.3], "callout": [call(0.2, "TAVA NA CABEÇA DELA!", "vermelho")],
     "atores": {LA: a(950, ("point", 0.1), ("laugh", 0.9), turn=0.35),
                MA: a(1650, turn=-0.3, expr="surprised") | {"keys": [{"t": 0.0, "pose": OC, "ease": "step"}]}}},
    {"linhas": 2, "cenario": SALA, "camera": corpo(1300), "fx": ["coracoes"],
     "callout": [call(0.2, "QUEM ACHOU? EUZINHA!", "rosa")],
     "atores": {LA: a(1050, ("bacana", 0.1), ("abraco", 1.3), turn=0.35),
                MA: a(1550, ("laugh", 0.2), ("abraco", 1.3), turn=-0.35) | {"keys": [{"t": 0.0, "pose": OC, "ease": "step"}]}}},
]


# ───────── intervalo 2 (só instrumental, ~14 s) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 2, 2)
R.partes["intervalo#2"] = [
    {**banda(d1, extra={MA: a(2300, ("dance", 0.0, "festa"), turn=-0.3)}), "titulo": "a banda"},
    {"seg": round(D2 - d1, 2), "cenario": "danca_ondas_verde", "camera": GCAM, "fx": ["confete"], "titulo": "a família dança",
     "atores": {MA: g(380, ("dance", 0.0, "palmas"), turn=0.2), LA: g(960, ("dance", 0.1, "pezinho")),
                LU: g(1540, ("dance", 0.0, "palmas"), turn=-0.2)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": CASA, "camera": cab(1300), "callout": [call(0.2, "GOSTOU DA MAMÃE?", "rosa")],
     "atores": {LA: a(1300, ("apontar_camera", 0.1))}},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LU: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0}}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {LA: a(950, ("point", 0.1), turn=0.3), MA: a(1650, ("wave", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LA: g(560, ("point", 0.2), turn=0.2) | {"depth": 1.0}}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.4, "cenario": CASA, "camera": corpo(1300), "fx": ["coracoes"],
     "callout": [call(0.2, "MAMÃE QUERIDA!", "rosa"), call(1.6, "TCHAU!", "amarelo")],
     "atores": {LA: a(700, ("wave", 0.0), turn=0.3), MA: a(1300, ("wave", 0.1)), LU: a(1900, ("wave", 0.2), turn=-0.3)}},
    {"seg": round(dfim - 3.4, 2), "cenario": JARDIM, "camera": cab(1300), "flash": True, "fx": ["coracoes"],
     "callout": [call(0.2, "TE AMO!", "vermelho")], "titulo": "o último beijo", "atores": {LA: a(1300, ("beijo", 0.2))}},
]

R.salvar("Roteiro de 29 'Mamãe Querida' (take '(3)' inteiro, 2:31, E16, nota 4,8): o superpoder da mamãe, refrão do abraço, "
         "ponte de carinhos e dança, e a VIRADA dos óculos na cabeça da mamãe (oculos_cabeca). 1º clipe da Laurinha no "
         "padrão novo (cabeça/busto/corpo, nitidez). Gerado por scripts/roteiros/ep29_mamae_querida.py.")
