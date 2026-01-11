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
	
	# AI 동적 밸런싱: GDD 값으로 덮어쓰기
	if GDDParser:
		GDDParser.apply_gdd_variables(game_config, "game_config")
		
	# 이벤트 연결
	_connect_signals()
	_reset()

func _connect_signals() -> void:
	CombatEvents.player_died.connect(_on_player_died)

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

	# 장애물 스폰은 ObstacleSpawner가 처리

func _reset() -> void:
	score = 0
	distance = 0.0
	current_difficulty = game_config.difficulty_level if game_config else 1.0
	is_game_over = false
	UIEvents.update_score(0)

func _update_difficulty() -> void:
	var diff_inc = 0.1
	var new_difficulty = 1.0 + (distance / 1000.0) * diff_inc
	var max_diff = 5.0
	current_difficulty = min(new_difficulty, max_diff)

func _on_player_died() -> void:
	is_game_over = true
	CombatEvents.game_over.emit(score)
	print("Game Over! Final Score: ", score)
	
	# 데이터 저장 처리
	var output_data = SaveSystem.get_data()
	if output_data:
		var is_new_record = output_data.update_high_score(score)
		if is_new_record:
			print("🏆 NEW HIGH SCORE: ", score)
			# UIEvents.new_high_score.emit(score) 같은 이벤트 추가 가능
		
		# 코인 획득 (거리 * 0.1) 예시
		var earned_coins = int(score * 0.1)
		output_data.add_coins(earned_coins)
		
		# 저장
		SaveSystem.save_game()
	
	# 2초 후 재시작 (SceneTransition 활용)
	await get_tree().create_timer(2.0).timeout
	
	# 현재 씬을 다시 로드 (부드러운 페이드 효과)
	# SceneTransition Autoload가 있다고 가정
	var current_scene = get_tree().current_scene.scene_file_path
	SceneTransition.change_scene(current_scene, "fade", 0.8)

func get_current_difficulty() -> float:
	return current_difficulty
