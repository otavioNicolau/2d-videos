# F0 — Validação técnica das integrações

Data: 2026-11-15 · Máquina: WSL2 Ubuntu 24.04, RTX 3050 6 GB, 10 GB RAM, 4 núcleos.
Testes reproduzíveis em [`spikes/`](../spikes/); saídas em `.spike/` (não versionado).

## Ferramentas instaladas

| Ferramenta | Versão | Onde | Como foi instalada |
|---|---|---|---|
| Godot | 4.7.2 | Linux `~/.local/opt/godot/4.7.2-stable/` e Windows `C:\Users\DELL\godot\4.7.2` | já existia |
| OpenToonz | 1.8.0 | `C:\Program Files\OpenToonz` (stuff em `C:\OpenToonz stuff`) | winget `DWANGO.OpenToonz` |
| Krita | 5.3.4.1 | `C:\Program Files\Krita (x64)` | winget `KDE.Krita` |
| Rhubarb Lip Sync | 1.14.0 | `tools/rhubarb/` (Linux) | release do GitHub |
| FFmpeg | 6.1.1 | Linux `/usr/bin/ffmpeg` | já existia |

## Resultados

| # | Integração | Resultado | Medida |
|---|---|---|---|
| a | Python gera nível PNG + ToonzScript → `OpenToonz.exe script.toonzscript` cria o `.tnz` | **Funciona** | ~2 s; exit code é 1 mesmo com sucesso → validar pela saída e pelo arquivo |
| b | `tcomposer.exe cena.tnz -o out.png -range 1 24` | **Funciona** | 24 quadros 1920×1080 RGBA em 2,3 s (NTFS) / 2,6 s (UNC); **idênticos pixel a pixel** aos desenhos; exposição em 2s respeitada |
| c | Krita: ORA → KRA e KRA → ORA/PNG via `krita.com --export` | **Funciona** | nomes e posições das camadas preservados; achatado com diferença 0; **15–18 s por chamada** |
| c' | Krita: `kritarunner.com -s modulo` (API Python sem GUI) | **Não funciona** no 5.3.4.1/Windows | o módulo nunca é importado (testado com `PYTHONHOME`/`PYTHONPATH` corretos) |
| d | Godot compondo cenário em camadas + nível do OpenToonz + câmera, Movie Maker → PNG | **Funciona** com Godot **Linux**, renderer Compatibility | llvmpipe (CPU, sem GPU no WSL): 49 quadros 1080p em 4 s (≈ 50% do tempo real), gargalo é a gravação PNG |
| e | Rhubarb `-r phonetic` em fala pt-BR (Kokoro) | **Funciona** | 3,6 s de fala → 26 posições de boca em 1 s; precisão a julgar com bocas desenhadas (F5) |
| f | Arquivos dentro do WSL acessados pelo Windows via `\\wsl.localhost\...` | **Funciona** em OpenToonz, tcomposer e Krita | um pouco mais lento que NTFS, irrelevante para o volume previsto |
| — | FFmpeg: PNG + WAV → MP4 H.264 1080p 24 fps + AAC | **Funciona** | 1,2 s para 2 s de vídeo |

## Problemas encontrados que viram regras

1. **Borda do cenário exposta:** no teste, o céu (parallax 0,15) não cobria o percurso da câmera e a borda apareceu nos últimos quadros. → QA obrigatório: cada camada precisa cobrir `viewport + deslocamento máximo × fator`.
2. **Exit code do OpenToonz não é confiável** → sucesso = marcador impresso pelo script + arquivo criado.
3. **Krita é lento por chamada** → usado só para ativos que mudam pouco (model sheets, cenários), nunca quadro a quadro.

## Limitações confirmadas

- O ToonzScript não desenha traços; o OpenToonz recebe desenhos prontos (PNG) e cuida de timing, edição e render.
- Sem API Python headless no Krita do Windows; integração por arquivos (ORA/KRA) e linha de comando.
- Sem GPU no WSL: composição 2D na CPU. Suficiente para 2D; se uma cena pesar, o Godot do Windows (com GPU) é o plano B, já usado no `~/videos`.
- Rhubarb em português usa o reconhecedor fonético (menos preciso que o inglês); edição manual dos visemas continua no plano.

Decisões resultantes: [ADR-0002](adr/0002-desenho-vetorial-procedural.md) a [ADR-0007](adr/0007-dados-no-wsl.md).
