# ADR-0017 — Estúdio multicanal

- **Data:** 20/11/2026
- **Estado:** aceita (pedido do usuário: "vamos ajustar o projeto para suportar mais de um canal"; canal 2 iniciado no mesmo dia)

## Contexto
O estúdio nasceu para um canal (Laurinha e Luisinho): pasta de músicas, bíblias, marca, logo do vídeo, vinheta, textos do
YouTube e pasta de entrega eram fixos no código. O usuário criou o canal **Fofolucos** (monstrinhos fofinhos e
assustadores, 5 a 8 anos, chapado sem contorno) e quer manter os dois na mesma esteira.

## Decisão
- **Perfil por canal** em `canais/<id>/canal.json` (nome, músicas, marca, logo, vinheta/chamada, entrega no Windows,
  textos/hashtags/playlists do YouTube, protagonistas, assinatura da letra, modelo de letra). Código: `toonstudio/core/canal.py`.
- **Canal da execução**: `--canal <id>` na CLI → senão o do projeto (`projects/<canal>/<projeto>`) → senão `laurinha`.
- **Mesma estrutura para todos**: `canais/<id>/{BIBLIA_VISUAL.md, canal.json, musicas/}`, `library/brand/<id>/`,
  `projects/<id>/epNN-…`; protótipos em `projects/_laboratorio/`. A Laurinha foi movida para esse padrão (sem mudar nada no
  resultado: roteiros regerados idênticos, 61 testes).
- **Estilo próprio por canal**: personagens (`flat_muri` × `flat_monstro`), cenários (`interior/plano` × `monstrinho`),
  estilos do Suno (E13 × F1) e voz. Nunca misturar estilos/cenários entre canais.
- **Por canal**: limpeza dos rascunhos de render (3 últimas músicas), históricos dos placares, playlists.

## Consequências
- Nome de projeto passa a incluir o canal (`laurinha/ep28-…`); o `episode.json` guarda `projeto`.
- Vídeos (`*.mp4/*.mov/*.wav` de `projects/**/output`) deixam de ser versionados (já ficam no Windows).
- Scripts de placar usam `TOONSTUDIO_CANAL` (padrão laurinha).
