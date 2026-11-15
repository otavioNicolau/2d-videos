# ADR-0010 — Vozes dos personagens: Higgs + escolha de tomada por transcrição cega + tom de cartoon

- **Status:** aceita · 2026-11-15 · complementa ADR-0006

## Decisão
- Cada fala: até 5 tomadas do Higgs TTS 3 (sementes diferentes) com marcações de emoção; transcrição cega (faster-whisper small);
  escolhe-se a tomada com maior similaridade e duração plausível. Depois: corte de silêncio, tom/tempo do personagem
  (rubberband; Tevico com formantes deslocados, Caramelo grave), loudnorm.
- Visemas: Rhubarb `-r phonetic` com o texto.
- Falas que o TTS não pronuncia (onomatopeias como "Rê-rê-rê") são reescritas com palavras reais; risada fica na atuação.

## Consequências
Na F5 o QA rejeitou automaticamente uma tomada de 7,3 s (Higgs "embalado") e três tomadas de uma onomatopeia.
O Higgs exige o aviso de licença (Creator Use Grant) na descrição de vídeos publicados.
Correção no venv do ~/videos: a decodificação do faster-whisper via PyAV falha (versão incompatível); o worker lê o WAV com soundfile.
