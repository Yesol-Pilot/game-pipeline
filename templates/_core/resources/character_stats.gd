class_name CharacterStats
extends Resource

# 캐릭터 기본 스탯
@export var health: int = 100
@export var damage: int = 10
@export var movement_speed: float = 200.0
@export var defense: int = 0

# 캐릭터 비주얼
@export var sprite_texture: Texture2D
@export var display_name: String = "Character"

# 캐릭터 특수 능력 (확장성을 위한 딕셔너리 예시)
@export var abilities: Dictionary = {}

func take_damage(amount: int) -> int:
	var actual_damage = max(0, amount - defense)
	health -= actual_damage
	return actual_damage
