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
        if (d / "versoes").exists() or c.ficha(d).get("suno_congelado"):   # já gravada/usada no Suno: registra o Style usado
            continue
        assert (d / "suno.txt").read_text(encoding="utf-8") == c.texto_suno(c.prompt(d)), \
            f"{d.name}/suno.txt desatualizado: rode `toonstudio musica prompt {d.name}`"


def test_style_is_built_per_rhythm_without_contradictions():
    import copy
    E = copy.deepcopy(c.estilos())
    E["canal"].setdefault("trio", {})["ativo"] = False                # modo normal: cada ritmo com a sua batida
    f = {"ritmo": "samba_enredo", "bpm": 145, "voz": "dueto"}
    s = c.style(f, E=E)
    assert "surdos" in s and "kick drum on every beat" not in s       # a batida do samba é do surdo
    for E_ in (E, c.estilos()):                                       # normal e trio (E12): nunca Style × Exclude opostos
        for rid in E_["ritmos"]:
            ff = {"ritmo": rid, "bpm": E_["ritmos"][rid]["bpm"][2], "voz": "laurinha"}
            assert not c.contradicoes(c.style(ff, E=E_), c.exclude(ff, E=E_)), rid
    calmo = c.style({"ritmo": "xote", "bpm": 100, "voz": "dueto"}, E=E)
    assert "heavy" not in calmo                                       # xote/ciranda/reggae: groove marcado, sem peso


def test_trio_so_teclado_baixo_bateria():
    """E16 (usuário, 21/11: 'quero teclado, com baixo, bateria'): o Style pede só teclado, contrabaixo e bateria; o sax
    (E12–E15) foi para o Exclude junto com o resto."""
    E = c.estilos()
    if not E["canal"].get("trio", {}).get("ativo"):
        return
    f = {"ritmo": "samba_enredo", "bpm": 145, "voz": "luisinho"}
    s, x = c.style(f), c.exclude(f)
    assert "bass" in s and "drums" in s and "keyboard" in s
    assert "saxophone" not in s and "saxophone" in x
    assert "whistle" not in s and "surdos" not in s and "guitar" not in s
    assert "guitar" in x and "whistle" in x
    # E13 (20/11): a bateria é o loop ELETRÔNICO do teclado — bateria de banda (ao vivo/acústica) fica no Exclude
    assert "drum-machine" in s and "live drums" in x and "acoustic drums" in x
    # E16 (21/11, "deixe de lado ritmos… faça o próprio"): groove próprio do canal, sem o nome do ritmo da ficha
    if c.groove_proprio(E):
        assert "samba" not in s.lower() and c.groove_proprio(E)["style"] in s


def test_shortcuts_follow_the_beat_weight():
    E, V = c.estilos(), c.vozes()
    letra = "[Virada]\n[Chorus]\nBate!\n[Bordão laurinha]\n[Intervalo 8s]\n"
    forte = c.expandir(letra, "forte", E, V)
    assert "[Keyboard Fill]" in forte and "[Instrumental Break - 8 seconds" in forte and "Bora, turminha!" in forte
    assert "Drum Fill" not in forte                                   # E9 = E6: virada de teclado, nunca de bateria
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


def _canal_do_prop(pid, monkeypatch):
    """Props que desenham um arquivo do canal (logo_png → logo.png do Fofolucos) só existem no canal que tem o arquivo."""
    if pid == "logo_png":
        monkeypatch.setenv("TOONSTUDIO_CANAL", "fofolucos")
    else:
        monkeypatch.delenv("TOONSTUDIO_CANAL", raising=False)


def test_brand_library_renders_props_family_and_scenes(monkeypatch):
    from toonstudio.backgrounds import registry
    from toonstudio.characters.flat_props import PROPS, ITEMS
    from toonstudio.core.registry import character
    for pid in list(PROPS) + ["mamae", "vovo"]:
        _canal_do_prop(pid, monkeypatch)
        character(pid).render({}, scale=0.2)
    monkeypatch.delenv("TOONSTUDIO_CANAL", raising=False)
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
    for p in sorted(Path("canais/laurinha/musicas").glob("*/ficha.json")):
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
    for p in sorted(Path("canais/laurinha/musicas").glob("*/ficha.json")):
        cena = json.loads(p.read_text(encoding="utf-8")).get("youtube", {}).get("miniatura_cena")
        if not cena:
            continue
        assert cena.get("fundo") in FUNDOS and len(cena.get("cores", [])) >= 3, f"{p.parent.name}: defina fundo e cores"
        chave = (cena["fundo"], tuple(map(tuple, cena["cores"])))
        assert chave not in vistos, f"{p.parent.name} repete o fundo de {vistos.get(chave)}"
        assert tuple(map(tuple, cena["cores"])) not in [k[1] for k in vistos], f"{p.parent.name} repete as cores de outra música"
        vistos[chave] = p.parent.name


