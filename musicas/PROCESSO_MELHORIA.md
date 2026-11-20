# Processo de melhoria contínua — Laurinha e Luisinho

Objetivo: cada música nova soar mais perto da referência (Animadinhos, 18 músicas medidas — [REFERENCIA_ANIMADINHOS.md](REFERENCIA_ANIMADINHOS.md))
e mais do jeito que o usuário gosta, **medindo** o que mudou em vez de adivinhar.

## O ciclo (toda música nova)

| # | Passo | Quem | Como |
|---|---|---|---|
| 1 | **Gerar** no Suno com o suno.txt da vez | usuário | o suno.txt mostra a versão do estilo (`ESTILO DO CANAL: E5`) |
| 2 | **Escolher** o melhor take e mandar | usuário | — |
| 3 | **Medir** o take contra a referência | Claude | `song import` + `song analyze`, depois `scripts/referencias/placar.py <nº>` |
| 4 | **Dar a nota de ouvido** (1 a 5) e um comentário | usuário | "voz boa, batida ainda de banda" — entra no placar com `--nota` e `--obs` |
| 5 | **Decidir o próximo ajuste**: o item que mais falhou nas últimas músicas e o comentário do usuário | Claude propõe, usuário aprova | o placar já sugere o que mexer em cada item |
| 6 | **Criar a nova versão do estilo** (E6, E7…) com o ajuste, registrada no histórico | Claude | `musicas/estilos.json → canal.historico` (versão, data, mudança, motivo, em quais músicas) |
| 7 | **Produzir o vídeo** normalmente (storyboard → aprovação → render → publicar) | os dois | a montagem já centraliza a voz, equilibra e masteriza |
| 8 | **Depois de publicado**, uma vez por semana: retenção média, % assistido e CTR da miniatura | usuário (YouTube Studio) | entra no histórico; é o juiz final (criança gostou = assistiu até o fim) |

**Regras**
- **Poucas mudanças por versão** (de preferência uma). O Suno varia de um take para outro, então cada versão vale por pelo menos 2 músicas antes de concluir que funcionou ou não.
- Se uma mudança **piorou** o placar ou a nota, ela volta atrás na versão seguinte (o histórico diz qual foi).
- Nada muda nas músicas já gravadas: o suno.txt de cada uma guarda o estilo usado.
- A nota de ouvido do usuário vale mais que o placar: o placar mostra **onde** está a diferença, o ouvido diz **se importa**.

## O placar (10 medidas, alvo = faixa da referência)

| Medida | Referência (mediana) | Alvo |
|---|---|---|
| Voz no som | 41 % | 35–48 % |
| Batida no som | 38 % | 32–46 % |
| Baixo no som | 11 % | 8–16 % |
| Outros instrumentos | 9 % | 4–13 % (pouca informação) |
| Largura da voz (0 = uma voz seca no centro) | 0,007 | até 0,06 |
| Batida de teclado (cada batida igual à outra) | 0,96 | 0,90 ou mais |
| Teclado/synth reconhecido | 0,067 | 0,04 ou mais |
| Bateria de banda reconhecida | 0,018 | até 0,04 |
| Percussão (chocalho/batucada) | 0,012 | até 0,04 |
| Duração do take | 2:47 | 2:20–3:05 |

O que a **montagem** já corrige sozinha (não precisa de take novo): voz no centro, equilíbrio voz/batida/baixo e o som
estridente (masterização). O que **só o Suno** corrige: batida de teclado × batida de banda, instrumentos, percussão, letra.

Comandos:
```
PYTHONPATH=. .venv/bin/python scripts/referencias/placar.py 15 --nota 4 --obs "comentário do usuário"
PYTHONPATH=. .venv/bin/python scripts/referencias/placar.py --historico
```
Histórico: `musicas/MELHORIA.json` (01–13 = linha de base no estilo E1).

## Versões do estilo
Ver `musicas/estilos.json → canal.historico`. Resumo:
- **E1** (01–13): banda completa, metais, viradas, coro e respostas.
- **E2** (14 v1): produção de teclado/eletrônico, efeitos de desenho.
- **E3**: uma voz só, arranjo mínimo.
- **E4** (14 v2): batida de teclado arranjador.
- **E5** (15 em diante): "teclado arranjador" no começo do Style, ritmo como "groove", baixo de teclado forte, voz seca no centro.

## Onde estamos (placar da 14 v2, estilo E4: 5 de 10)
Melhorou muito em relação à linha de base (voz/batida empatadas, bateria de banda quase zero, duração certa).
Falta: baixo (5,6 %), voz larga (0,17), batida ainda variada (0,77), pouco teclado reconhecido, percussão (0,07).
A E5 ataca baixo, voz e batida; a 15 e a 16 dizem se funcionou.

