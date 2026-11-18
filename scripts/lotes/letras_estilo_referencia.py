"""18/11/2026 — letras no jeito da referência (musicas/REFERENCIA_ANIMADINHOS.md), aprovado pelo usuário ("ajuste").

Regras: premissa engraçada · molde que troca uma palavra · rima em todo par de versos · o bloco repete igual (verso 2 = verso 1)
· UMA voz narrando (a Persona da música) · sem respostinha em todo verso · falar com a criança · lição só como piada.
- 14 Castelo de Areia reescrita (vai ser regravada).
- 6 temas "de lição" trocados por comida, humor e São João (São João cai em junho no calendário).
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

M = Path(__file__).resolve().parents[2] / "musicas"
E = json.loads((M / "estilos.json").read_text(encoding="utf-8"))
TAG = {"laurinha": "Laurinha, girl child vocal", "luisinho": "Luisinho, boy child vocal"}


def letra(intro_tag, gancho2, persona, verso, refrao, ponte, gostou, tchau, bordao=None, extra=False):
    """Bloco que volta: intro · verso · refrão · bordão+intervalo · ponte · verso (igual) · refrão · bordão+intervalo · ponte ·
    refrão forte · intervalo · convite (3 intervalos de dança, como a referência)."""
    v = f"[Verse - {TAG[persona]}]\n" + "\n".join(verso)
    r = "[Virada]\n[Chorus]\n" + "\n".join(refrao + refrao)
    rf = "[Virada]\n[Chorus - louder]\n" + "\n".join(refrao + refrao)
    if extra:                                    # música curta: mais uma volta do refrão no fim (referência: mediana 2:47)
        rf += "\n\n[Chorus - faster, everybody dancing]\n" + "\n".join(refrao + refrao)
    p = f"[Bridge - {persona.capitalize()} gives commands]\n" + "\n".join(ponte)
    b = bordao or persona
    outro = "luisinho" if persona == "laurinha" else "laurinha"
    convite = gostou.replace("? ", "?\n")
    grito = "Laurinha e Luisinho!"              # grito do canal (referência: 10 de 13 músicas, depois da intro e nas pausas)
    partes = [f"[Intro - {intro_tag}]\n" + "\n".join(gancho2) + f"\n{grito}", v, r, f"[Bordão {b}]\n{grito}\n[Intervalo 8s]", p, v, r,
              f"[Bordão {b}]\n{grito}\n[Intervalo 8s]", p, rf, "[Intervalo 6s]",
              f"[Outro - {persona.capitalize()} talks to the kids]\n{convite}\nChama o papai e a mamãe\nPra se inscrever no canal! Zum, zum!",
              f"[Outro - one big final hit, hard stop]\n{tchau}\n[End]"]
    return "\n\n".join(partes) + "\n"


def ficha_nova(base: dict, **kw) -> dict:
    f = dict(base)
    f.update(kw)
    f["bpm"] = E["ritmos"][f["ritmo"]]["bpm"][2]
    f["voz"] = f["persona"]
    f["status"] = "letra_revisada"
    f["versoes"] = []
    f["revisao"] = "18/11/2026: jeito da referência (premissa engraçada, molde, rima, bloco que volta, uma voz)"
    f.pop("dominio_publico", None)
    return f


SONGS = {}

# 14 — reescrita (axé, Laurinha)
SONGS["14"] = dict(
    pasta="14_castelo_de_areia", nova=False,
    letra=letra("bright keyboard riff and ocean waves", ["Castelo de areia! Zum, zum!", "Castelo de areia!"], "laurinha",
                ["Lá na praia tem areia,", "Tem baldinho e tem pazinha,", "Fiz um castelo tão grande,", "Maior que a minha casinha!",
                 "O siri chegou correndo:", "\"Esse castelo é meu!\"", "Subiu na torre mais alta", "E deu tchauzinho pro céu!"],
                ["Castelo de areia, ê!", "Torre, ponte e bandeira!", "Lá vem a onda… chuá!", "Derrubou a brincadeira!"],
                ["Quem quer brincar, cava o buraco!", "Quem quer pular, pula a ondinha!", "Quem é siri, anda de lado!",
                 "E quem é peixe, nada rapidinho!"],
                "Gostou do castelo? Dá um joinha!", "Castelo de areia! Tchau! Chuá!"),
    ficha=dict(persona="laurinha", estrutura="A",
               tema="o castelo de areia tão grande que o siri quis morar nele, e a onda que derruba tudo",
               cenas=[{"parte": "intro", "ideia": "a praia vista de pertinho; a Laurinha chega voando com o baldinho"},
                      {"parte": "verso 1", "ideia": "o castelo fica maior que a casinha dela; o siri chega correndo, sobe na torre e dá tchau"},
                      {"parte": "refrão", "ideia": "torre, ponte e bandeira… lá vem a onda (chuá!) e derruba tudo; todo mundo ri"},
                      {"parte": "ponte", "ideia": "comandos para quem assiste: cava o buraco, pula a ondinha, anda de lado igual siri, nada igual peixe"},
                      {"parte": "final", "ideia": "convite; o siri dá tchau de cima da torre (que a onda derruba no tchau)"}]))

SONGS["24"] = dict(  # curiosidade: o pão de queijo nasceu em Minas Gerais
    pasta="24_pao_de_queijo", velha="24_cara_de_que", nova=True,
    letra=letra("keyboard accordion riff, rooster crow", ["Pão de queijo, uai! Zum, zum!", "Pão de queijo!"], "luisinho",
                ["A vovó lá de Minas", "Fez um pão de queijo assim,", "Redondinho e quentinho,", "Do jeitinho que é pra mim!",
                 "Dei uma mordida grande,", "O queijo esticou, esticou,", "Foi parar lá no telhado,", "Passou a lua e voltou!"],
                ["Pão de queijo, uai, uai!", "Estica, estica e não sai!", "Pão de queijo, uai, uai!", "Mais um, vovó! Vai, vai!"],
                ["Estica pro lado!", "Estica pro outro!", "Estica lá pra cima!", "Nhac! Que delícia!"],
                "Gostou do pão de queijo? Dá um joinha!", "Pão de queijo! Tchau! Uai!"),
    ficha=dict(titulo="Pão de Queijo", gancho="pão de queijo", palavras_tema=["pão de queijo", "vovó", "estica", "uai"],
               tipo="comida", tema="o pão de queijo da vovó mineira que estica até a lua", ritmo="xote", persona="luisinho", estrutura="R",
               dia_a_dia=["lanche da tarde", "comida da vovó", "pão de queijo quentinho"], curiosidade="o pão de queijo nasceu em Minas Gerais",
               alternativas=["sertanejo_infantil"], cantam={"verso": "luisinho", "refrão": "luisinho", "ponte": "luisinho (comandos)"},
               cenas=[{"parte": "intro", "ideia": "a cozinha da vovó; a fornada sai fumegando do forno"},
                      {"parte": "verso 1", "ideia": "o Luisinho morde, o queijo estica até o telhado, passa pela lua e volta (cena absurda)"},
                      {"parte": "refrão", "ideia": "o queijo estica e não solta da boca do Luisinho; a vovó traz mais um"},
                      {"parte": "ponte", "ideia": "comandos: estica pro lado, pro outro, pra cima… nhac!"},
                      {"parte": "final", "ideia": "convite; a vovó e o Luisinho com a cesta de pão de queijo dando tchau"}],
               youtube={"resumo": "PÃO DE QUEIJO, UAI! 🧀 A vovó de Minas fez pão de queijo quentinho… o Luisinho deu uma mordida e o queijo esticou, esticou, passou pela lua e voltou! Estica pro lado, estica pro outro… nhac!",
                        "resumo_short": "PÃO DE QUEIJO, UAI! 🧀 Estica, estica com o Luisinho!", "curiosidade": ""},
               playlists=["Músicas Infantis da Laurinha e do Luisinho 🐝"]))

SONGS["33"] = dict(  # curiosidade: o brigadeiro foi inventado aqui no Brasil
    pasta="33_brigadeiro", velha="33_devagar_devagarinho", nova=True,
    letra=letra("bright piano and party horn", ["Brigadeiro! Zum, zum!", "Brigadeiro!"], "laurinha",
                ["Hoje é festa, parabéns,", "Tem balão e tem chapéu,", "Tem um prato de docinho", "Que parece vir do céu!",
                 "Mas na hora do parabéns,", "Olha só que desespero:", "O prato tá vazio…", "Sumiu o brigadeiro!"],
                ["Brigadeiro, brigadeiro!", "Quem comeu o brigadeiro?", "Brigadeiro, brigadeiro!", "Foi você? Fala primeiro!"],
                ["Foi o sapo? Não foi não!", "Foi a formiga? Não foi não!", "Foi o Luisinho? Foi, sim!", "Tem chocolate até no nariz!"],
                "Gostou da festa? Dá um joinha!", "Brigadeiro! Tchau! Nhac!"),
    ficha=dict(titulo="Brigadeiro", gancho="brigadeiro", palavras_tema=["brigadeiro", "festa", "parabéns", "quem comeu"],
               tipo="comida", tema="o brigadeiro que sumiu da festa: quem comeu?", ritmo="latino_infantil", persona="laurinha", estrutura="R",
               dia_a_dia=["festa de aniversário", "docinho", "parabéns pra você"], curiosidade="o brigadeiro foi inventado aqui no Brasil", alternativas=["pagodao"],
               cantam={"verso": "laurinha", "refrão": "laurinha", "ponte": "laurinha (pergunta para quem assiste)"},
               cenas=[{"parte": "intro", "ideia": "festa de aniversário: balões, chapéus e o prato cheio de brigadeiro"},
                      {"parte": "verso 1", "ideia": "na hora do parabéns, o prato está vazio! cara de susto geral"},
                      {"parte": "refrão", "ideia": "a Laurinha detetive com lupa pergunta para cada um (e para quem assiste)"},
                      {"parte": "ponte", "ideia": "o sapo? não. a formiga? não. o Luisinho? sim! nariz e bochecha sujos de chocolate"},
                      {"parte": "final", "ideia": "convite; o Luisinho ri com a boca de chocolate e oferece o último brigadeiro"}],
               youtube={"resumo": "BRIGADEIRO! 🍫 Hoje é festa, tem balão e chapéu… mas na hora do parabéns o prato está vazio! Quem comeu o brigadeiro? Foi o sapo? Não! Foi a formiga? Não! Foi o Luisinho… tem chocolate até no nariz!",
                        "resumo_short": "BRIGADEIRO! 🍫 Quem comeu? Descubra com a Laurinha!", "curiosidade": ""},
               playlists=["Músicas Infantis da Laurinha e do Luisinho 🐝"]))

SONGS["37"] = dict(  # curiosidade: na quadrilha, 'anarriê' quer dizer 'para trás'
    pasta="37_quadrilha_da_turminha", velha="37_canoa_de_papel", nova=True,
    letra=letra("keyboard accordion and triangle, festa junina", ["Quadrilha da turminha! Zum, zum!", "Quadrilha da turminha!"], "luisinho",
                ["Chegou o mês de junho,", "Bandeirinha no varal,", "Chapéu de palha na cabeça,", "Hoje é festa no quintal!",
                 "O sapo tirou a joaninha,", "O grilo tirou a formiga,", "E quem vai puxar a dança", "Sou eu, que alegria!"],
                ["Quadrilha da turminha!", "Balancê, balancê!", "Quadrilha da turminha!", "Olha a chuva! É mentira, ê!"],
                ["Olha a cobra! É mentira!", "Caminho da roça, vai!", "Anarriê, todo mundo gira…", "E o sapo escorregou e cai!"],
                "Gostou da quadrilha? Dá um joinha!", "Quadrilha da turminha! Tchau! Iuhu!"),
    ficha=dict(titulo="Quadrilha da Turminha", gancho="quadrilha da turminha", palavras_tema=["quadrilha", "junho", "balancê", "anarriê"],
               tipo="festa", tema="a quadrilha de São João da turminha, com o sapo atrapalhado", ritmo="forro_pe_de_serra",
               persona="luisinho", estrutura="R", dia_a_dia=["festa junina", "quadrilha", "São João"], curiosidade="na quadrilha, 'anarriê' quer dizer 'para trás'",
               alternativas=["baiao"], cantam={"verso": "luisinho", "refrão": "luisinho", "ponte": "luisinho (marcador da quadrilha)"},
               cenas=[{"parte": "intro", "ideia": "quintal enfeitado: bandeirinhas, chapéus de palha, mesa de milho"},
                      {"parte": "verso 1", "ideia": "os pares se formam: sapo e joaninha, grilo e formiga; o Luisinho de marcador"},
                      {"parte": "refrão", "ideia": "balancê; 'olha a chuva!' todo mundo se encolhe… 'é mentira!'"},
                      {"parte": "ponte", "ideia": "olha a cobra (é mentira!), caminho da roça, anarriê… o sapo escorrega e cai, todo mundo ri"},
                      {"parte": "final", "ideia": "convite; a turma em fila dando tchau com o chapéu"}],
               youtube={"resumo": "QUADRILHA DA TURMINHA! 🌽🎉 Chegou junho: bandeirinha no varal, chapéu de palha e festa no quintal! O sapo dança com a joaninha, o grilo com a formiga… balancê! Olha a chuva! É mentira! Anarriê… e o sapo escorregou!",
                        "resumo_short": "QUADRILHA DA TURMINHA! 🌽 Balancê com o Luisinho!", "curiosidade": ""},
               playlists=["Músicas Infantis da Laurinha e do Luisinho 🐝"]))

SONGS["38"] = dict(  # curiosidade: a pamonha é feita de milho verde ralado e cozida dentro da palha do milho
    pasta="38_pamonha", velha="38_tum_tum_coracao", nova=True,
    letra=letra("keyboard accordion riff and street car horn", ["Olha a pamonha! Zum, zum!", "Olha a pamonha!"], "laurinha",
                ["Lá vem o carro da pamonha,", "Buzinando na rua inteira,", "Tem pamonha de queijo,", "Tem pamonha de primeira!",
                 "O milho veio da roça,", "A palha é o cobertor,", "Dá uma mordidinha…", "Hum, que delícia, que sabor!"],
                ["Olha a pamonha, pamonha!", "Quentinha, ê!", "Olha a pamonha, pamonha!", "Quem quer? Eu quero! Ê!"],
                ["Pamonha de queijo? Quero!", "Pamonha de doce? Quero!", "Pamonha de chocolate?", "Ninguém nunca viu… mas eu quero!"],
                "Gostou da pamonha? Dá um joinha!", "Olha a pamonha! Tchau! Hum!"),
    ficha=dict(titulo="Olha a Pamonha!", gancho="olha a pamonha", palavras_tema=["pamonha", "milho", "quero", "carro da pamonha"],
               tipo="comida", tema="o carro da pamonha passando na rua, e a pamonha de chocolate que ninguém nunca viu",
               ritmo="xote", persona="laurinha", estrutura="A", dia_a_dia=["festa junina", "milho verde", "comida de São João"],
               curiosidade="a pamonha é feita de milho verde ralado e cozida dentro da palha do milho", alternativas=["baiao"], cantam={"verso": "laurinha", "refrão": "laurinha", "ponte": "laurinha (pergunta e responde)"},
               cenas=[{"parte": "intro", "ideia": "a rua; o carrinho da pamonha buzinando (com corneta) vem chegando"},
                      {"parte": "verso 1", "ideia": "a pamonha embrulhada na palha como num cobertor; a Laurinha morde e derrete de alegria"},
                      {"parte": "refrão", "ideia": "a turma corre atrás do carrinho gritando 'eu quero!'"},
                      {"parte": "ponte", "ideia": "de queijo? quero! de doce? quero! de chocolate?! (pamonha marrom imaginária) mas eu quero!"},
                      {"parte": "final", "ideia": "convite; todos com pamonha na mão dando tchau para o carrinho"}],
               youtube={"resumo": "OLHA A PAMONHA! 🌽 Lá vem o carro da pamonha buzinando na rua! Tem pamonha de queijo, tem pamonha de doce… e de chocolate? Ninguém nunca viu… mas a Laurinha quer!",
                        "resumo_short": "OLHA A PAMONHA! 🌽 Quem quer? Eu quero!", "curiosidade": ""},
               playlists=["Músicas Infantis da Laurinha e do Luisinho 🐝"]))

SONGS["44"] = dict(  # curiosidade: para andar de patinete a gente usa capacete
    pasta="44_vovo_patinete", velha="44_palavrinhas_magicas", nova=True,
    letra=letra("bright synth lead and scooter bell", ["Vovó patinete! Zum, zum!", "Vovó patinete!"], "laurinha",
                ["A vovó ganhou um patinete,", "Cor-de-rosa, com buzininha,", "Botou o capacete", "E saiu bem rapidinha!",
                 "Passou pelo cachorro,", "Passou pelo vovô,", "Deu tchau pra todo mundo", "E ninguém alcançou!"],
                ["Vovó patinete, fiu!", "Passou e ninguém viu!", "Vovó patinete, fiu!", "Mais rápida que um assobio!"],
                ["Segura o guidão!", "Põe um pé no chão!", "Dá impulso, vai!", "E faz a curva… iiih!"],
                "Gostou da vovó? Dá um joinha!", "Vovó patinete! Tchau! Fiu!"),
    ficha=dict(titulo="Vovó Patinete", gancho="vovó patinete", palavras_tema=["vovó", "patinete", "capacete", "fiu"],
               tipo="humor", tema="a vovó radical que ganhou um patinete e ninguém alcança", ritmo="latino_infantil",
               persona="laurinha", estrutura="R", dia_a_dia=["andar de patinete com capacete", "vovó", "brincar na rua com um adulto"],
               curiosidade="para andar de patinete a gente usa capacete", alternativas=["pop_infantil"], cantam={"verso": "laurinha", "refrão": "laurinha", "ponte": "laurinha (comandos)"},
               cenas=[{"parte": "intro", "ideia": "a vovó desembrulha o patinete cor-de-rosa e põe o capacete"},
                      {"parte": "verso 1", "ideia": "a vovó dispara pela rua: passa pelo cachorro, pelo vovô (o chapéu dele voa)"},
                      {"parte": "refrão", "ideia": "fiu! só fica o rastro de vento; ninguém alcança a vovó"},
                      {"parte": "ponte", "ideia": "comandos: segura o guidão, pé no chão, impulso… a curva e o 'iiih!'"},
                      {"parte": "final", "ideia": "convite; a vovó freia, pisca e dá tchau com a buzininha"}],
               youtube={"resumo": "VOVÓ PATINETE! 🛴👵 A vovó ganhou um patinete cor-de-rosa, botou o capacete e… fiu! Passou pelo cachorro, passou pelo vovô e ninguém alcançou! Segura o guidão, dá impulso e faz a curva!",
                        "resumo_short": "VOVÓ PATINETE! 🛴 Fiu! Ninguém alcança a vovó!", "curiosidade": ""},
               playlists=["Músicas Infantis da Laurinha e do Luisinho 🐝"]))

SONGS["48"] = dict(  # curiosidade: tem macarrão comprido, curtinho, em forma de concha e de lacinho
    pasta="48_macarrao_que_nao_acaba", velha="48_quando_eu_crescer", nova=True,
    letra=letra("funky electric piano riff", ["Macarrão que não acaba! Zum, zum!", "Macarrão que não acaba!"], "laurinha",
                ["Hoje tem macarronada,", "O prato tá cheinho,", "Enrolei no meu garfo", "E puxei um fiozinho…",
                 "Puxei, puxei, puxei,", "E o fio não acabou!", "Passou pela janela,", "Deu a volta e voltou!"],
                ["Macarrão que não acaba!", "Enrola, enrola, slurp!", "Macarrão que não acaba!", "Puxa, puxa… slurp!"],
                ["Passou pela cozinha,", "Passou pelo quintal,", "Deu a volta na lua", "E caiu no prato: que legal!"],
                "Gostou do macarrão? Dá um joinha!", "Macarrão que não acaba! Tchau! Slurp!"),
    ficha=dict(titulo="Macarrão que Não Acaba", gancho="macarrão que não acaba", palavras_tema=["macarrão", "fio", "slurp", "garfo"],
               tipo="comida", tema="o fio de macarrão que não acaba e dá a volta no mundo", ritmo="disco_infantil", persona="laurinha",
               estrutura="R", dia_a_dia=["almoço", "macarronada", "comer sozinho com o garfo"], curiosidade="tem macarrão comprido, curtinho, em forma de concha e de lacinho", alternativas=["funk_infantil"],
               cantam={"verso": "laurinha", "refrão": "laurinha", "ponte": "laurinha"},
               cenas=[{"parte": "intro", "ideia": "a mesa do almoço; o prato fumegante de macarrão"},
                      {"parte": "verso 1", "ideia": "a Laurinha puxa um fio que não acaba: sai pela janela e volta pela porta"},
                      {"parte": "refrão", "ideia": "enrola, enrola no garfo (o fio vira um novelo gigante) — slurp!"},
                      {"parte": "ponte", "ideia": "o fio atravessa a cozinha, o quintal, dá a volta na lua e cai de volta no prato"},
                      {"parte": "final", "ideia": "convite; a Laurinha com bigode de molho dando tchau"}],
               youtube={"resumo": "MACARRÃO QUE NÃO ACABA! 🍝 A Laurinha enrolou o garfo, puxou um fiozinho… e o macarrão não acabou! Passou pela janela, pela cozinha, pelo quintal, deu a volta na lua e caiu de volta no prato. Slurp!",
                        "resumo_short": "MACARRÃO QUE NÃO ACABA! 🍝 Slurp!", "curiosidade": ""},
               playlists=["Músicas Infantis da Laurinha e do Luisinho 🐝"]))

if __name__ == "__main__":
    for n, s in SONGS.items():
        dest = M / s["pasta"]
        if s["nova"]:
            velha = M / s["velha"] if (M / s["velha"]).exists() else dest
            base = json.loads((velha / "ficha.json").read_text(encoding="utf-8"))
            if velha != dest:
                subprocess.run(["git", "mv", str(velha), str(dest)], check=True)
            f = ficha_nova(base, **s["ficha"])
            f.pop("cantam", None)
            f["cantam"] = s["ficha"]["cantam"]
        else:
            f = json.loads((dest / "ficha.json").read_text(encoding="utf-8"))
            for k, v in s["ficha"].items():
                f[k] = v
            f["voz"] = f["persona"]
            f["versoes"] = f.get("versoes", [])
            f["revisao"] = "18/11/2026: jeito da referência (premissa engraçada, molde, rima, bloco que volta, uma voz)"
        (dest / "ficha.json").write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        (dest / "letra.txt").write_text(s["letra"], encoding="utf-8")
        print("ok", dest.name)
