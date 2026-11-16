# Como gerar as músicas no Suno

Cada arquivo em `letras/` tem três blocos para colar no Suno, no modo **Custom**:

1. **Style of Music** — o ritmo e os instrumentos (em inglês, o Suno entende melhor).
2. **Exclude** — o que evitar (lento, triste…), quando a sua versão do Suno tiver esse campo.
3. **Lyrics** — a letra com as marcações `[Verse]`, `[Chorus]` etc. (o Suno usa as marcações para montar a música).

| # | Música | Ritmo (só no campo Style) | BPM | Dia a dia | Curiosidade / aprendizado |
|---|---|---|---|---|---|
| 01 | Zum Zum, Cheguei! | Frevo | 160 | acordar, café, arrumar a cama, mochila, tchau pra mamãe | por que a muriçoca faz "zum" (a asinha batendo rápido) |
| 02 | Bate Palminha | Pagodão baiano | 135 | voltar da escola, lavar as mãos, brincar com amigos | dividir o bolo; quem tem amigo nunca fica sozinho |
| 03 | Sorriso Brilhante | Rock | 165 | escovar os dentes | pasta do tamanho de um grão de feijão, 2 minutinhos, fechar a torneira |
| 04 | Cadê a Cor? | Axé | 140 | cores do lanche, da mochila | misturar cores: azul+amarelo=verde, vermelho+amarelo=laranja, azul+vermelho=roxo |
| 05 | Conta Comigo | Samba-enredo | 145 | rotina da manhã (1→10) e da noite (10→1) | quantos dedos, rodas, patinhas da formiga |
| 06 | Passeio na Lagoa | Forró piseiro | 160 | passeio de domingo com a vovó, protetor e chapéu | o sapo já foi girino |

## Peças fixas do canal (independentes das músicas)
- `00_vinheta_abertura.txt` — vinheta de **até 5 s**, no início de todo vídeo.
- `99_chamada_inscreva.txt` — chamada para **se inscrever e curtir**, no fim de todo vídeo.
Geradas uma vez, com batida/tom próprios; ficam na biblioteca do canal e entram automaticamente em todos os clipes,
qualquer que seja o ritmo da música do episódio.

## Regras das letras
1. **Nunca citar o ritmo na letra** ("é o rock…", "é o axé…"): o ritmo vai só no campo Style.
2. **Refrão forte e grudento**, com sílabas divertidas e comandos de dança, repetido 3 vezes.
3. **Uma curiosidade ou aprendizado** por música (dito de forma divertida).
4. **Dia a dia da criança** em toda música (abaixo).
5. O grito "Laurinha e Luisinho!" fica nos intervalos — a vinheta de abertura já apresenta o canal.

### Toda música tem algo do DIA A DIA da criança
Para gerar identificação, cada letra traz momentos da rotina: acordar, café da manhã, escovar os dentes, lavar as
mãos, arrumar a cama, guardar os brinquedos, mochila e escola, lanche, dividir com o amigo, banho, hora de dormir,
passeio com a família. Situações simples e reconhecíveis, com bons hábitos mostrados de forma divertida (nunca
como bronca).

## Estrutura padrão do canal (inspirada na análise de clipes infantis de sucesso)
`Intro (instrumental)` → `Verso (4 linhas)` → `Refrão (sílabas divertidas + comandos de dança)` →
`"Vai!" + 8 s instrumental` → `Verso 2` → `Refrão` → `Ponte (curiosidade ou brincadeira)` → `"Vai!" + 8 s instrumental` → `Refrão` → `Tchau`.
Andamento rápido, tom maior, **bateria mais alta que tudo**, duração-alvo **2:45–3:00**.
**Muita batida:** todo Style leva `heavy drum-driven beat, pounding kick drum on every beat, booming bass drum, loud claps,
big drum fills before every chorus, percussion breakdowns, drums loudest in the mix`; a letra marca `[Drum Fill]` antes
de cada refrão e os intervalos são `[Drum Break]` (só batucada). Se o seu Suno limitar o tamanho do Style, mantenha
pelo menos: ritmo + BPM + `heavy drum-driven beat, pounding kick, big drum fills, drums loudest in the mix` + vozes.
Os intervalos instrumentais são os momentos de dança no clipe; o "inscreva-se" entra no vídeo, não na música.

## Dicas para sair bom
- Gere **2 a 4 versões** de cada e escolha a melhor; ouça se as palavras saíram claras.
- **Mesma voz em todas as músicas — Persona:** gere a primeira música até a voz ficar do seu gosto; na biblioteca,
  abra o menu da música (⋯) → **Create Persona** (nome: "Laurinha e Luisinho"); nas próximas, selecione essa Persona
  no modo Custom. Ela mantém o estilo da voz, mas pode variar um pouco — gere 2–3 versões e escolha. Se o seu plano
  tiver o recurso **Voices**, ele tende a ser mais fiel ao mesmo cantor. (Nomes de botões mudam com as versões do Suno.)
- Duração boa para clipe infantil: **2 a 3 minutos**.
- Baixe em **WAV** (melhor qualidade) ou MP3 e coloque em `~/2d/musicas/<nome-da-musica>/`.
  Mande também a letra final (se o Suno mudou alguma palavra) — ela é usada na legenda e na boca dos personagens.

## Direitos e publicação
- As letras são **originais**, escritas para o canal.
- **Atenção ao plano do Suno:** músicas geradas no plano gratuito **não podem ser usadas comercialmente**
  (vídeo monetizado no YouTube). Para o canal, gere as músicas num **plano pago** (Pro/Premier) — confira os termos
  atuais do Suno antes de publicar.
