extends Node

# Simple Turn-Based Battle Manager

enum TurnState { PLAYER_TURN, ENEMY_TURN, WON, LOST }
var current_state = TurnState.PLAYER_TURN

@export var player_unit: BattleUnit
@export var enemy_unit: BattleUnit

func _ready() -> void:
    # 초기화 및 시그널 연결
    player_unit.attack_finished.connect(_on_player_attack_finished)
    enemy_unit.attack_finished.connect(_on_enemy_attack_finished)
    
    player_unit.died.connect(_on_player_died)
    enemy_unit.died.connect(_on_enemy_died)
    
    start_turn()

func start_turn() -> void:
    match current_state:
        TurnState.PLAYER_TURN:
            print(">>> Player's Turn! Click to Attack.")
            # UI 활성화 로직 (버튼 등)
            
        TurnState.ENEMY_TURN:
            print(">>> Enemy's Turn!")
            # AI 딜레이 후 공격
            await get_tree().create_timer(1.0).timeout
            enemy_unit.attack(player_unit)

# --- Event Handlers ---

func on_attack_button_pressed() -> void:
    if current_state == TurnState.PLAYER_TURN:
        player_unit.attack(enemy_unit) 
        # 버튼 비활성화

func _on_player_attack_finished() -> void:
    if current_state != TurnState.WON:
        current_state = TurnState.ENEMY_TURN
        start_turn()

func _on_enemy_attack_finished() -> void:
    if current_state != TurnState.LOST:
        current_state = TurnState.PLAYER_TURN
        start_turn()

func _on_enemy_died() -> void:
    current_state = TurnState.WON
    print("VICTORY!")

func _on_player_died() -> void:
    current_state = TurnState.LOST
    print("GAME OVER...")
