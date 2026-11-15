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
		s.centered = false
		s.texture = _tex(l["file"], true)
		s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		var k := 1.0 / float(l["scale"])
		s.scale = Vector2(k, k)
		s.z_index = int(l["z"])
		add_child(s)
		layers.append([s, float(l["parallax"])])
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
	var cl := CanvasLayer.new()
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
		l[0].position = Vector2((cx - hw) * (1.0 - f), (cy - hh) * (1.0 - f))
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
	fade_rect.color.a = float(job["fade"][i]) if job.has("fade") else 0.0
	i += 1
