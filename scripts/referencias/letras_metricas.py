"""Medidas de letra (sem guardar letra): versos, palavras por verso, repetição, gancho, comandos, sons, ensino."""
import json, re, sys, glob, statistics as st
from pathlib import Path
CMD = r"\b(pula|pular|mexe|mexer|bate|bater|dan[çc]a|gira|girar|abaixa|levanta|roda|rebola|balan[çc]a|sacode|corre|para|parou|estátua|vai|vem|bora|faz|imita|joga|bota|levanta|senta|anda|marcha|chacoalha|requebra|abre|fecha|segura|solta)\b"
ENS = r"\b(aprender|aprende|ensina|sabia|importante|tem que|precisa|cuidado|devagar também|nunca|sempre|é bom|faz bem|saúde|educação|obrigado|por favor|desculpa)\b"
def som(w):  # onomatopeia/brincadeira sonora: sílaba repetida ou palavra curta repetida
    w = w.lower()
    return bool(re.fullmatch(r"(\w{1,3})\1+\w?", w)) or w in {"tchu","tcha","pa","pá","tum","bum","zum","plim","quá","miau","au","piu","oba","ê","ei","uh","lá","ra","ré","ti","dim","dom","blim","blom","tic","tac","bi","fom"}
def medir(linhas):
    L = [re.sub(r"[^\wÀ-ú' -]", " ", l).lower().split() for l in linhas]
    L = [l for l in L if l]
    words = [w for l in L for w in l]
    txt = [" ".join(l) for l in L]
    distintas = len(set(txt))
    return {"versos": len(L), "palavras": len(words), "pal_por_verso": round(st.median(len(l) for l in L), 1),
            "versos_diferentes": distintas, "repeticao_%": round(100 * (1 - distintas / max(1, len(L)))),
            "vocabulario": len(set(words)), "comandos_por_100": round(100 * len(re.findall(CMD, " ".join(txt))) / max(1, len(words)), 1),
            "sons_por_100": round(100 * sum(som(w) for w in words) / max(1, len(words)), 1),
            "ensino_por_100": round(100 * len(re.findall(ENS, " ".join(txt))) / max(1, len(words)), 2)}
if __name__ == "__main__":
    modo, pasta = sys.argv[1], Path(sys.argv[2])
    res = {}
    if modo == "ref":
        for p in sorted((pasta / "transcricoes").glob("*.json")):
            segs = json.loads(p.read_text(encoding="utf-8"))
            # quebra os segmentos do Whisper em versos curtos (vírgula/!/?/.)
            linhas = [x for s in segs for x in re.split(r"[,!?.…]+", s["t"]) if x.strip()]
            res[p.stem] = medir(linhas)
    else:
        for d in sorted(Path("canais/laurinha/musicas").glob("[0-9][0-9]_*")):
            t = (d / "letra.txt").read_text(encoding="utf-8")
            t = re.sub(r"\[[^\]]*\]", "", t)
            linhas = [x for l in t.splitlines() for x in re.split(r"[,!?.…()]+", l) if x.strip()]
            res[d.name] = medir(linhas)
    for k, v in res.items():
        print(k[:26].ljust(27), v)
    keys = next(iter(res.values())).keys()
    print("MEDIANA".ljust(27), {k: st.median(v[k] for v in res.values()) for k in keys})
