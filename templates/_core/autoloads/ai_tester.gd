extends Node

# AI Playtester
# Automatically controls the player to verify levels

var enabled: bool = false
var player: Node = null

# Config
var detection_distance: float = 300.0 # Pixel or Meters (needs adjustment based on game)

func _ready() -> void:
    # F1 Key to toggle AI
    set_process_input(true)

func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and event.keycode == KEY_F1:
        enabled = not enabled
        print("[AI Tester] Toggled: ", enabled)

func _physics_process(delta: float) -> void:
    if not enabled:
        return
        
    if not is_instance_valid(player):
        player = get_tree().get_first_node_in_group("player")
        return

    _scan_environment_2d()
    # _scan_environment_3d() # Future support

func _scan_environment_2d() -> void:
    if not player is Node2D: return
    
    var space_state = player.get_world_2d().direct_space_state
    var start = player.global_position
    var end = start + Vector2(detection_distance, 0) # Look Right
    
    var query = PhysicsRayQueryParameters2D.create(start, end)
    # Exclude player itself
    query.exclude = [player.get_rid()] 
    
    var result = space_state.intersect_ray(query)
    
    if result:
        # 장애물 발견!
        # 거리 확인
        var distance = start.distance_to(result.position)
        if distance < 150.0: # 임계값
            _perform_jump()

func _perform_jump() -> void:
    if Input.is_action_pressed("ui_accept"): return # 이미 누르는 중
    
    print("[AI Tester] Jumping!")
    Input.action_press("ui_accept")
    
    # 짧게 눌렀다 떼기 (가변 점프 대응)
    await get_tree().create_timer(0.2).timeout
    Input.action_release("ui_accept")
