extends Sprite2D
class_name Piece

# 퍼즐 조각 (Match-3)

@export var type: int = 0
var grid_position: Vector2i

func initialize(new_type: int, start_pos: Vector2) -> void:
	type = new_type
	position = start_pos
	# 타입에 따라 텍스처/색상 변경 (여기서는 modulate 사용 예시)
	match type:
		0: self.modulate = Color.RED
		1: self.modulate = Color.GREEN
		2: self.modulate = Color.BLUE
		3: self.modulate = Color.YELLOW
		4: self.modulate = Color.PURPLE
		_: self.modulate = Color.WHITE

func move_to(target_pos: Vector2, duration: float = 0.3) -> void:
	var tween = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "position", target_pos, duration)

func destroy() -> void:
	var tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tween.tween_property(self, "scale", Vector2.ZERO, 0.2)
	tween.tween_callback(queue_free)

func set_selected(selected: bool) -> void:
	if selected:
		self.modulate.a = 0.7
		self.scale = Vector2(1.1, 1.1)
	else:
		self.modulate.a = 1.0
		self.scale = Vector2(1.0, 1.0)
