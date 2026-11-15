# ADR-0012 — Storyboard rápido com aprovação por plano + aprovação humana do render final

- **Status:** aceita · 2026-11-15

## Contexto
O render completo leva ~25 min (Godot na CPU). Na F6, o storyboard rápido mostrou em 9 s problemas que custariam um render
inteiro (personagem escondido atrás do arbusto, cabeça fora do quadro).

## Decisão
- `toonstudio storyboard <ep>`: 3 painéis por plano (início/meio/fim), compostos em Python com o MESMO modelo de câmera e
  parallax do Godot, a partir da mesma timeline. Status por plano em `output/storyboard.json` (`board … aprovar|rejeitar`).
- O build registra como aviso todo plano não aprovado no storyboard.
- O MP4 só perde o sufixo `_CANDIDATO` com `approval.final_render = true` (`toonstudio approve --by NOME`).
- O pipeline recusa falas cuja duração real (do TTS) não cabe no plano.

## Consequências
Revisão barata antes do render caro; a decisão final continua sendo humana e fica registrada no episódio.
