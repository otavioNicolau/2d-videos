"""Identidade do canal no YouTube (peças fixas de marca): capa, foto de perfil, marca d'água e miniatura de episódio.

Feitas com as personagens e o logo oficiais (BIBLIA_VISUAL.md), renderizadas em alta resolução. Saída em library/brand/canal/.
Medidas do YouTube: capa 2560×1440 com área segura 1546×423 no centro (aparece em todos os aparelhos); perfil 800×800
(exibido em círculo); marca d'água 150×150; miniatura 1280×720.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from ..backgrounds import registry
from ..characters.base import expression
from ..core.config import LIBRARY
from ..core.registry import character

OUT = LIBRARY / "brand" / "laurinha" / "canal"   # canal padrão; o atual vem de _out()


def _out() -> Path:
    from ..core.canal import atual
    return atual().brand / "canal"
FONT = str(LIBRARY / "fonts" / "Poppins-ExtraBold.ttf")


def _char(cid: str, pose: dict, height: int) -> Image.Image:
    from ..core.canal import atual
    ch = character(cid)
    s = ch.render(pose, scale=2.4, jitter=float(atual().raw.get("tremor_traco", 0.5)))   # Fofolucos: traço liso
    a = s.makeImageSnapshot().toarray()
    im = Image.fromarray(a[..., [2, 1, 0, 3]])
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * height / im.height), height), Image.LANCZOS)


def _logo(width: int) -> Image.Image:
    im = _char("logo", {"escala": 1.0}, 600)
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


def _paste(dst: Image.Image, im: Image.Image, cx: float, bottom: float) -> None:
    dst.alpha_composite(im, (int(cx - im.width / 2), int(bottom - im.height)))


def _texto(d: ImageDraw.ImageDraw, txt: str, cx: float, y: float, size: int, fill, stroke=(255, 255, 255), sw: int | None = None):
    f = ImageFont.truetype(FONT, size)
    w = d.textlength(txt, font=f)
    d.text((cx - w / 2, y), txt, font=f, fill=fill, stroke_width=sw or max(2, size // 9), stroke_fill=stroke)


def _parque(w: int, h: int, x0: float = 0.18) -> Image.Image:
    """Fundo do parque chapado (céu, morros e chão) recortado na proporção pedida."""
    meta = registry.ensure("plano_parque")
    d = LIBRARY / "backgrounds" / "plano_parque" / "layers"
    base = None
    for ly in meta["layers"]:
        im = Image.open(d / ly["file"]).convert("RGBA")
        H = im.height
        W = int(H * w / h)
        x = int((im.width - W) * x0)
        crop = im.crop((x, 0, x + W, H)).resize((w, h), Image.LANCZOS)
        base = crop if base is None else Image.alpha_composite(base, crop)
    return base


def _ceu(w: int, h: int) -> Image.Image:
    meta = registry.ensure("plano_ceu")
    im = Image.open(LIBRARY / "backgrounds" / "plano_ceu" / "layers" / meta["layers"][0]["file"]).convert("RGBA")
    H = im.height
    W = int(H * w / h)
    return im.crop((0, 0, W, H)).resize((w, h), Image.LANCZOS)


ACENA = {**expression("joy"), "turn": 0.2, "mouth": "D", "hand_f_x": 125, "hand_f_y": -120, "paw_f": 3, "hand_f_bend": -0.5}
VOANDO = {**expression("joy"), "turn": -0.25, "mouth": "D", "fly": 1, "wing_phase": 0.4, "buzz": 1,
          "hand_n_x": -120, "hand_n_y": -60, "paw_n": 3, "hand_f_x": 120, "hand_f_y": -60, "paw_f": 3}
CHEGUEI = {**expression("joy"), "turn": 0.15, "mouth": "D", "hand_n_x": -135, "hand_n_y": -135, "hand_n_bend": 0.5, "paw_n": 3,
           "hand_f_x": 135, "hand_f_y": -135, "hand_f_bend": -0.5, "paw_f": 3}


def capa() -> Path:
    W, H = 2560, 1440
    img = _parque(W, H, 0.0)                                       # trecho das árvores; a casinha fica na borda direita
    sol = _char("sol", {"giro": 0.3}, 330)
    _paste(img, sol, 260, 430)                                      # fora da área segura (só TV/computador)
    # área segura: 1546×423 centrada (x 507..2053, y 508..931)
    logo = _logo(700)                                              # inteiro dentro da área segura (topo ≥ 508)
    _paste(img, logo, W / 2, 508 + logo.height)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 50)
    txt = "Músicas para cantar, dançar e aprender!"
    tw = d.textlength(txt, font=f)
    y0 = 508 + logo.height + 8
    d.rounded_rectangle([W / 2 - tw / 2 - 34, y0, W / 2 + tw / 2 + 34, y0 + 84], radius=42, fill=(255, 255, 255),
                        outline=(46, 112, 210), width=6)
    d.text((W / 2 - tw / 2, y0 + 10), txt, font=f, fill=(46, 112, 210))
    la = _char("laurinha", ACENA, 400)
    lu = _char("luisinho", {**ACENA, "turn": -0.2}, 395)
    _paste(img, la, 700, 928)
    _paste(img, lu, 1860, 928)
    _out().mkdir(parents=True, exist_ok=True)
    p = _out() / "capa_2560x1440.png"
    img.convert("RGB").save(p, quality=95)
    g = img.copy()
    dg = ImageDraw.Draw(g)
    dg.rectangle([507, 508, 2053, 931], outline=(255, 0, 0), width=6)
    g.convert("RGB").resize((1280, 720)).save(_out() / "capa_guia_area_segura.png")
    return p


def perfil() -> Path:
    S = 800
    img = Image.new("RGBA", (S, S), (255, 214, 64, 255))
    d = ImageDraw.Draw(img)
    for k in range(16):                                             # raios suaves
        a0 = k * math.pi / 8
        d.polygon([(S / 2, S / 2), (S / 2 + 900 * math.cos(a0), S / 2 + 900 * math.sin(a0)),
                   (S / 2 + 900 * math.cos(a0 + math.pi / 16), S / 2 + 900 * math.sin(a0 + math.pi / 16))], fill=(255, 225, 110, 255))
    baixo = {"hand_n_x": -30, "hand_n_y": 150, "hand_f_x": 30, "hand_f_y": 150}     # braços para baixo, fora do recorte
    la = _char("laurinha", {**expression("joy"), "turn": 0.2, "mouth": "D", **baixo}, 820)
    lu = _char("luisinho", {**expression("joy"), "turn": -0.2, "mouth": "D", **baixo}, 791)
    # close: os dois rostos grandes (leem no ícone pequeno), com antenas e laço inteiros dentro do círculo
    _paste(img, la, 200, 940)
    _paste(img, lu, 600, 940)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S, S], fill=255)
    p = _out() / "perfil_800x800.png"
    img.convert("RGB").save(p)
    prev = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    prev.paste(img, (0, 0), mask)
    prev.save(_out() / "perfil_previa_redonda.png")
    return p


def marca_dagua() -> Path:
    im = Image.open(_out() / "perfil_800x800.png").convert("RGBA").resize((150, 150), Image.LANCZOS)
    mask = Image.new("L", (150, 150), 0)
    ImageDraw.Draw(mask).ellipse([2, 2, 148, 148], fill=255)
    out = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    p = _out() / "marca_dagua_150x150.png"
    out.save(p)
    return p


# raios do fundo da miniatura: cores fortes e variadas (o amarelo sozinho some entre as outras miniaturas)
CORES_RAIOS = [(255, 77, 141), (255, 206, 26), (38, 196, 106), (41, 140, 255), (142, 68, 239), (255, 138, 31)]
TINTA = (30, 30, 60)                                               # contorno escuro do título (lê sobre qualquer cor)


def _pose(spec: dict) -> dict:
    p = dict(spec)
    return {**expression(p.pop("expr", "joy")), **p}


def _ajusta(im: Image.Image, maior: int, giro: float = 0) -> Image.Image:
    r = maior / max(im.size)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    return im.rotate(giro, expand=True, resample=Image.BICUBIC) if giro else im


FUNDOS = ("raios", "faixas", "circulo", "aneis")                   # formato do fundo: muda de um vídeo para o outro


def _halo(img: Image.Image, cx: float, cy: float, r: float = 290, a: int = 170) -> None:
    h = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(h).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    img.alpha_composite(h.filter(ImageFilter.GaussianBlur(60)))


def _fundo(formato: str, cores: list, cx: float, cy: float, W: int, H: int) -> Image.Image:
    """Fundo chapado da miniatura. raios = leque saindo da personagem; faixas = listras diagonais largas;
    circulo = fundo cortado na diagonal com um círculo grande atrás da personagem; aneis = círculos concêntricos."""
    if formato not in FUNDOS:
        raise ValueError(f"fundo de miniatura desconhecido: {formato} (use {FUNDOS})")
    img = Image.new("RGBA", (W, H), cores[0] + (255,))
    d = ImageDraw.Draw(img)
    if formato == "raios":
        n = len(cores) * 2
        for k in range(n):
            a0 = -math.pi / 2 + k * 2 * math.pi / n
            a1 = a0 + 2 * math.pi / n
            d.polygon([(cx, cy), (cx + 2200 * math.cos(a0), cy + 2200 * math.sin(a0)),
                       (cx + 2200 * math.cos(a1), cy + 2200 * math.sin(a1))], fill=cores[k % len(cores)] + (255,))
        _halo(img, cx, cy)
    elif formato == "faixas":
        larg, inc = 190, 0.55                                      # listras inclinadas (sobem para a direita)
        for k in range(-12, 20):
            x0 = k * larg
            d.polygon([(x0, H), (x0 + larg, H), (x0 + larg + H * inc, 0), (x0 + H * inc, 0)], fill=cores[k % len(cores)] + (255,))
        _halo(img, cx, cy, 300, 190)
    elif formato == "circulo":
        d.polygon([(0, 0), (W * 0.62, 0), (W * 0.40, H), (0, H)], fill=cores[0] + (255,))
        d.polygon([(W * 0.62, 0), (W, 0), (W, H * 0.55), (W * 0.52, H * 0.55)], fill=cores[1] + (255,))
        d.polygon([(W * 0.52, H * 0.55), (W, H * 0.55), (W, H), (W * 0.40, H)], fill=cores[3 % len(cores)] + (255,))
        r = 330
        d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=(255, 255, 255, 255))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cores[2 % len(cores)] + (255,))
        _halo(img, cx, cy, 220, 120)
    else:                                                          # aneis
        for i, r in enumerate(range(1500, 0, -120)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cores[i % len(cores)] + (255,))
        _halo(img, cx, cy, 260, 150)
    return img


def miniatura(titulo: str, nome: str, cena: dict | None = None) -> Path:
    """Miniatura 1280×720 no padrão dos canais infantis grandes: raios coloridos, personagem em close à esquerda,
    os objetos da música desenhados grandes e o título no canto superior direito. O canto inferior direito fica
    livre (o YouTube cobre com a duração). `cena` vem da ficha (youtube.miniatura_cena)."""
    W, H = 1280, 720
    cena = cena or {}
    heroi = cena.get("heroi", {"id": "laurinha", "pose": {"turn": 0.2, "mouth": "D", "hand_n_x": -135, "hand_n_y": -135,
                                                          "hand_n_bend": 0.5, "paw_n": 3, "hand_f_x": 135, "hand_f_y": -135,
                                                          "hand_f_bend": -0.5, "paw_f": 3}})
    par = cena.get("par", {"id": "luisinho" if heroi["id"] != "luisinho" else "laurinha",
                           "pose": {"turn": -0.2, "mouth": "D", "hand_n_x": -135, "hand_n_y": -135, "hand_n_bend": 0.5,
                                    "paw_n": 3, "hand_f_x": 135, "hand_f_y": -135, "hand_f_bend": -0.5, "paw_f": 3}})
    cx, cy = cena.get("centro", (430, 430))
    cores = [tuple(c) for c in cena.get("cores", CORES_RAIOS)]
    img = _fundo(cena.get("fundo", "raios"), cores, cx, cy, W, H)
    if par:                                                        # o par fica atrás, à direita, cortado embaixo
        im = _char(par["id"], _pose(par.get("pose", {})), par.get("tam", 600))
        _paste(img, im, par.get("x", 1060), H + par.get("corte", 150))
    for o in cena.get("objetos", []):                              # objetos da música (tam = maior lado em px)
        im = _ajusta(_char(o["id"], o.get("pose", {}), 400), o.get("tam", 300), o.get("giro", 0))
        _paste(img, im, o["x"], o["base"])
    im = _char(heroi["id"], _pose(heroi.get("pose", {})), heroi.get("tam", 760))
    _paste(img, im, heroi.get("x", cx), H + heroi.get("corte", 170))
    for o in cena.get("frente", []):                               # objetos na frente da personagem
        im = _ajusta(_char(o["id"], o.get("pose", {}), 400), o.get("tam", 300), o.get("giro", 0))
        _paste(img, im, o["x"], o["base"])
    espelho = cena.get("lado") == "direita"                       # destaque à direita e título à esquerda
    if espelho:
        img = ImageOps.mirror(img)
    d = ImageDraw.Draw(img)
    y = 30
    for i, l in enumerate(titulo.split("\n")):
        size = 104 if len(l) <= 10 else 88
        f = ImageFont.truetype(FONT, size)
        x = 40 if espelho else W - 40 - d.textlength(l, font=f)
        d.text((x, y), l, font=f, fill=TINTA, stroke_width=22, stroke_fill=TINTA)
        d.text((x, y), l, font=f, fill=(255, 255, 255) if i == 0 else (255, 226, 40), stroke_width=9, stroke_fill=TINTA)
        y += size + 12
    _out().mkdir(parents=True, exist_ok=True)
    p = _out() / f"miniatura_{nome}.png"
    img.convert("RGB").save(p, quality=95)
    return p


def tudo() -> list[Path]:
    return [capa(), perfil(), marca_dagua()]          # miniaturas: uma por música, feitas no `publicar`
