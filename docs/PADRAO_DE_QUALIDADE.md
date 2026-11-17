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
- [ ] Número de quadros de cada plano = duração × 30; vídeo e áudio com a mesma duração e o TAMANHO certo (`ffprobe`: 1920×1080 ou 1080×1920 no Short)
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
| 16/11 | Corte da vinheta pegou o fim do "Luisinho" anterior | corte pela grade de batidas, não pela voz | corte dentro das pausas de respiração da voz | cortes de fala/canto sempre nas pausas da voz (nunca só pela batida) |
| 16/11 | 1º render do Short saiu deitado e esticado | o Godot grava no tamanho de tela fixo do projeto (1920×1080) | `override.cfg` com o tamanho do vídeo durante a gravação | conferir `ffprobe` (largura × altura) de todo vídeo antes de entregar |
| 16/11 | Storyboard do Short ep02: turma de 4 cortada nas bordas, Formiguinha andando para cima da Laurinha, câmera parada enquanto a Laurinha voava | verticalização só enfileirava a 320 (cabem 2 em 1080) e não levava o destino de quem anda nem a câmera junto | 3+ personagens = foto de grupo (dupla na frente, convidados atrás e acima), parado no fundo sai, destino de andar/voar acompanha, câmera segue quem se move, panorâmica com objetos | conferir o storyboard vertical plano a plano antes do render (borda, rosto coberto, quem se move) |
| 16/11 | Sorriso Brilhante: v1 com base em tom menor; v2 cantou "Launinha" | rock pedia "distorted electric guitars" (puxa riff sombrio); a regra "Lau-ri-nha" da bíblia não estava no gerador | rock com guitarra pop-punk em tom maior; "minor key" e "fade out" no Exclude de todo o canal; o gerador escreve "Lau-ri-nha" no que é cantado | medir o tom da BASE (sem voz) quando o rock/guitarra der "menor"; regra da bíblia que não está no código não vale |
| 17/11 | Miniaturas só amarelas, sem nenhuma imagem da música (usuário comparou com canais grandes) | miniatura fixa: raios amarelos + dupla de braços para cima, igual em todo vídeo | raios em 6 cores fortes, personagem-destaque em close com o objeto da música na mão, objetos-tema grandes, título branco/amarelo com contorno escuro no canto superior direito, canto inferior direito livre (duração) | cada ficha publicada tem `youtube.miniatura_cena` (teste obriga); conferir a miniatura junto com as dos outros vídeos antes de entregar |
| 17/11 | Fundo igual em todas as miniaturas (mesmas cores e raios) | uma paleta e um formato fixos no código | paleta e formato por música na ficha (raios, faixas, círculo, anéis) e lado do destaque alternando | teste impede repetir cores ou combinação de fundo |
| 17/11 | Olho da Laurinha/Luisinho "errado" com o rosto meio virado (olho de trás espremido na borda, cara de vesga) e de perfil (olho e boca no contorno) | olhos e boca seguiam a esfera da cabeça à risca | olho quase não deforma, para num limite seguro dentro da cabeça, o de trás some antes de espremer (o da frente nunca); boca com o mesmo limite | teste varre giros de −1 a 1; ao mexer na cabeça, conferir a prancha de giros (0, ±0,3, ±0,45, ±1) |
| 17/11 | Rosto quase de frente com um olho só; piscada que some ou fica pela metade (cara de sono) | correção anterior escondia o olho de trás a partir do giro 0,37; piscada de 2 quadros com o desenho exposto em 2s, lid 0,92 (fresta branca) e intervalo fixo | rosto inteiro anda para o lado do giro, dois olhos até o perfil (0,7); piscada meio → fechado → fechado → abrindo em 1s, olho fechado em curvinha, intervalos sorteados 2,3–4,6 s com piscada dupla às vezes, ritmo próprio de cada personagem | teste dos dois olhos e da piscada; prancha de giros + piscada ao mexer no rosto |
| 17/11 | Sessão fechada no meio do render deixou .json vazios (qa, drawings, sing) e o build da 08 travou; árvore de Natal com topo cortado no vídeo (não aparece no storyboard) | gravação interrompida; nível desenhado em quadro fixo (LEVEL_CANVAS 900 acima do chão) | build apaga .json vazios e refaz a cena; árvore e Papai Noel escalados; teste de todo objeto caber no quadro | conferir os quadros do vídeo final de toda cena com objeto alto |
