# Padrão de qualidade e melhoria contínua — Laurinha e Luisinho

**Regra do dono do canal (16/11/2026): nada de rascunho. Toda entrega tem qualidade profissional, e cada clipe tem que sair
melhor que o anterior.** Este documento é obrigatório, como a [BIBLIA_VISUAL.md](../BIBLIA_VISUAL.md) e a
[BIBLIA_MUSICAL.md](../musicas/BIBLIA_MUSICAL.md).

## 1. O que nunca se entrega
- Cena genérica que não ilustra o verso (dança "de enchimento" no lugar da ação da letra).
- Movimento repetido, pula-pula, giro de corpo sem motivo, gesto escondido atrás da cabeça.
- Objeto, cenário ou personagem que "quase" parece o que é (a banana tem que parecer banana na hora).
- Vídeo com imagem fora de sincronia com o som, quadro preto, plano faltando ou sobrando.
- Qualquer coisa que eu não tenha olhado quadro a quadro antes.

## 2. Como cada clipe é feito (sem atalho)
1. **Roteiro verso a verso** (`musicas/<música>/roteiro.json`) cobrindo **todas** as partes da música: cada verso vira uma
   imagem com ação, objeto e cenário da letra; dança só no refrão e nos intervalos, com coreografia ligada à letra.
   O sistema recusa montar o clipe se faltar roteiro para alguma parte.
2. **Biblioteca antes do clipe:** se a letra pede um objeto, cenário, ação ou personagem que não existe, ele é desenhado no
   estilo da bíblia e conferido numa prancha **antes** de entrar no clipe.
3. **Storyboard completo** mostrado ao dono do canal antes do render (≈1 h).
4. **Render** e **conferência** (seção 3) antes de entregar.

## 3. Conferência obrigatória antes de mostrar qualquer coisa
- [ ] Cada verso: a imagem mostra o que a letra diz? (ler o storyboard verso a verso)
- [ ] Objetos e personagens reconhecíveis à primeira vista, inclusive em tamanho pequeno
- [ ] Gestos visíveis (fora da cabeça), sem pula-pula, sem tremelique, pés no chão depois de pousar
- [ ] Ninguém pisa na água, atravessa móvel ou some na borda sem querer
- [ ] Legenda = letra exata (sem marcações do Suno, sem parênteses)
- [ ] Número de quadros de cada plano = duração × 30; vídeo e áudio com a mesma duração (`ffprobe`)
- [ ] Quadros extraídos do MP4 final em pelo menos 10 momentos e olhados um a um
- [ ] Testes do projeto passando

## 4. Registro de lições (cada erro vira prevenção)
| Data | Problema percebido | Causa | Correção | Prevenção |
|---|---|---|---|---|
| 16/11 | Danças estranhas e repetitivas "pulando"; tremelique em 0:27 | passos feitos para outros personagens (giro ±0,3 por batida; pulo de 95 px) | passos próprios das muriçocas, de frente | dança só no refrão, ligada à letra (ADR-0016) |
| 16/11 | Animação fora do contexto da música | rascunho automático genérico | roteiro verso a verso + biblioteca de objetos | sistema recusa montar sem roteiro completo |
| 16/11 | Gestos não apareciam | braços curtos para a cabeça grande | braços ~30% mais longos | conferir gestos na tira de ações antes do clipe |
| 16/11 | Porta da casinha de cabeça para baixo | suavização arredondava a base do polígono | arco desenhado explicitamente | formas retas sempre amostradas (sem suavização) |
| 16/11 | Banana estranha (meia-lua / anel) | desenho geométrico simples demais | banana clássica com cabinho; mordida = descascada | todo objeto novo passa por prancha antes do clipe |
| 16/11 | Personagens flutuando depois de pousar | voo usava o ciclo do pássaro antigo | ciclo de voo próprio que pousa de verdade | conferir pouso no storyboard |
| 16/11 | Parênteses do coro na legenda | texto do Suno usado direto | legenda sem marcações | item da conferência |
| 16/11 | Risco de 1 s de dessincronia a partir de 1:41 | tela dividida guardava quadros antigos | pasta limpa + trava de duração na montagem | item da conferência (quadros × duração) |
| 16/11 | Voz da vinheta robotizada (2×) | voz sintetizada no estúdio; depois voz separada da música (Demucs) e recortada | áudio do Suno usado como veio, sem processar | **nunca usar voz separada/recortada para ouvir** — separação só para análise (boca, letra); fala sempre do Suno, inteira |
