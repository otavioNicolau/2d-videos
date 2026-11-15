extends Node2D
# F0: compõe cenário (camadas Krita + parallax) + nível de personagem (render OpenToonz), câmera em movimento.
const FPS := 24
const DUR := 2.0
var root_dir := ""
var char_frames: Array[Texture2D] = []
var layers: Array = []   # [Sprite2D, factor]
var cam: Camera2D
var ch: Sprite2D
var t := 0.0
var frame := 0

func _tex(p: String) -> Texture2D:
	var img := Image.load_from_file(p)
	if img == null:
		push_error("SPIKE_ERROR load " + p)
	return ImageTexture.create_from_image(img)

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--root="):
			root_dir = a.substr(7)
	var info: Array = JSON.parse_string(FileAccess.get_file_as_string(root_dir + "/bg/layers.json"))
	var factors := {"BG_ceu": 0.15, "MG_colinas": 0.5, "FG_arvore": 1.25}
	var z := 0
	for l in info:
		var s := Sprite2D.new()
		s.centered = false
		s.texture = _tex(root_dir + "/bg/" + l["name"] + ".png")
		s.position = Vector2(l["x"], l["y"])
		s.z_index = z if l["name"] != "FG_arvore" else 10
		z += 1
		add_child(s)
		layers.append([s, factors.get(l["name"], 1.0), s.position])
	for i in range(1, 25):
		char_frames.append(_tex(root_dir + "/render/out.%04d.png" % i))
	ch = Sprite2D.new(); ch.centered = false; ch.z_index = 5; add_child(ch)
	cam = Camera2D.new(); cam.anchor_mode = Camera2D.ANCHOR_MODE_FIXED_TOP_LEFT; add_child(cam); cam.make_current()
	print("SPIKE_READY renderer=", RenderingServer.get_current_rendering_method(), " adapter=", RenderingServer.get_video_adapter_name())

func _process(delta: float) -> void:
	var u := clampf(float(frame) / (DUR * FPS), 0.0, 1.0)
	var e := u * u * (3.0 - 2.0 * u)           # ease in/out
	var cam_x := 300.0 * e
	# parallax manual: cada camada se desloca proporcional ao fator (câmera fixa em 0, mundo se move)
	for l in layers:
		l[0].position.x = l[2].x - cam_x * (l[1] - 1.0) - cam_x
	ch.position.x = -cam_x
	ch.texture = char_frames[frame % char_frames.size()]
	frame += 1
	if frame > int(DUR * FPS):
		print("SPIKE_DONE frames=", frame)
		get_tree().quit()
