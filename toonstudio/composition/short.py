"""Short vertical (1080×1920) a partir de um clipe já roteirizado — sem refazer o roteiro.

1. Áudio: montagem de partes inteiras da música (cortes nos limites das partes, que já caem na batida), ex.:
   refrão → verso 1 → refrão (o Short abre no gancho: prende nos 2 primeiros segundos). Voz, batidas e letra são
   remontadas junto (boca e legenda continuam sincronizadas).
2. Imagem: os planos do clipe são reaproveitados e adaptados ao quadro vertical — zoom mínimo para cobrir a altura,
   câmera no personagem em foco, dançarinos aproximados, tela dividida vira plano único com os dois.
Sem vinheta (Short começa no refrão). Saída: projeto `<origem>-short`.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf

from ..core.config import PROJECTS, StudioError

W, H = 1080, 1920
GRAPHIC = ("danca_", "padrao_")


def _zoom_min(bg: str, meta: dict) -> float:
    h = 1240.0 if bg.startswith(GRAPHIC) else float(meta.get("height", 1080))
    return H / h + 0.03


def _verticaliza(sc: dict, bgw: dict) -> dict:
    """Adapta um plano 16:9 ao quadro vertical."""
    sc = copy.deepcopy(sc)
    if sc.get("panels"):                                   # tela dividida → os dois juntos num plano só
        p0, p1 = sc["panels"]
        chars = {**p0["characters"], **p1["characters"]}
        sc.pop("panels"); sc.pop("layout", None)
        sc["background"] = p0["background"]
        sc["fx"] = p0.get("fx", []) + [f for f in p1.get("fx", []) if f not in p0.get("fx", [])]
        sc["camera"] = p0["camera"]
        sc["characters"] = chars
        sing = p0.get("sing", []) + p1.get("sing", [])
        if sing:
            sc["sing"] = sing
    bg = sc["background"]
    graphic = bg.startswith(GRAPHIC)
    chars = sc.get("characters", {})
    if len(chars) >= 2 and (graphic or not sc.get("props")):   # sem objetos de cena: aproxima os dois
        xs = sorted(chars, key=lambda w: chars[w]["start"]["x"])
        n = len(xs)
        centro = 960 if graphic else sum(chars[w]["start"]["x"] for w in xs) / n
        for k, w in enumerate(xs):
            nx = centro + (k - (n - 1) / 2) * 320
            st = chars[w]["start"]
            if graphic and -400 < st["x"] < 2300 or not graphic:
                st["x"] = nx
            for a in chars[w].get("actions", []):
                if a.get("do") == "fly" and "to_x" in a:
                    a["to_x"] = nx
                    if not graphic and "to_y" in a:        # quadro vertical: não sobe até cortar a cabeça
                        a["to_y"] = max(float(a["to_y"]), 760.0)
    elif graphic and len(chars) == 1:
        for w in chars:
            chars[w]["start"]["x"] = 960 if -400 < chars[w]["start"]["x"] < 2300 else chars[w]["start"]["x"]
    zmin = _zoom_min(bg, bgw.get(bg, {}))
    width = 1920.0 if graphic else float(bgw.get(bg, {}).get("width", 1920))
    for k in sc["camera"]["keys"]:
        z = max(zmin, float(k["zoom"]) * 1.0)
        if not graphic and len(chars) >= 2 and not sc.get("props"):
            k["x"] = sum(c["start"]["x"] for c in chars.values()) / len(chars)
        elif not graphic and chars:                        # câmera no personagem em foco (quem canta ou o 1º)
            foco = None
            for s in sc.get("sing", []):
                foco = s["who"]
                break
            foco = foco if foco in chars else next(iter(chars))
            k["x"] = chars[foco]["start"]["x"]
            props = sc.get("props", {})
            if props:                                      # objeto de cena perto: enquadra os dois
                px = min(props.values(), key=lambda p: abs(p["start"]["x"] - k["x"]))["start"]["x"]
                if abs(px - k["x"]) < 420:
                    k["x"] = (px + k["x"]) / 2
        half_w, half_h = W / 2 / z, H / 2 / z
        if graphic:
            k["x"] = 960
            k["y"] = 620
        else:
            k["x"] = max(half_w + 5, min(width - half_w - 5, k["x"]))
            k["y"] = max(half_h + 5, min(1080 - half_h - 5, k.get("y", 540)))
        k["zoom"] = math.ceil(z * 1000) / 1000           # arredonda PARA CIMA: nunca abaixo do mínimo
    return sc


def _monta_audio(src: Path, trechos: list[tuple[float, float]], out: Path, fade: float = 0.03) -> None:
    a, sr = sf.read(src, dtype="float32")
    pedacos = []
    n = int(fade * sr)
    for t0, t1 in trechos:
        x = a[int(round(t0 * sr)):int(round(t1 * sr))].copy()
        ramp = np.linspace(0, 1, n)
        if x.ndim > 1:
            ramp = ramp[:, None]
        x[:n] *= ramp
        x[-n:] *= ramp[::-1]
        pedacos.append(x)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, np.concatenate(pedacos), sr)


def criar_short(src_project: str, partes: list[list[str]]) -> Path:
    """partes: cada item é uma lista de blocos CONTÍGUOS (ex.: [["refrao#1"], ["verso#1", "refrao#1"]])."""
    from ..backgrounds import registry
    from .clip_draft import blocos
    sdir = PROJECTS / src_project
    ep = json.loads((sdir / "episode.json").read_text(encoding="utf-8"))
    song = json.loads((sdir / "analise" / "song.json").read_text(encoding="utf-8"))
    letra = json.loads((sdir / "analise" / "letra.json").read_text(encoding="utf-8"))
    bl, occ = [], {}
    for b in blocos(song):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        bl.append({**b, "nome": f"{b['tipo']}#{occ[b['tipo']]}"})
    por_nome = {b["nome"]: b for b in bl}
    trechos = []
    for grupo in partes:
        try:
            trechos.append((por_nome[grupo[0]]["s"], por_nome[grupo[-1]]["e"]))
        except KeyError as e:
            raise StudioError(f"parte {e} não existe; partes: {list(por_nome)}")
    # planos do clipe dentro de cada trecho (os limites dos planos coincidem com os das partes)
    t, faixas = 0.0, []
    for s in ep["scenes"]:
        faixas.append((t, t + s["duration"], s))
        t += s["duration"]
    bgw = {}
    novas, tl, mapa = [], 0.0, []                          # mapa: (t0 origem, t1 origem, t0 no short)
    exatos = []
    for (t0, t1) in trechos:
        tol = 0.05                                         # planos começam em quadros inteiros (1/30 s)
        sel_f = [(a, b, s) for a, b, s in faixas if a >= t0 - tol and b <= t1 + tol]
        if not sel_f or abs(sel_f[0][0] - t0) > tol or abs(sel_f[-1][1] - t1) > tol:
            raise StudioError(f"os planos não coincidem com o trecho {t0:.2f}–{t1:.2f}s")
        t0, t1 = sel_f[0][0], sel_f[-1][1]                 # tempos EXATOS dos planos: áudio e imagem alinhados
        exatos.append((t0, t1))
        sel = [s for _, _, s in sel_f]
        mapa.append((t0, t1, tl))
        for k, s in enumerate(sel):
            for u in [s, *s.get("panels", [])]:
                b = u.get("background")
                if b and b not in bgw:
                    bgw[b] = registry.ensure(b)
            v = _verticaliza(s, bgw)
            v["id"] = f"s{len(novas) + 1:02d}" + v["id"][3:]
            if not novas:
                v.pop("transition_in", None)
                v["flash_in"] = True
            elif k == 0:
                v["transition_in"] = {"type": "zoom", "dur": 0.4}
            novas.append(v)
        tl += t1 - t0
    did = f"{src_project}-short"
    ddir = PROJECTS / did
    (ddir / "musica").mkdir(parents=True, exist_ok=True)
    (ddir / "analise").mkdir(parents=True, exist_ok=True)
    trechos = exatos
    _monta_audio(Path(song["files"]["work"]), trechos, ddir / "musica" / "trabalho.wav")
    _monta_audio(Path(song["files"]["vocals"]), trechos, ddir / "analise" / "vocals.wav")

    def remap(t: float) -> float | None:
        for a, b, d in mapa:
            if a - 1e-3 <= t < b + 1e-3:
                return round(t - a + d, 3)
        return None
    beats = [x for x in (remap(b) for b in song["beats"]) if x is not None]
    beats = sorted(set(beats))
    linhas = []
    for a, b, d in mapa:
        for l in letra["lines"]:
            if a - 0.05 <= l["s"] < b - 0.05:
                linhas.append({**l, "s": round(l["s"] - a + d, 3), "e": round(min(l["e"], b) - a + d, 3),
                               "words": [{**w, "s": round(w["s"] - a + d, 3), "e": round(min(w["e"], b) - a + d, 3)}
                                         for w in l["words"]]})
    total = round(sum(s["duration"] for s in novas), 4)
    song2 = {"schema": "song-1.0", "files": {"work": str(ddir / "musica" / "trabalho.wav"),
                                              "vocals": str(ddir / "analise" / "vocals.wav")},
             "bpm": song["bpm"], "beats": beats, "downbeat_phase": song.get("downbeat_phase", 0), "duration": total,
             "lines": [{k: v for k, v in l.items() if k != "words"} for l in linhas], "sections": [],
             "words": [w for l in linhas for w in l["words"]],                      # boca cantada (Rhubarb) por trecho
             "notes": f"montagem do Short a partir de {src_project}: " + ", ".join(f"{a:.2f}–{b:.2f}s" for a, b in trechos)}
    (ddir / "analise" / "song.json").write_text(json.dumps(song2, ensure_ascii=False, indent=1), encoding="utf-8")
    (ddir / "analise" / "letra.json").write_text(json.dumps({"source": letra.get("source"), "lines": linhas},
                                                            ensure_ascii=False, indent=1), encoding="utf-8")
    ep2 = {**{k: v for k, v in ep.items() if k not in ("scenes",)}, "id": did, "title": ep["title"] + " — Short",
           "resolution": [W, H], "scenes": novas,
           "soundtrack": {**ep["soundtrack"], "start": 0.0, "end": total, "fade_out": 0.3},
           "approval": {"storyboard": False, "final_render": False}}
    (ddir / "episode.json").write_text(json.dumps(ep2, ensure_ascii=False, indent=2), encoding="utf-8")
    return ddir
