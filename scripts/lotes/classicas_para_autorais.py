"""As cantigas tradicionais viram músicas autorais (18/11/2026).

O Suno bloqueou a letra tradicional da Borboletinha e do Carneirinho ("copyrighted material"); decisão do usuário:
converter todas as clássicas em autorais com o mesmo tema, ritmo e cenas, sem nenhum verso tradicional.
Uso: .venv/bin/python scripts/lotes/classicas_para_autorais.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lotes.revisao_auditoria import montar  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "musicas"


def dobra(b):
    return b + "\n" + b


def mandou(cmd, resp):
    return (f"Méé, carneirinho! (Méé!)\nMéé, carneirinho! (Méé!)\nO carneirinho mandou… (O quê?)\nTodo mundo {cmd}! ({resp}!)")


S = {}

S["12"] = dict(slug="mee_carneirinho", titulo="Méé, Carneirinho!", gancho="méé carneirinho", estrutura="D",
  palavras=["carneirinho", "méé", "lã", "mandou"], tema="brincadeira de \"o carneirinho mandou\" com comandos",
  curiosidade="a lã do carneirinho vira blusinha quentinha de frio",
  letra=montar("[Intro - batucada drums and whistle]\nMéé, carneirinho! (Méé!)",
    "[Verse - Laurinha, girl child vocal]\nLá no campo (Olha!)\nTem um carneirinho! (Méé!)\nBranquinho de algodão…\nEle quer brincar! (Bora!)",
    mandou("pular", "Pulei") + "\n" + mandou("sentar", "Sentei"), None,
    "[Verse - Luisinho, boy child vocal]\nBrrr, que friozinho! (Brrr!)\nA lã do carneirinho\nVira blusinha! (Blusinha!)\nQuentinha, quentinha! (Hum!)",
    "Gira, gira! (Gira!)\nBate palma! (Plá, plá!)\nFaz méé! (Méé!)\n[Stop - silence 2 seconds]\nCongelou! (Estátua!)",
    "Gostou da brincadeira? (Gostei!)", "Méé, carneirinho! Tchau! (Méé!)",
    ref2=mandou("girar", "Girei") + "\n" + mandou("abaixar", "Abaixei"), ref_final=mandou("dançar", "Dancei") + "\n" + mandou("pular", "Pulei")),
  cenas=[("intro", "campo visto de pertinho: um carneirinho fofo como nuvem pula na tela no \"Méé!\""),
         ("verso 1", "o carneirinho chama a turma para brincar de \"o carneirinho mandou\""),
         ("refrão", "a cada \"o carneirinho mandou…\" um comando novo e todos fazem: pular, sentar, girar, abaixar, dançar"),
         ("verso 2", "vento frio (Brrr!): a lã do carneirinho vira uma blusinha quentinha que a Laurinha veste"),
         ("ponte", "gira, palma, 'méé' e a música para: estátua"), ("final", "convite; o carneirinho de blusinha dá tchau")],
  yt=("MÉÉ, CARNEIRINHO! 🐑 Lá no campo tem um carneirinho que quer brincar: o carneirinho mandou… todo mundo pular! Sentar! Girar! Abaixar! Dançar! Brrr, que friozinho: a lã do carneirinho vira blusinha quentinha. Gira, bate palma, faz méé… estátua!",
      "MÉÉ, CARNEIRINHO! 🐑 O carneirinho mandou… brinque com a Laurinha e o Luisinho!", "A lã do carneirinho vira blusinha quentinha de frio"))


def vantagem(pergunta, verdade):
    return f"Dona Barata (Oi!)\nConta vantagem! (Conta!)\n{pergunta} (Mentira!)\n{verdade} (Ha ha!)"


S["15"] = dict(slug="conta_vantagem", titulo="Conta Vantagem!", gancho="conta vantagem", estrutura="B",
  palavras=["barata", "vantagem", "mentira", "verdade"], tema="a Dona Barata que conta vantagem, e a mentirinha de perna curta",
  curiosidade="a barata existe desde antes dos dinossauros",
  letra=montar("[Intro - bright guitar riff and drums]\nConta vantagem! (Ha ha!)",
    "[Verse - Luisinho, boy child vocal]\nChegou a Dona Barata (Oi!)\nToda arrumadinha!\nOlha o nariz em pé… (Hum!)\nLá vem mentirinha! (Ih!)",
    dobra(vantagem("Tem mil sapatos?", "Tem um só!")), None,
    "[Verse - Laurinha, girl child vocal]\nMentirinha, mentirinha… (Ih!)\nTem perna curtinha! (Curtinha!)\nTropeçou! (Ops!)\nFala a verdade! (Verdade!)",
    "Faz pose de chique! (Hum!)\nNariz em pé! (Hum!)\nTropeça! (Ops!)\nE ri de si mesma! (Ha ha!)",
    "Gostou da barata? (Gostei!)", "Conta vantagem! Tchau! (Ha ha!)",
    ref2=dobra(vantagem("Mora num castelo?", "Mora num buraquinho!")),
    ref_final="Dona Barata (Oi!)\nConta vantagem! (Conta!)\nFala a verdade? (Verdade!)\nÉ mais bonito! (Ê!)\n" + vantagem("Tem mil sapatos?", "Tem um só!")),
  cenas=[("intro", "a Dona Barata (antenas com laço, sorriso; engraçada, não nojenta) entra fazendo pose"),
         ("verso 1", "nariz em pé, desfilando para a turma; a Laurinha e o Luisinho se olham: lá vem mentirinha"),
         ("refrão", "ela diz que tem mil sapatos e aparece com um só; diz que mora num castelo e é um buraquinho; a turma ri"),
         ("verso 2", "a mentirinha ganha perninhas curtas e tropeça; a Dona Barata fala a verdade e todos aplaudem"),
         ("ponte", "dança da barata: pose de chique, nariz em pé, tropeço e risada"), ("final", "convite; a Dona Barata ri de si mesma no tchau")],
  yt=("CONTA VANTAGEM! 🪳😄 Chegou a Dona Barata toda arrumadinha… e contando vantagem! Diz que tem mil sapatos? Mentira, tem um só! Diz que mora num castelo? Mora num buraquinho! A mentirinha tem perna curtinha e tropeça: fala a verdade, que é mais bonito!",
      "CONTA VANTAGEM! 😄 A Dona Barata e a mentirinha de perna curta, com a Laurinha e o Luisinho!", "A barata existe desde antes dos dinossauros"))

S["18"] = dict(slug="roda_rodinha", titulo="Roda, Rodinha!", gancho="roda rodinha", estrutura="R",
  palavras=["roda", "mão", "amigos", "rodinha"], tema="roda de amigos de mãos dadas: ninguém fica de fora",
  curiosidade="na roda todo mundo dá a mão e ninguém fica de fora",
  letra=montar("[Intro - sanfona and electronic kick]\nRoda, rodinha! (Roda!)",
    "[Verse - Laurinha, girl child vocal]\nChama a turminha! (Vem!)\nDá a mão! (A mão!)\nJoaninha, Formiguinha… (Oi!)\nLuisinho também! (Eu!)",
    dobra("Roda, rodinha! (Roda!)\nDá a mão, vem cá! (Vem!)\nRoda, rodinha! (Roda!)\nNinguém fica pra lá! (Ninguém!)"), None,
    "[Verse - Luisinho, boy child vocal]\nQuem entra no meio? (Eu!)\nFaz um passinho! (Assim!)\nVolta pra roda… (Voltei!)\nAgora é você! (Eu!)",
    "Pra frente! (Pra frente!)\nPra trás! (Pra trás!)\nMeia-volta! (Volta!)\nE abraço! (Abraço!)",
    "Gostou da roda? (Gostei!)", "Roda, rodinha! Tchau! (Zum!)", ponte_tag="Laurinha gives commands, kids answer"),
  cenas=[("verso 1", "jardim: a Laurinha chama a turma e todos dão as mãos, formando uma roda"),
         ("refrão", "a roda gira vista de cima (como uma flor); quem está de fora é chamado e entra"),
         ("verso 2", "cada um entra no meio da roda e faz um passinho; os outros imitam"),
         ("ponte", "pra frente, pra trás, meia-volta e abraço coletivo"), ("final", "convite; a roda dando tchau de mãos dadas")],
  yt=("RODA, RODINHA! 💃 Chama a turminha e dá a mão: a Laurinha, o Luisinho, a Joaninha e a Formiguinha fazem uma roda em que ninguém fica de fora! Quem entra no meio faz um passinho e todo mundo imita. Pra frente, pra trás, meia-volta… e abraço!",
      "RODA, RODINHA! 💃 Dá a mão e entra na roda com a Laurinha e o Luisinho!", "Na roda todo mundo dá a mão e ninguém fica de fora"))

S["21"] = dict(slug="careta_de_limao", titulo="Careta de Limão!", gancho="careta de limão", estrutura="R",
  palavras=["limão", "careta", "azedo", "limonada"], tema="o limoeiro da vovó, a careta de azedo e a limonada",
  curiosidade="limão azedo faz careta, e com água e um pouquinho de açúcar vira limonada",
  letra=montar("[Intro - cavaquinho and pandeiro]\nCareta de limão! (Aaai!)",
    "[Verse - Laurinha, girl child vocal]\nNo quintal da vovó (Oi, vovó!)\nTem limão no pé!\nVerdinho, cheiroso… (Hum!)\nMorde pra ver! (Aaai!)",
    dobra("Careta de limão! (Aaai!)\nAzedinho, azedão! (Aaai!)\nMorde e faz careta…\nHa ha ha! (Ha ha!)"), None,
    "[Verse - Luisinho, boy child vocal]\nCareta de azedo! (Aaai!)\nCareta de doce! (Hum!)\nCareta de azedo! (Aaai!)\nQuem fez a maior? (Eu!)",
    "Espreme! (Espreme!)\nMexe! (Mexe!)\nUm golinho… (Hum!)\nLimonada da vovó! (Ê!)",
    "Gostou do limão? (Gostei!)", "Careta de limão! Tchau! (Aaai!)", ponte_tag="kids follow"),
  cenas=[("verso 1", "quintal da vovó com limoeiro gigante (para eles); a Laurinha morde o limão"),
         ("refrão", "close nas caretas de azedo, uma maior que a outra; a turma ri"),
         ("verso 2", "concurso de caretas: azedo (enorme), doce (sorriso), azedo de novo; quem fez a maior?"),
         ("ponte", "espreme, mexe, golinho: a limonada da vovó"), ("final", "convite; a vovó e os dois brindando limonada")],
  yt=("CARETA DE LIMÃO! 🍋 No quintal da vovó tem limão no pé… morde pra ver: aaai! Azedinho, azedão: careta de limão! Quem faz a maior careta? Depois a vovó espreme, mexe e… limonada! Um golinho: hum!",
      "CARETA DE LIMÃO! 🍋 Azedinho, azedão: faça careta com a Laurinha e o Luisinho!", "Limão azedo faz careta, e com água e um pouquinho de açúcar vira limonada"))

S["24"] = dict(slug="chule_de_sapo", titulo="Chulé de Sapo!", gancho="que chulé", estrutura="A",
  palavras=["sapo", "pé", "chulé", "lagoa"], tema="o sapo de pé fedido e a hora de lavar o pé no banho",
  curiosidade="o sapo bebe água pela pele, mas o nosso pezinho precisa de sabão no banho",
  letra=montar("[Intro - sanfona and electronic kick]\nEca, que chulé! (Eca!)",
    "[Verse - Luisinho, boy child vocal]\nLá na lagoa (Olha!)\nMora o sapo! (Croac!)\nIh, que cheirinho… (Eca!)\nOlha o pezinho! (Ih!)",
    dobra("Eca, que chulé! (Eca!)\nÉ o pé do sapo! (Croac!)\nEca, que chulé! (Eca!)\nLava esse pé! (Esfrega!)"), None,
    "[Verse - Laurinha, girl child vocal]\nO sapo bebe água (Glub!)\nPela pele! (Pela pele!)\nMas o pezinho? (Hein?)\nSabão no banho! (Sabão!)",
    "Lava o pé! (Esfrega!)\nEntre os dedinhos! (Cosquinha!)\nSeca bem! (Sequinho!)\nE o chulé? (Sumiu!)",
    "Gostou do sapinho? (Gostei!)", "Que chulé! Tchau! (Croac!)", ponte_tag="kids follow the commands"),
  cenas=[("verso 1", "lagoa: o sapo na vitória-régia; nuvenzinha verde de cheirinho sai do pé dele; o Luisinho tampa o nariz"),
         ("refrão", "o sapo dança forró de pé levantado; no \"eca, que chulé!\" todos tampam o nariz"),
         ("verso 2", "gotinhas brilhando entrando pela pele do sapo; depois banheiro: sabão com carinha e o pé com espuma"),
         ("ponte", "lava o pé com espuma, cosquinha entre os dedinhos, toalha, e a nuvem de chulé some"),
         ("final", "convite; o sapo de pé limpinho dá tchau")],
  yt=("CHULÉ DE SAPO! 🐸 Lá na lagoa mora o sapo… ih, que cheirinho! Eca, que chulé: é o pé do sapo! O sapo bebe água pela pele, mas o nosso pezinho precisa de sabão na hora do banho. Esfrega, cosquinha entre os dedinhos, seca bem… e o chulé sumiu!",
      "CHULÉ DE SAPO! 🐸 Eca, que chulé! Lava o pé com a Laurinha e o Luisinho!", "O sapo bebe água pela pele, mas o nosso pezinho precisa de sabão no banho"))


def canoa(quem):
    return f"Canoa de papel! (Rema!)\nBalança, balança… (Opa!)\nCanoa de papel! (Rema!)\nIh, {quem} caiu! (Splash!)"


S["27"] = dict(slug="canoa_de_papel", titulo="Canoa de Papel", gancho="canoa de papel", estrutura="R",
  palavras=["canoa", "papel", "remar", "laguinho"], tema="canoa de papel no laguinho do parque, e cuidado na água",
  curiosidade="quem tem asinha não afunda; e na água a gente brinca sempre com o papai e a mamãe",
  letra=montar("[Intro - sanfona and soft zabumba]\nCanoa de papel! (Rema!)",
    "[Verse - Luisinho, boy child vocal]\nDobra o papel… (Dobra!)\nDobra de novo… (Dobra!)\nVirou canoa! (Canoa!)\nBora remar! (Bora!)",
    canoa("a Laurinha"), None,
    "[Verse - Laurinha, girl child vocal]\nMas quem tem asinha (Zum!)\nNão afunda, não! (Não!)\nNa água, turminha… (Hein?)\nSó com papai e mamãe! (Só com eles!)",
    "Rema pra frente! (Rema!)\nBalança pra lá! (Pra lá!)\nBalança pra cá! (Pra cá!)\nE não caiu! (Ufa!)",
    "Gostou da canoa? (Gostei!)", "Canoa de papel! Tchau! (Splash!)", ref2=canoa("o Luisinho"), ref_final=canoa("a turminha"),
    ponte_tag="kids row and balance"),
  cenas=[("verso 1", "laguinho do parque visto de pertinho: o Luisinho dobra um papel que vira canoa"),
         ("refrão", "a canoa balança e alguém cai na água (splash); a cada volta cai um: Laurinha, Luisinho, a turminha"),
         ("verso 2", "quem tem asinha sai voando, sequinho; a família na beira: na água só com o papai e a mamãe"),
         ("ponte", "remar e equilibrar: pra lá, pra cá, e desta vez ninguém caiu"), ("final", "convite; a turma toda na canoa de papel dá tchau")],
  yt=("CANOA DE PAPEL! 🛶 Dobra o papel, dobra de novo… virou canoa! Bora remar? Balança, balança… ih, a Laurinha caiu! Splash! Mas quem tem asinha não afunda. E na água, turminha, só com o papai e a mamãe! Rema pra frente, balança pra lá e pra cá… e não caiu!",
      "CANOA DE PAPEL! 🛶 Rema e balança com a Laurinha e o Luisinho!", "Quem tem asinha não afunda; e na água a gente brinca sempre com o papai e a mamãe"))

S["30"] = dict(slug="blub_blub_peixinho", titulo="Blub, Blub, Peixinho!", gancho="blub blub peixinho", estrutura="E",
  palavras=["peixinho", "saudade", "amigo", "água"], tema="saudade do amigo que viajou, e a festa quando ele volta",
  curiosidade="o peixinho faz bolhinhas e nada com a nadadeira e o rabinho",
  letra=montar("[Intro - reggae skank guitar]\nBlub, blub, peixinho! (Blub!)",
    "[Verse - Luisinho, boy child vocal]\nA Laurinha viajou… (Ohh…)\nTô igual peixinho\nFora da água! (Ih!)\nToc, toc! (Quem é?)\nVoltou! (Voltou!)",
    dobra("Blub, blub, peixinho! (Blub!)\nNada, nada, nada! (Nada!)\nBlub, blub, peixinho! (Blub!)\nVoltou a alegria! (Ê!)"), None,
    "[Verse - Laurinha, girl child vocal]\nBoca de peixe! (Ó!)\nFaz bolhinha! (Blub!)\nNadadeira! (Mexe!)\nRabinho! (Balança!)",
    "Nada pra frente! (Nada!)\nNada de lado! (De lado!)\nMergulha… (Splash!)\nAbraço de amigo! (Abraço!)",
    "Gostou da história? (Gostei!)", "Blub, blub, peixinho! Tchau! (Blub!)", ponte_tag="kids swim"),
  cenas=[("verso 1", "o Luisinho sozinho olhando o aquário, igual peixinho fora da água; toc-toc: a Laurinha voltou com a mala"),
         ("refrão", "os dois nadam no ar como peixinhos, fazendo bolhinhas; o peixinho do aquário dança junto"),
         ("verso 2", "imitação do peixe: boca de peixe, bolhinha, nadadeira, rabinho"),
         ("ponte", "nadar pra frente, de lado, mergulho e abraço de amigos"), ("final", "convite; os dois e o peixinho do aquário dão tchau")],
  yt=("BLUB, BLUB, PEIXINHO! 🐟 A Laurinha viajou e o Luisinho ficou igual peixinho fora da água… toc, toc: ela voltou! Blub, blub, nada, nada: voltou a alegria! Faz boca de peixe, bolhinha, nadadeira e rabinho! Nada pra frente, de lado e abraço de amigo!",
      "BLUB, BLUB, PEIXINHO! 🐟 Nade com a Laurinha e o Luisinho!", "O peixinho faz bolhinhas e nada com a nadadeira e o rabinho"))


def ninho(n, resp):
    return f"Có-có-có! (Có!)\nOvinho no ninho! (Plim!)\nCó-có-có! (Có!)\nAgora são {n}! ({resp}!)"


S["33"] = dict(slug="ovinho_no_ninho", titulo="Ovinho no Ninho", gancho="ovinho no ninho", estrutura="F",
  palavras=["galinha", "ovinho", "ninho", "pintinho"], tema="contar os ovinhos da galinha e como nasce o pintinho",
  curiosidade="o pintinho nasce do ovo que a galinha choca, esquentando até ele bicar a casca",
  letra=montar("[Intro - viola caipira and country stomp]\nCó-có-có! Ovinho no ninho!",
    "[Verse - Laurinha, girl child vocal]\nBom dia, quintal! (Bom dia!)\nQuem tá cantando? (Có-có!)\nÉ a galinha! (Oi!)\nVamos contar? (Vamos!)",
    ninho("dois", "Dois") + "\n" + ninho("três", "Três"), None,
    "[Verse - Luisinho, boy child vocal]\nA galinha esquenta… (Choca!)\nChoca, choca, choca…\nToc, toc! (Rachou!)\nPiu, piu! Nasceu! (Nasceu!)",
    "Bate as asas! (Có-có!)\nCisca o chão! (Cisca!)\nAgachadinha… (Choca!)\nE pula! (Piu, piu!)",
    "Gostou da galinha? (Gostei!)", "Ovinho no ninho! Tchau! (Piu, piu!)",
    ref2=ninho("quatro", "Quatro") + "\n" + ninho("cinco", "Cinco"), ref_final=ninho("seis", "Seis") + "\n" + ninho("dez", "Dez"),
    ponte_tag="kids imitate the hen"),
  cenas=[("verso 1", "quintal visto de pertinho: a galinha gigante (para eles) no ninho de palha"),
         ("refrão", "a cada \"agora são…\" um ovinho novo aparece no ninho e o número gigante pula na tela"),
         ("verso 2", "a galinha choca, o ovo balança (toc, toc), racha e sai o pintinho (piu, piu!)"),
         ("ponte", "imitar a galinha: bate as asas, cisca o chão, agachadinho chocando e pula como pintinho"),
         ("final", "convite; a galinha e os pintinhos em fila dando tchau")],
  yt=("OVINHO NO NINHO! 🐔🥚 Bom dia, quintal! Quem tá cantando? É a galinha! Có-có-có, ovinho no ninho: agora são dois, três, quatro… até dez! E o pintinho? A galinha choca, choca, toc, toc… piu, piu, nasceu! Bate as asas, cisca o chão e pula!",
      "OVINHO NO NINHO! 🐔 Conte os ovinhos com a Laurinha e o Luisinho!", "O pintinho nasce do ovo que a galinha choca, esquentando até ele bicar a casca"))


def main():
    for n, s in S.items():
        d = next(M.glob(f"{n}_*"))
        novo = M / f"{n}_{s['slug']}"
        if d != novo:
            subprocess.run(["git", "mv", str(d), str(novo)], cwd=ROOT, check=True)
        (novo / "letra.txt").write_text(s["letra"], encoding="utf-8")
        fp = novo / "ficha.json"
        f = json.loads(fp.read_text(encoding="utf-8"))
        for k in ("dominio_publico", "miniatura_cena"):
            f.pop(k, None)
        yt = f.setdefault("youtube", {})
        yt.update({"resumo": s["yt"][0], "resumo_short": s["yt"][1], "curiosidade": s["yt"][2]})
        yt.pop("miniatura", None)
        f.update({"titulo": s["titulo"], "gancho": s["gancho"], "estrutura": s["estrutura"], "palavras_tema": s["palavras"],
                  "tema": s["tema"], "curiosidade": s["curiosidade"], "status": "letra_revisada",
                  "cenas": [{"parte": a, "ideia": b} for a, b in s["cenas"]],
                  "revisao": "clássica convertida em autoral 18/11/2026 (o Suno bloqueia letras tradicionais)"})
        f["cantam"]["refrão"] = "coro"
        f["tipo"] = f.get("tipo") if f.get("tipo") not in ("brincadeira",) else "brincadeira"
        fp.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(novo.name)


if __name__ == "__main__":
    main()
