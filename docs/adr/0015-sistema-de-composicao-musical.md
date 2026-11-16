# ADR-0015 — Sistema de composição musical (Suno) do canal Laurinha e Luisinho

- **Status:** F1 e F2 feitas · F3–F6 aguardando aprovação · 2026-11-16

## Contexto
As 6 primeiras letras eram arquivos de texto com o mesmo Style de bateria pesada e a mesma estrutura, o que tornava as
músicas previsíveis e, em alguns ritmos, contraditórias (bumbo em todo tempo num samba-enredo). Não havia registro de vozes,
avaliação das versões do Suno nem ligação entre a letra conhecida e a análise do áudio.
O Suno não tem API pública (só um programa de parceiros fechado desde jul/2026); APIs não oficiais violam os termos de uso.

## Decisão
- **Fonte única:** `musicas/BIBLIA_MUSICAL.md` (identidade, bordões, ritmo por tema, letra, estruturas R e A–F, avaliação).
- **Dados:** `musicas/estilos.json` (16 ritmos com andamento, bateria própria, peso da batida forte/média/marcada, Exclude),
  `musicas/vozes.json` (vozes oficiais e Personas, preenchidas à mão), `musicas/<nº>_<nome>/ficha.json` + `letra.txt`.
- O Style é **montado por ritmo**: gênero + andamento + peso + bateria e instrumentos do próprio ritmo + voz + canal.
- O Suno continua manual (copiar e colar). As letras continuam escritas pelo Claude no chat; nenhuma IA é chamada pelo código.
- Fases seguintes: F3 gerador do prompt e checagem da letra; F4 medição e comparação das versões; F5 alinhamento da letra
  conhecida em `song analyze` e rascunho de cenas; F6 piloto.

## Consequências
`musicas/letras/` segue válido para copiar e colar até o gerador da F3 substituí-lo. Áudio das versões fica fora do git.
