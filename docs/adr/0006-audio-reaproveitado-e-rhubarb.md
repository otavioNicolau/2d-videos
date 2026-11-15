# ADR-0006 — Áudio reaproveitado do `~/videos` e visemas pelo Rhubarb fonético

- **Status:** aceita · 2026-11-15 · escolha do usuário (reuso)

## Decisão
- Os módulos de TTS (Higgs, Qwen, Kokoro), alinhamento (faster-whisper) e mixagem do `~/videos` são **copiados e adaptados** para `toonstudio/audio`; o `~/videos` não é alterado. Os venvs e modelos já baixados são reaproveitados por caminho em `config.yaml`.
- Visemas: Rhubarb Lip Sync 1.14.0 com `-r phonetic` e o texto da fala (`-d`), saída JSON com as bocas A–H e X. A edição manual dos visemas permanece no plano.

## Consequências
Sem download de modelos novos; o português usa o reconhecedor fonético, menos preciso que o de inglês.
