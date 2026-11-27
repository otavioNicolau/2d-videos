"""Compila a especificação de um personagem numa cena (chaves + ações + falas) em poses por quadro e em
"desenhos" com exposição (1s/2s), como numa folha de exposição.

Ordem de avaliação de cada instante:
  chaves interpoladas (com easing) → ciclos ativos (mistura suave na entrada/saída) → respiração →
  ação secundária (molas: orelhas, cauda, cabeça) → boca (lip sync) → piscadas automáticas.
"""
from __future__ import annotations

import hashlib
import json
import math
import zlib
from dataclasses import dataclass, field
from typing import Any

from ..characters.base import FACE_NEUTRAL, Character, expression
from . import cycles, easing
from .library import REGISTRY

CATEGORICAL = {"mouth", "back", "holding", "holding_f", "paw_n", "paw_f"}
ROOT = ("x", "y", "z", "depth")


# piscada quadro a quadro (24 fps): meio fechado → fechado → fechado → abrindo (~0,17 s)
BLINK = (0.5, 1.0, 1.0, 0.45)


# teste 26/11 ("movimentos do Fofolucos mais profissionais"): muriçoca só PAIRA quando voa (pés firmes no chão).
# Aprovado pelo usuário 26/11 ("O TESTE FICOU BOM"): virou o PADRÃO. TOONSTUDIO_PAIRA=1 volta ao antigo (paira sempre).
import os as _os
PAIRA_NO_CHAO = _os.environ.get("TOONSTUDIO_PAIRA", "0") == "1"


@dataclass
class Key:
    t: float
    v: Any
    ease: str = "inout"


@dataclass
class Segment:
    t0: float
    t1: float
    kind: str           # walk | sneak | run | flap | dance:<estilo>
    T: float
    blend: float = 0.12
    amp: float = 1.0


