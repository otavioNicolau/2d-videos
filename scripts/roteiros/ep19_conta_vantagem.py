"""Roteiro verso a verso de 19 "Conta Vantagem!" (take v2, 2:46, uma voz: Luisinho v2, estilo E7) → musicas/19_conta_vantagem/roteiro.json.

A Dona Barata (óculos escuros, colar de pérolas) se gaba no JARDIM; o castelo e o carro aparecem dourados no SONHO (campo);
o CHINELO surge na COZINHA e ela corre primeiro. Na ponte a verdade: castelo → caixinha, carro → carretel (rufar + revelação),
a força é fraquinha e a coragem "foi pro céu" (CÉU). Refrão: formiguinha e joaninha riem ("Ha, ha, Baratinha!");
no fim todo mundo dança no SALÃO e a barata, envergonhada, acaba dançando junto; tchau de trás da caixinha.
Primeiro roteiro feito com o placar de CENA (≥45 planos, ≥4 lugares, efeitos sonoros) e a animação A2.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/ep19_conta_vantagem.py
"""
from __future__ import annotations

import json
from pathlib import Path

from toonstudio.composition.clip_draft import _q, _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "projects" / "ep19-conta-vantagem"
MUS = ROOT / "musicas" / "19_conta_vantagem"
song = json.loads((PROJ / "analise" / "song.json").read_text(encoding="utf-8"))
letra = json.loads((PROJ / "analise" / "letra.json").read_text(encoding="utf-8"))
BEATS = song["beats"]
LINES = letra["lines"]
JARDIM, SONHO, COZINHA, SALAO, CEU, CASA = "plano_jardim", "plano_campo", "plano_cozinha", "plano_salao", "plano_ceu", "plano_casa_frente"
LA, LU, FO, JO = "laurinha", "luisinho", "formiguinha", "joaninha"
CAM = {"x": 1300, "y": 600, "zoom": 1.15, "zoom_fim": 1.22}


def bloco_info():
    out, occ = {}, {}
    for b in blocos(song):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        out[f"{b['tipo']}#{occ[b['tipo']]}"] = (b, [l for l in LINES if b["s"] - 0.05 <= l["s"] < b["e"] - 0.05])
    return out


INFO = bloco_info()


def planos_tempo(key, planos):
    """Início/fim/versos de cada plano — a mesma conta de clip_draft.roteiro_bloco (inclui planos com `seg`)."""
    b, bl = INFO[key]
    res, li, t = [], 0, b["s"]
    for k, p in enumerate(planos):
        n = int(p.get("linhas", 1 if "seg" not in p else 0))
        st = b["s"] if k == 0 else (_snap(bl[li]["s"] - 0.12, BEATS) if n > 0 and li < len(bl) else t)
        mine = bl[li:li + n] if n > 0 else []
        li += n
        res.append([st, None, mine])
        t = st + float(p["seg"]) if "seg" in p else (mine[-1]["e"] if mine else st + 2.0)
    for k in range(len(res)):
        res[k][1] = res[k + 1][0] if k + 1 < len(res) else b["e"]
    return [(_q(a), _q(e), m) for a, e, m in res]


def tp(t0, versos, *alvos, default=0.4, fim=False):
    """Tempo (relativo ao plano) do começo — ou do FIM, para encaixar efeito sonoro sem cobrir a voz — da palavra."""
    alvos = tuple(a.lower() for a in alvos)
    for l in versos:
        for w in l["words"]:
            if w["w"].lower().strip("!?,.…:()\"'") in alvos:
                return round(max(0.0, (w["e"] if fim else w["s"]) - t0), 2)
    return default


def fim_verso(t0, versos, i=-1):
    """Fim do verso i do plano (relativo): o respiro onde entra o efeito sonoro."""
    return round(max(0.05, versos[i]["e"] - t0 + 0.05), 2) if versos else 0.3


def call(t, text, color):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color}


def som(t, sid, vol=-3.0):
    return {"t": round(max(0.0, t), 2), "id": sid, "vol": vol}


def barata(x=1300, y=930, depth=0.85, z=3, pose=None, keys=None):
    if not keys:
        keys = [{"t": round(j * 0.35, 2), "pose": {"pulo": 0.06 * (j % 2)}, "ease": "inout"} for j in range(24)]
    return {"id": "barata", "x": x, "y": y, "z": z, "depth": depth, "pose": {"oculos": 1.0, **(pose or {})}, "keys": keys or []}


