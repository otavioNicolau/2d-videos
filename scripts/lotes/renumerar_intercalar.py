"""Intercala as músicas novas entre 12 e 49 (18/11/2026). Datas presas: 16 Carnaval, 23 Páscoa, 29 Mães, 34 Junina,
42 Pais, 49 Crianças. Sem ritmo repetido em sequência e sem a mesma estrutura 3 vezes seguidas."""
import json, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; M = ROOT / "musicas"
ORDEM = ["mee_carneirinho", "andar_de_pinguim", "castelo_de_areia", "bolha_de_sabao", "carnaval_da_turminha", "que_forma_e_essa",
 "robo_dancarino", "conta_vantagem", "dino_pisa_forte", "dorme_acorda", "roda_rodinha", "pula_coelhinho", "cara_de_que",
 "polvo_oito_bracos", "gelatina", "careta_de_limao", "do_pe_a_cabeca", "mamae_querida", "bibi_fomfom", "chule_de_sapo",
 "bicho_faz_assim", "devagar_devagarinho", "pula_pipoca", "banda_da_turminha", "espelho_espelhinho", "canoa_de_papel",
 "tum_tum_coracao", "blub_blub_peixinho", "quente_ou_frio", "abelhinha", "meu_papai", "danca_da_minhoca",
 "palavrinhas_magicas", "ovinho_no_ninho", "pescoco_de_girafa", "atchim", "quando_eu_crescer", "dia_de_brincar"]
atual = {re.sub(r"^\d\d_", "", d.name): d for d in M.glob("[0-9][0-9]_*") if int(d.name[:2]) >= 12}
assert set(atual) == set(ORDEM) and len(ORDEM) == 38, set(atual) ^ set(ORDEM)
fichas = [json.loads((atual[s] / "ficha.json").read_text(encoding="utf-8")) for s in ORDEM]
for a, b in zip(fichas, fichas[1:]):
    assert a["ritmo"] != b["ritmo"], (a["titulo"], b["titulo"], a["ritmo"])
for a, b, c in zip(fichas, fichas[1:], fichas[2:]):
    assert not (a["estrutura"] == b["estrutura"] == c["estrutura"]), (a["titulo"], b["titulo"], c["titulo"])
for s in ORDEM:
    subprocess.run(["git", "mv", str(atual[s]), str(M / f"tmp_{s}")], cwd=ROOT, check=True)
for i, s in enumerate(ORDEM):
    subprocess.run(["git", "mv", str(M / f"tmp_{s}"), str(M / f"{12 + i:02d}_{s}")], cwd=ROOT, check=True)
    print(f"{12 + i:02d} {s}")
