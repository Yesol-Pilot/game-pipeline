extends Node3D

# 3D Level Generator (Infinite Runner)

@export var chunk_length: float = 20.0
@export var chunk_count: int = 5
@export var player_path: NodePath
@onready var player = get_node(player_path)

var current_z: float = 0.0
var chunks: Array = []

func _ready() -> void:
    # 초기 청크 생성
    for i in range(chunk_count):
        spawn_chunk()

func _process(delta: float) -> void:
    if player:
        # 플레이어가 일정 거리 이상 전진하면 새 청크 생성 및 옛날 청크 삭제
        if player.position.z < current_z + (chunk_length * (chunk_count - 2)): 
            # player.z는 음수로 증가함 (Godot Forward는 -Z)
            # 따라서 player.position.z 가 더 작아지면(멀어지면) 스폰해야 함
            pass
            
        # 간단한 로직: 플레이어 위치 기준이 아니라, 
        # 가장 뒤의 청크가 플레이어보다 훨씬 뒤로 가면 pos reset?
        # 무한 러너는 보통 플레이어 Z를 계속 가게 하거나, 
        # 세상을 뒤로 밀거나 함. 여기선 플레이어가 -Z로 계속 간다고 가정.
        
        var threshold = current_z  + (chunk_length * 2) # 대략적 계산
        if player.position.z < threshold: # 음수 좌표계 주의
             spawn_chunk()

func spawn_chunk() -> void:
    # 바닥 생성 (MeshInstance3D)
    var floor_mesh = MeshInstance3D.new()
    var box = BoxMesh.new()
    box.size = Vector3(10, 0.5, chunk_length)
    floor_mesh.mesh = box
    
    # 위치 설정 (Z축 -방향으로 생성)
    # 첫 청크는 0 ~ -20, 그 다음은 -20 ~ -40 ...
    # current_z는 시작점(0)부터 계속 감소해야 함 (-20, -40...)
    
    floor_mesh.position = Vector3(0, -0.25, current_z - (chunk_length / 2))
    
    # 재질 설정 (체커보드 느낌)
    var mat = StandardMaterial3D.new()
    mat.albedo_color = Color(randf(), randf(), randf())
    floor_mesh.material_override = mat
    
    add_child(floor_mesh)
    chunks.append(floor_mesh)
    
    # 장애물 생성 (간단)
    _spawn_obstacles(current_z)

    # 정리
    if chunks.size() > chunk_count + 2:
        var old_chunk = chunks.pop_front()
        old_chunk.queue_free()

    current_z -= chunk_length # 다음 청크는 더 먼곳(-Z)에

func _spawn_obstacles(start_z: float) -> void:
    var obs_count = randi() % 3
    for i in range(obs_count):
        var lane = (randi() % 3) - 1 # -1, 0, 1
        var z_offset = randf_range(0, chunk_length)
        
        var obs = MeshInstance3D.new()
        var box = BoxMesh.new()
        box.size = Vector3(1, 1, 1)
        obs.mesh = box
        
        var mat = StandardMaterial3D.new()
        mat.albedo_color = Color.RED
        obs.material_override = mat
        
        obs.position = Vector3(lane * 2.0, 0.5, start_z - z_offset)
        add_child(obs)
        chunks.append(obs) # 청크 리스트에 같이 넣어 삭제 관리 (단순화)
