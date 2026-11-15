"""Testes do modo clipe musical (ADR-0013)."""
import json
from pathlib import Path

from toonstudio.animation import cycles
from toonstudio.animation.timeline import compile_character
from toonstudio.audio.song import lines_from_words
from toonstudio.backgrounds import registry
from toonstudio.core.config import PROJECTS
from toonstudio.core.registry import character
from toonstudio.render import brand


def _w(text, t0, step=0.3):
    return [{"w": w, "s": t0 + i * step, "e": t0 + i * step + 0.25} for i, w in enumerate(text.split())]


def test_lyric_lines_keep_repetitions_together_and_break_on_new_verse():
    words = _w("Lango, lango, lango, na dança do calango,", 0) + _w("Vai, vai, vai, vai pro lado", 5)
    lines = [l["text"] for l in lines_from_words(words, gap=0.9, max_words=7)]
    assert lines[0].startswith("Lango, lango, lango,")
    assert any(l.startswith("Vai, vai, vai") for l in lines)


def test_beat_phase_uses_real_grid():
    beats = [0.5, 1.2, 1.9, 2.6]
    assert cycles.beat_phase(1.2, beats) == (1, 0.0)
    i, u = cycles.beat_phase(1.55, beats)
    assert i == 1 and abs(u - 0.5) < 1e-6


def test_head_sway_extremes_land_on_beats():
    beats = [i * 0.7 for i in range(10)]
    on = [cycles.dance("cabeca", b, beats)["head_tilt"] for b in beats[1:5]]
    mid = [cycles.dance("cabeca", b + 0.35, beats)["head_tilt"] for b in beats[1:5]]
    assert all(abs(v) > 0.2 for v in on), on             # extremo NA batida
    assert all(abs(v) < 0.05 for v in mid), mid          # passa pelo centro entre batidas
    assert on[0] * on[1] < 0                             # alterna o lado


def test_dance_action_follows_beats_in_timeline():
    beats = [i * 0.7 for i in range(20)]
    tl = compile_character(character("calanguinho"), {"start": {"x": 0, "y": 945}, "exposure": 1,
                                                       "actions": [{"t": 0, "do": "dance", "style": "cabeca", "dur": 5}]},
                           30, 5.0, beats=beats)
    a, b = tl.raw(1.4)["head_tilt"], tl.raw(2.1)["head_tilt"]
    assert a * b < 0 and abs(a) > 0.15


def test_dance_backgrounds_known_and_buildable():
    assert registry.known("danca_ondas_azul") and registry.known("danca_raios_roxo")
    assert not registry.known("danca_ondas_xadrez")
    meta = registry.ensure("danca_raios_laranja")
    assert any(l.get("spin_per_beat") for l in meta["layers"])


def test_ass_reveals_words_progressively(tmp_path):
    lines = [{"s": 1.0, "e": 2.2, "words": _w("vai pro lado", 1.0, 0.4)}]
    p = brand.ass(tmp_path / "t.ass", 1920, 1080, lines, "aviso", "rodapé", 5.0)
    txt = p.read_text()
    reveal = [l.split(",,")[-1].split("}")[-1] for l in txt.splitlines() if ",Letra," in l and l.startswith("Dialogue")]
    assert reveal == ["VAI", "VAI PRO", "VAI PRO LADO"]          # uma palavra a mais em cada evento
    assert "Dialogue: 1,0:00:01.00" in txt
    assert txt.count("Style: Letra") == 1 and "Aviso" in txt and "Rodape" in txt


def test_test_clip_validates_and_matches_audio_length():
    from toonstudio.core.validate import validate
    p = PROJECTS / "teste-danca-do-calango" / "episode.json"
    if not p.exists():
        return
    ep = json.loads(p.read_text(encoding="utf-8"))
    r = validate(ep)
    assert r.ok, r.errors
    total = sum(s["duration"] for s in ep["scenes"])
    assert abs(total - (ep["soundtrack"]["end"] - ep["soundtrack"]["start"])) < 0.05
