# ADR-0008 — Motor de animação: canais de pose, ciclos com pé plantado, molas e exposição em 1s/2s

- **Status:** aceita · 2026-11-15

## Decisão
- Pose = dicionário de canais numéricos (interpolados com easing: in/out/inout/back/elastic/step) e categóricos (boca, objeto na mão).
- Cena descreve cada personagem por `start` + `keys` (poses/expressões no tempo) + `actions` da biblioteca (`toonstudio/animation/library.py`).
  Ações têm antecipação, exagero, overshoot e assentamento embutidos (take, crash, fall, slip, jump, grab…).
- Ciclos procedurais (walk/sneak/run/flap) mantêm o pé de apoio parado no mundo (velocidade = passada / meio período) — testado.
- Ação secundária por molas amortecidas integradas no tempo (orelhas, cauda, cabeça) a partir da aceleração do corpo.
- Lip sync: os visemas do Rhubarb sobrepõem a boca durante a fala; piscadas automáticas determinísticas.
- Exposição: 2s por padrão; ações rápidas pedem 1s. A posição no palco segura junto com o desenho (sem patinação em 2s).
- Desenhos idênticos são deduplicados por hash da pose (posição no palco não entra).

## Consequências
Um diretor (humano ou IA) descreve a atuação em JSON de alto nível; o refinamento fino é feito por chaves.
