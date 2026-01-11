extends Node

# 전투 관련 신호 정의
signal player_attacked(target, damage: int)
signal player_damaged(amount: int)
signal player_died
signal enemy_spawned(enemy_type: String, position: Vector2)
signal enemy_defeated(enemy_type: String, score_value: int)
signal level_started(level_number: int)
signal level_completed(level_number: int)
signal game_over(final_score: int)

# 필요 시 중계 함수 추가 가능
func emit_player_attacked(target, damage: int):
	player_attacked.emit(target, damage)