def corre(t0, t1, x0, x1, ks=None):
    """Barata corre de x0 a x1 (perninhas a mil, corpo inclinado, olhando para onde vai)."""
    lado = 1.0 if x1 > x0 else -1.0
    return (ks or []) + [{"t": round(t0, 2), "pose": {"x": x0, "correndo": 0.0, "susto": 1.0, "lado": lado}, "ease": "step"},
                         {"t": round(t0 + 0.12, 2), "pose": {"correndo": 1.0}},
                         {"t": round(t1, 2), "pose": {"x": x1, "corre": round((t1 - t0) * 3.2, 2)}, "ease": "linear"}]


def metida(t_fala, t_aponta=None):
    ks = [{"t": 0.0, "pose": {"metida": 1.0, "aponta": 0.0, "fala": 0.0}, "ease": "step"}]
    for i in range(3):
        ks += [{"t": round(t_fala + 0.4 * i, 2), "pose": {"fala": 0.8}}, {"t": round(t_fala + 0.4 * i + 0.2, 2), "pose": {"fala": 0.0}}]
    if t_aponta is not None:
        ks += [{"t": max(0.1, t_aponta - 0.05), "pose": {"aponta": 0.0}}, {"t": t_aponta + 0.3, "pose": {"aponta": 1.0}, "ease": "out"}]
    return ks


def castelo(x=1400, real_em=None, depth=0.7):
    ks = [{"t": 0.0, "pose": {"real": 0.0, "brilho": 1.0}, "ease": "step"}]
    if real_em is not None:
        ks += [{"t": real_em, "pose": {"real": 1.0, "brilho": 0.0}, "ease": "step"}]
    return {"id": "castelo_caixa", "x": x, "y": 930, "z": 1, "depth": depth, "keys": ks}


def carro(x=1450, real_em=None, anda=None, depth=0.75):
    ks = [{"t": 0.0, "pose": {"real": 0.0, "anda": 0.0}, "ease": "step"}]
    if anda:
        ks += [{"t": anda[0], "pose": {"anda": 0.0}, "ease": "step"}, {"t": anda[1], "pose": {"anda": 4.0}, "ease": "linear"}]
    if real_em is not None:
        ks += [{"t": real_em, "pose": {"real": 1.0}, "ease": "step"}]
    return {"id": "carro_carretel", "x": x, "y": 935, "z": 2, "depth": depth, "keys": ks}


def chinelo_pula(x, t, depth=0.8):
    """O chinelo (piada que volta): dá um pulinho/giro no 'Baratinha!' e a barata se assusta."""
    return {"id": "chinelo", "x": x, "y": 930, "z": 2, "depth": depth,
            "keys": [{"t": 0.0, "pose": {"gira": 0.0, "bate": 0.0}}, {"t": max(0.1, t - 0.05), "pose": {"gira": 0.0}},
                     {"t": t + 0.25, "pose": {"gira": 0.12, "bate": 1.0}, "ease": "out"}, {"t": t + 0.6, "pose": {"gira": 0.0, "bate": 0.0}}]}


def chinelo_voa(t0, t1, x0, x1):
    return {"id": "chinelo", "x": x0, "y": 760, "z": 4, "depth": 0.7,
            "keys": [{"t": round(t0, 2), "pose": {"x": x0, "gira": 0.0}, "ease": "step"},
                     {"t": round(t1, 2), "pose": {"x": x1, "gira": 3.0}, "ease": "linear"}]}


def carretel_rola(d, x0=-300, x1=2900):
    return {"id": "carro_carretel", "x": x0, "y": 960, "z": 1, "depth": 0.55, "pose": {"real": 1.0},
            "keys": [{"t": 0.0, "pose": {"x": x0, "anda": 0.0}, "ease": "step"}, {"t": round(d, 2), "pose": {"x": x1, "anda": 6.0}, "ease": "linear"}]}


