# ADR-0012 — Storyboard rápido com aprovação por plano + aprovação humana do render final

- **Status:** aceita · 2026-11-15

## Contexto
O render completo leva ~25 min (Godot na CPU). Na F6, o storyboard rápido mostrou em 9 s problemas que custariam um render
inteiro (personagem escondido atrás do arbusto, cabeça fora do quadro).

## Decisão
- `toonstudio storyboard <ep>`: 3 painéis por plano (início/meio/fim), compostos em Python com o MESMO modelo de câmera e
  parallax do Godot, a partir da mesma timeline. Status por plano em `output/storyboard.json` (`board … aprovar|rejeitar`).
- O build registra como aviso todo plano não aprovado no storyboard.
- O MP4 só perde o sufixo `_CANDIDATO` com aprovação humana registrada no episódio.
- **Atualização 2026-11-23 (pedido do usuário, os dois canais):** a aprovação humana passa a ser a do STORYBOARD.
  Com `approval.storyboard = true` (`toonstudio approve <ep> --by NOME --storyboard`), o `build` já gera o vídeo
  DEFINITIVO (sem `_CANDIDATO`), e o fluxo segue direto: `build` → `final` (vinheta/abertura) → `publicar`
  (Vídeo longo + Pré-produção com storyboard e suno.txt). Não existe mais a pasta "Candidato (para aprovar)" nem a
  segunda aprovação do vídeo. `approval.final_render` continua aceito (compatibilidade).
- O pipeline recusa falas cuja duração real (do TTS) não cabe no plano.

## Consequências
Revisão barata antes do render caro; a decisão final continua sendo humana e fica registrada no episódio.
