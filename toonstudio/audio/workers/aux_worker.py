"""Processo auxiliar (roda no ~/videos/.venv): transcrição (faster-whisper) e Kokoro (reserva de voz).

Protocolo (linhas JSON): {"op": "asr", "wav": ..., "lang": "pt"} -> {"ok": true, "text": ...}
                         {"op": "kokoro", "text": ..., "voice": ..., "speed": 1.0, "out": wav} -> {"ok": true}
Primeira linha: {"ready": true}.
"""
import json
import os
import sys
import warnings

proto = os.fdopen(os.dup(sys.stdout.fileno()), "w", buffering=1)
sys.stdout = sys.stderr
warnings.filterwarnings("ignore")


def main() -> None:
    model_name = sys.argv[1] if len(sys.argv) > 1 else "small"
    asr = None
    kpipe = None
    proto.write(json.dumps({"ready": True}) + "\n")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            if req["op"] == "asr":
                if asr is None:
                    from faster_whisper import WhisperModel
                    asr = WhisperModel(model_name, device="cpu", compute_type="int8")
                import numpy as np
                import soundfile as sf
                a, sr = sf.read(req["wav"], dtype="float32")     # sem PyAV (versão incompatível no venv)
                if a.ndim > 1:
                    a = a.mean(axis=1)
                if sr != 16000:
                    n = int(len(a) * 16000 / sr)
                    a = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
                segs, _ = asr.transcribe(a, language=req.get("lang", "pt"), beam_size=5, vad_filter=False)
                proto.write(json.dumps({"ok": True, "text": " ".join(s.text.strip() for s in segs)}) + "\n")
            elif req["op"] == "kokoro":
                import numpy as np
                import soundfile as sf
                if kpipe is None:
                    from kokoro import KPipeline
                    kpipe = KPipeline(lang_code="p", repo_id="hexgrad/Kokoro-82M")
                chunks = [np.asarray(r.audio, dtype=np.float32) for r in kpipe(req["text"], voice=req["voice"],
                                                                                  speed=float(req.get("speed", 1.0)))
                          if r.audio is not None]
                sf.write(req["out"], np.concatenate(chunks), 24000)
                proto.write(json.dumps({"ok": True}) + "\n")
        except Exception as e:  # noqa: BLE001
            proto.write(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}) + "\n")


if __name__ == "__main__":
    main()
