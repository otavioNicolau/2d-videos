"""Registro de personagens/objetos e cenários disponíveis (fonte da verdade para validação e IA)."""
from __future__ import annotations

from ..characters.base import Character
from ..characters.caramelo import Caramelo
from ..characters.props import Torta
from ..characters.luizinho import Luizinho
from ..characters.tevico import Tevico

CHARACTERS: dict[str, type[Character]] = {"caramelo": Caramelo, "tevico": Tevico, "torta": Torta, "luizinho": Luizinho}
BACKGROUNDS = {"floresta_clareira": "toonstudio.backgrounds.forest"}

_cache: dict[str, Character] = {}


def character(cid: str) -> Character:
    if cid not in CHARACTERS:
        raise KeyError(f"personagem desconhecido: {cid} (disponíveis: {sorted(CHARACTERS)})")
    if cid not in _cache:
        _cache[cid] = CHARACTERS[cid]()
    return _cache[cid]
