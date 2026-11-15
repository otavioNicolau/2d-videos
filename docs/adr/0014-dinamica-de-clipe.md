# ADR-0014 — Dinâmica de clipe: coreografia por batidas, câmera na batida, transições, tela dividida, efeitos

- **Status:** aceita · 2026-11-15 · pedido do usuário: "o fundo tem que se movimentar, câmera aproximar, slider entre cenas,
  tela dividida, colorido, muito movimento"; referências de gênero analisadas (≈290 quadros de dois clipes).

## Decisão
- **Coreografia** (`animation/cycles.py: CHOREO`): passos definidos em poses-chave por batida (balanco, palmas, pulinho, passinho,
  cabeca, lango, bracos, lado, marcha, twist), interpolados por Catmull-Rom cíclica (arcos, sem paradas); canais aditivos (`turn+`).
- **Ação secundária pelo corpo**: molas em cabeça, cabelo e chapéu reagem à aceleração do corpo dançando.
- **Câmera na batida** (`camera.beat`): pulso de zoom, aproximar/afastar por compasso, balanço e quique; `camera.punch` = soco de zoom.
- **Fundos gráficos que rolam sem emenda** (xadrez 45°, bolinhas, ondas; período exato) e pulsam na batida; raios giram por batida.
- **Partículas** determinísticas no Godot (bolhas, confete, estrelas, corações, notas).
- **Transições** (`render/post.py`): deslizar (4 direções, com faixa branca), cortina diagonal, círculo, zoom, giro — sem mudar a
  duração (a música manda). **Tela dividida** (`panels` + `layout`): cada painel é uma sub-cena completa.
- **Palavras de destaque** (`callouts`): texto grande que pula (ASS com escala/rotação animadas).
- **Personagens**: volume suave (gradiente + brilho) no kit; olhos "^^"; modelo de criança reaproveitável (Luizinho → Laurinha).

## Consequências
Clipe com corte a cada ~4–5 s e algo se mexendo em toda parte. Cenas com fundos gráficos renderizam rápido (~0,2 s/quadro);
cenários pintados continuam lentos (~0,8 s/quadro). Tela dividida custa dois renders.
