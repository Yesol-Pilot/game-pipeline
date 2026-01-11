extends Node

# 광고 매니저 (AdManager)
# AdMob Wrapper & Mocking

signal banner_loaded
signal interstitial_closed
signal rewarded_ad_loaded
signal rewarded_ad_opened
signal rewarded_ad_closed
signal rewarded_ad_earned_reward(amount: int, type: String)
signal rewarded_ad_failed_to_load(error_code: int)

var is_test_mode: bool = true
var _is_rewarded_loaded: bool = false

func _ready() -> void:
    # SDK 초기화 로직 (여기서는 Mock)
    print("[AdManager] Initialized in Test Mode: ", is_test_mode)
    # 실제 연동 시: MobileAds.initialize()

func load_banner() -> void:
    print("[AdManager] Loading Banner...")
    # 실제 로직: ad_view.load_ad(request)
    await get_tree().create_timer(1.0).timeout
    banner_loaded.emit()
    print("[AdManager] Banner Loaded")

func show_banner() -> void:
    print("[AdManager] Show Banner")

func hide_banner() -> void:
    print("[AdManager] Hide Banner")

func load_rewarded_ad() -> void:
    print("[AdManager] Loading Rewarded Ad...")
    await get_tree().create_timer(2.0).timeout
    _is_rewarded_loaded = true
    rewarded_ad_loaded.emit()
    print("[AdManager] Rewarded Ad Loaded")

func show_rewarded_ad() -> void:
    if is_test_mode or _is_rewarded_loaded:
        print("[AdManager] Showing Rewarded Ad")
        rewarded_ad_opened.emit()
        
        # 3초 후 광고 시청 완료 시뮬레이션
        await get_tree().create_timer(3.0).timeout
        
        print("[AdManager] Rewarded Ad Completed")
        rewarded_ad_earned_reward.emit(100, "coins") # 보상 지급
        rewarded_ad_closed.emit()
        _is_rewarded_loaded = false # 소모됨
    else:
        print("[AdManager] Rewarded Ad Not Ready")
        rewarded_ad_failed_to_load.emit(0)

func show_interstitial() -> void:
    print("[AdManager] Showing Interstitial Ad")
    await get_tree().create_timer(2.0).timeout
    print("[AdManager] Interstitial Closed")
    interstitial_closed.emit()
