"""Short vertical (1080×1920) a partir de um clipe já roteirizado — sem refazer o roteiro.

1. Áudio: montagem de partes inteiras da música (cortes nos limites das partes, que já caem na batida), ex.:
   refrão → verso 1 → refrão (o Short abre no gancho: prende nos 2 primeiros segundos). Voz, batidas e letra são
   remontadas junto (boca e legenda continuam sincronizadas).
2. Imagem: os planos do clipe são reaproveitados e adaptados ao quadro vertical — zoom mínimo para cobrir a altura,
   câmera no personagem em foco, dançarinos aproximados, tela dividida vira plano único com os dois.
Sem vinheta (Short começa no refrão). Saída: projeto `<origem>-short`.
Regra dos canais (23/11/2026, usuário): Short de NO MÁXIMO 30 s, um por música, com o trecho mais interessante.
"""
from __future__ import annotations

import copy
import json
import math
import re
from pathlib import Path

import numpy as np
import soundfile as sf

from ..core.config import PROJECTS, StudioError

W, H = 1080, 1920
GRAPHIC = ("danca_", "padrao_", "mon_raios_", "mon_xadrez_", "mon_brilho_")   # fundos gráficos dos dois canais
ENFEITE = ("bolha", "nuvem")
COM_ROSTO = {"carneirinho", "sapo", "gato", "gamba", "pato", "coelhinho", "dino", "robo", "polvo", "elefante", "pinguim",
             "tatu", "siri", "grilo", "barata", "girino", "peixinho", "lua", "sol", "sabonete", "limao_cara", "pao_queijo",
             "gelatina", "plantinha", "nuvem_chule", "joaninha", "formiguinha"}                       # objetos só de ambiente: a câmera vertical não segue


def _zoom_min(bg: str, meta: dict) -> float:
    h = 1240.0 if bg.startswith(GRAPHIC) else float(meta.get("height", 1080))
    return H / h + 0.03


FRENTE = ("laurinha", "luisinho")                       # dupla do canal: sempre na fileira da frente


def _final_x(c: dict) -> float:
    x = c["start"]["x"]
    for a in c.get("actions", []):
        if "to_x" in a:
            x = a["to_x"]
    return x


def _move(c: dict, nx: float, ny: float | None = None, depth: float | None = None, z: int | None = None) -> None:
    """Leva o personagem para que TERMINE o plano em nx (quem anda/voa mantém o trajeto relativo)."""
    st = c["start"]
    dx = nx - _final_x(c)
    st["x"] += dx
    dy = 0.0 if ny is None else ny - st["y"]
    if ny is not None:
        st["y"] = ny
    for a in c.get("actions", []):
        if "to_x" in a:
            a["to_x"] += dx
        if "to_y" in a:
            a["to_y"] += dy
    if depth is not None:
        st["depth"] = depth
    if z is not None:
        st["z"] = z


def _trajeto(c: dict) -> list[tuple[float, float]]:
    """(t, x) do personagem ao longo do plano — a câmera vertical acompanha quem anda ou voa."""
    pts, x = [(0.0, c["start"]["x"])], c["start"]["x"]
    for a in sorted(c.get("actions", []), key=lambda a: a.get("t", 0.0)):
        if "to_x" in a:
            t0 = float(a.get("t", 0.0))
            pts += [(t0, x), (t0 + float(a.get("dur", 1.0)), a["to_x"])]
            x = a["to_x"]
    out = []
    for t, x in pts:
        if not out or t - out[-1][0] > 0.05:
            out.append((t, x))
    return out


def _fileiras(ws: list[str], chars: dict, centro: float | None = None) -> tuple[list[str], list[str]]:
    """Duas fileiras no quadro estreito. Na frente: quem estava no MEIO da cena 16:9 (o protagonista do plano — ex.: o
    vovô Ciço entre os netos; usuário 23/11: o vovô ficou escondido atrás) e o vizinho mais perto; o resto atrás.
    Sem centro conhecido, vale a dupla do canal (FRENTE)."""
    key = lambda w: _final_x(chars[w])
    dist = (lambda w: abs(key(w) - centro)) if centro is not None else (lambda w: 0.0)
    dupla = sorted([w for w in ws if w in FRENTE], key=dist)
    outros = sorted([w for w in ws if w not in FRENTE], key=dist)
    if centro is not None and outros and (not dupla or dist(outros[0]) + 100 < dist(dupla[0])):
        frente = [outros.pop(0)] + dupla[:1]               # protagonista no meio + o da dupla mais perto
        resto = dupla[1:] + outros
    else:
        frente, resto = dupla[:2], dupla[2:] + outros
    while len(frente) < 2 and resto:
        resto.sort(key=dist)
        frente.append(resto.pop(0))
    return sorted(frente, key=key), sorted(resto, key=key)


