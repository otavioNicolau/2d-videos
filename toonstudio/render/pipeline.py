"""Pipeline de produção de um episódio, cena a cena, com checkpoints por hash (só refaz o que mudou).

  validar → cenário → vozes (+visemas) → por cena: [timeline → desenhos (níveis) → OpenToonz (xsheet + tcomposer)
  → Godot (composição) → QA] → mixagem → montagem (FFmpeg) → pranchas de revisão.

Sem aprovação humana (`approval.final_render`), o MP4 sai como CANDIDATO.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from ..animation import easing
from ..animation.timeline import compile_character, expose
from ..core.config import GODOT_PROJECT, LIBRARY, PROJECTS, ROOT, State, StudioError, file_sha, setting, sha, tool
from ..core.registry import character
from ..core.validate import load_background, validate
from ..integrations import opentoonz as ot

LEVEL_CANVAS = (1300, 1000)      # quadro padrão dos níveis (unidades) — igual para todos (câmera única no OpenToonz)
LEVEL_ANCHOR = (650, 900)
CODE_HASH_PATHS = [ROOT / "toonstudio" / "characters", ROOT / "toonstudio" / "animation", ROOT / "toonstudio" / "drawing"]


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ------------------------------------------------------------------ desenho dos níveis (paralelo)
def _draw_one(args):
    cid, pose, path, scale, seed = args
    ch = character(cid)
    ch.render_png(pose, path, scale=scale, seed=seed, jitter=0.45, canvas=LEVEL_CANVAS, anchor=LEVEL_ANCHOR)
    return path


class Episode:
    def __init__(self, slug: str):
        self.slug = slug
        self.dir = PROJECTS / slug
        self.ep = json.loads((self.dir / "episode.json").read_text(encoding="utf-8"))
        self.build = self.dir / "build"
        self.state = State(self.build / "state.json")
        self.fps = int(self.ep["fps"])
        self.W, self.H = self.ep["resolution"]
        self.scale = float(setting("render", "level_scale", 1.5))
        self.report: dict = {"episode": self.ep["id"], "scenes": {}, "warnings": [], "lines": {}}

    # -------------------------------------------------------------- etapas
    def check(self) -> None:
        r = validate(self.ep)
        for w in r.warnings:
            log(f"aviso: {w}")
        self.report["warnings"] += r.warnings
        if not r.ok:
            raise StudioError("episódio inválido:\n  - " + "\n  - ".join(r.errors))
        sb = self.dir / "output" / "storyboard.json"
        board = json.loads(sb.read_text()) if sb.exists() else {}
        for s in self.ep["scenes"]:
            st = board.get(s["id"], {}).get("status", "sem storyboard")
            if st != "aprovado":
                note = board.get(s["id"], {}).get("notes", "")
                self.report["warnings"].append(f"storyboard {s['id']}: {st}{' — ' + note if note else ''}")
        log(f"validação ok ({len(self.ep['scenes'])} cenas)")

    def background(self) -> dict[str, dict]:
        """Todos os cenários usados (episódio + por cena), construídos sob demanda pelo registro."""
        from ..backgrounds import registry
        ids = {self.ep["background"], *(s.get("background") for s in self.ep["scenes"] if s.get("background"))}
        out = {}
        for bid in sorted(ids):
            out[bid] = registry.ensure(bid, scale=self.scale)
        return out

    def song(self) -> dict | None:
        """Análise da música (clipes): batidas, palavras, voz isolada. None em episódios sem trilha."""
        st = self.ep.get("soundtrack")
        if not st:
            return None
        sp = self.dir / st.get("analysis", "analise/song.json")
        if not sp.exists():
            raise StudioError(f"música sem análise: rode `toonstudio song analyze {self.slug}`")
        song = json.loads(sp.read_text(encoding="utf-8"))
        beats = song["beats"]
        if st.get("beat_grid", "half") == "half":
            beats = beats[song.get("downbeat_phase", 0) % 2::2]
        song["grid"] = beats
        return song

    def voices(self) -> dict[str, dict]:
        """Gera/recupera todas as falas. Retorna {chave: {wav, cues, duration, …}}."""
        from ..audio import voice as V
        lines = {}
        adir = self.build / "audio" / "lines"
        adir.mkdir(parents=True, exist_ok=True)
        try:
            for s in self.ep["scenes"]:
                for d in s.get("dialog", []):
                    vc = self.ep["cast"][d["who"]].get("voice")
                    if not vc:
                        raise StudioError(f"{d['who']} fala em {s['id']} mas não tem voz no elenco")
                    k = V.line_key(d["text"], vc, d.get("emotion", []))
                    wav, meta_p, cues_p = adir / f"{k}.wav", adir / f"{k}.json", adir / f"{k}.visemes.json"
                    if not (wav.exists() and meta_p.exists() and cues_p.exists()):
                        log(f"voz {d['who']}: “{d['text']}”")
                        meta = V.synth_line(d["text"], vc, d.get("emotion", []), wav, takes=5, log=log)
                        meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
                        V.visemes(wav, d["text"], cues_p)
                    meta = json.loads(meta_p.read_text())
                    cues = [(c["start"], c["value"]) for c in json.loads(cues_p.read_text())["mouthCues"]]
                    if meta.get("warning"):
                        self.report["warnings"].append(f"{s['id']} {d['who']}: {meta['warning']} (ouvido: “{meta['heard']}”)")
                    lines[f"{s['id']}:{d['t']}"] = {"wav": str(wav), "cues": cues, **meta}
        finally:
            V.shutdown()
        self.report["lines"] = {k: {kk: v[kk] for kk in ("text", "heard", "similarity", "duration")} for k, v in lines.items()}
        return lines

    # -------------------------------------------------------------- cena
    def scene(self, s: dict, bgs: dict, lines: dict, force: bool = False, offset: float = 0.0, song: dict | None = None) -> Path:
        sid = s["id"]
        sdir = self.build / "scenes" / sid
        n = int(round(s["duration"] * self.fps))
        bg_id = s.get("background", self.ep["background"])
        bg = bgs[bg_id]
        perf = {**s.get("characters", {}), **s.get("props", {})}
        line_meta = {k: {"cues": v["cues"], "duration": v["duration"]} for k, v in lines.items() if k.startswith(sid + ":")}
        # música: tempo da cena na música, grade de batidas local e bocas do canto
        g0 = (self.ep["soundtrack"]["start"] + offset) if song else 0.0
        beats_local = [b - g0 for b in song["grid"] if -2 <= b - g0 <= s["duration"] + 2] if song else []
        sing_cues = self._sing(s, song, g0) if song else {}
        h = sha({"scene": s, "cast": {w: self.ep["cast"][w] for w in perf}, "lines": line_meta, "fps": self.fps,
                 "res": [self.W, self.H], "scale": self.scale, "code": file_sha(*CODE_HASH_PATHS), "v": 4,
                 "godot": file_sha(GODOT_PROJECT / "compositor.gd"), "bg": [bg_id, bg.get("layers")],
                 "beats": [round(b, 3) for b in beats_local], "sing": sing_cues})
        comp_dir = sdir / "comp"
        if not force and self.state.fresh(f"scene:{sid}", h, comp_dir / f"{n:06d}.png"):
            log(f"{sid}: sem mudanças (cache)")
            self.report["scenes"][sid] = json.loads((sdir / "qa.json").read_text()) if (sdir / "qa.json").exists() else {}
            return comp_dir
        log(f"{sid}: animando ({n} quadros)")
        qa = {"frames": n, "performers": {}, "issues": []}
        tracks, columns = {}, []
        for who, spec in perf.items():
            cid = self.ep["cast"][who]["character"]
            ch = character(cid)
            spans = []
            for d in s.get("dialog", []):
                if d["who"] == who:
                    L = lines[f"{sid}:{d['t']}"]
                    spans.append((d["t"], d["t"] + L["duration"], [(d["t"] + t, v) for t, v in L["cues"]]))
            for sp_ in sing_cues.get(who, []):
                spans.append(tuple(sp_))
            tl = compile_character(ch, spec, self.fps, s["duration"], spans, beats=beats_local)
            cells, drawings, stage = expose(tl)
            ldir = sdir / "levels" / who
            if ldir.exists():
                shutil.rmtree(ldir)
            ldir.mkdir(parents=True)
            jobs = [(cid, d, str(ldir / f"{who}.{i + 1:04d}.png"), self.scale, i) for i, d in enumerate(drawings)]
            with ProcessPoolExecutor(max_workers=max(1, (os.cpu_count() or 2) - 1)) as ex:
                list(ex.map(_draw_one, jobs, chunksize=4))
            (ldir / "drawings.json").write_text(json.dumps(drawings, default=str))
            columns.append({"name": who, "level_dir": str(ldir), "cells": cells})
            tracks[who] = {"stage": stage, "z": int(spec.get("start", {}).get("z", spec.get("z", 1)))}
            hidden = [i + 1 for i in range(n) if drawings[cells[i] - 1].get("hidden", 0) > 0.5]
            qa["performers"][who] = {"drawings": len(drawings), "hidden_frames": hidden,
                                     "exposure": {"1s": sum(1 for i in range(1, n) if cells[i] != cells[i - 1])}}
            log(f"  {who}: {len(drawings)} desenhos únicos para {n} quadros")
        # OpenToonz: cena de edição + cenas de render
        edit = sdir / f"{sid}.tnz"
        prev = self.state.data.get(f"tnz:{sid}")
        if edit.exists() and prev and ot.scene_hash(edit) != prev:
            manual = ot.read_cells(edit)
            for c in columns:
                if c["name"] in manual:
                    log(f"  {c['name']}: usando timing editado à mão no OpenToonz")
                    c["cells"] = (manual[c["name"]] + [manual[c["name"]][-1]] * n)[:n]
            qa["issues"].append("timing de cena editado no OpenToonz foi respeitado")
        log(f"  OpenToonz: montando xsheet ({len(columns)} colunas)")
        render_scenes = ot.build_scenes(edit, sdir / "otscenes", columns)
        cw, chh = int(LEVEL_CANVAS[0] * self.scale), int(LEVEL_CANVAS[1] * self.scale)
        for p in [edit, *render_scenes.values()]:
            ot.patch_camera(p, cw, chh, self.fps)
        self.state.mark(f"tnz:{sid}", ot.scene_hash(edit))
        performers = []
        from concurrent.futures import ThreadPoolExecutor
        log(f"  tcomposer: {', '.join(c['name'] for c in columns)} (em paralelo)")
        with ThreadPoolExecutor(max_workers=min(3, len(columns))) as tp:
            rendered = dict(zip([c["name"] for c in columns],
                                tp.map(lambda c: ot.render(render_scenes[c["name"]], sdir / "otrender" / c["name"], n), columns)))
        for c in columns:
            who = c["name"]
            out = sdir / "otrender" / who
            frames = rendered[who]
            self._qa_level(qa, who, c["cells"], Path(c["level_dir"]), frames)
            st = tracks[who]["stage"]
            vis = [True] * n
            performers.append({"name": who, "dir": str(out), "pattern": "f.%04d.png",
                               "anchor": [LEVEL_ANCHOR[0] * self.scale, LEVEL_ANCHOR[1] * self.scale],
                               "level_scale": self.scale, "z": tracks[who]["z"],
                               "track": [[st[i]["x"], st[i]["y"], st[i].get("depth", 1.0), vis[i]] for i in range(n)]})
        # câmera por quadro
        cam = self._camera(s, n)
        fade = [0.0] * n
        if s.get("transition_out") == "fade":
            k = int(0.7 * self.fps)
            for i in range(n - k, n):
                fade[i] = (i - (n - k) + 1) / k
        if s is self.ep["scenes"][0]:
            k = int(0.4 * self.fps)
            for i in range(k):
                fade[i] = max(fade[i], 1 - (i + 1) / k)
        bgdir = LIBRARY / "backgrounds" / bg_id / "layers"
        layers = []
        for l in bg["layers"]:
            L = {"file": str(bgdir / l["file"]), "parallax": l["parallax"], "z": l["z"],
                 "scale": l.get("scale_override", bg["scale"])}
            if l.get("fixed"):
                L.update({"fixed": True, "center": bool(l.get("center")),
                          "x": 0.0 if l.get("center") else -(l["width"] - self.W) / 2,
                          "y": 0.0 if l.get("center") else -(l["height"] - self.H) / 2})
            if l.get("spin_per_beat") and song:
                from ..animation.cycles import beat_phase
                ang = []
                for i in range(n):
                    k_, u = beat_phase(g0 + i / self.fps, song["grid"])
                    ang.append(round(l["spin_per_beat"] * (k_ + (1 - (1 - min(u, 1)) ** 3)), 3))
                L["angles"] = ang
            layers.append(L)
        flash = [0.0] * n
        if s.get("flash_in"):
            for i, a in enumerate((1.0, 0.85, 0.6, 0.38, 0.2, 0.08)):
                if i < n:
                    flash[i] = a
        job = {"resolution": [self.W, self.H], "fps": self.fps, "frames": n, "camera": cam, "fade": fade, "flash": flash,
               "layers": layers, "performers": performers}
        jp = sdir / "job.json"
        jp.write_text(json.dumps(job))
        self._godot(jp, comp_dir, n)
        self._qa_comp(qa, comp_dir, n)
        (sdir / "qa.json").write_text(json.dumps(qa, indent=2, ensure_ascii=False))
        self.report["scenes"][sid] = qa
        self.state.mark(f"scene:{sid}", h)
        return comp_dir

    def _sing(self, s: dict, song: dict, g0: float) -> dict[str, list]:
        """Bocas do canto: Rhubarb na voz isolada, só nos trechos marcados em `sing` (tempo local da cena)."""
        from ..audio import song as songmod
        out: dict[str, list] = {}
        cdir = self.build / "audio" / "sing"
        cdir.mkdir(parents=True, exist_ok=True)
        for k, sg in enumerate(s.get("sing", [])):
            a, b = g0 + sg["from"], g0 + sg["to"]
            text = " ".join(w["w"] for w in song["words"] if a - 0.1 <= w["s"] < b) or "a"
            cp = cdir / f"{s['id']}_{sg['who']}_{k}_{a:.2f}_{b:.2f}.json"
            if cp.exists():
                cues = [tuple(c) for c in json.loads(cp.read_text())]
            else:
                cues = songmod.sung_visemes(Path(song["files"]["vocals"]), a, b, text, cdir / "tmp_rhubarb.json")
                cp.write_text(json.dumps(cues))
            out.setdefault(sg["who"], []).append([sg["from"], sg["to"], [[round(t - g0, 3), v] for t, v in cues]])
        return out

    def _check_dialog_fits(self, lines: dict) -> None:
        """A fala gerada tem duração real: ela precisa caber no plano (senão a boca para no corte e o som invade o próximo)."""
        errs = []
        for s in self.ep["scenes"]:
            for d in s.get("dialog", []):
                end = d["t"] + lines[f"{s['id']}:{d['t']}"]["duration"]
                if end > s["duration"] - 0.05:
                    errs.append(f"{s['id']}: “{d['text']}” termina em {end:.2f}s, mas o plano tem {s['duration']}s "
                                f"(aumente a duração para ≥ {end + 0.25:.2f}s ou antecipe a fala)")
        if errs:
            raise StudioError("falas que não cabem no plano:\n  - " + "\n  - ".join(errs))

    def _camera(self, s: dict, n: int) -> list[list[float]]:
        keys = s["camera"]["keys"]
        out = []
        rng = np.random.default_rng(len(s["id"]))
        shakes = s["camera"].get("shake", [])
        for i in range(n):
            t = i / self.fps
            k0 = keys[0]
            val = (k0["x"], k0["y"], k0["zoom"])
            for a, b in zip(keys, keys[1:]):
                if a["t"] <= t <= b["t"]:
                    u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
                    e = easing.get(b.get("ease", "inout"))(u)
                    val = tuple(a[c] + (b[c] - a[c]) * e for c in ("x", "y", "zoom"))
                    break
                if t > b["t"]:
                    val = (b["x"], b["y"], b["zoom"])
            x, y, z = val
            for sh in shakes:
                if sh["t"] <= t <= sh["t"] + sh["dur"]:
                    amp = sh["amp"] * (1 - (t - sh["t"]) / sh["dur"])
                    x += rng.uniform(-amp, amp)
                    y += rng.uniform(-amp, amp)
            out.append([round(x, 2), round(y, 2), round(z, 4)])
        return out

    def _godot(self, job: Path, out_dir: Path, n: int) -> None:
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)
        tmp = out_dir / "raw"
        tmp.mkdir()
        log(f"  Godot: compondo {n} quadros")
        t = time.time()
        p = subprocess.run([tool("godot"), "--path", str(GODOT_PROJECT), "--write-movie", str(tmp / "f.png"),
                            "--fixed-fps", str(self.fps), "--", f"--job={job}"], capture_output=True, timeout=1800)
        outp = (p.stdout + p.stderr).decode("utf-8", "replace")
        if "COMPOSITOR_ERROR" in outp or "SCRIPT ERROR" in outp or "Parse Error" in outp:
            raise StudioError("Godot falhou:\n" + "\n".join(l for l in outp.splitlines() if "ERROR" in l or "Error" in l)[:2000])
        raw = sorted(tmp.glob("f*.png"))
        if len(raw) < n:
            raise StudioError(f"Godot gravou {len(raw)} de {n} quadros:\n{outp[-1500:]}")
        for i in range(n):
            raw[i].rename(out_dir / f"{i + 1:06d}.png")
        shutil.rmtree(tmp)
        log(f"  Godot: {n} quadros em {time.time() - t:.1f}s")

    # -------------------------------------------------------------- QA
    def _qa_level(self, qa, who, cells, level_dir: Path, frames: list[Path]) -> None:
        from PIL import Image, ImageChops
        issues = qa["issues"]
        # 1) render do OpenToonz == desenho de origem (amostra): pixel a pixel
        for row in sorted({0, len(cells) // 2, len(cells) - 1}):
            src = level_dir / f"{who}.{cells[row]:04d}.png"
            a = Image.open(frames[row]).convert("RGBA")
            b = Image.open(src).convert("RGBA")
            if a.size != b.size:
                issues.append(f"{who}: quadro {row + 1} com tamanho {a.size} ≠ desenho {b.size}")
                continue
            diff = max(e[1] for e in ImageChops.difference(a, b).getextrema())
            if diff > 8:
                issues.append(f"{who}: render do OpenToonz difere do desenho no quadro {row + 1} (dif. máx {diff})")
        # 2) quadros vazios (personagem sumindo)
        empty = [i + 1 for i, f in enumerate(frames) if Image.open(f).getchannel("A").getbbox() is None]
        hidden = set(qa["performers"][who].get("hidden_frames", []))
        empty_unexpected = [i for i in empty if i not in hidden]
        if empty_unexpected:
            empty = empty_unexpected
            issues.append(f"{who}: {len(empty)} quadros vazios (ex.: {empty[:5]})")
        qa["performers"][who]["empty_frames"] = len(empty)

    def _qa_comp(self, qa, comp_dir: Path, n: int) -> None:
        from PIL import Image
        got = len(list(comp_dir.glob("*.png")))
        if got != n:
            qa["issues"].append(f"composição com {got} quadros (esperado {n})")
        # quadros pretos/congelados inesperados
        prev = None
        frozen = 0
        for i in range(0, n, max(1, n // 24)):
            im = Image.open(comp_dir / f"{i + 1:06d}.png").convert("L").resize((96, 54))
            arr = np.asarray(im, dtype=np.float32)
            if arr.mean() < 6 and i > 0.4 * self.fps and i < n - 0.8 * self.fps:
                qa["issues"].append(f"quadro {i + 1} quase preto")
            if prev is not None and np.abs(arr - prev).mean() < 0.05:
                frozen += 1
            prev = arr
        qa["frozen_samples"] = frozen

    # -------------------------------------------------------------- áudio e montagem
    def mix(self, lines: dict) -> Path:
        st = self.ep.get("soundtrack")
        if st:
            # clipe: o áudio é a música original — só recortamos o trecho numa CÓPIA (o arquivo original não é tocado)
            out = self.build / "audio" / "trilha_trecho.wav"
            out.parent.mkdir(parents=True, exist_ok=True)
            dur = st["end"] - st["start"]
            af = []
            if st.get("fade_out"):
                af.append(f"afade=t=out:st={dur - st['fade_out']:.3f}:d={st['fade_out']:.3f}")
            cmd = [tool("ffmpeg"), "-y", "-loglevel", "error", "-ss", f"{st['start']:.3f}", "-t", f"{dur:.3f}",
                   "-i", str(self.dir / st["file"]), "-ar", "48000", "-ac", "2"]
            if af:
                cmd += ["-af", ",".join(af)]
            subprocess.run(cmd + [str(out)], check=True)
            return out
        from ..audio import mixer
        return mixer.mix_episode(self, lines)

    def _overlays(self, out_dir: Path) -> list[str]:
        """Filtros de texto/marca: letra palavra a palavra, aviso inicial, rodapé e logo (clipes)."""
        from . import brand
        ov = self.ep.get("overlays", {})
        cap = self.ep.get("captions")
        st = self.ep.get("soundtrack")
        total = sum(s["duration"] for s in self.ep["scenes"])
        lines = []
        if cap and st:
            data = json.loads((self.dir / cap["lyrics"]).read_text(encoding="utf-8"))
            for ln in data["lines"]:
                ws = [{"w": w["w"], "s": w["s"] - st["start"], "e": w["e"] - st["start"]} for w in ln["words"]]
                if ws and ws[-1]["e"] > 0 and ws[0]["s"] < total:
                    lines.append({"s": ws[0]["s"], "e": ln["e"] - st["start"], "words": ws})
        if not (lines or ov.get("card") or ov.get("footer") or ov.get("logo")):
            return []
        assf = brand.ass(self.build / "textos.ass", self.W, self.H, lines, ov.get("card"), ov.get("footer"), total,
                         float(ov.get("card_dur", 5.0)))
        filt = f"ass={assf}:fontsdir={LIBRARY / 'fonts'}"
        if ov.get("logo"):
            lg = brand.logo(self.build / "logo.png", height=118)
            return ["-i", str(lg), "-filter_complex", f"[0:v][2:v]overlay=28:14[l];[l]{filt}[v]", "-map", "[v]"]
        return ["-vf", filt, "-map", "0:v"]

    def assemble(self, wav: Path) -> Path:
        approved = bool(self.ep.get("approval", {}).get("final_render"))
        out_dir = self.dir / "output"
        out_dir.mkdir(exist_ok=True)
        seq = self.build / "episode_frames"
        if seq.exists():
            shutil.rmtree(seq)
        seq.mkdir()
        k = 0
        for s in self.ep["scenes"]:
            for f in sorted((self.build / "scenes" / s["id"] / "comp").glob("*.png")):
                k += 1
                os.link(f, seq / f"{k:06d}.png")
        name = f"{self.ep['id']}{'' if approved else '_CANDIDATO'}.mp4"
        mp4 = out_dir / name
        log(f"FFmpeg: montando {k} quadros → {mp4.name}")
        extra = self._overlays(out_dir)
        vmap = extra if extra else ["-map", "0:v"]
        subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-framerate", str(self.fps), "-i", str(seq / "%06d.png"),
                        "-i", str(wav), *vmap, "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                        "-pix_fmt", "yuv420p", "-r", str(self.fps), "-c:a", "aac", "-b:a", "192k", "-shortest",
                        "-movflags", "+faststart", str(mp4)], check=True)
        shutil.rmtree(seq)
        return mp4

    def run(self, only: list[str] | None = None, force: bool = False) -> Path:
        t0 = time.time()
        self.check()
        bgs = self.background()
        song = self.song()
        lines = self.voices()
        self._check_dialog_fits(lines)
        offset = 0.0
        for s in self.ep["scenes"]:
            if not (only and s["id"] not in only):
                self.scene(s, bgs, lines, force=force and (not only or s["id"] in only), offset=offset, song=song)
            offset += s["duration"]
        wav = self.mix(lines)
        mp4 = self.assemble(wav)
        from ..qa import review
        review.write(self, mp4)
        log(f"pronto em {time.time() - t0:.0f}s: {mp4}")
        return mp4
