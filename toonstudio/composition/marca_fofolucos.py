"""Abertura (vinheta) do canal FOFOLUCOS — peça fixa, ≤ 5 s, renderizada UMA vez (projeto fofolucos/marca-vinheta).

Áudio: repetição do tema "Fofolucos Rawr" do Suno (21/11/2026, no ritmo da música 02), áudio ORIGINAL sem separar a voz,
cortado de 22,85 a 26,64 s do tema (library/audio/marca/fofolucos_tema.wav → fofolucos_vinheta.wav, 3,79 s).
Sílabas (ataques da voz): "Fo" 0,14 · "fo" 0,44 · "lu" 0,88 · "cos" 1,07 · "RAWR!" 1,23 · "Fo" 1,97 · "fo" 2,25 ·
"lu" 2,69 · "cos" 2,81 · "RAWR!" 3,07–3,75.
Animação: o logo aparece com "pop"; a turma BROTA de baixo de dois em dois no "Fo-fo-lu"; no 1º RAWR todos fazem a pose
RAWR; no 2º "Fofolucos" pulam no ritmo; no 2º RAWR a pose final com estrelinhas e o logo balança.
Uso: PYTHONPATH=. .venv/bin/python -m toonstudio.composition.marca_fofolucos   (escreve o episode.json)
     PYTHONPATH=. .venv/bin/python -m toonstudio.cli --canal fofolucos build fofolucos/marca-vinheta
"""
from __future__ import annotations

import json

from ..core.config import PROJECTS

DUR = 3.79
FO1, RAWR1, FO2, RAWR2 = (0.14, 0.44, 0.88), 1.23, (1.97, 2.25, 2.69, 2.81), 3.07
CHAO, FUNDO = 965, 1700            # pé no chão / bem escondido abaixo da tela (nem a antena do Gogo aparece)
# (monstrinho, x, quando brota, virada) — de dois em dois, de dentro para fora
TURMA = (("bilu", 1115, FO1[0], 0.15), ("mimi", 1485, FO1[0], -0.15), ("teco", 815, FO1[1], 0.2),
         ("nhoque", 1785, FO1[1], -0.2), ("gogo", 515, FO1[2], 0.25), ("zuzu", 2085, FO1[2], -0.25))


def _monstrinho(cid: str, x: float, t_brota: float, turn: float, k: int) -> dict:
    keys = [{"t": 0.0, "pose": {"y": FUNDO}, "ease": "step"},
            {"t": round(t_brota, 3), "pose": {"y": FUNDO}, "ease": "step"},
            {"t": round(t_brota + 0.22, 3), "pose": {"y": CHAO}, "ease": "back"}]
    acoes = [{"t": round(t_brota + 0.24, 3), "do": "dance", "style": "pulinho", "dur": round(RAWR1 - t_brota - 0.26, 3)},
             {"t": RAWR1, "do": "rawr", "dur": round(FO2[0] - RAWR1 - 0.02, 3)},
             {"t": FO2[0], "do": "dance", "style": "pulinho", "dur": round(RAWR2 - FO2[0] - 0.02, 3)},
             {"t": round(RAWR2 + 0.03 * (k % 3), 3), "do": "rawr", "dur": round(DUR - RAWR2 - 0.03 * (k % 3), 3)}]
    return {"start": {"x": x, "y": FUNDO, "turn": turn, "expr": "joy", "z": 3, "depth": 0.86}, "exposure": 1,
            "actions": acoes, "keys": keys}


def _logo() -> dict:
    ks = [{"t": 0.0, "pose": {"escala": 0.0, "giro": 0.0}, "ease": "step"},
          {"t": 0.18, "pose": {"escala": 1.12}, "ease": "out"}, {"t": 0.34, "pose": {"escala": 1.0}, "ease": "inout"}]
    for t in (RAWR1, RAWR2):                              # balança no RAWR
        ks += [{"t": t, "pose": {"escala": 1.0, "giro": 0.0}},
               {"t": round(t + 0.1, 3), "pose": {"escala": 1.08, "giro": 0.035}, "ease": "out"},
               {"t": round(t + 0.24, 3), "pose": {"escala": 1.0, "giro": -0.02}, "ease": "inout"},
               {"t": round(t + 0.4, 3), "pose": {"giro": 0.0}, "ease": "inout"}]
    for t in FO2:                                         # quiquezinho em cada sílaba do 2º "Fofolucos"
        ks += [{"t": t, "pose": {"escala": 1.0}}, {"t": round(t + 0.08, 3), "pose": {"escala": 1.04}, "ease": "out"},
               {"t": round(t + 0.2, 3), "pose": {"escala": 1.0}, "ease": "inout"}]
    ks.sort(key=lambda k: k["t"])
    return {"start": {"x": 1300, "y": 770, "z": 1, "escala": 0.0, "depth": 0.9}, "exposure": 1, "keys": ks}


def vinheta_episode() -> dict:
    cam = {"keys": [{"t": 0, "x": 1300, "y": 540, "zoom": 1.0}, {"t": DUR, "x": 1300, "y": 540, "zoom": 1.05, "ease": "inout"}],
           "beat": {"pulse": 0.0, "bar_zoom": 0.0, "sway": 0, "bounce": 0},
           "shake": [{"t": RAWR2, "dur": 0.35, "amp": 10.0}]}
    chars = {cid: _monstrinho(cid, x, t, tn, k) for k, (cid, x, t, tn) in enumerate(TURMA)}
    scene = {"id": "s01_vinheta", "title": "Vinheta Fofolucos", "duration": DUR, "background": "mon_vila", "camera": cam,
             "fx": ["estrelas"], "characters": chars, "props": {"logo_fofolucos": _logo()}}
    cast = {cid: {"character": cid} for cid, *_ in TURMA}
    cast["logo_fofolucos"] = {"character": "logo_png"}
    return {"schema": "1.1", "id": "marca-vinheta", "projeto": "fofolucos/marca-vinheta", "title": "Vinheta — Fofolucos",
            "logline": "Peça fixa do canal: abertura de 3,79 s com a repetição 'Fofolucos! Rawr!' do tema (Suno, áudio original).",
            "fps": 30, "resolution": [1920, 1080], "background": "mon_vila",
            "soundtrack": {"file": "musica/trabalho.wav", "analysis": "analise/song.json", "start": 0.0, "end": DUR,
                           "fade_out": 0.0, "beat_grid": "full"},
            "overlays": {"logo": False}, "cast": cast,
            "approval": {"storyboard": False, "final_render": False}, "scenes": [scene]}


def preparar() -> str:
    pdir = PROJECTS / "fofolucos" / "marca-vinheta"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "episode.json").write_text(json.dumps(vinheta_episode(), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(pdir / "episode.json")


if __name__ == "__main__":
    print(preparar())
