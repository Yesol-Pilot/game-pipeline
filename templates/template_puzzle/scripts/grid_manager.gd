extends Node2D
class_name GridManager

# Match-3 그리드 매니저

@export var width: int = 7
@export var height: int = 9
@export var cell_size: int = 80
@export var start_pos: Vector2 = Vector2(80, 200)

var grid: Array = [] # 2D Array [x][y]
var selected_piece: Piece = null
var is_processing: bool = false

# Piece 씬 프리로드 (가정: 같은 폴더에 piece.tscn 존재하거나 동적 생성)
# 여기서는 텍스처만 있는 Sprite2D를 piece.gd가 붙은 상태로 생성한다고 가정
var piece_script = preload("res://templates/template_puzzle/scripts/piece.gd")
var temp_texture = PlaceholderTexture2D.new() # 실제 에셋 로드시 교체

func _ready() -> void:
    temp_texture.size = Vector2(70, 70)
    _init_grid()
    _spawn_initial_pieces()

func _init_grid() -> void:
    grid = []
    for x in range(width):
        grid.append([])
        for y in range(height):
            grid[x].append(null)

func _spawn_initial_pieces() -> void:
    for x in range(width):
        for y in range(height):
            _spawn_piece(x, y)

func _spawn_piece(x: int, y: int) -> void:
    var type = randi() % 5
    var piece = Sprite2D.new()
    piece.texture = temp_texture
    piece.set_script(piece_script)
    add_child(piece)
    
    var world_pos = _grid_to_world(x, y)
    # 위에서 떨어지는 효과를 위해 y 시작점 조정 가능
    piece.initialize(type, world_pos)
    piece.grid_position = Vector2i(x, y)
    grid[x][y] = piece

func _grid_to_world(x: int, y: int) -> Vector2:
    return start_pos + Vector2(x * cell_size, y * cell_size)

func _input(event: InputEvent) -> void:
    if is_processing: return
    
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        _handle_click(event.position)

func _handle_click(pos: Vector2) -> void:
    var local_pos = pos - start_pos
    var x = int(local_pos.x / cell_size)
    var y = int(local_pos.y / cell_size)
    
    if _is_valid_grid(x, y):
        var clicked_piece = grid[x][y]
        
        if selected_piece == null:
            selected_piece = clicked_piece
            selected_piece.set_selected(true)
        elif selected_piece == clicked_piece:
            selected_piece.set_selected(false)
            selected_piece = null
        else:
            # 인접했는지 확인
            if _is_adjacent(selected_piece.grid_position, Vector2i(x, y)):
                selected_piece.set_selected(false)
                _swap_pieces(selected_piece, clicked_piece)
                selected_piece = null
            else:
                selected_piece.set_selected(false)
                selected_piece = clicked_piece
                selected_piece.set_selected(true)

func _is_valid_grid(x: int, y: int) -> bool:
    return x >= 0 and x < width and y >= 0 and y < height

func _is_adjacent(p1: Vector2i, p2: Vector2i) -> bool:
    return abs(p1.x - p2.x) + abs(p1.y - p2.y) == 1

func _swap_pieces(p1: Piece, p2: Piece) -> void:
    is_processing = true
    
    # 그리드 데이터 교환
    var temp_pos = p1.grid_position
    p1.grid_position = p2.grid_position
    p2.grid_position = temp_pos
    
    grid[p1.grid_position.x][p1.grid_position.y] = p1
    grid[p2.grid_position.x][p2.grid_position.y] = p2
    
    # 비주얼 이동
    p1.move_to(_grid_to_world(p1.grid_position.x, p1.grid_position.y))
    p2.move_to(_grid_to_world(p2.grid_position.x, p2.grid_position.y))
    
    await get_tree().create_timer(0.3).timeout
    
    # 매치 확인 (간단 구현: 매치 없으면 되돌리기 로직은 생략함)
    _find_and_destroy_matches()
    
    is_processing = false

func _find_and_destroy_matches() -> void:
    var matched_pieces = []
    
    # 가로 Check
    for y in range(height):
        for x in range(width - 2):
            var p1 = grid[x][y]
            var p2 = grid[x+1][y]
            var p3 = grid[x+2][y]
            if p1 and p2 and p3 and p1.type == p2.type and p2.type == p3.type:
                if not p1 in matched_pieces: matched_pieces.append(p1)
                if not p2 in matched_pieces: matched_pieces.append(p2)
                if not p3 in matched_pieces: matched_pieces.append(p3)
                
    # 세로 Check
    for x in range(width):
        for y in range(height - 2):
            var p1 = grid[x][y]
            var p2 = grid[x][y+1]
            var p3 = grid[x][y+2]
            if p1 and p2 and p3 and p1.type == p2.type and p2.type == p3.type:
                if not p1 in matched_pieces: matched_pieces.append(p1)
                if not p2 in matched_pieces: matched_pieces.append(p2)
                if not p3 in matched_pieces: matched_pieces.append(p3)
    
    if matched_pieces.size() > 0:
        print("Match Found! Count: ", matched_pieces.size())
        for p in matched_pieces:
            grid[p.grid_position.x][p.grid_position.y] = null
            p.destroy()
        
        # 빈 공간 채우기 로직 (Refill) 호출 필요 (여기는 생략)
