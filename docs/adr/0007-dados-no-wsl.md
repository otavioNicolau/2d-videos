# ADR-0007 — Todos os dados do estúdio ficam no WSL (`~/2d`)

- **Status:** aceita · 2026-11-15

## Contexto
Krita e OpenToonz rodam no Windows. Foram testados com arquivos no NTFS e dentro do WSL via `\\wsl.localhost\Ubuntu\...`: ambos funcionam; o UNC é um pouco mais lento.

## Decisão
Projetos, biblioteca e arquivos-fonte (KRA, níveis, cenas `.tnz`) ficam em `~/2d`, versionados no git (binários grandes avaliados depois). As ferramentas do Windows recebem caminhos convertidos por `wslpath -w`.

## Consequências
Uma única fonte da verdade, acessível ao Python sem lentidão de `/mnt/c`. Se algum recurso do OpenToonz falhar com UNC (ex.: projetos com aliases `+drawings`), a alternativa é um diretório de trabalho no NTFS sincronizado pelo pipeline.
