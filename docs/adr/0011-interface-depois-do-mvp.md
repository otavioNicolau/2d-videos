# ADR-0011 — Linha de comando + relatórios antes da interface gráfica

- **Status:** aceita · 2026-11-15

## Contexto
A especificação pede 15 telas. O critério de sucesso é um episódio com qualidade convincente; a interface não ajuda a provar isso.

## Decisão
- MVP com `toonstudio` (CLI): validate, build (incremental por cena), approve, modelsheet, background, catalog, krita, opentoonz.
- Revisão por arquivos: `output/REVISAO.md`, `output/prancha.png`, `output/qa_report.json`, pranchas de animação.
- Aprovação humana registrada no episódio (`approval.final_render`); sem ela o MP4 sai com sufixo `_CANDIDATO`.
- A interface (app Godot) vem depois, como camada fina sobre `toonstudio.render.pipeline.Episode`.
