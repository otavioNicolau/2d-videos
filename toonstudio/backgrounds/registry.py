"""Biblioteca de cenários: ids conhecidos e construção sob demanda (com cache por hash do código)."""
from __future__ import annotations

import json
from pathlib import Path

from ..core.config import LIBRARY, ROOT, file_sha

STATIC = {"floresta_clareira": "forest", "sertao": "sertao"}


def known(bg_id: str) -> bool:
    if bg_id in STATIC:
        return True
    if bg_id.startswith("danca_"):
        from .dance import COLORS
        parts = bg_id.split("_", 2)
        return len(parts) == 3 and parts[1] in ("ondas", "raios", "xadrez", "bolinhas") and parts[2] in COLORS
    return False


def catalog() -> list[str]:
    from .dance import COLORS
    return sorted(STATIC) + [f"danca_{k}_{c}" for k in ("ondas", "raios", "xadrez", "bolinhas") for c in COLORS]


def ensure(bg_id: str, scale: float = 1.5) -> dict:
    """Constrói o cenário se faltar ou se o código mudou. Retorna o background.json."""
    if not known(bg_id):
        raise KeyError(f"cenário desconhecido: {bg_id} (disponíveis: {', '.join(catalog())})")
    out = LIBRARY / "backgrounds" / bg_id / "layers"
    mod = STATIC.get(bg_id, "dance")
    h = file_sha(ROOT / "toonstudio" / "backgrounds" / f"{mod}.py", ROOT / "toonstudio" / "backgrounds" / "painter.py")
    stamp = out / ".hash"
    meta_p = out / "background.json"
    if not (meta_p.exists() and stamp.exists() and stamp.read_text() == h):
        if mod == "forest":
            from . import forest
            forest.build(out, scale=scale)
        elif mod == "sertao":
            from . import sertao
            sertao.build(out, scale=scale)
        else:
            from . import dance
            dance.build(bg_id, out, scale=1.0)
        stamp.write_text(h)
    return json.loads(meta_p.read_text(encoding="utf-8"))
