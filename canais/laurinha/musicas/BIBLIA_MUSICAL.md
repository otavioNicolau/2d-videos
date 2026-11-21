# Bíblia musical — Laurinha e Luisinho

Base obrigatória de toda música do canal, como a [BIBLIA_VISUAL.md](../BIBLIA_VISUAL.md) é para o visual.
Fonte única das regras: o passo a passo do Suno ([COMO_USAR_NO_SUNO.md](COMO_USAR_NO_SUNO.md)) só aplica o que está aqui.

| Arquivo | O que guarda |
|---|---|
| este documento | identidade, regras de letra, estruturas, avaliação |
| [estilos.json](estilos.json) | biblioteca de ritmos: andamento, bateria, instrumentos, peso da batida, Exclude, temas que combinam |
| [vozes.json](vozes.json) | vozes oficiais e Personas do Suno (nomes registrados depois de criadas) |
| `<nº>_<nome>/ficha.json` + `letra.txt` | cada música: tema, ritmo, estrutura, voz, cenas; a letra com as marcações do Suno |

---

## Essência do som (E14, 21/11/2026 — pedido do usuário)
**TECLADO + CONTRABAIXO + BATERIA, muitos deles**: "identifiquei outro instrumento que deixa a música divertida —
contra baixo, bateria, teclado". Os três altos e na frente: teclado arranjador (pisadinha, melodia aguda e o riff
"tram-tram" depois de cada frase), **contrabaixo elétrico groovado** (linha que anda e pula, tipo slap) e bateria
eletrônica do teclado (o mesmo loop a música toda). O sax fica só como toque na abertura e nos intervalos.
Vale da 29 em diante (`estilos.json → canal.trio`, versão E14; E13 = 27/28, sem contrabaixo).

## Igual ao Fofolucos (22/11/2026 — "deixar o canal Laurinha do mesmo jeito desse")
- **Estrutura enxuta** (as músicas saíam com mais de 3 min): **1 bordão só** (depois do 1º refrão) com intervalo de
  **4 s**; depois do 2º refrão, intervalo de **6 s**; o 3º refrão é **meio refrão** (as 4 primeiras linhas,
  `[Chorus - louder, last time, half chorus]`). Modelo em `canal.json → modelo_letra`. As letras 29–49 foram
  convertidas assim em 22/11 (o 2º bordão + intervalo de 8 s saíram; o 1º intervalo de 8 s virou 4 s).
- **Groove próprio do ritmo**: um ritmo pode trazer o seu groove em `estilos.json → ritmos.<r>.peso_style` (vale
  antes do groove do canal). Primeiro caso: **latino = dembow** (Fofolucos 03 "Cosquinha de Monstrinho", nota 4,9 —
  batida sincopada 0,72 e baixo no contratempo 0,59, os dois no alvo pela primeira vez). Usado na 33 e na 44.

## 0. Jeito de escrever (18/11/2026 — análise da referência, aprovado pelo usuário; vale para toda letra nova)
Detalhes em [REFERENCIA_ANIMADINHOS.md](REFERENCIA_ANIMADINHOS.md).
1. **Premissa engraçada numa frase**: um personagem com um exagero (o queijo que estica até a lua, a vovó de patinete que
   ninguém alcança, o macarrão que não acaba). Nada de "aula".
