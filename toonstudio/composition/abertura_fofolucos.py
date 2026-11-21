"""Abertura do canal FOFOLUCOS v2 (22/11/2026) — no formato da abertura do Animadinhos, ≤ 5 s.

Análise da referência (Animadinhos, igual em todos os vídeos, ~5,8 s):
  0,0–2,1 s  "roleta": um personagem por vez no centro, troca a cada 0,125 s, cada troca com um "bip" que SOBE de tom
             (escala cromática Dó5 → Lá#6); fundo claro (céu azul-clarinho, nuvens);
  2,1–3,7 s  a roleta PARA no personagem principal, que fica sozinho (resto do som soando);
  3,7 s      a turma inteira ESTOURA na tela em volta dele com um "Uhuuu!" de criança;
  4,6 s      clarão branco → logo com brilhos; ~1 s de logo e entra a música.
Pedido do usuário: "pegar só um efeito simples e mostrar os monstrinhos um por um" → em vez da mini-música do Suno, só
efeitos sintetizados (toonstudio/audio/sfx.py, sem licença a cumprir).
22/11: testada a frase "Fofolucos! RAWR!" do tema (voz isolada e voz + batida) → o usuário REPROVOU ("melhor deixar sem a
voz"). Abertura SEM VOZ NENHUMA.

Linha do tempo (4,7 s): roleta 0,00–2,00 (15 trocas de 4 quadros, bips subindo, termina no Bilu) · Bilu sozinho, carinha
fofinho (plim) · 3,00 estouro: a turma brota das nuvens (boing + pops) e todos fazem RAWR, câmera abre ·
3,70 clarão + logo com brilhos · 4,70 fim.
Uso: PYTHONPATH=. .venv/bin/python -m toonstudio.composition.abertura_fofolucos       (áudio + episode.json)
     PYTHONPATH=. .venv/bin/python -m toonstudio.cli --canal fofolucos build fofolucos/marca-abertura
"""
from __future__ import annotations

import json
import math

import numpy as np
import soundfile as sf

from ..audio import sfx
from ..core.config import PROJECTS

PDIR = PROJECTS / "fofolucos" / "marca-abertura"
SR = sfx.SR
SLOT = 4 / 30                       # 4 quadros por monstrinho na roleta
T0 = 0.0                            # 1ª troca já no 1º quadro (como a referência)
N_ROLETA = 15
POUSA = round(T0 + N_ROLETA * SLOT, 3)          # 2,10: a roleta para no Bilu
ESTOURO = 3.00                       # a turma brota
LOGO = 3.70                          # clarão + logo
DUR = 4.70
ORDEM = ("mimi", "teco", "zuzu", "gogo", "nhoque", "bilu")   # termina no Bilu (protagonista)
ROLETA = [ORDEM[(i - N_ROLETA) % len(ORDEM)] for i in range(N_ROLETA)]
X_ROLETA = 1450
CHAO, FUNDO = 1000, 1750
# estouro em ZIGUE-ZAGUE (frente pé 1000/depth 0,95 · trás pé 905/depth 0,78), 300 entre vizinhos: ninguém tampa ninguém
LUGAR = {"teco": (550, 905, 0.78), "zuzu": (850, 1000, 0.95), "gogo": (1150, 905, 0.78), "bilu": (1450, 1000, 0.95),
         "nhoque": (1750, 905, 0.78), "mimi": (2050, 1000, 0.95)}
BROTA = {"teco": 0.0, "gogo": 0.03, "zuzu": 0.06, "nhoque": 0.09, "mimi": 0.12}


# ───────────────────────────── som ─────────────────────────────
def _bip(f: float) -> np.ndarray:
    """Bip redondinho da roleta: escorrega um pouquinho de cima para a nota (fica "fofo"), some rápido."""
    t = np.arange(int(0.12 * SR)) / SR
    ff = f * (1 + 0.45 * np.exp(-t * 70))
    ph = 2 * np.pi * np.cumsum(ff) / SR
    x = (np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)) * np.minimum(1, t / 0.003) * np.exp(-t * 20)
    return x.astype(np.float32)


def _poe(buf: np.ndarray, x: np.ndarray, t: float, g: float) -> None:
    i = int(round(t * SR))
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += g * x[:n]


