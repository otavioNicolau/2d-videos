"""Placar de ANIMAÇÃO: mede como a Laurinha e o Luisinho se MEXEM num vídeo (braços, pernas, corpo, dança, batida).

Pedido do usuário (19/11/2026): "preciso de um processo de melhoria da animação — movimentos das danças, braços,
pernas — a cada vídeo". Sem render: recompila a atuação de cada cena (a mesma conta do pipeline) e lê a pose quadro a
quadro.

Uso:
  PYTHONPATH=. .venv/bin/python scripts/referencias/placar_animacao.py 19                      # mede e registra
  PYTHONPATH=. .venv/bin/python scripts/referencias/placar_animacao.py 19 --nota 4 --obs "braço duro no refrão"
  PYTHONPATH=. .venv/bin/python scripts/referencias/placar_animacao.py --historico
Histórico: musicas/MELHORIA_ANIMACAO.json · versões da animação (A1, A2…): musicas/PROCESSO_MELHORIA.md
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from toonstudio.animation.timeline import compile_character, expose  # noqa: E402
from toonstudio.core.config import PROJECTS  # noqa: E402
from toonstudio.core.registry import character  # noqa: E402
from toonstudio.render.pipeline import Episode  # noqa: E402

sys.path.insert(0, str(ROOT))
from toonstudio.core.canal import atual as _canal_atual   # multicanal (20/11/2026): TOONSTUDIO_CANAL=fofolucos …
M = _canal_atual().musicas
PJ_CANAL = _canal_atual().projetos
HIST = M / "MELHORIA_ANIMACAO.json"
CAST = tuple(_canal_atual().protagonistas) or ("laurinha", "luisinho")
VERSAO_ATUAL = "A3"           # versão da biblioteca de animação (subir a cada ajuste; registrar em PROCESSO_MELHORIA.md)

# (medida, rótulo, mínimo, máximo, o que mexer)
ITENS = [
    ("braco_amp", "braços: alcance médio na dança (u)", 110, 999, "passos com braço por cima da cabeça / bem aberto; menos 'mão na cintura'"),
    ("braco_vel", "braços: velocidade média na dança (u/s)", 160, 999, "mais batidas com braço (palmas, apontar, V alternado)"),
    ("perna_amp", "pernas: alcance médio na dança (u)", 40, 999, "joelho alto, passo lateral, pezinho batendo"),
    ("corpo_amp", "corpo: balanço (sobe/desce + lado)", 30, 999, "agachar na batida, balançar o quadril"),
    ("estilos", "estilos de dança diferentes no vídeo", 6, 99, "um passo novo por refrão; refrão 3 diferente do 1"),
    ("estilo_max_pct", "% do tempo de dança no estilo mais usado", 0, 35, "trocar o estilo a cada plano de dança"),
    ("desenhos_s", "desenhos diferentes por segundo (vida)", 14, 99, "movimento secundário: antena, asa, cabeça em contraponto"),
    ("parado_pct", "% do tempo em cena PARADO (> 1 s sem mudar)", 0, 8, "respiração, piscada, peso de um pé pro outro"),
    ("sincronia_pct", "% das batidas com 'acento' do movimento (±2 quadros)", 75, 100, "acento (parada brusca/mudança) NA batida"),
]


def _poses(tl) -> list[dict]:
    cells, drawings, _stage = expose(tl)
    return [drawings[c - 1] for c in cells]


def medir(n: str) -> dict:
    proj = next(PJ_CANAL.glob(f"ep{n}-*"))
    ep = Episode(proj.name)
    song = ep.song()
    fps = ep.fps
    hand, foot, body = [], [], []
    vel = []
    estilos: dict[str, float] = {}
    desenhos = quadros = parado = 0
    batidas = acentos = 0
    offset = 0.0
    scenes = []
    for s in ep.ep["scenes"]:
        for sub in (s.get("panels") or [s]):
            scenes.append((sub, offset, s["duration"]))
        offset += s["duration"]
    for s, off, dur in scenes:
        g0 = ep.ep["soundtrack"]["start"] + off if song else 0.0
        beats = [b - g0 for b in song["grid"] if -2 <= b - g0 <= dur + 2] if song else []
        for who in CAST:
            spec = (s.get("characters") or {}).get(who)
            if not spec:
                continue
            tl = compile_character(character(ep.ep["cast"][who]["character"]), spec, fps, dur, [], beats=beats)
            P = _poses(tl)
            nfr = len(P)
            if nfr < 2:
                continue
            cells, drawings, _ = expose(tl)
            desenhos += len(drawings)
            quadros += nfr
            hx = np.array([[p.get("hand_n_x", 0), p.get("hand_n_y", 0), p.get("hand_f_x", 0), p.get("hand_f_y", 0)] for p in P], float)
            fx = np.array([[p.get("foot_n_x", 0), p.get("foot_n_y", 0), p.get("foot_f_x", 0), p.get("foot_f_y", 0)] for p in P], float)
            bx = np.array([[p.get("body_x", 0), p.get("body_y", 0), 300 * p.get("rot", 0), 200 * p.get("lean", 0)] for p in P], float)
            # parado: trechos > 1 s em que o desenho não muda (estátua é de propósito: não conta)
            est = [(a["t"], a["t"] + (dur - a["t"] if a.get("dur") == "resto" else float(a.get("dur", 2.0))))
                   for a in spec.get("actions", []) if a["do"] == "estatua"]
            run = 0
            for i in range(1, nfr):
                t = i / fps
                if cells[i] == cells[i - 1] and not any(a <= t <= b for a, b in est):
                    run += 1
                else:
                    if run > fps:
                        parado += run
                    run = 0
            if run > fps:
                parado += run
            for a in spec.get("actions", []):
                if a["do"] != "dance":
                    continue
                t0 = float(a["t"])
                t1 = dur if a.get("dur") == "resto" else min(dur, t0 + float(a.get("dur", 2.0)))
                i0, i1 = int(t0 * fps), max(int(t0 * fps) + 2, int(t1 * fps))
                if i1 - i0 < fps:
                    continue
                estilos[a.get("style", "bob")] = estilos.get(a.get("style", "bob"), 0) + (t1 - t0)
                for arr, dest in ((hx, hand), (fx, foot), (bx, body)):
                    seg = arr[i0:i1]
                    for j in range(0, len(seg) - fps + 1, fps):          # alcance por segundo
                        w = seg[j:j + fps]
                        dest.append(float(np.mean(w.max(0) - w.min(0))))
                seg = hx[i0:i1]
                sp = np.linalg.norm(np.diff(seg, axis=0).reshape(-1, 2, 2), axis=2).sum(1) * fps / 2
                vel.append(float(np.mean(sp)))
                # sincronia: em cada batida dentro da dança, há mudança brusca de velocidade (acento) a ±2 quadros?
                # acento = mudança brusca de velocidade (top 15 % do trecho); por acaso, uma janela de 5 quadros pega ~55 %
                acc = np.abs(np.diff(sp))
                lim = np.percentile(acc, 85) if len(acc) > 4 else 0
                for b in beats:
                    k = int(round(b * fps)) - i0 - 1
                    if 2 <= k < len(acc) - 2:
                        batidas += 1
                        acentos += bool(acc[k - 2:k + 3].max() >= lim)
    total_d = sum(estilos.values()) or 1
    return {"braco_amp": round(st.mean(hand), 1) if hand else 0, "braco_vel": round(st.mean(vel), 1) if vel else 0,
            "perna_amp": round(st.mean(foot), 1) if foot else 0, "corpo_amp": round(st.mean(body), 1) if body else 0,
            "estilos": len(estilos), "estilo_max_pct": round(100 * max(estilos.values()) / total_d) if estilos else 0,
            "desenhos_s": round(desenhos / max(1, quadros) * fps, 1), "parado_pct": round(100 * parado / max(1, quadros), 1),
            "sincronia_pct": round(100 * acentos / max(1, batidas)), "estilos_usados": dict(sorted(estilos.items(), key=lambda x: -x[1]))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("musica", nargs="?")
    ap.add_argument("--nota", type=float, help="sua nota de olho para a animação, 1 a 5")
    ap.add_argument("--obs", default="")
    ap.add_argument("--versao", default=VERSAO_ATUAL)
    ap.add_argument("--historico", action="store_true")
    a = ap.parse_args()
    hist = json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else []
    cols = [i[0] for i in ITENS]
    if a.historico or not a.musica:
        print("mús vers " + " ".join(c[:9].rjust(9) for c in cols) + "  nota")
        print("ALVO     " + " ".join((f"≥{lo}" if lo > 0 else f"≤{hi}").rjust(9) for _, _, lo, hi, _ in ITENS))
        for h in hist:
            print(f"{h['musica']:<4}{h['versao']:<5}" + " ".join(f"{h['medidas'].get(c, '—')!s:>9}" for c in cols) + f"  {h.get('nota') or '—'}")
        return
    n = a.musica.zfill(2)
    m = medir(n)
    velho = next((h for h in hist if h["musica"] == n), {})
    ant = [h for h in hist if h["musica"] < n][-3:]
    linhas, falhas, piorou = [], [], []
    for k, rot, lo, hi, dica in ITENS:
        v = m[k]
        ok = lo <= v <= hi
        media = round(st.mean(h["medidas"][k] for h in ant), 1) if ant else None
        pior = media is not None and ((v > media) if hi < 99 else (v < media))
        linhas.append((rot, v, media, "ok" if ok else ("ABAIXO" if v < lo else "ACIMA")))
        if not ok:
            falhas.append((rot, dica))
        if pior:
            piorou.append(f"{rot}: {v} (média das 3 anteriores: {media})")
    d = next(M.glob(f"{n}_*"))
    reg = {"musica": n, "titulo": json.loads((d / "ficha.json").read_text(encoding="utf-8"))["titulo"], "versao": a.versao,
           "medidas": m, "acertos": f"{sum(1 for l in linhas if l[3] == 'ok')}/{len(ITENS)}",
           "nota": a.nota if a.nota is not None else velho.get("nota"), "obs": a.obs or velho.get("obs", ""), "piorou": piorou}
    hist = sorted([h for h in hist if h["musica"] != n] + [reg], key=lambda h: h["musica"])
    HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"PLACAR DE ANIMAÇÃO {n} {reg['titulo']} — versão {a.versao} — {reg['acertos']} dentro do alvo"
          + (f" — nota {reg['nota']}" if reg["nota"] else ""))
    print(f"{'medida':55s} {'nosso':>7} {'média 3 ant.':>12}  resultado")
    for rot, v, media, res in linhas:
        print(f"{rot:55s} {v!s:>7} {media!s:>12}  {res}")
    print("estilos de dança (s):", m["estilos_usados"])
    if piorou:
        print("\nPIOROU em relação às 3 anteriores:")
        for p in piorou:
            print(" -", p)
    if falhas:
        print("\nPARA MELHORAR (um ajuste por vídeo — o primeiro da lista ou o que o usuário apontar):")
        for rot, dica in falhas:
            print(f" - {rot}: {dica}")


if __name__ == "__main__":
    main()