2. **Molde que troca uma palavra** ("estica pro lado / pro outro / pra cima"; "foi o sapo? foi a formiga?"; "passou pela
   cozinha / pelo quintal / pela lua").
3. **Rima em todo par de versos**, palavras simples.
4. **O bloco repete igual**: verso → refrão → intervalo → ponte → **o mesmo verso** → refrão → intervalo → ponte → refrão
   forte → convite. Poucas linhas diferentes (~22).
5. **Uma voz narra a música inteira** (a Persona da ficha). Sem respostinha em todo verso: no máximo um "ê!/vai!" no refrão.
   (No Suno, texto entre parênteses vira voz de fundo — o gerador já converte, mas a letra nova nem usa.)
6. **Falar com quem assiste**: comandos ("estica pro lado") e perguntas ("foi você?").
7. **Lição só se for piada**; curiosidade vai só na descrição.
8. Temas: mais **comida**, **personagens engraçados** (série da Vovó), **São João** em junho; títulos com som engraçado.

## 1. O que aprendemos com o mercado (referência: Animadinhos)

Estudamos características gerais do gênero, **nunca** letras, melodias, arranjos, personagens ou títulos.

- **Catálogo (134 vídeos, nov/2026):** comida e objetos de casa (~30), animais (~30), brincadeiras e danças com comando (~20),
  datas do ano (~15, São João e Carnaval pesam muito), educativas e rotina (~13), personagens do canal (~10).
  Educativas são minoria: **diversão primeiro**, o aprendizado vem dentro da brincadeira.
- **Título = gancho = refrão:** uma ou duas palavras, muitas vezes com som divertido ou repetição.
- **Séries com personagem fixo** (um mesmo bicho em várias músicas) criam fidelidade.
- **Duração:** mediana 2:40; 75% até 3:00.

### Medição de 13 músicas (16/11/2026)
Batidão, Dança do Calango, Pintinho Amarelinho, Sorvete, Vamos pra Escola, Neneco, Boi Colorido, Morto-Vivo, Rock do Billy,
Lá Vem o Trem, Frevo, Teréu Théo Théo, Celular do Vovô. Medido por computador (separação de instrumentos, batidas,
transcrição da voz só para contar versos e repetições; nada da letra delas é guardado).

| Medida | Resultado | Para nós |
|---|---|---|
| Abertura | **a mesma vinheta de 3,7 s em todos os vídeos**; depois, ~4 s de introdução da música | confirma a vinheta fixa de até 5 s; intro da música ≤ 4 s |
| Andamento | dois grupos: **~130 BPM** (Sorvete, Neneco, Pintinho, Teréu, Trem) e **~160–172** (Batidão, Calango, Celular, Escola); Rock do Billy ~108; 4 ambíguas (metade/dobro) | não é tudo 172: a faixa de cada ritmo em `estilos.json` vale |
| Tom | **13 de 13 em tom maior** | sempre maior |
| Mixagem | bateria ~36% e voz ~37% (empatadas no topo); baixo ~12% | bateria tão alta quanto a voz nos ritmos de peso forte |
| Mixagem em 4 faixas (17/11, Celular do Vovô, pedido do usuário: "esse tipo de toque") | bateria 36%, **baixo 19%**, **instrumentos 23%**, **voz 23%**; as nossas saíam com voz 32–43%, baixo 13–16% e instrumentos 9–19% (arranjo magro, voz alta) | Style do canal pede banda cheia, baixo saltado, teclados e metais, voz dentro da mistura; tirado o "vocals buried" do Exclude |
| Tempo cantado | 46–76% (mediana 62%) | deixar ~1/3 da música para dançar |
| **Verso** | **3 a 5 palavras** (mediana 4), **1 a 2 s** cada | versos curtos; nossos versos de 6–8 palavras são longos |
| Variedade | 31–72 linhas cantadas, mas só **8–31 diferentes** (mediana ~23); 57–100% das linhas se repetem | poucas ideias, muito bem repetidas |
| **Gancho** | frase de **3 palavras** repetida **~10 vezes** (de 2 a 22); entra entre 11 e 61 s (mediana ~35 s) | o título vira gancho de 3 palavras |
| Forma | **9 de 13: um bloco de ~55–75 s cantado 2 ou 3 vezes** quase igual, separado por intervalos; 2 progressivas (cada parte nova, como uma lista de cores) | estruturas A (bloco que volta) e C/F (lista) são as do mercado |
| Intervalos | pares de 4–5 s com "Vai!" ou o grito do canal no meio; às vezes 8–15 s | intervalo puxado por bordão, 4–8 s |
| Grito do canal | 10 de 13, logo após a intro (~10–14 s) e dentro dos intervalos, até 8 vezes | nosso equivalente: os bordões |
| Final | corte seco e ~4 s de silêncio (tela final) | terminar com batida final limpa (`[End]`); a chamada entra no vídeo |
| Cortes de cena | ~4 a 22 por minuto (mediana ~10: um corte a cada ~6 s) | cortar na batida a cada 3–6 s |
| **Instrumentos** (18/11, reconhecedor de sons PANNs/AudioSet no instrumental, Celular do Vovô e Dança do Calango × nossas 11–13) | deles: **sintetizador, teclado, piano/piano elétrico, sampler e efeitos de desenho ("boing")**; bateria acústica, metais e guitarra ≈ 0; gêneros: "funny music", "video game music", latina/africana. Nossas: **bateria acústica (caixa, bumbo, viradas, aro), metais (trompete, trombone, sax), chocalho**; zero sintetizador/teclado; gêneros: swing, ska, salsa | o "toque" deles é **produção de teclado** (synth + piano elétrico + percussão programada + efeitos), não banda ao vivo |
| **Batida** (18/11, bateria separada, ataques por semicolcheia) | caixa/palma e chimbal/shaker **no contratempo** (o "e" entre os tempos), quase nunca em cima do tempo; bumbo sincopado | as nossas batiam caixa e chimbal **em cima do tempo** (jeito de rock/pop de banda) |
| **Som final** (18/11) | presença 2,5–6 kHz 3–4%, agudo 6–16 kHz ~0,8%, sub 16–22%, masterizado alto | as nossas: presença 10–11%, agudo 3–7%, sub 2–8% (estridente, fino) → masterização automática no `final` |

## 2. Identidade do canal

**Conceito: "o mundo visto por quem é pequenininho e voa".** A gota de chuva é gigante, a formiga é vizinha, o ventilador
vira tempestade, o jardim é uma floresta. O dia a dia da criança, visto de cima e de pertinho.

Toda música transmite: alegria, energia, diversão, criatividade, movimento, musicalidade brasileira e memorização fácil.

### Assinaturas
- **O "zum" das asinhas:** aparece em toda música (intro, virada, resposta do coro ou final). É o mesmo som da vinheta.
- **Bordões oficiais:**
  - Laurinha: **"Bora, turminha!"** (ela é a mais velha e puxa a turma);
  - Luisinho: **"Zum-zum, que massa!"** (o sapeca que se empolga).
  - Uso: o bordão ocupa o lugar do "Vai!" antes do intervalo de dança. Pelo menos um por música; os dois no dueto.
    Nunca mais de 3 vezes cada na mesma música.
- O nome do canal ("Laurinha e Luisinho!") pode aparecer como grito do coro em um intervalo; a vinheta já apresenta o canal.

### Personalidade musical
| | Laurinha | Luisinho |
|---|---|---|
| Papel | líder, organiza a brincadeira, explica a curiosidade | sapeca, faz a pergunta engraçada, erra e ri |
| Voz | menina, clara, doce e firme | menino, animado, brincalhão |
| Na letra | comandos ("agora todo mundo…"), perguntas ao coro | onomatopeias, exageros, "ih!", respostas erradas que viram piada |

## 3. Vozes e Personas (Suno)

- Formatos: só Laurinha · só Luisinho · versos alternados · dueto · coro infantil · pergunta e resposta com o coro.
- **Vozes fixas, nunca inventar voz nova por música.** As Personas oficiais ficam em [vozes.json](vozes.json):
  `laurinha`, `luisinho` e `dueto`. Enquanto não forem criadas no Suno, o campo `suno_persona` fica vazio
  e o Style usa a descrição padrão da voz.
- Criar a voz: gerar a música até a voz ficar boa → na biblioteca, menu da música (⋯) → **Create → Voice** (a antiga
  "Persona" virou "Voice" no Suno de 2026) → registrar o nome em `vozes.json`. Usar com **+ Voice**; o Suno confirma
  Voices no modelo v5.5.
- **Limite honesto:** marcações como `[Verse - Laurinha, girl child vocal]` são dicas; o Suno não garante duas vozes
  distintas e constantes na mesma faixa. Confirmado na 1ª música (16/11/2026): as duas versões cantaram os versos da
  Laurinha e do Luisinho com a mesma voz (~350 Hz). Toda versão é conferida de ouvido e medida.
- **Pronúncia em português do Brasil:** escrever como se canta; evitar palavras estrangeiras; se o Suno errar uma
  palavra, reescrever a grafia (sílabas com hífen, acento) e gerar de novo. A medição (seção 8) aponta as palavras erradas.
- **Nomes do canal (grafia SÓ para o Suno; na tela continua "Laurinha e Luisinho"):** escrever **"Lau-ri-nha"** (junto
  ele canta "Larinha") e **"Luizinho"** com z, junto (separado "Lu-i-si-nho" ele canta "Luissinho"). Sempre dentro de
  uma frase em português, com "native Brazilian Portuguese accent" no Style e outros sotaques no Exclude.

## 4. Escolha do ritmo

O ritmo nasce do **tema, da emoção e da brincadeira**, não de uma lista fixa. Detalhes de cada um em [estilos.json](estilos.json).

| Tema ou emoção | Ritmos preferidos |
|---|---|
| Carnaval, festa, euforia | frevo, marchinha, axé |
| Roça, São João, bichos do campo | forró piseiro, forró pé de serra, baião, xote |
| Dança e comandos ("parou!", "abaixa!") | funk infantil, axé, pagodão, piseiro |
| Aventura, energia, desafio | rock infantil |
| Roda, amizade, carinho | ciranda, samba infantil |
| Chuva, natureza, calma alegre | reggae infantil, xote |
| Rotina (banho, escovar, escola) | pop infantil, marchinha, forró |
| Desfile, contagem, grande festa | samba-enredo, batucada |
| Animal | o ritmo do jeito do bicho: quem pula → frevo ou funk; lento e pesado → reggae ou xote; quem voa → frevo ou ciranda; quem rebola ou rasteja → axé ou forró |

**Peso da batida (decisão do canal): batida sempre marcante, com o peso de cada ritmo.**
- `forte` (festa: frevo, axé, pagodão, piseiro, rock, funk, samba-enredo, batucada, marchinha): bateria e percussão
  fortes, **empatadas com a voz** (nunca abafando a voz — medição da referência ~36% × ~37%), virada antes de cada
  refrão, intervalos só de batucada.
- `media` (baião, pé de serra, pop, samba infantil): groove forte e bem marcado, percussão presente.
- `marcada` (xote, ciranda, reggae): groove marcado e dançante, **sem** bateria pesada.

A batida é descrita com os instrumentos do próprio ritmo (surdo e caixa no frevo, zabumba no forró, tamborzão no funk,
surdo de marcação no samba), nunca com um texto único igual para todos.

Sempre que o tema permitir, propor **2 ou 3 alternativas de ritmo** e gerar as melhores no Suno.

## 5. Tipos de música

| Tipo | Regras |
|---|---|
| **Animal** | o bicho é personagem (não aula de biologia); som e movimento característicos viram refrão para imitar; uma curiosidade divertida |
| **Rotina / dia a dia** | situação reconhecível (acordar, banho, lanche, escola, dormir); bom hábito mostrado como brincadeira, **nunca como bronca** |
| **Dança / brincadeira** | comandos curtos que a criança imita; paradas e retomadas; espaços instrumentais para a coreografia |
| **Festa / data** | clima de festa desde o primeiro segundo; refrão de multidão; preparar com antecedência no calendário |
| **Educativa** | um conceito por música (cores, números, formas); o conceito vira jogo de pergunta e resposta |
| **Historinha** | começo, problema, solução em 3 partes curtas; refrão comenta a história |

Séries são bem-vindas: um tema que funcionou pode voltar com variações (ex.: "Laurinha e…" em várias aventuras).

## 6. A letra

**Sempre:**
1. Vocabulário simples e **versos curtos: 3 a 5 palavras** (máximo 7), cantados em 1–2 s.
2. Rimas naturais; onomatopeias e palavras sonoras.
3. **Refrão forte e grudento:** 2 a 4 linhas, com repetição interna, sílabas divertidas e um comando de movimento.
4. **O título é o gancho do refrão:** frase de até 3 palavras, sonora, repetida ~8 a 12 vezes na música.
   Poucas ideias bem repetidas: ~20–25 linhas diferentes por música é o suficiente.
5. **O tema aparece nos primeiros 2 versos.**
6. Momento do **dia a dia da criança** em toda música.
7. Uma **curiosidade ou aprendizado**, dito de forma divertida.
8. Pelo menos um bordão e o "zum" (seção 2).
9. Movimentos que a criança pode imitar.
10. **Convite no final** (decisão de 17/11/2026): antes do tchau, Laurinha e Luisinho convidam para o **joinha** e para
    **se inscrever no canal**, sempre chamando o **papai e a mamãe** (canal para crianças: quem se inscreve é o adulto).
    3–4 versos curtos, com o tema da música (ex.: "Gostou do passeio? (Gostei!) / Dá um joinha! (Joinha!) / Chama o papai
    e a mamãe / Pra se inscrever no canal! (Zum, zum!)"). A checagem da letra acusa erro se faltar.

### Diretrizes da auditoria (17/11/2026 — `docs/auditoria/AUDITORIA_MUSICAS_11-39.md`)
O que mais prende a criança nas nossas melhores letras (Dino, Pipoca, Tum-Tum, Sapo): o refrão é **um som + um gesto +
uma graça**, sem explicação. Regras para toda música nova (a checagem avisa as marcadas com ✓):
1. Diversão primeiro: "Sabia que…" no máximo em 1 de cada 3 músicas ✓; o fato entra como jogo, piada ou desafio.
2. Refrão = 4 linhas cantadas 2 vezes, até 5 linhas diferentes ✓, com um som e um gesto.
3. Até ~25 linhas diferentes na música ✓ (referência: mediana ~23). Repetir é virtude.
4. Gancho = título = 2–3 palavras, 8–12 vezes ✓, entrando até ~30 s contando a vinheta.
5. Rodízio de estrutura (R, D, C, B, F, E): nunca a mesma em 3 músicas seguidas ✓.
6. A abertura promete a música (o gancho ou o som principal), não um "(X! Zum, zum!)" genérico ✓.
7. Um momento de surpresa por música: o Luisinho erra e o coro corrige, estátua, tempo dobrado, refrão que muda o final,
   cochicho que vira grito.
8. Pontes em rodízio: comandos, estátua, rápido/devagar, baixinho/alto, imitação de bicho, contagem, pergunta e resposta.
9. Refrão sem moral: boas maneiras e emoções entram como ação ou consequência.
10. Um formato educativo de cada tipo só uma vez (contagem, quiz de cores/formas, lista de profissões).
11. "(Hein?)" e "(Ê!)" no máximo 2–3 vezes por música; diminutivo só onde soa natural.
12. Ritmo pelo tema e pelo movimento, sem repetir em sequência; eletrônica, disco e sertanejo infantil também valem.
13. Clássica: testar a letra no Suno antes de produzir.
14. Pergunta final: a criança vai cantar o refrão sozinha amanhã?

**Nunca:**
- citar o ritmo na letra ("é o rock da…", "é o axé…"): o ritmo vai só no Style;
- letra longa, verso difícil de cantar, rima forçada, repetição sem propósito;
- introdução demorada;
- explicação com cara de aula ou de bronca;
- letra genérica que poderia ser de qualquer canal (precisa ter Laurinha, Luisinho, o voo, o "zum" ou o mundo pequenino);
- conteúdo adulto no funk ou em qualquer ritmo: sem gírias de baile, sem passos sensuais, sem violência.

## 7. Estruturas

Duração-alvo **2:20–2:50**. Intro de até 4 s; a voz entra até 5 s; o refrão aparece até ~35 s.
Intervalos de dança de 4–5 s (ou ~10 s com um bordão no meio), puxados por um bordão ou "Vai!".

| Código | Estrutura | Quando usar |
|---|---|---|
| **R** | bloco que volta: intro → [verso + refrão + intervalo] × 2 ou 3, quase igual, com uma variação pequena na última vez | a forma mais comum no mercado (9 de 13 medidas); dança, bichos, comida |
| **A** | clássica: intro → verso → refrão → intervalo → verso → refrão → ponte → intervalo → refrão → final | quando há história ou curiosidade para contar |
| **B** | pergunta e resposta do começo ao fim (Laurinha pergunta, o coro responde) | educativas, cores, sons de bichos |
| **C** | cumulativa: cada verso soma um item e repete os anteriores | listas, festa que vai crescendo, historinha divertida |
| **D** | brincadeira com paradas: a música para e todo mundo congela; volta mais forte | dança e brincadeira (estátua, abaixa e levanta) |
| **E** | historinha em 3 partes, o refrão comenta o que aconteceu | aventuras, problema e solução |
| **F** | contagem ou lista que sobe e desce | números, rotina passo a passo |

As estruturas são referência, não obrigação: variar de uma música para a outra para não ficar previsível.

### Marcações do Suno (em inglês; a letra cantada em português)
`[Intro - …]`, `[Verse - Laurinha, girl child vocal]`, `[Chorus - kids choir]`, `[Bridge - …]`, `[Shout] Bora, turminha!`,
`[Drum Fill]` (antes do refrão nos ritmos de peso forte), `[Drum Break - 4 seconds, …]` ou `[Instrumental Break - …]`
(nos ritmos de peso marcado), `[Outro]`, `[End]`. Respostas do coro entre parênteses: `(Cheguei!)`.

## 8. Avaliação antes de aprovar

Cada música passa por três tipos de verificação. **Nunca escolher automaticamente a primeira versão do Suno:**
gerar 2 a 4, medir, ouvir e decidir.

| # | Pergunta | Como verificar |
|---|---|---|
| 1 | O começo chama atenção? | medido: intro ≤ 4 s e voz até 5 s · ouvido |
| 2 | O tema fica claro rápido? | letra: palavra-tema no título, nos 2 primeiros versos e no refrão |
| 3 | O refrão é fácil de memorizar? | letra: 2–4 linhas curtas, repetição interna · medido: entra até ~35 s |
| 4 | A letra é adequada à idade? | letra: lista de palavras e temas proibidos · leitura humana |
| 5 | A melodia combina com a letra? | ouvido |
| 6 | O ritmo é dançante? | medido: andamento dentro da faixa do ritmo, intervalos de dança presentes · ouvido |
| 7 | A pronúncia está correta? | medido: transcrição da voz isolada comparada à letra (taxa de acerto e palavras erradas) · ouvido |
| 8 | A música tem identidade própria? | letra: bordão, "zum", Laurinha/Luisinho, mundo pequenino · ouvido |
| 9 | Há trecho cansativo ou repetitivo? | letra: mesma linha repetida demais · medido: trecho longo sem mudança · ouvido |
| 10 | Há boas oportunidades para animação? | letra: comandos de movimento, ações visuais, intervalos de dança; cenas sugeridas na ficha |

## 9. Fluxo de produção

| Passo | O quê | Comando |
|---|---|---|
| 1 | **Tema** → tipo (seção 5), 2–3 ritmos (seção 4), estrutura (seção 7) | — (no chat) |
| 2 | **Ficha + modelo de letra** | `toonstudio musica nova <nome> --titulo "…" --ritmo frevo --tipo animal --estrutura R` |
| 3 | **Letra** escrita no chat, com os atalhos `[Virada]`, `[Intervalo 10s]`, `[Bordão laurinha]` | `toonstudio musica checar <música>` |
| 4 | **Prompt do Suno** → `<pasta>/suno.txt` (com alternativas de ritmo da ficha) | `toonstudio musica prompt <música>` |
| 5 | **Suno:** 2–4 versões com a Persona oficial → baixar para `<pasta>/versoes/` | — (manual) |
| 6 | **Medir** as versões (andamento, tom, começo, gancho, intervalos, final, letra reconhecida) | `toonstudio musica medir <música>` |
| 7 | **Ouvir e escolher** (decisão humana; nunca a primeira automaticamente) | `toonstudio musica escolher <música> <versão>` |
| 8 | **Clipe:** importar, analisar, cenas a partir da ficha, com a [BIBLIA_VISUAL.md](../BIBLIA_VISUAL.md) | `toonstudio song import` / `song analyze` |

**Proibido cortar música (usuário, 20/11/2026: "quebra o ritmo").** O clipe usa o take do Suno inteiro, no tamanho
original — sem aparar o fim, sem tirar trecho, sem emendar. Take longo, com aviso cantado ou sobra: corrigir a letra /
`suno.txt` e gerar de novo no Suno. `song import` recusa arquivos editados/cortados.

`<música>` aceita o nome da pasta, o número (`03`) ou parte do nome (`lagoa`). A estimativa de duração da checagem é
grosseira; a duração real vem da medição.

## 10. Peças fixas do canal

Independentes da música do episódio; repetidas em todo vídeo:
- **Vinheta de abertura** (até 5 s): logotipo sonoro do estúdio — `library/audio/marca/vinheta.wav`
  (alternativas cantadas em `vinheta/vinheta.txt`).
- **Chamada final** (inscrever e curtir; sem sininho nem comentários em conteúdo para crianças):
  `chamada/chamada.txt` → `library/audio/marca/chamada.wav`.

## 11. Direitos

- Letras, melodias e títulos **originais**; referência de mercado só para características gerais.
- **Cantigas tradicionais: suspensas em 18/11/2026** — o Suno bloqueia as letras (ver [CLASSICAS.md](CLASSICAS.md)); todas viraram autorais.
  Regras que valiam quando eram usadas (17/11/2026): cantigas de domínio público intercaladas aos poucos com as
  originais. Catálogo e situação de cada uma em [CLASSICAS.md](CLASSICAS.md). Regras:
  - só cantiga **tradicional de autor desconhecido** (folclore); música com autor conhecido e ainda protegida, nunca
    (ex.: "O Pato", de Vinicius de Moraes e Toquinho);
  - a **letra tradicional fica no refrão**, com o título conhecido (é o que as famílias buscam); os **versos são nossos**,
    com a Laurinha, o Luisinho, o mundo pequenino, a curiosidade e o convite final;
  - **nunca copiar** gravação, arranjo, versos extras ou vídeo de outro canal (Galinha Pintadinha, Bob Zoom etc.);
  - trechos com conteúdo que hoje não serve (violência, castigo, tristeza de amor, estereótipo) ficam fora ou na versão
    moderna; o Suno cria uma melodia nova (a tradicional não é garantida);
  - se o filtro do Suno bloquear a letra tradicional, **não** trocar letras só para escapar do filtro: avisar e decidir;
  - a ficha marca `dominio_publico` com o trecho tradicional usado.
- Para publicar com monetização, gerar no plano pago do Suno e conferir os termos atuais antes.
