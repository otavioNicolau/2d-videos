"""Placar de melhoria: mede o take de uma música contra a referência (18 músicas da Animadinhos) e registra no histórico.

Uso (depois de `song import` + `song analyze` do take escolhido):
  PYTHONPATH=. .venv/bin/python scripts/referencias/placar.py 15                 # mede e registra
  PYTHONPATH=. .venv/bin/python scripts/referencias/placar.py 15 --nota 4 --obs "batida boa, voz ainda com eco"
  PYTHONPATH=. .venv/bin/python scripts/referencias/placar.py --historico       # tabela de todas as medidas

Processo completo: musicas/PROCESSO_MELHORIA.md. Saídas: musicas/<nº>/placar.json e musicas/MELHORIA.json (histórico).
"""
from __future__ import annotations

import argparse
import json
import re
import statistics as st
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "musicas"
REF = ROOT / "referencias" / "animadinhos" / "analise"
NOS = ROOT / "referencias" / "nossas"
HIST = M / "MELHORIA.json"

FAM = {"teclado_eletronico": ["Keyboard (musical)", "Piano", "Electric piano", "Hammond organ", "Electronic organ", "Synthesizer",
                              "Sampler", "Drum machine"],
       "bateria_banda": ["Drum kit", "Snare drum", "Drum roll", "Rimshot", "Cymbal"],
       "percussao": ["Percussion", "Maraca", "Rattle (instrument)", "Tambourine"],
       "metais": ["Brass instrument", "Trumpet", "Saxophone", "Trombone"]}

# (medida, como ler, alvo mínimo, alvo máximo, o que mexer se falhar)
ITENS = [
    ("voz_%", "voz no som (%)", 35, 48, "voz alta → Style 'vocals level with the beat'; baixa → 'clear lead vocal'"),
    ("bateria_%", "batida no som (%)", 32, 46, "batida fraca → 'strong kick and claps' no começo do Style"),
    ("baixo_%", "baixo no som (%)", 8, 16, "baixo fraco → 'deep bouncy keyboard bass'; Exclude 'weak bass'"),
    ("outros_%", "outros instrumentos (%)", 4, 13, "muita informação → 'minimal, one keyboard melody'; Exclude 'many instruments'"),
    ("largura_voz", "largura da voz (0 = uma voz no centro)", 0.0, 0.06, "voz larga → 'dry centered vocal'; Exclude 'vocal reverb, echo, backing vocals'"),
    ("batidas_identicas", "batida de teclado (loop igual)", 0.90, 1.0, "batida variada → 'one simple keyboard drum loop' no começo; Exclude 'drum variations, percussion ensemble'"),
    ("teclado_eletronico", "teclado/synth reconhecido", 0.04, 1.0, "pouco teclado → 'bright piano / keyboard melody' logo depois do ritmo"),
    ("bateria_banda", "bateria de banda reconhecida", 0.0, 0.04, "bateria de banda → Exclude 'live drums, drum fills, acoustic drums'"),
    ("percussao", "percussão (chocalho/batucada)", 0.0, 0.04, "percussão demais → tirar o nome do ritmo que puxa batucada (usar 'groove')"),
    ("duracao_s", "duração do take (s)", 140, 185, "curta → aumentar a letra (mais uma volta do refrão); longa → cortar o fim"),
]


def nota_item(v, lo, hi):
    if v is None:
        return "—"
    return "ok" if lo <= v <= hi else ("baixo" if v < lo else "alto")


