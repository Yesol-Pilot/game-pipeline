extends Node

# 상점 매니저
# 아이템 구매 및 인벤토리 관리

# 상품 카탈로그 (실제로는 JSON 파일이나 리소스에서 로드 권장)
var catalog = {
    "skin_ninja": {
        "id": "skin_ninja",
        "name": "Ninja Runner",
        "price": 500,
        "description": "Swift as the wind!"
    },
    "skin_robot": {
        "id": "skin_robot",
        "name": "Mecha-01",
        "price": 1200,
        "description": "Powered by fusion core."
    },
    "skin_alien": {
        "id": "skin_alien",
        "name": "Galactic Visitor",
        "price": 3000,
        "description": "From another world."
    }
}

func purchase_item(item_id: String) -> bool:
    var data = SaveSystem.get_data()
    if not data: return false
    
    if data.has_skin(item_id):
        print("Already owned: ", item_id)
        return false
        
    if not item_id in catalog:
        print("Item not found: ", item_id)
        return false
        
    var item = catalog[item_id]
    var cost = item.price
    
    if data.total_coins >= cost:
        data.total_coins -= cost
        data.unlock_skin(item_id)
        SaveSystem.save_game()
        print("Purchase successful: ", item_id)
        return true
    else:
        print("Not enough coins.")
        return false

func get_item_info(item_id: String) -> Dictionary:
    return catalog.get(item_id, {})

func get_all_items() -> Dictionary:
    return catalog
