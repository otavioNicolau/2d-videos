"""Pasta de publicação de um episódio — mesmo formato do projeto ~/videos:

  output/<slug>/                 (no projeto)            → cópia para C:\\Users\\DELL\\Videos\\Laurinha e Luisinho\\NN Título\\
    <slug>.mp4                   vídeo completo (vinheta + clipe + chamada, se existir)
    <slug>.descricao.txt         TÍTULO / DESCRIÇÃO / TAGS — pronto para colar no YouTube Studio
    <slug>.youtube.txt           capítulos e configurações do envio (público infantil, categoria, idioma, legenda)
    <slug>.srt                   legenda da letra (tempos do vídeo completo)
    miniatura-<slug>-1280x720.jpg
  …\\Laurinha e Luisinho\\Canal\\  capa, perfil, marca d'água e textos do canal

O resumo do vídeo vem da ficha (`youtube.resumo`), escrito no chat; o resto sai da ficha, da letra e da análise.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from ..core.config import LIBRARY, PROJECTS, StudioError, tool

WIN_ROOT = Path("/mnt/c/Users/DELL/Videos/Laurinha e Luisinho")


def _dur(p: Path) -> float:
    probe = shutil.which("ffprobe") or str(Path(tool("ffmpeg")).with_name("ffprobe"))
    r = subprocess.run([probe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def _ts(t: float, srt: bool = False) -> str:
    t = max(0.0, t)
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    if srt:
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"
    return f"{m:02d}:{int(s):02d}" if h == 0 else f"{h}:{m:02d}:{int(s):02d}"


def _win_safe(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "", name).strip()


def _slug(musica: Path) -> str:
    return re.sub(r"^\d+_", "", musica.name).replace("_", "-")


def _letra_publicavel(musica: Path) -> str:
    """Letra para a descrição: sem marcações do Suno, refrão repetido só indicado, nomes com a grafia do canal."""
    from ..audio import composer
    out, refrao_visto = [], None
    bordoes = {v["bordao"] for v in composer.vozes()["vozes"].values() if v.get("bordao")}
    for s in composer.secoes(musica):
        if not s["linhas"] or s["tipo"] == "intervalo":
            continue
        if s["tipo"] == "bordao":                            # bordão fixo do canal fica de fora; grito da música ("Mais rápido!") entra
            linhas = [l for l in s["linhas"] if re.sub(r"\s*\(.*?\)", "", l).strip() not in bordoes]
            if linhas:
                out.append("\n".join(linhas))
            continue
        if s["tipo"] == "virada":                            # verso cantado logo depois da virada ("Escova de novo!")
            if out:
                out[-1] += "\n" + "\n".join(s["linhas"])
            continue
        if s["tipo"] == "refrao":
            if refrao_visto is not None and s["linhas"] == refrao_visto:   # só o refrão IGUAL vira "(Refrão)"
                if out[-1] != "(Refrão)":                    # refrão repetido em seguida: indica uma vez só
                    out.append("(Refrão)")
                continue
            if refrao_visto is None:                          # refrão com comandos/versos novos sai por extenso
                refrao_visto = s["linhas"]
        linhas = [re.sub(r"\s+", " ", l.replace("Lau-ri-nha", "Laurinha").replace("Luizinho", "Luisinho")) for l in s["linhas"]]
        out.append("\n".join(linhas))
    return "\n\n".join(out)


def _capitulos(song: dict, offset: float, total: float, nomes_ficha: dict | None = None) -> list[tuple[float, str]]:
    nomes = {"intro": "Abertura", "verso": "Verso", "refrao": "Refrão", "ponte": "Hora da brincadeira", "intervalo": "Hora de dançar",
             "parada": "Hora da estátua", "subida": "Todo mundo junto",
             "final": "Tchau!", **(nomes_ficha or {})}           # ficha.capitulos troca o nome de uma parte (ex.: ponte)
    from .clip_draft import blocos
    caps = [(0.0, "Abertura")]
    nv = 0
    for b in blocos(song):
        if b["tipo"] in ("intro", "intervalo"):              # intervalo de dança (4–10 s) não vira capítulo
            continue
        nome = nomes.get(b["tipo"], b["tipo"].capitalize())
        if b["tipo"] == "verso":
            nv += 1
            nome = f"Verso {nv}"
        t = b["s"] + offset
        if nome == caps[-1][1]:                                 # refrão repetido em seguida = mesmo capítulo
            continue
        if t - caps[-1][0] >= 10 and total - t >= 10:          # regra do YouTube: capítulos de 10 s ou mais
            caps.append((t, nome))
    return caps if len(caps) >= 3 else []


PLAYLIST_GERAL = "Músicas Infantis da Laurinha e do Luisinho 🐝"
# links das playlists (nome → https://www.youtube.com/playlist?list=…): o usuário cria no Studio e passa o link; sem link sai só o nome
LINKS_PLAYLISTS = Path(__file__).resolve().parents[2] / "musicas" / "playlists_links.json"


def publicar(project: str, musica: Path, copiar: bool = True) -> Path:
    from ..audio import composer
    from .canal import miniatura
    from .marca import final
    pdir = PROJECTS / project
    f = composer.ficha(musica)
    yt = f.get("youtube", {})
    if not yt.get("resumo"):
        raise StudioError(f"a ficha {musica.name} precisa de youtube.resumo (escrito no chat) para a descrição")
    completo = final(project)
    slug = _slug(musica)
    out = pdir / "output" / slug
    out.mkdir(parents=True, exist_ok=True)
    mp4 = out / f"{slug}.mp4"
    shutil.copy2(completo, mp4)
    total = _dur(mp4)
    vin = LIBRARY / "brand" / "vinheta.mp4"
    offset = _dur(vin) if vin.exists() else 0.0
    titulo = f"{f['titulo'].upper()} 🐝 Laurinha e Luisinho (Música Infantil)"
    tags = ", ".join(dict.fromkeys([re.sub(r"[^\w\s]", "", f["titulo"].lower().replace("-", " ")).strip(), "Laurinha e Luisinho", "música infantil",
                                    "clipe infantil", "desenho infantil", "músicas para crianças",
                                    *[d for d in f.get("dia_a_dia", [])][:3], composer.estilos()["ritmos"][f["ritmo"]]["nome"].lower()]))
    hashtags = "#musicainfantil #laurinhaeluisinho #desenhoinfantil"
    desc = [f"TÍTULO\n{titulo}", "", "DESCRIÇÃO", yt["resumo"].strip(), ""]
    if f.get("curiosidade"):
        desc += [f"💡 Você sabia? {yt.get('curiosidade') or f['curiosidade'][0].upper() + f['curiosidade'][1:]}!".replace("!!", "!"), ""]
    pls = list(dict.fromkeys([PLAYLIST_GERAL, *f.get("playlists", [])]))      # musicas/PLAYLISTS.md
    links = json.loads(LINKS_PLAYLISTS.read_text(encoding="utf-8")) if LINKS_PLAYLISTS.exists() else {}
    desc += ["🎵 Letra:", _letra_publicavel(musica), "",
             "📺 Mais músicas nas playlists:"] + [f"▶️ {n}" + (f": {links[n]}" if links.get(n) else "") for n in pls] + ["",
             "👍 Peça para um adulto se inscrever no canal e deixar o joinha!", "",
             "Música e animação originais © Laurinha e Luisinho.", hashtags, "", "TAGS", tags, "",
             "PLAYLISTS (adicionar o vídeo em)"] + [f"- {n}" for n in pls] + ["",
             "OBS.: canal para crianças — comentários ficam desativados pelo YouTube (não há comentário fixado)."]
    (out / f"{slug}.descricao.txt").write_text("\n".join(desc) + "\n", encoding="utf-8")
    song = json.loads((pdir / "analise" / "song.json").read_text(encoding="utf-8"))
    caps = _capitulos(song, offset, total, f.get("capitulos"))
    ytx = ["Capítulos:"] + [f"{_ts(t)} {n}" for t, n in caps] if caps else ["(vídeo curto: sem capítulos)"]
    ytx += ["", "Configurações do envio:", "- Público: SIM, é conteúdo para crianças", "- Categoria: Música",
            "- Idioma do vídeo: Português (Brasil)", f"- Legenda: enviar {slug}.srt (Português)",
            f"- Miniatura: miniatura-{slug}-1280x720.jpg", "- Conteúdo alterado/sintético: desenho animado não realista (normalmente não exige aviso; confira no Studio)",
            "- Música gerada no plano pago do Suno (uso comercial)"]
    ytx += ["", "Playlists (adicionar o vídeo em):"] + [f"- {n}" for n in pls]
    (out / f"{slug}.youtube.txt").write_text("\n".join(ytx) + "\n", encoding="utf-8")
    letra = json.loads((pdir / "analise" / "letra.json").read_text(encoding="utf-8"))["lines"]
    itens: list[list] = []                                   # [início, fim, texto] no tempo do vídeo completo
    for i, l in enumerate(letra):
        prox = letra[i + 1]["s"] + offset - 0.02 if i + 1 < len(letra) else total
        s, e = l["s"] + offset, min(l["e"] + offset + 0.3, prox, total)    # nunca sobrepõe a próxima linha
        if e - s < 0.3 and itens:                            # curta demais para ler: junta à anterior
            if l["text"] != itens[-1][2]:
                itens[-1][2] += " " + l["text"]
            itens[-1][1] = max(itens[-1][1], e)
            continue
        itens.append([s, e, l["text"]])
    srt = []
    for i, (s, e, txt) in enumerate(itens, 1):
        srt += [str(i), f"{_ts(s, True)} --> {_ts(e, True)}", txt, ""]
    (out / f"{slug}.srt").write_text("\n".join(srt), encoding="utf-8")
    from PIL import Image
    mt = yt.get("miniatura") or f["titulo"].upper()
    png = miniatura(mt.replace("\\n", "\n"), slug, yt.get("miniatura_cena"))
    Image.open(png).convert("RGB").save(out / f"miniatura-{slug}-1280x720.jpg", quality=92)
    if copiar:
        n = re.match(r"^(\d+)_", musica.name)
        dest = WIN_ROOT / _win_safe(f"{n.group(1) if n else '00'} {f['titulo']}") / "Vídeo longo"   # como em ~/videos
        dest.mkdir(parents=True, exist_ok=True)
        for p in out.iterdir():
            shutil.copy2(p, dest / p.name)
        canal = WIN_ROOT / "Canal"
        canal.mkdir(parents=True, exist_ok=True)
        src = LIBRARY / "brand" / "canal"
        for p in src.glob("*.png"):
            if "guia" not in p.name and "miniatura" not in p.name:
                shutil.copy2(p, canal / p.name)
        md = src / "CANAL_YOUTUBE.md"
        if md.exists():
            (canal / "TEXTOS DO CANAL.txt").write_text(md.read_text(encoding="utf-8").replace("\n", "\r\n"), encoding="utf-8")
        return dest
    return out


def publicar_short(project: str, musica: Path, copiar: bool = True) -> Path:
    """Short vertical (projeto `<origem>-short`): mp4 + descrição (#shorts) + extras → …/NN Título/Short/."""
    from ..audio import composer
    pdir = PROJECTS / project
    f = composer.ficha(musica)
    yt = f.get("youtube", {})
    vids = sorted((pdir / "output").glob(f"{project}*.mp4"))
    if not vids:
        raise StudioError(f"renderize o Short antes (`toonstudio build {project}`)")
    slug = _slug(musica) + "-short"
    out = pdir / "output" / slug
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(vids[0], out / f"{slug}.mp4")
    titulo = f"{f['titulo'].upper()} 🐝 Laurinha e Luisinho #shorts"
    desc = [f"TÍTULO\n{titulo}", "", "DESCRIÇÃO", (yt.get("resumo_short") or yt["resumo"]).strip(), "",
            "▶️ Clipe completo no canal Laurinha e Luisinho!", "",
            "👍 Peça para um adulto se inscrever no canal e deixar o joinha!", "",
            "#shorts #musicainfantil #laurinhaeluisinho #desenhoinfantil", "",
            "OBS.: canal para crianças — comentários ficam desativados pelo YouTube."]
    (out / f"{slug}.descricao.txt").write_text("\n".join(desc) + "\n", encoding="utf-8")
    (out / f"{slug}.youtube.txt").write_text("\n".join([
        "Configurações do envio (Short):", "- Formato: vertical 1080×1920, menos de 60 s", "- Público: SIM, é conteúdo para crianças",
        "- Categoria: Música", "- Idioma do vídeo: Português (Brasil)",
        "- Miniatura: o YouTube usa um quadro do vídeo (escolha o do refrão, com os dois de braços para cima)"]) + "\n", encoding="utf-8")
    if copiar:
        n = re.match(r"^(\d+)_", musica.name)
        dest = WIN_ROOT / _win_safe(f"{n.group(1) if n else '00'} {f['titulo']}") / "Short"
        dest.mkdir(parents=True, exist_ok=True)
        for p in out.iterdir():
            shutil.copy2(p, dest / p.name)
        return dest
    return out
