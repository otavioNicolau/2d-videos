# Referência: Animadinhos × nossas músicas (análise de 18/11/2026)

Arquivos (fora do git, só consulta): `referencias/animadinhos/{videos,audio,stems,analise}` e `referencias/nossas/...`.
Programa: `scripts/referencias/analisar_referencias.py` (separação Demucs + reconhecedor de sons PANNs/AudioSet + librosa).
Para analisar mais músicas: pôr os vídeos em `referencias/animadinhos/videos`, extrair `audio/<nome>.wav` (60 s a partir de
15 s) e `audio/<nome>_full.wav` e rodar as etapas A e B.

## Resumo (medianas)

| Medida | Animadinhos (18) | Nossas 01–13 (Suno cru) |
|---|---|---|
| Peso das partes: voz / bateria / baixo / outros | **41 / 38 / 11 / 9 %** | **58 / 28 / 7 / 7 %** (voz alta demais, batida fraca) |
| Teclado, piano, órgão | 8 de 18 | 0 de 13 |
| Eletrônico (sintetizador, sampler, drum machine) | 6 de 18 | 0 de 13 |
| Efeitos de desenho (boing, sininho) | 4 de 18 | 0 de 13 |
| Violão/guitarra | 4 de 18 | 1 de 13 |
| Metais | 2 de 18 | 1 de 13 |
| Bateria acústica de banda | 4 de 18 | 9 de 13 |
| Percussão (chocalho, batucada) | 1 de 18 | 8 de 13 |
| Sanfona | 0 de 18 | 0 de 13 |
| Andamento | 94–199, **7 de 18 entre 94 e 117** (latino/reggaeton) | 85–161, quase todas 132–161 |
| Duração | mediana 2:47 | ~2:20 |
| Som: sub / presença / agudo / brilho | 15 / 5,9 / 0,7 / 0,3 % | 5,5 / 10,3 / 2,9 / 2,2 % (estridente) |

## Música por música (Animadinhos)

| Música | BPM | O que mais aparece | Estilo provável |
|---|---|---|---|
| Celular do Vovô | 117 | sintetizador, teclado, piano | latino/afro de teclado (suingueira) |
| Dança do Calango | 172 | teclado, sintetizador, piano | piseiro de teclado |
| Motoquinha | 94 | teclado, piano; "salsa" | reggaeton/latino |
| Dança do Esqueleto | 103 | sintetizador, drum machine, teclado | latino eletrônico |
| Patinho Quá-Quá | 97 | metais | latino com metais |
| Boi da Cara Preta | 110 | metais, sintetizador | swing com metais |
| ABC | 136 | drum machine, sampler, sintetizador | pop eletrônico |
| Nanda do Cabelão | 129 | drum machine, teclado, sintetizador | pop eletrônico |
| Pega-Pega | 129 | drum machine, sampler | pop eletrônico |
| Sapo Sapeca | 136 | sininho, boing, batida pesada | funk/eletrônico de brincadeira |
| Larguei a Chupeta | 103 | boing (forte), teclado, piano | pop de desenho |
| O Boi e a Vaca | 132 | teclado, piano, órgão | forró/brega de teclado |
| Contando de 1 a 10 | 152 | teclado, piano, órgão | marchinha de teclado |
| Teréu Théo Théo | 136 | bateria, teclado, piano | pop/axé |
| Boi Colorido | 140 | violão, bateria | sertanejo/boi |
| Morto-Vivo | 126 | violão, piano, bateria | pop com violão |
| Som dos Animais | ~100 | violão, bateria, teclado | sertanejo/country |
| Geladin | 96 | bateria acústica | pop-rock |

## Conclusões para o canal
1. Arranjo **enxuto**: batida forte + voz clara + um teclado/synth (ou violão). Nada de "banda completa".
2. Instrumento-base: **teclado** (piano, piano elétrico, órgão) ou **eletrônico** (synth, drum machine), com **efeitos de desenho**.
3. Voz e batida **empatadas** (41 × 38 %); as nossas saem com a voz muito na frente (58 × 28 %).
4. Falta o grupo **lento e dançante (94–117 BPM, latino/reggaeton)**.
5. Correção: o "contratempo" medido em 2 músicas não se confirmou nas 18 (chimbal e palmas em todas as colcheias).