def audio() -> np.ndarray:
    """Só efeitos (sem voz, decisão do usuário 22/11)."""
    buf = np.zeros(int(DUR * SR), np.float32)
    for i in range(N_ROLETA):                                    # roleta subindo de tom: Dó5 → Ré6
        _poe(buf, _bip(523.25 * 2 ** (i / 12)), T0 + i * SLOT, 0.42)
    _poe(buf, sfx.plim(), POUSA, 0.55)                           # parou no Bilu
    _poe(buf, sfx.whoosh(), ESTOURO - 0.22, 0.35)                # câmera abrindo
    for cid, d in BROTA.items():                                 # cada um brota com um "pop"
        _poe(buf, sfx.pop(), ESTOURO + d, 0.32)
    _poe(buf, sfx.boing(), ESTOURO, 0.6)                         # o "estouro" da turma (no lugar do "Uhuuu!")
    _poe(buf, sfx.ding(), LOGO, 0.45)                            # clarão + logo
    _poe(buf, sfx.plim(), LOGO + 0.12, 0.5)
    for k, f in enumerate((2637, 3136, 3951, 4699)):             # brilhinhos do logo
        t = np.arange(int(0.25 * SR)) / SR
        _poe(buf, (np.sin(2 * np.pi * f * t) * np.exp(-t * 14)).astype(np.float32), LOGO + 0.35 + 0.11 * k, 0.12)
    n = int(0.12 * SR)
    buf[-n:] *= np.linspace(1, 0, n)
    return (buf * (0.89 / max(1e-6, float(np.abs(buf).max())))).astype(np.float32)


# ───────────────────────────── imagem ─────────────────────────────
def _q(t: float) -> float:
    """Tempo de chave arredondado PARA BAIXO no milésimo: com round() a chave caía 0,3 ms depois do quadro e a roleta
    mostrava 1 quadro vazio entre dois monstrinhos (22/11)."""
    return math.floor(t * 1000 + 1e-6) / 1000


def _monstrinho_cena1(cid: str) -> dict:
    x1, y1, d1 = LUGAR[cid]
    slots = [T0 + i * SLOT for i, c in enumerate(ROLETA) if c == cid]
    keys = [{"t": 0.0, "pose": {"x": X_ROLETA, "y": FUNDO, "depth": 0.95}, "ease": "step"}]
    for k, t in enumerate(slots):
        ultimo = cid == "bilu" and k == len(slots) - 1
        keys += [{"t": _q(t), "pose": {"y": CHAO + 45}, "ease": "step"},
                 {"t": _q(t + 0.07), "pose": {"y": CHAO}, "ease": "back"}]
        if not ultimo:
            keys.append({"t": _q(t + SLOT), "pose": {"y": FUNDO}, "ease": "step"})
    acoes = []
    if cid == "bilu":
        acoes = [{"t": round(POUSA + 0.05, 3), "do": "fofinho", "dur": round(ESTOURO - POUSA - 0.1, 3)},
                 {"t": ESTOURO, "do": "rawr", "dur": round(LOGO - ESTOURO, 3)}]
    else:                                                       # troca de lugar escondido e brota das nuvens no RAWR
        tb = ESTOURO + BROTA[cid]
        keys += [{"t": round(POUSA + 0.05, 3), "pose": {"x": x1, "depth": d1, "y": y1 + 700}, "ease": "step"},
                 {"t": round(tb, 3), "pose": {"y": y1 + 700}, "ease": "step"},
                 {"t": round(tb + 0.2, 3), "pose": {"y": y1}, "ease": "back"}]
        acoes = [{"t": round(tb + 0.18, 3), "do": "rawr", "dur": round(LOGO - tb - 0.18, 3)}]
    keys.sort(key=lambda k: k["t"])
    turn = {"bilu": 0.0, "mimi": -0.15, "teco": 0.15, "zuzu": 0.2, "gogo": -0.2, "nhoque": -0.2}[cid]
    # olhos ABERTOS na roleta (como os rostos da referência); "joy" fecha os olhos
    return {"start": {"x": X_ROLETA, "y": FUNDO, "turn": turn, "expr": "happy", "z": 3 if d1 > 0.9 else 2, "depth": 0.95},
            "exposure": 1, "actions": acoes, "keys": keys}


def _monstrinho_cena2(cid: str, k: int) -> dict:
    x, y, d = LUGAR[cid]
    d2 = DUR - LOGO
    acoes = [{"t": 0.0, "do": "dance", "style": "pulinho", "dur": round(d2, 3)}] if cid != "bilu" else \
        [{"t": 0.0, "do": "wave", "dur": round(d2, 3)}]
    turn = {"bilu": 0.0, "mimi": -0.15, "teco": 0.15, "zuzu": 0.2, "gogo": -0.2, "nhoque": -0.2}[cid]
    return {"start": {"x": x, "y": y, "turn": turn, "expr": "happy", "z": 3 if d > 0.9 else 2, "depth": d}, "exposure": 1,
            "actions": acoes}


