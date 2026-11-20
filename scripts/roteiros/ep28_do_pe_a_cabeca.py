"""Roteiro verso a verso de 28 "Do Pé à Cabeça!" (take v1 sem a sobra do fim, 2:26, Laurinha, estilo E13, nota 4,9)
→ musicas/28_do_pe_a_cabeca/roteiro.json.

AULA DE DANÇA da turma: a dança SOBE PELO CORPO. A câmera anda do pé até a cabeça (câmera com `y_fim`, nova) e um anel
de estrelinhas (prop novo `destaque`) marca a parte da vez; a ação nova `tocar` põe as mãos no pé / joelho / barriga /
ombro / cabeça (com tapinhas no ritmo). "Do joelho pra barriga / da barriga pro ombrinho" = telas divididas com a
família (mamãe, vovó, vovô) e os amigos (joaninha, formiguinha) fazendo igual. Refrão: mexe tudo e MAIS RÁPIDO (treme,
roda). Ponte: mão no pé, no joelho, na barriga, na cabeça… e um BEIJO (ação nova `beijo`). A banda toca na escola
(nada de salão lilás). Final: a Laurinha cansada e rindo manda um beijo.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep28_do_pe_a_cabeca.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import LA, LU, Roteiro, call  # noqa: E402

R = Roteiro("ep28-do-pe-a-cabeca", "28_do_pe_a_cabeca", "laurinha")
ESCOLA, SALA, PARQUE, JARDIM, PRAIA, CASA = "plano_escola", "plano_sala", "plano_parque", "plano_jardim", "plano_praia", "plano_casa_frente"
QROSA, QAZUL, CAMPO, LAGOA, COZ, BANHO = "plano_quarto_rosa", "plano_quarto_azul", "plano_campo", "plano_lagoa", "plano_cozinha", "plano_banheiro"
PALCO = ESCOLA                    # 19/11: a banda toca na festa da escola (a aula de dança), nada de salão lilás
VO, VZ, MA, JO, FO = "vovo", "vovozinho", "mamae", "joaninha", "formiguinha"
PARTE_Y = {"pe": 905, "joelho": 860, "barriga": 780, "ombro": 700, "cabeca": 545}      # ator no chão (930), escala 1,45
NOME = {"pe": "PÉ!", "joelho": "JOELHO!", "barriga": "BARRIGA!", "ombro": "OMBRINHO!", "cabeca": "CABEÇA!"}
COR = {"pe": 0, "joelho": 1, "barriga": 2, "ombro": 3, "cabeca": 4}


def dur(T):
    return [round(t1 - t0, 2) for t0, t1, _ in T]


def obj(id_, x, y, depth, d, z=1, fixo=None, lin=None, pts=None):
    d = max(0.6, d)
    ks = [{"t": 0.0, "pose": dict(fixo or {}), "ease": "step"}]
    for c, (a, b) in (lin or {}).items():
        ks[0]["pose"][c] = float(a)
        ks.append({"t": round(d - 0.06, 2), "pose": {c: float(b)}, "ease": "linear"})
    for c, vs in (pts or {}).items():
        ks += [{"t": round(t, 2), "pose": {c: float(v)}, "ease": "out"} for t, v in vs]
    return {"id": id_, "x": x, "y": y, "z": z, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def marca(d, x, parte="pe", ate=None, depth=0.75):
    """o anel de estrelinhas na parte do corpo; com `ate` ele SOBE até essa outra parte durante o plano."""
    lin = {"giro": (0.0, d * 0.8)}
    if ate:
        lin["y"] = (PARTE_Y[parte], PARTE_Y[ate])
    pts = {"pulso": [(round(0.4 * j, 2), float(j % 2)) for j in range(1, int(d / 0.4))]}
    return obj("destaque", x, PARTE_Y[parte], depth, d, z=6, fixo={"cor": COR[ate or parte], "pulso": 0.0}, lin=lin, pts=pts)


def nuvem(d, x=500, y=430):
    return obj("nuvem", x, y, 0.35, d, z=0, lin={"x": (x, x + 260)})


def sol(d):
    return obj("sol", 2250, 200, 0.5, d, z=0, pts={"boca": [(0.6, 1.0)]}, lin={"giro": (0.0, 0.5)})


def gato(x, d, y=1010, depth=0.45, lado=1.0, miau=(0.8,)):
    ks = [{"t": 0.0, "pose": {"lado": lado, "rabo": 0.0, "miau": 0.0, "assusta": 0.0}, "ease": "step"}]
    ks += [{"t": round(0.4 * j, 2), "pose": {"rabo": float(j % 2)}, "ease": "inout"} for j in range(1, int(d / 0.4))]
    for t in miau:
        ks += [{"t": round(t, 2), "pose": {"miau": 1.0}, "ease": "out"}, {"t": round(t + 0.45, 2), "pose": {"miau": 0.0}, "ease": "in"}]
    return {"id": "gato", "x": x, "y": y, "z": 4, "depth": depth, "keys": sorted(ks, key=lambda k: k["t"])}


def toca(x, parte, turn=0.0, t=0.0, **kw):
    return {"x": x, "turn": turn, "acoes": [{"t": t, "do": "tocar", "parte": parte, "dur": "resto"}], **kw}


def danca(x, estilo, turn=0.0, t=0.1, **kw):
    return {"x": x, "turn": turn, "acoes": [{"t": t, "do": "dance", "style": estilo, "dur": "resto"}], **kw}


def sobe(x=1300, z0=1.9):
    """câmera que começa no pé e SOBE até a cabeça (28): zoom ~2 mostra só a parte da vez."""
    return {"x": x, "y": 820, "zoom": z0, "y_fim": 520, "zoom_fim": z0 + 0.05}


def pe_cam(x=1300):
    return {"x": x, "y": 820, "zoom": 2.0, "zoom_fim": 2.1}


def cabeca_cam(x=1300):
    return {"x": x, "y": 520, "zoom": 1.9, "zoom_fim": 2.0}


# ───────── intro ─────────
T = R.tempos("intro#1", [{"seg": 5.0}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1, "seg": 2.8}, {"seg": 3.6}, {"seg": 3.6}, {"seg": 0.0}])
d = dur(T)
R.partes["intro"] = [
    {"seg": 5.0, "cenario": ESCOLA, "camera": {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15}, "titulo": "a aula de dança",
     "callout": [call(1.0, "AULA DE DANÇA!", "rosa")], "objetos": {"s": sol(5.0), "n": nuvem(5.0, 400)},
     "atores": {LA: {"x": 800, "turn": 0.25, "acoes": [{"t": 0.2, "do": "espreguicar", "dur": 1.8}, {"t": 2.2, "do": "dance", "style": "pezinho", "dur": "resto"}]},
                LU: {"x": 2400, "turn": -0.3, "acoes": [{"t": 0.0, "do": "run", "to_x": 1800, "dur": 1.2}, {"t": 1.4, "do": "cheguei", "dur": "resto"}]}}},
    {"linhas": 1, "cenario": ESCOLA, "camera": sobe(), "callout": [call(0.2, "DO PÉ À CABEÇA!", "rosa")],
     "objetos": {"m": marca(d[1], 1300, "pe", ate="cabeca")},
     "atores": {LA: danca(1300, "pezinho", 0.1, t=0.0)}},
    {"linhas": 1, "cenario": ESCOLA, "camera": sobe(), "callout": [call(0.2, "DO PÉ À CABEÇA!", "azul")],
     "objetos": {"m": marca(d[2], 1300, "pe", ate="cabeca")},
     "atores": {LU: {"x": 1300, "turn": -0.1, "acoes": [{"t": 0.0, "do": "tocar", "partes": "pe,joelho,barriga,ombro,cabeca", "dur": "resto"}]}}},
    {"linhas": 1, "seg": 2.8, "cenario": PARQUE, "camera": {"x": 1300, "y": 560, "zoom": 1.1, "zoom_fim": 1.2},
     "callout": [call(0.2, "LAURINHA E LUISINHO!", "rosa")], "fx": ["confete"], "objetos": {"n": nuvem(2.8, 300)},
     "atores": {LA: {"x": 900, "turn": 0.25, "acoes": [{"t": 0.1, "do": "jump", "dur": 0.8}, {"t": 1.0, "do": "dance", "style": "chute", "dur": "resto"}]},
                LU: {"x": 1700, "turn": -0.25, "acoes": [{"t": 0.2, "do": "jump", "dur": 0.8}, {"t": 1.1, "do": "dance", "style": "sapinho", "dur": "resto"}]}}},
    {**R.banda(PALCO, 3.6, fx=["notas"]), "titulo": "a banda na festa da escola"},
    {"seg": 3.6, "cenario": SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "titulo": "a família se alonga",
     "objetos": {"c": gato(1300, 3.6, miau=(1.0, 2.6))},
     "atores": {VO: danca(450, "agacha", 0.3), VZ: danca(880, "bracos", 0.3, t=0.2), MA: danca(2150, "cintura", -0.3, t=0.15)}},
    {**R.banda(PALCO, max(0.6, d[6]), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.2, "zoom_fim": 1.1}),
     "titulo": "teclado e bateria"},
]
R.partes["intro"][4]["objetos"]["s"] = sol(3.6)
R.partes["intro"][6]["objetos"]["n"] = nuvem(max(0.6, d[6]), 2100)


# ───────── verso: o meu corpo tem um jeito… começa no pezinho e vai subindo devagar… começa de novo, rapidinho ─────────
def verso(key, n):
    T = R.tempos(key, [{"linhas": 1}] * 8)
    d = dur(T)
    eu = LA if n == 1 else LU
    a1, a2, b1, b2 = (LU, MA, VO, VZ) if n == 1 else (LA, JO, FO, MA)
    cen = {1: (SALA, ESCOLA, PARQUE), 2: (PRAIA, QAZUL, CAMPO)}[n]
    out = [
        # O meu corpo tem um jeito — dança na frente do espelho / na praia
        {"linhas": 1, "cenario": cen[0], "camera": {"x": 1300, "y": 560, "zoom": 1.1, "zoom_fim": 1.2},
         "callout": [call(0.4, "O MEU CORPO!", "rosa")],
         "objetos": {"e": obj("espelho", 2050, 640, 0.8, d[0], z=0, pts={"brilho": [(0.3, 1.0)]})} if n == 1 else
                    {"s": sol(d[0]), "si": obj("siri", 2050, 960, 0.5, d[0], z=3, lin={"anda": (0.0, d[0] * 2)}, pts={"aceno": [(0.4, 1.0)]})},
         "atores": {eu: danca(1100, "cintura", 0.2, t=0.0)}},
        # De dançar sem parar
        {"linhas": 1, "cenario": cen[0], "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["notas"],
         "callout": [call(0.3, "SEM PARAR!", "laranja")],
         "objetos": {"cx": obj("caixa_brinquedos", 2500, 930, 0.7, d[1], pts={"carrinho": [(0.4, 1.0)]})} if n == 1 else
                    {"n": nuvem(d[1], 400), "ca": obj("castelo_areia", 2350, 960, 0.5, d[1], fixo={"nivel": 1.0}, pts={"nivel": [(0.5, 3.0)]})},
         "atores": {eu: danca(700, "festa", 0.3, t=0.0), a1: danca(1800, "marcha", -0.3, t=0.0)}},
        # Começa lá no pezinho — close no pé
        {"linhas": 1, "cenario": cen[1], "camera": pe_cam(), "callout": [call(0.2, "PEZINHO!", "amarelo")],
         "objetos": {"m": marca(d[2], 1300, "pe")}, "atores": {eu: toca(1300, "pe", 0.1)}},
        # E vai subindo devagar! — a câmera sobe junto com as estrelinhas
        {"linhas": 1, "cenario": cen[1], "camera": sobe(1600), "callout": [call(0.3, "SUBINDO…", "verde")],
         "objetos": {"m": marca(d[3], 1600, "pe", ate="cabeca")},
         "atores": {eu: {"x": 1600, "turn": -0.1, "acoes": [{"t": 0.0, "do": "tocar", "partes": "joelho,barriga,ombro,cabeca", "dur": "resto"}]}}},
        # Do joelho pra barriga — tela dividida
        R.dividida({"cenario": cen[1], "camera": {"x": 1300, "y": 640, "zoom": 1.3, "zoom_fim": 1.4},
                    "objetos": {"m": marca(d[4], 1300, "joelho")}, "atores": {a1: toca(1300, "joelho", -0.1)}},
                   {"cenario": cen[0], "camera": {"x": 1300, "y": 600, "zoom": 1.3, "zoom_fim": 1.4},
                    "objetos": {"m": marca(d[4], 1300, "barriga")}, "atores": {a2: toca(1300, "barriga", 0.1, t=0.2)}},
                   linhas=1, layout="vertical" if n == 1 else "diagonal", callout=[call(0.2, "JOELHO… BARRIGA!", "azul")]),
        # Da barriga pro ombrinho — tela dividida
        R.dividida({"cenario": COZ if n == 1 else JARDIM, "camera": {"x": 1300, "y": 600, "zoom": 1.3, "zoom_fim": 1.4},
                    "objetos": {"m": marca(d[5], 1300, "barriga")}, "atores": {b1: toca(1300, "barriga", 0.1)}},
                   {"cenario": CAMPO if n == 1 else SALA, "camera": {"x": 1300, "y": 560, "zoom": 1.3, "zoom_fim": 1.4},
                    "objetos": {"m": marca(d[5], 1300, "ombro")}, "atores": {b2: toca(1300, "ombro", -0.1, t=0.2)}},
                   linhas=1, layout="diagonal" if n == 1 else "vertical", callout=[call(0.2, "OMBRINHO!", "verde")]),
        # E quando chega na cabeça — close na cabeça
        {"linhas": 1, "cenario": cen[1], "camera": cabeca_cam(), "callout": [call(0.2, "CABEÇA!", "roxo")],
         "objetos": {"m": marca(d[6], 1300, "cabeca")}, "atores": {eu: toca(1300, "cabeca", 0.0)}},
        # Começa de novo, rapidinho! — todo mundo roda
        {"linhas": 1, "cenario": cen[2], "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.12}, "tremor": [round(d[7] * 0.5, 2)],
         "callout": [call(0.3, "RAPIDINHO!", "vermelho")], "fx": ["estrelas"],
         "objetos": {"s": sol(d[7]), "n": nuvem(d[7], 350)}
                    | ({"p": obj("pipa", 2250, 520, 0.4, d[7], z=0, fixo={"rabiola": 1.0}, lin={"balanco": (0.0, d[7] * 1.2)})} if n == 1 else
                       {"pt": obj("pato", 1700, 980, 0.5, d[7], z=4, pts={"quem": [(0.4, 1.0), (0.9, 0.0)], "pulo": [(0.4, 1.0), (0.7, 0.0)]})}),
         "atores": {LA: danca(450, "roda", 0.3, t=0.0), LU: {"x": 2150, "turn": -0.3, "acoes": [{"t": 0.0, "do": "turn", "to": 0.3, "dur": 0.8},
                                                                                              {"t": 0.9, "do": "dance", "style": "treme", "dur": "resto"}]},
                    (VO if n == 1 else VZ): danca(1000, "pulinho", 0.3, t=0.2)}},
    ]
    return out


R.partes["verso#1"] = verso("verso#1", 1)
R.partes["verso#2"] = verso("verso#2", 2)


# ───────── refrão: do pé à cabeça! mexe tudo, ê! / do pé à cabeça! mais rápido, ê-ê! ─────────
CORES = ["rosa", "laranja", "roxo"]
CEN_REF = {1: (ESCOLA, QROSA, CASA), 2: (PRAIA, CAMPO, LAGOA), 3: (PARQUE, None, None)}


def refrao(n):
    T = R.tempos(f"refrao#{n}", [{"linhas": 2}] * 4)
    out = []
    for i, (t0, t1, _) in enumerate(T):
        d = round(t1 - t0, 2)
        if n == 3 and i in (1, 3):
            p = R.banda(PALCO, d, teclado=(i == 3), fx=["confete"], cam={"x": 1300, "y": 620, "zoom": 1.05, "zoom_fim": 1.12})
            p.pop("seg")
            p.update({"linhas": 2, "callout": [call(0.3, "MAIS RÁPIDO!", "vermelho")]})
            p["objetos"]["s"] = sol(d)
        elif i == 0:                                              # mexe tudo, ê! — a câmera sobe pela fila que dança
            cen = CEN_REF[n][0]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 700, "zoom": 1.1, "y_fim": 520, "zoom_fim": 1.05},
                 "fx": ["estrelas"], "callout": [call(0.2, "DO PÉ À CABEÇA!", CORES[n - 1]), call(round(d * 0.5, 2), "MEXE TUDO!", "amarelo")],
                 "objetos": {"s": sol(d), "nb": obj("bolha", 1300, 900, 0.3, d, z=0, lin={"balanco": (0.0, 2.0), "y": (900, 300)})}
                            | ({1: {"n": nuvem(d, 350)}, 2: {"ca": obj("castelo_areia", 1300, 960, 0.45, d, z=1, fixo={"nivel": 1.0}, pts={"nivel": [(0.8, 2.0), (1.6, 3.0)]})},
                                3: {"p": obj("pipa", 2250, 520, 0.4, d, z=0, fixo={"rabiola": 1.0}, lin={"balanco": (0.0, d * 1.2)})}}[n]),
                 "atores": {LA: danca(600, "festa", 0.3, t=0.0), LU: danca(2000, "bracos", -0.3, t=0.1)}}
            if n == 1:
                p["flash"] = True
        elif i == 1:                                              # mais rápido, ê-ê! — todo mundo treme
            cen = CEN_REF[n][1]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.05}, "tremor": [round(d * 0.55, 2)],
                 "callout": [call(round(d * 0.45, 2), "MAIS RÁPIDO!", "vermelho")],
                 "objetos": {"c": gato(1680, d, lado=-1.0, miau=(0.5, 1.8))}
                            | ({"cm": {"id": "cama", "x": 2400, "y": 900, "z": 0, "depth": 0.7}} if n == 1 else {"n": nuvem(d, 400), "s": sol(d)}),
                 "atores": {(MA if n == 1 else VO): danca(320, "treme", 0.3, t=0.0), (VO if n == 1 else VZ): danca(880, "treme", 0.3, t=0.15),
                            LA: danca(1860, "treme", -0.3, t=0.05), LU: danca(2280, "treme", -0.3, t=0.2)}}
        elif i == 2:                                              # tela dividida: a Laurinha × um amigo, o mesmo passo
            p = R.dividida({"cenario": SALA if n != 2 else PRAIA, "camera": {"x": 1300, "y": 560, "zoom": 1.2, "zoom_fim": 1.3},
                            "objetos": {"m": marca(d, 1300, "pe", ate="cabeca", depth=0.6)}, "atores": {LA: danca(1300, "twist", 0.1, t=0.0)}},
                           {"cenario": JARDIM if n != 2 else LAGOA, "camera": {"x": 1300, "y": 560, "zoom": 1.2, "zoom_fim": 1.3},
                            "objetos": {"s": sol(d)}, "atores": {({1: JO, 2: VZ, 3: FO}[n]): danca(1300, "twist", -0.1, t=0.0)}},
                           linhas=2, layout="diagonal" if n % 2 else "vertical", callout=[call(0.3, "MEXE TUDO!", CORES[n - 1])])
        else:                                                     # mais rápido! roda, roda
            cen = CEN_REF[n][2]
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["confete"],
                 "callout": [call(round(d * 0.45, 2), "MAIS RÁPIDO!", "vermelho")],
                 "objetos": {"n": nuvem(d, 350)} | ({"s": sol(d)} if n == 1 else
                                                     {"sp": obj("sapo", 1700, 990, 0.6, d, z=4, pts={"croac": [(0.5, 1.0), (1.0, 0.0)], "pulo": [(1.2, 1.0), (1.6, 0.0)]})}),
                 "atores": {LA: danca(450, "roda", 0.3, t=0.0), LU: danca(2150, "roda", -0.3, t=0.1),
                            (JO if n == 1 else FO): danca(1150, "pulinho", 0.2, t=0.2)}}
        out.append(p)
    return out


for n in (1, 2, 3):
    R.partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos (bordão + banda na escola) ─────────
def intervalo(key, n):
    b, bl = R.bloco(key)
    D = b["e"] - b["s"]
    if not bl:
        s1 = round(D / 2, 2)
        banda = {**R.banda(PALCO, s1, fx=["confete"], cam={"x": 1350, "y": 600, "zoom": 1.15, "zoom_fim": 1.05}), "titulo": "a banda (sax)"}
        banda["objetos"]["n"] = nuvem(s1, 2100)
        return [banda,
                {"seg": round(D - s1, 2), "cenario": QAZUL, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.1}, "titulo": "a família dança",
                 "objetos": {"c": gato(1300, D - s1, miau=(0.5, 2.0)), "cx": obj("caixa_brinquedos", 2500, 930, 0.7, D - s1, pts={"carrinho": [(0.6, 1.0)]})},
                 "atores": {VO: danca(450, "pulinho", 0.3), VZ: danca(2100, "gingado", -0.3, t=0.2)}}]
    p1 = round(bl[1]["s"] - b["s"] - 0.15, 2)
    p2 = 3.4
    out = [{"linhas": 1, "seg": p1, "cenario": ESCOLA if n == 1 else PRAIA, "camera": "close:laurinha", "callout": [call(0.2, "BORA, TURMINHA!", "rosa")],
            "objetos": {"s": sol(p1)},
            "atores": {LA: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
           {"linhas": 1, "seg": p2, "cenario": "danca_raios_rosa" if n == 1 else CASA,
            "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.1} if n == 1 else {"x": 1300, "y": 560, "zoom": 1.05, "zoom_fim": 1.15},
            "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")], "fx": ["confete"],
            "objetos": {"b": obj("bolha", 960, 900, 0.3, p2, z=0, lin={"balanco": (0.0, 2.0), "y": (900, 250)})} if n == 1 else {"n": nuvem(p2, 400)},
            "atores": {LA: ({"x": 420, "y": 1010, "depth": 1.0} if n == 1 else {"x": 600}) | {"turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "cintura" if n == 1 else "palmas", "dur": "resto"}]},
                       LU: ({"x": 1500, "y": 1010, "depth": 1.0} if n == 1 else {"x": 2000}) | {"turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "joelho" if n == 1 else "lado", "dur": "resto"}]}}}]
    resto = D - p1 - p2
    s3 = round(resto / 2, 2)
    out += [{**R.banda(PALCO, s3, fx=["notas"], cam={"x": 1350, "y": 600, "zoom": 1.1, "zoom_fim": 1.2}), "titulo": "a banda"},
            {**R.banda(PALCO, round(resto - s3, 2), teclado=True, fx=["notas"], cam={"x": 1250, "y": 620, "zoom": 1.25, "zoom_fim": 1.15}),
             "titulo": "teclado e bateria"}]
    out[2]["objetos"]["s"] = sol(s3)
    out[3]["objetos"]["n"] = nuvem(round(resto - s3, 2), 2100)
    if n == 2:                                                    # 2º intervalo: a família dança no lugar da 1ª banda
        out[2] = {"seg": s3, "cenario": JARDIM, "camera": {"x": 1300, "y": 540, "zoom": 1.05, "zoom_fim": 1.15}, "titulo": "a família dança",
                  "fx": ["notas"], "objetos": {"s": sol(s3), "c": gato(1300, s3, miau=(0.8,))},
                  "atores": {MA: danca(450, "twist", 0.3), VZ: danca(2150, "passinho", -0.3, t=0.2)}}
    return out


R.partes["intervalo#1"] = intervalo("intervalo#1", 1)
R.partes["intervalo#2"] = intervalo("intervalo#2", 2)
R.partes["intervalo#3"] = intervalo("intervalo#3", 3)

# ───────── ponte: mão no pé! mão no joelho! mão na barriga! mão na cabeça… e um beijo! ─────────
T = R.tempos("ponte#1", [{"linhas": 1}] * 4)
dp = dur(T)
PONTE = [("pe", COZ, "MÃO NO PÉ!", "amarelo"), ("joelho", BANHO, "MÃO NO JOELHO!", "rosa"), ("barriga", JARDIM, "MÃO NA BARRIGA!", "azul")]
R.partes["ponte#1"] = []
for i, (parte, cen, txt, cor) in enumerate(PONTE):
    R.partes["ponte#1"].append(
        {"linhas": 1, "cenario": cen, "camera": {"x": 1300, "y": 680, "zoom": 1.25, "zoom_fim": 1.32}, "callout": [call(0.1, txt, cor)],
         "objetos": {"m1": marca(dp[i], 700, parte, depth=0.6), "m2": marca(dp[i], 1900, parte, depth=0.6),
                     "n": obj("numero", 1300, 330, 0.8, dp[i], z=5, fixo={"n": i + 1, "pop": 0.0}, pts={"pop": [(0.3, 1.0)]})},
         "atores": {LA: toca(700, parte, 0.2), LU: toca(1900, parte, -0.2, t=0.1)}})
R.partes["ponte#1"].append(
    {"linhas": 1, "cenario": "danca_bolinhas_rosa", "camera": {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(0.1, "MÃO NA CABEÇA…", "roxo"), call(round(dp[3] * 0.5, 2), "E UM BEIJO!", "vermelho")],
     "objetos": {"n": obj("numero", 960, 330, 0.8, dp[3], z=5, fixo={"n": 4, "pop": 0.0}, pts={"pop": [(0.3, 1.0)]})},
     "atores": {LA: {"x": 450, "y": 1010, "depth": 1.0, "turn": 0.2,
                     "acoes": [{"t": 0.0, "do": "tocar", "parte": "cabeca", "dur": round(dp[3] * 0.45, 2)}, {"t": round(dp[3] * 0.5, 2), "do": "beijo", "dur": "resto"}]},
                LU: {"x": 1470, "y": 1010, "depth": 1.0, "turn": -0.2,
                     "acoes": [{"t": 0.1, "do": "tocar", "parte": "cabeca", "dur": round(dp[3] * 0.45, 2)}, {"t": round(dp[3] * 0.55, 2), "do": "beijo", "dur": "resto"}]}}})

# ───────── final: convite + tchau + a Laurinha cansada e rindo manda um beijo ─────────
R.partes["final#1"] = R.convite(ESCOLA, gostou="GOSTOU DA DANÇA?", extra_casa={"n": nuvem(3.0, 400)})
for p_ in R.partes["final#1"]:
    if not p_.get("camera"):
        p_["camera"] = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    elif isinstance(p_["camera"], dict) and "zoom_fim" not in p_["camera"]:
        p_["camera"]["zoom_fim"] = p_["camera"]["zoom"] + 0.08
R.partes["final#1"][0]["objetos"] = {"s": sol(2.0)}
R.partes["final#1"][2]["atores"]["mamae"]["x"] = 800
R.partes["final#1"][2]["atores"][LA]["x"] = 1800
(f0, f1, _), = R.tempos("final#2", [{"linhas": 1}])
dfim = round(f1 - f0, 2)
R.partes["final#2"] = [
    {"linhas": 1, "seg": 3.0, "cenario": ESCOLA, "camera": {"x": 1300, "y": 540, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(0.2, "DO PÉ À CABEÇA!", "rosa"), call(1.4, "TCHAU!", "amarelo")],
     "objetos": {"s": sol(3.0), "c": gato(1680, 3.0, lado=-1.0, miau=(1.2,))},
     "atores": {VO: {"x": 320, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LA: {"x": 880, "turn": 0.3, "acoes": [{"t": 0.0, "do": "wave", "dur": "resto"}]},
                LU: {"x": 2250, "turn": -0.3, "acoes": [{"t": 0.0, "do": "jump", "dur": 0.8}, {"t": 0.9, "do": "wave", "dur": "resto"}]}}},
    {"seg": 3.0, "cenario": ESCOLA, "camera": {"x": 1300, "y": 560, "zoom": 1.15, "zoom_fim": 1.25}, "titulo": "cansada e rindo",
     "objetos": {"n": nuvem(3.0, 350)},
     "atores": {LA: {"x": 1300, "turn": 0.1, "acoes": [{"t": 0.0, "do": "ofegante", "dur": 1.6}, {"t": 1.7, "do": "laugh", "dur": "resto"}]}}},
    {"seg": round(dfim - 6.0, 2), "cenario": ESCOLA, "camera": "close:laurinha", "fx": ["coracoes"], "callout": [call(0.2, "UM BEIJO!", "vermelho")],
     "titulo": "o beijo de tchau", "objetos": {"s": sol(round(dfim - 6.0, 2))},
     "atores": {LA: {"x": 1300, "acoes": [{"t": 0.1, "do": "beijo", "dur": "resto"}]}}},
]

R.salvar("Roteiro de 'Do Pé à Cabeça!' (take v1 sem a sobra do fim, 2:26, Laurinha, estilo E13, nota 4,9): aula de dança; a "
         "dança sobe pelo corpo (câmera do pé à cabeça, anel de estrelinhas na parte da vez, ação 'tocar'); joelho/barriga/"
         "ombrinho em telas divididas com a família e os amigos; refrão mexe tudo / mais rápido; ponte mão no pé… e um beijo; "
         "banda na escola. Gerado por scripts/roteiros/ep28_do_pe_a_cabeca.py.")
