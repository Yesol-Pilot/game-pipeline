extends Resource
class_name GameData

## 게임 데이터 모델
## 플레이어의 영구적인 진행 상황을 저장

@export var high_score: int = 0
@export var total_coins: int = 0
@export var unlocked_skins: Array[String] = ["default"]
@export var settings: Dictionary = {
    "sound_on": true,
    "music_on": true
}
@export var last_login_time: Dictionary = {} # 일일 보상 체크용 Time.get_datetime_dict_from_system()

func update_high_score(new_score: int) -> bool:
    if new_score > high_score:
        high_score = new_score
        return true
    return false

func add_coins(amount: int) -> void:
    total_coins += amount

func unlock_skin(skin_id: String) -> void:
    if not skin_id in unlocked_skins:
        unlocked_skins.append(skin_id)

func has_skin(skin_id: String) -> bool:
    return skin_id in unlocked_skins
