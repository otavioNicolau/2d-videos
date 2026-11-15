"""Mixagem do episódio: falas, efeitos, ambiente e trilha com "ducking" sob as falas; loudness final por FFmpeg."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

from ..core.config import LIBRARY, tool
from . import music, sfx

SR = sfx.SR


def _load(p: str) -> np.ndarray:
    a, sr = sf.read(p, dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    if sr != SR:
        a = signal.resample_poly(a, SR, sr).astype(np.float32)
    return a


def _place(bus: np.ndarray, x: np.ndarray, t: float, gain_db: float = 0.0, pan: float = 0.0) -> None:
    i = int(t * SR)
    if i >= bus.shape[0]:
        return
    g = 10 ** (gain_db / 20)
    seg = x[: bus.shape[0] - i] * g
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[i:i + len(seg), 0] += seg * l * 1.414
    bus[i:i + len(seg), 1] += seg * r * 1.414


def mix_episode(ep, lines: dict) -> Path:
    total = sum(s["duration"] for s in ep.ep["scenes"])
    n = int(total * SR) + SR
    voice = np.zeros((n, 2), np.float32)
    fx = np.zeros((n, 2), np.float32)
    amb = np.zeros((n, 2), np.float32)
    lib = LIBRARY / "audio" / "sfx"
    off = 0.0
    for idx, s in enumerate(ep.ep["scenes"]):
        for d in s.get("dialog", []):
            L = lines[f"{s['id']}:{d['t']}"]
            _place(voice, _load(L["wav"]), off + d["t"], d.get("volume_db", 0.0))
        for x in s.get("sfx", []):
            _place(fx, sfx.get(x["id"], lib), off + x["t"], x.get("volume_db", -4.0), x.get("pan", 0.0))
        a = sfx.forest_ambience(s["duration"], seed=idx)
        _place(amb, a, off, -14)
        off += s["duration"]
    # trilha com ducking (envelope suave sob a voz)
    m = ep.ep.get("music")
    mus = np.zeros((n, 2), np.float32)
    if m:
        th = music.theme(total)
        _place(mus, th, 0.0, float(m.get("volume_db", -20)))
        env = np.abs(voice[:, 0])
        win = int(0.25 * SR)
        env = np.convolve(env, np.ones(win) / win, mode="same")
        duck = 1 - 0.55 * np.clip(env / 0.02, 0, 1)
        duck = np.convolve(duck, np.ones(win) / win, mode="same")
        mus *= duck[:, None]
    mixbus = voice * 1.0 + fx * 0.9 + amb + mus
    # fade-out no fim
    end = int(total * SR)
    k = int(0.8 * SR)
    mixbus[end - k:end] *= np.linspace(1, 0, k)[:, None]
    mixbus = mixbus[:end]
    raw = ep.build / "audio" / "mix_raw.wav"
    raw.parent.mkdir(parents=True, exist_ok=True)
    peak = float(np.max(np.abs(mixbus))) or 1
    sf.write(raw, mixbus / max(peak, 1.0) * 0.95, SR, subtype="FLOAT")
    out = ep.build / "audio" / "mix.wav"
    subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "48000", str(out)], check=True)
    return out
