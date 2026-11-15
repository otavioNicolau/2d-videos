"""Registro de personagens/objetos e cenários disponíveis (fonte da verdade para validação e IA)."""
from __future__ import annotations

from ..characters.base import Character
from ..characters.calanguinho import Calanguinho
from ..characters.caramelo import Caramelo
from ..characters.props import Torta
from ..characters.chibi import TURMA, Chibi
from ..characters.tevico import Tevico

CHARACTERS: dict = {"caramelo": Caramelo, "tevico": Tevico, "torta": Torta, "calanguinho": Calanguinho}
from ..characters.muricoca import LAURINHA_M, LUIZINHO_M, Muricoca
CHARACTERS["laurinha_muricoca"] = lambda: Muricoca("laurinha_muricoca", "Laurinha", LAURINHA_M)
CHARACTERS["luizinho_muricoca"] = lambda: Muricoca("luizinho_muricoca", "Luizinho", LUIZINHO_M)
# a turma do canal (modelo chibi): construída a partir do visual de cada criança
for _cid, (_name, _look) in TURMA.items():
    CHARACTERS[_cid] = (lambda c=_cid, n=_name, l=_look: Chibi(c, n, l))
BACKGROUNDS = {"floresta_clareira": "toonstudio.backgrounds.forest"}

_cache: dict[str, Character] = {}


def character(cid: str) -> Character:
    if cid not in CHARACTERS:
        raise KeyError(f"personagem desconhecido: {cid} (disponíveis: {sorted(CHARACTERS)})")
    if cid not in _cache:
        _cache[cid] = CHARACTERS[cid]()
    return _cache[cid]