def _verticaliza(sc: dict, bgw: dict) -> dict:
    """Adapta um plano 16:9 ao quadro vertical (1080 de largura: cabem 2 personagens lado a lado)."""
    sc = copy.deepcopy(sc)
    if sc.get("panels"):                                   # tela dividida → os dois juntos num plano só
        p0, p1 = sc["panels"]
        chars = {**p0["characters"], **p1["characters"]}
        sc.pop("panels"); sc.pop("layout", None)
        sc["background"] = p0["background"]
        sc["fx"] = p0.get("fx", []) + [f for f in p1.get("fx", []) if f not in p0.get("fx", [])]
        sc["camera"] = p0["camera"]
        sc["characters"] = chars
        sing = p0.get("sing", []) + p1.get("sing", [])
        if sing:
            sc["sing"] = sing
    bg = sc["background"]
    graphic = bg.startswith(GRAPHIC)
    chars = sc.get("characters", {})
    props = {k: v for k, v in sc.get("props", {}).items()
             if (sc.get("cast", {}).get(k, {}).get("character") or k) not in ENFEITE and k not in ("bo", "nv")}
    cantam = {s.get("who") for s in sc.get("sing", [])}
    # quem só está parado no fundo sai do quadro estreito (o plano anterior já o mostrou)
    ociosos = [w for w, c in chars.items() if not c.get("actions") and w not in cantam]
    if len(chars) >= 3 and len(ociosos) < len(chars):
        for w in ociosos:
            chars.pop(w)
    # 24/11 (usuário: "não dá pra ver o rosto do carneirinho"): bicho/objeto COM ROSTO é arrumado como personagem
    # (entra na dupla/fileiras e pode ir para a frente), não empurrado para trás da turma como objeto de cenário
    rosto = {k: v for k, v in props.items() if re.sub(r"\d+$", "", k) in COM_ROSTO}
    if rosto:
        props = {k: v for k, v in props.items() if k not in rosto}
        chars = {**chars, **rosto}
    zmin = _zoom_min(bg, bgw.get(bg, {}))
    width = 1920.0 if graphic else float(bgw.get(bg, {}).get("width", 1920))
    vis = W / zmin                                         # largura visível do cenário no quadro vertical
    keys = sc["camera"]["keys"]
    alvo: list[tuple[float, float]] | None = None          # (t, x) da câmera; None = mantém
    ws = sorted(chars, key=lambda w: _final_x(chars[w]))
    if graphic:
        if len(ws) >= 3:                                   # foto de grupo: dupla na frente, convidados atrás e acima
            fr, tr = _fileiras(ws, chars, centro=float(keys[0].get("x", 960)))
            for k, w in enumerate(fr):
                _move(chars[w], 960 + (k - (len(fr) - 1) / 2) * 300, 1190, 1.0, 3)
            for k, w in enumerate(tr):
                _move(chars[w], 960 + (k - (len(tr) - 1) / 2) * 400, 800, 0.85, 2)
        elif len(ws) == 2:
            for k, w in enumerate(ws):
                if -400 < chars[w]["start"]["x"] < 2300:
                    _move(chars[w], 960 + (k - 0.5) * 320)
        elif len(ws) == 1:
            w = ws[0]
            if -400 < chars[w]["start"]["x"] < 2300:
                _move(chars[w], 960 - (90 if props else 0))
                c = chars[w]                               # quem atravessa: caminhada curta (começa dentro do quadro)
                fim = _final_x(c)
                if abs(c["start"]["x"] - fim) > 260:
                    c["start"]["x"] = fim + math.copysign(260, c["start"]["x"] - fim)
        m = vis / 2 - 90                                   # objetos de cena para dentro do quadro
        for pr in props.values():
            pr["start"]["x"] = max(960 - m, min(960 + m, pr["start"]["x"]))
        alvo = [(0.0, 960.0)]
    elif props and not chars:                             # só objetos: câmera no PRINCIPAL (o 1º do plano: o sapo…)
        alvo = [(0.0, next(iter(props.values()))["start"]["x"])]
    elif len(ws) >= 3:
        y0 = chars[ws[0]]["start"]["y"]
        cx = sum(_final_x(chars[w]) for w in ws) / len(ws)
        fr, tr = _fileiras(ws, chars, centro=float(keys[0].get("x", cx)))
        for k, w in enumerate(fr):
            _move(chars[w], cx + (k - (len(fr) - 1) / 2) * 300, y0 + 40, None, 3)
        for k, w in enumerate(tr):
            d = float(chars[w]["start"].get("depth") or 1.0) * 0.75
            _move(chars[w], cx + (k - (len(tr) - 1) / 2) * 300, y0 - 200, d, 2)
        alvo = [(0.0, cx)]
    elif len(ws) == 2:
        cx = sum(_final_x(chars[w]) for w in ws) / 2
        for k, w in enumerate(ws):
            _move(chars[w], cx + (k - 0.5) * 320)
            for a in chars[w].get("actions", []):          # quadro vertical: não sobe até cortar a cabeça
                if a.get("do") == "fly" and "to_y" in a:
                    a["to_y"] = max(float(a["to_y"]), 760.0)
        alvo = [(0.0, cx)]
    elif ws:
        alvo = _trajeto(chars[ws[0]])                      # câmera acompanha quem anda/voa
    if rosto and alvo is not None:                         # bicho de perfil olha para o MEIO do quadro (rosto visível)
        ax = 960.0 if graphic else alvo[0][1]
        for r in rosto.values():
            lado = -1.0 if r["start"]["x"] > ax + 20 else 1.0
            r["start"]["lado"] = lado
            for k in r.get("keys", []):
                if "lado" in k.get("pose", {}):
                    k["pose"]["lado"] = lado
    if props and chars and alvo is not None and not graphic:
        # 24/11: com objeto grande junto (formas, robô, barata de carro…) os personagens ficavam cortados na borda —
        # agora eles se arrumam como sem objeto (dupla/fileiras) e o OBJETO é que vem para dentro do quadro
        ax = alvo[0][1]
        m = vis / 2 - 110
        for pr in props.values():
            pr["start"]["x"] = max(ax - m, min(ax + m, pr["start"]["x"]))
        if len(ws) == 2 and any(abs(pr["start"]["x"] - ax) < 250 for pr in props.values()):
            for k, w in enumerate(ws):                     # objeto no meio: a dupla abre para os lados, objeto atrás
                _move(chars[w], ax + (k - 0.5) * 2 * min(m, 230), None, None, 3)
            for pr in props.values():
                pr["start"]["z"] = min(int(pr["start"].get("z", 1)), 2)
    if alvo is not None:
        base = dict(keys[0])
        keys = []
        for t, x in alvo:
            keys.append({**base, "t": round(t, 3), "x": x, **({"ease": "inout"} if keys else {})})
        if keys[-1]["t"] < sc["duration"] - 1e-3:
            keys.append({**keys[-1], "t": float(sc["duration"])})
        sc["camera"]["keys"] = keys
    for k in sc["camera"]["keys"]:
        z = max(zmin, float(k["zoom"]))
        half_w, half_h = W / 2 / z, H / 2 / z
        if graphic:
            k["x"] = 960
            k["y"] = 620
        else:
            k["x"] = max(half_w + 5, min(width - half_w - 5, k["x"]))
            k["y"] = max(half_h + 5, min(1080 - half_h - 5, k.get("y", 540)))
        k["zoom"] = math.ceil(z * 1000) / 1000           # arredonda PARA CIMA: nunca abaixo do mínimo
    return sc


