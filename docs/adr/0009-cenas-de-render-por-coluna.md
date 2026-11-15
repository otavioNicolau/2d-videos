# ADR-0009 — Uma cena de edição por plano + cenas de render por coluna no OpenToonz

- **Status:** aceita · 2026-11-15 · complementa ADR-0003

## Contexto
O tcomposer compõe todas as colunas de uma cena. O `Renderer` do ToonzScript (que renderiza colunas isoladas) **trava** quando
o script é executado pela linha de comando (testado: >5 min sem resposta; processo encerrado).

## Decisão
- `build/scenes/<sid>/<sid>.tnz`: cena de EDIÇÃO com uma coluna por personagem/objeto — é a que o animador abre.
- `build/scenes/<sid>/otscenes/<quem>.tnz`: cenas de RENDER de uma coluna, renderizadas pelo tcomposer (PNG RGBA).
- Todos os níveis usam o mesmo quadro padrão (1300×1000 unidades × escala 1,5) e a mesma câmera → render 1:1, conferido pelo QA.
- Se a cena de edição for alterada à mão (hash diferente do gerado), o pipeline lê as células dela e regenera as de render:
  o xsheet do OpenToonz continua sendo a fonte da verdade do timing.

## Consequências
Retime manual funciona. Redesenhar um quadro à mão no OpenToonz exige salvar o nível PNG; o caminho de volta para o pipeline
(sem sobrescrever o redesenho) ainda não está implementado — registrado como limitação.
