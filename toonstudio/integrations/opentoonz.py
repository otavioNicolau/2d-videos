"""Integração com o OpenToonz 1.8 (ADR-0003): ToonzScript por linha de comando + tcomposer.

Por cena (plano):
  <sid>.tnz            — cena de EDIÇÃO: uma coluna por personagem/objeto, timing no xsheet (o animador abre esta)
  render/<who>.tnz     — cena de RENDER de cada coluna (o tcomposer compõe todas as colunas; separamos para o Godot)
Se a cena de edição foi alterada à mão (hash diferente do que geramos), as células são lidas DELA.

Limitações conhecidas (validadas na F0): ToonzScript não ajusta câmera/fps → editamos o XML gerado pelo próprio
OpenToonz; o exit code do OpenToonz é 1 mesmo com sucesso → sucesso = marcador impresso + arquivo existente;
o `Renderer` do ToonzScript trava fora da interface → render só pelo tcomposer.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ..core.config import StudioError, file_sha, to_win, tool

DPI = 120.0   # câmera e níveis a 120 dpi → 1 pixel do desenho = 1 pixel do render (validado na F0)


def _js(path: Path | str) -> str:
    return to_win(path).replace("\\", "\\\\")


def compress(cells: list[int]) -> list[tuple[int, int, int]]:
    """[(linha inicial, quantidade, desenho)] — exposições seguradas."""
    out: list[tuple[int, int, int]] = []
    for r, d in enumerate(cells):
        if out and out[-1][2] == d and out[-1][0] + out[-1][1] == r:
            out[-1] = (out[-1][0], out[-1][1] + 1, d)
        else:
            out.append((r, 1, d))
    return out


def _cells_js(col: int, var: str, cells: list[int]) -> str:
    lines = []
    for r0, n, d in compress(cells):
        for r in range(r0, r0 + n):
            lines.append(f"scene.setCell({r}, {col}, {var}, {d});")
    return "\n".join(lines)


def build_scenes(edit_tnz: Path, render_dir: Path, columns: list[dict], timeout: int = 240) -> dict[str, Path]:
    """columns: [{"name", "level_dir", "cells"}]. Cria a cena de edição e as cenas de render numa execução só."""
    render_dir.mkdir(parents=True, exist_ok=True)
    parts = ["// Cartoon Studio: edit scene + one render scene per column"]
    parts.append("scene = new Scene();")
    for i, c in enumerate(columns):
        parts.append(f'lv{i} = scene.loadLevel("{c["name"]}", "{_js(Path(c["level_dir"]) / (c["name"] + "..png"))}");')
        parts.append(_cells_js(i, f"lv{i}", c["cells"]))
    parts.append(f'scene.save("{_js(edit_tnz)}");')
    outs: dict[str, Path] = {}
    for i, c in enumerate(columns):
        rt = render_dir / f'{c["name"]}.tnz'
        outs[c["name"]] = rt
        parts.append("scene = new Scene();")
        parts.append(f'lv = scene.loadLevel("{c["name"]}", "{_js(Path(c["level_dir"]) / (c["name"] + "..png"))}");')
        parts.append(_cells_js(0, "lv", c["cells"]))
        parts.append(f'scene.save("{_js(rt)}");')
    parts.append('print("STUDIO_SCENES_OK");')
    script = edit_tnz.with_suffix(".toonzscript")
    script.write_text("\n".join(parts), encoding="utf-8")
    for p in [edit_tnz, *outs.values()]:
        p.unlink(missing_ok=True)
    import time
    started = time.time() - 2
    try:
        proc = subprocess.run([tool("opentoonz"), to_win(script)], capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(["/mnt/c/Windows/System32/taskkill.exe", "/IM", "OpenToonz.exe", "/F"], capture_output=True)
        raise StudioError(f"OpenToonz não terminou em {timeout}s ao montar {edit_tnz.name} (processo encerrado)")
    out = (proc.stdout + proc.stderr).decode("utf-8", "replace")
    # o OpenToonz nem sempre repassa o print() do script para a saída: o critério é o arquivo novo em disco
    missing = [p for p in [edit_tnz, *outs.values()] if not p.exists() or p.stat().st_mtime < started]
    if missing:
        raise StudioError(f"OpenToonz não criou {', '.join(p.name for p in missing) or 'as cenas'}:\n{out[-1200:]}")
    return outs


def patch_camera(tnz: Path, w_px: int, h_px: int, fps: int) -> None:
    """Câmera do tamanho do quadro do nível (render 1:1) e fps do episódio."""
    x = tnz.read_text(encoding="utf-8")
    x, n1 = re.subn(r"<cameraSize>\s*[\d.]+ [\d.]+\s*</cameraSize>",
                    f"<cameraSize>\n          {w_px / DPI:.6g} {h_px / DPI:.6g} \n        </cameraSize>", x)
    x, n2 = re.subn(r"<cameraRes>\s*\d+ \d+\s*</cameraRes>", f"<cameraRes>\n          {w_px} {h_px} \n        </cameraRes>", x)
    x, _ = re.subn(r"<fps>\s*[\d.]+\s*</fps>", f"<fps>\n          {fps} \n        </fps>", x)
    if not (n1 and n2):
        raise StudioError(f"formato inesperado de câmera em {tnz.name} (OpenToonz mudou o .tnz?)")
    tnz.write_text(x, encoding="utf-8")


def read_cells(tnz: Path) -> dict[str, list[int]]:
    """Lê as células do xsheet de uma cena (para respeitar retimes feitos à mão no OpenToonz).

    Formato do .tnz 1.8: <levelSet><levels><level id='1'> nome <info .../> … e, nas colunas,
    <cell> linha quantidade <level id='1'/>quadro incremento </cell>."""
    x = tnz.read_text(encoding="utf-8")
    idname = {lid: name for lid, name in re.findall(r"<level id='(\d+)'>\s*([^\s<]+)", x)}
    out: dict[str, list[int]] = {}
    for col in re.findall(r"<levelColumn.*?</levelColumn>", x, flags=re.S):
        cells: dict[int, int] = {}
        name = None
        for r0, n, lid, fid, inc in re.findall(r"<cell>\s*(\d+) (\d+) <level id='(\d+)'/>(\d+)\S* (-?\d+)\s*</cell>", col):
            name = idname.get(lid, lid)
            for k in range(int(n)):
                cells[int(r0) + k] = int(fid) + k * int(inc)
        if name and cells:
            out[name] = [cells.get(r, 0) for r in range(max(cells) + 1)]
    return out


def render(tnz: Path, out_dir: Path, frames: int, timeout: int = 900) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob("*.png"):
        f.unlink()
    try:
        proc = subprocess.run([tool("tcomposer"), to_win(tnz), "-o", to_win(out_dir / "f.png"), "-range", "1", str(frames)],
                              capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise StudioError(f"tcomposer passou de {timeout}s em {tnz.name}")
    got = sorted(out_dir.glob("f.*.png"))
    if len(got) != frames:
        log = (proc.stdout + proc.stderr).decode("utf-8", "replace")
        raise StudioError(f"tcomposer gerou {len(got)} de {frames} quadros para {tnz.name}:\n{log[-1200:]}")
    return got


def scene_hash(tnz: Path) -> str:
    return file_sha(tnz)
