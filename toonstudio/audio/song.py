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


def analyze(project_dir: Path, log=print, musica: Path | None = None) -> Path:
    """`musica`: pasta da música em musicas/ (ficha + letra) → letra CONHECIDA alinhada ao áudio (legenda e boca exatas)
    e partes da música (verso, refrão, intervalo…) com quem canta. Sem ela, a letra vem só da transcrição."""
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
    sections, coverage = [], None
    if musica is not None:
        from . import composer
        log("alinhando a letra conhecida…")
        al = align_known_lyrics(words, composer.secoes(musica), va)
        lines, sections, coverage = al["lines"], al["sections"], al["coverage"]
        log(f"  {round(100 * coverage)}% das palavras da letra com tempo reconhecido; o resto interpolado")
        (adir / "letra.json").write_text(json.dumps({"source": f"letra conhecida: {musica.name}", "words": words,
                                                     "lines": lines}, ensure_ascii=False, indent=1), encoding="utf-8")
    out = {"schema": "song-1.0", "files": {"work": str(work), "vocals": str(vocals)}, **rh, "vocal_spans": va,
           "words": words, "lines": [{k: v for k, v in l.items() if k != "words"} for l in lines],
           "sections": sections, "lyrics_coverage": coverage, "musica": musica.name if musica else None,
           "notes": "tempos podem ser corrigidos à mão; com letra conhecida, o texto é o da ficha"}
    p = adir / "song.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def _tokens(text: str) -> list[str]:
    from .composer import _norm
    return _norm(text).split()


def _voiced_points(t0: float, t1: float, n: int, spans: list[list[float]] | None) -> list[tuple[float, float]]:
    """n intervalos consecutivos dentro de [t0, t1], só sobre o tempo com voz (spans); sem voz, divide por igual."""
    segs = [(max(a, t0), min(b, t1)) for a, b in (spans or []) if b > t0 and a < t1]
    segs = [(a, b) for a, b in segs if b - a > 0.05]
    if not segs:
        segs = [(t0, t1)] if t1 > t0 else [(t0, t0 + 0.3 * n)]
    total = sum(b - a for a, b in segs)
    step = total / max(1, n)

    def at(x):                       # posição x (em tempo de voz) → tempo absoluto
        for a, b in segs:
            if x <= b - a:
                return a + x
            x -= b - a
        return segs[-1][1]
    return [(at(i * step), at((i + 1) * step)) for i in range(n)]


def _fix_stretched(ws: list[dict], max_gap: float = 2.0, step: float = 0.32, keep: str | None = None) -> None:
    """Se há um buraco > max_gap entre palavras da mesma linha, um lado é colado ao outro. `keep` diz qual lado é o
    verdadeiro ('right' para a 1ª linha de uma parte que vem depois de um intervalo; 'left' para a última antes de um);
    sem pista, fica o lado com mais palavras."""
    if len(ws) < 2:
        return
    for w in ws:                          # uma palavra esticada (interpolada sobre um intervalo) também é um buraco
        if w["e"] - w["s"] > max_gap:
            if keep == "right":
                w["s"] = round(w["e"] - step, 3)
            else:
                w["e"] = round(w["s"] + step, 3)
    gaps = [(ws[i + 1]["s"] - ws[i]["e"], i) for i in range(len(ws) - 1)]
    g, i = max(gaps)
    if g <= max_gap:
        return
    left, right = ws[:i + 1], ws[i + 1:]
    if keep == "right" or (keep is None and len(left) <= len(right)):   # move a esquerda para logo antes da direita
        t = right[0]["s"]
        for w in reversed(left):
            w["e"], w["s"] = round(t, 3), round(t - step, 3)
            t -= step
    else:                                 # move a direita para logo depois da esquerda
        t = left[-1]["e"]
        for w in right:
            w["s"], w["e"] = round(t, 3), round(t + step, 3)
            t += step


