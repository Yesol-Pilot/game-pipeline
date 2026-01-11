extends CharacterBody3D

# 3D Runner Player Controller
# 3-Lane System (-1: Left, 0: Center, 1: Right)

@export var speed: float = 10.0
@export var jump_force: float = 8.0
@export var lane_distance: float = 2.0 # 레인 간 간격 (미터)
@export var lane_change_speed: float = 10.0

var current_lane: int = 0 # -1, 0, 1
var target_x: float = 0.0
var gravity: float = 20.0

func _physics_process(delta: float) -> void:
    # 1. 전진 이동
    velocity.z = -speed
    
    # 2. 중력 적용
    if not is_on_floor():
        velocity.y -= gravity * delta
    
    # 3. 점프
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = jump_force
        
    # 4. 레인 변경 입력
    if Input.is_action_just_pressed("ui_left"):
        change_lane(-1)
    elif Input.is_action_just_pressed("ui_right"):
        change_lane(1)
        
    # 5. 가로 이동 (부드러운 보간)
    var target_pos = Vector3(target_x, position.y, position.z)
    # X축만 보간하고 Y, Z는 물리 엔진에 맡김? 
    # CharacterBody3D에서는 velocity로 제어하는 것이 정석이지만, 
    # 레인 게임 특성상 X 좌표를 직접 제어하거나 velocity.x를 계산해야 함.
    
    var x_diff = target_x - position.x
    velocity.x = x_diff * lane_change_speed
    
    move_and_slide()

func change_lane(direction: int) -> void:
    var new_lane = current_lane + direction
    if new_lane >= -1 and new_lane <= 1:
        current_lane = new_lane
        target_x = current_lane * lane_distance
