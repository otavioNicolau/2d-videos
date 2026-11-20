"""Limpeza dos rascunhos de render (`projects/*/build`): cada vídeo deixa 2–7 GB de quadros por cena.

Regra do canal (pedido do usuário, 20/11/2026: "precisamos sempre estar limpando — deixe apenas as 3 últimas músicas"):
- fica o `build` só dos 3 episódios de número mais alto (epNN-…, inclusive os -short do mesmo número);
- os outros projetos (episódios antigos, testes, laboratórios) perdem o `build`;
- NUNCA apaga o `build` de um episódio que ainda não tem MP4 final (output/*.mp4 que não seja CANDIDATO);
- NUNCA apaga o `build` de um projeto que está renderizando agora;
- só a pasta `build`: output (MP4), analise, musica, episode.json e roteiros ficam sempre.
Roda sozinha no fim de cada `publicar`; à mão: `toonstudio limpar [--manter 3] [--simular]`.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from ..core.config import PROJECTS


def _tamanho(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file() and not f.is_symlink())


def _renderizando() -> set[str]:
    try:
        out = subprocess.run(["pgrep", "-af", "toonstudio.cli build"], capture_output=True, text=True).stdout
    except OSError:
        return set()
    return {m.group(1) for m in re.finditer(r"toonstudio\.cli build (\S+)", out)}


def _tem_mp4_final(proj: Path) -> bool:
    return any("CANDIDATO" not in p.name for p in (proj / "output").rglob("*.mp4")) if (proj / "output").exists() else False


def limpar_builds(manter: int = 3, simular: bool = False, root: Path = PROJECTS) -> list[tuple[str, int, str]]:
    """Regra por CANAL (multicanal, 20/11/2026): a raiz (Laurinha) e cada `projects/<canal>/` guardam o build só dos
    `manter` episódios mais recentes DAQUELE canal."""
    feito = _limpar_pasta(manter, simular, root)
    if root == PROJECTS:
        from ..core.canal import lista
        for cid in lista():
            sub = root / cid
            if sub.is_dir():
                feito += [(f"{cid}/{n}", t, r) for n, t, r in _limpar_pasta(manter, simular, sub)]
    return feito


def _limpar_pasta(manter: int, simular: bool, root: Path) -> list[tuple[str, int, str]]:
    """Apaga os `build` fora dos `manter` episódios mais recentes. Devolve [(projeto, bytes, resultado)]."""
    nums = sorted({int(m.group(1)) for d in root.iterdir() if (m := re.match(r"^ep(\d+)-", d.name))})
    recentes = set(nums[-manter:]) if manter > 0 else set()
    rodando = _renderizando()
    feito = []
    for d in sorted(root.iterdir()):
        b = d / "build"
        if not d.is_dir() or not b.is_dir():
            continue
        m = re.match(r"^ep(\d+)-", d.name)
        if m and int(m.group(1)) in recentes:
            continue
        rel = str(d.relative_to(PROJECTS)) if d.is_relative_to(PROJECTS) else d.name
        if d.name in rodando or rel in rodando:
            feito.append((d.name, 0, "mantido: renderizando agora"))
            continue
        if m and not _tem_mp4_final(d):
            feito.append((d.name, 0, "mantido: ainda sem MP4 final"))
            continue
        tam = _tamanho(b)
        if not simular:
            shutil.rmtree(b)
        feito.append((d.name, tam, "simulado" if simular else "apagado"))
    return feito


def resumo(feito: list[tuple[str, int, str]]) -> str:
    total = sum(t for _, t, r in feito if r in ("apagado", "simulado"))
    linhas = [f"  {n}: {t / 2**30:.1f} GB {r}" if t else f"  {n}: {r}" for n, t, r in feito]
    return "\n".join(linhas + [f"liberado: {total / 2**30:.1f} GB (build só das 3 músicas mais recentes)"])
