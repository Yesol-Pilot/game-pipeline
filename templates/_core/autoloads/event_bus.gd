extends Node
## 이벤트 버스 (Event Bus) - 전역 시그널 허브
## 코어 로직과 프레젠테이션 계층 간 통신을 담당하는 싱글톤

# ===== 게임 상태 =====
signal game_state_changed(new_state: int)
signal game_started()
signal game_paused()
signal game_resumed()
signal game_over(reason: String)

# ===== 점수 시스템 =====
signal score_updated(current_score: int, added_points: int)
signal high_score_updated(new_high_score: int)

# ===== 플레이어 =====
signal player_jumped()
signal player_died(reason: String)
signal player_respawned()
signal player_action(action_name: String, data: Dictionary)

# ===== 리소스/재화 =====
signal resource_collected(type: String, amount: int)
signal currency_updated(currency_type: String, new_amount: int)
signal upgrade_purchased(upgrade_id: String)

# ===== 레벨 =====
signal level_loaded(level_data: Resource)
signal level_completed(level_id: int, stars: int)
signal chunk_spawned(chunk_id: String)

# ===== 스킨/테마 =====
signal skin_changed(new_skin: Resource)
signal skin_load_requested(skin_path: String)

# ===== UI =====
signal ui_button_pressed(button_id: String)
signal popup_requested(popup_type: String, data: Dictionary)
signal tutorial_step_completed(step_id: int)

# ===== 오디오 =====
signal sfx_requested(sfx_id: String)
signal music_change_requested(music_id: String)

# ===== 광고/수익화 =====
signal ad_requested(ad_type: String)
signal ad_completed(ad_type: String, success: bool)
signal reward_granted(reward_type: String, amount: int)


func _ready() -> void:
	print("[이벤트버스] 초기화 완료")
