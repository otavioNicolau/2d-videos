"""Identidade do canal "Luizinho e Turminha" (logo) e textos na tela (letra palavra a palavra, avisos) em ASS/libass."""
from __future__ import annotations

from pathlib import Path

import skia

from ..core.config import LIBRARY

FONT = LIBRARY / "fonts" / "Poppins-ExtraBold.ttf"


def logo(out: Path, height: int = 150) -> Path:
    """Selo do canal: nuvem amarela com borda vermelha, 'LUIZINHO' vermelho e 'e Turminha' azul, contorno branco."""
    tf = skia.Typeface.MakeFromFile(str(FONT))
    W, H = int(height * 2.6), height
    s = skia.Surface(W, H + 40)
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.translate(0, 36)         # folga para os "gomos" da nuvem no alto
    path = skia.Path()
    r = H * 0.42
    path.addRRect(skia.RRect.MakeRectXY(skia.Rect(8, 10, W - 8, H - 8), r, r))
    for (x, y, rr) in ((W * 0.18, H * 0.2, H * 0.22), (W * 0.45, H * 0.12, H * 0.26), (W * 0.75, H * 0.2, H * 0.22)):
        path.addCircle(x, y + 10, rr)
    path.setFillType(skia.PathFillType.kWinding)
    border = skia.Paint(AntiAlias=True, Color=skia.Color(224, 52, 46), Style=skia.Paint.kStroke_Style, StrokeWidth=14)
    c.drawPath(path, border)
    c.drawPath(path, skia.Paint(AntiAlias=True, Color=skia.Color(255, 214, 64)))

    def text(t, size, color, y):
        font = skia.Font(tf, size)
        w = font.measureText(t)
        x = (W - w) / 2
        blob = skia.TextBlob.MakeFromString(t, font)
        c.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=skia.ColorWHITE, Style=skia.Paint.kStroke_Style,
                                              StrokeWidth=size * 0.16, StrokeJoin=skia.Paint.kRound_Join))
        c.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=color))
    text("LUIZINHO", H * 0.42, skia.Color(224, 52, 46), H * 0.6)
    text("e Turminha", H * 0.26, skia.Color(46, 112, 210), H * 0.86)
    out.parent.mkdir(parents=True, exist_ok=True)
    s.makeImageSnapshot().save(str(out), skia.kPNG)
    return out


def _ts(t: float) -> str:
    t = max(0.0, t)
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _esc(t: str) -> str:
    return t.replace("{", "(").replace("}", ")").replace("\n", "\\N")


def ass(out: Path, W: int, H: int, lines: list[dict], card: str | None, footer: str | None, duration: float,
        card_dur: float = 5.0) -> Path:
    """Letra: palavra por palavra (cada palavra aparece quando é cantada), amarela, maiúscula, contorno escuro."""
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Letra,Poppins ExtraBold,72,&H004DE1FF,&H004DE1FF,&H00102040,&H80000000,0,0,0,0,100,100,1,0,1,6,3,2,80,80,58,1
Style: Aviso,Poppins ExtraBold,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB0000000,0,0,0,0,100,100,0,0,3,14,0,5,160,160,40,1
Style: Rodape,Poppins ExtraBold,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,3,6,0,9,40,40,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    lines = sorted(lines, key=lambda l: l["words"][0]["s"])
    for li, ln in enumerate(lines):
        words = ln["words"]
        nxt = lines[li + 1]["words"][0]["s"] if li + 1 < len(lines) else 1e9
        for k, w in enumerate(words):
            start = w["s"]
            # o verso some antes do próximo entrar (nunca duas linhas empilhadas)
            end = words[k + 1]["s"] if k + 1 < len(words) else min(ln["e"] + 0.45, nxt - 0.03)
            if end - start < 0.04:
                continue
            txt = " ".join(x["w"] for x in words[:k + 1]).upper()
            ev.append(f"Dialogue: 1,{_ts(start)},{_ts(end)},Letra,,0,0,0,,{{\\fad(60,0)}}{_esc(txt)}")
    if card:
        ev.append(f"Dialogue: 3,{_ts(0)},{_ts(card_dur)},Aviso,,0,0,0,,{{\\fad(200,300)}}{_esc(card)}")
    if footer:
        ev.append(f"Dialogue: 2,{_ts(0)},{_ts(duration)},Rodape,,0,0,0,,{_esc(footer)}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
    return out
