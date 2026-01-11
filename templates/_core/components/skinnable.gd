class_name Skinnable extends Node
## 스킨 적용 컴포넌트 - 시각적 요소에 부착하여 스킨 변경 시 자동 업데이트
## 이 컴포넌트는 SkinManager의 시그널을 구독하고 부모 노드의 비주얼을 교체함

enum SkinnableType {
	PLAYER,
	OBSTACLE,
	BACKGROUND,
	UI,
	DECORATION,
	CUSTOM
}

@export var skinnable_type: SkinnableType = SkinnableType.CUSTOM
@export var custom_skin_key: String = ""  # CUSTOM 타입일 때 사용할 키

# 대상 노드 참조 (Sprite2D, Sprite3D, MeshInstance3D 등)
@export var target_sprite: Sprite2D
@export var target_sprite_3d: Sprite3D
@export var target_mesh: MeshInstance3D
@export var target_audio: AudioStreamPlayer

var _original_texture: Texture2D
var _original_stream: AudioStream


func _ready() -> void:
	# 원본 저장
	_save_originals()
	
	# 스킨 변경 시그널 연결
	if SkinManager:
		SkinManager.skin_changed.connect(_on_skin_updated)
		
		# 현재 스킨 즉시 적용
		if SkinManager.current_skin:
			_on_skin_updated(SkinManager.current_skin)


func _save_originals() -> void:
	"""원본 비주얼 저장 (폴백용)"""
	if target_sprite:
		_original_texture = target_sprite.texture
	if target_audio:
		_original_stream = target_audio.stream


func _on_skin_updated(skin: Resource) -> void:
	"""스킨 변경 시 호출"""
	if skin == null:
		return
	
	match skinnable_type:
		SkinnableType.PLAYER:
			_apply_player_skin(skin)
		SkinnableType.OBSTACLE:
			_apply_obstacle_skin(skin)
		SkinnableType.BACKGROUND:
			_apply_background_skin(skin)
		SkinnableType.CUSTOM:
			_apply_custom_skin(skin)


func _apply_player_skin(skin: Resource) -> void:
	"""플레이어 스킨 적용"""
	if not get_parent().is_in_group("Player"):
		return
	
	# 텍스처 적용
	if target_sprite and skin.has("player_texture") and skin.player_texture:
		target_sprite.texture = skin.player_texture
	
	# 3D 모델/씬 교체 로직은 player_scene 사용
	# (실제 구현 시 기존 노드 제거 후 새 씬 인스턴스화 필요)


func _apply_obstacle_skin(skin: Resource) -> void:
	"""장애물 스킨 적용"""
	if not get_parent().is_in_group("Obstacle"):
		return
	
	# obstacle_scene에서 텍스처 추출 또는 직접 교체


func _apply_background_skin(skin: Resource) -> void:
	"""배경 스킨 적용"""
	if target_sprite and skin.has("ground_texture") and skin.ground_texture:
		target_sprite.texture = skin.ground_texture


func _apply_custom_skin(skin: Resource) -> void:
	"""커스텀 키 기반 스킨 적용"""
	if custom_skin_key.is_empty():
		return
	
	if skin.has(custom_skin_key):
		var value = skin.get(custom_skin_key)
		
		if value is Texture2D and target_sprite:
			target_sprite.texture = value
		elif value is AudioStream and target_audio:
			target_audio.stream = value


func reset_to_original() -> void:
	"""원본 비주얼로 복원"""
	if target_sprite and _original_texture:
		target_sprite.texture = _original_texture
	if target_audio and _original_stream:
		target_audio.stream = _original_stream
