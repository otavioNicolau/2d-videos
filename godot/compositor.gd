extends Node2D
## Compõe uma cena a partir de um job JSON gerado pelo pipeline Python e grava pelo Movie Maker.
##
## O job traz TUDO por quadro (câmera, posição de cada personagem, quadro renderizado pelo OpenToonz):
## o Godot não decide timing nem pose — só posiciona, aplica parallax/zoom e ordena em profundidade.
## Uso: godot --path godot --write-movie out/f.png --fixed-fps 24 -- --job=/abs/job.json

var job: Dictionary
var frames := 0
var i := 0
var cam: Camera2D
var layers: Array = []        # [Sprite2D, parallax, scale]
var performers: Array = []    # [Sprite2D, dict]
var fade_rect: ColorRect
var particles: Node2D
var tex_cache := {}

func _fail(msg: String) -> void:
	printerr("COMPOSITOR_ERROR ", msg)
	get_tree().quit(1)

func _tex(path: String, mipmaps := false) -> Texture2D:
	if tex_cache.has(path):
		return tex_cache[path]
	var img := Image.load_from_file(path)
	if img == null or img.is_empty():
		_fail("imagem não carregou: " + path)
		return null
	if mipmaps:
		img.generate_mipmaps()  # cenário (carregado uma vez): redução sem serrilhar
	var t := ImageTexture.create_from_image(img)
	if tex_cache.size() > 6:
		tex_cache.clear()
	tex_cache[path] = t
	return t

func _ready() -> void:
	var path := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--job="):
			path = a.substr(6)
	if path == "":
		_fail("faltou --job=")
		return
	var txt := FileAccess.get_file_as_string(path)
	var parsed = JSON.parse_string(txt)
	if typeof(parsed) != TYPE_DICTIONARY:
		_fail("job inválido: " + path)
		return
	job = parsed
	frames = int(job["frames"])
	RenderingServer.set_default_clear_color(Color(0, 0, 0))
	for l in job["layers"]:
		var s := Sprite2D.new()
		s.centered = bool(l.get("center", false))
		s.texture = _tex(l["file"], true)
		s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		var k := 1.0 / float(l["scale"])
		s.scale = Vector2(k, k)
		s.z_index = int(l["z"])
		add_child(s)
		layers.append([s, float(l["parallax"]), l])
	for p in job["performers"]:
		var s := Sprite2D.new()
		s.centered = false
		s.z_index = int(p["z"])
		s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		add_child(s)
		performers.append([s, p])
	cam = Camera2D.new()
	add_child(cam)
	cam.make_current()
	if job.has("particles") and job["particles"].size() > 0:
		var pl := CanvasLayer.new()
		pl.layer = 1
		add_child(pl)
		particles = Node2D.new()
		particles.set_script(load("res://particles.gd"))
		particles.specs = job["particles"]
		particles.fps = float(job["fps"])
		particles.W = float(job["resolution"][0])
		particles.H = float(job["resolution"][1])
		pl.add_child(particles)
	var cl := CanvasLayer.new()
	cl.layer = 2
	add_child(cl)
	fade_rect = ColorRect.new()
	fade_rect.color = Color(0, 0, 0, 0)
	fade_rect.size = Vector2(job["resolution"][0], job["resolution"][1])
	cl.add_child(fade_rect)
	print("COMPOSITOR_READY frames=", frames, " renderer=", RenderingServer.get_current_rendering_method())

func _process(_delta: float) -> void:
	if i >= frames:
		print("COMPOSITOR_DONE frames=", i)
		get_tree().quit()
		return
	var c: Array = job["camera"][i]
	var cx := float(c[0])
	var cy := float(c[1])
	var z := float(c[2])
	cam.position = Vector2(cx, cy)
	cam.zoom = Vector2(z, z)
	# parallax relativo ao deslocamento da câmera desde a posição "de casa" (meia tela):
	# a camada de fator f mostra o trecho centrado em (cx - W/2)*f + W/2 → sprite em (cx - W/2)*(1-f)
	var hw := float(job["resolution"][0]) / 2.0
	var hh := float(job["resolution"][1]) / 2.0
	for l in layers:
		var f: float = l[1]
		var ld: Dictionary = l[2]
		if ld.get("fixed", false):
			# camada gráfica presa à tela (fundos de dança): centrada na câmera; zoom ainda aplica
			var off := Vector2(float(ld.get("x", 0.0)), float(ld.get("y", 0.0)))
			l[0].position = Vector2(cx, cy) + (off if l[0].centered else off - Vector2(hw, hh))
		else:
			l[0].position = Vector2((cx - hw) * (1.0 - f), (cy - hh) * (1.0 - f))
		if ld.has("angles"):
			l[0].rotation_degrees = float(ld["angles"][i])
		if ld.has("anim"):
			# [dx, dy, escala] por quadro: fundo que flutua, desliza e pulsa na batida
			var an: Array = ld["anim"][i]
			l[0].position += Vector2(float(an[0]), float(an[1]))
			var kk := float(an[2]) / float(ld["scale"])     # an[2] = fator de pulso (1 = tamanho normal)
			l[0].scale = Vector2(kk, kk)
	for pr in performers:
		var s: Sprite2D = pr[0]
		var p: Dictionary = pr[1]
		var tr: Array = p["track"][i]
		var file: String = p["dir"] + "/" + (p["pattern"] % (i + 1))
		s.texture = _tex(file)
		var depth := float(tr[2])
		var k := depth / float(p["level_scale"])
		s.scale = Vector2(k, k)
		s.position = Vector2(float(tr[0]) - float(p["anchor"][0]) * k, float(tr[1]) - float(p["anchor"][1]) * k)
		s.visible = bool(tr[3])
	if particles:
		particles.frame = i
		particles.beat_hit = float(job["beat_hit"][i]) if job.has("beat_hit") else 0.0
		particles.queue_redraw()
	var fl := float(job["flash"][i]) if job.has("flash") else 0.0
	if fl > 0.0:
		fade_rect.color = Color(1, 1, 1, fl)        # clarão branco na batida (entrada de refrão)
	else:
		fade_rect.color = Color(0, 0, 0, float(job["fade"][i]) if job.has("fade") else 0.0)
	i += 1
