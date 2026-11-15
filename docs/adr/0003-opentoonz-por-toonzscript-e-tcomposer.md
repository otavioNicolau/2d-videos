# ADR-0003 — OpenToonz automatizado por ToonzScript em linha de comando + tcomposer

- **Status:** aceita · 2026-11-15 · validado em `spikes/f0_opentoonz.py`

## Contexto
O formato `.tnz` é XML sem documentação oficial. O OpenToonz 1.8 executa um ToonzScript passado como argumento (`OpenToonz.exe arquivo.toonzscript`) e traz o renderizador de linha de comando `tcomposer.exe`.

## Decisão
- Python gera os níveis (PNG `nome.0001.png`) e um ToonzScript que carrega os níveis, preenche o xsheet (`setCell`, exposição em 1s/2s/holds) e salva a cena. **Quem escreve o `.tnz` é o próprio OpenToonz**, não o nosso código.
- Ajustes que o ToonzScript não expõe (fps, câmera) são feitos editando o XML gerado, usando como referência um `.tnz` real do 1.8.
- Render dos níveis por `tcomposer` (PNG RGBA). Sucesso = marcador impresso pelo script + arquivo existente (o exit code é 1 mesmo com sucesso).
- O xsheet do OpenToonz é a **fonte da verdade do timing** de cada personagem; o Godot não recalcula timing.

## Consequências
- Um animador pode abrir qualquer cena, usar onion skin, redesenhar quadros e re-renderizar sem quebrar o pipeline.
- Dependência de um formato não documentado limitada a poucos campos; testes de regressão cobrem a edição do XML.

## Alternativas
Escrever o `.tnz` do zero (frágil); importar XDTS (exige interface gráfica); pular o OpenToonz e mandar os PNGs direto ao Godot (descartado: viola a responsabilidade definida na especificação e impede a edição manual).
