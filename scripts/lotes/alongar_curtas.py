"""Músicas no jeito da referência com estimativa abaixo de 150 s ganham mais uma volta do refrão no fim
(referência: mediana 2:47; o Suno costuma entregar ~0,85–1,1× a estimativa)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from toonstudio.audio import composer as c  # noqa: E402

for d in sorted(c.todas()):
    f = c.ficha(d)
    if "jeito da referência" not in f.get("revisao", ""):
        continue
    est = c.checar(d).metricas["duracao_estimada"]
    t = (d / "letra.txt").read_text(encoding="utf-8")
    if est >= 150 or "[Chorus - faster" in t:
        continue
    m = re.search(r"(\[Virada\]\n\[Chorus - louder\]\n(?:.+\n)+)", t)
    linhas = m.group(1).split("\n", 2)[2]
    t = t.replace(m.group(1), m.group(1) + "\n[Chorus - faster, everybody dancing]\n" + linhas)
    (d / "letra.txt").write_text(t, encoding="utf-8")
    print(d.name, f"{est:.0f} →", f"{c.checar(d).metricas['duracao_estimada']:.0f} s")
