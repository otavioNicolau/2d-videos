# ADR-0016 — Clipe ilustrado verso a verso (atuação no contexto da letra)

- **Status:** aceita · 2026-11-16 · pedido do usuário após o 1º clipe: "movimentos repetitivos pulando; a animação tem que
  ser no contexto da música (abrir a janela, dirigir, voar…); algo altamente profissional; criar a marca".

## Análise (referência de mercado, 3 clipes quadro a quadro + o nosso 1º clipe)
- Na referência **cada verso vira uma imagem**: "acordo" → cama; "escovo os dentinhos" → escova; "tomo café" → xícara;
  "vou pra escola" → ônibus. O **objeto é protagonista** (às vezes com carinha: sol, sorvete), o **fundo ilustra a palavra**
  (moranguinhos para "morango") e o personagem fica quase parado com um gesto claro. O movimento vem do **corte a cada verso**.
  **Dança só no refrão**, simples e de frente.
- No nosso 1º clipe: dança em quase todo plano; o passo "balanço" girava o corpo ±0,3 a cada batida (as muriçocas trocavam
  frente/perfil = tremelique) e o "pulinho" subia 95 px; os braços curtos escondiam os gestos atrás da cabeça grande.

## Decisão
- **Roteiro verso a verso** (`musicas/<música>/roteiro.json`) → `clip_draft.roteiro_bloco`: um plano por verso, corte na
  batida, cenário/atores/objetos/câmera por plano; refrão com a mesma coreografia em todas as vezes.
- **Biblioteca da marca** no estilo da BIBLIA_VISUAL: objetos de mão (`holding`) e de cena com canais (janela que abre,
  lençol que se arruma, sol que pisca e acena…), cenários de rotina (quartos, cozinha, casa, escola, céu), fundos de
  desenhos (`padrao_<motivo>_<cor>`), mamãe e vovó muriçoca.
- **Atuação** (`animation/acting.py`): beber (bigodinho), comer (mordida), espreguiçar, empurrar, ajeitar o laço, pentear,
  puxar, guardar, pôr a mochila, pensar, "cheguei!", apontar.
- **Passos das muriçocas** (asinhas, frevo com sombrinha, agacha, lado_frente, festa): de frente, sem giro nem pula-pula.
- **Voo das muriçocas** com ciclo próprio (asas zumbindo, pernas penduradas), liga na decolagem e desliga no pouso.
- **Braços ~30% mais longos** nas muriçocas (56+52 em vez de 42+40) para os gestos passarem da cabeça.

## Consequências
Mais planos (≈1 por verso) e mais cenários pintados → render mais lento que fundos gráficos. Novas músicas pedem um
roteiro escrito no chat e, quando a letra pede um objeto novo, o objeto entra na biblioteca antes do clipe.
