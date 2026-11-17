"""Testes do sistema de composição musical (ADR-0015; musicas/BIBLIA_MUSICAL.md)."""
import json
import shutil

import numpy as np

from toonstudio.audio import composer as c


def _musica(tmp_path, letra, **ficha):
    d = tmp_path / "99_teste"
    d.mkdir()
    f = {"schema": "musica-1.0", "titulo": "Bate Palminha", "gancho": "bate palminha", "palavras_tema": ["escola"],
         "tipo": "brincadeira", "dia_a_dia": ["escola"], "curiosidade": "x", "ritmo": "pagodao", "bpm": 135, "estrutura": "R",
         "voz": "dueto", "cenas": [{"parte": "refrão", "ideia": "roda"}], "duracao_alvo": [140, 170], "alternativas": []}
    f.update(ficha)
    (d / "ficha.json").write_text(json.dumps(f), encoding="utf-8")
    (d / "letra.txt").write_text(letra, encoding="utf-8")
    return d


def test_all_channel_songs_pass_the_bible_checks():
    E = c.estilos()
    assert c.todas(), "nenhuma música com ficha"
    for d in c.todas():
        f = c.ficha(d)
        assert f["ritmo"] in E["ritmos"] and f["gancho"], d.name
        ck = c.checar(d)
        assert not ck.erros, (d.name, [i.msg for i in ck.erros])
        assert ck.metricas["versos_longos"] == 0, d.name
        assert ck.metricas["gancho_vezes"] >= 8, d.name


def test_suno_txt_is_generated_not_hand_edited():
    for d in c.todas():
        assert (d / "suno.txt").read_text(encoding="utf-8") == c.texto_suno(c.prompt(d)), \
            f"{d.name}/suno.txt desatualizado: rode `toonstudio musica prompt {d.name}`"


def test_style_is_built_per_rhythm_without_contradictions():
    E = c.estilos()
    f = {"ritmo": "samba_enredo", "bpm": 145, "voz": "dueto"}
    s = c.style(f)
    assert "surdos" in s and "kick drum on every beat" not in s       # a batida do samba é do surdo
    for rid in E["ritmos"]:
        ff = {"ritmo": rid, "bpm": E["ritmos"][rid]["bpm"][2], "voz": "laurinha"}
        assert not c.contradicoes(c.style(ff), c.exclude(ff)), rid
    calmo = c.style({"ritmo": "xote", "bpm": 100, "voz": "dueto"})
    assert "heavy" not in calmo                                       # xote/ciranda/reggae: groove marcado, sem peso


def test_shortcuts_follow_the_beat_weight():
    E, V = c.estilos(), c.vozes()
    letra = "[Virada]\n[Chorus]\nBate!\n[Bordão laurinha]\n[Intervalo 8s]\n"
    forte = c.expandir(letra, "forte", E, V)
    assert "[Drum Fill]" in forte and "[Drum Break - 8 seconds" in forte and "Bora, turminha!" in forte
    marcada = c.expandir(letra, "marcada", E, V)
    assert "Drum" not in marcada and "[Instrumental Break - 8 seconds" in marcada


def test_checker_flags_genre_in_lyrics_and_bad_words(tmp_path):
    d = _musica(tmp_path, "[Chorus]\nÉ o rock da escovinha\nBate palminha\n[Intervalo 8s]\n[Intervalo 8s]\n")
    regras = {i.regra for i in c.checar(d).erros}
    assert "ritmo citado" in regras
    shutil.rmtree(d)
    d = _musica(tmp_path, "[Chorus]\nVem rebolar até o chão\n")
    assert "idade" in {i.regra for i in c.checar(d).erros}


def test_checker_wants_short_verses_hook_and_identity(tmp_path):
    d = _musica(tmp_path, "[Verse]\nEu fui pra escola hoje cedo com a minha mochila nova\n[Chorus]\nBate palminha\n")
    ck = c.checar(d)
    msgs = " ".join(i.msg for i in ck.itens if i.nivel == "aviso")
    assert "mais de 7 palavras" in msgs and "cantado 1 vezes" in msgs and "bordão" in msgs and "zum" in msgs


def test_lyrics_comparison_and_tempo_octave():
    r = c.comparar_letra("bate palminha bate o pezinho".split(), "bate palminha bate o pesinho".split())
    assert r["acerto"] == 80 and r["nao_reconhecidas"] == ["pezinho"]
    assert c._bpm_coerente(86.1, 172)[0] == 172.2
    assert c._bpm_coerente(140, 140) == (140, "")


