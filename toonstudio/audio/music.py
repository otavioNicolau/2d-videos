"""Trilha de fundo sintetizada: tema saltitante em dó maior (marimba + baixo pizzicato + escovinha).

Honesto: é uma trilha simples, gerada por código. Para um episódio publicado, recomenda-se trilha composta/licenciada
(ADR-0006 do ~/videos chegou à mesma conclusão).
"""
from __future__ import annotations

import numpy as np

from .sfx import SR, _lp, _norm, pluck

BPM = 132
BEAT = 60 / BPM
NOTES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(name: str) -> float:
    n, octv = name[:-1], int(name[-1])
    semis = NOTES[n[0]] + (1 if "#" in n else 0) + 12 * (octv - 4)
    return 261.63 * 2 ** (semis / 12)


def marimba(freq, dur):
    t = np.arange(int(dur * SR)) / SR
    x = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * 18)) * np.exp(-t * 5.5)
    return x * np.minimum(1, t / 0.003)


# melodia em colcheias (nota ou "-" pausa), 4 compassos x 2
MELODY = ("E5 G5 C6 G5 E5 - D5 - | F5 A5 D6 A5 F5 - E5 - | E5 G5 C6 E6 D6 C6 B5 G5 | A5 - G5 - C6 - - - |"
          "C6 B5 A5 G5 F5 E5 D5 - | E5 F5 G5 A5 G5 - E5 - | F5 E5 D5 C5 B4 C5 D5 E5 | C5 - G4 - C5 - - - |")
BASS = "C3 G2 C3 G2 | D3 A2 D3 A2 | C3 G2 E3 G2 | F3 G2 C3 G2 | F3 C3 F3 C3 | C3 G2 C3 G2 | G2 D3 G2 B2 | C3 G2 C3 - |"


def theme(dur: float) -> np.ndarray:
    mel = [m for m in MELODY.replace("|", " ").split()]
    bas = [b for b in BASS.replace("|", " ").split()]
    loop = len(mel) * BEAT / 2
    n = int(dur * SR) + SR
    out = np.zeros(n)
    t0 = 0.0
    while t0 < dur:
        for i, m in enumerate(mel):
            if m != "-":
                s = int((t0 + i * BEAT / 2) * SR)
                x = marimba(hz(m), 0.6) * 0.5
                out[s:s + len(x)] += x[: max(0, n - s)]
        for i, b in enumerate(bas):
            if b != "-":
                s = int((t0 + i * BEAT) * SR)
                x = pluck(hz(b), 0.5, seed=i) * 0.55
                out[s:s + len(x)] += x[: max(0, n - s)]
        rng = np.random.default_rng(int(t0))
        for i in range(len(bas) * 2):
            s = int((t0 + i * BEAT / 2) * SR)
            k = int(0.04 * SR)
            hit = rng.normal(0, 1, k) * np.exp(-np.linspace(0, 8, k)) * (0.08 if i % 2 else 0.04)
            out[s:s + k] += hit[: max(0, n - s)]
        t0 += loop
    out = out[: int(dur * SR)]
    fade = int(1.5 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    return _norm(_lp(out, 9000), 0.7)
