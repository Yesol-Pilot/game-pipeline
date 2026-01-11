
import sys
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
import json

# ==========================================
# 🚨 Aggressive Mocking for Missing Dependencies
# ==========================================
MOCK_MODULES = [
    'playwright', 'playwright.async_api',
    'pytrends', 'pytrends.request',
    'PIL', 'PIL.Image',
    'rembg',
    'requests',
    'fastapi',
    'uvicorn',
    'jwt',
    'cryptography', 'cryptography.hazmat', 'cryptography.hazmat.primitives',
    'google', 'google.oauth2', 'google.oauth2.service_account',
    'googleapiclient', 'googleapiclient.discovery', 'googleapiclient.http'
]

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

# ==========================================
# Main Test Logic
# ==========================================

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

def run_e2e_simulation():
    print("🚀 [E2E Simulation] 게임 파이프라인 실전 테스트 시작...\n")
    print("🔧 [Setup] 외부 라이브러리 및 API Mock 설정 완료")

    # GDD 데이터 샘플
    sample_gdd = {
        "game_title": "Hyper Runner 2026",
        "core_loop": ["Run", "Jump", "Score"],
        "mechanics": ["Jump", "Slide"],
        "art_style": {"style": "Cyberpunk"},
        "assets_required": [
            {"asset_id": "player", "asset_type": "player", "generation_prompt": "prompt"},
            {"asset_id": "bg", "asset_type": "background", "generation_prompt": "prompt"}
        ],
        "monetization": {}
    }

    # Context Managers for Patching
    # Note: We patch the classes where they are IMPORTED or DEFINED
    # Since core/__init__ imports them, patching core.gdd_generator...GDDGenerator is correct if cli imports from there?
    # cli.py imports: from core.gdd_generator.gdd_generator import GDDGenerator
    
    with patch('core.gdd_generator.gdd_generator.GDDGenerator') as MockGDDGen, \
         patch('core.builder.godot_builder.GodotBuilder') as MockBuilder:
        
        # 1. Pipeline: GDD Generation
        mock_gdd_instance = MockGDDGen.return_value
        # GDDGenerator returns a GDD object, not dict. We need to mock the object or the method returning it.
        # But wait, cmd_new creates GDDGenerator instance.
        
        # Let's mock the generate_from_trends to return a simple OBJECT behaving like GDD dataclass or just patch return value
        # In cmd_new: gdd = generator.generate_from_trends(...)
        # generator.save_gdd(gdd, ...)
        
        # We can just let generate_from_trends return 'sample_gdd' (dict) IF save_gdd can handle it?
        # No, save_gdd expects GDD object usually (dataclass).
        # But my mock logic for save_gdd can just print whatever it gets.
        
        mock_gdd_instance.generate_from_trends.return_value = sample_gdd
        
        def save_gdd_side_effect(gdd, path):
            print(f"  📝 [Mock] GDD 파일 생성: {path}")
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(gdd, f, indent=2, ensure_ascii=False)
        mock_gdd_instance.save_gdd.side_effect = save_gdd_side_effect

        # 2. Pipeline: Builder
        mock_builder_instance = MockBuilder.return_value
        
        def build_side_effect(project, platform, output_dir):
            print(f"  🔨 [Mock] Godot 빌드 시뮬레이션: {platform} -> {output_dir}")
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            if platform == 'html5':
                (Path(output_dir) / "index.html").touch()
            elif platform == 'android':
                (Path(output_dir) / "game.aab").touch()
            return {"success": True}
        mock_builder_instance.build.side_effect = build_side_effect

        # --- EXECUTION ---
        import cli
        
        # A. Create Game
        print("\n🎬 [Action 1] 새 게임 생성 (cli.py new)...")
        class NewArgs:
            name = "SimulationGame"
            template = "runner"
        cli.cmd_new(NewArgs())
        
        # Verify
        if Path("games/SimulationGame/gdd.json").exists():
            print(f"  ✅ GDD 파일 확인됨")
        else:
            print("  ❌ GDD 파일 생성 실패")

        # B. Build Game
        print("\n🎬 [Action 2] 게임 빌드 (cli.py build)...")
        class BuildArgs:
            project = "games/SimulationGame"
            platforms = ["html5", "android"]
            godot = "godot"
        cli.cmd_build(BuildArgs())
        
        # Verify
        if Path("builds/html5/index.html").exists():
            print("  ✅ HTML5 빌드 아티팩트 확인됨")
        else:
            print("  ❌ HTML5 빌드 실패")

    print("\n🎉 [Complete] E2E 파이프라인 시뮬레이션 완료!")

if __name__ == "__main__":
    run_e2e_simulation()
