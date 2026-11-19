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


# ───── efeitos de desenho para os clipes (18/11): sintetizados, sem licença ─────

def boing():
    """Mola de desenho: tom que oscila e cai (pulo, quique)."""
    t = _t(0.7)
    f = 260 * (1 + 0.35 * np.sin(2 * np.pi * 16 * t) * np.exp(-t * 4)) * (1 + 0.6 * np.exp(-t * 6))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    return _norm(x + 0.3 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR) * np.exp(-t * 7), 0.8)


def whoosh():
    """Vento de passagem (corte, voo, giro)."""
    t = _t(0.5)
    n = _rng(21).normal(0, 1, len(t))
    out = np.zeros_like(t)
    seg = 480
    for i in range(0, len(t), seg):
        u = i / len(t)
        fc = 400 + 2600 * np.sin(np.pi * u)
        out[i:i + seg] = _bp(n[i:i + seg], fc * 0.6, fc * 1.5)
    return _norm(out * np.sin(np.pi * t / 0.5) ** 2, 0.6)


def ding():
    """Sininho de acerto (resposta certa, ideia)."""
    t = _t(1.1)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((1568, 1.0, 3.5), (3136, 0.35, 5), (4700, 0.15, 8)))
    return _norm(x * np.minimum(1, t / 0.003), 0.6)


def plim():
    """Brilho mágico: arpejo agudo subindo (algo aparece, acende)."""
    out = np.zeros(int(0.9 * SR))
    for k, f in enumerate((1319, 1568, 2093, 2637, 3136)):
        i = int(k * 0.07 * SR)
        t = _t(0.5)
        x = np.sin(2 * np.pi * f * t) * np.exp(-t * 9)
        out[i:i + len(x)] += x[: len(out) - i]
    return _norm(out, 0.5)


def bip_bop():
    """Robô: "bip" agudo + "bop" grave, onda quadrada suave."""
    out = np.zeros(int(0.42 * SR))
    for st, f, d in ((0.0, 1480, 0.12), (0.2, 740, 0.16)):
        t = _t(d)
        x = np.tanh(3 * np.sin(2 * np.pi * f * t)) * np.minimum(1, t / 0.004) * np.minimum(1, (d - t) / 0.02)
        i = int(st * SR)
        out[i:i + len(x)] += x
    return _norm(_lp(out, 6000), 0.55)


def bips():
    """Robô "pensando": sequência rápida de bips aleatórios."""
    rng = _rng(22)
    out = np.zeros(int(0.8 * SR))
    for k in range(8):
        f = rng.choice([880, 1175, 1480, 1760, 2093])
        t = _t(0.07)
        x = np.tanh(2.5 * np.sin(2 * np.pi * f * t)) * np.minimum(1, (0.07 - t) / 0.01)
        i = int(k * 0.095 * SR)
        out[i:i + len(x)] += x
    return _norm(_lp(out, 6000), 0.45)


def zap():
    """Faísca elétrica (travou!): estalos + zumbido."""
    t = _t(0.45)
    rng = _rng(23)
    crack = _hp(rng.normal(0, 1, len(t)), 2000) * (rng.random(len(t)) < 0.02) * 6
    buzz = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.25 * _bp(rng.normal(0, 1, len(t)), 800, 4000)
    return _norm((crack + buzz) * np.exp(-t * 5), 0.6)


def pfff():
    """Murchar / pilha acabando: tom que despenca + ar escapando."""
    t = _t(0.9)
    f = 900 * np.exp(-t * 3) + 80
    tone = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 2.5) * 0.6
    ar = _bp(_rng(24).normal(0, 1, len(t)), 1500, 6000) * np.exp(-t * 3) * 0.5
    return _norm(_lp(tone, 4000) + ar, 0.6)


def splash():
    """Água: respingo (onda, poça, mergulho)."""
    t = _t(0.8)
    rng = _rng(25)
    x = _bp(rng.normal(0, 1, len(t)), 700, 7000) * np.exp(-t * 6)
    for k in range(10):                                         # gotinhas
        i = int(rng.uniform(0.05, 0.6) * SR)
        tt = _t(0.04)
        g = np.sin(2 * np.pi * np.cumsum(rng.uniform(900, 1800) * (1 + 3 * tt / 0.04)) / SR) * np.exp(-tt * 60) * 0.4
        x[i:i + len(g)] += g[: len(x) - i]
    return _norm(x, 0.6)


def palminhas():
    """Três palminhas."""
    out = np.zeros(int(0.9 * SR))
    rng = _rng(26)
    for k in range(3):
        n = int(0.06 * SR)
        h = _bp(rng.normal(0, 1, n), 900, 5000) * np.exp(-np.linspace(0, 9, n))
        i = int(k * 0.26 * SR)
        out[i:i + n] += h
    return _norm(out, 0.6)


def tambor():
    """Rufar curto + prato (revelação, "tcharam!")."""
    out = np.zeros(int(1.4 * SR))
    rng = _rng(27)
    for k in range(18):
        n = int(0.05 * SR)
        h = _bp(rng.normal(0, 1, n), 150, 2500) * np.exp(-np.linspace(0, 7, n)) * (0.4 + 0.6 * k / 18)
        i = int(k * 0.045 * SR)
        out[i:i + n] += h
    t = _t(0.6)
    i = int(0.82 * SR)
    prato = _hp(rng.normal(0, 1, len(t)), 5000) * np.exp(-t * 5) * 0.8
    out[i:i + len(t)] += prato[: len(out) - i]
    return _norm(out, 0.6)


# efeitos gravados (bichos, crianças): .wav em library/audio/sfx/<pasta>/<id>.wav — origem e licença em LICENCAS.md
LIB_SFX = Path(__file__).resolve().parents[2] / "library" / "audio" / "sfx"


def gravados() -> dict[str, Path]:
    """Efeitos gravados utilizáveis: só os que têm origem e licença anotadas em LICENCAS.md (primeira coluna = arquivo)."""
    lic = LIB_SFX / "LICENCAS.md"
    if not lic.exists():
        return {}
    ok = {c.split("|")[1].strip() for c in lic.read_text(encoding="utf-8").splitlines() if c.startswith("|") and c.count("|") >= 4}
    return {f.stem: f for f in sorted(LIB_SFX.rglob("*.wav")) if f.name in ok}


def ids() -> set[str]:
    return set(CATALOG) | set(gravados())


CATALOG = {"pizz_1": pizz_1, "pizz_2": pizz_2, "pizz_3": pizz_3, "whistle_up": whistle_up, "whistle_down": whistle_down,
           "pop": pop, "zip": zip, "tink": tink, "patter": patter, "bonk": bonk, "thud": thud, "rustle": rustle,
           "tweets": tweets, "flutter": flutter, "munch": munch,
           "boing": boing, "whoosh": whoosh, "ding": ding, "plim": plim, "bip_bop": bip_bop, "bips": bips, "zap": zap,
           "pfff": pfff, "splash": splash, "palminhas": palminhas, "tambor": tambor}


def get(sfx_id: str, lib_dir: Path | None = None) -> np.ndarray:
    """Efeito por id: gravado (library/audio/sfx/**/<id>.wav) tem prioridade; senão o sintetizado do CATALOG."""
    f = gravados().get(sfx_id) or (lib_dir / f"{sfx_id}.wav" if lib_dir is not None else None)
    if f is not None and f.exists():
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