## Trilha de CENA (19/11/2026: "estamos simplificando as cenas, temos que sempre evoluir")
O placar da música mede o som. O placar de cena mede a **imagem**: quantos cortes, quantos cenários, quantas ações
diferentes, câmera, objetos, coadjuvantes e efeitos sonoros. Os alvos vêm das melhores (12 e 13).

| Medida | Alvo |
|---|---|
| planos (cortes) | 45 ou mais (3,5–4,5 s por plano) |
| cenários de verdade (fora o fundo de dança) | 4 ou mais: a história anda de lugar |
| planos em fundo de dança | até 25 % |
| tipos de ação diferentes | 24 ou mais |
| câmera viva (close, zoom, movimento) | 60 % ou mais |
| tipos de objeto/bicho | 6 ou mais |
| objetos animados por plano | 1,2 ou mais |
| coadjuvantes | 1 ou mais |
| mesma arrumação do plano anterior | até 15 % |
| efeitos sonoros por plano (da 19 em diante) | 0,8 ou mais |

**Regra:** depois de escrever o roteiro e ANTES do storyboard, rodar
`PYTHONPATH=. .venv/bin/python scripts/referencias/placar_cena.py <nº>`. Da 19 em diante, se falhar um alvo ou ficar
abaixo da média das 3 anteriores em qualquer medida, o roteiro volta para ser refeito (o script sai com erro).
O resultado vai junto do storyboard para o usuário. Histórico: `musicas/MELHORIA_CENAS.json`
(`--historico` mostra a tabela).

## Trilha de ANIMAÇÃO (19/11/2026: "processo de melhoria da animação — danças, braços, pernas — a cada vídeo")
Mede como a Laurinha e o Luisinho **se mexem**: alcance e velocidade dos braços, alcance das pernas, balanço do corpo,
quantos estilos de dança, se um estilo domina, tempo parado e se o movimento "acentua" a batida. Sem render: o script
recompila a atuação de cada cena e lê a pose quadro a quadro.

