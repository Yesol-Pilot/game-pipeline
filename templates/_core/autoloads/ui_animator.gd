extends Node

# UI 애니메이션 유틸리티
# 버튼, 팝업 등에 생동감을 불어넣는 Tween 래퍼

func bounce_in(node: Control, duration: float = 0.5, delay: float = 0.0) -> void:
    node.scale = Vector2.ZERO
    node.pivot_offset = node.size / 2.0
    
    var tween = create_tween().set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
    if delay > 0:
        tween.tween_interval(delay)
    tween.tween_property(node, "scale", Vector2.ONE, duration)

func click_effect(node: Control) -> void:
    node.pivot_offset = node.size / 2.0
    var tween = create_tween().set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
    tween.tween_property(node, "scale", Vector2(0.9, 0.9), 0.05)
    tween.tween_property(node, "scale", Vector2.ONE, 0.05)

func count_number(label: Label, start: int, end: int, duration: float = 1.0) -> void:
    var tween = create_tween().set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
    # Tween using a method to update text
    tween.tween_method(func(val): label.text = str(int(val)), start, end, duration)

func fade_in(node: CanvasItem, duration: float = 0.3) -> void:
    node.modulate.a = 0.0
    node.visible = true
    var tween = create_tween()
    tween.tween_property(node, "modulate:a", 1.0, duration)

func fade_out(node: CanvasItem, duration: float = 0.3) -> void:
    var tween = create_tween()
    tween.tween_property(node, "modulate:a", 0.0, duration)
    tween.tween_callback(func(): node.visible = false)
