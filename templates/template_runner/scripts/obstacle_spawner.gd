extends Node
class_name ObstacleSpawner

## 장애물 생성기

@export var obstacle_scene: PackedScene
@export var spawn_parent: Node
@export var game_manager: RunnerGameManager

# 스폰 설정
@export var base_spawn_interval: float = 2.0
@export var min_spawn_interval: float = 0.8

var current_timer: float = 0.0

func _process(delta: float) -> void:
    # 게임 오버 체크 (GameManager 상태 확인)
    if game_manager and game_manager.is_game_over:
        return
        
    current_timer += delta
    
    # 난이도에 따른 인터벌 조정
    var difficulty = 1.0
    if game_manager:
        difficulty = game_manager.get_current_difficulty()
    
    var current_interval = max(min_spawn_interval, base_spawn_interval / difficulty)
    
    if current_timer >= current_interval:
        current_timer = 0.0
        spawn_obstacle()

func spawn_obstacle() -> void:
    if not obstacle_scene:
        return
        
    var obstacle = obstacle_scene.instantiate()
    
    # 위치 설정 (화면 오른쪽 끝 가정)
    # 실제 위치는 씬 구조에 따라 다름. 여기서는 예시 값.
    var spawn_pos = Vector2(1200, 500) 
    
    if obstacle is Node2D:
        obstacle.position = spawn_pos
        
    # 장애물 이동 속도 설정 (난이도 반영)
    if obstacle.has_method("set_speed"):
        var speed = 400.0 * (game_manager.get_current_difficulty() if game_manager else 1.0)
        obstacle.set_speed(speed)
        
    spawn_parent.add_child(obstacle)
