extends Node
## 게임 매니저 (Game Manager) - 게임 상태 관리 싱글톤

enum GameState {
	NONE,
	LOADING,
	MENU,
	PLAYING,
	PAUSED,
	GAME_OVER,
	LEVEL_COMPLETE
}

var current_state: GameState = GameState.NONE
var previous_state: GameState = GameState.NONE
var game_config: Resource = null

# 타임 스케일 (일시정지용)
var time_scale: float = 1.0

signal state_changed(old_state: GameState, new_state: GameState)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # 일시정지 시에도 동작
	_load_game_config()
	print("[게임매니저] 초기화 완료")


func _load_game_config() -> void:
	"""게임 설정 로드"""
	var config_path = "res://configs/game_config.tres"
	if ResourceLoader.exists(config_path):
		game_config = load(config_path)


func change_state(new_state: GameState) -> void:
	"""게임 상태 변경"""
	if current_state == new_state:
		return
	
	previous_state = current_state
	current_state = new_state
	
	# 상태별 처리
	match new_state:
		GameState.PLAYING:
			_on_game_started()
		GameState.PAUSED:
			_on_game_paused()
		GameState.GAME_OVER:
			_on_game_over()
		GameState.LEVEL_COMPLETE:
			_on_level_complete()
	
	state_changed.emit(previous_state, new_state)
	EventBus.game_state_changed.emit(new_state)


func _on_game_started() -> void:
	"""게임 시작 처리"""
	get_tree().paused = false
	time_scale = 1.0
	Engine.time_scale = time_scale
	EventBus.game_started.emit()


func _on_game_paused() -> void:
	"""일시정지 처리"""
	get_tree().paused = true
	EventBus.game_paused.emit()


func _on_game_over() -> void:
	"""게임 오버 처리"""
	get_tree().paused = true
	EventBus.game_over.emit("기본 게임 오버")


func _on_level_complete() -> void:
	"""레벨 완료 처리"""
	get_tree().paused = true


# ===== 공용 API =====

func start_game() -> void:
	"""게임 시작"""
	change_state(GameState.PLAYING)


func pause_game() -> void:
	"""게임 일시정지"""
	if current_state == GameState.PLAYING:
		change_state(GameState.PAUSED)


func resume_game() -> void:
	"""게임 재개"""
	if current_state == GameState.PAUSED:
		change_state(GameState.PLAYING)


func toggle_pause() -> void:
	"""일시정지 토글"""
	if current_state == GameState.PLAYING:
		pause_game()
	elif current_state == GameState.PAUSED:
		resume_game()


func game_over(reason: String = "") -> void:
	"""게임 오버"""
	change_state(GameState.GAME_OVER)
	EventBus.player_died.emit(reason)


func restart_game() -> void:
	"""게임 재시작"""
	get_tree().paused = false
	get_tree().reload_current_scene()


func go_to_menu() -> void:
	"""메인 메뉴로 이동"""
	get_tree().paused = false
	change_state(GameState.MENU)
	# get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func is_playing() -> bool:
	"""게임 플레이 중인지 확인"""
	return current_state == GameState.PLAYING


func is_paused() -> bool:
	"""일시정지 중인지 확인"""
	return current_state == GameState.PAUSED
