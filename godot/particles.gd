extends Node2D
## Partículas decorativas determinísticas (dependem só do número do quadro → render reproduzível).
## Tipos: bolhas, confete, notas, estrelas, coracoes, chuva. Ficam acima dos personagens e abaixo dos textos.

var specs: Array = []
var frame := 0
var fps := 30.0
var W := 1920.0
var H := 1080.0
var beat_hit := 0.0      # 0..1, impulso da batida (vem do job) — faz as partículas "pulsarem" no tempo

const CONF_COLORS := [Color("#FF5A5F"), Color("#FFC21A"), Color("#2EC4B6"), Color("#7B3FD1"), Color("#3C8BF0"), Color("#FF8A1F"), Color("#F76FB3")]

func _rnd(seed: int, k: int) -> float:
	# hash determinístico → [0, 1)
	var x := sin(float(seed * 9301 + k * 49297) * 0.0001 + float(k) * 12.9898) * 43758.5453
	return x - floor(x)

func _draw() -> void:
	var t := frame / fps
	for sp in specs:
		var kind: String = sp["type"]
		var n: int = int(sp.get("count", 12))
		var sd: int = int(sp.get("seed", 1))
		var sc: float = float(sp.get("scale", 1.0))
		for i in range(n):
			var r1 := _rnd(sd, i * 7 + 1)
			var r2 := _rnd(sd, i * 7 + 2)
			var r3 := _rnd(sd, i * 7 + 3)
			var r4 := _rnd(sd, i * 7 + 4)
			var size := (18.0 + 42.0 * r3) * sc
			if kind == "bolhas":
				var vy := 40.0 + 70.0 * r2
				var y := H + 80.0 - fmod(r1 * (H + 160.0) + vy * t, H + 160.0)
				var x := r4 * W + 40.0 * sin(t * (0.8 + r2) + i)
				var rr := size * (1.0 + 0.08 * beat_hit)
				draw_circle(Vector2(x, y), rr, Color(1, 1, 1, 0.10))
				draw_arc(Vector2(x, y), rr, 0, TAU, 32, Color(1, 1, 1, 0.75), 2.5, true)
				draw_arc(Vector2(x, y), rr * 0.72, PI * 1.1, PI * 1.45, 10, Color(1, 1, 1, 0.9), 3.5, true)
				draw_circle(Vector2(x + rr * 0.35, y - rr * 0.4), rr * 0.12, Color(1, 1, 1, 0.9))
			elif kind == "confete":
				var vy2 := 90.0 + 140.0 * r2
				var y2 := fmod(r1 * (H + 100.0) + vy2 * t, H + 100.0) - 50.0
				var x2 := r4 * W + 60.0 * sin(t * (1.5 + r3 * 2.0) + i * 1.7)
				var ang := t * (2.0 + 4.0 * r3) + i
				var c: Color = CONF_COLORS[i % CONF_COLORS.size()]
				draw_set_transform(Vector2(x2, y2), ang, Vector2(1.0, 0.35 + 0.65 * abs(sin(t * 3.0 + i))))
				draw_rect(Rect2(-size * 0.25, -size * 0.12, size * 0.5, size * 0.24), c)
				draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
			elif kind == "chuva":
				# gotinhas azuis caindo inclinadas (chuva fininha: count baixo; chuva forte: count alto)
				var vy4 := 700.0 + 500.0 * r2
				var y4 := fmod(r1 * (H + 200.0) + vy4 * t, H + 200.0) - 100.0
				var x4 := fposmod(r4 * W - 0.18 * vy4 * t, W)
				var gl := size * 0.9
				var pts := PackedVector2Array([Vector2(x4, y4 - gl), Vector2(x4 + gl * 0.28, y4), Vector2(x4, y4 + gl * 0.32), Vector2(x4 - gl * 0.28, y4)])
				draw_colored_polygon(pts, Color("#9CD8FF"))
				draw_polyline(PackedVector2Array([pts[0], pts[1], pts[2], pts[3], pts[0]]), Color("#4A9BE0"), 2.0, true)
			elif kind == "estrelas" or kind == "coracoes" or kind == "notas":
				var vx := (r2 - 0.5) * 60.0
				var vy3 := -(25.0 + 45.0 * r3)
				var x3 := fposmod(r4 * W + vx * t, W)
				var y3 := fposmod(r1 * H + vy3 * t, H)
				var pulse := 1.0 + 0.25 * beat_hit
				var rot := sin(t * 1.5 + i) * 0.4
				draw_set_transform(Vector2(x3, y3), rot, Vector2(pulse, pulse))
				if kind == "estrelas":
					_star(size * 0.55, Color(1, 1, 1, 0.9) if i % 3 == 0 else Color("#FFE14D"))
				elif kind == "coracoes":
					_heart(size * 0.5, Color("#FF6B8B") if i % 2 == 0 else Color(1, 1, 1, 0.85))
				else:
					_note(size * 0.5, Color("#FF7EB6") if i % 2 == 0 else Color(1, 1, 1, 0.9))
				draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)

func _star(r: float, c: Color) -> void:
	var pts := PackedVector2Array()
	for k in range(10):
		var rr := r if k % 2 == 0 else r * 0.45
		var a := -PI / 2 + k * PI / 5
		pts.append(Vector2(cos(a), sin(a)) * rr)
	draw_colored_polygon(pts, c)

func _heart(r: float, c: Color) -> void:
	var pts := PackedVector2Array()
	for k in range(40):
		var a := k * TAU / 40.0
		var x := 16.0 * pow(sin(a), 3)
		var y := -(13.0 * cos(a) - 5.0 * cos(2 * a) - 2.0 * cos(3 * a) - cos(4 * a))
		pts.append(Vector2(x, y) * r / 16.0)
	draw_colored_polygon(pts, c)

func _note(r: float, c: Color) -> void:
	# colcheia: cabeça inclinada + haste + bandeirinha (já dentro da transformação da partícula)
	var head := PackedVector2Array()
	for k in range(20):
		var a := k * TAU / 20.0
		head.append(Vector2(cos(a) * r * 0.42, sin(a) * r * 0.3).rotated(-0.4) + Vector2(-r * 0.25, r * 0.6))
	draw_colored_polygon(head, c)
	draw_line(Vector2(r * 0.12, r * 0.55), Vector2(r * 0.12, -r * 0.85), c, max(2.0, r * 0.16))
	draw_colored_polygon(PackedVector2Array([Vector2(r * 0.12, -r * 0.85), Vector2(r * 0.7, -r * 0.45),
		Vector2(r * 0.6, -r * 0.2), Vector2(r * 0.12, -r * 0.5)]), c)
