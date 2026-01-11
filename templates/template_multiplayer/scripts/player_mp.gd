extends CharacterBody3D

# Multiplayer Player Controller

@export var speed: float = 5.0
@export var jump_force: float = 4.5
var gravity: float = 9.8

func _enter_tree():
    # 이름(문자열 ID)을 기반으로 권한 설정
    # 예: "1"이면 Host가 권한을 가짐
    set_multiplayer_authority(name.to_int())

func _physics_process(delta: float):
    # 권한이 있는 클라이언트(나 자신)만 입력을 처리
    if not is_multiplayer_authority():
        return

    # 중력
    if not is_on_floor():
        velocity.y -= gravity * delta

    # 점프
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = jump_force

    # 이동
    var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    
    if direction:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)

    move_and_slide()
    
    # 위치 정보는 MultiplayerSynchronizer 노드가 자동으로 전파함 (Editor 설정 필요)
    # 여기서는 코드로만 표현
