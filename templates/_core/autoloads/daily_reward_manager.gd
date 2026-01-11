extends Node

# 일일 보상 매니저
# 24시간 주기 보상 지급

func _ready() -> void:
    # 게임 시작 시 체크
    check_daily_reward()

func check_daily_reward() -> void:
    var data = SaveSystem.get_data()
    if not data: return
    
    var last_time_dict = data.last_login_time
    var current_time_dict = Time.get_datetime_dict_from_system()
    var current_unix = Time.get_unix_time_from_datetime_dict(current_time_dict)
    
    var last_unix = 0
    if not last_time_dict.is_empty():
        last_unix = Time.get_unix_time_from_datetime_dict(last_time_dict)
    
    # 24시간 = 86400초
    # 테스트를 위해 60초로 설정하거나 실제 24시간 적용
    var reward_cooldown = 86400 
    
    if last_unix == 0 or (current_unix - last_unix) >= reward_cooldown:
        _give_reward(data)
        
    # 로그인 시간 갱신 및 저장
    data.last_login_time = current_time_dict
    SaveSystem.save_game()

func _give_reward(data: GameData) -> void:
    var reward_coins = 100
    data.add_coins(reward_coins)
    
    print("🎁 Daily Reward! +", reward_coins, " Coins")
    # UIEvents.popup_opened.emit("DailyRewardPopup", {"amount": reward_coins})
