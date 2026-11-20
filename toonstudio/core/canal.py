"""Canais do estúdio (multicanal, 20/11/2026). Cada canal tem um perfil em `canais/<id>/canal.json`:
nome, pasta de músicas, marca (logo, vinheta, chamada), pasta de entrega no Windows e textos do YouTube.

Qual canal vale agora:
  1. `--canal <id>` na linha de comando (vira a variável TOONSTUDIO_CANAL);
  2. o canal do PROJETO (`projects/<canal>/<projeto>` ou o arquivo `canal.txt` dentro do projeto);
  3. o padrão: `laurinha` (Laurinha e Luisinho: canais/laurinha/, library/brand/laurinha/).
Os projetos de cada canal ficam em `projects/<canal>/epNN-…` (o nome do projeto é "laurinha/ep28-…", "fofolucos/ep01-…");
os testes e protótipos ficam em `projects/_laboratorio/`.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .config import PROJECTS, ROOT

CANAIS = ROOT / "canais"
PADRAO = "laurinha"
ENV = "TOONSTUDIO_CANAL"


@dataclass
class Canal:
    id: str
    nome: str
    musicas: Path                       # fichas, letras, estilos.json, vozes.json, históricos dos placares
    brand: Path                         # pasta da marca (capa, perfil, miniaturas em <brand>/canal/)
    windows: Path                       # entrega: <windows>/NN Título/{Pré-produção, Vídeo longo}
    logo_png: Path | None = None        # logo do canto do vídeo (se não houver: logo de texto `logo_texto`)
    logo_texto: tuple = ("LAURINHA", "e Luisinho")
    vinheta: Path | None = None
    chamada: Path | None = None
    titulo_sufixo: str = ""             # "<TÍTULO> 🐝 Laurinha e Luisinho (Música Infantil)"
    hashtags: str = ""
    tags: list = field(default_factory=list)
    copyright: str = ""
    playlist_geral: str = ""
    protagonistas: tuple = ()           # quem o auto-rascunho e os placares tratam como principais
    projetos: Path = PROJECTS           # onde ficam os projetos do canal (projects/<canal>/)
    raw: dict = field(default_factory=dict)


def _p(v: str | None) -> Path | None:
    if not v:
        return None
    p = Path(v)
    return p if p.is_absolute() else ROOT / p


def carregar(cid: str) -> Canal:
    f = CANAIS / cid / "canal.json"
    if not f.exists():
        raise KeyError(f"canal desconhecido: {cid} (existentes: {', '.join(lista())})")
    d = json.loads(f.read_text(encoding="utf-8"))
    return Canal(id=cid, nome=d["nome"], musicas=_p(d["musicas"]), brand=_p(d["brand"]), windows=Path(d["windows"]),
                 logo_png=_p(d.get("logo_png")), logo_texto=tuple(d.get("logo_texto", ("", ""))), vinheta=_p(d.get("vinheta")),
                 chamada=_p(d.get("chamada")), titulo_sufixo=d.get("titulo_sufixo", ""), hashtags=d.get("hashtags", ""),
                 tags=d.get("tags", []), copyright=d.get("copyright", ""), playlist_geral=d.get("playlist_geral", ""),
                 protagonistas=tuple(d.get("protagonistas", ())),
                 projetos=PROJECTS / cid, raw=d)


def lista() -> list[str]:
    return sorted(p.parent.name for p in CANAIS.glob("*/canal.json"))


def atual() -> Canal:
    return carregar(os.environ.get(ENV) or PADRAO)


def id_do_projeto(project: str | Path) -> str:
    """Canal de um projeto: `fofolucos/ep01-…` → fofolucos; `canal.txt` dentro dele; senão o padrão."""
    p = Path(project)
    pdir = p if p.is_absolute() else PROJECTS / p
    txt = pdir / "canal.txt"
    if txt.exists():
        return txt.read_text(encoding="utf-8").strip()
    rel = pdir.relative_to(PROJECTS) if pdir.is_relative_to(PROJECTS) else None
    if rel is not None and len(rel.parts) >= 2 and (CANAIS / rel.parts[0] / "canal.json").exists():
        return rel.parts[0]
    return PADRAO


def usar_do_projeto(project: str | Path) -> Canal:
    """Fixa o canal da execução pelo projeto (a menos que `--canal` já tenha fixado)."""
    if not os.environ.get(ENV):
        os.environ[ENV] = id_do_projeto(project)
    return atual()