def _logo() -> dict:
    ks = [{"t": 0.0, "pose": {"escala": 0.0, "giro": 0.0}, "ease": "step"},
          {"t": 0.03, "pose": {"escala": 0.3}, "ease": "step"},
          {"t": 0.22, "pose": {"escala": 1.32, "giro": 0.04}, "ease": "out"},
          {"t": 0.38, "pose": {"escala": 1.16, "giro": -0.02}, "ease": "inout"},
          {"t": 0.55, "pose": {"escala": 1.22, "giro": 0.0}, "ease": "inout"},
          {"t": round(DUR - LOGO, 3), "pose": {"escala": 1.24}, "ease": "inout"}]
    return {"start": {"x": 1300, "y": 720, "z": 4, "escala": 0.0, "depth": 0.9}, "exposure": 1, "keys": ks}


def episode() -> dict:
    cam1 = {"keys": [{"t": 0, "x": X_ROLETA, "y": 760, "zoom": 1.7},
                     {"t": round(ESTOURO - 0.12, 3), "x": X_ROLETA, "y": 760, "zoom": 1.76, "ease": "inout"},
                     {"t": round(ESTOURO + 0.22, 3), "x": 1300, "y": 540, "zoom": 1.0, "ease": "out"},
                     {"t": LOGO, "x": 1300, "y": 540, "zoom": 1.03, "ease": "inout"}],
            "beat": {"pulse": 0.0, "bar_zoom": 0.0, "sway": 0, "bounce": 0},
            "shake": [{"t": ESTOURO + 0.25, "dur": 0.3, "amp": 9.0}]}
    cam2 = {"keys": [{"t": 0, "x": 1300, "y": 540, "zoom": 1.03}, {"t": round(DUR - LOGO, 3), "x": 1300, "y": 540, "zoom": 1.07, "ease": "inout"}],
            "beat": {"pulse": 0.0, "bar_zoom": 0.0, "sway": 0, "bounce": 0}}
    s1 = {"id": "s01_roleta", "title": "Roleta da turma", "duration": LOGO, "background": "mon_abertura", "camera": cam1,
          "sem_fade_in": True,
          "characters": {cid: _monstrinho_cena1(cid) for cid in LUGAR}}
    s2 = {"id": "s02_logo", "title": "Logo", "duration": round(DUR - LOGO, 3), "background": "mon_abertura", "camera": cam2,
          "flash_in": True, "fx": ["estrelas"],
          "characters": {cid: _monstrinho_cena2(cid, k) for k, cid in enumerate(LUGAR)}, "props": {"logo_fofolucos": _logo()}}
    cast = {cid: {"character": cid} for cid in LUGAR}
    cast["logo_fofolucos"] = {"character": "logo_png"}
    return {"schema": "1.1", "id": "marca-abertura", "projeto": "fofolucos/marca-abertura", "title": "Abertura — Fofolucos (v2)",
            "logline": "Abertura no formato Animadinhos: roleta da turma um por um (bips subindo), para no Bilu, RAWR com a "
                       "turma brotando das nuvens, clarão e logo. Só efeitos + o RAWR do tema.",
            "fps": 30, "resolution": [1920, 1080], "background": "mon_abertura",
            "soundtrack": {"file": "musica/trabalho.wav", "analysis": "analise/song.json", "start": 0.0, "end": DUR,
                           "fade_out": 0.0, "beat_grid": "full"},
            "overlays": {"logo": False}, "cast": cast,
            "approval": {"storyboard": False, "final_render": False}, "scenes": [s1, s2]}


def preparar() -> str:
    (PDIR / "musica").mkdir(parents=True, exist_ok=True)
    (PDIR / "analise").mkdir(parents=True, exist_ok=True)
    sf.write(str(PDIR / "musica" / "trabalho.wav"), audio(), SR)
    beats = [round(T0 + i * SLOT * 2, 3) for i in range(int((DUR - T0) / (SLOT * 2)) + 1)]
    song = {"schema": "song-1.0", "files": {"work": str(PDIR / "musica" / "trabalho.wav")}, "bpm": round(60 / (SLOT * 2), 2),
            "beats": beats, "downbeat_phase": 0, "beat_energy": [1.0] * len(beats), "duration": DUR, "vocal_spans": [],
            "words": [], "lines": [], "sections": [], "lyrics_coverage": None, "musica": None,
            "notes": "abertura sintetizada (abertura_fofolucos.py): sem letra"}
    (PDIR / "analise" / "song.json").write_text(json.dumps(song, ensure_ascii=False, indent=1), encoding="utf-8")
    (PDIR / "canal.txt").write_text("fofolucos", encoding="utf-8")
    (PDIR / "episode.json").write_text(json.dumps(episode(), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(PDIR / "episode.json")


if __name__ == "__main__":
    print(preparar())