@dataclass
class CharTimeline:
    char: Character
    fps: int
    duration: float
    channels: dict[str, list[Key]] = field(default_factory=dict)
    segments: list[Segment] = field(default_factory=list)
    ex_spans: list[tuple[float, float, int]] = field(default_factory=list)
    default_ex: int = 2
    mouth_spans: list[tuple[float, float, list[tuple[float, str]]]] = field(default_factory=list)
    blinks: bool = True
    beats: list[float] = field(default_factory=list)     # grade principal de batidas da música (clipes)

    # ---------------------------------------------------------------- construção
    def add_key(self, t: float, values: dict[str, Any], ease: str = "inout") -> None:
        for k, v in values.items():
            self.channels.setdefault(k, []).append(Key(t, v, ease))

    def finalize(self) -> None:
        for ks in self.channels.values():
            ks.sort(key=lambda k: k.t)

    # ---------------------------------------------------------------- avaliação
    def _interp(self, name: str, t: float, default: Any) -> Any:
        ks = self.channels.get(name)
        if not ks:
            return default
        if t < ks[0].t:
            # antes da primeira chave vale o padrão do personagem: a mudança acontece NA chave (interpolando a partir
            # do padrão), não desde o quadro 0
            if ks[0].t <= 0 or ks[0].ease == "step" or name in CATEGORICAL or not isinstance(ks[0].v, (int, float)):
                return default if ks[0].t > 0 else ks[0].v
            return default
        prev = ks[0]
        for k in ks[1:]:
            if t < k.t:
                if name in CATEGORICAL or not isinstance(k.v, (int, float)) or isinstance(k.v, bool):
                    return prev.v
                if k.ease == "step":
                    return prev.v
                u = (t - prev.t) / max(k.t - prev.t, 1e-6)
                return prev.v + (k.v - prev.v) * easing.get(k.ease)(u)
            prev = k
        return prev.v

    def finalize_defaults(self) -> None:
        """Cada canal que começa depois de 0 ganha uma chave implícita em 0 com o valor padrão (interpola a partir dele)."""
        base = self.char.pose()
        base.update({"x": 0.0, "y": 0.0, "z": 0, "depth": 1.0})
        for name, ks in self.channels.items():
            ks.sort(key=lambda k: k.t)
            if ks and ks[0].t > 0 and name in base:
                ks.insert(0, Key(0.0, base[name], "step"))

    def raw(self, t: float) -> dict[str, Any]:
        base = self.char.pose()
        base.update({"x": 0.0, "y": 0.0, "z": 0, "depth": 1.0})
        p = {k: self._interp(k, t, v) for k, v in base.items()}
        for k in self.channels:
            if k not in p:
                p[k] = self._interp(k, t, 0.0)
        # ciclos
        active = False
        for s in self.segments:
            if s.t0 - s.blend <= t <= s.t1 + s.blend:
                w = 1.0
                if t < s.t0 + s.blend:
                    w = max(0.0, (t - (s.t0 - s.blend)) / (2 * s.blend))
                elif t > s.t1 - s.blend:
                    w = max(0.0, ((s.t1 + s.blend) - t) / (2 * s.blend))
                w = easing.inout(min(1.0, w))
                if s.kind == "flap":
                    ov = cycles.flap(t - s.t0, s.T)
                elif s.kind == "voo":
                    ov = cycles.voo(t - s.t0, s.T)
                elif s.kind.startswith("dance:"):
                    ov = cycles.dance(s.kind[6:], t, self.beats, s.amp, s.t0)
                else:
                    ov = cycles.gait(self.char.id, s.kind, (t - s.t0) / s.T)
                for k, v in ov.items():
                    if k.endswith("+"):                # canal aditivo: soma ao valor da cena (ex.: turn+)
                        base = k[:-1]
                        p[base] = cycles.soma_giro(p.get(base, 0.0), v * w) if base == "turn" else p.get(base, 0.0) + v * w
                        continue
                    if p.get("holding") and (k.startswith("hand_n") or k == "paw_n") and \
                            not (s.kind.startswith("dance:") and s.kind[6:] in cycles.DANCE_WITH_ITEM):
                        continue                      # a mão que segura o objeto não entra no ciclo (exceto passos COM o objeto)
                    if isinstance(v, (int, float)) and k not in CATEGORICAL:
                        p[k] = p.get(k, 0.0) * (1 - w) + v * w
                    elif w > 0.5:
                        p[k] = v
                active = active or w > 0.5
        item_dance = any(s.kind.startswith("dance:") and s.kind[6:] in cycles.DANCE_WITH_ITEM and s.t0 <= t <= s.t1
                         for s in self.segments)
        if p.get("holding") and "hand_n_x" not in self.channels and not item_dance:
            p.update({"hand_n_x": 62.0, "hand_n_y": 38.0, "hand_n_bend": 0.4, "paw_n": 0})    # carrega à frente, na altura da barriga (rosto livre)
        if not active:
            for k, v in cycles.breathe(t).items():
                p[k] = p.get(k, 0.0) + v
        return p

    def evaluate_all(self) -> list[dict[str, Any]]:
        """Poses de todos os quadros (com molas de ação secundária integradas no tempo)."""
        n = int(round(self.duration * self.fps))
        dt = 1.0 / self.fps
        poses = [self.raw(i * dt) for i in range(n)]
        # ação secundária: orelhas/cauda/cabeça respondem à aceleração do corpo (follow-through)
        ear, ear_v, tail, tail_v, hx, hx_v = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        hy, hy_v, hb, hb_v, hat, hat_v = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        bx0 = (poses[0]["x"] + poses[0].get("body_x", 0.0)) if poses else 0.0
        prev_vx, prev_x, prev_by, prev_vy = 0.0, bx0, poses[0].get("body_y", 0.0) if poses else 0.0, 0.0
        for i, p in enumerate(poses):
            f = 1.0 if p["turn"] >= 0 else -1.0
            # corpo inteiro (deslocamento no palco + balanço da dança): a cabeça/cabelo/chapéu respondem a ele
            bx = p["x"] + p.get("body_x", 0.0) * f
            vx = (bx - prev_x) / dt
            ax = (vx - prev_vx) / dt
            vy = (p.get("body_y", 0.0) + p["y"] - prev_by) / dt
            ay = (vy - prev_vy) / dt
            prev_x, prev_vx, prev_by, prev_vy = bx, vx, p.get("body_y", 0.0) + p["y"], vy
            ax, ay = max(-6e4, min(6e4, ax)), max(-6e4, min(6e4, ay))
            for _ in range(2):        # follow-through vertical: cabeça "pesa" ao quicar; cabelo e chapéu atrasam
                h = dt / 2
                hy_a = -160 * hy - 22 * hy_v - 0.0008 * ay
                hy_v += hy_a * h
                hy += hy_v * h
                hb_a = -70 * hb - 6 * hb_v - 0.00012 * ay
                hb_v += hb_a * h
                hb += hb_v * h
                hat_a = -80 * hat - 7 * hat_v - 0.00005 * ax * f
                hat_v += hat_a * h
                hat += hat_v * h
            p["head_dy"] = p.get("head_dy", 0.0) + max(-4, min(4, hy * 12))
            if getattr(self.char, "flies", False) and (PAIRA_NO_CHAO or p.get("fly", 0.0) > 0.5):
                # inseto voador: asas sempre batendo (14 batidas/s), paira, inclina na direção do voo,
                # perninhas ficam para trás quando acelera
                tt = i * dt
                p["wing_phase"] = tt * 14.0
                p["body_y"] = p.get("body_y", 0.0) + 14 * math.sin(2 * math.pi * 0.9 * tt) + 5 * math.sin(2 * math.pi * 2.3 * tt + 1)
                p["body_x"] = p.get("body_x", 0.0) + 6 * math.sin(2 * math.pi * 0.55 * tt + 0.7)
                p["bank"] = max(-0.45, min(0.45, vx * f / 2600.0))
                p["dangle"] = max(-0.6, min(0.8, abs(vx) / 1800.0 + vy / 2500.0))
            elif getattr(self.char, "flies", False):
                p["wing_phase"] = i * dt * 14.0                  # no chão: pés firmes, asas só zumbem no "buzz"
            p["hair_bounce"] = p.get("hair_bounce", 0.0) + max(-0.5, min(0.5, hb * 4))
            p["hat_tilt"] = p.get("hat_tilt", 0.0) + max(-0.3, min(0.3, hat * 2))
            # mola amortecida: k rigidez, c amortecimento, impulsos pela aceleração
            for _ in range(2):
                h = dt / 2
                ear_a = -60 * ear - 7 * ear_v - 0.0009 * ax * f - 0.004 * vy
                ear_v += ear_a * h
                ear += ear_v * h
                tail_a = -45 * tail - 5 * tail_v + 0.0007 * ax * f
                tail_v += tail_a * h
                tail += tail_v * h
                hx_a = -90 * hx - 11 * hx_v - 0.002 * ax * f
                hx_v += hx_a * h
                hx += hx_v * h
            p["ear_swing"] = p.get("ear_swing", 0.0) + max(-0.9, min(0.9, ear))
            p["tail_wag"] = p.get("tail_wag", 0.0) + max(-0.8, min(0.8, tail))
            p["head_dx"] = p.get("head_dx", 0.0) + max(-25, min(25, hx * 40))
            # cachorro feliz abana o rabo
            if self.char.id == "caramelo" and p.get("smile", 0) > 0.6:
                p["tail_wag"] += 0.35 * math.sin(i * dt * 2 * math.pi * 3.0)
            # boca: lip sync sobrepõe a boca do roteiro durante a fala
            t = i * dt
            for t0, t1, cues in self.mouth_spans:
                if t0 <= t < t1:
                    m = "X"
                    for ct, cv in cues:
                        if t >= ct:
                            m = cv
                    p["mouth"] = m
                    # cabeça acompanha a fala (pequenos acentos nas vogais abertas)
                    if m in "CDH":
                        p["head_dy"] = p.get("head_dy", 0.0) - 3
                        p["head_tilt"] = p.get("head_tilt", 0.0) + 0.02
            # piscadas automáticas (BLINK quadro a quadro) em intervalos variados, às vezes dupla; sem atropelar
            # pálpebras já fechadas, olhos felizes (^^) ou olhos arregalados
            if self.blinks and p["lid"] < 0.5 and p.get("eye_scale", 1) < 1.2 and p.get("eyes_happy", 0) < 0.5:
                for bt in self.blink_times():
                    k = int((t - bt) * self.fps + 1e-6)
                    if 0 <= k < len(BLINK) and t >= bt:
                        p["lid"] = max(p["lid"], BLINK[k])
                        break
        return poses

    def blink_times(self) -> list[float]:
        """Inícios das piscadas: intervalo sorteado de 2,3 a 4,6 s (semente = personagem + duração da cena, então
        Laurinha e Luisinho nunca piscam juntos nem no mesmo ritmo); 18% das vezes piscada dupla."""
        if getattr(self, "_blinks", None) is None:
            import random
            rng = random.Random(zlib.crc32(f"{self.char.id}:{self.duration:.3f}".encode()))
            out, t = [], rng.uniform(0.5, 2.0)
            while t < self.duration - 0.2:
                out.append(t)
                if rng.random() < 0.18:
                    out.append(t + 0.34)
                t += rng.uniform(2.3, 4.6)
            self._blinks = out
        return self._blinks

    def exposure_at(self, t: float) -> int:
        if self.blinks and any(bt <= t < bt + (len(BLINK) + 0.5) / self.fps for bt in self.blink_times()):
            return 1                                   # piscada em 1s: cada quadro dela aparece (em 2s ela sumia)
        ex = self.default_ex
        for t0, t1, e in self.ex_spans:
            if t0 <= t < t1:
                ex = e
        return ex


