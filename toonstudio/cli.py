"""Linha de comando do estúdio.

  toonstudio validate <episódio>            valida contra schema, biblioteca e cobertura de câmera
  toonstudio build <episódio> [--scene s03] [--force]   produz (incremental) e gera o MP4 (candidato sem aprovação)
  toonstudio approve <episódio> --by NOME   registra a aprovação humana do render final
  toonstudio modelsheet <personagem>        folha de modelo PNG + KRA (Krita)
  toonstudio background <id>                pinta o cenário e gera KRA com as camadas
  toonstudio catalog                        biblioteca de animações/expressões (JSON)
  toonstudio song import <projeto> <arquivo>  copia a música (original intocado, somente leitura) + cópia de trabalho
  toonstudio song analyze <projeto> [--musica 01]   com --musica: letra conhecida alinhada + partes da música;
                                            voz separada, batidas, letra palavra a palavra → analise/song.json
  toonstudio musica lista                   músicas do canal: ritmo, estrutura, status
  toonstudio musica nova <nome> --titulo T --ritmo R --tipo X [--estrutura A] [--voz dueto]   ficha + modelo de letra
  toonstudio musica checar <música>         confere a letra contra a BIBLIA_MUSICAL (versos, gancho, ritmo citado…)
  toonstudio musica prompt <música>         gera <pasta>/suno.txt (Título, Style, Exclude, Lyrics, Persona, alternativas)
  toonstudio musica medir <música> [arquivos…]   mede as versões do Suno (versoes/) → avaliacao.json + tabela
  toonstudio musica escolher <música> <versão>   registra a versão escolhida (decisão humana)
  toonstudio marca vinheta|chamada <arquivo> corta a peça fixa na batida (vinheta ≤ 5 s, chamada ≤ 10 s)
  toonstudio clipe montar <projeto> --musica 01 [--force]   episode.json do roteiro verso a verso (recusa se incompleto)
  toonstudio publicar <projeto> --musica 01  pasta de publicação (mp4, descrição, srt, extras, miniatura) → Vídeos/Laurinha e Luisinho
  toonstudio short <projeto> [--partes "refrao#1|verso#1,refrao#1"]   Short vertical a partir do clipe roteirizado
  toonstudio final <projeto>                vídeo completo: vinheta + clipe + chamada (peças fixas de library/brand)
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
    sg = sub.add_parser("song"); sg.add_argument("op", choices=["import", "analyze"]); sg.add_argument("episode")
    sg.add_argument("file", nargs="?"); sg.add_argument("--musica")
    mu = sub.add_parser("musica"); mu.add_argument("op", choices=["lista", "nova", "checar", "prompt", "medir", "escolher"])
    mu.add_argument("nome", nargs="?"); mu.add_argument("extra", nargs="*")
    mu.add_argument("--titulo"); mu.add_argument("--ritmo"); mu.add_argument("--tipo", default="")
    mu.add_argument("--estrutura", default="A"); mu.add_argument("--voz", default="dueto")
    vn = sub.add_parser("marca"); vn.add_argument("peca", choices=["vinheta", "chamada"]); vn.add_argument("arquivo")
    vn.add_argument("--inicio", type=float); vn.add_argument("--fim", type=float)
    cl = sub.add_parser("clipe"); cl.add_argument("op", choices=["montar"]); cl.add_argument("episode")
    cl.add_argument("--musica", required=True); cl.add_argument("--force", action="store_true")
    fi = sub.add_parser("final"); fi.add_argument("episode")
    pu = sub.add_parser("publicar"); pu.add_argument("episode"); pu.add_argument("--musica", required=True)
    pu.add_argument("--short", action="store_true")
    sh = sub.add_parser("short"); sh.add_argument("episode"); sh.add_argument("--partes", default="refrao#1|verso#1,refrao#1")
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
        if args.cmd == "song":
            from .audio import song
            pdir = PROJECTS / args.episode
            if args.op == "import":
                if not args.file:
                    raise StudioError("informe o arquivo de áudio (MP3/WAV/M4A) a importar")
                print(song.import_song(Path(args.file), pdir))
            else:
                from .audio import voice
                try:
                    mus = None
                    if args.musica:
                        from .audio import composer
                        mus = composer.pasta(args.musica)
                    print(song.analyze(pdir, musica=mus))
                finally:
                    voice.shutdown()
            return 0
        if args.cmd == "musica":
            return _musica(args)
        if args.cmd == "marca":
            from .audio.brand_audio import trim_on_beat
            lim = 5.0 if args.peca == "vinheta" else 10.0
            r = trim_on_beat(Path(args.arquivo), args.peca, max_len=lim, min_len=2.5 if args.peca == "vinheta" else 6.0,
                             start=args.inicio, end=args.fim)
            print(f"{args.peca}: {r['duracao']}s (trecho {r['inicio']}–{r['fim']}s do original) → {r['arquivo']}")
            return 0
        if args.cmd == "clipe":
            from .audio import composer
            from .composition.clip_draft import rascunho
            pdir = PROJECTS / args.episode
            out = pdir / "episode.json"
            if out.exists() and not args.force:
                raise StudioError(f"{out} já existe (use --force para substituir)")
            try:
                ep = rascunho(pdir, composer.pasta(args.musica))
            except ValueError as e:
                raise StudioError(str(e))
            out.write_text(json.dumps(ep, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{out}: {len(ep['scenes'])} planos, {ep['soundtrack']['end']:.1f}s — conferir o storyboard antes do render")
            return 0
        if args.cmd == "publicar":
            from .audio import composer
            from .composition.publicar import publicar, publicar_short
            fn = publicar_short if args.short else publicar
            print(fn(args.episode, composer.pasta(args.musica)))
            return 0
        if args.cmd == "short":
            from .composition.short import criar_short
            partes = [g.split(",") for g in args.partes.split("|")]
            print(criar_short(args.episode, partes))
            return 0
        if args.cmd == "final":
            from .composition.marca import final
            print(final(args.episode))
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


def _musica(args) -> int:
    from .audio import composer as c
    if args.op == "lista":
        E = c.estilos()
        for d in c.todas():
            f = c.ficha(d)
            print(f"{d.name:26} {E['ritmos'][f['ritmo']]['nome']:24} {f['bpm']:>3} BPM  estrutura {f.get('estrutura', '?')}  {f.get('status', '')}")
        return 0
    if not args.nome:
        raise StudioError("informe a música (nome da pasta, número ou parte do nome)")
    if args.op == "nova":
        if not (args.titulo and args.ritmo):
            raise StudioError("use --titulo e --ritmo (ritmos em musicas/estilos.json)")
        print(c.nova(args.nome, args.titulo, args.ritmo, args.tipo, args.estrutura, args.voz))
        return 0
    d = c.pasta(args.nome)
    if args.op == "checar":
        ck = c.checar(d)
        for i in ck.itens:
            print(f"{ {'erro': 'ERRO ', 'aviso': 'aviso', 'ok': '  ok '}[i.nivel]}  {i.regra}: {i.msg}")
        print(json.dumps(ck.metricas, ensure_ascii=False))
        return 1 if ck.erros else 0
    if args.op == "prompt":
        ck = c.checar(d)
        if ck.erros:
            for i in ck.erros:
                print("ERRO:", i.regra, "-", i.msg)
            raise StudioError("corrija a letra antes de gerar o prompt")
        print(c.escrever_prompt(d))
        return 0
    if args.op == "medir":
        from .audio import voice
        try:
            out = c.medir(d, [Path(x) for x in args.extra] or None)
        finally:
            voice.shutdown()
        print(c.tabela(json.loads(out.read_text(encoding="utf-8"))))
        return 0
    if args.op == "escolher":
        if not args.extra:
            raise StudioError("informe a versão (nome do arquivo sem extensão)")
        print(c.escolher(d, args.extra[0]))
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
