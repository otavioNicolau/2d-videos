# Cartoon Studio AI — instruções para o Claude

Estúdio de animação 2D cartoon (comédia física, estilo TV clássica) que transforma uma ideia em episódio.
Personagens e universos **sempre originais** — referências clássicas só como inspiração técnica.

## Estado
- F0–F6 executadas: MVP "A Torta do Caramelo" em `projects/torta-do-caramelo/` (saída em `output/`, revisão em `output/REVISAO.md`).
- Arquitetura: [docs/arquitetura.md](docs/arquitetura.md). Pendente: F7 (IA ideia→episode.json), F8 (interface Godot).
- Decisões em [docs/adr/](docs/adr/). Decisão estrutural nova → novo ADR.

## Responsabilidades (não duplicar)
- **Python** (`toonstudio/`): orquestra, desenha os quadros vetoriais (ADR-0002), valida, áudio.
- **OpenToonz** 1.8: timing por personagem (xsheet = fonte da verdade), edição manual, render de níveis via `tcomposer` (ADR-0003).
- **Krita** 5.3.4.1: arquivos-fonte KRA (model sheets, cenários); troca por ORA via `krita --export` (ADR-0004).
- **Godot** 4.7.2 Linux, Compatibility: só composição (câmera, parallax, camadas, áudio) via Movie Maker (ADR-0005).
- **FFmpeg**: montagem final MP4.

## Caminhos
- OpenToonz: `/mnt/c/Program Files/OpenToonz/{OpenToonz,tcomposer}.exe` — exit code 1 mesmo com sucesso.
- Krita: `/mnt/c/Program Files/Krita (x64)/bin/krita.com` — `kritarunner` não funciona no Windows.
- Godot: `~/.local/opt/godot/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64`
- Rhubarb: `tools/rhubarb/rhubarb -r phonetic` (tools/ não é versionado).
- Caminhos para o Windows: `wslpath -w` (dados ficam no WSL, ADR-0007).

## Regras
- Código funcional não prova qualidade artística: renderizar, **olhar os quadros** (pranchas) e corrigir.
- Nada de imagem estática deslizando no lugar de animação.
- Não esconder limitações; aprovação humana antes do render final.

## Fluxo de trabalho
`validate` → `storyboard` (prévia em segundos; `board ... aprovar`) → `build` (incremental por cena) → olhar `output/prancha.png`
e quadros de `build/scenes/<sid>/comp/` → corrigir → `approve` → `build`. Testes: `.venv/bin/python -m pytest`.
