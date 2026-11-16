"""Rascunho de clipe a partir das partes da música (ADR-0015, F5).

Entrada: `analise/song.json` com letra conhecida alinhada (`song analyze --musica`) + ficha da música.
Saída: `episode.json` (schema 1.1) para revisar no storyboard ANTES do render. É um ponto de partida: as regras abaixo
seguem a BIBLIA_VISUAL (cenário plano nos versos, fundos de dança nos refrões) e a BIBLIA_MUSICAL (gancho na tela,
bordão nos intervalos); o refinamento de cada plano é feito à mão no episode.json.

Regras
- Blocos: intro · verso · refrão (a virada entra no refrão) · intervalo (bordão + batucada) · ponte · final.
- Planos de ~4 s (3–6 s), cortados NA BATIDA e, quando possível, no começo de um verso.
- Troca de bloco = transição colorida (rodízio); dentro do bloco = corte seco; 1º plano do refrão com clarão.
- Versos: plano_parque, câmera passeando por lugares diferentes do parque, quem canta em destaque.
- Refrão e intervalo: fundos de dança (cores em rodízio), os dois dançando passos diferentes; 2º plano do refrão em tela dividida.
- Boca: quem canta a parte (coro = os dois).
"""
from __future__ import annotations

import json
from pathlib import Path

FPS = 30
PARQUE = "plano_parque"
# lugares do plano_parque (a lagoa ocupa x 2700–3480: ninguém pisa na água)
LUGARES = [{"nome": "casa", "cam": 1900, "la": 1640, "lu": 2160},
           {"nome": "árvores", "cam": 1150, "la": 900, "lu": 1400},
           {"nome": "beira da lagoa", "cam": 3100, "la": 2540, "lu": 3620},
           {"nome": "morro", "cam": 2350, "la": 2120, "lu": 2580},
           {"nome": "flores", "cam": 3500, "la": 3640, "lu": 4060}]
DANCA = ["danca_raios_rosa", "danca_bolinhas_amarelo", "danca_ondas_azul", "danca_xadrez_verde", "danca_raios_laranja",
         "danca_bolinhas_rosa", "danca_xadrez_azul", "danca_ondas_rosa", "danca_raios_roxo", "danca_xadrez_vermelho",
         "danca_ondas_verde"]
PASSOS = [("palmas", "pulinho"), ("bracos", "lado"), ("gingado", "passinho"), ("twist", "palmas"), ("lado", "bracos"),
          ("pulinho", "gingado"), ("passinho", "twist"), ("marcha", "balanco")]
TRANS = ["deslizar_esq", "circulo", "cortina", "deslizar_dir", "giro", "zoom", "deslizar_cima"]
CORES = ["amarelo", "rosa", "azul", "verde", "laranja"]
BEAT_CAM = {"pulse": 0.0, "bar_zoom": 0.04, "sway": 6, "bounce": 0}   # sem "mola" (pedido do usuário)
CAST = {"laurinha": "laurinha", "luisinho": "luisinho"}
GROUND = 930


def _snap(t: float, beats: list[float]) -> float:
    return min(beats, key=lambda b: abs(b - t)) if beats else t


