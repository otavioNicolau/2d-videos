# Bíblia musical — FOFOLUCOS

Regras de toda música do canal **Fofolucos** (monstrinhos da Vila Monstrinha, crianças de **5 a 8 anos**).
Herda o processo do canal 1 (`musicas/BIBLIA_MUSICAL.md` e `musicas/PROCESSO_MELHORIA.md`): placares de música, cena e
animação, nota de ouvido e de olho, um ajuste por vez. Aqui só o que é diferente.

## 1. Voz
- **Uma voz principal: menino de 11 a 14 anos** — animado, claro, firme, divertido e um pouco "malandrinho" (o narrador
  da Vila Monstrinha). `vozes.json → fofolucos`. A Persona do Suno é criada do 1º take aprovado.
- Bordão do canal: **"Fofolucos! Rawr!"** (`[Bordão fofolucos]`).
- Os monstrinhos aparecem pelo nome na letra (Bilu, Teco, Gogo, Mimi, Zuzu, Nhoque), mas quem canta é a voz principal.

## 2. Som (estilo F2, 21/11)
- **Essência: TECLADO + CONTRABAIXO + BATERIA, muitos deles** (usuário, 21/11: "o contrabaixo deixa a música
  divertida"). Os três altos e na frente: **teclado** (pisadinha + melodia aguda + riff curto respondendo cada frase),
  **contrabaixo** elétrico groovado (linha que anda e pula, tipo slap) e **bateria = loop eletrônico do teclado** (a mesma
  batida a música toda, bumbo pesado, caixa estalada, palmas). F1 (01, nota 4,9) era só teclado + bateria.
- **Assinatura do canal: órgão de desenho "assustador-divertido"** (só na abertura e nos intervalos), no lugar do sax.
- Clima: festa de monstrinhos — engraçado, um friozinho na barriga, **nunca escuro, nunca de dar medo**; sempre tom maior.
- Duração alvo 2:20–2:50, formato do trio (1 ponte, sem refrão "faster"). **Proibido cortar a música.**
  Estrutura enxuta (21/11, "sempre gera mais de 3 min"): **1 bordão só** (depois do 1º refrão), intervalos de **4 e 6 s**,
  o 3º refrão é **meio refrão** (4 linhas). Groove viciante no andamento do ritmo (nunca abaixo do mínimo dele).

- **Groove próprio do canal — F4** (21/11, usuário: "ajuste fofolucos para groove próprio também"): da 04 em diante o
  Style não leva nome de ritmo; vai o groove dos Fofolucos (bumbo sincopado "boom-ch-boom-chick", caixa e palmas no
  contratempo, teclado pulando no contratempo, baixo nos vãos, um padrão de 2 compassos repetido a música toda), com o
  bloco de produção (MUITO teclado, contrabaixo slap, bateria eletrônica) e o órgão de desenho só na intro/intervalos.
  Config: `estilos.json → canal.groove_proprio`; o `ritmo` da ficha vira só referência.
- **Andamento 130–140 BPM** em toda música nova (usuário, 21/11: "quero 120 a 150 … nos dois canais") —
  `estilos.json → canal.bpm_faixa`; vale mais que a faixa do ritmo (o latino da 03 foi a 110, antes da regra).

## 3. Letra (5 a 8 anos)
- 23/11/2026: a faixa de 5 a 8 anos passou a valer também para o canal Laurinha e Luisinho (regras comuns em
  `canais/laurinha/musicas/BIBLIA_MUSICAL.md → Público: 5 a 8 anos`).
- **NUNCA a palavra "monstro"** (usuário, 21/11): sempre **monstrinho/monstrinhos** — também no título, nos letreiros
  e na descrição do YouTube. O verificador da letra acusa erro (`canal.json → palavras_evitar`, que também barra
  maluco/louco → maluquinho e chifrão/chifrudo → chifrinho).
- Mais **história e piada** que o canal 1; vocabulário um pouco mais rico; **refrão-desafio** para cantar junto
  ("quem consegue…?", "faz a cara de monstrinho!").
- Temas: escola de monstrinhos, amizade, desafios, medos bobos (o monstrinho com medo do escuro… ou de criança!), festa do
  pijama, comidas nojentinhas engraçadas, esportes, travessuras — **sem** conteúdo de bebê (cores/números básicos).
- Fim de toda música: convite para o joinha e para se inscrever **com o papai e a mamãe** (regra do estúdio).
- Nada de "que delícia"/"gostoso".


## Duração a 130–140 BPM (21/11/2026 — usuário: "cuidado pro Suno não fazer música de 1:30")
Andamento mais rápido encurta a música (a mesma letra a 130 em vez de 108 BPM sai ~17 % menor). Estrutura atual:
**1 bordão + intervalo de 6 s**, **ponte cantada 2 vezes** ("De novo!" no meio), **intervalo de 8 s** e **último refrão
inteiro**. O verificador estima a duração com o andamento (≈1,3 compasso por linha cantada, medido nos takes reais:
Fofolucos 02/03 e Laurinha 29) e avisa abaixo de 140 s. Laurinha 29–49: estimativa 2:23–2:33.
