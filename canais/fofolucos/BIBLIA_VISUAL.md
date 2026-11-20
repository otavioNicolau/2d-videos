# Bíblia visual — FOFOLUCOS

Base obrigatória de todo personagem, objeto e cenário do canal **Fofolucos**: os monstrinhos fofinhos e assustadores
da **Vila Monstrinha**, para crianças de **5 a 8 anos**. Mudanças só com autorização do dono do canal.
Aprovado pelo usuário em 20/11/2026 (turma, cenários, enquadramentos e logo).

## 1. Estilo
- **Chapado SEM contorno**: formas de cor pura; a separação entre partes é feita por tons do mesmo corpo
  (braço de trás mais escuro, barriguinha mais clara). Nada de linha de contorno (é o que separa do canal da Laurinha).
- **Cabeção** (≈ 55 % da altura) e corpinho curto; braços e pernas grossinhos; mão de luva redonda; pé de tênis.
- **Olho de bolinha** escura com dois brilhos brancos, **abaixo do meio do rosto**; boca simples escura com língua.
- **Sobrancelha sempre** (atitude para 5 a 8 anos), em arco suave; brava = inclinada / "V".
- Cores **saturadas**; bochecha rosada.
- **Fofinho e assustador**: presas e dentes pontudos, garrinhas brancas, rabinho com **pompom**, manchas, chifres/antenas.
- **Nunca "diabinho"** (20/11/2026 — muitas famílias rejeitam): nada de rabo com ponta de flecha, nem a combinação
  vermelho + chifres + rabo pontudo + orelha/asa de morcego; nada de tridente, fogo ou cara de "capetinha".
- **Palavras na letra**: "maluquinho" (não "louco"/"maluco"); evitar "chifrão"/"chifrudo" (duplo sentido para adulto).
- Pose de marca: **"RAWR!"** (garras para cima, dentes, sobrancelha brava) — sempre divertida, nunca de dar medo de verdade.
- Inspiração: o jeito geral dos clipes infantis de referência (chapado, cabeção, cores fortes). **Personagens, nome,
  logo e cenas são originais.**

## 2. A turma (sem dupla fixa — cada música escolhe quem aparece)
| id | Nome | Cor | Jeito de monstro |
|---|---|---|---|
| `bilu` | **Bilu** | azul | um olhão com anel amarelo, chifres curvos, presas, pelo espetado |
| `teco` | **Teco** | roxo | três olhinhos (um na testa), anteninhas, dentes em serrinha |
| `gogo` | **Gogo** | verde | olhos na ponta das antenas, bocão de dentes |
| `mimi` | **Mimi** | rosa | peludinha (pelagem em volta da cabeça), chifrinhos brancos, presas |
| `zuzu` | **Zuzu** | laranja | chifre único listrado, olhos com anel verde |
| `nhoque` | **Nhoque** | coral | bocão comilão, orelhas redondas |

Código: `toonstudio/characters/flat_monstro.py` (mesmo esqueleto de poses da Laurinha: danças, ações, expressões e
visemas funcionam igual). Nunca pôr um monstrinho na frente de fundo da mesma cor (Teco × roxo, Bilu × azul…).

## 3. Cenários (próprios, diferentes dos da Laurinha)
`toonstudio/backgrounds/monstrinho.py` — chapados sem contorno, céu com degradê suave, nuvens fofas, árvores de copa redonda.
- De história: `mon_parque`, `mon_vila` (Vila Monstrinha: casinhas com chifrinhos e janelas-olho), `mon_quarto`,
  `mon_palco`, `mon_noite`, `mon_escola`, `mon_cozinha`.
- De refrão/destaque: `mon_raios_<cor>` (espiral que gira na batida), `mon_xadrez_<cor>`, `mon_brilho_<cor>`
  (cores: roxo, azul, verde, laranja, rosa, vermelho).

## 4. Enquadramento (medido na referência, 20/11)
Misturar sempre três tamanhos (a referência varia muito; o nosso canal 1 repetia o mesmo tamanho):
- **CABEÇA** — cabeça e peito enchendo a tela (expressão, piada, "RAWR!"), zoom ≈ 2,3;
- **BUSTO** — corte na cintura (cantar), zoom ≈ 1,75;
- **CORPO TODO** — o monstrinho com ≈ 60 % da altura da tela (dança, ação).
Alvo: ~20 % cabeça, ~45 % busto, ~35 % corpo todo.

## 5. Marca
Logo: `library/brand/fofolucos/logo.png` (letras nas cores da turma, borda de adesivo, os dois "O" são olhos de monstro,
chifres no F e no S, presinha no U) — gerado por `scripts/canais/fofolucos_logo.py`.
Entregas: `C:\Users\DELL\Videos\Fofolucos\NN Título\{Pré-produção, Vídeo longo}` e `Fofolucos\Canal\`.