**A cada vídeo**
| # | Passo | Quem |
|---|---|---|
| 1 | Depois do render: `PYTHONPATH=. .venv/bin/python scripts/referencias/placar_animacao.py <nº>` | Claude |
| 2 | **Nota de olho** da animação (1 a 5) + comentário ("braço duro", "perna parada") → `--nota --obs` | usuário |
| 3 | Escolher **um** ajuste (o que o usuário apontou ou o item mais longe do alvo) | Claude propõe, usuário aprova |
| 4 | Fazer o ajuste na biblioteca de animação (`toonstudio/animation/`) como nova versão **A1, A2…** | Claude |
| 5 | **Laboratório de dança** ANTES × DEPOIS: `scripts/referencias/laboratorio_danca.py --versao A<n>` → `Canal\Laboratório de dança\` | Claude gera, usuário olha |
| 6 | Aprovado, a versão vale para o próximo vídeo; o placar diz se melhorou | os dois |

Alvos iniciais (a nota de olho manda; ajustar os alvos quando ela discordar):
braços ≥ 110 u de alcance e ≥ 160 u/s · pernas ≥ 40 u · corpo ≥ 30 u · ≥ 6 estilos por vídeo · nenhum estilo > 35 %
do tempo de dança · parado ≤ 8 % · acento na batida ≥ 75 %. Histórico: `musicas/MELHORIA_ANIMACAO.json`.

**Versões da animação**
- **A0** (até a 18): 22 passos em `cycles.CHOREO`. Linha de base medida nas 12–18: pernas quase paradas (5–14 u),
  corpo pouco balanço (14–29 u), braços médios (27–114 u), 5 estilos por vídeo nas 16–18 (11 na 12), a 16 com 76 % de frevo.
- **A1** (19/11, a partir da 19): usuário olhou o laboratório A0 — "balanço, lado: os braços estão estranhos". Os dois
  passos refeitos: braços sempre por fora do corpo (antes um braço virava gancho em cima da barriga/quadril), abertos
  e balançando com o peso; tronco quase de frente (giro ±0,32 → ±0,12); no "lado", passo de pé de verdade e o braço
  do lado esticado apontando longe. Usuário em seguida: "lado da cabeça fica mudando" — o giro do passo (turn+) cruzava o meio e o desenho espelhava
  (laço/rosto pulando de lado a cada batida). Corrigido no motor (`cycles.soma_giro`): o giro de dança nunca passa
  para o outro lado, em TODOS os passos. Laboratório: `Canal\Laboratório de dança\A1 - laurinha.mp4` e `- luisinho.mp4`.
  **Aprovado pelo usuário (19/11).**
- **A2** (19/11, APROVADO pelo usuário no laboratório): pernas e corpo. 14 dos 22 passos não mexiam a perna (a "festa", a
  mais usada, tinha perna E corpo parados). Ginga de base (`cycles._ginga`) nos canais que o passo não define:
  joelhos dobram e o corpo desce NA batida, peso de um pé para o outro a cada 2 batidas, calcanhar do pé livre sobe
  no contratempo. Simulação na 18: pernas 13 → 20, corpo 14 → 17. Laboratório: `A2 (pernas e corpo) - *.mp4`.

## Batida contagiante (19/11/2026: "temos que focar nas batidas do som contagiante que faz a pessoa gostar")
`scripts/referencias/batida.py` faz o raio-x da bateria e do baixo separados: síncope (golpes no contratempo), baixo
fora do tempo forte, bumbo reto em todo tempo, palma no 2 e no 4, pegada, e o desenho da batida em 16 posições.
Referência: síncope 0,69 · baixo sincopado 0,52 · bumbo reto 0,50. Nossas 01–18: 0,56 · 0,59 · 0,67.
A nota de ouvido acompanha a síncope: 14 (0,39) → 3 · 15 (0,52) → 4 · 16 (0,68) → 4 · 17 (0,74) → 4 · 18 (0,72, baixo
0,90) → 4,6. A 19 v1 (rock com "punk-rock drumming, driving kick") saiu reta: 0,41 / 0,39.
O placar da música ganhou os itens **síncope ≥ 0,60** e **baixo sincopado ≥ 0,50**. Estilo **E7** = batida sincopada.
**E8** (19/11): o usuário ouviu a 19 v2 (E7) — "Animadinhos são ritmos e batidas que não mudam muito durante a música;
a nossa está ficando ainda estilo banda". Medido: loop igual ref 0,96 × 19 v1 0,84 × 19 v2 0,75; outros instrumentos
9 % × 20 %. E8 mantém a síncope do E7 e pede UM loop que nunca muda, sem virada entre as partes, mesma batida no verso e
no refrão (Exclude: beat changes, breakdown, build-up, half-time, drum breaks, guitar solo). Vale da 20 em diante.
- **A3** (19/11, APROVADO pelo usuário no laboratório; vale da 20 em diante): nota de olho da 19 = 4; pernas ainda
  paradas (12, meta 40) e "festa" com 46 % da dança. (1) Ginga de base com PASSO de verdade: o pé livre sai para o lado
  e volta, joelho/calcanhar sobem mais (22 → 32), e entra também nos passos de perna fraca (balanço…). (2) Quatro
  passos novos com perna: **chute** (chutinho alternado), **joelho** (joelho alto + mão no joelho), **sapinho**
  (pernas abertas, agacha e pula), **cintura** (mãos na cintura, quadril e ponta do pé). Braços sempre por fora do corpo.
  Laboratório: `A3 (pernas e passos novos) - *.mp4`. Roteiros da 20 em diante: nenhum passo com mais de 1/3 da dança.

**E9 / E10** (19/11): E7 piorou (19 = 3,8) e o usuário ouviu segunda voz e perda das batidas viciantes da 15–17 → E9 =
volta ao E6 + Exclude contra segunda voz. Medido: da 14 à 19 o texto do Style não mexeu em segunda voz (0,06–0,18 × 0,007),
batida igual (0,71–0,80 × 0,96) e teclado reconhecido (0,01–0,03 × 0,067). O usuário quer ajustar NO SUNO (download é
limitado: 1 take por música) → **E10** = E9 + opções Advanced do Suno v6 no topo do suno.txt (Vocal Gender pela voz,
Duration Custom 2:40, Weirdness 20 %, Style Influence 80 %, Audio Influence 60 %, Variety mínima, Personalize Off).

**E13** (20/11): 21–25 no trio E12 tiraram 4,8; a **26 Gelatina (reggae 96) tirou 4,7 — "está sem batida viciante"**. O placar
mostrou a diferença: **bateria de banda 0,046** (21–25: 0,011–0,017, o triplo) e o loop menos repetido (0,738): o reggae
puxou bateria acústica de banda. E13 = E12 com a bateria do trio sendo **o loop ELETRÔNICO do teclado** (drum machine, a
mesma batida a música toda, sem baterista ao vivo) e "live drums / acoustic drums" de volta no Exclude. Um ajuste por vez:
vale da 27 em diante; conferir no placar da 27 se a "bateria de banda" volta para ~0,015 e o loop sobe.
Também 20/11: o bloco AVISOS do suno.txt ficava DEPOIS do [End] — foi copiado junto e o Suno cantou o aviso no fim da 26
(cortado do take). Agora os avisos ficam antes da letra e há a marca "FIM DA LETRA — não copie daqui para baixo".

**Lição 20/11 (27):** antes de passar um `suno.txt` ao usuário, conferir se a LETRA está no formato do trio: 1 ponte só,
nenhum refrão "faster", intro só com teclado/sax/bateria. A 27 foi gerada com a letra antiga (2 pontes + "faster") e saiu
com 3:26; foi cortada no compasso para 2:50. As letras 28–49 foram corrigidas em lote (`scripts/lotes/formato_trio.py`).
