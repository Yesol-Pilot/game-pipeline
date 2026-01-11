extends Camera2D
class_name ShakeCamera

## 쉐이크 카메라
## 플레이어 피격 시 화면 흔들림 효과 제공

@export var decay: float = 0.8  # 흔들림 감소 속도
@export var max_offset: Vector2 = Vector2(100, 75)  # 최대 흔들림 범위
@export var max_roll: float = 0.1  # 최대 회전 각도 (라디안)
@export var noise: FastNoiseLite  # 노이즈 (자연스러운 흔들림)

var trauma: float = 0.0  # 현재 흔들림 강도 (0.0 ~ 1.0)
var trauma_power: int = 2  # 흔들림 지수 (값이 클수록 강한 흔들림만 남음)
var noise_y: int = 0

func _ready() -> void:
    if not noise:
        noise = FastNoiseLite.new()
        noise.seed = randi()
        noise.frequency = 0.1 # 적절한 진동수 설정
        
    randomize()
    
    # 이벤트 연결
    CombatEvents.player_damaged.connect(_on_player_damaged)
    CombatEvents.player_died.connect(_on_player_died)

func _process(delta: float) -> void:
    if trauma > 0:
        trauma = max(trauma - decay * delta, 0)
        _shake()
    else:
        # 흔들림 종료 시 원위치
        offset = Vector2.ZERO
        rotation = 0.0

func add_trauma(amount: float) -> void:
    trauma = min(trauma + amount, 1.0)

func _shake() -> void:
    var amount = pow(trauma, trauma_power)
    noise_y += 1
    
    # 노이즈 기반 흔들림 계산
    var rot_val = max_roll * amount * noise.get_noise_2d(noise.seed, noise_y)
    var offset_val = Vector2(
        max_offset.x * amount * noise.get_noise_2d(noise.seed * 2, noise_y),
        max_offset.y * amount * noise.get_noise_2d(noise.seed * 3, noise_y)
    )
    
    rotation = rot_val
    offset = offset_val

func _on_player_damaged(amount: int) -> void:
    add_trauma(0.4) # 피격 시 적당한 흔들림

func _on_player_died() -> void:
    add_trauma(1.0) # 사망 시 강한 흔들림
