extends Node
## 방치형 RPG 게임 매니저

# 플레이어 스탯
var player_level: int = 1
var player_exp: int = 0
var player_hp: float = 100.0
var player_max_hp: float = 100.0
var player_attack: float = 10.0
var player_attack_speed: float = 1.0

# 자원
var gold: int = 0
var gems: int = 0

# 스테이지
var current_stage: int = 1
var current_wave: int = 1
var max_waves: int = 10

# 몬스터
var current_monster: Dictionary = {}
var monster_hp: float = 0.0

# 오프라인 시간
var last_played_time: int = 0

# 타이머
var attack_timer: float = 0.0

signal gold_changed(amount: int)
signal exp_changed(current: int, needed: int)
signal level_up(new_level: int)
signal stage_changed(stage: int, wave: int)
signal monster_damaged(damage: float, remaining_hp: float)
signal monster_killed()
signal player_damaged(damage: float, remaining_hp: float)


func _ready() -> void:
	_load_game()
	_calculate_offline_reward()
	_spawn_monster()


func _process(delta: float) -> void:
	if monster_hp <= 0:
		return
	
	# 자동 공격
	attack_timer += delta
	if attack_timer >= 1.0 / player_attack_speed:
		attack_timer = 0.0
		_attack_monster()


func _attack_monster() -> void:
	"""몬스터 공격"""
	var damage = player_attack * (1 + randf() * 0.2)  # 0~20% 랜덤 변동
	monster_hp -= damage
	monster_damaged.emit(damage, max(0, monster_hp))
	
	if monster_hp <= 0:
		_on_monster_killed()


func _on_monster_killed() -> void:
	"""몬스터 처치"""
	var reward_gold = current_stage * 10 + current_wave * 2
	var reward_exp = current_stage * 5 + current_wave
	
	gold += reward_gold
	player_exp += reward_exp
	
	gold_changed.emit(gold)
	_check_level_up()
	monster_killed.emit()
	
	# 다음 웨이브
	current_wave += 1
	if current_wave > max_waves:
		current_wave = 1
		current_stage += 1
	
	stage_changed.emit(current_stage, current_wave)
	_spawn_monster()


func _spawn_monster() -> void:
	"""몬스터 스폰"""
	var base_hp = 50 + current_stage * 30 + current_wave * 10
	var base_attack = 5 + current_stage * 2
	
	current_monster = {
		"name": "몬스터 Lv.%d" % (current_stage * 10 + current_wave),
		"hp": base_hp,
		"attack": base_attack
	}
	
	monster_hp = base_hp


func _check_level_up() -> void:
	"""레벨업 체크"""
	var exp_needed = _get_exp_for_level(player_level + 1)
	
	while player_exp >= exp_needed:
		player_exp -= exp_needed
		player_level += 1
		
		# 스탯 증가
		player_max_hp += 20
		player_hp = player_max_hp
		player_attack += 5
		
		level_up.emit(player_level)
		exp_needed = _get_exp_for_level(player_level + 1)
	
	exp_changed.emit(player_exp, exp_needed)


func _get_exp_for_level(level: int) -> int:
	"""레벨업 필요 경험치"""
	return int(100 * pow(1.5, level - 1))


# ===== 업그레이드 =====

func upgrade_attack(cost: int) -> bool:
	"""공격력 업그레이드"""
	if gold < cost:
		return false
	
	gold -= cost
	player_attack += 2
	gold_changed.emit(gold)
	return true


func upgrade_hp(cost: int) -> bool:
	"""체력 업그레이드"""
	if gold < cost:
		return false
	
	gold -= cost
	player_max_hp += 20
	player_hp = min(player_hp + 20, player_max_hp)
	gold_changed.emit(gold)
	return true


func upgrade_speed(cost: int) -> bool:
	"""공격 속도 업그레이드"""
	if gold < cost:
		return false
	
	gold -= cost
	player_attack_speed += 0.1
	gold_changed.emit(gold)
	return true


# ===== 저장/로드 =====

func _save_game() -> void:
	"""게임 저장"""
	var save_data = {
		"player_level": player_level,
		"player_exp": player_exp,
		"player_attack": player_attack,
		"player_max_hp": player_max_hp,
		"player_attack_speed": player_attack_speed,
		"gold": gold,
		"gems": gems,
		"current_stage": current_stage,
		"current_wave": current_wave,
		"last_played_time": Time.get_unix_time_from_system()
	}
	
	var file = FileAccess.open("user://save.json", FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(save_data))


func _load_game() -> void:
	"""게임 로드"""
	if not FileAccess.file_exists("user://save.json"):
		return
	
	var file = FileAccess.open("user://save.json", FileAccess.READ)
	if file:
		var json = JSON.new()
		var parse_result = json.parse(file.get_as_text())
		if parse_result == OK:
			var data = json.get_data()
			player_level = data.get("player_level", 1)
			player_exp = data.get("player_exp", 0)
			player_attack = data.get("player_attack", 10.0)
			player_max_hp = data.get("player_max_hp", 100.0)
			player_hp = player_max_hp
			player_attack_speed = data.get("player_attack_speed", 1.0)
			gold = data.get("gold", 0)
			gems = data.get("gems", 0)
			current_stage = data.get("current_stage", 1)
			current_wave = data.get("current_wave", 1)
			last_played_time = data.get("last_played_time", 0)


func _calculate_offline_reward() -> void:
	"""오프라인 보상 계산"""
	if last_played_time == 0:
		return
	
	var current_time = Time.get_unix_time_from_system()
	var offline_seconds = current_time - last_played_time
	
	# 최대 8시간까지만 계산
	offline_seconds = min(offline_seconds, 8 * 60 * 60)
	
	if offline_seconds < 60:
		return
	
	# 분당 예상 처치 수 기반 보상 (50% 효율)
	var kills_per_minute = player_attack_speed * 60 / max(1, current_stage)
	var total_kills = kills_per_minute * (offline_seconds / 60.0) * 0.5
	
	var offline_gold = int(total_kills * (current_stage * 10))
	var offline_exp = int(total_kills * (current_stage * 5))
	
	gold += offline_gold
	player_exp += offline_exp
	
	_check_level_up()
	
	print("오프라인 보상: 골드 +%d, 경험치 +%d" % [offline_gold, offline_exp])


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		_save_game()
	elif what == NOTIFICATION_APPLICATION_PAUSED:
		_save_game()
