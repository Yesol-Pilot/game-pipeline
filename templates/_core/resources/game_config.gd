class_name GameConfig
extends Resource

# 게임 전역 설정
@export_group("Audio")
@export var master_volume: float = 1.0
@export var music_volume: float = 0.8
@export var sfx_volume: float = 1.0

@export_group("Gameplay")
@export var difficulty_level: int = 1
@export var game_speed: float = 1.0
@export var max_lives: int = 3

@export_group("Debug")
@export var debug_mode: bool = false
@export var show_fps: bool = false

# 설정을 저장하거나 불러오는 함수 예시
func save_config(path: String = "user://game_config.tres"):
	ResourceSaver.save(self, path)

static func load_config(path: String = "user://game_config.tres") -> GameConfig:
	if ResourceLoader.exists(path):
		return ResourceLoader.load(path) as GameConfig
	return GameConfig.new()