def barata_danca(x, d, y=1010, depth=1.0):
    return barata(x, y=y, depth=depth, pose={"oculos": 1.0},
                  keys=[{"t": round(j * 0.35, 2), "pose": {"pulo": 0.35 * (j % 2), "aponta": float((j // 2) % 2)}, "ease": "inout"} for j in range(int(d / 0.35) + 1)])


partes: dict = {}

# ───────── intro: a barata desfila no jardim; a turma chega ─────────
P = [{"seg": 2.0}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}]
(a0, a1, _), (b0, b1, vb), (c0, c1, vc), (d0, d1, _) = planos_tempo("intro#1", P)
partes["intro"] = [
    {"seg": 2.0, "cenario": JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08},
     "objetos": {"b": barata(2700, keys=[{"t": 0.0, "pose": {"x": 2700, "metida": 1.0}, "ease": "step"},
                                         {"t": round(a1 - a0 - 0.1, 2), "pose": {"x": 1700}, "ease": "out", "in": round(a1 - a0 - 0.2, 2)}])},
     "sons": [som(0.2, "plim", -6)]},
    {"linhas": 1, "cenario": JARDIM, "camera": {"x": 1600, "y": 640, "zoom": 1.45, "zoom_fim": 1.55},
     "callout": [call(0.4, "CONTA VANTAGEM!", "laranja")],
     "objetos": {"b": barata(1650, depth=1.0, keys=metida(0.1, tp(b0, vb, "vantagem", default=0.6)))},
     "sons": [som(0.02, "pop", -5)]},
    {"linhas": 1, "cenario": JARDIM, "camera": CAM,
     "objetos": {"b": barata(1750, pose={"metida": 1.0})},
     "atores": {LA: {"x": -250, "y": 520, "turn": 0.4, "acoes": [{"t": 0.0, "do": "fly", "dur": 1.0, "to_x": 650, "to_y": 930},
                                                                {"t": 1.1, "do": "laugh", "dur": "resto"}]},
                LU: {"x": -300, "y": 420, "turn": 0.4, "acoes": [{"t": 0.15, "do": "fly", "dur": 1.0, "to_x": 1050, "to_y": 930},
                                                                {"t": 1.2, "do": "point", "dur": "resto"}]}},
     "sons": [som(0.1, "whoosh", -8)]},
    {"linhas": 1, "cenario": "danca_raios_amarelo", "fx": ["confete"], "callout": [call(0.15, "LAURINHA E LUISINHO!", "rosa")],
     "objetos": {"b": barata_danca(1700, 5.4, depth=0.75)},
     "atores": {LA: {"x": 560, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                LU: {"x": 1360, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": "resto"}]}},
     "sons": [som(fim_verso(d0, [l for l in LINES if d0 <= l["s"] < d1]), "palminhas", -6)]},
]


# ───────── verso: vantagem (jardim) → sonho dourado (campo) → força → chinelo (cozinha) → correu ─────────
def verso(key, n):
    P = [{"linhas": 2}, {"linhas": 2}, {"linhas": 2}, {"linhas": 1}, {"linhas": 1}]
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd), (e0, e1, ve) = planos_tempo(key, P)
    tcast, tcar = tp(b0, vb, "castelo", default=0.3), tp(b0, vb, "carro", default=1.4)
    plateia = ({FO: {"x": 560, "turn": 0.4, "acoes": [{"t": 0.3, "do": "pensar", "dur": "resto"}]},
                JO: {"x": 860, "turn": 0.4, "acoes": [{"t": 0.6, "do": "look_around", "dur": "resto"}]}} if n == 2 else
               {LU: {"x": 650, "turn": 0.4, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}})
    return [
        {"linhas": 2, "cenario": JARDIM, "camera": {"x": 1350, "y": 600, "zoom": 1.2, "zoom_fim": 1.3} if n == 1 else
            {"x": 1200, "y": 600, "zoom": 1.25, "zoom_fim": 1.15},
         "objetos": {"b": barata(1650 if n == 1 else 1400, keys=metida(0.2, 1.3))}, "atores": plateia,
         "sons": [som(fim_verso(a0, va, 0), "pop", -6)]},
        # o sonho: tudo dourado, a barata posando de estrela
        {"linhas": 2, "cenario": SONHO, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.12}, "fx": ["estrelas"],
         "callout": [call(tcast + 0.3, "UM CASTELO!", "amarelo"), call(tcar + 0.3, "UM CARRÃO!", "vermelho")],
         "objetos": {"cast": castelo(1500 if n == 1 else 900, depth=0.62), "car": carro(900 if n == 1 else 1650, depth=0.7,
                     anda=(tcar, b1 - b0) if n == 2 else None),
                     "b": barata(1250, depth=0.8, keys=metida(0.1, tcast))},
         "sons": [som(max(0.05, tcast - 0.25), "plim", -5), som(fim_verso(b0, vb), "ding", -6)]},
        {"linhas": 2, "cenario": JARDIM, "camera": {"x": 1300, "y": 640, "zoom": 1.35, "zoom_fim": 1.45},
         "callout": [call(tp(c0, vc, "forte", default=0.5) + 0.2, "A MAIS FORTE!", "laranja")],
         "objetos": {"b": barata(1300, depth=0.95, keys=metida(0.1) + [{"t": 0.6, "pose": {"pulo": 0.0}},
                                                                     {"t": 1.1, "pose": {"pulo": 1.0}, "ease": "linear"}])},
         "atores": {LA: {"x": 2000, "turn": -0.4, "expr": "surprised", "acoes": [{"t": 0.4, "do": "shock_reaction", "dur": "resto"}]}},
         "sons": [som(1.05, "boing", -6)]},
        # o chinelo: corte para a cozinha, zoom no chinelo, tambor de suspense
        {"linhas": 1, "cenario": COZINHA, "camera": {"x": 1300, "y": 760, "zoom": 1.6 if n == 1 else 1.4, "zoom_fim": 1.9 if n == 1 else 1.7},
         "flash": True, "callout": [call(0.3, "O CHINELO!", "azul")],
         "objetos": {"ch": {"id": "chinelo", "x": 1300, "y": 940, "z": 3, "depth": 1.2,
                            "keys": [{"t": 0.0, "pose": {"gira": 0.0}}, {"t": 0.5, "pose": {"gira": 0.04 if n == 1 else 1.0}, "ease": "out"}]}},
         "sons": [som(0.05, "thud", -4)]},
        {"linhas": 1, "cenario": JARDIM, "camera": CAM if n == 1 else {"x": 1500, "y": 600, "zoom": 1.1, "zoom_fim": 1.0},
         "callout": [call(0.6, "CORREU!", "vermelho")],
         "objetos": {"b": barata(1400, keys=corre(0.2, e1 - e0 - 0.1, 1400, -400 if n == 1 else 3000)),
                     "ch": chinelo_voa(0.6, e1 - e0 - 0.1, 2900 if n == 1 else -300, -300 if n == 1 else 2900)},
         "atores": ({LU: {"x": 2000, "turn": -0.4, "acoes": [{"t": 0.3, "do": "laugh", "dur": 1.6}, {"t": 2.0, "do": "slip"}]}} if n == 1 else
                    {FO: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.3, "do": "laugh", "dur": "resto"}]},
                     JO: {"x": 1000, "turn": 0.3, "acoes": [{"t": 0.5, "do": "jump", "dur": 0.8}, {"t": 1.4, "do": "laugh", "dur": "resto"}]}}),
         "sons": [som(0.15, "zip", -5), som(0.6, "whoosh", -7)]},
    ]


partes["verso#1"] = verso("verso#1", 1)
partes["verso#2"] = verso("verso#2", 2)

CORES = ["laranja", "verde", "azul", "rosa"]


# ───────── refrão: "Ih, é mentirinha!" (cara de quem sabe) e "Ha, ha, Baratinha!" (a turma ri, ela se envergonha) ─────────
def refrao(n):
    P = [{"linhas": 2}, {"linhas": 2}, {"linhas": 2}, {"linhas": 2}]
    T = planos_tempo(f"refrao#{n}", P)
    out = []
    cen = [JARDIM, JARDIM, SALAO, SALAO][n - 1]
    for i, (t0, t1, v) in enumerate(T):
        ri = i % 2 == 1
        tw = tp(t0, v, "baratinha" if ri else "mentirinha", default=1.4)
        if not ri:                                                # "Ih, é mentirinha!": Luisinho cochicha pra câmera, a barata posa
            p = {"linhas": 2, "cenario": cen, "camera": ("close:luisinho" if i == 0 and n in (1, 3) else
                                                         {"x": 1200 + 150 * n, "y": 620, "zoom": 1.3, "zoom_fim": 1.38}),
                 "callout": [call(tw + 0.1, "MENTIRINHA!", "verde")],
                 "atores": {LU: {"x": 1000 if i == 0 else 900, "turn": 0.0 if i == 0 else 0.3,
                                 "acoes": [{"t": 0.1, "do": "apontar_camera" if i == 0 else "sorriso", "dur": round(max(0.5, tw), 2)},
                                           {"t": round(tw + 0.1, 2), "do": "laugh" if n > 2 else "bacana", "dur": "resto"}]}},
                 "sons": [som(fim_verso(t0, v, 0), "pop", -6)]}
            if i != 0 or n not in (1, 3):
                p["objetos"] = {"b": barata(1700, depth=0.9, keys=metida(0.1, 0.5))}
            if i == 0:
                p["callout"].insert(0, call(0.1, "CONTA VANTAGEM!", CORES[n - 1]))
                p["flash"] = True
        else:                                                     # "Ha, ha, Baratinha!": a turma ri, ela se envergonha
            festa = n >= 3
            p = {"linhas": 2, "cenario": cen, "camera": {"x": 1300, "y": 600, "zoom": 1.05 if festa else 1.15, "zoom_fim": 1.12 if festa else 1.25},
                 "callout": [call(tw + 0.1, "HA, HA!", "amarelo")], "fx": ["confete"] if festa else [],
                 "objetos": {"b": barata(1300, depth=0.85, keys=[{"t": 0.0, "pose": {"metida": 1.0, "vergonha": 0.0}, "ease": "step"},
                                                               {"t": max(0.1, tw - 0.1), "pose": {"metida": 1.0}},
                                                               {"t": tw + 0.3, "pose": {"metida": 0.0, "vergonha": 1.0, "oculos": 0.0}, "ease": "step"}])},
                 "atores": {FO: {"x": 600 if i == 1 else 2000, "turn": 0.35 if i == 1 else -0.35,
                                 "acoes": [{"t": round(max(0.1, tw - 0.2), 2), "do": "laugh", "dur": "resto"}]},
                            JO: {"x": 2050 if i == 1 else 650, "turn": -0.35 if i == 1 else 0.35,
                                 "acoes": [{"t": round(max(0.1, tw), 2), "do": "laugh", "dur": "resto"}]},
                            LA: {"x": 900 if i == 1 else 1700, "turn": 0.3 if i == 1 else -0.3,
                                 "acoes": [{"t": 0.1, "do": "dance", "style": ["palmas", "pezinho", "gingado", "bracos"][n - 1], "dur": round(max(0.5, tw), 2)},
                                           {"t": round(tw + 0.1, 2), "do": "laugh", "dur": "resto"}]}},
                 "sons": [som(fim_verso(t0, v, 0), "palminhas" if festa else "whistle_down", -6)]}
            p["objetos"]["gag"] = carretel_rola(t1 - t0) if festa else chinelo_pula(1750, round(tw, 2))
            if festa and i == 3:                                   # refrão final: a barata entra na festa e dança junto
                p["objetos"]["b"]["keys"] += [{"t": round(t1 - t0 - 1.0, 2), "pose": {"vergonha": 0.0, "pulo": 0.0}, "ease": "step"},
                                              {"t": round(t1 - t0 - 0.5, 2), "pose": {"pulo": 1.0}, "ease": "linear"}]
        out.append(p)
    return out


for n in (1, 2, 3, 4):
    partes[f"refrao#{n}"] = refrao(n)


# ───────── intervalos: bordão, dança no salão; a barata envergonhada atrás da caixinha e a Laurinha chama ─────────
def intervalo(key, n):
    b, bl = INFO[key]
    if not bl:                                                    # intervalo 3 (instrumental): festa no salão
        d = b["e"] - b["s"]
        return [{"seg": round(d / 3, 2), "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": 1.0, "zoom_fim": 1.1}, "fx": ["confete"],
                 "titulo": "festa",
                 "objetos": {"b": barata(1300, pose={"oculos": 0.0}, keys=[{"t": j * 0.55, "pose": {"pulo": float(j % 2)}, "ease": "linear"}
                                                                          for j in range(int(d / 3 / 0.55))])},
                 "atores": {LA: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                            LU: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "balanco", "dur": "resto"}]}},
                 "sons": [som(0.1, "palminhas", -7)]},
                {"seg": round(d / 3, 2), "cenario": SALAO, "camera": {"x": 1000, "y": 640, "zoom": 1.35, "zoom_fim": 1.25},
                 "atores": {FO: {"x": 800, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "lado", "dur": "resto"}]},
                            JO: {"x": 1250, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "marcha", "dur": "resto"}]}},
                 "sons": [som(0.2, "boing", -8)]},
                {"seg": round(d - 2 * round(d / 3, 2), 2), "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": 1.15, "zoom_fim": 1.0},
                 "objetos": {"b": barata(1300, pose={"oculos": 1.0}, keys=[{"t": j * 0.6, "pose": {"pulo": float(j % 2)}, "ease": "linear"}
                                                                          for j in range(int(d / 3 / 0.6))])},
                 "atores": {LA: {"x": 650, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "bracos", "dur": "resto"}]},
                            LU: {"x": 1950, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                            FO: {"x": 950, "turn": 0.2, "acoes": [{"t": 0.0, "do": "dance", "style": "gingado", "dur": "resto"}]},
                            JO: {"x": 1650, "turn": -0.2, "acoes": [{"t": 0.0, "do": "dance", "style": "palmas", "dur": "resto"}]}},
                 "sons": [som(0.1, "tambor", -7)]}]
    resto = b["e"] - b["s"]
    t_bord = [l for l in bl if "Laurinha" in l["text"]][0]["s"] - b["s"]
    p1 = round(max(1.2, t_bord - 0.15), 2)
    s3 = round((resto - p1 - 4.2) / 2, 2)
    return [
        {"linhas": 1, "seg": p1, "cenario": JARDIM if n == 1 else SALAO, "camera": "close:luisinho",
         "callout": [call(0.2, "QUE MASSA!", "azul")],
         "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}, "sons": [som(0.02, "boing", -7)]},
        {"linhas": 1, "seg": 4.2, "cenario": "danca_bolinhas_rosa" if n == 1 else "danca_xadrez_azul", "fx": ["confete"],
         "callout": [call(0.3, "LAURINHA E LUISINHO!", "rosa")], "objetos": {"b": barata_danca(1700, 4.2, depth=0.75)},
         "atores": {LA: {"x": 560, "y": 1010, "depth": 1.15, "turn": 0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]},
                    LU: {"x": 1360, "y": 1010, "depth": 1.15, "turn": -0.25, "acoes": [{"t": 0.0, "do": "dance", "style": "festa", "dur": "resto"}]}},
         "sons": [som(1.6, "palminhas", -6)]},
        # a barata espia de trás da caixinha, envergonhada; a Laurinha chama para dançar
        {"seg": s3, "cenario": JARDIM, "camera": {"x": 1500, "y": 660, "zoom": 1.4, "zoom_fim": 1.5}, "titulo": "a barata envergonhada",
         "objetos": {"cx": castelo(1600, real_em=0.0, depth=0.55),
                     "b": barata(1380, depth=0.75, pose={"oculos": 0.0}, keys=[{"t": 0.0, "pose": {"vergonha": 1.0, "lado": -1.0}, "ease": "step"},
                                                                              {"t": round(s3 - 1.2, 2), "pose": {"vergonha": 1.0}},
                                                                              {"t": round(s3 - 0.7, 2), "pose": {"vergonha": 0.0, "fala": 0.6}}])},
         "atores": {LA: {"x": 2500, "turn": -0.4, "acoes": [{"t": 0.2, "do": "sneak", "to_x": 1950},
                                                          {"t": round(max(1.8, s3 - 1.4), 2), "do": "wave", "dur": "resto"}]}},
         "sons": [som(0.3, "whoosh", -8)]},
        {"seg": round(resto - p1 - 4.2 - s3, 2), "cenario": SALAO, "camera": {"x": 1300, "y": 600, "zoom": 1.05, "zoom_fim": 1.15},
         "fx": ["confete"], "titulo": "festa",
         "objetos": {"b": barata(1300, pose={"oculos": 0.0}, keys=[{"t": j * 0.55, "pose": {"pulo": float(j % 2)}, "ease": "linear"}
                                                                  for j in range(int((resto - p1 - 4.2 - s3) / 0.55))]),
                     "rola": carretel_rola(resto - p1 - 4.2 - s3)},
         "atores": {FO: {"x": 700, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "passinho", "dur": "resto"}]},
                    JO: {"x": 1900, "turn": -0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "twist", "dur": "resto"}]}},
         "sons": [som(0.2, "boing", -8)]},
    ]


