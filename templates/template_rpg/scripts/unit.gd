extends Node2D

class_name BattleUnit

@export var stats: Resource # CharacterStats
var current_hp: int

signal died
signal damaged(amount)
signal attack_finished

func _ready() -> void:
    if stats:
        current_hp = stats.hp
    else:
        current_hp = 100 # Fallback

func take_damage(amount: int) -> void:
    current_hp -= amount
    emit_signal("damaged", amount)
    
    # 텍스트 플로팅 효과 (단순 print 대체)
    print(name + " took " + str(amount) + " damage!")
    
    if current_hp <= 0:
        current_hp = 0
        die()

func die() -> void:
    emit_signal("died")
    queue_free()

func attack(target: BattleUnit) -> void:
    # 공격 애니메이션 위치 이동 (Tween)
    var original_pos = position
    var tween = create_tween()
    
    # 1. 전진
    tween.tween_property(self, "position", target.position + Vector2(0, 50), 0.2)
    tween.tween_callback(func(): 
        target.take_damage(stats.damage if stats else 10)
    )
    
    # 2. 복귀
    tween.tween_property(self, "position", original_pos, 0.2).set_delay(0.1)
    tween.tween_callback(func():
        emit_signal("attack_finished")
    )
