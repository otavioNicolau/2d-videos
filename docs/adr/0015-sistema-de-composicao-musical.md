# ADR-0015 — Sistema de composição musical (Suno) do canal Laurinha e Luisinho

- **Status:** F1–F4 feitas · F5 (ligação com a animação) e F6 (piloto) pendentes · 2026-11-16

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
- **F3** `toonstudio/audio/composer.py` + `toonstudio musica nova|checar|prompt`: atalhos de letra traduzidos pelo peso do
  ritmo, checagem pela bíblia, `suno.txt` gerado (um teste garante que não é editado à mão).
- **F4** `toonstudio musica medir|escolher`: andamento (corrigindo metade/dobro pelo andamento pedido), tom, voz, gancho,
  intervalos, final, % da letra reconhecida pela transcrição da voz isolada → `avaliacao.json`; a escolha é humana.
- Pendentes: F5 alinhamento da letra conhecida em `song analyze` e rascunho de cenas; F6 piloto.

## Consequências
O texto de copiar e colar é gerado (`<pasta>/suno.txt`, por `toonstudio musica prompt`); a vinheta e a chamada ficam em `musicas/vinheta/` e `musicas/chamada/`. Áudio das versões fica fora do git.