def test_eyes_stay_round_and_inside_the_head_at_any_turn():
    """Olho de trás não vira risco grudado no contorno; o da frente nunca some (nem de perfil)."""
    from toonstudio.characters.base import View
    from toonstudio.characters.flat_muri import _olho
    r = 112.0                                  # raio da cabeça em FlatMuri
    for t in [i / 20 for i in range(-20, 21)]:
        v = View(t)
        frente = -1 if t >= 0 else 1
        assert _olho(v, 0.0, r, frente) is not None, f"olho da frente sumiu no giro {t}"
        for side in (-1, 1):
            e = _olho(v, 0.0, r, side)
            if e:
                x, larg = e
                assert larg >= 0.75, f"olho espremido no giro {t}"
                assert abs(x) + 22 * larg <= r * 0.85, f"olho encostando na borda no giro {t}"


def test_both_eyes_until_profile_and_full_blink():
    """Rosto quase de frente nunca fica com um olho só (só some no perfil, giro > 0,7); a piscada fecha de verdade
    (quadro com lid 1 exposto em 1s), em intervalos variados e com ritmo diferente para cada personagem."""
    from toonstudio.animation.timeline import BLINK, CharTimeline
    from toonstudio.characters.base import View
    from toonstudio.characters.flat_muri import _olho
    from toonstudio.core.registry import character
    for t in [i / 20 for i in range(-14, 15)]:
        assert _olho(View(t), 0.0, 112.0, -1) and _olho(View(t), 0.0, 112.0, 1), f"um olho só no giro {t}"
    assert max(BLINK) == 1.0
    tl = CharTimeline(character("laurinha"), 24, 20.0)
    bts = tl.blink_times()
    gaps = [b - a for a, b in zip(bts, bts[1:])]
    assert len(bts) >= 4 and max(gaps) - min(gaps) > 0.5, "piscada em intervalo fixo (robótico)"
    assert all(tl.exposure_at(b + 1.5 / 24) == 1 for b in bts), "piscada em 2s (some na exposição)"
    assert bts != CharTimeline(character("luisinho"), 24, 20.0).blink_times()


def test_wave_keeps_hand_up_during_the_whole_goodbye():
    from toonstudio.animation.timeline import compile_character
    from toonstudio.core.registry import character
    tl = compile_character(character("laurinha"), {"start": {"x": 900, "y": 930, "turn": 0.15},
                                                   "actions": [{"t": 0.0, "do": "wave", "dur": 2.4}]}, 24, 3.0)
    P = tl.evaluate_all()
    assert all(P[i]["hand_n_y"] < -75 and P[i]["hand_n_x"] < -125 for i in range(6, 56)), "a mão do tchau escorrega ou some atrás da cabeça"


def test_every_prop_fits_the_level_canvas(monkeypatch):
    """O render desenha cada nível num quadro fixo (LEVEL_CANVAS/ANCHOR): o que passa da borda é cortado no vídeo
    (a árvore de Natal saiu sem o topo, e o storyboard não mostra isso)."""
    import numpy as np
    from toonstudio.characters.flat_props import PROPS
    from toonstudio.core.registry import character
    from toonstudio.render.pipeline import LEVEL_ANCHOR, LEVEL_CANVAS
    cortados = []
    for pid in PROPS:
        from toonstudio.characters.base import to_array
        _canal_do_prop(pid, monkeypatch)
        a = to_array(character(pid).render({}, 0.25, 0, 0, canvas=LEVEL_CANVAS, anchor=LEVEL_ANCHOR))
        al = a[..., 3]
        if al[0, :].max() > 0 or al[:, 0].max() > 0 or al[:, -1].max() > 0:
            cortados.append(pid)
    assert not cortados, f"objetos cortados pelo quadro do nível: {cortados}"


def test_lyrics_fit_suno_limit():
    """Campo Lyrics do Suno aceita até 5000 caracteres (quebras de linha contam)."""
    from pathlib import Path
    for d in sorted(Path("canais/laurinha/musicas").glob("[0-9][0-9]_*")):
        p = c.prompt(d)
        assert len(p["lyrics"].rstrip()) <= c.LIMITE_LETRA, d.name
        for a in p["alternativas"]:
            assert len(a["lyrics"].rstrip()) <= c.LIMITE_LETRA, (d.name, a["ritmo"])


