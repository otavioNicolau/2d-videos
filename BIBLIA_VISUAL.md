# BÍBLIA VISUAL — Laurinha e Luisinho

> **Documento-base obrigatório.** Todo personagem, animal, objeto e cenário do projeto segue estas regras.
> Mudanças só com autorização do responsável pelo canal, registradas no histórico no fim do arquivo.

**Referência de linguagem visual:** desenho animado infantil britânico de TV em vetor chapado (episódio
"Encontra um túnel secreto / Esconde-esconde", compilação de 2 h analisada em 2026-11-15: 1.841 quadros
amostrados a cada 4 s, sequências quadro a quadro e cores medidas em 1080p).

**Uso da referência:** só para entender a *linguagem* (traço, formas, cor, acabamento, ritmo). **Nada** de
personagens, nomes, porcos, famílias, cenários reconhecíveis, logotipos ou trilha da série de referência.
Assinaturas visuais exclusivas dela também ficam de fora (ver §9).

---

## 1. Diagnóstico da referência

| Aspecto | O que a referência faz |
|---|---|
| Técnica | Ilustração **vetorial 2D plana**, recortes (cut-out) animados em 2D. Nada de 3D. |
| Contorno | Linha **na mesma família de cor da peça**, alguns tons mais escura e mais saturada (pele rosa `#FEAEDE` → linha `#EB8BC4`; vestido laranja `#FE8E5D` → linha `#EC6F37`). Linha preta só em peças escuras ou em detalhes (pupila, sobrancelha, cílios). |
| Espessura | **Uniforme** dentro de cada objeto, pontas e junções **arredondadas**. Proporcional ao tamanho do elemento: ≈ 1–1,2 % da altura do personagem (≈ 12 px num close de 1080p, ≈ 4–5 px em plano geral). Leve irregularidade "de caneta", sem variação grosso/fino de pincel. |
| Preenchimento | **Cor chapada.** Sem gradiente, sem sombra, sem brilho, sem textura. A única "profundidade" é cor chapada um pouco mais escura em manchas internas (folhas) e sombras ovais chapadas no chão. |
| Formas | Ovais, gotas, retângulos de cantos muito arredondados. Silhuetas simplíssimas. Detalhes internos como **traços soltos** (rabiscos de folha, riscos de grama "‖", pontinhos em pedra). |
| Rostos | Bochecha = círculo chapado mais saturado sem contorno. Olho = elipse branca contornada + pupila preta pequena (ponto). Boca = traço único curvo ou forma aberta escura com língua. Cílios em 3 tracinhos. |
| Membros | **Braços e pernas são linhas** (traço grosso da cor da pele), mãos com 3–4 dedos-traço. Pés = forma oval preta simples. |
| Proporção | Cabeça enorme (≈ 50 % da altura), corpo em "sino"/vestido trapezoidal, pernas curtas. |
| Cenário | Céu **azul chapado** `#87B8F6` sem gradiente; nuvens brancas chapadas **sem contorno**; grama verde chapada `#75C66B` com tracinhos; água azul-escura chapada `#225CA8`; morros = curvas suaves; árvores = tronco de traço + folhas em gota com rabiscos internos; pedras cinza `#7F7D7B` com pontinhos. Planos separados por **sobreposição** e escala, sem desfoque. |
| Interiores | Paredes de cor única saturada (amarelo, roxo, verde, azul), móveis em retângulos arredondados de cor chapada, objetos com contorno colorido. |
| Animação | Animação **limitada**: muitos quadros segurados (10 de 23 quadros idênticos numa sequência medida), poses-chave, deslizamentos de recortes, troca de bocas. Câmera quase sempre **parada**, cortes secos, panorâmica lateral simples. Personagens andam em **perfil**, com passinhos curtos e quique leve. |

---

## 2. Paleta oficial

Saturação alta, luminosidade média-alta, tons "de lápis de cor novo". Cada cor de preenchimento tem a sua cor de
contorno (preenchimento escurecido ≈ 15 % e saturado). Gerar sempre por `linha = escurecer(cor, 0.85)`.

