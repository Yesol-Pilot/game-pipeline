extends Node
## 스킨 매니저 (Skin Manager) - 런타임 스킨 관리 싱글톤
## 게임의 시각적 테마를 동적으로 교체하는 핵심 엔진

const SkinConfig = preload("res://_core/resources/skin_config.gd")

var current_skin: Resource = null
var default_skin_path: String = "res://skins/default/config.tres"
var _skin_cache: Dictionary = {}

signal skin_changed(new_skin: Resource)
signal skin_load_failed(path: String, error: String)


func _ready() -> void:
	# 기본 스킨 로드
	load_skin(default_skin_path)
	print("[스킨매니저] 초기화 완료")


func load_skin(skin_path: String) -> bool:
	"""스킨 설정 파일 로드"""
	# 캐시 확인
	if _skin_cache.has(skin_path):
		_apply_skin(_skin_cache[skin_path])
		return true
	
	# 리소스 로드
	if not ResourceLoader.exists(skin_path):
		skin_load_failed.emit(skin_path, "파일이 존재하지 않습니다")
		_fallback_to_default()
		return false
	
	var skin = load(skin_path)
	if skin == null:
		skin_load_failed.emit(skin_path, "리소스 로드 실패")
		_fallback_to_default()
		return false
	
	# 유효성 검사
	if not _validate_skin(skin):
		skin_load_failed.emit(skin_path, "필수 필드 누락")
		_fallback_to_default()
		return false
	
	# 캐시 저장 및 적용
	_skin_cache[skin_path] = skin
	_apply_skin(skin)
	return true


func _apply_skin(skin: Resource) -> void:
	"""스킨 적용 및 시그널 발송"""
	current_skin = skin
	skin_changed.emit(skin)
	EventBus.skin_changed.emit(skin)
	print("[스킨매니저] 스킨 적용: ", skin.theme_name if skin.has("theme_name") else "이름 없음")


func _validate_skin(skin: Resource) -> bool:
	"""스킨 필수 필드 검증"""
	# 최소 필수 필드 확인
	if not skin.has("theme_name"):
		return false
	return true


func _fallback_to_default() -> void:
	"""기본 스킨으로 폴백"""
	if current_skin != null:
		return  # 이미 스킨이 있으면 유지
	
	if default_skin_path != "" and ResourceLoader.exists(default_skin_path):
		var default_skin = load(default_skin_path)
		if default_skin:
			_apply_skin(default_skin)


func get_texture(key: String) -> Texture2D:
	"""현재 스킨에서 텍스처 가져오기"""
	if current_skin == null:
		return null
	
	if current_skin.has(key) and current_skin.get(key) is Texture2D:
		return current_skin.get(key)
	
	return null


func get_scene(key: String) -> PackedScene:
	"""현재 스킨에서 씬 가져오기"""
	if current_skin == null:
		return null
	
	if current_skin.has(key) and current_skin.get(key) is PackedScene:
		return current_skin.get(key)
	
	return null


func get_audio(key: String) -> AudioStream:
	"""현재 스킨에서 오디오 가져오기"""
	if current_skin == null:
		return null
	
	if current_skin.has(key) and current_skin.get(key) is AudioStream:
		return current_skin.get(key)
	
	return null


# ===== 외부 에셋 로딩 (모딩 지원) =====

static func load_external_texture(path: String) -> Texture2D:
	"""런타임 외부 텍스처 로딩"""
	if not FileAccess.file_exists(path):
		return null
	var image = Image.load_from_file(path)
	if image == null:
		return null
	return ImageTexture.create_from_image(image)


static func load_external_audio(path: String) -> AudioStream:
	"""런타임 외부 오디오 로딩"""
	if not FileAccess.file_exists(path):
		return null
	
	# OGG 파일
	if path.ends_with(".ogg"):
		var file = FileAccess.open(path, FileAccess.READ)
		if file == null:
			return null
		var stream = AudioStreamOggVorbis.new()
		stream.data = file.get_buffer(file.get_length())
		return stream
	
	return null
