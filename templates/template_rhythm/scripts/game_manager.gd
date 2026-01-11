extends Node2D
## 리듬 게임 플레이 매니저

# 설정
@export var lanes: int = 4
@export var note_speed: float = 800.0
@export var perfect_window: float = 0.05
@export var good_window: float = 0.1
@export var lane_width: float = 200.0

# 노트 데이터
var note_queue: Array = []  # {time, lane, type}
var active_notes: Array = []
var music_position: float = 0.0

# 점수
var score: int = 0
var combo: int = 0
var max_combo: int = 0
var perfect_count: int = 0
var good_count: int = 0
var miss_count: int = 0

# 레퍼런스
@onready var audio_player: AudioStreamPlayer = $AudioPlayer
@onready var hit_line_y: float = 1600.0  # 판정선 Y 위치

signal note_hit(lane: int, judgement: String)
signal combo_changed(new_combo: int)
signal score_changed(new_score: int)


func _ready() -> void:
	_setup_lanes()


func _setup_lanes() -> void:
	"""레인 초기화"""
	var total_width = lanes * lane_width
	var start_x = (1080 - total_width) / 2 + lane_width / 2
	
	for i in range(lanes):
		var lane_x = start_x + i * lane_width
		# 레인 비주얼 생성
		var lane_bg = ColorRect.new()
		lane_bg.size = Vector2(lane_width - 10, 1600)
		lane_bg.position = Vector2(lane_x - lane_width / 2 + 5, 0)
		lane_bg.color = Color(0.2, 0.2, 0.3, 0.5)
		add_child(lane_bg)
	
	# 판정선
	var hit_line = ColorRect.new()
	hit_line.size = Vector2(total_width, 10)
	hit_line.position = Vector2((1080 - total_width) / 2, hit_line_y)
	hit_line.color = Color(1, 1, 1, 0.8)
	add_child(hit_line)


func load_chart(chart_data: Dictionary) -> void:
	"""채보 로드"""
	note_queue.clear()
	
	for note in chart_data.get("notes", []):
		note_queue.append({
			"time": note.get("time", 0.0),
			"lane": note.get("lane", 0),
			"type": note.get("type", "normal")
		})
	
	# 시간순 정렬
	note_queue.sort_custom(func(a, b): return a.time < b.time)


func start_game() -> void:
	"""게임 시작"""
	score = 0
	combo = 0
	music_position = 0.0
	
	audio_player.play()
	set_process(true)


func _process(delta: float) -> void:
	if not audio_player.playing:
		return
	
	music_position = audio_player.get_playback_position()
	
	# 노트 스폰
	_spawn_notes()
	
	# 노트 이동 및 미스 처리
	_update_notes(delta)


func _spawn_notes() -> void:
	"""노트 스폰 (판정선 도달 시간 기준)"""
	var spawn_ahead_time = hit_line_y / note_speed
	
	while note_queue.size() > 0:
		var next_note = note_queue[0]
		if next_note.time - music_position <= spawn_ahead_time:
			_create_note(note_queue.pop_front())
		else:
			break


func _create_note(note_data: Dictionary) -> void:
	"""노트 생성"""
	var note = ColorRect.new()
	note.size = Vector2(lane_width - 20, 50)
	
	var lane_x = _get_lane_x(note_data.lane)
	note.position = Vector2(lane_x - note.size.x / 2, -50)
	note.color = _get_lane_color(note_data.lane)
	
	note.set_meta("lane", note_data.lane)
	note.set_meta("target_time", note_data.time)
	note.set_meta("type", note_data.type)
	
	add_child(note)
	active_notes.append(note)


func _get_lane_x(lane: int) -> float:
	"""레인 중심 X 좌표"""
	var total_width = lanes * lane_width
	var start_x = (1080 - total_width) / 2 + lane_width / 2
	return start_x + lane * lane_width


func _get_lane_color(lane: int) -> Color:
	"""레인별 색상"""
	var colors = [
		Color(1, 0.3, 0.3),  # 빨강
		Color(0.3, 1, 0.3),  # 초록
		Color(0.3, 0.3, 1),  # 파랑
		Color(1, 1, 0.3),    # 노랑
	]
	return colors[lane % colors.size()]


func _update_notes(delta: float) -> void:
	"""노트 업데이트"""
	var to_remove = []
	
	for note in active_notes:
		note.position.y += note_speed * delta
		
		# 미스 판정 (판정선 지나침)
		var target_time = note.get_meta("target_time")
		if music_position - target_time > good_window:
			_on_miss(note)
			to_remove.append(note)
	
	for note in to_remove:
		active_notes.erase(note)
		note.queue_free()


func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch and event.pressed:
		var lane = _get_lane_from_x(event.position.x)
		if lane >= 0 and lane < lanes:
			_check_hit(lane)


func _get_lane_from_x(x: float) -> int:
	"""X 좌표로 레인 인덱스 계산"""
	var total_width = lanes * lane_width
	var start_x = (1080 - total_width) / 2
	
	if x < start_x or x > start_x + total_width:
		return -1
	
	return int((x - start_x) / lane_width)


func _check_hit(lane: int) -> void:
	"""히트 판정"""
	var closest_note = null
	var closest_diff = INF
	
	for note in active_notes:
		if note.get_meta("lane") != lane:
			continue
		
		var target_time = note.get_meta("target_time")
		var diff = abs(music_position - target_time)
		
		if diff < closest_diff:
			closest_diff = diff
			closest_note = note
	
	if closest_note == null:
		return
	
	if closest_diff <= perfect_window:
		_on_hit(closest_note, "PERFECT")
	elif closest_diff <= good_window:
		_on_hit(closest_note, "GOOD")
	else:
		return  # 너무 이르면 무시


func _on_hit(note: Node, judgement: String) -> void:
	"""히트 처리"""
	var lane = note.get_meta("lane")
	
	active_notes.erase(note)
	note.queue_free()
	
	combo += 1
	max_combo = max(max_combo, combo)
	
	match judgement:
		"PERFECT":
			score += 100 * (1 + combo / 10)
			perfect_count += 1
		"GOOD":
			score += 50 * (1 + combo / 10)
			good_count += 1
	
	note_hit.emit(lane, judgement)
	combo_changed.emit(combo)
	score_changed.emit(score)


func _on_miss(note: Node) -> void:
	"""미스 처리"""
	combo = 0
	miss_count += 1
	
	note_hit.emit(note.get_meta("lane"), "MISS")
	combo_changed.emit(combo)
