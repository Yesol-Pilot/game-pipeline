extends Node
## 게임 매니저 - 점수, 난이도, 스폰 관리

# 템플릿 파라미터
@export var spawn_rate: float = 2.0
@export var initial_difficulty: float = 1.0
@export var difficulty_curve: float = 0.1
@export var max_difficulty: float = 5.0

var score: int = 0
var distance: float = 0.0
var current_difficulty: float = 1.0
var spawn_timer: float = 0.0

signal score_updated(new_score: int)
signal difficulty_updated(new_difficulty: float)

func _ready() -> void:
	_reset()

func _process(delta: float) -> void:
	# 거리 증가
	distance += delta * 100.0 * current_difficulty
	
	# 난이도 업데이트
	_update_difficulty()
	
	# 스폰 타이머
	spawn_timer += delta
	if spawn_timer >= spawn_rate / current_difficulty:
		spawn_timer = 0.0
		_spawn_obstacle()

func _reset() -> void:
	score = 0
	distance = 0.0
	current_difficulty = initial_difficulty
	spawn_timer = 0.0

func add_score(amount: int) -> void:
	score += amount
	score_updated.emit(score)

func _update_difficulty() -> void:
	var new_difficulty = initial_difficulty + (distance / 1000.0) * difficulty_curve
	current_difficulty = min(new_difficulty, max_difficulty)
	difficulty_updated.emit(current_difficulty)

func _spawn_obstacle() -> void:
	# 장애물 스폰 로직
	pass

func get_score() -> int:
	return score

func get_distance() -> float:
	return distance
