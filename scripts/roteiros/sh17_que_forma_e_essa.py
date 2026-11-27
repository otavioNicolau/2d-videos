"""Roteiro PRÓPRIO do Short 17 "Que Forma É Essa?" (26/11, mesmo jeito do Short 18 aprovado).

Um QUIZ na cozinha: a cada "Que forma é essa?" uma comida-personagem aparece ACIMA DA CABEÇA de quem responde
(usuário: "personagem abaixo e a forma acima da cabeça"), quica, e na resposta a forma ACENDE (pizza = círculo, torrada =
quadrado, queijo = triângulo, ovo = oval). Sem fundo de raios/bolinhas; uma da dupla por plano; pés no chão; "zum!".

Base: `toonstudio short laurinha/ep17-que-forma-e-essa --partes "refrao#4" --ate fim` (tempos, áudio, legendas).
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/sh17_que_forma_e_essa.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "projects" / "laurinha" / "ep17-que-forma-e-essa-short" / "episode.json"
CZ = "plano_cozinha"
CX = 1300.0
LA, LU = "laurinha", "luisinho"
NOME = {0: "pz", 1: "tr", 2: "qj", 3: "ov", 4: "pr"}


def cam(*keys):
    out = []
    for i, k in enumerate(keys):
        t, x, z = k[:3]
        y = k[3] if len(k) > 3 else 544.0
        out.append({"t": round(t, 3), "x": x, "y": y, "zoom": z, **({"ease": "inout"} if i else {})})
    return out


def per(x, turn=0.15, y=990, acts=()):
    return {"start": {"x": x, "y": y, "turn": turn, "expr": "happy", "z": 3, "depth": 1.0}, "exposure": 1,
            "actions": [dict(a) for a in acts]}


def A(do, t, dur, **kw):
    return {"do": do, "t": round(t, 3), "dur": round(max(0.3, dur), 3), **kw}


def k(t, ease=None, **pose):
    d = {"t": round(max(0.0, t), 3), "pose": pose}
    if ease:
        d["ease"] = ease
    return d


def comida(tipo, x=CX, y=470, depth=0.75, z=4, keys=()):
    return NOME[tipo], {"start": {"x": x, "y": y, "z": z, "tipo": tipo, "depth": depth}, "exposure": 1, "keys": list(keys)}


def pergunta(tipo, t_pulo, t_acende, d):
    """A comida aparece (escala), quica na pergunta e ACENDE na resposta."""
    ks = [k(0, "step", brilho=0.0, pulo=0.0, boca=0.0)]
    for tp in t_pulo:
        ks += [k(tp, pulo=0.0), k(tp + 0.25, "out", pulo=1.0), k(tp + 0.5, "in", pulo=0.0)]
    ks += [k(t_acende - 0.05, brilho=0.0, boca=0.0), k(t_acende + 0.2, "back", brilho=1.0, boca=1.0),
           k(min(d, t_acende + 0.8), boca=0.0)]
    return comida(tipo, keys=ks)


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

    # 1 "Que forma é essa? / Responde ligeiro!" — a Laurinha pensa; a PIZZA aparece acima da cabeça e quica
    P[0] = dict(cam=cam((0, CX, 1.808), (D[0], CX, 1.95)),
                chars={LA: per(CX, acts=[A("pensar", 0.2, 2.4), A("point", 2.7, D[0] - 2.75)])},
                props=dict([pergunta(0, [loc(0, 1.58)], loc(0, 3.34), D[0])]), sing=LA,
                calls=call(loc(0, 1.16), "QUE FORMA É ESSA?", "verde"))
    # 2 "Que forma é essa? / Quem acertou primeiro?" — o Luisinho e a TORRADA; ele acerta: "quadrado!" (acende) e faz o ZUM
    tz = loc(1, 6.0)
    P[1] = dict(cam=cam((0, CX, 1.808), (D[1], CX, 1.9)),
                chars={LU: per(CX, acts=[A("pensar", 0.1, tz - 0.2), A("zum", tz, D[1] - tz - 0.05)])},
                props=dict([pergunta(1, [loc(1, 4.88)], tz, D[1])]), sing=LU, calls=call(tz + 0.1, "ACERTOU!", "verde"))
    # 3 "Que forma é essa? / Responde ligeiro!" — close na Laurinha olhando o QUEIJO; levanta a mão e acende: "triângulo!"
    ta = loc(2, 9.5)
    P[2] = dict(cam=cam((0, CX, 2.1, 620), (D[2], CX, 2.2, 620)),
                chars={LA: per(CX, y=1060, acts=[A("look_around", 0.1, ta - 0.2), A("cheguei", ta, D[2] - ta - 0.05)])},
                props=dict([(lambda nm_pr: (nm_pr[0], {**nm_pr[1], "start": {**nm_pr[1]["start"], "y": 545}}))(pergunta(2, [loc(2, 8.18)], ta, D[2]))]), sing=LA, calls=call(ta, "RESPONDE LIGEIRO!", "laranja"))
    # 4 "Que forma é essa? / Quem acertou primeiro?" — o Luisinho e o OVO: "oval!" e ri
    ta = loc(3, 12.62)
    P[3] = dict(cam=cam((0, CX, 1.808), (D[3], CX, 1.95)),
                chars={LU: per(CX, acts=[A("pensar", 0.1, ta - 0.2), A("laugh", ta, D[3] - ta - 0.05)])},
                props=dict([pergunta(3, [loc(3, 11.48)], ta, D[3])]), sing=LU, calls=call(ta, "QUEM ACERTOU?", "azul"))
    # 5 (instrumental) — na mesa do lanche as 5 comidas dançam em fila e as formas acendem uma por uma
    ks_all = {}
    for i, tipo in enumerate(range(5)):
        tp = 0.3 + i * 0.75
        ks = [k(0, "step", brilho=0.0, pulo=0.0)]
        for j in range(3):
            b = 0.2 + j * 1.4 + i * 0.12
            ks += [k(b, pulo=0.0), k(b + 0.22, "out", pulo=1.0), k(b + 0.45, "in", pulo=0.0)]
        ks += [k(tp, brilho=0.0), k(tp + 0.2, "back", brilho=1.0)]
        nm, pr = comida(tipo, x=CX - 176 + i * 88, y=618, depth=0.42, z=2, keys=ks)
        ks_all[nm] = pr
    P[4] = dict(cam=cam((0, CX, 1.95, 580), (D[4], CX, 1.95, 580)), chars={},
                props={"mesa": {"start": {"x": CX, "y": 930, "z": 1, "depth": 1.3}, "exposure": 1}, **ks_all},
                sing=None, fx=["confete"], calls=[])
    # 6 "Gostou das formas?" — close no Luisinho falando com a criança
    P[5] = dict(cam=cam((0, CX, 2.2, 600), (D[5], CX, 2.35, 600)),
                chars={LU: per(CX, acts=[A("apontar_camera", 0.1, D[5] - 0.15)])}, props={}, sing=LU,
                calls=call(0.2, "GOSTOU?", "rosa"))
    # 7 "Dá um joinha!" — a Laurinha na cozinha com o JOINHA acima da cabeça
    P[6] = dict(cam=cam((0, CX, 1.808), (D[6], CX, 1.808)),
                chars={LA: per(CX, acts=[A("bacana", 0.2, D[6] - 0.25)])},
                props={"joinha": {"start": {"x": CX, "y": 330, "z": 4, "depth": 0.6}, "exposure": 1,
                                  "keys": [k(0, escala=0.0), k(0.4, "back", escala=1.0)]}},
                sing=LA, fx=["estrelas"], calls=[])
    # 8 "Chama o papai e a mamãe" — a mamãe entra na cozinha acenando; o Luisinho aponta para ela
    P[7] = dict(cam=cam((0, CX, 1.808), (D[7], CX, 1.808)),
                chars={LU: per(CX - 120, 0.3, y=930, acts=[A("point", 0.3, D[7] - 0.35)]),
                       "mamae": per(CX + 380, -0.3, y=930, acts=[A("walk", 0.0, 0.8, to_x=CX + 150), A("wave", 0.85, D[7] - 0.9)])},
                props={}, sing=LU, calls=call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde"))
    # 9 "Pra se inscrever no canal!" — a Laurinha aponta e o INSCREVA-SE aparece e é clicado
    tc = loc(8, 27.8)
    P[8] = dict(cam=cam((0, CX, 1.808), (D[8], CX, 1.808)),
                chars={LA: per(CX, acts=[A("point", 0.2, D[8] - 0.25)])},
                props={"botao": {"start": {"x": CX, "y": 300, "z": 4, "depth": 0.55}, "exposure": 1,
                                 "keys": [k(0, escala=0.0, aperta=0.0), k(0.4, "back", escala=1.0), k(tc, "out", aperta=1.0),
                                          k(tc + 0.3, "in", aperta=0.0)]}},
                sing=LA, fx=["coracoes"], calls=[])
    # 10 "Zum, zum!" — o Luisinho faz o ZUM embaixo do botão, que fica apertadinho
    P[9] = dict(cam=cam((0, CX, 1.808), (D[9], CX, 1.9)),
                chars={LU: per(CX, acts=[A("zum", 0.1, 1.5), A("dance", 1.7, D[9] - 1.75, style="festa")])},
                props={"botao": {"start": {"x": CX, "y": 300, "z": 4, "depth": 0.55}, "exposure": 1,
                                 "keys": [k(0, aperta=0.0), k(0.47, "out", aperta=1.0)]}},
                sing=LU, fx=["coracoes"], calls=[])
    # 11 "Que forma é essa? Tchau! Círculo!" — a Laurinha e a PIZZA: tchau… "círculo!" (acende)
    tt, tc = loc(10, 34.4), loc(10, 34.74)
    P[10] = dict(cam=cam((0, CX, 1.808), (D[10], CX, 1.95)),
                 chars={LA: per(CX, acts=[A("pensar", 0.05, tt - 0.1), A("wave", tt, D[10] - tt - 0.05)])},
                 props=dict([pergunta(0, [loc(10, 33.0)], tc, D[10])]), sing=LA, calls=call(tt, "TCHAU!", "amarelo"))
    # 12 (fim) — o Luisinho dança com o PRESENTE quicando acima da cabeça
    P[11] = dict(cam=cam((0, CX, 1.808), (D[11], CX, 1.808)),
                 chars={LU: per(CX, acts=[A("dance", 0.0, D[11], style="festa")])},
                 props=dict([pergunta(4, [0.3, 1.3, 2.3], 1.8, D[11])]), sing=None, calls=[])
    # 13 (fim) — a mesa do lanche: as comidas dão tchau quicando
    P[12] = dict(cam=cam((0, CX, 1.95, 580), (D[12], CX, 1.95, 580)), chars={},
                 props={"mesa": {"start": {"x": CX, "y": 930, "z": 1, "depth": 1.3}, "exposure": 1},
                        **{nm: {**pr, "keys": [k(0, "step", brilho=1.0, pulo=0.0)] +
                                [kk for j in range(2) for kk in (k(0.3 + j * 1.3 + i * 0.1, pulo=0.0),
                                                                 k(0.55 + j * 1.3 + i * 0.1, "out", pulo=1.0),
                                                                 k(0.8 + j * 1.3 + i * 0.1, "in", pulo=0.0))]}
                           for i, (nm, pr) in enumerate(ks_all.items())}},
                 sing=None, fx=["coracoes"], calls=[])
    # 14 (fim) — a Laurinha fecha com o ZUM e a pizza acesa acima da cabeça
    P[13] = dict(cam=cam((0, CX, 1.808), (D[13], CX, 2.0)),
                 chars={LA: per(CX, acts=[A("zum", 0.3, 1.6), A("wave", 2.0, D[13] - 2.05)])},
                 props=dict([comida(0, keys=[k(0, "step", brilho=1.0, pulo=0.0), k(0.3, pulo=0.0), k(0.55, "out", pulo=1.0),
                                             k(0.8, "in", pulo=0.0)])]), sing=None, calls=[])

    for i, s in enumerate(sc):
        p = P[i]
        s["background"] = CZ
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
