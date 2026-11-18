"""Análise das músicas de referência (Animadinhos) — gênero, instrumentos, batida e som. 18/11/2026.

Etapa A (.venv-audio: demucs + panns_inference):  separa bateria/baixo/outros/voz de cada trecho de 60 s e reconhece
  instrumentos (no instrumental) e gêneros (na música inteira do trecho) com o modelo PANNs/AudioSet.
Etapa B (.venv: librosa):  andamento, onde caem bumbo, caixa/palma e chimbal/shaker na semicolcheia, peso de cada faixa
  separada, equilíbrio de frequências e volume.

Uso:
  .venv-audio/bin/python scripts/referencias/analisar_referencias.py A referencias/animadinhos
  .venv/bin/python       scripts/referencias/analisar_referencias.py B referencias/animadinhos
  (também serve para as NOSSAS músicas: basta uma pasta com audio/<nome>.wav e audio/<nome>_full.wav)
Saída: <pasta>/analise/<nome>.json  (números só; nada de letra)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

INST = ["Drum kit", "Drum machine", "Snare drum", "Bass drum", "Hi-hat", "Cymbal", "Drum roll", "Rimshot", "Percussion", "Tambourine",
        "Maraca", "Rattle (instrument)", "Cowbell", "Clapping", "Hands", "Timbales", "Steelpan", "Marimba, xylophone", "Glockenspiel",
        "Whistle", "Accordion", "Harmonica", "Synthesizer", "Sampler", "Keyboard (musical)", "Electronic organ", "Hammond organ",
        "Piano", "Electric piano", "Electric guitar", "Acoustic guitar", "Guitar", "Bass guitar", "Ukulele", "Plucked string instrument",
        "Brass instrument", "Trumpet", "Trombone", "Saxophone", "Flute", "Violin, fiddle", "Bowed string instrument", "Boing",
        "Jingle, tinkle", "Ding-dong", "Sound effect", "Whoosh, swoosh, swish", "Beep, bleep", "Bell", "Zither", "Banjo", "Mandolin"]
GEN = ["Salsa music", "Music of Latin America", "Music of Africa", "Afrobeat", "Reggae", "Ska", "Funk", "Pop music", "Rock music",
       "Rock and roll", "Disco", "Electronic music", "Techno", "House music", "Dance music", "Electronic dance music", "Hip hop music",
       "Swing music", "Jazz", "Country", "Bluegrass", "Christian music", "Gospel music", "Funny music", "Happy music", "Video game music",
       "Traditional music", "Polka", "Flamenco", "Music of Asia", "Middle Eastern music", "Children's music", "Soundtrack music",
       "Christmas music", "Exciting music", "Theme music", "Jingle (music)"]


def etapa_a(pasta: Path) -> None:
    from panns_inference import AudioTagging, labels
    at = AudioTagging(checkpoint_path=None, device="cpu")
    idx = {l: i for i, l in enumerate(labels)}
    stems_dir = pasta / "stems"
    out = pasta / "analise"
    out.mkdir(exist_ok=True)

    def tags(a: np.ndarray, sr: int, lista: list[str]) -> dict:
        a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * 32000 / sr)), np.arange(len(a)), a).astype(np.float32)
        W = 320000
        P = np.array([at.inference(a[i:i + W][None, :])[0][0] for i in range(0, max(1, len(a) - W + 1), W)])
        m = P.mean(0)
        return {l: round(float(m[idx[l]]), 3) for l in lista if l in idx}

    for wav in sorted((pasta / "audio").glob("*.wav")):
        if wav.stem.endswith("_full"):
            continue
        js = out / f"{wav.stem}.json"
        d = json.loads(js.read_text(encoding="utf-8")) if js.exists() else {}
        if "instrumentos" in d:
            continue
        sd = stems_dir / "htdemucs" / wav.stem
        if not (sd / "drums.wav").exists():
            subprocess.run([sys.executable, "-m", "demucs", "-n", "htdemucs", "-o", str(stems_dir), str(wav)], check=True,
                           capture_output=True)
        parts = {k: sf.read(str(sd / f"{k}.wav"), dtype="float32")[0].mean(1) for k in ("drums", "bass", "other", "vocals")}
        inst = parts["drums"] + parts["bass"] + parts["other"]
        mix, sr = sf.read(str(wav), dtype="float32")
        d["instrumentos"] = tags(inst, 44100, INST)
        d["generos"] = tags(mix.mean(1), sr, GEN)
        d["generos_instrumental"] = tags(inst, 44100, GEN)
        js.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print("A ok:", wav.stem, flush=True)


def etapa_b(pasta: Path) -> None:
    import librosa
    out = pasta / "analise"
    bands = [(20, 60), (60, 250), (250, 1000), (1000, 2500), (2500, 6000), (6000, 10000), (10000, 16000)]

    def onsets(x, sr, lo, hi):
        S = np.abs(librosa.stft(x, n_fft=2048, hop_length=256))
        f = librosa.fft_frequencies(sr=sr, n_fft=2048)
        env = np.maximum(0, np.diff(np.log1p(S[(f >= lo) & (f < hi)].sum(0)), prepend=0))
        pk = librosa.util.peak_pick(env, pre_max=3, post_max=3, pre_avg=8, post_avg=8, delta=np.percentile(env, 90) * 0.5, wait=4)
        return librosa.frames_to_time(pk, sr=sr, hop_length=256)

    for wav in sorted((pasta / "audio").glob("*.wav")):
        if wav.stem.endswith("_full"):
            continue
        js = out / f"{wav.stem}.json"
        d = json.loads(js.read_text(encoding="utf-8")) if js.exists() else {}
        y, sr = sf.read(str(wav), dtype="float32")
        y = y.mean(1)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
        d["bpm"] = round(float(np.atleast_1d(tempo)[0]), 1)
        sd = pasta / "stems" / "htdemucs" / wav.stem
        stems = {k: sf.read(str(sd / f"{k}.wav"), dtype="float32")[0].mean(1) for k in ("drums", "bass", "other", "vocals")}
        en = {k: float((v ** 2).mean()) for k, v in stems.items()}
        tot = sum(en.values())
        d["peso_faixas"] = {k: round(100 * v / tot, 1) for k, v in en.items()}
        grade = {}
        for nome, lo, hi in (("bumbo", 30, 120), ("caixa_palma", 1200, 5000), ("chimbal_shaker", 7000, 16000)):
            t = onsets(stems["drums"], 44100, lo, hi)
            ph = []
            for ti in t:
                k = np.searchsorted(beats, ti) - 1
                if 0 <= k < len(beats) - 1:
                    u = (ti - beats[k]) / (beats[k + 1] - beats[k])
                    ph.append(int(round(u * 4)) % 4)
            h = np.bincount(ph, minlength=4)[:4]
            grade[nome] = {"por_minuto": round(60 * len(t) / (len(stems["drums"]) / 44100)),
                           "no_tempo_%": round(100 * h[0] / max(1, h.sum())), "contratempo_%": round(100 * h[2] / max(1, h.sum())),
                           "semicolcheias_%": round(100 * (h[1] + h[3]) / max(1, h.sum()))}
        d["batida"] = grade
        full, srf = sf.read(str(pasta / "audio" / f"{wav.stem}_full.wav"), dtype="float32")
        N = 8192
        win = np.hanning(N)
        acc = np.zeros(N // 2 + 1)
        for i in range(0, len(full) - N, N):
            acc += np.abs(np.fft.rfft(full[i:i + N] * win)) ** 2
        f = np.fft.rfftfreq(N, 1 / srf)
        t_ = acc[f >= 20].sum()
        d["som_%"] = dict(zip(["sub", "grave", "medio_grave", "medio", "presenca", "agudo", "brilho"],
                              [round(100 * acc[(f >= lo) & (f < hi)].sum() / t_, 1) for lo, hi in bands]))
        d["duracao_s"] = round(len(full) / srf, 1)
        # largura da voz (lado/meio): referência 0,00–0,02 = uma voz seca no centro
        vv, _ = sf.read(str(sd / "vocals.wav"), dtype="float32")
        if vv.ndim == 2:
            mm, ss = (vv[:, 0] + vv[:, 1]) / 2, (vv[:, 0] - vv[:, 1]) / 2
            em = librosa.feature.rms(y=mm, hop_length=1024)[0]
            es = librosa.feature.rms(y=ss, hop_length=1024)[0]
            msk = em > np.percentile(em, 50)
            d["largura_voz"] = round(float(np.median(es[msk] / (em[msk] + 1e-9))), 3)
        # batida de teclado: o quanto cada ataque da bateria se parece com outro (referência 0,95–0,98 = loop pronto)
        dr = stems["drums"]
        on = librosa.onset.onset_detect(y=dr, sr=44100, units="time")
        Sx = np.abs(librosa.stft(dr, n_fft=1024, hop_length=256))
        fr = librosa.time_to_frames(on, sr=44100, hop_length=256)
        fr = fr[fr < Sx.shape[1] - 2]
        if len(fr) > 5:
            V = np.log1p(Sx[:, fr]).T
            V = (V - V.mean(1, keepdims=True)) / (V.std(1, keepdims=True) + 1e-9)
            C = np.corrcoef(V)
            np.fill_diagonal(C, -1)
            d["batidas_identicas"] = round(float(np.median(C.max(1))), 3)
        js.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print("B ok:", wav.stem, d["bpm"], flush=True)


if __name__ == "__main__":
    {"A": etapa_a, "B": etapa_b}[sys.argv[1]](Path(sys.argv[2]))
