"""Pós-composição em quadros (PIL): transições entre cenas e tela dividida.

Transições não mudam a duração (a música manda): os primeiros quadros da cena nova se misturam com o último
quadro da cena anterior, segurado. Tipos: deslizar_esq, deslizar_dir, deslizar_cima, deslizar_baixo, cortina,
circulo, zoom, giro.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from ..animation import easing

TRANSITIONS = ("deslizar_esq", "deslizar_dir", "deslizar_cima", "deslizar_baixo", "cortina", "circulo", "zoom", "giro")


def transition_frame(a: Image.Image, b: Image.Image, kind: str, u: float) -> Image.Image:
    """u em [0,1]: 0 = só A, 1 = só B."""
    W, H = a.size
    e = easing.inout_strong(u)
    if kind.startswith("deslizar"):
        dx, dy = {"deslizar_esq": (-1, 0), "deslizar_dir": (1, 0), "deslizar_cima": (0, -1), "deslizar_baixo": (0, 1)}[kind]
        out = Image.new("RGB", (W, H))
        ox, oy = int(dx * W * e), int(dy * H * e)
        out.paste(a, (ox, oy))
        out.paste(b, (ox - dx * W, oy - dy * H))
        # faixa branca entre as duas imagens (o "slider" fica mais gráfico)
        d = ImageDraw.Draw(out)
        if dx:     # costura entre A e B: borda direita de A (indo à esquerda) ou esquerda de A (indo à direita)
            x = ox + W if dx < 0 else ox
            d.rectangle([x - 9, 0, x + 9, H], fill=(255, 255, 255))
        else:
            y = oy + (H if dy < 0 else 0)
            d.rectangle([0, y - 9, W, y + 9], fill=(255, 255, 255))
        return out
    if kind == "cortina":      # limpa na diagonal com borda colorida
        out = a.copy()
        mask = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(mask)
        x = -H + (W + 2 * H) * e
        d.polygon([(-H, 0), (x, 0), (x - H * 0.6, H), (-H, H)], fill=255)
        out.paste(b, (0, 0), mask)
        d2 = ImageDraw.Draw(out)
        d2.line([(x, 0), (x - H * 0.6, H)], fill=(255, 214, 64), width=26)
        d2.line([(x + 18, 0), (x - H * 0.6 + 18, H)], fill=(255, 255, 255), width=10)
        return out
    if kind == "circulo":      # íris abrindo a partir do centro
        out = a.copy()
        mask = Image.new("L", (W, H), 0)
        r = math.hypot(W, H) / 2 * e
        ImageDraw.Draw(mask).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=255)
        out.paste(b, (0, 0), mask)
        ImageDraw.Draw(out).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], outline=(255, 255, 255), width=14)
        return out
    if kind == "zoom":         # A cresce e clareia, B aparece por baixo
        z = 1 + 1.4 * e
        aw, ah = int(W * z), int(H * z)
        az = a.resize((aw, ah)).crop(((aw - W) // 2, (ah - H) // 2, (aw - W) // 2 + W, (ah - H) // 2 + H))
        return Image.blend(az, b, min(1.0, e * 1.3))
    if kind == "giro":         # A gira e encolhe com borrão; B entra girando
        if e < 0.5:
            k = e / 0.5
            img, ang, sc = a, 200 * k, 1 - 0.85 * k
        else:
            k = (e - 0.5) / 0.5
            img, ang, sc = b, -200 * (1 - k), 0.15 + 0.85 * k
        bg = Image.new("RGB", (W, H), (255, 255, 255))
        sm = img.resize((max(1, int(W * sc)), max(1, int(H * sc)))).rotate(ang, expand=True, fillcolor=(255, 255, 255))
        bg.paste(sm, ((W - sm.width) // 2, (H - sm.height) // 2))
        blur = 6 * math.sin(math.pi * e)
        return bg.filter(ImageFilter.GaussianBlur(blur)) if blur > 0.5 else bg
    raise KeyError(f"transição desconhecida: {kind} (disponíveis: {', '.join(TRANSITIONS)})")


def split_frame(panels: list[Image.Image], layout: str, t: float) -> Image.Image:
    """Tela dividida: 'vertical' (lado a lado) ou 'diagonal' (corte inclinado que balança de leve)."""
    W, H = panels[0].size
    out = Image.new("RGB", (W, H), (255, 255, 255))
    a, b = panels[0], panels[1]
    if layout == "vertical":
        out.paste(a.crop((W // 4, 0, W // 4 + W // 2, H)), (0, 0))
        out.paste(b.crop((W // 4, 0, W // 4 + W // 2, H)), (W // 2, 0))
        ImageDraw.Draw(out).rectangle([W // 2 - 8, 0, W // 2 + 8, H], fill=(255, 255, 255))
        return out
    # diagonal: linha que oscila suavemente
    wob = 40 * math.sin(t * 2.2)
    xt, xb = W * 0.58 + wob, W * 0.42 - wob
    out.paste(a, (-int(W * 0.21), 0))            # painel A deslocado: o centro dele cai no meio da metade esquerda
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(xt, 0), (W, 0), (W, H), (xb, H)], fill=255)
    bb = Image.new("RGB", (W, H))
    bb.paste(b, (int(W * 0.21), 0))
    out.paste(bb, (0, 0), mask)
    d = ImageDraw.Draw(out)
    d.line([(xt, -10), (xb, H + 10)], fill=(255, 255, 255), width=22)
    d.line([(xt + 4, -10), (xb + 4, H + 10)], fill=(255, 210, 63), width=7)
    return out


def apply_transition(prev_last: Path, frames: list[Path], kind: str, n: int, out_dir: Path) -> dict[int, Path]:
    """Gera os n primeiros quadros da cena nova misturados com o último da anterior. Retorna {índice: caminho}."""
    a = Image.open(prev_last).convert("RGB")
    out = {}
    out_dir.mkdir(parents=True, exist_ok=True)
    for i in range(min(n, len(frames))):
        u = (i + 1) / (n + 1)
        img = transition_frame(a, Image.open(frames[i]).convert("RGB"), kind, u)
        p = out_dir / f"tr_{frames[i].parent.parent.name}_{i:03d}.png"
        img.convert("RGBA").save(p, compress_level=1)    # mesmo formato dos quadros do Godot (evita reinício no FFmpeg)
        out[i] = p
    return out
