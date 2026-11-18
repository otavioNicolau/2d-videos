"""Transcreve as músicas de referência (só para análise; o texto fica em referencias/, fora do git)."""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf
from faster_whisper import WhisperModel
pasta = Path(sys.argv[1])
out = pasta / "transcricoes"; out.mkdir(exist_ok=True)
m = WhisperModel("small", device="cpu", compute_type="int8")
for wav in sorted((pasta / "audio").glob("*_full.wav")):
    nome = wav.stem[:-5]
    js = out / f"{nome}.json"
    if js.exists():
        continue
    vs = pasta / "stems_full" / "htdemucs" / wav.stem / "vocals.wav"
    a, sr = sf.read(str(vs if vs.exists() else wav), dtype="float32")
    a = a.mean(1) if a.ndim > 1 else a
    a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * 16000 / sr)), np.arange(len(a)), a).astype(np.float32)
    segs, _ = m.transcribe(a, language="pt", vad_filter=False, beam_size=5, condition_on_previous_text=False)
    linhas = [{"s": round(s.start, 1), "e": round(s.end, 1), "t": s.text.strip()} for s in segs]
    js.write_text(json.dumps(linhas, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok", nome, len(linhas), flush=True)