| Uso | Preenchimento | Contorno |
|---|---|---|
| Céu | `#87B8F6` | — (sem contorno) |
| Nuvem | `#FFFFFF` | — |
| Grama | `#75C66B` | `#4E9E46` |
| Grama escura / arbusto | `#149638` | `#0E6E28` |
| Folha de árvore | `#6DAD47` | `#36791F` |
| Tronco / galho | `#534946` (traço) | — |
| Água | `#225CA8` | `#173F78` |
| Pedra | `#7F7D7B` | `#5E5C5A` |
| Madeira | `#7D4724` | `#5A3016` |
| Amarelo (pato, sol) | `#F3E441` | `#C9B820` |
| Laranja | `#FEA53E` | `#D9801E` |
| Vermelho | `#E9545D` | `#C2353E` |
| Rosa chiclete | `#FEAEDE` | `#EB8BC4` |
| Bochecha | `#FE89D0` | — |
| Roxo de parede | `#B865E6` | `#8E43BC` |
| Branco de olho | `#FFFFFF` | cor do contorno da cabeça |
| Pupila / cílios | `#000000` / `#1A1A1A` | — |

Cores próprias dos protagonistas: ver §4.

---

## 3. Regras de traço e acabamento (obrigatórias)

1. **Uma espessura por objeto**, sempre ≈ 1,1 % da altura do personagem principal da cena (escala junto com o elemento).
2. **Contorno = cor da peça escurecida.** Preto só em pupila, cílios, sobrancelha, sapato e objetos que já são escuros.
3. **Preenchimento chapado.** Proibido: gradiente, brilho especular, sombra interna, desfoque, textura, luz cinematográfica.
4. Pontas e cantos **arredondados**. Nenhuma ponta afiada, exceto chapéus/enfeites que pedem.
5. Detalhe interno = **traço solto** da cor do contorno (rabisco de folha, risquinho de grama, costura).
6. Sombra (quando usada) = **oval chapado** escuro e semitransparente sob os pés. Nada mais.
7. Cenário **não** tem desfoque. Profundidade só por sobreposição, escala e cor levemente mais clara no fundo.
8. Câmera: enquadramentos estáveis; cortes secos; panorâmica lateral lenta; zoom só em momentos pontuais.

---

## 4. Protagonistas

**Laurinha — muriçoca.** Simpática, expressiva, divertida. **Luisinho — mosquito.** Simpático, curioso, brincalhão.

Design (proposta da primeira versão, a validar):

| | Laurinha | Luisinho |
|---|---|---|
| Cor da cabeça/corpo | rosa-lilás `#F7A8D8` (contorno `#D47AB6`) | azul-céu `#7CC2F2` (contorno `#4C93C8`) |
| Barriguinha (abdômen) | listras rosa/amarelo | listras azul/amarelo |
| Identidade | laço amarelo com estrela, 3 cílios | topetinho em espiral, sobrancelha marcada |
| Antenas | traço + bolinha rosa | traço + bolinha azul |
| Asas | 2 gotas brancas semitransparentes **chapadas**, contorno azul-claro | idem |
| Tênis | rosa com sola amarela | azul com sola laranja |

Proporções: cabeça ≈ 50 % da altura total; olhos grandes (elipse branca + pupila-ponto); boca de traço único que abre
em forma escura com língua; braços e pernas **em traço**, com mãos de 3 dedos; corpo em gota. Silhueta reconhecível
pelas antenas + asas + abdômen listrado.

Partes separadas para animação: cabeça, olhos, pálpebras, boca (bocas de fala), antenas, asas (2 poses + batida),
corpo, abdômen, braços, pernas, tênis.

---

### Olhos no giro e piscada
- Com o rosto virado até o giro 0,7 aparecem os **dois** olhos, redondinhos, e o rosto inteiro (olhos e boca) anda para o lado do giro. Só no perfil (giro acima de 0,7) fica um olho.
- O olho nunca encosta no contorno da cabeça e nunca vira um risco.
- Piscada: meio fechado → fechado → fechado → abrindo (~0,17 s), cada quadro aparece. O olho fechado é uma curvinha para baixo (a Laurinha com os cílios caídos no canto), sem fresta branca. Intervalos variados (2,3–4,6 s), às vezes piscada dupla, e a Laurinha e o Luisinho nunca piscam juntos.

## 5. Biblioteca de elementos (mesmas regras)

- **Natureza:** árvores (gota, redonda, pinheiro de triângulos arredondados), arbusto de gotas, grama com tracinhos,
  flores (miolo + 5 pétalas ovais), pedras com pontinhos, rio/lago chapado, nuvens sem contorno, sol (círculo + raios
  em gota), lua, morros em curva.
- **Ambientes:** casa (bloco arredondado + telhado + janelas de moldura colorida), quarto, cozinha, sala, jardim,
  parque, escola, floresta, quintal, lagoa — paredes de cor única saturada, móveis em blocos arredondados.
