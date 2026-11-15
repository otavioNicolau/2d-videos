# Limitações conhecidas (estado em 2026-11-15, após o MVP)

Escrito para quem vai decidir os próximos passos. Nada aqui está escondido no código.

## Qualidade artística
- **Teto do desenho procedural** (ADR-0002): o resultado é cartoon de TV limpo (contorno com espessura variável, squash &
  stretch, takes, pancada com achatamento). Não é o traço à mão dos desenhos dos anos 1940–50: a pose é construída por
  partes paramétricas, então certas silhuetas (mãos com dedos articulados, perspectiva forte, rotações de corpo 3D,
  "smears" desenhados quadro a quadro) não saem. A F2 (folhas de modelo) é o lugar para o usuário julgar.
- **Corrida do Caramelo**: melhorou com mais inclinação e passada, mas as pernas curtas limitam a leitura; um ciclo de
  corrida "em roda" (pernas borradas) seria o próximo passo.
- **Vistas**: frente, 3/4, perfil e costas existem para os dois; poses de costas foram pouco usadas e menos revisadas.
- **Cenário**: pintura por código (sem contorno, com textura de papel). As árvores do plano médio se repetem; um artista
  no Krita (o KRA com as camadas está em `library/backgrounds/floresta_clareira/`) melhoraria muito.
- **Trilha sonora**: sintetizada (marimba + baixo), simples. Para publicar, recomenda-se música composta ou licenciada.

## Áudio
- Vozes: Higgs TTS 3 é aleatório; o QA por transcrição escolhe a tomada, mas **ninguém ouviu** as vozes nesta sessão
  (o assistente não ouve áudio). A conferência humana das vozes é obrigatória antes de aprovar.
- Onomatopeias (risadas, "rê-rê-rê") o TTS não pronuncia: foram reescritas com palavras; a risada fica na atuação.
- Lip sync em português usa o reconhecedor fonético do Rhubarb (aproximado). Editar: `build/audio/lines/<hash>.visemes.json`.

## Integração
- **OpenToonz**: o `Renderer` do ToonzScript trava pela linha de comando → render só pelo tcomposer, uma cena por coluna
  (ADR-0009). Retime manual na cena de edição é respeitado; **redesenho manual de um quadro** no OpenToonz ainda não volta
  para o pipeline sem ser sobrescrito no próximo build.
- **Krita**: sem API Python headless no Windows (kritarunner não importa módulos) → só conversões por linha de comando,
  15–18 s por chamada.
- **Godot sem GPU no WSL**: composição na CPU (llvmpipe), ~1,2 s por quadro 1080p → ~25 min para o episódio inteiro.
  Plano B pronto: rodar o mesmo projeto no Godot do Windows (GPU).

## Escopo da especificação ainda não entregue
- **F7 — IA de produção** (ideia → história → roteiro → `episode.json`): o contrato (schema + validador + catálogo da
  biblioteca) existe e foi exercitado; o episódio do MVP foi escrito no chat. Falta o módulo que chama a API do Claude
  com o schema e repara com os erros do validador (o padrão do `~/videos/vidgen/scriptgen.py` serve de base).
- **F8 — Interface gráfica** (15 telas): adiada (ADR-0011). Hoje: CLI + relatórios + storyboard com aprovação por plano.
- **Biblioteca de cenários**: só a floresta (pedida no MVP). Casas, cozinhas, praias etc. não existem.
- Animações da biblioteca sem uso no MVP (`slip`, `bounce`, `sit`, `stand`, `point`, `look_around`) foram testadas só por
  renderização unitária, não revisadas em cena.
