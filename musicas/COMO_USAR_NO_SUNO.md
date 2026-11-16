# Como gerar as músicas no Suno

Cada música tem uma pasta (`01_zum_zum_cheguei/` …) com o arquivo **`suno.txt`** pronto para colar no Suno, modo **Custom**:

1. **Style of Music** — ritmo, andamento, bateria e instrumentos do ritmo, vozes (em inglês, o Suno entende melhor).
   Se o Suno cortar o texto, use o **Style curto** logo abaixo.
2. **Exclude** — o que evitar, quando a sua versão do Suno tiver esse campo.
3. **Lyrics** — a letra com as marcações `[Verse]`, `[Chorus]` etc.
4. **Persona** — qual voz oficial usar (enquanto não existir, a voz vai descrita no Style).
5. **Alternativas de ritmo** — a mesma letra em outro ritmo; vale gerar as duas e comparar.

O `suno.txt` é gerado (`toonstudio musica prompt`) a partir de `ficha.json` + `letra.txt`: para mudar algo, me peça
ou edite a ficha/letra, nunca o `suno.txt`.

| # | Música | Ritmo (alternativas) | BPM | Estrutura | Gancho | Dia a dia | Curiosidade |
|---|---|---|---|---|---|---|---|
| 01 | Zum Zum, Cheguei! | Frevo (marchinha) | 160 | A clássica | "zum, zum, cheguei" | acordar, café, cama, mochila | por que a muriçoca faz "zum" |
| 02 | Bate Palminha | Pagodão baiano (samba infantil, axé) | 135 | R bloco que volta | "bate palminha" | voltar da escola, lavar as mãos | dividir o bolo; quem tem amigo nunca fica sozinho |
| 03 | Sorriso Brilhante | Rock (pop infantil) | 165 | D com paradas ("Parou! Congelou!") | "sorriso brilhante" | escovar os dentes | grão de feijão, 2 minutinhos, fechar a torneira |
| 04 | Cadê a Cor? | Axé (funk infantil, pop) | 140 | B pergunta e resposta | "cadê a cor" | lanche, mochila | misturar cores |
| 05 | Conta Comigo | Samba-enredo (batucada) | 145 | F contagem | "conta comigo" | rotina da manhã e da noite | dedos, rodas, patinhas da formiga |
| 06 | Passeio na Lagoa | Forró piseiro (pé de serra) | 160 | A clássica | "passeio na lagoa" | passeio com a vovó, protetor e chapéu | o sapo já foi girino |

## Peças fixas do canal (independentes das músicas)
- `vinheta/vinheta.txt` — vinheta de **até 5 s**, no início de todo vídeo (versão atual: logotipo sonoro do estúdio).
- `chamada/chamada.txt` — chamada para **se inscrever e curtir**, no fim de todo vídeo.
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
