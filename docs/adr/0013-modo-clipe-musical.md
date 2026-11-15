# ADR-0013 — Modo "clipe musical" (canal Luizinho e Turminha) sobre o mesmo pipeline

- **Status:** aceita · 2026-11-15

## Contexto
O usuário quer clipes musicais infantis (gênero "Mundo Bita": vetor chapado, cores saturadas, cada estrofe vira cena) para
o canal **Luizinho e Turminha**. As músicas chegam prontas (mixadas, sem stems), feitas no Suno; o roteiro visual é feito
pelo Claude no chat; o pipeline anima e monta. Referência de gênero apenas: nada de personagens, músicas ou marca do Mundo Bita.

## Decisão
- Mesmo pipeline (Python → OpenToonz → Godot → FFmpeg). Extensões, não um segundo sistema:
  schema 1.1 com bloco `soundtrack` (áudio original intocado, batidas, seções, letra com tempos); ações com duração em batidas;
  boca a partir da voz cantada (separada localmente); perfis de estilo no motor de desenho.
- **Kit de personagens** (`characters/kit.py`): olhos, sobrancelhas, bocas, mãos e tênis compartilhados, para a turma crescer
  sem duplicar código. Personagens antigos continuam como estão até haver motivo para migrar (com teste de imagem igual).
- **Luizinho** é um menino estilizado a partir de uma foto de referência que fica só em `library/characters/luizinho/referencia/`
  (ignorada pelo git, nunca publicada nem enviada a serviços externos).
- Editor: web local servido pelo Python, com prévia em baixa resolução gerada pelo pipeline (Godot segue como compositor).

## Consequências
O episódio "A Torta do Caramelo" (schema 1.0) continua válido. O gargalo de render (Godot na CPU) precisa ser resolvido
antes da produção em lote.
