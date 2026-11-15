"""Storyboard / animatic rápido ANTES do render caro: 3 quadros por plano (início, meio, fim), compostos em Python
com o mesmo modelo de câmera/parallax do Godot, em 960×540. Cada plano tem status de aprovação em storyboard.json.

  toonstudio storyboard <ep>                       → output/storyboard.png + storyboard.json (status "pendente")
  toonstudio board <ep> <cena> aprovar|rejeitar "nota"  → registra a decisão
O build avisa quando há planos rejeitados ou pendentes.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..animation.timeline import compile_character
from ..core.config import LIBRARY
from ..core.registry import character
from ..core.validate import load_background

Image.MAX_IMAGE_PIXELS = None
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
PW, PH = 960, 540


def _camera_at(s, t):
    keys = s["camera"]["keys"]
    from ..animation import easing
    val = (keys[0]["x"], keys[0]["y"], keys[0]["zoom"])
    for a, b in zip(keys, keys[1:]):
        if a["t"] <= t <= b["t"]:
            u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
            e = easing.get(b.get("ease", "inout"))(u)
            return tuple(a[c] + (b[c] - a[c]) * e for c in ("x", "y", "zoom"))
        if t > b["t"]:
            val = (b["x"], b["y"], b["zoom"])
    return val


def panel(ep: dict, s: dict, t: float, layers: list) -> Image.Image:
    W, H = ep["resolution"]
    cx, cy, z = _camera_at(s, t)
    k = PW / W
    out = Image.new("RGBA", (PW, PH), (0, 0, 0, 255))
    vw, vh = W / z, H / z

    def blit(im: Image.Image, wx: float, wy: float, sc: float):
        # (wx, wy) = canto sup. esq. em coordenadas da camada; sc = unidades por pixel da imagem
        x = (wx - (cx - vw / 2)) * z * k
        y = (wy - (cy - vh / 2)) * z * k
        w, h = int(im.width * sc * z * k), int(im.height * sc * z * k)
        if w > 0 and h > 0:
            _paste(out, im.resize((w, h)), int(x), int(y))

    items = []
    for l, im in layers:
        f = l["parallax"]
        off_x = (cx - W / 2) * (1 - f)
        off_y = (cy - H / 2) * (1 - f)
        items.append((l["z"], "bg", (im, off_x, off_y, 1 / l["_scale"])))
    perf = {**s.get("characters", {}), **s.get("props", {})}
    for who, spec in perf.items():
        ch = character(ep["cast"][who]["character"])
        tl = compile_character(ch, spec, ep["fps"], s["duration"])
        p = tl.raw(min(t, s["duration"] - 1e-3))
        im = Image.fromarray(ch.render_array(p, scale=0.5, jitter=0.0), "RGBA")
        items.append((int(spec.get("start", {}).get("z", 1)), "ch",
                      (im, p["x"] - ch.anchor[0] * p.get("depth", 1.0), p["y"] - ch.anchor[1] * p.get("depth", 1.0), 2.0 * p.get("depth", 1.0))))
    for _, _, (im, x, y, sc) in sorted(items, key=lambda i: i[0]):
        blit(im, x, y, sc)
    return out


def _paste(dst: Image.Image, im: Image.Image, x: int, y: int) -> None:
    l, t = max(0, -x), max(0, -y)
    crop = im.crop((l, t, im.width, im.height))
    if crop.width > 0 and crop.height > 0:
        dst.alpha_composite(crop, (max(0, x), max(0, y)))


def build(ep_dir: Path) -> Path:
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    bg = load_background(ep["background"])
    bdir = LIBRARY / "backgrounds" / ep["background"] / "layers"
    layers = []
    for l in bg["layers"]:
        im = Image.open(bdir / l["file"]).convert("RGBA")
        im = im.resize((im.width // 3, im.height // 3))
        layers.append(({**l, "_scale": bg["scale"] / 3}, im))
    status_p = ep_dir / "output" / "storyboard.json"
    status = json.loads(status_p.read_text()) if status_p.exists() else {}
    f = ImageFont.truetype(FONT, 20)
    tw, th = 480, 270
    sheet = Image.new("RGB", (3 * (tw + 8) + 330, len(ep["scenes"]) * (th + 12) + 12), (28, 26, 30))
    d = ImageDraw.Draw(sheet)
    for r, s in enumerate(ep["scenes"]):
        y = 12 + r * (th + 12)
        st = status.setdefault(s["id"], {"status": "pendente", "notes": ""})
        col = {"aprovado": (120, 220, 120), "rejeitado": (240, 110, 100)}.get(st["status"], (240, 210, 120))
        d.text((12, y), s["id"], fill=(255, 255, 255), font=f)
        d.text((12, y + 28), f"{s['duration']}s · {s.get('shot', '')}", fill=(200, 200, 200), font=f)
        d.text((12, y + 56), st["status"].upper(), fill=col, font=f)
        for i, line in enumerate(_wrap(s.get("description", ""), 30)[:7]):
            d.text((12, y + 90 + i * 22), line, fill=(215, 215, 215), font=ImageFont.truetype(FONT, 16))
        for i, frac in enumerate((0.05, 0.5, 0.95)):
            pn = panel(ep, s, frac * s["duration"], layers).convert("RGB").resize((tw, th))
            sheet.paste(pn, (330 + i * (tw + 8), y))
    out = ep_dir / "output"
    out.mkdir(exist_ok=True)
    sheet.save(out / "storyboard.png")
    status_p.write_text(json.dumps(status, indent=2, ensure_ascii=False))
    return out / "storyboard.png"


def decide(ep_dir: Path, scene: str, decision: str, notes: str = "") -> dict:
    p = ep_dir / "output" / "storyboard.json"
    status = json.loads(p.read_text()) if p.exists() else {}
    status[scene] = {"status": {"aprovar": "aprovado", "rejeitar": "rejeitado"}[decision], "notes": notes}
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(status, indent=2, ensure_ascii=False))
    return status[scene]


def _wrap(t: str, n: int) -> list[str]:
    out, cur = [], ""
    for w in t.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])
