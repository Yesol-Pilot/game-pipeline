extends Control
class_name ShopPopup

## 상점 팝업 UI
## Code-Driven UI: 씬 파일 없이 코드로 UI 구성

var background: Panel
var item_list: VBoxContainer
var close_button: Button
var coin_label: Label

func _ready() -> void:
    # 1. UI 구조 생성
    _setup_ui()
    
    # 2. 데이터 표시
    _update_list()
    _update_coin_display()
    
    # 3. 등장 애니메이션
    UIAnimator.bounce_in(background)

func _setup_ui() -> void:
    # 전체 화면 커버
    anchors_preset = Control.PRESET_FULL_RECT
    
    # 반투명 배경
    var dimmer = ColorRect.new()
    dimmer.color = Color(0, 0, 0, 0.5)
    dimmer.anchors_preset = Control.PRESET_FULL_RECT
    add_child(dimmer)
    
    # 메인 패널
    background = Panel.new()
    background.custom_minimum_size = Vector2(800, 1000)
    background.set_anchors_preset(Control.PRESET_CENTER)
    background.pivot_offset = Vector2(400, 500) # 중앙 기준
    add_child(background)
    
    # 제목
    var title = Label.new()
    title.text = "ITEM SHOP"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.position = Vector2(0, 50)
    title.size = Vector2(800, 50)
    title.add_theme_font_size_override("font_size", 48)
    background.add_child(title)
    
    # 코인 표시
    coin_label = Label.new()
    coin_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    coin_label.position = Vector2(0, 120)
    coin_label.size = Vector2(750, 40)
    coin_label.add_theme_font_size_override("font_size", 32)
    coin_label.add_theme_color_override("font_color", Color.GOLD)
    background.add_child(coin_label)
    
    # 아이템 리스트 (스크롤)
    var scroll = ScrollContainer.new()
    scroll.position = Vector2(50, 200)
    scroll.size = Vector2(700, 600)
    background.add_child(scroll)
    
    item_list = VBoxContainer.new()
    item_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    item_list.add_theme_constant_override("separation", 20)
    scroll.add_child(item_list)
    
    # 닫기 버튼
    close_button = Button.new()
    close_button.text = "CLOSE"
    close_button.position = Vector2(200, 850)
    close_button.size = Vector2(400, 100)
    close_button.pressed.connect(_on_close_pressed)
    background.add_child(close_button)

func _update_list() -> void:
    # 기존 아이템 제거
    for child in item_list.get_children():
        child.queue_free()
        
    var items = ShopManager.get_all_items()
    var data = SaveSystem.get_data()
    
    for id in items:
        var info = items[id]
        var btn = Button.new()
        btn.custom_minimum_size = Vector2(0, 120)
        
        var is_owned = data.has_skin(id)
        var price_text = str(info.price) + " C"
        if is_owned:
            price_text = "OWNED"
            btn.disabled = true
            
        btn.text = info.name + "\n" + price_text
        btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
        
        # 버튼 클릭 시 구매 시도
        if not is_owned:
            btn.pressed.connect(func(): _on_buy_pressed(id, btn))
            
        item_list.add_child(btn)

func _update_coin_display() -> void:
    var data = SaveSystem.get_data()
    if data:
        coin_label.text = "Coins: " + str(data.total_coins)

func _on_buy_pressed(id: String, btn: Button) -> void:
    UIAnimator.click_effect(btn)
    
    var success = ShopManager.purchase_item(id)
    if success:
        _update_list() # 목록 갱신 (구매 완료 표시)
        _update_coin_display() # 코인 갱신
        # 성공 효과음 등 추가 가능
    else:
        # 실패 피드백 (예: 버튼 흔들기)
        var tween = create_tween()
        tween.tween_property(btn, "position:x", btn.position.x + 10, 0.05)
        tween.tween_property(btn, "position:x", btn.position.x - 10, 0.05)
        tween.tween_property(btn, "position:x", btn.position.x, 0.05)

func _on_close_pressed() -> void:
    UIAnimator.click_effect(close_button)
    # 닫기 애니메이션
    var tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
    tween.tween_property(background, "scale", Vector2.ZERO, 0.3)
    tween.tween_callback(queue_free)