- **Animais:** pato, borboleta, abelha, formiga, joaninha, pássaro, peixe, sapo — todos com o mesmo olho
  (elipse + ponto), bochecha chapada e membros em traço.
- **Objetos:** brinquedos, bola, bicicleta, mesa, cadeira, copo, prato, instrumentos musicais, utensílios.

Organização de arquivos:
```
library/visual/
  personagens/<id>/   partes SVG + PNG (fundo transparente) + folha de modelo
  animais/<id>/
  natureza/<id>/
  ambientes/<id>/      camadas FG/MG/BG
  objetos/<id>/
  paleta.json          (esta tabela, legível por código)
```
SVG quando o elemento for estático; os personagens animados continuam desenhados por código (mesmas regras) e
exportados em PNG/SVG por quadro.

---

## 6. Checklist de consistência (obrigatório antes de entrar na biblioteca)

1. A espessura do contorno é a da regra (≈ 1,1 % da altura do personagem)?
2. As cores estão na paleta e o contorno é a cor da peça escurecida?
3. As formas são simples e arredondadas?
4. Parece pertencer ao mesmo desenho que Laurinha e Luisinho?
5. O nível de detalhe é baixo (detalhes só em traços soltos)?
6. Combina lado a lado com os protagonistas (prancha de comparação)?
7. Está 100 % chapado (sem gradiente, brilho, desfoque, aparência 3D)?

Elemento que falhar em qualquer item é corrigido antes de entrar. A verificação 7 também é automática no código
(teste que rejeita gradientes/desfoques nos elementos do estilo).

---

## 7. Animação

- Poses-chave claras e seguradas; movimento em 2s/3s nas ações calmas, 1s só em ações rápidas.
- Andar em perfil com passinhos e quique pequeno; voo com asas trocando entre 2–3 poses e corpo flutuando devagar.
- Bocas trocadas por visema (fala/canto). Piscadas.
- Sem molas exageradas, sem braço de borracha, sem câmera pulsando.

## 7b. Miniatura (YouTube, 1280×720)
- Fundo: cada vídeo tem CORES e FORMATO próprios (nunca repetir a combinação de outro vídeo). Formatos: `raios` (leque), `faixas` (listras diagonais), `circulo` (fundo cortado na diagonal + círculo grande atrás da personagem), `aneis` (círculos concêntricos). 4 cores fortes, ligadas ao tema, que contrastem com a personagem (Luisinho azul não vai sobre azul).
- Personagem-destaque grande, cortada na cintura, com o objeto da música na mão; o par do outro lado, menor. Alternar o lado entre os vídeos (`lado: direita` espelha a cena e leva o título para a esquerda).
- Objetos-tema da música desenhados grandes (ex.: tubo de pasta e gotinha, janela e sol, joaninha). Nunca miniatura sem imagem da música.
- Título no canto superior oposto ao destaque: 1ª linha branca, 2ª amarela, contorno escuro grosso. Sem logo.
- Canto inferior direito sem nada importante (o YouTube cobre com a duração). Alternar a personagem-destaque entre os vídeos.
- A cena fica na ficha da música (`youtube.miniatura_cena`) e é gerada no `publicar`.

## 8. Processo de criação

1. Análise da referência (feito) → 2. Esta bíblia → 3. Paleta → 4. Regras de traço → 5. Proporções
→ 6. Guia visual → 7. **Proposta de Laurinha e Luisinho** → 8. Amostra de cenário → 9. Comparação com a referência
→ 10. Só após validação: biblioteca completa.

## 9. O que NÃO copiar da referência

- Nenhum personagem, espécie-protagonista (porcos), nome, família, logotipo, vinheta ou música.
- **Assinatura exclusiva do traço de rosto em perfil com os dois olhos do mesmo lado do focinho**: não usar —
  nossos personagens mostram o rosto de frente/3⁄4 com os dois olhos simétricos.
- Cenários icônicos (casa no topo do morro, poças de lama como tema recorrente).

---

## Histórico

- 2026-11-15 — versão 1, a partir da análise da referência.
- 2026-11-15 — primeira proposta: `toonstudio/characters/flat_muri.py` (Laurinha e Luisinho), `toonstudio/backgrounds/plano.py` (plano_parque); folhas de modelo em `library/visual/personagens/` e prancha `library/visual/prancha_laurinha_luisinho.png`. Pendente: validação do usuário.