def _monta_audio(src: Path, trechos: list[tuple[float, float]], out: Path, fade: float = 0.03) -> None:
    a, sr = sf.read(src, dtype="float32")
    pedacos = []
    n = int(fade * sr)
    for t0, t1 in trechos:
        x = a[int(round(t0 * sr)):int(round(t1 * sr))].copy()
        ramp = np.linspace(0, 1, n)
        if x.ndim > 1:
            ramp = ramp[:, None]
        x[:n] *= ramp
        x[-n:] *= ramp[::-1]
        pedacos.append(x)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, np.concatenate(pedacos), sr)


def _arquivo(sdir: Path, f: str) -> Path:
    """Caminho do áudio; projetos antigos guardam o endereço de antes da pasta do canal (projects/epNN-… →
    projects/<canal>/epNN-…): procura o mesmo arquivo dentro do projeto atual."""
    q = Path(f)
    if q.exists():
        return q
    partes = q.parts
    if sdir.name in partes:
        r = sdir.joinpath(*partes[partes.index(sdir.name) + 1:])
        if r.exists():
            return r
    raise StudioError(f"áudio não encontrado: {f}")


def _desloca(sc: dict, delta: float, dur_nova: float) -> None:
    """Desloca todos os eventos do plano em `delta` s (positivo = acontecem mais tarde) e corta o que sai de
    [0, dur_nova]: câmera, chaves e ações de personagens/objetos, letreiros, trechos cantados, tremor e efeitos."""
    def chaves(ks: list) -> list:
        ks = [dict(k, t=round(float(k["t"]) + delta, 3)) for k in ks]
        antes = [k for k in ks if k["t"] < 0]
        dentro = [k for k in ks if 0 <= k["t"] <= dur_nova]
        depois = [k for k in ks if k["t"] > dur_nova]
        if antes and (not dentro or dentro[0]["t"] > 0):
            dentro.insert(0, dict(antes[-1], t=0.0))
        if depois and (not dentro or dentro[-1]["t"] < dur_nova):
            dentro.append(dict(depois[0], t=round(dur_nova, 3)))
        return dentro or ks[:1]

    def acoes(acs: list) -> list:
        out = []
        for a in acs:
            a = dict(a)
            t = float(a.get("t", 0.0)) + delta
            if isinstance(a.get("dur"), (int, float)) and t < 0:
                a["dur"] = round(float(a["dur"]) + t, 3)
                if a["dur"] <= 0.05:
                    continue
            a["t"] = round(max(0.0, t), 3)
            if a["t"] < dur_nova - 0.05:
                out.append(a)
        return out
    cam = sc["camera"]
    cam["keys"] = chaves(cam["keys"])
    if cam.get("shake"):
        cam["shake"] = [dict(x, t=round(float(x["t"]) + delta, 3)) for x in cam["shake"] if 0 <= float(x["t"]) + delta < dur_nova]
    for grupo in ("characters", "props"):
        for c in (sc.get(grupo) or {}).values():
            if c.get("keys"):
                c["keys"] = chaves(c["keys"])
            if c.get("actions"):
                c["actions"] = acoes(c["actions"])
    if sc.get("callouts"):
        cs = []
        for c in sc["callouts"]:
            t = float(c.get("t", 0.0)) + delta
            if t + float(c.get("dur", 1.8)) > 0.4 and t < dur_nova - 0.3:
                cs.append(dict(c, t=round(max(0.0, t), 3)))
        sc["callouts"] = cs
    if sc.get("sing"):
        sc["sing"] = [dict(s, **{"from": round(max(0.0, float(s["from"]) + delta), 3),
                                 "to": round(min(dur_nova - 0.02, float(s["to"]) + delta), 3)})
                      for s in sc["sing"] if min(dur_nova - 0.02, float(s["to"]) + delta) - max(0.0, float(s["from"]) + delta) > 0.1]
    if sc.get("sfx"):
        sc["sfx"] = [dict(x, t=round(float(x["t"]) + delta, 3)) for x in sc["sfx"] if 0 <= float(x["t"]) + delta < dur_nova]
    sc["duration"] = round(dur_nova, 4)


