"""Roteiro PRÓPRIO do Short 19 "Conta Vantagem!" (26/11, mesmo jeito dos Shorts 17 e 18 aprovados).

A DONA BARATA é a estrela: se gaba do castelo dourado (que vira CAIXINHA no "mentirinha!") e do carro conversível (que
vira CARRETEL); a turma ri ("Ha, ha, Baratinha!"); no intervalo o CHINELO aparece e ela sai correndo; depois, envergonhada,
acaba dançando com a turma; ela mesma aponta o INSCREVA-SE e dá tchau de trás da caixinha. Lugares de verdade
(jardim, cozinha, salão); uma da dupla por plano; pés no chão; "zum!".

Base: `toonstudio short laurinha/ep19-conta-vantagem --partes "refrao#4" --ate fim` (tempos, áudio, legendas).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/sh19_conta_vantagem.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "projects" / "laurinha" / "ep19-conta-vantagem-short" / "episode.json"
JA, CZ, SA = "plano_jardim", "plano_cozinha", "plano_salao"
CX = 1300.0
LA, LU = "laurinha", "luisinho"


def cam(*keys):
    out = []
    for i, k in enumerate(keys):
        t, x, z = k[:3]
        y = k[3] if len(k) > 3 else 544.0
        out.append({"t": round(t, 3), "x": x, "y": y, "zoom": z, **({"ease": "inout"} if i else {})})
    return out


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


def barata(x, y=960, depth=1.05, oculos=1.0, lado=1.0, keys=(), z=3):
    return {"start": {"x": x, "y": y, "z": z, "oculos": oculos, "depth": depth, "lado": lado}, "exposure": 1, "keys": list(keys)}


def fala(ts):
    """boquinha da barata nas sílabas (tempos dentro do plano)."""
    out = []
    for t in ts:
        out += [k(t, fala=0.0), k(t + 0.08, "out", fala=0.8), k(t + 0.25, "in", fala=0.0)]
    return out


def call(t, text, color):
    return [{"t": round(t, 2), "text": text, "dur": 1.6, "color": color, "y": 170}]


def main() -> None:
    e = json.loads(EP.read_text())
    sc = e["scenes"]
    assert len(sc) == 14, f"base do Short mudou ({len(sc)} planos) — refazer os tempos deste roteiro"
    ini, t = [], 0.0
    for s in sc:
        ini.append(t)
        t += s["duration"]
    loc = lambda i, tg: round(tg - ini[i], 3)
    D = [s["duration"] for s in sc]
    P = {}

    # 1 "Conta vantagem! Ih, é mentirinha!" — no jardim a barata aponta o CASTELO DOURADO… e ele vira CAIXINHA
    tm = loc(0, 3.09)
    P[0] = dict(bg=JA, cam=cam((0, CX, 1.808), (D[0], CX, 1.9)), chars={},
                props={"cast": {"start": {"x": CX + 140, "y": 900, "z": 1, "real": 0.0, "depth": 0.5}, "exposure": 1,
                                "keys": [k(0, "step", real=0.0, brilho=1.0), k(tm - 0.1, real=0.0, brilho=1.0),
                                         k(tm + 0.2, "out", real=1.0, brilho=0.0)]},
                       "b": barata(CX - 105, keys=[k(0, "step", metida=1.0, aponta=0.0, vergonha=0.0)] +
                                   [k(0.9, aponta=0.0), k(1.2, "back", aponta=1.0)] + fala([loc(0, 1.28), loc(0, 1.69), loc(0, 2.0)]) +
                                   [k(tm, metida=1.0, aponta=1.0), k(tm + 0.25, "step", metida=0.0, aponta=0.0, vergonha=1.0, oculos=0.0)])},
                sing=None, calls=call(loc(0, 1.28), "CONTA VANTAGEM!", "laranja") + call(tm, "MENTIRINHA!", "rosa"))
    # 2 "Conta vantagem! Ha, ha, Baratinha!" — close na Laurinha rindo da barata
    th = loc(1, 5.31)
    P[1] = dict(bg=JA, cam=cam((0, CX, 2.2, 600), (D[1], CX, 2.35, 600)),
                chars={LA: per(CX, acts=[A("look_around", 0.1, th - 0.2), A("laugh", th, D[1] - th - 0.05)])},
                props={}, sing=LA, calls=call(th, "HA, HA!", "amarelo"))
    # 3 "Conta vantagem! Ih, é mentirinha!" — o CARRO conversível… vira CARRETEL de linha
    tm = loc(2, 8.63)
    P[2] = dict(bg=JA, cam=cam((0, CX, 1.808), (D[2], CX, 1.9)), chars={},
                props={"car": {"start": {"x": CX + 130, "y": 980, "z": 2, "real": 0.0, "depth": 0.52}, "exposure": 1,
                               "keys": [k(0, "step", real=0.0, anda=0.0), k(tm - 0.1, real=0.0, anda=1.5),
                                        k(tm + 0.2, "out", real=1.0, anda=1.5)]},
                       "b": barata(CX - 110, keys=[k(0, "step", metida=1.0, aponta=1.0, vergonha=0.0)] +
                                   fala([loc(2, 6.95), loc(2, 7.37), loc(2, 7.7)]) +
                                   [k(tm, metida=1.0), k(tm + 0.25, "step", metida=0.0, aponta=0.0, vergonha=1.0, oculos=0.0)])},
                sing=None, calls=call(tm, "MENTIRINHA!", "rosa"))
    # 4 "Conta vantagem! Ha, ha, Baratinha!" — o Luisinho e a joaninha caem na risada
    th = loc(3, 10.89)
    P[3] = dict(bg=JA, cam=cam((0, CX, 1.808), (D[3], CX, 1.9)),
                chars={LU: per(CX - 140, 0.3, y=960, acts=[A("point", 0.1, th - 0.2), A("laugh", th, D[3] - th - 0.05)]),
                       "joaninha": per(CX + 150, -0.3, y=960, depth=0.85, acts=[A("laugh", th, D[3] - th - 0.05)])},
                props={}, sing=LU, calls=call(th, "HA, HA, BARATINHA!", "amarelo"))
    # 5 (instrumental) — na cozinha o CHINELO voa… a barata leva um susto e sai CORRENDO
    P[4] = dict(bg=CZ, cam=cam((0, CX, 1.808), (D[4], CX, 1.808)), chars={},
                props={"b": barata(CX - 60, oculos=0.0, lado=1.0,
                                   keys=[k(0, "step", susto=0.0, correndo=0.0, corre=0.0, x=CX - 60), k(0.9, susto=0.0),
                                         k(1.15, "back", susto=1.0), k(1.9, susto=1.0, correndo=0.0, x=CX - 60),
                                         k(2.0, "step", susto=0.0, correndo=1.0),
                                         k(2.0, "step", corre=0.0), k(D[4], "linear", corre=12.0, x=CX + 520)]),
                       "ch": {"start": {"x": CX - 320, "y": 260, "z": 4, "deitado": 0.0, "depth": 0.6}, "exposure": 1,
                              "keys": [k(0, "step", gira=0.0, bate=0.0, x=CX - 420, y=200), k(1.0, "linear", gira=1.5, x=CX - 120, y=700),
                                       k(1.15, "step", deitado=1.0), k(1.2, "out", bate=1.0, y=1000), k(1.6, "in", bate=0.0)]}},
                sing=None, calls=call(1.1, "AAAH!", "vermelho"))
    # 6 (instrumental) — no salão a Laurinha e a formiguinha dançam
    P[5] = dict(bg=SA, cam=cam((0, CX - 40, 1.808), (D[5], CX + 40, 1.808)),
                chars={LA: per(CX - 140, 0.3, y=960, acts=[A("dance", 0.0, D[5], style="festa")]),
                       "formiguinha": per(CX + 150, -0.3, y=960, depth=0.85, acts=[A("dance", 0.0, D[5], style="cabeca")])},
                props={}, sing=None, calls=[])
    # 7 (instrumental) — a barata, envergonhada, acaba dançando com o Luisinho (e ele fecha com o ZUM)
    P[6] = dict(bg=SA, cam=cam((0, CX, 1.808), (D[6], CX, 1.95)),
                chars={LU: per(CX - 140, 0.3, y=960, acts=[A("dance", 0.0, 2.6, style="festa"), A("zum", 2.7, D[6] - 2.75)])},
                props={"b": barata(CX + 150, oculos=0.0, lado=-1.0,
                                   keys=[k(0, "step", vergonha=1.0, pulo=0.0), k(1.2, vergonha=1.0), k(1.6, vergonha=0.0)] +
                                   [kk for j in range(4) for kk in (k(1.7 + j * 0.6, pulo=0.0), k(1.95 + j * 0.6, "out", pulo=1.0),
                                                                    k(2.2 + j * 0.6, "in", pulo=0.0))])},
                sing=None, fx=["confete"], calls=[])
    # 8 "Gostou da Dona Barata?" — close: a barata de óculos, metida, pergunta para a criança
    P[7] = dict(bg=JA, cam=cam((0, CX, 2.1, 600), (D[7], CX, 2.25, 600)), chars={},
                props={"b": barata(CX, y=1000, depth=1.15, keys=[k(0, "step", metida=1.0, aponta=0.0), k(0.4, "back", aponta=1.0)] +
                                   fala([loc(7, w) for w in (24.59, 25.51, 25.71, 25.95, 26.3)]))},
                sing=None, calls=call(0.2, "GOSTOU?", "rosa"))
    # 9 "Dá um joinha!" — a Laurinha no jardim com o JOINHA acima da cabeça
    P[8] = dict(bg=JA, cam=cam((0, CX, 1.808), (D[8], CX, 1.808)),
                chars={LA: per(CX, acts=[A("bacana", 0.2, D[8] - 0.25)])},
                props={"joinha": {"start": {"x": CX, "y": 330, "z": 4, "depth": 0.6}, "exposure": 1,
                                  "keys": [k(0, escala=0.0), k(0.4, "back", escala=1.0)]}},
                sing=LA, fx=["estrelas"], calls=[])
    # 10 "Chama o papai e a mamãe" — a mamãe chega no jardim acenando; o Luisinho aponta
    P[9] = dict(bg=JA, cam=cam((0, CX, 1.808), (D[9], CX, 1.808)),
                chars={LU: per(CX - 120, 0.3, y=930, acts=[A("point", 0.3, D[9] - 0.35)]),
                       "mamae": per(CX + 380, -0.3, y=930, acts=[A("walk", 0.0, 0.8, to_x=CX + 150), A("wave", 0.85, D[9] - 0.9)])},
                props={}, sing=LU, calls=call(0.2, "CHAMA O PAPAI E A MAMÃE!", "verde"))
    # 11 "Pra se inscrever no canal!" — a própria barata aponta o INSCREVA-SE e ele é clicado
    tc = loc(10, 33.49)
    P[10] = dict(bg=JA, cam=cam((0, CX, 1.808), (D[10], CX, 1.808)), chars={},
                 props={"b": barata(CX, y=1000, keys=[k(0, "step", metida=0.0, aponta=0.0), k(0.5, "back", aponta=1.0)] +
                                    fala([loc(10, w) for w in (31.53, 32.41, 32.67, 33.21, 33.49)])),
                        "botao": {"start": {"x": CX, "y": 300, "z": 4, "depth": 0.55}, "exposure": 1,
                                  "keys": [k(0, escala=0.0, aperta=0.0), k(0.4, "back", escala=1.0), k(tc, "out", aperta=1.0),
                                           k(tc + 0.3, "in", aperta=0.0)]}},
                 sing=None, fx=["coracoes"], calls=[])
    # 12 "Zum, zum!" — o Luisinho faz o ZUM embaixo do botão, que afunda nos dois "zum"
    z1, z2 = loc(11, 34.55), loc(11, 35.29)
    P[11] = dict(bg=JA, cam=cam((0, CX, 1.808), (D[11], CX, 1.9)),
                 chars={LU: per(CX, acts=[A("zum", max(0.05, z1 - 0.15), 1.5), A("dance", 1.8, D[11] - 1.85, style="festa")])},
                 props={"botao": {"start": {"x": CX, "y": 300, "z": 4, "depth": 0.55}, "exposure": 1,
                                  "keys": [k(0, aperta=0.0), k(z1, "out", aperta=1.0), k(z1 + 0.3, "in", aperta=0.0),
                                           k(z2, "out", aperta=1.0), k(z2 + 0.3, "in", aperta=0.0)]}},
                 sing=LU, fx=["coracoes"], calls=[])
    # 13 "Conta vantagem! Tchau! Ha ha!" — a barata dá tchau de trás da CAIXINHA; a Laurinha ri
    tt, th = loc(12, 39.83), loc(12, 40.69)
    P[12] = dict(bg=JA, cam=cam((0, CX, 1.808), (D[12], CX, 1.808)),
                 chars={LA: per(CX - 150, 0.3, y=960, acts=[A("laugh", 0.1, max(0.4, tt - 0.4)), A("wave", max(0.5, tt - 0.2), D[12] - max(0.5, tt - 0.2) - 0.05)])},
                 props={"cx": {"start": {"x": CX + 150, "y": 990, "z": 4, "real": 1.0, "depth": 0.55}, "exposure": 1},
                        "b": barata(CX + 150, y=900, depth=0.95, oculos=0.0, lado=-1.0, z=2,
                                    keys=[k(0, "step", aponta=0.0, vergonha=1.0), k(tt - 0.1, aponta=0.0, vergonha=1.0),
                                          k(tt + 0.2, "back", aponta=1.0, vergonha=0.0), k(tt + 0.5, aponta=0.5),
                                          k(tt + 0.8, aponta=1.0), k(tt + 1.1, aponta=0.5)])},
                 sing=LA, calls=call(tt, "TCHAU!", "amarelo"))
    # 14 (fim) — a barata e o Luisinho dançam juntos; ele fecha com o ZUM
    P[13] = dict(bg=SA, cam=cam((0, CX, 1.808), (D[13], CX, 1.95)),
                 chars={LU: per(CX - 140, 0.3, y=960, acts=[A("dance", 0.0, 1.2, style="cabeca"), A("zum", 1.3, D[13] - 1.35)])},
                 props={"b": barata(CX + 150, oculos=1.0, lado=-1.0,
                                    keys=[k(0, "step", metida=1.0, pulo=0.0)] +
                                    [kk for j in range(4) for kk in (k(0.2 + j * 0.6, pulo=0.0), k(0.45 + j * 0.6, "out", pulo=1.0),
                                                                     k(0.7 + j * 0.6, "in", pulo=0.0))])},
                 sing=None, fx=["confete"], calls=[])

    for i, s in enumerate(sc):
        p = P[i]
        s["background"] = p["bg"]
        s.pop("panels", None)
        s.pop("layout", None)
        s["camera"] = {"keys": p["cam"], "beat": s.get("camera", {}).get("beat", {"pulse": 0.0, "bar_zoom": 0.04, "sway": 6, "bounce": 0})}
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
