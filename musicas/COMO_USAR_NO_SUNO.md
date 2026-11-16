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

## Regras
Todas as regras (identidade, bordões, escolha do ritmo, letra, estruturas, avaliação) estão na
**[BIBLIA_MUSICAL.md](BIBLIA_MUSICAL.md)**. Ritmos em [estilos.json](estilos.json); vozes em [vozes.json](vozes.json);
cada música tem a sua pasta `<nº>_<nome>/` com `ficha.json` e `letra.txt`.

## Dicas para sair bom
- Gere **2 a 4 versões** de cada e escolha a melhor; ouça se as palavras saíram claras.
- **Mesma voz em todas as músicas — Personas oficiais** (`laurinha`, `luisinho`, `dueto`, em [vozes.json](vozes.json)):
  gere a música até a voz ficar do seu gosto; na biblioteca, abra o menu da música (⋯) → **Create Persona**; me diga o
  nome que você deu e de qual música/versão veio, para eu registrar. Nas próximas, selecione a Persona no modo Custom.
  Ela mantém o estilo da voz, mas pode variar um pouco. Se o seu plano tiver **Voices**, tende a ser mais fiel.
  (Nomes de botões mudam com as versões do Suno.)
- Duração-alvo: **2:20 a 2:50**.
- **Nunca fique com a primeira versão:** baixe as 2–4 versões em **WAV** (ou MP3) para `~/2d/musicas/<nº>_<nome>/versoes/`;
  o estúdio mede cada uma (andamento, começo, pronúncia) e você escolhe.
  Mande também a letra final (se o Suno mudou alguma palavra) — ela é usada na legenda e na boca dos personagens.

## Direitos e publicação
- As letras são **originais**, escritas para o canal.
- **Atenção ao plano do Suno:** músicas geradas no plano gratuito **não podem ser usadas comercialmente**
  (vídeo monetizado no YouTube). Para o canal, gere as músicas num **plano pago** (Pro/Premier) — confira os termos
  atuais do Suno antes de publicar.
