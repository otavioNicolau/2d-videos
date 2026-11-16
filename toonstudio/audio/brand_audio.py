"""Peças fixas de áudio do canal (vinheta de abertura e chamada final): corte automático na batida.

O Suno gera trechos mais longos que o necessário; aqui escolhemos a melhor janela:
- começa no primeiro ataque forte (sem silêncio no início);
- termina numa BATIDA, no máximo em `max_len` segundos, de preferência num pico (golpe final) seguido de queda;
- fade-out curto (sem clique), volume igualado ao das músicas (loudnorm −14 LUFS);
- o original fica intocado; a versão final vai para library/audio/marca/.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from ..core.config import LIBRARY, StudioError, tool


def trim_on_beat(src: Path, name: str, max_len: float = 5.0, min_len: float = 2.5, start: float | None = None,
                 end: float | None = None, fade: float = 0.25) -> dict:
    import librosa
    y, sr = librosa.load(str(src), sr=44100, mono=True)
    if not len(y):
        raise StudioError(f"áudio vazio: {src}")
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    times = librosa.times_like(onset, sr=sr)
    _, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, units="time")
    rms = librosa.feature.rms(y=y)[0]
    rt = librosa.times_like(rms, sr=sr)
    if start is None:   # primeiro ataque forte
        thr = 0.25 * onset.max()
        start = float(times[np.argmax(onset > thr)])
        start = max(0.0, start - 0.03)
    if end is None:
        cands = [b for b in beats if min_len <= b - start <= max_len]
        if not cands:
            end = start + max_len
        else:
            # prefere a batida com mais energia logo antes (golpe final) e queda logo depois
            def score(b):
                i = int(np.searchsorted(rt, b))
                before = rms[max(0, i - 8):i].mean() if i > 0 else 0
                after = rms[i:i + 8].mean() if i < len(rms) else 0
                return before - 0.6 * after + 0.02 * (b - start)
            end = max(cands, key=score) + 0.35          # deixa o golpe soar um pouco
            end = min(end, start + max_len)
    dur = end - start
    if dur > max_len + 1e-6:
        raise StudioError(f"trecho de {dur:.2f}s passa do limite de {max_len}s")
    out_dir = LIBRARY / "audio" / "marca"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{name}.wav"
    subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
                    "-af", f"afade=t=in:st=0:d=0.01,afade=t=out:st={max(0.0, dur - fade):.3f}:d={fade},"
                           f"loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", "48000", "-ac", "2", str(out)], check=True)
    a, osr = sf.read(out)
    return {"arquivo": str(out), "inicio": round(start, 3), "fim": round(end, 3), "duracao": round(len(a) / osr, 3)}
