extends Node2D
## 메인 스크립트 - 게임 상태 관리

enum GameState { MENU, PLAYING, PAUSED, GAME_OVER }

var current_state: GameState = GameState.MENU

@onready var game_scene = preload("res://scenes/game.tscn")

func _ready() -> void:
	# 초기화
	_show_menu()

func _show_menu() -> void:
	current_state = GameState.MENU
	# 메뉴 UI 표시 로직

func start_game() -> void:
	current_state = GameState.PLAYING
	# 게임 시작 로직

func pause_game() -> void:
	current_state = GameState.PAUSED
	get_tree().paused = true

func resume_game() -> void:
	current_state = GameState.PLAYING
	get_tree().paused = false

func game_over() -> void:
	current_state = GameState.GAME_OVER
	# 게임 오버 처리 로직

func restart_game() -> void:
	get_tree().reload_current_scene()
