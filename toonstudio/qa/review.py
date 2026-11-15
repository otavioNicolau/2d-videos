"""Relatório de revisão do episódio: prancha (storyboard pós-render) + QA + pendências de aprovação humana."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def contact_sheet(ep, out: Path, per_scene: int = 4) -> Path:
    tw, th = 384, 216
    rows = []
    for s in ep.ep["scenes"]:
        comp = sorted((ep.build / "scenes" / s["id"] / "comp").glob("*.png"))
        if not comp:
            continue
        picks = [comp[int(i * (len(comp) - 1) / (per_scene - 1))] for i in range(per_scene)]
        rows.append((s, [Image.open(p).convert("RGB").resize((tw, th)) for p in picks]))
    f = ImageFont.truetype(FONT, 18)
    sheet = Image.new("RGB", (per_scene * (tw + 8) + 260, len(rows) * (th + 10) + 10), (24, 22, 26))
    d = ImageDraw.Draw(sheet)
    for r, (s, ims) in enumerate(rows):
        y = 10 + r * (th + 10)
        d.text((10, y + 6), s["id"], fill=(255, 220, 120), font=f)
        d.text((10, y + 32), f"{s['duration']:.1f}s · {s.get('shot', '')}", fill=(200, 200, 200), font=f)
        for i, line in enumerate(_wrap(s.get("title", ""), 22)[:3]):
            d.text((10, y + 60 + i * 22), line, fill=(230, 230, 230), font=f)
        for i, im in enumerate(ims):
            sheet.paste(im, (260 + i * (tw + 8), y))
    sheet.save(out)
    return out


def _wrap(t: str, n: int) -> list[str]:
    out, cur = [], ""
    for w in t.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])


def write(ep, mp4: Path) -> Path:
    out_dir = ep.dir / "output"
    sheet = contact_sheet(ep, out_dir / "prancha.png")
    rep = dict(ep.report)
    rep["video"] = str(mp4)
    rep["contact_sheet"] = str(sheet)
    rep["approved"] = bool(ep.ep.get("approval", {}).get("final_render"))
    (out_dir / "qa_report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    lines = [f"# Revisão — {ep.ep['title']}", "", f"- Vídeo: `{mp4.name}`", f"- Prancha: `{sheet.name}`",
             f"- Aprovação humana do render final: **{'SIM' if rep['approved'] else 'PENDENTE (vídeo é candidato)'}**", "",
             "## Falas (QA por transcrição cega)", "", "| cena | texto | ouvido | sim. | dur. |", "|---|---|---|---|---|"]
    for k, v in rep.get("lines", {}).items():
        lines.append(f"| {k} | {v['text']} | {v['heard']} | {v['similarity']:.2f} | {v['duration']:.2f}s |")
    lines += ["", "## Cenas", ""]
    for sid, q in rep["scenes"].items():
        perf = ", ".join(f"{w}: {p.get('drawings')} desenhos" for w, p in q.get("performers", {}).items())
        lines.append(f"- **{sid}** — {q.get('frames')} quadros; {perf}")
        for i in q.get("issues", []):
            lines.append(f"  - ⚠ {i}")
    if rep["warnings"]:
        lines += ["", "## Avisos", ""] + [f"- {w}" for w in rep["warnings"]]
    (out_dir / "REVISAO.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_dir / "REVISAO.md"
