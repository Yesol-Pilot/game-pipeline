extends Node

# UI 관련 신호 정의
signal score_updated(new_score: int)
signal health_updated(current_health: int, max_health: int)
signal message_shown(text: String, duration: float)
signal popup_opened(popup_name: String)
signal popup_closed(popup_name: String)
signal screen_transition_requested(screen_name: String)

# 공통 UI 업데이트 함수
func update_score(score: int):
	score_updated.emit(score)

func update_health(current: int, max_hp: int):
	health_updated.emit(current, max_hp)
