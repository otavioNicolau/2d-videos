"""Efeitos sonoros de desenho animado sintetizados (sem amostras de terceiros, sem licença a cumprir).

Cada efeito é uma função determinística → numpy float32 mono a SR. Arquivos em library/audio/sfx/*.wav
(qualquer .wav colocado lá também vira id utilizável).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, r=None, curve=4.0):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    if r is None:
        e[na:] = np.exp(-curve * np.linspace(0, 1, n - na))
    return e


def _bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def _hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def _norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return (x / m * peak).astype(np.float32)


def _rng(seed):
    return np.random.default_rng(seed)


def pluck(freq, dur=0.6, seed=0, bright=0.5):
    """Karplus-Strong: corda beliscada (pizzicato)."""
    n = int(dur * SR)
    N = int(SR / freq)
    buf = _rng(seed).uniform(-1, 1, N)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = 0.5 * (buf[i % N] + buf[(i + 1) % N]) * (0.994 + 0.004 * bright)
    return _norm(out * _env(n, 0.002, curve=3.0))


def pizz_1():
    return pluck(196.0, seed=1)


def pizz_2():
    return pluck(246.9, seed=2)


def pizz_3():
    return pluck(293.7, seed=3)


def slide(f0, f1, dur, vib=6.0, seed=0):
    t = _t(dur)
    f = f0 * (f1 / f0) ** (t / dur)
    f = f * (1 + 0.015 * np.sin(2 * np.pi * vib * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.12 * np.sin(2 * ph)
    breath = _bp(_rng(seed).normal(0, 1, len(t)), 1500, 6000) * 0.05
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06)
    return _norm((tone + breath) * env, 0.7)


def whistle_up():
    return slide(520, 1900, 0.45)


def whistle_down():
    return slide(1900, 260, 0.75, vib=5)


def pop():
    t = _t(0.18)
    f = 300 + 900 * (t / 0.18) ** 0.5
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)
    click = np.zeros_like(t)
    click[:200] = _rng(4).normal(0, 0.6, 200) * np.linspace(1, 0, 200)
    return _norm(x + click, 0.8)


def zip():  # noqa: A001 - nome do efeito
    t = _t(0.38)
    n = _rng(5).normal(0, 1, len(t))
    out = np.zeros_like(t)
    seg = 512
    for i in range(0, len(t), seg):
        u = i / len(t)
        fc = 900 + 5000 * u
        out[i:i + seg] = _bp(n[i:i + seg], fc * 0.7, min(fc * 1.4, 20000))
    env = np.sin(np.pi * np.clip(t / 0.38, 0, 1)) ** 1.5
    return _norm(out * env, 0.75)


def tink():
    t = _t(0.5)
    x = (np.sin(2 * np.pi * 2350 * t) + 0.4 * np.sin(2 * np.pi * 5870 * t)) * np.exp(-t * 9)
    return _norm(x, 0.5)


def patter():
    out = np.zeros(int(1.8 * SR))
    rng = _rng(6)
    step = 1 / 13.0
    for k in range(int(1.8 / step)):
        i = int(k * step * SR)
        n = int(0.05 * SR)
        hit = _lp(rng.normal(0, 1, n), 900) * np.exp(-np.linspace(0, 6, n)) * (0.7 + 0.3 * rng.random())
        hit += 0.6 * np.sin(2 * np.pi * (110 + 30 * (k % 2)) * np.arange(n) / SR) * np.exp(-np.linspace(0, 8, n))
        out[i:i + n] += hit[: len(out) - i]
    out *= np.minimum(1, np.linspace(0, 1.8, len(out)) / 0.1) * np.minimum(1, (1.8 - np.linspace(0, 1.8, len(out))) / 0.3)
    return _norm(out, 0.6)


def bonk():
    """Pancada de madeira + baque grave + "boing" de mola (cabeçada clássica)."""
    t = _t(0.9)
    knock = _bp(_rng(7).normal(0, 1, len(t)), 500, 1400, 4) * np.exp(-t * 45)
    body = np.sin(2 * np.pi * 85 * t) * np.exp(-t * 9)
    fb = 330 * (1 + 0.18 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 3))
    boing = np.sin(2 * np.pi * np.cumsum(fb) / SR) * np.exp(-t * 4.5) * 0.55
    return _norm(knock * 1.4 + body + boing, 0.95)


def thud():
    t = _t(0.6)
    x = np.sin(2 * np.pi * 58 * t) * np.exp(-t * 10) + _lp(_rng(8).normal(0, 1, len(t)), 400) * np.exp(-t * 18) * 0.8
    return _norm(x, 0.95)


def rustle():
    t = _t(1.0)
    n = _hp(_rng(9).normal(0, 1, len(t)), 2500)
    am = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * t + 3 * np.sin(2 * np.pi * 1.3 * t)))
    return _norm(n * am * np.exp(-t * 2.5) * np.minimum(1, t / 0.02), 0.45)


def tweets():
    out = np.zeros(int(1.8 * SR))
    rng = _rng(10)
    for k in range(7):
        st = int((0.05 + k * 0.24) * SR)
        d = 0.12
        t = _t(d)
        f = 2600 + 900 * np.sin(np.pi * t / d) + rng.uniform(-200, 200)
        ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        out[st:st + len(ch)] += ch[: len(out) - st]
    return _norm(out, 0.4)


def flutter():
    t = _t(0.9)
    n = _bp(_rng(11).normal(0, 1, len(t)), 300, 2500)
    am = np.clip(np.sin(2 * np.pi * 11 * t), 0, 1) ** 2
    return _norm(n * am * np.minimum(1, (0.9 - t) / 0.2), 0.5)


def munch():
    t = _t(0.26)
    rng = _rng(12)
    x = np.zeros_like(t)
    for k in range(5):
        i = int((0.01 + k * 0.035) * SR)
        n = int(0.03 * SR)
        x[i:i + n] += _bp(rng.normal(0, 1, n), 600, 3500) * np.exp(-np.linspace(0, 5, n))
    x += _lp(rng.normal(0, 1, len(t)), 300) * np.exp(-t * 12) * 0.5
    return _norm(x, 0.6)


def forest_ambience(dur: float, seed: int = 0) -> np.ndarray:
    """Vento baixo + passarinhos esparsos (fundo de cena)."""
    rng = _rng(100 + seed)
    t = _t(dur)
    wind = _lp(rng.normal(0, 1, len(t)), 500) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t + seed))
    out = wind * 0.25
    k = 0.7
    while k < dur - 0.5:
        d = rng.uniform(0.08, 0.16)
        tt = _t(d)
        f0 = rng.uniform(3000, 4800)
        f = f0 + rng.uniform(-900, 900) * np.sin(np.pi * tt / d)
        ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / d) ** 2 * rng.uniform(0.05, 0.12)
        for rep in range(int(rng.integers(1, 4))):
            i = int((k + rep * (d + 0.04)) * SR)
            out[i:i + len(ch)] += ch[: len(out) - i]
        k += rng.uniform(0.8, 2.2)
    return _norm(out, 0.35)


CATALOG = {"pizz_1": pizz_1, "pizz_2": pizz_2, "pizz_3": pizz_3, "whistle_up": whistle_up, "whistle_down": whistle_down,
           "pop": pop, "zip": zip, "tink": tink, "patter": patter, "bonk": bonk, "thud": thud, "rustle": rustle,
           "tweets": tweets, "flutter": flutter, "munch": munch}


def get(sfx_id: str, lib_dir: Path | None = None) -> np.ndarray:
    if lib_dir is not None:
        f = lib_dir / f"{sfx_id}.wav"
        if f.exists():
            import soundfile as sf
            a, sr = sf.read(f, dtype="float32")
            if a.ndim > 1:
                a = a.mean(axis=1)
            if sr != SR:
                a = signal.resample_poly(a, SR, sr).astype(np.float32)
            return a
    if sfx_id not in CATALOG:
        raise KeyError(f"efeito desconhecido: {sfx_id}")
    return CATALOG[sfx_id]()
