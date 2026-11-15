# Cartoon Studio AI

Estúdio de animação 2D de comédia física (estilo desenho clássico de TV, personagens e universo **originais**) que
transforma um episódio descrito em JSON — escrito por IA ou à mão — em vídeo MP4, usando Krita, OpenToonz, Godot e FFmpeg.

Primeiro episódio (MVP): **“A Torta do Caramelo”** — `projects/torta-do-caramelo/` (≈31 s, 7 planos).

## O que tem de verdade
- Personagens desenhados por código vetorial, **redesenhados quadro a quadro** a partir da pose (ADR-0002):
  Caramelo (vira-lata caramelo) e Tevico (bem-te-vi). Folhas de modelo com 5 vistas, 13 expressões, 9 bocas — PNG + KRA.
- Motor de animação com antecipação, overshoot, squash & stretch, smears/linhas de velocidade, arcos, ação secundária
  por molas, ciclos com pé plantado, biblioteca de ações reutilizáveis (ADR-0008).
- OpenToonz: xsheet por plano (exposição em 1s/2s), render por `tcomposer`; retime manual é respeitado (ADR-0003, 0009).
- Krita: folhas de modelo e cenário em camadas como `.kra` editáveis (ADR-0004).
- Godot: composição com parallax de 6 camadas, câmera com zoom e tremor (ADR-0005).
- Vozes com emoção (Higgs TTS 3), tomada escolhida por transcrição cega, tom de cartoon, lip sync pelo Rhubarb (ADR-0010).
- Efeitos sonoros e trilha sintetizados (sem licenças de terceiros), mixagem com ducking.
- Validação por schema + biblioteca + cobertura de câmera; QA de render; aprovação humana antes do final (ADR-0011).

## Uso
```bash
python3 -m venv .venv && .venv/bin/pip install skia-python numpy pillow jsonschema pytest soundfile scipy
.venv/bin/python -m toonstudio.cli validate torta-do-caramelo
.venv/bin/python -m toonstudio.cli build torta-do-caramelo          # gera output/torta-do-caramelo_CANDIDATO.mp4
.venv/bin/python -m toonstudio.cli approve torta-do-caramelo --by "Seu Nome" && .venv/bin/python -m toonstudio.cli build torta-do-caramelo
.venv/bin/python -m pytest
```
Requisitos desta máquina e caminhos das ferramentas: [`config.yaml`](config.yaml), [`docs/f0-validacao.md`](docs/f0-validacao.md).
Arquitetura: [`docs/arquitetura.md`](docs/arquitetura.md) · Decisões: [`docs/adr/`](docs/adr/).

## Licenças
Código, desenhos, cenários, efeitos e trilha gerados por este repositório. Vozes: Higgs TTS 3 (Boson AI, Creator Use Grant —
vídeos publicados exigem na descrição: “This audio was created with Boson AI's Higgs Audio — https://www.boson.ai/higgs-audio”);
referências de voz geradas com Kokoro-82M (Apache-2.0). Rhubarb Lip Sync: MIT.
