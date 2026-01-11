"""
단위 테스트 - 코어 모듈
pytest -v tests/
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

# 프로젝트 경로 설정
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gdd_generator.gdd_generator import GDDGenerator, GDD


class TestGDDGenerator:
    """GDD 생성기 테스트"""
    
    @pytest.fixture
    def generator(self):
        config = {
            "provider": "test",
            "schema_path": str(Path(__file__).parent.parent / "schemas" / "gdd_schema.json")
        }
        return GDDGenerator(config)
    
    @pytest.fixture
    def sample_trends(self):
        return {
            "tiktok": [{"hashtag": "#테스트", "view_count": 1000000}],
            "google": [{"keyword": "테스트", "interest": 80}]
        }
    
    def test_generate_from_trends_creates_gdd(self, generator, sample_trends):
        """트렌드로부터 GDD 생성 테스트"""
        gdd = generator.generate_from_trends(
            sample_trends["tiktok"],
            sample_trends["google"],
            "runner"
        )
        
        assert gdd is not None
        assert gdd.game_title != ""
        assert gdd.template_type == "runner"
    
    def test_gdd_has_required_fields(self, generator, sample_trends):
        """GDD 필수 필드 존재 테스트"""
        gdd = generator.generate_from_trends(
            sample_trends["tiktok"],
            sample_trends["google"],
            "puzzle"
        )
        
        assert hasattr(gdd, "game_title")
        assert hasattr(gdd, "core_loop")
        assert hasattr(gdd, "mechanics")
        assert hasattr(gdd, "art_style")
        assert hasattr(gdd, "assets_required")
    
    def test_validate_gdd_valid(self, generator, sample_trends):
        """유효한 GDD 검증 테스트"""
        gdd = generator.generate_from_trends(
            sample_trends["tiktok"],
            sample_trends["google"],
            "clicker"
        )
        
        is_valid, errors = generator.validate_gdd(gdd)
        assert is_valid, f"검증 실패: {errors}"
    
    def test_validate_gdd_invalid_empty_title(self, generator):
        """빈 제목 GDD 검증 실패 테스트"""
        gdd = GDD(
            game_title="",
            trend_source={},
            core_loop=[],
            mechanics=[],
            art_style={},
            assets_required=[],
            monetization={},
            template_type="runner"
        )
        
        is_valid, errors = generator.validate_gdd(gdd)
        assert not is_valid
        assert "game_title" in str(errors)
    
    def test_save_and_load_gdd(self, generator, sample_trends, tmp_path):
        """GDD 저장 및 로드 테스트"""
        gdd = generator.generate_from_trends(
            sample_trends["tiktok"],
            sample_trends["google"],
            "runner"
        )
        
        filepath = tmp_path / "test_gdd.json"
        generator.save_gdd(gdd, str(filepath))
        
        assert filepath.exists()
        
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        
        assert loaded["game_title"] == gdd.game_title
        assert loaded["template_type"] == gdd.template_type


class TestAssetGenerator:
    """자산 생성기 테스트"""
    
    @pytest.fixture
    def generator(self):
        from core.asset_pipeline.asset_generator import AssetGenerator
        return AssetGenerator({"api_key": ""})  # API 키 없이 테스트
    
    def test_placeholder_generation(self, generator, tmp_path):
        """플레이스홀더 생성 테스트"""
        output_path = str(tmp_path / "test_sprite.png")
        
        result = generator.generate_sprite(
            prompt="test sprite",
            output_path=output_path
        )
        
        assert result is not None
        assert result.asset_type == "placeholder"
        assert Path(output_path).exists()
    
    def test_build_prompt(self, generator):
        """프롬프트 빌드 테스트"""
        prompt = generator._build_prompt("a cute robot", "pixel-art")
        
        assert "cute robot" in prompt
        assert "pixel art" in prompt.lower()


class TestSlackNotifier:
    """슬랙 알림 테스트"""
    
    @pytest.fixture
    def notifier(self):
        from core.orchestrator.slack_notifier import SlackNotifier
        return SlackNotifier({"webhook_url": "", "channel": "#test"})
    
    def test_build_blocks(self, notifier):
        """Block Kit 메시지 빌드 테스트"""
        class MockGDD:
            game_title = "테스트 게임"
            template_type = "runner"
            core_loop = ["시작", "플레이", "종료"]
            mechanics = ["점프", "슬라이드"]
            created_at = "2026-01-01T00:00:00"
        
        blocks = notifier._build_blocks(MockGDD(), "http://callback")
        
        assert len(blocks) > 0
        assert any("테스트 게임" in str(block) for block in blocks)


class TestProjectStructure:
    """프로젝트 구조 테스트"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent
    
    def test_core_modules_exist(self, project_root):
        """코어 모듈 존재 테스트"""
        required_modules = [
            "core/__init__.py",
            "core/pipeline.py",
            "core/crawler/__init__.py",
            "core/gdd_generator/__init__.py",
            "core/builder/__init__.py",
            "core/asset_pipeline/__init__.py",
            "core/orchestrator/__init__.py",
        ]
        
        for module in required_modules:
            assert (project_root / module).exists(), f"모듈 누락: {module}"
    
    def test_templates_exist(self, project_root):
        """템플릿 존재 테스트"""
        templates = ["runner", "puzzle", "clicker", "match3", "rhythm", "idle"]
        
        for template in templates:
            template_dir = project_root / "templates" / f"template_{template}"
            assert template_dir.exists(), f"템플릿 누락: {template}"
            assert (template_dir / "project.godot").exists(), f"project.godot 누락: {template}"
    
    def test_schemas_valid_json(self, project_root):
        """스키마 JSON 유효성 테스트"""
        schema_files = [
            "schemas/gdd_schema.json",
            "schemas/template_config_schema.json",
        ]
        
        for schema_file in schema_files:
            filepath = project_root / schema_file
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)  # JSON 파싱 가능해야 함
                assert "$schema" in data or "properties" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
