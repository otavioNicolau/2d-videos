"""Sistema de composição musical do canal (ADR-0015; regras em musicas/BIBLIA_MUSICAL.md).

Não compõe sozinho nem fala com o Suno (não há API pública): as letras são escritas no chat e coladas no Suno à mão.
Este módulo
  * monta os campos do Suno (Título, Style, Exclude, Lyrics, Persona) a partir de ficha.json + letra.txt +
    estilos.json + vozes.json, com alternativas de ritmo e aviso de contradições;
  * checa a letra contra a bíblia (versos curtos, gancho, ritmo citado, bordões, movimento, palavras proibidas…);
  * mede as versões geradas no Suno (andamento, começo, refrão, intervalos, pronúncia pela transcrição) para o humano escolher.

Atalhos aceitos em letra.txt (traduzidos pelo peso da batida do ritmo):
  [Virada]             → [Keyboard Fill] nos ritmos de peso forte e médio; some nos de peso marcado (E9 = E6)
  [Intervalo 8s]       → intervalo instrumental do peso do ritmo (estilos.json → peso → intervalo)
  [Bordão laurinha]    → [Shout - Laurinha] Bora, turminha!   (bordão de vozes.json)
"""
from __future__ import annotations

import json
import re
import statistics
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from ..core.config import ROOT, StudioError

MUSICAS = ROOT / "canais" / "laurinha" / "musicas"   # canal padrão (Laurinha); o canal atual vem de _mus()


def _mus() -> Path:
    """Pasta de músicas do canal atual (toonstudio.core.canal; padrão: musicas/)."""
    from ..core.canal import atual
    return atual().musicas
STYLE_AVISO = 1000          # limite usual do campo Style nas versões recentes do Suno (pode variar)

GENEROS_NA_LETRA = ["frevo", "rock", "axé", "axe", "samba", "forró", "forro", "xote", "baião", "baiao", "funk", "reggae",
                    "pagode", "pagodão", "ciranda", "marchinha", "piseiro", "pop", "batucada", "sertanejo", "rap", "hip hop"]
# '*' no fim = prefixo (safad → safado, safada). Comparação sem acento.
PROIBIDAS = ["rebola*", "sarra*", "novinha", "popozao", "bunda", "cachorra", "safad*", "gostosa", "gostoso", "matar", "morre*",
             "sangue", "arma", "armas", "tiro", "cerveja", "bebida", "cigarro", "beijo na boca", "namorad*"]
OFENSAS = ["burro", "burra", "idiota", "chato", "chata", "feio", "feia", "gordo", "gorda", "bobo", "boba"]
MOVIMENTO = ["pula", "gira", "roda", "bate", "mexe", "abaixa", "levanta", "agacha", "balança", "arrasta", "pro lado",
             "pro outro", "mão pra cima", "parou", "voa", "voei", "dança", "sacode", "pisa", "estica", "aponta",
             "palminha", "pezinho", "escova", "mostra", "conta", "tchau", "abraça"]


# ───────────────────────── dados ─────────────────────────

def _json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def estilos() -> dict:
    return _json(_mus() / "estilos.json")


def vozes() -> dict:
    return _json(_mus() / "vozes.json")


def pasta(nome: str) -> Path:
    """Aceita o nome completo da pasta ('01_zum_zum_cheguei'), o número ('01') ou parte do nome ('lagoa')."""
    cands = [d for d in sorted(_mus().iterdir()) if (d / "ficha.json").exists()]
    exact = [d for d in cands if d.name == nome]
    hit = exact or [d for d in cands if d.name.startswith(nome + "_")] or [d for d in cands if nome in d.name]
    if len(hit) != 1:
        raise StudioError(f"música '{nome}' não encontrada" if not hit else f"'{nome}' é ambíguo: {[d.name for d in hit]}")
    return hit[0]


def todas() -> list[Path]:
    return [d for d in sorted(_mus().iterdir()) if (d / "ficha.json").exists()]


def ficha(d: Path) -> dict:
    return _json(d / "ficha.json")


# ───────────────────────── letra ─────────────────────────

