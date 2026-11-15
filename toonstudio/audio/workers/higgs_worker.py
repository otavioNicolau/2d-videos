"""(Copiado de ~/videos/backend/vidgen/tts/higgs_worker.py — ADR-0006.)
Processo auxiliar do Higgs TTS 3 (Boson AI). Roda no venv isolado .venv-higgs (transformers >= 5.5,
bitsandbytes). Carrega o modelo uma vez, em 4 bits (cabe numa GPU de 6 GB), e atende pedidos (ADR-0016).

Protocolo (linhas JSON): recebe em stdin
  {"text", "ref", "ref_text", "seed", "max_new_tokens", "temperature", "out"}
e responde em stdout {"ok": true, "sr": 24000, "dur": s} ou {"ok": false, "error": "..."}.
A primeira linha emitida é {"ready": true, "device": ...}.
Modelo: multimodalart/higgs-audio-v3-tts-4b-transformers (pesos originais da Boson; código revisado em 2026-11-12).
Licença: Boson Higgs TTS 3 — Creator Use Grant (II-A): vídeos monetizados exigem o aviso na descrição.
"""
import json
import os
import sys
import warnings

proto = os.fdopen(os.dup(sys.stdout.fileno()), "w", buffering=1)
sys.stdout = sys.stderr
warnings.filterwarnings("ignore")

REPO = "multimodalart/higgs-audio-v3-tts-4b-transformers"


def main() -> None:
    import torch
    import torchaudio
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    tok = AutoTokenizer.from_pretrained(REPO)
    q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                           llm_int8_skip_modules=["audio", "codebook", "lm_head", "embed"])
    model = AutoModelForCausalLM.from_pretrained(REPO, trust_remote_code=True, dtype=torch.bfloat16,
                                                 quantization_config=q, device_map="cuda").eval()
    sr_out = model.config.sample_rate
    refs: dict[str, tuple] = {}
    proto.write(json.dumps({"ready": True, "device": "cuda", "sr": sr_out}) + "\n")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            if req["ref"] not in refs:
                refs[req["ref"]] = torchaudio.load(req["ref"])
            ref, sr = refs[req["ref"]]
            torch.manual_seed(int(req.get("seed", 0)))
            with torch.inference_mode():
                wav = model.generate_speech(req["text"], tok, reference_audio=ref, reference_sample_rate=sr,
                                            reference_text=req.get("ref_text"), temperature=float(req.get("temperature", 0.7)),
                                            top_p=0.95, max_new_tokens=int(req.get("max_new_tokens", 2048)))
            torchaudio.save(req["out"], wav.unsqueeze(0), sr_out)
            proto.write(json.dumps({"ok": True, "sr": sr_out, "dur": len(wav) / sr_out}) + "\n")
        except Exception as e:  # responde o erro e continua vivo
            proto.write(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}) + "\n")


if __name__ == "__main__":
    main()
