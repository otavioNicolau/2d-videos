"""Peças fixas do canal em vídeo (BIBLIA_MUSICAL §10): vinheta de abertura e chamada final.

Renderizadas UMA vez (projetos `marca-vinheta` e `marca-chamada`) e guardadas em library/brand/; a montagem final de cada
episódio (`toonstudio final <projeto>`) junta vinheta + clipe + chamada. A animação casa com os sons da peça:
vinheta = logotipo sonoro de audio/sound_logo.py (zumbido →, zumbido ←, sininhos 1,25 s, "Laurinha!" 1,55 s,
"e Luisinho!" 2,3 s, "zum!" 3,25 s, total 4,2 s).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ..core.config import LIBRARY, PROJECTS, StudioError, tool

BRAND = LIBRARY / "brand"


def _boca(t0: float, silabas: int, passo: float = 0.17) -> list[dict]:
    """Chaves de boca para uma fala curta (sílabas abertas/fechadas alternadas)."""
    ks, t = [], t0
    for i in range(silabas):
        ks.append({"t": round(t, 3), "pose": {"mouth": "D" if i % 2 == 0 else "C"}, "ease": "step"})
        ks.append({"t": round(t + passo * 0.6, 3), "pose": {"mouth": "X"}, "ease": "step"})
        t += passo
    return ks


def vinheta_episode(dur: float = 4.2, falas: bool = False) -> dict:
    """falas=False: vinheta SEM voz (as personagens não mexem a boca)."""
    cam = {"keys": [{"t": 0, "x": 1300, "y": 540, "zoom": 1.0}, {"t": dur, "x": 1300, "y": 540, "zoom": 1.06, "ease": "inout"}],
           "beat": {"pulse": 0.0, "bar_zoom": 0.0, "sway": 0, "bounce": 0}}
    la = {"start": {"x": -300, "y": 520, "turn": 0.9, "expr": "joy", "z": 3}, "exposure": 1,
          "actions": [{"t": 0.0, "do": "fly", "to_x": 2950, "to_y": 360, "dur": 1.3, "land": False},
                      {"t": 1.36, "do": "fly", "to_x": 640, "to_y": 940, "dur": 0.32},
                      {"t": 2.25, "do": "wave", "dur": 0.9},
                      {"t": 3.25, "do": "dance", "style": "asinhas", "dur": round(dur - 3.25, 3)}],
          "keys": [{"t": 1.33, "pose": {"x": -250, "y": 760}, "ease": "step"}] + (_boca(1.55, 3) if falas else [])}
    lu = {"start": {"x": 2950, "y": 700, "turn": -0.9, "expr": "joy", "z": 3}, "exposure": 1,
          "actions": [{"t": 0.35, "do": "fly", "to_x": -300, "to_y": 620, "dur": 1.3, "land": False},
                      {"t": 1.95, "do": "fly", "to_x": 1960, "to_y": 940, "dur": 0.32, "land_turn": -0.15},
                      {"t": 2.95, "do": "wave", "dur": 0.3},
                      {"t": 3.25, "do": "dance", "style": "asinhas", "dur": round(dur - 3.25, 3)}],
          "keys": [{"t": 1.9, "pose": {"x": 2900, "y": 760}, "ease": "step"}] + (_boca(2.3, 4, 0.16) if falas else [])}
    logo = {"start": {"x": 1300, "y": 780, "z": 1, "escala": 0.0}, "exposure": 1,
            "keys": [{"t": 1.2, "pose": {"escala": 0.0}, "ease": "step"}, {"t": 1.42, "pose": {"escala": 1.15}, "ease": "out"},
                     {"t": 1.6, "pose": {"escala": 1.0}, "ease": "inout"}, {"t": 3.25, "pose": {"escala": 1.0, "giro": 0.0}},
                     {"t": 3.4, "pose": {"escala": 1.08, "giro": 0.05}, "ease": "out"},
                     {"t": 3.6, "pose": {"escala": 1.0, "giro": -0.03}, "ease": "inout"},
                     {"t": 3.8, "pose": {"giro": 0.0}, "ease": "inout"}]}
    scene = {"id": "s01_vinheta", "title": "Vinheta Laurinha e Luisinho", "duration": dur, "background": "plano_ceu",
             "camera": cam, "fx": ["estrelas"], "characters": {"laurinha": la, "luisinho": lu}, "props": {"logo": logo}}
    return {"schema": "1.1", "id": "marca-vinheta", "title": "Vinheta — Laurinha e Luisinho",
            "logline": "Peça fixa do canal: abertura de 4,2 s sincronizada com o logotipo sonoro.", "fps": 30,
            "resolution": [1920, 1080], "background": "plano_ceu",
            "soundtrack": {"file": "musica/trabalho.wav", "analysis": "analise/song.json", "start": 0.0, "end": dur,
                           "fade_out": 0.0, "beat_grid": "full"},
            "overlays": {"logo": False},
            "cast": {"laurinha": {"character": "laurinha"}, "luisinho": {"character": "luisinho"}, "logo": {"character": "logo"}},
            "approval": {"storyboard": False, "final_render": False}, "scenes": [scene]}


def final(project: str) -> Path:
    """Vídeo completo do episódio: vinheta (se houver) + clipe + chamada (se houver), 1080p 30 fps, áudio 48 kHz."""
    pdir = PROJECTS / project
    out_dir = pdir / "output"
    clips = sorted(out_dir.glob(f"{project}*.mp4"))
    clips = [c for c in clips if "COMPLETO" not in c.name]
    if not clips:
        raise StudioError(f"renderize o clipe antes (`toonstudio build {project}`)")
    clip = clips[0]
    parts = [p for p in (BRAND / "vinheta.mp4", clip, BRAND / "chamada.mp4") if p.exists()]
    tag = "COMPLETO" + ("_CANDIDATO" if "CANDIDATO" in clip.name else "")
    out = out_dir / f"{project}_{tag}.mp4"
    ins, fil = [], ""
    for i, p in enumerate(parts):
        ins += ["-i", str(p)]
        fil += (f"[{i}:v]scale=1920:1080,fps=30,format=yuv420p,setsar=1[v{i}];"
                f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];")
    fil += "".join(f"[v{i}][a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=1[v][a]"
    cru = out.with_name(out.stem + "_som_cru.mp4")
    subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", *ins, "-filter_complex", fil, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-c:a", "pcm_s16le",
                    str(cru.with_suffix(".mov"))], check=True)
    # masterização (18/11): EQ casado com a referência + −14 LUFS / −1 dBTP — o som cru do Suno é estridente no volume alto
    from ..audio.master import masterizar, rebalancear
    bruto, mestre = out.with_name(out.stem + "_audio_cru.wav"), out.with_name(out.stem + "_audio_master.wav")
    rebal = out.with_name(out.stem + "_audio_rebal.wav")
    subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(cru.with_suffix(".mov")), "-vn", "-c:a", "pcm_s16le",
                    str(bruto)], check=True)
    rb = rebalancear(bruto, rebal)               # voz × batida no peso da referência (o Suno põe a voz muito na frente)
    rel = {"rebalanceamento": rb, **masterizar(rebal, mestre)}
    subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(cru.with_suffix(".mov")), "-i", str(mestre),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out)],
                   check=True)
    (out_dir / "master.json").write_text(json.dumps(rel, indent=1, default=float), encoding="utf-8")
    for p in (cru.with_suffix(".mov"), bruto, rebal, mestre):
        p.unlink(missing_ok=True)
    return out


def preparar_vinheta() -> Path:
    pdir = PROJECTS / "marca-vinheta"
    pdir.mkdir(parents=True, exist_ok=True)
    ep = vinheta_episode()
    (pdir / "episode.json").write_text(json.dumps(ep, ensure_ascii=False, indent=2), encoding="utf-8")
    return pdir


def vinheta_suno_episode(dur: float = 3.6) -> dict:
    """Vinheta com o áudio do Suno SEM processamento (voz natural): "Laurinha" 0,0–0,94 s · "e Luisinho" 0,94–2,2 s ·
    "Zum!" 2,2–2,8 s. O logo já entra na primeira sílaba; cada um chega voando no próprio nome."""
    ep = vinheta_episode(dur, falas=False)
    sc = ep["scenes"][0]
    sc["camera"]["keys"][-1]["t"] = dur
    la = {"start": {"x": -260, "y": 760, "turn": 0.9, "expr": "joy", "z": 3}, "exposure": 1,
          "actions": [{"t": 0.0, "do": "fly", "to_x": 640, "to_y": 940, "dur": 0.32},
                      {"t": 1.3, "do": "wave", "dur": 0.8},
                      {"t": 2.2, "do": "dance", "style": "asinhas", "dur": round(dur - 2.2, 3)}],
          "keys": _boca(0.04, 3, 0.29)}
    lu = {"start": {"x": 2900, "y": 760, "turn": -0.9, "expr": "joy", "z": 3}, "exposure": 1,
          "actions": [{"t": 0.95, "do": "fly", "to_x": 1960, "to_y": 940, "dur": 0.32, "land_turn": -0.15},
                      {"t": 2.2, "do": "dance", "style": "asinhas", "dur": round(dur - 2.2, 3)}],
          "keys": _boca(1.0, 4, 0.29)}
    logo = {"start": {"x": 1300, "y": 780, "z": 1, "escala": 0.0}, "exposure": 1,
            "keys": [{"t": 0.0, "pose": {"escala": 0.0}, "ease": "step"}, {"t": 0.22, "pose": {"escala": 1.15}, "ease": "out"},
                     {"t": 0.4, "pose": {"escala": 1.0}, "ease": "inout"}, {"t": 2.2, "pose": {"escala": 1.0, "giro": 0.0}},
                     {"t": 2.35, "pose": {"escala": 1.08, "giro": 0.05}, "ease": "out"},
                     {"t": 2.55, "pose": {"escala": 1.0, "giro": -0.03}, "ease": "inout"},
                     {"t": 2.75, "pose": {"giro": 0.0}, "ease": "inout"}]}
    sc.update({"duration": dur, "characters": {"laurinha": la, "luisinho": lu}, "props": {"logo": logo}})
    ep["soundtrack"].update({"file": "musica/suno.wav", "end": dur})
    ep["logline"] = "Peça fixa do canal: abertura com a vinheta cantada no Suno (voz natural, sem processamento)."
    return ep


def vinheta_tema_episode(dur: float = 3.62) -> dict:
    """Vinheta oficial (16/11/2026): repetição nº 2 do tema "Zum Zum" do Suno, áudio original sem processar.
    Palavras (transcrição): "Laurinha" 0,0–0,64 · "Luisinho" 0,78–1,56 · "zum" 1,68 / 2,62 / 2,94 s."""
    ep = vinheta_episode(dur, falas=False)
    sc = ep["scenes"][0]
    sc["camera"]["keys"][-1]["t"] = dur
    zums = (1.68, 2.62, 2.94)
    la = {"start": {"x": -260, "y": 760, "turn": 0.9, "expr": "joy", "z": 3}, "exposure": 1,
          "actions": [{"t": 0.0, "do": "fly", "to_x": 640, "to_y": 940, "dur": 0.3},
                      {"t": 1.66, "do": "dance", "style": "asinhas", "dur": round(dur - 1.66, 3)}],
          "keys": _boca(0.08, 3, 0.19)}
    lu = {"start": {"x": 2900, "y": 760, "turn": -0.9, "expr": "joy", "z": 3}, "exposure": 1,
          "actions": [{"t": 0.55, "do": "fly", "to_x": 1960, "to_y": 940, "dur": 0.3, "land_turn": -0.15},
                      {"t": 1.66, "do": "dance", "style": "asinhas", "dur": round(dur - 1.66, 3)}],
          "keys": _boca(0.8, 4, 0.19)}
    lk = [{"t": 0.0, "pose": {"escala": 0.0}, "ease": "step"}, {"t": 0.2, "pose": {"escala": 1.15}, "ease": "out"},
          {"t": 0.38, "pose": {"escala": 1.0}, "ease": "inout"}]
    for z in zums:                                     # o logo balança em cada "zum"
        lk += [{"t": z, "pose": {"escala": 1.0, "giro": 0.0}}, {"t": z + 0.1, "pose": {"escala": 1.07, "giro": 0.04}, "ease": "out"},
               {"t": z + 0.24, "pose": {"escala": 1.0, "giro": 0.0}, "ease": "inout"}]
    sc.update({"duration": dur, "characters": {"laurinha": la, "luisinho": lu},
               "props": {"logo": {"start": {"x": 1300, "y": 780, "z": 1, "escala": 0.0}, "exposure": 1, "keys": lk}}})
    ep["soundtrack"].update({"file": "musica/tema_v2.wav", "end": dur})
    ep["logline"] = "Peça fixa do canal: vinheta = repetição do tema 'Zum Zum' (Suno), áudio original."
    return ep
