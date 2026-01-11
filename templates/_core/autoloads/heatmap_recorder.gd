extends Node

# Heatmap Recorder (Data Collector)
# Records player death positions to analyze difficulty balance

var death_points: Array = []
var session_id: String = ""

func _ready() -> void:
    session_id = str(Time.get_unix_time_from_system())
    
    # CombatEvents가 있다면 연결
    if has_node("/root/CombatEvents"):
        var combat = get_node("/root/CombatEvents")
        combat.player_died.connect(_on_player_died)

func _on_player_died() -> void:
    var player = get_tree().get_first_node_in_group("player")
    if player:
        var pos = player.global_position
        var data_point = {
            "x": pos.x,
            "y": pos.y,
            "z": 0.0 # 2D Default
        }
        
        # 3D Support
        if pos is Vector3:
             data_point["z"] = pos.z
             
        death_points.append(data_point)
        print("[Heatmap] Death recorded at: ", data_point)
        _save_report()

func _save_report() -> void:
    # 로컬 저장 (추후 서버 전송 가능)
    var file = FileAccess.open("user://heatmap_" + session_id + ".json", FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(death_points, "\t"))
        
    # In a real scenario, you would POST this to /api/analytics
