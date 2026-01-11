extends Node

# 분석 매니저 (AnalyticsManager)
# 사용자 행동 데이터 로깅

func log_event(event_name: String, parameters: Dictionary = {}) -> void:
    # 콘솔 출력 (디버깅)
    print("📊 [Analytics] ", event_name, " params: ", parameters)
    
    # 실제 구현 시: Firebase.Analytics.log_event(event_name, parameters)
    # 또는 자체 서버로 전송

func log_level_start(level_id: int) -> void:
    log_event("level_start", {"level": level_id})

func log_level_end(level_id: int, result: String, score: int) -> void:
    log_event("level_end", {"level": level_id, "result": result, "score": score})

func log_item_purchase(item_id: String, price: int) -> void:
    log_event("item_purchase", {"item_id": item_id, "price": price})

func log_screen_view(screen_name: String) -> void:
    log_event("screen_view", {"screen_name": screen_name})
