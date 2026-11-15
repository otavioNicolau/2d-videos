# ADR-0004 — Krita integrado por linha de comando, com ORA como formato de troca

- **Status:** aceita · 2026-11-15 · validado em `spikes/f0_krita.py`

## Contexto
O Krita 5.3.4.1 tem API Python, mas no Windows o `kritarunner` (execução sem interface) não importa módulos. A exportação `krita.com --export` funciona para qualquer formato. Escrever `.kra` direto é inviável (camadas em formato de tiles); o OpenRaster (ORA) é um zip com um PNG por camada.

## Decisão
- Estúdio → Krita: Python escreve ORA (camadas nomeadas, padrão `BG_`/`MG_`/`FG_`/`FX_`) e `krita --export` gera o `.kra` editável.
- Krita → estúdio: `krita --export` do `.kra` para ORA (camadas com nome e posição) e PNG achatado.
- O `.kra` é o arquivo-fonte versionado; os PNGs são derivados e regeneráveis.

## Consequências
- Sem plugin para instalar; funciona com o Krita fechado.
- 15–18 s por chamada: usado só para ativos que mudam pouco, nunca quadro a quadro.
- Um plugin do Krita (botão "enviar ao estúdio") fica para a fase da interface, se fizer falta.
