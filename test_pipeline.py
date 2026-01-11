"""
파이프라인 테스트 스크립트
MVP 검증을 위한 간단한 테스트 실행
"""

import asyncio
import json
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_gdd_generator():
    """GDD 생성 테스트"""
    print("\n" + "=" * 50)
    print("GDD 생성기 테스트")
    print("=" * 50)
    
    from core.gdd_generator import GDDGenerator
    
    config = {
        "provider": "gemini",
        "schema_path": str(project_root / "schemas" / "gdd_schema.json")
    }
    
    generator = GDDGenerator(config)
    
    # 테스트 트렌드 데이터
    tiktok_trends = [
        {"hashtag": "#테스트챌린지", "view_count": 2000000}
    ]
    google_trends = [
        {"keyword": "테스트챌린지", "interest": 80}
    ]
    
    # GDD 생성
    gdd = generator.generate_from_trends(tiktok_trends, google_trends, "runner")
    
    # 검증
    is_valid, errors = generator.validate_gdd(gdd)
    
    print(f"  게임 제목: {gdd.game_title}")
    print(f"  템플릿: {gdd.template_type}")
    print(f"  코어 루프: {len(gdd.core_loop)}단계")
    print(f"  메카닉: {len(gdd.mechanics)}개")
    print(f"  유효성: {'✓' if is_valid else '✗ ' + str(errors)}")
    
    # 저장
    output_path = project_root / "test_gdd.json"
    generator.save_gdd(gdd, str(output_path))
    print(f"  저장 위치: {output_path}")
    
    return gdd


def test_project_structure():
    """프로젝트 구조 검증"""
    print("\n" + "=" * 50)
    print("프로젝트 구조 검증")
    print("=" * 50)
    
    required_paths = [
        "core/__init__.py",
        "core/pipeline.py",
        "core/crawler/tiktok_crawler.py",
        "core/crawler/google_trends_crawler.py",
        "core/gdd_generator/gdd_generator.py",
        "core/builder/godot_builder.py",
        "core/orchestrator/slack_notifier.py",
        "templates/template_runner/project.godot",
        "templates/template_runner/scenes/main.tscn",
        "templates/template_runner/scenes/game.tscn",
        "templates/template_runner/scenes/player.tscn",
        "templates/template_runner/scenes/obstacle.tscn",
        "templates/_core/autoloads/event_bus.gd",
        "templates/_core/autoloads/skin_manager.gd",
        "templates/_core/autoloads/game_manager.gd",
        "schemas/gdd_schema.json",
        "schemas/template_config_schema.json",
        "config/project_config.json",
        "MASTER_RULES.md",
    ]
    
    all_exist = True
    for path_str in required_paths:
        path = project_root / path_str
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  [{status}] {path_str}")
        if not exists:
            all_exist = False
    
    return all_exist


def test_template_copy():
    """템플릿 복사 테스트"""
    print("\n" + "=" * 50)
    print("템플릿 복사 테스트")
    print("=" * 50)
    
    import shutil
    from datetime import datetime
    
    template_path = project_root / "templates" / "template_runner"
    
    if not template_path.exists():
        print("  ✗ 템플릿이 존재하지 않습니다")
        return False
    
    # 테스트용 게임 폴더 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_game_path = project_root / "games" / "runner" / f"test_{timestamp}"
    
    try:
        shutil.copytree(template_path, test_game_path)
        print(f"  ✓ 템플릿 복사 성공: {test_game_path}")
        
        # 정리 (테스트 폴더 삭제)
        shutil.rmtree(test_game_path)
        print("  ✓ 테스트 폴더 정리 완료")
        return True
        
    except Exception as e:
        print(f"  ✗ 복사 실패: {e}")
        return False


def main():
    """전체 테스트 실행"""
    print("\n")
    print("╔" + "═" * 48 + "╗")
    print("║       MVP 파이프라인 테스트 시작              ║")
    print("╚" + "═" * 48 + "╝")
    
    results = []
    
    # 1. 구조 검증
    results.append(("프로젝트 구조", test_project_structure()))
    
    # 2. GDD 생성 테스트
    try:
        gdd = test_gdd_generator()
        results.append(("GDD 생성", gdd is not None))
    except Exception as e:
        print(f"  ✗ GDD 생성 실패: {e}")
        results.append(("GDD 생성", False))
    
    # 3. 템플릿 복사 테스트
    results.append(("템플릿 복사", test_template_copy()))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 통과" if passed else "✗ 실패"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False
    
    print("\n" + ("🎉 모든 테스트 통과!" if all_passed else "⚠️ 일부 테스트 실패"))
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
