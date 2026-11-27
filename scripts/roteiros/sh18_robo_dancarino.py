"""Roteiro PRÓPRIO do Short 18 "Robô Dançarino" (26/11, usuário: "está aparentando rascunho, conteúdo reaproveitado").

Não reaproveita os planos do clipe: a história acontece toda na OFICINA (sem fundo de raios/bolinhas), um plano por
frase, com o robô como parceiro de cena — liga no botão, trava ("Bip, bop, travou!"), a turma imita a estátua, volta
("voltou!"), gira a cabeça, aperta o INSCREVA-SE e no fim a pilha acaba. Uma da dupla por plano; pés no chão; "zum!".

Base: `toonstudio short laurinha/ep18-robo-dancarino --partes "refrao#3" --ate fim` (tempos, áudio, legendas).
Este script reescreve só o CONTEÚDO dos planos (cenário, câmera, personagens, objetos, ações) do episode.json do -short.
Rodar: PYTHONPATH=. .venv/bin/python scripts/roteiros/sh18_robo_dancarino.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "projects" / "laurinha" / "ep18-robo-dancarino-short" / "episode.json"
OF = "plano_oficina"
CX = 1000.0                     # centro do quadro vertical na oficina
LA, LU = "laurinha", "luisinho"
RITMO = 0.75                    # passinhos do robô por segundo (como no clipe)


def cam(*keys):
    """keys: (t, x, zoom[, y]) → câmera; y padrão do quadro aberto/close."""
    out = []
    for i, k in enumerate(keys):
        t, x, z = k[:3]
        y = k[3] if len(k) > 3 else (544.0 if z < 2.2 else 560.0)
        out.append({"t": round(t, 3), "x": x, "y": y, "zoom": z, **({"ease": "inout"} if i else {})})
    return out


def per(x, turn=0.3, y=930, depth=1.0, acts=()):
    return {"start": {"x": x, "y": y, "turn": turn, "expr": "happy", "z": 3, "depth": depth}, "exposure": 1,
            "actions": [dict(a) for a in acts]}


def A(do, t, dur, **kw):
    return {"do": do, "t": round(t, 3), "dur": round(dur, 3), **kw}


def robo(x=1130.0, y=930, depth=0.9, keys=(), lado=-1.0):
    return {"start": {"x": x, "y": y, "z": 3, "depth": depth, "lado": lado}, "exposure": 1, "keys": list(keys)}


def k(t, ease=None, **pose):
    d = {"t": round(max(0.0, t), 3), "pose": pose}
    if ease:
        d["ease"] = ease
    return d


def danca(t0, t1, f0=0.0):
    return [k(t0, "step", danca=round(f0, 3)), k(t1, "linear", danca=round(f0 + (t1 - t0) * RITMO, 3))]


def trava(t):
    return [k(t - 0.05, trava=0.0), k(t + 0.08, "step", trava=1.0)]


def volta(t):
    return [k(t - 0.02, trava=1.0), k(t + 0.08, "step", trava=0.0), k(t + 0.1, pulo=0.0), k(t + 0.55, "linear", pulo=1.0)]


def main() -> None:
    e = json.loads(EP.read_text())
    sc = e["scenes"]
    assert len(sc) == 15, f"base do Short mudou ({len(sc)} planos) — refazer os tempos deste roteiro"
    ini = []
    t = 0.0
    for s in sc:
        ini.append(t)
        t += s["duration"]
    loc = lambda i, tg: round(tg - ini[i], 3)            # tempo da música (no Short) → tempo dentro do plano i
    D = [s["duration"] for s in sc]
    TRAVOU1, VOLTOU1, TRAVOU2, VOLTOU2, TCHAU, BIP = 4.84, 9.94, 15.34, 20.44, 35.09, 35.94

    P = {}
    # 1 "Robô dançarino!" — o Luisinho aperta o botão vermelho e o robô liga e começa a dançar
    P[0] = dict(cam=cam((0, CX, 1.808), (D[0], CX, 1.95)),
                chars={LU: per(880, 0.35, acts=[A("point", 0.3, 0.9), A("dance", 1.3, D[0] - 1.3, style="festa")])},
                props={"robo": robo(keys=[k(0, "step", luz=0.0, botao=0.0, murcha=0.5), k(0.75, "step", botao=1.0),
                                          k(0.8, luz=0.0, murcha=0.5), k(1.15, "back", luz=1.0, murcha=0.0)] + danca(1.2, D[0]))},
                sing=LU)
    # 2 "Bip, bop, travou!" — close no robô dançando… TRAVA (olhos de X, faísca)
    P[1] = dict(cam=cam((0, 1150, 2.2, 600), (D[1], 1150, 2.35, 600)), chars={},
                props={"robo": robo(1150, keys=danca(0, loc(1, TRAVOU1), 0.9) + trava(loc(1, TRAVOU1)))}, sing=None)
    # 3 "Robô dançarino!" — a Laurinha chega, leva um susto e IMITA a estátua do robô
    P[2] = dict(cam=cam((0, CX, 1.808), (D[2], CX, 1.808)),
                chars={LA: per(880, 0.35, acts=[A("shock_reaction", 0.1, 0.9), A("estatua", 1.1, D[2] - 1.15)])},
                props={"robo": robo(keys=[k(0, "step", trava=1.0)])}, sing=LA)
    # 4 "Bip, bop, voltou!" — o Luisinho dá um tapinha, o robô VOLTA com um pulinho e o Luisinho faz o ZUM
    tv = loc(3, VOLTOU1)
    P[3] = dict(cam=cam((0, CX, 1.808), (D[3], CX, 1.9)),
                chars={LU: per(880, 0.35, acts=[A("point", 0.2, 0.8), A("zum", tv + 0.15, min(1.3, D[3] - tv - 0.2))])},
                props={"robo": robo(keys=[k(0, "step", trava=1.0)] + volta(tv) + danca(tv + 0.6, D[3], 2.0))}, sing=LU)
    # 5 "Robô dançarino!" — a Laurinha e o robô dançam juntinhos (passo de robô)
    P[4] = dict(cam=cam((0, CX - 40, 1.808), (D[4], CX + 40, 1.808)),
                chars={LA: per(880, 0.35, acts=[A("dance", 0.0, D[4], style="marcha")])},
                props={"robo": robo(keys=danca(0, D[4], 3.0))}, sing=LA)
    # 6 "Bip, bop, travou!" — travou de novo… e o Luisinho trava JUNTO (estátua)
    tt = loc(5, TRAVOU2)
    P[5] = dict(cam=cam((0, CX, 1.808), (D[5], CX, 1.95)),
                chars={LU: per(880, 0.35, acts=[A("dance", 0.0, tt, style="cabeca"), A("estatua", tt + 0.05, D[5] - tt - 0.1)])},
                props={"robo": robo(keys=danca(0, tt, 5.0) + trava(tt))}, sing=LU)
    # 7 "Robô dançarino!" — close: travado, o robô gira a CABEÇA inteira e a luzinha pisca (graça)
    P[6] = dict(cam=cam((0, CX, 2.3, 600), (D[6], CX, 2.45, 600)), chars={},
                props={"robo": robo(CX, keys=[k(0, "step", trava=1.0, cabeca=0.0, luz=1.0), k(0.4, cabeca=0.0),
                                              k(1.6, "inout", cabeca=1.0), k(1.8, "step", luz=0.0), k(2.0, "step", luz=1.0),
                                              k(2.2, "step", luz=0.0), k(2.4, "step", luz=1.0)])}, sing=None)
    # 8 "Bip, bop, voltou!" — voltou! braço e perna de robô para cima e a Laurinha faz o ZUM
    tv = loc(7, VOLTOU2)
    P[7] = dict(cam=cam((0, CX, 1.808), (D[7], CX, 1.9)),
                chars={LA: per(880, 0.35, acts=[A("zum", max(0.1, tv - 0.1), min(1.4, D[7] - tv - 0.05))])},
                props={"robo": robo(keys=[k(0, "step", trava=1.0, braco=0.0, perna=0.0)] + volta(tv) +
                                    [k(tv + 0.6, braco=0.0, perna=0.0), k(tv + 1.0, "back", braco=1.0, perna=1.0)])}, sing=LA)
    # 9 "Gostou do robô?" — o Luisinho pergunta para a câmera; o robô acena com o braço
    P[8] = dict(cam=cam((0, CX, 2.2, 600), (D[8], CX, 2.4, 600)),            # close: pergunta olhando para a criança
                chars={LU: per(CX, 0.15, acts=[A("apontar_camera", 0.15, D[8] - 0.2)])}, props={}, sing=LU)
    # 10 "Dá um joinha!" — na oficina, a Laurinha faz o joinha e o JOINHA aparece acima da cabeça
    P[9] = dict(cam=cam((0, CX, 1.808), (D[9], CX, 1.808)),
                chars={LA: per(CX, 0.15, y=990, acts=[A("bacana", 0.2, D[9] - 0.25)])},
                props={"joinha": {"start": {"x": CX, "y": 330, "z": 4, "depth": 0.6}, "exposure": 1,
                                  "keys": [k(0, escala=0.0), k(0.4, "back", escala=1.0)]}}, fx=["estrelas"], sing=LA)
    # 11 "Chama o papai e a mamãe" — a mamãe entra na oficina acenando; o Luisinho aponta para ela
    P[10] = dict(cam=cam((0, CX, 1.808), (D[10], CX, 1.808)),
                 chars={LU: per(880, 0.3, acts=[A("point", 0.3, D[10] - 0.35)]),
                        "mamae": per(1380, -0.3, acts=[A("walk", 0.0, 0.8, to_x=1150), A("wave", 0.85, D[10] - 0.9)])},
                 props={}, sing=LU)
    # 12 "Pra se inscrever no canal!" — o robô aperta o botão vermelho do peito e o INSCREVA-SE aparece e é clicado
    P[11] = dict(cam=cam((0, CX, 1.808), (D[11], CX, 1.808)),
                 chars={LA: per(880, 0.3, y=960, acts=[A("point", 0.2, D[11] - 0.25)])},
                 props={"robo": robo(1150, 960, keys=[k(0, braco=0.0, botao=0.0), k(0.9, "out", braco=1.0),
                                                      k(1.45, "step", botao=1.0)]),
                        "botao": {"start": {"x": CX, "y": 300, "z": 4, "depth": 0.55}, "exposure": 1,
                                  "keys": [k(0, escala=0.0, aperta=0.0), k(0.4, "back", escala=1.0), k(1.5, "out", aperta=1.0),
                                           k(1.8, "in", aperta=0.0)]}}, fx=["coracoes"], sing=LA)
    # 13 "… canal! Zum, zum!" — o Luisinho faz o ZUM embaixo do botão (que fica apertadinho no "zum")
    tz = loc(12, 31.82)
    P[12] = dict(cam=cam((0, CX, 1.808), (D[12], CX, 1.9)),
                 chars={LU: per(CX, 0.15, y=990, acts=[A("point", 0.1, max(0.3, tz - 0.3)), A("zum", tz - 0.1, min(1.5, D[12] - tz))])},
                 props={"botao": {"start": {"x": CX, "y": 300, "z": 4, "depth": 0.55}, "exposure": 1,
                                  "keys": [k(0, aperta=0.0), k(tz, "out", aperta=1.0), k(tz + 0.3, "in", aperta=0.0),
                                           k(loc(12, 32.51), "out", aperta=1.0), k(loc(12, 32.51) + 0.3, "in", aperta=0.0)]}},
                 fx=["coracoes"], sing=LU)
    # 14 "Robô dançarino! Tchau! Bip!" — a Laurinha e o robô dão tchau; no "Bip!" o robô abre a boca
    tc, tb = loc(13, TCHAU), loc(13, BIP)
    P[13] = dict(cam=cam((0, CX, 1.808), (D[13], CX, 1.808)),
                 chars={LA: per(880, 0.3, acts=[A("dance", 0.0, max(0.5, tc - 0.1), style="festa"), A("wave", tc, D[13] - tc - 0.05)])},
                 props={"robo": robo(keys=danca(0, tc, 6.0) + [k(tc, braco=0.0), k(tc + 0.3, "out", braco=1.0), k(tc + 0.6, braco=0.6),
                                                               k(tb - 0.05, boca=0.0), k(tb + 0.1, "out", boca=1.0),
                                                               k(tb + 0.5, boca=0.0), k(tb + 0.6, braco=1.0)])}, sing=LA)
    # 15 (fim da música) — a pilha do robô ACABA: a cabeça cai devagar… e o Luisinho ri
    P[14] = dict(cam=cam((0, CX, 1.808), (D[14], CX + 15, 1.95)),
                 chars={LU: per(880, 0.35, acts=[A("dance", 0.0, 1.0, style="festa"), A("laugh", 1.4, D[14] - 1.45)])},
                 props={"robo": robo(keys=danca(0, 0.8, 7.0) + [k(0.8, pilha=1.0, murcha=0.0, luz=1.0), k(1.6, "inout", pilha=0.0),
                                                                k(2.3, "out", murcha=1.0, luz=0.0)])}, sing=None)

    for i, s in enumerate(sc):
        p = P[i]
        s["background"] = OF
        s.pop("panels", None)
        s.pop("layout", None)
        s["camera"] = {"keys": p["cam"], "beat": s.get("camera", {}).get("beat", {"pulse": 0.0, "bar_zoom": 0.04, "sway": 6, "bounce": 0})}
        s["characters"] = p["chars"]
        s["props"] = p["props"]
        s["fx"] = p.get("fx", [])
        if "botao" in p["props"] or "joinha" in p["props"]:
            s["callouts"] = []                             # texto por cima do joinha/botão (26/11)
        quem = p["sing"]
        s["sing"] = [{**x, "who": quem} for x in s.get("sing", [])] if quem else []
        if quem:
            if not s["sing"]:                              # plano sem voz da base: nada a sincronizar
                s["sing"] = []
    e["approval"]["storyboard"] = False
    EP.write_text(json.dumps(e, ensure_ascii=False, indent=2))
    print(f"{EP.relative_to(ROOT)}: {len(sc)} planos reescritos (roteiro próprio do Short)")


if __name__ == "__main__":
    main()
