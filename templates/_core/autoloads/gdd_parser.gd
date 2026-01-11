extends Node

# GDD 파서 (Dynamic Balancing)
# gdd.json 파일을 읽어 GameConfig 및 Stats에 자동 적용

signal config_applied(gdd_data: Dictionary)

const GDD_PATH = "res://gdd.json"

func apply_gdd_variables(target_object: Object, section: String) -> void:
    if not FileAccess.file_exists(GDD_PATH):
        print("[GDDParser] No GDD file found at ", GDD_PATH)
        return
        
    var content = FileAccess.get_file_as_string(GDD_PATH)
    var json = JSON.new()
    var error = json.parse(content)
    
    if error != OK:
        print("[GDDParser] JSON Parse Error: ", json.get_error_message())
        return
        
    var data = json.get_data()
    if not data is Dictionary:
        return
        
    # 해당 섹션(예: "mechanics", "stats")이 있는지 확인
    if not section in data:
        return
        
    var section_data = data[section]
    if not section_data is Dictionary:
        return
        
    # 리플렉션으로 프로퍼티 주입
    for key in section_data:
        if key in target_object:
            var val = section_data[key]
            target_object.set(key, val)
            print("[GDDParser] Applied override: ", key, " = ", val)
            
    config_applied.emit(data)

func load_full_gdd() -> Dictionary:
    if not FileAccess.file_exists(GDD_PATH):
        return {}
    var content = FileAccess.get_file_as_string(GDD_PATH)
    var json = JSON.new()
    if json.parse(content) == OK:
        return json.get_data()
    return {}
