"""Placar de CENA: mede a riqueza visual de um roteiro (musicas/<nº>/roteiro.json) e compara com os anteriores.

Regra do canal (19/11/2026, pedido do usuário: "temos que sempre evoluir"): um roteiro novo só vai para o storyboard se
  1) passa nos mínimos de cada medida (alvos tirados das melhores, 12 e 13), e
  2) não fica abaixo da média das 3 músicas anteriores em nenhuma medida (nunca simplificar).

Uso:
  PYTHONPATH=. .venv/bin/python scripts/referencias/placar_cena.py 19            # mede, compara e registra
  PYTHONPATH=. .venv/bin/python scripts/referencias/placar_cena.py --historico   # tabela 10 → hoje
Histórico: musicas/MELHORIA_CENAS.json. Processo: musicas/PROCESSO_MELHORIA.md (trilha "cena").
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from toonstudio.core.canal import atual as _canal_atual   # multicanal (20/11/2026): TOONSTUDIO_CANAL=fofolucos …
M = _canal_atual().musicas
PJ_CANAL = _canal_atual().projetos
HIST = M / "MELHORIA_CENAS.json"
_PP = _canal_atual().raw.get("placar_principais")         # Fofolucos: sem dupla fixa → a turma toda conta como elenco
PRINCIPAIS = tuple(_PP) if _PP is not None else (tuple(_canal_atual().protagonistas) or ("laurinha", "luisinho"))

# (medida, rótulo, mínimo, máximo, como melhorar)
ITENS = [
    ("planos", "planos (cortes)", 45, 999, "quebrar planos longos: reação em close, detalhe do objeto, plano geral"),
    ("cenarios_reais", "cenários de verdade (fora o fundo de dança)", 4, 99, "a história anda: casa → quintal → rua → festa"),
    ("pct_fundo_danca", "% de planos em fundo de dança", 0, 25, "dançar DENTRO do cenário, com o objeto da história"),
    ("tipos_acao", "tipos de ação diferentes", 24, 999, "atuação que conta a letra: pensar, tropeçar, cochichar, esconder…"),
    ("pct_camera", "% de planos com câmera viva (close/zoom/movimento)", 60, 100, "close na reação, zoom na piada, plano geral na dança"),
    ("tipos_objeto", "tipos de objeto/bicho em cena", 6, 999, "um objeto novo por verso; coadjuvantes (bichos, mamãe, vovó)"),
    ("objetos_animados_pl", "objetos animados por plano", 1.2, 99, "o objeto reage: pula, acende, cai, gira"),
    ("coadjuvantes", "coadjuvantes (fora Laurinha e Luisinho)", 1, 99, "mamãe, vovó, vovô, joaninha, formiguinha, bichos"),
    ("pct_arranjo_repetido", "% de planos com a mesma arrumação do anterior", 0, 15, "trocar lado, altura, profundidade, quem está em cena"),
    ("telas_divididas", "telas divididas (dois lugares ao mesmo tempo)", 2, 99, "dois personagens em lugares diferentes fazendo a mesma coisa; antes × depois"),
    ("sons_pl", "efeitos sonoros por plano (a partir da 19)", 0.8, 99, "cada ação com dono tem som: musicas/EFEITOS_SONOROS.md"),
]
SO_DA_19 = {"sons_pl"}


def _efeitos_ligados() -> bool:
    sys.path.insert(0, str(ROOT))
    from toonstudio.core.config import setting
    return bool(setting("clipe", "efeitos_sonoros", True))


def medir(roteiro: dict) -> dict:
    P = [p for v in roteiro["partes"].values() for p in v]
    n = len(P)
    cen, tipos, tobj, coad = set(), set(), set(), set()
    danca = cam = anim = sons = rep = telas = 0
    prev = None
    for p in P:
        telas += bool(p.get("tela_dividida"))
        c = p.get("cenario")
        c = c if isinstance(c, str) else json.dumps(c)
        if c.startswith(("danca_", "padrao_", "mon_raios_", "mon_xadrez_", "mon_brilho_")):   # fundos gráficos (os dois canais)
            danca += 1
        else:
            cen.add(c)
        subs = [p] + list((p.get("tela_dividida") or {}).get("paineis", []))      # tela dividida: conta o que há em cada metade
        at = {w: a for sb in subs for w, a in (sb.get("atores") or {}).items()}
        for w, a in at.items():
            if w not in PRINCIPAIS:
                coad.add(w)
            for x in a.get("acoes", []):
                tipos.add(x["do"] + (":" + x.get("style", "") if x["do"] == "dance" else ""))
        ob = {f"{i}:{k}": v for i, sb in enumerate(subs) for k, v in (sb.get("objetos") or {}).items()}
        for k, v in ob.items():
            tobj.add(v.get("id", k.split(":", 1)[-1]))
            anim += bool(v.get("keys") or v.get("acoes"))          # A4: objeto que "dança" na batida (bateria) também conta
        cm = p.get("camera") or next((sb.get("camera") for sb in subs[1:] if sb.get("camera")), None)
        if (isinstance(cm, str) and cm.startswith("close")) or \
                (isinstance(cm, dict) and (abs(cm.get("zoom_fim", cm.get("zoom", 1.0)) - cm.get("zoom", 1.0)) > 0.04 or cm.get("zoom", 1.0) >= 1.3)):
            cam += 1
        sons += len(p.get("sons") or [])
        arr = (c, tuple(sorted((w, round(float(a.get("x", 0)) / 300)) for w, a in at.items())),
               tuple(sorted(v.get("id", k) for k, v in ob.items())))
        rep += arr == prev
        prev = arr
    return {"planos": n, "cenarios_reais": len(cen), "pct_fundo_danca": round(100 * danca / n), "tipos_acao": len(tipos),
            "pct_camera": round(100 * cam / n), "tipos_objeto": len(tobj | {c for c in coad}), "objetos_animados_pl": round(anim / n, 2),
            "coadjuvantes": len(coad), "pct_arranjo_repetido": round(100 * rep / n), "sons_pl": round(sons / n, 2),
            "telas_divididas": telas}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("musica", nargs="?")
    ap.add_argument("--historico", action="store_true")
    a = ap.parse_args()
    hist = json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else []
    if a.historico or not a.musica:
        cols = [i[0] for i in ITENS]
        print("mús " + " ".join(c[:9].rjust(9) for c in cols))
        print("ALVO" + " ".join((f"≥{lo}" if lo > 0 else f"≤{hi}").rjust(9) for _, _, lo, hi, _ in ITENS))
        for h in hist:
            print(f"{h['musica']:<4}" + " ".join(f"{h['medidas'].get(c, '—')!s:>9}" for c in cols) + f"  {h['acertos']}")
        return
    n = a.musica.zfill(2)
    d = next(M.glob(f"{n}_*"))
    m = medir(json.loads((d / "roteiro.json").read_text(encoding="utf-8")))
    ant = [h for h in hist if h["musica"] < n][-3:]
    linhas, falhas, piorou = [], [], []
    for k, rot, lo, hi, dica in ITENS:
        v = m[k]
        if k in SO_DA_19 and (int(n) < 19 or not _efeitos_ligados()):
            linhas.append((rot, v, "—", "não conta")); continue
        ok = lo <= v <= hi
        media = round(st.mean(h["medidas"][k] for h in ant), 2) if ant else None
        menor_melhor = hi < 99
        pior = media is not None and ((v > media) if menor_melhor else (v < media))
        linhas.append((rot, v, media, "ok" if ok else ("ABAIXO" if v < lo else "ACIMA")))
        if not ok:
            falhas.append((rot, dica))
        if pior:
            piorou.append(f"{rot}: {v} (média das 3 anteriores: {media})")
    conta = [l for l in linhas if l[3] != "não conta"]
    acertos = f"{sum(1 for l in conta if l[3] == 'ok')}/{len(conta)}"
    reg = {"musica": n, "titulo": json.loads((d / "ficha.json").read_text(encoding="utf-8"))["titulo"], "medidas": m,
           "acertos": acertos, "piorou": piorou}
    hist = sorted([h for h in hist if h["musica"] != n] + [reg], key=lambda h: h["musica"])
    HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"PLACAR DE CENA {n} {reg['titulo']} — {acertos} dentro do alvo")
    print(f"{'medida':52s} {'nosso':>7} {'média 3 ant.':>12}  resultado")
    for rot, v, media, res in linhas:
        print(f"{rot:52s} {v!s:>7} {media!s:>12}  {res}")
    if piorou:
        print("\nPIOROU em relação às 3 anteriores (não pode — refazer antes do storyboard):")
        for p in piorou:
            print(" -", p)
    if falhas:
        print("\nPARA MELHORAR:")
        for rot, dica in falhas:
            print(f" - {rot}: {dica}")
    if int(n) >= 19 and (piorou or falhas):
        sys.exit(1)


if __name__ == "__main__":
    main()
