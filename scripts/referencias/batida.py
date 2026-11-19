"""Raio-x da BATIDA: o que faz a batida ser contagiante, medido na faixa de bateria (Demucs) das referências e das nossas.

Pedido do usuário (19/11/2026): "temos que focar nas batidas do som contagiante que faz a pessoa gostar".
Para cada música (trecho de 60 s já separado em referencias/*/stems/htdemucs/<nome>/drums.wav e bass.wav):
- bumbo em todo tempo (four-on-the-floor) · palma/caixa no 2 e no 4 · contratempo (síncope) · densidade de golpes
- "pegada": quanto o volume pulsa no ritmo da batida (o que faz o corpo mexer)
- baixo sincopado (baixo fora do tempo forte = "bounce")
- padrão de 16 posições por compasso (bumbo e palma), para ver o desenho da batida
Uso: .venv/bin/python scripts/referencias/batida.py            → tabela referência × nossas + padrões
Saída: referencias/batida.json (fora do git) e o resumo na tela.
"""
from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

import librosa
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "referencias"
SR = 22050


def _env(y, lo, hi):
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=256))
    f = librosa.fft_frequencies(sr=SR, n_fft=2048)
    band = S[(f >= lo) & (f < hi)].sum(0)
    o = np.maximum(0, np.diff(np.log1p(band), prepend=np.log1p(band[0])))
    return o / (o.max() or 1)


def medir(pasta: Path) -> dict | None:
    dr, ba = pasta / "drums.wav", pasta / "bass.wav"
    if not dr.exists():
        return None
    y, _ = librosa.load(dr, sr=SR, mono=True)
    yb = librosa.load(ba, sr=SR, mono=True)[0] if ba.exists() else None
    hop = 256
    tempo, beats = librosa.beat.beat_track(y=y, sr=SR, hop_length=hop, units="frames")
    tempo = float(np.atleast_1d(tempo)[0])
    if len(beats) < 16:
        return None
    kick, clap = _env(y, 30, 150), _env(y, 1500, 7000)
    bass = _env(yb, 30, 250) if yb is not None else None
    # grade de 16 posições por compasso (4 tempos × 4 semicolcheias), interpolada entre as batidas detectadas
    grid = []
    for i in range(len(beats) - 1):
        a, b = beats[i], beats[i + 1]
        grid += [int(a + (b - a) * k / 4) for k in range(4)]
    grid = np.array(grid)
    nbar = len(grid) // 16
    grid = grid[: nbar * 16]

    def padrao(env):
        v = np.array([env[max(0, g - 2): g + 3].max() for g in grid]).reshape(nbar, 16)
        return v.mean(0)

    pk, pc = padrao(kick), padrao(clap)
    pb = padrao(bass) if bass is not None else np.zeros(16)
    tempos = [0, 4, 8, 12]
    off = [i for i in range(16) if i not in tempos]

    def frac(p, pos):
        return float(p[pos].sum() / (p.sum() or 1))

    # pegada: autocorrelação da energia da bateria no período de 1 tempo (pulso claro e forte)
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    per = int(np.median(np.diff(beats)))
    r = rms - rms.mean()
    pegada = float(np.dot(r[:-per], r[per:]) / (np.dot(r, r) or 1))
    golpes = len(librosa.onset.onset_detect(y=y, sr=SR, hop_length=hop)) / max(1, len(beats))
    return {"bpm": round(tempo), "bumbo_no_tempo": round(frac(pk, tempos) * 4 / 4, 2),
            "four_on_floor": round(float(np.mean([pk[t] for t in tempos]) / (pk.max() or 1)), 2),
            "palma_2_e_4": round(float((pc[4] + pc[12]) / 2 / (pc.max() or 1)), 2),
            "sincope": round(frac(pc + pk, off), 2), "baixo_sincopado": round(frac(pb, off), 2),
            "golpes_por_tempo": round(golpes, 2), "pegada": round(pegada, 2),
            "padrao_bumbo": "".join("X" if v > 0.6 * pk.max() else ("x" if v > 0.35 * pk.max() else ".") for v in pk),
            "padrao_palma": "".join("X" if v > 0.6 * pc.max() else ("x" if v > 0.35 * pc.max() else ".") for v in pc)}


def main():
    out = {"referencia": {}, "nossas": {}}
    for grupo, base in (("referencia", REF / "animadinhos" / "stems" / "htdemucs"), ("nossas", REF / "nossas" / "stems" / "htdemucs")):
        for p in sorted(base.iterdir()):
            if p.name.endswith("_full"):
                continue
            m = medir(p)
            if m:
                out[grupo][p.name] = m
                print(f"{grupo[:3]} {p.name[:28]:28s} bpm {m['bpm']:3d} bumbo4 {m['four_on_floor']:.2f} palma2e4 {m['palma_2_e_4']:.2f} "
                      f"síncope {m['sincope']:.2f} baixoSinc {m['baixo_sincopado']:.2f} golpes {m['golpes_por_tempo']:.1f} "
                      f"pegada {m['pegada']:.2f}  B {m['padrao_bumbo']}  P {m['padrao_palma']}", flush=True)
    (REF / "batida.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ks = ["four_on_floor", "palma_2_e_4", "sincope", "baixo_sincopado", "golpes_por_tempo", "pegada"]
    print("\nMEDIANAS        " + " ".join(k[:12].rjust(12) for k in ks))
    for g in ("referencia", "nossas"):
        print(f"{g:15s} " + " ".join(f"{st.median(v[k] for v in out[g].values()):12.2f}" for k in ks))


if __name__ == "__main__":
    sys.exit(main())
