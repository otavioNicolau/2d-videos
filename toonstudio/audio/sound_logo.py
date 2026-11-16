"""Logotipo sonoro do canal (vinheta sem ritmo musical), feito por síntese — duração exata e controlada.

Roteiro (≈4 s): duas muriçocas passam zumbindo (uma da esquerda, outra da direita, com efeito Doppler) →
brilho mágico (arpejo de sininhos) → vozes dizem "Laurinha!" "e Luisinho!" → "zum!" + brilho final que se apaga.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000


def _t(d):
    return np.arange(int(d * SR)) / SR


def buzz_flyby(dur: float, f0: float, direction: int, seed: int) -> np.ndarray:
    """Zumbido de asa: dente-de-serra filtrado com vibrato rápido, Doppler e pan estéreo."""
    t = _t(dur)
    u = t / dur
    doppler = 1 + 0.12 * direction * (0.5 - u) * 2 * 0.5           # aproxima (agudo) → afasta (grave)
    f = f0 * doppler * (1 + 0.025 * np.sin(2 * np.pi * 34 * t))     # vibrato de asa
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * (ph / (2 * np.pi) % 1) - 1
    x = signal.sosfilt(signal.butter(2, [f0 * 0.8, f0 * 6], btype="band", fs=SR, output="sos"), saw)
    amp = np.sin(np.pi * u) ** 1.6                                   # chega, passa perto, vai embora
    x = x * amp * (0.75 + 0.25 * np.sin(2 * np.pi * 120 * t))      # granulação das asas
    pan = (u - 0.5) * 2 * direction                                 # -1 esquerda … +1 direita
    L = x * np.sqrt(0.5 * (1 - pan))
    R = x * np.sqrt(0.5 * (1 + pan))
    return np.stack([L, R], axis=1)


def chime(freq: float, dur: float = 1.2) -> np.ndarray:
    t = _t(dur)
    x = (np.sin(2 * np.pi * freq * t) + 0.45 * np.sin(2 * np.pi * freq * 2.76 * t) + 0.2 * np.sin(2 * np.pi * freq * 5.4 * t))
    return x * np.exp(-t * 4.0) * np.minimum(1, t / 0.002)


def sparkle(dur: float, seed: int = 3) -> np.ndarray:
    """Brilho mágico: chuvinha de sininhos agudos aleatórios."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)
    for _ in range(int(dur * 18)):
        st = int(rng.uniform(0, dur * 0.8) * SR)
        c = chime(rng.uniform(2600, 5200), 0.35) * rng.uniform(0.08, 0.18)
        out[st:st + len(c)] += c[: n - st]
    return out


def place(bus, x, t, gain=1.0):
    i = int(t * SR)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    seg = x[: max(0, bus.shape[0] - i)] * gain
    bus[i:i + len(seg)] += seg


def build(voice_a: Path | None, voice_b: Path | None, out: Path, total: float = 4.2) -> Path:
    bus = np.zeros((int(total * SR), 2))
    place(bus, buzz_flyby(1.3, 520, +1, 1), 0.0, 0.55)                  # Laurinha passa (agudinha) →
    place(bus, buzz_flyby(1.3, 410, -1, 2), 0.35, 0.5)                  # Luisinho passa ←
    for k, nfreq in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):         # arpejo de sininhos (dó-mi-sol-dó)
        place(bus, chime(nfreq), 1.25 + k * 0.09, 0.35)
    place(bus, sparkle(1.4, 5), 1.25, 1.0)
    for f, t0, g in ((voice_a, 1.55, 0.95), (voice_b, 2.3, 0.95)):
        if f is None:                        # versão sem voz (vozes sintéticas/recortadas soaram robóticas)
            continue
        a, sr = sf.read(f, dtype="float32")
        if a.ndim > 1:
            a = a.mean(axis=1)
        if sr != SR:
            a = signal.resample_poly(a, SR, sr)
        place(bus, a / (np.abs(a).max() or 1), t0, g)
    zum = buzz_flyby(0.45, 700, +1, 9) * np.linspace(1, 0.2, int(0.45 * SR))[:, None]
    place(bus, zum, 3.25, 0.45)                                          # "zum!" final
    place(bus, chime(2093.0, 1.0), 3.3, 0.4)
    place(bus, sparkle(0.9, 8), 3.3, 1.0)
    fade = int(0.4 * SR)
    bus[-fade:] *= np.linspace(1, 0, fade)[:, None]
    bus /= max(1e-6, np.abs(bus).max()) / 0.9
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, bus.astype(np.float32), SR)
    return out
