"""Peças comuns dos roteiros (21 em diante): tempos dos planos, palavras, destaques, a BANDA da turma, telas divididas e o
fechamento (chaves dentro do plano, nada depois do fim, gravação do roteiro.json com escala 1,45).
Uso: from _comum import Roteiro   (os scripts rodam com scripts/roteiros no sys.path)
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

from toonstudio.composition.clip_draft import _q, _snap, blocos

ROOT = Path(__file__).resolve().parents[2]
LA, LU = "laurinha", "luisinho"
SALAO = "plano_salao"


# ── enquadramentos dos dois canais (Fofolucos 21/11 → Laurinha 21/11: "cenas próximas") ──
# misturar CABEÇA / BUSTO / CORPO no mesmo bloco; a câmera ainda sobe sozinha se cabelo/chifre/antena for cortar
# (canal.json camera_protege_topo) e o boneco é desenhado na resolução do plano (nivel_escala_auto)
def cab(x=1300):
    return {"x": x, "y": 500, "zoom": 1.85, "zoom_fim": 1.95}


def busto(x=1300, y=560):
    return {"x": x, "y": y, "zoom": 1.55, "zoom_fim": 1.62}


def corpo(x=1300, x_fim=None):
    c = {"x": x, "y": 560, "zoom": 1.0, "zoom_fim": 1.08}
    if x_fim:
        c["x_fim"] = x_fim
    return c


GCAM = {"x": 960, "y": 560, "zoom": 1.0, "zoom_fim": 1.06}       # fundos gráficos (raios/xadrez/brilho/padrão)


def call(t, text, color, **kw):
    return {"t": round(max(0.0, t), 2), "text": text, "color": color, **kw}


class Roteiro:
    def __init__(self, projeto: str, musica: str, canta: str):
        from toonstudio.core.canal import carregar, id_do_projeto      # multicanal: "fofolucos/ep01-…"
        self.proj = ROOT / "projects" / projeto
        self.mus = carregar(id_do_projeto(projeto)).musicas / musica
        self.song = json.loads((self.proj / "analise" / "song.json").read_text(encoding="utf-8"))
        self.lines = json.loads((self.proj / "analise" / "letra.json").read_text(encoding="utf-8"))["lines"]
        self.beats = self.song["beats"]
        self.canta = canta
        self.estilos = itertools.cycle(["chute", "joelho", "sapinho", "cintura", "pezinho", "marcha", "lado", "balanco",
                                        "bracos", "gingado", "palmas", "festa"])
        self.info, occ = {}, {}
        for b in blocos(self.song):
            occ[b["tipo"]] = occ.get(b["tipo"], 0) + 1
            self.info[f"{b['tipo']}#{occ[b['tipo']]}"] = (b, [l for l in self.lines if b["s"] - 0.05 <= l["s"] < b["e"] - 0.05])
        self.partes: dict = {}

    # ── tempos ──
    def tempos(self, key, planos):
        b, bl = self.info[key]
        res, li, t = [], 0, b["s"]
        for k, p in enumerate(planos):
            n = int(p.get("linhas", 1 if "seg" not in p else 0))
            st = b["s"] if k == 0 else (_snap(bl[li]["s"] - 0.12, self.beats) if n > 0 and li < len(bl) else t)
            mine = bl[li:li + n] if n > 0 else []
            li += n
            res.append([st, None, mine])
            t = st + float(p["seg"]) if "seg" in p else (mine[-1]["e"] if mine else st + 2.0)
        for k in range(len(res)):
            res[k][1] = res[k + 1][0] if k + 1 < len(res) else b["e"]
        return [(_q(a), _q(e), m) for a, e, m in res]

    def bloco(self, key):
        return self.info[key]

    @staticmethod
    def tps(t0, versos, *alvos):
        alvos = tuple(a.lower() for a in alvos)
        return [round(max(0.0, w["s"] - t0), 2) for l in versos for w in l["words"] if w["w"].lower().strip("!?,.…:()\"'") in alvos]

    def tp(self, t0, versos, *alvos, default=0.4):
        r = self.tps(t0, versos, *alvos)
        return r[0] if r else default

    def estilo(self):
        return next(self.estilos)

    # ── a banda (19/11: a turma toca teclado, bateria e sax) ──
    def banda(self, cen, d, teclado=False, cam=None, extra=None, fx=None, sax=LA, bateria=LU):
        p = {"seg": round(d, 2), "cenario": cen, "camera": cam or {"x": 1300, "y": 600, "zoom": 1.1, "zoom_fim": 1.18},
             "fx": fx or ["notas"],
             # A4 (19/11): bateria aberta (o Luisinho aparece por cima), baqueta seguindo o antebraço, prato/caixa/tom
             # NA grade de batidas da música — a bateria "dança" kit_a4 no mesmo compasso do toca_bateria_a4
             "objetos": {"bat": {"id": "bateria_show", "x": 1700, "y": 940, "z": 4, "depth": 0.6,
                                 "acoes": [{"t": 0.0, "do": "dance", "style": "kit_a4", "dur": "resto"}]}},
             "atores": {bateria: {"x": 1700, "y": 930, "turn": -0.2, "z": 3, "segura": "baqueta_a4", "segura_f": "baqueta_a4",
                                  "acoes": [{"t": 0.0, "do": "dance", "style": "toca_bateria_a4", "dur": "resto"}]}}}
        if teclado:
            p["objetos"]["tec"] = {"id": "teclado_inst", "x": 800, "y": 940, "z": 4, "depth": 0.62,
                                   "keys": [{"t": 0.0, "pose": {"tecla": 0.0}, "ease": "step"}, {"t": round(d, 2), "pose": {"tecla": round(d * 2, 1)}, "ease": "linear"}]}
            p["atores"][sax] = {"x": 800, "y": 930, "turn": 0.2, "z": 3, "acoes": [{"t": 0.0, "do": "dance", "style": "toca_teclado", "dur": "resto"}]}
        else:
            p["atores"][sax] = {"x": 800, "turn": 0.3, "segura": "saxofone", "acoes": [{"t": 0.0, "do": "dance", "style": "toca_sax", "dur": "resto"}]}
        if extra:
            p["atores"].update(extra)
        return p

    @staticmethod
    def dividida(painel_a, painel_b, linhas=None, layout="vertical", callout=None):
        p = {"tela_dividida": {"layout": layout, "paineis": [painel_a, painel_b]}}
        if linhas is not None:
            p["linhas"] = linhas
        if callout:
            p["callout"] = callout
        return p

    # ── fechamento ──
    @staticmethod
    def _transicoes(keys):
        ultimo, out = {}, []
        for k in keys:
            k = dict(k)
            if k.get("ease", "inout") != "step" and "in" not in k:
                prev = [ultimo[c] for c in k["pose"] if c in ultimo]
                if prev:
                    k["in"] = round(max(0.0, k["t"] - max(prev) - 0.03), 3)
            for c in k["pose"]:
                ultimo[c] = k["t"]
            out.append(k)
        return out

    def salvar(self, nota: str, escala: float = 1.45):
        for chave, planos in self.partes.items():
            k_info = chave if chave in self.info else f"{chave}#1"
            for p, (t0, t1, _) in zip(planos, self.tempos(k_info, planos)):
                p["cantam"] = p.get("cantam") or [self.canta]          # Fofolucos: cada plano escolhe quem "canta"
                d = t1 - t0
                assert d >= 0.6, (chave, t0, t1)
                if p.get("tremor"):
                    p["tremor"] = [round(t, 2) for t in p["tremor"] if 0.0 <= t < d - 0.15]
                subs = [p] + list((p.get("tela_dividida") or {}).get("paineis", []))
                for sb in subs:
                    for a in (sb.get("atores") or {}).values():
                        a["acoes"] = [ac for ac in a.get("acoes", []) if ac["t"] < d - 0.3] or a.get("acoes", [])[:1]
                        if a.get("keys"):
                            a["keys"] = [k for k in a["keys"] if k["t"] < d - 0.05]
                    for o in (sb.get("objetos") or {}).values():
                        if o.get("keys"):
                            ks = [dict(k, t=round(min(k["t"], d - 0.04), 3)) if d - 0.04 < k["t"] <= d + 0.06 else k for k in o["keys"]]
                            o["keys"] = self._transicoes(sorted([k for k in ks if k["t"] <= d - 0.02], key=lambda k: k["t"]))
        faltam = [k for k in self.info if k not in self.partes and k.split("#")[0] not in self.partes]
        assert not faltam, faltam
        rot = {"schema": "roteiro-1.0", "escala_personagens": escala, "nota": nota, "partes": self.partes}
        (self.mus / "roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        n = sum(len(v) for v in self.partes.values())
        print("roteiro:", n, "planos ·", round(self.song["duration"] / n, 1), "s por plano")
        for chave, planos in self.partes.items():
            k_info = chave if chave in self.info else f"{chave}#1"
            print(chave, [round(t1 - t0, 1) for t0, t1, _ in self.tempos(k_info, planos)])

    # ── final padrão (convite) ──
    def convite(self, cen_close, cen_casa="plano_casa_frente", quem=None, gostou="GOSTOU?", extra_casa=None):
        quem = quem or self.canta
        return [
            {"linhas": 1, "cenario": cen_close, "camera": f"close:{quem}", "callout": [call(0.3, gostou, "azul")],
             "atores": {quem: {"x": 1300, "acoes": [{"t": 0.1, "do": "apontar_camera", "dur": "resto"}]}}},
            {"linhas": 1, "cenario": "danca_bolinhas_amarelo", "callout": [call(0.3, "DÁ UM JOINHA!", "azul")], "fx": ["estrelas"],
             "objetos": {"joinha": {"x": 1380, "y": 900, "z": 3, "depth": 1.3,
                                    "keys": [{"t": 0.0, "pose": {"escala": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"}]}},
             "atores": {quem: {"x": 680, "acoes": [{"t": 0.2, "do": "bacana", "dur": "resto"}]}}},
            {"linhas": 1, "cenario": cen_casa, "camera": {"x": 1300, "y": 540, "zoom": 1.1}, "callout": [call(0.3, "CHAMA O PAPAI E A MAMÃE!", "verde")],
             "objetos": extra_casa or {},
             "atores": {"mamae": {"x": 1100, "turn": 0.2, "acoes": [{"t": 0.2, "do": "wave", "dur": 1.4}]},
                        quem: {"x": 1450, "turn": -0.3, "acoes": [{"t": 0.1, "do": "point", "dur": "resto"}]}}},
            {"linhas": 1, "cenario": "danca_raios_vermelho", "callout": [call(0.5, "INSCREVA-SE!", "vermelho")], "fx": ["coracoes"],
             "objetos": {"botao": {"id": "botao_inscrever", "x": 1260, "y": 760, "z": 3, "depth": 1.2,
                                   "keys": [{"t": 0.0, "pose": {"escala": 0.0, "aperta": 0.0}}, {"t": 0.4, "pose": {"escala": 1.0}, "ease": "back"},
                                            {"t": 1.6, "pose": {"aperta": 1.0}, "ease": "out"}, {"t": 1.9, "pose": {"aperta": 0.0}, "ease": "in"}]}},
             "atores": {quem: {"x": 600, "acoes": [{"t": 0.2, "do": "point", "dur": "resto"}]}}},
        ]
