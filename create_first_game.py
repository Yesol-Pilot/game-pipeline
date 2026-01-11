"""
첫 게임 생성 테스트 스크립트
실제 파이프라인 동작을 시뮬레이션하여 검증
"""

import asyncio
import json
import shutil
from pathlib import Path
from datetime import datetime

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent


def create_test_gdd():
    """테스트용 GDD 생성"""
    print("\n[1/4] 테스트 GDD 생성 중...")
    
    gdd = {
        "game_title": "테스트 러너 게임",
        "trend_source": {
            "tiktok_hashtags": ["#테스트챌린지"],
            "google_trends_keywords": ["테스트"],
            "collected_at": datetime.now().isoformat()
        },
        "core_loop": [
            "플레이어가 자동으로 달린다",
            "화면 터치 시 점프한다",
            "장애물과 충돌하면 게임 오버",
            "거리에 따라 점수 획득"
        ],
        "mechanics": [
            "화면 터치 시 점프",
            "더블 점프 가능",
            "코인 수집"
        ],
        "art_style": {
            "style_prompt": "pixel art style, vibrant colors, cute characters",
            "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
        },
        "character_dna": {
            "main_character": "a cute pixel robot"
        },
        "assets_required": [
            {
                "asset_id": "player_sprite",
                "asset_type": "sprite",
                "generation_prompt": "A running {character_dna}, {art_style}",
                "filename": "player_sprite.png"
            },
            {
                "asset_id": "obstacle_sprite",
                "asset_type": "sprite",
                "generation_prompt": "A simple obstacle, {art_style}",
                "filename": "obstacle_sprite.png"
            },
            {
                "asset_id": "background",
                "asset_type": "sprite",
                "generation_prompt": "A colorful game background, {art_style}",
                "filename": "background.png"
            }
        ],
        "monetization": {
            "ad_placements": ["interstitial", "rewarded"]
        },
        "template_type": "runner",
        "created_at": datetime.now().isoformat()
    }
    
    # GDD 저장
    gdd_path = PROJECT_ROOT / "test_output" / "gdd.json"
    gdd_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(gdd_path, "w", encoding="utf-8") as f:
        json.dump(gdd, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ GDD 생성 완료: {gdd_path}")
    return gdd, gdd_path


def copy_template(template_type: str = "runner"):
    """템플릿 복사"""
    print("\n[2/4] 템플릿 복사 중...")
    
    template_path = PROJECT_ROOT / "templates" / f"template_{template_type}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    game_path = PROJECT_ROOT / "test_output" / f"game_{timestamp}"
    
    if template_path.exists():
        shutil.copytree(template_path, game_path)
        print(f"  ✓ 템플릿 복사 완료: {game_path}")
    else:
        game_path.mkdir(parents=True, exist_ok=True)
        print(f"  ⚠ 템플릿 없음, 빈 폴더 생성: {game_path}")
    
    return game_path


def create_placeholder_assets(game_path: Path, gdd: dict):
    """플레이스홀더 자산 생성"""
    print("\n[3/4] 플레이스홀더 자산 생성 중...")
    
    assets_dir = game_path / "assets" / "sprites"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    for asset in gdd.get("assets_required", []):
        filename = asset.get("filename", f"{asset['asset_id']}.png")
        asset_path = assets_dir / filename
        
        # 빈 파일 생성 (실제로는 이미지 생성 API 사용)
        asset_path.touch()
        print(f"  ✓ 자산 생성: {filename}")
    
    return assets_dir


def generate_report(gdd: dict, game_path: Path):
    """결과 리포트 생성"""
    print("\n[4/4] 리포트 생성 중...")
    
    report = f"""
╔══════════════════════════════════════════════════╗
║          게임 생성 테스트 완료                    ║
╚══════════════════════════════════════════════════╝

📋 기본 정보
  - 게임 제목: {gdd['game_title']}
  - 템플릿: {gdd['template_type']}
  - 생성 시간: {gdd['created_at'][:19]}

🎮 게임 루프
{chr(10).join(['  ' + str(i+1) + '. ' + step for i, step in enumerate(gdd['core_loop'])])}

🎨 아트 스타일
  - {gdd['art_style']['style_prompt']}

📁 출력 경로
  - 프로젝트: {game_path}
  - GDD: {game_path.parent / 'gdd.json'}

✅ 다음 단계
  1. config/project_config.json에 API 키 설정
  2. pip install -r requirements.txt
  3. python core/pipeline.py 실행
"""
    
    print(report)
    
    # 리포트 저장
    report_path = PROJECT_ROOT / "test_output" / "report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    return report_path


def main():
    """테스트 실행"""
    print("\n" + "=" * 50)
    print("첫 게임 생성 테스트")
    print("=" * 50)
    
    # 1. GDD 생성
    gdd, gdd_path = create_test_gdd()
    
    # 2. 템플릿 복사
    game_path = copy_template(gdd["template_type"])
    
    # 3. 플레이스홀더 자산 생성
    create_placeholder_assets(game_path, gdd)
    
    # 4. 리포트 생성
    generate_report(gdd, game_path)
    
    print("\n🎉 테스트 완료!")
    print(f"   결과 확인: {PROJECT_ROOT / 'test_output'}")


if __name__ == "__main__":
    main()