def _envelope(vocais: Path) -> tuple[np.ndarray, float, float]:
    """Energia da voz isolada em janelas de 20 ms (para achar os silêncios entre as frases)."""
    v, sr = sf.read(vocais, dtype="float32")
    v = v.mean(1) if v.ndim > 1 else v
    h = int(0.02 * sr)
    n = len(v) // h
    env = np.sqrt((v[:n * h].reshape(n, h) ** 2).mean(1) + 1e-12)
    return env, 0.02, float(np.percentile(env, 75))


def _quieto(env: np.ndarray, passo: float, ref: float, t0: float, t1: float, lim: float = 0.3) -> bool:
    """Sem voz em [t0, t1] (entre as frases o silêncio é curto: ~0,15 s)."""
    i0, i1 = max(0, int(t0 / passo)), min(len(env), int(math.ceil(t1 / passo)))
    return i1 <= i0 or float(env[i0:i1].max()) < lim * ref


def _vale(env: np.ndarray, passo: float, t0: float, t1: float) -> float:
    """Instante de MENOS voz em [t0, t1] (quando a frase emenda sem silêncio: corta entre as sílabas)."""
    i0, i1 = max(0, int(t0 / passo)), min(len(env), int(t1 / passo))
    return (i0 + int(np.argmin(env[i0:i1]))) * passo if i1 > i0 else t0