partes["intervalo#1"] = intervalo("intervalo#1", 1)
partes["intervalo#2"] = intervalo("intervalo#2", 2)
partes["intervalo#3"] = intervalo("intervalo#3", 3)


# ───────── ponte: a verdade (castelo → caixinha, carro → carretel, força fraquinha, coragem foi pro céu) ─────────
def ponte(key, n):
    P = [{"linhas": 1}, {"linhas": 1}, {"linhas": 1}, {"linhas": 1}]
    (a0, a1, va), (b0, b1, vb), (c0, c1, vc), (d0, d1, vd) = planos_tempo(key, P)
    tcx, tct = tp(a0, va, "caixinha", default=1.0), tp(b0, vb, "carretel", default=1.0)
    tfr = tp(c0, vc, "fraquinha", default=1.0)
    return [
        {"linhas": 1, "cenario": SONHO if n == 1 else JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.1, "zoom_fim": 1.2},
         "callout": [call(tcx + 0.1, "CAIXINHA!", "marrom")],
         "objetos": {"cx": castelo(1300, real_em=tcx, depth=0.75)},
         "atores": {LU: {"x": 2050, "turn": -0.4, "acoes": [{"t": 0.1, "do": "point", "dur": round(max(0.5, tcx), 2)},
                                                          {"t": round(tcx + 0.1, 2), "do": "laugh", "dur": "resto"}]}},
         "sons": [som(0.05, "tambor", -5)]},
        {"linhas": 1, "cenario": SONHO if n == 1 else COZINHA, "camera": {"x": 1300, "y": 700, "zoom": 1.4, "zoom_fim": 1.5},
         "callout": [call(tct + 0.1, "CARRETEL!", "azul")],
         "objetos": {"car": carro(1300, real_em=tct, anda=(0.0, b1 - b0), depth=0.9)},
         "sons": [som(max(0.05, tct - 0.3), "zap", -7), som(fim_verso(b0, vb), "pop", -6)]},
        {"linhas": 1, "cenario": JARDIM, "camera": {"x": 1300, "y": 640, "zoom": 1.45, "zoom_fim": 1.55},
         "callout": [call(tfr + 0.1, "FRAQUINHA!", "rosa")],
         "objetos": {"b": barata(1300, depth=1.0, pose={"oculos": 0.0},
                                 keys=[{"t": 0.0, "pose": {"aponta": 1.0, "pulo": 0.0}}, {"t": round(tfr, 2), "pose": {"pulo": 0.25}, "ease": "out"},
                                       {"t": round(tfr + 0.4, 2), "pose": {"pulo": 0.0, "aponta": 0.0, "vergonha": 1.0}, "ease": "in"}])},
         "atores": {JO: {"x": 2000, "turn": -0.4, "acoes": [{"t": round(tfr + 0.2, 2), "do": "laugh", "dur": "resto"}]},
                    LA: {"x": 650, "turn": 0.4, "acoes": [{"t": 0.1, "do": "sit"}, {"t": round(tfr + 0.3, 2), "do": "laugh", "dur": "resto"}]}},
         "sons": [som(round(tfr + 0.45, 2), "bonk", -6)]},
        # "a coragem foi pro céu": a câmera sobe para o céu; a barata em pânico sobe "voando" de susto
        {"linhas": 1, "cenario": CEU, "camera": {"x": 1300, "y": 620, "zoom": 1.0, "zoom_fim": 1.15}, "fx": ["estrelas"],
         "callout": [call(0.4, "FOI PRO CÉU!", "azul")],
         "objetos": {"b": barata(1300, y=1100, depth=0.8, pose={"oculos": 0.0, "susto": 1.0},
                                 keys=[{"t": 0.0, "pose": {"y": 1150}}, {"t": round(d1 - d0 - 0.2, 2), "pose": {"y": 500}, "ease": "out", "in": round(d1 - d0 - 0.3, 2)}])},
         "sons": [som(0.1, "whistle_up", -5)]},
    ]


