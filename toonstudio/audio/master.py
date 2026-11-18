"""Masterização do áudio final (18/11/2026, pedido do usuário: "o nosso vídeo em volume alto fica ruim de ouvir, o dele não").

Medição contra a referência (Celular do Vovô e Dança do Calango, Animadinhos), energia por faixa de frequência:

    faixa            referência     nossas (Suno cru, 11–13)
    sub 20–60 Hz        16–22%            2–8%      → falta o "empurrão" da batida
    presença 2,5–6 kHz   3–4%            10–11%     → estridente: cansa e machuca no volume alto
    agudo 6–16 kHz      ~0,8%            3–7%       → chiado / sibilância do Suno

`masterizar` mede o equilíbrio da própria faixa e aplica um EQ que aproxima o perfil da referência (correção parcial,
limitada a ±9 dB por faixa, para não criar artefato), depois normaliza a −14 LUFS com pico real de −1 dBTP (padrão do
YouTube: acima disso ele abaixa o volume; abaixo, toca mais baixo que os outros vídeos).
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from ..core.config import tool

# (limite inferior, limite superior, frequência central do ajuste, largura em oitavas, % alvo da energia)
# alvo = mediana de 18 músicas da referência (referencias/animadinhos/analise, 18/11/2026)
FAIXAS = [(20, 60, 45, 1.2, 15.3), (60, 250, 120, 1.6, 31.1), (250, 1000, 500, 1.8, 36.5), (1000, 2500, 1600, 1.3, 11.1),
          (2500, 6000, 3800, 1.3, 5.9), (6000, 10000, 7800, 0.9, 0.7), (10000, 16000, 12500, 0.9, 0.3)]
ALVO_LUFS, PICO_DBTP = -14.0, -1.0
FORCA, LIMITE_DB = 0.75, 9.0


def perfil(wav: Path) -> list[float]:
    """% da energia em cada faixa de FAIXAS (mono, janelas de 8192)."""
    a, sr = sf.read(str(wav), dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    n = 8192
    win = np.hanning(n).astype(np.float32)
    acc = np.zeros(n // 2 + 1)
    for i in range(0, max(1, len(a) - n), n):
        acc += np.abs(np.fft.rfft(a[i:i + n] * win)) ** 2
    f = np.fft.rfftfreq(n, 1 / sr)
    tot = acc[f >= 20].sum() or 1.0
    return [100 * acc[(f >= lo) & (f < hi)].sum() / tot for lo, hi, *_ in FAIXAS]


def cadeia_eq(atual: list[float]) -> tuple[str, list[float]]:
    ganhos = []
    for (_, _, _, _, alvo), p in zip(FAIXAS, atual):
        g = FORCA * 10 * math.log10(max(alvo, 1e-3) / max(p, 1e-3))
        ganhos.append(round(max(-LIMITE_DB, min(LIMITE_DB, g)), 1))
    eq = ["highpass=f=25"] + [f"equalizer=f={fc}:width_type=o:width={w}:g={g}" for (_, _, fc, w, _), g in zip(FAIXAS, ganhos)
                              if abs(g) >= 0.5] + ["lowpass=f=16000"]
    return ",".join(eq), ganhos


def _loudnorm_medida(wav: Path, pre: str) -> dict:
    r = subprocess.run([tool("ffmpeg"), "-hide_banner", "-nostats", "-i", str(wav), "-af",
                        f"{pre},loudnorm=I={ALVO_LUFS}:TP={PICO_DBTP}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    return json.loads(re.findall(r"\{[^{}]*\}", r.stderr, re.S)[-1])


def masterizar(entrada: Path, saida: Path, passadas: int = 2) -> dict:
    """EQ casado com a referência (2 passadas: mede → corrige → mede de novo) + loudnorm linear de 2 etapas."""
    fonte, ganhos_tot = entrada, []
    for i in range(passadas):
        eq, ganhos = cadeia_eq(perfil(fonte))
        tmp = saida.with_name(f"{saida.stem}.eq{i}.wav")
        subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(fonte), "-af", eq, "-ar", "48000", str(tmp)], check=True)
        ganhos_tot.append(ganhos)
        fonte = tmp
    m = _loudnorm_medida(fonte, "anull")
    ln = (f"loudnorm=I={ALVO_LUFS}:TP={PICO_DBTP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(fonte), "-af", f"{ln},alimiter=limit=0.89:level=false",
                    "-ar", "48000", str(saida)], check=True)
    for p in saida.parent.glob(saida.stem + ".eq*.wav"):
        p.unlink()
    return {"perfil_antes": [round(x, 1) for x in perfil(entrada)], "perfil_depois": [round(x, 1) for x in perfil(saida)],
            "ganhos_db": ganhos_tot, "loudnorm": m}
