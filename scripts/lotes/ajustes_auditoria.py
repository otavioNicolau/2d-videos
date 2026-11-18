"""Ajustes pequenos aprovados na auditoria (músicas Boas/Excelentes) — 17/11/2026."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lotes.revisao_auditoria import montar  # noqa: E402

M = Path(__file__).resolve().parents[2] / "musicas"


def pasta(n):
    return next(M.glob(f"{n}_*"))


def troca(n, pares, todas=False):
    p = pasta(n) / "letra.txt"
    s = p.read_text(encoding="utf-8")
    for a, b in pares:
        assert a in s, (n, a)
        s = s.replace(a, b) if todas else s.replace(a, b, 1)
    p.write_text(s, encoding="utf-8")


def ficha(n, **kw):
    p = pasta(n) / "ficha.json"
    f = json.loads(p.read_text(encoding="utf-8"))
    E = json.loads((M / "estilos.json").read_text(encoding="utf-8"))
    for k, v in kw.items():
        if k == "cenas_patch":
            for parte, ideia in v.items():
                for c in f["cenas"]:
                    if c["parte"] == parte:
                        c["ideia"] = ideia
        else:
            f[k] = v
    if "ritmo" in kw:
        f["bpm"] = E["ritmos"][kw["ritmo"]]["bpm"][2]
    f["revisao"] = "auditoria 17/11/2026 (ajuste pequeno)"
    p.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# 11 Foguete pra Lua — contagem antes de cada refrão; ritmo eletrônico
p = pasta("11") / "letra.txt"
s = p.read_text(encoding="utf-8")
s = s.replace("[Intro - sparkly synths countdown]", "[Intro - sparkly synths countdown, space sound effects]")
s = s.replace("Foguete pra lua! (Vruuum!)\nFoguete pra lua! (Vruuum!)\nCinto apertado,",
              "Três, dois, um… (Vruuum!)\nFoguete pra lua! (Vruuum!)\nFoguete pra lua! (Vruuum!)\nCinto apertado,")
p.write_text(s, encoding="utf-8")
ficha("11", ritmo="eletronica_infantil", alternativas=["pop_infantil"],
      cenas_patch={"refrão": "cada refrão começa com a contagem \"três, dois, um… vruuum!\" e a decolagem com fumaça colorida; passam estrelas com carinha e um cometa"})

# 12 Carneirinho — verso 1 mais curto; lã sem "Sabia que"
troca("12", [("Lá no campo (Olha!)\nTem um carneirinho! (Méé!)\nBranquinho, fofinho,\nIgual nuvenzinha!\nEle brinca de roda\nCom a turminha!\nCarneirinho, carneirão! (Méé!)\nBora brincar? (Bora!)",
              "Lá no campo (Olha!)\nTem um carneirinho! (Méé!)\nCarneirinho, carneirão! (Méé!)\nBora brincar? (Bora!)"),
             ("Sabia que a lã (Hein?)\nDo carneirinho (Méé!)", "E a lã do carneirinho? (Méé!)")])

# 13 Castelo de Areia — verso 2 vira o jogo do siri
troca("13", [("Sabia que a areia (Hein?)\nMolhadinha gruda? (Gruda!)\nSeca, ela escorre (Escorre!)\nPelo dedinho!\nE o siri? (Hein?)\nAnda de ladinho! (Ladinho!)",
              "Olha o siri! (Siri!)\nAnda de ladinho! (Ladinho!)\nBelisca o pé… (Ai!)\nSai correndo! (Ha ha!)")])
ficha("13", curiosidade="o siri anda de ladinho", cenas_patch={"verso 2": "um siri aparece andando de ladinho, belisca o pé do Luisinho (ai!) e sai correndo"})

# 16 Carnaval — grito de bloco antes do refrão; confete sem "Sabia que"
troca("16", [("[Virada]\n[Chorus - kids choir]", "[Shout - kids choir] Abre a roda que eu vou passar! (Passa!)\n[Virada]\n[Chorus - kids choir]")], todas=True)
troca("16", [("Sabia que o confete (Hein?)\nÉ papel picadinho? (Papel!)\nJoga pro alto, (Joga!)\nCai igual chuvinha!",
              "Pega o confete! (Peguei!)\nJoga pro alto! (Joga!)\nCaiu na cabeça… (Ih!)\nChuva de cor! (Ê!)")])

# 18 Ciranda — verso 2 sem aula
troca("18", [("Sabia que a ciranda (Hein?)\nÉ lá da praia? (Da praia!)\nLá em Pernambuco\nDançam de mãos dadas,\nPé pra frente,\nPé pra trás! (Assim!)\nRoda que roda\nAté o sol raiar!",
              "Gira, gira a roda! (Gira!)\nQuem entra no meio? (Eu!)\nPé pra frente,\nPé pra trás! (Assim!)")])
ficha("18", curiosidade="na roda todo mundo dá a mão e ninguém fica de fora",
      cenas_patch={"verso 2": "a roda gira e cada amigo entra no meio (\"Eu!\"); pé pra frente, pé pra trás"})

# 20 Polvo — contagem só na 1ª linha do refrão; o resto vira abraço de polvo
troca("20", [("Polvo de oito braços! (Oito!)\nUm, dois, três, quatro!\nCinco, seis, sete, oito!\nAbraça todo mundo! (Abraço!)",
              "Polvo de oito braços! (Oito!)\nAbraço de polvo! (Aperta!)\nAbraço de polvo! (Aperta!)\nAbraça todo mundo! (Abraço!)")], todas=True)

# 22 Bi-bi — refrão termina em som; a faixa vai para a ponte; sem "Sabia que" do ônibus
troca("22", [("Atravessa na faixa,\nDe mão dada\nCom o papai! (Ê!)", "Piuí! (Piuí!)\nVruum, vruum! (Vruum!)\nBi-bi, fom-fom! (Ê!)")], todas=True)
troca("22", [("Sabia que o ônibus da escola (Hein?)\nÉ amarelinho? (Amarelo!)\nPra ver de longe! (De longe!)", "E o ônibus da escola? (Fom, fom!)")])
troca("22", [("Bi-bi! (Fom-fom!)", "Atravessa na faixa! (Mão dada!)")])
ficha("22", curiosidade="no sinal vermelho a gente para, e atravessa na faixa de mão dada com um adulto")

# 23 Coelhinho — cenoura sem "Sabia que" (piada)
troca("23", [("Sabia que o coelho (Hein?)\nMexe o nariz (Tum, tum!)\nPra sentir cheirinho?\nE a cenoura? (Hum!)\nEle gosta mais\nDe capim e folhinha! (Folhinha!)",
              "Mexe o nariz… (Tum, tum!)\nSentiu cheirinho! (Hum!)\nE a cenoura? (Não quero!)\nCapim é melhor! (Ha ha!)")])

# 28 Tum-Tum — correção científica
troca("28", [("Ele leva o arzinho\nPro corpo inteiro! (Inteiro!)", "Ele leva o sangue\nPro corpo inteiro! (Inteiro!)")])
ficha("28", curiosidade="o coração é do tamanho da mão fechada e leva o sangue pro corpo inteiro")

# 31 Abelhinha — refrão sem frases de enchimento
troca("31", [("Abelhinha, abelhinha! (Zum, zum!)\nVoa de flor em flor!\nAbelhinha, abelhinha! (Zum, zum!)\nFaz o mel com amor!\nPega o docinho,\nLeva pra colmeia!\nAbelhinha, abelhinha! (Zum, zum!)\nTrabalha o dia inteiro!",
              "Abelhinha, abelhinha! (Zum, zum!)\nPousou na flor! (Pousou!)\nAbelhinha, abelhinha! (Zum, zum!)\nPegou o docinho! (Hum!)\nAbelhinha, abelhinha! (Zum, zum!)\nPousou na flor! (Pousou!)\nAbelhinha, abelhinha! (Zum, zum!)\nPegou o docinho! (Hum!)")], todas=True)

# 33 Galinha — ritmo sertanejo/country
troca("33", [("[Intro - samba-reggae drums]", "[Intro - viola caipira and country stomp]")])
ficha("33", ritmo="sertanejo_infantil", alternativas=["axe"],
      dominio_publico={**json.loads((pasta("33") / "ficha.json").read_text(encoding="utf-8"))["dominio_publico"],
                       "observacao": "estilo Sertanejo infantil (country) (diferente das versões conhecidas)"})

# 26 Banda — cumulativa
def banda(n):
    linhas = ["Tum, tum, faz o tambor! (Tum!)", "Fiu, fiu, faz a flauta! (Fiu!)", "Chique, chique, o chocalho! (Chique!)", "Plém, plém, o violão! (Plém!)"]
    return "Banda da turminha! (Ê!)\nBanda da turminha! (Ê!)\n" + "\n".join(linhas[:n]) + "\nMarchando pelo chão! (Ê!)"
txt = montar(
    "[Intro - brass band fanfare]\n(Tã-rã-rã! Zum, zum!)",
    "[Verse - Luisinho, boy child vocal]\nAchei um tambor! (Tum!)\nA Laurinha, a flauta! (Fiu!)\nBora montar\nUma banda? (Bora!)",
    banda(2), None,
    "[Verse - Laurinha, girl child vocal]\nE a Joaninha? (Chocalho!)\nE a Formiguinha? (Violão!)\nChegou mais gente! (Ê!)\nA banda cresceu! (Cresceu!)",
    "Tambor na barriga! (Tum, tum!)\nPalma na mão! (Plá, plá!)\nPé no chão! (Pá, pá!)\nAgora todo mundo! (Tã-rã-rã!)",
    "Gostou da banda? (Gostei!)", "Banda da turminha! Tchau! (Tã-rã!)", ref2=banda(3), ref_final=banda(4), ponte_tag="body percussion, kids follow")
(pasta("26") / "letra.txt").write_text(txt, encoding="utf-8")
ficha("26", estrutura="C", curiosidade="dá pra fazer música com o corpo: barriga, palma e pé",
      cenas=[{"parte": "verso 1", "ideia": "o Luisinho acha um tambor, a Laurinha uma flauta: começa a banda"},
             {"parte": "refrão", "ideia": "cumulativo: cada refrão soma um instrumento (tambor e flauta → +chocalho → +violão) e a banda marcha"},
             {"parte": "verso 2", "ideia": "a Joaninha chega com o chocalho e a Formiguinha com o violão: a banda cresce"},
             {"parte": "ponte", "ideia": "percussão com o corpo: barriga, palma e pé"}],
      youtube={**json.loads((pasta("26") / "ficha.json").read_text(encoding="utf-8"))["youtube"],
               "resumo": "BANDA DA TURMINHA! 🥁🎺 O Luisinho achou um tambor, a Laurinha uma flauta… bora montar uma banda? A cada refrão entra um instrumento: tum, tum, fiu, fiu, chique, chique, plém, plém! A Joaninha e a Formiguinha chegam e a banda cresce. Toca com a barriga, a palma e o pé!",
               "curiosidade": "Dá pra fazer música com o corpo: barriga, palma e pé"})
print("ajustes aplicados")
