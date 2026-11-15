# Arquitetura do Cartoon Studio

Transforma uma ideia num episódio 2D de comédia física. Cada ferramenta tem uma responsabilidade só:

| Ferramenta | Responsabilidade | Como é automatizada |
|---|---|---|
| Python (`toonstudio/`) | roteiro→cenas (contrato JSON), **desenho vetorial dos quadros**, animação, áudio, validação, orquestração | — |
| Krita 5.3 | arquivos-fonte editáveis: folhas de modelo e cenário em camadas (`.kra`) | `krita --export` ORA↔KRA (ADR-0004) |
| OpenToonz 1.8 | **timing** (xsheet, exposição em 1s/2s), edição manual com onion skin, render dos níveis | ToonzScript por CLI + `tcomposer` (ADR-0003, 0009) |
| Godot 4.7 | **composição**: cenário com parallax, câmera (zoom, tremor), profundidade, fade | job JSON + Movie Maker (ADR-0005) |
| FFmpeg | montagem final MP4, loudness, efeitos de voz | CLI |

## Fluxo de um episódio

```
projects/<ep>/episode.json  (schemas/episode.schema.json)
   │  validate: schema + biblioteca real + cobertura de câmera
   ▼
cenário  library/backgrounds/<id>/layers/*.png + background.json  (+ <id>.kra)
vozes    build/audio/lines/<hash>.wav + .visemes.json   (Higgs → Whisper QA → tom → Rhubarb)
   │
   ▼ por cena (checkpoint por hash — só o que mudou é refeito)
timeline   animation/timeline.py: chaves + ações + ciclos + molas + lip sync → pose por quadro
exposição  desenhos únicos (dedupe por pose) + células (1s/2s) + trilha de palco
desenho    characters/*.py desenham cada pose (Skia) → build/scenes/<sid>/levels/<quem>/<quem>.0001.png
OpenToonz  <sid>.tnz (edição, todas as colunas) + otscenes/<quem>.tnz → tcomposer → otrender/<quem>/f.0001.png
Godot      job.json → compositor.gd → comp/000001.png
QA         render OpenToonz == desenho (pixel), quadros vazios, quadros pretos/congelados, contagem
   │
   ▼
mixagem    falas + efeitos sintetizados + ambiente + trilha com ducking → loudnorm −16 LUFS
montagem   FFmpeg H.264 CRF 17 + AAC → output/<ep>_CANDIDATO.mp4 (ou final, após `approve`)
revisão    output/REVISAO.md, prancha.png, qa_report.json
```

## Módulos

- `core/` — config, caminhos WSL↔Windows, estado por hash, validação, registro de personagens.
- `drawing/ink.py` — primitivas de nanquim: contorno de espessura variável (grosso no lado da sombra), traços afinados,
  tubos de borracha, line boil.
- `characters/` — `base.py` (pose, vistas por `turn`, expressões, visemas), `caramelo.py`, `tevico.py`, `props.py` (torta),
  `modelsheet.py` (folha de modelo PNG/ORA/KRA).
- `animation/` — `easing.py`, `cycles.py` (andar, pé-ante-pé, correr, voar, respirar), `library.py` (biblioteca de ações),
  `timeline.py` (compilação e exposição).
- `backgrounds/` — `painter.py` (pintura sem contorno, textura de papel), `forest.py` (clareira em 6 camadas).
- `audio/` — `voice.py` (+ workers em venvs isolados), `sfx.py` (efeitos sintetizados), `music.py`, `mixer.py`.
- `integrations/` — `opentoonz.py`, `krita.py`.
- `render/pipeline.py` — orquestração por cena; `qa/` — pranchas e relatório.
- `godot/compositor.gd` — composição.

## Contratos
- Episódio: `schemas/episode.schema.json`. Coordenadas de palco em unidades (1080 de altura); personagens pelo ponto de apoio.
- Parallax: a camada de fator *f* mostra o trecho centrado em `(cx − W/2)·f + W/2` — a mesma fórmula no validador e no Godot (testado).
- Níveis: quadro padrão 1300×1000 u × 1,5, âncora (650, 900); câmera do OpenToonz a 120 dpi do mesmo tamanho (render 1:1).

## Comandos
```bash
.venv/bin/python -m toonstudio.cli validate torta-do-caramelo
.venv/bin/python -m toonstudio.cli build torta-do-caramelo [--scene s03_roubo] [--force]
.venv/bin/python -m toonstudio.cli approve torta-do-caramelo --by "Nome"
.venv/bin/python -m toonstudio.cli modelsheet caramelo
.venv/bin/python -m toonstudio.cli opentoonz torta-do-caramelo s03_roubo   # retime à mão; o build respeita
.venv/bin/python -m pytest
```
