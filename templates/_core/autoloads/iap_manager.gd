extends Node

# 인앱 결제 매니저 (IAPManager)
# Godot IAP Wrapper & Mocking

signal purchase_success(product_id: String)
signal purchase_failed(product_id: String, reason: String)

var products = {
    "gem_pack_small": {"id": "gem_pack_small", "price": "$0.99"},
    "remove_ads": {"id": "remove_ads", "price": "$2.99"}
}

func _ready() -> void:
    # Google Play Billing 초기화 등
    print("[IAPManager] Initialized")

func request_product_info() -> void:
    print("[IAPManager] Requesting Product Info...")
    # 실제로는 스토어 연결
    
func purchase_product(product_id: String) -> void:
    print("[IAPManager] Purchasing: ", product_id)
    
    if not product_id in products:
        purchase_failed.emit(product_id, "Invalid Product ID")
        return
        
    # Mock 결제 프로세스
    await get_tree().create_timer(1.5).timeout
    
    # 랜덤 성공/실패 시뮬레이션 (90% 성공)
    if randf() < 0.9:
        print("[IAPManager] Purchase Successful: ", product_id)
        purchase_success.emit(product_id)
        # 여기서 GameData 업데이트 로직을 직접 호출하지 않고, 시그널을 받은 쪽(ShopManager 등)에서 처리 권장
        # 또는 여기서 처리하고 Global Signal 발송
    else:
        print("[IAPManager] Purchase Failed")
        purchase_failed.emit(product_id, "User Cancelled")
