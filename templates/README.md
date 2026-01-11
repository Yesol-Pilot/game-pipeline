# 게임 템플릿 저장소

이 폴더에는 하이퍼 캐주얼 게임 개발을 위한 Godot 템플릿이 저장됩니다.

## 📁 템플릿 구조

각 템플릿은 다음 구조를 따릅니다:

```
template_{게임유형}/
├── project.godot           # Godot 프로젝트 파일
├── scenes/                 # 장면 파일 (.tscn)
│   ├── main.tscn           # 메인 장면
│   ├── game.tscn           # 게임 플레이 장면
│   └── ui/                 # UI 장면
├── scripts/                # GDScript 파일
│   ├── main.gd             # 메인 스크립트
│   ├── player.gd           # 플레이어 로직
│   └── game_manager.gd     # 게임 관리자
├── assets/                 # 자산 (플레이스홀더)
│   ├── sprites/            # 스프라이트 이미지
│   ├── audio/              # 오디오 파일
│   └── fonts/              # 폰트 파일
├── export_presets.cfg      # 내보내기 설정
└── template_config.json    # 템플릿 메타데이터
```

## 🎮 템플릿 유형

| 유형 | 설명 | 핵심 메카닉 |
|------|------|-------------|
| `runner` | 무한 러너 | 달리기, 점프, 장애물 회피 |
| `puzzle` | 물리 퍼즐 | 드래그, 충돌, 목표 달성 |
| `clicker` | 클리커/태퍼 | 터치, 업그레이드, 보상 |
| `match3` | 매치-3 | 스와이프, 매칭, 콤보 |
| `arcade` | 아케이드 | 조준, 발사, 점수 경쟁 |

## 📐 템플릿 설정 스키마

`template_config.json` 파일은 다음 구조를 따릅니다:

```json
{
  "template_name": "string",
  "template_type": "runner|puzzle|clicker|match3|arcade",
  "version": "string",
  "godot_version": "string",
  "description": "string",
  "parameters": {
    "adjustable_values": []
  },
  "assets_required": [],
  "export_targets": ["android", "html5", "windows"]
}
```

## 🔧 사용법

1. 적합한 템플릿 선택
2. `games/{게임유형}/` 폴더로 복사
3. `template_config.json`의 파라미터 수정
4. 플레이스홀더 자산을 AI 생성 자산으로 교체
5. Godot 헤드리스 빌드 실행
