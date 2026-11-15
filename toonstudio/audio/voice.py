"""Dublagem: gera cada fala na voz do personagem, escolhe a melhor tomada e extrai os visemas.

Fluxo por fala (cache por hash do texto + voz + emoção):
  Higgs TTS (várias sementes) → transcrição cega (Whisper) → similaridade com o texto → melhor tomada →
  corte de silêncio → tom/tempo do personagem (rubberband) → Rhubarb (fonético, pt-BR) → visemas A–H/X.
Reserva: Kokoro (vozes pt-BR), se o Higgs não estiver disponível.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import soundfile as sf

from ..core.config import ROOT, StudioError, setting, sha, tool

WORKERS = Path(__file__).parent / "workers"
EMOTIONS = {
    "medo": ["emotion:fear"], "tristeza": ["emotion:sadness"], "raiva": ["emotion:anger"], "alegria": ["emotion:elation"],
    "surpresa": ["emotion:surprise"], "zombaria": ["emotion:amusement"], "orgulho": ["emotion:pride"],
    "firme": ["emotion:determination"], "confusao": ["emotion:confusion"], "entusiasmo": ["emotion:enthusiasm"],
    "grito": ["style:shouting"], "sussurro": ["style:whispering"], "rapido": ["prosody:speed_fast"],
    "lento": ["prosody:speed_slow"], "agudo": ["prosody:pitch_high"], "grave": ["prosody:pitch_low"],
    "intenso": ["prosody:expressive_high"],
}


class _Worker:
    def __init__(self, python: str, script: Path, *args: str):
        self.cmd = [python, str(script), *args]
        self.p: subprocess.Popen | None = None

    def call(self, req: dict, timeout_hint: str = "") -> dict:
        if self.p is None or self.p.poll() is not None:
            if not Path(self.cmd[0]).exists():
                raise StudioError(f"interpretador ausente: {self.cmd[0]} (ver config.yaml → audio)")
            self.p = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                      text=True, bufsize=1)
            first = self.p.stdout.readline()
            if not first or not json.loads(first).get("ready"):
                raise StudioError(f"worker não iniciou: {' '.join(self.cmd)}")
        self.p.stdin.write(json.dumps(req, ensure_ascii=False) + "\n")
        self.p.stdin.flush()
        resp = json.loads(self.p.stdout.readline() or '{"ok": false, "error": "worker morreu"}')
        if not resp.get("ok"):
            raise StudioError(f"worker {Path(self.cmd[1]).stem}: {resp.get('error')}")
        return resp

    def close(self):
        if self.p and self.p.poll() is None:
            self.p.stdin.close()
            self.p.wait(timeout=30)


_higgs: _Worker | None = None
_aux: _Worker | None = None


def higgs() -> _Worker:
    global _higgs
    if _higgs is None:
        _higgs = _Worker(setting("audio", "higgs_python"), WORKERS / "higgs_worker.py")
    return _higgs


def aux() -> _Worker:
    global _aux
    if _aux is None:
        _aux = _Worker(setting("audio", "aux_python"), WORKERS / "aux_worker.py", str(setting("audio", "whisper_model", "small")))
    return _aux


def shutdown():
    for w in (_higgs, _aux):
        if w:
            w.close()


def _norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z ]+", " ", s).split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm_text(a), _norm_text(b)).ratio()


def _trim(audio: np.ndarray, sr: int, thr_db: float = -42, pad: float = 0.05) -> np.ndarray:
    if not len(audio):
        return audio
    win = int(0.01 * sr)
    e = np.sqrt(np.convolve(audio ** 2, np.ones(win) / win, mode="same"))
    on = np.where(20 * np.log10(e + 1e-9) > thr_db)[0]
    if not len(on):
        return audio
    a, b = max(0, on[0] - int(pad * sr)), min(len(audio), on[-1] + int(pad * sr))
    return audio[a:b]


def _voice_fx(src: Path, dst: Path, pitch: float, tempo: float, formant: str) -> None:
    filt = []
    if abs(pitch) > 0.01:
        filt.append(f"rubberband=pitch={2 ** (pitch / 12):.5f}:formant={formant}:pitchq=quality")
    if abs(tempo - 1) > 0.01:
        filt.append(f"atempo={tempo:.3f}")
    filt.append("loudnorm=I=-18:TP=-2:LRA=7")
    subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(src), "-af", ",".join(filt), "-ar", "48000",
                    "-ac", "1", str(dst)], check=True)


def synth_line(text: str, voice: dict, emotion: list[str], out_wav: Path, takes: int = 4, log=print) -> dict:
    """Gera a fala, escolhe a melhor tomada e grava `out_wav` (48 kHz mono). Retorna metadados."""
    tags = list(voice.get("tags", []))
    for e in emotion:
        tags += EMOTIONS.get(e, [])
    tagged = "".join(f"<|{t}|>" for t in dict.fromkeys(tags)) + text
    ref = Path(setting("audio", "voice_refs")) / f"{voice['ref']}.wav"
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    best = None
    with tempfile.TemporaryDirectory() as td:
        for k in range(takes):
            raw = Path(td) / f"take{k}.wav"
            try:
                if voice["provider"] == "higgs":
                    words = len(text.split())
                    higgs().call({"text": tagged, "ref": str(ref), "ref_text": ref.with_suffix(".txt").read_text(encoding="utf-8").strip(),
                                  "seed": 11 + 7 * k, "temperature": 0.7, "max_new_tokens": int(25 * (words * 0.9 + 4)),
                                  "out": str(raw)})
                else:
                    aux().call({"op": "kokoro", "text": text, "voice": voice["ref"], "speed": 1.0, "out": str(raw)})
            except StudioError as e:
                log(f"    tomada {k}: falhou ({e})")
                continue
            a, sr = sf.read(raw, dtype="float32")
            if a.ndim > 1:
                a = a.mean(axis=1)
            a = _trim(a, sr)
            dur = len(a) / sr
            sf.write(raw, a, sr)
            heard = aux().call({"op": "asr", "wav": str(raw)})["text"]
            sim = similarity(heard, text)
            # duração plausível: ~0,05–0,6 s por caractere falado
            plaus = 0.04 * len(text) <= dur <= 0.16 * len(text) + 1.2
            score = sim - (0 if plaus else 0.3)
            log(f"    tomada {k}: {dur:.2f}s sim={sim:.2f} ouvido='{heard}'")
            if best is None or score > best[0]:
                best = (score, raw.read_bytes(), sr, heard, sim, dur)
            if sim >= 0.92 and plaus:
                break
        if best is None:
            raise StudioError(f"nenhuma tomada gerada para: {text}")
        chosen = Path(td) / "best.wav"
        chosen.write_bytes(best[1])
        _voice_fx(chosen, out_wav, float(voice.get("pitch", 0)), float(voice.get("tempo", 1.0)), voice.get("formant", "preserved"))
    a, sr = sf.read(out_wav, dtype="float32")
    return {"text": text, "heard": best[3], "similarity": round(best[4], 3), "duration": len(a) / sr,
            "warning": None if best[4] >= 0.8 else "transcrição diverge do texto — revisar a pronúncia"}


def visemes(wav: Path, text: str, out_json: Path) -> list[tuple[float, str]]:
    """Rhubarb Lip Sync (reconhecedor fonético, adequado a português) → [(t, boca)]."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        dialog = f.name
    subprocess.run([tool("rhubarb"), "-r", "phonetic", "-f", "json", "--extendedShapes", "GHX", "-d", dialog, "-q",
                    str(wav), "-o", str(out_json)], check=True, capture_output=True)
    Path(dialog).unlink(missing_ok=True)
    cues = json.loads(out_json.read_text())["mouthCues"]
    return [(c["start"], c["value"]) for c in cues]


def line_key(text: str, voice: dict, emotion: list[str]) -> str:
    return sha({"text": text, "voice": voice, "emotion": emotion, "v": 2})
