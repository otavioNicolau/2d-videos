# Cartoon Studio AI — instruções para o Claude

Estúdio de animação 2D cartoon (comédia física, estilo TV clássica) que transforma uma ideia em episódio.
Personagens e universos **sempre originais** — referências clássicas só como inspiração técnica.

## Estado
- F0–F6 executadas: MVP "A Torta do Caramelo" em `projects/_laboratorio/torta-do-caramelo/` (saída em `output/`, revisão em `output/REVISAO.md`).
- **Multicanal (20/11/2026)** — dois canais na mesma esteira, cada um com perfil em `canais/<id>/canal.json`:
  | Canal | Bíblias e músicas | Marca | Episódios | Entregas (Windows) |
  |---|---|---|---|---|
  | **Laurinha e Luisinho** (`laurinha`, padrão) | `canais/laurinha/` | `library/brand/laurinha/` | `projects/laurinha/epNN-…` | `Videos\Laurinha e Luisinho\` |
  | **Fofolucos** (`fofolucos`) | `canais/fofolucos/` | `library/brand/fofolucos/` | `projects/fofolucos/epNN-…` | `Videos\Fofolucos\` |
  Testes e protótipos ficam em `projects/_laboratorio/`. Canal da execução: `--canal <id>` na CLI, senão o do projeto
  (`laurinha/ep28-…`), senão `laurinha`. Scripts de placar: `TOONSTUDIO_CANAL=fofolucos …`. Código: `toonstudio/core/canal.py`.
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
- **Identidade visual: a bíblia visual DO CANAL é a base obrigatória** de todo personagem, animal, objeto e cenário — [Laurinha](canais/laurinha/BIBLIA_VISUAL.md) (chapado com contorno) · [Fofolucos](canais/fofolucos/BIBLIA_VISUAL.md) (chapado SEM contorno, monstrinhos). Nunca misturar estilos/cenários entre canais. Mudanças só com autorização do usuário.
- **Entregas SEMPRE na pasta do canal em `C:\Users\DELL\Videos\<Canal>\`** (nunca no Downloads): `NN Título\{Pré-produção, Vídeo longo}\` — **sem Shorts** (decisão do usuário 16/11/2026: só o vídeo normal; `toonstudio short` fica parado) e `Canal\` (capa, perfil, textos, `Vinheta\`). Mesmo formato do projeto ~/videos.
- **Nunca rascunho: padrão profissional sempre e melhoria contínua — [docs/PADRAO_DE_QUALIDADE.md](docs/PADRAO_DE_QUALIDADE.md)** (regra do dono do canal). Todo clipe tem roteiro verso a verso completo, passa pela conferência antes de ser mostrado e cada erro percebido entra no registro de lições.
- **Identidade musical: a bíblia musical DO CANAL é a base obrigatória** de toda música — [Laurinha](canais/laurinha/musicas/BIBLIA_MUSICAL.md) · [Fofolucos](canais/fofolucos/musicas/BIBLIA_MUSICAL.md). Ritmos em `canais/<id>/musicas/estilos.json`, vozes em `canais/<id>/musicas/vozes.json`. **Proibido cortar a música do Suno** (o vídeo usa o take inteiro).
- Código funcional não prova qualidade artística: renderizar, **olhar os quadros** (pranchas) e corrigir.
- Nada de imagem estática deslizando no lugar de animação.
- Não esconder limitações; aprovação humana antes do render final.

## Fluxo de trabalho
`validate` → `storyboard` (prévia em segundos; `board ... aprovar`) → `build` (incremental por cena) → olhar `output/prancha.png`
e quadros de `build/scenes/<sid>/comp/` → corrigir → `approve` → `build`. Testes: `.venv/bin/python -m pytest`.
