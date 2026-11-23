"""Montagem do clipe a partir das partes da música e do ROTEIRO verso a verso (ADR-0015/0016).

PADRAO_DE_QUALIDADE.md: nada de rascunho — sem roteiro completo, a montagem é recusada. O gerador genérico abaixo só
existe para testes internos (`permitir_generico=True`) e nunca é usado para entregar clipe.

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
from functools import lru_cache

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


def rascunho(project_dir: Path, musica: Path, titulo: str | None = None, permitir_generico: bool = False) -> dict:
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
    rot_p = musica / "roteiro.json"
    rot_full = json.loads(rot_p.read_text(encoding="utf-8")) if rot_p.exists() else {}
    roteiro = rot_full.get("partes", {})
    global ESCALA
    ESCALA = float(rot_full.get("escala_personagens", 1.0))   # 19/11: personagens maiores na tela (referência ~85 % da altura)
    if not permitir_generico:                 # PADRAO_DE_QUALIDADE.md: nada de rascunho — roteiro completo, verso a verso
        cont: dict = {}
        faltam = []
        for b in blocos(song):
            cont[b["tipo"]] = cont.get(b["tipo"], 0) + 1
            if not (roteiro.get(f"{b['tipo']}#{cont[b['tipo']]}") or roteiro.get(b["tipo"])):
                faltam.append(f"{b['tipo']}#{cont[b['tipo']]} ({b['s']:.1f}–{b['e']:.1f}s)")
        if faltam:
            raise ValueError(f"roteiro incompleto em {rot_p}: faltam as partes {', '.join(faltam)} "
                             "(padrão de qualidade: todo verso precisa de cena própria)")
    cast_extra: dict = {}
    occ: dict = {}
    for bi, b in enumerate(blocos(song)):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        spec = roteiro.get(f"{b['tipo']}#{occ[b['tipo']]}") or roteiro.get(b["tipo"])
        if spec:
            scenes += roteiro_bloco(b, spec, occ[b["tipo"]], lines, beats, cast_extra, len(scenes) + 1)
            continue
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
    from ..core.config import PROJECTS as _PJ
    ep = {"schema": "1.1", "id": project_dir.name, "projeto": str(project_dir.relative_to(_PJ)) if project_dir.is_relative_to(_PJ) else project_dir.name,
          "title": titulo or f["titulo"],
          "logline": f"Clipe de \"{f['titulo']}\" — {f.get('tema', '')}. Montado do roteiro verso a verso (roteiro.json).",
          "fps": FPS, "resolution": [1920, 1080], "background": PARQUE,
          "soundtrack": {"file": "musica/trabalho.wav", "analysis": "analise/song.json", "start": 0.0, "end": total,
                         "fade_out": 0.6, "beat_grid": "full"},
          "captions": {"lyrics": "analise/letra.json", "style": "palavra_a_palavra"},
          "overlays": _overlays_do_canal(project_dir),
          "cast": {**{k: {"character": v} for k, v in CAST.items()}, **cast_extra},
          "approval": {"storyboard": False, "final_render": False},
          "scenes": scenes}
    return ep


# ───────────────────────── roteiro verso a verso (ADR-0016) ─────────────────────────
# musicas/<música>/roteiro.json:
# {"partes": {"intro": [plano…], "verso#1": [...], "refrao": [...], "intervalo#2": [...], ...}}
# Chave = tipo do bloco + "#n" (ocorrência) ou só o tipo (vale para todas as ocorrências, ex.: o refrão = mesma coreografia).
# plano = {"linhas": 1, "seg": s (planos sem verso), "cenario": id | [id por ocorrência], "camera": "aberto"|"medio:ator"|
#          "close:ator"|{x,y,zoom,zoom_fim}, "atores": {nome: {x,y,turn,expr,depth,z,segura,mochila,bigode,acoes:[…],keys:[…]}},
#          "objetos": {nome: {id?, x,y,z, pose:{…}, keys:[{t,pose}]}}, "fx": [...], "callout": "TEXTO" | [{t,text,…}],
#          "flash": bool, "tremor": [t…] (a tela treme), "sons": [{t, id, vol}] (efeito sonoro; vol em dB, 0 = nível padrão), "escurece": [a0, a1] (luz baixando), "transicao": tipo, "cantam": [...], "tela_dividida": {"layout", "paineis": [sub-plano, sub-plano]}}
# Atuação: "dur": "resto" vai até o fim do plano. O canto (boca) vem da letra: quem canta a parte e está no plano.
def _overlays_do_canal(project_dir: Path) -> dict:
    """Logo do canto do vídeo: o do canal do projeto (multicanal, 20/11/2026)."""
    from ..core.canal import usar_do_projeto
    cn = usar_do_projeto(project_dir)
    ov = {"logo": True, "channel": list(cn.logo_texto)}
    if cn.logo_png and cn.logo_png.exists():
        ov["logo_png"] = str(cn.logo_png)
    return ov


GRAPHIC = ("danca_", "padrao_", "mon_raios_", "mon_xadrez_", "mon_brilho_")
ESCALA = 1.0            # multiplica o tamanho (depth) de atores e objetos do roteiro; "escala_personagens" no roteiro.json
NAO_ESCALA = {"joinha", "botao_inscrever", "logo", "numero"}      # peças de interface: tamanho fixo
SING_CAST = ("laurinha", "luisinho")


def _bg_width(bg: str) -> float:
    if bg.startswith(GRAPHIC):
        return 1920.0
    from ..backgrounds import registry
    return float(registry.ensure(bg)["width"])


def _camera(spec, bg: str, atores: dict, dur: float) -> dict:
    graphic = bg.startswith(GRAPHIC)
    w = _bg_width(bg)
    if isinstance(spec, dict):
        x, y, z0 = spec.get("x", w / 2), spec.get("y", 540), spec.get("zoom", 1.0)
        z1 = spec.get("zoom_fim", z0 + 0.05)
    else:
        spec = spec or "aberto"
        kind, _, who = spec.partition(":")
        if graphic:
            x, y = 960, 560
        else:
            x, y = w / 2, 540
        z0 = 1.0
        if who and who in atores:
            a = atores[who]
            x = a.get("x", x)
            base_y = a.get("y", 1010 if graphic else GROUND)
            if kind == "medio":                              # personagem maior (ESCALA) → menos zoom para o mesmo enquadramento
                y, z0 = base_y - 330 * ESCALA, max(1.0, 1.3 / ESCALA)
            elif kind == "close":
                y, z0 = base_y - 380 * ESCALA, max(1.15, 1.75 / ESCALA)
        z1 = z0 + 0.06
    if graphic:
        x = 960 if abs(x - 960) < 1 else x
    else:
        x = _clamp_x(x, min(z0, z1), w)
        half_h = 540 / max(1.0, min(z0, z1))
        y = max(half_h, min(1080 - half_h, y))
    xf, yf = x, y
    if isinstance(spec, dict) and (spec.get("x_fim") is not None or spec.get("y_fim") is not None):
        xf = spec["x_fim"] if spec.get("x_fim") is not None else x
        yf = spec["y_fim"] if spec.get("y_fim") is not None else y
        if not graphic:
            xf = _clamp_x(xf, min(z0, z1), w)
            half_h = 540 / max(1.0, min(z0, z1))
            yf = max(half_h, min(1080 - half_h, yf))
    if _protege_topo():
        y, yf = _sem_cortar_topo(y, x, z0, z1, atores, graphic), _sem_cortar_topo(yf, xf, z0, z1, atores, graphic)
    return {"keys": [{"t": 0, "x": round(x, 1), "y": round(y, 1), "zoom": z0},
                     {"t": round(dur, 3), "x": round(xf, 1), "y": round(yf, 1), "zoom": z1, "ease": "inout"}],
            "beat": dict(BEAT_CAM)}


def _performance(a: dict, dur: float, graphic: bool) -> dict:
    from ..animation.acting import HOLD_SIDE
    st = {"x": a.get("x", 960), "y": a.get("y", 1010 if graphic else GROUND), "turn": a.get("turn", 0.15),
          "expr": a.get("expr", "happy"), "z": a.get("z", 3)}
    if graphic or "depth" in a or ESCALA != 1.0:
        st["depth"] = round(a.get("depth", 1.3 if graphic else 1.0) * ESCALA, 3)
    for k in ("mochila", "bigode", "fly", "dangle"):
        if k in a:
            st[k] = a[k]
    if a.get("segura"):
        st.update({"holding": a["segura"], **HOLD_SIDE})
    if a.get("segura_f"):                                    # 19/11: objeto também na mão de trás (2ª baqueta)
        st["holding_f"] = a["segura_f"]
    if a.get("pose"):
        st.update(a["pose"])
    acts = []
    for ac in a.get("acoes", []):
        ac = dict(ac)
        ac.setdefault("t", 0.0)
        if ac.get("dur") == "resto":
            ac["dur"] = round(max(0.3, dur - ac["t"]), 3)
        acts.append(ac)
    perf = {"start": st, "exposure": 1, "actions": acts}
    if a.get("keys"):
        perf["keys"] = a["keys"]
    return perf


def _protege_topo() -> bool:
    from ..core.canal import atual
    return bool(atual().raw.get("camera_protege_topo"))


@lru_cache(maxsize=None)
def _altura(cid: str) -> float:
    """Altura real do personagem acima do pé (chifre, antena, olho na haste…), em unidades, medida no desenho."""
    import numpy as np
    from ..core.registry import character
    from ..render.pipeline import LEVEL_ANCHOR, LEVEL_CANVAS
    s = character(cid).render({}, scale=0.5, canvas=LEVEL_CANVAS, anchor=LEVEL_ANCHOR)
    ys = np.nonzero(np.asarray(s.makeImageSnapshot().toarray())[..., 3] > 10)[0]
    return (LEVEL_ANCHOR[1] - ys.min() / 0.5) if len(ys) else 500.0


def _sem_cortar_topo(y: float, x: float, z0: float, z1: float, atores: dict, graphic: bool, margem: float = 28) -> float:
    """Câmera sobe o necessário para nenhum chifre/antena/olho de quem está no quadro sair por cima (20/11, pedido do
    usuário: closes cortavam os chifres). Considera o zoom máximo do plano + o 'perto/longe' da batida."""
    z = max(z0, z1) * (1 + BEAT_CAM.get("bar_zoom", 0.0)) * (1 + BEAT_CAM.get("pulse", 0.0))
    topo = None
    for who, a in atores.items():
        if abs(a.get("x", 960) - x) > 960 / z + 250:
            continue
        try:
            h = _altura(who)
        except Exception:
            continue
        d = a.get("depth", 1.3 if graphic else 1.0) * ESCALA
        acoes = {ac.get("do") for ac in a.get("acoes", [])}
        extra = 95 if acoes & {"jump", "pulinho", "shock_reaction"} else (45 if "rawr" in acoes else 0)   # pulo / esticão do RAWR
        t = a.get("y", 1010 if graphic else GROUND) - (h + extra) * d - margem
        topo = t if topo is None else min(topo, t)
    if topo is None:
        return y
    return max(540 / max(1.0, min(z0, z1)), min(y, topo + 540 / z))       # nunca acima do topo do cenário (zoom mínimo)


def _props_sem_contorno() -> bool:
    from ..core.canal import atual
    return bool(atual().raw.get("props_sem_contorno"))


def _objetos(objs: dict, cast: dict, dur: float | None = None) -> dict:
    out = {}
    for name, o in (objs or {}).items():
        cid = o.get("id", name)
        cast[name] = {"character": cid}
        st = {"x": o.get("x", 960), "y": o.get("y", GROUND), "z": o.get("z", 1), **o.get("pose", {})}
        if _props_sem_contorno():                             # multicanal: Fofolucos = chapado SEM contorno também nos objetos
            st["sem_contorno"] = 1.0
        if "depth" in o or (ESCALA != 1.0 and cid not in NAO_ESCALA):
            st["depth"] = round(o.get("depth", 1.0) * (1.0 if cid in NAO_ESCALA else ESCALA), 3)
        perf = {"start": st, "exposure": 1}
        if o.get("keys"):
            perf["keys"] = o["keys"]
        if o.get("acoes"):                                    # A4: o objeto também "dança" na grade de batidas (bateria_show)
            perf["actions"] = [{**ac, "dur": round(max(0.1, dur - ac.get("t", 0.0)), 3) if ac.get("dur") == "resto" and dur
                                else ac.get("dur", 1.0)} for ac in o["acoes"]]
        out[name] = perf
    return out


def _aproximar(p: dict, bg: str) -> dict:
    """Personagens maiores (ESCALA) ocupam mais tela: quem estava na ponta sairia cortado. Aproxima atores e objetos do
    centro da câmera na mesma proporção (posições, destinos de ação e chaves de x); fora de cena continua fora."""
    import copy
    p = copy.deepcopy(p)
    cam = p.get("camera")
    cx = cam.get("x", _bg_width(bg) / 2) if isinstance(cam, dict) else _bg_width(bg) / 2
    f = 1.0 / ESCALA ** 0.9

    def ap(x):
        return round(cx + (float(x) - cx) * f, 1)

    for a in (p.get("atores") or {}).values():
        if "x" in a:
            a["x"] = ap(a["x"])
        for k in a.get("keys", []):                         # 21/11: ator que anda por chaves (motorista do carrinho)
            if "x" in k.get("pose", {}):                    # acompanha o objeto, que já era aproximado
                k["pose"]["x"] = ap(k["pose"]["x"])
        for ac in a.get("acoes", []):
            for k in ("to_x", "wall_x"):
                if k in ac:
                    ac[k] = ap(ac[k])
    for o in (p.get("objetos") or {}).values():
        if o.get("id", "") in NAO_ESCALA:
            continue
        if "x" in o:
            o["x"] = ap(o["x"])
        for k in o.get("keys", []):
            if "x" in k.get("pose", {}):
                k["pose"]["x"] = ap(k["pose"]["x"])
    if isinstance(cam, str) and ":" in cam:                    # close/médio seguem o ator (já aproximado)
        pass
    return p


def _plano_scene(p: dict, occ: int, dur: float, plines: list, t0: float, cantam_bloco: list, cast: dict, sid: str) -> dict:
    bg = p.get("cenario", PARQUE)
    if isinstance(bg, list):
        bg = bg[(occ - 1) % len(bg)]
    graphic = bg.startswith(GRAPHIC)
    if ESCALA > 1.0 and not graphic:
        p = _aproximar(p, bg)
    sc: dict = {"id": sid, "title": (plines[0]["text"] if plines else p.get("titulo", "instrumental"))[:60], "duration": dur,
                "description": " / ".join(l["text"] for l in plines)[:300]}
    if p.get("tela_dividida"):
        td = p["tela_dividida"]
        sc["layout"] = td.get("layout", "diagonal")
        sc["panels"] = []
        for sub in td["paineis"]:
            sub_bg = sub.get("cenario", bg)
            if isinstance(sub_bg, list):
                sub_bg = sub_bg[(occ - 1) % len(sub_bg)]
            g2 = sub_bg.startswith(GRAPHIC)
            atores = sub.get("atores", {})
            for w in atores:
                cast.setdefault(w, {"character": w})
            panel = {"background": sub_bg, "camera": _camera(sub.get("camera"), sub_bg, atores, dur),
                     "characters": {w: _performance(a, dur, g2) for w, a in atores.items()}}
            if sub.get("fx"):
                panel["fx"] = sub["fx"]
            props = _objetos(sub.get("objetos"), cast, dur)       # 20/11: objetos também em cada metade da tela
            if props:
                panel["props"] = props
            sing = [s for w in atores for s in _sing(plines, t0, t0 + dur, p.get("cantam") or cantam_bloco, w) if w in SING_CAST]
            if sing:
                panel["sing"] = sing
            sc["panels"].append(panel)
        return sc
    atores = p.get("atores", {})
    for w in atores:
        cast.setdefault(w, {"character": w})
    sc["background"] = bg
    sc["camera"] = _camera(p.get("camera"), bg, atores, dur)
    if p.get("tremor"):                                       # 19/11: a tela treme (pisada do Dino) — shake nativo do render
        sc["camera"]["shake"] = [{"t": round(float(t), 3), "dur": 0.35, "amp": 14.0} for t in p["tremor"] if 0 <= float(t) < dur - 0.1]
    sc["characters"] = {w: _performance(a, dur, graphic) for w, a in atores.items()}
    props = _objetos(p.get("objetos"), cast, dur)
    if props:
        sc["props"] = props
    if p.get("fx"):
        sc["fx"] = p["fx"]
    if p.get("flash"):
        sc["flash_in"] = True
    if p.get("sons"):                                       # efeitos sonoros: entram na montagem final (marca.final)
        sc["sfx"] = [{"t": round(min(max(0.0, float(x.get("t", 0.0))), max(0.0, dur - 0.05)), 3), "id": x["id"],
                      "volume_db": float(x.get("vol", 0.0))} for x in p["sons"]]
    if p.get("escurece"):                                   # [opacidade no início, no fim] do véu escuro (noite)
        sc["escurece"] = [round(float(v), 3) for v in p["escurece"]]
    co = p.get("callout")
    if co:
        if isinstance(co, str):
            co = [{"t": 0.2, "text": co}]
        # o destaque nunca passa do fim do próprio plano (senão encavala com o do plano seguinte)
        sc["callouts"] = [{"t": c.get("t", 0.2), "text": c["text"], "dur": round(min(c.get("dur", 1.8), max(0.6, dur - c.get("t", 0.2))), 3),
                           "color": c.get("color", CORES[len(c["text"]) % len(CORES)]), "y": c.get("y", 170)} for c in co]
        # nem encavala com o PRÓXIMO destaque do mesmo plano (21/11, Fofolucos 02: "M FOFINHO! O!", "FOF TCHAU! OS!")
        cs = sorted(sc["callouts"], key=lambda c: c["t"])
        for a, b in zip(cs, cs[1:]):
            if a.get("y") == b.get("y"):
                a["dur"] = round(max(0.3, min(a["dur"], b["t"] - a["t"] - 0.05)), 3)
        sc["callouts"] = cs
    sing = [s for w in atores if w in SING_CAST for s in _sing(plines, t0, t0 + dur, p.get("cantam") or cantam_bloco, w)]
    if sing:
        sc["sing"] = sing
    return sc


def roteiro_bloco(b: dict, planos_spec: list, occ: int, lines: list, beats: list, cast: dict, first_sid: int) -> list[dict]:
    """Planos de um bloco a partir do roteiro: cada plano consome N versos; corte na batida antes do 1º verso do plano."""
    blines = [l for l in lines if b["s"] - 0.05 <= l["s"] < b["e"] - 0.05]
    starts, li, t = [], 0, b["s"]
    for k, p in enumerate(planos_spec):
        n = int(p.get("linhas", 1 if "seg" not in p else 0))
        if k == 0:
            st = b["s"]
        elif n > 0 and li < len(blines):
            st = _snap(blines[li]["s"] - 0.12, beats)
        else:
            st = t
        mine = blines[li:li + n] if n > 0 else []
        li += n
        starts.append((st, p, mine))
        t = st + float(p["seg"]) if "seg" in p else (mine[-1]["e"] if mine else st + 2.0)
    if li < len(blines) and starts:                         # versos que sobraram ficam no último plano
        st, p, mine = starts[-1]
        starts[-1] = (st, p, mine + blines[li:])
    kept: list = []                                       # plano curto demais: some e o anterior absorve versos e tempo
    for k, (st, p, mine) in enumerate(starts):
        en = starts[k + 1][0] if k + 1 < len(starts) else b["e"]
        if _q(en) - _q(st) < 0.6 and kept:
            kept[-1] = (kept[-1][0], kept[-1][1], kept[-1][2] + mine)
            continue
        kept.append((st, p, mine))
    scenes = []
    for k, (st, p, mine) in enumerate(kept):
        en = kept[k + 1][0] if k + 1 < len(kept) else b["e"]
        t0q, t1q = _q(st), _q(en)
        sid = f"s{first_sid + len(scenes):02d}_{b['tipo']}"
        sc = _plano_scene(p, occ, round(t1q - t0q, 4), mine, t0q, b["cantam"], cast, sid)
        if k == 0 and first_sid > 1:
            sc["transition_in"] = {"type": p.get("transicao", TRANS[(first_sid + occ) % len(TRANS)]), "dur": 0.4}
        elif p.get("transicao"):
            sc["transition_in"] = {"type": p["transicao"], "dur": 0.35}
        scenes.append(sc)
    return scenes
