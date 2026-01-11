extends CharacterBody2D
## 플레이어 스크립트 - 이동 및 점프 처리

# 템플릿 파라미터 (template_config.json에서 주입)
@export var gravity: float = 980.0
@export var jump_height: float = 400.0
@export var max_jumps: int = 2

var jump_count: int = 0
var is_dead: bool = false

signal player_died
signal coin_collected(amount: int)

func _ready() -> void:
	jump_count = 0
	is_dead = false

func _physics_process(delta: float) -> void:
	if is_dead:
		return
	
	# 중력 적용
	velocity.y += gravity * delta
	
	# 점프 입력 처리
	if _is_jump_pressed() and jump_count < max_jumps:
		_jump()
	
	move_and_slide()
	
	# 바닥 착지 시 점프 카운트 초기화
	if is_on_floor():
		jump_count = 0

func _is_jump_pressed() -> bool:
	return Input.is_action_just_pressed("jump")

func _jump() -> void:
	velocity.y = -jump_height
	jump_count += 1
	# 점프 사운드 재생
	# $JumpSound.play()

func die() -> void:
	if is_dead:
		return
	is_dead = true
	player_died.emit()

func collect_coin() -> void:
	coin_collected.emit(1)
