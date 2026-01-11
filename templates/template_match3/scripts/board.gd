extends Node2D
## 매치3 게임 보드 스크립트

# 보드 설정
@export var grid_width: int = 8
@export var grid_height: int = 8
@export var cell_size: int = 100
@export var gem_types: int = 6
@export var min_match: int = 3

# 젬 씬
@export var gem_scene: PackedScene

# 보드 데이터
var board: Array = []  # 2D 배열 [x][y]
var selected_gem: Vector2i = Vector2i(-1, -1)
var is_swapping: bool = false
var is_processing: bool = false

# 점수
var score: int = 0
var moves: int = 30
var combo: int = 0

signal score_changed(new_score: int)
signal moves_changed(new_moves: int)
signal combo_triggered(combo_count: int)
signal game_over()


func _ready() -> void:
	_init_board()
	_fill_board()


func _init_board() -> void:
	"""보드 초기화"""
	board.clear()
	for x in range(grid_width):
		var column = []
		for y in range(grid_height):
			column.append(-1)  # -1 = 빈 칸
		board.append(column)


func _fill_board() -> void:
	"""보드 채우기 (초기 매칭 방지)"""
	for x in range(grid_width):
		for y in range(grid_height):
			var gem_type = _get_valid_gem_type(x, y)
			board[x][y] = gem_type
			_spawn_gem(x, y, gem_type)


func _get_valid_gem_type(x: int, y: int) -> int:
	"""초기 매칭을 방지하는 젬 타입 선택"""
	var possible = range(gem_types)
	
	# 왼쪽 2개 확인
	if x >= 2:
		if board[x-1][y] == board[x-2][y]:
			possible = possible.filter(func(t): return t != board[x-1][y])
	
	# 아래 2개 확인
	if y >= 2:
		if board[x][y-1] == board[x][y-2]:
			possible = possible.filter(func(t): return t != board[x][y-1])
	
	return possible[randi() % possible.size()]


func _spawn_gem(x: int, y: int, gem_type: int) -> void:
	"""젬 스폰"""
	if gem_scene == null:
		return
	
	var gem = gem_scene.instantiate()
	gem.position = _grid_to_world(x, y)
	gem.set_type(gem_type)
	gem.grid_pos = Vector2i(x, y)
	add_child(gem)


func _grid_to_world(x: int, y: int) -> Vector2:
	"""그리드 좌표를 월드 좌표로 변환"""
	return Vector2(x * cell_size + cell_size / 2, y * cell_size + cell_size / 2)


func _input(event: InputEvent) -> void:
	if is_processing or is_swapping:
		return
	
	if event is InputEventMouseButton:
		if event.pressed:
			var grid_pos = _world_to_grid(event.position - global_position)
			_on_cell_clicked(grid_pos)
	
	elif event is InputEventMouseMotion and selected_gem != Vector2i(-1, -1):
		# 스와이프 감지
		pass


func _world_to_grid(world_pos: Vector2) -> Vector2i:
	"""월드 좌표를 그리드 좌표로 변환"""
	return Vector2i(int(world_pos.x / cell_size), int(world_pos.y / cell_size))


func _on_cell_clicked(grid_pos: Vector2i) -> void:
	"""셀 클릭 처리"""
	if not _is_valid_pos(grid_pos):
		selected_gem = Vector2i(-1, -1)
		return
	
	if selected_gem == Vector2i(-1, -1):
		# 첫 번째 선택
		selected_gem = grid_pos
	else:
		# 두 번째 선택 - 스와이프 시도
		if _is_adjacent(selected_gem, grid_pos):
			_try_swap(selected_gem, grid_pos)
		selected_gem = Vector2i(-1, -1)


func _is_valid_pos(pos: Vector2i) -> bool:
	"""유효한 그리드 위치인지 확인"""
	return pos.x >= 0 and pos.x < grid_width and pos.y >= 0 and pos.y < grid_height


func _is_adjacent(a: Vector2i, b: Vector2i) -> bool:
	"""인접한 셀인지 확인"""
	return abs(a.x - b.x) + abs(a.y - b.y) == 1


