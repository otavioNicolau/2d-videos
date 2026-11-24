"""Roteiro verso a verso de 32 "O Bigodão do Vovô Ciço!" (take 2 escolhido pelo usuário, 2:30, 136 BPM, Sol menor, estilo E17,
nota 4,9; letra 5 a 8 anos) → canais/laurinha/musicas/32_bigodao_do_vovo/roteiro.json.

O VOVÔ CIÇO (personagem novo `vovo_cico`, aprovado 23/11: o vovô do canal com BIGODÃO enrolado e sobrancelhas grossas —
cara de bravo, mas é um amor) tem CIÚMES do bigode: ninguém pode tocar ("no bigode, não, não, não!"). Refrão = a turma
tenta tocar, ele desvia… "Bravo? Que nada! Vem abraçar!" (abraço). Ponte = comandos (bigode com o dedo — o bigodinho
branco da Laurinha/Luisinho —, cara de zangado, esconde que o vovô tá do lado; de mansinho, na ponta do pé… "Ei! Nem
pensar, né!"). 2º verso = a VIRADA do amor: o Luisinho cai e chora, o vovô chega bravo, abre um sorrisão e deixa, SÓ
HOJE e em segredo, ele puxar o bigode — e sorri.
Casa do vovô = `plano_sala`; padrão da Laurinha: CABEÇA / BUSTO / CORPO.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep32_bigodao_do_vovo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import GCAM, LA, LU, Roteiro, busto, cab, call, corpo  # noqa: E402

R = Roteiro("laurinha/ep32-bigodao-do-vovo", "32_bigodao_do_vovo", "laurinha")
SALA, CASA, JARDIM, PARQUE = "plano_sala", "plano_casa_frente", "plano_jardim", "plano_parque"
VC, MA = "vovo_cico", "mamae"
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


def vovo(x, *acoes, bravo=True, turn=0.0, **kw):
    """o vovô Ciço: `bravo` = cara fechada (sobrancelhas em V); senão sorrindo (é um amor)."""
    kw.setdefault("expr", "angry" if bravo else "joy")
    return a(x, *acoes, turn=turn, **kw)


def bigodinho(at, liga=1.0, t_tira=None):
    """o bigode de brincadeira (dedo/leite) no rosto da criança; `t_tira` = instante em que esconde."""
    ks = [{"t": 0.0, "pose": {"bigode": liga}, "ease": "step"}]
    if t_tira is not None:
        ks.append({"t": round(t_tira, 2), "pose": {"bigode": 0.0}, "ease": "step"})
    at["keys"] = at.get("keys", []) + ks
    return at


def banda(d, extra=None):
    """a banda toca NA SALA do vovô: Laurinha no teclado, Luisinho na bateria, o vovô dança à direita."""
    p = R.banda(SALA, d, teclado=True, sax=LA, bateria=LU, cam={"x": 1350, "y": 600, "zoom": 1.0, "zoom_fim": 1.04},
                extra=extra or {VC: a(2300, ("dance", 0.0, "festa"), turn=-0.3, expr="joy")})
    p["cantam"] = [LA]
    return p


# ───────── intro (sem introdução instrumental: a voz entra no 0) ─────────
T = R.tempos("intro#1", [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"seg": 0.0}])
d = dur(T)
R.partes["intro#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "titulo": "o vovô Ciço do bigodão",
     "callout": [call(0.3, "VOVÔ CIÇO DO BIGODÃO!", "azul")], "atores": {VC: vovo(1300, ("look_around", 0.3))}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "callout": [call(0.2, "NINGUÉM PODE TOCAR!", "vermelho")],
     "atores": {VC: vovo(1300, ("point", 0.2), turn=0.1)}},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "camera": GCAM, "flash": True, "fx": ["estrelas"],
     "callout": [call(0.1, "LAURINHA E LUISINHO!", "roxo")],
     "atores": {LA: g(640, ("wave", 0.1), turn=0.25) | {"depth": 1.05}, LU: g(1280, ("wave", 0.2), turn=-0.25) | {"depth": 1.05}}},
    {**banda(max(0.6, d[3])), "titulo": "a banda na sala do vovô"},
]


# ───────── 1º verso: o bigodão, a cara de bravo… e ninguém pode tocar ─────────
T = R.tempos("verso#1", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.3, "O VOVÔ CIÇO!", "azul")],
     "atores": {LA: a(650, ("wave", 0.2), turn=0.3), VC: vovo(1300, ("wave", 0.3)), LU: a(1950, ("wave", 0.25), turn=-0.3)}},
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "callout": [call(0.3, "UM BIGODÃO ENROLADO!", "laranja")],
     "atores": {VC: vovo(1300, ("look_around", 0.2))}},
    {"linhas": 1, "cenario": "danca_xadrez_vermelho", "camera": GCAM, "callout": [call(0.2, "PARECE BRAVO…", "vermelho")],
     "atores": {VC: g(960, ("estatua", 0.0)) | {"depth": 1.3, "expr": "angry"}}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "fx": ["coracoes"], "callout": [call(0.2, "MAS É O VOVÔ MAIS AMADO!", "rosa")],
     "atores": {LA: a(950, ("abraco", 0.1), turn=0.3), VC: vovo(1650, ("abraco", 0.1), bravo=False, turn=-0.3)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.2, "NINGUÉM PODE TOCAR!", "vermelho")],
     "atores": {LU: a(800, ("point", 0.3), turn=0.35), VC: vovo(1550, ("look_around", 0.4), turn=-0.3)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.2, "NEM O GATO!", "laranja")],
     "objetos": {"gato": obj("gato", 900, CHAO, 1.1, d[5], z=4, fixo={"lado": 1.0}, pts={"aceno": [(0.3, 1.0)], "rabo": [(1.2, 2.0)]})},
     "atores": {VC: vovo(1650, ("point", 0.4), turn=-0.3)}},
    {"linhas": 1, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.2, "SE ALGUÉM CHEGA PERTO…", "roxo")],
     "atores": {LA: a(500, ("sneak", 0.0), turn=0.4) | {"acoes": [{"t": 0.0, "do": "sneak", "to_x": 1000.0, "dur": round(max(0.6, d[6]) - 0.1, 2)}]},
                VC: vovo(1700, ("estatua", 0.0), turn=-0.2)}},
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "callout": [call(0.1, "NÃO, NÃO, NÃO!", "vermelho")],
     "atores": {VC: vovo(1300, ("point", 0.0))}},
]


# ───────── refrão: bigodão do vovô! ninguém pode tocar! bravo? que nada! vem abraçar! ─────────
REF = {
    1: dict(tenta=(LA, LU), cen_abraco=SALA, abraca=LA, danca=("danca_xadrez_verde", (LA, VC, LU)), close=JARDIM),
    2: dict(tenta=(LU, MA), cen_abraco=CASA, abraca=LU, danca=("danca_bolinhas_laranja", (LU, VC, MA)), close=CASA),
    3: dict(tenta=(MA, LA), cen_abraco=SALA, abraca=MA, danca=("danca_raios_azul", (MA, VC, LA)), close=SALA),
}


def refrao(n):
    linhas = len(R.bloco(f"refrao#{n}")[1])
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * (linhas // 2))
    out = []
    cfg = REF[n]
    for i, (t0, t1, versos) in enumerate(T):
        dd = round(t1 - t0, 2)
        if i % 4 == 0:                                     # "Bigodão do vovô! Ninguém pode tocar!" — tentam tocar, ele desvia
            q1, q2 = cfg["tenta"]
            out.append({"linhas": 2, "cenario": SALA, "camera": corpo(1300), "cantam": [LA],
                        "callout": [call(0.1, "BIGODÃO DO VOVÔ!", "azul"), call(round(dd * 0.5, 2), "NINGUÉM PODE TOCAR!", "vermelho")],
                        "atores": {q1: a(600, ("point", 0.3), turn=0.35), VC: vovo(1300, ("look_around", 0.2), ("point", round(dd * 0.55, 2))),
                                   q2: a(2000, ("point", 0.5), turn=-0.35)}})
        elif i % 4 == 1:                                   # "Bravo? Que nada! Vem abraçar!" — o abraço de urso
            q = cfg["abraca"]
            out.append({"linhas": 2, "cenario": cfg["cen_abraco"], "camera": busto(1300), "cantam": [LA], "fx": ["coracoes"],
                        "callout": [call(0.2, "BRAVO?", "vermelho"), call(round(dd * 0.45, 2), "QUE NADA! VEM ABRAÇAR!", "rosa")],
                        "atores": {q: a(950, ("abraco", round(dd * 0.45, 2)), turn=0.3),
                                   VC: vovo(1650, ("abraco", round(dd * 0.45, 2)), bravo=False, turn=-0.3)}})
        elif i % 4 == 2:                                   # a dança do bigodão no fundo colorido
            cen, quem = cfg["danca"]
            out.append({"linhas": 2, "cenario": cen, "camera": GCAM, "fx": ["confete"], "flash": n == 1, "cantam": [LA],
                        "callout": [call(0.1, "BIGODÃO DO VOVÔ!", "azul")],
                        "atores": {c: g(x, ("dance", 0.05 * j, st), turn=tv) | ({"expr": "joy"} if c == VC else {})
                                   for j, (c, x, tv, st) in enumerate(zip(quem, (380, 960, 1540), (0.2, 0.0, -0.2), ("roda", "festa", "roda")))}})
        else:                                              # CABEÇA do vovô: bravo… e o sorrisão
            out.append({"linhas": 2, "cenario": cfg["close"], "camera": cab(1300), "cantam": [LA],
                        "callout": [call(round(dd * 0.5, 2), "VEM ABRAÇAR!", "rosa")],
                        "atores": {VC: vovo(1300, ("laugh", round(dd * 0.45, 2)), bravo=False,
                                            keys=[{"t": 0.0, "pose": {"brow_l": 0.9, "brow_r": 0.9, "brow_y": -0.4}, "ease": "step"},
                                                  {"t": round(dd * 0.4, 2), "pose": {"brow_l": 0.0, "brow_r": 0.0, "brow_y": 0.5}, "ease": "out"}])}})
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── bordão + intervalo 1 ─────────
T = R.tempos("intervalo#1", [{"linhas": 2}, {"seg": 5.0}, {"seg": 0.0}])
d = dur(T)
R.partes["intervalo#1"] = [
    {"linhas": 2, "cenario": CASA, "camera": cab(1300), "cantam": [LA], "callout": [call(0.2, "BORA, TURMINHA!", "laranja")],
     "atores": {LA: a(1300, ("apontar_camera", 0.1), ("wave", 2.0))}},
    {**banda(max(0.6, d[1])), "titulo": "a banda na sala do vovô"},
    {"seg": max(0.6, d[2]), "cenario": "danca_ondas_amarelo", "camera": GCAM, "fx": ["confete"], "titulo": "o vovô dança com os netos",
     "atores": {LA: g(380, ("dance", 0.0, "cintura"), turn=0.2), VC: g(960, ("dance", 0.1, "festa")) | {"expr": "joy"},
                LU: g(1540, ("dance", 0.0, "bracos"), turn=-0.2)}},
]


# ───────── ponte: comandos ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4 + [{"linhas": 2}] + [{"linhas": 1}] * 3)     # "E mais!" junto com "de mansinho"
d = dur(T)
R.partes["ponte#1"] = [
    {"linhas": 1, "cenario": "danca_raios_laranja", "camera": GCAM, "callout": [call(0.1, "FAZ BIGODE COM O DEDO!", "laranja")],
     "atores": {LU: bigodinho(g(960, ("point", 0.1)) | {"depth": 1.2})}},
    {"linhas": 1, "cenario": "danca_xadrez_amarelo", "camera": GCAM, "callout": [call(0.1, "FAZ CARA DE ZANGADO!", "vermelho")],
     "atores": {LA: bigodinho(g(960, ("estatua", 0.0)) | {"depth": 1.2, "expr": "angry"})}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "callout": [call(0.1, "AGORA ESCONDE O BIGODE…", "roxo")],
     "atores": {LU: bigodinho(a(950, ("look_around", 0.0), turn=0.3), t_tira=round(d[2] * 0.5, 2)),
                VC: vovo(1650, ("estatua", 0.0), turn=-0.3)}},
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "callout": [call(0.1, "O VOVÔ TÁ DO LADO!", "azul")],
     "atores": {VC: vovo(1300, ("look_around", 0.1))}},
    {"linhas": 2, "cenario": SALA, "camera": corpo(1300), "callout": [call(0.1, "E MAIS! CHEGA DE MANSINHO…", "verde")],
     "atores": {LA: a(400, turn=0.4) | {"acoes": [{"t": 0.3, "do": "sneak", "to_x": 1000.0, "dur": round(max(0.6, d[4]) - 0.5, 2)}]},
                VC: vovo(1750, ("estatua", 0.0), turn=-0.2, keys=[{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"}])}},
    {"linhas": 1, "cenario": "danca_bolinhas_rosa", "camera": GCAM, "callout": [call(0.1, "NA PONTA DO PÉ…", "rosa")],
     "atores": {LU: g(500, turn=0.4) | {"depth": 1.1, "acoes": [{"t": 0.0, "do": "sneak", "to_x": 1300.0, "dur": round(max(0.6, d[5]) - 0.1, 2)}]}}},
    {"linhas": 1, "cenario": SALA, "camera": busto(1300), "callout": [call(0.1, "VAI TOCAR NO BIGODE?", "laranja")],
     "atores": {LA: a(950, ("point", 0.2), turn=0.35), VC: vovo(1650, ("estatua", 0.0), turn=-0.3,
                                                                keys=[{"t": 0.0, "pose": {"lid": 1.0}, "ease": "step"},
                                                                      {"t": round(d[6] * 0.7, 2), "pose": {"lid": 0.0}, "ease": "out"}])}},
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "callout": [call(0.1, "EI! NEM PENSAR, NÉ!", "vermelho")],
     "atores": {VC: vovo(1300, ("point", 0.0))}},
]


# ───────── 2º verso: a VIRADA do amor — o Luisinho cai, e só hoje pode puxar ─────────
T = R.tempos("verso#2", [{"linhas": 1}] * 8)
d = dur(T)
R.partes["verso#2"] = [
    {"linhas": 1, "cenario": JARDIM, "camera": corpo(1300), "callout": [call(0.2, "O LUISINHO CAIU!", "laranja")],
     "atores": {LU: a(1300, ("sit", 0.3), expr="sad")}},
    {"linhas": 1, "cenario": JARDIM, "camera": cab(1300), "callout": [call(0.2, "CHOROU UM CHORÃO!", "azul")],
     "atores": {LU: a(1300, ("estatua", 0.0), expr="crying")}},
    {"linhas": 1, "cenario": JARDIM, "camera": corpo(1300), "callout": [call(0.2, "O VOVÔ CHEGOU BRAVO…", "vermelho")],
     "atores": {VC: vovo(2300, turn=-0.4) | {"acoes": [{"t": 0.0, "do": "walk", "to_x": 1600.0, "dur": round(max(0.6, d[2]) - 0.1, 2)}]},
                LU: a(900, ("estatua", 0.0), turn=0.3, expr="crying")}},
    {"linhas": 1, "cenario": JARDIM, "camera": cab(1300), "fx": ["coracoes"], "callout": [call(0.2, "E ABRIU UM SORRISÃO!", "rosa")],
     "atores": {VC: vovo(1300, ("laugh", 0.3), bravo=False)}},
    {"linhas": 1, "cenario": JARDIM, "camera": busto(1300), "callout": [call(0.2, "SÓ HOJE, PODE PEGAR!", "verde")],
     "atores": {LU: a(950, ("estatua", 0.0), turn=0.3, expr="surprised"), VC: vovo(1650, ("point", 0.2), bravo=False, turn=-0.3)}},
    {"linhas": 1, "cenario": JARDIM, "camera": cab(1300), "callout": [call(0.2, "MAS É SEGREDO, VIU?", "roxo")],
     "atores": {VC: vovo(1300, ("estatua", 0.0), turn=0.1, expr="sly")}},
    {"linhas": 1, "cenario": JARDIM, "camera": busto(1300), "callout": [call(0.2, "O LUISINHO PUXOU…", "laranja")],
     "atores": {LU: a(1000, ("point", 0.1), turn=0.35, expr="joy"), VC: vovo(1600, ("laugh", 0.5), bravo=False, turn=-0.3)}},
    {"linhas": 1, "cenario": JARDIM, "camera": busto(1300), "fx": ["coracoes"], "callout": [call(0.2, "E O VOVÔ SORRIU!", "rosa")],
     "atores": {LU: a(950, ("abraco", 0.1), turn=0.3), VC: vovo(1650, ("abraco", 0.1), bravo=False, turn=-0.3)}},
]


# ───────── intervalo 2 (só instrumental) ─────────
b2, _ = R.bloco("intervalo#2")
D2 = b2["e"] - b2["s"]
d1 = round(D2 / 2, 2)
R.partes["intervalo#2"] = [
    {**banda(d1), "titulo": "a banda na sala do vovô"},
    {"seg": round(D2 - d1, 2), "cenario": "danca_xadrez_laranja", "camera": GCAM, "fx": ["confete"], "titulo": "a turma dança",
     "atores": {MA: g(380, ("dance", 0.0, "palmas"), turn=0.2), VC: g(960, ("dance", 0.1, "roda")) | {"expr": "joy"},
                LU: g(1540, ("dance", 0.0, "palmas"), turn=-0.2)}},
]


# ───────── final: convite + tchau ─────────
T = R.tempos("final#1", [{"linhas": 1}] * 4)
d = dur(T)
R.partes["final#1"] = [
    {"linhas": 1, "cenario": SALA, "camera": cab(1300), "callout": [call(0.2, "E O SEU VOVÔ? TEM BIGODE?", "azul")],
     "atores": {LA: bigodinho(a(1300, ("apontar_camera", 0.1)))}},
    {"linhas": 1, "cenario": "danca_raios_verde", "camera": GCAM, "callout": [call(0.2, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}},
                                                                              {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {VC: g(640, ("bacana", 0.2), turn=0.2) | {"depth": 1.0, "expr": "joy"}}},
    {"linhas": 1, "cenario": CASA, "camera": busto(1300), "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {LU: a(950, ("point", 0.1), turn=0.3), MA: a(1650, ("wave", 0.2), turn=-0.3)}},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "camera": GCAM, "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LA: g(560, ("point", 0.2), turn=0.2) | {"depth": 1.0}}},
]
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.2, "cenario": SALA, "camera": corpo(1300), "fx": ["coracoes"],
     "callout": [call(0.2, "BIGODÃO DO VOVÔ!", "azul"), call(1.5, "TCHAU!", "amarelo")],
     "atores": {LA: a(650, ("wave", 0.0), turn=0.3), VC: vovo(1300, ("wave", 0.1), bravo=False), LU: a(1950, ("wave", 0.1), turn=-0.3)}},
    {"seg": round(dfim - 3.2, 2), "cenario": SALA, "camera": cab(1300), "flash": True, "callout": [call(0.2, "NEM PENSAR!", "vermelho")],
     "titulo": "o último 'nem pensar' do vovô", "atores": {VC: vovo(1300, ("point", 0.1))}},
]

R.salvar("Roteiro de 32 'O Bigodão do Vovô Ciço!' (take 2, 2:30, E17, nota 4,9, letra 5–8): o vovô Ciço (vovo_cico) de "
         "bigodão e cara de bravo que é um amor; ninguém pode tocar no bigode; refrão do 'vem abraçar'; ponte de comandos; "
         "a virada: o Luisinho cai e o vovô deixa, só hoje, puxar o bigode. Gerado por scripts/roteiros/ep32_bigodao_do_vovo.py.")
