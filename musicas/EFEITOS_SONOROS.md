# Efeitos sonoros nos clipes (a partir da 19)

Objetivo: o clipe "conversar" com a criança também pelo som. O bicho late quando aparece, o robô faz bip, as crianças
comemoram no fim do refrão. Os desenhos animados de referência usam isso o tempo todo.

## Como entra no vídeo
- No roteiro, cada plano pode ter `"sons": [{"t": 1.2, "id": "latido", "vol": -3}]`. `t` é contado em segundos desde
  o começo do plano. `vol` é em dB: 0 é o nível padrão (soa como uma batida da música), −3 a −6 para efeitos de fundo.
- A montagem final (`marca.final`) mistura os efeitos **depois** do equilíbrio voz/batida e **antes** da masterização,
  então eles saem no mesmo volume e com o mesmo timbre do resto. O número de efeitos usados fica em `output/master.json`.
- Um efeito gravado (.wav em `library/audio/sfx/<pasta>/<id>.wav`) tem prioridade sobre o sintetizado de mesmo nome.

## Regras de uso
1. **Nunca em cima de palavra cantada.** O efeito vai no fim do verso, na respiração entre versos ou no intervalo.
   A letra é a estrela, e o efeito responde a ela.
2. **De 1 a 3 efeitos por plano.** Mais do que isso vira bagunça (o mesmo problema do "muita informação" da voz).
3. **O efeito tem dono.** Toca quando a coisa acontece na tela: o cachorro abre a boca e late, o robô trava e solta faísca.
4. **No refrão, o mesmo efeito toda vez.** Vira um "bordão sonoro" que a criança espera (por exemplo, "travou!" e zap).
5. **Crianças comemorando** ("eba!", "uhuu!", risadinha) no fim do refrão, nos intervalos e no tchau. Nunca grito
   assustado, choro ou som alto e estridente: o público é de 2 a 6 anos e o vídeo é "feito para crianças".
6. **Bicho:** o som do bicho entra quando ele aparece ou é cantado, de preferência uma vez por plano.

## Efeitos sintetizados (já prontos, sem licença)
| id | som | uso |
|---|---|---|
| boing | mola | pulo, quique, susto engraçado |
| whoosh | vento de passagem | voo, giro, corte rápido |
| ding | sininho | acertou, ideia |
| plim | brilho mágico | algo aparece, acende, forma acesa |
| bip_bop / bips | robô | robô fala ou pensa |
| zap | faísca | travou, choque engraçado |
| pfff | murchar | pilha acabou, balão murcha |
| splash | respingo | água, onda, poça |
| palminhas | três palmas | comemorar |
| tambor | rufar + prato | revelação ("tcharam!") |
| pop | estalo | bolha estoura, callout aparece |
| whistle_up / whistle_down | apito de desenho | subir / cair |
| tweets | passarinhos | campo, manhã |
| bonk | pancada com mola | trombada engraçada |

Para ouvir: a pasta `Canal\Efeitos sonoros (teste)` no Windows.

## Efeitos gravados (o usuário baixa; não dá para sintetizar bem)
Fonte recomendada: **Biblioteca de áudio do YouTube** (YouTube Studio → Biblioteca de áudio → Efeitos sonoros), que é
liberada para vídeos do YouTube. Segunda opção: **Pixabay** (efeitos sonoros: uso comercial livre, sem crédito).
Não usar som de outro canal nem de vídeo baixado.

Salvar como `.wav` ou `.mp3` convertido, com o nome abaixo, na pasta indicada. Anotar a origem em
`library/audio/sfx/LICENCAS.md`.

| pasta | arquivo | o que procurar |
|---|---|---|
| bichos | latido.wav | "dog bark" (cachorrinho, 1 ou 2 latidos curtos) |
| bichos | miau.wav | "cat meow" (miado curto e fofo) |
| bichos | piu.wav | "bird chirp" / "chick" (pintinho piando) |
| bichos | quack.wav | "duck quack" |
| bichos | mee.wav | "sheep" / "lamb baa" |
| bichos | muu.wav | "cow moo" |
| bichos | croac.wav | "frog croak" |
| bichos | galo.wav | "rooster" (cocoricó) |
| bichos | relincho.wav | "horse neigh" |
| criancas | eba.wav | "kids cheer" / "children yay" (curto, alegre) |
| criancas | uhuu.wav | "kids woohoo" |
| criancas | risada.wav | "kids laugh" / "children giggle" |
| criancas | aplausos.wav | "kids applause" (curto) |
| criancas | ooh.wav | "kids ooh" / "children wow" (surpresa) |
| desenho | buzina.wav | "clown horn" / "bike horn" |
| desenho | apito.wav | "referee whistle" curto |
