"""Identidade do canal FOFOLUCOS no YouTube: capa (2560×1440), foto de perfil (800×800) e marca d'água (150×150).

Bíblia: canais/fofolucos/BIBLIA_VISUAL.md — chapado sem contorno, traço liso (sem tremor), a turma da Vila Monstrinha
e o logo aprovado (library/brand/fofolucos/logo.png). Medidas do YouTube: a capa só mostra a faixa 1546×423 do centro
no celular, 2560×423 no computador e tudo na TV.
Uso: PYTHONPATH=. .venv/bin/python -m toonstudio.composition.canal_fofolucos
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..characters.base import expression
from ..core.config import LIBRARY
from ..core.registry import character

FONT = str(LIBRARY / "fonts" / "Poppins-ExtraBold.ttf")
BRAND = LIBRARY / "brand" / "fofolucos"
OUT = BRAND / "canal"
W, H = 2560, 1440
SEG = (507, 508, 2053, 931)                 # área segura (aparece em todos os aparelhos)
ROXO = (92, 52, 190)
VILA_DX = 10                                  # desloca as casinhas (nenhum monstrinho na frente de casa da mesma cor)

RAWR = {**expression("joy"), "mouth": "D", "jaw": 0.35, "smile": 0.6, "brow_l": 0.85, "brow_r": 0.85,
        "hand_n_x": -125, "hand_n_y": -115, "hand_n_bend": 0.6, "paw_n": 3,
        "hand_f_x": 125, "hand_f_y": -115, "hand_f_bend": -0.6, "paw_f": 3, "eyes_happy": 0.0, "lid": 0.0}
OLA = {**expression("joy"), "mouth": "D", "smile": 1.0, "eyes_happy": 0.0, "lid": 0.0,
       "hand_f_x": 125, "hand_f_y": -125, "paw_f": 3, "hand_f_bend": -0.5}
FESTA = {**expression("joy"), "mouth": "D", "smile": 1.0, "hand_n_x": -130, "hand_n_y": -130, "hand_n_bend": 0.6, "paw_n": 3,
         "hand_f_x": 130, "hand_f_y": -130, "hand_f_bend": -0.6, "paw_f": 3}


def _mon(cid: str, pose: dict, k: float) -> Image.Image:
    """Monstrinho em alta, traço liso; k = pixels por unidade (mesma escala para todos → tamanhos reais entre eles)."""
    s = character(cid).render(pose, scale=k * 2, jitter=0.0)
    a = s.makeImageSnapshot().toarray()
    im = Image.fromarray(a[..., [2, 1, 0, 3]])
    im = im.crop(im.getbbox())
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)


def _paste(dst: Image.Image, im: Image.Image, cx: float, bottom: float) -> None:
    dst.alpha_composite(im, (int(cx - im.width / 2), int(bottom - im.height)))


def _sombra(dst: Image.Image, cx: float, y: float, w: float) -> None:
    s = Image.new("RGBA", dst.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).ellipse([cx - w / 2, y - w * 0.07, cx + w / 2, y + w * 0.07], fill=(40, 30, 70, 70))
    dst.alpha_composite(s.filter(ImageFilter.GaussianBlur(6)))


def _vila(h: int, chao_y: int, dx: int = 0) -> Image.Image:
    """Céu + a Vila Monstrinha (cenário mon_vila do canal) com a calçada na altura chao_y, repetida na largura."""
    from ..backgrounds import registry
    registry.ensure("mon_vila")
    src = Image.open(LIBRARY / "backgrounds" / "mon_vila" / "layers" / "MG_cena.png").convert("RGBA")
    # na imagem do cenário a calçada fica a ~72 % da altura; escala para a calçada cair em chao_y com as casas baixinhas
    k = h / src.height
    vila = src.resize((int(src.width * k), h), Image.LANCZOS)
    top = int(chao_y - 0.72 * h)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    ceu0, ceu1 = src.getpixel((10, 5)), src.getpixel((10, int(src.height * 0.6)))
    d = ImageDraw.Draw(img)
    alto = tuple(max(0, int(c * 0.86)) for c in ceu0[:3])
    for y in range(max(1, top)):                                   # céu mais fundo no alto → emenda sem degrau no cenário
        t = y / max(1, top)
        d.line([(0, y), (W, y)], fill=tuple(int(alto[c] + (ceu0[c] - alto[c]) * t) for c in range(3)) + (255,))
    x = (W - 2 * vila.width) // 2 + dx
    for i in range(3):
        img.alpha_composite(vila, (x + i * vila.width - vila.width // 2, top))
    chao = src.getpixel((10, src.height - 5))
    d.rectangle([0, top + h, W, H], fill=chao)
    return img


def _nuvem(dst: Image.Image, cx: float, cy: float, r: float) -> None:
    n = Image.new("RGBA", dst.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(n)
    for dx, dy, rr in ((-1.0, 0.25, 0.7), (0.0, 0.0, 1.0), (1.05, 0.2, 0.75), (0.5, 0.45, 0.6), (-0.5, 0.45, 0.6)):
        d.ellipse([cx + dx * r - rr * r, cy + dy * r - rr * r, cx + dx * r + rr * r, cy + dy * r + rr * r], fill=(255, 255, 255, 255))
    dst.alpha_composite(n)


def _texto_pilula(img: Image.Image, txt: str, cx: float, y0: float, size: int) -> float:
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, size)
    tw = d.textlength(txt, font=f)
    hgt = int(size * 1.7)
    d.rounded_rectangle([cx - tw / 2 - 34, y0, cx + tw / 2 + 34, y0 + hgt], radius=hgt // 2, fill=(255, 255, 255), outline=ROXO, width=6)
    d.text((cx - tw / 2, y0 + (hgt - size * 1.25) / 2), txt, font=f, fill=ROXO)
    return y0 + hgt


def capa() -> Path:
    img = _vila(560, 985, dx=VILA_DX)
    for cx, cy, r in ((260, 190, 70), (2300, 260, 60), (1180, 120, 45)):       # fora da área segura (TV)
        _nuvem(img, cx, cy, r)
    logo = Image.open(BRAND / "logo.png").convert("RGBA")
    lw = 780
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    # a turma na faixa do meio (pés na calçada); no celular aparecem o Bilu e a Mimi, no computador os seis
    k = 0.72
    turma = [("teco", {**OLA, "turn": 0.3}, 215), ("gogo", {**FESTA, "turn": 0.25}, 455), ("bilu", {**RAWR, "turn": 0.15}, 650),
             ("mimi", {**RAWR, "turn": -0.15}, 1915), ("zuzu", {**OLA, "turn": -0.25, "hand_n_x": -125, "hand_n_y": -125,
                                                                 "paw_n": 3, "hand_n_bend": 0.5, "hand_f_x": 40, "hand_f_y": 150}, 2105),
             ("nhoque", {**FESTA, "turn": -0.3}, 2345)]
    for cid, pose, cx in turma:
        _sombra(img, cx, SEG[3] - 2, 230)
        _paste(img, _mon(cid, pose, k), cx, SEG[3] + 4)
    _paste(img, logo, W / 2, SEG[1] + 6 + logo.height)                         # logo e frase por cima de tudo
    _texto_pilula(img, "Músicas para cantar e dançar com os monstrinhos!", W / 2, SEG[1] + 22 + logo.height, 36)
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "capa_2560x1440.png"
    img.convert("RGB").save(p, quality=95)
    g = img.copy()
    dg = ImageDraw.Draw(g)
    dg.rectangle(SEG, outline=(255, 0, 0), width=6)                             # celular
    dg.rectangle([0, SEG[1], W, SEG[3]], outline=(255, 200, 0), width=4)        # computador
    g.convert("RGB").resize((1280, 720)).save(OUT / "capa_guia_area_segura.png")
    img.crop(SEG).convert("RGB").save(OUT / "capa_previa_celular.png")
    img.crop((0, SEG[1], W, SEG[3])).convert("RGB").save(OUT / "capa_previa_computador.png")
    return p


def perfil() -> Path:
    """Bilu, o do olhão (o traço que mais se reconhece pequenininho), em close sobre raios laranja."""
    S = 800
    img = Image.new("RGBA", (S, S), (255, 138, 43, 255))
    d = ImageDraw.Draw(img)
    for i in range(18):                                               # raios em leque (assinatura dos fundos do canal)
        a0 = i * 2 * math.pi / 18
        d.polygon([(S / 2, S / 2), (S / 2 + 900 * math.cos(a0), S / 2 + 900 * math.sin(a0)),
                   (S / 2 + 900 * math.cos(a0 + math.pi / 18), S / 2 + 900 * math.sin(a0 + math.pi / 18))], fill=(255, 168, 70, 255))
    pose = {**expression("joy"), "turn": 0.08, "mouth": "D", "smile": 1.0, "eyes_happy": 0.0, "lid": 0.0, "eye_scale": 1.1,
            "hand_n_x": -30, "hand_n_y": 150, "hand_f_x": 30, "hand_f_y": 150}
    bi = _mon("bilu", pose, 2.2)
    # cabeça (com os chifres) enchendo o círculo: o corpo sai por baixo
    _paste(img, bi, S / 2, 80 + bi.height)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S, S], fill=255)
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "perfil_800x800.png"
    img.convert("RGB").save(p)
    prev = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    prev.paste(img, (0, 0), mask)
    prev.save(OUT / "perfil_previa_redonda.png")
    pequeno = prev.resize((98, 98), Image.LANCZOS)                     # como aparece ao lado do nome do canal
    pequeno.save(OUT / "perfil_previa_98px.png")
    return p


def marca_dagua() -> Path:
    im = Image.open(OUT / "perfil_800x800.png").convert("RGBA").resize((150, 150), Image.LANCZOS)
    mask = Image.new("L", (150, 150), 0)
    ImageDraw.Draw(mask).ellipse([2, 2, 148, 148], fill=255)
    out = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    p = OUT / "marca_dagua_150x150.png"
    out.save(p)
    return p


def tudo() -> list[Path]:
    return [capa(), perfil(), marca_dagua()]


if __name__ == "__main__":
    for q in tudo():
        print(q)
