# ADR-0005 — Composição no Godot Linux (renderer Compatibility); Windows como plano B

- **Status:** aceita · 2026-11-15 · validado em `spikes/godot_compositor/`

## Contexto
No WSL não há Vulkan nem GPU para o OpenGL (só llvmpipe, na CPU). O projeto `~/videos` roda o Godot no Windows porque precisa de 3D com sombras e SSAO. A composição 2D (sprites, parallax, câmera) é leve.

## Decisão
- O Godot 4.7.2 **Linux**, com renderer `gl_compatibility`, compõe as cenas e grava pelo Movie Maker (`--write-movie f.png --fixed-fps N`): tempo determinístico, PNG por quadro + WAV.
- Imagens são carregadas em tempo de execução (`Image.load_from_file`), sem etapa de importação.
- Se uma cena ficar lenta demais na CPU, a mesma cena roda no Godot do Windows (GPU), já validado no `~/videos`.

## Consequências
Sem interop para compor; ≈ 50% do tempo real numa cena simples em 1080p. O desempenho será medido de novo nas cenas reais do MVP.
