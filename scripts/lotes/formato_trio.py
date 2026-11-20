"""Leva as letras ainda não gravadas para o FORMATO DO TRIO (o das 24/25/26, que deram 4,8): só a 1ª ponte fica (as
outras eram cópias), sai o refrão 'faster' e a intro perde instrumento fora do trio (cavaquinho, violão, guitarra,
órgão → teclado). Motivo (20/11/2026): a 27 foi gerada com a letra antiga e saiu com 3:26 (cortada para 2:50).
Uso: PYTHONPATH=. .venv/bin/python scripts/lotes/formato_trio.py 28 49
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TROCA = [("happy electric guitar riff", "happy keyboard riff"), ("acoustic guitar riff", "bright keyboard riff"),
         ("cavaquinho riff", "keyboard riff"), ("organ bubble", "keyboard bubble")]


def revisar(t: str) -> str:
    blocos = re.split(r"\n\n+", t.strip("\n"))
    out, ponte = [], False
    for b in blocos:
        cab = b.split("\n", 1)[0]
        if cab.startswith("[Chorus - faster"):
            continue
        if cab.startswith("[Bridge"):
            if ponte:
                continue
            ponte = True
        out.append(b)
    t = "\n\n".join(out) + "\n"
    intro = t.split("\n", 1)[0]
    novo = intro
    for a, b in TROCA:
        novo = novo.replace(a, b)
    return t.replace(intro, novo, 1)


def main(a: int, b: int) -> None:
    for d in sorted((ROOT / "musicas").glob("[0-9][0-9]_*")):
        n = int(d.name[:2])
        if not (a <= n <= b) or not (d / "letra.txt").exists():
            continue
        if "suno_congelado" in json.loads((d / "ficha.json").read_text(encoding="utf-8")):
            print(d.name, "congelada — não mexo")
            continue
        velho = (d / "letra.txt").read_text(encoding="utf-8")
        novo = revisar(velho)
        if novo != velho:
            (d / "letra.txt").write_text(novo, encoding="utf-8")
        print(d.name, len(velho.splitlines()), "→", len(novo.splitlines()), "linhas |", novo.split("\n", 1)[0])


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