def test_ending_detection_hard_stop_vs_fade():
    sr = 8000
    t = np.arange(sr * 6) / sr
    tom = (0.5 * np.sin(2 * np.pi * 220 * t)).astype("float32")
    seco = np.concatenate([tom, np.zeros(sr * 3, "float32")])
    assert c._final(seco, sr) == {"tipo": "corte seco", "silencio": 3.0}
    fade = tom * np.clip((6 - t) / 3, 0, 1).astype("float32")
    assert c._final(fade, sr)["tipo"] == "esmaecendo"


def test_known_lyrics_alignment_tolerates_asr_spelling_and_skips_silence():
    from toonstudio.audio.song import align_known_lyrics
    secs = [{"tag": "Verse", "tipo": "verso", "cantam": ["laurinha"], "linhas": ["O sol deu bom dia"]},
            {"tag": "Drum Break", "tipo": "intervalo", "cantam": [], "linhas": []},
            {"tag": "Chorus", "tipo": "refrao", "cantam": ["coro"], "linhas": ["Zum, zum, cheguei!", "Bati as asinhas"]}]
    heard = [{"w": w, "s": s, "e": s + 0.4} for w, s in
             (("o", 1.0), ("sol", 1.5), ("deu", 2.0), ("bom", 2.5), ("dia", 3.0),
              ("zunzun", 10.0), ("ceguei", 10.6), ("tiazazinhas", 11.5))]
    al = align_known_lyrics(heard, secs, spans=[[1.0, 3.5], [10.0, 12.5]])
    texts = [l["text"] for l in al["lines"]]
    assert texts == ["O sol deu bom dia", "Zum, zum, cheguei!", "Bati as asinhas"]     # texto é o da letra
    chorus = al["lines"][1]
    assert 9.8 <= chorus["s"] <= 10.2 and chorus["e"] < 11.5                            # "zunzun ceguei" casou
    brk = al["sections"][1]
    assert brk["s"] >= 3.3 and brk["e"] <= 10.1                                         # intervalo fica no silêncio


def test_stretched_line_keeps_the_side_after_an_instrumental_break():
    from toonstudio.audio.song import _fix_stretched
    ws = [{"w": "Zum,", "s": 104.8, "e": 105.1}, {"w": "zum,", "s": 105.1, "e": 105.3},
          {"w": "cheguei!", "s": 105.3, "e": 105.5}, {"w": "(Cheguei!)", "s": 105.5, "e": 113.3}]
    _fix_stretched(ws, keep="right")
    assert ws[0]["s"] > 111.5 and ws[-1]["e"] == 113.3


def test_clip_draft_blocks_cover_the_song_and_merge_fill_and_shout():
    from toonstudio.composition.clip_draft import blocos
    song = {"duration": 30.0, "beats": [i * 0.5 for i in range(61)], "sections": [
        {"tag": "Intro", "tipo": "intro", "cantam": [], "s": 0.0, "e": 2.0},
        {"tag": "Verse", "tipo": "verso", "cantam": ["laurinha"], "s": 4.0, "e": 12.0},
        {"tag": "Drum Fill", "tipo": "virada", "cantam": [], "s": 12.0, "e": 12.0},
        {"tag": "Chorus", "tipo": "refrao", "cantam": ["coro"], "s": 12.5, "e": 20.0},
        {"tag": "Shout", "tipo": "bordao", "cantam": ["laurinha"], "s": 20.0, "e": 21.0},
        {"tag": "Drum Break", "tipo": "intervalo", "cantam": [], "s": 21.0, "e": 26.0},
        {"tag": "End", "tipo": "fim", "cantam": [], "s": 30.0, "e": 30.0}]}
    b = blocos(song)
    assert [x["tipo"] for x in b] == ["intro", "verso", "refrao", "intervalo"]
    assert b[0]["s"] == 0.0 and b[-1]["e"] == 30.0
    assert all(abs(x["e"] - y["s"]) < 1e-9 for x, y in zip(b, b[1:]))                  # contínuo, sem buraco
    assert all(x["s"] in song["beats"] for x in b[1:])                                  # cortes na batida


def test_official_muricocas_can_fly_in_validation():
    from toonstudio.core.validate import _flies
    assert _flies("laurinha") and _flies("luisinho") and not _flies("caramelo")


