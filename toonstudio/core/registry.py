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
from ..characters.flat_muri import LAURINHA as _FL, LUISINHO as _FU, FlatMuri
CHARACTERS["laurinha"] = lambda: FlatMuri("laurinha", "Laurinha", _FL)      # estilo oficial (BIBLIA_VISUAL.md)
CHARACTERS["luisinho"] = lambda: FlatMuri("luisinho", "Luisinho", _FU)
from ..characters.flat_muri import MAMAE as _FM, VOVO as _FV
CHARACTERS["mamae"] = lambda: FlatMuri("mamae", "Mamãe", _FM)
CHARACTERS["vovo"] = lambda: FlatMuri("vovo", "Vovó", _FV)
from ..characters.flat_muri import JOANINHA as _FJ, FORMIGUINHA as _FF
CHARACTERS["joaninha"] = lambda: FlatMuri("joaninha", "Joaninha", _FJ)
CHARACTERS["formiguinha"] = lambda: FlatMuri("formiguinha", "Formiguinha", _FF)
from ..characters.flat_muri import FORMIGA_MAE as _FMA
CHARACTERS["formiga_mae"] = lambda: FlatMuri("formiga_mae", "Mamãe Formiga", _FMA)
from ..characters.flat_muri import VOVOZINHO as _FVZ
CHARACTERS["vovozinho"] = lambda: FlatMuri("vovozinho", "Vovô", _FVZ)
from ..characters.flat_monstro import BULU as _MB, TETE as _MT, FlatMonstro        # 2º canal: Bulu e Tetê (monstrinhos)
CHARACTERS["bulu"] = lambda: FlatMonstro("bulu", "Bulu", _MB)
CHARACTERS["tete"] = lambda: FlatMonstro("tete", "Tetê", _MT)
from ..characters.flat_monstro import BULU_58 as _MB58, TETE_58 as _MT58
CHARACTERS["bulu_58"] = lambda: FlatMonstro("bulu_58", "Bulu", _MB58)
CHARACTERS["tete_58"] = lambda: FlatMonstro("tete_58", "Tetê", _MT58)
from ..characters.flat_props import PROPS as _PROPS
for _pid, _cls in _PROPS.items():
    CHARACTERS[_pid] = _cls
# a turma do canal (modelo chibi): construída a partir do visual de cada criança
for _cid, (_name, _look) in TURMA.items():
    CHARACTERS.setdefault(_cid, (lambda c=_cid, n=_name, l=_look: Chibi(c, n, l)))
BACKGROUNDS = {"floresta_clareira": "toonstudio.backgrounds.forest"}

_cache: dict[str, Character] = {}


def character(cid: str) -> Character:
    if cid not in CHARACTERS:
        raise KeyError(f"personagem desconhecido: {cid} (disponíveis: {sorted(CHARACTERS)})")
    if cid not in _cache:
        _cache[cid] = CHARACTERS[cid]()
    return _cache[cid]