def _norm(s: str) -> str:
    """minúsculas, sem acentos e sem pontuação: 'Zum-zum, Cheguei!' → 'zum zum cheguei'."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def parse(letra: str) -> list[tuple[str, str]]:
    """[(tipo, texto)]: tipo 'tag' para marcações [..] e 'canto' para versos cantados."""
    out = []
    for raw in letra.splitlines():
        l = raw.strip()
        if not l:
            continue
        m = re.match(r"^\[([^\]]+)\]\s*(.*)$", l)
        if m:
            out.append(("tag", m.group(1).strip()))
            if m.group(2):                       # ex.: [Shout - Laurinha] Bora, turminha!
                out.append(("canto", m.group(2).strip()))
        else:
            out.append(("canto", l))
    return out


def expandir(letra: str, peso: str, E: dict, V: dict) -> str:
    """Traduz os atalhos ([Virada], [Intervalo Ns], [Bordão x]) para marcações do Suno."""
    intervalo = E["peso"][peso]["intervalo"]
    trio = E["canal"].get("trio", {})
    if trio.get("ativo"):                     # E12: intervalos e abertura só com bateria, teclado e sax
        intervalo = trio.get("intervalo", intervalo)
        if trio.get("intro"):
            letra = re.sub(r"^\[\s*Intro\b[^\]]*\]", trio["intro"], letra, count=1, flags=re.M | re.I)
        if trio.get("resposta_teclado"):      # 20/11: o teclado responde cada verso cantado (tram tram tram-ram)
            letra = re.sub(r"^\[\s*(Verse|Chorus)([^\]]*)\]", lambda m: f"[{m.group(1)}{m.group(2)}, short keyboard riff after each line]",
                           letra, flags=re.M | re.I)
    fill = {"forte": "[Keyboard Fill]", "media": "[Keyboard Fill]", "marcada": ""}[peso]   # E9 = E6 (19/11): virada de teclado de volta
    out = []
    for raw in letra.splitlines():
        s = raw.strip()
        if re.fullmatch(r"\[\s*virada\s*\]", s, re.I):
            if fill:
                out.append(fill)
            continue
        m = re.fullmatch(r"\[\s*intervalo\s*(\d+)\s*s?\s*\]", s, re.I)
        if m:
            out.append(intervalo.format(s=m.group(1)))
            continue
        m = re.fullmatch(r"\[\s*bord[aã]o\s+(\w+)\s*\]", s, re.I)
        if m:
            v = V["vozes"].get(m.group(1).lower())
            if not v or not v.get("bordao"):
                raise StudioError(f"bordão desconhecido: {m.group(1)}")
            out.append(f"[Shout - {v.get('shout_tag') or m.group(1).capitalize()}] {v['bordao']}")   # shout_tag: Fofolucos = "same kid boy voice"
            continue
        out.append(voz_unica(raw.rstrip()))
    return "\n".join(out).strip() + "\n"


def voz_unica(linha: str) -> str:
    """18/11/2026 — referência = UMA voz, centralizada, sem coro. No Suno, texto entre parênteses vira voz de fundo e
    "kids choir" vira coro: a resposta passa a ser cantada pela mesma voz ("Derrubou! (Ha ha!)" → "Derrubou! Ha ha!")
    e as marcações perdem o coro ("[Chorus - kids choir, louder]" → "[Chorus - louder]")."""
    s = linha.strip()
    if s.startswith("["):
        m = re.match(r"\[([^\]]*)\](.*)$", s)
        tag, resto = m.group(1), m.group(2)
        tag = re.sub(r",?\s*kids choir answers", "", tag, flags=re.I)
        tag = re.sub(r"\s*-\s*kids choir\s*,\s*", " - ", tag, flags=re.I)
        tag = re.sub(r"\s*-\s*kids choir\s*$", "", tag, flags=re.I)
        tag = re.sub(r"\bkids\s+(follow|answer)\w*[^,\]]*", "", tag, flags=re.I).rstrip(" -,")
        return f"[{tag}] {voz_unica(resto.strip())}" if resto.strip() else f"[{tag}]"
    return re.sub(r"\s*\(([^)]*)\)", lambda m: " " + m.group(1), linha).strip() if "(" in linha else linha


# ───────────────────────── prompt do Suno ─────────────────────────

GRAFIA_SUNO = {"Luisinho": "Luizinho"}       # BIBLIA_MUSICAL §3: escrito com z o Suno não canta "Luissinho"
GRAFIA_CANTO = {"Laurinha": "Lau-ri-nha"}     # só no que é CANTADO (fora dos [colchetes]): junto ele canta "Larinha"/"Launinha"


def grafia_suno(letra: str) -> str:
    """Grafia SÓ para o texto do Suno (pronúncia); legenda e tela continuam com o nome oficial."""
    for a, b in GRAFIA_SUNO.items():
        letra = letra.replace(a, b)
    partes = re.split(r"(\[[^\]]*\])", letra)     # marcações [..] ficam com o nome normal (são instruções)
    for i in range(0, len(partes), 2):
        for a, b in GRAFIA_CANTO.items():
            partes[i] = partes[i].replace(a, b)
    return "".join(partes)


def style(f: dict, ritmo: str | None = None, bpm: int | None = None, E: dict | None = None, V: dict | None = None) -> str:
    E = E or estilos()
    V = V or vozes()
    rid = ritmo or f["ritmo"]
    r = E["ritmos"][rid]
    p = E["peso"][r["peso"]]
    bpm = bpm or (f["bpm"] if rid == f["ritmo"] else r["bpm"][2])
    voz = V["vozes"][f.get("voz", "dueto")]["style"]
    # 18/11 (take v2 da 14): o Suno pesa mais o começo do Style — "teclado arranjador" vem antes do ritmo, e o ritmo entra como
    # "groove" (o nome sozinho, ex. "axé music, Bahia carnival", puxava percussão ao vivo e batida variada)
    genero = r["genero"].split(",")[0].strip()
    trio = E["canal"].get("trio", {})
    if trio.get("ativo"):                 # E12 (19/11): só sax, bateria e teclado — o ritmo entra só como groove
        # 21/11: o ritmo pode trazer o PRÓPRIO groove (ex.: latino = dembow); o do canal ("palmas no 2 e 4") apagava o dembow
        parts = [E["canal"].get("duracao", ""), trio["abertura"], f"{genero} groove", f"{bpm} bpm", r.get("peso_style") or trio["peso_style"],
                 trio["producao"], r["clima"], f.get("style_extra", ""), voz, V["coro"].get("style", ""), E["canal"]["sempre"]]
        return ", ".join(x for x in parts if x)
    parts = [E["canal"].get("duracao", ""), E["canal"].get("abertura", ""), f"{genero} groove", f"{bpm} bpm", r["bateria"], p["style"],
             E["canal"].get("producao", ""), r["instrumentos"], r["clima"], f.get("style_extra", ""),
             voz, V["coro"].get("style", ""), E["canal"]["sempre"]]
    return ", ".join(x for x in parts if x)


def style_curto(f: dict, ritmo: str | None = None, E: dict | None = None, V: dict | None = None) -> str:
    """Versão mínima para quando o campo Style for curto: ritmo, andamento, peso, bateria, voz."""
    E = E or estilos()
    V = V or vozes()
    rid = ritmo or f["ritmo"]
    r = E["ritmos"][rid]
    bpm = f["bpm"] if rid == f["ritmo"] else r["bpm"][2]
    peso = {"forte": "punchy electronic beat, strong kick and claps", "media": "strong punchy groove",
            "marcada": "steady marked groove"}[r["peso"]]
    return ", ".join([x for x in [E["canal"].get("duracao", "")] if x] + [r["genero"].split(",")[0], f"{bpm} bpm", peso, r["bateria"].split(",")[0],
                      V["vozes"][f.get("voz", "dueto")]["style"], "major key, Brazilian Portuguese"])


def exclude(f: dict, ritmo: str | None = None, E: dict | None = None) -> str:
    E = E or estilos()
    r = E["ritmos"][ritmo or f["ritmo"]]
    items = E["canal"]["exclude_sempre"] + E["peso"][r["peso"]]["exclude"] + r.get("exclude", []) + f.get("exclude_extra", [])
    trio = E["canal"].get("trio", {})
    if trio.get("ativo"):
        items = [x for x in items if x not in trio.get("tirar_do_exclude", [])] + trio.get("exclude_extra", [])
    return ", ".join(dict.fromkeys(items))


def contradicoes(sty: str, exc: str) -> list[str]:
    """Termos do Exclude que também aparecem no Style (o Suno recebe ordens opostas)."""
    s = sty.lower()
    out = []
    for term in (t.strip().lower() for t in exc.split(",")):
        if term and re.search(r"\b" + re.escape(term) + r"\b", s):
            out.append(term)
    if re.search(r"\bslow\b", s) and re.search(r"\b(fast|energetic|1[4-9]\d bpm)\b", s):
        out.append("slow × fast")
    return out


LIMITE_LETRA = 5000      # campo Lyrics do Suno (conta as quebras de linha)


def prompt(d: Path) -> dict:
    E, V = estilos(), vozes()
    f = ficha(d)
    letra = (d / "letra.txt").read_text(encoding="utf-8")
    r = E["ritmos"][f["ritmo"]]
    voz = V["vozes"][f.get("persona") or f.get("voz", "dueto")]     # "persona": quem conduz (uma Voice por faixa no Suno)
    res = {"titulo": f["titulo"], "ritmo": r["nome"], "bpm": f["bpm"], "style": style(f, E=E, V=V),
           "style_curto": style_curto(f, E=E, V=V), "exclude": exclude(f, E=E),
           "lyrics": grafia_suno(expandir(letra, r["peso"], E, V)), "persona": voz.get("suno_persona"), "voz": f.get("persona") or f.get("voz", "dueto"),
           "avisos": [], "alternativas": []}
    if len(res["lyrics"].rstrip()) > LIMITE_LETRA:
        res["avisos"].append(f"letra com {len(res['lyrics'].rstrip())} caracteres: passa do limite do Suno ({LIMITE_LETRA})")
    lo, hi, _ = r["bpm"]
    if not lo <= f["bpm"] <= hi:
        res["avisos"].append(f"andamento {f['bpm']} fora da faixa do {r['nome']} ({lo}–{hi})")
    c = contradicoes(res["style"], res["exclude"])
    if c:
        res["avisos"].append("contradição Style × Exclude: " + ", ".join(c))
    if len(res["style"]) > STYLE_AVISO:
        res["avisos"].append(f"Style com {len(res['style'])} caracteres; use o Style curto se o Suno cortar")
    for alt in f.get("alternativas", []):
        ra = E["ritmos"][alt]
        res["alternativas"].append({"ritmo": ra["nome"], "id": alt, "bpm": ra["bpm"][2], "style": style(f, alt, E=E, V=V),
                                    "exclude": exclude(f, alt, E=E), "lyrics": grafia_suno(expandir(letra, ra["peso"], E, V))})
    return res


def _bloco_avancado(p: dict) -> list[str]:
    """Opções Advanced do Suno v6 (E10): o quanto o Suno obedece ao Style e à Voice."""
    av = estilos()["canal"].get("suno_avancado")
    if not av:
        return []
    linhas = ["AJUSTES AVANÇADOS (Suno v6 → Advanced; conferir antes de gerar):"]
    linhas += [f"  {k}: {v}" for k, v in av.items()]
    return linhas + [""]


def texto_suno(p: dict) -> str:
    """O arquivo de copiar e colar (suno.txt)."""
    pers = p["persona"] or f"(ainda não criada — a voz vai descrita no Style; ao criar, registre em {_mus().relative_to(ROOT)}/vozes.json → {p['voz']})"
    blocos = [
        f"TÍTULO: {p['titulo']}",
        f"RITMO: {p['ritmo']} · {p['bpm']} BPM",
        f"PERSONA (Suno): {pers}",
        f"ESTILO DO CANAL: {estilos()['canal'].get('versao_por_voz', {}).get(p['voz'], estilos()['canal'].get('versao', '?'))} ({_mus().relative_to(ROOT)}/PROCESSO_MELHORIA.md)",
        "",
        *_bloco_avancado(p),
        f"STYLE OF MUSIC ({len(p['style'])} caracteres):",
        p["style"],
        "",
        f"STYLE CURTO (se o Suno cortar o de cima; {len(p['style_curto'])} caracteres):",
        p["style_curto"],
        "",
        "EXCLUDE:",
        p["exclude"],
        "",
        f"LYRICS ({len(p['lyrics'].rstrip())} de {LIMITE_LETRA} caracteres no Suno; apague o campo e cole só daqui até o [End]):",
        "",
        p["lyrics"].rstrip(),
        "",
        "=" * 30 + " FIM DA LETRA — não copie daqui para baixo " + "=" * 30,
    ]
    for a in []:                                       # E10 (19/11): alternativas de ritmo fora do suno.txt (confundiam na hora de colar)
        blocos += ["", "=" * 68, f"ALTERNATIVA DE RITMO: {a['ritmo']} · {a['bpm']} BPM (mesma letra)", "=" * 68,
                   "STYLE OF MUSIC:", a["style"], "", "EXCLUDE:", a["exclude"]]
        if a["lyrics"] != p["lyrics"]:
            blocos += ["", f"LYRICS (marcações ajustadas para este ritmo; {len(a['lyrics'].rstrip())} de {LIMITE_LETRA} caracteres):", "",
                       a["lyrics"].rstrip()]
    if p["avisos"]:                                    # 20/11: os avisos ficam ANTES da letra — depois do [End] o usuário copiou
        i = blocos.index(next(b for b in blocos if b.startswith("STYLE OF MUSIC")))   # junto e o Suno CANTOU o aviso (26)
        blocos[i:i] = ["AVISOS (para conferir — NÃO vão para o Suno):"] + [f"- {x}" for x in p["avisos"]] + [""]
    head = "GERADO por `toonstudio musica prompt` a partir de ficha.json + letra.txt — não edite aqui; edite a ficha/letra."
    return head + "\n\n" + "\n".join(blocos) + "\n"


def escrever_prompt(d: Path) -> Path:
    out = d / "suno.txt"
    out.write_text(texto_suno(prompt(d)), encoding="utf-8")
    return out


# ───────────────────────── checagem da letra ─────────────────────────

def _tem(texto_norm: str, termo: str) -> bool:
    """procura a palavra/expressão inteira (ou prefixo, se termina em '*') num texto já normalizado."""
    pref = termo.endswith("*")
    alvo = _norm(termo.rstrip("*"))
    return bool(alvo) and re.search(r"\b" + re.escape(alvo) + ("" if pref else r"\b"), texto_norm) is not None


@dataclass
class Item:
    nivel: str          # "erro" | "aviso" | "ok"
    regra: str
    msg: str


@dataclass
class Checagem:
    itens: list[Item] = field(default_factory=list)
    metricas: dict = field(default_factory=dict)

    def add(self, nivel, regra, msg):
        self.itens.append(Item(nivel, regra, msg))

    @property
    def erros(self):
        return [i for i in self.itens if i.nivel == "erro"]


def _segundos_tag(tag: str) -> float:
    m = re.search(r"(\d+)\s*(?:s\b|sec|second)", tag, re.I)
    return float(m.group(1)) if m else 0.0


def estimar_duracao(seq: list[tuple[str, str]]) -> float:
    """Estimativa GROSSEIRA (calibrada na referência: ~1,9 s por verso de ~4 palavras, ~1 compasso de respiro entre as
    partes). A medição real das versões do Suno (F4) é que vale."""
    t = 0.0
    for kind, txt in seq:
        if kind == "canto":
            t += max(1.2, 0.45 * len(txt.split()))
        else:
            low = txt.lower()
            if low.startswith(("intro",)):
                t += 4.0
            elif low.startswith(("virada", "drum fill", "percussion fill", "keyboard fill")):
                t += 1.5
            elif low.startswith(("outro",)):
                t += 3.0
            elif low.startswith(("verse", "chorus", "bridge", "verso", "refr", "ponte")):
                t += 1.5                    # respiro instrumental entre as partes
            t += _segundos_tag(txt)
    return round(t, 1)


def checar(d: Path) -> Checagem:
    f = ficha(d)
    E = estilos()
    letra = (d / "letra.txt").read_text(encoding="utf-8")
    seq = parse(letra)
    canto = [t for k, t in seq if k == "canto"]
    tags = [t for k, t in seq if k == "tag"]
    ck = Checagem()
    full = _norm(" ".join(canto))
    words = [len(l.split()) for l in canto]

    # 1/2 — tema e gancho
    g = f.get("gancho", "")
    if not g:
        ck.add("erro", "gancho", "ficha sem 'gancho' (a frase-título do refrão)")
    else:
        ng = _norm(g)
        n = len(re.findall(r"\b" + re.escape(ng) + r"\b", full))
        ck.metricas["gancho_vezes"] = n
        if len(g.split()) > 4:
            ck.add("aviso", "gancho", f"gancho com {len(g.split())} palavras (ideal até 3)")
        if n < 8:
            ck.add("aviso", "gancho", f"gancho \"{g}\" cantado {n} vezes (referência: ~8 a 12)")
        else:
            ck.add("ok", "gancho", f"gancho \"{g}\" cantado {n} vezes")
        if not set(ng.split()) & set(_norm(f["titulo"]).split()):
            ck.add("aviso", "gancho", "o título não contém o gancho")
    tema = [_norm(x) for x in f.get("palavras_tema", [])]
    if tema:
        inicio = _norm(" ".join(canto[:4]))
        if not any(t in inicio for t in tema):
            ck.add("aviso", "tema", "o tema não aparece nos primeiros versos")
        else:
            ck.add("ok", "tema", "tema aparece logo no começo")

    # 3 — versos curtos e repetição
    med = statistics.median(words) if words else 0
    longos = [l for l in canto if len(l.split()) > 7]
    ck.metricas.update(linhas=len(canto), diferentes=len(set(map(_norm, canto))), palavras_verso=med,
                       versos_longos=len(longos))
    if longos:
        ck.add("aviso", "verso", f"{len(longos)} verso(s) com mais de 7 palavras, ex.: \"{longos[0]}\"")
    ck.add("ok" if med <= 5 else "aviso", "verso", f"mediana de {med} palavras por verso (ideal 3–5)")
    if len(set(map(_norm, canto))) > 25:
        ck.add("aviso", "variedade", f"{len(set(map(_norm, canto)))} linhas diferentes (referência ~20–25)")
    run, prev, maxrun = 0, None, 0
    for l in map(_norm, canto):
        run = run + 1 if l == prev else 1
        prev = l
        maxrun = max(maxrun, run)
    if maxrun > 4:
        ck.add("aviso", "cansativo", f"a mesma linha repetida {maxrun} vezes seguidas")

    # 4 — idade
    hits = [w.rstrip("*") for w in PROIBIDAS if _tem(full, w)]
    if hits:
        ck.add("erro", "idade", "palavras inadequadas para a idade: " + ", ".join(hits))
    from ..core.canal import atual as _canal_atual
    evitar = _canal_atual().raw.get("palavras_evitar", {})        # regra de cada canal (ex.: Fofolucos: monstro → monstrinho)
    ev = [f"{w} (use {s})" for w, s in evitar.items() if _tem(full, w)]
    if ev:
        ck.add("erro", "palavras do canal", "palavra que o canal evita: " + ", ".join(ev))
    ofs = [w for w in OFENSAS if _tem(full, w)]
    if ofs:
        ck.add("aviso", "idade", "confira o contexto (pode soar como xingamento): " + ", ".join(ofs))

    # regra do canal — nunca citar o ritmo na letra
    gen = [w for w in GENEROS_NA_LETRA if _tem(full, w) and w not in f.get("titulo", "").lower()]   # título de cantiga não conta
    if gen:
        ck.add("erro", "ritmo citado", "a letra cita o ritmo: " + ", ".join(sorted(set(gen))))

    # 8 — identidade
    from ..core.canal import atual as _canal_atual            # multicanal: a assinatura é do canal (zum / rawr…)
    ass = _canal_atual().raw.get("assinatura") or {"palavra": "zum", "descricao": "o \"zum\" das asinhas",
                                                   "bordoes": "Bora, turminha! / Zum-zum, que massa!"}
    bordoes = len([t for t in tags if t.lower().startswith(("bordão", "bordao", "shout"))])
    if not bordoes:
        ck.add("aviso", "identidade", f"nenhum bordão ({ass['bordoes']})")
    if ass["palavra"] not in full:
        ck.add("aviso", "identidade", f"sem {ass['descricao']}")
    if bordoes and ass["palavra"] in full:
        ck.add("ok", "identidade", f"{bordoes} bordão(ões) e {ass['descricao']}")
    for campo, regra in (("dia_a_dia", "dia a dia"), ("curiosidade", "curiosidade")):
        if not f.get(campo):
            ck.add("aviso", regra, f"ficha sem '{campo}'")

    # convite do canal no final (decisão do usuário 17/11/2026): joinha + inscrever, sempre com um adulto (canal infantil)
    fim = full[int(len(full) * 0.75):]
    sev = "aviso" if f.get("status") == "aprovada" else "erro"      # músicas já gravadas antes da regra: só aviso
    if not ("joinha" in fim and "inscrev" in fim):
        ck.add(sev, "convite", "o final não convida para o joinha e para se inscrever no canal (com o papai/a mamãe)")
    elif not any(w in fim for w in ("papai", "mamãe", "mamae", "adulto")):
        ck.add(sev, "convite", "o convite do final precisa chamar um adulto (papai/mamãe): canal para crianças")
    else:
        ck.add("ok", "convite", "o final convida para o joinha e para se inscrever, com o papai/a mamãe")

    # auditoria 17/11/2026 (docs/auditoria): refrão curto, sem aula no meio, abertura que promete a música
    refs = re.findall(r"^\[Chorus[^\]]*\]\n((?:(?!\[|\n\n).*\n?)+)", letra, flags=re.M)
    if refs:
        linhas_ref = [x for x in (_norm(re.sub(r"\([^)]*\)", "", l)) for l in refs[0].strip().splitlines()) if x]
        ck.metricas["refrao_diferentes"] = len(set(linhas_ref))
        if len(set(linhas_ref)) > 5:
            ck.add("aviso", "refrão", f"refrão com {len(set(linhas_ref))} linhas diferentes (ideal: 4 linhas cantadas 2×, até 5 diferentes)")
    if re.search(r"^Sabia que", letra, flags=re.M):
        ck.metricas["sabia_que"] = True
        ck.add("aviso", "aula", "verso com \"Sabia que…\": no máximo 1 em cada 3 músicas (o fato entra como jogo ou piada)")
    if re.search(r"^\(.*Zum, zum!\)$", letra.split("\n\n")[0], flags=re.M):
        ck.add("aviso", "abertura", "abertura genérica \"(X! Zum, zum!)\": prefira o gancho ou o som da música")

    # 10 — animação
    mov = sorted({m for m in MOVIMENTO if _tem(full, m)})
    ck.metricas["movimentos"] = mov
    ck.add("ok" if len(mov) >= 3 else "aviso", "animação", f"{len(mov)} comando(s)/ação(ões) de movimento: {', '.join(mov)}")
    if not f.get("cenas"):
        ck.add("aviso", "animação", "ficha sem sugestões de cenas")

    # estrutura e marcações
    low = [t.lower() for t in tags]
    if not any(t.startswith("chorus") or t.startswith("refr") for t in low):
        ck.add("erro", "estrutura", "sem [Chorus]")
    nint = len([t for t in low if t.startswith(("intervalo", "drum break", "instrumental break")) or "solo" in t])
    if nint < 2:
        ck.add("aviso", "estrutura", f"{nint} intervalo(s) de dança (referência: 2–3)")
    peso = E["ritmos"][f["ritmo"]]["peso"]
    if any(t.startswith(("drum fill", "drum break")) for t in low):
        ck.add("aviso", "marcações", "use [Virada]/[Intervalo Ns] em vez de [Drum Fill]/[Drum Break] (o gerador ajusta ao ritmo)")
    if peso == "marcada" and any("heavy" in t for t in low):
        ck.add("aviso", "marcações", "marcação 'heavy' num ritmo de batida marcada")

    # respostinhas (18/11): a referência quase não tem (≈0,7 por 100 palavras); no Suno viram voz de fundo
    nresp = len(re.findall(r"\([^)]*\)", "\n".join(l for l in letra.splitlines() if not l.strip().startswith("["))))
    if nresp > 6:
        ck.add("aviso", "respostas", f"{nresp} respostas entre parênteses (referência: quase nenhuma; uma voz só, sem respostinha em todo verso)")
    # duração estimada
    est = estimar_duracao(seq)
    ck.metricas["duracao_estimada"] = est
    lo, hi = f.get("duracao_alvo", [140, 170])
    if est < lo:  # sem folga: a 12 (estimativa 122 s) saiu com 103 s e o Suno completou com outra letra
        ck.add("aviso", "duração", f"estimativa {est:.0f} s, abaixo do alvo {lo}–{hi} s (estimativa grosseira)")
    elif est > hi + 20:
        ck.add("aviso", "duração", f"estimativa {est:.0f} s, acima do alvo {lo}–{hi} s (estimativa grosseira)")
    else:
        ck.add("ok", "duração", f"estimativa {est:.0f} s (alvo {lo}–{hi} s; grosseira)")
    return ck


# ───────────────────────── nova música ─────────────────────────

MODELOS = {
    "R": "[Intro - {intro}]\n(Zum, zum!)\n\n[Verse - Laurinha, girl child vocal]\n…\n\n[Virada]\n[Chorus - kids choir]\n…\n\n"
         "[Bordão laurinha]\n[Intervalo 8s]\n\n[Verse - Luisinho, boy child vocal]\n…\n\n[Virada]\n[Chorus - kids choir]\n…\n\n"
         "[Bordão luisinho]\n[Intervalo 8s]\n\n[Virada]\n[Chorus - kids choir, louder]\n…\n\n[Outro]\n… (Zum!)\n[End]\n",
}
MODELOS["A"] = MODELOS["R"].replace("[Bordão luisinho]", "[Bridge - Laurinha and Luisinho]\n…\n\n[Bordão luisinho]")


def nova(nome: str, titulo: str, ritmo: str, tipo: str, estrutura: str = "A", voz: str = "dueto") -> Path:
    E = estilos()
    if ritmo not in E["ritmos"]:
        raise StudioError(f"ritmo desconhecido: {ritmo} (opções: {', '.join(E['ritmos'])})")
    n = max([int(d.name[:2]) for d in todas() if d.name[:2].isdigit()] + [0]) + 1
    d = _mus() / f"{n:02d}_{nome}"
    if d.exists():
        raise StudioError(f"{d} já existe")
    d.mkdir()
    r = E["ritmos"][ritmo]
    f = {"schema": "musica-1.0", "titulo": titulo, "gancho": "", "palavras_tema": [], "tipo": tipo, "tema": "", "dia_a_dia": [],
         "curiosidade": "", "ritmo": ritmo, "bpm": r["bpm"][2], "estrutura": estrutura, "voz": voz, "cantam": {}, "cenas": [],
         "duracao_alvo": [140, 170], "alternativas": [], "status": "rascunho", "versoes": []}
    (d / "ficha.json").write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    from ..core.canal import atual as _canal_atual
    mod_canal = _canal_atual().raw.get("modelo_letra")          # multicanal: cada canal tem o seu modelo de letra
    modelo = (mod_canal or MODELOS.get(estrutura, MODELOS["A"])).format(intro=r["instrumentos"].split(",")[0])
    (d / "letra.txt").write_text(modelo, encoding="utf-8")
    return d


# ───────────────────────── medição das versões do Suno (F4) ─────────────────────────

AUDIO_EXT = (".wav", ".mp3", ".m4a", ".flac", ".ogg")
_KS_MAIOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_KS_MENOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
_NOTAS = "Dó Dó# Ré Ré# Mi Fá Fá# Sol Sol# Lá Lá# Si".split()


def tom(wav: Path) -> str:
    """Tom aproximado (perfil de Krumhansl sobre o cromagrama)."""
    import librosa
    import numpy as np
    y, sr = librosa.load(str(wav), sr=22050, mono=True)
    c = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
    best = max((float(np.corrcoef(np.roll(p, k), c)[0, 1]), k, nome)
               for p, nome in ((np.array(_KS_MAIOR), "maior"), (np.array(_KS_MENOR), "menor")) for k in range(12))
    return f"{_NOTAS[best[1]]} {best[2]}"


def _bpm_coerente(medido: float, alvo: float) -> tuple[float, str]:
    """A detecção de batida erra por metade/dobro; escolhe a leitura mais próxima do andamento pedido e avisa."""
    cands = [(abs(medido * k - alvo), medido * k, k) for k in (0.5, 1.0, 2.0, 2 / 3, 1.5)]
    _, bpm, k = min(cands)
    nota = "" if k == 1.0 else f"leitura {medido:.0f} ajustada ×{k:g}"
    return round(bpm, 1), nota


def palavras_esperadas(d: Path) -> list[str]:
    E, V = estilos(), vozes()
    f = ficha(d)
    letra = expandir((d / "letra.txt").read_text(encoding="utf-8"), E["ritmos"][f["ritmo"]]["peso"], E, V)
    return _norm(" ".join(t for k, t in parse(letra) if k == "canto")).split()


def comparar_letra(esperadas: list[str], ouvidas: list[str]) -> dict:
    """Quanto da letra a transcrição da voz isolada reconheceu, em ordem. Proxy de pronúncia (Whisper também erra)."""
    sm = SequenceMatcher(None, esperadas, ouvidas, autojunk=False)
    ok = [False] * len(esperadas)
    for b in sm.get_matching_blocks():
        for i in range(b.a, b.a + b.size):
            ok[i] = True
    faltou = {}
    for w, hit in zip(esperadas, ok):
        if not hit and len(w) > 3:
            faltou[w] = faltou.get(w, 0) + 1
    nunca = sorted((w for w in faltou if w not in set(ouvidas)), key=lambda w: -faltou[w])
    return {"acerto": round(100 * sum(ok) / max(1, len(esperadas))), "nao_reconhecidas": nunca[:12]}


def _primeira_vez(ouvidas: list[dict], frase: str) -> float | None:
    alvo = _norm(frase).split()
    ws = [_norm(w["w"]) for w in ouvidas]
    for i in range(len(ws) - len(alvo) + 1):
        if ws[i:i + len(alvo)] == alvo:
            return round(ouvidas[i]["s"], 1)
    return None


def _final(a, sr, hop: float = 0.1) -> dict:
    """Como a música termina: 'corte seco' (para no volume cheio) ou 'esmaecendo' (fade); silêncio depois do último som."""
    import numpy as np
    n = int(hop * sr)
    env = np.sqrt(np.convolve(a ** 2, np.ones(n) / n, mode="valid")[::n]) if len(a) > n else np.array([0.0])
    ref = float(np.median(env[env > 0])) if (env > 0).any() else 1e-9
    som = np.where(env > 0.1 * ref)[0]
    last = int(som[-1]) if len(som) else len(env) - 1
    silencio = round((len(env) - 1 - last) * hop, 1)
    k = int(3 / hop)
    trecho = env[max(0, last - k):last + 1]
    fade = len(trecho) > 4 and float(trecho[-3:].mean()) < 0.5 * float(trecho[: len(trecho) // 2].mean())
    return {"tipo": "esmaecendo" if fade else "corte seco", "silencio": silencio}


def medir_versao(d: Path, audio: Path, log=print) -> dict:
    import numpy as np
    import soundfile as sf
    import subprocess
    from ..core.config import tool
    from . import song
    f = ficha(d)
    r = estilos()["ritmos"][f["ritmo"]]
    adir = d / "versoes" / ".analise" / audio.stem
    adir.mkdir(parents=True, exist_ok=True)
    work = adir / "trabalho.wav"
    if not work.exists() or work.stat().st_mtime < audio.stat().st_mtime:
        subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", str(audio), "-vn", "-ar", "44100", "-ac", "2", str(work)],
                       check=True)
    log(f"  {audio.name}: batidas…")
    rh = song.rhythm(work)
    bpm, nota_bpm = _bpm_coerente(rh["bpm"], f["bpm"])
    log(f"  {audio.name}: separando a voz…")
    vocals = song.separate_vocals(work, adir)
    va = song.vocal_activity(vocals)
    log(f"  {audio.name}: transcrevendo a voz…")
    ouvidas = song.lyrics_words(vocals)
    cmp = comparar_letra(palavras_esperadas(d), [_norm(w["w"]) for w in ouvidas if _norm(w["w"])])
    dur = rh["duration"]
    sung = sum(b - a for a, b in va)
    gaps = [[round(a[1], 1), round(b[0] - a[1], 1)] for a, b in zip(va, va[1:]) if b[0] - a[1] >= 2.5]
    a, sr = sf.read(work, dtype="float32")
    a = a.mean(axis=1) if a.ndim > 1 else a
    fim = _final(a, sr)
    m = {"arquivo": audio.name, "duracao": round(dur, 1), "bpm": bpm, "bpm_nota": nota_bpm, "tom": tom(work),
         "voz_inicio": va[0][0] if va else None, "refrao_inicio": _primeira_vez(ouvidas, f.get("gancho", "")) if f.get("gancho") else None,
         "cantado": round(100 * sung / dur), "intervalos": gaps, "fim_depois_da_voz": round(dur - va[-1][1], 1) if va else None,
         "final": fim["tipo"], "silencio_final": fim["silencio"], **cmp}
    pontos = []
    lo, hi, _ = r["bpm"]
    if not lo - 3 <= bpm <= hi + 3:
        pontos.append(f"andamento {bpm:.0f} fora da faixa do {r['nome']} ({lo}–{hi})")
    if m["voz_inicio"] is not None and m["voz_inicio"] > 6:
        pontos.append(f"voz só entra em {m['voz_inicio']} s (ideal ≤ 5 s)")
    if m["refrao_inicio"] is None:
        pontos.append("o gancho não foi reconhecido na transcrição")
    elif m["refrao_inicio"] > 45:
        pontos.append(f"gancho só aparece em {m['refrao_inicio']} s (referência ~35 s)")
    da, db = f.get("duracao_alvo", [140, 170])
    if not da - 10 <= dur <= db + 10:
        pontos.append(f"duração {dur:.0f} s fora do alvo {da}–{db} s")
    if m["acerto"] < 80:
        pontos.append(f"só {m['acerto']}% da letra reconhecida — ouvir a pronúncia")
    if m["tom"].endswith("menor"):
        pontos.append("tom menor (o canal é sempre em tom maior)")
    if len(gaps) < 2:
        pontos.append("menos de 2 intervalos de dança")
    m["pontos_a_conferir"] = pontos
    return m


OUVIDO = ["1 começo chama atenção", "5 melodia combina com a letra", "6 dá vontade de dançar", "7 pronúncia natural",
          "8 tem a cara do canal", "9 nenhum trecho cansativo"]


def medir(d: Path, arquivos: list[Path] | None = None, log=print) -> Path:
    vdir = d / "versoes"
    arquivos = arquivos or sorted(p for p in vdir.glob("*") if p.suffix.lower() in AUDIO_EXT)
    if not arquivos:
        raise StudioError(f"nenhuma versão em {vdir} (baixe as versões do Suno para lá)")
    out = d / "avaliacao.json"
    av = _json(out) if out.exists() else {"schema": "avaliacao-1.0", "versoes": {}, "ouvido": {}, "escolhida": None}
    for a in arquivos:
        av["versoes"][a.stem] = medir_versao(d, a, log)
        av["ouvido"].setdefault(a.stem, {k: None for k in OUVIDO})
    out.write_text(json.dumps(av, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def tabela(av: dict) -> str:
    cols = [("versão", lambda k, m: k), ("dur", lambda k, m: f"{m['duracao']:.0f}s"), ("BPM", lambda k, m: f"{m['bpm']:.0f}"),
            ("tom", lambda k, m: m["tom"]), ("voz", lambda k, m: f"{m['voz_inicio']}s"),
            ("gancho", lambda k, m: f"{m['refrao_inicio']}s" if m["refrao_inicio"] is not None else "—"),
            ("cantado", lambda k, m: f"{m['cantado']}%"), ("interv.", lambda k, m: str(len(m["intervalos"]))),
            ("letra", lambda k, m: f"{m['acerto']}%"), ("final", lambda k, m: m["final"])]
    rows = [[c[0] for c in cols]] + [[c[1](k, m) for c in cols] for k, m in av["versoes"].items()]
    w = [max(len(r[i]) for r in rows) for i in range(len(cols))]
    lines = ["  ".join(x.ljust(w[i]) for i, x in enumerate(r)) for r in rows]
    for k, m in av["versoes"].items():
        if m["pontos_a_conferir"] or m["nao_reconhecidas"]:
            lines.append(f"\n{k}:")
            lines += [f"  - {p}" for p in m["pontos_a_conferir"]]
            if m["nao_reconhecidas"]:
                lines.append("  - palavras não reconhecidas: " + ", ".join(m["nao_reconhecidas"]))
    lines.append("\nA escolha é humana: ouça as versões e registre com `toonstudio musica escolher <música> <versão>`.")
    return "\n".join(lines)


def escolher(d: Path, versao: str) -> str:
    out = d / "avaliacao.json"
    if not out.exists():
        raise StudioError("meça as versões antes (`toonstudio musica medir`)")
    av = _json(out)
    if versao not in av["versoes"]:
        raise StudioError(f"versão '{versao}' não medida; medidas: {list(av['versoes'])}")
    av["escolhida"] = versao
    out.write_text(json.dumps(av, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    f = ficha(d)
    f["status"] = "aprovada"
    f["versoes"] = sorted(av["versoes"])
    f["escolhida"] = versao
    (d / "ficha.json").write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    arq = av["versoes"][versao]["arquivo"]
    return f"escolhida: {arq} → próximo passo: `toonstudio song import <projeto> {d / 'versoes' / arq}`"


# ───────────────────────── partes da música (F5) ─────────────────────────

INSTRUMENTAL = ("intro", "drum break", "instrumental break", "drum fill", "percussion fill", "keyboard fill", "guitar solo", "stop", "end",
                "solo", "break")


def tipo_secao(tag: str) -> str:
    t = tag.lower()
    for chave, tipo in (("intro", "intro"), ("verse", "verso"), ("chorus", "refrao"), ("bridge", "ponte"), ("outro", "final"),
                        ("shout", "bordao"), ("drum fill", "virada"), ("percussion fill", "virada"), ("keyboard fill", "virada"), ("stop", "parada"),
                        ("build", "subida"),
                        ("end", "fim")):
        if t.startswith(chave):
            return tipo
    if "break" in t or "solo" in t:
        return "intervalo"
    return "outro"


def cantor(tag: str) -> list[str]:
    t = tag.lower()
    quem = [n for n in ("laurinha", "luisinho") if n in t]
    if not quem and ("choir" in t or "everybody" in t or "kids" in t or t.startswith("chorus")):
        quem = ["coro"]
    return quem


def secoes(d: Path) -> list[dict]:
    """Partes da letra expandida, em ordem: [{tag, tipo, cantam, linhas}]. Versos soltos antes de qualquer tag vão para 'intro'."""
    E, V = estilos(), vozes()
    f = ficha(d)
    letra = expandir((d / "letra.txt").read_text(encoding="utf-8"), E["ritmos"][f["ritmo"]]["peso"], E, V)
    out: list[dict] = []
    for kind, txt in parse(letra):
        if kind == "tag":
            out.append({"tag": txt, "tipo": tipo_secao(txt), "cantam": cantor(txt), "linhas": []})
        else:
            if not out:
                out.append({"tag": "Intro", "tipo": "intro", "cantam": ["coro"], "linhas": []})
            out[-1]["linhas"].append(txt)
    # linhas que vêm logo depois de uma marcação instrumental (ex.: "(Laurinha e Luisinho!)" num intervalo) são gritos do coro
    for s in out:
        if s["linhas"] and s["tipo"] in ("intervalo", "virada", "parada") and not s["cantam"]:
            s["cantam"] = ["coro"]
    return out