def compile_character(char: Character, spec: dict, fps: int, duration: float,
                      mouth_spans: list[tuple[float, float, list[tuple[float, str]]]] | None = None,
                      beats: list[float] | None = None) -> CharTimeline:
    """spec: {"start": {...}, "keys": [{"t", "pose", "expr", "amount", "ease", "in"}], "actions": [{"t", "do", ...}],
    "exposure": 2}

    Semântica de animador: um canal SEGURA o valor até a próxima mudança começar. Uma chave de cena chega em `t`
    depois de uma transição de `in` segundos (padrão 0,25; 0 se ease = step). Uma ação segura todos os canais que
    ela mexe até o seu início — nada "começa a cair" antes da trombada."""
    tl = CharTimeline(char, fps, duration, default_ex=int(spec.get("exposure", 2)), beats=list(beats or []))
    base = char.pose()
    base.update({"x": 0.0, "y": 0.0, "z": 0, "depth": 1.0})
    start = dict(spec.get("start", {}))
    expr0 = start.pop("expr", None)
    init = {"x": 0.0, "y": 0.0, "z": 0, "depth": 1.0}
    if expr0:
        init.update(expression(expr0))
    init.update(start)
    tl.add_key(0.0, init, "step")
    state = {"x": init["x"], "y": init["y"], "turn": init.get("turn", char.defaults.get("turn", 0.5))}

    def hold(names, t0):
        """Chave de "segura" em t0 com o valor vigente (antes da mudança)."""
        tl.finalize()
        vals = {n: tl._interp(n, t0, base.get(n, 0.0)) for n in names}
        tl.add_key(t0, vals, "step")

    events = [("key", float(k["t"]), k) for k in spec.get("keys", [])] + \
             [("act", float(a["t"]), a) for a in spec.get("actions", [])]
    events.sort(key=lambda e: (e[1], 0 if e[0] == "key" else 1))
    for kind, t0, ev in events:
        if kind == "key":
            vals = dict(ev.get("pose", {}))
            if "expr" in ev:
                vals = {**expression(ev["expr"], float(ev.get("amount", 1.0))), **vals}
            ease = ev.get("ease", "inout")
            tr = 0.0 if ease == "step" else float(ev.get("in", 0.25))
            if tr > 0 and t0 - tr > 0:
                hold(vals.keys(), t0 - tr)
            tl.add_key(t0, vals, ease)
            continue
        name = ev["do"]
        if name not in REGISTRY:
            raise KeyError(f"ação desconhecida: {name} (biblioteca: {sorted(REGISTRY)})")
        tl.finalize()
        state["x"] = tl._interp("x", t0, state["x"])
        state["y"] = tl._interp("y", t0, state["y"])
        state["pose"] = {n: tl._interp(n, t0, v) for n, v in base.items()}
        res = REGISTRY[name].fn(char.id, dict(state), ev)
        touched = set().union(*[v.keys() for _, v, _ in res.keys]) if res.keys else set()
        hold(touched, t0)
        for dt_, vals, ease in res.keys:
            tl.add_key(t0 + dt_, vals, ease)
        if res.cycle:
            ckind, T = res.cycle
            tl.segments.append(Segment(t0, t0 + res.dur, ckind, T, amp=float(ev.get("amp", 1.0))))
        if res.ex:
            tl.ex_spans.append((t0, t0 + res.dur + 0.3, res.ex))
        state.update(res.end_state)
    tl.finalize()
    tl.finalize_defaults()
    tl.mouth_spans = mouth_spans or []
    return tl


