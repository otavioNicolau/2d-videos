"""Biblioteca de cenários: ids conhecidos e construção sob demanda (com cache por hash do código)."""
from __future__ import annotations

import json
from pathlib import Path

from ..core.config import LIBRARY, ROOT, file_sha

STATIC = {"floresta_clareira": "forest", "sertao": "sertao", "fofo_parque": "fofo", "fofo_cidade": "fofo", "fofo_praia": "fofo", "plano_parque": "plano"}


INTERIOR = ("plano_banheiro", "plano_quarto_rosa", "plano_quarto_azul", "plano_cozinha", "plano_casa_frente", "plano_escola", "plano_ceu", "plano_jardim", "plano_lagoa", "plano_sala", "plano_espaco", "plano_lua", "plano_campo", "plano_gelo", "plano_mar_gelado", "plano_praia", "plano_salao", "plano_oficina", "plano_fundo_mar")


def known(bg_id: str) -> bool:
    if bg_id.startswith("mon_"):                      # 2º canal: Bulu e Tetê (chapado sem contorno)
        from .monstrinho import known as _mk
        return _mk(bg_id)
    if bg_id in STATIC:
        return True
    if bg_id in INTERIOR:
        return True
    if bg_id.startswith("padrao_"):
        from .dance import COLORS
        from .interior import MOTIVOS
        parts = bg_id.split("_", 2)
        return len(parts) == 3 and parts[1] in MOTIVOS and parts[2] in COLORS
    if bg_id.startswith("danca_"):
        from .dance import COLORS
        parts = bg_id.split("_", 2)
        return len(parts) == 3 and parts[1] in ("ondas", "raios", "xadrez", "bolinhas") and parts[2] in COLORS
    return False


def catalog() -> list[str]:
    from .dance import COLORS
    from .interior import MOTIVOS
    from .monstrinho import catalog as _mcat
    return _mcat() + (sorted(STATIC) + list(INTERIOR) + [f"danca_{k}_{c}" for k in ("ondas", "raios", "xadrez", "bolinhas") for c in COLORS]
                      + [f"padrao_{m}_{c}" for m in MOTIVOS for c in COLORS])


ESC_CENA_LAURINHA = 2.2


def ensure(bg_id: str, scale: float = 1.5) -> dict:
    """Constrói o cenário se faltar ou se o código mudou. Retorna o background.json."""
    if not known(bg_id):
        raise KeyError(f"cenário desconhecido: {bg_id} (disponíveis: {', '.join(catalog())})")
    out = LIBRARY / "backgrounds" / bg_id / "layers"
    mod = "monstrinho" if bg_id.startswith("mon_") else (STATIC.get(bg_id) or ("interior" if bg_id in INTERIOR or bg_id.startswith("padrao_") else "dance"))
    if mod in ("plano", "interior"):          # 21/11: cenários da Laurinha a 2,2x como os do Fofolucos (closes nítidos)
        scale = max(scale, ESC_CENA_LAURINHA)
    h = file_sha(ROOT / "toonstudio" / "backgrounds" / f"{mod}.py", ROOT / "toonstudio" / "backgrounds" / "painter.py") + f":{scale}"
    stamp = out / ".hash"
    meta_p = out / "background.json"
    if not (meta_p.exists() and stamp.exists() and stamp.read_text() == h):
        if mod == "forest":
            from . import forest
            forest.build(out, scale=scale)
        elif mod == "sertao":
            from . import sertao
            sertao.build(out, scale=scale)
        elif mod == "interior":
            from . import interior
            interior.build(bg_id, out, scale=scale)
        elif mod == "plano":
            from . import plano
            plano.build(bg_id, out, scale=scale)
        elif mod == "monstrinho":
            from . import monstrinho
            monstrinho.build(bg_id, out, scale=scale)
        elif mod == "fofo":
            from . import fofo
            fofo.build(bg_id, out, scale=scale)
        else:
            from . import dance
            dance.build(bg_id, out, scale=1.0)
        stamp.write_text(h)
    return json.loads(meta_p.read_text(encoding="utf-8"))
