extends CharacterBody2D
class_name RunnerPlayer

## 플레이어 스크립트 - 리소스 기반 및 이벤트 주도 구조

# 리소스 주입 (Stats)
@export var stats: CharacterStats
# 기본값 설정 (에디터에서 할당되지 않았을 경우를 대비)
@export var default_stats: CharacterStats

# 상태 변수
var jump_count: int = 0
var is_dead: bool = false
var current_health: int

func _ready() -> void:
	# 스탯 초기화
	if not stats and default_stats:
		stats = default_stats.duplicate()
	
	if stats:
		current_health = stats.health
		
	jump_count = 0
	is_dead = false

func _physics_process(delta: float) -> void:
	if is_dead:
		return
	
	# 중력 적용
	velocity.y += 980.0 * delta # 기본 중력, 필요 시 GameConfig에서 가져올 수 있음
	
	# 점프 입력 처리
	if Input.is_action_just_pressed("jump"):
		try_jump()
	
	move_and_slide()
	
	# 바닥 착지 시 점프 카운트 초기화
	if is_on_floor():
		jump_count = 0

func try_jump() -> void:
	# Stats 리소스의 movement_speed 등을 활용할 수 있음 (현재는 점프 로직에 집중)
	# max_jumps가 stats에 없다면 기본값 2 사용
	var max_jumps = 2 
	# 만약 stats에 정의되어 있다면: var max_jumps = stats.abilities.get("max_jumps", 2)
	
	if jump_count < max_jumps:
		_perform_jump()

func _perform_jump() -> void:
	# 점프력 계산 (Stats 기반)
	var jump_power = 400.0  # 기본값
	# if stats: jump_power = stats.movement_speed * 2.0 # 예시 로직
	
	velocity.y = -jump_power
	jump_count += 1
	
	# 사운드 등 효과는 여기서 직접 재생하지 않고 시그널로 처리 가능 (선택적)

func take_damage(amount: int) -> void:
	if is_dead: return
	
	if stats:
		var damage_taken = stats.take_damage(amount)
		current_health = stats.health
		CombatEvents.player_damaged.emit(damage_taken)
		UIEvents.update_health(current_health, 100) # Max HP 하드코딩 대신 stats.max_health 등 필요
		
		if stats.health <= 0:
			die()
	else:
		# 리소스가 없는 경우의 폴백
		die()

func die() -> void:
	if is_dead: return
	is_dead = true
	CombatEvents.player_died.emit()
	# 사망 애니메이션 재생 등

func collect_coin() -> void:
	# 점수 추가는 GameManager가 CombatEvents나 다른 신호를 듣고 처리
	# 여기서는 '코인 획득' 이벤트만 발생시킴
	# UIEvents.score_updated.emit(...) 직접 호출보다는 GameManager가 관리하는 것이 좋음
	pass

