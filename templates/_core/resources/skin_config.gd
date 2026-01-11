class_name SkinConfig extends Resource
## 스킨 설정 리소스 - 게임의 시각적 테마 정의
## AI 에이전트가 이 리소스를 생성/수정하여 게임 외형을 완전히 변경 가능

@export_group("전역 속성")
@export var theme_name: String = "기본 테마"
@export var theme_description: String = ""
@export var bg_color: Color = Color.SKY_BLUE
@export var bg_music: AudioStream
@export var ui_theme: Theme

@export_group("플레이어 비주얼")
@export var player_scene: PackedScene  # 플레이어 씬 (2D/3D)
@export var player_texture: Texture2D  # 플레이어 텍스처 (스프라이트용)
@export var player_particles_run: PackedScene  # 달리기 파티클
@export var player_particles_jump: PackedScene  # 점프 파티클
@export var player_particles_death: PackedScene  # 사망 파티클

@export_group("환경")
@export var ground_texture: Texture2D
@export var ground_material: Material  # 3D용
@export var obstacle_scene: PackedScene
@export var background_scene: PackedScene  # 패럴랙스 배경 씬
@export var decoration_scenes: Array[PackedScene]  # 장식용 오브젝트

@export_group("UI 요소")
@export var button_texture_normal: Texture2D
@export var button_texture_pressed: Texture2D
@export var coin_icon: Texture2D
@export var heart_icon: Texture2D
@export var star_icon: Texture2D

@export_group("오디오")
@export var sfx_jump: AudioStream
@export var sfx_coin: AudioStream
@export var sfx_death: AudioStream
@export var sfx_button_click: AudioStream
@export var sfx_level_complete: AudioStream

@export_group("셰이더 파라미터")
@export var world_curve_strength: Vector2 = Vector2(0.0, 0.0)  # 월드 커브 효과
@export var color_correction: Color = Color.WHITE


func get_player_visual() -> Resource:
	"""플레이어 비주얼 리소스 반환 (씬 우선, 없으면 텍스처)"""
	if player_scene:
		return player_scene
	return player_texture


func has_valid_player() -> bool:
	"""플레이어 비주얼이 설정되었는지 확인"""
	return player_scene != null or player_texture != null
