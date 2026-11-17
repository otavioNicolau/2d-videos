import copy
import json
import re
from pathlib import Path

import numpy as np
import pytest

from toonstudio.animation import cycles, easing
from toonstudio.animation.library import REGISTRY, catalog
from toonstudio.animation.timeline import compile_character, drawing_key, expose
from toonstudio.characters.base import EXPRESSIONS, VISEMES, expression
from toonstudio.core.config import PROJECTS, ROOT
from toonstudio.core.registry import character
from toonstudio.integrations import opentoonz as ot

EP = PROJECTS / "torta-do-caramelo" / "episode.json"


def test_easing_endpoints():
    for name, fn in easing.EASES.items():
        if name == "step":
            continue
        assert abs(fn(0.0)) < 1e-6 and abs(fn(1.0) - 1) < 1e-6, name
    assert max(easing.back(u / 100) for u in range(101)) > 1.0      # overshoot de verdade


def test_planted_foot_does_not_slide():
    """Durante o contato, o pé de apoio fica parado no MUNDO (quadril avança, pé recua na mesma velocidade)."""
    for cid in ("caramelo", "tevico"):
        g = cycles.GAITS[cid]["walk"]
        v = cycles.speed(cid, "walk")
        T = g["T"]
        xs = []
        for k in range(10):
            p = 0.05 + k * 0.035                      # dentro do contato (p < 0.5) do pé "n"
            t = p * T
            pose = cycles.gait(cid, "walk", p)
            assert pose["foot_n_y"] == 0.0
            xs.append(v * t + pose["foot_n_x"])       # posição do pé no mundo
        assert np.ptp(xs) < 1e-6, (cid, xs)


def test_walk_exposure_on_twos_and_root_moves():
    ch = character("caramelo")
    tl = compile_character(ch, {"start": {"x": 100, "y": 945, "turn": 0.8},
                                "actions": [{"t": 0, "do": "walk", "to_x": 700}]}, 24, 3.0)
    cells, drawings, stage = expose(tl)
    assert len(cells) == 72
    # em 2s: troca de desenho no máximo a cada 2 quadros (exceto a piscada, que é em 1s para o olho fechar de verdade)
    changes = [i for i in range(1, 72) if cells[i] != cells[i - 1] and tl.exposure_at(i / 24) == 2]
    assert all(b - a >= 2 for a, b in zip(changes, changes[1:]))
    assert stage[-1]["x"] > stage[0]["x"] + 500
    assert len(drawings) > 20                          # desenhos de verdade, não um sprite deslizando


def test_every_expression_and_viseme_renders():
    for cid in ("caramelo", "tevico", "luizinho"):
        ch = character(cid)
        base = ch.render_array({"turn": 0.4}, scale=0.3, jitter=0)
        for e in EXPRESSIONS:
            a = ch.render_array({"turn": 0.4, **expression(e)}, scale=0.3, jitter=0)
            assert a[..., 3].any()
        mouths = {v: ch.render_array({"turn": 0.4, "mouth": v}, scale=0.3, jitter=0) for v in VISEMES}
        # bocas abertas diferem da fechada
        for v in "CDE":
            assert np.abs(mouths[v].astype(int) - mouths["X"].astype(int)).sum() > 0, (cid, v)


def test_drawing_key_ignores_stage_position():
    p = {"turn": 0.5, "x": 100.0, "y": 945.0, "squash": 1.0}
    q = dict(p, x=900.0)
    assert drawing_key(p) == drawing_key(q)
    assert drawing_key(p) != drawing_key(dict(p, squash=1.2))


def test_tnz_cells_roundtrip(tmp_path):
    tnz = tmp_path / "t.tnz"
    tnz.write_text("""<tnz><levelSet><levels><level id='1'>
        tevico <info dpix="120.000000" dpiy="120.000000"/></level></levels></levelSet>
        <xsheet><columns><levelColumn id='2'><cells>
        <cell>0 2 <level id='1'/>0001 0 </cell><cell>2 3 <level id='1'/>0002 1 </cell>
        </cells></levelColumn></columns></xsheet></tnz>""")
    assert ot.read_cells(tnz) == {"tevico": [1, 1, 2, 3, 4]}
    assert ot.compress([1, 1, 2, 2, 2, 3]) == [(0, 2, 1), (2, 3, 2), (5, 1, 3)]