def _bordas_no_silencio(novas: list[dict], exatos: list, mapa: list, song: dict, vocais: Path, letra: dict) -> None:
    """Começo e fim do Short no SILÊNCIO entre as frases, pela energia da voz isolada (usuário 24/11: "veja se tem
    outros… com áudio cortado"): começa na batida em silêncio logo antes da 1ª palavra do refrão e termina na batida
    em silêncio depois da última nota — nunca com um pedaço da frase vizinha. Os planos das pontas esticam/encolhem."""
    env, passo, ref = _envelope(vocais)
    beats = song.get("beats", [])
    fase = int(song.get("downbeat_phase", 0) or 0)
    a, _ = exatos[0]
    linhas = [l for l in letra["lines"] if exatos[0][0] - 0.05 <= l["s"] < exatos[0][1]]
    ls = float(linhas[0]["s"]) if linhas else a                  # 1ª linha do refrão: nunca começar depois dela
    # ── começo: batida em silêncio mais perto de `a` (de 1,2 s antes até a 1ª linha)
    cands = [b for b in beats if a - 1.2 <= b <= min(a + 0.3, ls + 0.02) and _quieto(env, passo, ref, b - 0.06, b + 0.06)]
    if not cands:
        grade = [a - 1.2 + k * passo for k in range(int(1.5 / passo))]
        cands = [t for t in grade if t <= ls + 0.02 and _quieto(env, passo, ref, t - 0.04, t + 0.04)]
    if not cands:                                              # emenda sem silêncio: no vale ANTES da 1ª linha
        v = _vale(env, passo, ls - 0.6, ls + 0.02)
        cands = [round(v if env[int(v / passo)] < 0.45 * ref else ls - 0.15, 3)]
    if cands:
        novo_a = round(min(cands, key=lambda b: (abs(b - a) if b <= a + 0.02 else abs(b - a) + 0.5)), 3)
        delta = a - novo_a                                     # >0: começa mais cedo
        if abs(delta) > 1 / 30 and novas[0]["duration"] + delta > 0.6:
            _desloca(novas[0], delta, novas[0]["duration"] + delta)
            exatos[0] = (novo_a, exatos[0][1])
            mapa[0] = (novo_a, mapa[0][1], 0.0)
            for i in range(1, len(mapa)):
                mapa[i] = (mapa[i][0], mapa[i][1], mapa[i][2] + delta)
    # ── fim: silêncio (≥ 0,18 s) mais perto do limite do trecho, entre a última nota e a próxima frase
    t0u, t1u = exatos[-1]
    grade = [t1u - 0.8 + k * passo for k in range(int(2.0 / passo))]
    livres = [t for t in grade if t > t0u + 3 and _quieto(env, passo, ref, t - 0.1, t + 0.04)]
    if livres:
        alvo = min(livres, key=lambda t: abs(t - t1u))
        ini_gap = alvo
        while ini_gap - passo > t0u and _quieto(env, passo, ref, ini_gap - passo - 0.1, ini_gap - passo + 0.04):
            ini_gap -= passo
        fim_gap = alvo
        while _quieto(env, passo, ref, fim_gap - 0.1, fim_gap + passo + 0.04) and fim_gap < t1u + 1.2:
            fim_gap += passo
        bts = [(i, b) for i, b in enumerate(beats) if ini_gap + 0.04 <= b <= fim_gap - 0.06]
        cab = [b for i, b in bts if (i - fase) % 4 == 0]
        novo = round((cab or [b for _, b in bts] or [ini_gap + 0.06])[0], 3)
    else:                                                      # emenda sem silêncio: entre as sílabas
        prox = [float(l["s"]) for l in letra["lines"] if float(l["s"]) > t1u - 0.3 and l not in linhas]
        novo = round(_vale(env, passo, t1u - 0.4, min([t1u + 0.6] + [x - 0.03 for x in prox])), 3)
    if abs(novo - t1u) < 1 / 30:
        return
    fim_short = mapa[-1][2] + (novo - t0u)
    acc, keep = 0.0, []
    for s in novas:
        if acc >= fim_short - 0.4 and keep:
            break
        keep.append(s)
        acc += s["duration"]
    novas[:] = keep
    soma = sum(s["duration"] for s in novas[:-1])
    _desloca(novas[-1], 0.0, fim_short - soma)
    exatos[-1] = (t0u, novo)
    mapa[-1] = (t0u, novo, mapa[-1][2])


