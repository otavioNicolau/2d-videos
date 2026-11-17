"""Configuração, caminhos do projeto e conversão WSL ↔ Windows."""
from __future__ import annotations

import functools
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "library"
PROJECTS = ROOT / "projects"
SCHEMAS = ROOT / "schemas"
GODOT_PROJECT = ROOT / "godot"


def _parse_yaml(text: str) -> dict:
    """Leitor mínimo de YAML (mapas aninhados por indentação, valores escalares) — evita dependência extra."""
    root: dict = {}
    stack = [(-1, root)]
    for raw in text.splitlines():
        line = raw.split(" #")[0].rstrip() if not raw.strip().startswith("#") else ""
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = line.strip().partition(":")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        val = val.strip()
        if not val:
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            if val.startswith('"') and val.endswith('"'):
                v: Any = val[1:-1]
            elif val in ("true", "false"):
                v = val == "true"
            else:
                try:
                    v = float(val) if "." in val else int(val)
                except ValueError:
                    v = val
            parent[key] = v
    return root


@functools.lru_cache
def config() -> dict:
    return _parse_yaml((ROOT / "config.yaml").read_text(encoding="utf-8"))


def tool(name: str) -> str:
    p = config()["tools"][name]
    p = os.path.expanduser(p)
    if not p.startswith("/") and "/" in p:
        p = str(ROOT / p)
    return p


def setting(section: str, key: str, default: Any = None) -> Any:
    v = config().get(section, {}).get(key, default)
    if isinstance(v, str) and v.startswith("~"):
        return os.path.expanduser(v)
    if isinstance(v, str) and v.startswith("./") or (isinstance(v, str) and v.startswith(".venv")):
        return str(ROOT / v)                     # caminho relativo à raiz do projeto
    return v


def to_win(p: Path | str) -> str:
    return subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True, check=True).stdout.strip()


def sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str, ensure_ascii=False).encode()).hexdigest()[:16]


def file_sha(*paths: Path) -> str:
    h = hashlib.sha256()
    for p in paths:
        for f in sorted(Path(p).rglob("*")) if Path(p).is_dir() else [Path(p)]:
            if f.is_file() and "__pycache__" not in f.parts:
                h.update(str(f.relative_to(ROOT) if f.is_relative_to(ROOT) else f).encode())
                h.update(f.read_bytes())
    return h.hexdigest()[:16]


class State:
    """Checkpoints por hash (render por cena: só o que mudou é refeito)."""

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {}

    def fresh(self, key: str, h: str, *outputs: Path) -> bool:
        return self.data.get(key) == h and all(Path(o).exists() for o in outputs)

    def mark(self, key: str, h: str) -> None:
        self.data[key] = h
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, sort_keys=True))


class StudioError(RuntimeError):
    """Erro de produção com mensagem acionável (o que falhou e o que fazer)."""
