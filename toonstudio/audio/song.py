"""Análise musical para clipes (ADR-0013): importação sem alterar o original, separação de voz, batidas, intensidade,
trechos cantados, letra palavra a palavra e visemas do canto. Saída: `analise/song.json` — revisável e editável.

Não presume perfeição: seções e tempos da letra são sugestões; o arquivo é a fonte da verdade depois de revisado.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from ..core.config import ROOT, StudioError, setting, tool


def import_song(src: Path, project_dir: Path) -> dict:
    """Copia o original (somente leitura) e cria a cópia de trabalho WAV. O original nunca é modificado."""
    mdir = project_dir / "musica"
    mdir.mkdir(parents=True, exist_ok=True)
    orig = mdir / ("original" + src.suffix.lower())
    if not orig.exists():
        shutil.copy2(src, orig)
        orig.chmod(0o444)
    work = mdir / "trabalho.wav"
    subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(orig), "-vn", "-ar", "44100", "-ac", "2", str(work)],
                   check=True)
    return {"original": str(orig), "work": str(work)}


def separate_vocals(work: Path, out_dir: Path) -> Path:
    vocals = out_dir / "stems" / "htdemucs" / work.stem / "vocals.wav"
    if not vocals.exists():
        py = ROOT / ".venv-audio" / "bin" / "python"
        r = subprocess.run([str(py), "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs", "-o", str(out_dir / "stems"),
                            str(work)], capture_output=True, text=True)
        if not vocals.exists():
            raise StudioError(f"Demucs falhou:\n{r.stderr[-1500:]}")
    return vocals


def rhythm(work: Path) -> dict:
    import librosa
    y, sr = librosa.load(str(work), sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="frames")
    times = librosa.frames_to_time(beats, sr=sr)
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    # tempo forte: fase (0..3) cujos batimentos têm maior ataque
    strength = onset[np.minimum(beats, len(onset) - 1)]
    phase = int(np.argmax([strength[i::4].mean() if len(strength[i::4]) else 0 for i in range(4)]))
    energy = rms[np.minimum(beats, len(rms) - 1)]
    energy = (energy / (energy.max() or 1)).round(3)
    return {"bpm": float(np.atleast_1d(tempo)[0]), "beats": [round(float(t), 3) for t in times],
            "downbeat_phase": phase, "beat_energy": energy.tolist(), "duration": float(len(y) / sr)}


def vocal_activity(vocals: Path, hop: float = 0.05) -> list[list[float]]:
    """Intervalos com voz (para separar trechos cantados de instrumentais)."""
    a, sr = sf.read(vocals, dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    n = int(hop * sr)
    rms = np.sqrt(np.convolve(a ** 2, np.ones(n) / n, mode="same"))[::n]
    on = rms > max(0.02, np.percentile(rms, 60) * 0.5)
    spans, start = [], None
    for i, v in enumerate(on):
        t = i * hop
        if v and start is None:
            start = t
        if not v and start is not None:
            if t - start > 0.15:
                spans.append([round(start, 2), round(t, 2)])
            start = None
    merged = []
    for s in spans:
        if merged and s[0] - merged[-1][1] < 0.6:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return merged


def lyrics_words(vocals: Path) -> list[dict]:
    from .voice import aux
    r = aux().call({"op": "asr", "wav": str(vocals), "words": True, "lang": "pt"})
    words = []
    for s in r.get("segments", []):
        for w in s["words"]:
            if w["w"]:
                words.append({"w": w["w"], "s": round(w["s"], 3), "e": round(w["e"], 3), "p": round(w["p"], 3)})
    return words


def lines_from_words(words: list[dict], gap: float = 0.55, max_words: int = 7) -> list[dict]:
    """Agrupa palavras em versos (para legenda e cenas): quebra em pausa ou pontuação."""
    lines, cur = [], []
    for w in words:
        punct = cur and cur[-1]["w"][-1:] in ".!?" or (cur and cur[-1]["w"][-1:] == "," and len(cur) >= 3)
        cap = cur and len(cur) >= 3 and w["w"][:1].isupper()        # verso novo começa com maiúscula
        if cur and (w["s"] - cur[-1]["e"] > gap or len(cur) >= max_words or punct or cap):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    return [{"s": l[0]["s"], "e": l[-1]["e"], "text": " ".join(w["w"] for w in l), "words": l} for l in lines]


def sung_visemes(vocals: Path, t0: float, t1: float, text: str, out_json: Path) -> list[tuple[float, str]]:
    """Rhubarb (fonético) num trecho da voz isolada → [(t absoluto, boca)]."""
    a, sr = sf.read(vocals, dtype="float32")
    seg = a[int(t0 * sr):int(t1 * sr)]
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "v.wav"
        sf.write(wav, seg if seg.ndim == 1 else seg.mean(axis=1), sr)
        txt = Path(td) / "t.txt"
        txt.write_text(text, encoding="utf-8")
        subprocess.run([tool("rhubarb"), "-r", "phonetic", "-f", "json", "--extendedShapes", "GHX", "-d", str(txt), "-q",
                        str(wav), "-o", str(out_json)], check=True, capture_output=True)
    cues = json.loads(out_json.read_text())["mouthCues"]
    return [(round(t0 + c["start"], 3), c["value"]) for c in cues]


def analyze(project_dir: Path, log=print) -> Path:
    work = project_dir / "musica" / "trabalho.wav"
    if not work.exists():
        raise StudioError("música não importada: use `toonstudio song import <arquivo> <projeto>`")
    adir = project_dir / "analise"
    adir.mkdir(exist_ok=True)
    log("separando a voz (Demucs)…")
    vocals = separate_vocals(work, adir)
    log("batidas e intensidade…")
    rh = rhythm(work)
    log(f"  {rh['bpm']:.1f} BPM, {len(rh['beats'])} batidas")
    log("trechos cantados…")
    va = vocal_activity(vocals)
    log("letra palavra a palavra (Whisper na voz isolada)…")
    words = lyrics_words(vocals)
    lines = lines_from_words(words)
    out = {"schema": "song-1.0", "files": {"work": str(work), "vocals": str(vocals)}, **rh, "vocal_spans": va,
           "words": words, "lines": [{k: v for k, v in l.items() if k != "words"} for l in lines],
           "sections": [], "notes": "seções preenchidas na revisão (ver docs); tempos podem ser corrigidos à mão"}
    p = adir / "song.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return p
