"""Roteiro PRÓPRIO do Short 20 "Dino Pisa Forte" (26/11, mesmo jeito dos Shorts 17–19 aprovados).

O DINO grandão e bonzinho é a estrela: chega pela rua pisando e a TELA TREME no "tum, tum, tremeu!"; a cada pisada
alguém pula ("Quem pulou? Fui eu!"): o Luisinho, o gato, a Laurinha, a vovó. No intervalo ele dança, anda na ponta do pé
(com o Luisinho de fininho) e dá a PISADA FORTE. Ele mesmo ruge no "Gostou do dino?" e termina com tchau + "Tum!".
Lugares de verdade (rua, sala, jardim, salão); uma da dupla por plano; pés no chão; "zum!"; sem texto por cima do
joinha/botão.

Base: `toonstudio short laurinha/ep20-dino-pisa-forte --partes "refrao#4" --ate fim` (tempos, áudio, legendas).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/sh20_dino_pisa_forte.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "projects" / "laurinha" / "ep20-dino-pisa-forte-short" / "episode.json"
RUA, SALA, JA, SALAO, CASA = "plano_rua", "plano_sala", "plano_jardim", "plano_salao", "plano_casa_frente"
CX = 1300.0
LA, LU = "laurinha", "luisinho"


def cam(*keys, shake=None):
    out = []
    for i, k in enumerate(keys):
        t, x, z = k[:3]
        y = k[3] if len(k) > 3 else 544.0
        out.append({"t": round(t, 3), "x": x, "y": y, "zoom": z, **({"ease": "inout"} if i else {})})
    return out, (shake or [])


def per(x, turn=0.15, y=990, depth=1.0, acts=()):
    return {"start": {"x": x, "y": y, "turn": turn, "expr": "happy", "z": 3, "depth": depth}, "exposure": 1,
            "actions": [dict(a) for a in acts]}


def A(do, t, dur, **kw):
    return {"do": do, "t": round(t, 3), "dur": round(max(0.3, dur), 3), **kw}


def k(t, ease=None, **pose):
    d = {"t": round(max(0.0, t), 3), "pose": pose}
    if ease:
        d["ease"] = ease
    return d


def dino(x=CX, y=960, depth=0.72, z=2, lado=1.0, keys=()):
    return {"start": {"x": x, "y": y, "z": z, "depth": depth, "lado": lado}, "exposure": 1,
            "keys": [k(0, "step", pisa=0.0, levinho=0.0, ruge=0.0, tchau=0.0)] + list(keys)}


def pisadas(ts, pe0=0.0):
    """o Dino PISA nos tempos ts (o pé desce na batida), alternando os pés."""
    out, pe = [], pe0
    for t in ts:
        out += [k(t - 0.36, "step", pisa=0.0, pe=pe), k(t, "linear", pisa=1.0), k(t + 0.04, "step", pisa=0.0)]
        pe = 1.0 - pe
    return out


def treme(ts, amp=14.0):
    return [{"t": round(t, 3), "dur": 0.35, "amp": amp} for t in ts]


def gato(x, y=960, depth=0.8, lado=-1.0, pulos=()):
    ks = [k(0, "step", y=y, assusta=0.0, rabo=0.0)]
    for t in pulos:
        ks += [k(t - 0.02, y=y, assusta=0.0), k(t + 0.22, "out", y=y - 170, assusta=1.0), k(t + 0.45, "in", y=y, assusta=0.0)]
    return {"start": {"x": x, "y": y, "z": 3, "depth": depth, "lado": lado}, "exposure": 1, "keys": ks}


def call(t, text, color):
    return [{"t": round(t, 2), "text": text, "dur": 1.4, "color": color, "y": 170}]


def main() -> None:
    e = json.loads(EP.read_text())
    sc = e["scenes"]
    assert len(sc) == 12, f"base do Short mudou ({len(sc)} planos) — refazer os tempos deste roteiro"
    ini, t = [], 0.0
    for s in sc:
        ini.append(t)
        t += s["duration"]
    loc = lambda i, tg: round(tg - ini[i], 3)
    D = [s["duration"] for s in sc]
    P = {}

    # 1 "Dino pisa forte! Tum, tum, tremeu!" — na rua o Dino pisa, a TELA TREME e ele dá um rugidinho no "tremeu!"
    t1, t2, tr = loc(0, 1.73), loc(0, 2.15), loc(0, 2.47)
    c, sh = cam((0, CX, 1.808), (D[0], CX, 1.9), shake=treme([t1, t2]))
    P[0] = dict(bg=RUA, cam=c, shake=sh, chars={},
                props={"d": dino(depth=0.8, keys=pisadas([loc(0, 0.59), loc(0, 0.99), t1, t2]) +
                                 [k(tr - 0.05, ruge=0.0), k(tr + 0.15, "out", ruge=1.0), k(min(D[0], tr + 0.6), "in", ruge=0.0)])},
                sing=None, calls=call(t1, "TUM, TUM!", "laranja"))
    # 2 "Dino pisa forte! Quem pulou? Fui eu!" — o Dino pisa atrás e o LUISINHO pula; "Fui eu!" com o ZUM
    tp, tf = loc(1, 4.85), loc(1, 5.33)
    c, sh = cam((0, CX, 1.808), (D[1], CX, 1.9), shake=treme([loc(1, 3.79)], 10))
    P[1] = dict(bg=SALA, cam=c, shake=sh,
                chars={LU: per(CX - 150, 0.3, y=990, acts=[A("jump", tp - 0.2, 0.6), A("zum", tf, D[1] - tf - 0.05)])},
                props={"d": dino(CX + 105, 900, 0.54, lado=-1.0, keys=pisadas([loc(1, 3.79)]))},
                sing=LU, calls=call(tf, "FUI EU!", "azul"))
    # 3 "Dino pisa forte! Tum, tum, tremeu!" — na sala: o GATO pula a cada tum e a Laurinha leva um susto
    t1, t2 = loc(2, 8.21), loc(2, 8.57)
    c, sh = cam((0, CX, 1.808), (D[2], CX, 1.808), shake=treme([t1, t2]))
    P[2] = dict(bg=SALA, cam=c, shake=sh,
                chars={LA: per(CX - 150, 0.3, y=990, acts=[A("look_around", 0.1, t1 - 0.2), A("shock_reaction", t1, D[2] - t1 - 0.05)])},
                props={"gato": gato(CX + 140, pulos=[t1, t2])}, sing=LA, calls=call(t1, "TREMEU!", "laranja"))
    # 4 "Dino pisa forte! Quem pulou? Fui eu!" — no jardim a LAURINHA pula e levanta a mão: "Fui eu!"
    tp, tf = loc(3, 11.31), loc(3, 11.81)
    c, sh = cam((0, CX, 1.808), (D[3], CX, 1.9), shake=treme([loc(3, 10.25)], 10))
    P[3] = dict(bg=JA, cam=c, shake=sh,
                chars={LA: per(CX - 150, 0.3, y=990, acts=[A("jump", tp - 0.2, 0.6), A("cheguei", tf + 0.2, D[3] - tf - 0.25)])},
                props={"d": dino(CX + 105, 900, 0.54, lado=-1.0, keys=pisadas([loc(3, 10.25)]))},
                sing=LA, calls=call(tf, "FUI EU!", "rosa"))
    # 5 (instrumental) — no salão o Dino DANÇA (balança o rabo) e o Luisinho dança junto
    c, sh = cam((0, CX - 30, 1.808), (D[4], CX + 30, 1.808))
    P[4] = dict(bg=SALAO, cam=c, shake=sh,
                chars={LU: per(CX - 150, 0.3, y=990, acts=[A("dance", 0.0, D[4] - 1.3, style="festa"), A("zum", D[4] - 1.3, 1.25)])},
                props={"d": dino(CX + 105, 900, 0.54, lado=-1.0, keys=[k(0, "step", danca=0.0), k(D[4], "linear", danca=D[4] * 0.8)])},
                sing=None, fx=["confete"], calls=[])
    # 6 (instrumental) — PISA FRAQUINHO: o Dino na ponta do pé e a Laurinha de fininho
    c, sh = cam((0, CX, 1.808), (D[5], CX, 1.808))
    P[5] = dict(bg=SALA, cam=c, shake=sh,
                chars={LA: per(CX - 230, 0.35, y=990, acts=[A("sneak", 0.1, D[5] - 0.2, to_x=CX - 140)])},
                props={"d": dino(CX + 105, 900, 0.54, lado=-1.0, keys=[k(0.1, levinho=0.0), k(0.5, "inout", levinho=1.0)])},
                sing=None, calls=call(0.3, "PSIU…", "verde"))
    # 7 (instrumental) — a PISADA FORTE: tremor grande e a vovó pula ("ai, ai, devagar!")
    tb = 1.6
    c, sh = cam((0, CX, 1.808), (D[6], CX, 1.808), shake=treme([tb], 26))
    P[6] = dict(bg=JA, cam=c, shake=sh,
                chars={"vovo": per(CX - 150, 0.3, y=990, acts=[A("jump", tb - 0.1, 0.6), A("shake_fist", tb + 0.8, D[6] - tb - 0.85)])},
                props={"d": dino(CX + 105, 900, 0.54, lado=-1.0, keys=pisadas([tb]) +
                                 [k(tb + 0.9, levinho=0.0), k(tb + 1.3, "inout", levinho=1.0)])},
                sing=None, calls=call(tb, "PISA FORTE!", "laranja"))
    # 8 "Gostou do dino?" — close no Dino, que dá um rugidinho fofo para a criança
    c, sh = cam((0, CX, 2.0, 520), (D[7], CX, 2.15, 520))
    P[7] = dict(bg=SALA, cam=c, shake=sh, chars={},
                props={"d": dino(CX, 1000, 0.75, keys=[k(0.3, ruge=0.0), k(0.55, "out", ruge=1.0), k(1.2, ruge=1.0),
                                                     k(1.5, "in", ruge=0.0), k(1.6, tchau=0.0), k(1.9, "out", tchau=1.0)])},
                sing=None, calls=call(0.2, "GOSTOU?", "rosa"))
    # 9 "Dá um joinha!" — a Laurinha com o JOINHA acima da cabeça (sala)
    c, sh = cam((0, CX, 1.808), (D[8], CX, 1.808))
    P[8] = dict(bg=SALA, cam=c, shake=sh, chars={LA: per(CX, acts=[A("bacana", 0.1, D[8] - 0.15)])},
                props={"joinha": {"start": {"x": CX, "y": 330, "z": 4, "depth": 0.6}, "exposure": 1,
                                  "keys": [k(0, escala=0.0), k(0.3, "back", escala=1.0)]}},
                sing=LA, fx=["estrelas"], calls=[])
    # 10 "Chama o papai e a mamãe" — na frente de casa a mamãe chega acenando; o Luisinho aponta
    c, sh = cam((0, CX, 1.808), (D[9], CX, 1.808))
    P[9] = dict(bg=CASA, cam=c, shake=sh,
                chars={LU: per(CX - 120, 0.3, y=930, acts=[A("point", 0.3, D[9] - 0.35)]),
                       "mamae": per(CX + 380, -0.3, y=930, acts=[A("walk", 0.0, 0.8, to_x=CX + 150), A("wave", 0.85, D[9] - 0.9)])},
                props={}, sing=LU, calls=call(0.2, "CHAMA O PAPAI E A MAMÃE!", "verde"))
    # 11 "Pra se inscrever no canal! Zum, zum!" — o botão é clicado e o Luisinho faz o ZUM (o botão afunda nos "zum")
    tc, z1, z2 = loc(10, 31.27), loc(10, 32.45), loc(10, 33.13)
    c, sh = cam((0, CX, 1.808), (D[10], CX, 1.9))
    P[10] = dict(bg=SALA, cam=c, shake=sh,
                 chars={LU: per(CX, acts=[A("point", 0.2, z1 - 0.35), A("zum", z1 - 0.1, D[10] - z1 + 0.05)])},
                 props={"botao": {"start": {"x": CX, "y": 300, "z": 4, "depth": 0.55}, "exposure": 1,
                                  "keys": [k(0, escala=0.0, aperta=0.0), k(0.4, "back", escala=1.0), k(tc, "out", aperta=1.0),
                                           k(tc + 0.3, "in", aperta=0.0), k(z1, "out", aperta=1.0), k(z1 + 0.3, "in", aperta=0.0),
                                           k(z2, "out", aperta=1.0), k(z2 + 0.3, "in", aperta=0.0)]}},
                 sing=LU, fx=["coracoes"], calls=[])
    # 12 "Dino pisa forte! Tchau! Tum!" — o Dino e a Laurinha dão tchau; no "Tum!" a última pisada e o gato pula
    tt, tm = loc(11, 35.29), loc(11, 35.47)
    c, sh = cam((0, CX, 1.808), (D[11], CX, 1.808), shake=treme([tm], 22))
    P[11] = dict(bg=CASA, cam=c, shake=sh,
                 chars={LA: per(CX - 150, 0.3, y=990, acts=[A("dance", 0.0, max(0.5, tt - 0.1), style="cabeca"), A("wave", tt, D[11] - tt - 0.05)])},
                 props={"d": dino(CX + 105, 900, 0.54, lado=-1.0, keys=pisadas([loc(11, 34.31), tm]) +
                                  [k(tt - 0.1, tchau=0.0), k(tt + 0.2, "out", tchau=1.0)])},
                 sing=LA, calls=call(tt, "TCHAU!", "amarelo"))

    for i, s in enumerate(sc):
        p = P[i]
        s["background"] = p["bg"]
        s.pop("panels", None)
        s.pop("layout", None)
        s["camera"] = {"keys": p["cam"], "beat": s.get("camera", {}).get("beat", {"pulse": 0.0, "bar_zoom": 0.04, "sway": 6, "bounce": 0})}
        if p["shake"]:
            s["camera"]["shake"] = p["shake"]
        s["characters"] = p["chars"]
        s["props"] = p["props"]
        s["fx"] = p.get("fx", [])
        s["callouts"] = p["calls"]
        quem = p["sing"]
        s["sing"] = [{**x, "who": quem} for x in s.get("sing", [])] if quem else []
    e["approval"]["storyboard"] = False
    EP.write_text(json.dumps(e, ensure_ascii=False, indent=2))
    print(f"{EP.relative_to(ROOT)}: {len(sc)} planos reescritos (roteiro próprio do Short)")


if __name__ == "__main__":
    main()