# ------------------------------------------------------------------ folha de exposição
def drawing_key(p: dict[str, Any]) -> str:
    """Identidade visual de uma pose (o que muda o desenho). Posição no palco não entra."""
    vis = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in p.items() if k not in ROOT}
    return hashlib.sha1(json.dumps(vis, sort_keys=True, default=str).encode()).hexdigest()[:16]


def expose(tl: CharTimeline) -> tuple[list[int], list[dict[str, Any]], list[dict[str, float]]]:
    """Retorna (células por quadro → nº do desenho, poses dos desenhos únicos, posição no palco por quadro).

    A posição no palco acompanha o desenho exposto (segura junto com ele), para o pé não patinar em 2s."""
    poses = tl.evaluate_all()
    cells: list[int] = []
    drawings: list[dict[str, Any]] = []
    index: dict[str, int] = {}
    stage: list[dict[str, float]] = []
    hold_left = 0
    current = 0
    held_root: dict[str, float] = {}
    for i, p in enumerate(poses):
        if hold_left <= 0:
            ex = tl.exposure_at(i / tl.fps)
            key = drawing_key(p)
            if key not in index:
                drawings.append(p)
                index[key] = len(drawings)
            current = index[key]
            held_root = {k: float(p.get(k, 0.0)) for k in ROOT}
            held_root["turn"] = float(p["turn"])
            hold_left = ex
        cells.append(current)
        stage.append(dict(held_root))
        hold_left -= 1
    return cells, drawings, stage