def _divide_longos(novas: list[dict], bgw: dict, beats: list[float], max_dur: float = 4.5) -> list[dict]:
    """Plano longo e parado deixa o Short "genérico" (usuário 24/11, Fofolucos 04 e Laurinha antigas): todo plano com
    mais de `max_dur` s vira pedaços de ~3 s cortados NA BATIDA, alternando o quadro aberto com CLOSES em cada
    personagem do plano (as ações continuam no mesmo tempo da música)."""
    out, t0 = [], 0.0
    for sc in novas:
        d = float(sc["duration"])
        chars = [w for w, c in (sc.get("characters") or {}).items() if c.get("start")]
        if d <= max_dur or not chars or sc.get("panels"):
            out.append(sc)
            t0 += d
            continue
        n = max(2, round(d / 3.0))
        cortes = [0.0]
        for k in range(1, n):
            alvo = d * k / n
            bs = [b - t0 for b in beats if 1.2 <= b - t0 <= d - 1.2]
            c = min(bs, key=lambda b: abs(b - alvo)) if bs else alvo
            if c - cortes[-1] >= 1.2:
                cortes.append(round(c, 3))
        cortes.append(d)
        bg = sc["background"]
        graphic = bg.startswith(GRAPHIC)
        width = 1920.0 if graphic else float(bgw.get(bg, {}).get("width", 1920))
        ordem = sorted(chars, key=lambda w: _final_x(sc["characters"][w]))
        for k in range(len(cortes) - 1):
            a, b = cortes[k], cortes[k + 1]
            p = copy.deepcopy(sc)
            p.pop("flash_in", None) if k else None
            p.pop("transition_in", None) if k else None
            _desloca(p, -a, b - a)
            if k % 2 == 1:                                  # close no personagem da vez
                w = ordem[(k // 2) % len(ordem)]
                cx = _final_x(sc["characters"][w])
                z = 2.0 if graphic else 2.4
                half_w = W / 2 / z
                cx = max(half_w + 5, min(width - half_w - 5, cx))
                y = 760.0 if graphic else 560.0
                p["camera"]["keys"] = [{**p["camera"]["keys"][0], "t": 0.0, "x": cx, "y": y, "zoom": z},
                                       {**p["camera"]["keys"][0], "t": round(b - a, 3), "x": cx, "y": y, "zoom": round(z * 1.04, 3),
                                        "ease": "inout"}]
            out.append(p)
        t0 += d
    for i, s in enumerate(out):
        s["id"] = f"s{i + 1:02d}" + (s["id"][3:] if len(s["id"]) > 3 else "")
    return out


def _fim_no_ritmo(novas: list[dict], exatos: list[tuple[float, float]], mapa: list, song: dict, letra: dict) -> None:
    """O Short termina NO RITMO, sem cortar a voz (usuário 23/11: "no final pegue o ritmo pra evitar cortar a voz"):
    o fim vai para a 1ª batida depois da última palavra cantada do trecho (de preferência a cabeça do compasso) e antes
    da próxima voz da música. Se a voz ainda soa no limite do trecho, o último plano é esticado até essa batida; se
    acaba antes, os planos do fim são encurtados."""
    t0u, t1u = exatos[-1]
    palavras = [w for l in letra["lines"] for w in l.get("words", [])]
    ws = [w for w in palavras if t0u - 0.05 <= w["s"] < t1u]
    if not ws or not novas:
        return
    fim_voz = max(w["e"] for w in ws)
    prox = min([w["s"] for w in palavras if w["s"] > fim_voz + 0.05] or [song["duration"]])
    limite = min(prox - 0.1, song["duration"] - 0.05)
    beats, fase = song.get("beats", []), int(song.get("downbeat_phase", 0) or 0)
    cands = [(i, b) for i, b in enumerate(beats) if fim_voz + 0.15 <= b <= limite]
    cabeca = [b for i, b in cands if (i - fase) % 4 == 0 and b - fim_voz <= 2.2]
    novo = (cabeca or [b for _, b in cands] or [min(limite, fim_voz + 0.4)])[0]
    novo = round(max(novo, fim_voz + 0.12), 3)
    if abs(novo - t1u) < 1 / 30:
        return
    fim_short = mapa[-1][2] + (novo - t0u)                  # novo fim na linha do tempo do Short
    acc, keep = 0.0, []
    for s in novas:
        if acc >= fim_short - 0.4 and keep:                 # sobra < 0,4 s: vai para o plano anterior
            break
        keep.append(s)
        acc += s["duration"]
    novas[:] = keep
    soma = sum(s["duration"] for s in novas[:-1])
    ult = novas[-1]
    ult["duration"] = round(fim_short - soma, 4)
    ult["camera"]["keys"] = [k for k in ult["camera"]["keys"] if k["t"] <= ult["duration"]] or ult["camera"]["keys"][:1]
    for u in [ult, *ult.get("panels", [])]:               # trechos cantados e letreiros não passam do novo fim
        if u.get("sing"):
            u["sing"] = [{**sg, "to": round(min(float(sg["to"]), ult["duration"] - 0.02), 3)}
                         for sg in u["sing"] if float(sg["from"]) < ult["duration"] - 0.1]
        if u.get("callouts"):
            u["callouts"] = [c for c in u["callouts"] if float(c.get("t", 0.0)) < ult["duration"] - 0.2]
    exatos[-1] = (t0u, novo)
    mapa[-1] = (t0u, novo, mapa[-1][2])


def criar_short(src_project: str, partes: list[list[str]]) -> Path:
    """partes: cada item é uma lista de blocos CONTÍGUOS (ex.: [["refrao#1"], ["verso#1", "refrao#1"]])."""
    from ..backgrounds import registry
    from .clip_draft import blocos
    sdir = PROJECTS / src_project
    ep = json.loads((sdir / "episode.json").read_text(encoding="utf-8"))
    song = json.loads((sdir / "analise" / "song.json").read_text(encoding="utf-8"))
    letra = json.loads((sdir / "analise" / "letra.json").read_text(encoding="utf-8"))
    bl, occ = [], {}
    for b in blocos(song):
        occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
        bl.append({**b, "nome": f"{b['tipo']}#{occ[b['tipo']]}"})
    por_nome = {b["nome"]: b for b in bl}
    trechos = []
    for grupo in partes:
        try:
            trechos.append((por_nome[grupo[0]]["s"], por_nome[grupo[-1]]["e"]))
        except KeyError as e:
            raise StudioError(f"parte {e} não existe; partes: {list(por_nome)}")
    # planos do clipe dentro de cada trecho (os limites dos planos coincidem com os das partes)
    t, faixas = 0.0, []
    for s in ep["scenes"]:
        faixas.append((t, t + s["duration"], s))
        t += s["duration"]
    bgw = {}
    novas, tl, mapa = [], 0.0, []                          # mapa: (t0 origem, t1 origem, t0 no short)
    exatos = []
    for (t0, t1) in trechos:
        tol = 0.05                                         # planos começam em quadros inteiros (1/30 s)
        sel_f = [(a, b, s) for a, b, s in faixas if a >= t0 - tol and b <= t1 + tol]
        if not sel_f or abs(sel_f[0][0] - t0) > tol or abs(sel_f[-1][1] - t1) > tol:
            raise StudioError(f"os planos não coincidem com o trecho {t0:.2f}–{t1:.2f}s")
        t0, t1 = sel_f[0][0], sel_f[-1][1]                 # tempos EXATOS dos planos: áudio e imagem alinhados
        exatos.append((t0, t1))
        sel = [s for _, _, s in sel_f]
        mapa.append((t0, t1, tl))
        for k, s in enumerate(sel):
            for u in [s, *s.get("panels", [])]:
                b = u.get("background")
                if b and b not in bgw:
                    bgw[b] = registry.ensure(b)
            v = _verticaliza(s, bgw)
            v["id"] = f"s{len(novas) + 1:02d}" + v["id"][3:]
            if not novas:
                v.pop("transition_in", None)
                v["flash_in"] = True
            elif k == 0:
                v["transition_in"] = {"type": "zoom", "dur": 0.4}
            novas.append(v)
        tl += t1 - t0
    _bordas_no_silencio(novas, exatos, mapa, song, _arquivo(sdir, song["files"]["vocals"]), letra)
    did = f"{src_project}-short"
    ddir = PROJECTS / did
    (ddir / "musica").mkdir(parents=True, exist_ok=True)
    (ddir / "analise").mkdir(parents=True, exist_ok=True)
    trechos = exatos

    _monta_audio(_arquivo(sdir, song["files"]["work"]), trechos, ddir / "musica" / "trabalho.wav")
    _monta_audio(_arquivo(sdir, song["files"]["vocals"]), trechos, ddir / "analise" / "vocals.wav")

    def remap(t: float) -> float | None:
        for a, b, d in mapa:
            if a - 1e-3 <= t < b + 1e-3:
                return round(t - a + d, 3)
        return None
    beats = [x for x in (remap(b) for b in song["beats"]) if x is not None]
    beats = sorted(set(beats))
    linhas = []
    for a, b, d in mapa:
        for l in letra["lines"]:
            if a - 0.05 <= l["s"] < b - 0.05:
                linhas.append({**l, "s": round(l["s"] - a + d, 3), "e": round(min(l["e"], b) - a + d, 3),
                               "words": [{**w, "s": round(w["s"] - a + d, 3), "e": round(min(w["e"], b) - a + d, 3)}
                                         for w in l["words"]]})
    novas[:] = _divide_longos(novas, bgw, beats)
    total = round(sum(s["duration"] for s in novas), 4)
    if total > 30.05:                                      # usuário, 23/11: Shorts de no máximo 30 s
        raise StudioError(f"o Short ficou com {total:.1f}s (máximo 30 s): escolha partes menores")
    song2 = {"schema": "song-1.0", "files": {"work": str(ddir / "musica" / "trabalho.wav"),
                                              "vocals": str(ddir / "analise" / "vocals.wav")},
             "bpm": song["bpm"], "beats": beats, "downbeat_phase": song.get("downbeat_phase", 0), "duration": total,
             "lines": [{k: v for k, v in l.items() if k != "words"} for l in linhas], "sections": [],
             "words": [w for l in linhas for w in l["words"]],                      # boca cantada (Rhubarb) por trecho
             "notes": f"montagem do Short a partir de {src_project}: " + ", ".join(f"{a:.2f}–{b:.2f}s" for a, b in trechos)}
    (ddir / "analise" / "song.json").write_text(json.dumps(song2, ensure_ascii=False, indent=1), encoding="utf-8")
    (ddir / "analise" / "letra.json").write_text(json.dumps({"source": letra.get("source"), "lines": linhas},
                                                            ensure_ascii=False, indent=1), encoding="utf-8")
    ep2 = {**{k: v for k, v in ep.items() if k not in ("scenes",)}, "id": Path(did).name, "title": ep["title"] + " — Short",
           "resolution": [W, H], "scenes": novas,
           "soundtrack": {**ep["soundtrack"], "start": 0.0, "end": total, "fade_out": 0.3},
           "approval": {"storyboard": False, "final_render": False}}
    (ddir / "episode.json").write_text(json.dumps(ep2, ensure_ascii=False, indent=2), encoding="utf-8")
    return ddir
