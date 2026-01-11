extends Node2D
## 클리커 게임 메인 스크립트

# 게임 데이터
var coins: float = 0.0
var click_value: float = 1.0
var auto_click_rate: float = 0.0  # 초당 자동 클릭

# 업그레이드 데이터
var upgrades: Array = []

@onready var coin_label: Label = $UILayer/MainUI/CurrencyDisplay/CoinLabel
@onready var click_value_label: Label = $UILayer/MainUI/ClickValueLabel
@onready var upgrade_list: VBoxContainer = $UILayer/MainUI/UpgradePanel/UpgradeList

signal coins_changed(new_amount: float)
signal upgrade_purchased(upgrade_id: String)


func _ready() -> void:
	_load_upgrades()
	_update_ui()
	
	# 자동 클릭 타이머
	var timer = Timer.new()
	timer.wait_time = 0.1
	timer.autostart = true
	timer.timeout.connect(_on_auto_click_tick)
	add_child(timer)


func _on_click_button_pressed() -> void:
	"""클릭 버튼 누름"""
	add_coins(click_value)
	_spawn_click_effect()
	EventBus.sfx_requested.emit("click")


func add_coins(amount: float) -> void:
	"""코인 추가"""
	coins += amount
	coins_changed.emit(coins)
	EventBus.resource_collected.emit("coin", int(amount))
	_update_ui()


func _on_auto_click_tick() -> void:
	"""자동 클릭 처리"""
	if auto_click_rate > 0:
		add_coins(auto_click_rate * 0.1)


func purchase_upgrade(upgrade_data: Dictionary) -> bool:
	"""업그레이드 구매"""
	var cost = upgrade_data.get("cost", 0)
	if coins < cost:
		return false
	
	coins -= cost
	
	# 업그레이드 효과 적용
	var effect_type = upgrade_data.get("effect_type", "")
	var effect_value = upgrade_data.get("effect_value", 0)
	
	match effect_type:
		"click_value":
			click_value += effect_value
		"auto_click":
			auto_click_rate += effect_value
		"multiplier":
			click_value *= effect_value
	
	upgrade_purchased.emit(upgrade_data.get("id", ""))
	EventBus.upgrade_purchased.emit(upgrade_data.get("id", ""))
	_update_ui()
	return true


func _update_ui() -> void:
	"""UI 갱신"""
	coin_label.text = _format_number(coins)
	click_value_label.text = "+%s / 클릭" % _format_number(click_value)


func _format_number(value: float) -> String:
	"""큰 숫자 포맷팅 (1K, 1M, 1B 등)"""
	if value < 1000:
		return str(int(value))
	elif value < 1000000:
		return "%.1fK" % (value / 1000)
	elif value < 1000000000:
		return "%.1fM" % (value / 1000000)
	else:
		return "%.1fB" % (value / 1000000000)


func _spawn_click_effect() -> void:
	"""클릭 이펙트 생성"""
	# 클릭 시 +값 표시 효과
	pass


func _load_upgrades() -> void:
	"""업그레이드 데이터 로드"""
	upgrades = [
		{"id": "click1", "name": "클릭 강화 I", "cost": 10, "effect_type": "click_value", "effect_value": 1},
		{"id": "auto1", "name": "자동 클리커 I", "cost": 50, "effect_type": "auto_click", "effect_value": 1},
		{"id": "click2", "name": "클릭 강화 II", "cost": 100, "effect_type": "click_value", "effect_value": 5},
		{"id": "mult1", "name": "2배 증폭", "cost": 500, "effect_type": "multiplier", "effect_value": 2},
	]


# 오프라인 보상 계산
func calculate_offline_reward(seconds_offline: float) -> float:
	"""오프라인 보상 계산"""
	return auto_click_rate * seconds_offline * 0.5  # 50% 효율
