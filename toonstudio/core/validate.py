"""Validação do episódio: estrutural (JSON Schema) + semântica (contra a biblioteca real) + continuidade espacial.

Erros bloqueiam o render; avisos vão para o relatório.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema

from ..animation.library import REGISTRY
from ..characters.base import EXPRESSIONS
from .config import LIBRARY, SCHEMAS
from .registry import CHARACTERS


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_background(bg_id: str) -> dict:
    p = LIBRARY / "backgrounds" / bg_id / "layers" / "background.json"
    if not p.exists():
        raise FileNotFoundError(f"cenário {bg_id} não construído: rode `toonstudio background {bg_id}`")
    return json.loads(p.read_text(encoding="utf-8"))


def sfx_ids() -> set[str]:
    from ..audio import sfx
    return set(sfx.CATALOG)


def validate(ep: dict) -> Report:
    r = Report()
    schema = json.loads((SCHEMAS / "episode.schema.json").read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    for e in sorted(v.iter_errors(ep), key=lambda e: list(e.path)):
        r.errors.append(f"schema: {'/'.join(map(str, e.path)) or '(raiz)'}: {e.message}")
    if r.errors:
        return r
    W, H = ep["resolution"]
    try:
        bg = load_background(ep["background"])
    except FileNotFoundError as e:
        r.errors.append(str(e))
        return r
    cast = ep["cast"]
    for name, c in cast.items():
        if c["character"] not in CHARACTERS:
            r.errors.append(f"elenco {name}: personagem {c['character']} não existe na biblioteca")
    known_sfx = sfx_ids()
    seen = set()
    for s in ep["scenes"]:
        sid, dur = s["id"], s["duration"]
        if sid in seen:
            r.errors.append(f"{sid}: id de cena repetido")
        seen.add(sid)
        perf = {**s.get("characters", {}), **s.get("props", {})}
        for who, p in perf.items():
            if who not in cast:
                r.errors.append(f"{sid}: '{who}' não está no elenco")
            for a in p.get("actions", []):
                if a["do"] not in REGISTRY:
                    r.errors.append(f"{sid}/{who}: ação '{a['do']}' não existe (biblioteca: {', '.join(sorted(REGISTRY))})")
                if a["t"] > dur:
                    r.errors.append(f"{sid}/{who}: ação '{a['do']}' começa em {a['t']}s, depois do fim da cena ({dur}s)")
                if a["do"] in ("walk", "sneak", "run") and "to_x" not in a:
                    r.errors.append(f"{sid}/{who}: '{a['do']}' exige to_x")
                if a["do"] == "fly" and cast.get(who, {}).get("character") != "tevico":
                    r.errors.append(f"{sid}/{who}: só personagens alados voam")
            for k in p.get("keys", []):
                if "expr" in k and k["expr"] not in EXPRESSIONS:
                    r.errors.append(f"{sid}/{who}: expressão '{k['expr']}' não existe ({', '.join(sorted(EXPRESSIONS))})")
                if k["t"] > dur + 1e-6:
                    r.warnings.append(f"{sid}/{who}: chave em {k['t']}s após o fim da cena")
            e0 = p.get("start", {}).get("expr")
            if e0 and e0 not in EXPRESSIONS:
                r.errors.append(f"{sid}/{who}: expressão inicial '{e0}' não existe")
        for d in s.get("dialog", []):
            if d["who"] not in s.get("characters", {}):
                r.errors.append(f"{sid}: fala de '{d['who']}', que não está em cena (sem boca para sincronizar)")
            if d["t"] >= dur:
                r.errors.append(f"{sid}: fala começa depois do fim da cena")
        for x in s.get("sfx", []):
            if x["id"] not in known_sfx:
                r.errors.append(f"{sid}: efeito sonoro '{x['id']}' não existe ({', '.join(sorted(known_sfx))})")
        # câmera: o quadro visível precisa estar coberto por TODAS as camadas do cenário (regra da F0)
        for k in s["camera"]["keys"]:
            vw, vh = W / k["zoom"], H / k["zoom"]
            x0, y0 = k["x"] - vw / 2, k["y"] - vh / 2
            for layer in bg["layers"]:
                f = layer["parallax"]
                center = (k["x"] - W / 2) * f + W / 2          # mesmo modelo do compositor (godot/compositor.gd)
                left, right = center - vw / 2, center + vw / 2
                if left < -1 or right > layer["width"] + 1:
                    r.errors.append(f"{sid}: câmera em x={k['x']} (zoom {k['zoom']}) mostra além da camada {layer['name']} "
                                    f"({left:.0f}..{right:.0f}, largura {layer['width']})")
            if y0 < -1 or y0 + vh > bg["height"] + 1:
                r.errors.append(f"{sid}: câmera em y={k['y']} (zoom {k['zoom']}) mostra fora do cenário na vertical")
    if not ep.get("approval", {}).get("final_render"):
        r.warnings.append("render final ainda não aprovado (approval.final_render = false): será gerado como CANDIDATO")
    return r