func _try_swap(a: Vector2i, b: Vector2i) -> void:
	"""스와이프 시도"""
	is_swapping = true
	
	# 임시 교환
	var temp = board[a.x][a.y]
	board[a.x][a.y] = board[b.x][b.y]
	board[b.x][b.y] = temp
	
	# 매칭 확인
	if _has_match_at(a) or _has_match_at(b):
		# 유효한 스와이프
		moves -= 1
		moves_changed.emit(moves)
		await _animate_swap(a, b)
		_process_matches()
	else:
		# 무효 - 되돌리기
		board[b.x][b.y] = board[a.x][a.y]
		board[a.x][a.y] = temp
	
	is_swapping = false


func _animate_swap(a: Vector2i, b: Vector2i) -> void:
	"""스와이프 애니메이션"""
	# Tween 애니메이션 구현
	await get_tree().create_timer(0.2).timeout


func _has_match_at(pos: Vector2i) -> bool:
	"""해당 위치에 매칭이 있는지 확인"""
	var gem_type = board[pos.x][pos.y]
	return _count_horizontal(pos, gem_type) >= min_match or _count_vertical(pos, gem_type) >= min_match


func _count_horizontal(pos: Vector2i, gem_type: int) -> int:
	"""가로 연속 개수"""
	var count = 1
	# 왼쪽
	var x = pos.x - 1
	while x >= 0 and board[x][pos.y] == gem_type:
		count += 1
		x -= 1
	# 오른쪽
	x = pos.x + 1
	while x < grid_width and board[x][pos.y] == gem_type:
		count += 1
		x += 1
	return count


func _count_vertical(pos: Vector2i, gem_type: int) -> int:
	"""세로 연속 개수"""
	var count = 1
	# 위
	var y = pos.y - 1
	while y >= 0 and board[pos.x][y] == gem_type:
		count += 1
		y -= 1
	# 아래
	y = pos.y + 1
	while y < grid_height and board[pos.x][y] == gem_type:
		count += 1
		y += 1
	return count


func _process_matches() -> void:
	"""매칭 처리 (연쇄 포함)"""
	is_processing = true
	combo = 0
	
	while true:
		var matches = _find_all_matches()
		if matches.is_empty():
			break
		
		combo += 1
		combo_triggered.emit(combo)
		
		# 매칭된 젬 제거
		for pos in matches:
			score += 10 * combo
			board[pos.x][pos.y] = -1
		
		score_changed.emit(score)
		await get_tree().create_timer(0.3).timeout
		
		# 젬 낙하
		_drop_gems()
		await get_tree().create_timer(0.3).timeout
		
		# 빈 공간 채우기
		_refill_board()
		await get_tree().create_timer(0.3).timeout
	
	is_processing = false
	
	if moves <= 0:
		game_over.emit()


func _find_all_matches() -> Array:
	"""모든 매칭 위치 찾기"""
	var matches = []
	
	for x in range(grid_width):
		for y in range(grid_height):
			if board[x][y] == -1:
				continue
			
			var pos = Vector2i(x, y)
			if _has_match_at(pos):
				# 매칭된 모든 셀 추가
				var gem_type = board[x][y]
				
				# 가로 매칭
				if _count_horizontal(pos, gem_type) >= min_match:
					var start_x = x
					while start_x > 0 and board[start_x-1][y] == gem_type:
						start_x -= 1
					var end_x = x
					while end_x < grid_width - 1 and board[end_x+1][y] == gem_type:
						end_x += 1
					for mx in range(start_x, end_x + 1):
						if not Vector2i(mx, y) in matches:
							matches.append(Vector2i(mx, y))
				
				# 세로 매칭
				if _count_vertical(pos, gem_type) >= min_match:
					var start_y = y
					while start_y > 0 and board[x][start_y-1] == gem_type:
						start_y -= 1
					var end_y = y
					while end_y < grid_height - 1 and board[x][end_y+1] == gem_type:
						end_y += 1
					for my in range(start_y, end_y + 1):
						if not Vector2i(x, my) in matches:
							matches.append(Vector2i(x, my))
	
	return matches


func _drop_gems() -> void:
	"""빈 공간으로 젬 낙하"""
	for x in range(grid_width):
		var write_y = grid_height - 1
		for read_y in range(grid_height - 1, -1, -1):
			if board[x][read_y] != -1:
				if write_y != read_y:
					board[x][write_y] = board[x][read_y]
					board[x][read_y] = -1
				write_y -= 1


func _refill_board() -> void:
	"""빈 공간에 새 젬 채우기"""
	for x in range(grid_width):
		for y in range(grid_height):
			if board[x][y] == -1:
				board[x][y] = randi() % gem_types
