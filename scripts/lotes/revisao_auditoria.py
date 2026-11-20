"""Aplica as revisões aprovadas da auditoria (docs/auditoria/AUDITORIA_MUSICAS_11-39.md) — 17/11/2026.

Uso: .venv/bin/python scripts/lotes/revisao_auditoria.py
Reescreve letra.txt e atualiza a ficha (estrutura, ritmo, cenas, YouTube) das músicas Regulares e cria a 36 nova.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "canais" / "laurinha" / "musicas"


def convite(gostou):
    return ("[Outro - Laurinha and Luisinho talk to the kids, kids choir answers]\n" + gostou +
            "\nDá um joinha! (Joinha!)\nChama o papai e a mamãe\nPra se inscrever no canal! (Zum, zum!)\n")


def montar(intro, v1, ref, meio, v2, ponte, gostou, tchau, ref_final=None, ref2=None, pos=None, ponte_tag="kids follow the commands",
           fim_tag="one big final hit, hard stop", trad=False):
    t = ", traditional" if trad else ""
    r2 = ref2 or ref
    rf = ref_final or ref
    p = (pos + "\n") if pos else ""
    return "\n".join([
        intro, "", v1, "", f"[Virada]\n[Chorus - kids choir{t}]\n{ref}\n{p}",
        "[Bordão laurinha]\n[Intervalo 10s]\n(Laurinha e Luisinho!)\n", v2, "",
        f"[Virada]\n[Chorus - kids choir{t}]\n{r2}\n{p}", f"[Bridge - {ponte_tag}]\n{ponte}\n",
        "[Bordão luisinho]\n[Intervalo 10s]\n", f"[Virada]\n[Chorus - kids choir, louder{t}]\n{rf}\n{p}",
        convite(gostou), f"[Outro - {fim_tag}]\n{tchau}\n[End]\n"])


def dobra(bloco):
    return bloco + "\n" + bloco


L = {}

# 14 — jogo de adivinhar; o Luisinho erra e o coro corrige
L["14"] = montar(
    "[Intro - pagodão percussion]\nQue forma é essa? (Hein?)",
    "[Verse - Laurinha, girl child vocal]\nA bola é… (Redonda!)\nA roda é… (Redonda!)\nE a lua cheia? (Redonda!)\nIsso é um círculo! (Círculo!)",
    dobra("Que forma é essa? (Hein?)\nQue forma é essa? (Hein?)\nDesenha no ar\nE fala pra mim! (Ê!)"), None,
    "[Verse - Luisinho, boy child vocal]\nA janela é… (Quadrado!)\nO presente é… (Quadrado!)\nE o telhado? (Quadrado!)\nIh, errei! (Triângulo!)",
    "Círculo com o braço! (Ó!)\nQuadrado com o dedo! (Plim!)\nTelhado com a mão! (Pontinha!)\nE o ovo? (Oval!)",
    "Gostou das formas? (Gostei!)", "Que forma é essa? Tchau! (Zum!)", ponte_tag="kids draw the shapes in the air")

# 19 — jogo de imitar caras
L["19"] = montar(
    "[Intro - sanfona and soft zabumba]\nCara de quê? (De quê?)",
    "[Verse - Luisinho, boy child vocal]\nCara de feliz! (Ê!)\nCara de bravo! (Grrr!)\nCara de susto! (Ah!)\nCara de sono… (Uaaah!)",
    dobra("Cara de quê? (De quê?)\nCara de quê? (De quê?)\nMostra pra mim\nA tua carinha! (Ê!)"), None,
    "[Verse - Laurinha, girl child vocal]\nFicou bravo? (Conta até três!)\nFicou triste? (Pede um abraço!)\nFicou com medo? (Chama a mamãe!)\nTudo bem sentir! (Tudo bem!)",
    "Cheira a florzinha… (Inspira!)\nAssopra a velinha! (Fuuu!)\nMais uma vez… (Inspira!)\nCara de feliz! (Ê!)",
    "Gostou da brincadeira? (Gostei!)", "Cara de feliz! Tchau! (Zum!)", ponte_tag="soft, kids breathe along")

# 21 — careta de azedo
L["21"] = montar(
    "[Intro - cavaquinho and pandeiro]\n(Tindolelê! Tindolalá!)",
    "[Verse - Laurinha, girl child vocal]\nNo quintal da vovó (Oi, vovó!)\nTem limão no pé!\nVerdinho, cheiroso… (Hum!)\nMorde pra ver! (Aaai!)",
    dobra("Meu limão, meu limoeiro,\nMeu pé de jacarandá!\nUma vez, tindolelê, (Tindolelê!)\nOutra vez, tindolalá! (Tindolalá!)"), None,
    "[Verse - Luisinho, boy child vocal]\nCareta de azedo! (Aaai!)\nCareta de doce! (Hum!)\nCareta de azedo! (Aaai!)\nHa ha ha ha! (Ha ha!)",
    "Espreme! (Espreme!)\nMexe! (Mexe!)\nUm golinho… (Hum!)\nLimonada da vovó! (Ê!)",
    "Gostou do limão? (Gostei!)", "Tindolelê, tindolalá! Tchau! (Zum!)", trad=True)

# 25 — devagar × rapidinho, peekaboo no casco
REF25 = ("Devagar, devagarinho… (Devagar!)\nDevagar, devagarinho… (Devagar!)\n[Double time]\nAgora rapidinho! (Corre, corre, corre!)\n"
         "[Half time]\nIh, voltou devagar! (Ufa!)")
L["25"] = montar(
    "[Intro - reggae skank guitar]\nDevagar… devagarinho…",
    "[Verse - Laurinha, girl child vocal]\nQuem vem chegando? (Quem?)\nCasinha nas costas!\nÉ a tartaruga! (Oi!)\nSem pressa nenhuma!",
    REF25, None,
    "[Verse - Luisinho, boy child vocal]\nCadê a cabeça? (Cadê?)\nEscondeu no casco!\nCadê a cabeça? (Cadê?)\nAchou! (Achou!)",
    "Devagar… (Devagar…)\nRapidinho! (Rapidinho!)\nDevagar…\n[Stop - silence 2 seconds]\nParou! Tartaruga! (Estátua!)",
    "Gostou da tartaruga? (Gostei!)", "Devagarinho… Tchau! (Zum!)", ponte_tag="kids follow the tempo")

# 27 — menos letra, nomes em rodízio
def canoa(nome):
    return (f"A canoa virou! (Virou!)\nPois deixaram ela virar,\nFoi por causa {nome}\nQue não soube remar!\n"
            f"Se eu fosse um peixinho\nE soubesse nadar,\nEu tirava {nome.replace('da ', 'a ').replace('do ', 'o ')}\nDo fundo do mar! (Zum!)")
L["27"] = montar(
    "[Intro - sanfona and soft zabumba]\n(Rema, rema! Zum, zum!)",
    "[Verse - Luisinho, boy child vocal]\nDobrei um papel… (Dobra!)\nVirou canoa! (Canoa!)\nRema, rema… (Rema!)\nIh, vai virar! (Ih!)",
    canoa("da Laurinha"), None,
    "[Verse - Laurinha, girl child vocal]\nMas quem tem asinha (Zum!)\nNão afunda, não! (Não!)\nVoou da canoa… (Voou!)\nSequinha! (Ufa!)",
    "Rema pra frente! (Rema!)\nBalança pra lá! (Pra lá!)\nBalança pra cá! (Pra cá!)\nA canoa virou? (Não virou!)",
    "Gostou da canoa? (Gostei!)", "A canoa virou! Tchau! (Zum!)", ref2=canoa("do Luisinho"), ref_final=canoa("da turminha"),
    ponte_tag="kids row and balance", trad=True)

# 29 — canção de gestos
L["29"] = montar(
    "[Intro - cavaquinho and soft percussion]\nMamãe querida! (Beijo!)",
    "[Verse - Laurinha, girl child vocal]\nAcordei cedinho… (Psiu!)\nPé ante pé!\nCafé na caminha… (Surpresa!)\nPra minha mamãe!",
    dobra("Mamãe querida! (Beijo!)\nMamãe querida! (Beijo!)\nTe amo daqui\nAté a lua! (Até a lua!)"), None,
    "[Verse - Luisinho, boy child vocal]\nE a mamãe canguru? (Leva na bolsinha!)\nE a mamãe passarinho? (Faz o ninho!)\n"
    "E a mamãe galinha? (Choca o ovo!)\nE a minha mamãe? (Me dá abraço!)",
    "Abraço apertado! (Aperta!)\nBeijinho na bochecha! (Muá!)\nCoração com a mão! (Coração!)\nAté a lua! (Até a lua!)",
    "Gostou da música? (Gostei!)", "Mamãe querida! Tchau! (Beijo!)", ponte_tag="kids do the gestures")

# 30 — reencontro alegre + pós-refrão de movimento
L["30"] = montar(
    "[Intro - reggae skank guitar]\n(Blub, blub! Zum, zum!)",
    "[Verse - Luisinho, boy child vocal]\nA Laurinha viajou… (Ohh…)\nTô igual peixinho\nFora da água! (Ih!)\nToc, toc! (Quem é?)\nVoltou! (Voltou!)",
    "Como pode um peixe vivo\nViver fora da água fria?\nComo poderei viver\nSem a tua companhia?", None,
    "[Verse - Laurinha, girl child vocal]\nBoca de peixe! (Ó!)\nFaz bolhinha! (Blub!)\nNadadeira! (Mexe!)\nRabinho! (Balança!)",
    "Nada pra frente! (Nada!)\nNada de lado! (De lado!)\nMergulha… (Splash!)\nAbraço de amigo! (Abraço!)",
    "Gostou da história? (Gostei!)", "Peixe vivo! Tchau! (Blub!)", trad=True, ponte_tag="kids swim",
    pos="[Post-chorus - kids choir]\nBlub, blub! (Blub, blub!)\nNada, nada! (Nada, nada!)\nPeixe vivo! (Peixe vivo!)\nNa água fria! (Ê!)")

# 32 — a mágica acontece de verdade
L["32"] = montar(
    "[Intro - ciranda drums and acoustic guitar]\nPalavrinha mágica! (Plim!)",
    "[Verse - Laurinha, girl child vocal]\nPor favor! (Plim!)\nA porta abriu! (Uau!)\nObrigada! (Plim!)\nA flor sorriu! (Uau!)",
    dobra("Palavrinha mágica! (Plim!)\nPalavrinha mágica! (Plim!)\nFala bem bonito…\nPlim! Funcionou! (Uau!)"), None,
    "[Verse - Luisinho, boy child vocal]\nPisei no pé… (Ai!)\nDesculpa! (Plim!)\nAmizade voltou! (Uau!)\nAbraço! (Plim!)",
    "Bem baixinho… (por favor…)\nBem alto! (POR FAVOR!)\nBem baixinho… (obrigado…)\nBem alto! (OBRIGADO!)",
    "Gostou da mágica? (Gostei!)", "Plim! Tchau! (Uau!)", ponte_tag="whisper, then shout")

# 35 — esticar no refrão + língua roxa
L["35"] = montar(
    "[Intro - sanfona and zabumba]\nEstica, estica! (Estica!)",
    "[Verse - Luisinho, boy child vocal]\nVoei lá no alto… (Zum!)\nQuem tá aqui? (Hein?)\nUma cabeça pintadinha…\nÉ a girafa! (Oi!)",
    dobra("Pescoço de girafa! (Estica!)\nPescoço de girafa! (Estica!)\nMais alto, mais alto…\nPegou a folhinha! (Nhac!)"), None,
    "[Verse - Laurinha, girl child vocal]\nMostra a língua! (Blé!)\nÉ roxinha! (Roxinha!)\nLimpa a orelha… (Eca!)\nCom a língua! (Ha ha!)",
    "Na pontinha do pé! (Pontinha!)\nEstica o braço! (Estica!)\nMais um pouquinho… (Ufa!)\nE abaixa pra beber! (Glub!)",
    "Gostou da girafa? (Gostei!)", "Pescoço de girafa! Tchau! (Nhac!)", ponte_tag="kids stretch")

# 36 — NOVA autoral (substitui Alecrim Dourado): Atchim!
L["36"] = montar(
    "[Intro - sanfona, zabumba and triângulo]\nAaa… aaa… ATCHIM!",
    "[Verse - Luisinho, boy child vocal]\nCoceguinha no nariz… (Ih!)\nTá vindo, tá vindo… (Aaa…)\nSegura, segura… (Aaa…)\nATCHIM! (Saúde!)",
    dobra("Atchim, atchim! (Saúde!)\nNo cotovelo, sim! (Sim!)\nAtchim, atchim! (Saúde!)\nE lava a mão no fim! (Ê!)"), None,
    "[Verse - Laurinha, girl child vocal]\nO elefante espirra… (ATCHIIIM!)\nO ratinho espirra… (atchim…)\nE a muriçoca? (Hein?)\nAtchim-zum! (Ha ha!)",
    "Aaa… (Aaa…)\nAaa… (Aaa…)\n[Stop - silence 2 seconds]\nNão saiu! (Ih!)\nATCHIM! (Saúde!)",
    "Gostou do atchim? (Gostei!)", "Atchim, atchim! Tchau! (Saúde!)", ponte_tag="slow build up, kids hold the breath")

# 37 — adivinha pelo som; o fim do refrão muda a cada volta
def crescer(rev):
    return f"Quando eu crescer! (Crescer!)\nEu vou ser… (O quê?)\nAdivinha, adivinha…\nTchan, tchan, tchan! ({rev}!)"
L["37"] = montar(
    "[Intro - disco strings and four-on-the-floor]\nQuando eu crescer… (O quê?)",
    "[Verse - Laurinha, girl child vocal]\nUóóó, uóóó! (Sirene!)\nMangueira na mão! (Splash!)\nApaga o fogo! (Apagou!)\nQuem é? (Bombeiro!)",
    crescer("Bombeiro"), None,
    "[Verse - Luisinho, boy child vocal]\nTum-tum, tum-tum! (Coração!)\nDiz \"aaah\"! (Aaah!)\nCuida do dodói! (Sarou!)\nQuem é? (Médica!)",
    "Mexe a panela! (Hum!)\nEscreve no quadro! (A, B, C!)\nPilota o foguete! (Vruuum!)\nE você? (Eu vou ser…)",
    "Gostou da brincadeira? (Gostei!)", "Quando eu crescer! Tchau! (Zum!)", ref2=crescer("Médica"),
    ref_final=crescer("O que eu quiser"), ponte_tag="kids mime")

# 38 — abraço de urso vira o gancho
L["38"] = montar(
    "[Intro - bright guitar riff and drums]\n(Upa, upa! Zum, zum!)",
    "[Verse - Luisinho, boy child vocal]\nQuem me joga pro alto? (Papai!)\nQuem faz cavalinho? (Papai!)\nQuem tem voz de dragão? (Rawr!)\nÉ o meu papai! (Papai!)",
    dobra("Meu papai! (Papai!)\nMeu papai! (Papai!)\nAbraço de urso! (Hum!)\nUpa, upa, upa! (Upa!)"), None,
    "[Verse - Laurinha, girl child vocal]\nE o papai pinguim? (Hein?)\nChoca o ovo no pé! (No pé!)\nNo frio do gelo… (Brrr!)\nQue papai legal! (Legal!)",
    "Cavalinho! (Upa!)\nAviãozinho! (Vruuum!)\nCosquinha! (Ha ha!)\nAbraço de urso! (Hum!)",
    "Gostou da música? (Gostei!)", "Meu papai! Tchau! (Hum!)", ponte_tag="kids play")

# 39 — cumulativa
L["39"] = montar(
    "[Intro - samba-reggae drums]\nDia de brincar! (Ê!)",
    "[Verse - Laurinha, girl child vocal]\nHoje é o nosso dia! (Viva!)\nDia das Crianças! (Viva!)\nChama todo mundo… (Vem!)\nBora brincar! (Bora!)",
    "Dia de brincar! (Ê!)\nDia de brincar! (Ê!)\nPega-pega! (Peguei!)\nDia de brincar! (Ê!)", None,
    "[Verse - Luisinho, boy child vocal]\nMais uma? (Mais uma!)\nEsconde-esconde! (Achei!)\nE mais uma? (Mais uma!)\nAmarelinha! (Pulei!)",
    "Num pé só! (Num pé!)\nNos dois! (Nos dois!)\nGira e senta! (Sentei!)\nLevanta e grita! (Viva!)",
    "Gostou da brincadeira? (Gostei!)", "Dia de brincar! Tchau! (Zum!)",
    ref2="Dia de brincar! (Ê!)\nDia de brincar! (Ê!)\nPega-pega! (Peguei!)\nEsconde-esconde! (Achei!)\nAmarelinha! (Pulei!)\nDia de brincar! (Ê!)",
    ref_final="Dia de brincar! (Ê!)\nDia de brincar! (Ê!)\nPega-pega! (Peguei!)\nEsconde-esconde! (Achei!)\nAmarelinha! (Pulei!)\nPula corda! (Um, dois, três!)\nDia de brincar! (Ê!)")

FICHA = {
 "14": dict(estrutura="B", cenas=[("verso 1","a Laurinha mostra coisas redondas (bola, roda, lua cheia) e o círculo se desenha no ar"),
   ("refrão","os dois desenham formas no ar com o dedo; a forma aparece em traço de giz colorido"),
   ("verso 2","o Luisinho erra (\"o telhado é quadrado!\"), o coro corrige \"Triângulo!\" e ele ri"),
   ("ponte","desenhar com o corpo: círculo com o braço, quadrado com o dedo, telhado com as mãos; o ovo aparece: oval!")]),
 "19": dict(estrutura="R", cenas=[("verso 1","o Luisinho faz cada cara em close: feliz, bravo, susto, sono"),
   ("refrão","a câmera aponta para a criança: \"mostra pra mim a tua carinha\"; os dois fazem caras diferentes"),
   ("verso 2","a Laurinha conta até três quando fica brava, pede abraço quando fica triste, chama a mamãe com medo"),
   ("ponte","respiração da flor e da velinha, devagar, e volta a cara de feliz")]),
 "21": dict(estrutura="R", curiosidade="limão azedo faz careta! (e a limonada da vovó é docinha)",
   cenas=[("verso 1","quintal da vovó com limoeiro gigante; a Laurinha morde o limão"),
   ("refrão","roda em volta do limoeiro balançando no tindolelê/tindolalá"),
   ("verso 2","jogo de careta: azedo (careta enorme), doce (sorriso), azedo de novo, todos riem"),
   ("ponte","espreme, mexe, golinho: limonada da vovó")]),
 "25": dict(estrutura="D", curiosidade="a tartaruga esconde a cabeça no casco, que é a casinha dela",
   cenas=[("verso 1","jardim visto de pertinho: a tartaruga enorme chegando sem pressa"),
   ("refrão","devagar em câmera lenta; no \"agora rapidinho\" tudo acelera e a turma corre; volta devagar (\"ufa\")"),
   ("verso 2","esconde-esconde: a cabeça some no casco (\"cadê?\") e aparece (\"achou!\")"),
   ("ponte","devagar, rapidinho, devagar… para: estátua")]),
 "27": dict(estrutura="R", curiosidade="quem tem asinha não afunda; e na água a gente brinca sempre com o papai e a mamãe",
   cenas=[("verso 1","o Luisinho dobra um papel que vira canoa no laguinho do parque; rema, balança e vai virar"),
   ("refrão","a canoa vira (splash); o nome muda a cada volta: Laurinha, Luisinho, turminha"),
   ("verso 2","a Laurinha sai voando da água, sequinha"),
   ("ponte","remar e equilibrar: pra lá, pra cá, não virou!")]),
 "29": dict(estrutura="R", cenas=[("verso 1","a Laurinha na ponta do pé leva café na cama para a mamãe"),
   ("refrão","abraço e beijo; no \"até a lua\" os braços sobem e a câmera sobe até a lua"),
   ("verso 2","quiz das mamães bichos: canguru com bolsinha, passarinho no ninho, galinha chocando, a mamãe muriçoca abraçando"),
   ("ponte","gestos para fazer na mãe de verdade: abraço apertado, beijinho, coração com a mão")]),
 "30": dict(estrutura="E", curiosidade="o peixinho faz bolhinhas e nada com a nadadeira e o rabinho",
   cenas=[("verso 1","o Luisinho sozinho, igual peixinho fora da água; toc-toc: a Laurinha voltou"),
   ("refrão","refrão tradicional + pós-refrão de dança do peixe (blub, blub, nada, nada)"),
   ("verso 2","boca de peixe, bolhinha, nadadeira, rabinho: imitação com o corpo"),
   ("ponte","nadar pra frente, de lado, mergulho e abraço de amigos")]),
 "32": dict(estrutura="R", curiosidade="o sorriso pega: quando alguém sorri pra gente, a gente sorri também",
   cenas=[("verso 1","por favor: a porta abre com brilho (plim); obrigada: a flor sorri"),
   ("refrão","cada \"palavrinha mágica\" solta estrelinhas e algo acontece (\"plim! funcionou!\")"),
   ("verso 2","o Luisinho pisa no pé da Joaninha, pede desculpa e a amizade volta com abraço"),
   ("ponte","jogo baixinho/alto: cochicha por favor, grita POR FAVOR")]),
 "35": dict(estrutura="R", cenas=[("verso 1","o Luisinho voa até a copa e encontra a cabeça da girafa"),
   ("refrão","todos esticam o pescoço cada vez mais alto até pegar a folhinha (nhac!)"),
   ("verso 2","a girafa mostra a língua roxa e limpa a orelha com ela (eca! ha ha!)"),
   ("ponte","alongamento: pontinha do pé, estica o braço, abaixa pra beber água")]),
 "37": dict(estrutura="B", ritmo="disco_infantil", alternativas=["frevo"],
   cenas=[("verso 1","sirene e mangueira: a Laurinha de bombeira apaga o fogo; adivinha quem é"),
   ("refrão","\"tchan, tchan, tchan!\" e a revelação muda a cada volta (bombeiro, médica, o que eu quiser) com luz de palco"),
   ("verso 2","tum-tum do estetoscópio, \"diz aaah\": o Luisinho de médico"),
   ("ponte","mímica: cozinheiro, professora, piloto de foguete; a câmera pergunta à criança \"e você?\"")]),
 "38": dict(estrutura="R", cenas=[("verso 1","papai joga pro alto, faz cavalinho, conta história com voz de dragão"),
   ("refrão","abraço de urso e cavalinho (upa, upa)"),
   ("verso 2","papai pinguim chocando o ovo no pé, no gelo"),
   ("ponte","cavalinho, aviãozinho, cosquinha, abraço de urso")]),
 "39": dict(estrutura="C", cenas=[("verso 1","Dia das Crianças: a turma chega chamando todo mundo"),
   ("refrão","cumulativo: cada volta soma uma brincadeira (pega-pega → esconde-esconde → amarelinha → pula-corda)"),
   ("verso 2","\"mais uma?\": esconde-esconde (achei!) e amarelinha (pulei!)"),
   ("ponte","amarelinha guiada: num pé, nos dois, gira, senta e grita viva")]),
}

NOVA36 = dict(titulo="Atchim!", gancho="atchim atchim", palavras_tema=["atchim", "espirro", "nariz", "saúde"],
  tema="espirrar no cotovelo e lavar a mão (com muito espirro engraçado)", tipo="rotina", estrutura="D", ritmo="baiao",
  dia_a_dia=["espirrar no cotovelo", "dizer saúde", "lavar as mãos"],
  curiosidade="espirro a gente faz no cotovelo, e depois lava a mão",
  alternativas=["forro_piseiro"], persona="luisinho",
  cenas=[("intro","close no nariz do Luisinho: aaa… aaa… ATCHIM! (as antenas balançam)"),
   ("verso 1","coceguinha no nariz, tá vindo, segura… ATCHIM! e a Laurinha responde \"Saúde!\""),
   ("refrão","espirro no cotovelo (gesto) e lavar a mão no fim, com espuma"),
   ("verso 2","espirros de bichos: elefante (enorme), ratinho (pequenininho), muriçoca (atchim-zum!)"),
   ("ponte","suspense: aaa… aaa… parou! não saiu… ATCHIM!"),
   ("final","convite; todos espirram juntos no tchau (\"Saúde!\")")],
  youtube={"resumo": "ATCHIM! 🤧 Coceguinha no nariz… tá vindo… ATCHIM! O Luisinho espirra, a Laurinha diz \"Saúde!\" e a turma aprende: espirro a gente faz no cotovelo, e depois lava a mão! E como espirra o elefante? E o ratinho? E a muriçoca? Atchim-zum!",
           "resumo_short": "ATCHIM! 🤧 No cotovelo, sim! Espirre junto com a Laurinha e o Luisinho!",
           "curiosidade": "Espirro a gente faz no cotovelo, e depois lava a mão"},
  cantam={"verso 1": "luisinho", "refrão": "coro", "verso 2": "laurinha", "ponte": "suspense do espirro, coro", "final": "todo mundo"})


def main():
    for n, txt in L.items():
        d = next(M.glob(f"{n}_*"))
        if n == "36" and d.name != "36_atchim":
            subprocess.run(["git", "mv", str(d), str(M / "36_atchim")], cwd=ROOT, check=True)
            d = M / "36_atchim"
        (d / "letra.txt").write_text(txt, encoding="utf-8")
        fp = d / "ficha.json"
        f = json.loads(fp.read_text(encoding="utf-8"))
        if n == "36":
            for k in ("dominio_publico", "miniatura_cena"):
                f.pop(k, None)
            f.update({k: v for k, v in NOVA36.items() if k != "cenas"})
            f["cenas"] = [{"parte": a, "ideia": b} for a, b in NOVA36["cenas"]]
            E = json.loads((M / "estilos.json").read_text(encoding="utf-8"))
            f["bpm"] = E["ritmos"][f["ritmo"]]["bpm"][2]
        else:
            spec = FICHA[n]
            for k, v in spec.items():
                if k == "cenas":
                    f["cenas"] = [{"parte": a, "ideia": b} for a, b in v]
                else:
                    f[k] = v
            if "ritmo" in spec:
                E = json.loads((M / "estilos.json").read_text(encoding="utf-8"))
                f["bpm"] = E["ritmos"][spec["ritmo"]]["bpm"][2]
        f["status"] = "letra_revisada"
        f["revisao"] = "auditoria 17/11/2026 (docs/auditoria/AUDITORIA_MUSICAS_11-39.md)"
        fp.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(d.name)


if __name__ == "__main__":
    main()