def _q(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


def blocos(song: dict) -> list[dict]:
    """Funde as partes da letra em blocos visuais contínuos que cobrem a música inteira."""
    secs = [s for s in song["sections"] if s["tipo"] != "fim"]
    out: list[dict] = []
    for s in secs:
        tipo = s["tipo"]
        if tipo == "virada":
            continue                                   # a virada abre o refrão seguinte
        if tipo == "bordao":
            tipo = "intervalo"
        if tipo == "intervalo" and out and out[-1]["tipo"] == "intervalo":
            out[-1]["cantam"] = sorted(set(out[-1]["cantam"]) | set(s["cantam"]))
            out[-1]["tags"].append(s["tag"])
            continue
        out.append({"tipo": tipo, "s": s["s"], "cantam": list(s["cantam"]), "tags": [s["tag"]]})
    out[0]["s"] = 0.0
    beats = song.get("beats", [])
    for b in out[1:]:
        b["s"] = _snap(b["s"] - 0.15, beats)           # o corte chega um tiquinho antes da voz, na batida
    dur = song["duration"]
    for a, b in zip(out, out[1:] + [None]):
        a["e"] = b["s"] if b else dur
    return [b for b in out if b["e"] - b["s"] > 0.5]


def planos(b: dict, lines: list[dict], beats: list[float], alvo: float = 4.0) -> list[tuple[float, float]]:
    """Divide um bloco em planos de ~4 s, cortando na batida mais próxima do começo de um verso."""
    s, e = b["s"], b["e"]
    n = max(1, round((e - s) / alvo))
    if n == 1:
        return [(s, e)]
    starts = [l["s"] for l in lines if s + 2.5 < l["s"] < e - 2.5]
    cuts = []
    for k in range(1, n):
        ideal = s + k * (e - s) / n
        cand = min(starts, key=lambda t: abs(t - ideal)) if starts else ideal
        if abs(cand - ideal) > 1.5:
            cand = ideal
        c = _snap(cand - 0.1, beats)
        if (not cuts and c - s >= 2.5) or (cuts and c - cuts[-1] >= 2.5):
            if e - c >= 2.5:
                cuts.append(c)
    edges = [s] + cuts + [e]
    return list(zip(edges, edges[1:]))


def _sing(lines, t0, t1, quem_bloco, who):
    out = []
    for l in lines:
        if l["e"] <= t0 or l["s"] >= t1:
            continue
        quem = l.get("_cantam") or quem_bloco
        if who in quem or "coro" in quem or not quem:
            out.append({"who": who, "from": round(max(0.0, l["s"] - t0), 3), "to": round(min(t1, l["e"]) - t0, 3)})
    dur = round(t1 - t0, 4)
    out = [dict(s, to=round(min(s["to"], dur - 0.01), 3)) for s in out]
    out = [s for s in out if s["to"] - s["from"] >= 0.1]
    merged = []
    for s in out:                                         # junta trechos colados (boca não fecha entre versos rápidos)
        if merged and s["from"] - merged[-1]["to"] < 0.35:
            merged[-1]["to"] = s["to"]
        else:
            merged.append(s)
    return merged


def _clamp_x(x: float, zoom: float, largura: float = 4400, margem: float = 40) -> float:
    """Câmera nunca mostra além da borda do cenário (o validador recusa)."""
    meia = 960 / max(1.0, zoom) + margem
    return max(meia, min(largura - meia, x))


def _cam(x, y, z0, z1, dur, largura: float | None = None):
    if largura:
        x = _clamp_x(x, min(z0, z1), largura)
    return {"keys": [{"t": 0, "x": x, "y": y, "zoom": z0}, {"t": round(dur, 3), "x": x, "y": y, "zoom": z1, "ease": "inout"}],
            "beat": dict(BEAT_CAM)}


def rascunho(project_dir: Path, musica: Path, titulo: str | None = None) -> dict:
    from ..audio import composer
    song = json.loads((project_dir / "analise" / "song.json").read_text(encoding="utf-8"))
    if not song.get("sections"):
        raise ValueError("song.json sem partes: rode `toonstudio song analyze <projeto> --musica <música>`")
    f = composer.ficha(musica)
    beats = song["beats"]
    secs = song["sections"]
    lines = [dict(l, _cantam=secs[l["secao"]]["cantam"]) for l in song["lines"]]
    gancho = f.get("gancho", "").upper().rstrip("!") + "!"
    bordoes = {v["bordao"] for v in composer.vozes()["vozes"].values() if v.get("bordao")}
    scenes, n_ref, n_dan, n_par, n_tr = [], 0, 0, 0, 0
    for bi, b in enumerate(blocos(song)):
        shots = planos(b, lines, beats)
        if b["tipo"] == "refrao":
            n_ref += 1
        for k, (t0, t1) in enumerate(shots):
            t0q, t1q = _q(t0), _q(t1)
            dur = round(t1q - t0q, 4)
            sid = f"s{len(scenes) + 1:02d}_{b['tipo']}"
            sc: dict = {"id": sid, "title": f"{b['tipo']} {k + 1}/{len(shots)} ({t0q:.1f}–{t1q:.1f}s)", "duration": dur}
            if k == 0 and scenes:
                sc["transition_in"] = {"type": TRANS[n_tr % len(TRANS)], "dur": 0.4}
                n_tr += 1
            seg_lines = [l for l in lines if l["e"] > t0q and l["s"] < t1q]
            sc["description"] = " / ".join(l["text"] for l in seg_lines)[:300]
            sing = {w: _sing(lines, t0q, t1q, b["cantam"], w) for w in CAST}
            tipo = b["tipo"]
            if tipo in ("refrao", "intervalo"):
                bg = DANCA[n_dan % len(DANCA)]
                n_dan += 1
                p_la, p_lu = PASSOS[(n_dan - 1) % len(PASSOS)]
                if tipo == "refrao" and k == 1 and dur >= 3.0:          # tela dividida no 2º plano do refrão
                    sc["layout"] = "diagonal" if n_ref % 2 else "vertical"
                    sc["panels"] = []
                    for who, passo, bgp, turn in (("laurinha", p_la, bg, 0.15), ("luisinho", p_lu, DANCA[n_dan % len(DANCA)], -0.15)):
                        sc["panels"].append({"background": bgp, "fx": ["estrelas" if who == "laurinha" else "notas"],
                                             "camera": {"keys": [{"t": 0, "x": 960, "y": 560, "zoom": 1.2}], "beat": dict(BEAT_CAM)},
                                             "sing": sing[who],
                                             "characters": {who: {"start": {"x": 960, "y": 1010, "turn": turn, "expr": "happy",
                                                                            "depth": 1.35, "z": 3}, "exposure": 1,
                                                                  "actions": [{"t": 0.0, "do": "dance", "style": passo, "dur": dur}]}}})
                    n_dan += 1
                    scenes.append(sc)
                    continue
                sc["background"] = bg
                sc["fx"] = ["confete" if tipo == "intervalo" else ["estrelas", "notas", "coracoes"][k % 3]]
                sc["camera"] = _cam(960, 560, 1.0, 1.08, dur)
                if tipo == "refrao" and k == 0:
                    sc["flash_in"] = True
                    sc["callouts"] = [{"t": 0.2, "text": gancho, "dur": 1.8, "color": CORES[n_ref % len(CORES)], "y": 170}]
                if tipo == "intervalo":
                    falas = [l for l in seg_lines if l["text"] in bordoes]
                    if falas:
                        sc["callouts"] = [{"t": round(max(0.0, falas[0]["s"] - t0q), 2), "text": falas[0]["text"].upper(),
                                           "dur": 1.6, "color": CORES[(bi + 2) % len(CORES)], "y": 170}]
                chars = {}
                for who, x, passo, turn in (("laurinha", 640, p_la, 0.25), ("luisinho", 1280, p_lu, -0.25)):
                    chars[who] = {"start": {"x": x, "y": 1010, "turn": turn, "expr": "happy", "depth": 1.3, "z": 3},
                                  "exposure": 1, "actions": [{"t": 0.0, "do": "dance", "style": passo, "dur": dur}]}
                sc["characters"] = chars
            else:                                                      # intro, verso, ponte, final: no parque
                zum_intro = tipo == "intro" and k > 0 and any(_q(l["s"]) < t1q and l["e"] > t0q and "zum" in l["text"].lower()
                                                               for l in seg_lines)
                if zum_intro:                                          # "(Zum, zum, zum!)" da abertura: festa colorida
                    bg = DANCA[n_dan % len(DANCA)]
                    n_dan += 1
                    sc.update({"background": bg, "fx": ["estrelas"], "flash_in": True,
                               "camera": _cam(960, 560, 1.0, 1.1, dur),
                               "callouts": [{"t": round(max(0.0, seg_lines[0]["s"] - t0q), 2), "text": "ZUM, ZUM, ZUM!",
                                             "dur": 1.6, "color": "amarelo", "y": 170}],
                               "characters": {w: {"start": {"x": x, "y": 1010, "turn": tn, "expr": "joy", "depth": 1.3, "z": 3},
                                                  "exposure": 1, "actions": [{"t": 0.0, "do": "dance", "style": "pulinho", "dur": dur}]}
                                              for w, x, tn in (("laurinha", 640, 0.25), ("luisinho", 1280, -0.25))}})
                    sing_scene = [s for w in CAST for s in sing[w]]
                    if sing_scene:
                        sc["sing"] = sing_scene
                    scenes.append(sc)
                    continue
                sc["background"] = PARQUE
                lugar = LUGARES[n_par % len(LUGARES)]
                n_par += 1
                canta = [w for w in CAST if sing[w]]
                foco = canta[0] if len(canta) == 1 else None
                outro = next((w for w in CAST if w != foco), None) if foco else None
                fx_ = {"intro": ["estrelas"], "final": ["coracoes"]}.get(tipo)
                if fx_:
                    sc["fx"] = fx_
                pos = {"laurinha": lugar["la"], "luisinho": lugar["lu"]}
                # enquadramento: rodízio close / dupla / voo (versos com um cantor só)
                modo = "dupla"
                if foco and tipo == "verso":
                    modo = ["close", "dupla", "voo", "close"][k % 4]
                elif tipo == "ponte":
                    modo = ["dupla", "close_la", "close_lu"][k % 3]
                if modo == "close_la":
                    modo, foco, outro = "close", "laurinha", "luisinho"
                elif modo == "close_lu":
                    modo, foco, outro = "close", "luisinho", "laurinha"
                if modo == "close":
                    camx, zoom = pos[foco], 1.5
                elif modo == "voo":
                    camx, zoom = (pos["laurinha"] + pos["luisinho"]) / 2, 1.0
                else:
                    camx, zoom = lugar["cam"], 1.12
                sc["camera"] = _cam(camx, 690 if modo == "close" else 540, zoom, zoom + 0.06, dur, largura=4400)
                chars = {}
                for who, turn in (("laurinha", 0.3), ("luisinho", -0.3)):
                    st = {"x": pos[who], "y": GROUND, "turn": turn, "expr": "happy", "z": 3 if who == foco else 2}
                    if tipo == "intro" and k == 0:                     # chegam voando de fora do quadro
                        st.update({"x": lugar["cam"] + (pos[who] - lugar["cam"]) * 5, "y": GROUND - 260})
                        acts = [{"t": 0.0, "do": "fly", "to_x": pos[who], "to_y": GROUND, "dur": min(2.6, dur - 0.4)}]
                    elif tipo == "final":
                        acts = [{"t": 0.0, "do": "wave", "dur": min(2.5, dur)}]
                        if dur > 3.2:
                            acts.append({"t": 2.6, "do": "fly", "to_x": pos[who] + (pos[who] - lugar["cam"]) * 4,
                                         "to_y": GROUND - 420, "dur": round(dur - 2.7, 3)})
                    elif modo == "voo" and who == foco:                # quem canta atravessa voando
                        alvo = pos[outro] + (-260 if pos[outro] > pos[foco] else 260)
                        st["y"] = GROUND - 120
                        acts = [{"t": 0.2, "do": "fly", "to_x": alvo, "to_y": GROUND, "dur": round(min(3.0, dur - 0.4), 3)}]
                    elif who == foco:
                        acts = [{"t": 0.0, "do": "dance", "style": ["balanco", "gingado", "passinho"][k % 3], "dur": dur}]
                    elif tipo == "ponte":
                        acts = [{"t": 0.0, "do": "dance", "style": "pulinho" if k % 2 else "balanco", "dur": dur}]
                    else:                                              # quem não canta reage
                        acts = [{"t": 0.3, "do": ["wave", "look_around", "laugh"][k % 3], "dur": round(min(1.8, dur - 0.3), 3)}]
                    chars[who] = {"start": st, "exposure": 1, "actions": acts}
                sc["characters"] = chars
            sing_scene = [s for w in CAST for s in sing[w]]
            if sing_scene:
                sc["sing"] = sing_scene
            scenes.append(sc)
    if scenes:
        scenes[-1]["transition_out"] = "fade"
    total = round(sum(s["duration"] for s in scenes), 4)
    ep = {"schema": "1.1", "id": project_dir.name, "title": titulo or f["titulo"],
          "logline": f"Clipe de \"{f['titulo']}\" — {f.get('tema', '')}. Rascunho gerado (clip_draft) para revisão.",
          "fps": FPS, "resolution": [1920, 1080], "background": PARQUE,
          "soundtrack": {"file": "musica/trabalho.wav", "analysis": "analise/song.json", "start": 0.0, "end": total,
                         "fade_out": 0.6, "beat_grid": "full"},
          "captions": {"lyrics": "analise/letra.json", "style": "palavra_a_palavra"},
          "overlays": {"logo": True, "channel": ["LAURINHA", "e Luisinho"]},
          "cast": {k: {"character": v} for k, v in CAST.items()},
          "approval": {"storyboard": False, "final_render": False},
          "scenes": scenes}
    return ep