def preparar(n: str) -> tuple[Path, dict]:
    d = next(M.glob(f"{n}_*"))
    proj = next((ROOT / "projects").glob(f"ep{n}-*"))
    nome = proj.name
    wav = proj / "musica" / "trabalho.wav"
    (NOS / "audio").mkdir(parents=True, exist_ok=True)
    for f in (NOS / "audio" / f"{nome}.wav", NOS / "audio" / f"{nome}_full.wav", NOS / "analise" / f"{nome}.json"):
        f.unlink(missing_ok=True)
    stem = NOS / "stems" / "htdemucs" / nome
    if stem.exists():
        subprocess.run(["rm", "-rf", str(stem)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "15", "-t", "60", "-i", str(wav), "-ac", "2", "-ar", "44100",
                    str(NOS / "audio" / f"{nome}.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ac", "1", "-ar", "44100", str(NOS / "audio" / f"{nome}_full.wav")], check=True)
    script = ROOT / "scripts" / "referencias" / "analisar_referencias.py"
    subprocess.run([str(ROOT / ".venv-audio" / "bin" / "python"), str(script), "A", str(NOS)], check=True, capture_output=True)
    subprocess.run([str(ROOT / ".venv" / "bin" / "python"), str(script), "B", str(NOS)], check=True, capture_output=True)
    return d, json.loads((NOS / "analise" / f"{nome}.json").read_text(encoding="utf-8"))


def medidas(a: dict) -> dict:
    m = {"voz_%": a["peso_faixas"]["vocals"], "bateria_%": a["peso_faixas"]["drums"], "baixo_%": a["peso_faixas"]["bass"],
         "outros_%": a["peso_faixas"]["other"], "largura_voz": a.get("largura_voz"), "batidas_identicas": a.get("batidas_identicas"),
         "duracao_s": a.get("duracao_s")}
    for f, ls in FAM.items():
        m[f] = round(max(a["instrumentos"].get(l, 0) for l in ls), 3)
    return m


def referencia() -> dict:
    out = {}
    D = [json.loads(p.read_text(encoding="utf-8")) for p in REF.glob("*.json")]
    for k in [i[0] for i in ITENS]:
        vals = [medidas(x).get(k) for x in D]
        vals = [v for v in vals if v is not None]
        out[k] = round(st.median(vals), 3) if vals else None
    return out


def estilo_usado(d: Path) -> str:
    t = (d / "suno.txt").read_text(encoding="utf-8") if (d / "suno.txt").exists() else ""
    m = re.search(r"ESTILO DO CANAL: (\S+)", t)
    return m.group(1) if m else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("musica", nargs="?")
    ap.add_argument("--nota", type=int, help="sua nota de ouvido, 1 a 5")
    ap.add_argument("--obs", default="")
    ap.add_argument("--estilo", help="versão do Style usada no take (padrão: a do suno.txt)")
    ap.add_argument("--historico", action="store_true")
    a = ap.parse_args()
    hist = json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else []
    if a.historico or not a.musica:
        cols = ["voz_%", "baixo_%", "outros_%", "largura_voz", "batidas_identicas", "teclado_eletronico", "percussao"]
        print("música  estilo  " + "  ".join(c[:10].rjust(10) for c in cols) + "  nota")
        ref = referencia()
        print("REFER.  ------  " + "  ".join(f"{ref[c]:>10}" for c in cols))
        for h in hist:
            print(f"{h['musica']:<7} {h['estilo']:<7} " + "  ".join(f"{h['medidas'].get(c, '—')!s:>10}" for c in cols) + f"  {h.get('nota') or '—'}")
        return
    n = a.musica.zfill(2)
    d, an = preparar(n)
    m = medidas(an)
    ref = referencia()
    est = a.estilo or estilo_usado(d)
    linhas, falhas = [], []
    for k, rotulo, lo, hi, dica in ITENS:
        r = nota_item(m.get(k), lo, hi)
        linhas.append((rotulo, m.get(k), ref.get(k), f"{lo}–{hi}", r))
        if r not in ("ok", "—"):
            falhas.append((rotulo, r, dica))
    ok = sum(1 for l in linhas if l[4] == "ok")
    reg = {"musica": n, "titulo": json.loads((d / "ficha.json").read_text(encoding="utf-8"))["titulo"], "estilo": est,
           "medidas": m, "acertos": f"{ok}/{len(ITENS)}", "nota": a.nota, "obs": a.obs,
           "falhas": [f"{x[0]} ({x[1]})" for x in falhas]}
    (d / "placar.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    hist = [h for h in hist if h["musica"] != n] + [reg]
    hist.sort(key=lambda h: h["musica"])
    HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"PLACAR {n} {reg['titulo']} — estilo {est} — {ok}/{len(ITENS)} dentro do alvo" + (f" — nota {a.nota}" if a.nota else ""))
    print(f"{'medida':40s} {'nossa':>8} {'refer.':>8} {'alvo':>10}  resultado")
    for rotulo, v, r, alvo, res in linhas:
        print(f"{rotulo:40s} {v!s:>8} {r!s:>8} {alvo:>10}  {res}")
    if falhas:
        print("\nPRÓXIMO AJUSTE (um por vez — o primeiro da lista):")
        for rot, res, dica in falhas:
            print(f" - {rot} ({res}): {dica}")


if __name__ == "__main__":
    main()