def align_known_lyrics(words: list[dict], sections: list[dict], spans: list[list[float]] | None = None) -> dict:
    """Alinha a letra CONHECIDA (partes da ficha) às palavras transcritas (com tempo) da voz isolada.

    A comparação é letra a letra (tolera "zunzun ceguei" × "zum, zum, cheguei"). A transcrição só dá os tempos: o texto
    exibido e usado na boca é sempre o da letra. Palavras sem correspondência ganham tempo distribuído sobre os trechos
    com voz (`spans`) entre as vizinhas reconhecidas. Retorna {lines, sections, coverage}."""
    from difflib import SequenceMatcher
    from .composer import _norm
    hc, ht = [], []                       # caracteres ouvidos e seus tempos
    for w in words:
        s = _norm(w["w"]).replace(" ", "")
        for i, ch in enumerate(s):
            d = (w["e"] - w["s"]) / max(1, len(s))
            hc.append(ch)
            ht.append((w["s"] + i * d, w["s"] + (i + 1) * d))
    disp, ec = [], []                     # (seção, linha, palavra exibida, [índices de caractere]); caracteres esperados
    for si, s in enumerate(sections):
        for li, line in enumerate(s["linhas"]):
            for dw in line.split():
                cs = _norm(dw).replace(" ", "")
                disp.append((si, li, dw, list(range(len(ec), len(ec) + len(cs)))))
                ec += list(cs)
    t_of: dict[int, tuple[float, float]] = {}
    for b in SequenceMatcher(None, ec, hc, autojunk=False).get_matching_blocks():
        if b.size >= 2:                   # casamentos de 1 letra solta são ruído
            for k in range(b.size):
                t_of[b.a + k] = ht[b.b + k]
    anchors = []
    for _, _, _, idx in disp:
        ts = [t_of[i] for i in idx if i in t_of]
        ok = idx and len(ts) / len(idx) >= 0.5
        anchors.append((min(a for a, _ in ts), max(b for _, b in ts)) if ok else None)
    known = [i for i, a in enumerate(anchors) if a]
    if not known:
        raise ValueError("nenhuma palavra da letra foi reconhecida no áudio")
    first_voice = spans[0][0] if spans else max(0.0, anchors[known[0]][0] - 2.0)
    last_voice = spans[-1][1] if spans else anchors[known[-1]][1] + 2.0
    times: list[tuple[float, float] | None] = list(anchors)
    i = 0
    while i < len(disp):              # preenche cada sequência de palavras sem tempo
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(disp) and times[j] is None:
            j += 1
        t0 = times[i - 1][1] if i > 0 else min(first_voice, times[j][0] if j < len(disp) else first_voice)
        t1 = times[j][0] if j < len(disp) else max(last_voice, t0 + 0.3 * (j - i))
        for k, iv in enumerate(_voiced_points(t0, t1, j - i, spans)):
            times[i + k] = iv
        i = j
    lines, cur = [], None
    for (si, li, dw, _), (s, e), a in zip(disp, times, anchors):
        if cur is None or cur["_k"] != (si, li):
            cur = {"_k": (si, li), "secao": si, "words": [], "ok": 0}
            lines.append(cur)
        cur["words"].append({"w": dw.replace("(", "").replace(")", ""),  # parêntese só orienta o Suno (coro)
                              "s": round(max(0.0, s), 3), "e": round(max(s + 0.05, e), 3)})
        cur["ok"] += 1 if a else 0
    inst = ("intervalo", "virada", "parada", "intro")
    for n, l in enumerate(lines):         # palavra casada com uma repetição vizinha (ex.: bordão cantado 2×) estica a linha
        si = l["secao"]
        first = n == 0 or lines[n - 1]["secao"] != si
        last = n == len(lines) - 1 or lines[n + 1]["secao"] != si
        before = [sections[k]["tipo"] for k in range(si) if not sections[k]["linhas"] or k == si - 1]
        after_inst = first and si > 0 and sections[si - 1]["tipo"] in inst or (first and before[-2:] and before[-1] in inst)
        before_inst = last and si + 1 < len(sections) and sections[si + 1]["tipo"] in inst
        _fix_stretched(l["words"], keep="right" if after_inst else "left" if before_inst else None)
    out_lines = [{"s": l["words"][0]["s"], "e": l["words"][-1]["e"], "text": " ".join(w["w"] for w in l["words"]),
                  "secao": l["secao"], "confianca": round(l["ok"] / len(l["words"]), 2), "words": l["words"]} for l in lines]
    secs = []
    for si, s in enumerate(sections):
        ls = [l for l in out_lines if l["secao"] == si]
        secs.append({"tag": s["tag"], "tipo": s["tipo"], "cantam": s["cantam"],
                     "s": ls[0]["s"] if ls else None, "e": ls[-1]["e"] if ls else None})
    for i, s in enumerate(secs):          # partes sem canto (intervalos, viradas) ficam entre a anterior e a próxima
        if s["s"] is None:
            prev_e = next((x["e"] for x in reversed(secs[:i]) if x["e"] is not None), 0.0)
            nxt_s = next((x["s"] for x in secs[i + 1:] if x["s"] is not None), None)
            s["s"], s["e"] = prev_e, (nxt_s if nxt_s is not None else prev_e)
    return {"lines": out_lines, "sections": secs, "coverage": round(len(known) / max(1, len(disp)), 2)}
