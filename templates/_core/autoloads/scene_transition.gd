extends Node

# 씬 전환 관리자
# 부드러운 화면 전환(Fade, Wipe)을 처리

signal transition_start
signal transition_finished

var _canvas_layer: CanvasLayer
var _color_rect: ColorRect

func _ready() -> void:
    # 전환 효과용 CanvasLayer 생성 (최상단)
    _canvas_layer = CanvasLayer.new()
    _canvas_layer.layer = 100 # 매우 높은 레이어 번호
    add_child(_canvas_layer)
    
    _color_rect = ColorRect.new()
    _color_rect.anchors_preset = Control.PRESET_FULL_RECT
    _color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _color_rect.color = Color(0, 0, 0, 0) # 투명
    _canvas_layer.add_child(_color_rect)

func change_scene(scene_path: String, type: String = "fade", duration: float = 0.5) -> void:
    transition_start.emit()
    
    _color_rect.mouse_filter = Control.MOUSE_FILTER_STOP # 터치 방지
    
    if type == "fade":
        await _fade_out(duration)
    # 향후 쉐이더 기반 효과 추가 가능
    
    get_tree().change_scene_to_file(scene_path)
    
    if type == "fade":
        await _fade_in(duration)
        
    _color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    transition_finished.emit()

func _fade_out(duration: float) -> void:
    var tween = create_tween()
    tween.tween_property(_color_rect, "color:a", 1.0, duration)
    await tween.finished

func _fade_in(duration: float) -> void:
    var tween = create_tween()
    tween.tween_property(_color_rect, "color:a", 0.0, duration)
    await tween.finished
