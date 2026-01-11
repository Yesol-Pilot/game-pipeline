extends Node
class_name RunnerGameManager

## 게임 매니저 - 리소스 및 이벤트 기반 구조

# 리소스 주입
@export var game_config: GameConfig
# 기본 설정 리소스 (Fallback)
@export var default_config: GameConfig

# 상태 변수
var score: int = 0
var distance: float = 0.0
var current_difficulty: float = 1.0
var is_game_over: bool = false

# 타이머
var spawn_timer: float = 0.0

func _ready() -> void:
	# Config 초기화
	if not game_config and default_config:
		game_config = default_config.duplicate()
	elif not game_config:
		game_config = GameConfig.new()
		
	# 이벤트 연결
	_connect_signals()
	_reset()

func _connect_signals() -> void:
	CombatEvents.player_died.connect(_on_player_died)
	# 적 처치 시 점수 획득 등의 이벤트도 여기서 연결 가능

func _process(delta: float) -> void:
	if is_game_over:
		return
		
	# 게임 속도 (Config 기반)
	var speed_multiplier = game_config.game_speed if game_config else 1.0
	
	# 거리 증가
	distance += delta * 100.0 * current_difficulty * speed_multiplier
	
	# 난이도 업데이트
	_update_difficulty()
	
	# 점수 자동 증가 (러너 게임 특성)
	score = int(distance)
	UIEvents.update_score(score) # UI에 점수 업데이트 전송
	
	# 장애물 스폰 타이머 -> Spawner가 처리하도록 위임하거나 여기서 신호 발송
	# 이번 구현에서는 Spawner를 별도 노드로 분리할 예정이므로 여기서는 난이도만 관리

func _reset() -> void:
	score = 0
	distance = 0.0
	current_difficulty = game_config.difficulty_level if game_config else 1.0
	is_game_over = false
	UIEvents.update_score(0)

func _update_difficulty() -> void:
	var diff_inc = 0.1 # 기본 증가량
	# Config나 난이도 커브에 따라 조정 가능
	var new_difficulty = 1.0 + (distance / 1000.0) * diff_inc
	var max_diff = 5.0 # 하드코딩 혹은 Config
	current_difficulty = min(new_difficulty, max_diff)
	
	# 난이도 변경 알림 (필요 시)
	# SystemEvents.difficulty_changed.emit(current_difficulty)

func _on_player_died() -> void:
	is_game_over = true
	CombatEvents.game_over.emit(score)
	print("Game Over! Final Score: ", score)
	
	# 2초 후 재시작 또는 UI 표시 (Timer 사용)
	await get_tree().create_timer(2.0).timeout
	# get_tree().reload_current_scene() # 간단한 재시작
	# 또는 팝업 표시 요청: UIEvents.popup_opened.emit("GameOverPopup")

# 헬퍼 함수
func get_current_difficulty() -> float:
	return current_difficulty