def test_catalogue_is_not_one_formula():
    """Auditoria 17/11/2026: no lote 11+ o "Sabia que…" aparece em no máximo ~1/3 das músicas e nenhuma estrutura se
    repete em 3 músicas seguidas (o mercado alterna bloco-que-volta, paradas, cumulativa, pergunta e resposta…)."""
    import re
    from pathlib import Path
    lote = [d for d in sorted(Path("canais/laurinha/musicas").glob("[0-9][0-9]_*")) if int(d.name[:2]) >= 11]
    sabia = [d.name for d in lote if re.search(r"^Sabia que", (d / "letra.txt").read_text(encoding="utf-8"), re.M)]
    assert len(sabia) <= round(len(lote) / 3) + 1, f"'Sabia que' em {len(sabia)} de {len(lote)}: {sabia}"
    est = [c.ficha(d).get("estrutura") for d in lote]
    for i in range(len(est) - 2):
        assert not (est[i] == est[i + 1] == est[i + 2]), f"estrutura {est[i]} em 3 seguidas a partir de {lote[i].name}"


def test_master_tames_harsh_suno_highs():
    """Masterização (18/11): faixa com agudo estridente e pouco sub recebe corte na presença/agudo e reforço no sub."""
    from toonstudio.audio.master import FAIXAS, cadeia_eq
    estridente = [2.0, 24.0, 43.0, 16.0, 10.0, 2.5, 1.5]
    _, ganhos = cadeia_eq(estridente)
    assert len(ganhos) == len(FAIXAS)
    assert ganhos[0] > 3 and ganhos[4] < -1 and ganhos[5] < -3 and ganhos[6] < -4
    assert all(abs(g) <= 9.0 for g in ganhos)


