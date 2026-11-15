# ADR-0002 — Personagens e cenários desenhados por código vetorial procedural

- **Status:** aceita · 2026-11-15 · escolha do usuário

## Contexto
Nenhuma das ferramentas obrigatórias desenha sozinha: a API do OpenToonz não cria traços e a do Krita só recebe pixels prontos. Alternativas avaliadas: artista humano (qualidade máxima, não automático) e IA geradora de imagem (tremulação e perda de consistência quadro a quadro; 6 GB de VRAM).

## Decisão
- Personagens e cenários são definidos como **formas vetoriais paramétricas** (Bézier, traço de espessura variável, paleta fixa) em Python.
- Cada quadro é **redesenhado a partir da pose** (squash & stretch, smears, arcos, antecipação, overlap, line boil) — nunca um sprite estático deslocado.
- A saída de cada desenho é PNG com alfa, entregue ao OpenToonz como nível; os arquivos-fonte artísticos (model sheets, cenários) também saem como KRA para revisão e retoque no Krita.

## Consequências
- Automático e consistente entre cenas e episódios.
- Teto visual honesto: cartoon de TV limpo; não alcança o traço à mão dos anos 1940–50. A aprovação das model sheets (F2) é o ponto de decisão artística.
- Qualquer quadro pode ser retocado à mão no OpenToonz/Krita depois.
