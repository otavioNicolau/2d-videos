"""Gera letra.txt + ficha.json de músicas novas a partir de especificações escritas à mão (partes cantadas, cenas, YouTube).

Uso: .venv/bin/python scripts/gerar_musicas.py <arquivo.py com SONGS = [dict(...), ...]>
O esqueleto da letra (bordões, intervalos, viradas, convite do joinha) segue a BIBLIA_MUSICAL; o que é cantado vem da spec.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOZ = {"laurinha": "Laurinha, girl child vocal", "luisinho": "Luisinho, boy child vocal"}
OUTRO = {"luisinho": "laurinha", "laurinha": "luisinho"}


def bloco(tag, linhas):
    return f"[{tag}]\n" + "\n".join(linhas) + "\n"


def letra(s):
    v1 = s["v1_canta"]; v2 = OUTRO[v1]
    ch = s["refrao"] if isinstance(s["refrao"][0], list) else [s["refrao"]] * 3
    trad = ", traditional" if s.get("dp") else ""
    out = [bloco(f"Intro - {s['intro_tag']}", [s["intro"]]),
           bloco(f"Verse - {VOZ[v1]}", s["v1"]),
           "[Virada]\n" + bloco(f"Chorus - kids choir{trad}", ch[0]),
           "[Bordão laurinha]\n[Intervalo 10s]\n(Laurinha e Luisinho!)\n",
           bloco(f"Verse - {VOZ[v2]}", s["v2"]),
           "[Virada]\n" + bloco(f"Chorus - kids choir{trad}", ch[1]),
           bloco(f"Bridge - {s.get('ponte_tag', 'Laurinha gives commands, kids answer')}", s["ponte"])]
    if s.get("parada"):
        out.append("[Stop - silence 2 seconds]\n" + s["parada"] + "\n")
    out.append("[Bordão luisinho]\n[Intervalo 10s]\n")
    out.append("[Virada]\n" + bloco(f"Chorus - kids choir, louder{trad}", ch[2]))
    if s.get("final"):
        out.append(bloco("Chorus - everybody, one more time", s["final"]))
    out.append(bloco("Outro - Laurinha and Luisinho talk to the kids, kids choir answers",
                     [s["gostou"], "Dá um joinha! (Joinha!)", "Chama o papai e a mamãe", "Pra se inscrever no canal! (Zum, zum!)"]))
    out.append(f"[Outro - {s.get('fim_tag', 'one big final hit, hard stop')}]\n{s['tchau']}\n[End]\n")
    return "\n".join(out)


def criar(s, numero=None):
    d = next((p for p in (ROOT / "musicas").glob(f"*_{s['nome']}")), None)
    if d is None:
        r = subprocess.run([str(ROOT / ".venv/bin/python"), "-m", "toonstudio.cli", "musica", "nova", s["nome"], "--titulo", s["titulo"],
                            "--ritmo", s["ritmo"], "--tipo", s["tipo"], "--estrutura", s["estrutura"]],
                           cwd=ROOT, env={"PYTHONPATH": str(ROOT), "PATH": "/usr/bin:/bin"}, capture_output=True, text=True, check=True)
        d = Path(r.stdout.strip().splitlines()[-1])
        if numero is not None:
            alvo = d.parent / f"{numero:02d}_{s['nome']}"
            d.rename(alvo)
            d = alvo
    (d / "letra.txt").write_text(letra(s), encoding="utf-8")
    p = d / "ficha.json"; f = json.loads(p.read_text(encoding="utf-8"))
    v1 = s["v1_canta"]
    f.update({"gancho": s["gancho"], "palavras_tema": s["tema_palavras"], "tema": s["tema"], "dia_a_dia": s["dia_a_dia"],
              "curiosidade": s["curiosidade"], "alternativas": s["alt"], "status": "letra_revisada",
              "cantam": {"verso 1": v1, "refrão": "coro" + (" (cantiga tradicional)" if s.get("dp") else ""), "verso 2": OUTRO[v1],
                         "ponte": s.get("ponte_quem", "comandos, coro responde"), "final": "todo mundo"},
              "cenas": [{"parte": k, "ideia": v} for k, v in s["cenas"]],
              "youtube": {"resumo": s["yt"][0], "resumo_short": s["yt"][1], "curiosidade": s["yt"][2]}})
    if v1 == "luisinho":
        f["persona"] = "luisinho"
    if s.get("data"):
        f["data_comemorativa"] = s["data"]
    if s.get("dp"):
        f["dominio_publico"] = {"tradicional": True, "origem": "cantiga tradicional brasileira (folclore, autor desconhecido)",
                                "trecho_tradicional": s["dp"], "observacao": s.get("dp_obs", "")}
    p.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return d


if __name__ == "__main__":
    ns = {}
    exec(Path(sys.argv[1]).read_text(encoding="utf-8"), ns)
    for s in ns["SONGS"]:
        print(criar(s, s.get("numero")).name)