def test_roteiro_shots_cover_the_block_and_follow_the_lines():
    from toonstudio.composition.clip_draft import roteiro_bloco
    b = {"tipo": "verso", "s": 10.0, "e": 20.0, "cantam": ["laurinha"]}
    lines = [{"s": 10.2, "e": 12.0, "text": "Acordei", "_cantam": ["laurinha"]},
             {"s": 12.5, "e": 15.0, "text": "Abri a janela", "_cantam": ["laurinha"]},
             {"s": 15.5, "e": 19.0, "text": "Bom dia", "_cantam": ["laurinha"]}]
    spec = [{"cenario": "danca_raios_rosa", "atores": {"laurinha": {"x": 640}}},
            {"cenario": "danca_raios_azul", "atores": {"luisinho": {"x": 960}}},
            {"cenario": "danca_raios_roxo", "atores": {"laurinha": {"x": 960, "acoes": [{"do": "bacana", "dur": "resto"}]}}}]
    beats = [10 + i * 0.25 for i in range(41)]
    cast = {}
    sc = roteiro_bloco(b, spec, 1, lines, beats, cast, 5)
    assert len(sc) == 3 and abs(sum(s["duration"] for s in sc) - 10.0) < 1e-3
    assert [s["description"] for s in sc] == ["Acordei", "Abri a janela", "Bom dia"]
    assert "sing" not in sc[1]                                  # Luisinho está no plano, mas o verso é da Laurinha
    assert sc[2]["characters"]["laurinha"]["actions"][0]["dur"] > 3   # "resto" vira a duração até o fim do plano
    assert "luisinho" in cast and sc[0]["transition_in"]


def test_muricoca_flight_lands_with_feet_on_the_ground():
    from toonstudio.animation.timeline import compile_character
    from toonstudio.core.registry import character
    spec = {"start": {"x": 0, "y": 600, "turn": 0.15}, "actions": [{"t": 0.0, "do": "fly", "to_x": 300, "to_y": 1000, "dur": 0.6}]}
    poses = compile_character(character("laurinha"), spec, 30, 1.5).evaluate_all()
    assert poses[8]["fly"] > 0.5 and poses[-1]["fly"] < 0.5 and abs(poses[-1]["y"] - 1000) < 1


def test_brand_library_renders_props_family_and_scenes():
    from toonstudio.backgrounds import registry
    from toonstudio.characters.flat_props import PROPS, ITEMS
    from toonstudio.core.registry import character
    for pid in list(PROPS) + ["mamae", "vovo"]:
        character(pid).render({}, scale=0.2)
    for item in ITEMS:
        character("laurinha").render({"holding": item}, scale=0.2)
    for bg in ("plano_quarto_rosa", "plano_cozinha", "plano_escola", "padrao_bananas_azul"):
        assert registry.known(bg)


def test_short_vertical_framing_covers_frame_and_merges_split_screen():
    from toonstudio.composition.short import _verticaliza, _zoom_min, H
    sc = {"id": "s05_refrao", "duration": 3.0, "layout": "diagonal", "panels": [
        {"background": "danca_xadrez_rosa", "camera": {"keys": [{"t": 0, "x": 960, "y": 560, "zoom": 1.2}]},
         "characters": {"laurinha": {"start": {"x": 960, "y": 1010}, "actions": []}}},
        {"background": "danca_xadrez_azul", "camera": {"keys": [{"t": 0, "x": 960, "y": 560, "zoom": 1.2}]},
         "characters": {"luisinho": {"start": {"x": 960, "y": 1010}, "actions": []}}}]}
    v = _verticaliza(sc, {})
    assert "panels" not in v and set(v["characters"]) == {"laurinha", "luisinho"}
    xs = sorted(c["start"]["x"] for c in v["characters"].values())
    assert xs[1] - xs[0] >= 300 and abs(sum(xs) / 2 - 960) < 1        # lado a lado, centrados
    assert all(k["zoom"] >= _zoom_min("danca_xadrez_rosa", {}) for k in v["camera"]["keys"])
    assert _zoom_min("plano_quarto_rosa", {"height": 1080}) * 1080 >= H   # cenário pintado cobre a altura do quadro