def test_sons_do_roteiro_entram_na_mixagem_final(tmp_path, monkeypatch):
    """Efeito do roteiro ("sons" → cena "sfx") é somado ao áudio no tempo certo (com a vinheta antes) e no nível da música."""
    import json
    import numpy as np
    import soundfile as sf
    from toonstudio.audio import sfx
    from toonstudio.composition.marca import _efeitos_sonoros
    import toonstudio.core.config as cfg
    monkeypatch.setattr(cfg, "setting", lambda sec, key, default=None: True if key == "efeitos_sonoros" else default)
    sr = 48000
    t = np.arange(4 * sr) / sr
    musica = (0.1 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    wav = tmp_path / "a.wav"
    sf.write(wav, np.stack([musica, musica], 1), sr)
    ep = {"scenes": [{"duration": 1.0}, {"duration": 3.0, "sfx": [{"t": 0.5, "id": "ding", "volume_db": 0.0}]}]}
    (tmp_path / "episode.json").write_text(json.dumps(ep))
    assert _efeitos_sonoros(tmp_path, wav, 1.0) == 1
    a, _ = sf.read(wav)
    dif = np.abs(a[:, 0] - musica)
    antes, depois = dif[: int(2.45 * sr)].max(), dif[int(2.5 * sr): int(2.6 * sr)].max()
    assert antes < 1e-3 and depois > 0.05                       # entra em 1,0 (vinheta) + 1,0 (cena 1) + 0,5 = 2,5 s
    assert "ding" in sfx.ids() and "latido" not in sfx.ids()    # gravado sem licença anotada não vale


def test_duracao_da_vinheta_le_com_ffprobe():
    """A montagem final mede a vinheta para posicionar os efeitos (quebrou a publicação da 17 quando procurou o ffprobe
    na configuração em vez do sistema)."""
    from toonstudio.composition.marca import BRAND, _duracao
    if (BRAND / "vinheta.mp4").exists():
        assert 2.0 < _duracao(BRAND / "vinheta.mp4") < 10.0


def test_nomes_da_turma_com_a_cor_de_cada_um():
    """No destaque e na letra, LAURINHA sai rosa e LUISINHO azul (antes "LAURINHA E LUISINHO!" saía todo rosa)."""
    from toonstudio.render.brand import CALLOUT_COLORS, _nomes_coloridos
    t = _nomes_coloridos("LAURINHA E LUISINHO!", *CALLOUT_COLORS["amarelo"])
    rosa, azul = CALLOUT_COLORS["rosa"][0], CALLOUT_COLORS["azul"][0]
    assert t.index(rosa) < t.index("LAURINHA") < t.index(azul) < t.index("LUISINHO")


def test_importar_outro_take_troca_o_audio_e_a_analise(tmp_path):
    """A 19 v2 foi importada por cima da v1 e o projeto continuou com a v1 (original e voz separada antigos)."""
    import numpy as np
    import soundfile as sf
    from toonstudio.audio.song import import_song
    a, b = tmp_path / "a.wav", tmp_path / "b.wav"
    sf.write(a, np.zeros(4410, np.float32), 44100)
    sf.write(b, np.ones(8820, np.float32) * 0.1, 44100)
    proj = tmp_path / "ep"
    import_song(a, proj)
    (proj / "analise" / "stems").mkdir(parents=True)
    import_song(b, proj)
    assert sf.info(proj / "musica" / "original.wav").frames == 8820
    assert not (proj / "analise" / "stems").exists()


def test_efeitos_sonoros_desligados_na_config_nao_entram(tmp_path, monkeypatch):
    """config.yaml → clipe.efeitos_sonoros: false (usuário, 19/11): a montagem ignora os "sons" do roteiro."""
    import json
    import numpy as np
    import soundfile as sf
    import toonstudio.core.config as cfg
    from toonstudio.composition.marca import _efeitos_sonoros
    monkeypatch.setattr(cfg, "setting", lambda sec, key, default=None: False if key == "efeitos_sonoros" else default)
    wav = tmp_path / "a.wav"
    sf.write(wav, np.zeros((48000, 2), np.float32), 48000)
    (tmp_path / "episode.json").write_text(json.dumps({"scenes": [{"duration": 1.0, "sfx": [{"t": 0.1, "id": "ding"}]}]}))
    assert _efeitos_sonoros(tmp_path, wav, 0.0) == 0
    assert np.abs(sf.read(wav)[0]).max() == 0



def test_suno_txt_has_nothing_after_the_lyrics_end():
    """26 (20/11): o bloco AVISOS vinha depois do [End]; o usuário copiou 'até o fim da letra' e o Suno CANTOU o aviso."""
    from toonstudio.audio import composer
    p = {"titulo": "T", "ritmo": "R", "bpm": 96, "persona": "P", "voz": "laurinha", "style": "s", "style_curto": "c",
         "exclude": "e", "lyrics": "[Verse]\nLá lá\n[End]\n", "avisos": ["andamento 96 fora da faixa"], "alternativas": []}
    t = composer.texto_suno(p)
    fim = t.rindex("[End]")
    depois = t[fim + len("[End]"):]
    assert "andamento" not in depois and "AVISOS" not in depois
    assert t.index("AVISOS") < t.index("LYRICS")
    assert depois.strip().startswith("=") and "não copie" in depois


def test_limpeza_mantem_build_so_das_3_musicas_mais_recentes(tmp_path):
    """Regra do canal (20/11/2026): só as 3 últimas músicas guardam o `build`; nunca apaga sem MP4 final; o resto fica."""
    from toonstudio.composition.limpeza import limpar_builds

    def proj(nome, mp4=True):
        d = tmp_path / nome
        (d / "build" / "scenes").mkdir(parents=True)
        (d / "build" / "scenes" / "q.png").write_bytes(b"x" * 10)
        (d / "output").mkdir()
        if mp4:
            (d / "output" / "video.mp4").write_bytes(b"v")
        return d

    velhos = [proj("ep01-a"), proj("ep02-b"), proj("ep02-b-short")]
    sem_mp4 = proj("ep03-c", mp4=False)
    novos = [proj("ep04-d"), proj("ep05-e"), proj("ep06-f", mp4=False)]
    teste = proj("teste-x")
    limpar_builds(manter=3, root=tmp_path)
    assert all(not (d / "build").exists() for d in velhos + [teste])
    assert all((d / "output" / "video.mp4").exists() for d in velhos)
    assert (sem_mp4 / "build").exists()
    assert all((d / "build").exists() for d in novos)


def test_proibido_importar_musica_cortada(tmp_path):
    """Regra do canal (20/11/2026): proibido cortar música — o vídeo usa o take inteiro."""
    import pytest
    from toonstudio.audio.song import import_song
    from toonstudio.core.config import StudioError
    for nome in ("v1_editada.wav", "Música (v1 cortada 2m50).wav"):
        f = tmp_path / nome
        f.write_bytes(b"RIFF")
        with pytest.raises(StudioError):
            import_song(f, tmp_path / "proj")


def test_multicanal_perfis_e_projeto(monkeypatch):
    """Multicanal (20/11/2026): Laurinha é o padrão com os caminhos de sempre; Fofolucos tem pasta, marca e entrega próprias;
    o canal de um projeto vem da pasta (projects/<canal>/…)."""
    from toonstudio.core import canal
    from toonstudio.core.config import ROOT
    monkeypatch.delenv(canal.ENV, raising=False)
    la, fo = canal.carregar("laurinha"), canal.carregar("fofolucos")
    assert la.musicas == ROOT / "canais" / "laurinha" / "musicas" and la.windows.name == "Laurinha e Luisinho"
    assert fo.musicas == ROOT / "canais" / "fofolucos" / "musicas" and fo.windows.name == "Fofolucos"
    assert fo.logo_png and fo.logo_png.exists()
    assert canal.atual().id == "laurinha"
    assert canal.id_do_projeto("laurinha/ep28-do-pe-a-cabeca") == "laurinha"
    assert canal.id_do_projeto("fofolucos/ep01-teste") == "fofolucos"
    monkeypatch.setenv(canal.ENV, "fofolucos")
    from toonstudio.audio import composer
    assert composer.estilos()["canal"]["versao"] == "F5"
    assert "fofolucos" in composer.vozes()["vozes"]
