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
