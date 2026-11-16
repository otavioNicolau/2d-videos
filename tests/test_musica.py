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