partes["ponte#1"] = ponte("ponte#1", 1)
partes["ponte#2"] = ponte("ponte#2", 2)

# ───────── final: convite e tchau (a barata envergonhada acena de trás da caixinha) ─────────
partes["final#1"] = [
    {"linhas": 1, "cenario": JARDIM, "camera": "close:luisinho", "callout": [call(0.3, "GOSTOU?", "azul")],
     "atores": {LU: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}, "sons": [som(0.02, "pop", -6)]},
    {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.3, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
     "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3, "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
     "atores": {LU: {"x": 680, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}, "sons": [som(0.4, "ding", -6)]},
    {"linhas": 1, "cenario": CASA, "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
     "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                LU: {"x": 1450, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}, "sons": [som(0.05, "tweets", -10)]},
    {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
     "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                           "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                    {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
     "atores": {LU: {"x": 600, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}, "sons": [som(1.6, "pop", -5)]},
]
partes["final#2"] = [
    {"linhas": 1, "cenario": JARDIM, "camera": {"x": 1300, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}, "fx": ["coracoes"],
     "callout": [call(0.8, "TCHAU!", "amarelo")],
     "objetos": {"cx": castelo(1550, real_em=0.0, depth=0.55),
                 "b": barata(1450, depth=0.7, pose={"oculos": 0.0}, keys=[{"t": 0.0, "pose": {"vergonha": 1.0}, "ease": "step"},
                                                                         {"t": 1.0, "pose": {"vergonha": 0.0, "aponta": 0.0}},
                                                                         {"t": 1.4, "pose": {"aponta": 1.0}, "ease": "out"}])},
     "atores": {LA: {"x": 600, "turn": 0.3, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 3.4}, {"t": 3.6, "do": "fly", "dur": 1.4, "to_x": -300, "to_y": 300}]},
                LU: {"x": 950, "turn": 0.2, "acoes": [{"t": 0.0, "do": "dance", "style": "tchau", "dur": 3.4}, {"t": 3.7, "do": "fly", "dur": 1.4, "to_x": -350, "to_y": 350}]}},
     "sons": [som(3.6, "whoosh", -8)]},
]


def transicoes(keys):
    ultimo, out = {}, []
    for k in keys:
        k = dict(k)
        if k.get("ease", "inout") != "step" and "in" not in k:
            prev = [ultimo[c] for c in k["pose"] if c in ultimo]
            if prev:
                k["in"] = round(max(0.0, k["t"] - max(prev) - 0.03), 3)
        for c in k["pose"]:
            ultimo[c] = k["t"]
        out.append(k)
    return out


for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    for p, (t0, t1, _) in zip(planos, planos_tempo(k_info, planos)):
        p["cantam"] = ["luisinho"]
        d = t1 - t0
        assert d >= 0.6, (chave, t0, t1)
        p["sons"] = [s for s in p.get("sons", []) if s["t"] < d - 0.1]
        if not p["sons"]:
            p.pop("sons")
        for o in (p.get("objetos") or {}).values():
            if o.get("keys"):
                ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                o["keys"] = transicoes(sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"]))

faltam = [k for k in INFO if k not in partes and k.split("#")[0] not in partes]
assert not faltam, faltam
rot = {"schema": "roteiro-1.0",
       "escala_personagens": 1.45,     # 19/11 (usuário + filha de 12 anos): personagens pequenos × Animadinhos (~85 % da altura)
       "nota": "Roteiro de 'Conta Vantagem!' (take v2 de 19/11/2026, 2:46, Luisinho v2, estilo E7): a Dona Barata se gaba no jardim, "
               "sonha com castelo e carrão dourados, corre do chinelo da cozinha; na ponte a verdade (caixinha, carretel); refrão com a "
               "formiguinha e a joaninha rindo; festa no salão onde a barata acaba dançando. Efeitos sonoros por plano. "
               "Gerado por scripts/roteiros/ep19_conta_vantagem.py.",
       "partes": partes}
(MUS / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
n = sum(len(v) for v in partes.values())
print("roteiro:", n, "planos ·", round(song["duration"] / n, 1), "s por plano")
for chave, planos in partes.items():
    k_info = chave if chave in INFO else f"{chave}#1"
    print(chave, [round(t1 - t0, 1) for t0, t1, _ in planos_tempo(k_info, planos)])
