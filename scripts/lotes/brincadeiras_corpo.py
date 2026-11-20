"""10 músicas novas de brincadeira com o corpo (pedido do usuário, 18/11/2026: temas como "No Ritmo Quá Quá",
"A Onda do Caranguejo", "Cabeça Ombro Joelho e Pé", "Morto-Vivo" — só a receita do gênero, nada copiado).

Uso: .venv/bin/python scripts/lotes/brincadeiras_corpo.py
Cria as músicas (numeradas no fim) e depois o renumerar_intercalar.py as espalha entre 12 e 49.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lotes.revisao_auditoria import montar  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "canais" / "laurinha" / "musicas"


def d2(b):
    return b + "\n" + b


V = {"laurinha": "Laurinha, girl child vocal", "luisinho": "Luisinho, boy child vocal"}
OUT = {"laurinha": "luisinho", "luisinho": "laurinha"}


def verso(quem, linhas):
    return f"[Verse - {V[quem]}]\n" + "\n".join(linhas)


S = []

# 1 — Dorme, Acorda!
S.append(dict(slug="dorme_acorda", titulo="Dorme, Acorda!", ritmo="funk_infantil", tipo="brincadeira", estrutura="D", v1="luisinho",
  gancho="dorme acorda", palavras=["dorme", "acorda", "sono", "galo"], tema="brincadeira de dormir e acordar cada vez mais rápido, com pegadinha",
  curiosidade="o galo canta de manhã cedinho e acorda todo mundo",
  letra=montar("[Intro - tamborzão beat and claps]\nDorme… acorda! (Ê!)",
    verso("luisinho", ["Fecha o olhinho… (Psiu!)", "Deita a cabeça… (Ronc!)", "Ih, tô com sono… (Uaaah!)", "Dorme, acorda! (Ê!)"]),
    d2("Dorme! (Ronc, ronc!)\nAcorda! (Ê!)\nDorme, acorda,\nDorme, acorda! (Ê!)"), None,
    verso("laurinha", ["Galo cantou! (Cocoricó!)", "Despertador! (Trimmm!)", "Sol na janela… (Bom dia!)", "Espreguiça! (Uaaah!)"]),
    "Dorme… (Ronc…)\nAcorda! (Ê!)\nDorme… (Ronc…)\n[Stop - silence 2 seconds]\nQuem dormiu de verdade? (Ha ha!)",
    "Gostou da brincadeira? (Gostei!)", "Dorme, acorda! Tchau! (Ê!)",
    ref2="[Faster]\n" + d2("Dorme! (Ronc, ronc!)\nAcorda! (Ê!)\nDorme, acorda,\nDorme, acorda! (Ê!)"),
    ref_final="[Very fast]\nDorme! (Ronc, ronc!)\nAcorda! (Ê!)\nDorme, acorda,\nDorme, acorda! (Ê!)\nDorme! (Ronc!)\nAcorda! (Ê!)\nCochilou… (Ih!)\nAcorda, Luisinho! (Ha ha!)",
    ponte_tag="kids follow, with a trick"),
  cenas=[("intro", "quarto azul: o Luisinho de olho fechado, ronca e acorda num pulo"),
         ("verso 1", "fecha o olhinho, deita na cama, boceja: tá com sono"),
         ("refrão", "dorme (deita e ronca, Zzz na tela) / acorda (pula de braços para cima), cada volta mais rápido; no fim ele cochila de verdade e a Laurinha acorda"),
         ("verso 2", "galo cantando na janela, despertador tocando, sol entrando, espreguiçada"),
         ("ponte", "dorme, acorda, dorme… a música para: quem dormiu de verdade? todos riem"),
         ("final", "convite; o Luisinho boceja no tchau")],
  yt=("DORME, ACORDA! 😴⏰ Fecha o olhinho, deita a cabeça… dorme! Ronc, ronc! Acorda! Ê! A brincadeira vai ficando cada vez mais rápida… e o Luisinho cochilou de verdade! O galo canta, o despertador toca e o sol entra na janela: bom dia!",
      "DORME, ACORDA! 😴 Ronc, ronc… acorda! Brinque com a Laurinha e o Luisinho!", "O galo canta de manhã cedinho e acorda todo mundo")))

# 2 — Do Pé à Cabeça!
BL = "Do pé à cabeça! (Ê!)\nPé, joelho… (Toca!)\nBarriga, ombro… (Toca!)\nE a cabeça! (Ê!)"
S.append(dict(slug="do_pe_a_cabeca", titulo="Do Pé à Cabeça!", ritmo="axe", tipo="danca", estrutura="C", v1="laurinha",
  gancho="do pé à cabeça", palavras=["pé", "joelho", "ombro", "cabeça"], tema="tocar as partes do corpo, cada volta mais rápido",
  curiosidade="o osso mais comprido do corpo fica na coxa: é o fêmur",
  letra=montar("[Intro - samba-reggae drums]\nDo pé à cabeça! (Ê!)",
    verso("laurinha", ["Bora acordar o corpo? (Bora!)", "Começa pelo pé… (Pé!)", "Sobe, sobe… (Sobe!)", "Do pé à cabeça! (Ê!)"]),
    d2(BL), None,
    verso("luisinho", ["Mexe o dedão! (Dedão!)", "Gira o joelho! (Gira!)", "Balança o bumbum! (Ha ha!)", "E o nariz? (Bip!)"]),
    "Agora devagar… (Devagar…)\nPé… joelho…\nBarriga… ombro…\nCa-be-ça! (Ê!)",
    "Gostou da brincadeira? (Gostei!)", "Do pé à cabeça! Tchau! (Zum!)",
    ref2="[Faster]\n" + d2(BL), ref_final="[Very fast]\n" + BL + "\nUfa, cansei! (Ha ha!)", ponte_tag="slow, kids touch each part"),
  cenas=[("verso 1", "a Laurinha de frente para a câmera aponta o pé e vai subindo até a cabeça"),
         ("refrão", "os dois tocam pé, joelho, barriga, ombro e cabeça; cada volta mais rápido até se enrolarem e rirem"),
         ("verso 2", "o Luisinho mexe o dedão, gira o joelho, balança o bumbum e aperta o próprio nariz (bip!)"),
         ("ponte", "câmera lenta engraçada: pé… joelho… barriga… ombro… ca-be-ça!"),
         ("final", "convite; os dois caem sentados cansados (ufa!) e dão tchau")],
  yt=("DO PÉ À CABEÇA! 🦶👋🙆 Bora acordar o corpo: pé, joelho, barriga, ombro e cabeça! A cada volta fica mais rápido… até cansar! Mexe o dedão, gira o joelho, balança o bumbum e aperta o nariz: bip! Sabia que o osso mais comprido do corpo fica na coxa?",
      "DO PÉ À CABEÇA! 🙆 Toque as partes do corpo cada vez mais rápido com a Laurinha e o Luisinho!", "O osso mais comprido do corpo fica na coxa: é o fêmur")))

# 3 — Andar de Pinguim
S.append(dict(slug="andar_de_pinguim", titulo="Andar de Pinguim", ritmo="frevo", tipo="animal", estrutura="R", v1="luisinho",
  gancho="andar de pinguim", palavras=["pinguim", "gelo", "escorrega", "nadar"], tema="imitar o jeito de andar do pinguim",
  curiosidade="o pinguim tem asa mas não voa no céu: ele \"voa\" nadando debaixo d'água",
  letra=montar("[Intro - brass fanfare and snare]\nAndar de pinguim! (Ê!)",
    verso("luisinho", ["Voei pro gelo! (Brrr!)", "Quem tá aí? (Hein?)", "De casaca preta… (Oi!)", "É o pinguim! (Pinguim!)"]),
    d2("Andar de pinguim! (Ê!)\nPé grudadinho! (Tic, tic!)\nAndar de pinguim! (Ê!)\nBalança, balança! (Ê!)"), None,
    verso("laurinha", ["Escorrega de barriga! (Uiii!)", "Mergulha no mar! (Splash!)", "Na água ele voa… (Uau!)", "Mas no céu não dá! (Ha ha!)"]),
    "Braço colado! (Colado!)\nPé de pato! (Tic, tic!)\nEscorrega… (Uiii!)\nAbraço pra esquentar! (Hum!)",
    "Gostou do pinguim? (Gostei!)", "Andar de pinguim! Tchau! (Brrr!)", ponte_tag="kids walk like penguins"),
  cenas=[("verso 1", "o Luisinho voa até o gelo (Brrr!) e encontra um pinguim simpático de casaca"),
         ("refrão", "fila de pinguins andando de pé grudado e balançando; os dois imitam atrás"),
         ("verso 2", "o pinguim escorrega de barriga no gelo, mergulha e \"voa\" debaixo d'água; tenta voar no céu e cai (ha ha)"),
         ("ponte", "braço colado, pé de pato, escorrega e abraço coletivo para esquentar"),
         ("final", "convite; os pinguins acenando com as asinhas")],
  yt=("ANDAR DE PINGUIM! 🐧 O Luisinho voou pro gelo e encontrou o pinguim de casaca preta! Pé grudadinho, tic, tic, balança, balança: todo mundo andando de pinguim! Ele escorrega de barriga, mergulha e na água parece que voa… mas no céu não dá!",
      "ANDAR DE PINGUIM! 🐧 Pé grudadinho e balança com a Laurinha e o Luisinho!", "O pinguim tem asa mas não voa no céu: ele \"voa\" nadando debaixo d'água")))

# 4 — Bicho Faz Assim!
def bicho(nome, resp):
    return f"Bicho faz assim! (Assim!)\nE o {nome}? ({resp})\nBicho faz assim! (Assim!)\nTodo mundo faz! (Ê!)"
S.append(dict(slug="bicho_faz_assim", titulo="Bicho Faz Assim!", ritmo="pagodao", tipo="animal", estrutura="B", v1="laurinha",
  gancho="bicho faz assim", palavras=["bicho", "sapo", "cobra", "macaco"], tema="o coro fala o bicho e todo mundo imita o jeito dele",
  curiosidade="cada bicho se mexe de um jeito: o sapo pula, a cobra rasteja e o passarinho voa",
  letra=montar("[Intro - pagodão percussion]\nBicho faz assim! (Assim!)",
    verso("laurinha", ["Vamos brincar? (Bora!)", "Eu falo o bicho… (Hein?)", "Você imita! (Imito!)", "Preparado? (Sim!)"]),
    bicho("sapo", "Pula, pula!") + "\n" + bicho("cobra", "Ssss!"), None,
    verso("luisinho", ["E a muriçoca? (Hein?)", "Bate a asinha… (Zum, zum!)", "Pica o braço? (Não!)", "Só dá abraço! (Ha ha!)"]),
    "Mais rápido! (Rápido!)\nSapo! (Pula!)\nCobra! (Ssss!)\nMacaco! (Uh, uh!)\nJacaré! (Nhac!)",
    "Gostou dos bichos? (Gostei!)", "Bicho faz assim! Tchau! (Zum!)",
    ref2=bicho("macaco", "Uh, uh! Coça, coça!") + "\n" + bicho("elefante", "Fuuum!"),
    ref_final=bicho("passarinho", "Piu, piu! Voa!") + "\n" + bicho("jacaré", "Nhac!"), ponte_tag="fast, kids imitate each animal"),
  cenas=[("verso 1", "a Laurinha apresenta a brincadeira; a cada bicho, ele aparece grandão ao lado dela"),
         ("refrão", "aparece o bicho (sapo, cobra, macaco, elefante, passarinho, jacaré) e os dois imitam: pulam, rastejam, coçam, fazem tromba, voam, abrem a boca"),
         ("verso 2", "e a muriçoca? o Luisinho bate as asas e, em vez de picar, dá um abraço"),
         ("ponte", "rapidinho: os bichos passam um atrás do outro e os dois mal conseguem acompanhar"),
         ("final", "convite; todos os bichos acenam no tchau")],
  yt=("BICHO FAZ ASSIM! 🐸🐍🐒🐘 A Laurinha fala o bicho e todo mundo imita: o sapo pula, a cobra faz ssss, o macaco coça, o elefante faz fuuum com a tromba, o passarinho voa e o jacaré… nhac! E a muriçoca? Em vez de picar, dá abraço!",
      "BICHO FAZ ASSIM! 🐸 Imite os bichos com a Laurinha e o Luisinho!", "Cada bicho se mexe de um jeito: o sapo pula, a cobra rasteja e o passarinho voa")))

# 5 — Robô Dançarino
S.append(dict(slug="robo_dancarino", titulo="Robô Dançarino", ritmo="eletronica_infantil", tipo="danca", estrutura="D", v1="luisinho",
  gancho="robô dançarino", palavras=["robô", "botão", "pilha", "dança"], tema="dançar como robô, travar e acabar a pilha",
  curiosidade="o robô precisa de energia (pilha ou bateria) para funcionar, igual a gente precisa de comida",
  letra=montar("[Intro - sparkly synths and robot sound effects]\nRobô dançarino! (Bip, bop!)",
    verso("luisinho", ["Achei um botão… (Hein?)", "Apertei! (Clic!)", "Ligou um robô! (Bip!)", "Robô dançarino! (Bop!)"]),
    d2("Robô dançarino! (Bip, bop!)\nBraço duro, perna dura! (Tec, tec!)\nRobô dançarino! (Bip, bop!)\nVira, vira… trava! (Trac!)"), None,
    verso("laurinha", ["Ih, a pilha tá acabando… (Uuuu…)", "Devagar… devagar…", "Desligou! (Bip…)", "Recarrega! (Plim!)"]),
    "Liga! (Bip!)\nTrava! (Trac!)\nLiga! (Bip!)\n[Stop - silence 2 seconds]\nLigou de novo! (Bip, bop!)",
    "Gostou do robô? (Gostei!)", "Robô dançarino! Tchau! (Bip!)", ponte_tag="robotic, kids freeze and move"),
  cenas=[("verso 1", "o Luisinho acha um botão no quarto e aperta: o Luisinho vira um robô (antenas piscando)"),
         ("refrão", "dança de robô: braço duro, perna dura, vira e trava; luzinhas piscando no fundo"),
         ("verso 2", "a pilha acaba: os movimentos ficam lentos até ele desligar; a Laurinha encaixa uma pilha gigante e ele religa"),
         ("ponte", "liga, trava, liga… a música para e ele fica parado… e liga de novo!"),
         ("final", "convite; o robô acena duro no tchau")],
  yt=("ROBÔ DANÇARINO! 🤖 O Luisinho achou um botão, apertou… e virou robô! Braço duro, perna dura, vira, vira… trava! Ih, a pilha tá acabando: devagar… desligou! Recarrega e liga de novo: bip, bop! Dance de robô com a Laurinha e o Luisinho!",
      "ROBÔ DANÇARINO! 🤖 Bip, bop! Dance de robô com a Laurinha e o Luisinho!", "O robô precisa de energia (pilha ou bateria) para funcionar, igual a gente precisa de comida")))

# 6 — Gelatina!
S.append(dict(slug="gelatina", titulo="Gelatina!", ritmo="reggae_infantil", tipo="danca", estrutura="R", v1="laurinha",
  gancho="gelatina", palavras=["gelatina", "treme", "mole", "dura"], tema="tremer como gelatina, ficar mole e ficar dura",
  curiosidade="a gelatina fica durinha na geladeira e amolece no calor",
  letra=montar("[Intro - reggae skank guitar]\nGelatina! (Treme, treme!)",
    verso("laurinha", ["Sobremesa da vovó! (Oba!)", "Vermelhinha… (Hum!)", "Bate na mesa… (Tum!)", "Gelatina tremendo! (Ha ha!)"]),
    d2("Gelatina! (Treme, treme!)\nTreme o corpo todo! (Treme!)\nGelatina! (Treme, treme!)\nDerreteu no chão! (Splash!)"), None,
    verso("luisinho", ["Na geladeira… (Brrr!)", "Ficou durinha! (Dura!)", "Lá no sol… (Ui!)", "Ficou molinha! (Mole!)"]),
    "Fica dura! (Dura!)\nFica mole! (Mole!)\nDura! (Dura!)\nMole! (Mole!)\nTreme tudo! (Treme, treme!)",
    "Gostou da gelatina? (Gostei!)", "Gelatina! Tchau! (Treme!)", ponte_tag="kids go stiff and floppy"),
  cenas=[("verso 1", "cozinha da vovó: uma gelatina vermelha gigante (para eles) com carinha; a Laurinha bate na mesa e ela treme"),
         ("refrão", "todos tremem como gelatina e se derretem no chão (splash)"),
         ("verso 2", "a gelatina vai à geladeira (Brrr, fica dura) e ao sol (fica molinha); os dois imitam"),
         ("ponte", "dura (estátua reta) / mole (corpo mole) cada vez mais rápido, e treme tudo"),
         ("final", "convite; a gelatina treme no tchau")],
  yt=("GELATINA! 🍮 Sobremesa da vovó: bate na mesa e a gelatina treme, treme! Treme o corpo todo… e derreteu no chão! Na geladeira ela fica durinha, no sol fica molinha. Fica dura, fica mole, dura, mole… treme tudo!",
      "GELATINA! 🍮 Treme, treme com a Laurinha e o Luisinho!", "A gelatina fica durinha na geladeira e amolece no calor")))

# 7 — Espelho, Espelhinho
def esp(a, ra, b, rb):
    return f"Espelho, espelhinho! (Faz igual!)\n{a} ({ra})\nEspelho, espelhinho! (Faz igual!)\n{b} ({rb})"
S.append(dict(slug="espelho_espelhinho", titulo="Espelho, Espelhinho", ritmo="disco_infantil", tipo="brincadeira", estrutura="B", v1="luisinho",
  gancho="espelho espelhinho", palavras=["espelho", "igual", "copiar", "careta"], tema="brincadeira de imitar o amigo como num espelho",
  curiosidade="no espelho a mão direita parece a esquerda: tudo fica trocadinho",
  letra=montar("[Intro - disco strings and four-on-the-floor]\nEspelho, espelhinho! (Faz igual!)",
    verso("luisinho", ["Eu faço assim… (Assim!)", "Você faz igual! (Igual!)", "Eu sou o espelho… (Hein?)", "Do meu amigo! (Ê!)"]),
    esp("Mão pra cima!", "Pra cima!", "Uma voltinha!", "Volta!") + "\n" + esp("Pula num pé!", "Pulei!", "Faz careta!", "Blé!"), None,
    verso("laurinha", ["Agora troca! (Troca!)", "Você faz… (O quê?)", "E eu copio! (Copio!)", "Ih, errei! (Ha ha!)"]),
    "Faz careta! (Blé!)\nPisca o olho! (Pisca!)\nMostra a língua! (Blé!)\nE ri! (Ha ha!)",
    "Gostou da brincadeira? (Gostei!)", "Espelho, espelhinho! Tchau! (Tchau!)",
    ref2=esp("Bate palma!", "Plá, plá!", "Abraço em você!", "Abraço!") + "\n" + esp("Mão no nariz!", "Bip!", "Pulinho!", "Pulei!"),
    ref_final=esp("Mão pra cima!", "Pra cima!", "Dá tchauzinho!", "Tchau!") + "\n" + esp("Pula num pé!", "Pulei!", "Faz careta!", "Blé!"),
    ponte_tag="silly faces, kids copy"),
  cenas=[("verso 1", "quarto com um espelho grande: o Luisinho de um lado, o reflexo (a Laurinha) do outro, fazendo igual"),
         ("refrão", "cada comando é feito pelos dois ao mesmo tempo, espelhados; a câmera convida a criança a fazer junto"),
         ("verso 2", "agora a Laurinha copia, mas erra de lado (ha ha): no espelho tudo fica trocado"),
         ("ponte", "concurso de caretas no espelho: careta, piscadinha, língua e gargalhada"),
         ("final", "convite; os dois dão tchau um para o outro pelo espelho")],
  yt=("ESPELHO, ESPELHINHO! 🪞 Eu faço assim, você faz igual! Mão pra cima, uma voltinha, pula num pé, faz careta… Agora troca: a Laurinha copia o Luisinho… ih, errou! No espelho tudo fica trocadinho. Faça igual junto com eles!",
      "ESPELHO, ESPELHINHO! 🪞 Faça igual com a Laurinha e o Luisinho!", "No espelho a mão direita parece a esquerda: tudo fica trocadinho")))

# 8 — Bolha de Sabão
S.append(dict(slug="bolha_de_sabao", titulo="Bolha de Sabão", ritmo="pop_infantil", tipo="brincadeira", estrutura="R", v1="laurinha",
  gancho="bolha de sabão", palavras=["bolha", "sabão", "assopra", "estourou"], tema="fazer bolhas de sabão que voam e estouram",
  curiosidade="a bolha de sabão brilha com as cores do arco-íris",
  letra=montar("[Intro - bright synths and handclaps]\nBolha de sabão! (Ploc!)",
    verso("laurinha", ["Água com sabão… (Mexe!)", "Assopra devagar… (Fuuu…)", "Nasceu uma bolha! (Uau!)", "Bolha de sabão! (Brilha!)"]),
    d2("Bolha de sabão! (Fuuu…)\nVoa, voa, voa! (Voa!)\nBolha de sabão! (Fuuu…)\nEstourou! (Ploc!)"), None,
    verso("luisinho", ["Olha o arco-íris (Uau!)", "Dentro da bolha! (Colorida!)", "Pousou no nariz… (Hein?)", "Ploc! (Ha ha!)"]),
    "Assopra fraquinho… (Fuuu…)\nBolha gigante! (Uau!)\nAssopra bem forte… (FUUU!)\nMil bolhinhas! (Ploc, ploc, ploc!)",
    "Gostou da bolha? (Gostei!)", "Bolha de sabão! Tchau! (Ploc!)", ponte_tag="soft then strong blowing"),
  cenas=[("verso 1", "quintal: a Laurinha mexe a água com sabão e assopra; nasce uma bolha brilhante"),
         ("refrão", "bolhas enormes (para eles) voando; os dois pulam e estouram (ploc!)"),
         ("verso 2", "dentro da bolha aparece um arco-íris; uma bolha pousa no nariz do Luisinho e estoura"),
         ("ponte", "assopra fraquinho: bolha gigante; assopra forte: mil bolhinhas pela tela"),
         ("final", "convite; chuva de bolhinhas no tchau")],
  yt=("BOLHA DE SABÃO! 🫧 Água com sabão, assopra devagar… nasceu uma bolha! Voa, voa, voa… ploc, estourou! Olha o arco-íris dentro da bolha! Assopra fraquinho: bolha gigante! Assopra forte: mil bolhinhas!",
      "BOLHA DE SABÃO! 🫧 Assopra e estoura as bolhas com a Laurinha e o Luisinho!", "A bolha de sabão brilha com as cores do arco-íris")))

# 9 — Dança da Minhoca
S.append(dict(slug="danca_da_minhoca", titulo="Dança da Minhoca", ritmo="forro_piseiro", tipo="animal", estrutura="A", v1="luisinho",
  gancho="dança da minhoca", palavras=["minhoca", "terra", "estica", "encolhe"], tema="a minhoca que estica, encolhe, se enrola e some na terra",
  curiosidade="a minhoca cava caminhos na terra e deixa a terra fofinha para as plantas",
  letra=montar("[Intro - sanfona and electronic kick]\nDança da minhoca! (Mexe, mexe!)",
    verso("luisinho", ["Choveu no jardim… (Plic, ploc!)", "Saiu da terra… (Hein?)", "Comprida, comprida… (Uau!)", "É a minhoca! (Oi!)"]),
    d2("Dança da minhoca! (Mexe, mexe!)\nEstica e encolhe! (Estica!)\nDança da minhoca! (Mexe, mexe!)\nSe enrola e some! (Cadê?)"), None,
    verso("laurinha", ["Ela cava a terra… (Cava!)", "Faz caminhozinho… (Uau!)", "A terra fica fofinha… (Fofinha!)", "E a planta cresce! (Cresceu!)"]),
    "Deita no chão! (Deitei!)\nEstica, estica! (Estica!)\nEncolhe! (Encolhi!)\nAchou! (Achou!)",
    "Gostou da minhoca? (Gostei!)", "Dança da minhoca! Tchau! (Mexe!)", ponte_tag="kids wiggle on the floor"),
  cenas=[("verso 1", "jardim depois da chuva visto de pertinho: uma minhoca rosa simpática sai da terra, comprida como um trem para eles"),
         ("refrão", "a minhoca dança: estica, encolhe, se enrola e some num buraquinho (cadê?) e aparece de novo"),
         ("verso 2", "corte da terra (quadro): a minhoca cava caminhos, a terra fica fofinha e uma plantinha cresce"),
         ("ponte", "os dois deitados no chão imitando a minhoca: estica, encolhe… achou!"),
         ("final", "convite; a minhoca acena com a pontinha")],
  yt=("DANÇA DA MINHOCA! 🪱 Choveu no jardim e saiu da terra… comprida, comprida: é a minhoca! Estica e encolhe, se enrola e some… cadê? Ela cava a terra, deixa tudo fofinho e a plantinha cresce! Deita no chão e dança junto!",
      "DANÇA DA MINHOCA! 🪱 Estica e encolhe com a Laurinha e o Luisinho!", "A minhoca cava caminhos na terra e deixa a terra fofinha para as plantas")))

# 10 — Quente ou Frio?
QF = "Quente ou frio? (Hein?)\nQue calor! (Ufa, ufa!)\nQuente ou frio? (Hein?)\nQue frio! (Brrr!)"
S.append(dict(slug="quente_ou_frio", titulo="Quente ou Frio?", ritmo="samba_infantil", tipo="brincadeira", estrutura="D", v1="laurinha",
  gancho="quente ou frio", palavras=["quente", "frio", "calor", "treme"], tema="se abanar no calor e tremer no frio, alternando cada vez mais rápido",
  curiosidade="quando faz frio a gente treme, e tremer esquenta o corpo",
  letra=montar("[Intro - cavaquinho and pandeiro]\nQuente ou frio? (Hein?)",
    verso("laurinha", ["Que calor! (Ufa!)", "Abana, abana! (Abana!)", "Que frio! (Brrr!)", "Quente ou frio? (Treme!)"]),
    d2(QF), None,
    verso("luisinho", ["No calor: sorvete! (Hum!)", "No frio: casaco! (Quentinho!)", "E na praia? (Calor!)", "E no gelo? (Brrr!)"]),
    "Calor! (Ufa!)\nFrio! (Brrr!)\nCalor! (Ufa!)\nFrio! (Brrr!)\n[Stop - silence 2 seconds]\nMorninho… (Ah, bom!)",
    "Gostou da brincadeira? (Gostei!)", "Quente ou frio? Tchau! (Brrr!)",
    ref2="[Faster]\n" + d2(QF), ref_final="[Very fast]\n" + QF + "\nQuente ou frio? (Hein?)\nMorninho! (Ah, bom!)", ponte_tag="faster and faster, with a trick"),
  cenas=[("verso 1", "a Laurinha num sol de rachar (suor, se abana) e de repente neve (treme, dentes batendo)"),
         ("refrão", "o fundo alterna sol e neve na batida; os dois se abanam no calor e tremem no frio, cada vez mais rápido"),
         ("verso 2", "calor: sorvete; frio: casaco; praia: calor; gelo com pinguim: brrr"),
         ("ponte", "calor, frio, calor, frio… a música para: morninho! (ah, bom!)"),
         ("final", "convite; os dois de casaco e óculos de sol ao mesmo tempo no tchau")],
  yt=("QUENTE OU FRIO? ☀️❄️ Que calor! Abana, abana! Que frio! Brrr, treme! A brincadeira vai alternando cada vez mais rápido… até ficar morninho! No calor: sorvete; no frio: casaco. Sabia que tremer esquenta o corpo?",
      "QUENTE OU FRIO? ☀️❄️ Abana no calor e treme no frio com a Laurinha e o Luisinho!", "Quando faz frio a gente treme, e tremer esquenta o corpo")))


def criar(s):
    d = next(M.glob(f"*_{s['slug']}"), None)
    if d is None:
        r = subprocess.run([str(ROOT / ".venv/bin/python"), "-m", "toonstudio.cli", "musica", "nova", s["slug"], "--titulo", s["titulo"],
                            "--ritmo", s["ritmo"], "--tipo", s["tipo"], "--estrutura", s["estrutura"]],
                           cwd=ROOT, env={"PYTHONPATH": str(ROOT), "PATH": "/usr/bin:/bin"}, capture_output=True, text=True, check=True)
        d = Path(r.stdout.strip().splitlines()[-1])
    (d / "letra.txt").write_text(s["letra"], encoding="utf-8")
    fp = d / "ficha.json"
    f = json.loads(fp.read_text(encoding="utf-8"))
    f.update({"gancho": s["gancho"], "palavras_tema": s["palavras"], "tema": s["tema"], "curiosidade": s["curiosidade"],
              "alternativas": [], "status": "letra_revisada", "estrutura": s["estrutura"],
              "cantam": {"verso 1": s["v1"], "refrão": "coro", "verso 2": OUT[s["v1"]], "ponte": "comandos, coro responde", "final": "todo mundo"},
              "cenas": [{"parte": a, "ideia": b} for a, b in s["cenas"]],
              "youtube": {"resumo": s["yt"][0], "resumo_short": s["yt"][1], "curiosidade": s["yt"][2]},
              "origem": "brincadeiras com o corpo (18/11/2026), inspiradas no gênero de No Ritmo Quá Quá / Morto-Vivo — nada copiado"})
    if s["v1"] == "luisinho":
        f["persona"] = "luisinho"
    fp.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return d


if __name__ == "__main__":
    for s in S:
        print(criar(s).name)