def test_short_vertical_fits_groups_and_follows_movement():
    """Quadro vertical: 3+ personagens viram foto de grupo (dupla na frente, nada cortado); quem anda leva o
    destino junto; a câmera acompanha quem voa; o parado no fundo sai do quadro estreito."""
    from toonstudio.composition.short import _verticaliza, _zoom_min, W
    def ch(x, acts=()):
        return {"start": {"x": x, "y": 1010, "depth": 1.3, "z": 3}, "actions": list(acts)}
    cam = {"keys": [{"t": 0, "x": 960, "y": 560, "zoom": 1.0}]}
    sc = {"id": "s1", "duration": 3.0, "background": "danca_ondas_azul", "camera": cam,
          "characters": {w: ch(x, [{"do": "dance", "style": "roda", "dur": 3}]) for w, x in
                         [("laurinha", 480), ("joaninha", 800), ("luisinho", 1120), ("formiguinha", 1440)]}}
    v = _verticaliza(sc, {})
    half = W / 2 / _zoom_min("danca_ondas_azul", {})
    for w, c in v["characters"].items():
        assert abs(c["start"]["x"] - 960) + 150 * c["start"]["depth"] <= half, w     # ninguém cortado
    assert v["characters"]["laurinha"]["start"]["z"] > v["characters"]["joaninha"]["start"]["z"]
    sc2 = {"id": "s2", "duration": 3.9, "background": "plano_parque", "camera": cam,
           "characters": {"laurinha": ch(1300, [{"t": 0.1, "do": "wave", "dur": 3}]), "joaninha": ch(980),
                          "formiguinha": ch(1700, [{"t": 0.1, "do": "walk", "to_x": 1450, "dur": 1.2}])}}
    v2 = _verticaliza(sc2, {"plano_parque": {"width": 2400, "height": 1080}})
    assert "joaninha" not in v2["characters"]
    c = v2["characters"]
    assert c["formiguinha"]["actions"][0]["to_x"] - c["laurinha"]["start"]["x"] >= 300   # chega AO LADO, não em cima
    sc3 = {"id": "s3", "duration": 3.0, "background": "plano_escola", "camera": cam,
           "characters": {"laurinha": ch(1300, [{"t": 0, "do": "fly", "to_x": 1720, "to_y": 950, "dur": 1.0}])}}
    k3 = _verticaliza(sc3, {"plano_escola": {"width": 2400, "height": 1080}})["camera"]["keys"]
    assert k3[0]["x"] < k3[-1]["x"] and abs(k3[-1]["x"] - 1720) < 1                    # câmera vai junto


def test_skipped_repeated_line_is_dropped_from_lyrics():
    from toonstudio.audio.song import drop_skipped
    w = lambda *ts: [{"w": "x", "s": t, "e": t + 0.05} for t in ts]
    lines = [{"s": 123.7, "e": 125.6, "text": "Bate palminha!", "confianca": 0.4, "words": w(123.7, 125.0)},
             {"s": 127.04, "e": 127.28, "text": "Bate palminha!", "confianca": 0.0, "words": w(127.04, 127.2)},
             {"s": 127.28, "e": 133.9, "text": "Vem pra roda", "confianca": 1.0, "words": w(127.3, 130.0)}]
    assert [l["s"] for l in drop_skipped(lines)] == [123.7, 127.28]


def test_published_songs_have_a_colorful_thumbnail_scene():
    """Miniatura sem imagem da música (só personagens sobre fundo liso) não passa: cada ficha publicada descreve a cena,
    e todos os ids existem."""
    from pathlib import Path
    from toonstudio.core.registry import CHARACTERS
    for p in sorted(Path("musicas").glob("*/ficha.json")):
        yt = json.loads(p.read_text(encoding="utf-8")).get("youtube", {})
        if not yt.get("miniatura"):
            continue
        cena = yt.get("miniatura_cena")
        assert cena and cena.get("objetos"), f"{p.parent.name}: falta youtube.miniatura_cena com os objetos da música"
        ids = [cena["heroi"]["id"], *[o["id"] for o in cena.get("objetos", []) + cena.get("frente", [])]]
        if cena.get("par"):
            ids.append(cena["par"]["id"])
        for i in ids:
            assert i in CHARACTERS, f"{p.parent.name}: '{i}' não existe"


def test_thumbnails_do_not_repeat_background():
    """Cada miniatura tem fundo próprio: a combinação (formato, cores) não se repete entre músicas."""
    from pathlib import Path
    from toonstudio.composition.canal import FUNDOS
    vistos = {}
    for p in sorted(Path("musicas").glob("*/ficha.json")):
        cena = json.loads(p.read_text(encoding="utf-8")).get("youtube", {}).get("miniatura_cena")
        if not cena:
            continue
        assert cena.get("fundo") in FUNDOS and len(cena.get("cores", [])) >= 3, f"{p.parent.name}: defina fundo e cores"
        chave = (cena["fundo"], tuple(map(tuple, cena["cores"])))
        assert chave not in vistos, f"{p.parent.name} repete o fundo de {vistos.get(chave)}"
        assert tuple(map(tuple, cena["cores"])) not in [k[1] for k in vistos], f"{p.parent.name} repete as cores de outra música"
        vistos[chave] = p.parent.name
