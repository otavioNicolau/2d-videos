"""Linha de comando do estúdio.

  toonstudio validate <episódio>            valida contra schema, biblioteca e cobertura de câmera
  toonstudio build <episódio> [--scene s03] [--force]   produz (incremental) e gera o MP4 (candidato sem aprovação)
  toonstudio approve <episódio> --by NOME   registra a aprovação humana do render final
  toonstudio modelsheet <personagem>        folha de modelo PNG + KRA (Krita)
  toonstudio background <id>                pinta o cenário e gera KRA com as camadas
  toonstudio catalog                        biblioteca de animações/expressões (JSON)
  toonstudio storyboard <episódio>          prévia rápida (3 painéis por plano) antes do render caro
  toonstudio board <episódio> <cena> aprovar|rejeitar ["nota"]   decisão de storyboard por plano
  toonstudio krita <arquivo.kra|ora>        abre no Krita (Windows)
  toonstudio opentoonz <episódio> <cena>    abre a cena de edição no OpenToonz
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .core.config import LIBRARY, PROJECTS, StudioError, to_win, tool


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="toonstudio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("episode")
    b = sub.add_parser("build"); b.add_argument("episode"); b.add_argument("--scene", action="append"); b.add_argument("--force", action="store_true")
    a = sub.add_parser("approve"); a.add_argument("episode"); a.add_argument("--by", required=True); a.add_argument("--notes", default="")
    m = sub.add_parser("modelsheet"); m.add_argument("character")
    g = sub.add_parser("background"); g.add_argument("id", nargs="?", default="floresta_clareira")
    sub.add_parser("catalog")
    sb = sub.add_parser("storyboard"); sb.add_argument("episode")
    bd = sub.add_parser("board"); bd.add_argument("episode"); bd.add_argument("scene"); bd.add_argument("decision", choices=["aprovar", "rejeitar"]); bd.add_argument("notes", nargs="?", default="")
    k = sub.add_parser("krita"); k.add_argument("file")
    o = sub.add_parser("opentoonz"); o.add_argument("episode"); o.add_argument("scene")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "validate":
            from .core.validate import validate
            ep = json.loads((PROJECTS / args.episode / "episode.json").read_text(encoding="utf-8"))
            r = validate(ep)
            for e in r.errors:
                print("ERRO:", e)
            for w in r.warnings:
                print("aviso:", w)
            print("ok" if r.ok else f"{len(r.errors)} erro(s)")
            return 0 if r.ok else 1
        if args.cmd == "build":
            from .render.pipeline import Episode
            Episode(args.episode).run(only=args.scene, force=args.force)
            return 0
        if args.cmd == "approve":
            p = PROJECTS / args.episode / "episode.json"
            ep = json.loads(p.read_text(encoding="utf-8"))
            ep.setdefault("approval", {}).update({"final_render": True, "approved_by": args.by, "notes": args.notes})
            p.write_text(json.dumps(ep, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"render final aprovado por {args.by}; rode `build` para gerar o MP4 final")
            return 0
        if args.cmd == "modelsheet":
            from .characters.modelsheet import build
            from .core.registry import character
            from .integrations.krita import ora_to_kra
            out = LIBRARY / "characters" / args.character
            r = build(character(args.character), out, scale=1.0 if args.character == "caramelo" else 1.4)
            kra = ora_to_kra(r["ora"])
            print(r["png"], kra)
            return 0
        if args.cmd == "background":
            from .backgrounds import forest
            from .integrations.krita import layers_to_kra
            out = LIBRARY / "backgrounds" / args.id
            meta = forest.build(out / "layers")
            print(layers_to_kra(out / "layers", out / f"{args.id}.kra", meta))
            return 0
        if args.cmd == "storyboard":
            from .composition.storyboard import build
            print(build(PROJECTS / args.episode))
            return 0
        if args.cmd == "board":
            from .composition.storyboard import decide
            print(decide(PROJECTS / args.episode, args.scene, args.decision, args.notes))
            return 0
        if args.cmd == "catalog":
            from .animation.library import catalog
            print(json.dumps(catalog(), ensure_ascii=False, indent=2))
            return 0
        if args.cmd == "krita":
            subprocess.Popen([tool("krita"), to_win(Path(args.file).resolve())])
            return 0
        if args.cmd == "opentoonz":
            tnz = PROJECTS / args.episode / "build" / "scenes" / args.scene / f"{args.scene}.tnz"
            subprocess.Popen([tool("opentoonz"), to_win(tnz)])
            print("depois de editar o timing e salvar, rode `build` — as células editadas serão respeitadas")
            return 0
    except StudioError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