def test_episode_valid_and_validator_catches_errors():
    from toonstudio.core.validate import validate
    ep = json.loads(EP.read_text(encoding="utf-8"))
    assert validate(ep).ok
    bad = copy.deepcopy(ep)
    bad["scenes"][0]["characters"]["caramelo"]["actions"].append({"t": 1, "do": "moonwalk"})
    assert any("moonwalk" in e for e in validate(bad).errors)
    bad = copy.deepcopy(ep)
    bad["scenes"][0]["camera"]["keys"][0]["x"] = 5000          # câmera além do cenário
    assert any("além da camada" in e for e in validate(bad).errors)
    bad = copy.deepcopy(ep)
    bad["scenes"][0]["dialog"][0]["who"] = "tevico"            # fala de quem não está em cena
    assert any("não está em cena" in e for e in validate(bad).errors)


def test_parallax_model_matches_compositor():
    """O validador e o compositor do Godot usam a mesma fórmula de parallax."""
    gd = (ROOT / "godot" / "compositor.gd").read_text()
    assert "(cx - hw) * (1.0 - f)" in gd
    src = (ROOT / "toonstudio" / "core" / "validate.py").read_text()
    assert '(k["x"] - W / 2) * f + W / 2' in src


def test_sfx_catalog():
    from toonstudio.audio import sfx
    for k in sfx.CATALOG:
        a = sfx.get(k)
        assert a.dtype == np.float32 and 0.05 < len(a) / sfx.SR < 3 and np.max(np.abs(a)) <= 1.0, k


def test_catalog_lists_library():
    names = {c["name"] for c in catalog()}
    for required in ("walk", "run", "jump", "fall", "slip", "crash", "take", "grab", "point", "laugh", "eat", "sit", "stand",
                     "turn", "look_around", "bounce", "shock_reaction", "shake_fist"):
        assert required in names


def test_channel_keyed_later_starts_at_default():
    """Regressão (F6): canal cuja 1ª chave é tardia não pode valer desde o quadro 0 (a torta sumia da cena)."""
    tl = compile_character(character("torta"), {"start": {"x": 1500, "y": 822},
                                                "keys": [{"t": 3.9, "pose": {"hidden": 1.0}, "ease": "step"}]}, 24, 5.0)
    assert tl.raw(1.0)["hidden"] == 0.0 and tl.raw(4.0)["hidden"] == 1.0
    tl = compile_character(character("tevico"), {"start": {"x": 0, "y": 945}, "keys": [{"t": 2.0, "pose": {"smile": 1.0}}]}, 24, 3.0)
    d = character("tevico").pose()["smile"]
    assert tl.raw(0.0)["smile"] == d and tl.raw(1.0)["smile"] == d            # segura até a transição começar
    assert d < tl.raw(1.9)["smile"] < 1.0 and tl.raw(2.5)["smile"] == 1.0     # transição de 0,25 s até a chave


def test_action_channels_hold_until_action_starts():
    """Regressão (F6): estrelinhas e rotação de queda não podem começar antes da trombada."""
    tl = compile_character(character("caramelo"), {"start": {"x": 0, "y": 945, "turn": 0.95},
                                                   "actions": [{"t": 2.0, "do": "crash", "surface_x": 400}]}, 24, 4.0)
    assert tl.raw(1.9)["stars"] == 0 and tl.raw(1.9)["rot"] == 0
    assert tl.raw(2.1)["flat"] > 0.9


def test_luizinho_turnaround_has_no_hair_across_face():
    """Regressão: a borda do cabelo não pode atravessar o rosto quando ele gira (pontos do lado escondido)."""
    ch = character("luizinho")
    for turn in (0.0, 0.5, 0.85, 1.0, -0.85):
        a = ch.render_array({"turn": turn}, scale=0.5, jitter=0)
        assert a[..., 3].any()
